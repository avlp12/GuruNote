"""
저장된 GuruNote 작업의 거시적 통계.

Step 3.3 — "지식 증류기" 로드맵.

사용자가 쌓아둔 노트 전체에 대한 요약 지표를 계산한다:
  - 총 작업 수 (성공/실패 분리)
  - 총 / 평균 / 최장 녹취 시간
  - 분야 분포 상위 N
  - 업로더 분포 상위 N
  - 태그 빈도 상위 N
  - 월별 작업 추이
  - 첫/마지막 작업 날짜

의존성 없음 (collections.Counter + datetime 만 사용). 차트는 CTkTextbox
내부 Unicode block 문자로 렌더링해 matplotlib 같은 무거운 dep 를 피한다.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DashboardStats:
    """계산된 대시보드 지표."""

    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_duration_sec: float = 0.0
    avg_duration_sec: float = 0.0
    max_duration_sec: float = 0.0
    total_speakers: int = 0  # 세그먼트별 num_speakers 합 (중복 셈 포함 — 개별 unique 추적은 미흡)
    first_created_at: Optional[str] = None
    last_created_at: Optional[str] = None
    # top-N 리스트: [(name, count), ...]
    fields: list[tuple[str, int]] = field(default_factory=list)
    uploaders: list[tuple[str, int]] = field(default_factory=list)
    tags: list[tuple[str, int]] = field(default_factory=list)
    monthly: list[tuple[str, int]] = field(default_factory=list)  # ("2026-04", count)


def compute_stats(
    jobs: list[dict],
    *,
    top_fields: int = 10,
    top_uploaders: int = 10,
    top_tags: int = 20,
) -> DashboardStats:
    """`load_index()` 결과를 받아 `DashboardStats` 로 집계."""
    out = DashboardStats()
    if not jobs:
        return out

    field_ctr: Counter[str] = Counter()
    uploader_ctr: Counter[str] = Counter()
    tag_ctr: Counter[str] = Counter()
    monthly_ctr: Counter[str] = Counter()
    durations: list[float] = []
    created_list: list[str] = []

    for j in jobs:
        out.total_jobs += 1
        status = (j.get("status") or "").lower()
        if status == "completed":
            out.completed_jobs += 1
        elif status == "failed":
            out.failed_jobs += 1

        d = float(j.get("duration_sec") or 0.0)
        if d > 0:
            durations.append(d)

        ns = int(j.get("num_speakers") or 0)
        out.total_speakers += ns

        f = (j.get("field") or "").strip()
        if f:
            field_ctr[f] += 1
        up = (j.get("uploader") or "").strip()
        if up:
            uploader_ctr[up] += 1
        for t in j.get("tags") or []:
            t = str(t).strip()
            if t:
                tag_ctr[t] += 1

        created = (j.get("created_at") or "").strip()
        if created:
            created_list.append(created)
            # "2026-04-17T..." → "2026-04"
            monthly_ctr[created[:7]] += 1

    if durations:
        out.total_duration_sec = sum(durations)
        out.avg_duration_sec = out.total_duration_sec / len(durations)
        out.max_duration_sec = max(durations)

    if created_list:
        created_list.sort()
        out.first_created_at = created_list[0]
        out.last_created_at = created_list[-1]

    out.fields = field_ctr.most_common(top_fields)
    out.uploaders = uploader_ctr.most_common(top_uploaders)
    out.tags = tag_ctr.most_common(top_tags)
    # 월별은 시간 순 정렬 (most_common 이 아니라)
    out.monthly = sorted(monthly_ctr.items())

    return out


# =============================================================================
# 텍스트 리포트 렌더링 (matplotlib / chart lib 없이)
# =============================================================================
_BAR_FILLED = "█"
_BAR_MAX_WIDTH = 24


def _human_duration(seconds: float) -> str:
    """초 → '1시간 23분' / '45분 12초' 형태."""
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}시간 {m}분"
    if m > 0:
        return f"{m}분 {s}초"
    return f"{s}초"


def _bar(count: int, max_count: int, width: int = _BAR_MAX_WIDTH) -> str:
    if max_count <= 0:
        return ""
    n = max(1, int(round(count / max_count * width)))
    return _BAR_FILLED * n


def _format_top(
    title: str,
    items: list[tuple[str, int]],
    total: int,
    show_percent: bool = False,
    label_width: int = 22,
) -> str:
    if not items:
        return f"\n{title}\n" + "─" * len(title) + "\n  (데이터 없음)\n"
    max_count = items[0][1]
    lines = [f"\n{title}", "─" * (len(title) * 2)]  # 한글 2byte 폭 고려
    for name, count in items:
        bar = _bar(count, max_count)
        label = (name[:label_width - 1] + "…") if len(name) > label_width else name
        pct_str = f" ({count / total * 100:.0f}%)" if show_percent and total else ""
        lines.append(f"  {label:<{label_width}} {bar} {count}{pct_str}")
    return "\n".join(lines) + "\n"


def render_report(stats: DashboardStats) -> str:
    """`DashboardStats` → 사람이 읽는 multi-line 텍스트 리포트."""
    if stats.total_jobs == 0:
        # 주의: `"A\n" "─" * 24` 는 implicit concat → `"A\n─" * 24` 로 반복되므로
        # 반드시 `+` 를 써서 multiply 우선순위 밖으로 빼낸다.
        return (
            "📊 GuruNote 대시보드\n"
            + ("─" * 24) + "\n\n"
            + "아직 저장된 작업이 없습니다.\n"
            + "유튜브 URL 또는 로컬 파일을 처리해 히스토리를 쌓아보세요.\n"
        )

    lines: list[str] = []
    lines.append("📊 GuruNote 대시보드")
    lines.append("=" * 24)
    lines.append("")
    lines.append("전체 통계")
    lines.append("─" * 18)
    lines.append(
        f"  총 작업          {stats.total_jobs} "
        f"(완료 {stats.completed_jobs} · 실패 {stats.failed_jobs})"
    )
    if stats.total_duration_sec > 0:
        lines.append(
            f"  총 녹취 시간     {_human_duration(stats.total_duration_sec)} "
            f"(평균 {_human_duration(stats.avg_duration_sec)}, "
            f"최장 {_human_duration(stats.max_duration_sec)})"
        )
    if stats.total_speakers > 0:
        lines.append(f"  누적 화자 수     {stats.total_speakers} 명 (중복 포함)")
    if stats.first_created_at:
        lines.append(f"  최초 작업        {stats.first_created_at[:10]}")
    if stats.last_created_at:
        lines.append(f"  최근 작업        {stats.last_created_at[:10]}")
    lines.append("")

    lines.append(_format_top(
        "분야별 분포", stats.fields,
        total=stats.total_jobs, show_percent=True,
    ).rstrip())
    lines.append(_format_top(
        "상위 업로더", stats.uploaders,
        total=stats.total_jobs, show_percent=False,
    ).rstrip())
    lines.append(_format_top(
        "상위 태그", stats.tags,
        total=stats.total_jobs, show_percent=False, label_width=26,
    ).rstrip())
    lines.append(_format_top(
        "월별 작업 추이", stats.monthly,
        total=stats.total_jobs, show_percent=False, label_width=10,
    ).rstrip())

    return "\n".join(lines) + "\n"
