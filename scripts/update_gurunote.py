"""
GuruNote 원클릭 업데이트 스크립트.

예시:
  python scripts/update_gurunote.py --check
  python scripts/update_gurunote.py --update
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gurunote.updater import check_updates, update_project


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="GuruNote 업데이트 도우미")
    p.add_argument("--check", action="store_true", help="업데이트 가능 여부만 확인")
    p.add_argument("--update", action="store_true", help="git pull + requirements 업그레이드 실행")
    p.add_argument("--no-deps", action="store_true", help="업데이트 시 dependencies 업그레이드 생략")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    log = print
    if args.check:
        print(check_updates(log))
        return
    if args.update:
        update_project(log, upgrade_deps=not args.no_deps)
        print("✅ 업데이트 완료")
        return
    print("옵션을 선택하세요: --check 또는 --update")


if __name__ == "__main__":
    main()
