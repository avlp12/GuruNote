/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-3a: HistoryScreen — 라이브러리 카드 그리드 (검색/필터 없이 정적).
 * 디자인 spec: docs/design/v2-reference.html (시각적 참고만).
 *
 * Bridge: list_history({limit, offset}) → {ok, total, items: [...]}
 *   각 item 에 video_id + thumbnail_url enrichment 적용됨 (bridge.py).
 *
 * Phase 2B-3b/c/d 에서 검색/필터/정렬/facet 추가.
 */

const { useState, useEffect } = React;

const STATUS_BADGE = {
  completed: { label: '완료',    cls: 'job-card__badge--success' },
  done:      { label: '완료',    cls: 'job-card__badge--success' },
  failed:    { label: '실패',    cls: 'job-card__badge--error' },
  error:     { label: '실패',    cls: 'job-card__badge--error' },
  running:   { label: '진행 중', cls: 'job-card__badge--running' },
  stopped:   { label: '중지',    cls: 'job-card__badge--error' },
};

function formatDuration(sec) {
  if (sec == null || sec <= 0) return '';
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function JobCard({ item, onClick }) {
  const [imgError, setImgError] = useState(false);
  const status = STATUS_BADGE[item.status] || { label: item.status || '?', cls: '' };
  const title = item.organized_title || item.title || '제목 없음';
  const showImg = item.thumbnail_url && !imgError;

  return (
    <article className="job-card" onClick={() => onClick && onClick(item)}>
      <div className="job-card__thumb">
        {showImg ? (
          <img
            src={item.thumbnail_url}
            alt={title}
            onError={() => setImgError(true)}
            loading="lazy"
          />
        ) : (
          <div className="job-card__thumb-fallback">
            <span className="job-card__thumb-fallback-label">텍스트 온리</span>
            <div className="job-card__thumb-fallback-title">{title}</div>
          </div>
        )}
        <span className={'job-card__badge ' + status.cls}>{status.label}</span>
        {item.duration_sec > 0 && (
          <span className="job-card__duration">{formatDuration(item.duration_sec)}</span>
        )}
      </div>
      <div className="job-card__body">
        {item.field && <span className="job-card__field">{item.field}</span>}
        <h3 className="job-card__title">{title}</h3>
        <div className="job-card__meta">
          {item.uploader && <span>{item.uploader}</span>}
          {item.upload_date && <span>· {item.upload_date}</span>}
        </div>
        {item.tags && item.tags.length > 0 && (
          <div className="job-card__tags">
            {item.tags.slice(0, 4).map(tag => (
              <span key={tag} className="job-card__tag">{tag}</span>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}

function HistoryScreen() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      while (!window.pywebview?.api) {
        await new Promise(r => setTimeout(r, 50));
      }
      // bridge.py 가 인자 없이 호출 시 전체 list 반환 (defensive payload-aware
      // 패치도 함께 적용됨). 페이지네이션이 필요해지면 Phase 2B-3 후속에서 wiring.
      const result = await window.pywebview.api.list_history();
      if (!result?.ok) {
        throw new Error(result?.error || 'list_history failed');
      }
      setItems(result.items || []);
      setTotal(result.total || 0);
    } catch (e) {
      console.error('[HistoryScreen]', e);
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadHistory(); }, []);

  const handleCardClick = (item) => {
    // Phase 2B-3d / 2B-4 에서 detail view 또는 EditorScreen 으로 이동.
    console.log('[JobCard click]', item.job_id, item.organized_title || item.title);
    if (window.showToast) {
      window.showToast(`노트 열기 (Phase 2B-4): ${item.organized_title || item.title}`);
    }
  };

  return (
    <div className="history-screen">
      <div className="history-topbar">
        <div className="history-topbar__crumbs">GuruNote · 라이브러리</div>
        <div className="history-topbar__title">작업 히스토리</div>
        <div className="history-topbar__sub">
          {loading ? '불러오는 중...' : `증류된 노트 ${total}개 · 지식 라이브러리`}
        </div>
      </div>

      <div className="history-toolbar">
        {/* Phase 2B-3b: 검색 바, 필터 chips */}
        {/* Phase 2B-3c: 정렬 dropdown */}
        <button
          type="button"
          className="btn btn--ghost history-toolbar__refresh"
          onClick={loadHistory}
          disabled={loading}
        >
          <span className="msi">refresh</span>
          새로고침
        </button>
      </div>

      {error && (
        <div className="history-empty" style={{ borderColor: 'var(--gn-danger)', color: 'var(--gn-danger)' }}>
          오류: {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="history-empty">
          아직 증류된 노트가 없습니다.<br />
          생성 화면에서 첫 노트를 만들어보세요.
        </div>
      )}

      {!loading && items.length > 0 && (
        <div className="job-grid">
          {items.map(item => (
            <JobCard key={item.job_id} item={item} onClick={handleCardClick} />
          ))}
        </div>
      )}

      {loading && (
        <div className="history-loading">불러오는 중...</div>
      )}
    </div>
  );
}

window.HistoryScreen = HistoryScreen;
