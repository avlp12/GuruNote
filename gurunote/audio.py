"""
Step 1: 오디오 소스 → 로컬 mp3 오디오 파일.

소스 종류:
  - 유튜브 URL → `download_audio()` (yt-dlp)
  - 로컬 동영상/오디오 파일 → `extract_audio_from_file()` (ffmpeg subprocess)
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yt_dlp

# ffmpeg 가 직접 처리할 수 있는 미디어 확장자
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma", ".opus"}
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".ts", ".m4v"}
SUPPORTED_EXTS = AUDIO_EXTS | VIDEO_EXTS


@dataclass
class AudioDownloadResult:
    audio_path: str
    video_id: str
    video_title: str
    duration_sec: float
    uploader: Optional[str]
    webpage_url: str


def is_probably_youtube_url(url: str) -> bool:
    if not url:
        return False
    u = url.strip().lower()
    return u.startswith(("http://", "https://")) and (
        "youtube.com" in u or "youtu.be" in u
    )


def download_audio(url: str, out_dir: str) -> AudioDownloadResult:
    """
    유튜브 URL 에서 오디오만 추출해 mp3 로 저장한다.

    Args:
        url: 유튜브 영상 URL
        out_dir: 임시 출력 디렉토리

    Returns:
        AudioDownloadResult — 파일 경로 + 메타데이터

    Raises:
        yt_dlp.utils.DownloadError, FileNotFoundError
    """
    os.makedirs(out_dir, exist_ok=True)

    ydl_opts = {
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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    video_id = info.get("id", "audio")
    video_title = info.get("title", "Untitled")
    duration_sec = float(info.get("duration") or 0.0)
    uploader = info.get("uploader") or info.get("channel")
    webpage_url = info.get("webpage_url") or url

    audio_path = os.path.join(out_dir, f"{video_id}.mp3")
    if not os.path.exists(audio_path):
        # FFmpeg 변환이 어떤 이유로 다른 확장자를 남겼다면 폴더에서 찾는다.
        candidates = sorted(Path(out_dir).glob(f"{video_id}.*"))
        if not candidates:
            raise FileNotFoundError(
                f"오디오 파일을 찾을 수 없습니다: {out_dir} (id={video_id})"
            )
        audio_path = str(candidates[0])

    return AudioDownloadResult(
        audio_path=audio_path,
        video_id=video_id,
        video_title=video_title,
        duration_sec=duration_sec,
        uploader=uploader,
        webpage_url=webpage_url,
    )


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
