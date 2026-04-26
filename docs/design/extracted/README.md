# Design Reference — Extracted Assets

추출 일시: 2026-04-26 (Phase 2A Commit 3a Step 0 재추출)
원본: `docs/design/v2-reference.html` (Claude Design bundler template)

## 컴포넌트 매핑 (정확)

### `screens-main-and-history.jsx`
원본 manifest UUID: `a03bd33a-6fbf-4957-9009-b5ec83c2f6df`

정의된 컴포넌트:
- `MainScreen` — 생성 화면 (URL 입력 + STT/LLM segment + 파이프라인 + 결과 카드)
- `ResultSummary` — 결과 요약 탭 (영상 썸네일 + Insights + Timeline + 마크다운)
- `ResultKorean` — 결과 한국어 전사 탭 (화자 분리)
- `ResultEnglish` — 결과 원문 영어 탭
- `ResultLog` — 결과 로그 탭
- `HistoryScreen` — 히스토리 화면 (검색 + 필터 + 카드 그리드 + facet tree)
- `JobCard` — 히스토리 개별 카드

### `screens-editor-dashboard-settings.jsx`
원본 manifest UUID: `274955f4-a880-489d-b3c1-9b68c666c78a`

정의된 컴포넌트:
- `EditorScreen` — 노트 편집 (split: raw + preview)
- `DashboardScreen` — 대시보드
- `SettingsScreen` — 설정 (.env UI 편집)
- `SettingsLLM` — 설정의 LLM provider 섹션

### `primitives-and-shared.jsx`
원본 manifest UUID: `10b5b24f-4035-412a-ae89-acce512a93fb`

정의된 컴포넌트:
- 모듈 내부 (function 으로 노출 안 됨): `Icon`, `Btn`, `Chip` (arrow function)
- `StepIndicator` — 파이프라인 5-step indicator (Main + Running)
- `FacetTree` — History 의 사이드 facet tree

### `app-sidebar-and-routes.jsx`
원본: template 의 inline `<script type="text/babel">`

정의된 컴포넌트:
- `Sidebar` — 라이트 사이드바 (brand + CTA + 5 nav + 라이브러리 carousel + 사용자 footer)
- `App` — 라우터 (route state + 5 화면 분기 + Tweaks accent/density)
- `TWEAK_DEFAULTS` — 색상/density/showTweaks 기본값

### `material3-from-template.css`
원본: template 의 `<style>` 블록 2개 (Layout shell + Screen-specific)

내용: 약 46,557 chars / ~1,438 라인. 주의: body padding/background 28px,
.gn-window border-radius 14px / box-shadow / height 820px 등 preview chrome 잔재 포함.
production 채택 시 cleanup 필요 (Step 3a-2 에서 이미 한 번 한 cleanup 참고).

## raw/

원본 디코드본 보존:
- `*.js` — 컴포넌트 JSX 파일 3개 + React 런타임 2개 + Babel standalone
- `_template.html` — bundler 풀어진 HTML
- `*.woff2` — 폰트 8개 (Pretendard, JetBrains Mono, Material Symbols Outlined 외)

woff2 size:
- `2b77527d…` 2,057,688 B — Pretendard Variable (가장 큰 가변 폰트)
- `fcb1f6d9…`   317,592 B — Material Symbols Outlined (예상)
- `f05182c0…`    31,432 B
- `d846deb5…`    11,624 B
- `aa18d7d3…`     8,872 B
- `45ad720b…`     6,836 B
- `b07df8bd…`     5,888 B
- `170eba6c…`     1,640 B (가장 작음 — 좁은 unicode-range woff2 일 가능성)

## 어제 (2026-04-25) 추출 누락 (정정)

어제 Step 1 추출본 `main_screen.jsx`, `editor.jsx` 는 a03bd33a 와 274955f4 의
일부만 포함했음:

| 어제 추출본 | 누락된 컴포넌트 |
|---|---|
| main_screen.jsx | HistoryScreen, JobCard |
| editor.jsx | DashboardScreen, SettingsScreen, SettingsLLM |
| primitives.jsx | StepIndicator, FacetTree (10b5b24f 의 일부만) |
| (없음) | Sidebar, App, ROUTES (template inline script) |

이번 재추출에서 모두 보강.

## reference branch

- `archive/commit-2-aborted` (4d7222f) — 어제 Commit 2 보존
- `backup/pre-tailwind-rewrite-20260425` (cedae0e) — Phase 2A 시작점
