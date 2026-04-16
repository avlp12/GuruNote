"""
Step 2: 음성 인식 + 화자 분리 (Speaker Diarization).

기본 엔진은 **Microsoft VibeVoice-ASR** (오픈소스, MIT, 화자/타임스탬프/도메인
핫워드를 단일 패스로 처리). VibeVoice 가 설치돼 있지 않거나 GPU 메모리가
부족해 로딩에 실패하면 **AssemblyAI Cloud API** 로 자동 폴백한다.

두 엔진 모두 결과를 `gurunote.types.Transcript` 형태로 정규화해 반환하므로
LLM/요약 단계는 어느 엔진을 썼는지 신경 쓰지 않아도 된다.
"""

from __future__ import annotations

import os
import platform
import re
import warnings
from typing import Callable, List, Optional

# PyTorch CUDA 메모리 단편화 방지 — Linux 에서만 지원.
# Windows 에서는 expandable_segments 가 미지원이라 UserWarning 이 뜨므로 건너뜀.
if platform.system() != "Windows":
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

from gurunote.types import Segment, Transcript

# 진행 상태 콜백 시그니처: (메시지: str) -> None
ProgressFn = Callable[[str], None]


# IT/AI 도메인 핫워드 — VibeVoice 의 customized context 로 주입할 용어 목록.
# 정확도(특히 고유명사 + 약어)를 끌어올리는 핵심 무기.
IT_AI_HOTWORDS: List[str] = [
    # 모델/연구실
    "OpenAI", "Anthropic", "DeepMind", "Google DeepMind", "Meta AI", "xAI",
    "Mistral", "Cohere", "Hugging Face", "NVIDIA",
    # 인물
    "Sam Altman", "Dario Amodei", "Demis Hassabis", "Yann LeCun",
    "Andrej Karpathy", "Ilya Sutskever", "Geoffrey Hinton", "Lex Fridman",
    # 모델명
    "GPT-4", "GPT-4o", "GPT-5", "Claude", "Claude Sonnet", "Claude Opus",
    "Gemini", "Llama", "Mistral", "Mixtral", "Qwen", "DeepSeek", "o1", "o3",
    # 기술 용어
    "LLM", "RAG", "Fine-tuning", "Pretraining", "Transformer",
    "Attention", "Embedding", "Tokenizer", "Inference", "Quantization",
    "Diffusion", "Multimodal", "Agent", "Tool use", "MCP",
    "Reinforcement Learning", "RLHF", "Chain of Thought", "Mixture of Experts",
    "Context window", "Hallucination", "Alignment", "AGI", "ASI",
    # 인프라
    "CUDA", "TPU", "GPU", "H100", "A100", "PyTorch", "JAX", "TensorRT",
]


# =============================================================================
# VibeVoice 설치 감지 + 설치
# =============================================================================
def is_vibevoice_installed() -> bool:
    """VibeVoice 패키지가 import 가능한지 확인."""
    try:
        import vibevoice  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


def install_vibevoice(progress: Optional[ProgressFn] = None) -> bool:
    """
    pip 로 VibeVoice 를 설치한다.

    Returns:
        True 면 설치 성공, False 면 실패.
    """
    import subprocess
    import sys

    log = progress or (lambda _msg: None)
    log("📦 VibeVoice-ASR 설치 중 (git+https, 수 분 소요 가능)…")

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pip", "install",
                "vibevoice @ git+https://github.com/microsoft/VibeVoice.git",
            ],
            capture_output=True, text=True, timeout=600,
        )
        if result.returncode == 0:
            log("✅ VibeVoice 설치 완료!")
            return True
        log(f"❌ VibeVoice 설치 실패:\n{result.stderr[:300]}")
        return False
    except Exception as exc:  # noqa: BLE001
        log(f"❌ VibeVoice 설치 실패: {exc}")
        return False


# =============================================================================
# Public API
# =============================================================================
def transcribe(
    audio_path: str,
    engine: str = "auto",
    progress: Optional[ProgressFn] = None,
    hotwords: Optional[List[str]] = None,
    stop_event: Optional[object] = None,
) -> Transcript:
    """
    오디오 파일을 화자 분리된 Transcript 로 변환한다.

    Args:
        audio_path: 로컬 오디오 파일 경로 (mp3/wav/m4a/flac …)
        engine: "vibevoice" | "assemblyai" | "auto"
        progress: 진행 메시지 콜백 (Streamlit 등)
        hotwords: 도메인 핫워드. None 이면 IT_AI_HOTWORDS 기본값 사용.

    Returns:
        Transcript — 정규화된 화자 분리 스크립트
    """
    log = progress or (lambda _msg: None)
    engine = (engine or "auto").lower().strip()
    hotwords = hotwords if hotwords is not None else IT_AI_HOTWORDS

    if engine == "vibevoice":
        try:
            result = _transcribe_vibevoice(audio_path, log=log, hotwords=hotwords, stop_event=stop_event)
            _assert_transcript_not_empty(result)
            return result
        except Exception:
            # 강제 모드에서도 실패 시 GPU 메모리 해제 후 에러 전파
            _unload_vibevoice()
            raise

    if engine == "assemblyai":
        result = _transcribe_assemblyai(audio_path, log=log)
        _assert_transcript_not_empty(result)
        return result

    # auto: 하드웨어에 따라 최적 엔진 선택
    device = _detect_device()
    quant = _select_quantization()

    if device == "cpu" or quant == "skip":
        # CPU 또는 Apple Silicon 메모리 부족 → VibeVoice 건너뜀
        reason = "GPU 미감지" if device == "cpu" else (
            f"Apple Silicon 통합 메모리 부족 ({_get_system_memory_gb():.0f}GB < {_MPS_MIN_MEMORY_GB:.0f}GB)"
        )
        log(f"[auto] {reason} — AssemblyAI Cloud API 로 직행합니다.")
        result = _transcribe_assemblyai(audio_path, log=log)
        _assert_transcript_not_empty(result)
        return result

    # GPU (CUDA / MPS) → VibeVoice 우선, 실패 시 AssemblyAI 폴백
    try:
        hw_label = "CUDA" if device == "cuda" else "Apple Silicon (MPS)"
        log(f"[auto] {hw_label} 감지 — VibeVoice-ASR 로 전사를 시도합니다.")
        result = _transcribe_vibevoice(audio_path, log=log, hotwords=hotwords, stop_event=stop_event)
        _assert_transcript_not_empty(result)
        return result
    except Exception as exc:  # noqa: BLE001
        log(f"VibeVoice 실패 ({exc}). 모델 언로드 후 AssemblyAI 로 폴백합니다.")
        _unload_vibevoice()
        result = _transcribe_assemblyai(audio_path, log=log)
        _assert_transcript_not_empty(result)
        return result


def _assert_transcript_not_empty(transcript: Transcript) -> None:
    """빈 전사 결과를 조기에 차단해 후속 LLM 단계의 무의미한 호출을 막는다."""
    if not transcript.segments:
        raise RuntimeError(
            "전사 결과가 비어 있습니다. 오디오 품질/형식 또는 STT 엔진 설정을 확인해주세요."
        )
    has_text = any((seg.text or "").strip() for seg in transcript.segments)
    if not has_text:
        raise RuntimeError(
            "전사 텍스트가 비어 있습니다. 다른 STT 엔진(예: AssemblyAI)으로 다시 시도해주세요."
        )


# =============================================================================
# VibeVoice-ASR 엔진 (오픈소스, GPU 권장)
# =============================================================================
_VIBEVOICE_SINGLETON: dict = {}  # 모델은 한번만 로드해 캐시


def _unload_vibevoice() -> None:
    """
    VibeVoice 모델을 GPU 에서 완전히 내린다.

    OOM/에러 발생 후 GPU 메모리가 계속 점유되는 문제를 해결:
      1. 싱글톤 캐시에서 model/processor 참조 제거
      2. Python GC 로 참조 카운트 정리 (del 만으로는 부족)
      3. torch.cuda.empty_cache() 로 PyTorch 캐시 블록 반환
    이 세 단계를 모두 거쳐야 OS 레벨의 GPU 메모리가 실제로 해제된다.
    """
    import gc

    model = _VIBEVOICE_SINGLETON.pop("model", None)
    _VIBEVOICE_SINGLETON.pop("processor", None)
    _VIBEVOICE_SINGLETON.pop("device", None)
    _VIBEVOICE_SINGLETON.pop("ready", None)

    if model is not None:
        del model

    gc.collect()

    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:  # noqa: BLE001
        pass


def _detect_device() -> str:
    """현재 사용 가능한 최적 디바이스를 감지한다."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:  # noqa: BLE001
        pass
    return "cpu"


def _get_system_memory_gb() -> float:
    """
    시스템 총 RAM(GB). Apple Silicon 의 통합 메모리 크기 판단에 사용.

    macOS: sysctl hw.memsize
    Linux: os.sysconf
    Windows: 해당 없음 (CUDA VRAM 으로 별도 관리)
    """
    try:
        if platform.system() == "Darwin":
            import subprocess
            r = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0 and r.stdout.strip():
                return int(r.stdout.strip()) / (1024 ** 3)
    except Exception:  # noqa: BLE001
        pass
    # Linux fallback (os.sysconf)
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return (pages * page_size) / (1024 ** 3)
    except Exception:  # noqa: BLE001
        pass
    return 0.0


# VibeVoice 7B fp16 = ~14GB. 시스템 OS 가 ~4GB 사용하므로 최소 18GB 필요.
_MPS_MIN_MEMORY_GB = 18.0


def _select_quantization() -> str:
    """
    VRAM + 하드웨어에 맞는 양자화 레벨을 자동 선택한다.

    사용자 오버라이드: VIBEVOICE_QUANTIZATION 환경변수
      - "none" / "bf16"  : 양자화 없음 (bf16/fp16, ~14GB)
      - "8bit"           : 8-bit 양자화 (~7GB)  — CUDA 전용
      - "4bit"           : 4-bit NF4 양자화 (~4GB) — CUDA 전용
      - "auto"           : 하드웨어 기준 자동 (기본)

    자동 기준:
      - Apple Silicon (MPS) 통합 메모리 < 18GB → "skip" (VibeVoice 불가)
      - Apple Silicon (MPS) 통합 메모리 ≥ 18GB → "none" (fp16, bitsandbytes 미지원)
      - CPU → "none" (CPU 추론 자체가 비권장)
      - CUDA VRAM ≥ 80GB → "none" (bf16)
      - CUDA VRAM ≥ 48GB → "8bit"
      - CUDA 기타 → "4bit"

    Returns:
      "none", "4bit", "8bit", 또는 "skip" (VibeVoice 사용 불가)
    """
    user = os.environ.get("VIBEVOICE_QUANTIZATION", "auto").lower().strip()
    if user in ("none", "bf16"):
        return "none"
    if user in ("4bit", "4"):
        return "4bit"
    if user in ("8bit", "8"):
        return "8bit"
    if user != "auto":
        return "4bit"

    device = _detect_device()

    if device == "mps":
        # Apple Silicon — 통합 메모리 크기로 판단
        mem_gb = _get_system_memory_gb()
        if mem_gb < _MPS_MIN_MEMORY_GB:
            return "skip"  # fp16 7B (~14GB) + OS (~4GB) = 최소 18GB 필요
        return "none"  # fp16 (bitsandbytes 미지원)

    if device == "cpu":
        return "none"

    # CUDA: VRAM 감지
    try:
        import torch
        vram_gb = torch.cuda.get_device_properties(0).total_mem / (1024 ** 3)
        if vram_gb >= 80:
            return "none"
        if vram_gb >= 48:
            return "8bit"
    except Exception:  # noqa: BLE001
        pass
    return "4bit"


def _load_vibevoice():
    """VibeVoice 모델 + 프로세서를 lazy-load 후 캐시."""
    if _VIBEVOICE_SINGLETON.get("ready"):
        return _VIBEVOICE_SINGLETON["model"], _VIBEVOICE_SINGLETON["processor"], _VIBEVOICE_SINGLETON["device"]

    import torch
    from vibevoice.modular.modeling_vibevoice_asr import (  # type: ignore
        VibeVoiceASRForConditionalGeneration,
    )
    from vibevoice.processor.vibevoice_asr_processor import (  # type: ignore
        VibeVoiceASRProcessor,
    )

    model_id = os.environ.get("VIBEVOICE_MODEL_ID", "microsoft/VibeVoice-ASR")
    device = _detect_device()
    quant = _select_quantization()

    if quant == "skip":
        raise RuntimeError(
            f"Apple Silicon 통합 메모리({_get_system_memory_gb():.0f}GB)가 "
            f"VibeVoice 7B 실행에 부족합니다 (최소 {_MPS_MIN_MEMORY_GB:.0f}GB 필요).\n"
            "STT 엔진을 'assemblyai' 로 변경해주세요."
        )

    # 디바이스별 attention 구현 선택
    if device == "cuda":
        try:
            import flash_attn  # noqa: F401
            attn_impl = "flash_attention_2"
        except ImportError:
            attn_impl = "sdpa"
    else:
        # MPS / CPU → flash_attention 미지원
        attn_impl = "sdpa"

    # MPS/CPU 에서 양자화 강제 요청이 들어오면 경고 후 none 으로 폴백
    if quant in ("4bit", "8bit") and device != "cuda":
        quant = "none"  # bitsandbytes 는 CUDA 전용

    # VibeVoice + Transformers + PyTorch + bitsandbytes 가 내는 무해한 경고 억제.
    # warnings.warn() 뿐 아니라 transformers logging 도 일시적으로 ERROR 로 올린다.
    import logging as _logging
    _prev_tf_level = _logging.getLogger("transformers").level
    _prev_bnb_level = _logging.getLogger("bitsandbytes").level
    _logging.getLogger("transformers").setLevel(_logging.ERROR)
    _logging.getLogger("bitsandbytes").setLevel(_logging.ERROR)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")  # 모든 경고 억제 (모델 로딩 구간 한정)

        processor = VibeVoiceASRProcessor.from_pretrained(
            model_id,
            language_model_pretrained_name="Qwen/Qwen2.5-7B",
        )

        # 양자화 레벨에 따라 로딩 방식 분기
        load_kwargs: dict = {
            "attn_implementation": attn_impl,
            "trust_remote_code": True,
        }

        if quant == "4bit":
            from transformers import BitsAndBytesConfig  # type: ignore

            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            load_kwargs["device_map"] = "auto"
            _log_quant = "4-bit NF4 (~4GB)"
        elif quant == "8bit":
            from transformers import BitsAndBytesConfig  # type: ignore

            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_8bit=True,
            )
            load_kwargs["device_map"] = "auto"
            _log_quant = "8-bit (~7GB)"
        else:
            if device == "cuda":
                load_kwargs["dtype"] = torch.bfloat16
                _log_quant = f"bf16 (~14GB, {device})"
            elif device == "mps":
                load_kwargs["dtype"] = torch.float16
                _log_quant = f"fp16 (~14GB, Apple Silicon MPS)"
            else:
                load_kwargs["dtype"] = torch.float32
                _log_quant = f"fp32 (~28GB, CPU — 매우 느림)"

        model = VibeVoiceASRForConditionalGeneration.from_pretrained(
            model_id, **load_kwargs
        )

        # device_map="auto" 를 쓰지 않은 경우 수동 이동
        if "device_map" not in load_kwargs:
            model = model.to(device)

        model.eval()

    # 로깅 레벨 복원
    _logging.getLogger("transformers").setLevel(_prev_tf_level)
    _logging.getLogger("bitsandbytes").setLevel(_prev_bnb_level)

    _VIBEVOICE_SINGLETON.update(
        {"model": model, "processor": processor, "device": device,
         "ready": True, "quant": quant, "quant_label": _log_quant}
    )

    _VIBEVOICE_SINGLETON.update(
        {"model": model, "processor": processor, "device": device, "ready": True}
    )
    return model, processor, device


def _transcribe_vibevoice(
    audio_path: str, log: ProgressFn, hotwords: List[str],
    stop_event: Optional[object] = None,
) -> Transcript:
    """VibeVoice-ASR 로 전사. CUDA OOM 발생 시 토큰 수를 줄여 재시도."""
    import torch

    log("📦 VibeVoice 모델 로딩 중 (최초 1회는 수 GB 다운로드 필요)…")
    model, processor, device = _load_vibevoice()
    quant_label = _VIBEVOICE_SINGLETON.get("quant_label", "unknown")
    log(f"✅ 모델 로딩 완료 (device={device}, {quant_label})")

    # 추론 전 GPU 캐시 정리 — 이전 실행 잔여 메모리 반환
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    log("🎧 오디오 인코딩 중…")
    context_info = _build_context_info(hotwords)
    if context_info:
        log(f"🧠 도메인 핫워드 {len(hotwords)} 개를 컨텍스트로 주입합니다.")

    inputs = processor(
        audio=[audio_path],
        sampling_rate=None,
        return_tensors="pt",
        padding=True,
        add_generation_prompt=True,
        context_info=context_info,
    )
    inputs = {
        k: (v.to(device) if isinstance(v, torch.Tensor) else v)
        for k, v in inputs.items()
    }

    # OOM 방어: 처음 32768 토큰으로 시도 → 실패 시 16384 → 8192 순으로 축소 재시도.
    # 토큰 수를 줄이면 긴 영상의 후반부가 잘릴 수 있지만 전체 크래시보다 낫다.
    token_attempts = [32768, 16384, 8192]
    raw_text = ""
    for attempt_idx, max_tokens in enumerate(token_attempts):
        try:
            if attempt_idx > 0:
                log(f"🔄 max_new_tokens={max_tokens} 으로 재시도합니다…")
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            log(f"VibeVoice 추론 중 (max_tokens={max_tokens})...")

            # StoppingCriteria — 중지 버튼이 눌리면 매 토큰 생성마다 체크해 즉시 중단
            generate_kwargs: dict = {
                "max_new_tokens": max_tokens,
                "do_sample": False,
                "num_beams": 1,
                "pad_token_id": processor.pad_id,
                "eos_token_id": processor.tokenizer.eos_token_id,
            }
            if stop_event is not None:
                from transformers import StoppingCriteria, StoppingCriteriaList  # type: ignore

                class _StopOnEvent(StoppingCriteria):
                    def __init__(self, event):
                        self._event = event
                    def __call__(self, input_ids, scores, **kw):
                        return self._event.is_set()

                generate_kwargs["stopping_criteria"] = StoppingCriteriaList(
                    [_StopOnEvent(stop_event)]
                )

            with torch.no_grad():
                output_ids = model.generate(**inputs, **generate_kwargs)

            # 중지 요청으로 조기 종료된 경우
            if stop_event is not None and stop_event.is_set():
                log("[Stop] 추론이 중지되었습니다. GPU 메모리를 해제합니다.")
                del inputs, output_ids
                _unload_vibevoice()
                raise RuntimeError("사용자가 작업 중지를 요청했습니다.")

            input_length = inputs["input_ids"].shape[1]
            generated = output_ids[0, input_length:]
            eos_pos = (generated == processor.tokenizer.eos_token_id).nonzero(as_tuple=True)[0]
            if len(eos_pos) > 0:
                generated = generated[: eos_pos[0] + 1]
            raw_text = processor.decode(generated, skip_special_tokens=True)

            # 성공 시 GPU 메모리 반환
            del output_ids, generated
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            break  # 성공 — 루프 탈출

        except RuntimeError as exc:
            # CUDA OOM 인지 확인
            if "out of memory" not in str(exc).lower():
                raise  # OOM 이 아닌 다른 RuntimeError 는 즉시 전파
            # OOM 발생 — 텐서 정리 후 다음 시도
            log(f"⚠️ CUDA OOM 발생 (max_tokens={max_tokens})")
            # output_ids 가 할당되기 전 실패할 수 있어 safe delete
            for var_name in ("output_ids", "generated"):
                if var_name in dir():
                    try:
                        exec(f"del {var_name}")  # noqa: S102
                    except Exception:  # noqa: BLE001
                        pass
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            if attempt_idx == len(token_attempts) - 1:
                # 모든 시도 실패 — 모델을 GPU 에서 완전히 내려 메모리 반환
                log("🧹 GPU 메모리 해제를 위해 VibeVoice 모델을 언로드합니다…")
                del inputs
                _unload_vibevoice()
                raise RuntimeError(
                    f"CUDA 메모리 부족: GPU VRAM({_get_gpu_info()})으로는 이 영상을 "
                    "VibeVoice 로 처리할 수 없습니다.\n\n"
                    "해결 방법:\n"
                    "  1) STT 엔진을 'auto' 또는 'assemblyai' 로 변경\n"
                    "  2) 더 짧은 영상으로 시도\n"
                    "  3) 다른 GPU 프로세스를 종료해 VRAM 확보\n\n"
                    "GPU 메모리는 이미 해제되었습니다."
                ) from exc

    # inputs 정리
    del inputs
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    log("🧩 결과 파싱 중…")
    try:
        raw_segments = processor.post_process_transcription(raw_text)
    except Exception:  # noqa: BLE001
        raw_segments = []

    segments = _normalize_vibevoice_segments(raw_segments, raw_text)
    log(f"✅ VibeVoice 전사 완료 — {len(segments)} 세그먼트")

    return Transcript(
        segments=segments,
        engine="vibevoice",
        raw={"text": raw_text, "segments": raw_segments},
    )


def _normalize_vibevoice_segments(raw_segments, raw_text: str) -> List[Segment]:
    """
    VibeVoice 의 segment dict (start_time, end_time, speaker_id, text) 를
    공통 Segment 로 변환. 파싱 실패 시 raw_text 전체를 한 세그먼트로 폴백.
    """
    segments: List[Segment] = []
    for seg in raw_segments or []:
        try:
            segments.append(
                Segment(
                    speaker=str(seg.get("speaker_id", "1")),
                    start=_to_seconds(seg.get("start_time", 0)),
                    end=_to_seconds(seg.get("end_time", 0)),
                    text=str(seg.get("text", "")).strip(),
                )
            )
        except Exception:  # noqa: BLE001
            continue

    if not segments and raw_text.strip():
        segments.append(Segment(speaker="1", start=0.0, end=0.0, text=raw_text.strip()))
    return segments


def _get_gpu_info() -> str:
    """현재 GPU/디바이스 정보를 사람이 읽을 수 있는 문자열로 반환."""
    device = _detect_device()
    try:
        import torch
        if device == "cuda" and torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            total = torch.cuda.get_device_properties(0).total_mem / (1024 ** 3)
            return f"{name}, {total:.1f} GB VRAM"
        if device == "mps":
            mem = _get_system_memory_gb()
            return f"Apple Silicon MPS, {mem:.0f} GB 통합 메모리"
    except Exception:  # noqa: BLE001
        pass
    return "정보 없음"


def _build_context_info(hotwords: Optional[List[str]]) -> Optional[str]:
    """
    핫워드 리스트 → VibeVoice processor 의 `context_info` 문자열.

    프로세서는 비어있지 않은 문자열을 user prompt 의 "extra info" 위치에 끼워
    넣어 디코딩 시 도메인 단어 편향을 만든다. None/빈 리스트면 None 반환.
    """
    if not hotwords:
        return None
    cleaned = [w.strip() for w in hotwords if w and w.strip()]
    if not cleaned:
        return None
    return "Domain hotwords (proper nouns, technical terms): " + ", ".join(cleaned)


def _to_seconds(value) -> float:
    """초(float) 또는 'HH:MM:SS' / 'MM:SS' / 'MM:SS.mmm' 문자열 → float."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return 0.0
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return float(s)
    parts = s.split(":")
    try:
        parts = [float(p) for p in parts]
    except ValueError:
        return 0.0
    if len(parts) == 3:
        h, m, sec = parts
        return h * 3600 + m * 60 + sec
    if len(parts) == 2:
        m, sec = parts
        return m * 60 + sec
    return parts[0]


# =============================================================================
# AssemblyAI 폴백 엔진
# =============================================================================
def _transcribe_assemblyai(audio_path: str, log: ProgressFn) -> Transcript:
    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "AssemblyAI 폴백을 쓰려면 .env 에 ASSEMBLYAI_API_KEY 를 설정해야 합니다."
        )

    import assemblyai as aai  # type: ignore

    aai.settings.api_key = api_key
    config = aai.TranscriptionConfig(speaker_labels=True)

    log("☁️ AssemblyAI 에 업로드 후 화자 분리 전사 중…")
    transcriber = aai.Transcriber()
    result = transcriber.transcribe(audio_path, config=config)

    if result.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"AssemblyAI 에러: {result.error}")

    segments: List[Segment] = []
    for utt in result.utterances or []:
        segments.append(
            Segment(
                speaker=str(utt.speaker),
                start=float(utt.start) / 1000.0,  # ms → s
                end=float(utt.end) / 1000.0,
                text=(utt.text or "").strip(),
            )
        )

    log(f"✅ AssemblyAI 전사 완료 — {len(segments)} 세그먼트")
    return Transcript(
        segments=segments,
        engine="assemblyai",
        raw={"id": result.id, "status": str(result.status)},
    )
