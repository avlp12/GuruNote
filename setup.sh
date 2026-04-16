#!/bin/bash
echo ""
echo "================================================"
echo "    GuruNote 환경 설정"
echo "================================================"
echo ""

# 1. venv
if [ ! -f ".venv/bin/python" ]; then
    echo "[1/4] 가상환경 생성 중..."
    python3 -m venv .venv
else
    echo "[1/4] 가상환경 확인 OK"
fi

PIP=".venv/bin/pip"
PYTHON=".venv/bin/python"

# 2. 플랫폼 감지 → STT 엔진 선택
#    우선순위: NVIDIA GPU (CUDA WhisperX) > Apple Silicon (MLX Whisper) > CPU/AssemblyAI
echo ""
OS="$(uname -s)"
ARCH="$(uname -m)"
STT_PROFILE="cpu"

if command -v nvidia-smi &> /dev/null; then
    echo "[2/4] NVIDIA GPU 감지됨 — CUDA PyTorch + WhisperX 설치"
    $PIP install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --index-url https://download.pytorch.org/whl/cu128
    STT_PROFILE="gpu"
elif [ "$OS" = "Darwin" ] && [ "$ARCH" = "arm64" ]; then
    echo "[2/4] Apple Silicon 감지됨 — MLX Whisper 설치 (Metal/MPS GPU 가속)"
    STT_PROFILE="mac"
else
    echo "[2/4] GPU 미감지 — CPU 모드 (STT 는 AssemblyAI Cloud API 사용)"
fi

# 3. 공통 패키지 설치
echo ""
echo "[3/4] GuruNote 공통 패키지 설치 중..."
$PIP install -r requirements.txt

# 3-bis. 플랫폼별 STT 패키지 설치
if [ "$STT_PROFILE" = "gpu" ]; then
    echo ""
    echo "[3/4+] WhisperX (CUDA) 설치 중..."
    $PIP install -r requirements-gpu.txt
elif [ "$STT_PROFILE" = "mac" ]; then
    echo ""
    echo "[3/4+] MLX Whisper (Apple Silicon) 설치 중..."
    $PIP install -r requirements-mac.txt
fi

# 4. 검증
echo ""
echo "[4/4] 환경 검증..."
$PYTHON -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}, MPS: {getattr(torch.backends, \"mps\", None) and torch.backends.mps.is_available()}')"
if [ "$STT_PROFILE" = "gpu" ]; then
    $PYTHON -c "import whisperx; print('WhisperX OK')" 2>/dev/null || echo "WhisperX: 설치 필요"
elif [ "$STT_PROFILE" = "mac" ]; then
    $PYTHON -c "import mlx_whisper; print('mlx-whisper OK')" 2>/dev/null || echo "mlx-whisper: 설치 필요"
    $PYTHON -c "import pyannote.audio; print('pyannote.audio OK')" 2>/dev/null || echo "pyannote.audio: 설치 필요"
fi

echo ""
echo "================================================"
echo "    설정 완료! 실행: .venv/bin/python gui.py"
echo "================================================"
