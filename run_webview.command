#!/bin/bash
# GuruNote — React/PyWebView UI launcher (macOS, v1.0+ 권장 진입점).
#
# 더블 클릭 또는 터미널 실행으로 GuruNote 를 띄웁니다.
# stdout/stderr 는 콘솔에 그대로 남아 pywebview + 파이프라인 디버깅이 쉽도록
# 의도적으로 ~/.gurunote/gui.log 리다이렉트를 사용하지 않습니다.
# (CustomTkinter 백그라운드 진입점이 필요하면 run_gui.command 를 사용)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Prefer project venv if present (matches setup.sh layout).
if [ -x "./.venv/bin/python" ]; then
  PY="./.venv/bin/python"
elif [ -x "./venv/bin/python" ]; then
  PY="./venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi

if [ -z "$PY" ]; then
  osascript -e 'display dialog "Python not found. See README for setup." buttons {"OK"} default button 1 with icon stop' 2>/dev/null
  echo "Python not found. Run setup.sh first." >&2
  exit 1
fi

exec "$PY" app_webview.py "$@"
