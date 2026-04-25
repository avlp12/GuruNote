/* global React */
const { useState, useMemo, useEffect, useRef } = React;

/* ============================================================
   Shared primitives
   ============================================================ */
const Icon = ({ name, className = '', style }) => (
  <span className={`msi ${className}`} style={style}>{name}</span>
);

const Chip = ({ icon, children, selected, onClick, variant = 'filter', style }) => (
  <button
    className={`chip ${variant} ${selected ? 'selected' : ''}`}
    onClick={onClick}
    style={style}
  >
    {icon && <Icon name={icon} />}
    {children}
  </button>
);

const Btn = ({ icon, children, variant = 'tonal', size, onClick, style, disabled }) => (
  <button
    className={`btn ${variant}${size ? ' ' + size : ''}`}
    onClick={onClick}
    style={style}
    disabled={disabled}
  >
    {icon && <Icon name={icon} />}
    {children}
  </button>
);

/* ============================================================
   Step progress — 5-step pipeline indicator (new design)
   ============================================================ */
const STEPS = [
  { key: 'audio',    label: '오디오',     desc: 'yt-dlp',           icon: 'graphic_eq' },
  { key: 'stt',      label: '화자 분리',  desc: 'WhisperX / MLX',   icon: 'record_voice_over' },
  { key: 'translate',label: '번역',       desc: 'LLM 한국어',        icon: 'translate' },
  { key: 'summary',  label: '요약',       desc: "Guru's Insights",   icon: 'auto_awesome' },
  { key: 'assemble', label: '조립',       desc: 'Markdown',          icon: 'article' },
];

function StepIndicator({ current = 2, progress = 0.55, elapsed = '2m 36s', eta = '~2m left' }) {
  return (
    <div className="step-indicator">
      <div className="step-track">
        <div className="step-line">
          <div
            className="step-line-fill"
            style={{ width: `${(current / (STEPS.length - 1)) * 100}%` }}
          />
        </div>
        {STEPS.map((s, i) => {
          const state = i < current ? 'done' : i === current ? 'active' : 'pending';
          return (
            <div key={s.key} className={`step-node ${state}`}>
              <div className="step-dot">
                {state === 'done' ? (
                  <Icon name="check" className="sm" />
                ) : state === 'active' ? (
                  <div className="step-spinner" />
                ) : (
                  <span className="step-num">{i + 1}</span>
                )}
              </div>
              <div className="step-meta">
                <div className="step-label">
                  <Icon name={s.icon} className="xs" /> {s.label}
                </div>
                <div className="step-desc">{s.desc}</div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="step-status">
        <div className="step-progress-bar">
          <div className="step-progress-fill" style={{ width: `${progress * 100}%` }} />
        </div>
        <div className="step-status-meta">
          <span className="step-pct">{Math.round(progress * 100)}%</span>
          <span className="step-time">
            <Icon name="schedule" className="xs" /> {elapsed} elapsed
          </span>
          <span className="step-time">
            <Icon name="hourglass_top" className="xs" /> {eta}
          </span>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   4-facet Tree Nav (new design)
   ============================================================ */
const FACETS = [
  { key: 'field',  title: '주제',   icon: 'category',
    nodes: [
      { label: 'AI / ML',         count: 42, color: '#1a73e8' },
      { label: '스타트업',        count: 18, color: '#188038' },
      { label: '반도체',          count: 11, color: '#e37400' },
      { label: '개발자 문화',     count: 9,  color: '#7b5ac1' },
      { label: '제품 디자인',     count: 7,  color: '#d93880' },
    ],
  },
  { key: 'person', title: '인물',   icon: 'person',
    nodes: [
      { label: 'Lex Fridman',     count: 14 },
      { label: 'Andrej Karpathy', count: 8 },
      { label: 'Sam Altman',      count: 6 },
      { label: 'Dario Amodei',    count: 5 },
      { label: 'Naval Ravikant',  count: 4 },
    ],
  },
  { key: 'title',  title: '제목',   icon: 'sort_by_alpha',
    nodes: [
      { label: 'A–E', count: 22 },
      { label: 'F–J', count: 14 },
      { label: 'K–O', count: 18 },
      { label: 'P–T', count: 25 },
      { label: 'U–Z', count: 8 },
    ],
  },
  { key: 'tag',    title: '태그',   icon: 'local_offer',
    nodes: [
      { label: 'GPT-5',           count: 12 },
      { label: 'RAG',             count: 9 },
      { label: 'AGI',             count: 8 },
      { label: 'MoE',             count: 6 },
      { label: 'Agent',           count: 5 },
      { label: 'Alignment',       count: 4 },
    ],
  },
];

function FacetTree({ active, setActive, searchQuery, setSearchQuery }) {
  const [expanded, setExpanded] = useState({ field: true, person: true, title: false, tag: true });
  const toggle = (k) => setExpanded({ ...expanded, [k]: !expanded[k] });

  const filtered = (nodes) => {
    if (!searchQuery) return nodes;
    const q = searchQuery.toLowerCase();
    return nodes.filter(n => n.label.toLowerCase().includes(q));
  };

  return (
    <div className="facet-tree">
      <div className="facet-search">
        <Icon name="search" className="sm" />
        <input
          placeholder="트리 내 검색…"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
      </div>
      {FACETS.map(f => (
        <div key={f.key} className="facet-group">
          <button
            className={`facet-header ${expanded[f.key] ? 'open' : ''}`}
            onClick={() => toggle(f.key)}
          >
            <Icon name="chevron_right" className="sm facet-chevron" />
            <Icon name={f.icon} className="sm facet-ico" />
            <span className="facet-title">{f.title}</span>
            <span className="facet-count">{f.nodes.length}</span>
          </button>
          {expanded[f.key] && (
            <div className="facet-nodes">
              {filtered(f.nodes).map(n => {
                const isActive = active && active.facet === f.key && active.label === n.label;
                return (
                  <button
                    key={n.label}
                    className={`facet-node ${isActive ? 'active' : ''}`}
                    onClick={() => setActive(isActive ? null : { facet: f.key, label: n.label, title: f.title })}
                  >
                    <span className="facet-bullet" style={{ background: n.color || '#5f6368' }} />
                    <span className="facet-node-label">{n.label}</span>
                    <span className="facet-node-count">{n.count}</span>
                  </button>
                );
              })}
              {filtered(f.nodes).length === 0 && (
                <div className="facet-empty">검색 결과 없음</div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/* ============================================================
   Sample job data
   ============================================================ */
const JOBS = [
  {
    id: 'j1',
    title: 'GPT-5 and the Future of AI',
    uploader: 'Lex Fridman',
    date: '2025-09-15',
    duration: '01:42:30',
    field: 'AI / ML',
    tags: ['GPT-5', 'AGI', 'Alignment'],
    speakers: 2,
    engine: 'whisperx',
    status: '완료',
    thumb: 'linear-gradient(135deg, #4285f4 0%, #1a73e8 60%, #174ea6 100%)',
    thumbnailUrl: 'https://i.ytimg.com/vi/jvqFAi7vkBc/mqdefault.jpg',
    sourceUrl: 'https://www.youtube.com/watch?v=jvqFAi7vkBc',
  },
  {
    id: 'j2',
    title: 'Andrej Karpathy — Software 2.0 and the Road to AGI',
    uploader: 'Andrej Karpathy',
    date: '2025-09-08',
    duration: '02:14:05',
    field: 'AI / ML',
    tags: ['Software 2.0', 'Training', 'LLM'],
    speakers: 2,
    engine: 'mlx',
    status: '완료',
    thumb: 'linear-gradient(135deg, #34a853 0%, #188038 100%)',
    thumbnailUrl: 'https://i.ytimg.com/vi/LCEmiRjPEtQ/mqdefault.jpg',
    sourceUrl: 'https://www.youtube.com/watch?v=LCEmiRjPEtQ',
  },
  {
    id: 'j3',
    title: 'Scaling Laws, Mixture of Experts, and Post-Training',
    uploader: 'Dwarkesh Patel',
    date: '2025-08-30',
    duration: '01:28:40',
    field: 'AI / ML',
    tags: ['MoE', 'Scaling', 'RLHF'],
    speakers: 3,
    engine: 'whisperx',
    status: '완료',
    thumb: 'linear-gradient(135deg, #fbbc04 0%, #e37400 100%)',
  },
  {
    id: 'j4',
    title: 'Dario Amodei — Constitutional AI and the Path to Safety',
    uploader: 'Anthropic',
    date: '2025-08-22',
    duration: '00:58:12',
    field: 'AI / ML',
    tags: ['Alignment', 'RLAIF', 'Claude'],
    speakers: 2,
    engine: 'whisperx',
    status: '완료',
    thumb: 'linear-gradient(135deg, #ea4335 0%, #c5221f 100%)',
    thumbnailUrl: 'https://i.ytimg.com/vi/ugvHCXCOmm4/mqdefault.jpg',
    sourceUrl: 'https://www.youtube.com/watch?v=ugvHCXCOmm4',
  },
  {
    id: 'j5',
    title: '반도체 산업의 다음 10년 — TSMC, Nvidia, 그리고 Samsung',
    uploader: '언더스탠딩',
    date: '2025-08-14',
    duration: '01:12:20',
    field: '반도체',
    tags: ['TSMC', 'Nvidia', 'Foundry'],
    speakers: 2,
    engine: 'mlx',
    status: '완료',
    thumb: 'linear-gradient(135deg, #7b5ac1 0%, #512da8 100%)',
  },
  {
    id: 'j6',
    title: 'Naval on Wealth, Leverage, and Long-Term Thinking',
    uploader: 'Naval Ravikant',
    date: '2025-08-01',
    duration: '00:45:30',
    field: '스타트업',
    tags: ['Leverage', 'Philosophy'],
    speakers: 2,
    engine: 'assemblyai',
    status: '완료',
    thumb: 'linear-gradient(135deg, #00bcd4 0%, #00897b 100%)',
  },
];

/* Expose */
Object.assign(window, { Icon, Chip, Btn, StepIndicator, FacetTree, JOBS, STEPS });
