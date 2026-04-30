/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-4a: EditorScreen — 노트 편집 화면.
 *
 * 디자인 spec (docs/design/v2-reference.html):
 *   - 좌측 main: 4 탭 (요약/한국어/영어/Log) + 모드 토글 (읽기/편집)
 *   - 우측 sidebar (320px): 썸네일 + 메타 + 태그 + 액션
 *   - 1080px 이하 sidebar 자동 숨김 (responsive)
 *
 * Bridge wiring (실제 기존 메서드 활용):
 *   - get_history_detail({job_id}) → {ok, markdown, full_html, meta, filename}
 *   - update_note({job_id, markdown}) → {ok, path}  (Phase 2B-4a 에서 구현)
 *   - save_result_as({markdown, default_filename}) → {path, cancelled}
 */

const { useState, useEffect, useMemo } = React;

/* Phase 2B-4a-2: 사용자 발견 — '영어 원문' 라벨이 한국어 원본에는 부적절.
   탭 id/라벨 변경 + 한국어 detected 시 '번역' 탭 숨김 (번역 결과 = 원문 동일하므로 무의미). */
const EDITOR_TABS_BASE = [
  { id: 'summary',     label: '요약', icon: 'auto_awesome' },
  { id: 'translation', label: '번역', icon: 'translate', langDependent: true },
  { id: 'original',    label: '원문', icon: 'subject' },
];

/* Phase 2B-5b-2: bridge 의 _err code → 사용자 친화 한국어 메시지.
   향후 다른 code 발견 시 여기 추가해 일관성 유지 (raw e.message 폴백). */
const EDITOR_ERROR_MESSAGES = {
  HISTORY_NOT_FOUND: '이 노트의 결과 파일이 없습니다 (처리가 완료되지 않았을 수 있습니다).',
  INVALID_ID: '잘못된 노트 식별자입니다.',
  READ_FAILED: '노트를 읽는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
};

/* 한국어 detected 시 '번역' 탭 (langDependent) 제거. */
function getVisibleTabs(detectedLanguage) {
  const isKorean = detectedLanguage === 'ko' || detectedLanguage === 'kor' || detectedLanguage === 'korean';
  if (isKorean) return EDITOR_TABS_BASE.filter((t) => !t.langDependent);
  return EDITOR_TABS_BASE;
}

/* 한글/라틴 letter 비율 — backend 가 detected_language 미제공 시 fallback.
   Path 형태 입력은 basename + 확장자 제거 후 counting (로컬 파일 대비). */
function estimateKorean(s) {
  if (!s) return 0;
  const base = (s.split(/[\\/]/).pop() || '').replace(/\.[a-z0-9]+$/i, '');
  let korean = 0;
  let latin = 0;
  for (const ch of base) {
    const code = ch.codePointAt(0);
    if ((code >= 0xAC00 && code <= 0xD7A3) || (code >= 0x1100 && code <= 0x11FF)) korean++;
    else if (/[a-zA-Z]/.test(ch)) latin++;
  }
  const total = korean + latin;
  return total > 0 ? korean / total : 0;
}

function fmtDuration(sec) {
  if (sec == null || sec <= 0) return '';
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

/* === EditorScreen === */
function EditorScreen({ jobId, onBackToHistory }) {
  const [activeTab, setActiveTab] = useState('summary');
  const [mode, setMode] = useState('read'); // 'read' | 'edit'
  const [item, setItem] = useState(null);
  const [markdown, setMarkdown] = useState('');
  const [fullHtml, setFullHtml] = useState('');
  const [editedContent, setEditedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // jobId 가 바뀌면 get_history_detail 호출
  useEffect(() => {
    if (!jobId) {
      setItem(null);
      setMarkdown('');
      setFullHtml('');
      return undefined;
    }
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        while (!window.pywebview?.api && !cancelled) {
          await new Promise((r) => setTimeout(r, 50));
        }
        if (cancelled) return;
        const result = await window.pywebview.api.get_history_detail({ job_id: jobId });
        if (cancelled) return;
        if (!result?.ok) {
          // Phase 2B-5b-2: code 기반 한국어 메시지 (없으면 backend 의 raw error 폴백).
          const friendly = EDITOR_ERROR_MESSAGES[result?.code]
            || result?.error
            || 'get_history_detail failed';
          throw new Error(friendly);
        }
        setItem(result.meta || null);
        setMarkdown(result.markdown || '');
        setFullHtml(result.full_html || '');
        setEditedContent(result.markdown || '');
        setMode('read');
      } catch (e) {
        console.error('[EditorScreen] load:', e);
        if (!cancelled) setError(e.message || String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [jobId]);

  // Phase 2B-4a-2: detected_language 결정 — backend 미제공 시 fallback (title basename 한글 비율).
  // organized_title 은 LLM 번역이라 항상 한글 → fallback 에 사용 안 함.
  const detectedLang = item?.detected_language ||
    (item?.title && estimateKorean(item.title) > 0.5 ? 'ko' : null);
  const visibleTabs = useMemo(() => getVisibleTabs(detectedLang), [detectedLang]);

  // activeTab 이 숨겨진 탭이면 첫 visible 로 fallback
  useEffect(() => {
    if (!visibleTabs.find((t) => t.id === activeTab)) {
      setActiveTab(visibleTabs[0]?.id || 'summary');
    }
  }, [visibleTabs, activeTab]);

  const dirty = mode === 'edit' && editedContent !== markdown;

  const handleSave = async () => {
    if (!jobId || !dirty) return;
    try {
      const result = await window.pywebview.api.update_note({
        job_id: jobId,
        markdown: editedContent,
      });
      if (result?.ok) {
        setMarkdown(editedContent);
        // full_html 은 backend 서버사이드 렌더 — 빠른 갱신 위해 textarea 그대로 유지
        // (다음 read_job 시 자동 갱신)
        setMode('read');
        if (window.showToast) window.showToast('저장되었습니다.', 'success');
      } else {
        if (window.showToast) window.showToast(`저장 실패: ${result?.error || '알 수 없는 오류'}`, 'error');
      }
    } catch (e) {
      console.error('[EditorScreen] update_note:', e);
      if (window.showToast) window.showToast(`저장 오류: ${e.message || e}`, 'error');
    }
  };

  const handleDownload = async () => {
    if (!jobId || !markdown) return;
    const title = item?.organized_title || item?.title || 'GuruNote';
    const safeTitle = title.replace(/[\\/:*?"<>|]/g, '_').slice(0, 80);
    try {
      const result = await window.pywebview.api.save_result_as({
        markdown: dirty ? editedContent : markdown,
        default_filename: `${safeTitle}.md`,
      });
      if (result?.cancelled) return;
      if (result?.path) {
        if (window.showToast) window.showToast(`저장됨: ${result.path}`, 'success');
      } else {
        if (window.showToast) window.showToast(`다운로드 실패: ${result?.error || '알 수 없는 오류'}`, 'error');
      }
    } catch (e) {
      console.error('[EditorScreen] save_result_as:', e);
      if (window.showToast) window.showToast(`다운로드 오류: ${e.message || e}`, 'error');
    }
  };

  // jobId 없을 때 empty state
  if (!jobId) {
    return (
      <div className="editor-screen">
        <div className="editor-topbar">
          <div className="editor-topbar__crumbs">GuruNote · 노트 편집</div>
          <div className="editor-topbar__title">노트 편집</div>
        </div>
        <div className="editor-empty">
          <span className="msi">edit_note</span>
          <div>편집할 노트를 선택해주세요.</div>
          <button
            type="button"
            className="btn btn--ghost"
            onClick={onBackToHistory}
          >
            <span className="msi">history</span>
            라이브러리에서 선택
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="editor-screen">
        <div className="editor-empty">불러오는 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="editor-screen">
        <div className="editor-topbar">
          <div className="editor-topbar__crumbs">GuruNote · 노트 편집</div>
          <div className="editor-topbar__title">오류</div>
        </div>
        <div className="editor-empty">
          <span className="msi" style={{ color: 'var(--gn-danger)' }}>error</span>
          <div style={{ color: 'var(--gn-danger)' }}>{error}</div>
          <button
            type="button"
            className="btn btn--ghost"
            onClick={onBackToHistory}
          >
            <span className="msi">history</span>
            라이브러리로
          </button>
        </div>
      </div>
    );
  }

  const title = item?.organized_title || item?.title || '제목 없음';

  return (
    <div className="editor-screen">
      <div className="editor-topbar">
        <div className="editor-topbar__crumbs">
          GuruNote · 라이브러리 · 노트 편집
        </div>
        <div className="editor-topbar__title" title={title}>{title}</div>
      </div>

      <div className="editor-screen__body">
        {/* Main: tabs + mode + content */}
        <div className="editor-screen__main">
          <div className="editor-tabs">
            {visibleTabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={'editor-tab' + (activeTab === tab.id ? ' editor-tab--active' : '')}
                onClick={() => setActiveTab(tab.id)}
              >
                <span className="msi" style={{ fontSize: 16, marginRight: 6 }}>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === 'summary' && (
            <div className="editor-mode-bar">
              <span className="editor-mode-bar__label">모드</span>
              <div className="editor-mode-toggle" role="radiogroup" aria-label="편집 모드">
                <button
                  type="button"
                  role="radio"
                  aria-checked={mode === 'read'}
                  className={'editor-mode-btn' + (mode === 'read' ? ' editor-mode-btn--active' : '')}
                  onClick={() => setMode('read')}
                >
                  <span className="msi" style={{ fontSize: 14, marginRight: 4 }}>visibility</span>
                  읽기
                </button>
                <button
                  type="button"
                  role="radio"
                  aria-checked={mode === 'edit'}
                  className={'editor-mode-btn' + (mode === 'edit' ? ' editor-mode-btn--active' : '')}
                  onClick={() => setMode('edit')}
                >
                  <span className="msi" style={{ fontSize: 14, marginRight: 4 }}>edit</span>
                  편집
                </button>
              </div>
              {mode === 'edit' && (
                <button
                  type="button"
                  className="btn btn--primary editor-mode-bar__save"
                  style={{ height: 32, padding: '0 14px', fontSize: 12, minWidth: 0 }}
                  onClick={handleSave}
                  disabled={!dirty}
                >
                  저장
                </button>
              )}
            </div>
          )}

          {activeTab === 'summary' && mode === 'read' && (
            <div
              className="editor-content editor-content--rendered"
              dangerouslySetInnerHTML={{ __html: fullHtml }}
            />
          )}

          {activeTab === 'summary' && mode === 'edit' && (
            <textarea
              className="editor-content__textarea"
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              spellCheck={false}
            />
          )}

          {activeTab === 'translation' && (
            <div className="editor-content">
              <div className="editor-empty" style={{ paddingTop: 80 }}>
                <span className="msi">translate</span>
                <div>Phase 2B-3-backend 에서 wiring 됩니다 (transcript 필드 추가).</div>
                <div style={{ fontSize: 12, marginTop: 8 }}>
                  (read_job 결과에 transcript_korean 필드가 추가되면 자동 표시)
                </div>
              </div>
            </div>
          )}

          {activeTab === 'original' && (
            <div className="editor-content">
              <div className="editor-empty" style={{ paddingTop: 80 }}>
                <span className="msi">subject</span>
                <div>Phase 2B-3-backend 에서 wiring 됩니다 (transcript 필드 추가).</div>
                <div style={{ fontSize: 12, marginTop: 8 }}>
                  (read_job 결과에 transcript_original 필드가 추가되면 자동 표시)
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar: thumb + meta + tags + actions */}
        {item && (
          <aside className="editor-screen__side">
            <div className="editor-side__thumb">
              {item.thumbnail_url && <img src={item.thumbnail_url} alt={title} />}
            </div>

            <div className="editor-side__section">
              <div className="editor-side__section-title">메타 정보</div>
              <dl className="editor-side__meta">
                {item.field        && (<><dt>주제</dt><dd>{item.field}</dd></>)}
                {item.uploader     && (<><dt>업로더</dt><dd>{item.uploader}</dd></>)}
                {item.upload_date  && (<><dt>업로드일</dt><dd>{item.upload_date}</dd></>)}
                {item.duration_sec > 0 && (<><dt>길이</dt><dd>{fmtDuration(item.duration_sec)}</dd></>)}
                {item.num_speakers > 0 && (<><dt>화자 수</dt><dd>{item.num_speakers}명</dd></>)}
                {item.stt_engine   && (<><dt>STT</dt><dd>{item.stt_engine}</dd></>)}
                {item.llm_provider && (<><dt>LLM</dt><dd>{item.llm_provider}</dd></>)}
              </dl>
            </div>

            {item.tags && item.tags.length > 0 && (
              <div className="editor-side__section">
                <div className="editor-side__section-title">태그</div>
                <div className="editor-side__tags">
                  {item.tags.map((tag) => (
                    <span key={tag} className="editor-side__tag">{tag}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="editor-side__section">
              <div className="editor-side__section-title">액션</div>
              <div className="editor-side__actions">
                <button type="button" className="editor-side__action" onClick={handleDownload}>
                  <span className="msi">download</span>
                  마크다운 다운로드
                </button>
                <button type="button" className="editor-side__action" onClick={() => window.showToast?.('Phase 3A (RAG) 에서 활성화')}>
                  <span className="msi">hub</span>
                  연관 노트
                </button>
                <button type="button" className="editor-side__action" onClick={onBackToHistory}>
                  <span className="msi">arrow_back</span>
                  라이브러리로
                </button>
                <button
                  type="button"
                  className="editor-side__action editor-side__action--danger"
                  onClick={() => window.showToast?.('Phase 2B-3-backend 에서 활성화')}
                >
                  <span className="msi">delete</span>
                  노트 삭제
                </button>
              </div>
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}

window.EditorScreen = EditorScreen;
