"""
stdout / stderr 의 파일 디스크립터 레벨 리다이렉트.

`python gui.py` 로 직접 실행할 때 WeasyPrint / pyannote / mlx-whisper 등의
native 라이브러리가 C 레벨에서 stderr 에 출력하는 경고 / tqdm 진행률 바가
Terminal 창으로 쏟아져 나와 macOS 가 Terminal 을 포그라운드로 가져오는
문제를 해결한다.

접근:
  - Python 의 `sys.stdout` / `sys.stderr` 를 재할당하는 것만으로는 부족.
    cffi 로 래핑된 C 라이브러리가 `fprintf(stderr, ...)` 로 직접 FD 2 에
    쓰면 우회된다.
  - `os.dup2` 로 **FD 1, 2 자체를 로그 파일로 redirect** 해야 완전 차단.
  - Tkinter 메인 루프 시작 전(`gui.py` 모듈 로드 직후)에 호출.

기존 stdout/stderr 이 TTY 였다면 (= 사용자가 Terminal 에서 실행)
이 리다이렉트가 적용되지만, 만약 이미 `run_gui.command` 로 실행돼
파일로 리다이렉트된 상태라면 중복 처리는 무해하다.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

_LOG_DIR = Path.home() / ".gurunote"
_LOG_PATH = _LOG_DIR / "gui.log"

_done = False


def redirect_to_log() -> None:
    """FD 1/2 를 `~/.gurunote/gui.log` 로 리다이렉트. 멱등.

    사용자 지정 환경변수로 우회 가능:
      GURUNOTE_NO_REDIRECT=1  → 터미널 출력 유지 (디버깅용)
    """
    global _done
    if _done:
        return
    if os.environ.get("GURUNOTE_NO_REDIRECT"):
        return

    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        # append 모드, line-buffered
        fp = open(_LOG_PATH, "a", buffering=1, encoding="utf-8")
    except Exception:  # noqa: BLE001
        return

    try:
        fp.write(f"\n===== GUI startup: {datetime.now().isoformat(timespec='seconds')} =====\n")
        fp.flush()
    except Exception:  # noqa: BLE001
        pass

    # Python 레벨 stream 교체
    try:
        sys.stdout = fp
        sys.stderr = fp
    except Exception:  # noqa: BLE001
        pass

    # FD 레벨 dup2 — C 라이브러리의 direct fprintf 도 커버
    try:
        os.dup2(fp.fileno(), 1)
        os.dup2(fp.fileno(), 2)
    except Exception:  # noqa: BLE001
        pass

    _done = True


def log_path() -> Path:
    """현재 로그 파일 경로 (다른 모듈에서 사용자에게 표시할 때 사용)."""
    return _LOG_PATH
