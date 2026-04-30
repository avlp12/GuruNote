/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-6a: 글로벌 TopBar — 전 화면 공통 헤더.
 *
 * Reference: docs/design/extracted/app-sidebar-and-routes.jsx:152-182 의 .gn-appbar
 *
 * Layout (좌→우):
 *   [breadcrumb + h2 title] · margin-left:auto → [search input + ⌘K chip]
 *
 * 사용자 결정 (Step 6a):
 *   - 우측 아이콘 3개 (알림 / 도움말 / pause/play) 제거 — 진짜 동작 갖춰지는
 *     시점에 부활 (정직, fake 동작 없음).
 *   - search input 은 readOnly + onClick 빈 stub — Phase 2B-6d 의 SearchPalette
 *     모달 wiring 시점에 활성화.
 *
 * Babel standalone global scope 회피: 모든 top-level const 는 TOPBAR_ 접두사.
 */

/* crumbs 정책 (사용자 결정):
 *   GuruNote 의 화면들은 모두 top-level nav 라 진짜 계층이 없음 ('GuruNote › 생성'
 *   의 마지막 segment 와 title 이 동일 → dead path). 의미 있는 path 만 유지.
 *   라이브러리 → 히스토리 만 진짜 계층. Phase 2B-6b 의 EditorScreen 재구조화 시
 *   jobId 있을 때 editor 의 crumbs 도 ['라이브러리'] 로 자연 진화.
 */
const TOPBAR_ROUTE_META = {
  main:      { crumbs: [],            title: '생성' },
  history:   { crumbs: ['라이브러리'], title: '히스토리' },
  editor:    { crumbs: [],            title: '노트 편집' },
  dashboard: { crumbs: [],            title: '대시보드' },
  settings:  { crumbs: [],            title: '설정' },
};

function TopBar({ route }) {
  const meta = TOPBAR_ROUTE_META[route] || { crumbs: [], title: route };
  const { crumbs, title } = meta;

  return (
    <div className="gn-appbar">
      <div className="gn-appbar__lead">
        {crumbs.length > 0 && (
          <div className="gn-appbar__crumbs">
            {crumbs.map((c, i) => (
              <React.Fragment key={i}>
                {i > 0 && <span className="msi gn-appbar__crumb-sep">chevron_right</span>}
                <span>{c}</span>
              </React.Fragment>
            ))}
          </div>
        )}
        <h2 className="gn-appbar__title">{title}</h2>
      </div>

      <div className="gn-search" onClick={() => { /* Phase 2B-6d: SearchPalette 모달 wiring */ }}>
        <span className="msi">search</span>
        <input
          type="text"
          className="gn-search__input"
          placeholder="전체 노트 검색..."
          readOnly
          aria-label="전체 노트 검색"
        />
        <span className="gn-search__shortcut">⌘K</span>
      </div>
    </div>
  );
}

window.TopBar = TopBar;
