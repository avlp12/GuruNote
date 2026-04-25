/* GuruNote Sidebar — Phase 2A Step 3b
 * SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * 출처: docs/design/extracted/v2-extracted.html 의 Sidebar 컴포넌트
 * 클래스명은 추출된 material3.css 와 매치 (자식 셀렉터 패턴 .gn-brand .logo 등)
 *
 * nav 항목은 <div role="button" tabIndex={0}> 패턴 (Design 원본 + 키보드 접근성)
 * 라이브러리 group / 사이드바 footer 는 후속 step 에서 채움.
 */

const NAV_ITEMS = [
  { k: 'main',      icon: 'auto_awesome', label: '생성' },
  { k: 'history',   icon: 'history',      label: '히스토리' },
  { k: 'editor',    icon: 'edit_note',    label: '노트 편집' },
  { k: 'dashboard', icon: 'insights',     label: '대시보드' },
  { k: 'settings',  icon: 'settings',     label: '설정' },
];

function Sidebar({ activeRoute, onNavigate, version }) {
  const handleKeyActivate = (route) => (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onNavigate(route);
    }
  };

  return (
    <aside className="gn-sidebar">
      <div className="gn-brand">
        <div className="logo">G</div>
        <div>
          <div className="name">GuruNote</div>
          <div className="ver">{version || 'v—'}</div>
        </div>
      </div>

      <button className="gn-cta" onClick={() => onNavigate('main')}>
        <Icon name="add" />
        <span>새 노트 만들기</span>
        <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--gn-on-surface-muted)', fontFamily: 'var(--font-mono)' }}>⌘N</span>
      </button>

      <div className="gn-nav-group">
        {NAV_ITEMS.map((n) => (
          <div
            key={n.k}
            role="button"
            tabIndex={0}
            className={`gn-nav-item ${activeRoute === n.k ? 'active' : ''}`}
            onClick={() => onNavigate(n.k)}
            onKeyDown={handleKeyActivate(n.k)}
          >
            <Icon name={n.icon} />
            <span>{n.label}</span>
          </div>
        ))}
      </div>

      <div className="gn-sidebar-spacer" />
    </aside>
  );
}
