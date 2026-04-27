/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-1: App — Sidebar + route-based screen switch.
 * 5 화면은 inline placeholder — 본격 구현은 Step 2B-2 ~ 2B-4.
 */

const { useState, useEffect } = React;

const ROUTE_LABELS = {
  main:      { title: '생성',      crumb: '생성',      phase: '2B-2' },
  history:   { title: '히스토리',  crumb: '히스토리',  phase: '2B-3' },
  editor:    { title: '노트 편집', crumb: '노트 편집', phase: '2B-4' },
  dashboard: { title: '대시보드',  crumb: '대시보드',  phase: '2B-4' },
  settings:  { title: '설정',      crumb: '설정',      phase: '2B-4' },
};

function ScreenPlaceholder({ route }) {
  const meta = ROUTE_LABELS[route] || { title: route, phase: '?' };
  return (
    <div className="screen-placeholder">
      <h2>{meta.title}</h2>
      <p>이 화면은 Phase {meta.phase} 에서 본격 구현됩니다.</p>
    </div>
  );
}

function App() {
  const [route, setRoute] = useState('main');
  const [version, setVersion] = useState(null);

  // bridge probe — 사이드바 brand 의 버전 표시용
  useEffect(() => {
    let cancelled = false;
    const probe = async () => {
      while (!window.pywebview?.api && !cancelled) {
        await new Promise(r => setTimeout(r, 50));
      }
      if (cancelled) return;
      try {
        const info = await window.pywebview.api.get_app_info();
        if (!cancelled && info?.version) setVersion(info.version);
      } catch (e) {
        console.warn('[app] get_app_info failed:', e);
      }
    };
    probe();
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="app-shell">
      <Sidebar route={route} onNavigate={setRoute} version={version} />
      <main className="app-main">
        <ScreenPlaceholder route={route} />
      </main>
    </div>
  );
}

window.App = App;
