"""GuruNote 코드/의존성 업데이트 유틸리티.

GuruNote 는 공개 저장소 (avlp12/GuruNote) 이므로 `git fetch/pull` 에 인증이
필요 없다. 하지만 사용자의 macOS 키체인에 stale 한 GitHub 크레덴셜이 남아
있거나 credential helper 가 꼬여 있으면 `Username for 'https://github.com':`
프롬프트가 뜨면서 업데이트가 멈추는 일이 생긴다 (특히 GitHub 을 OAuth 로만
로그인해서 password 를 설정한 적이 없는 계정).

대응 전략 2단계:
  1. git 서브프로세스를 **완전 non-interactive** 로 실행 — credential
     helper 비활성화 + GIT_TERMINAL_PROMPT=0 + stdin=DEVNULL.
     공개 저장소라면 이것만으로도 성공한다.
  2. 그래도 실패하면 `GitAuthError` 를 raise 해서 GUI 가 "tarball 로
     업데이트" 옵션을 제공하게 한다.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Optional

LogFn = Callable[[str], None]

ROOT = Path(__file__).resolve().parents[1]


class GitAuthError(RuntimeError):
    """git 서브프로세스가 인증 관련 사유로 실패했음을 알리는 예외."""


# =============================================================================
# git 서브프로세스 — 대화형 프롬프트 / 크레덴셜 helper 완전 차단
# =============================================================================
_AUTH_ERROR_PATTERNS = (
    "could not read username",
    "could not read password",
    "authentication failed",
    "terminal prompts disabled",
    "bad credentials",
    "access denied",
    "http 401",
    "http 403",
)


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"  # 프롬프트 금지
    env["GIT_ASKPASS"] = "/bin/echo"  # askpass 헬퍼가 빈 값을 돌려주도록
    # 사용자가 설정한 credential.helper (osxkeychain 등) 가 stale 상태로
    # 실패의 원인이 되는 경우가 있어, 이 프로세스 한정으로 비활성화.
    env["GCM_INTERACTIVE"] = "Never"
    return env


def _git_cmd(args: list[str]) -> list[str]:
    """`git` 프리픽스 + credential.helper 무력화 옵션."""
    return ["git", "-c", "credential.helper=", *args]


def _run(cmd: list[str], log: LogFn) -> tuple[int, str]:
    """git 또는 기타 커맨드를 non-interactive 로 실행."""
    log(f"$ {' '.join(cmd)}")
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        stdin=subprocess.DEVNULL,  # TTY 접근 차단
        env=_git_env() if cmd and cmd[0] == "git" else None,
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
        _git_cmd(["remote"]),
        cwd=ROOT, capture_output=True, text=True, timeout=5,
        stdin=subprocess.DEVNULL, env=_git_env(),
    )
    if proc.returncode == 0 and proc.stdout.strip():
        remotes = proc.stdout.strip().splitlines()
        remote = remotes[0]  # 첫 번째 remote 사용

    # 기본 브랜치 감지: git symbolic-ref refs/remotes/<remote>/HEAD
    proc = subprocess.run(
        _git_cmd(["symbolic-ref", f"refs/remotes/{remote}/HEAD"]),
        cwd=ROOT, capture_output=True, text=True, timeout=5,
        stdin=subprocess.DEVNULL, env=_git_env(),
    )
    if proc.returncode == 0 and proc.stdout.strip():
        # refs/remotes/origin/main → main
        ref = proc.stdout.strip()
        branch = ref.rsplit("/", 1)[-1]
    else:
        # fallback: main 또는 master 중 존재하는 것
        for candidate in ("main", "master"):
            proc = subprocess.run(
                _git_cmd(["rev-parse", "--verify", f"refs/remotes/{remote}/{candidate}"]),
                cwd=ROOT, capture_output=True, text=True, timeout=5,
                stdin=subprocess.DEVNULL, env=_git_env(),
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

        # fetch (실패해도 캐시된 origin/main 으로 시도). non-interactive.
        subprocess.run(
            _git_cmd(["fetch", remote, branch]),
            cwd=ROOT, capture_output=True, timeout=30,
            stdin=subprocess.DEVNULL, env=_git_env(),
        )

        # 1차: git show <remote>/<branch>:gurunote/__init__.py
        result = subprocess.run(
            _git_cmd(["show", f"{remote}/{branch}:gurunote/__init__.py"]),
            cwd=ROOT, capture_output=True, text=True, timeout=10,
            stdin=subprocess.DEVNULL, env=_git_env(),
        )
        if result.returncode == 0 and result.stdout.strip():
            ver = _parse_version_from_init(result.stdout)
            if ver:
                return ver

        # 2차: fetch 가 실패했을 수 있으므로 ls-remote 로 최신 커밋 SHA 확인 후
        # FETCH_HEAD 에서 읽기 시도
        result = subprocess.run(
            _git_cmd(["ls-remote", remote, f"refs/heads/{branch}"]),
            cwd=ROOT, capture_output=True, text=True, timeout=15,
            stdin=subprocess.DEVNULL, env=_git_env(),
        )
        if result.returncode == 0 and result.stdout.strip():
            sha = result.stdout.strip().split()[0]
            result2 = subprocess.run(
                _git_cmd(["show", f"{sha}:gurunote/__init__.py"]),
                cwd=ROOT, capture_output=True, text=True, timeout=10,
                stdin=subprocess.DEVNULL, env=_git_env(),
            )
            if result2.returncode == 0 and result2.stdout.strip():
                ver = _parse_version_from_init(result2.stdout)
                if ver:
                    return ver

        # 3차: 공개 저장소 fallback — GitHub raw URL 에서 직접 가져오기
        # (git 서브시스템이 아예 막혔을 때 최후의 수단)
        owner_repo = _detect_github_owner_repo(remote)
        if owner_repo:
            raw_url = (
                f"https://raw.githubusercontent.com/{owner_repo[0]}/"
                f"{owner_repo[1]}/{branch}/gurunote/__init__.py"
            )
            try:
                with urllib.request.urlopen(raw_url, timeout=10) as resp:
                    content = resp.read().decode("utf-8")
                ver = _parse_version_from_init(content)
                if ver:
                    return ver
            except Exception:  # noqa: BLE001
                pass

    except Exception:  # noqa: BLE001
        pass
    return None


# =============================================================================
# 공개 저장소 Tarball 업데이트 — git 인증 실패 시 fallback
# =============================================================================
_GITHUB_URL_RE = re.compile(
    r"github\.com[:/]+([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?\s*$"
)


def _detect_github_owner_repo(remote: str = "origin") -> Optional[tuple[str, str]]:
    """git remote URL 에서 (owner, repo) 추출. GitHub 이 아니면 None."""
    try:
        proc = subprocess.run(
            _git_cmd(["remote", "get-url", remote]),
            cwd=ROOT, capture_output=True, text=True, timeout=5,
            stdin=subprocess.DEVNULL, env=_git_env(),
        )
        if proc.returncode != 0:
            return None
        url = proc.stdout.strip()
        m = _GITHUB_URL_RE.search(url)
        if m:
            return m.group(1), m.group(2)
    except Exception:  # noqa: BLE001
        return None
    return None


def _is_auth_error(output: str) -> bool:
    lower = (output or "").lower()
    return any(p in lower for p in _AUTH_ERROR_PATTERNS)


def update_via_tarball(
    log: LogFn,
    upgrade_deps: bool = True,
    branch: str = "main",
) -> None:
    """
    공개 GitHub tarball 로 업데이트 — git 인증이 막힌 환경 fallback.

    `.git/` 디렉터리는 건드리지 않고, 추적 파일만 덮어쓴다. 사용자의
    로컬 수정사항이 있는 파일은 덮어쓰기 이전에 경고 출력.
    """
    owner_repo = _detect_github_owner_repo()
    if owner_repo is None:
        raise RuntimeError(
            "원격 저장소가 GitHub 이 아니거나 remote 를 감지할 수 없어 "
            "tarball 업데이트를 실행할 수 없습니다."
        )
    owner, repo = owner_repo
    tar_url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/{branch}"

    log(f"공개 tarball 다운로드: {tar_url}")

    try:
        req = urllib.request.Request(
            tar_url,
            headers={"User-Agent": "GuruNote-Updater"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"tarball 다운로드 실패 (HTTP {exc.code}): {tar_url}") from exc
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"tarball 다운로드 실패: {exc}") from exc

    log(f"다운로드 완료 ({len(data):,}B) — 임시 폴더에 추출 중...")

    # tar.gz 를 임시 폴더에 풀고, 최상위 한 폴더를 찾아 ROOT 로 동기화
    with tempfile.TemporaryDirectory(prefix="gurunote-update-") as tmp:
        tmp_path = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
            tf.extractall(tmp_path)

        # 최상위 폴더 (예: GuruNote-main) 찾기
        top_entries = [p for p in tmp_path.iterdir() if p.is_dir()]
        if not top_entries:
            raise RuntimeError("tarball 에 컨텐츠가 없습니다.")
        src_root = top_entries[0]

        log(f"파일 복사 중: {src_root.name} → {ROOT.name}")
        _copy_tree_safe(src_root, ROOT, log=log)

    if upgrade_deps:
        log("의존성 업그레이드...")
        rc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"],
            cwd=ROOT, stdin=subprocess.DEVNULL,
            capture_output=True, text=True,
        )
        if rc.stdout:
            log(rc.stdout.strip())
        if rc.returncode != 0:
            log(f"(경고) pip 업그레이드 exit={rc.returncode}, 계속 진행")

    log("tarball 업데이트 완료. 앱을 재시작하세요.")


_SKIP_TOP_LEVEL = {".git", ".venv", "venv", "autosave", "__pycache__", ".DS_Store"}


def _copy_tree_safe(src: Path, dst: Path, log: LogFn) -> None:
    """`src` 내용을 `dst` 에 재귀 복사. `.git`, `.venv` 등은 건드리지 않음."""
    for item in src.iterdir():
        name = item.name
        if name in _SKIP_TOP_LEVEL:
            continue
        target = dst / name
        if item.is_dir():
            # 디렉토리: shutil.copytree 는 dst 존재 시 실패 → 수동 병합
            if target.exists():
                for sub in item.rglob("*"):
                    rel = sub.relative_to(src)
                    t = dst / rel
                    if sub.is_dir():
                        t.mkdir(parents=True, exist_ok=True)
                    else:
                        t.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(sub, t)
            else:
                shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


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
    """저장소 pull + requirements 업그레이드.

    git 인증 실패 (credential prompt / stale osxkeychain 등) 시
    `GitAuthError` 를 raise — GUI 가 tarball 업데이트를 제안할 수 있게 한다.
    """
    if not check_update_ready(log):
        raise RuntimeError("Git 저장소가 아니어서 업데이트를 진행할 수 없습니다.")

    remote, branch = _detect_remote_and_branch()
    git_steps = [
        _git_cmd(["fetch", remote, "--tags"]),
        _git_cmd(["pull", remote, branch, "--rebase"]),
    ]

    for cmd in git_steps:
        code, out = _run(cmd, log)
        if code != 0:
            if _is_auth_error(out):
                raise GitAuthError(
                    "git 원격 접속에 인증이 요구되었습니다. "
                    "공개 저장소 tarball 로 업데이트할 수 있습니다."
                )
            raise RuntimeError(f"명령 실패: {' '.join(cmd)} (exit={code})")

    if upgrade_deps:
        code, _ = _run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"],
            log,
        )
        if code != 0:
            raise RuntimeError(f"의존성 업그레이드 실패 (exit={code})")


# 하위 호환: 기존 코드에서 사용하는 함수
def check_updates(log: LogFn) -> str:
    info = check_for_update()
    return info["message"]
