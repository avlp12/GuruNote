/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-1: Sidebar — 우리 코드 (디자인 spec 참고, 코드 cp 폐기).
 *
 * 디자인 spec (docs/design/v2-reference.html):
 *   - 좌측 260px width, 라이트 테마
 *   - G 로고 + GuruNote v0.8.0.6
 *   - "+ 새 노트 만들기" CTA (단축키 ⌘N)
 *   - 5 nav: 생성 / 히스토리 / 노트 편집 / 대시보드 / 설정
 *   - 라이브러리 section: 즐겨찾기 / 최근 7일 / 태그 (각 badge)
 *   - 사용자 footer 는 추후 멀티 유저 시 추가 (Phase 2B-1 폐기 결정)
 */

const NAV_ITEMS = [
  { id: 'main',      icon: 'auto_awesome',  label: '생성',      badge: null },
  { id: 'history',   icon: 'history',       label: '히스토리',  badge: null },
  { id: 'editor',    icon: 'edit_note',     label: '노트 편집', badge: null },
  { id: 'dashboard', icon: 'insights',      label: '대시보드',  badge: null },
  { id: 'settings',  icon: 'settings',      label: '설정',      badge: null },
];

// 라이브러리 carousel — 추후 bridge.list_history 연동 시 실제 카운트로 (Phase 2B-3).
// 지금은 정적 placeholder. 디자이너 mockup 의 6/14/32 는 사용 안 함.
const LIBRARY_ITEMS = [
  { icon: 'star',     label: '즐겨찾기' },
  { icon: 'schedule', label: '최근 7일' },
  { icon: 'label',    label: '태그' },
];

function Sidebar({ route, onNavigate, version }) {
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
        {NAV_ITEMS.map(item => (
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
            {item.badge != null && (
              <span className="sidebar__nav-badge">{item.badge}</span>
            )}
          </button>
        ))}
      </nav>

      <nav className="sidebar__nav-group" aria-label="라이브러리">
        <div className="sidebar__nav-label">라이브러리</div>
        {LIBRARY_ITEMS.map(item => (
          <button
            key={item.label}
            type="button"
            className="sidebar__nav-item"
            onClick={() => {/* Phase 2B-3 에서 wiring */}}
          >
            <span className="msi">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar__spacer" />

      {/* 사용자 footer 는 폐기. 추후 멀티 유저 시 추가 (사용자 결정). */}
    </aside>
  );
}

window.Sidebar = Sidebar;
