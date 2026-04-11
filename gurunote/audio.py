"""
Step 1: 유튜브 URL → 로컬 mp3 오디오 파일.

`yt-dlp` 를 얇게 감싼 함수 한 개. UI 코드와 STT 코드 양쪽이 import 한다.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yt_dlp


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


def cleanup_dir(dir_path: str) -> None:
    """Step 5: 임시 폴더 통째로 정리."""
    if dir_path and os.path.isdir(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
