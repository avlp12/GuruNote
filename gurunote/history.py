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
import os
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
    # Phase A — 지식 증류기 메타데이터
    organized_title: str = "",
    field: str = "",
    tags: Optional[List[str]] = None,
    uploader: str = "",
    upload_date: str = "",
) -> Path:
    """
    작업 결과를 디스크에 저장하고 인덱스를 갱신한다.

    Args:
        title: yt-dlp 가 가져온 원본 영상 제목 (또는 로컬 파일명)
        organized_title: LLM 이 정리한 한국어 제목 (없으면 title 사용)
        field: 분야 분류 (예: "AI/ML", "스타트업")
        tags: 태그 리스트 (5개 권장)
        uploader: 채널/업로더 이름 (분류용)
        upload_date: 영상 게시일 (YYYY-MM-DD 또는 yt-dlp 의 YYYYMMDD)

    Returns:
        job_dir 경로
    """
    job_dir = _ensure_dirs(job_id)
    created_at = datetime.now(timezone.utc).isoformat()

    meta: dict[str, Any] = {
        "job_id": job_id,
        "title": title,
        "organized_title": organized_title or title,
        "field": field,
        "tags": list(tags) if tags else [],
        "uploader": uploader,
        "upload_date": upload_date,
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
    _write_index_atomic(index)


def _write_index_atomic(index: List[dict]) -> None:
    """
    `history.json` 을 원자적으로 쓴다.

    HistoryDialog 가 `load_index()` 를 호출하는 타이밍과 `save_job()` 의 write
    가 겹치면 부분 기록된 파일이 읽혀 `JSONDecodeError` 가 났었다 (load_index
    는 예외를 삼켜 빈 리스트 반환 → 사용자가 일시적으로 히스토리가 사라진 것처럼
    봄). 임시 파일에 쓴 뒤 `os.replace` 로 대체하면 POSIX 는 원자적, Windows 도
    대부분의 경우 sector-level 원자성을 보장.
    """
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = INDEX_PATH.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(tmp, INDEX_PATH)


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


def update_job_markdown(job_id: str, new_md: str) -> None:
    """
    기존 작업의 `result.md` 만 교체한다. metadata.json 은 건드리지 않음.

    사용자가 HistoryDialog 의 Edit 버튼으로 LLM 결과를 수정한 뒤 저장할 때
    쓰인다. 인덱스의 `has_markdown` 은 True 로 보정 (원래 False 였거나
    stale 이었던 경우 대응).

    Args:
        job_id: 대상 작업 ID
        new_md: 새 마크다운 전체 내용 (frontmatter 포함)

    Raises:
        FileNotFoundError — 잡 폴더가 존재하지 않음
    """
    job_dir = JOBS_DIR / job_id
    if not job_dir.is_dir():
        raise FileNotFoundError(f"작업 폴더가 없습니다: {job_dir}")
    md_path = job_dir / "result.md"
    md_path.write_text(new_md, encoding="utf-8")

    # 인덱스의 has_markdown 이 혹시 False 였다면 보정 (stale 대응)
    index = load_index()
    changed = False
    for j in index:
        if j.get("job_id") == job_id and not j.get("has_markdown"):
            j["has_markdown"] = True
            changed = True
            break
    if changed:
        _write_index_atomic(index)


def rebuild_index() -> dict:
    """
    `~/.gurunote/jobs/` 전체를 스캔해 `history.json` 인덱스를 재생성.

    용도:
      - `history.json` 이 삭제됐거나 손상됐을 때 복구
      - 다른 머신에서 `~/.gurunote/jobs/` 폴더만 복사해 왔을 때 마이그레이션
      - 일부 metadata.json 이 손상됐을 때 나머지를 살려서 재인덱싱

    동작:
      - 각 `jobs/<id>/metadata.json` 을 읽어 인덱스 항목으로 변환
      - `has_markdown` 은 실제 `result.md` 존재 여부로 재계산 (stale 메타
        방어)
      - 손상된 json 은 건너뛰고 `errors` 에 job_id 누적
      - 결과 인덱스를 `created_at` 최신순으로 정렬해 원자적 write

    Returns:
        {
            "total_scanned": int,     # 잡 폴더 총 개수
            "indexed": int,           # 인덱스에 포함된 개수
            "errors": list[str],      # metadata.json 파싱 실패한 job_id 리스트
            "missing_md": list[str],  # metadata 엔 has_markdown=True 였지만
                                      # result.md 파일이 실제로 없는 job_id
        }
    """
    JOBS_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    errors: list[str] = []
    missing_md: list[str] = []
    total = 0

    for job_dir in JOBS_DIR.iterdir():
        if not job_dir.is_dir():
            continue
        total += 1
        meta_path = job_dir / "metadata.json"
        if not meta_path.exists():
            errors.append(job_dir.name + " (metadata.json 없음)")
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{job_dir.name} ({exc})")
            continue

        # has_markdown 재계산 — 메타가 오래돼 파일이 사라진 경우 방어
        md_path = job_dir / "result.md"
        has_md = md_path.exists()
        if meta.get("has_markdown") and not has_md:
            missing_md.append(job_dir.name)
        meta["has_markdown"] = has_md

        # job_id 필드가 비어 있으면 폴더명으로 채움 (이전 포맷 복구)
        if not meta.get("job_id"):
            meta["job_id"] = job_dir.name

        entries.append(meta)

    # 최신순 정렬
    entries.sort(key=lambda m: m.get("created_at") or "", reverse=True)
    _write_index_atomic(entries)

    return {
        "total_scanned": total,
        "indexed": len(entries),
        "errors": errors,
        "missing_md": missing_md,
    }


def delete_job(job_id: str) -> None:
    """히스토리에서 작업 삭제 (파일 + 인덱스). 원자적 write 사용."""
    job_dir = JOBS_DIR / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir, ignore_errors=True)
    index = load_index()
    index = [j for j in index if j.get("job_id") != job_id]
    _write_index_atomic(index)
