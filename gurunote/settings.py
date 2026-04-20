"""앱 내 설정 저장/로드 유틸리티 (.env + os.environ 동기화)."""

from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from dotenv import set_key

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


# =============================================================================
# HuggingFace 토큰 canonical name = HF_TOKEN
# -----------------------------------------------------------------------------
# 세 가지 이름이 실전에서 섞여 쓰여 왔다:
#
#   HF_TOKEN                   ← huggingface_hub 가 공식 우선순위로 읽음
#   HUGGING_FACE_HUB_TOKEN     ← huggingface_hub 의 2차 fallback
#   HUGGINGFACEHUB_API_TOKEN   ← LangChain 등 생태계 일부가 쓰는 옛 이름
#   HUGGINGFACE_TOKEN          ← GuruNote 가 과거에 쓰던 이름 (라이브러리는 이 이름을 모름)
#
# GuruNote 는 HF_TOKEN 을 canonical 로 통일한다. 읽을 때는 위 우선순위로
# fallback 하고, 앱 시작 시점에 canonical 값을 모든 별칭에 export 하여 외부
# 라이브러리(pyannote, huggingface_hub) 도 자동으로 찾게 한다.
# =============================================================================
HF_TOKEN_CANONICAL = "HF_TOKEN"
HF_TOKEN_ALIASES = (
    "HF_TOKEN",
    "HUGGINGFACE_TOKEN",
    "HUGGING_FACE_HUB_TOKEN",
    "HUGGINGFACEHUB_API_TOKEN",
)


def load_hf_token() -> str:
    """HF_TOKEN 을 우선순위대로 찾아 리턴. 없으면 빈 문자열.

    우선순위는 ``HF_TOKEN_ALIASES`` 순서. 처음으로 non-empty 값을 찾으면 그 값.
    """
    for alias in HF_TOKEN_ALIASES:
        value = (os.environ.get(alias) or "").strip()
        if value:
            return value
    return ""


def ensure_hf_token_env() -> str:
    """토큰을 찾아 **모든 별칭 env 변수에 export**. 멱등.

    앱 시작 시 1회 호출하면 이후 ``os.environ["HF_TOKEN"]`` / ``["HUGGING_FACE_HUB_TOKEN"]``
    등을 찾는 어떤 라이브러리도 동일 값을 본다. 기존 사용자 ``.env`` 가
    ``HUGGINGFACE_TOKEN`` 만 가지고 있어도 이 함수가 ``HF_TOKEN`` 으로 주입한다.

    Returns:
        찾은 토큰 문자열 (없으면 빈 문자열).
    """
    token = load_hf_token()
    if token:
        for alias in HF_TOKEN_ALIASES:
            os.environ[alias] = token
    return token


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
