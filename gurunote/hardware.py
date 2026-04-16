"""
하드웨어 자동 감지 + 권장 설정 프리셋.

사용자가 Settings 다이얼로그에서 플랫폼/메모리 크기별 사전 정의된 값을 드롭다운
으로 고를 수 있게 프리셋을 제공한다. 개별 필드는 여전히 수동 수정 가능.

감지 항목:
  - NVIDIA GPU VRAM 크기 (GB) — torch.cuda 사용
  - Apple Silicon Unified Memory 크기 (GB) — sysctl hw.memsize

감지는 best-effort 이며 실패 시 None 을 반환. 감지 실패 ≠ 하드웨어 부재.
"""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from typing import Optional


# =============================================================================
# 프리셋 스키마
# =============================================================================
@dataclass(frozen=True)
class HardwareProfile:
    """Settings 다이얼로그의 드롭다운 1개 항목."""

    key: str                        # dropdown 내부 키 (예: "nvidia-24gb")
    display_name: str               # UI 표시 텍스트
    # STT (WhisperX — NVIDIA CUDA 경로에서 사용)
    whisperx_model: str
    whisperx_batch: int
    # STT (MLX Whisper — Apple Silicon 경로에서 사용)
    mlx_model: str
    # LLM 공통 권장값 (하드웨어 무관하게 합리적 기본값이지만 한번에 채우기 편의)
    llm_temperature: float = 0.2
    translation_max_tokens: int = 8192
    summary_max_tokens: int = 4096


# =============================================================================
# 프리셋 카탈로그
# =============================================================================
# 순서는 Settings 드롭다운 표시 순서. 상단일수록 강력한 하드웨어.
PRESETS: dict[str, HardwareProfile] = {
    # --- NVIDIA (Linux/Windows) ---
    "nvidia-24gb": HardwareProfile(
        key="nvidia-24gb",
        display_name="NVIDIA 24GB+ (RTX 4090 / A100 / H100)",
        whisperx_model="distil-large-v3",
        whisperx_batch=32,
        mlx_model="mlx-community/whisper-large-v3-mlx",
    ),
    "nvidia-12gb": HardwareProfile(
        key="nvidia-12gb",
        display_name="NVIDIA 12GB (RTX 3080 / 4070 Ti)",
        whisperx_model="distil-large-v3",
        whisperx_batch=16,
        mlx_model="mlx-community/whisper-large-v3-mlx",
    ),
    "nvidia-8gb": HardwareProfile(
        key="nvidia-8gb",
        display_name="NVIDIA 8GB (RTX 3060 Ti / 4060)",
        whisperx_model="distil-large-v3",
        whisperx_batch=8,
        mlx_model="mlx-community/whisper-large-v3-mlx",
    ),
    "nvidia-6gb": HardwareProfile(
        key="nvidia-6gb",
        display_name="NVIDIA 6GB (RTX 2060 / 3050)",
        whisperx_model="distil-large-v3",
        whisperx_batch=4,
        mlx_model="mlx-community/whisper-large-v3-mlx",
    ),
    # --- Apple Silicon (macOS arm64) ---
    "apple-ultra": HardwareProfile(
        key="apple-ultra",
        display_name="Apple Silicon Ultra (M1~M3 Ultra, 64GB+ Unified Memory)",
        whisperx_model="distil-large-v3",
        whisperx_batch=16,
        mlx_model="mlx-community/whisper-large-v3-mlx",
    ),
    "apple-pro-max": HardwareProfile(
        key="apple-pro-max",
        display_name="Apple Silicon Pro/Max (16~64GB Unified Memory)",
        whisperx_model="distil-large-v3",
        whisperx_batch=16,
        mlx_model="mlx-community/whisper-large-v3-turbo",
    ),
    "apple-base": HardwareProfile(
        key="apple-base",
        display_name="Apple Silicon base (8~16GB Unified Memory)",
        whisperx_model="distil-large-v3",
        whisperx_batch=16,
        mlx_model="mlx-community/whisper-small-mlx",
    ),
    # --- 클라우드 전용 ---
    "cloud-only": HardwareProfile(
        key="cloud-only",
        display_name="Cloud only (AssemblyAI, 로컬 GPU 없음)",
        whisperx_model="distil-large-v3",  # 쓰이지 않지만 기본값 유지
        whisperx_batch=16,
        mlx_model="mlx-community/whisper-large-v3-mlx",
    ),
}

CUSTOM_KEY = "custom"
AUTO_KEY = "auto"


def dropdown_options() -> list[str]:
    """Settings 드롭다운의 label 목록 (순서 유지)."""
    labels: list[str] = ["자동 감지 (권장)"]
    labels += [p.display_name for p in PRESETS.values()]
    labels.append("직접 입력 (custom)")
    return labels


def label_to_key(label: str) -> str:
    """드롭다운 label → preset key.  `AUTO_KEY` / `CUSTOM_KEY` / PRESETS 의 key."""
    if label.startswith("자동 감지"):
        return AUTO_KEY
    if label.startswith("직접 입력"):
        return CUSTOM_KEY
    for key, profile in PRESETS.items():
        if label == profile.display_name:
            return key
    return CUSTOM_KEY


def key_to_label(key: str) -> str:
    """preset key → 드롭다운 label."""
    if key == AUTO_KEY:
        return "자동 감지 (권장)"
    if key == CUSTOM_KEY:
        return "직접 입력 (custom)"
    profile = PRESETS.get(key)
    return profile.display_name if profile else "직접 입력 (custom)"


# =============================================================================
# 감지 로직
# =============================================================================
def detect_nvidia_vram_gb() -> Optional[int]:
    """
    NVIDIA GPU VRAM 크기 (GB). 감지 불가 시 None.

    torch.cuda 를 사용하므로 CUDA PyTorch 가 설치된 환경에서만 동작.
    """
    try:
        import torch  # noqa: F401

        if not torch.cuda.is_available():
            return None
        props = torch.cuda.get_device_properties(0)
        # 소수점 내림 후 반올림: 8589934592 bytes ≈ 8GB
        return round(props.total_memory / (1024 ** 3))
    except Exception:  # noqa: BLE001
        return None


def detect_apple_silicon_memory_gb() -> Optional[int]:
    """
    Apple Silicon Mac 의 Unified Memory 크기 (GB). 감지 불가 시 None.

    `sysctl hw.memsize` 를 subprocess 로 호출.
    """
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        return None
    try:
        result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        bytes_val = int(result.stdout.strip())
        return round(bytes_val / (1024 ** 3))
    except Exception:  # noqa: BLE001
        return None


def detect_recommended_preset() -> str:
    """현재 하드웨어에 맞는 프리셋 key 를 추천. 감지 실패 시 'cloud-only'."""
    vram = detect_nvidia_vram_gb()
    if vram is not None:
        if vram >= 24:
            return "nvidia-24gb"
        if vram >= 12:
            return "nvidia-12gb"
        if vram >= 8:
            return "nvidia-8gb"
        return "nvidia-6gb"

    ram = detect_apple_silicon_memory_gb()
    if ram is not None:
        if ram >= 64:
            return "apple-ultra"
        if ram >= 16:
            return "apple-pro-max"
        return "apple-base"

    return "cloud-only"


def detect_description() -> str:
    """UI 용 감지 결과 요약 문자열."""
    vram = detect_nvidia_vram_gb()
    if vram is not None:
        return f"NVIDIA GPU 감지됨 (VRAM ~{vram}GB)"
    ram = detect_apple_silicon_memory_gb()
    if ram is not None:
        return f"Apple Silicon 감지됨 (Unified Memory ~{ram}GB)"
    return "로컬 GPU 미감지 (AssemblyAI Cloud STT 권장)"
