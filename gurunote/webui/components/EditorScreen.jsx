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

const EDITOR_TABS = [
  { id: 'summary', label: '요약',     icon: 'auto_awesome' },
  { id: 'korean',  label: '한국어',   icon: 'translate' },
  { id: 'english', label: '영어 원문', icon: 'description' },
];

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
          throw new Error(result?.error || 'get_history_detail failed');
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
        <div className="editor-empty" style={{ color: 'var(--gn-danger)' }}>
          {error}
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
            {EDITOR_TABS.map((tab) => (
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

          {activeTab === 'korean' && (
            <div className="editor-content">
              <div className="editor-empty" style={{ paddingTop: 80 }}>
                <span className="msi">translate</span>
                <div>한국어 transcript 표시는 Phase 2B-4 후속 wiring 예정입니다.</div>
              </div>
            </div>
          )}

          {activeTab === 'english' && (
            <div className="editor-content">
              <div className="editor-empty" style={{ paddingTop: 80 }}>
                <span className="msi">description</span>
                <div>영어 원문 transcript 표시는 Phase 2B-4 후속 wiring 예정입니다.</div>
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
                <button type="button" className="editor-side__action" onClick={() => window.showToast?.('Phase 2B-3 후속 — 연관 노트 추천')}>
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
                  onClick={() => window.showToast?.('Phase 2B-4 후속 — 삭제 wiring 예정')}
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
