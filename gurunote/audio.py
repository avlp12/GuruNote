"""
Step 1: 오디오 소스 → 로컬 mp3 오디오 파일.

소스 종류:
  - 유튜브 URL → `download_audio()` (yt-dlp)
  - 로컬 동영상/오디오 파일 → `extract_audio_from_file()` (ffmpeg subprocess)
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yt_dlp

# ffmpeg 가 직접 처리할 수 있는 미디어 확장자
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma", ".opus"}
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".ts", ".m4v"}
SUPPORTED_EXTS = AUDIO_EXTS | VIDEO_EXTS

# yt-dlp 로 받아볼 자막 언어 우선순위
SUBTITLE_LANGS = ["en", "en-US", "en-GB", "ko"]

# yt-dlp 가 선택한 포맷이 vtt 가 아닐 수 있어 여러 확장자를 모두 탐색한다.
# `_parse_subtitle_file()` 이 VTT 와 SRT 를 모두 처리.
SUBTITLE_EXTS = [".vtt", ".srt", ".ttml", ".srv3", ".json3", ".sub"]


@dataclass
class Chapter:
    """유튜브 영상의 챕터 (설명 타임스탬프 또는 YouTube 공식 챕터)."""

    start: float          # 초
    end: float            # 초
    title: str

    def to_dict(self) -> dict:
        return {"start": self.start, "end": self.end, "title": self.title}


@dataclass
class AudioDownloadResult:
    audio_path: str
    video_id: str
    video_title: str
    duration_sec: float
    uploader: Optional[str]
    webpage_url: str
    # YouTube 전용 메타데이터 (로컬 파일은 모두 기본값)
    upload_date: Optional[str] = None        # "YYYY-MM-DD" 형식
    description: str = ""                     # 영상 설명
    chapters: List[Chapter] = field(default_factory=list)
    subtitles_text: str = ""                  # 공식/자동 자막 (VTT → 평문)
    subtitles_source: str = ""                # "manual" | "auto" | ""
    tags: List[str] = field(default_factory=list)

    @property
    def is_youtube(self) -> bool:
        return self.webpage_url.startswith(("http://", "https://")) and (
            "youtube.com" in self.webpage_url or "youtu.be" in self.webpage_url
        )

    def to_context_dict(self) -> dict:
        """LLM 에 주입할 영상 컨텍스트 dict. 로컬 파일이면 자동으로 빈 값이 많아진다."""
        return {
            "title": self.video_title,
            "uploader": self.uploader,
            "upload_date": self.upload_date,
            "webpage_url": self.webpage_url if self.is_youtube else "",
            "description": self.description,
            "chapters": [c.to_dict() for c in self.chapters],
            "subtitles_text": self.subtitles_text,
            "subtitles_source": self.subtitles_source,
            "tags": list(self.tags),
        }


def is_probably_youtube_url(url: str) -> bool:
    if not url:
        return False
    u = url.strip().lower()
    return u.startswith(("http://", "https://")) and (
        "youtube.com" in u or "youtu.be" in u
    )


def download_audio(url: str, out_dir: str) -> AudioDownloadResult:
    """
    유튜브 URL 에서 오디오 + 메타데이터 + 자막을 가져온다.

    신뢰성 설계:
      - **오디오 다운로드는 필수** — 1차 호출에서 실패 시 그대로 예외 전파
      - **자막 다운로드는 best-effort** — 2차 별도 호출에서 실패 시 로그만 남기고
        계속 진행. 자막 엔드포인트의 간헐적 HTTP 403/429 등이 오디오 파이프라인
        전체를 무너뜨리지 않도록 격리.

    함께 수집하는 부가 정보:
      - 영상 게시일 (upload_date)
      - 설명 텍스트 (description)
      - 챕터 (YouTube 공식 챕터 또는 설명 타임스탬프 파싱)
      - 기존 자막 (수동 → 자동 순서로 영어, 없으면 한국어)
      - 태그

    Args:
        url: 유튜브 영상 URL
        out_dir: 임시 출력 디렉토리

    Returns:
        AudioDownloadResult — 파일 경로 + 메타데이터

    Raises:
        yt_dlp.utils.DownloadError, FileNotFoundError — **오디오 단계에서만**
    """
    os.makedirs(out_dir, exist_ok=True)

    # --- 1차: 오디오 다운로드 (실패 시 예외 전파) ---
    ydl_opts_audio = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noprogress": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
        info = ydl.extract_info(url, download=True)

    video_id = info.get("id", "audio")
    video_title = info.get("title", "Untitled")
    duration_sec = float(info.get("duration") or 0.0)
    uploader = info.get("uploader") or info.get("channel")
    webpage_url = info.get("webpage_url") or url
    description = info.get("description") or ""
    tags = info.get("tags") or []

    # 게시일 YYYYMMDD → YYYY-MM-DD
    raw_date = info.get("upload_date") or ""
    upload_date = _format_upload_date(raw_date)

    # 챕터: yt-dlp 가 파싱해주는 경우 우선, 없으면 설명에서 추정
    chapters = _extract_chapters(info, duration_sec)

    # --- 2차: 자막 다운로드 (best-effort, 모든 예외 swallow) ---
    _try_download_subtitles(url, out_dir)

    # 자막: 우선순위대로 파일을 찾아 평문 변환
    subtitles_text, subtitles_source = _load_best_subtitle(out_dir, video_id)

    audio_path = os.path.join(out_dir, f"{video_id}.mp3")
    if not os.path.exists(audio_path):
        candidates = sorted(
            p for p in Path(out_dir).glob(f"{video_id}.*")
            if p.suffix.lower() in AUDIO_EXTS
        )
        if not candidates:
            raise FileNotFoundError(
                f"오디오 파일을 찾을 수 없습니다: {out_dir} (id={video_id})"
            )
        audio_path = str(candidates[0])

    # yt-dlp 의 duration 을 ffprobe 로 교차 검증.
    # 일부 영상에서 yt-dlp 가 잘못된 duration 을 보고하는 경우가 있어
    # (예: 32분 영상을 19,425초로 보고) 실제 파일 길이를 기준으로 교정.
    ffprobe_dur = _get_duration_ffprobe(audio_path)
    if ffprobe_dur and ffprobe_dur > 0:
        if duration_sec <= 0 or abs(duration_sec - ffprobe_dur) / max(ffprobe_dur, 1) > 0.1:
            # 10% 이상 차이나면 ffprobe 값을 신뢰
            duration_sec = ffprobe_dur

    return AudioDownloadResult(
        audio_path=audio_path,
        video_id=video_id,
        video_title=video_title,
        duration_sec=duration_sec,
        uploader=uploader,
        webpage_url=webpage_url,
        upload_date=upload_date,
        description=description,
        chapters=chapters,
        subtitles_text=subtitles_text,
        subtitles_source=subtitles_source,
        tags=list(tags),
    )


# =============================================================================
# YouTube 메타데이터 보조 함수
# =============================================================================
def _format_upload_date(raw: str) -> Optional[str]:
    """yt-dlp 의 'YYYYMMDD' → ISO 'YYYY-MM-DD'. 실패 시 None."""
    raw = (raw or "").strip()
    if len(raw) == 8 and raw.isdigit():
        return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"
    return None


# 챕터 타임스탬프 라인: "00:00 Intro" / "1:02:03 - Deep dive" / "[12:34] Section"
_CHAPTER_LINE_RE = re.compile(
    r"^[\s\-\*\[\(•●·▪︎]*"             # 선행 장식 문자
    r"(\d{1,2}(?::\d{2}){1,2})"        # 타임스탬프 (M:SS 또는 H:MM:SS)
    r"[\s\-\]\):]+"                     # 구분자
    r"(.+?)"                            # 챕터 제목
    r"\s*$",
    re.MULTILINE,
)


def _extract_chapters(info: dict, duration_sec: float) -> List[Chapter]:
    """
    yt-dlp 가 제공한 chapters 필드를 우선 사용하고,
    없으면 영상 설명(description) 에서 타임스탬프 라인을 파싱한다.
    """
    raw_chapters = info.get("chapters") or []
    chapters: List[Chapter] = []

    if raw_chapters:
        for ch in raw_chapters:
            try:
                chapters.append(
                    Chapter(
                        start=float(ch.get("start_time", 0) or 0),
                        end=float(ch.get("end_time", 0) or 0),
                        title=str(ch.get("title", "")).strip(),
                    )
                )
            except Exception:  # noqa: BLE001
                continue
        if chapters:
            return chapters

    # Fallback: 설명에서 추정
    description = info.get("description") or ""
    candidates: List[Chapter] = []
    for match in _CHAPTER_LINE_RE.finditer(description):
        ts_str, title = match.group(1), match.group(2).strip()
        seconds = _ts_to_seconds(ts_str)
        if seconds is None:
            continue
        # 타이틀이 너무 짧거나 URL 만 있는 라인은 건너뜀
        if len(title) < 2 or title.startswith(("http://", "https://")):
            continue
        candidates.append(Chapter(start=seconds, end=0.0, title=title))

    if len(candidates) < 2:
        return []

    # 타임스탬프 기준 오름차순 정렬 후, 다음 챕터의 start 를 현재 end 로 설정
    candidates.sort(key=lambda c: c.start)
    for i, ch in enumerate(candidates):
        if i + 1 < len(candidates):
            ch.end = candidates[i + 1].start
        else:
            ch.end = duration_sec or ch.start

    return candidates


def _ts_to_seconds(ts: str) -> Optional[float]:
    """M:SS 또는 H:MM:SS → 초."""
    parts = ts.split(":")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if len(nums) == 2:
        m, s = nums
        return m * 60 + s
    if len(nums) == 3:
        h, m, s = nums
        return h * 3600 + m * 60 + s
    return None


def _try_download_subtitles(url: str, out_dir: str) -> None:
    """
    자막을 best-effort 로 다운로드한다. 모든 예외는 swallow — 자막 엔드포인트의
    간헐적 HTTP 403/429 가 오디오 파이프라인을 중단시키지 않도록 격리한다.

    `skip_download=True` 로 오디오 재다운로드를 막고, `ignoreerrors=True` 로
    개별 언어/포맷 실패를 전체 호출 실패로 격상시키지 않는다.
    """
    ydl_opts_subs = {
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "quiet": True,
        "noprogress": True,
        "no_warnings": True,
        "skip_download": True,              # 오디오는 이미 받았음
        "writesubtitles": True,             # 수동 자막
        "writeautomaticsub": True,          # 자동 자막
        "subtitleslangs": SUBTITLE_LANGS,
        "subtitlesformat": "vtt/srt/best",  # 우선 vtt, 없으면 srt 등으로 fallback
        "ignoreerrors": True,               # 자막 실패가 호출 실패가 되지 않게
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts_subs) as ydl:
            ydl.extract_info(url, download=True)
    except Exception:  # noqa: BLE001 — 자막은 optional 이므로 모든 예외 무시
        return


def _load_best_subtitle(out_dir: str, video_id: str) -> tuple[str, str]:
    """
    yt-dlp 가 다운로드한 자막 파일 중 가장 적합한 것을 선택해 평문으로 반환.

    - SUBTITLE_LANGS 우선순위대로 탐색
    - SUBTITLE_EXTS 의 여러 확장자(vtt/srt/ttml/…)를 모두 시도
    - yt-dlp 는 수동/자동 자막을 파일명으로 구분하지 않으므로 `"auto_or_manual"`
      소스로만 표기.

    Returns:
        (subtitles_text, source) — source 는 "auto_or_manual" | ""
    """
    out = Path(out_dir)
    for lang in SUBTITLE_LANGS:
        for ext in SUBTITLE_EXTS:
            p = out / f"{video_id}.{lang}{ext}"
            if p.exists() and p.stat().st_size > 0:
                text = _parse_subtitle_file(p)
                if text.strip():
                    return text, "auto_or_manual"
    return "", ""


def _parse_subtitle_file(path: Path) -> str:
    """VTT / SRT 를 평문으로 변환. 알 수 없는 포맷은 best-effort 텍스트 추출."""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    ext = path.suffix.lower()
    if ext == ".srt":
        return _srt_to_plaintext(raw)
    if ext == ".vtt":
        return _vtt_to_plaintext(raw)
    # ttml/srv3/json3 등은 태그 제거로 대략적인 평문만 추출 (정확도 낮아도
    # LLM 컨텍스트로는 충분).
    stripped = re.sub(r"<[^>]+>", " ", raw)
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return stripped


def _srt_to_plaintext(srt: str) -> str:
    """SRT 포맷에서 타임스탬프/번호/태그를 걷어내고 평문만 남긴다."""
    lines = srt.splitlines()
    out: List[str] = []
    seen: set[str] = set()
    for line in lines:
        s = line.strip()
        if not s or s.isdigit() or "-->" in s:
            continue
        t = re.sub(r"<[^>]+>", "", s)
        t = re.sub(r"&[a-z]+;", " ", t).strip()
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return "\n".join(out)


def _vtt_to_plaintext(vtt: str) -> str:
    """WebVTT 포맷에서 타임스탬프/헤더를 걷어내고 평문만 남긴다."""
    lines = vtt.splitlines()
    out: List[str] = []
    seen: set[str] = set()  # 자동 자막은 같은 문장이 중복되는 경향이 있어 중복 제거
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("WEBVTT") or stripped.startswith("NOTE"):
            continue
        # 타임스탬프 라인
        if "-->" in stripped:
            continue
        # 큐 번호
        if stripped.isdigit():
            continue
        # 인라인 태그 제거: <c>, <00:00:00.000>, </c>, &nbsp; 등
        text = re.sub(r"<[^>]+>", "", stripped)
        text = re.sub(r"&[a-z]+;", " ", text)
        text = text.strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return "\n".join(out)


def is_supported_local_file(path: str) -> bool:
    """로컬 파일이 지원되는 미디어 형식인지 확인."""
    if not path:
        return False
    p = Path(path)
    return p.is_file() and p.suffix.lower() in SUPPORTED_EXTS


def extract_audio_from_file(file_path: str, out_dir: str) -> AudioDownloadResult:
    """
    로컬 동영상/오디오 파일에서 mp3 를 추출한다.

    - 이미 mp3 인 경우 → 복사만 수행
    - 그 외 오디오/동영상 → ffmpeg 로 mp3 192kbps 변환

    Args:
        file_path: 원본 미디어 파일의 절대/상대 경로
        out_dir: 임시 출력 디렉토리

    Returns:
        AudioDownloadResult

    Raises:
        FileNotFoundError, RuntimeError (ffmpeg 실패)
    """
    src = Path(file_path).resolve()
    if not src.is_file():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    ext = src.suffix.lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(
            f"지원하지 않는 파일 형식입니다: {ext}\n"
            f"지원 형식: {', '.join(sorted(SUPPORTED_EXTS))}"
        )

    os.makedirs(out_dir, exist_ok=True)
    title = src.stem
    out_mp3 = os.path.join(out_dir, f"{title}.mp3")

    if ext == ".mp3":
        # 이미 mp3 → 복사
        shutil.copy2(str(src), out_mp3)
    else:
        # ffmpeg 로 mp3 변환
        cmd = [
            "ffmpeg", "-y", "-i", str(src),
            "-vn",                         # 비디오 스트림 제거
            "-acodec", "libmp3lame",
            "-ab", "192k",
            "-ar", "44100",
            "-ac", "2",
            out_mp3,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg 오디오 추출 실패 (exit {result.returncode}):\n"
                f"{result.stderr[:500]}"
            )

    if not os.path.exists(out_mp3):
        raise FileNotFoundError(f"변환된 오디오 파일을 찾을 수 없습니다: {out_mp3}")

    # 파일 크기로 대략적인 길이 추정 (mp3 192kbps ≈ 24KB/s)
    size_bytes = os.path.getsize(out_mp3)
    duration_estimate = size_bytes / (192 * 1000 / 8)

    # ffprobe 가 있으면 정확한 길이 사용
    duration_sec = _get_duration_ffprobe(out_mp3) or duration_estimate

    return AudioDownloadResult(
        audio_path=out_mp3,
        video_id=title,
        video_title=title,
        duration_sec=duration_sec,
        uploader=None,
        webpage_url=str(src),
    )


def _get_duration_ffprobe(audio_path: str) -> Optional[float]:
    """ffprobe 로 정확한 오디오 길이(초)를 가져온다. 실패 시 None."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path,
            ],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:  # noqa: BLE001
        pass
    return None


def cleanup_dir(dir_path: str) -> None:
    """Step 5: 임시 폴더 통째로 정리."""
    if dir_path and os.path.isdir(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
