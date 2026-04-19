# Apply-All Checklist

각 Phase 순서대로 처리한다. 하나의 Phase 가 끝날 때마다 스모크 테스트 +
커밋. 체크박스를 채우며 진행.

---

## Phase 1 — 전역 테마

- [ ] `patches/ui_theme.py` 를 `gurunote/ui_theme.py` 에 **덮어쓰기**
- [ ] `patches/APPLY.md` § A 블록을 `gui.py` 의 사이드바 빌드 지점에 적용
- [ ] `patches/APPLY.md` § B 블록을 `gui.py` 의 탑바 빌드 지점에 적용
- [ ] `python gui.py` 기동 → 앱 배경이 흰색, 사이드바가 연회색인지 확인
- [ ] `git add -A && git commit -m "ui: phase 1 — light theme tokens + chrome"`

**검증 포인트**
- 사이드바 active 항목에 좌측 3px 파란 rail 이 보인다
- Settings/기타 다이얼로그를 열어도 **크래시 없이** 열린다 (안쪽 스타일은 아직 Phase N)

---

## Phase 2 — History Dialog

- [ ] `patches/history_render_card.py` 의 `_render_card` 메서드를
      `HistoryDialog` 에 교체 주입
- [ ] 같은 파일 하단의 `_render_placeholder` 헬퍼를 **같은 클래스에 추가**
- [ ] `python gui.py` 기동 → History 탭 열기
- [ ] 확인:
  - [ ] 썸네일이 없는 카드가 3-스타일(파랑/초록/노랑) 중 하나로 고정 렌더
  - [ ] 카드 hover 시 중앙에 재생 버튼(▶ 44×44) 등장
  - [ ] 재생 버튼 클릭 → 기본 브라우저로 `source_url` 오픈
  - [ ] 분야 chip 이 파란 soft container 로 표시
  - [ ] status pill 이 상태별로 올바른 (bg, text) 쌍으로 표시
  - [ ] 우클릭 → 노트 에디터가 열린다
- [ ] `git commit -m "ui: phase 2 — history cards (light)"`

---

## Phase 3 — Main 화면

- [ ] `patches/phase3_main_screen.py` 의 상수 `STEP_COLORS` 를
      파일 상단에 추가 (또는 `ui_theme.py` 로 이동)
- [ ] `_build_step_indicator`, `_set_step_state` 를 `GuruNoteApp` 에 추가
- [ ] `_build_input_hero`, `_build_segmented`, `_on_segmented_click` 추가
- [ ] `_build_result_tabs`, `_on_tab_click` 추가
- [ ] 기존 `_build_main_layout` 에서 과거 input 카드/progress 카드/result
      카드를 위 메서드 호출로 교체
- [ ] 확인:
  - [ ] Hero 카드 — 22 bold 제목 + Apple Silicon chip
  - [ ] URL 입력 48h pill + "GuruNote 생성하기" 파란 CTA 48h
  - [ ] STT/LLM segmented pill 이 4개 옵션, 선택 항목만 파란 배경
  - [ ] 파이프라인 시작 시 step indicator 1→2→3→4→5 진행되며 ✓ 채워짐
  - [ ] 결과 탭이 underline 스타일로 표시, 활성 탭만 파란 바
- [ ] `git commit -m "ui: phase 3 — main screen (light)"`

---

## Phase 4 — Settings Dialog

- [ ] `patches/phase4_settings.py` 의 `SettingsDialog` 전체를 기존 클래스와
      교체
- [ ] 확인:
  - [ ] 좌측 네비 6항목 (LLM/STT/Obsidian/Notion/고급/정보)
  - [ ] LLM 섹션: provider 4-up 카드, 선택 시 파란 테두리 + ✓
  - [ ] API Key 필드에 👁 토글 아이콘 동작
  - [ ] STT/Obsidian 에 Detect Banner (연두 배경) 표시
  - [ ] About 섹션에 G 로고 블록 + 버전 mono 텍스트
  - [ ] 저장 버튼 클릭 시 기존 save_settings 호출로 연결됨
- [ ] **로직 연결 TODO**: `_render_llm` 내부의 3-column 파라미터 필드
      (Temperature/Max Tokens) 를 `_field` 로 3번 호출해 실제 Entry 생성.
- [ ] **로직 연결 TODO**: `_on_save` / `_on_test_conn` 의 `messagebox`
      스텁을 기존 `save_settings()` / `test_connection()` 호출로 교체.
- [ ] `git commit -m "ui: phase 4 — settings dialog (light)"`

---

## Phase 5 — Note Editor

- [ ] `NoteEditorDialog._build_ui` 를 `patches/phase5_note_editor.py` 의
      `_build_ui` 로 교체
- [ ] `NoteEditorDialog._configure_preview_tags` 를 해당 패치의 버전으로
      교체
- [ ] `_tb`, `_preview`, `_preview_btn`, `_job_id`, `_initial_md`,
      `_original_title`, `_on_save_click`, `_on_close_attempt`,
      `_toggle_preview`, `_schedule_preview_refresh` 가 원래 클래스에
      존재하는지 확인 — 존재하면 그대로 씀
- [ ] 확인:
  - [ ] 분할 2 pane (Raw | Preview)
  - [ ] Raw pane 이 Menlo 13, Preview 가 system 13
  - [ ] ⌘S(macOS)/Ctrl+S 저장 작동
  - [ ] 제목 옆 dirty dot 표시 로직이 기존대로 유지
  - [ ] Preview 마크다운 렌더 — h1/h2/h3/bold/italic/code/quote/link
  - [ ] 타임스탬프 `00:00` 패턴이 파란 mono 로 강조 (ts 태그 로직이 기존에
        있어야 함 — 없으면 Phase 5에 추가)
- [ ] `git commit -m "ui: phase 5 — note editor (light)"`

---

## 최종 검증

- [ ] `grep -RInE "#[0-9a-fA-F]{6}" gurunote/gui.py` 실행 →
      **Phase 2 placeholder 3 색(그라디언트용) 이외 hex 없음**
- [ ] `ruff check gurunote/` 통과 (또는 기존 baseline 유지)
- [ ] `python -m compileall gurunote` 통과
- [ ] 실제 YouTube URL 1건으로 end-to-end 파이프라인 1회 실행 성공
- [ ] History → 카드 재생 버튼 → 외부 브라우저 오픈 OK
- [ ] Settings 저장 → 재기동 후 값 유지
- [ ] 노트 편집 → ⌘S 저장 → 재오픈 시 반영

---

## 문제 시 우선순위

1. **앱이 안 뜬다** — Phase 1 토큰에 오타/누락이 있다. `ui_theme.py` 가
   `gui.py` 에서 기대하는 모든 상수 (`C_*`, `RADIUS_*`, `STATUS_COLORS`)
   를 export 하는지 확인.
2. **위젯이 깨져 보인다** — customtkinter 는 `border_width` 를 지정해야
   테두리가 나온다. 빠진 곳 없는지 확인.
3. **한글이 안 보인다/깨진다** — font family 를 명시하지 말 것. Tk 기본
   시스템 폰트가 한글을 가장 잘 렌더링한다. 단, mono 영역은 `Menlo` 유지.
4. **색이 이상하다** — `ui_theme.py` 의 상수값을 다시 대조. `C_PRIMARY`
   는 정확히 `#1a73e8`.
