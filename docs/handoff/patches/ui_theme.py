"""
GuruNote UI 디자인 토큰 — Google-style Light Theme (v0.8.0.6)
============================================================

이 파일은 기존 Material 3 Dark Purple 테마를 Google Workspace 스타일의
라이트 테마로 교체한 패치입니다. 기존 `gurunote/ui_theme.py` 를 이 파일로
**그대로 덮어쓰면** 앱 전체(`gui.py`, `ui_components.py`) 가 자동으로 새
팔레트를 사용합니다.

디자인 원칙
-----------
- **배경**: 순수 화이트(#ffffff) 가 아니라 Google Surface 계열의 은은한
  쿨 그레이(#f8f9fc, #f1f3f9) 를 사용해 눈 피로를 줄이면서 앱과 콘텐츠의
  위계를 만든다.
- **Primary**: Google Blue 600 (#1a73e8). 채워진 배경 위에는 흰 텍스트.
- **Accent/Secondary**: Google Green 600 (#1e8e3e). 진행/성공/하이라이트.
- **텍스트**: Google 문서/앱의 표준 색 계층 — 제목 #202124, 본문 #3c4043,
  보조 #5f6368, muted #80868b.
- **Border**: Google Material 표준 outline #dadce0.
- **반경**: pill/chip 은 full(999), 카드/다이얼로그는 12/16.

CustomTkinter 한계
------------------
`ctk` 위젯은 CSS 그림자/hover 트랜지션/gradient 를 직접 지원하지 않으므로
HTML 디자인의 모든 미묘한 요소는 근사치로만 재현됩니다 (색/여백/반경/폰트
는 1:1, 그림자는 border 로 대체).
"""
from __future__ import annotations

# =============================================================================
# 색상 — Google Workspace Light theme
# =============================================================================
# Surface 계층 (위로 갈수록 앞으로 나오는 느낌)
C_BG = "#ffffff"           # base — 메인 콘텐츠 영역
C_SIDEBAR = "#f8f9fc"      # 사이드바/필터바 — 아주 연한 쿨 그레이
C_SURFACE = "#ffffff"      # 카드/다이얼로그 (흰색 + border 로 분리)
C_SURFACE_HI = "#f1f3f9"   # hover / 선택된 리스트 아이템
C_BORDER = "#dadce0"       # Material outline — 카드/입력 테두리

# Primary (Google Blue)
C_PRIMARY = "#1a73e8"        # Google Blue 600 — CTA / 선택 상태
C_PRIMARY_HO = "#1557b0"     # hover 시 한 단계 진하게
C_PRIMARY_BRIGHT = "#8ab4f8" # Blue 300 — 아이콘/밝은 하이라이트
C_ON_PRIMARY = "#ffffff"     # primary 배경 위 텍스트

# Accent (Google Green — 성공/진행)
C_ACCENT = "#1e8e3e"         # Green 600

# Text (Google 기본 텍스트 계층)
C_TEXT = "#202124"           # 제목/중요
C_TEXT_DIM = "#5f6368"       # 보조/캡션
C_TEXT_MUTED = "#80868b"     # placeholder / 비활성

# Semantic (Google Material 계열)
C_SUCCESS = "#1e8e3e"        # Green 600
C_WARNING = "#f9ab00"        # Yellow 700
C_DANGER = "#d93025"         # Red 600
C_INFO = "#1a73e8"           # Blue 600

# =============================================================================
# 간격 (4·8 grid) — 기존 값 유지 (레이아웃 코드 호환)
# =============================================================================
SPACE_XXS = 2
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 24
SPACE_XXL = 32
SPACE_XXXL = 48

# =============================================================================
# 반경 — Google 스타일에 맞게 살짝 조정
# =============================================================================
RADIUS_SM = 8      # 작은 요소 (small button)
RADIUS_MD = 12     # 카드/dialog content
RADIUS_LG = 16     # 큰 카드/modal outer
RADIUS_PILL = 999  # chip / segmented pill — Google Search bar 스타일

# =============================================================================
# 높이 — 기존 값 유지
# =============================================================================
HEIGHT_SM = 28
HEIGHT_MD = 32
HEIGHT_LG = 40
HEIGHT_XL = 48

# =============================================================================
# 폰트 크기 — 기존 값 유지
# =============================================================================
FONT_PAGE_TITLE = 27
FONT_HEADING = 21
FONT_SECTION = 16
FONT_SUBSECTION = 14
FONT_BODY = 13
FONT_META = 11

WEIGHT_BOLD = "bold"
WEIGHT_NORMAL = "normal"

# =============================================================================
# 버튼 변형
# =============================================================================
BTN_PRIMARY = "primary"
BTN_SECONDARY = "secondary"
BTN_GHOST = "ghost"
BTN_DANGER = "danger"

# =============================================================================
# 상태 pill 색상 — 라이트 테마에 맞는 배경/텍스트 조합
#   Tuple: (background, text)
# =============================================================================
STATUS_COLORS = {
    "완료":    ("#e6f4ea", "#1e8e3e"),   # green container
    "실패":    ("#fce8e6", "#d93025"),   # red container
    "처리 중": ("#feefc3", "#b06000"),   # yellow container
    "대기":    ("#f1f3f4", "#5f6368"),   # neutral container
}

__all__ = [
    # Surface
    "C_BG", "C_SIDEBAR", "C_SURFACE", "C_SURFACE_HI", "C_BORDER",
    # Primary
    "C_PRIMARY", "C_PRIMARY_HO", "C_PRIMARY_BRIGHT", "C_ON_PRIMARY",
    # Accent
    "C_ACCENT",
    # Text
    "C_TEXT", "C_TEXT_DIM", "C_TEXT_MUTED",
    # Semantic
    "C_SUCCESS", "C_WARNING", "C_DANGER", "C_INFO",
    # Spacing
    "SPACE_XXS", "SPACE_XS", "SPACE_SM", "SPACE_MD", "SPACE_LG",
    "SPACE_XL", "SPACE_XXL", "SPACE_XXXL",
    # Radius
    "RADIUS_SM", "RADIUS_MD", "RADIUS_LG", "RADIUS_PILL",
    # Height
    "HEIGHT_SM", "HEIGHT_MD", "HEIGHT_LG", "HEIGHT_XL",
    # Font
    "FONT_PAGE_TITLE", "FONT_HEADING", "FONT_SECTION", "FONT_SUBSECTION",
    "FONT_BODY", "FONT_META",
    "WEIGHT_BOLD", "WEIGHT_NORMAL",
    # Button variants
    "BTN_PRIMARY", "BTN_SECONDARY", "BTN_GHOST", "BTN_DANGER",
    # Status
    "STATUS_COLORS",
]
