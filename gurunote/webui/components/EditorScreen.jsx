/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-6b: EditorScreen — split pane (Raw / Preview) + editor-head 액션 바.
 *
 * Reference: docs/design/extracted/screens-editor-dashboard-settings.jsx:7-95 의
 *            EditorScreen + material3-from-template.css:1265-1298
 *
 * 사용자 결정 (Step 6b):
 *   - C1-라: tab 시스템 통째 제거 (요약/번역/원문). 단일 markdown (요약) 만.
 *            번역/원문 placeholder 도 같이 제거 — Phase 2B-3-backend 에서 transcript
 *            필드 추가 시 정식 UI 결정.
 *   - C2-라: 우측 액션 sidebar 부분 통합:
 *            * 메타정보 + 태그 → Preview 영역 위 inline md-meta-strip (chip)
 *            * 마크다운 다운로드 → editor-head 액션 바
 *            * 라이브러리로 → editor-head 액션 바
 *            * 연관 노트 / 노트 삭제 → 통째 제거 (진짜 wiring 시점에 부활)
 *            * 썸네일 → Preview 영역 위 (실제 thumbnail_url, 6b-1 backend enrichment)
 *   - E1: ⌘S keydown listener (mount/unmount life-cycle)
 *   - F3: TopBar 무손상, editor-head 가 file path crumb + title + dirty-dot 담당
 *
 * Bridge wiring:
 *   - get_history_detail({job_id}) → {ok, markdown, full_html, meta, filename}
 *     (6b-1: meta 에 thumbnail_url + video_id enrichment 추가됨)
 *   - update_note({job_id, markdown}) → {ok, path}
 *   - save_result_as({markdown, default_filename}) → {path, cancelled}
 *
 * Babel standalone global scope 회피: 모든 top-level const 는 EDITOR_ 접두사.
 */

const { useState, useEffect, useRef } = React;

/* Phase 2B-5b-2: bridge 의 _err code → 사용자 친화 한국어 메시지. */
const EDITOR_ERROR_MESSAGES = {
  HISTORY_NOT_FOUND: '이 노트의 결과 파일이 없습니다 (처리가 완료되지 않았을 수 있습니다).',
  INVALID_ID: '잘못된 노트 식별자입니다.',
  READ_FAILED: '노트를 읽는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
};

function fmtDuration(sec) {
  if (sec == null || sec <= 0) return '';
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

/* === EditorScreen === */
function EditorScreen({ jobId, onBackToLibrary }) {
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
      setEditedContent('');
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
          const friendly = EDITOR_ERROR_MESSAGES[result?.code]
            || result?.error
            || 'get_history_detail failed';
          throw new Error(friendly);
        }
        setItem(result.meta || null);
        setMarkdown(result.markdown || '');
        setFullHtml(result.full_html || '');
        setEditedContent(result.markdown || '');
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

  const dirty = editedContent !== markdown;

  const handleSave = async () => {
    if (!jobId || !dirty) return;
    try {
      const result = await window.pywebview.api.update_note({
        job_id: jobId,
        markdown: editedContent,
      });
      if (result?.ok) {
        setMarkdown(editedContent);
        // full_html 은 backend 서버사이드 렌더 — 다음 read_job 시 자동 갱신.
        if (window.showToast) window.showToast('저장되었습니다.', 'success');
      } else {
        if (window.showToast) window.showToast(`저장 실패: ${result?.error || '알 수 없는 오류'}`, 'error');
      }
    } catch (e) {
      console.error('[EditorScreen] update_note:', e);
      if (window.showToast) window.showToast(`저장 오류: ${e.message || e}`, 'error');
    }
  };

  const handleCancel = () => {
    setEditedContent(markdown);
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

  // Phase 2B-6b: ⌘S (Cmd/Ctrl+S) 단축키 — handleSave 의 최신 클로저를 ref 로 보존.
  const handleSaveRef = useRef(handleSave);
  handleSaveRef.current = handleSave;

  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        handleSaveRef.current();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  /* === jobId 없을 때 empty state (Step 2B-5b-2 보존) === */
  if (!jobId) {
    return (
      <div className="editor-screen">
        <div className="editor-empty">
          <span className="msi">edit_note</span>
          <div>편집할 노트를 선택해주세요.</div>
          <button
            type="button"
            className="btn btn--ghost"
            onClick={onBackToLibrary}
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

  /* === 오류 상태 (Step 2B-5b-2 보존) === */
  if (error) {
    return (
      <div className="editor-screen">
        <div className="editor-empty">
          <span className="msi" style={{ color: 'var(--gn-danger)' }}>error</span>
          <div style={{ color: 'var(--gn-danger)' }}>{error}</div>
          <button
            type="button"
            className="btn btn--ghost"
            onClick={onBackToLibrary}
          >
            <span className="msi">history</span>
            라이브러리로
          </button>
        </div>
      </div>
    );
  }

  /* === 정상 상태 — split pane === */
  const title = item?.organized_title || item?.title || '제목 없음';
  const lineCount = editedContent.split('\n').length;
  const charCount = editedContent.length;

  return (
    <div className="editor-screen">
      {/* === editor-head: 좌 path crumb + title + dirty-dot / 우 액션 바 === */}
      <div className="editor-head">
        <div className="editor-head__lead">
          <div className="editor-head__crumb">
            <span>라이브러리</span>
            <span className="msi" style={{ fontSize: 14 }}>chevron_right</span>
            <span className="editor-head__crumb-current">{title}</span>
          </div>
          <h2 className="editor-head__title" title={title}>
            {title}
            {dirty && <span className="editor-head__dirty" aria-label="저장되지 않은 변경" />}
          </h2>
        </div>

        <div className="editor-head__actions">
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={handleDownload}
            title="마크다운 다운로드"
          >
            <span className="msi">download</span>
            다운로드
          </button>
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={onBackToLibrary}
            title="라이브러리로"
          >
            <span className="msi">arrow_back</span>
            라이브러리
          </button>
          {dirty && (
            <button
              type="button"
              className="btn btn--ghost btn--sm"
              onClick={handleCancel}
              title="변경 취소"
            >
              <span className="msi">close</span>
              취소
            </button>
          )}
          <button
            type="button"
            className="btn btn--primary btn--sm"
            onClick={handleSave}
            disabled={!dirty}
            title="저장 (⌘S)"
          >
            <span className="msi">save</span>
            저장 <span className="editor-head__shortcut">⌘S</span>
          </button>
        </div>
      </div>

      {/* === editor-split: 좌 Raw / 우 Preview === */}
      <div className="editor-split">
        <div className="editor-pane">
          <div className="editor-pane-head">
            <span className="msi" style={{ fontSize: 14 }}>code</span>
            <span>Raw · Markdown</span>
            <span className="editor-pane-head__meta">
              {lineCount} lines · {charCount} chars
            </span>
          </div>
          <textarea
            className="editor-textarea"
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            spellCheck={false}
          />
        </div>

        <div className="editor-pane">
          <div className="editor-pane-head">
            <span className="msi" style={{ fontSize: 14 }}>article</span>
            <span>Preview · Rendered</span>
            {dirty && (
              <span className="editor-pane-head__meta editor-pane-head__meta--warn">
                저장 후 갱신
              </span>
            )}
          </div>
          <div className="editor-preview">
            {item?.thumbnail_url && (
              <div className="editor-thumbnail">
                <img src={item.thumbnail_url} alt={title} />
              </div>
            )}

            <div className="md-meta-strip">
              {item?.uploader && (
                <span className="md-meta-chip">
                  <span className="msi">podcasts</span>
                  {item.uploader}
                </span>
              )}
              {item?.upload_date && (
                <span className="md-meta-chip">
                  <span className="msi">event</span>
                  {item.upload_date}
                </span>
              )}
              {item?.field && (
                <span className="md-meta-chip">
                  <span className="msi">label</span>
                  {item.field}
                </span>
              )}
              {item?.duration_sec > 0 && (
                <span className="md-meta-chip">
                  <span className="msi">timer</span>
                  {fmtDuration(item.duration_sec)}
                </span>
              )}
              {item?.num_speakers > 0 && (
                <span className="md-meta-chip">
                  <span className="msi">groups</span>
                  {item.num_speakers}명
                </span>
              )}
              {Array.isArray(item?.tags) && item.tags.map((tag) => (
                <span key={tag} className="md-meta-chip md-meta-chip--tag">{tag}</span>
              ))}
            </div>

            <div
              className="editor-preview__body"
              dangerouslySetInnerHTML={{ __html: fullHtml }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

window.EditorScreen = EditorScreen;
