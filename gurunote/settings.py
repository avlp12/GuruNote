"""앱 내 설정 저장/로드 유틸리티 (.env + os.environ 동기화)."""

from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from dotenv import set_key

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


def ensure_env_file() -> Path:
    if not ENV_PATH.exists():
        ENV_PATH.write_text("# GuruNote 설정 (자동 생성)\n", encoding="utf-8")
    return ENV_PATH


def backup_env_file() -> Path:
    env_path = ensure_env_file()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup = env_path.with_name(f".env.backup_{ts}")
    shutil.copy2(env_path, backup)
    return backup


def save_settings(settings: Mapping[str, str], create_backup: bool = True) -> tuple[int, Path | None]:
    """
    설정을 .env 와 os.environ 에 동시에 반영.

    Returns:
      (changed_count, backup_path_or_none)
    """
    env_path = ensure_env_file()
    backup_path = backup_env_file() if create_backup else None

    changed = 0
    for key, raw_value in settings.items():
        value = (raw_value or "").strip()
        old = os.environ.get(key, "")
        if old == value:
            continue

        if value:
            os.environ[key] = value
            set_key(str(env_path), key, value)
        else:
            os.environ.pop(key, None)
            set_key(str(env_path), key, "")
        changed += 1

    return changed, backup_path
