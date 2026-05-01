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

  // Phase 2B-6d: 히스토리 sub-context — '라이브러리' 아래의 어느 진입점인지 추적.
  //   null      = 메인 nav 직접 진입 (default 'history')
  //   'recent'  = 사이드바 '최근 7일' 진입
  //   'tags'    = 사이드바 '태그' 진입
  //   handleLibraryNav 가 set, handleSidebarNavigate('history') 가 clear.
  //   TopBar 의 title 동적 변경에 사용 (breadcrumbs ['라이브러리'] + h2 '최근 7일' 등).
  const [historyContext, setHistoryContext] = useState(null);

  // Phase 2B-5b-2 + 2B-6d: Sidebar 메인 nav 클릭 wrapper.
  //   - '노트 편집' → currentJobId reset (stale fetch 회피, Step 2B-5b-2)
  //   - '히스토리'  → historyContext clear (라이브러리 sub-context 잔재 회피)
  //   - 카드 [편집] 액션의 navigateToEditor 는 이 핸들러를 거치지 않으므로 명시적
  //     jobId 흐름은 무손상.
  const handleSidebarNavigate = useCallback((target) => {
    if (target === 'editor') {
      setCurrentJobId(null);
    }
    if (target === 'history') {
      setHistoryContext(null);
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
      setHistoryContext('recent');
      setRoute('history');
    } else if (libType === 'tags') {
      setHistoryFilter({ initialExpandedGroup: 'tag' });
      setHistoryFilterKey((k) => k + 1);
      setHistoryContext('tags');
      setRoute('history');
    }
    // 'favorites' is disabled; no handler invocation.
  }, []);

  // Phase 2B-6d: SearchPalette (⌘K) state.
  //   open=true 시 SearchPalette 마운트, false 시 언마운트.
  //   Trigger: ⌘K 글로벌 keydown / TopBar gn-search onClick / Esc 로 close.
  const [searchPaletteOpen, setSearchPaletteOpen] = useState(false);
  const openSearchPalette = useCallback(() => setSearchPaletteOpen(true), []);
  const closeSearchPalette = useCallback(() => setSearchPaletteOpen(false), []);
  const handlePaletteSelect = useCallback((item) => {
    setSearchPaletteOpen(false);
    if (item?.job_id) {
      setCurrentJobId(item.job_id);
      setRoute('editor');
    }
  }, []);

  // Phase 2B-6d: 새 노트 만들기 CTA (⌘N) — counter pattern (historyFilterKey 와 동일).
  //   Sidebar CTA 클릭 또는 ⌘N keydown 시 increment + setRoute('main').
  //   MainScreen 이 prop 으로 받아 useEffect 로 form reset (url + selectedFile).
  //   진행 중 (running) 가드는 MainScreen 내부에서 처리.
  const [newNoteRequestKey, setNewNoteRequestKey] = useState(0);
  const handleNewNote = useCallback(() => {
    setNewNoteRequestKey((k) => k + 1);
    setRoute('main');
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

  // Phase 2B-6d: 글로벌 keydown — ⌘K (SearchPalette open) + ⌘N (새 노트).
  //   ⌘S 는 EditorScreen 내부 listener 가 담당 (충돌 없음 — 다른 키).
  //   SearchPalette 의 자체 Esc 처리는 SearchPalette 내부에서 (open 시만 등록).
  useEffect(() => {
    const onKey = (e) => {
      if (!(e.metaKey || e.ctrlKey)) return;
      const k = e.key.toLowerCase();
      if (k === 'k') {
        e.preventDefault();
        setSearchPaletteOpen(true);
      } else if (k === 'n') {
        e.preventDefault();
        handleNewNote();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [handleNewNote]);

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
            onNewNote={handleNewNote}
          />
          <main className="gn-main">
            <TopBar
              route={route}
              historyContext={historyContext}
              onSearchOpen={openSearchPalette}
            />
            <div className="gn-content">{
            route === 'main'    ? <MainScreen newNoteRequestKey={newNoteRequestKey} /> :
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
      <SearchPalette
        open={searchPaletteOpen}
        items={historyItems}
        onClose={closeSearchPalette}
        onSelect={handlePaletteSelect}
      />
      <div id="toast-container" className="toast-container" />
    </>
  );
}

window.App = App;
