"""
Apple Silicon (M1/M2/M3/M4/M5) GPU 로컬 STT 엔진.

`mlx-whisper` (Apple MLX 프레임워크) 로 Whisper 추론을 수행하고,
`pyannote.audio` 화자 분리 파이프라인을 MPS(Metal Performance Shaders)
디바이스에서 실행해 화자 라벨을 부여한다.

WhisperX(CUDA) 와 동일한 `gurunote.types.Transcript` 형태로 결과를 반환하므로
LLM/요약 단계는 어떤 엔진이 사용됐는지 신경 쓰지 않아도 된다.

기본 모델:
    - Whisper:    `mlx-community/whisper-large-v3-mlx`
                  (`MLX_WHISPER_MODEL` 환경변수로 오버라이드)
    - Diarization: `pyannote/speaker-diarization-3.1`
                  (HUGGINGFACE_TOKEN 필요, 모델 사용 동의 필요)
"""

from __future__ import annotations

import os
import platform
import warnings
from typing import Callable, Dict, List, Optional, Tuple

from gurunote.types import Segment, Transcript

ProgressFn = Callable[[str], None]

DEFAULT_MLX_MODEL = "mlx-community/whisper-large-v3-mlx"
DEFAULT_DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"


# =============================================================================
# 환경 검사 헬퍼
# =============================================================================
def is_apple_silicon() -> bool:
    """macOS arm64 (M1/M2/M3/M4/M5) 여부."""
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def is_mlx_whisper_available() -> bool:
    try:
        import mlx_whisper  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


def is_mlx_ready() -> bool:
    """현재 환경에서 MLX 엔진이 실제로 동작 가능한지 (플랫폼 + 패키지)."""
    return is_apple_silicon() and is_mlx_whisper_available()


def _check_mps_ready() -> bool:
    """torch.backends.mps 사용 가능 여부 (pyannote diarization 가속용)."""
    try:
        import torch
        return bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())
    except Exception:  # noqa: BLE001
        return False


# =============================================================================
# 화자 라벨 정규화 + 할당
# =============================================================================
def _normalize_speaker_label(raw: str) -> str:
    """SPEAKER_00 → A, SPEAKER_01 → B …"""
    if raw and raw.startswith("SPEAKER_"):
        try:
            idx = int(raw.split("_")[-1])
            return chr(ord("A") + idx)
        except (ValueError, IndexError):
            return raw
    return raw or "A"


def _assign_speaker_by_overlap(
    seg_start: float,
    seg_end: float,
    turns: List[Tuple[float, float, str]],
) -> str:
    """
    Whisper 세그먼트(seg_start, seg_end) 와 가장 많이 겹치는 diarization 화자를 반환.

    Args:
        turns: [(turn_start, turn_end, speaker_label)] — pyannote 결과
    """
    if not turns:
        return "A"

    overlap_by_speaker: Dict[str, float] = {}
    for t_start, t_end, t_speaker in turns:
        overlap = min(seg_end, t_end) - max(seg_start, t_start)
        if overlap > 0:
            overlap_by_speaker[t_speaker] = overlap_by_speaker.get(t_speaker, 0.0) + overlap

    if not overlap_by_speaker:
        return "A"

    best = max(overlap_by_speaker.items(), key=lambda kv: kv[1])[0]
    return _normalize_speaker_label(best)


# =============================================================================
# 메인 엔트리
# =============================================================================
def transcribe_mlx(
    audio_path: str,
    log: ProgressFn,
    hotwords: List[str],
) -> Transcript:
    """
    Apple Silicon GPU 로컬 STT 실행.

    Returns:
        Transcript (engine="mlx")
    """
    if not is_apple_silicon():
        raise RuntimeError(
            "MLX 엔진은 macOS Apple Silicon (M1/M2/M3/M4/M5) 에서만 동작합니다."
        )
    if not is_mlx_whisper_available():
        raise RuntimeError(
            "mlx-whisper 가 설치되지 않았습니다.\n"
            "  pip install -r requirements-mac.txt\n"
            "  (또는: pip install mlx-whisper pyannote.audio onnxruntime)"
        )

    # pyannote / huggingface 의 무해한 경고 억제 (WhisperX 와 동일 패턴)
    warnings.filterwarnings("ignore", message=".*symlink.*")
    warnings.filterwarnings("ignore", message=".*hf_xet.*")
    warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")
    warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")

    import mlx_whisper  # type: ignore

    model_repo = os.environ.get("MLX_WHISPER_MODEL", DEFAULT_MLX_MODEL)
    initial_prompt = ", ".join(hotwords[:30]) if hotwords else None

    # 1. Whisper 전사 (MLX = Apple GPU/Neural Engine native)
    log(f"MLX Whisper 모델 로딩 ({model_repo})...")
    log("전사 중 (Apple GPU 가속, 단어 레벨 타임스탬프)...")
    transcribe_kwargs: dict = {
        "path_or_hf_repo": model_repo,
        "word_timestamps": True,
        "verbose": False,
    }
    if initial_prompt:
        transcribe_kwargs["initial_prompt"] = initial_prompt

    result = mlx_whisper.transcribe(audio_path, **transcribe_kwargs)
    raw_segments = result.get("segments", []) or []
    language = result.get("language", "en")
    log(f"전사 완료 — {len(raw_segments)} 세그먼트, 언어={language}")

    # 2. 화자 분리 (선택: HF 토큰 + 모델 동의 필요)
    #    토큰 이름 우선순위: HF_TOKEN > HUGGINGFACE_TOKEN > HUGGING_FACE_HUB_TOKEN
    #    > HUGGINGFACEHUB_API_TOKEN (gurunote.settings.load_hf_token 참고)
    from gurunote.settings import load_hf_token  # noqa: PLC0415
    diarization_turns: List[Tuple[float, float, str]] = []
    hf_token = load_hf_token()
    if hf_token:
        try:
            diarization_turns = _diarize_with_pyannote(audio_path, hf_token, log)
        except Exception as exc:  # noqa: BLE001
            err_msg = str(exc)
            if "401" in err_msg or "gated" in err_msg.lower() or "restricted" in err_msg.lower():
                log(
                    "화자 분리 실패: pyannote 모델 접근 권한이 없습니다.\n"
                    "  아래 페이지에서 'Agree and access repository' 를 클릭하세요:\n"
                    "  https://huggingface.co/pyannote/speaker-diarization-3.1\n"
                    "  화자 분리 없이 단일 화자(A) 로 진행합니다."
                )
            elif "AudioMetaData" in err_msg:
                # torchaudio 2.8+ 에서 `AudioMetaData` 가 제거되어 pyannote.audio 3.x
                # 와 호환 불가. 4.0+ 는 torchcodec 로 마이그레이션해 해결.
                log(
                    "화자 분리 실패: pyannote.audio 3.x 와 최신 torchaudio 가\n"
                    "  호환되지 않습니다 ('AudioMetaData' 제거됨).\n"
                    "  pyannote.audio 4.0+ 로 업그레이드하세요:\n"
                    "    .venv/bin/pip install --upgrade 'pyannote.audio>=4.0'\n"
                    "  단일 화자(A) 로 진행합니다."
                )
            else:
                log(f"화자 분리 실패: {exc}\n  단일 화자(A) 로 진행합니다.")
    else:
        log(
            "HF_TOKEN 미설정 — 화자 분리를 건너뜁니다.\n"
            "  화자 분리를 원하면 Settings 에서 HF_TOKEN 을 설정하고,\n"
            "  https://huggingface.co/pyannote/speaker-diarization-3.1\n"
            "  에서 모델 사용에 동의하세요."
        )

    # 3. Segment 정규화 (화자 할당)
    segments: List[Segment] = []
    for seg in raw_segments:
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", 0.0))
        text = (seg.get("text") or "").strip()

        if diarization_turns:
            speaker = _assign_speaker_by_overlap(start, end, diarization_turns)
        else:
            speaker = "A"

        segments.append(Segment(speaker=speaker, start=start, end=end, text=text))

    speaker_count = len({s.speaker for s in segments})
    log(f"MLX 전사 완료 — {len(segments)} 세그먼트, {speaker_count} 화자")

    return Transcript(
        segments=segments,
        engine="mlx",
        language=language,
        raw={"language": language, "model": model_repo},
    )


# =============================================================================
# pyannote diarization (MPS 가속)
# =============================================================================
def _diarize_with_pyannote(
    audio_path: str,
    hf_token: str,
    log: ProgressFn,
) -> List[Tuple[float, float, str]]:
    """
    pyannote.audio 화자 분리 → [(start, end, speaker_label)] 리스트.
    MPS 디바이스에서 실행 (가능한 경우), 일부 op 는 자동 CPU 폴백.
    """
    log("화자 분리 중 (pyannote, MPS 가속)...")

    from pyannote.audio import Pipeline  # type: ignore
    import torch

    diar_model = os.environ.get("PYANNOTE_DIARIZATION_MODEL", DEFAULT_DIARIZATION_MODEL)

    # pyannote.audio 3.x 는 token=, 그 이전(또는 4.x) 은 use_auth_token= 를 받을 수 있어
    # WhisperX 분기(stt.py)와 동일한 try/except TypeError 폴백을 사용한다.
    try:
        pipeline = Pipeline.from_pretrained(diar_model, token=hf_token)
    except TypeError:
        pipeline = Pipeline.from_pretrained(diar_model, use_auth_token=hf_token)

    if pipeline is None:
        raise RuntimeError(
            f"pyannote 파이프라인 로드 실패 ({diar_model}). "
            "HuggingFace 토큰과 모델 사용 동의를 확인하세요."
        )

    if _check_mps_ready():
        try:
            pipeline.to(torch.device("mps"))
        except Exception as exc:  # noqa: BLE001
            log(f"  MPS 디바이스 이동 실패 ({exc}) — CPU 로 진행")

    diarization = pipeline(audio_path)

    turns: List[Tuple[float, float, str]] = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        turns.append((float(turn.start), float(turn.end), str(speaker)))

    log(f"화자 분리 완료 — {len(turns)} 발화 구간")
    return turns
