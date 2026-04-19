# GuruNote Light Theme 적용 가이드

이 패치 세트는 앱을 **Material 3 Dark Purple → Google Workspace Light** 로 전환합니다.
HTML 디자인(`GuruNote Redesign.html`) 에서 확정한 팔레트와 1:1 매핑됩니다.

---

## 1. 덮어쓸 파일 (1개)

### `gurunote/ui_theme.py`
이 폴더의 `ui_theme.py` 를 그대로 `gurunote/ui_theme.py` 에 덮어쓰세요.
앱이 다음 토큰을 참조하는 모든 곳에서 자동으로 새 색이 적용됩니다:
- `ui_components.button()` → 모든 버튼
- `ui_components.card()` → 모든 카드 래퍼
- `ui_components.chip()` → 상태 pill, 태그 칩

---

## 2. `gui.py` 상단 교체 (2블록)

### (A) Appearance mode — line ~130 근처

**Before**
```python
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
```

**After**
```python
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
```

### (B) 색상 상수 블록 — line ~137~160 근처

`gui.py` 에는 `ui_theme` 과 **중복 정의된** `C_BG`, `C_SIDEBAR`, … 가 존재합니다.
이 블록 전체(아래 Before) 를 삭제하고 ui_theme 에서 re-export 로 교체하세요.

**Before (삭제)**
```python
# ── 컬러 팔레트 — Material 3 다크 테마 기반 ──
# ... 주석 포함 ~20줄 ...
C_BG = "#141218"
C_SIDEBAR = "#1D1B20"
C_SURFACE = "#211F26"
C_SURFACE_HI = "#2B2930"
C_BORDER = "#49454F"
C_PRIMARY = "#4F378B"
C_PRIMARY_HO = "#5D43A8"
C_PRIMARY_BRIGHT = "#D0BCFF"
C_ON_PRIMARY = "#FFFFFF"
C_ACCENT = "#CCC2DC"
C_TEXT = "#E6E0E9"
C_TEXT_DIM = "#938F99"
C_SUCCESS = "#81C995"
C_DANGER = "#F2B8B5"
```

**After (추가)**
```python
# ── 컬러 팔레트 — ui_theme 에서 가져옴 (단일 출처) ──
# 기존 하드코딩을 ui_theme.C_* 로 일원화. 테마를 바꾸려면
# gurunote/ui_theme.py 하나만 수정하면 됩니다.
from gurunote.ui_theme import (
    C_BG, C_SIDEBAR, C_SURFACE, C_SURFACE_HI, C_BORDER,
    C_PRIMARY, C_PRIMARY_HO, C_PRIMARY_BRIGHT, C_ON_PRIMARY,
    C_ACCENT, C_TEXT, C_TEXT_DIM,
    C_SUCCESS, C_DANGER,
)
```

> `ut` alias 는 파일 상단에서 이미 `from gurunote import ui_theme as ut` 로
> 가져오고 있으니 추가 import 만 위의 형태로 붙이면 됩니다.

---

## 3. 선택 사항 — ctk OptionMenu / Entry 기본 색

`ctk.CTkOptionMenu`, `ctk.CTkEntry` 는 `set_appearance_mode("light")` 에서
자동으로 라이트 팔레트를 씁니다. 다만 앱 전역이 **흰 배경 + 파란 액센트**
에 맞도록 명시적으로 스타일을 덮는 걸 권장합니다.

```python
# 필요 시 HistoryDialog / SettingsDialog 등에서
entry = ctk.CTkEntry(
    parent,
    fg_color="#ffffff",
    border_color=C_BORDER,
    text_color=C_TEXT,
    placeholder_text_color=C_TEXT_DIM,
)
```

---

## 4. 검증 순서

1. `git stash` 로 현재 변경사항 백업
2. `ui_theme.py` 덮어쓰기 → `python gui.py` 실행
3. 에러 없이 뜨면 `gui.py` 수정 (A), (B) 적용 → 다시 실행
4. 각 화면에서 라이트 팔레트가 제대로 반영되는지 확인:
   - Main 화면: 헤더 배경, CTA 버튼 파랑, 진행 막대
   - History: 카드 배경 화이트 + 테두리, 썸네일 위 제목
   - Settings, Dashboard, Note Editor

---

## 5. 알려진 호환 이슈

- `C_PRIMARY_BRIGHT` 는 라이트 테마에서 더 이상 "아이콘 하이라이트" 역할을
  하지 않습니다. 지금 토큰은 **Blue 300 #8ab4f8** 으로 유지돼 있지만,
  사용 위치가 라이트 배경 위일 경우 대비가 낮으므로 `C_PRIMARY` 로
  교체하는 걸 권장합니다 (`cmd+f C_PRIMARY_BRIGHT` 검토).
- `STATUS_COLORS` 의 튜플 의미가 `(fg, text)` → **`(background, text)`** 로
  바뀌었습니다. 기존 사용처가 3~4곳이므로 변수명만 확인하면 됩니다.
