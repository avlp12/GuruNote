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

/* === Facet helpers (Phase 2B-3d) === */
const FACET_GROUPS = [
  { id: 'field',    icon: 'category', label: '주제' },
  { id: 'uploader', icon: 'person',   label: '인물' },
  { id: 'title',    icon: 'subject',  label: '제목' },
  { id: 'tag',      icon: 'sell',     label: '태그' },
];

function buildFacets(items) {
  const fields = new Map();
  const uploaders = new Map();
  const titles = new Set();
  const tags = new Map();

  for (const it of items) {
    if (it.field) fields.set(it.field, (fields.get(it.field) || 0) + 1);
    if (it.uploader) uploaders.set(it.uploader, (uploaders.get(it.uploader) || 0) + 1);
    if (it.organized_title) titles.add(it.organized_title);
    for (const tag of (it.tags || [])) {
      if (tag) tags.set(tag, (tags.get(tag) || 0) + 1);
    }
  }

  const toSortedArr = (map) =>
    [...map.entries()]
      .map(([label, count]) => ({ label, count }))
      .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label, 'ko'));

  return {
    field:    toSortedArr(fields),
    uploader: toSortedArr(uploaders),
    title:    [...titles]
                .sort((a, b) => a.localeCompare(b, 'ko'))
                .map((t) => ({ label: t, count: 1 })),
    tag:      toSortedArr(tags),
  };
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

/* === FacetPanel (Phase 2B-3d) === */
function FacetPanel({ items, activeFacets, onToggle, initialExpandedGroup }) {
  // Phase 2B-5a: groups start expanded by default (empty Set). initialExpandedGroup
  // is informational here — all groups already expand on mount, but we use it as
  // the trigger to scrollIntoView the named group's header.
  const [collapsed, setCollapsed] = useState(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const groupHeaderRefs = useRef({});

  const facets = useMemo(() => buildFacets(items), [items]);

  // Phase 2B-5a: scroll the requested group's header into view on mount.
  useEffect(() => {
    if (!initialExpandedGroup) return;
    const el = groupHeaderRefs.current[initialExpandedGroup];
    if (el && typeof el.scrollIntoView === 'function') {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggleGroup = (id) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const filterFacetItems = (arr) => {
    const t = searchTerm.trim().toLowerCase();
    if (!t) return arr;
    return arr.filter((it) => it.label.toLowerCase().includes(t));
  };

  return (
    <aside className="history-screen__facets">
      <div className="facet-panel__header">
        <span className="msi" style={{ fontSize: 16 }}>account_tree</span>
        <span>내비게이션</span>
      </div>

      <input
        type="text"
        className="facet-panel__search"
        placeholder="트리 내 검색..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      {FACET_GROUPS.map((group) => {
        const arr = filterFacetItems(facets[group.id] || []);
        if (arr.length === 0) return null;
        const isCollapsed = collapsed.has(group.id);
        return (
          <div
            key={group.id}
            className={'facet-group' + (isCollapsed ? ' facet-group--collapsed' : '')}
          >
            <button
              type="button"
              className="facet-group__header"
              ref={(el) => { groupHeaderRefs.current[group.id] = el; }}
              onClick={() => toggleGroup(group.id)}
              aria-expanded={!isCollapsed}
            >
              <span className="msi facet-group__icon">{group.icon}</span>
              <span>{group.label}</span>
              <span className="facet-group__count">{arr.length}</span>
              <span className="msi facet-group__chevron">expand_more</span>
            </button>
            <div className="facet-group__items">
              {arr.slice(0, 30).map((item) => {
                const facetKey = `${group.id}:${item.label}`;
                const active = activeFacets.has(facetKey);
                return (
                  <button
                    key={facetKey}
                    type="button"
                    className={'facet-item' + (active ? ' facet-item--active' : '')}
                    onClick={() => onToggle(group.id, item.label)}
                  >
                    <span className="facet-item__dot" />
                    <span className="facet-item__label" title={item.label}>{item.label}</span>
                    <span className="facet-item__count">{item.count}</span>
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
    </aside>
  );
}

/* === ActiveFilters chain (Phase 2B-3d) === */
function ActiveFilters({ search, activeFacets, onClearSearch, onResetFacet, onClearAll }) {
  const facetArr = [...activeFacets];
  if (!search && facetArr.length === 0) return null;

  return (
    <div className="active-filters">
      <span>적용된 필터:</span>
      {search && (
        <span className="active-filter">
          검색: "{search}"
          <button type="button" className="active-filter__remove" onClick={onClearSearch} aria-label="검색 제거">
            <span className="msi" style={{ fontSize: 12 }}>close</span>
          </button>
        </span>
      )}
      {facetArr.map((key) => {
        const idx = key.indexOf(':');
        const group = key.slice(0, idx);
        const label = key.slice(idx + 1);
        const groupLabel = (FACET_GROUPS.find((g) => g.id === group) || {}).label || group;
        return (
          <span key={key} className="active-filter">
            {groupLabel}: {label}
            <button type="button" className="active-filter__remove" onClick={() => onResetFacet(key)} aria-label="필터 제거">
              <span className="msi" style={{ fontSize: 12 }}>close</span>
            </button>
          </span>
        );
      })}
      <button type="button" className="active-filters__clear" onClick={onClearAll}>
        모두 비우기
      </button>
    </div>
  );
}

/* === DetailPanel (Phase 2B-3d) — slide-in modal === */
function DetailPanel({ item, onClose, onEdit }) {
  useEffect(() => {
    const onEsc = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onEsc);
    return () => document.removeEventListener('keydown', onEsc);
  }, [onClose]);

  if (!item) return null;

  const title = item.organized_title || item.title || '제목 없음';
  const dur = item.duration_sec > 0
    ? `${Math.floor(item.duration_sec / 60)}:${String(Math.floor(item.duration_sec % 60)).padStart(2, '0')}`
    : null;

  return (
    <div className="detail-overlay" onClick={onClose}>
      <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
        <div className="detail-panel__header">
          <h2 className="detail-panel__title" title={title}>{title}</h2>
          <button type="button" className="detail-panel__close" onClick={onClose} aria-label="닫기">
            <span className="msi">close</span>
          </button>
        </div>

        <div className="detail-panel__body">
          <div className="detail-thumb">
            {item.thumbnail_url && <img src={item.thumbnail_url} alt={title} />}
          </div>

          <dl className="detail-meta-grid">
            {item.field        && (<><dt>주제</dt><dd>{item.field}</dd></>)}
            {item.uploader     && (<><dt>업로더</dt><dd>{item.uploader}</dd></>)}
            {item.upload_date  && (<><dt>업로드일</dt><dd>{item.upload_date}</dd></>)}
            {item.created_at   && (<><dt>생성일</dt><dd>{item.created_at}</dd></>)}
            {dur               && (<><dt>길이</dt><dd>{dur}</dd></>)}
            {item.num_speakers > 0 && (<><dt>화자 수</dt><dd>{item.num_speakers}명</dd></>)}
            {item.stt_engine   && (<><dt>STT</dt><dd>{item.stt_engine}</dd></>)}
            {item.llm_provider && (<><dt>LLM</dt><dd>{item.llm_provider}</dd></>)}
            {item.status       && (<><dt>상태</dt><dd>{item.status}</dd></>)}
            {item.source_url   && (<><dt>출처</dt><dd>{item.source_url}</dd></>)}
          </dl>

          {item.tags && item.tags.length > 0 && (
            <>
              <div className="detail-section-title">태그</div>
              <div className="detail-tags">
                {item.tags.map((tag) => (
                  <span key={tag} className="detail-tag">{tag}</span>
                ))}
              </div>
            </>
          )}

          {item.error_message && (
            <>
              <div className="detail-section-title" style={{ color: 'var(--gn-danger)' }}>오류 메시지</div>
              <div style={{ fontSize: 12, color: 'var(--gn-danger)', whiteSpace: 'pre-wrap' }}>
                {item.error_message}
              </div>
            </>
          )}

          <div className="detail-section-title">본문</div>
          <div style={{ color: 'var(--gn-on-surface-muted)', fontSize: 13 }}>
            {item.has_markdown
              ? '본문 미리보기는 Phase 2B-4 (노트 편집 화면) 에서 표시됩니다.'
              : '본문 데이터가 없습니다.'}
          </div>
        </div>

        <div className="detail-actions-bar">
          <button type="button" className="btn btn--ghost" onClick={() => { if (onEdit) onEdit(item); onClose(); }}>
            <span className="msi">edit</span>
            편집
          </button>
          <button type="button" className="btn btn--ghost" onClick={() => window.showToast?.('Phase 2B-4 다운로드 wiring 예정')}>
            <span className="msi">download</span>
            다운로드
          </button>
          <button type="button" className="btn btn--ghost" onClick={() => window.showToast?.('Phase 3A (RAG) 에서 활성화')}>
            <span className="msi">hub</span>
            연관 노트
          </button>
        </div>
      </div>
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

function JobCard({ item, onClick, onEdit }) {
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
      <div className="job-card__actions" onClick={(e) => e.stopPropagation()}>
        <button
          type="button"
          className="job-action"
          title="열기"
          onClick={() => onClick && onClick(item)}
        >
          <span className="msi">open_in_new</span>
        </button>
        <button
          type="button"
          className="job-action"
          title="편집"
          onClick={() => onEdit && onEdit(item)}
        >
          <span className="msi">edit</span>
        </button>
        <button
          type="button"
          className="job-action"
          title="다운로드"
          onClick={() => window.showToast?.('Phase 2B-4 다운로드 wiring 예정')}
        >
          <span className="msi">download</span>
        </button>
        <button
          type="button"
          className="job-action"
          title="연관 노트"
          onClick={() => window.showToast?.('Phase 3A (RAG) 에서 활성화')}
        >
          <span className="msi">hub</span>
        </button>
        <button
          type="button"
          className="job-action job-action--more"
          title="더 보기"
          onClick={() => window.showToast?.('Phase 2B-3-backend 에서 활성화')}
        >
          <span className="msi">more_horiz</span>
        </button>
      </div>
    </article>
  );
}

/**
 * HistoryScreen — props 로 items / loading / error / onReload 받음.
 * list_history 호출은 App.jsx 에서 lifting 하여 Sidebar 카운트와 공유.
 */
function HistoryScreen({
  items, total, loading, error, onReload, onEditNote,
  // Phase 2B-5a: 1-shot initial filter from sidebar library shortcuts
  initialFacets,           // Set<"groupId:label"> | undefined
  initialTimeWindow,       // null | number (days) | undefined
  initialExpandedGroup,    // 'tag' | 'field' | ... | undefined — auto-expand + scrollIntoView
  onFilterApplied,         // () => void — called once on mount so App.jsx can clear historyFilter
}) {
  // Phase 2B-3b: 검색 + chips state
  const [searchInput, setSearchInput] = useState('');
  const debouncedSearch = useDebounced(searchInput, 150);
  const filteredItems = useMemo(
    () => filterItems(items, debouncedSearch),
    [items, debouncedSearch]
  );

  // Phase 2B-3d: facet filter — Set of "groupId:label"
  const [activeFacets, setActiveFacets] = useState(
    () => (initialFacets ? new Set(initialFacets) : new Set())
  );

  // Phase 2B-5a: 시간 window filter — facet 와 별개의 dimension (AND)
  const [timeWindow, setTimeWindow] = useState(initialTimeWindow || null);

  // Phase 2B-5a: 1-shot reset — initial filter 를 mount 시 1회 적용 후 부모에 알림
  useEffect(() => {
    if (onFilterApplied) onFilterApplied();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFacetToggle = (groupId, label) => {
    const key = `${groupId}:${label}`;
    setActiveFacets((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key); else next.add(key);
      return next;
    });
  };

  const handleResetFacet = (key) => {
    setActiveFacets((prev) => {
      const next = new Set(prev);
      next.delete(key);
      return next;
    });
  };

  const handleClearAll = () => {
    setSearchInput('');
    setActiveFacets(new Set());
    setTimeWindow(null);
  };

  // facet filter — 검색 결과에 적용 (AND across groups)
  const facetFilteredItems = useMemo(() => {
    if (activeFacets.size === 0) return filteredItems;
    return filteredItems.filter((item) => {
      for (const key of activeFacets) {
        const idx = key.indexOf(':');
        const group = key.slice(0, idx);
        const label = key.slice(idx + 1);
        switch (group) {
          case 'field':    if (item.field !== label) return false; break;
          case 'uploader': if (item.uploader !== label) return false; break;
          case 'title':    if (item.organized_title !== label) return false; break;
          case 'tag':      if (!(item.tags || []).includes(label)) return false; break;
          default: break;
        }
      }
      return true;
    });
  }, [filteredItems, activeFacets]);

  // Phase 2B-5a: timeWindow filter — facet 결과 위에 적용 (별도 dimension)
  const timeWindowFilteredItems = useMemo(() => {
    if (!timeWindow) return facetFilteredItems;
    const cutoff = Date.now() - timeWindow * 24 * 60 * 60 * 1000;
    return facetFilteredItems.filter((it) => {
      const ts = it.created_at ? Date.parse(it.created_at) : NaN;
      return Number.isFinite(ts) && ts >= cutoff;
    });
  }, [facetFilteredItems, timeWindow]);

  // Phase 2B-3c: 정렬 state — timeWindow 결과 위에 적용 (filter chain 의 마지막)
  const [sortBy, setSortBy] = useState('latest');
  const sortedFinalItems = useMemo(
    () => sortItems(timeWindowFilteredItems, sortBy),
    [timeWindowFilteredItems, sortBy]
  );

  // Phase 2B-3d: detail view state
  const [detailItem, setDetailItem] = useState(null);

  const handleChipClick = (chip) => {
    if (window.showToast) {
      // chip 이 이미 '검색' 으로 끝나면 ('의미 검색') 추가 ' 검색' 없이 조사만 — 'X 검색 검색은' 중복 회피.
      const tail = chip.endsWith('검색') ? '은' : ' 검색은';
      window.showToast(`${chip}${tail} Phase 3A (RAG) 에서 활성화됩니다.`);
    }
  };

  const handleCardClick = (item) => {
    setDetailItem(item);
  };

  return (
    <div className="history-screen">
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

        {timeWindow && (
          <div className="hist-toolbar__chip hist-toolbar__chip--active">
            <span className="msi" style={{ fontSize: 14 }}>schedule</span>
            최근 {timeWindow}일
            <button
              type="button"
              className="hist-toolbar__chip-clear"
              onClick={() => setTimeWindow(null)}
              title="시간 필터 해제"
              aria-label="시간 필터 해제"
            >
              <span className="msi" style={{ fontSize: 14 }}>close</span>
            </button>
          </div>
        )}

        <button
          type="button"
          className="btn btn--ghost btn--sm history-toolbar__refresh"
          onClick={onReload}
          disabled={loading}
        >
          <span className="msi">refresh</span>
          새로고침
        </button>
      </div>

      <ActiveFilters
        search={debouncedSearch}
        activeFacets={activeFacets}
        onClearSearch={() => setSearchInput('')}
        onResetFacet={handleResetFacet}
        onClearAll={handleClearAll}
      />

      <div className="history-screen__body">
        <div className="history-screen__main">
          {debouncedSearch && (
            <div className="history-result-meta">
              "<b>{debouncedSearch}</b>" 검색 결과 <b>{sortedFinalItems.length}</b>개 · 전체 {items.length}개
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

          {!loading && !error && items.length > 0 && (debouncedSearch || activeFacets.size > 0 || timeWindow) && sortedFinalItems.length === 0 && (
            <div className="history-empty">
              조건에 해당하는 노트가 없습니다.
            </div>
          )}

          {!loading && sortedFinalItems.length > 0 && (
            <div className="job-grid">
              {sortedFinalItems.map((item) => (
                <JobCard
                  key={item.job_id}
                  item={item}
                  onClick={handleCardClick}
                  onEdit={(it) => onEditNote && onEditNote(it.job_id)}
                />
              ))}
            </div>
          )}

          {loading && (
            <div className="history-loading">불러오는 중...</div>
          )}
        </div>

        <FacetPanel
          items={items}
          activeFacets={activeFacets}
          onToggle={handleFacetToggle}
          initialExpandedGroup={initialExpandedGroup}
        />
      </div>

      {detailItem && (
        <DetailPanel
          item={detailItem}
          onClose={() => setDetailItem(null)}
          onEdit={(it) => onEditNote && onEditNote(it.job_id)}
        />
      )}
    </div>
  );
}

window.HistoryScreen = HistoryScreen;
