"""
Phase 4 — Settings 다이얼로그 리라이트 (Google Light Theme)
==========================================================

`gui.py` 의 `SettingsDialog` 를 아래 구조로 교체합니다.

핵심 변경점
-----------
1. **2-column 레이아웃** — 왼쪽 네비(240px) + 오른쪽 콘텐츠(flex)
2. **Provider Card Grid** — OpenAI/Anthropic/Gemini/Local 을 4-up 카드로
3. **Google 스타일 필드** — 48px height, 12px padding, 1px border
4. **API Key 마스킹 토글** — 눈 아이콘 버튼으로 보기/숨기기
5. **Detect Banner** — 하드웨어/Vault 자동 감지 결과 표시 (green container)
"""
# ruff: noqa
from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional

from gurunote import ui_theme as ut
from gurunote.settings import save_settings


# =============================================================================
# SettingsDialog — 기존 SettingsDialog 클래스 전체를 아래로 교체
# =============================================================================
SETTINGS_SECTIONS = [
    ("llm",      "🤖",  "LLM Provider"),
    ("stt",      "🎙️",  "STT 엔진"),
    ("obsidian", "📓",  "Obsidian Vault"),
    ("notion",   "☁️",  "Notion 통합"),
    ("advanced", "⚙️",  "고급"),
    ("about",    "ℹ️",  "GuruNote 정보"),
]

PROVIDERS = [
    {"key": "openai",    "name": "OpenAI",    "model": "gpt-5.4",           "dot": "#10a37f"},
    {"key": "anthropic", "name": "Anthropic", "model": "claude-sonnet-4-6", "dot": "#d97757"},
    {"key": "gemini",    "name": "Gemini",    "model": "gemini-2.5-flash",  "dot": "#4285f4"},
    {"key": "local",     "name": "Local",     "model": "Ollama / vLLM",     "dot": "#5f6368"},
]


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent)
        self.title("GuruNote · 설정")
        self.geometry("960x680")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=ut.C_BG)
        self._section = ctk.StringVar(value="llm")
        self._build_ui()
        self.after(100, self.focus_force)

    def _build_ui(self) -> None:
        # 헤더
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            header, text="설정",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ut.C_TEXT,
        ).pack(side="left")
        ctk.CTkLabel(
            header, text="API 키 · 엔진 · 통합 관리",
            font=ctk.CTkFont(size=13),
            text_color=ut.C_TEXT_DIM,
        ).pack(side="left", padx=(12, 0), pady=(6, 0))

        # 2-column 본문
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=(12, 24))
        body.grid_columnconfigure(0, weight=0, minsize=240)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # 좌측 네비
        nav = ctk.CTkFrame(
            body, fg_color=ut.C_BG, corner_radius=ut.RADIUS_LG,
            border_width=1, border_color=ut.C_BORDER,
        )
        nav.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self._nav_buttons = {}
        for key, icon, label in SETTINGS_SECTIONS:
            btn = ctk.CTkButton(
                nav, text=f"  {icon}   {label}",
                anchor="w", height=44,
                fg_color="transparent", hover_color=ut.C_SURFACE_HI,
                text_color=ut.C_TEXT,
                font=ctk.CTkFont(size=13),
                corner_radius=ut.RADIUS_SM,
                command=lambda k=key: self._on_select_section(k),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._nav_buttons[key] = btn

        # 콘텐츠 영역
        self._content = ctk.CTkScrollableFrame(body, fg_color="transparent")
        self._content.grid(row=0, column=1, sticky="nsew")

        self._on_select_section("llm")

    def _on_select_section(self, key: str) -> None:
        self._section.set(key)
        # 네비 버튼 색 갱신
        for k, btn in self._nav_buttons.items():
            active = (k == key)
            btn.configure(
                fg_color="#e8f0fe" if active else "transparent",
                text_color=ut.C_PRIMARY if active else ut.C_TEXT,
            )
        # 콘텐츠 재렌더
        for w in self._content.winfo_children():
            w.destroy()
        renderer = {
            "llm":      self._render_llm,
            "stt":      self._render_stt,
            "obsidian": self._render_obsidian,
            "notion":   self._render_notion,
            "advanced": self._render_advanced,
            "about":    self._render_about,
        }[key]
        renderer()

    # -------------------------------------------------------------------------
    # 공통 카드 + 필드 헬퍼
    # -------------------------------------------------------------------------
    def _card(self, title: str, subtitle: Optional[str] = None) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self._content, fg_color=ut.C_BG, corner_radius=ut.RADIUS_LG,
            border_width=1, border_color=ut.C_BORDER,
        )
        card.pack(fill="x", pady=(0, 16))
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            head, text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ut.C_TEXT,
        ).pack(side="left")
        if subtitle:
            ctk.CTkLabel(
                head, text=subtitle,
                font=ctk.CTkFont(size=12), text_color=ut.C_TEXT_DIM,
            ).pack(side="left", padx=(12, 0), pady=(2, 0))
        return card

    def _field(self, parent, label: str, value: str = "",
               password: bool = False, mono: bool = False) -> ctk.CTkEntry:
        """Google 스타일 label + input (outlined)."""
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(
            wrap, text=label,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ut.C_TEXT_DIM,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))
        entry = ctk.CTkEntry(
            wrap, height=42, corner_radius=ut.RADIUS_SM,
            fg_color=ut.C_BG, border_color=ut.C_BORDER, border_width=1,
            text_color=ut.C_TEXT,
            show="•" if password else "",
            font=ctk.CTkFont(
                family="Menlo" if mono else None, size=13,
            ),
        )
        entry.pack(fill="x")
        if value:
            entry.insert(0, value)
        return entry

    def _detect_banner(self, parent, ok: bool, title: str, body: str) -> None:
        bg = "#e6f4ea" if ok else "#feefc3"
        fg = ut.C_SUCCESS if ok else "#b06000"
        icon = "✓" if ok else "!"
        banner = ctk.CTkFrame(
            parent, fg_color=bg, corner_radius=ut.RADIUS_SM,
        )
        banner.pack(fill="x", padx=24, pady=(12, 8))
        ctk.CTkLabel(
            banner, text=f"  {icon}   {title}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=fg, anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(
            banner, text=body,
            font=ctk.CTkFont(size=11), text_color=fg, anchor="w",
            justify="left", wraplength=560,
        ).pack(fill="x", padx=16, pady=(0, 12))

    # -------------------------------------------------------------------------
    # 섹션 렌더러 — LLM
    # -------------------------------------------------------------------------
    def _render_llm(self) -> None:
        import os
        card = self._card("LLM Provider", "번역/요약에 사용됩니다")

        # Provider 카드 그리드 (4-up)
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=24, pady=(12, 16))
        for i in range(4):
            grid.grid_columnconfigure(i, weight=1, uniform="p")

        self._provider_var = ctk.StringVar(value=os.getenv("LLM_PROVIDER", "openai"))
        for i, p in enumerate(PROVIDERS):
            self._provider_button(grid, p, i)

        # API Key
        self._field(card, "OpenAI API Key",
                    value=os.getenv("OPENAI_API_KEY", ""), password=True)
        self._field(card, "모델",
                    value=os.getenv("OPENAI_MODEL", "gpt-5.4"))

        # 3-column 파라미터
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 8))
        for i in range(3):
            row.grid_columnconfigure(i, weight=1)
        # Temperature / Translation / Summary max tokens
        # ... (실제 Entry 생성 로직은 _field 호출 3번)

        # 액션 버튼 row
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=24, pady=(8, 20))
        ctk.CTkButton(
            actions, text="연결 테스트",
            height=40, corner_radius=ut.RADIUS_PILL,
            fg_color=ut.C_BG, hover_color=ut.C_SURFACE_HI,
            text_color=ut.C_PRIMARY,
            border_width=1, border_color=ut.C_BORDER,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_test_conn,
        ).pack(side="left")
        ctk.CTkButton(
            actions, text="저장",
            height=40, width=120, corner_radius=ut.RADIUS_PILL,
            fg_color=ut.C_PRIMARY, hover_color=ut.C_PRIMARY_HO,
            text_color=ut.C_ON_PRIMARY,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_save,
        ).pack(side="right")

    def _provider_button(self, grid, p: dict, col: int) -> None:
        active = (self._provider_var.get() == p["key"])
        frame = ctk.CTkFrame(
            grid,
            fg_color="#e8f0fe" if active else ut.C_BG,
            corner_radius=ut.RADIUS_MD,
            border_width=2 if active else 1,
            border_color=ut.C_PRIMARY if active else ut.C_BORDER,
            height=88,
        )
        frame.grid(row=0, column=col, padx=6, sticky="ew")
        frame.grid_propagate(False)
        # 색 점
        dot = ctk.CTkFrame(
            frame, width=10, height=10, corner_radius=5,
            fg_color=p["dot"],
        )
        dot.place(x=14, y=14)
        ctk.CTkLabel(
            frame, text=p["name"],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ut.C_TEXT,
        ).place(x=32, y=10)
        ctk.CTkLabel(
            frame, text=p["model"],
            font=ctk.CTkFont(family="Menlo", size=11),
            text_color=ut.C_TEXT_DIM,
        ).place(x=14, y=38)
        if active:
            ctk.CTkLabel(
                frame, text="✓",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=ut.C_PRIMARY,
            ).place(relx=1.0, x=-16, y=10, anchor="ne")
        # 클릭
        def _click(_e=None, k=p["key"]):
            self._provider_var.set(k)
            self._render_llm()
        for w in (frame,):
            w.bind("<Button-1>", _click)

    # -------------------------------------------------------------------------
    # 섹션 렌더러 — STT / Obsidian / Notion / Advanced / About
    # -------------------------------------------------------------------------
    def _render_stt(self) -> None:
        import os
        card = self._card("STT 엔진", "자동 감지: Apple Silicon · MLX")
        self._detect_banner(
            card, ok=True, title="MLX Whisper 자동 선택됨",
            body="Apple Silicon M4 Max 감지 · Metal/MPS GPU 가속 활성",
        )
        self._field(card, "MLX Whisper 모델",
                    value=os.getenv("MLX_WHISPER_MODEL", "mlx-community/whisper-large-v3-mlx"),
                    mono=True)
        self._field(card, "HuggingFace Token (화자 분리용)",
                    value=os.getenv("HUGGINGFACE_TOKEN", ""), password=True)
        # 하단 spacing
        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _render_obsidian(self) -> None:
        import os
        card = self._card("Obsidian Vault")
        vault = os.getenv("OBSIDIAN_VAULT_PATH", "")
        if vault:
            self._detect_banner(card, ok=True, title="Vault 감지됨", body=vault)
        self._field(card, "Vault 경로", value=vault, mono=True)
        self._field(card, "하위 폴더",
                    value=os.getenv("OBSIDIAN_SUBFOLDER", "GuruNote"))
        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _render_notion(self) -> None:
        import os
        card = self._card("Notion 통합")
        self._field(card, "Integration Token",
                    value=os.getenv("NOTION_TOKEN", ""), password=True)
        self._field(card, "Parent ID (database / page UUID)",
                    value=os.getenv("NOTION_PARENT_ID", ""), mono=True)
        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _render_advanced(self) -> None:
        card = self._card("고급")
        ctk.CTkLabel(
            card, text="하드웨어 프리셋 · 청크 크기 · 재시도 전략 등",
            font=ctk.CTkFont(size=13), text_color=ut.C_TEXT_DIM,
        ).pack(padx=24, pady=20)

    def _render_about(self) -> None:
        card = self._card("GuruNote")
        ctk.CTkLabel(
            card, text="G",
            width=72, height=72, corner_radius=18,
            fg_color=ut.C_PRIMARY, text_color=ut.C_ON_PRIMARY,
            font=ctk.CTkFont(size=32, weight="bold"),
        ).pack(pady=(24, 12))
        ctk.CTkLabel(
            card, text="GuruNote",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ut.C_TEXT,
        ).pack()
        ctk.CTkLabel(
            card, text="v0.8.0.6",
            font=ctk.CTkFont(family="Menlo", size=11),
            text_color=ut.C_TEXT_DIM,
        ).pack(pady=(0, 12))
        ctk.CTkLabel(
            card,
            text="유튜브 링크 한 줄로 해외 IT/AI 팟캐스트를\n화자 분리된 한국어 마크다운 요약본으로.",
            font=ctk.CTkFont(size=12), text_color=ut.C_TEXT_DIM,
            justify="center",
        ).pack(pady=(0, 24))

    # -------------------------------------------------------------------------
    # 핸들러
    # -------------------------------------------------------------------------
    def _on_test_conn(self) -> None:
        messagebox.showinfo("연결 테스트", "구현 필요 — 기존 test_connection() 호출")

    def _on_save(self) -> None:
        messagebox.showinfo("저장", "구현 필요 — 기존 save_settings() 호출")
