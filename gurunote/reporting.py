"""파이프라인 진행 상황을 단계별 Markdown 리포트로 저장."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import os
import re
from pathlib import Path


def _sanitize(name: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]", "", (name or "gurunote"))
    cleaned = re.sub(r"\s+", "_", cleaned).strip("._")
    return cleaned or "gurunote"


@dataclass
class PipelineReport:
    title: str
    source: str
    report_dir: Path = field(default_factory=lambda: Path(os.environ.get("GURUNOTE_REPORT_DIR", "reports")))
    path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.path = self.report_dir / f"GuruNote_Report_{ts}_{_sanitize(self.title)}.md"
        self.path.write_text(
            "# GuruNote 작업 보고서\n\n"
            f"- 생성시각(UTC): {datetime.now(timezone.utc).isoformat()}\n"
            f"- 제목: {self.title}\n"
            f"- 소스: {self.source}\n\n"
            "## 단계 로그\n\n",
            encoding="utf-8",
        )

    def step(self, step_name: str, status: str, detail: str) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"- [{ts}] **{step_name}** · `{status}`  \n  {detail}\n")

    def finalize(self, success: bool, detail: str = "") -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        outcome = "SUCCESS ✅" if success else "FAILED ❌"
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"\n## 결과\n- [{ts}] {outcome}\n")
            if detail:
                f.write(f"- 상세: {detail}\n")
