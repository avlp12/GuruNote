/* GuruNote MainScreen (idle minimal) — Phase 2A Step 3c
 * SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Minimal functional version — hero + 파일 선택 버튼 한 개.
 * 풍부한 Material 3 idle UI (drop zone, 최근 파일, URL 입력 등) 는 Commit 3.
 *
 * pywebview API 가 ready 되기 전 클릭 방지를 위해 isReady state 사용.
 * start_pipeline 은 backend 가 dict shape 요구 — local 파일 source 로 wrap.
 */

function MainScreen({ onStart }) {
  const [isReady, setIsReady] = React.useState(false);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const checkReady = () => {
      if (window.pywebview?.api) setIsReady(true);
    };
    checkReady();
    window.addEventListener('pywebviewready', checkReady);
    return () => window.removeEventListener('pywebviewready', checkReady);
  }, []);

  const handlePickFile = async () => {
    if (!isReady || busy) return;
    setError(null);
    setBusy(true);
    try {
      const picked = await window.pywebview.api.pick_file();
      if (!picked || picked.cancelled || !picked.path) {
        setBusy(false);
        return;
      }
      // backend start_pipeline expects {kind, value, engine, provider}
      const source = {
        kind: 'local',
        value: picked.path,
        engine: 'auto',
        provider: 'openai',
      };
      const result = await window.pywebview.api.start_pipeline(source);
      onStart?.(result?.job_id, picked.path);
    } catch (e) {
      console.error('pick_file or start_pipeline failed:', e);
      setError(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="gn-main">
      <div className="gn-content" style={{ padding: '60px 40px', textAlign: 'center' }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, marginBottom: 12 }}>
          새 노트를 만들어 보세요
        </h1>
        <p style={{ fontSize: 14, color: 'var(--gn-on-surface-muted)', marginBottom: 32 }}>
          오디오 또는 비디오 파일을 선택하면 자동으로 텍스트로 변환하고 지식 노트로 정리합니다.
        </p>
        <Btn
          variant="primary"
          onClick={handlePickFile}
          disabled={!isReady || busy}
        >
          <Icon name="upload_file" /> {busy ? '시작 중...' : '파일 선택'}
        </Btn>
        {!isReady && (
          <p style={{ fontSize: 12, color: 'var(--gn-on-surface-muted)', marginTop: 12 }}>
            pywebview 초기화 중...
          </p>
        )}
        {error && (
          <p style={{ fontSize: 12, color: 'var(--gn-danger)', marginTop: 12 }}>
            오류: {error}
          </p>
        )}
      </div>
    </main>
  );
}
