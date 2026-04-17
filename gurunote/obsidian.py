"""
Obsidian vault 로 결과 마크다운을 직접 저장.

Phase D — "지식 증류기" 로드맵.

Phase A 의 YAML frontmatter 가 이미 Obsidian 호환 형식 (title / tags / field
등) 으로 emit 되므로, 사용자는 파일을 vault 폴더에 복사하기만 하면 Obsidian 이
즉시 인식해 태그 검색 / Dataview 쿼리가 가능하다.

설계:
  - `OBSIDIAN_VAULT_PATH` 환경변수에 vault 루트 경로를 저장
  - `OBSIDIAN_SUBFOLDER` (기본 "GuruNote") 에 해당 vault 내부 하위 폴더 지정
  - vault 는 `.obsidian/` 하위 디렉토리 존재로 판별 (Obsidian 앱이 자동 생성)
  - 파일명 충돌 시 timestamp suffix 로 덮어쓰기 회피
  - Path traversal 차단 — filename / subfolder 에 `..` 나 절대경로 금지
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


DEFAULT_SUBFOLDER = "GuruNote"


def is_obsidian_vault(path: Path) -> bool:
    """Vault 는 `.obsidian/` 하위 디렉토리를 갖는 특징으로 판별.

    Obsidian 이 vault 를 처음 열 때 자동 생성하므로, 이 폴더의 존재가
    "유효한 vault" 의 가장 신뢰할 수 있는 지표다.
    """
    try:
        return path.is_dir() and (path / ".obsidian").is_dir()
    except Exception:  # noqa: BLE001
        return False


def resolve_vault_path() -> Optional[Path]:
    """`OBSIDIAN_VAULT_PATH` 환경변수 → 절대 Path. 미설정/무효 시 None.

    `~` 확장 + 심볼릭 링크 해결. 디렉토리 존재만 검증 (vault 마커는 별도
    `is_obsidian_vault` 로 확인).
    """
    raw = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
    if not raw:
        return None
    try:
        path = Path(os.path.expanduser(raw)).resolve()
    except Exception:  # noqa: BLE001
        return None
    if not path.is_dir():
        return None
    return path


def resolve_subfolder() -> str:
    """`OBSIDIAN_SUBFOLDER` 환경변수 → 정규화된 하위 폴더명. 기본 'GuruNote'."""
    raw = (os.environ.get("OBSIDIAN_SUBFOLDER") or DEFAULT_SUBFOLDER).strip()
    # 경로 구분자 / traversal 방지 — 단일 폴더 이름만 허용
    raw = raw.strip("/").strip("\\")
    if ".." in raw or "/" in raw or "\\" in raw:
        return DEFAULT_SUBFOLDER
    return raw or DEFAULT_SUBFOLDER


def save_to_vault(
    full_md: str,
    filename: str,
    vault_path: Optional[Path] = None,
    subfolder: Optional[str] = None,
) -> Path:
    """
    결과 마크다운을 Obsidian vault 하위 폴더에 저장.

    Args:
        full_md: 최종 GuruNote 마크다운 (YAML frontmatter 포함)
        filename: 저장할 파일명 (`.md` 확장자 자동 추가)
        vault_path: 명시 경로. None 이면 `OBSIDIAN_VAULT_PATH` 환경변수 사용.
        subfolder: 명시 하위 폴더. None 이면 `OBSIDIAN_SUBFOLDER` 또는
            `DEFAULT_SUBFOLDER` ("GuruNote") 사용.

    Returns:
        저장된 파일의 절대 경로. 동일 파일명이 이미 있으면 `_YYYYMMDD_HHMMSS`
        접미사가 붙은 경로.

    Raises:
        RuntimeError — vault 경로 미설정 또는 유효하지 않음.
        ValueError — filename 또는 subfolder 가 경로 이스케이프 시도.
    """
    if vault_path is None:
        vault_path = resolve_vault_path()
    if vault_path is None:
        raise RuntimeError(
            "Obsidian vault 경로가 설정되지 않았습니다.\n"
            "Settings 다이얼로그에서 `OBSIDIAN_VAULT_PATH` 를 지정하거나\n"
            ".env 에 직접 기록하세요."
        )
    if not vault_path.is_dir():
        raise RuntimeError(
            f"Vault 경로가 존재하지 않거나 디렉토리가 아닙니다: {vault_path}"
        )

    # filename 검증 (Path traversal 방지)
    safe_name = (filename or "").strip()
    if not safe_name:
        raise ValueError("파일명이 비어 있습니다.")
    if "/" in safe_name or "\\" in safe_name or ".." in safe_name:
        raise ValueError(f"유효하지 않은 파일명 (경로 구분자/'..' 금지): {filename}")
    if not safe_name.lower().endswith(".md"):
        safe_name += ".md"

    # subfolder 해석 + 검증
    if subfolder is None:
        sf = resolve_subfolder()
    else:
        sf = subfolder.strip().strip("/").strip("\\")
        if ".." in sf or "/" in sf or "\\" in sf:
            raise ValueError(f"유효하지 않은 subfolder: {subfolder}")
    target_dir = vault_path / sf if sf else vault_path
    target_dir.mkdir(parents=True, exist_ok=True)

    out_path = target_dir / safe_name
    if out_path.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = out_path.stem
        out_path = target_dir / f"{stem}_{ts}.md"

    out_path.write_text(full_md, encoding="utf-8")
    return out_path
