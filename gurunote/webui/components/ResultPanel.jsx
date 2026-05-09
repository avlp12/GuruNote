/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-3-backend Layer 7: ResultPanel — 4 tab UI 분리.
 *
 * 사용 영역 (3 곳):
 *   - MainScreen (CreateScreen, live pipeline 결과)
 *   - HistoryScreen DetailPanel (카드 클릭 quick preview)
 *   - EditorScreen Preview pane (full edit + tab catch)
 *
 * Tabs:
 *   - 요약 (summary)         — result.summary_html (History) 또는 result.full_html (live)
 *   - 한국어 스크립트 (korean) — result.korean_transcript
 *   - 영어 원문 (english)      — result.english_transcript / 한국어 원본 fallback
 *   - Log                    — log array (live) 또는 log string (History, pipeline.log)
 *
 * Props:
 *   - result: {
 *       summary_html?, full_html?, korean_transcript?, english_transcript?
 *     } 또는 null
 *   - log: array<string> (live) 또는 string (History) 또는 null
 *
 * Babel standalone scope 회피: 모든 top-level const 는 RP_ 접두사.
 */

const { useState: RP_useState } = React;

const RP_TABS = [
  { id: 'summary', label: '요약',     icon: 'auto_awesome' },
  { id: 'korean',  label: '한국어',   icon: 'translate' },
  { id: 'english', label: '영어 원문', icon: 'description' },
  { id: 'log',     label: 'Log',      icon: 'terminal' },
];

function ResultPanel({ result, log }) {
  const [activeTab, setActiveTab] = RP_useState('summary');

  // log: array (live) 또는 string (History) 정규화 → array
  const logLines = Array.isArray(log)
    ? log
    : (typeof log === 'string' && log ? log.split('\n') : []);

  // Layer 9: transcript 렌더링. Korean → text 그대로. English **...** → <strong>.
  // 오류 시 fallback: ** 단순 제거.
  const renderTranscript = (text, hasStrong) => {
    if (!text) return null;
    if (!hasStrong) return text;
    try {
      const parts = text.split(/(\*\*[^*]+\*\*)/g);
      return parts.map((part, idx) =>
        part.startsWith('**') && part.endsWith('**')
          ? React.createElement('strong', { key: idx }, part.slice(2, -2))
          : part
      );
    } catch (err) {
      console.warn('[ResultPanel] strong render fallback:', err);
      return text.replace(/\*\*/g, '');
    }
  };

  if (!result && logLines.length === 0) {
    return (
      <div className="result-empty">
        파이프라인을 실행하면 여기에 결과가 표시됩니다.
      </div>
    );
  }

  // summary tab: prefer summary_html (History parse 결과) → fallback full_html (live)
  const summaryHtml = result?.summary_html || result?.full_html || '';

  return (
    <>
      <div className="result-tabs">
        {RP_TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={'result-tab' + (activeTab === tab.id ? ' result-tab--active' : '')}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="msi" style={{ fontSize: 16, marginRight: 6 }}>{tab.icon}</span>
            {tab.label}
            {tab.id === 'log' && logLines.length > 0 && (
              <span className="result-tab__count">{logLines.length}</span>
            )}
          </button>
        ))}
      </div>

      {activeTab === 'summary' && summaryHtml && (
        <div className="result-rendered" dangerouslySetInnerHTML={{ __html: summaryHtml }} />
      )}
      {activeTab === 'summary' && !summaryHtml && (
        <div className="result-empty">처리 완료 후 요약이 표시됩니다.</div>
      )}

      {activeTab === 'korean' && (
        result?.korean_transcript
          ? <div className="result-transcript">{renderTranscript(result.korean_transcript, false)}</div>
          : <div className="result-empty">처리 완료 후 표시됩니다.</div>
      )}

      {activeTab === 'english' && (
        result?.english_transcript === ''
          ? <div className="result-empty">이 노트는 한국어 원본 콘텐츠입니다 — 원문 스크립트 섹션 부재.</div>
          : result?.english_transcript
            ? <div className="result-transcript">{renderTranscript(result.english_transcript, true)}</div>
            : <div className="result-empty">처리 완료 후 표시됩니다.</div>
      )}

      {activeTab === 'log' && (
        <div className="log-pane">
          {logLines.length === 0 ? '대기 중...' : logLines.join('\n')}
        </div>
      )}
    </>
  );
}

window.ResultPanel = ResultPanel;
