"""
저장된 GuruNote 작업 본문 전문 검색.

Phase F — "지식 증류기" 로드맵. 이번 PR 은 **키워드(substring) 검색** 단계.
의미(임베딩) 검색은 추후 phase.

HistoryDialog 는 기본적으로 메타 (제목/업로더/태그/분야) 만 검색한다. 본문은
큰 파일 (~100KB+) 이라 매번 전체를 읽으면 UI 가 느려지므로, 본문 검색은 사용자
opt-in (HistoryDialog 의 "📄 본문 포함" 토글).

이 모듈은:
  - `_body_cache(job_id)`: lru_cache 로 128개 job 까지 본문 캐시. YAML
    frontmatter 는 미리 벗겨내 메타 중복 매칭을 피함 (frontmatter 는 history.json
    메타로 이미 검색됨).
  - `match_body(job_id, query)`: 첫 매칭 위치 ±80 자 스니펫 반환, 매칭 없으면
    None. case-insensitive.
  - `clear_cache()`: 잡 삭제/리프레시 시 캐시 무효화.
"""

from __future__ import annotations

import functools
import re
from typing import Optional

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@functools.lru_cache(maxsize=128)
def _body_cache(job_id: str) -> str:
    """저장된 result.md 본문 (frontmatter 제외). 로드 실패 시 빈 문자열."""
    # 지연 import — gurunote.history 의 초기화 비용을 search 모듈 import 시점과 분리
    from gurunote.history import get_job_markdown

    md = get_job_markdown(job_id) or ""
    m = _FRONTMATTER_RE.match(md)
    if m:
        md = md[m.end():]
    return md


def match_body(job_id: str, query: str) -> Optional[str]:
    """본문에서 query (case-insensitive) 의 첫 매칭을 찾아 ±80자 스니펫 반환.

    매칭 없으면 None. 빈 query 는 None (전체 반환 방지).
    """
    q = (query or "").strip().lower()
    if not q:
        return None
    body = _body_cache(job_id)
    if not body:
        return None
    lower = body.lower()
    idx = lower.find(q)
    if idx < 0:
        return None
    start = max(0, idx - 80)
    end = min(len(body), idx + len(q) + 80)
    # 개행 제거 + 양쪽 공백 정리 (한 줄 스니펫)
    snippet = body[start:end].replace("\n", " ").replace("\r", "").strip()
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(body) else ""
    return f"{prefix}{snippet}{suffix}"


def clear_cache() -> None:
    """작업 삭제 / 히스토리 리프레시 시 호출해 stale 캐시 제거."""
    _body_cache.cache_clear()
