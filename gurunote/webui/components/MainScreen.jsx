/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-2: MainScreen — 생성 화면 (URL/파일 입력 + 처리 + 결과).
 *
 * 디자인 spec (docs/design/v2-reference.html 시각 참고):
 *   - 토픽바 (breadcrumb + title)
 *   - 입력 카드 (URL + 파일 선택 XOR + 생성/중지)
 *   - STT 엔진 + LLM Provider segment
 *   - 파이프라인 카드 (5-step indicator + progress + meta)
 *   - 결과 카드 (4탭: 요약/한국어/영어/Log)
 *
 * Bridge wiring:
 *   - pick_file → {path, size}
 *   - start_pipeline / stop_pipeline → 파이프라인 제어
 *   - get_settings → STT/LLM 기본값
 *   - window.__emit 으로 들어오는 progress / log / log_batch / result 구독
 */

const { useState, useEffect, useRef, useCallback } = React;

const SUPPORTED_AUDIO = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma', '.opus'];
const SUPPORTED_VIDEO = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.wmv', '.flv', '.ts', '.m4v'];
const SUPPORTED_EXTS = new Set([...SUPPORTED_AUDIO, ...SUPPORTED_VIDEO]);

const STT_OPTIONS = ['auto', 'whisperx', 'mlx', 'assemblyai'];
const LLM_OPTIONS = [
  { value: 'openai',            label: 'openai' },
  { value: 'anthropic',         label: 'anthropic' },
  { value: 'gemini',            label: 'gemini' },
  { value: 'openai_compatible', label: 'local' },
];

// 5-step pipeline thresholds (gui.py 와 동일).
const STEP_THRESHOLDS = [0.18, 0.55, 0.78, 0.90, 1.0];
const STEP_LABELS = ['오디오', 'STT', '번역', '요약', '조립'];

const RESULT_TABS = [
  { id: 'summary', label: '요약',     icon: 'auto_awesome' },
  { id: 'korean',  label: '한국어',   icon: 'translate' },
  { id: 'english', label: '영어 원문', icon: 'description' },
  { id: 'log',     label: 'Log',      icon: 'terminal' },
];

/* === Helpers === */
function getExt(path) {
  const i = path.lastIndexOf('.');
  return i < 0 ? '' : path.slice(i).toLowerCase();
}
function basename(path) {
  const i = Math.max(path.lastIndexOf('/'), path.lastIndexOf('\\'));
  return i < 0 ? path : path.slice(i + 1);
}
function formatSize(bytes) {
  if (bytes == null) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1073741824) return `${(bytes / 1048576).toFixed(1)} MB`;
  return `${(bytes / 1073741824).toFixed(2)} GB`;
}
function formatTime(sec) {
  if (sec == null || sec < 0) return '';
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}
function humanizeError(err) {
  const msg = (err && err.message) || String(err);
  const m = msg.match(/^([A-Z_]+):(.*)$/);
  if (!m) return msg;
  const [, code, detail] = m;
  switch (code) {
    case 'INVALID_URL': return '유튜브 URL 형식이 아닙니다.';
    case 'INVALID_LOCAL_FILE': return `지원되지 않는 파일입니다: ${detail}`;
    case 'API_KEY_MISSING': return `API 키가 설정되지 않았습니다: ${detail}`;
    case 'NO_ACTIVE_SESSION': return '실행 중인 작업이 없습니다.';
    default: return msg;
  }
}

/* === Toast (전역 helper, App 에서 mount 한 toast container 사용) === */
function showToast(message, kind) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const t = document.createElement('div');
  t.className = 'toast' + (kind ? ` toast--${kind}` : '');
  t.textContent = message;
  container.appendChild(t);
  requestAnimationFrame(() => t.classList.add('toast--visible'));
  setTimeout(() => {
    t.classList.remove('toast--visible');
    setTimeout(() => t.remove(), 200);
  }, 4000);
}
window.showToast = showToast;

/* === StepIndicator === */
function StepIndicator({ pct }) {
  return (
    <div className="steps">
      {STEP_LABELS.map((label, i) => (
        <React.Fragment key={i}>
          <div className={
            'step-node' +
            (pct >= STEP_THRESHOLDS[i] ? ' step-node--done' :
             (i === 0 && pct > 0) || (i > 0 && pct >= STEP_THRESHOLDS[i-1]) ? ' step-node--active' : '')
          }>
            {pct >= STEP_THRESHOLDS[i] ? '✓' : i + 1}
          </div>
          {i < STEP_LABELS.length - 1 && (
            <div className={
              'step-connector' +
              (pct >= STEP_THRESHOLDS[i] ? ' step-connector--done' : '')
            } />
          )}
        </React.Fragment>
      ))}
      {STEP_LABELS.map((label, i) => (
        <React.Fragment key={`l-${i}`}>
          <div className={
            'step-label' +
            (pct >= STEP_THRESHOLDS[i] || (i > 0 && pct >= STEP_THRESHOLDS[i-1]) ? ' step-label--active' : '')
          }>{label}</div>
          {i < STEP_LABELS.length - 1 && <div />}
        </React.Fragment>
      ))}
    </div>
  );
}

/* === ResultPanel — 4탭 === */
function ResultPanel({ result, log }) {
  const [activeTab, setActiveTab] = useState('summary');

  if (!result && !log.length) {
    return (
      <div className="result-empty">
        파이프라인을 실행하면 여기에 결과가 표시됩니다.
      </div>
    );
  }

  return (
    <>
      <div className="result-tabs">
        {RESULT_TABS.map(tab => (
          <button
            key={tab.id}
            type="button"
            className={'result-tab' + (activeTab === tab.id ? ' result-tab--active' : '')}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="msi" style={{ fontSize: 16, marginRight: 6 }}>{tab.icon}</span>
            {tab.label}
            {tab.id === 'log' && log.length > 0 && (
              <span className="result-tab__count">{log.length}</span>
            )}
          </button>
        ))}
      </div>

      {activeTab === 'summary' && result?.full_html && (
        <div className="result-rendered" dangerouslySetInnerHTML={{ __html: result.full_html }} />
      )}
      {activeTab === 'summary' && !result?.full_html && (
        <div className="result-empty">처리 완료 후 요약이 표시됩니다.</div>
      )}

      {activeTab === 'korean' && (
        <div className="result-empty">
          {result?.korean_transcript || '처리 완료 후 표시됩니다.'}
        </div>
      )}

      {activeTab === 'english' && (
        <div className="result-empty">
          {result?.english_transcript || '처리 완료 후 표시됩니다.'}
        </div>
      )}

      {activeTab === 'log' && (
        <div className="log-pane">
          {log.length === 0 ? '대기 중...' : log.join('\n')}
        </div>
      )}
    </>
  );
}

/* === MainScreen === */
function MainScreen({ newNoteRequestKey }) {
  // 입력 상태
  const [url, setUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState(null); // { path, size } or null
  const [stt, setStt] = useState('auto');
  const [llm, setLlm] = useState('openai');
  const [dragOver, setDragOver] = useState(false);

  // 파이프라인 상태
  const [running, setRunning] = useState(false);
  const [pct, setPct] = useState(0);
  const [stage, setStage] = useState(null);
  const [log, setLog] = useState([]);
  const [result, setResult] = useState(null);
  const [startedAt, setStartedAt] = useState(null);
  const [now, setNow] = useState(Date.now());
  const jobIdRef = useRef(null);

  // Phase 2B-6d: 새 노트 만들기 (CTA / ⌘N) — counter prop 변경 시 form reset.
  //   사용자 결정 (C-1 가): url + selectedFile 만 clear, STT/LLM 보존.
  //   진행 중 (running) 가드 — 처리 중에는 reset 막고 toast.
  //   처음 mount 시 (newNoteRequestKey === 0) 는 skip — 초기 mount 가 reset 트리거 안 됨.
  useEffect(() => {
    if (!newNoteRequestKey) return;
    if (running) {
      if (window.showToast) window.showToast('처리 중입니다. 완료 후 새로 시작하세요.', 'warning');
      return;
    }
    setUrl('');
    setSelectedFile(null);
    if (window.showToast) window.showToast('새 노트 — URL 또는 파일을 입력하세요.', 'info');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [newNoteRequestKey]);

  // bridge probe — 기본 STT/LLM 설정
  useEffect(() => {
    let cancelled = false;
    const probe = async () => {
      while (!window.pywebview?.api && !cancelled) {
        await new Promise(r => setTimeout(r, 50));
      }
      if (cancelled) return;
      try {
        const settings = await window.pywebview.api.get_settings();
        if (cancelled) return;
        if (settings?.values?.LLM_PROVIDER) {
          setLlm(settings.values.LLM_PROVIDER);
        }
      } catch (e) {
        console.warn('[MainScreen] get_settings failed:', e);
      }
    };
    probe();
    return () => { cancelled = true; };
  }, []);

  // 경과 시간 ticker (running 시만)
  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [running]);

  // bridge event bus 구독 — session.py 가 evaluate_js("window.__emit(...)") 로 push
  useEffect(() => {
    if (!window.bus) {
      window.bus = new EventTarget();
      window.__emit = (name, payload) =>
        window.bus.dispatchEvent(new CustomEvent(name, { detail: payload }));
    }

    const onProgress = (e) => {
      if (typeof e.detail?.pct === 'number') setPct(e.detail.pct);
    };
    const onLog = (e) => {
      if (e.detail?.line) setLog(prev => [...prev, e.detail.line]);
    };
    const onLogBatch = (e) => {
      if (Array.isArray(e.detail?.lines)) setLog(prev => [...prev, ...e.detail.lines]);
    };
    const onStageChange = (e) => {
      if (e.detail?.stage) setStage(e.detail.stage);
    };
    const onResult = (e) => {
      const payload = e.detail || {};
      setRunning(false);
      jobIdRef.current = null;
      if (!payload.ok) {
        showToast(`파이프라인 실패: ${payload.error || '알 수 없는 오류'}`, 'error');
        setResult(null);
        return;
      }
      setPct(1.0);
      setResult(payload);
    };

    window.bus.addEventListener('progress', onProgress);
    window.bus.addEventListener('log', onLog);
    window.bus.addEventListener('log_batch', onLogBatch);
    window.bus.addEventListener('stage_change', onStageChange);
    window.bus.addEventListener('result', onResult);

    return () => {
      window.bus.removeEventListener('progress', onProgress);
      window.bus.removeEventListener('log', onLog);
      window.bus.removeEventListener('log_batch', onLogBatch);
      window.bus.removeEventListener('stage_change', onStageChange);
      window.bus.removeEventListener('result', onResult);
    };
  }, []);

  // XOR 토글: URL 입력 시 파일 비움 (값이 실제 입력된 경우만)
  const handleUrlChange = (e) => {
    const v = e.target.value;
    setUrl(v);
    if (v && selectedFile) setSelectedFile(null);
  };

  // XOR 토글: 파일 선택 성공 시 URL 비움
  const handlePickFile = useCallback(async () => {
    try {
      const result = await window.pywebview.api.pick_file();
      if (!result?.path) return; // cancelled — preserve URL
      const ext = getExt(result.path);
      if (!SUPPORTED_EXTS.has(ext)) {
        showToast(
          `지원하지 않는 형식입니다: ${ext}\n지원: ${[...SUPPORTED_AUDIO, ...SUPPORTED_VIDEO].join(' ')}`,
          'warning'
        );
        return;
      }
      setSelectedFile({ path: result.path, size: result.size });
      if (url) setUrl('');
    } catch (e) {
      console.error('[pick_file]', e);
      showToast(`파일 선택 오류: ${e.message || e}`, 'error');
    }
  }, [url]);

  const handleRemoveFile = () => setSelectedFile(null);

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    const files = e.dataTransfer?.files;
    if (!files || files.length === 0) return;
    if (files.length > 1) {
      showToast('파일은 1개만 선택할 수 있습니다.', 'warning');
      return;
    }
    const f = files[0];
    const fullPath = f.pywebviewFullPath || f.name;
    if (!SUPPORTED_EXTS.has(getExt(fullPath))) {
      showToast(`지원하지 않는 형식입니다: ${getExt(fullPath)}`, 'warning');
      return;
    }
    setSelectedFile({ path: fullPath, size: typeof f.size === 'number' ? f.size : null });
    if (url) setUrl('');
  };

  // 생성하기
  const handleRun = async () => {
    let source;
    if (selectedFile) {
      source = { kind: 'local', value: selectedFile.path, engine: stt, provider: llm };
    } else if (url.trim()) {
      source = { kind: 'youtube', value: url.trim(), engine: stt, provider: llm };
    } else {
      showToast('URL 또는 파일을 먼저 선택하세요.', 'warning');
      return;
    }

    setRunning(true);
    setPct(0);
    setStage(null);
    setLog([]);
    setResult(null);
    setStartedAt(Date.now());
    setNow(Date.now());

    try {
      const r = await window.pywebview.api.start_pipeline(source);
      jobIdRef.current = r.job_id;
    } catch (e) {
      console.error('[start_pipeline]', e);
      showToast(humanizeError(e), 'error');
      setRunning(false);
    }
  };

  // 중지
  const handleStop = async () => {
    if (!jobIdRef.current) return;
    try {
      await window.pywebview.api.stop_pipeline(jobIdRef.current);
      showToast('중지 요청을 보냈습니다. 현재 단계가 끝나면 중지됩니다.');
    } catch (e) {
      showToast(humanizeError(e), 'error');
    }
  };

  const canRun = !running && (selectedFile || url.trim());
  const elapsed = startedAt ? Math.floor((now - startedAt) / 1000) : 0;

  return (
    <div className="main-screen">
      {/* === 입력 카드 === */}
      <section className="card">
        <div className="card__header">
          <div>
            <div className="card__title">지식을 증류하세요</div>
            <div className="card__sub">유튜브 링크 또는 로컬 오디오/비디오 파일에서 화자 분리된 한국어 요약본을 생성합니다.</div>
          </div>
          <span className="card__chip">
            <span className="msi" style={{ fontSize: 14 }}>memory</span>
            Apple Silicon · MLX
          </span>
        </div>

        <div className="input-row">
          <input
            type="text"
            className={'url-input' + (dragOver ? ' url-input--drag-over' : '')}
            placeholder="🔗  https://youtube.com/watch?v=…  또는 파일을 드래그하여 놓으세요"
            value={url}
            onChange={handleUrlChange}
            disabled={running}
            onDragEnter={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragOver={(e) => e.preventDefault()}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            autoComplete="off"
          />
          <button type="button" className="btn btn--ghost" onClick={handlePickFile} disabled={running}>
            <span className="msi">folder_open</span>
            파일 선택
          </button>
          {!running && (
            <button type="button" className="btn btn--primary" onClick={handleRun} disabled={!canRun}>
              <span className="msi">play_arrow</span>
              생성하기
            </button>
          )}
          {running && (
            <button type="button" className="btn btn--ghost" onClick={handleStop}>
              <span className="msi">stop</span>
              중지
            </button>
          )}
        </div>

        {selectedFile && (
          <div className="file-badge">
            <span className="file-badge__icon msi">
              {SUPPORTED_VIDEO.includes(getExt(selectedFile.path)) ? 'movie' : 'music_note'}
            </span>
            <span className="file-badge__name" title={selectedFile.path}>{basename(selectedFile.path)}</span>
            {selectedFile.size != null && (
              <span className="file-badge__size">{formatSize(selectedFile.size)}</span>
            )}
            <button type="button" className="file-badge__remove" onClick={handleRemoveFile} aria-label="파일 선택 취소">
              <span className="msi" style={{ fontSize: 16 }}>close</span>
            </button>
          </div>
        )}

        <div className="options-row">
          <div className="opt-group">
            <div className="opt-group__label">STT 엔진</div>
            <div className="segmented">
              {STT_OPTIONS.map(opt => (
                <button
                  key={opt}
                  type="button"
                  className={'seg-opt' + (stt === opt ? ' seg-opt--active' : '')}
                  onClick={() => setStt(opt)}
                  disabled={running}
                >{opt}</button>
              ))}
            </div>
          </div>

          <div className="opt-group">
            <div className="opt-group__label">LLM Provider</div>
            <div className="segmented">
              {LLM_OPTIONS.map(opt => (
                <button
                  key={opt.value}
                  type="button"
                  className={'seg-opt' + (llm === opt.value ? ' seg-opt--active' : '')}
                  onClick={() => setLlm(opt.value)}
                  disabled={running}
                >{opt.label}</button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* === 파이프라인 카드 === */}
      <section className="card">
        <div className="card__header">
          <div className="card__title" style={{ fontSize: 16 }}>파이프라인</div>
          <span style={{ fontSize: 13, color: 'var(--gn-on-surface-muted)' }}>
            {running ? (stage || '처리 중…') : '대기'}
          </span>
        </div>

        <StepIndicator pct={pct} />

        <div className={'progress' + (running ? '' : ' progress--idle')}>
          <div className="progress__bar">
            <div className="progress__fill" style={{ width: `${pct * 100}%` }} />
          </div>
          <div className="progress__meta">
            <span>{Math.round(pct * 100)}%</span>
            <span>{formatTime(elapsed)} 경과</span>
          </div>
        </div>
      </section>

      {/* === 결과 카드 === */}
      <section className="card">
        <div className="card__header">
          <div className="card__title" style={{ fontSize: 16 }}>
            {result?.video_title || '결과'}
          </div>
        </div>
        <ResultPanel result={result} log={log} />
      </section>
    </div>
  );
}

window.MainScreen = MainScreen;
