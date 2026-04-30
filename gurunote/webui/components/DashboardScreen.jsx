/* SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * Phase 2B-4b: DashboardScreen — 분석 통계 화면.
 *
 * Frontend only — bridge 추가 작업 0.
 * App.jsx 의 historyItems (이미 lifting state) 를 props 로 받아서 통계 계산.
 *
 * 4 영역:
 *   1. 통계 카드 4개 (총 노트 / 총 처리 시간 / 평균 길이 / 평균 화자 수)
 *   2. 주제 분포 (field facet 가로 bar chart)
 *   3. 태그 cloud (top 30, 빈도 비례 font-size)
 *   4. 활동 timeline (최근 30일 daily count, bar chart)
 */

const { useMemo } = React;

/* === 통계 헬퍼 === */
function computeStats(items) {
  if (!items || items.length === 0) {
    return {
      total: 0, totalDuration: 0, avgDuration: 0,
      avgSpeakers: 0, completedCount: 0,
    };
  }
  let totalDuration = 0;
  let speakersSum = 0;
  let speakersCount = 0;
  let completedCount = 0;
  for (const it of items) {
    if (it.duration_sec > 0) totalDuration += it.duration_sec;
    if (it.num_speakers > 0) {
      speakersSum += it.num_speakers;
      speakersCount++;
    }
    if (it.status === 'completed' || it.status === 'done') completedCount++;
  }
  return {
    total: items.length,
    totalDuration,
    avgDuration: items.length > 0 ? totalDuration / items.length : 0,
    avgSpeakers: speakersCount > 0 ? speakersSum / speakersCount : 0,
    completedCount,
  };
}

function fmtDurationLong(sec) {
  if (!sec || sec <= 0) return '0분';
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  if (h > 0) return `${h}시간 ${m}분`;
  return `${m}분`;
}

function fmtDurationShort(sec) {
  if (!sec || sec <= 0) return '0:00';
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function buildFieldDistribution(items) {
  const counts = new Map();
  for (const it of items) {
    if (it.field) counts.set(it.field, (counts.get(it.field) || 0) + 1);
  }
  return [...counts.entries()]
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label, 'ko'));
}

function buildTagCloud(items, topN = 30) {
  const counts = new Map();
  for (const it of items) {
    for (const tag of (it.tags || [])) {
      if (tag) counts.set(tag, (counts.get(tag) || 0) + 1);
    }
  }
  return [...counts.entries()]
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label, 'ko'))
    .slice(0, topN);
}

function buildTimeline(items, days = 30) {
  // 최근 N일 daily count
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const buckets = [];
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    buckets.push({ date: d, count: 0 });
  }
  const startMs = buckets[0].date.getTime();

  for (const it of items) {
    if (!it.created_at) continue;
    const ts = new Date(it.created_at);
    if (isNaN(ts.getTime())) continue;
    const dayStart = new Date(ts);
    dayStart.setHours(0, 0, 0, 0);
    const ms = dayStart.getTime();
    if (ms < startMs) continue;
    const idx = Math.floor((ms - startMs) / (24 * 60 * 60 * 1000));
    if (idx >= 0 && idx < buckets.length) {
      buckets[idx].count++;
    }
  }
  return buckets;
}

/* === Components === */
function StatCard({ icon, label, value, sub }) {
  return (
    <div className="stat-card">
      <div className="stat-card__icon">
        <span className="msi">{icon}</span>
      </div>
      <div className="stat-card__label">{label}</div>
      <div className="stat-card__value">{value}</div>
      {sub && <div className="stat-card__sub">{sub}</div>}
    </div>
  );
}

function FieldDistribution({ data, total }) {
  if (data.length === 0) {
    return (
      <div className="dashboard-empty" style={{ padding: 'var(--sp-4)' }}>
        주제 데이터가 없습니다.
      </div>
    );
  }
  const max = data[0].count;
  return (
    <div className="field-bars">
      {data.map((row) => (
        <div key={row.label} className="field-bar">
          <div className="field-bar__label" title={row.label}>{row.label}</div>
          <div className="field-bar__track">
            <div
              className="field-bar__fill"
              style={{ width: `${(row.count / max) * 100}%` }}
            />
          </div>
          <div className="field-bar__count">
            {row.count} · {Math.round((row.count / total) * 100)}%
          </div>
        </div>
      ))}
    </div>
  );
}

function TagCloud({ tags }) {
  if (tags.length === 0) {
    return (
      <div className="dashboard-empty" style={{ padding: 'var(--sp-4)' }}>
        태그 데이터가 없습니다.
      </div>
    );
  }
  const max = tags[0].count;
  const min = tags[tags.length - 1].count;
  const range = Math.max(max - min, 1);
  // font-size 0.85em ~ 1.4em 매핑
  const sizeFor = (count) => {
    const t = (count - min) / range;
    return (0.85 + t * 0.55).toFixed(2);
  };
  return (
    <div className="tag-cloud">
      {tags.map((tag) => (
        <span
          key={tag.label}
          className="tag-cloud__item"
          style={{ fontSize: `${sizeFor(tag.count)}em` }}
          title={`${tag.label} (${tag.count}회)`}
        >
          {tag.label}
          <span className="tag-cloud__count">{tag.count}</span>
        </span>
      ))}
    </div>
  );
}

function ActivityTimeline({ buckets }) {
  if (buckets.length === 0) return null;
  const max = Math.max(...buckets.map((b) => b.count), 1);
  const first = buckets[0].date;
  const last = buckets[buckets.length - 1].date;
  const middle = buckets[Math.floor(buckets.length / 2)].date;
  const fmtDate = (d) => `${d.getMonth() + 1}/${d.getDate()}`;

  return (
    <>
      <div className="timeline-chart">
        {buckets.map((b, i) => (
          <div
            key={i}
            className={'timeline-bar' + (b.count === 0 ? ' timeline-bar--empty' : '')}
            style={{ height: b.count === 0 ? '2px' : `${(b.count / max) * 100}%` }}
            title={`${fmtDate(b.date)} · ${b.count}개 노트`}
          />
        ))}
      </div>
      <div className="timeline-axis">
        <span>{fmtDate(first)}</span>
        <span>{fmtDate(middle)}</span>
        <span>{fmtDate(last)}</span>
      </div>
    </>
  );
}

/* === DashboardScreen === */
function DashboardScreen({ items, total, loading, error, onReload }) {
  const stats = useMemo(() => computeStats(items), [items]);
  const fieldData = useMemo(() => buildFieldDistribution(items), [items]);
  const tagData = useMemo(() => buildTagCloud(items, 30), [items]);
  const timelineData = useMemo(() => buildTimeline(items, 30), [items]);

  return (
    <div className="dashboard-screen">
      {loading && (
        <div className="dashboard-empty" style={{ color: 'var(--gn-on-surface-muted)' }}>
          불러오는 중...
        </div>
      )}
      {error && (
        <div className="dashboard-empty" style={{ color: 'var(--gn-danger)' }}>
          <span className="msi">error</span>
          <div>오류: {error}</div>
        </div>
      )}

      {!loading && stats.total === 0 && !error && (
        <div className="dashboard-empty">
          <span className="msi">analytics</span>
          <div>아직 통계를 표시할 노트가 없습니다.</div>
          <div style={{ fontSize: 12, marginTop: 8 }}>
            생성 화면에서 첫 노트를 만들어보세요.
          </div>
        </div>
      )}

      {stats.total > 0 && (
        <>
          <div className="dashboard-stats">
            <StatCard
              icon="library_books"
              label="총 노트 수"
              value={stats.total}
              sub={`완료 ${stats.completedCount}개`}
            />
            <StatCard
              icon="schedule"
              label="총 처리 시간"
              value={fmtDurationLong(stats.totalDuration)}
              sub={fmtDurationShort(stats.totalDuration)}
            />
            <StatCard
              icon="timer"
              label="평균 노트 길이"
              value={fmtDurationShort(stats.avgDuration)}
              sub="per 노트"
            />
            <StatCard
              icon="groups"
              label="평균 화자 수"
              value={stats.avgSpeakers > 0 ? stats.avgSpeakers.toFixed(1) : '-'}
              sub="명 / 노트"
            />
          </div>

          <div className="dashboard-section">
            <div className="dashboard-section__title">
              <span className="msi">category</span>
              주제 분포
            </div>
            <FieldDistribution data={fieldData} total={stats.total} />
          </div>

          <div className="dashboard-section">
            <div className="dashboard-section__title">
              <span className="msi">sell</span>
              태그 클라우드 (상위 30)
            </div>
            <TagCloud tags={tagData} />
          </div>

          <div className="dashboard-section">
            <div className="dashboard-section__title">
              <span className="msi">timeline</span>
              최근 30일 활동
            </div>
            <ActivityTimeline buckets={timelineData} />
          </div>
        </>
      )}
    </div>
  );
}

window.DashboardScreen = DashboardScreen;
