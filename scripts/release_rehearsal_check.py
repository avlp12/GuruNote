"""
태그 릴리스 리허설 체크 스크립트.

목표:
- 태그 릴리스 전에 필수 파일/경로/워크플로우 구성이 맞는지 빠르게 검증
- 실패 시 즉시 원인 출력 + non-zero exit

예시:
    python scripts/release_rehearsal_check.py --tag v0.1.1
    python scripts/release_rehearsal_check.py --tag v0.1.1 --local-tools
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release-desktop.yml"
PACKAGE_SCRIPT = ROOT / "scripts" / "package_desktop.py"
README = ROOT / "README.md"


def fail(msg: str) -> None:
    print(f"❌ {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def run(cmd: list[str]) -> str:
    try:
        out = subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        fail(f"명령 실패: {' '.join(cmd)}\n{exc.output.strip()}")
    return out


def validate_tag(tag: str) -> None:
    # semver + 선택적 pre-release
    pattern = r"^v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$"
    if not re.match(pattern, tag):
        fail(f"태그 형식이 올바르지 않습니다: {tag} (예: v0.1.1, v1.0.0-rc.1)")
    ok(f"태그 형식 확인: {tag}")


def check_files_exist() -> None:
    for p in (WORKFLOW, PACKAGE_SCRIPT, README):
        if not p.exists():
            fail(f"필수 파일이 없습니다: {p.relative_to(ROOT)}")
    ok("필수 파일 존재 확인")


def check_git_clean() -> None:
    out = run(["git", "status", "--porcelain"]).strip()
    if out:
        fail("워킹 트리가 깨끗하지 않습니다. 커밋/정리 후 다시 시도하세요.")
    ok("워킹 트리 clean")


def check_workflow_contract() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    required_snippets = [
        'tags:\n      - "v*"',
        "workflow_dispatch:",
        "dist/GuruNote.exe",
        "dist/GuruNote-Installer.exe",
        "dist/GuruNote.dmg",
        "dist/GuruNote.pkg",
        "softprops/action-gh-release@v2",
    ]
    missing = [s for s in required_snippets if s not in text]
    if missing:
        fail("릴리스 워크플로우 필수 항목 누락: " + ", ".join(missing))
    ok("릴리스 워크플로우 핵심 항목 확인")


def check_package_script_smoke() -> None:
    run([sys.executable, str(PACKAGE_SCRIPT), "--help"])
    ok("패키징 스크립트 help 스모크 테스트 통과")


def check_local_tools() -> None:
    """
    현재 OS 기준 로컬 도구 확인.
    - Windows: pyinstaller, iscc 권장
    - macOS: pyinstaller, create-dmg/pkgbuild 권장
    - Linux: pyinstaller만 체크(교차 빌드 불가 안내)
    """
    if shutil.which("pyinstaller") is None:
        fail("pyinstaller 가 없습니다. `pip install pyinstaller` 후 다시 시도하세요.")
    ok("pyinstaller 설치 확인")

    if sys.platform.startswith("win"):
        iscc = shutil.which("iscc")
        if not iscc:
            fail("Windows 설치형 exe 리허설을 위해 Inno Setup(ISCC)가 필요합니다.")
        ok("Inno Setup(ISCC) 확인")
        return

    if sys.platform == "darwin":
        if shutil.which("create-dmg") is None:
            fail("DMG 리허설을 위해 create-dmg 가 필요합니다. `brew install create-dmg`")
        if shutil.which("pkgbuild") is None:
            fail("PKG 리허설을 위해 pkgbuild 가 필요합니다.")
        ok("macOS create-dmg/pkgbuild 확인")
        return

    # Linux
    print("⚠️ Linux 환경입니다. Windows/macOS 설치 패키지 실제 빌드는 각 OS 러너에서 검증하세요.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="태그 릴리스 리허설 체크")
    parser.add_argument("--tag", required=True, help="릴리스 예정 태그 (예: v0.1.1)")
    parser.add_argument(
        "--local-tools",
        action="store_true",
        help="현재 머신 기준으로 패키징 로컬 도구(pyinstaller 등)까지 검사",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print("🔎 GuruNote 릴리스 리허설 체크 시작\n")
    validate_tag(args.tag)
    check_files_exist()
    check_git_clean()
    check_workflow_contract()
    check_package_script_smoke()
    if args.local_tools:
        check_local_tools()

    print("\n🎉 리허설 체크 통과: 태그 릴리스를 진행할 수 있습니다.")
    print(f"다음 명령: git tag -a {args.tag} -m \"{args.tag}\" && git push origin {args.tag}")


if __name__ == "__main__":
    main()
