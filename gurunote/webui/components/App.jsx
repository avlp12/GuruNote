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

  // Phase 2B-5b-2: Sidebar 메인 nav 클릭 wrapper.
  //   - '노트 편집' 메인 nav 클릭은 특정 노트 컨텍스트가 없는 진입.
  //     stale currentJobId (이전 세션 / 이전 클릭의 잔재) 가 그대로 남아 깨진
  //     노트를 다시 fetch 하는 경우가 있음 → 명시적으로 null 로 reset 해서
  //     EditorScreen 의 empty state 분기로 안전하게 진입.
  //   - 카드 [편집] 액션의 navigateToEditor 는 이 핸들러를 거치지 않으므로
  //     명시적 jobId 흐름은 무손상.
  const handleSidebarNavigate = useCallback((target) => {
    if (target === 'editor') {
      setCurrentJobId(null);
    }
    setRoute(target);
  }, []);

  // History state — Sidebar 카운트 + HistoryScreen 그리드 공유.
  const [historyItems, setHistoryItems] = useState([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState(null);

  // Phase 2B-5a: 1-shot initial filter for HistoryScreen (sidebar library shortcuts).
  // Shape: { initialFacets?: Set, initialTimeWindow?: number, initialExpandedGroup?: string }
  // Cleared by HistoryScreen via onFilterApplied so subsequent direct nav (e.g.
  // "히스토리" main-nav click) doesn't re-apply a stale filter.
  const [historyFilter, setHistoryFilter] = useState(null);
  // Monotonic counter — incremented on every library nav so HistoryScreen's React
  // key changes, forcing a remount that re-runs useState initializers with the
  // new initial* props. onFilterApplied does NOT touch this, so resetting
  // historyFilter to null after mount doesn't trigger a second remount.
  const [historyFilterKey, setHistoryFilterKey] = useState(0);

  const handleLibraryNav = useCallback((libType) => {
    if (libType === 'recent') {
      setHistoryFilter({ initialTimeWindow: 7 });
      setHistoryFilterKey((k) => k + 1);
      setRoute('history');
    } else if (libType === 'tags') {
      setHistoryFilter({ initialExpandedGroup: 'tag' });
      setHistoryFilterKey((k) => k + 1);
      setRoute('history');
    }
    // 'favorites' is disabled; no handler invocation.
  }, []);

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
      <div className="gn-window">
        <div className="gn-body">
          <Sidebar
            route={route}
            onNavigate={handleSidebarNavigate}
            version={version}
            historyItems={historyItems}
            historyTotal={historyTotal}
            onLibraryNav={handleLibraryNav}
          />
          <main className="gn-main">
            <TopBar route={route} />
            <div className="gn-content">{
            route === 'main'    ? <MainScreen /> :
            route === 'history' ? (
              <HistoryScreen
                key={`history-${historyFilterKey}`}
                items={historyItems}
                total={historyTotal}
                loading={historyLoading}
                error={historyError}
                onReload={loadHistory}
                onEditNote={navigateToEditor}
                initialFacets={historyFilter?.initialFacets}
                initialTimeWindow={historyFilter?.initialTimeWindow}
                initialExpandedGroup={historyFilter?.initialExpandedGroup}
                onFilterApplied={() => setHistoryFilter(null)}
              />
            ) :
            route === 'editor' ? (
              <EditorScreen
                jobId={currentJobId}
                onBackToLibrary={() => setRoute('history')}
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
            route === 'settings' ? (
              <SettingsScreen />
            ) :
            <ScreenPlaceholder route={route} />
          }</div>
          </main>
        </div>
      </div>
      <div id="toast-container" className="toast-container" />
    </>
  );
}

window.App = App;
