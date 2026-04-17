"""
YouTube 썸네일 추출 + 로컬 캐시.

History 그리드 뷰에서 각 작업의 썸네일을 빠르게 표시하기 위해 일련의 해상도
변형을 순차 시도해 `~/.gurunote/thumbnails/` 에 JPEG 로 캐시한다.

해상도 폴백 체인: `mqdefault` (320x180) → `hqdefault` (480x360) → `default`
(120x90). 일부 영상은 특정 해상도가 없어서 YouTube 가 1-2KB placeholder JPEG
를 반환하므로 다운로드 크기로 검증한다.

로컬 파일 소스 (유튜브 URL 없음) 의 작업은 `extract_youtube_id` 가 None 을
반환하고, 호출자가 플레이스홀더를 표시하면 된다.
"""

from __future__ import annotations

import os
import re
import threading
from pathlib import Path
from typing import Callable, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

THUMBNAIL_DIR = Path.home() / ".gurunote" / "thumbnails"

# 환경변수로 디버그 로그 on/off. `GURUNOTE_THUMB_DEBUG=1 python gui.py` 로
# 썸네일 시도/실패 추적 가능.
_DEBUG = bool(os.environ.get("GURUNOTE_THUMB_DEBUG"))


def _dbg(msg: str) -> None:
    if _DEBUG:
        print(f"[thumbnails] {msg}")


# 표준 유튜브 URL 패턴을 모두 커버:
#   - https://www.youtube.com/watch?v=XXXXXXXXXXX
#   - https://youtu.be/XXXXXXXXXXX
#   - https://www.youtube.com/embed/XXXXXXXXXXX
#   - https://www.youtube.com/v/XXXXXXXXXXX
#   - https://www.youtube.com/shorts/XXXXXXXXXXX
#   - https://www.youtube.com/live/XXXXXXXXXXX   (라이브 스트림 replay)
_YT_ID_RE = re.compile(
    r"(?:v=|youtu\.be/|/embed/|/v/|/shorts/|/live/)([A-Za-z0-9_-]{11})"
)

# 해상도 폴백 체인. 첫 성공에서 중단.
_THUMB_VARIANTS: tuple[str, ...] = (
    "mqdefault.jpg",
    "hqdefault.jpg",
    "sddefault.jpg",
    "default.jpg",
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


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    # 일부 경로에서 i.ytimg.com 이 referer 비어있으면 1x1 투명 PNG 반환.
    "Referer": "https://www.youtube.com/",
    "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
}


def _try_fetch(video_id: str, variant: str, timeout: float) -> Optional[bytes]:
    """한 해상도 시도 — 성공 바이트(유효 크기) 또는 None."""
    url = f"https://i.ytimg.com/vi/{video_id}/{variant}"
    try:
        req = Request(url, headers=_HEADERS)
        with urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                _dbg(f"{video_id} {variant} status={resp.status}")
                return None
            data = resp.read()
    except HTTPError as exc:
        _dbg(f"{video_id} {variant} HTTP {exc.code}")
        return None
    except (URLError, TimeoutError, OSError) as exc:
        _dbg(f"{video_id} {variant} network err: {exc}")
        return None
    except Exception as exc:  # noqa: BLE001
        _dbg(f"{video_id} {variant} unknown err: {exc}")
        return None

    # YouTube 는 존재하지 않는 해상도에 1-2KB 회색 placeholder 를 반환한다.
    if len(data) < 2048:
        _dbg(f"{video_id} {variant} too small ({len(data)}B) — treating as miss")
        return None
    return data


def download_thumbnail(video_id: str, timeout: float = 6.0) -> Optional[Path]:
    """
    해상도 폴백 체인으로 썸네일 다운로드 + 캐시. 이미 캐시되어 있으면 즉시 반환.
    모든 variant 실패 시 None.

    성능:
      - mqdefault 파일 크기 ~10-20KB, 각 variant 당 네트워크 왕복 1회
      - 타임아웃 6초 × 4 variant 최악 = 24초 (실제론 첫 성공에서 즉시 반환)
      - 실패 원인 (제거된 영상, 비공개, 네트워크/방화벽) 모두 None 으로 silent
    """
    path = cached_thumbnail_path(video_id)
    if path.exists():
        return path

    try:
        THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # noqa: BLE001
        _dbg(f"{video_id} mkdir err: {exc}")
        return None

    for variant in _THUMB_VARIANTS:
        data = _try_fetch(video_id, variant, timeout)
        if data is None:
            continue
        try:
            # atomic: 임시 파일 → replace 로 동시성 안전
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(data)
            os.replace(tmp, path)
        except Exception as exc:  # noqa: BLE001
            _dbg(f"{video_id} write err: {exc}")
            return None
        _dbg(f"{video_id} hit {variant} ({len(data):,}B)")
        return path

    _dbg(f"{video_id} all variants failed")
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
