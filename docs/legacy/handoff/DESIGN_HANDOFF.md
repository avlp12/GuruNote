# GuruNote UI Redesign — Handoff Package

**For: Claude Code / Codex / any coding agent**
**Design source of truth:** `GuruNote Redesign.html` (HTML mockup in this project)
**Target codebase:** `gurunote/gui.py` (customtkinter, Python 3.11+)

---

## 0. 목표 한 줄

현재 다크 네이비 톤의 GuruNote 데스크톱 앱을 **Google Workspace 풍
라이트 테마**로 전면 리디자인. 색/타이포/여백/컴포넌트를 모두
아래 토큰 사양에 맞추되, 기존 비즈니스 로직(파이프라인 실행, 설정 저장,
노트 에디터 dirty-check 등)은 **절대 건드리지 않는다.**

---

## 1. 이 패키지 안의 파일

| 파일 | 역할 |
|---|---|
| `DESIGN_HANDOFF.md` | **(이 문서)** 전체 맥락 + 적용 순서 |
| `DESIGN_TOKENS.md` | 색/타이포/여백/라디우스 전체 토큰표 |
| `COMPONENT_SPECS.md` | 버튼/칩/카드/입력 등 컴포넌트별 픽셀 스펙 |
| `APPLY_ALL.md` | Phase 1~5 체크리스트 + 검증 항목 |
| `patches/ui_theme.py` | **Phase 1** 완성본 — `gurunote/ui_theme.py` 로 교체 |
| `patches/APPLY.md` | **Phase 1** `gui.py` 상단 2블록 교체 가이드 |
| `patches/history_render_card.py` | **Phase 2** `HistoryDialog._render_card` drop-in |
| `patches/phase3_main_screen.py` | **Phase 3** Main 화면 블록 모음 |
| `patches/phase4_settings.py` | **Phase 4** `SettingsDialog` 전체 교체본 |
| `patches/phase5_note_editor.py` | **Phase 5** `NoteEditorDialog` 두 메서드 교체본 |
| `GuruNote Redesign.html` | **시각적 레퍼런스** — 렌더링된 최종 형태 |

---

## 2. 기본 원칙 (Non-negotiable)

1. **모든 색은 `ui_theme.py` 상수에서만** 가져온다. `gui.py` 안에 hex
   리터럴이 보이면 버그. 유일한 예외는 Phase 2 placeholder 의 스타일별
   하드코딩 색 3쌍 (Google Blue/Green/Yellow 톤).
2. **폰트 패밀리는 지정하지 않는다** (Tk 기본 시스템 폰트 사용).
   예외는 `family="Menlo"` 로 명시된 mono 영역 (API key, path,
   타임스탬프, 코드 블록).
3. **테두리/그림자** — customtkinter 는 box-shadow 미지원.
   `border_width=1, border_color=ut.C_BORDER` 로 **대체**한다.
   elevation 이 필요한 카드는 `border_width=1` + 충분한 padding 만으로
   표현한다.
4. **라디우스 규칙** — pill = `RADIUS_PILL` (24), large card = `RADIUS_LG`
   (16), medium card = `RADIUS_MD` (12), small chip/input = `RADIUS_SM` (8).
5. **간격 규칙** — 카드 내부 padding 24, 카드 사이 간격 16~20,
   폼 필드 사이 12, 그룹 간 구분선은 쓰지 않고 **간격 32** 로 분리.
6. **Hover/Active 상태**:
   - Primary 버튼: hover = `C_PRIMARY_HO` (더 진한 파랑)
   - Outlined/Ghost: hover = `C_SURFACE_HI` (#f1f3f9)
   - 카드 hover: **transform 금지** (Tk 한계) — 대신 border 색 변경
7. **아이콘** — Material Symbols 이름 대신 **유니코드 심벌 + 이모지**
   (🔗 ▶ ✓ ! 👁 💾 ⚙️ 🎙️ 📓 ☁️ ℹ️ 🤖). Tk 네이티브로 렌더링된다.

---

## 3. HTML ↔ Python 매핑표

| HTML 섹션 | 파일 | Python 대상 |
|---|---|---|
| 전역 CSS 변수 (`--gn-*`) | `patches/ui_theme.py` | `gurunote/ui_theme.py` |
| Sidebar (`.sidebar`) | `patches/APPLY.md` § A | `GuruNoteApp._build_sidebar` |
| Top bar (`.topbar`) | `patches/APPLY.md` § B | `GuruNoteApp._build_topbar` |
| Main 화면 (`MainScreen`) | `patches/phase3_main_screen.py` | `GuruNoteApp._build_main_layout` |
| Step indicator | `patches/phase3_main_screen.py` | `_build_step_indicator` |
| Result tabs | `patches/phase3_main_screen.py` | `_build_result_tabs` |
| History 카드 (`HistoryScreen`) | `patches/history_render_card.py` | `HistoryDialog._render_card` |
| Settings 전체 (`SettingsScreen`) | `patches/phase4_settings.py` | `SettingsDialog` 클래스 |
| Note Editor (`EditorScreen`) | `patches/phase5_note_editor.py` | `NoteEditorDialog._build_ui` |
| Dashboard | **(out of scope)** | 신규 — 지금은 만들지 않음 |

---

## 4. 적용 순서 (엄수)

```
Phase 1 — 전역 테마 (토큰 + 사이드바 + 톱바 색만 교체)
  └─ 여기까지만 적용해도 앱이 깨지지 않고 "라이트 테마" 로 보인다.

Phase 2 — History Dialog
  └─ 카드 3-스타일 placeholder, hover 재생, 분야 chip

Phase 3 — Main 화면
  └─ Hero input card, segmented options, step indicator, result tabs

Phase 4 — Settings Dialog
  └─ 2-column 레이아웃, provider grid, detect banner

Phase 5 — Note Editor
  └─ 헤더 재구성, 라이트 테마용 마크다운 태그
```

**각 Phase 후 `python gui.py` 로 수동 스모크 테스트.**
하나의 Phase 가 끝날 때마다 커밋한다 (`git commit -m "ui: phase N — …"`).

---

## 5. 코딩 에이전트에게 주는 지시 (copy-paste용)

> 당신은 `gurunote/gui.py` 를 리디자인하는 역할이다.
> 1. `DESIGN_TOKENS.md` 와 `COMPONENT_SPECS.md` 를 먼저 전부 읽는다.
> 2. `GuruNote Redesign.html` 을 브라우저(또는 이미지)로 확인해 시각적
>    목표를 머릿속에 고정한다.
> 3. `APPLY_ALL.md` 의 체크리스트를 **Phase 순서대로** 하나씩 처리한다.
> 4. 각 Phase 의 `patches/*.py` 는 **그대로 복붙할 수 있는 형태**로
>    준비돼 있다. `# BEGIN: …` / `# END: …` 주석 블록을 단위로 잘라서
>    `gui.py` 에 주입하거나 해당 메서드/클래스를 교체하라.
> 5. 기존 비즈니스 로직 호출부(파이프라인 실행, save_settings,
>    dirty-check 등)는 **절대 수정하지 않는다**. 시그니처와 내부
>    상태 변수명(예: `self._tb`, `self._preview`, `self._job_id`)은
>    그대로 유지하라.
> 6. Phase 완료마다 `python -m compileall gurunote` 와
>    `python gui.py --smoke` (있으면) 로 최소 검증을 하고,
>    `APPLY_ALL.md` 체크박스를 채운 뒤 커밋한다.
> 7. 불확실한 지점이 있으면 **코드를 추측하지 말고** 해당 섹션의
>    HTML 원본을 그대로 모사하는 방향을 택하라. 토큰 이름이 목록에
>    없으면 `ui_theme.py` 에 새로 추가하지 말고 **가장 가까운
>    기존 토큰을 재사용**하라.

---

## 6. Out of Scope

- Dashboard 화면 (HTML 에는 있지만 이번 리디자인 범위 아님)
- 다크 테마 토글 (Phase 1 에서 라이트만 채택)
- 반응형 (고정 1440+ 데스크톱 전제)
- 애니메이션/트랜지션 (Tk 한계)
- 실제 Material Symbols 폰트 탑재 (유니코드로 대체)

---

## 7. Definition of Done

- [ ] 모든 화면(Main/History/Settings/NoteEditor)이 라이트 테마
- [ ] `gui.py` 안에 하드코딩된 hex 색이 **Phase 2 placeholder 3색 이외**
      에는 없음
- [ ] `ui_theme.py` 의 모든 `C_*`, `RADIUS_*` 상수가 최소 1회 이상 사용됨
- [ ] 파이프라인 1회 end-to-end 실행 성공 (URL → STT → 결과 표시)
- [ ] 설정 저장/로드, 노트 저장(⌘S), 히스토리 재생 버튼 동작
- [ ] `GuruNote Redesign.html` 과 시각적으로 "느낌이 같다" (픽셀 완벽 X)
