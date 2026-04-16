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
set STT_PROFILE=cpu
nvidia-smi >nul 2>&1
if %errorlevel%==0 (
    echo [2/4] NVIDIA GPU 감지됨 — CUDA PyTorch 설치 (whisperx 호환 2.8.0)
    %PIP% install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --index-url https://download.pytorch.org/whl/cu128
    set STT_PROFILE=gpu
) else (
    echo [2/4] NVIDIA GPU 미감지 — CPU 모드 (STT 는 AssemblyAI 사용)
)

:: 3. 공통 패키지 설치
::    whisperx 등 STT 엔진은 플랫폼별로 분리 (requirements-gpu.txt / requirements-mac.txt).
echo.
echo [3/4] GuruNote 공통 패키지 설치 중...
%PIP% install -r requirements.txt

if "%STT_PROFILE%"=="gpu" (
    echo.
    echo [3/4+] WhisperX ^(CUDA^) 설치 중...
    %PIP% install -r requirements-gpu.txt
)

:: 4. 검증
echo.
echo [4/4] 환경 검증...
%PYTHON% -c "import torch; cuda=torch.cuda.is_available(); v=torch.__version__; print(f'PyTorch {v}, CUDA: {cuda}')"
if "%STT_PROFILE%"=="gpu" (
    %PYTHON% -c "import whisperx; print('WhisperX OK')" 2>nul || echo WhisperX: 설치 필요
)
%PYTHON% -c "import customtkinter; print(f'CustomTkinter {customtkinter.__version__}')"

echo.
echo ================================================
echo     설정 완료!
echo.
echo     실행 (권장 -- venv activate 불필요):
echo       run_desktop.bat        (데스크톱 앱)
echo       run_web.bat            (웹 앱 Streamlit)
echo.
echo     직접 실행:
echo       .venv\Scripts\python.exe gui.py
echo       .venv\Scripts\streamlit.exe run app.py
echo ================================================
echo.
pause
