#!/bin/bash
# GuruNote 데스크톱 앱 실행 (macOS / Linux)
# setup.sh 가 생성한 .venv 를 activate 없이 직접 사용.
set -e
cd "$(dirname "$0")"

if [ ! -f ".venv/bin/python" ]; then
    echo "❌ .venv 를 찾을 수 없습니다. 먼저 'bash setup.sh' 를 실행하세요."
    exit 1
fi

exec .venv/bin/python gui.py "$@"
