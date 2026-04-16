@echo off
chcp 65001 >nul 2>&1
echo.
echo ================================================
echo     GuruNote 환경 설정
echo ================================================
echo.

:: 1. venv 확인/생성
if not exist ".venv\Scripts\python.exe" (
    echo [1/4] 가상환경 생성 중...
    python -m venv .venv
) else (
    echo [1/4] 가상환경 확인 OK
)

set PIP=.venv\Scripts\pip.exe
set PYTHON=.venv\Scripts\python.exe

:: 2. NVIDIA GPU 감지 → CUDA torch 를 먼저 설치
::    (whisperx 보다 먼저 깔아야 CPU torch 를 안 깜)
echo.
nvidia-smi >nul 2>&1
if %errorlevel%==0 (
    echo [2/4] NVIDIA GPU 감지됨 — CUDA PyTorch 설치 (whisperx 호환 2.8.0)
    %PIP% install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --index-url https://download.pytorch.org/whl/cu128
) else (
    echo [2/4] NVIDIA GPU 미감지 — CPU 모드 (STT 는 AssemblyAI 사용)
)

:: 3. 나머지 패키지 설치
::    whisperx 가 torch 를 의존성으로 갖지만, 이미 CUDA 버전이 설치돼 있으면
::    pip 가 "already satisfied" 로 건너뜀 → CPU 버전 안 깔림
echo.
echo [3/4] GuruNote 패키지 설치 중...
%PIP% install -r requirements.txt

:: 4. 검증
echo.
echo [4/4] 환경 검증...
%PYTHON% -c "import torch; cuda=torch.cuda.is_available(); v=torch.__version__; print(f'PyTorch {v}, CUDA: {cuda}')"
%PYTHON% -c "import whisperx; print('WhisperX OK')" 2>nul || echo WhisperX: 설치 필요
%PYTHON% -c "import customtkinter; print(f'CustomTkinter {customtkinter.__version__}')"

echo.
echo ================================================
echo     설정 완료!
echo     실행: .venv\Scripts\python.exe gui.py
echo ================================================
echo.
pause
