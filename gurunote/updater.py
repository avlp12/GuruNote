"""GuruNote 코드/의존성 업데이트 유틸리티."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

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


def _run_silent(cmd: list[str]) -> tuple[int, str]:
    """로그 없이 실행."""
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return proc.returncode, (proc.stdout or "").strip()


def check_update_ready(log: LogFn) -> bool:
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        log("Git 저장소가 아니어서 자동 업데이트를 실행할 수 없습니다.")
        return False
    return True


def get_local_version() -> str:
    """현재 설치된 GuruNote 버전."""
    try:
        from gurunote import __version__
        return __version__
    except Exception:  # noqa: BLE001
        return "unknown"


def _detect_remote_and_branch() -> tuple[str, str]:
    """
    실제 remote 이름과 기본 브랜치를 감지.
    Returns: (remote_name, branch_name)  기본값 ("origin", "main")
    """
    remote = "origin"
    branch = "main"

    # remote 이름 감지
    proc = subprocess.run(
        ["git", "remote"],
        cwd=ROOT, capture_output=True, text=True, timeout=5,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        remotes = proc.stdout.strip().splitlines()
        remote = remotes[0]  # 첫 번째 remote 사용

    # 기본 브랜치 감지: git symbolic-ref refs/remotes/<remote>/HEAD
    proc = subprocess.run(
        ["git", "symbolic-ref", f"refs/remotes/{remote}/HEAD"],
        cwd=ROOT, capture_output=True, text=True, timeout=5,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        # refs/remotes/origin/main → main
        ref = proc.stdout.strip()
        branch = ref.rsplit("/", 1)[-1]
    else:
        # fallback: main 또는 master 중 존재하는 것
        for candidate in ("main", "master"):
            proc = subprocess.run(
                ["git", "rev-parse", "--verify", f"refs/remotes/{remote}/{candidate}"],
                cwd=ROOT, capture_output=True, text=True, timeout=5,
            )
            if proc.returncode == 0:
                branch = candidate
                break

    return remote, branch


def _parse_version_from_init(content: str) -> Optional[str]:
    """__init__.py 내용에서 __version__ 값을 추출."""
    for line in content.splitlines():
        if "__version__" in line and "=" in line:
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def get_remote_version() -> Optional[str]:
    """
    원격 기본 브랜치의 최신 버전을 가져온다 (git fetch 후 원격 __init__.py 읽기).
    remote 이름, 기본 브랜치를 자동 감지하며, 실패 시 None.
    """
    try:
        remote, branch = _detect_remote_and_branch()

        # fetch (실패해도 캐시된 origin/main 으로 시도)
        subprocess.run(
            ["git", "fetch", remote, branch],
            cwd=ROOT, capture_output=True, timeout=30,
        )

        # 1차: git show <remote>/<branch>:gurunote/__init__.py
        result = subprocess.run(
            ["git", "show", f"{remote}/{branch}:gurunote/__init__.py"],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            ver = _parse_version_from_init(result.stdout)
            if ver:
                return ver

        # 2차: fetch 가 실패했을 수 있으므로 ls-remote 로 최신 커밋 SHA 확인 후
        # FETCH_HEAD 에서 읽기 시도
        result = subprocess.run(
            ["git", "ls-remote", remote, f"refs/heads/{branch}"],
            cwd=ROOT, capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            sha = result.stdout.strip().split()[0]
            result2 = subprocess.run(
                ["git", "show", f"{sha}:gurunote/__init__.py"],
                cwd=ROOT, capture_output=True, text=True, timeout=10,
            )
            if result2.returncode == 0 and result2.stdout.strip():
                ver = _parse_version_from_init(result2.stdout)
                if ver:
                    return ver

    except Exception:  # noqa: BLE001
        pass
    return None


def check_for_update() -> dict:
    """
    버전 비교 결과를 반환.

    Returns:
        {
            "local": "0.4.0",
            "remote": "0.5.0" or None,
            "update_available": True/False,
            "message": "사용자에게 보여줄 메시지"
        }
    """
    local = get_local_version()
    remote = get_remote_version()

    if remote is None:
        return {
            "local": local,
            "remote": None,
            "update_available": False,
            "message": (
                f"현재 버전: v{local}\n"
                "원격 버전을 확인할 수 없습니다.\n"
                "(네트워크 연결 또는 git remote 설정을 확인하세요)"
            ),
        }

    if local == remote:
        return {
            "local": local,
            "remote": remote,
            "update_available": False,
            "message": f"v{local} — 최신 버전입니다. 업데이트가 필요없습니다.",
        }

    return {
        "local": local,
        "remote": remote,
        "update_available": True,
        "message": f"새 버전이 있습니다: v{local} → v{remote}",
    }


def update_project(log: LogFn, upgrade_deps: bool = True) -> None:
    """저장소 pull + requirements 업그레이드."""
    if not check_update_ready(log):
        raise RuntimeError("Git 저장소가 아니어서 업데이트를 진행할 수 없습니다.")

    remote, branch = _detect_remote_and_branch()
    steps = [
        ["git", "fetch", remote, "--tags"],
        ["git", "pull", remote, branch, "--rebase"],
    ]
    if upgrade_deps:
        steps.append([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"])

    for cmd in steps:
        code, _ = _run(cmd, log)
        if code != 0:
            raise RuntimeError(f"명령 실패: {' '.join(cmd)} (exit={code})")


# 하위 호환: 기존 코드에서 사용하는 함수
def check_updates(log: LogFn) -> str:
    info = check_for_update()
    return info["message"]
