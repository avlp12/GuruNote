/* global React, Icon, Chip, Btn */
const { useState } = React;

/* ============================================================
   NOTE EDITOR — split raw + preview
   ============================================================ */
function EditorScreen() {
  const [md, setMd] = useState(`---
title: GPT-5 and the Future of AI
uploader: Lex Fridman
date: 2025-09-15
tags: [GPT-5, AGI, Alignment]
field: AI / ML
---

# 📌 영상 제목 및 핵심 주제 요약

OpenAI CEO **Sam Altman**이 Lex Fridman 팟캐스트에 출연해 GPT-5의 아키텍처, AGI 로드맵, AI 안전성 연구 방향을 심층 논의.

# 💡 Guru's Insights

- **스케일링 법칙은 아직 유효하다** — 파라미터 수 증가에 따른 성능 향상이 포화되지 않음
- **멀티모달 통합이 다음 도약의 열쇠** — 네이티브 멀티모달 아키텍처
- **AI Alignment 연구에 수익의 20% 투자** — Superalignment 팀 재정비

# ⏱️ 타임라인

- [00:00] 인사 및 GPT-5 발표 배경
- [12:30] 아키텍처 변화 — Transformer를 넘어서
- [35:00] AGI 정의와 실현 시점`);
  const [dirty, setDirty] = useState(false);

  return (
    <div className="screen editor-screen">
      <div className="editor-head">
        <div>
          <div style={{ fontSize: 12, color: 'var(--gn-on-surface-muted)' }}>
            ~/.gurunote/jobs/j1/result.md
          </div>
          <h2 style={{ margin: '2px 0 0', fontSize: 20, fontWeight: 600 }}>
            GPT-5 and the Future of AI
            {dirty && <span className="dirty-dot" />}
          </h2>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Btn icon="visibility" variant="outlined" size="sm">Preview</Btn>
          <Btn icon="close" variant="outlined" size="sm">취소</Btn>
          <Btn icon="save" variant="primary" size="sm">저장 (⌘S)</Btn>
        </div>
      </div>

      <div className="editor-split card">
        <div className="editor-pane">
          <div className="editor-pane-head">
            <Icon name="code" className="sm" /> Raw · Markdown
            <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--gn-on-surface-muted)' }}>
              {md.split('\n').length} lines · {md.length} chars
            </span>
          </div>
          <textarea
            className="editor-textarea"
            value={md}
            onChange={e => { setMd(e.target.value); setDirty(true); }}
            spellCheck={false}
          />
        </div>
        <div className="editor-pane">
          <div className="editor-pane-head">
            <Icon name="article" className="sm" /> Preview · Rendered
          </div>
          <div className="editor-preview">
            <div className="md-meta-strip">
              <span className="md-chip"><Icon name="podcasts" className="xs" /> Lex Fridman</span>
              <span className="md-chip"><Icon name="event" className="xs" /> 2025-09-15</span>
              <span className="md-chip"><Icon name="label" className="xs" /> AI / ML</span>
            </div>
            <h1>📌 영상 제목 및 핵심 주제 요약</h1>
            <p>OpenAI CEO <strong>Sam Altman</strong>이 Lex Fridman 팟캐스트에 출연해 GPT-5의 아키텍처, AGI 로드맵, AI 안전성 연구 방향을 심층 논의.</p>
            <h1>💡 Guru's Insights</h1>
            <ul>
              <li><strong>스케일링 법칙은 아직 유효하다</strong> — 파라미터 수 증가에 따른 성능 향상이 포화되지 않음</li>
              <li><strong>멀티모달 통합이 다음 도약의 열쇠</strong> — 네이티브 멀티모달 아키텍처</li>
              <li><strong>AI Alignment 연구에 수익의 20% 투자</strong> — Superalignment 팀 재정비</li>
            </ul>
            <h1>⏱️ 타임라인</h1>
            <ul>
              <li><span className="ts">00:00</span> 인사 및 GPT-5 발표 배경</li>
              <li><span className="ts">12:30</span> 아키텍처 변화 — Transformer를 넘어서</li>
              <li><span className="ts">35:00</span> AGI 정의와 실현 시점</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   DASHBOARD
   ============================================================ */
function DashboardScreen() {
  const fieldStats = [
    { label: 'AI / ML',      count: 42, color: '#1a73e8' },
    { label: '스타트업',      count: 18, color: '#188038' },
    { label: '반도체',        count: 11, color: '#e37400' },
    { label: '개발자 문화',   count: 9,  color: '#7b5ac1' },
    { label: '제품 디자인',   count: 7,  color: '#d93880' },
  ];
  const max = Math.max(...fieldStats.map(s => s.count));
  const months = [12, 18, 14, 22, 28, 35, 42, 38, 31, 45, 52, 48];
  const maxM = Math.max(...months);
  return (
    <div className="screen dashboard-screen">
      <div className="hist-head">
        <div>
          <h2 style={{ margin: 0, fontSize: 22, fontWeight: 600 }}>대시보드</h2>
          <p style={{ margin: '4px 0 0', color: 'var(--gn-on-surface-variant)', fontSize: 13 }}>
            지식 라이브러리 거시 지표
          </p>
        </div>
        <Btn icon="refresh" variant="outlined" size="sm">Refresh</Btn>
      </div>

      {/* KPI row */}
      <div className="kpi-grid">
        {[
          { label: '총 노트',    value: '87',        delta: '+12', icon: 'note', color: '#1a73e8' },
          { label: '총 녹취',    value: '94h',       delta: '+8h', icon: 'schedule', color: '#188038' },
          { label: '평균 길이',  value: '64m',       delta: '+2m', icon: 'timeline', color: '#e37400' },
          { label: '실패율',     value: '2.3%',      delta: '-1.1%', icon: 'error_outline', color: '#7b5ac1', good: true },
        ].map(k => (
          <div key={k.label} className="kpi card">
            <div className="kpi-ico" style={{ background: `${k.color}18`, color: k.color }}>
              <Icon name={k.icon} />
            </div>
            <div className="kpi-value">{k.value}</div>
            <div className="kpi-label">{k.label}</div>
            <div className={`kpi-delta ${k.good ? 'good' : ''}`}>
              <Icon name={k.delta.startsWith('-') ? 'trending_down' : 'trending_up'} className="xs" />
              {k.delta} 이번 달
            </div>
          </div>
        ))}
      </div>

      <div className="dash-grid">
        {/* Field distribution */}
        <div className="card" style={{ gridColumn: 'span 2' }}>
          <div className="card-header">
            <Icon name="pie_chart" style={{ color: 'var(--gn-primary)' }} />
            <h3>분야별 분포</h3>
            <span className="sub">top 5</span>
          </div>
          <div className="card-body">
            <div className="bar-list">
              {fieldStats.map(s => (
                <div key={s.label} className="bar-row">
                  <span className="bar-label">{s.label}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${(s.count / max) * 100}%`, background: s.color }} />
                  </div>
                  <span className="bar-value">{s.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Semantic index */}
        <div className="card">
          <div className="card-header">
            <Icon name="auto_awesome" style={{ color: 'var(--gn-primary)' }} />
            <h3>의미 검색 인덱스</h3>
          </div>
          <div className="card-body">
            <div className="idx-stat">
              <span className="idx-k">모델</span>
              <span className="idx-v mono">all-MiniLM-L6-v2</span>
            </div>
            <div className="idx-stat">
              <span className="idx-k">Chunks</span>
              <span className="idx-v mono">2,814</span>
            </div>
            <div className="idx-stat">
              <span className="idx-k">작업 수</span>
              <span className="idx-v mono">87</span>
            </div>
            <div className="idx-stat">
              <span className="idx-k">빌드 시각</span>
              <span className="idx-v mono">2026-04-15 09:22</span>
            </div>
            <Btn icon="refresh" variant="tonal" style={{ width: '100%', marginTop: 12, justifyContent: 'center' }}>
              Semantic Rebuild
            </Btn>
          </div>
        </div>

        {/* Monthly trend */}
        <div className="card" style={{ gridColumn: 'span 3' }}>
          <div className="card-header">
            <Icon name="show_chart" style={{ color: 'var(--gn-primary)' }} />
            <h3>월별 작업 추이</h3>
            <span className="sub">최근 12개월</span>
          </div>
          <div className="card-body">
            <div className="month-chart">
              {months.map((m, i) => (
                <div key={i} className="month-col">
                  <div className="month-bar" style={{ height: `${(m / maxM) * 100}%` }} />
                  <span className="month-label">{((i + 5) % 12) + 1}월</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   SETTINGS
   ============================================================ */
function SettingsScreen() {
  const [section, setSection] = useState('llm');
  return (
    <div className="screen settings-screen">
      <div className="hist-head">
        <div>
          <h2 style={{ margin: 0, fontSize: 22, fontWeight: 600 }}>설정</h2>
          <p style={{ margin: '4px 0 0', color: 'var(--gn-on-surface-variant)', fontSize: 13 }}>
            API 키 · 엔진 · 통합 관리
          </p>
        </div>
      </div>

      <div className="settings-layout">
        <nav className="settings-nav card">
          {[
            { k: 'llm',      icon: 'smart_toy',   label: 'LLM Provider' },
            { k: 'stt',      icon: 'mic',         label: 'STT 엔진' },
            { k: 'obsidian', icon: 'hub',         label: 'Obsidian' },
            { k: 'notion',   icon: 'cloud',       label: 'Notion' },
            { k: 'advanced', icon: 'tune',        label: '고급' },
            { k: 'about',    icon: 'info',        label: 'GuruNote 정보' },
          ].map(s => (
            <button
              key={s.k}
              className={`settings-nav-item ${section === s.k ? 'active' : ''}`}
              onClick={() => setSection(s.k)}
            >
              <Icon name={s.icon} className="sm" /> {s.label}
              <Icon name="chevron_right" className="sm" style={{ marginLeft: 'auto', opacity: 0.5 }} />
            </button>
          ))}
        </nav>

        <div className="settings-content">
          {section === 'llm' && <SettingsLLM />}
          {section === 'stt' && <SettingsSTT />}
          {section === 'obsidian' && <SettingsObsidian />}
          {section === 'notion' && <SettingsNotion />}
          {section === 'advanced' && <SettingsAdvanced />}
          {section === 'about' && <SettingsAbout />}
        </div>
      </div>
    </div>
  );
}

function SettingsLLM() {
  const [provider, setProvider] = useState('openai');
  return (
    <div className="card">
      <div className="card-header">
        <Icon name="smart_toy" style={{ color: 'var(--gn-primary)' }} />
        <h3>LLM Provider</h3>
        <span className="sub">번역/요약 단계에서 사용됩니다</span>
      </div>
      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        <div className="provider-grid">
          {[
            { k: 'openai',    name: 'OpenAI',     model: 'gpt-5.4',            color: '#10a37f' },
            { k: 'anthropic', name: 'Anthropic',  model: 'claude-sonnet-4-6',  color: '#d97757' },
            { k: 'gemini',    name: 'Gemini',     model: 'gemini-2.5-flash',   color: '#4285f4' },
            { k: 'local',     name: 'Local',      model: 'Ollama / vLLM',      color: '#5f6368' },
          ].map(p => (
            <button
              key={p.k}
              className={`provider-card ${provider === p.k ? 'active' : ''}`}
              onClick={() => setProvider(p.k)}
            >
              <div className="provider-dot" style={{ background: p.color }} />
              <div className="provider-name">{p.name}</div>
              <div className="provider-model mono">{p.model}</div>
              {provider === p.k && <Icon name="check_circle" className="provider-check" />}
            </button>
          ))}
        </div>
        <div className="field">
          <label>OpenAI API Key</label>
          <div style={{ position: 'relative' }}>
            <input type="password" className="input" defaultValue="sk-proj-abc123def456ghi789jkl0mnopqrstuvwxyz" />
            <button className="gn-iconbtn" style={{ position: 'absolute', right: 6, top: 4 }}>
              <Icon name="visibility_off" className="sm" />
            </button>
          </div>
        </div>
        <div className="field">
          <label>모델</label>
          <input className="input" defaultValue="gpt-5.4" />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div className="field">
            <label>Temperature</label>
            <input className="input" defaultValue="0.3" />
          </div>
          <div className="field">
            <label>번역 Max Tokens</label>
            <input className="input" defaultValue="16384" />
          </div>
          <div className="field">
            <label>요약 Max Tokens</label>
            <input className="input" defaultValue="4096" />
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Btn icon="wifi_tethering" variant="outlined">연결 테스트</Btn>
          <Btn icon="save" variant="primary" style={{ marginLeft: 'auto' }}>저장</Btn>
        </div>
      </div>
    </div>
  );
}

const SettingsSTT = () => (
  <div className="card">
    <div className="card-header">
      <Icon name="mic" style={{ color: 'var(--gn-primary)' }} />
      <h3>STT 엔진</h3>
      <span className="sub">자동 감지: Apple Silicon · MLX</span>
    </div>
    <div className="card-body">
      <div className="detect-banner">
        <Icon name="memory" style={{ color: 'var(--gn-success)' }} />
        <div>
          <strong>MLX Whisper 자동 선택됨</strong>
          <p>Apple Silicon M4 Max 감지 · Metal/MPS GPU 가속 활성 · 64GB Unified Memory</p>
        </div>
        <Btn icon="build" variant="outlined" size="sm">재감지</Btn>
      </div>
      <div className="field" style={{ marginTop: 20 }}>
        <label>MLX Whisper 모델</label>
        <input className="input" defaultValue="mlx-community/whisper-large-v3-mlx" />
      </div>
      <div className="field" style={{ marginTop: 12 }}>
        <label>HuggingFace Token (화자 분리용)</label>
        <input type="password" className="input" defaultValue="hf_abcdef1234567890" />
      </div>
    </div>
  </div>
);

const SettingsObsidian = () => (
  <div className="card">
    <div className="card-header">
      <Icon name="hub" style={{ color: 'var(--gn-primary)' }} />
      <h3>Obsidian Vault</h3>
    </div>
    <div className="card-body">
      <div className="detect-banner good">
        <Icon name="check_circle" style={{ color: 'var(--gn-success)' }} />
        <div>
          <strong>Vault 감지됨</strong>
          <p className="mono">~/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyVault</p>
        </div>
      </div>
      <div className="field" style={{ marginTop: 20 }}>
        <label>하위 폴더</label>
        <input className="input" defaultValue="GuruNote" />
      </div>
    </div>
  </div>
);

const SettingsNotion = () => (
  <div className="card">
    <div className="card-header">
      <Icon name="cloud" style={{ color: 'var(--gn-primary)' }} />
      <h3>Notion 통합</h3>
    </div>
    <div className="card-body">
      <div className="field">
        <label>Integration Token</label>
        <input type="password" className="input" defaultValue="secret_abc123..." />
      </div>
      <div className="field" style={{ marginTop: 12 }}>
        <label>Parent ID (database / page UUID)</label>
        <input className="input mono" defaultValue="a1b2c3d4-e5f6-7890-abcd-ef1234567890" />
      </div>
    </div>
  </div>
);

const SettingsAdvanced = () => (
  <div className="card">
    <div className="card-header">
      <Icon name="tune" style={{ color: 'var(--gn-primary)' }} />
      <h3>고급</h3>
    </div>
    <div className="card-body">
      <p style={{ color: 'var(--gn-on-surface-variant)', fontSize: 13 }}>
        하드웨어 프리셋, 청크 크기, 재시도 전략 등 전문가용 설정.
      </p>
    </div>
  </div>
);

const SettingsAbout = () => (
  <div className="card">
    <div className="card-header">
      <Icon name="info" style={{ color: 'var(--gn-primary)' }} />
      <h3>GuruNote</h3>
    </div>
    <div className="card-body" style={{ textAlign: 'center', padding: 40 }}>
      <div style={{
        width: 72, height: 72, margin: '0 auto 16px', borderRadius: 18,
        background: 'linear-gradient(135deg, #1a73e8, #4285f4)',
        display: 'grid', placeItems: 'center', color: '#fff',
        fontWeight: 700, fontSize: 32, boxShadow: '0 8px 20px rgba(26,115,232,0.35)',
      }}>G</div>
      <h3 style={{ margin: 0, fontSize: 18 }}>GuruNote</h3>
      <p className="mono" style={{ margin: '4px 0 16px', color: 'var(--gn-on-surface-muted)' }}>v0.8.0.6</p>
      <p style={{ color: 'var(--gn-on-surface-variant)', fontSize: 13, maxWidth: 320, margin: '0 auto' }}>
        유튜브 링크 한 줄로 해외 IT/AI 팟캐스트를 화자 분리된 한국어 마크다운 요약본으로.
      </p>
      <Btn icon="system_update" variant="tonal" style={{ marginTop: 16 }}>업데이트 확인</Btn>
    </div>
  </div>
);

window.EditorScreen = EditorScreen;
window.DashboardScreen = DashboardScreen;
window.SettingsScreen = SettingsScreen;
