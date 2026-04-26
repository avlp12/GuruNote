/* global React, Icon, Chip, Btn, StepIndicator, FacetTree, JOBS, STEPS */
const { useState } = React;

/* ============================================================
   MAIN screen — input + progress + results
   ============================================================ */
function MainScreen({ runState }) {
  const [url, setUrl] = useState('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
  const [engine, setEngine] = useState('auto');
  const [provider, setProvider] = useState('openai');
  const [tab, setTab] = useState('summary');
  return (
    <div className="screen main-screen">
      {/* Hero input card */}
      <div className="input-hero card elevated">
        <div className="input-hero-head">
          <div>
            <h2 className="hero-title">지식을 증류하세요</h2>
            <p className="hero-sub">유튜브 링크 한 줄로 해외 IT/AI 팟캐스트를 화자 분리된 한국어 마크다운 요약본으로</p>
          </div>
          <div className="hero-meta">
            <span className="chip selected" style={{ cursor: 'default' }}>
              <Icon name="bolt" className="xs" /> Apple Silicon · MLX
            </span>
          </div>
        </div>

        <div className="url-input-row">
          <div className="url-input">
            <Icon name="link" />
            <input
              type="text"
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=... 또는 로컬 파일 선택"
            />
            <button className="chip" style={{ border: 'none', background: 'var(--gn-surface-container)' }}>
              <Icon name="folder_open" className="xs" /> 로컬 파일
            </button>
          </div>
          <Btn icon="play_arrow" variant="primary" size="lg">GuruNote 생성하기</Btn>
        </div>

        <div className="option-row">
          <div className="opt-group">
            <label>STT 엔진</label>
            <div className="seg">
              {['auto', 'whisperx', 'mlx', 'assemblyai'].map(e => (
                <button key={e} className={`seg-opt ${engine === e ? 'active' : ''}`} onClick={() => setEngine(e)}>
                  {e}
                </button>
              ))}
            </div>
          </div>
          <div className="opt-group">
            <label>LLM Provider</label>
            <div className="seg">
              {['openai', 'anthropic', 'gemini', 'local'].map(p => (
                <button key={p} className={`seg-opt ${provider === p ? 'active' : ''}`} onClick={() => setProvider(p)}>
                  {p}
                </button>
              ))}
            </div>
          </div>
          <div className="opt-group right">
            <label>하드웨어 프리셋</label>
            <button className="select">
              <Icon name="memory" className="sm" /> M4 Max · 64GB <Icon name="expand_more" />
            </button>
          </div>
        </div>
      </div>

      {/* Progress card */}
      {runState === 'running' && (
        <div className="card elevated" style={{ marginTop: 20 }}>
          <div className="card-header">
            <Icon name="rocket_launch" style={{ color: 'var(--gn-primary)' }} />
            <h3>파이프라인 실행 중</h3>
            <span className="sub">GPT-5 and the Future of AI · Lex Fridman</span>
            <Btn icon="stop_circle" variant="outlined" size="sm" style={{ marginLeft: 12 }}>중지</Btn>
          </div>
          <div className="card-body">
            <StepIndicator current={2} progress={0.55} />
          </div>
        </div>
      )}

      {/* Results */}
      <div className="card elevated" style={{ marginTop: 20 }}>
        <div className="card-header" style={{ borderBottom: 'none', paddingBottom: 0 }}>
          <Icon name="description" style={{ color: 'var(--gn-primary)' }} />
          <h3>결과</h3>
          <span className="sub">GPT-5 and the Future of AI · 01:42:30</span>
          <div style={{ display: 'flex', gap: 8, marginLeft: 'auto' }}>
            <Btn icon="download" variant="outlined" size="sm">.md</Btn>
            <Btn icon="picture_as_pdf" variant="outlined" size="sm">PDF</Btn>
            <Btn icon="hub" variant="outlined" size="sm">Obsidian</Btn>
            <Btn icon="cloud_upload" variant="tonal" size="sm">Notion</Btn>
          </div>
        </div>
        <div className="tabs" style={{ padding: '0 20px' }}>
          {[
            { k: 'summary',  label: '요약',     icon: 'auto_awesome', count: null },
            { k: 'korean',   label: '한국어',   icon: 'translate',    count: null },
            { k: 'english',  label: '영어 원문', icon: 'subject',     count: null },
            { k: 'log',      label: 'Log',      icon: 'terminal',     count: 142 },
          ].map(t => (
            <div key={t.k} className={`tab ${tab === t.k ? 'active' : ''}`} onClick={() => setTab(t.k)}>
              <Icon name={t.icon} className="xs" /> {t.label}
              {t.count != null && <span className="count">{t.count}</span>}
            </div>
          ))}
        </div>
        <div className="result-body">
          {tab === 'summary' && <ResultSummary />}
          {tab === 'korean'  && <ResultKorean />}
          {tab === 'english' && <ResultEnglish />}
          {tab === 'log'     && <ResultLog />}
        </div>
      </div>
    </div>
  );
}

function ResultSummary() {
  return (
    <div className="md-view">
      {/* Hero — 영상 썸네일 + 메타 (History 카드의 thumbnail 스타일 공유) */}
      <div className="result-hero">
        <div className="result-hero-thumb job-thumb" style={{ background: 'linear-gradient(135deg, #4285f4 0%, #1a73e8 60%, #174ea6 100%)' }}>
          <div className="thumb-pattern" />
          <div className="thumb-stage">
            <div className="thumb-typo">
              <div className="thumb-typo-line">GPT-5 and the Future</div>
              <div className="thumb-typo-tag">#GPT-5</div>
            </div>
          </div>
          <div className="job-thumb-status">
            <Icon name="check_circle" className="xs" /> 완료
          </div>
          <div className="job-thumb-dur">01:42:30</div>
          <button className="thumb-play" title="유튜브에서 재생">
            <Icon name="play_arrow" />
          </button>
        </div>
        <div className="result-hero-info">
          <span className="job-field">AI / ML</span>
          <h3 className="result-hero-title">GPT-5 and the Future of AI</h3>
          <div className="result-hero-meta">
            <span><Icon name="podcasts" className="xs" /> Lex Fridman</span>
            <span><Icon name="event" className="xs" /> 2025-09-15</span>
            <span><Icon name="mic" className="xs" /> WhisperX</span>
            <span><Icon name="group" className="xs" /> 2 화자</span>
          </div>
          <div className="job-tags" style={{ marginTop: 4 }}>
            {['GPT-5', 'AGI', 'Alignment'].map(t => <span key={t} className="job-tag">#{t}</span>)}
          </div>
        </div>
      </div>

      <h1>📌 핵심 주제</h1>
      <p>OpenAI CEO Sam Altman이 Lex Fridman 팟캐스트에 출연해 GPT-5의 아키텍처, AGI 로드맵, AI 안전성 연구 방향을 심층 논의.</p>

      <h1>💡 Guru's Insights</h1>
      <ul className="insight-list">
        <li>
          <Icon name="trending_up" style={{ color: 'var(--gn-primary)' }} />
          <div>
            <strong>스케일링 법칙은 아직 유효하다</strong>
            <p>파라미터 수 증가에 따른 성능 향상이 포화되지 않았으며, 단, 효율적인 학습 기법(MoE, RLHF v3) 결합이 필수.</p>
          </div>
        </li>
        <li>
          <Icon name="hub" style={{ color: 'var(--gn-success)' }} />
          <div>
            <strong>멀티모달 통합이 다음 도약의 열쇠</strong>
            <p>텍스트·오디오·비디오를 단일 latent space에서 처리하는 네이티브 멀티모달 아키텍처가 GPT-5의 핵심 차별점.</p>
          </div>
        </li>
        <li>
          <Icon name="security" style={{ color: 'var(--gn-warning)' }} />
          <div>
            <strong>AI Alignment 연구에 수익의 20% 투자</strong>
            <p>Superalignment 팀을 재정비하고, Constitutional AI와 RLAIF를 결합한 새로운 안전성 평가 프레임워크 공개.</p>
          </div>
        </li>
      </ul>

      <h1>⏱️ 타임라인</h1>
      <ul className="timeline">
        <li><span className="ts">00:00</span> 인사 및 GPT-5 발표 배경</li>
        <li><span className="ts">12:30</span> 아키텍처 변화 — Transformer를 넘어서</li>
        <li><span className="ts">35:00</span> AGI 정의와 실현 시점에 대한 견해</li>
        <li><span className="ts">58:20</span> AI 안전성과 Superalignment 팀</li>
        <li><span className="ts">1:22:10</span> 오픈소스 vs 프론티어 모델 격차</li>
      </ul>
    </div>
  );
}

function ResultKorean() {
  return (
    <div className="transcript">
      {[
        { ts: '00:00', sp: 'A', name: 'Lex Fridman', text: '오늘 특별한 게스트를 모셨습니다. OpenAI의 CEO, Sam Altman씨입니다.' },
        { ts: '00:15', sp: 'B', name: 'Sam Altman', text: '초대해주셔서 감사합니다, Lex. 항상 이 대화를 기대하고 있었어요.' },
        { ts: '00:28', sp: 'A', name: 'Lex Fridman', text: 'GPT-5 발표가 얼마 전이었는데요, 이번 모델의 가장 큰 돌파구는 무엇이었나요?' },
        { ts: '00:42', sp: 'B', name: 'Sam Altman', text: '여러 가지가 있지만 가장 중요한 건 멀티모달 네이티브 설계입니다. 텍스트, 오디오, 비디오를 같은 latent space에서 처리합니다.' },
        { ts: '01:18', sp: 'A', name: 'Lex Fridman', text: '네이티브 멀티모달이란 구체적으로 어떤 의미인가요?' },
        { ts: '01:30', sp: 'B', name: 'Sam Altman', text: '기존엔 모달리티마다 encoder를 붙였다면, 이제는 tokenizer 레벨에서 통합됩니다.' },
      ].map((s, i) => (
        <div key={i} className="seg">
          <div className="seg-ts">{s.ts}</div>
          <div className={`seg-avatar sp-${s.sp}`}>{s.sp}</div>
          <div className="seg-body">
            <div className="seg-name">{s.name}</div>
            <div className="seg-text">{s.text}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ResultEnglish() {
  return (
    <div className="transcript">
      {[
        { ts: '00:00', sp: 'A', name: 'Lex Fridman', text: "We have a very special guest today — Sam Altman, CEO of OpenAI." },
        { ts: '00:15', sp: 'B', name: 'Sam Altman', text: "Thanks for having me, Lex. Always looking forward to these conversations." },
        { ts: '00:28', sp: 'A', name: 'Lex Fridman', text: "GPT-5 launched recently. What was the biggest breakthrough this time?" },
      ].map((s, i) => (
        <div key={i} className="seg">
          <div className="seg-ts">{s.ts}</div>
          <div className={`seg-avatar sp-${s.sp}`}>{s.sp}</div>
          <div className="seg-body">
            <div className="seg-name">{s.name}</div>
            <div className="seg-text">{s.text}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ResultLog() {
  const lines = [
    { t: '14:23:05', lv: 'info', msg: '[Step 1] 유튜브 오디오 추출 중...' },
    { t: '14:23:18', lv: 'ok',   msg: '[Step 1] OK: GPT-5 and the Future of AI (42.3 MB, 6150s)' },
    { t: '14:23:18', lv: 'dim',  msg: '  > 게시일: 2025-09-15' },
    { t: '14:23:18', lv: 'dim',  msg: '  > 공식 챕터 8개 감지' },
    { t: '14:23:20', lv: 'info', msg: '[Step 2] 화자 분리 STT 중...' },
    { t: '14:25:41', lv: 'ok',   msg: '[Step 2] OK: 847 세그먼트, 2 화자' },
    { t: '14:25:42', lv: 'info', msg: '[Step 3] LLM 한국어 번역 중...' },
    { t: '14:27:10', lv: 'ok',   msg: '[Step 3] OK: 번역 완료 (18,420 chars)' },
    { t: '14:27:30', lv: 'ok',   msg: '[Step 4] OK: 요약 완료' },
    { t: '14:27:32', lv: 'ok',   msg: '[Step 5] OK: 마크다운 조립' },
    { t: '14:27:32', lv: 'done', msg: '[Done] GuruNote 생성 완료' },
  ];
  return (
    <div className="log-view">
      {lines.map((l, i) => (
        <div key={i} className={`log-line lv-${l.lv}`}>
          <span className="log-ts">{l.t}</span>
          <span className="log-msg">{l.msg}</span>
        </div>
      ))}
    </div>
  );
}

/* ============================================================
   HISTORY screen — cards + facet tree
   ============================================================ */
function HistoryScreen() {
  const [active, setActive] = useState(null);
  const [search, setSearch] = useState('');
  const [treeSearch, setTreeSearch] = useState('');
  const [sort, setSort] = useState('최신순');
  const [semantic, setSemantic] = useState(false);
  const [body, setBody] = useState(false);

  return (
    <div className="screen history-screen">
      <div className="hist-head">
        <div>
          <h2 style={{ margin: 0, fontSize: 22, fontWeight: 600, letterSpacing: '-0.01em' }}>작업 히스토리</h2>
          <p style={{ margin: '4px 0 0', color: 'var(--gn-on-surface-variant)', fontSize: 13 }}>
            증류된 노트 {JOBS.length}개 · 지식 라이브러리
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Btn icon="refresh" variant="outlined" size="sm">새로고침</Btn>
          <Btn icon="build" variant="outlined" size="sm">Rebuild</Btn>
        </div>
      </div>

      <div className="hist-filter-bar card">
        <div className="hist-search">
          <Icon name="search" />
          <input
            placeholder="제목 / 업로더 / 태그 검색…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="hist-filters">
          <Chip selected={body} onClick={() => setBody(!body)} icon="description">본문 포함</Chip>
          <Chip selected={semantic} onClick={() => setSemantic(!semantic)} icon="auto_awesome">의미 검색</Chip>
          <div style={{ width: 1, height: 24, background: 'var(--gn-outline-variant)', margin: '0 8px' }} />
          {['최신순', '오래된순', '길이 긴 순', '제목 A-Z'].map(s => (
            <Chip key={s} selected={sort === s} onClick={() => setSort(s)}>{s}</Chip>
          ))}
        </div>
        {active && (
          <button className="chip selected" onClick={() => setActive(null)} style={{ marginLeft: 'auto' }}>
            <Icon name="filter_alt" className="xs" /> {active.title} › {active.label}
            <Icon name="close" className="xs" />
          </button>
        )}
      </div>

      <div className="hist-body">
        <div className="hist-grid">
          {JOBS.map(j => <JobCard key={j.id} job={j} />)}
        </div>
        <aside className="facet-panel card">
          <div className="facet-panel-head">
            <Icon name="account_tree" className="sm" /> 내비게이션
          </div>
          <FacetTree active={active} setActive={setActive} searchQuery={treeSearch} setSearchQuery={setTreeSearch} />
        </aside>
      </div>
    </div>
  );
}

function JobCard({ job }) {
  // 실제 유튜브 썸네일이 있으면 그걸 우선 사용, 로드 실패 시 placeholder로 폴백
  const [imgFailed, setImgFailed] = useState(!job.thumbnailUrl);
  const useImage = job.thumbnailUrl && !imgFailed;

  // Deterministic "style accent" per card for fallback placeholder
  const accent = (job.id.charCodeAt(1) || 0) % 3; // 0: 타이포 오버레이, 1: 이니셜 아바타, 2: 대비 블록
  const initials = job.uploader.split(' ').map(s => s[0]).join('').slice(0, 2).toUpperCase();
  const onPlay = (e) => {
    e.stopPropagation();
    if (job.sourceUrl) window.open(job.sourceUrl, '_blank');
    else console.log('[GuruNote] play source:', job.title);
  };
  return (
    <article className="job-card card hoverable elevated">
      <div className="job-thumb" style={{ background: useImage ? '#0b0b0b' : job.thumb }}>
        {useImage ? (
          /* 실제 유튜브 썸네일 */
          <img
            className="thumb-img"
            src={job.thumbnailUrl}
            alt={job.title}
            loading="lazy"
            onError={() => setImgFailed(true)}
          />
        ) : (
          /* Placeholder — 실제 썸네일이 없거나 로드 실패한 경우만 */
          <>
            <div className="thumb-pattern" />
            <div className="thumb-stage">
              {accent === 0 && (
                <div className="thumb-typo">
                  <div className="thumb-typo-line">{job.title.split(/[—:·]/)[0].trim().slice(0, 22)}</div>
                  {job.tags[0] && <div className="thumb-typo-tag">#{job.tags[0]}</div>}
                </div>
              )}
              {accent === 1 && (
                <div className="thumb-avatar">{initials}</div>
              )}
              {accent === 2 && (
                <div className="thumb-badge-stack">
                  <div className="thumb-badge-lg">{initials}</div>
                  <div className="thumb-badge-sm">{job.uploader}</div>
                </div>
              )}
            </div>
          </>
        )}
        {/* 상단 정보 */}
        <div className="job-thumb-status">
          <Icon name="check_circle" className="xs" /> {job.status}
        </div>
        <div className="job-thumb-dur">{job.duration}</div>
        {/* 호버 재생 버튼 */}
        <button className="thumb-play" onClick={onPlay} title="원본 소스 재생">
          <Icon name="play_arrow" />
        </button>
      </div>
      <div className="job-body">
        <div className="job-meta-top">
          <span className="job-field">{job.field}</span>
          <span className="job-date">{job.date}</span>
        </div>
        <h4 className="job-title">{job.title}</h4>
        <div className="job-meta-bottom">
          <span><Icon name="podcasts" className="xs" /> {job.uploader}</span>
          <span><Icon name="mic" className="xs" /> {job.engine}</span>
          <span><Icon name="group" className="xs" /> {job.speakers}명</span>
        </div>
        <div className="job-tags">
          {job.tags.map(t => <span key={t} className="job-tag">#{t}</span>)}
        </div>
      </div>
      <div className="job-actions">
        <button className="gn-iconbtn" title="열기"><Icon name="open_in_new" className="sm" /></button>
        <button className="gn-iconbtn" title="편집"><Icon name="edit" className="sm" /></button>
        <button className="gn-iconbtn" title=".md"><Icon name="download" className="sm" /></button>
        <button className="gn-iconbtn" title="Obsidian"><Icon name="hub" className="sm" /></button>
        <button className="gn-iconbtn" title="더보기" style={{ marginLeft: 'auto' }}><Icon name="more_vert" className="sm" /></button>
      </div>
    </article>
  );
}

window.MainScreen = MainScreen;
window.HistoryScreen = HistoryScreen;
