"""
Phase 5 — NoteEditorDialog 리라이트 (Google Light Theme)
========================================================

`gui.py` 의 `NoteEditorDialog` 의 `_build_ui` + `_configure_preview_tags`
두 메서드를 아래로 교체합니다. 로직(Preview 토글, Cmd+S 저장, dirty 체크)은
그대로 유지하되 색/폰트/여백만 라이트 테마 값으로 바꿉니다.
"""
# ruff: noqa
from __future__ import annotations

import customtkinter as ctk
from gurunote import ui_theme as ut


# =============================================================================
# 대체 블록 — NoteEditorDialog._build_ui
# =============================================================================
def _build_ui(self) -> None:
    self.configure(fg_color=ut.C_BG)

    # 상단 헤더 — 파일 경로 + 제목 + 액션 버튼
    header = ctk.CTkFrame(self, fg_color="transparent")
    header.pack(fill="x", padx=24, pady=(20, 12))

    left = ctk.CTkFrame(header, fg_color="transparent")
    left.pack(side="left", fill="x", expand=True)
    ctk.CTkLabel(
        left, text=f"~/.gurunote/jobs/{self._job_id}/result.md",
        font=ctk.CTkFont(family="Menlo", size=11),
        text_color=ut.C_TEXT_DIM, anchor="w",
    ).pack(fill="x")
    ctk.CTkLabel(
        left, text=self._original_title,
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=ut.C_TEXT, anchor="w",
    ).pack(fill="x", pady=(2, 0))

    # 액션 버튼들 (우측)
    actions = ctk.CTkFrame(header, fg_color="transparent")
    actions.pack(side="right")

    self._preview_btn = ctk.CTkButton(
        actions, text="👁  Preview",
        height=36, corner_radius=ut.RADIUS_PILL,
        fg_color=ut.C_BG, hover_color=ut.C_SURFACE_HI,
        text_color=ut.C_PRIMARY,
        border_width=1, border_color=ut.C_BORDER,
        font=ctk.CTkFont(size=12, weight="bold"),
        command=self._toggle_preview,
    )
    self._preview_btn.pack(side="left", padx=4)

    ctk.CTkButton(
        actions, text="취소",
        height=36, corner_radius=ut.RADIUS_PILL,
        fg_color=ut.C_BG, hover_color=ut.C_SURFACE_HI,
        text_color=ut.C_TEXT_DIM,
        border_width=1, border_color=ut.C_BORDER,
        font=ctk.CTkFont(size=12, weight="bold"),
        command=self._on_close_attempt,
    ).pack(side="left", padx=4)

    ctk.CTkButton(
        actions, text="💾  저장 (⌘S)",
        height=36, width=130, corner_radius=ut.RADIUS_PILL,
        fg_color=ut.C_PRIMARY, hover_color=ut.C_PRIMARY_HO,
        text_color=ut.C_ON_PRIMARY,
        font=ctk.CTkFont(size=12, weight="bold"),
        command=self._on_save_click,
    ).pack(side="left", padx=(4, 0))

    # 분할 본문 (raw | preview)
    body = ctk.CTkFrame(self, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=24, pady=(0, 24))
    body.grid_rowconfigure(0, weight=1)
    body.grid_columnconfigure(0, weight=1, uniform="split")
    body.grid_columnconfigure(1, weight=1, uniform="split")
    self._body_frame = body

    # Raw pane
    raw_frame = ctk.CTkFrame(
        body, fg_color=ut.C_BG, corner_radius=ut.RADIUS_LG,
        border_width=1, border_color=ut.C_BORDER,
    )
    raw_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    raw_head = ctk.CTkFrame(raw_frame, fg_color="transparent", height=40)
    raw_head.pack(fill="x", padx=16, pady=(10, 4))
    raw_head.pack_propagate(False)
    ctk.CTkLabel(
        raw_head, text="< >  Raw · Markdown",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=ut.C_TEXT_DIM,
    ).pack(side="left")

    self._tb = ctk.CTkTextbox(
        raw_frame, wrap="word",
        font=ctk.CTkFont(family="Menlo", size=13),
        fg_color=ut.C_BG, text_color=ut.C_TEXT,
        border_width=0, corner_radius=0,
    )
    self._tb.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    self._tb.insert("1.0", self._initial_md)
    self._tb.bind("<KeyRelease>", lambda _e: self._schedule_preview_refresh())

    # Preview pane
    pv_frame = ctk.CTkFrame(
        body, fg_color=ut.C_BG, corner_radius=ut.RADIUS_LG,
        border_width=1, border_color=ut.C_BORDER,
    )
    pv_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
    pv_head = ctk.CTkFrame(pv_frame, fg_color="transparent", height=40)
    pv_head.pack(fill="x", padx=16, pady=(10, 4))
    pv_head.pack_propagate(False)
    ctk.CTkLabel(
        pv_head, text="📄  Preview · Rendered",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=ut.C_TEXT_DIM,
    ).pack(side="left")

    self._preview = ctk.CTkTextbox(
        pv_frame, wrap="word",
        font=ctk.CTkFont(size=13),
        fg_color=ut.C_BG, text_color=ut.C_TEXT,
        border_width=0, corner_radius=0, state="disabled",
    )
    self._preview.pack(fill="both", expand=True, padx=20, pady=(0, 16))
    self._configure_preview_tags()

    # 키 바인딩
    import platform as _p
    save_key = "<Command-s>" if _p.system() == "Darwin" else "<Control-s>"
    self.bind(save_key, lambda _e: self._on_save_click())


# =============================================================================
# 대체 블록 — NoteEditorDialog._configure_preview_tags
# =============================================================================
def _configure_preview_tags(self) -> None:
    """라이트 테마용 마크다운 렌더링 태그."""
    tb = self._preview
    tb.tag_config("h1", font=ctk.CTkFont(size=22, weight="bold"),
                  foreground=ut.C_TEXT, spacing1=8, spacing3=4)
    tb.tag_config("h2", font=ctk.CTkFont(size=18, weight="bold"),
                  foreground=ut.C_TEXT, spacing1=6, spacing3=3)
    tb.tag_config("h3", font=ctk.CTkFont(size=15, weight="bold"),
                  foreground=ut.C_TEXT)
    tb.tag_config("bold", font=ctk.CTkFont(size=13, weight="bold"),
                  foreground=ut.C_TEXT)
    tb.tag_config("italic", font=ctk.CTkFont(size=13, slant="italic"),
                  foreground=ut.C_TEXT_DIM)
    tb.tag_config(
        "code",
        font=ctk.CTkFont(family="Menlo", size=12),
        foreground="#c7254e",         # Google code red
        background="#f6f8fa",         # GitHub-ish code bg
    )
    tb.tag_config("quote",
                  foreground=ut.C_PRIMARY,
                  lmargin1=20, lmargin2=20,
                  font=ctk.CTkFont(size=13, slant="italic"))
    tb.tag_config("hr", foreground=ut.C_BORDER)
    tb.tag_config("link", foreground=ut.C_PRIMARY, underline=True)
    tb.tag_config("bullet", lmargin1=14, lmargin2=28,
                  foreground=ut.C_TEXT)
    tb.tag_config("ts",
                  font=ctk.CTkFont(family="Menlo", size=12, weight="bold"),
                  foreground=ut.C_PRIMARY)
