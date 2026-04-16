#!/bin/bash
# GuruNote 웹 앱 실행 (Streamlit, macOS / Linux)
# setup.sh 가 생성한 .venv 를 activate 없이 직접 사용.
set -e
cd "$(dirname "$0")"

if [ ! -f ".venv/bin/streamlit" ]; then
    echo "❌ .venv/bin/streamlit 을 찾을 수 없습니다. 먼저 'bash setup.sh' 를 실행하세요."
    exit 1
fi

exec .venv/bin/streamlit run app.py "$@"
