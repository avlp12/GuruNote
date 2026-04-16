@echo off
:: GuruNote 웹 앱 실행 (Streamlit, Windows)
:: setup.bat 가 생성한 .venv 를 activate 없이 직접 사용.
cd /d "%~dp0"

if not exist ".venv\Scripts\streamlit.exe" (
    echo [ERROR] .venv\Scripts\streamlit.exe 를 찾을 수 없습니다. 먼저 setup.bat 를 실행하세요.
    exit /b 1
)

".venv\Scripts\streamlit.exe" run app.py %*
