#!/bin/bash
# GuruNote GUI launcher for macOS.
#
# Double-click this file (or run from Terminal) to launch GuruNote in the
# background without a visible Terminal window trailing along.
#
# All stdout/stderr from the pipeline (pyannote downloads, mlx-whisper tqdm,
# etc.) are captured in ~/.gurunote/gui.log — tail that file for diagnostics:
#
#   tail -f ~/.gurunote/gui.log
#
# If you launched this from Terminal.app via double-click, you can safely
# close the Terminal window after the app appears.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="$HOME/.gurunote"
LOG_FILE="$LOG_DIR/gui.log"
mkdir -p "$LOG_DIR"

# Prefer project venv if present (matches README quick-start).
if [ -x "./.venv/bin/python" ]; then
  PY="./.venv/bin/python"
elif [ -x "./venv/bin/python" ]; then
  PY="./venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi

if [ -z "$PY" ]; then
  osascript -e 'display dialog "Python not found. See README for setup." buttons {"OK"} default button 1 with icon stop'
  exit 1
fi

# Launch detached: nohup + disown so the Terminal window can close cleanly.
# stdin redirected from /dev/null to ensure no TTY attachment.
nohup "$PY" gui.py </dev/null >>"$LOG_FILE" 2>&1 &
disown

# Give AppKit a moment to create the window, then close the Terminal window
# we were launched from (if any). Silently ignore on non-Terminal launches.
sleep 1
osascript >/dev/null 2>&1 <<'APPLESCRIPT' || true
tell application "System Events"
  set termRunning to exists (processes where name is "Terminal")
end tell
if termRunning then
  tell application "Terminal"
    try
      close (every window whose name contains "run_gui.command")
    end try
  end tell
end if
APPLESCRIPT
