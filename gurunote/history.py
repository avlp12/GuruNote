"""
GuruNote 작업 히스토리 — 완료/실패 작업을 로컬에 보존.

저장 위치: ~/.gurunote/jobs/<job_id>/
  ├── metadata.json   (제목, 날짜, 엔진, 상태 등)
  ├── result.md       (완료 시 최종 마크다운)
  └── pipeline.log    (전체 파이프라인 로그)

인덱스: ~/.gurunote/history.json (job_id → 메타 요약)
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

GURUNOTE_DIR = Path.home() / ".gurunote"
JOBS_DIR = GURUNOTE_DIR / "jobs"
INDEX_PATH = GURUNOTE_DIR / "history.json"


# =============================================================================
# Job 데이터 구조
# =============================================================================
def new_job_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:20]


def _ensure_dirs(job_id: str) -> Path:
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


# =============================================================================
# 로그 파일 관리
# =============================================================================
class JobLogger:
    """파이프라인 실행 중 로그를 파일 + 콜백 동시 기록."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        self._dir = _ensure_dirs(job_id)
        self._path = self._dir / "pipeline.log"
        self._file = open(self._path, "a", encoding="utf-8")  # noqa: SIM115

    def write(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._file.write(f"[{ts}] {msg}\n")
        self._file.flush()

    def close(self) -> None:
        if self._file and not self._file.closed:
            self._file.close()

    @property
    def path(self) -> Path:
        return self._path


# =============================================================================
# 히스토리 저장 / 로드
# =============================================================================
def save_job(
    job_id: str,
    *,
    title: str,
    source_url: str = "",
    stt_engine: str = "",
    llm_provider: str = "",
    status: str = "completed",
    duration_sec: float = 0.0,
    num_speakers: int = 0,
    error_message: str = "",
    full_md: str = "",
) -> Path:
    """
    작업 결과를 디스크에 저장하고 인덱스를 갱신한다.

    Returns:
        job_dir 경로
    """
    job_dir = _ensure_dirs(job_id)
    created_at = datetime.now(timezone.utc).isoformat()

    meta: dict[str, Any] = {
        "job_id": job_id,
        "title": title,
        "created_at": created_at,
        "source_url": source_url,
        "stt_engine": stt_engine,
        "llm_provider": llm_provider,
        "status": status,
        "duration_sec": duration_sec,
        "num_speakers": num_speakers,
        "error_message": error_message,
    }

    # 메타데이터
    (job_dir / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 마크다운 (완료 시)
    if full_md:
        (job_dir / "result.md").write_text(full_md, encoding="utf-8")
        meta["has_markdown"] = True
    else:
        meta["has_markdown"] = False

    # 인덱스 갱신
    _update_index(job_id, meta)

    return job_dir


def _update_index(job_id: str, meta: dict) -> None:
    index = load_index()
    # 같은 job_id 가 있으면 덮어쓰기
    index = [j for j in index if j.get("job_id") != job_id]
    index.insert(0, meta)  # 최신이 맨 위
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_index() -> List[dict]:
    """히스토리 인덱스를 로드한다. 파일 없으면 빈 리스트."""
    if not INDEX_PATH.exists():
        return []
    try:
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []


def get_job_markdown(job_id: str) -> Optional[str]:
    """저장된 마크다운을 읽어 반환. 없으면 None."""
    md_path = JOBS_DIR / job_id / "result.md"
    if md_path.exists():
        return md_path.read_text(encoding="utf-8")
    return None


def get_job_log(job_id: str) -> Optional[str]:
    """저장된 파이프라인 로그를 읽어 반환. 없으면 None."""
    log_path = JOBS_DIR / job_id / "pipeline.log"
    if log_path.exists():
        return log_path.read_text(encoding="utf-8")
    return None


def delete_job(job_id: str) -> None:
    """히스토리에서 작업 삭제 (파일 + 인덱스)."""
    job_dir = JOBS_DIR / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir, ignore_errors=True)
    index = load_index()
    index = [j for j in index if j.get("job_id") != job_id]
    INDEX_PATH.write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
