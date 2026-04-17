"""
YouTube 썸네일 추출 + 로컬 캐시.

History 그리드 뷰에서 각 작업의 썸네일을 빠르게 표시하기 위해 `mqdefault.jpg`
(320x180) 를 `~/.gurunote/thumbnails/` 에 한 번만 다운로드해 캐시한다.

로컬 파일 소스 (유튜브 URL 없음) 의 작업은 `extract_youtube_id` 가 None 을
반환하고, 호출자가 플레이스홀더를 표시하면 된다.
"""

from __future__ import annotations

import re
import threading
from pathlib import Path
from typing import Callable, Optional
from urllib.request import Request, urlopen

THUMBNAIL_DIR = Path.home() / ".gurunote" / "thumbnails"

# 표준 유튜브 URL 패턴을 모두 커버:
#   - https://www.youtube.com/watch?v=XXXXXXXXXXX
#   - https://youtu.be/XXXXXXXXXXX
#   - https://www.youtube.com/embed/XXXXXXXXXXX
#   - https://www.youtube.com/v/XXXXXXXXXXX
#   - https://www.youtube.com/shorts/XXXXXXXXXXX
_YT_ID_RE = re.compile(
    r"(?:v=|youtu\.be/|/embed/|/v/|/shorts/)([A-Za-z0-9_-]{11})"
)


def extract_youtube_id(url: str) -> Optional[str]:
    """URL 에서 11자리 YouTube 비디오 ID 를 추출. 실패 시 None."""
    if not url:
        return None
    m = _YT_ID_RE.search(url)
    return m.group(1) if m else None


def cached_thumbnail_path(video_id: str) -> Path:
    """비디오 ID 에 대응하는 캐시 파일 경로 (존재하지 않아도 반환)."""
    return THUMBNAIL_DIR / f"{video_id}.jpg"


def is_thumbnail_cached(video_id: str) -> bool:
    return cached_thumbnail_path(video_id).exists()


def download_thumbnail(video_id: str, timeout: float = 5.0) -> Optional[Path]:
    """
    `mqdefault.jpg` (320x180) 를 다운로드해 캐시. 이미 있으면 즉시 반환.
    실패 시 None.

    성능:
      - mqdefault 파일 크기 ~10-20KB → 5초 타임아웃 충분
      - 실패 원인 (제거된 영상, 비공개, 네트워크 오류) 모두 None 으로 silent
    """
    path = cached_thumbnail_path(video_id)
    if path.exists():
        return path

    url = f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
    try:
        THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 GuruNote"})
        with urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            data = resp.read()
        # 유튜브는 썸네일이 없을 때 120x90 픽셀의 회색 placeholder 이미지를 반환
        # (약 1-2KB). 지나치게 작으면 실패로 간주.
        if len(data) < 2048:
            return None
        path.write_bytes(data)
        return path
    except Exception:  # noqa: BLE001
        return None


def download_thumbnail_async(
    video_id: str,
    on_complete: Callable[[Optional[Path]], None],
    timeout: float = 5.0,
) -> None:
    """
    백그라운드 스레드에서 썸네일 다운로드. 완료 시 `on_complete(path_or_None)` 호출.

    GUI 의 첫 히스토리 그리드 렌더링을 차단하지 않기 위한 fire-and-forget 용도.
    호출자는 `on_complete` 안에서 Tkinter 위젯을 직접 만지지 말고, queue /
    `after()` 를 통해 메인 스레드로 마샬링해야 한다.
    """
    def _worker() -> None:
        try:
            path = download_thumbnail(video_id, timeout=timeout)
        except Exception:  # noqa: BLE001
            path = None
        try:
            on_complete(path)
        except Exception:  # noqa: BLE001
            pass

    threading.Thread(target=_worker, daemon=True).start()
