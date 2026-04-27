/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-3a: HistoryScreen — 라이브러리 카드 그리드 (검색/필터 없이 정적).
 * 디자인 spec: docs/design/v2-reference.html (시각적 참고만).
 *
 * Bridge: list_history({limit, offset}) → {ok, total, items: [...]}
 *   각 item 에 video_id + thumbnail_url enrichment 적용됨 (bridge.py).
 *
 * Phase 2B-3b/c/d 에서 검색/필터/정렬/facet 추가.
 */

const { useState, useEffect, useMemo, useRef } = React;

/* === Search helpers (Phase 2B-3b) === */
function useDebounced(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debouncedValue;
}

function filterItems(items, term) {
  if (!term) return items;
  const t = term.toLowerCase().trim();
  if (!t) return items;
  return items.filter((item) => {
    const title = (item.organized_title || item.title || '').toLowerCase();
    const uploader = (item.uploader || '').toLowerCase();
    const tags = (item.tags || []).join(' ').toLowerCase();
    return title.includes(t) || uploader.includes(t) || tags.includes(t);
  });
}

/* === Sort helpers (Phase 2B-3c) === */
const SORT_OPTIONS = [
  { id: 'latest',   label: '최신순' },
  { id: 'oldest',   label: '오래된순' },
  { id: 'duration', label: '길이 긴 순' },
  { id: 'title',    label: '제목 A-Z' },
];

function sortItems(items, sortBy) {
  // 비파괴 — 항상 새 배열 반환.
  const arr = [...items];
  switch (sortBy) {
    case 'oldest':
      return arr.sort((a, b) =>
        (a.created_at || '').localeCompare(b.created_at || ''));
    case 'duration':
      return arr.sort((a, b) =>
        (b.duration_sec || 0) - (a.duration_sec || 0));
    case 'title':
      return arr.sort((a, b) =>
        (a.organized_title || a.title || '').localeCompare(
          b.organized_title || b.title || '', 'ko'));
    case 'latest':
    default:
      return arr.sort((a, b) =>
        (b.created_at || '').localeCompare(a.created_at || ''));
  }
}

function SortChips({ value, onChange }) {
  return (
    <div className="sort-chips" role="radiogroup" aria-label="정렬 기준">
      {SORT_OPTIONS.map((opt) => (
        <button
          key={opt.id}
          type="button"
          role="radio"
          aria-checked={value === opt.id}
          className={'sort-chip' + (value === opt.id ? ' sort-chip--active' : '')}
          onClick={() => onChange(opt.id)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

const STATUS_BADGE = {
  completed: { label: '완료',    cls: 'job-card__badge--success' },
  done:      { label: '완료',    cls: 'job-card__badge--success' },
  failed:    { label: '실패',    cls: 'job-card__badge--error' },
  error:     { label: '실패',    cls: 'job-card__badge--error' },
  running:   { label: '진행 중', cls: 'job-card__badge--running' },
  stopped:   { label: '중지',    cls: 'job-card__badge--error' },
};

function formatDuration(sec) {
  if (sec == null || sec <= 0) return '';
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function JobCard({ item, onClick }) {
  const [imgError, setImgError] = useState(false);
  const status = STATUS_BADGE[item.status] || { label: item.status || '?', cls: '' };
  const title = item.organized_title || item.title || '제목 없음';
  const showImg = item.thumbnail_url && !imgError;

  return (
    <article className="job-card" onClick={() => onClick && onClick(item)}>
      <div className="job-card__thumb">
        {showImg ? (
          <img
            src={item.thumbnail_url}
            alt={title}
            onError={() => setImgError(true)}
            loading="lazy"
          />
        ) : (
          <div className="job-card__thumb-fallback">
            <span className="job-card__thumb-fallback-label">텍스트 온리</span>
            <div className="job-card__thumb-fallback-title">{title}</div>
          </div>
        )}
        <span className={'job-card__badge ' + status.cls}>{status.label}</span>
        {item.duration_sec > 0 && (
          <span className="job-card__duration">{formatDuration(item.duration_sec)}</span>
        )}
      </div>
      <div className="job-card__body">
        {item.field && <span className="job-card__field">{item.field}</span>}
        <h3 className="job-card__title">{title}</h3>
        <div className="job-card__meta">
          {item.uploader && <span>{item.uploader}</span>}
          {item.upload_date && <span>· {item.upload_date}</span>}
        </div>
        {item.tags && item.tags.length > 0 && (
          <div className="job-card__tags">
            {item.tags.slice(0, 4).map(tag => (
              <span key={tag} className="job-card__tag">{tag}</span>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}

/**
 * HistoryScreen — props 로 items / loading / error / onReload 받음.
 * list_history 호출은 App.jsx 에서 lifting 하여 Sidebar 카운트와 공유.
 */
function HistoryScreen({ items, total, loading, error, onReload }) {
  // Phase 2B-3b: 검색 + chips state
  const [searchInput, setSearchInput] = useState('');
  const debouncedSearch = useDebounced(searchInput, 150);
  const filteredItems = useMemo(
    () => filterItems(items, debouncedSearch),
    [items, debouncedSearch]
  );

  // Phase 2B-3c: 정렬 state — 검색 결과에 정렬 적용
  const [sortBy, setSortBy] = useState('latest');
  const sortedFilteredItems = useMemo(
    () => sortItems(filteredItems, sortBy),
    [filteredItems, sortBy]
  );

  const handleChipClick = (chip) => {
    // Phase 2B-3 후속에서 backend wiring (markdown body / embedding 의미 검색).
    if (window.showToast) {
      window.showToast(`${chip} 검색은 Phase 2B-3 후속에서 활성화됩니다.`);
    }
  };

  const handleCardClick = (item) => {
    // Phase 2B-3d / 2B-4 에서 detail view 또는 EditorScreen 으로 이동.
    console.log('[JobCard click]', item.job_id, item.organized_title || item.title);
    if (window.showToast) {
      window.showToast(`노트 열기 (Phase 2B-4): ${item.organized_title || item.title}`);
    }
  };

  return (
    <div className="history-screen">
      <div className="history-topbar">
        <div className="history-topbar__crumbs">GuruNote · 라이브러리</div>
        <div className="history-topbar__title">작업 히스토리</div>
        <div className="history-topbar__sub">
          {loading ? '불러오는 중...' : `증류된 노트 ${total}개 · 지식 라이브러리`}
        </div>
      </div>

      <div className="history-toolbar">
        <div className="search-box">
          <span className="msi search-box__icon">search</span>
          <input
            type="text"
            className="search-box__input"
            placeholder="제목 / 업로더 / 태그 검색..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            autoComplete="off"
          />
          {searchInput && (
            <button
              type="button"
              className="search-box__clear"
              onClick={() => setSearchInput('')}
              aria-label="검색어 비우기"
            >
              <span className="msi" style={{ fontSize: 18 }}>close</span>
            </button>
          )}
        </div>

        <div className="filter-chips">
          <button
            type="button"
            className="filter-chip"
            onClick={() => handleChipClick('본문 포함')}
          >
            <span className="filter-chip__icon msi">description</span>
            본문 포함
          </button>
          <button
            type="button"
            className="filter-chip"
            onClick={() => handleChipClick('의미 검색')}
          >
            <span className="filter-chip__icon msi">psychology</span>
            의미 검색
          </button>
        </div>

        <SortChips value={sortBy} onChange={setSortBy} />

        <button
          type="button"
          className="btn btn--ghost history-toolbar__refresh"
          onClick={onReload}
          disabled={loading}
        >
          <span className="msi">refresh</span>
          새로고침
        </button>
      </div>

      {debouncedSearch && (
        <div className="history-result-meta">
          "<b>{debouncedSearch}</b>" 검색 결과 <b>{filteredItems.length}</b>개 · 전체 {items.length}개
        </div>
      )}

      {error && (
        <div className="history-empty" style={{ borderColor: 'var(--gn-danger)', color: 'var(--gn-danger)' }}>
          오류: {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="history-empty">
          아직 증류된 노트가 없습니다.<br />
          생성 화면에서 첫 노트를 만들어보세요.
        </div>
      )}

      {!loading && !error && items.length > 0 && debouncedSearch && sortedFilteredItems.length === 0 && (
        <div className="history-empty">
          "{debouncedSearch}" 에 해당하는 노트가 없습니다.
        </div>
      )}

      {!loading && sortedFilteredItems.length > 0 && (
        <div className="job-grid">
          {sortedFilteredItems.map(item => (
            <JobCard key={item.job_id} item={item} onClick={handleCardClick} />
          ))}
        </div>
      )}

      {loading && (
        <div className="history-loading">불러오는 중...</div>
      )}
    </div>
  );
}

window.HistoryScreen = HistoryScreen;
