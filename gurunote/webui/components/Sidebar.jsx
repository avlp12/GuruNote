/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-1 + 2B-3c-rework: Sidebar — 우리 코드 (디자인 spec 참고, 코드 cp 폐기).
 *
 * 디자인 spec (docs/design/v2-reference.html):
 *   - 좌측 260px width, 라이트 테마
 *   - G 로고 + GuruNote v0.8.0.6
 *   - "+ 새 노트 만들기" CTA (단축키 ⌘N)
 *   - 5 nav: 생성 / 히스토리 / 노트 편집 / 대시보드 / 설정
 *     · '히스토리' 옆 동적 카운트 (전체 노트 수)
 *   - 라이브러리 section: 즐겨찾기 / 최근 7일 / 태그 (각 카운트, 동적)
 *   - 사용자 footer 는 추후 멀티 유저 시 추가 (Phase 2B-1 폐기 결정)
 */

const NAV_ITEMS = [
  { id: 'main',      icon: 'auto_awesome',  label: '생성',      countKey: null },
  { id: 'history',   icon: 'history',       label: '히스토리',  countKey: 'history' },
  { id: 'editor',    icon: 'edit_note',     label: '노트 편집', countKey: null },
  { id: 'dashboard', icon: 'insights',      label: '대시보드',  countKey: null },
  { id: 'settings',  icon: 'settings',      label: '설정',      countKey: null },
];

const RECENT_DAYS = 7;

function recentItemCount(items, days) {
  if (!items || items.length === 0) return 0;
  const threshold = Date.now() - days * 24 * 60 * 60 * 1000;
  let n = 0;
  for (const it of items) {
    const t = it.created_at ? Date.parse(it.created_at) : NaN;
    if (Number.isFinite(t) && t >= threshold) n++;
  }
  return n;
}

function uniqueTagCount(items) {
  if (!items || items.length === 0) return 0;
  const set = new Set();
  for (const it of items) {
    if (Array.isArray(it.tags)) {
      for (const tag of it.tags) {
        if (tag) set.add(tag);
      }
    }
  }
  return set.size;
}

function Sidebar({ route, onNavigate, version, historyItems, historyTotal }) {
  const items = historyItems || [];
  const counts = {
    history:    historyTotal != null ? historyTotal : items.length,
    favorites:  0,  // Phase 2B-3 후속 — favorites 기능 추가 시 wiring
    recent:     recentItemCount(items, RECENT_DAYS),
    tags:       uniqueTagCount(items),
  };

  const libraryItems = [
    { icon: 'star',     label: '즐겨찾기', count: counts.favorites },
    { icon: 'schedule', label: '최근 7일', count: counts.recent },
    { icon: 'label',    label: '태그',     count: counts.tags },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__brand-logo">G</div>
        <div>
          <div className="sidebar__brand-name">GuruNote</div>
          <div className="sidebar__brand-ver">v{version || '?.?.?'}</div>
        </div>
      </div>

      <button
        type="button"
        className="sidebar__cta"
        onClick={() => onNavigate('main')}
      >
        <span className="msi">add</span>
        <span>새 노트 만들기</span>
        <span className="sidebar__cta-shortcut">⌘N</span>
      </button>

      <nav className="sidebar__nav-group" aria-label="주 메뉴">
        {NAV_ITEMS.map((item) => {
          const badge = item.countKey ? counts[item.countKey] : null;
          return (
            <button
              key={item.id}
              type="button"
              className={
                'sidebar__nav-item' +
                (route === item.id ? ' sidebar__nav-item--active' : '')
              }
              onClick={() => onNavigate(item.id)}
              aria-current={route === item.id ? 'page' : undefined}
            >
              <span className="msi">{item.icon}</span>
              <span>{item.label}</span>
              {badge != null && badge > 0 && (
                <span className="sidebar__nav-badge">{badge}</span>
              )}
            </button>
          );
        })}
      </nav>

      <nav className="sidebar__nav-group" aria-label="라이브러리">
        <div className="sidebar__nav-label">라이브러리</div>
        {libraryItems.map((item) => (
          <button
            key={item.label}
            type="button"
            className="sidebar__nav-item"
            onClick={() => {/* Phase 2B-3 후속에서 wiring */}}
          >
            <span className="msi">{item.icon}</span>
            <span>{item.label}</span>
            {item.count > 0 && (
              <span className="sidebar__nav-badge">{item.count}</span>
            )}
          </button>
        ))}
      </nav>

      <div className="sidebar__spacer" />

      {/* 사용자 footer 는 폐기. 추후 멀티 유저 시 추가 (사용자 결정). */}
    </aside>
  );
}

window.Sidebar = Sidebar;
