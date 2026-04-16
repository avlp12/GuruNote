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

# 2. GPU → CUDA torch 먼저 설치
echo ""
if command -v nvidia-smi &> /dev/null; then
    echo "[2/4] NVIDIA GPU 감지됨 — CUDA PyTorch 먼저 설치"
    $PIP install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
else
    echo "[2/4] NVIDIA GPU 미감지 — CPU 모드"
fi

# 3. 나머지 패키지 (torch 이미 있으면 스킵됨)
echo ""
echo "[3/4] GuruNote 패키지 설치 중..."
$PIP install -r requirements.txt

# 4. 검증
echo ""
echo "[4/4] 환경 검증..."
$PYTHON -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
$PYTHON -c "import whisperx; print('WhisperX OK')" 2>/dev/null || echo "WhisperX: 설치 필요"

echo ""
echo "================================================"
echo "    설정 완료! 실행: .venv/bin/python gui.py"
echo "================================================"
