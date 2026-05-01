/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-6d: SearchPalette — ⌘K 글로벌 검색 모달.
 *
 * Reference 정합 영역:
 *   - 시각: app-sidebar-and-routes.jsx:169-170 의 search input 의 모달 활성화
 *   - 모달 spec 자체는 우리 자체 결정 (Reference 에 모달 spec 없음)
 *
 * 사용자 결정 (Step 6d):
 *   - A-1: ⌘K + TopBar gn-search click 으로 open, Esc 로 close
 *   - A-2: 검색 4 필드 (title / 태그 / 분야 / 업로더)
 *   - A-3: 결과 단순 list (제목 + 분야/태그 chip + 업로더 sub)
 *   - A-4: 매치 substring highlight 안 함 (v1)
 *
 * 호스팅: App.jsx 의 searchPaletteOpen state. open=true 시 마운트, false 시 언마운트.
 *   - ⌘K keydown 은 App.jsx 에서 글로벌 등록
 *   - TopBar 의 gn-search onClick 도 App.jsx 의 setter 호출
 *
 * Babel standalone global scope 회피: top-level const 는 PALETTE_ 접두사.
 */

const { useState, useEffect, useMemo, useRef } = React;

const PALETTE_MAX_RESULTS = 30;

/* 검색 필터 — title (organized_title 우선) / 태그 / 분야 / 업로더 4 필드 */
function paletteFilter(items, term) {
  if (!term) return items;
  const t = term.toLowerCase().trim();
  if (!t) return items;
  return items.filter((item) => {
    const title = (item.organized_title || item.title || '').toLowerCase();
    const tags = (item.tags || []).join(' ').toLowerCase();
    const field = (item.field || '').toLowerCase();
    const uploader = (item.uploader || '').toLowerCase();
    return title.includes(t) || tags.includes(t) || field.includes(t) || uploader.includes(t);
  });
}

function SearchPalette({ open, items, onClose, onSelect }) {
  const [query, setQuery] = useState('');
  const [activeIdx, setActiveIdx] = useState(0);
  const inputRef = useRef(null);
  const listRef = useRef(null);

  // open 변경 시 query / activeIdx 초기화 + input focus
  useEffect(() => {
    if (open) {
      setQuery('');
      setActiveIdx(0);
      // 다음 paint 에 focus (display: none → block 직후라 약간의 delay 필요)
      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    }
  }, [open]);

  const results = useMemo(
    () => paletteFilter(items || [], query).slice(0, PALETTE_MAX_RESULTS),
    [items, query]
  );

  // query 가 바뀌면 active 첫 항목으로 reset
  useEffect(() => {
    setActiveIdx(0);
  }, [query]);

  // 키보드 navigation: ↑↓ Enter Esc
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        onClose();
        return;
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setActiveIdx((i) => Math.min(i + 1, results.length - 1));
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        setActiveIdx((i) => Math.max(i - 1, 0));
        return;
      }
      if (e.key === 'Enter') {
        e.preventDefault();
        const item = results[activeIdx];
        if (item) {
          onSelect(item);
        }
        return;
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open, results, activeIdx, onClose, onSelect]);

  // active item 이 화면 밖이면 scroll
  useEffect(() => {
    const list = listRef.current;
    if (!list) return;
    const node = list.children[activeIdx];
    if (node && typeof node.scrollIntoView === 'function') {
      node.scrollIntoView({ block: 'nearest' });
    }
  }, [activeIdx]);

  if (!open) return null;

  return (
    <div
      className="gn-palette-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="전체 노트 검색"
      onClick={(e) => {
        // backdrop click → close (palette 본체 click 는 stopPropagation)
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="gn-palette" onClick={(e) => e.stopPropagation()}>
        <div className="gn-palette__head">
          <span className="msi gn-palette__head-ico">search</span>
          <input
            ref={inputRef}
            type="text"
            className="gn-palette__input"
            placeholder="제목 / 태그 / 분야 / 업로더 검색..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoComplete="off"
            spellCheck={false}
          />
          <span className="gn-palette__head-hint">Esc</span>
        </div>

        <div className="gn-palette__results" ref={listRef}>
          {results.length === 0 && query.trim() && (
            <div className="gn-palette__empty">
              <span className="msi">search_off</span>
              <div>"{query.trim()}" 에 해당하는 노트가 없습니다.</div>
            </div>
          )}
          {results.length === 0 && !query.trim() && (items || []).length === 0 && (
            <div className="gn-palette__empty">
              <span className="msi">inbox</span>
              <div>아직 노트가 없습니다.</div>
            </div>
          )}
          {results.length === 0 && !query.trim() && (items || []).length > 0 && (
            <div className="gn-palette__hint">
              검색어를 입력하거나 ↑↓ Enter 로 이동하세요. ({items.length}개 노트)
            </div>
          )}
          {results.map((item, i) => {
            const title = item.organized_title || item.title || '제목 없음';
            const isActive = i === activeIdx;
            return (
              <button
                key={item.job_id}
                type="button"
                className={'gn-palette__item' + (isActive ? ' gn-palette__item--active' : '')}
                onMouseEnter={() => setActiveIdx(i)}
                onClick={() => onSelect(item)}
              >
                <div className="gn-palette__item-title" title={title}>{title}</div>
                <div className="gn-palette__item-meta">
                  {item.field && (
                    <span className="gn-palette__item-chip gn-palette__item-chip--field">
                      {item.field}
                    </span>
                  )}
                  {(item.tags || []).slice(0, 3).map((tag) => (
                    <span key={tag} className="gn-palette__item-chip">{tag}</span>
                  ))}
                  {item.uploader && (
                    <span className="gn-palette__item-uploader" title={item.uploader}>
                      {item.uploader}
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        <div className="gn-palette__foot">
          <span className="gn-palette__foot-shortcut"><kbd>↑</kbd><kbd>↓</kbd> 이동</span>
          <span className="gn-palette__foot-shortcut"><kbd>Enter</kbd> 열기</span>
          <span className="gn-palette__foot-shortcut"><kbd>Esc</kbd> 닫기</span>
        </div>
      </div>
    </div>
  );
}

window.SearchPalette = SearchPalette;
