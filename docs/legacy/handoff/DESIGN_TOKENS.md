# GuruNote Design Tokens

> **Source of truth.** 모든 수치/색은 이 표에서만 나온다. `gui.py` 안에
> 이 표 밖의 hex 리터럴이 보이면 버그.

---

## 1. Color — Light Theme

모두 `gurunote/ui_theme.py` 에 `C_*` 상수로 정의됨.

### 1.1 Surface / Background

| Token | Hex | 용도 |
|---|---|---|
| `C_BG` | `#ffffff` | 앱 배경, 카드 배경, 입력 배경 |
| `C_SIDEBAR` | `#f8f9fc` | 사이드바, segmented 그룹 배경 |
| `C_SURFACE_HI` | `#f1f3f9` | hover 상태, 읽기 전용 필드 |
| `C_BORDER` | `#dadce0` | 모든 테두리 (카드/입력/칩) |
| `C_BORDER_STRONG` | `#9aa0a6` | 강조 테두리 (현재 미사용, 예비) |

### 1.2 Text

| Token | Hex | 용도 |
|---|---|---|
| `C_TEXT` | `#202124` | 기본 본문 (Google Grey 900) |
| `C_TEXT_DIM` | `#5f6368` | 부가 설명, label, 비활성 (Grey 700) |
| `C_TEXT_MUTED` | `#80868b` | 타임스탬프, placeholder |

### 1.3 Primary / Brand

| Token | Hex | 용도 |
|---|---|---|
| `C_PRIMARY` | `#1a73e8` | Google Blue 600 — CTA, 활성 탭, 강조 |
| `C_PRIMARY_HO` | `#1967d2` | hover (Blue 700) |
| `C_PRIMARY_SOFT` | `#e8f0fe` | soft container (선택 배경, chip bg) |
| `C_ON_PRIMARY` | `#ffffff` | primary 위 텍스트 |

### 1.4 Status

| Token | Hex | 용도 |
|---|---|---|
| `C_SUCCESS` | `#188038` | done, 연결 성공 (Green 700) |
| `C_SUCCESS_SOFT` | `#e6f4ea` | soft container |
| `C_WARNING` | `#b06000` | 경고 텍스트 |
| `C_WARNING_SOFT` | `#feefc3` | soft container |
| `C_ERROR` | `#c5221f` | 실패 (Red 700) |
| `C_ERROR_SOFT` | `#fce8e6` | soft container |
| `C_INFO` | `#1a73e8` | 정보 (= primary) |
| `C_INFO_SOFT` | `#e8f0fe` | soft container |

### 1.5 Status Pill Matrix

`STATUS_COLORS: dict[str, tuple[str, str]]` — `(bg, text)`.
Phase 2 `_render_card` 가 이 테이블에서 꺼내 쓴다.

| status | bg | text |
|---|---|---|
| `queued` | `C_SURFACE_HI` | `C_TEXT_DIM` |
| `running` | `C_INFO_SOFT` | `C_PRIMARY` |
| `done` | `C_SUCCESS_SOFT` | `C_SUCCESS` |
| `failed` | `C_ERROR_SOFT` | `C_ERROR` |
| `canceled` | `C_SURFACE_HI` | `C_TEXT_MUTED` |

### 1.6 Placeholder (Phase 2 전용 하드코딩 허용)

업로드 이미지가 없는 카드의 썸네일에 쓰는 3-스타일 그라디언트.
`job_id` 해시 % 3 로 결정.

| Style | 그라디언트 | 강조 색 |
|---|---|---|
| 0 (Blue) | `#4285f4 → #1a73e8 → #174ea6` | 대형 타이포 + "AUDIO" 배지 |
| 1 (Green) | `#34a853 → #188038 → #0d652d` | 원형 글래스 아바타 + 이니셜 |
| 2 (Yellow)| `#fbbc04 → #f29900 → #e37400` | 흰 블록 + 업로더 pill |

---

## 2. Typography

Tk 기본 시스템 폰트 사용. `family` 는 mono 영역(`Menlo`) 에만 지정.

| Token / 용도 | 크기 | weight | 색 | 비고 |
|---|---|---|---|---|
| 앱 타이틀 ("GuruNote") | 16 | bold | `C_TEXT` | 사이드바 상단 |
| 화면 제목 (`<h2>`) | 22 | bold | `C_TEXT` | 각 스크린 헤더 |
| 카드 제목 (`<h3>`) | 16 | bold | `C_TEXT` | 카드 헤더 |
| Hero 제목 | 22 | bold | `C_TEXT` | Main Hero |
| 부가 설명 sub | 13 | normal | `C_TEXT_DIM` | 제목 옆 보조 텍스트 |
| 본문 | 13 | normal | `C_TEXT` | 기본 |
| 폼 label | 11 | bold | `C_TEXT_DIM` | uppercase 아님 |
| 입력 텍스트 | 13 | normal | `C_TEXT` | 높이 42~48 |
| chip / pill | 11 | bold | — | 색은 chip 종류별 |
| 버튼 | 13 | bold | — | 색은 버튼 종류별 |
| 타임스탬프 / 경로 / API key | 11~12 | normal | `C_TEXT_DIM` | **`family="Menlo"`** |
| 카드 placeholder 타이포 (Style 0) | 28 | bold | #fff | thumbnail 안 |

---

## 3. Spacing

| 용도 | px |
|---|---|
| 카드 내부 padding (상하좌우) | 24 |
| 카드 헤더 아래 여백 | 16 |
| 폼 필드 사이 | 12 |
| 컴포넌트 그룹 간 큰 간격 | 32 |
| 카드 사이 세로 간격 | 16~20 |
| 화면 전체 좌우 padding | 24 |
| 사이드바 너비 | 240 |
| 탑바 높이 | 56 |

---

## 4. Radius

`gurunote/ui_theme.py`:

| Token | px | 용도 |
|---|---|---|
| `RADIUS_SM` | 8 | 작은 chip, 입력, 배너 |
| `RADIUS_MD` | 12 | 일반 카드, 버튼 |
| `RADIUS_LG` | 16 | 큰 카드, 다이얼로그 컨테이너 |
| `RADIUS_PILL` | 24 | pill 버튼, segmented group, URL input, status pill |

---

## 5. Dimensions (주요 고정값)

| 컴포넌트 | 치수 |
|---|---|
| URL 입력 높이 | 48 |
| Primary CTA 높이 | 48, width 200+ |
| 폼 입력 높이 | 42 |
| Segmented 옵션 높이 | 28 |
| 탭 높이 | 36 (+ 2px underline) |
| 히스토리 카드 썸네일 | 16:9, 최소 width 260 |
| Step indicator 노드 | 32×32 원형 |
| Step indicator 연결선 | height 2 |
| About 로고 블록 | 72×72, radius 18 |
| 재생 버튼 (카드 hover) | 44×44 원형 |

---

## 6. Motion

- 기본 transition: **없음** (Tk 한계)
- hover 상태 전이: 색만 즉시 바뀜
- 카드 hover 효과: **border_color 를 `C_BORDER` → `C_PRIMARY` 로 교체**
  (transform/shadow 불가)
