
/* global React, ReactDOM, Icon, Btn, MainScreen, HistoryScreen, EditorScreen, DashboardScreen, SettingsScreen */
const { useState, useEffect, useMemo } = React;

/* ============================================================
   Tweaks — persisted defaults
   ============================================================ */
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "blue",
  "density": "default",
  "showTweaks": false
}/*EDITMODE-END*/;

/* ============================================================
   Sidebar
   ============================================================ */
function Sidebar({ route, setRoute }) {
  const nav = [
    { k: 'main',      icon: 'auto_awesome',       label: '생성',           badge: null },
    { k: 'history',   icon: 'history',            label: '히스토리',       badge: '87' },
    { k: 'editor',    icon: 'edit_note',          label: '노트 편집',      badge: null },
    { k: 'dashboard', icon: 'insights',           label: '대시보드',       badge: null },
    { k: 'settings',  icon: 'settings',           label: '설정',           badge: null },
  ];
  const quick = [
    { icon: 'star',       label: '즐겨찾기',       badge: '6' },
    { icon: 'schedule',   label: '최근 7일',       badge: '14' },
    { icon: 'label',      label: '태그',           badge: '32' },
  ];
  return (
    <aside className="gn-sidebar">
      <div className="gn-brand">
        <div className="logo">G</div>
        <div>
          <div className="name">GuruNote</div>
          <div className="ver">v0.8.0.6</div>
        </div>
      </div>

      <button className="gn-cta" onClick={() => setRoute('main')}>
        <Icon name="add" />
        <span>새 노트 만들기</span>
        <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--gn-on-surface-muted)', fontFamily: 'var(--font-mono)' }}>⌘N</span>
      </button>

      <div className="gn-nav-group">
        {nav.map(n => (
          <div
            key={n.k}
            className={`gn-nav-item ${route === n.k ? 'active' : ''}`}
            onClick={() => setRoute(n.k)}
          >
            <Icon name={n.icon} />
            <span>{n.label}</span>
            {n.badge && <span className="badge">{n.badge}</span>}
          </div>
        ))}
      </div>

      <div className="gn-nav-group">
        <div className="gn-nav-label">라이브러리</div>
        {quick.map(n => (
          <div key={n.label} className="gn-nav-item">
            <Icon name={n.icon} />
            <span>{n.label}</span>
            {n.badge && <span className="badge">{n.badge}</span>}
          </div>
        ))}
      </div>

      <div className="gn-sidebar-spacer" />

      <div className="gn-sidebar-footer">
        <div className="gn-avatar">JS</div>
        <div className="who">
          <div className="name">정승호</div>
          <div className="sub">Apple Silicon · M4 Max</div>
        </div>
        <button className="gn-iconbtn" style={{ marginLeft: 'auto', width: 32, height: 32 }}>
          <Icon name="more_vert" className="sm" />
        </button>
      </div>
    </aside>
  );
}

/* ============================================================
   App shell
   ============================================================ */
const ROUTES = {
  main:      { title: '생성',           crumb: ['GuruNote', '생성'] },
  history:   { title: '히스토리',       crumb: ['GuruNote', '라이브러리', '히스토리'] },
  editor:    { title: '노트 편집',      crumb: ['GuruNote', '편집기'] },
  dashboard: { title: '대시보드',       crumb: ['GuruNote', '대시보드'] },
  settings:  { title: '설정',           crumb: ['GuruNote', '설정'] },
};

function App() {
  const [route, setRoute] = useState('main');
  const [runState, setRunState] = useState('running'); // idle | running | done
  const [tweaksOpen, setTweaksOpen] = useState(false);
  const [tweaks, setTweaks] = useState(TWEAK_DEFAULTS);

  // Apply tweaks to body
  useEffect(() => {
    document.body.dataset.accent = tweaks.accent;
    document.body.dataset.density = tweaks.density;
  }, [tweaks]);

  // Persist route
  useEffect(() => {
    const saved = localStorage.getItem('gn:route');
    if (saved && ROUTES[saved]) setRoute(saved);
  }, []);
  useEffect(() => { localStorage.setItem('gn:route', route); }, [route]);

  // Tweaks host protocol
  useEffect(() => {
    const onMsg = (e) => {
      if (e.data?.type === '__activate_edit_mode') setTweaksOpen(true);
      if (e.data?.type === '__deactivate_edit_mode') setTweaksOpen(false);
    };
    window.addEventListener('message', onMsg);
    window.parent.postMessage({ type: '__edit_mode_available' }, '*');
    return () => window.removeEventListener('message', onMsg);
  }, []);

  const setTweak = (patch) => {
    const next = { ...tweaks, ...patch };
    setTweaks(next);
    window.parent.postMessage({ type: '__edit_mode_set_keys', edits: patch }, '*');
  };

  const meta = ROUTES[route];

  return (
    <div className="gn-window" data-screen-label="01 GuruNote App">
      {/* Titlebar */}
      <div className="gn-titlebar">
        <div className="gn-traffic">
          <span className="dot red"></span>
          <span className="dot yellow"></span>
          <span className="dot green"></span>
        </div>
        <div className="title">GuruNote — {meta.title}</div>
        <div style={{ width: 54 }} /> {/* balance traffic lights */}
      </div>

      <div className="gn-body">
        <Sidebar route={route} setRoute={setRoute} />

        <main className="gn-main">
          {/* Appbar */}
          <div className="gn-appbar">
            <div>
              <div className="crumbs">
                {meta.crumb.map((c, i) => (
                  <React.Fragment key={i}>
                    {i > 0 && <Icon name="chevron_right" />}
                    <span>{c}</span>
                  </React.Fragment>
                ))}
              </div>
              <h2>{meta.title}</h2>
            </div>

            <div className="gn-search">
              <Icon name="search" />
              <input placeholder="전체 노트 검색… (⌘K)" />
              <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--gn-on-surface-muted)', padding: '2px 6px', background: 'var(--gn-surface)', borderRadius: 4 }}>⌘K</span>
            </div>

            <button className="gn-iconbtn" title="알림"><Icon name="notifications" /></button>
            <button className="gn-iconbtn" title="도움말"><Icon name="help_outline" /></button>
            <button
              className={`gn-iconbtn ${runState === 'running' ? 'filled' : ''}`}
              title="실행 상태 토글"
              onClick={() => setRunState(runState === 'running' ? 'idle' : 'running')}
            >
              <Icon name={runState === 'running' ? 'pause' : 'play_arrow'} />
            </button>
          </div>

          {/* Content */}
          <div className="gn-content">
            {route === 'main'      && <MainScreen runState={runState} />}
            {route === 'history'   && <HistoryScreen />}
            {route === 'editor'    && <EditorScreen />}
            {route === 'dashboard' && <DashboardScreen />}
            {route === 'settings'  && <SettingsScreen />}
          </div>
        </main>
      </div>

      {/* Tweaks panel */}
      {tweaksOpen && (
        <div className="tweaks">
          <div className="tweaks-header">
            <Icon name="tune" className="sm" /> Tweaks
            <button className="gn-iconbtn" style={{ marginLeft: 'auto', width: 28, height: 28 }} onClick={() => setTweaksOpen(false)}>
              <Icon name="close" className="sm" />
            </button>
          </div>
          <div className="tweaks-body">
            <div className="tweak-row">
              <div className="label">악센트 컬러</div>
              <div className="swatches">
                {[
                  { k: 'blue',   c: '#1a73e8' },
                  { k: 'green',  c: '#188038' },
                  { k: 'red',    c: '#d93025' },
                  { k: 'purple', c: '#673ab7' },
                ].map(s => (
                  <div
                    key={s.k}
                    className={`tweak-swatch ${tweaks.accent === s.k ? 'active' : ''}`}
                    style={{ background: s.c }}
                    onClick={() => setTweak({ accent: s.k })}
                  />
                ))}
              </div>
            </div>
            <div className="tweak-row">
              <div className="label">밀도</div>
              <div className="seg" style={{ alignSelf: 'flex-start' }}>
                {['compact', 'default', 'spacious'].map(d => (
                  <button
                    key={d}
                    className={`seg-opt ${tweaks.density === d ? 'active' : ''}`}
                    onClick={() => setTweak({ density: d })}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>
            <div className="tweak-row">
              <div className="label">실행 상태 프리뷰</div>
              <div className="seg" style={{ alignSelf: 'flex-start' }}>
                {['idle', 'running', 'done'].map(s => (
                  <button
                    key={s}
                    className={`seg-opt ${runState === s ? 'active' : ''}`}
                    onClick={() => setRunState(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
