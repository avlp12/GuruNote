"""
앱 아이콘 생성 + 캐시.

tkinter 의 messagebox / CTkToplevel 은 아이콘이 지정되지 않으면 macOS/
Windows 의 기본 "Python Launcher" 아이콘 (로켓) 을 쓴다. 이 모듈은 PIL 로
간단한 "G" 모노그램 아이콘을 한 번 렌더해 `~/.gurunote/app_icon.png` 에
캐시하고, 메인 윈도우 및 모든 Toplevel 다이얼로그에서 `iconphoto` 로
적용할 수 있게 한다.

왜 런타임 생성인가:
  - PyInstaller 번들에 `.ico`/`.icns` 를 포함하면 플랫폼별 빌드 복잡도 증가
  - PNG 한 장이면 Tk `iconphoto` 로 충분하고, 디자인 변경 시 코드만 수정
  - 최초 1회 ~50ms, 이후 캐시에서 즉시 로드
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

_CACHE_DIR = Path.home() / ".gurunote"
_CACHE_PATH = _CACHE_DIR / "app_icon.png"

# Material 3 다크 팔레트의 primary container 색. 배경과 대비되게 진한 보라.
_BG_COLOR = (103, 80, 164, 255)   # #6750A4
_FG_COLOR = (255, 255, 255, 255)

_SIZE = 256


def _pick_font(size: int):
    """한영 렌더링 가능한 볼드 계열 폰트 1개를 픽."""
    from PIL import ImageFont  # type: ignore

    candidates = [
        # macOS
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVu-Sans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        # Windows
        "C:\\Windows\\Fonts\\Arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:  # noqa: BLE001
            continue
    return ImageFont.load_default()


def _render_icon() -> bytes:
    """PNG 바이트 반환. PIL 미설치 시 ImportError."""
    from PIL import Image, ImageDraw  # type: ignore

    img = Image.new("RGBA", (_SIZE, _SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 살짝 둥근 정사각 (material you squircle 느낌)
    margin = 8
    draw.rounded_rectangle(
        (margin, margin, _SIZE - margin, _SIZE - margin),
        radius=56, fill=_BG_COLOR,
    )

    # "G" 중앙 정렬
    font = _pick_font(150)
    text = "G"
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (_SIZE - tw) // 2 - bbox[0]
        y = (_SIZE - th) // 2 - bbox[1] - 6  # visual centering tweak
    except Exception:  # noqa: BLE001
        x, y = 70, 40
    draw.text((x, y), text, fill=_FG_COLOR, font=font)

    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def get_app_icon_path() -> Optional[Path]:
    """
    캐시된 아이콘 경로 반환. 없으면 생성. PIL 미설치 / 렌더 실패 시 None.

    호출자는 `if path: toplevel.iconphoto(False, tk.PhotoImage(file=str(path)))` 로 적용.
    """
    if _CACHE_PATH.exists():
        return _CACHE_PATH
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_bytes(_render_icon())
        return _CACHE_PATH
    except Exception:  # noqa: BLE001
        return None
