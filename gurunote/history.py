"""GuruNote 작업 이력(성공/실패) 저장 및 조회 유틸."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gurunote.exporter import sanitize_filename


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _history_dir() -> Path:
    path = Path(os.environ.get("GURUNOTE_HISTORY_DIR", "history"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_history_entry(
    *,
    title: str,
    source: str,
    status: str,
    full_md: str = "",
    report_path: str = "",
    stt_engine: str = "",
    llm_provider: str = "",
    error: str = "",
) -> dict[str, Any]:
    """
    작업 결과를 기본 자동 저장한다.

    status: "success" | "failed"
    """
    now = _utc_now()
    run_id = now.strftime("%Y%m%d_%H%M%S_%f")
    base_name = sanitize_filename(title or "gurunote")
    run_dir = _history_dir() / f"{run_id}_{base_name}"
    run_dir.mkdir(parents=True, exist_ok=True)

    result_path = ""
    if full_md:
        result_file = run_dir / f"GuruNote_{base_name}.md"
        result_file.write_text(full_md, encoding="utf-8")
        result_path = str(result_file)

    meta = {
        "run_id": run_id,
        "created_at": now.isoformat(),
        "title": title,
        "source": source,
        "status": status,
        "result_path": result_path,
        "report_path": report_path,
        "stt_engine": stt_engine,
        "llm_provider": llm_provider,
        "error": error,
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return meta


def list_history(limit: int = 50) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for meta_path in _history_dir().glob("*/metadata.json"):
        try:
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            items.append(payload)
        except Exception:
            continue
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items[:limit]

