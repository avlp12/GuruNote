"""
Phase 3 — Main 화면 리라이트 패치 (Google Light Theme)
======================================================

`gui.py` 의 `GuruNoteApp._build_main_layout` / `_build_input_card` /
`_build_progress_card` / `_build_result_card` 에 해당하는 영역을 아래 코드로
교체하세요. 함수 시그니처/이름은 현재 `gui.py` 와 맞추어 **최소 침습**
적용이 가능합니다.

핵심 변경점
-----------
1. **Hero Input Card** — 64px height CTA, 48px URL 입력, segmented STT/LLM 옵션
2. **Step Indicator** — 5단계 원형 노드 + 진행 라인 (파랑 #1a73e8 진행, 회색 #dadce0 기본)
3. **결과 탭** — Google 스타일 underline tab (active 아래 2px 파란 선)
4. **그림자 대체** — ctk 는 box-shadow 미지원 → `border_color=C_BORDER` + 1px border
5. **폰트** — Pretendard 우선, 없으면 SF Pro / Apple SD Gothic / Segoe UI

이 파일은 "복붙해서 넣을 블록 모음" 형태입니다. `# BEGIN ...` / `# END ...`
주석으로 각 블록의 위치를 표시했습니다.
"""
# ruff: noqa
# =============================================================================
# 공통 상수 — 파일 상단에 추가
# =============================================================================
# BEGIN: STEP_COLORS
STEP_COLORS = {
    "done":    ("#1a73e8", "#ffffff"),  # (fill, text) — 완료
    "active":  ("#1a73e8", "#ffffff"),  # 진행 중 (pulse ring 추가)
    "pending": ("#f1f3f9", "#5f6368"),  # 대기
}
# END


# =============================================================================
# BEGIN: _build_step_indicator
# gui.py 의 GuruNoteApp 클래스 내부에 추가 (기존 progress-bar 는 유지해도 됨)
# =============================================================================
def _build_step_indicator(self, parent) -> None:
    """5단계 원형 노드 + 진행 라인.

    Pipeline step 5개:  오디오 → STT → 번역 → 요약 → 조립
    `self._step_nodes` 에 (circle, label) 튜플 리스트를 저장해
    `_set_step_state(idx, state)` 로 갱신.
    """
    import customtkinter as ctk
    from gurunote import ui_theme as ut

    wrap = ctk.CTkFrame(parent, fg_color="transparent")
    wrap.pack(fill="x", padx=24, pady=(8, 4))

    # 노드 + 연결선을 겹쳐 그리기 위해 grid 사용
    for i in range(9):  # 5 nodes + 4 connectors
        wrap.grid_columnconfigure(i, weight=1 if i % 2 == 1 else 0)

    self._step_nodes = []
    self._step_connectors = []
    labels = ["오디오", "STT", "번역", "요약", "조립"]

    for i, name in enumerate(labels):
        col = i * 2
        node = ctk.CTkFrame(
            wrap, width=32, height=32, corner_radius=16,
            fg_color=ut.C_SURFACE_HI, border_width=0,
        )
        node.grid(row=0, column=col, padx=4)
        node.grid_propagate(False)
        num = ctk.CTkLabel(
            node, text=str(i + 1),
            text_color=ut.C_TEXT_DIM,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        num.place(relx=0.5, rely=0.5, anchor="center")

        lbl = ctk.CTkLabel(
            wrap, text=name,
            text_color=ut.C_TEXT_DIM,
            font=ctk.CTkFont(size=11),
        )
        lbl.grid(row=1, column=col, pady=(6, 0))

        self._step_nodes.append((node, num, lbl))

        # connector line (마지막 노드 다음엔 없음)
        if i < len(labels) - 1:
            line = ctk.CTkFrame(wrap, height=2, fg_color=ut.C_BORDER)
            line.grid(row=0, column=col + 1, sticky="ew")
            self._step_connectors.append(line)


def _set_step_state(self, idx: int, state: str) -> None:
    """state: 'pending' | 'active' | 'done'."""
    from gurunote import ui_theme as ut
    if not hasattr(self, "_step_nodes"):
        return
    node, num, lbl = self._step_nodes[idx]
    if state == "done":
        node.configure(fg_color=ut.C_PRIMARY)
        num.configure(text="✓", text_color=ut.C_ON_PRIMARY)
        lbl.configure(text_color=ut.C_PRIMARY)
    elif state == "active":
        node.configure(fg_color=ut.C_PRIMARY)
        num.configure(text=str(idx + 1), text_color=ut.C_ON_PRIMARY)
        lbl.configure(text_color=ut.C_PRIMARY)
    else:
        node.configure(fg_color=ut.C_SURFACE_HI)
        num.configure(text=str(idx + 1), text_color=ut.C_TEXT_DIM)
        lbl.configure(text_color=ut.C_TEXT_DIM)
    # 완료된 단계 이전 connector 들은 파란색
    for i, line in enumerate(self._step_connectors):
        done = (state in ("done",) and idx > i) or (idx > i)
        line.configure(fg_color=ut.C_PRIMARY if done else ut.C_BORDER)
# END: _build_step_indicator


# =============================================================================
# BEGIN: _build_input_hero
# =============================================================================
def _build_input_hero(self, parent) -> None:
    """Hero input card — 큰 제목, URL 입력, 옵션 row."""
    import customtkinter as ctk
    from gurunote import ui_theme as ut

    hero = ctk.CTkFrame(
        parent, fg_color=ut.C_BG, corner_radius=ut.RADIUS_LG,
        border_width=1, border_color=ut.C_BORDER,
    )
    hero.pack(fill="x", padx=20, pady=(20, 12))

    # 헤더 행
    head = ctk.CTkFrame(hero, fg_color="transparent")
    head.pack(fill="x", padx=24, pady=(20, 8))
    ctk.CTkLabel(
        head, text="지식을 증류하세요",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color=ut.C_TEXT,
    ).pack(side="left")
    ctk.CTkLabel(
        head, text="Apple Silicon · MLX",
        fg_color="#e8f0fe", text_color=ut.C_PRIMARY,
        corner_radius=ut.RADIUS_PILL,
        font=ctk.CTkFont(size=11, weight="bold"),
        padx=12, pady=4,
    ).pack(side="right")

    ctk.CTkLabel(
        hero,
        text="유튜브 링크 한 줄로 해외 IT/AI 팟캐스트를 화자 분리된 한국어 요약본으로",
        font=ctk.CTkFont(size=13),
        text_color=ut.C_TEXT_DIM,
        anchor="w", justify="left",
    ).pack(fill="x", padx=24, pady=(0, 16))

    # URL 입력 + CTA
    row = ctk.CTkFrame(hero, fg_color="transparent")
    row.pack(fill="x", padx=24, pady=(0, 12))
    self.url_entry = ctk.CTkEntry(
        row, height=48, corner_radius=24,
        fg_color=ut.C_BG, border_color=ut.C_BORDER, border_width=1,
        text_color=ut.C_TEXT, placeholder_text_color=ut.C_TEXT_DIM,
        placeholder_text="🔗  https://youtube.com/watch?v=...",
        font=ctk.CTkFont(size=14),
    )
    self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

    self.run_btn = ctk.CTkButton(
        row, text="▶  GuruNote 생성하기",
        height=48, width=200, corner_radius=24,
        fg_color=ut.C_PRIMARY, hover_color=ut.C_PRIMARY_HO,
        text_color=ut.C_ON_PRIMARY,
        font=ctk.CTkFont(size=14, weight="bold"),
        command=self._on_run_clicked,
    )
    self.run_btn.pack(side="right")

    # 옵션 row — STT / LLM segmented
    opts = ctk.CTkFrame(hero, fg_color="transparent")
    opts.pack(fill="x", padx=24, pady=(0, 20))

    self._stt_var = ctk.StringVar(value="auto")
    self._llm_var = ctk.StringVar(value="openai")

    self._build_segmented(opts, "STT 엔진", self._stt_var,
                          ["auto", "whisperx", "mlx", "assemblyai"])
    self._build_segmented(opts, "LLM Provider", self._llm_var,
                          ["openai", "anthropic", "gemini", "local"])


def _build_segmented(self, parent, label: str, var, options: list[str]) -> None:
    """Google 스타일 segmented pill group."""
    import customtkinter as ctk
    from gurunote import ui_theme as ut

    group = ctk.CTkFrame(parent, fg_color="transparent")
    group.pack(side="left", padx=(0, 24), pady=4)
    ctk.CTkLabel(
        group, text=label,
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=ut.C_TEXT_DIM,
    ).pack(anchor="w", pady=(0, 6))

    seg = ctk.CTkFrame(
        group, fg_color=ut.C_SIDEBAR, corner_radius=ut.RADIUS_PILL,
        border_width=1, border_color=ut.C_BORDER,
    )
    seg.pack(anchor="w")
    for opt in options:
        btn = ctk.CTkButton(
            seg, text=opt, height=28, corner_radius=ut.RADIUS_PILL,
            fg_color="transparent", hover_color=ut.C_SURFACE_HI,
            text_color=ut.C_TEXT_DIM,
            font=ctk.CTkFont(size=12),
            command=lambda o=opt: self._on_segmented_click(var, o),
        )
        btn.pack(side="left", padx=2, pady=2)
        # 선택 상태 반영 (initial)
        if var.get() == opt:
            btn.configure(fg_color=ut.C_PRIMARY, text_color=ut.C_ON_PRIMARY)


def _on_segmented_click(self, var, option: str) -> None:
    var.set(option)
    # 전체 재렌더는 비싸므로 호출측에서 해당 그룹만 갱신하는 것이 이상적.
    # MVP 는 var 업데이트만, 시각적 갱신은 다음 렌더 사이클에서 처리.
# END: _build_input_hero


# =============================================================================
# BEGIN: _build_result_tabs
# 결과 카드 상단의 탭 스트립 — Google underline tab
# =============================================================================
def _build_result_tabs(self, parent, tabs: list[tuple[str, str]]) -> None:
    """tabs: [(key, label), ...]"""
    import customtkinter as ctk
    from gurunote import ui_theme as ut

    bar = ctk.CTkFrame(parent, fg_color="transparent", height=44)
    bar.pack(fill="x", padx=20)
    bar.pack_propagate(False)

    self._tab_buttons = {}
    self._tab_underlines = {}
    for key, label in tabs:
        col = ctk.CTkFrame(bar, fg_color="transparent")
        col.pack(side="left", padx=(0, 20))
        btn = ctk.CTkButton(
            col, text=label, height=36,
            fg_color="transparent", hover_color=ut.C_SURFACE_HI,
            text_color=ut.C_TEXT_DIM,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda k=key: self._on_tab_click(k),
        )
        btn.pack()
        underline = ctk.CTkFrame(col, height=2, fg_color="transparent")
        underline.pack(fill="x")
        self._tab_buttons[key] = btn
        self._tab_underlines[key] = underline


def _on_tab_click(self, key: str) -> None:
    from gurunote import ui_theme as ut
    for k, btn in self._tab_buttons.items():
        active = (k == key)
        btn.configure(
            text_color=ut.C_PRIMARY if active else ut.C_TEXT_DIM,
        )
        self._tab_underlines[k].configure(
            fg_color=ut.C_PRIMARY if active else "transparent",
        )
    self._active_tab = key
    self._render_active_tab()
# END: _build_result_tabs
