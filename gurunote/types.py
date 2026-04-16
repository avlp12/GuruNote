"""
파이프라인의 모든 단계 사이에서 공유되는 데이터 타입.

STT 엔진(WhisperX / AssemblyAI)의 결과를 동일한 `Transcript` 형태로 정규화해
LLM 단계와 마크다운 내보내기 단계에서 엔진에 종속되지 않게 한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Segment:
    """단일 발화 세그먼트 (한 화자의 한 발화 단위)."""

    speaker: str           # 화자 라벨 (예: "A", "B", "1") — 정규화된 문자열
    start: float           # 시작 시각 (초)
    end: float             # 종료 시각 (초)
    text: str              # 발화 텍스트 (영어 원문)

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    def to_dict(self) -> dict:
        return {
            "speaker": self.speaker,
            "start": self.start,
            "end": self.end,
            "text": self.text,
        }


@dataclass
class Transcript:
    """STT 단계의 최종 결과물."""

    segments: List[Segment] = field(default_factory=list)
    language: Optional[str] = None
    engine: str = ""              # 어떤 엔진이 만든 결과인지 (whisperx / assemblyai)
    raw: Optional[dict] = None    # 디버깅용 원본 응답

    @property
    def duration(self) -> float:
        if not self.segments:
            return 0.0
        return self.segments[-1].end

    @property
    def speakers(self) -> List[str]:
        seen: list[str] = []
        for seg in self.segments:
            if seg.speaker not in seen:
                seen.append(seg.speaker)
        return seen

    def to_plaintext(self, with_timestamps: bool = True) -> str:
        """LLM 입력용 플레인 텍스트 (Speaker A: ... 형식)."""
        lines = []
        for seg in self.segments:
            if with_timestamps:
                ts = _format_ts(seg.start)
                lines.append(f"[{ts}] Speaker {seg.speaker}: {seg.text}")
            else:
                lines.append(f"Speaker {seg.speaker}: {seg.text}")
        return "\n".join(lines)


def _format_ts(seconds: float) -> str:
    """초 → HH:MM:SS 또는 MM:SS 포맷."""
    if seconds is None:
        return "00:00"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
