# GuruNote Component Specs

> 각 컴포넌트의 픽셀/색/상태 사양. `DESIGN_TOKENS.md` 의 토큰을 참조한다.

---

## 1. Button

모든 버튼: `corner_radius=RADIUS_PILL` (24), 높이 36/40/48, padding 좌우 20.

### 1.1 Primary (파란 CTA)
- `fg_color = C_PRIMARY`, `hover_color = C_PRIMARY_HO`, `text_color = C_ON_PRIMARY`
- font size 13 bold (기본) / 14 bold (Main Hero CTA 만 48h)
- 예: "GuruNote 생성하기", "저장", "저장 (⌘S)"

### 1.2 Tonal (연한 파란 배경 — soft container)
- `fg_color = C_PRIMARY_SOFT`, `hover_color = "#d2e3fc"`, `text_color = C_PRIMARY`
- 2차 액션. 예: Settings > "Semantic Rebuild"

### 1.3 Outlined
- `fg_color = C_BG`, `hover_color = C_SURFACE_HI`, `text_color = C_PRIMARY`
- `border_width = 1`, `border_color = C_BORDER`
- 예: "연결 테스트", "취소", "Preview", ".md 다운로드"

### 1.4 Ghost / Text
- `fg_color = "transparent"`, `hover_color = C_SURFACE_HI`
- `text_color = C_TEXT_DIM` (비활성) / `C_PRIMARY` (활성)
- border 없음. 사이드바 네비 아이템, 탭, segmented 옵션에 사용.

### 1.5 Icon Button
- 32×32, `corner_radius = 16`, `fg_color = "transparent"`, `hover_color = C_SURFACE_HI`
- 유니코드 이모지 1자 또는 심벌 (예: 👁 ✕ ⋮)

---

## 2. Chip / Pill

### 2.1 Status Pill (Phase 2 History 카드)
- `corner_radius = RADIUS_PILL`, height 22, padx 10 pady 3
- `(bg, text)` 쌍은 `STATUS_COLORS[status]`
- font size 11 bold
- 접두 도트 없음 (색만으로 전달)

### 2.2 Soft Chip (분야 / 태그)
- `fg_color = C_PRIMARY_SOFT`, `text_color = C_PRIMARY`, radius `RADIUS_PILL`
- font size 11 bold, padx 10 pady 3
- "AI / ML", "스타트업" 같은 분류

### 2.3 Segmented Option
- 그룹 컨테이너: `fg_color = C_SIDEBAR`, radius `RADIUS_PILL`, border 1/C_BORDER
- 옵션 버튼: height 28, radius `RADIUS_PILL`
  - 비활성: `fg_color = "transparent"`, `text_color = C_TEXT_DIM`, hover `C_SURFACE_HI`
  - 활성: `fg_color = C_PRIMARY`, `text_color = C_ON_PRIMARY`
- font size 12, 두께 normal

---

## 3. Card

### 3.1 Standard Card
- `fg_color = C_BG`
- `corner_radius = RADIUS_LG` (16)
- `border_width = 1`, `border_color = C_BORDER`
- padding 24 사방
- **그림자 없음** (Tk 한계)

### 3.2 Card Header
- 구조: `[icon(16px primary)] [title(16 bold)] [subtitle(13 dim)] … [right actions]`
- 제목 아래 구분선 **없음**. padding-bottom 으로만 분리.

### 3.3 History Card (특수)
- 가로: 1열이 1개 row, 썸네일(16:9) 좌측 + 메타 우측
- 또는 grid-3 (min-width 320)
- hover: `border_color = C_PRIMARY` 로 변경 (transform 불가)
- hover 시 썸네일 중앙에 44×44 재생 버튼 표시

### 3.4 Provider Card (Settings > LLM)
- 4-up 가로 그리드, height 88
- 비활성: border 1/C_BORDER, fg `C_BG`
- 활성: border 2/C_PRIMARY, fg `C_PRIMARY_SOFT`, 우상단 체크 아이콘

### 3.5 KPI Card (Dashboard — out of scope)
- 아이콘 박스 44×44 (fg = `{color}18`, text = color)
- 값 (28 bold, `C_TEXT`)
- label (12, `C_TEXT_DIM`)
- delta (12, `C_SUCCESS` or `C_ERROR`)

---

## 4. Input Field

### 4.1 Standard (Outlined)
- height 42, `corner_radius = RADIUS_SM`
- `fg_color = C_BG`, `border_width = 1`, `border_color = C_BORDER`
- `text_color = C_TEXT`, placeholder `C_TEXT_MUTED`
- font size 13 (mono = `family="Menlo"` 12)

### 4.2 URL Hero Input (Main)
- height 48, `corner_radius = 24` (pill)
- 선행 이모지 🔗 를 placeholder 안에
- 우측 끝에 "로컬 파일" chip-button 배치 가능

### 4.3 Password (API Key)
- Standard + `show = "•"`
- 우측 absolute 에 👁 / 🙈 토글 Icon Button (32×32)

### 4.4 Label 위치
- 입력 **위** 4px 간격, font 11 bold, `C_TEXT_DIM`
- uppercase 로 변환하지 말 것

---

## 5. Step Indicator (Main > 진행 카드)

- 5개 노드, 각 32×32 원형
- 라벨: "오디오" / "STT" / "번역" / "요약" / "조립"
- 노드 상태:
  | state | bg | 숫자 색 | 라벨 색 |
  |---|---|---|---|
  | pending | `C_SURFACE_HI` | `C_TEXT_DIM` | `C_TEXT_DIM` |
  | active | `C_PRIMARY` | `C_ON_PRIMARY` | `C_PRIMARY` |
  | done | `C_PRIMARY` (체크 ✓) | `C_ON_PRIMARY` | `C_PRIMARY` |
- 연결선: height 2, done 이면 `C_PRIMARY`, 아니면 `C_BORDER`

---

## 6. Tabs (결과 카드 상단)

- Underline 스타일 (Google Material3)
- 탭 버튼: height 36, fg transparent, hover `C_SURFACE_HI`
- 비활성: `text_color = C_TEXT_DIM`
- 활성: `text_color = C_PRIMARY` + 아래 2px `C_PRIMARY` bar
- 탭 간 간격: 20
- 카운트 뱃지가 필요하면 11 bold, `C_PRIMARY_SOFT` bg, 파일 "Log · 142"

---

## 7. Sidebar

- width 240, `fg_color = C_SIDEBAR`
- 항목 높이 44, 가로 padding 16
- active: `fg_color = "#e8f0fe"`, `text_color = C_PRIMARY`, 좌측 3px 파란 rail
- hover: `fg_color = C_SURFACE_HI`, text `C_TEXT`
- 비활성: `fg_color = transparent`, text `C_TEXT`
- 아이콘은 이모지 20×20

---

## 8. Top Bar

- height 56, `fg_color = C_BG`, bottom border 1/C_BORDER
- 좌측: 화면 title (16 bold)
- 우측: Icon buttons (검색, 알림, 프로필)

---

## 9. Dialog / Modal

- `CTkToplevel` + `grab_set()`
- 컨테이너: `fg_color = C_BG`, radius 으로 감싸진 scrollable body
- 헤더: 22 bold title + 13 dim subtitle, padding 24
- 본문과 헤더 사이 구분선 **없음**
- 하단 액션 row: 우측 정렬, Primary + Outlined 조합

---

## 10. Detect Banner (자동 감지 배너)

Settings 에서 하드웨어/Vault 감지 결과 표시.

| kind | bg | fg |
|---|---|---|
| success | `C_SUCCESS_SOFT` | `C_SUCCESS` |
| warning | `C_WARNING_SOFT` | `C_WARNING` |
| error | `C_ERROR_SOFT` | `C_ERROR` |

- radius `RADIUS_SM`
- padding 16 좌우 · 12 상하
- 구조: `[icon] [title(13 bold)] [body(11 wrap)]` 세로 쌓기

---

## 11. Note Editor Preview (Markdown)

| 태그 | 스펙 |
|---|---|
| `h1` | 22 bold, `C_TEXT`, spacing 위 8/아래 4 |
| `h2` | 18 bold, `C_TEXT` |
| `h3` | 15 bold, `C_TEXT` |
| `bold` | 13 bold |
| `italic` | 13 italic, `C_TEXT_DIM` |
| `code` | `family="Menlo"` 12, fg `#c7254e`, bg `#f6f8fa` |
| `quote` | 13 italic, fg `C_PRIMARY`, lmargin 20 |
| `link` | fg `C_PRIMARY`, underline |
| `bullet` | lmargin1 14 lmargin2 28 |
| `ts` (타임스탬프) | `family="Menlo"` 12 bold, fg `C_PRIMARY` |

---

## 12. 상태 → 색 매핑 (추가 참고)

| 개념 | 색 |
|---|---|
| 활성/선택 | `C_PRIMARY` |
| 성공/완료 | `C_SUCCESS` |
| 경고 | `C_WARNING` |
| 실패 | `C_ERROR` |
| 대기/비활성 | `C_TEXT_DIM` / `C_BORDER` |
| 강조 배경 | `C_PRIMARY_SOFT` (= Google Blue container) |
