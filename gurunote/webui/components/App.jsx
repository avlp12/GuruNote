/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-1 + 2B-2 + 2B-3c-rework: App — Sidebar + route-based screen switch.
 * Phase 2B-3c-rework: list_history state lifting — Sidebar 의 nav/library 카운트
 * 와 HistoryScreen 의 카드 그리드가 같은 데이터를 공유.
 */

const { useState, useEffect, useCallback } = React;

const ROUTE_LABELS = {
  main:      { title: '생성',      phase: '2B-2' },
  history:   { title: '히스토리',  phase: '2B-3' },
  editor:    { title: '노트 편집', phase: '2B-4' },
  dashboard: { title: '대시보드',  phase: '2B-4' },
  settings:  { title: '설정',      phase: '2B-4' },
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

  // Phase 2B-4a: 현재 편집 중인 job_id (HistoryScreen → EditorScreen 진입)
  const [currentJobId, setCurrentJobId] = useState(null);
  const navigateToEditor = useCallback((jobId) => {
    setCurrentJobId(jobId);
    setRoute('editor');
  }, []);

  // History state — Sidebar 카운트 + HistoryScreen 그리드 공유.
  const [historyItems, setHistoryItems] = useState([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState(null);

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      while (!window.pywebview?.api) {
        await new Promise((r) => setTimeout(r, 50));
      }
      const result = await window.pywebview.api.list_history();
      if (!result?.ok) {
        throw new Error(result?.error || 'list_history failed');
      }
      setHistoryItems(result.items || []);
      setHistoryTotal(result.total || 0);
    } catch (e) {
      console.error('[App] list_history failed:', e);
      setHistoryError(e.message || String(e));
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const probe = async () => {
      while (!window.pywebview?.api && !cancelled) {
        await new Promise((r) => setTimeout(r, 50));
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
    loadHistory();
    return () => { cancelled = true; };
  }, [loadHistory]);

  return (
    <>
      <div className="app-shell">
        <Sidebar
          route={route}
          onNavigate={setRoute}
          version={version}
          historyItems={historyItems}
          historyTotal={historyTotal}
        />
        <main className="app-main">
          {
            route === 'main'    ? <MainScreen /> :
            route === 'history' ? (
              <HistoryScreen
                items={historyItems}
                total={historyTotal}
                loading={historyLoading}
                error={historyError}
                onReload={loadHistory}
                onEditNote={navigateToEditor}
              />
            ) :
            route === 'editor' ? (
              <EditorScreen
                jobId={currentJobId}
                onBackToHistory={() => setRoute('history')}
              />
            ) :
            route === 'dashboard' ? (
              <DashboardScreen
                items={historyItems}
                total={historyTotal}
                loading={historyLoading}
                error={historyError}
                onReload={loadHistory}
              />
            ) :
            <ScreenPlaceholder route={route} />
          }
        </main>
      </div>
      <div id="toast-container" className="toast-container" />
    </>
  );
}

window.App = App;
