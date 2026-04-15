"""GuruNote 코드/의존성 업데이트 유틸리티."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Callable

LogFn = Callable[[str], None]

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], log: LogFn) -> tuple[int, str]:
    log(f"$ {' '.join(cmd)}")
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    if out.strip():
        log(out.strip())
    return proc.returncode, out


def check_update_ready(log: LogFn) -> bool:
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        log("⚠️ Git 저장소가 아니어서 자동 업데이트를 실행할 수 없습니다.")
        return False
    return True


def update_project(log: LogFn, upgrade_deps: bool = True) -> None:
    """
    저장소 pull + requirements 업그레이드.
    실패 시 RuntimeError.
    """
    if not check_update_ready(log):
        raise RuntimeError("Git 저장소가 아니어서 업데이트를 진행할 수 없습니다.")

    steps = [
        ["git", "fetch", "--all", "--tags"],
        ["git", "pull", "--rebase"],
    ]
    if upgrade_deps:
        steps.append([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"])

    for cmd in steps:
        code, _ = _run(cmd, log)
        if code != 0:
            raise RuntimeError(f"명령 실패: {' '.join(cmd)} (exit={code})")


def check_updates(log: LogFn) -> str:
    """
    현재 브랜치가 원격 대비 ahead/behind 인지 문자열로 반환.
    """
    if not check_update_ready(log):
        return "Git 저장소 아님"

    code, _ = _run(["git", "fetch", "--all", "--tags"], log)
    if code != 0:
        raise RuntimeError("원격 정보 fetch 실패")

    code, out = _run(["git", "status", "-sb"], log)
    if code != 0:
        raise RuntimeError("git status 확인 실패")
    return out.strip()
