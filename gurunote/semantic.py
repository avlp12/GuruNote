"""
저장된 GuruNote 작업 본문에 대한 의미 검색 (semantic search).

Step 3.4 — "지식 증류기" 로드맵 마지막. Phase F 의 키워드(substring) 검색을
임베딩 기반 유사도 검색으로 보완한다. 예를 들어 "AI 가 일자리를 대체할까"
같은 의미 쿼리로 "자동화", "노동 시장", "대체 고용" 등 직접 매칭이 없는
관련 구절을 찾아낼 수 있다.

설계:
  - `sentence-transformers` 의 다국어 모델
    (`paraphrase-multilingual-MiniLM-L12-v2`, 384-dim, ~117MB) 로 embed
  - 본문을 1000자 + 100자 overlap chunk 로 분할해 각각 embed
  - 전체 인덱스를 `~/.gurunote/embeddings.npz` 단일 파일로 저장 (vectors
    + metadata: job_id / chunk_idx / chunk_text)
  - 쿼리 시 query embed + numpy cosine sim → top-K chunks → HistoryDialog
    가 매칭된 job 들에 스니펫과 함께 표시

의존성: `requirements-search.txt` 로 분리 (선택 설치). 미설치 시
`is_available()` False → UI 가 안내 다이얼로그 표시.

인덱스 빌드는 **명시적 버튼 클릭** (Dashboard 의 "Rebuild Semantic Index")
으로만 수행. 매 저장마다 자동 인덱싱하면 모델 추론 비용이 크기 때문.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Optional

# 인덱스 저장 경로
_INDEX_DIR = Path.home() / ".gurunote"
_INDEX_PATH = _INDEX_DIR / "embeddings.npz"
_META_PATH = _INDEX_DIR / "embeddings_meta.json"

# 모델 설정 (환경변수로 오버라이드 가능)
import os as _os
_DEFAULT_MODEL = _os.environ.get(
    "GURUNOTE_SEMANTIC_MODEL",
    "paraphrase-multilingual-MiniLM-L12-v2",
)

# Chunk 분할 파라미터
_CHUNK_CHARS = 1000
_CHUNK_OVERLAP = 100

# 모델 싱글톤 캐시 (첫 로드 시 모델 무게 다운로드 수 분 걸릴 수 있음)
_model_cache: dict = {}

ProgressFn = Callable[[str], None]


# =============================================================================
# 가용성 체크
# =============================================================================
def is_available() -> bool:
    """`sentence-transformers` + `numpy` import 가능 여부."""
    try:
        import sentence_transformers  # type: ignore  # noqa: F401
        import numpy  # noqa: F401
        return True
    except Exception:  # noqa: BLE001
        return False


def missing_packages_hint() -> str:
    return (
        "의미 검색에 필요한 패키지가 설치되어 있지 않습니다.\n"
        "다음 명령으로 설치 후 재실행하세요:\n"
        "  pip install -r requirements-search.txt\n\n"
        "첫 실행 시 다국어 임베딩 모델 (~117MB) 을 HuggingFace 에서\n"
        "다운로드합니다 (이후 로컬 캐시)."
    )


def is_index_built() -> bool:
    return _INDEX_PATH.exists() and _META_PATH.exists()


def index_stats() -> dict:
    """현재 인덱스 상태 요약 (사용자에게 표시할 용도)."""
    if not is_index_built():
        return {"built": False}
    try:
        meta = json.loads(_META_PATH.read_text(encoding="utf-8"))
        import numpy as np  # type: ignore
        data = np.load(_INDEX_PATH)
        return {
            "built": True,
            "model": meta.get("model", "?"),
            "num_chunks": int(data["vectors"].shape[0]),
            "num_jobs": len(set(meta.get("job_ids", []))),
            "built_at": meta.get("built_at", ""),
        }
    except Exception as exc:  # noqa: BLE001
        return {"built": True, "error": str(exc)}


# =============================================================================
# Chunk 분할
# =============================================================================
_FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def _split_into_chunks(text: str) -> list[str]:
    """본문을 문자 수 기준 overlap chunk 로 분할. frontmatter 는 제외."""
    # YAML frontmatter 제거 (메타는 `gurunote.history` 에서 별도 검색)
    text = _FRONTMATTER_RE.sub("", text)
    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        end = min(i + _CHUNK_CHARS, n)
        # 경계에서 단어 중간에 자르지 않도록 공백까지 확장 시도
        if end < n:
            next_space = text.find(" ", end)
            if 0 < next_space - end < 50:
                end = next_space
        chunks.append(text[i:end].strip())
        if end >= n:
            break
        i = max(i + _CHUNK_CHARS - _CHUNK_OVERLAP, i + 1)
    return [c for c in chunks if c]


# =============================================================================
# 모델 로딩 (지연 + 싱글톤)
# =============================================================================
def _get_model(model_name: str = _DEFAULT_MODEL):
    """`SentenceTransformer` 싱글톤. 첫 호출 시 무게 다운로드."""
    if model_name in _model_cache:
        return _model_cache[model_name]
    from sentence_transformers import SentenceTransformer  # type: ignore
    model = SentenceTransformer(model_name)
    _model_cache[model_name] = model
    return model


# =============================================================================
# 인덱스 빌드
# =============================================================================
def build_index(
    jobs: list[dict],
    log: Optional[ProgressFn] = None,
    model_name: str = _DEFAULT_MODEL,
) -> dict:
    """
    주어진 job 리스트의 본문을 chunk 로 분할해 임베딩 인덱스 생성.

    Args:
        jobs: `load_index()` 결과. `job_id` 와 `has_markdown` 이 필요.
        log: 진행 로그 콜백 (선택).
        model_name: sentence-transformers 모델명.

    Returns:
        {"num_jobs": int, "num_chunks": int, "skipped": int}
    """
    log = log or (lambda _msg: None)
    if not is_available():
        raise RuntimeError(missing_packages_hint())

    from gurunote.history import get_job_markdown
    import numpy as np  # type: ignore

    log(f"모델 로딩: {model_name} (첫 실행 시 ~117MB 다운로드)")
    model = _get_model(model_name)

    all_chunks: list[str] = []
    meta: list[dict] = []
    skipped = 0

    target_jobs = [j for j in jobs if j.get("has_markdown")]
    log(f"인덱싱 대상 잡: {len(target_jobs)} 건")

    for idx, j in enumerate(target_jobs, start=1):
        job_id = j.get("job_id", "")
        if not job_id:
            skipped += 1
            continue
        md = get_job_markdown(job_id) or ""
        chunks = _split_into_chunks(md)
        if not chunks:
            skipped += 1
            continue
        for ci, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            meta.append({
                "job_id": job_id,
                "chunk_idx": ci,
                "title": j.get("organized_title") or j.get("title") or "",
                "preview": chunk[:160],
            })
        if idx % 10 == 0:
            log(f"  {idx}/{len(target_jobs)} 잡 완료")

    if not all_chunks:
        raise RuntimeError(
            "인덱싱할 본문이 없습니다. 작업을 먼저 저장한 뒤 다시 시도하세요."
        )

    log(f"{len(all_chunks)} 개 chunk 임베딩 중…")
    vectors = model.encode(
        all_chunks,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,  # cosine sim 을 dot product 로 계산하기 위해
    )
    vectors = np.asarray(vectors, dtype=np.float32)

    _INDEX_DIR.mkdir(parents=True, exist_ok=True)
    np.savez(_INDEX_PATH, vectors=vectors)
    _META_PATH.write_text(
        json.dumps({
            "model": model_name,
            "num_chunks": len(all_chunks),
            "num_jobs": len({m["job_id"] for m in meta}),
            "job_ids": [m["job_id"] for m in meta],
            "chunk_idxs": [m["chunk_idx"] for m in meta],
            "titles": [m["title"] for m in meta],
            "previews": [m["preview"] for m in meta],
            "built_at": _now_iso(),
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    log(f"인덱스 저장 완료: {_INDEX_PATH}")
    return {
        "num_jobs": len({m["job_id"] for m in meta}),
        "num_chunks": len(all_chunks),
        "skipped": skipped,
    }


def clear_index() -> None:
    """인덱스 파일 삭제 — 디스크 정리 또는 강제 재빌드 용."""
    for p in (_INDEX_PATH, _META_PATH):
        if p.exists():
            p.unlink()


def update_job_in_index(
    job_id: str,
    full_md: str,
    title: str = "",
    log: Optional[ProgressFn] = None,
    model_name: str = _DEFAULT_MODEL,
) -> Optional[dict]:
    """
    단일 작업의 임베딩을 인덱스에 incremental 업데이트.

    동작:
      - 인덱스가 아직 없거나 sentence-transformers 미설치 → silent no-op
        (`None` 반환). 첫 빌드는 사용자가 명시적으로 "Semantic Rebuild" 해야 함.
      - 인덱스가 있으면:
          1. 같은 job_id 의 기존 chunk 들 제거 (재저장/편집 대응)
          2. 새 본문을 chunk 분할 + embed
          3. 기존 vectors 에 append, meta 갱신, 원자적 저장

    `save_job()` 직후나 `update_job_markdown()` 직후 백그라운드 thread 에서
    호출하면 사용자는 Dashboard 의 "Semantic Rebuild" 를 다시 누르지 않아도
    검색 결과에 새 작업이 반영됨.

    Returns:
        {"removed_old": int, "added_new": int}  성공 시
        None — 인덱스 미존재 / 패키지 미설치 / 본문 비어 / 에러
    """
    log = log or (lambda _msg: None)
    if not is_available() or not is_index_built():
        return None
    try:
        import numpy as np  # type: ignore
        data = np.load(_INDEX_PATH)
        existing_vectors = data["vectors"]
        meta = json.loads(_META_PATH.read_text(encoding="utf-8"))

        # 1) 기존 chunk 제거 (job_id 일치하는 항목)
        keep_mask = [j != job_id for j in meta.get("job_ids", [])]
        removed = sum(1 for k in keep_mask if not k)
        if removed > 0:
            existing_vectors = existing_vectors[keep_mask]
            for key in ("job_ids", "chunk_idxs", "titles", "previews"):
                if key in meta:
                    meta[key] = [v for v, keep in zip(meta[key], keep_mask) if keep]

        # 2) 새 본문 chunk 분할 + embed
        chunks = _split_into_chunks(full_md)
        if not chunks:
            # 본문 비어있음 → 그냥 cleaned-up 인덱스만 저장
            np.savez(_INDEX_PATH, vectors=existing_vectors)
            meta["built_at"] = _now_iso()
            _META_PATH.write_text(
                json.dumps(meta, ensure_ascii=False), encoding="utf-8"
            )
            log(f"[Semantic] {job_id}: 본문 없음 — old {removed} 제거만")
            return {"removed_old": removed, "added_new": 0}

        log(f"[Semantic] {job_id}: {len(chunks)} chunk 임베딩 중…")
        model = _get_model(model_name)
        new_vectors = model.encode(
            chunks, batch_size=32, show_progress_bar=False,
            normalize_embeddings=True,
        )
        new_vectors = np.asarray(new_vectors, dtype=np.float32)

        # 3) append + 저장
        combined = np.vstack([existing_vectors, new_vectors]) if len(existing_vectors) else new_vectors
        np.savez(_INDEX_PATH, vectors=combined)
        for ci, chunk in enumerate(chunks):
            meta.setdefault("job_ids", []).append(job_id)
            meta.setdefault("chunk_idxs", []).append(ci)
            meta.setdefault("titles", []).append(title)
            meta.setdefault("previews", []).append(chunk[:160])
        meta["num_chunks"] = len(meta.get("job_ids", []))
        meta["num_jobs"] = len(set(meta.get("job_ids", [])))
        meta["built_at"] = _now_iso()
        _META_PATH.write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )
        log(f"[Semantic] {job_id}: -{removed} +{len(chunks)} 인덱스 갱신")
        return {"removed_old": removed, "added_new": len(chunks)}
    except Exception as exc:  # noqa: BLE001
        log(f"[Semantic] 인덱스 갱신 실패 ({exc}) — 무시하고 계속")
        return None


def _now_iso() -> str:
    from datetime import datetime
    return datetime.now().isoformat(timespec="seconds")


# =============================================================================
# 검색
# =============================================================================
def search(
    query: str,
    top_k: int = 10,
    min_score: float = 0.25,
    model_name: str = _DEFAULT_MODEL,
) -> list[dict]:
    """
    query 에 대해 의미 유사도가 높은 chunk 상위 top_k 를 반환.

    Returns:
        [
            {
                "job_id": str,
                "score": float (0~1),
                "title": str,
                "preview": str,    # chunk 첫 160자
                "chunk_idx": int,
            },
            ...
        ]
        점수 내림차순. `min_score` 미만은 제외 (noisy match 필터).

    Raises:
        RuntimeError — 패키지 미설치 또는 인덱스 미빌드
    """
    if not is_available():
        raise RuntimeError(missing_packages_hint())
    if not is_index_built():
        raise RuntimeError(
            "의미 검색 인덱스가 아직 빌드되지 않았습니다.\n"
            "Dashboard 의 'Rebuild Semantic Index' 버튼으로 먼저 빌드하세요."
        )
    q = (query or "").strip()
    if not q:
        return []

    import numpy as np  # type: ignore

    model = _get_model(model_name)
    qv = model.encode([q], normalize_embeddings=True)
    qv = np.asarray(qv, dtype=np.float32)

    data = np.load(_INDEX_PATH)
    vectors = data["vectors"]
    # 양쪽 normalized 이므로 dot product = cosine sim
    sims = (vectors @ qv.T).flatten()

    meta = json.loads(_META_PATH.read_text(encoding="utf-8"))
    job_ids = meta.get("job_ids", [])
    chunk_idxs = meta.get("chunk_idxs", [])
    titles = meta.get("titles", [])
    previews = meta.get("previews", [])

    # top-K (중복 job 제거하여 대표 chunk 1개씩만)
    order = sims.argsort()[::-1]
    seen_jobs: set[str] = set()
    out: list[dict] = []
    for idx in order:
        score = float(sims[idx])
        if score < min_score:
            break
        jid = job_ids[idx]
        if jid in seen_jobs:
            continue
        seen_jobs.add(jid)
        out.append({
            "job_id": jid,
            "score": score,
            "title": titles[idx] if idx < len(titles) else "",
            "preview": previews[idx] if idx < len(previews) else "",
            "chunk_idx": int(chunk_idxs[idx]) if idx < len(chunk_idxs) else 0,
        })
        if len(out) >= top_k:
            break

    return out
