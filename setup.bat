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

:: venv 의 pip/python 사용 (시스템 Python 이 아닌 venv 안의 것)
set PIP=.venv\Scripts\pip.exe
set PYTHON=.venv\Scripts\python.exe

:: 2. NVIDIA GPU 감지
echo.
nvidia-smi >nul 2>&1
if %errorlevel%==0 (
    echo [2/4] NVIDIA GPU 감지됨 — CUDA PyTorch 를 설치합니다.
    echo       (이미 설치돼 있으면 건너뜁니다)
    %PIP% install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
) else (
    echo [2/4] NVIDIA GPU 미감지 — CPU PyTorch 로 진행합니다.
    echo       (STT 는 AssemblyAI Cloud API 를 사용합니다)
)

:: 3. 패키지 설치
echo.
echo [3/4] GuruNote 패키지 설치 중...
%PIP% install -r requirements.txt

:: 4. 검증
echo.
echo [4/4] 환경 검증 중...
%PYTHON% -c "import torch; cuda=torch.cuda.is_available(); print(f'PyTorch {torch.__version__}, CUDA: {cuda}')"
%PYTHON% -c "import whisperx; print('WhisperX OK')" 2>nul || echo WhisperX: 설치 필요 (pip install whisperx)
%PYTHON% -c "import customtkinter; print(f'CustomTkinter {customtkinter.__version__}')"

echo.
echo ================================================
echo     설정 완료! 다음 명령으로 실행하세요:
echo       .venv\Scripts\python.exe gui.py
echo ================================================
echo.
pause
