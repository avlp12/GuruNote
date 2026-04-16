"""
GuruNote 🎙️ — CustomTkinter 네이티브 데스크톱 GUI
====================================================

Streamlit 없이도 독립 실행 가능한 데스크톱 애플리케이션.
`gurunote.*` 패키지를 직접 호출하며, 파이프라인(Step 1~5)은
백그라운드 스레드에서 실행해 UI가 멈추지 않는다.

실행:
    python gui.py

패키징:
    pyinstaller --windowed --onefile gui.py
"""

from __future__ import annotations

import os
import queue
import tempfile
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk
from dotenv import load_dotenv

from gurunote.audio import (
    SUPPORTED_EXTS,
    cleanup_dir,
    download_audio,
    extract_audio_from_file,
    is_probably_youtube_url,
    is_supported_local_file,
)
from gurunote.exporter import build_gurunote_markdown, sanitize_filename
from gurunote.llm import LLMConfig, summarize_translation, test_connection, translate_transcript
from gurunote.settings import save_settings
from gurunote.stt import install_vibevoice, is_vibevoice_installed, transcribe
from gurunote.types import _format_ts
from gurunote.updater import check_updates, update_project

# 환경변수 로드
load_dotenv()

# =============================================================================
# 테마 & 상수
# =============================================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_TITLE = "GuruNote"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 820

STT_OPTIONS = ["auto", "vibevoice", "assemblyai"]
LLM_OPTIONS = ["openai", "openai_compatible", "anthropic"]

# ── 브랜드 컬러 팔레트 ──
C_BG = "#1A1B2E"
C_SIDEBAR = "#212240"
C_SURFACE = "#262842"
C_SURFACE_HI = "#303260"
C_BORDER = "#3A3C5E"
C_PRIMARY = "#6C63FF"
C_PRIMARY_HO = "#5A52E0"
C_ACCENT = "#22D3EE"
C_TEXT = "#E8E8F0"
C_TEXT_DIM = "#8B8DA8"
C_SUCCESS = "#4ADE80"
C_DANGER = "#F87171"
STEP_LABELS = ["오디오", "STT", "번역", "요약", "조립"]


# =============================================================================
# 파이프라인 워커 (백그라운드 스레드)
# =============================================================================
class PipelineWorker:
    """
    GUI 스레드를 블로킹하지 않고 파이프라인을 실행한다.
    진행 메시지는 `msg_queue`로, 최종 결과/에러는 `result_queue`로 전달.
    """

    def __init__(
        self,
        engine: str,
        provider: str,
        *,
        youtube_url: str = "",
        local_file: str = "",
    ):
        self.youtube_url = youtube_url
        self.local_file = local_file
        self.engine = engine
        self.provider = provider
        self.msg_queue: queue.Queue[str] = queue.Queue()
        self.progress_queue: queue.Queue[float] = queue.Queue()
        self.result_queue: queue.Queue[dict] = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _log(self, msg: str) -> None:
        if self._stop_event.is_set():
            raise RuntimeError("사용자가 작업 중지를 요청했습니다.")
        self.msg_queue.put(msg)

    def _set_progress(self, pct: float) -> None:
        self.progress_queue.put(max(0.0, min(1.0, pct)))

    def request_stop(self) -> None:
        self._stop_event.set()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        tmp_dir = tempfile.mkdtemp(prefix="gurunote_")
        try:
            self._set_progress(0.02)
            # Step 1
            if self.youtube_url:
                self._log("⬇️ [Step 1] 유튜브 오디오 추출 중…")
                audio = download_audio(self.youtube_url, tmp_dir)
            else:
                self._log("🎵 [Step 1] 로컬 파일에서 오디오 추출 중…")
                audio = extract_audio_from_file(self.local_file, tmp_dir)
            audio_size = os.path.getsize(audio.audio_path) / (1024 * 1024)
            self._log(
                f"✅ [Step 1] {audio.video_title} ({audio_size:.1f} MB, "
                f"{int(audio.duration_sec)}s)"
            )
            if audio.upload_date:
                self._log(f"📅 게시일: {audio.upload_date}")
            if audio.chapters:
                self._log(f"⏱️ 공식 챕터 {len(audio.chapters)}개 감지")
            if audio.subtitles_text:
                self._log(
                    f"💬 기존 자막 감지 ({len(audio.subtitles_text):,} chars) — "
                    "화자 이름/챕터 참고에 활용"
                )
            video_ctx = audio.to_context_dict()
            self._set_progress(0.18)
            effective_engine = self.engine
            if audio.duration_sec > 3600 and self.engine == "auto":
                effective_engine = "assemblyai"
                self._log("ℹ️ 60분 초과 오디오는 auto 모드에서 AssemblyAI 로 자동 전환합니다.")
            elif audio.duration_sec > 3600 and self.engine == "vibevoice":
                self._log(
                    "⚠️ VibeVoice 단일 패스는 최대 60분 처리에 최적화되어 있어 "
                    "긴 영상은 일부만 전사될 수 있습니다."
                )

            # Step 2
            self._log("🎙️ [Step 2] 화자 분리 STT 중…")
            transcript = transcribe(
                audio.audio_path,
                engine=effective_engine,
                progress=self._log,
            )
            self._log(
                f"✅ [Step 2] {len(transcript.segments)} 세그먼트, "
                f"{len(transcript.speakers)} 화자, 엔진={transcript.engine}"
            )
            self._set_progress(0.55)

            # Step 3
            self._log("🌐 [Step 3] LLM 한국어 번역 중…")
            llm_cfg = LLMConfig.from_env(provider=self.provider)
            translated = translate_transcript(
                transcript, config=llm_cfg, progress=self._log,
                video_context=video_ctx,
            )
            self._log(f"✅ [Step 3] 번역 완료 ({len(translated):,} chars)")
            self._set_progress(0.78)

            # Step 4
            self._log("📝 [Step 4] GuruNote 요약본 생성 중…")
            summary_md = summarize_translation(
                translated,
                title=audio.video_title,
                config=llm_cfg,
                progress=self._log,
                video_context=video_ctx,
            )
            self._log("✅ [Step 4] 요약 완료")
            self._set_progress(0.90)

            # Step 5
            self._log("📦 [Step 5] 마크다운 조립 중…")
            full_md = build_gurunote_markdown(
                title=audio.video_title,
                webpage_url=audio.webpage_url,
                summary_md=summary_md,
                translated_text=translated,
                transcript=transcript,
                uploader=audio.uploader,
                stt_engine=transcript.engine,
                upload_date=audio.upload_date,
                chapters=audio.chapters,
                subtitles_source=audio.subtitles_source,
            )
            self._log("🎉 GuruNote 생성 완료!")
            self._set_progress(1.0)

            self.result_queue.put(
                {
                    "ok": True,
                    "audio": audio,
                    "transcript": transcript,
                    "translated": translated,
                    "summary_md": summary_md,
                    "full_md": full_md,
                }
            )
        except Exception as exc:
            self.msg_queue.put(f"❌ 오류: {exc}")
            self.result_queue.put({"ok": False, "error": str(exc)})
        finally:
            cleanup_dir(tmp_dir)


# =============================================================================
# 설정 다이얼로그 (API 키 관리)
# =============================================================================
# 설정 필드 정의: (환경변수명, 라벨, 마스킹 여부)
_SETTINGS_FIELDS = [
    ("LLM_PROVIDER", "LLM Provider (openai/openai_compatible/anthropic)", False),
    ("OPENAI_API_KEY", "OpenAI API Key", True),
    ("OPENAI_BASE_URL", "OpenAI Base URL (Local/Compatible)", False),
    ("OPENAI_MODEL", "OpenAI 모델", False),
    ("ANTHROPIC_API_KEY", "Anthropic API Key", True),
    ("ANTHROPIC_MODEL", "Anthropic 모델", False),
    ("LLM_TEMPERATURE", "LLM Temperature", False),
    ("LLM_TRANSLATION_MAX_TOKENS", "번역 Max Tokens", False),
    ("LLM_SUMMARY_MAX_TOKENS", "요약 Max Tokens", False),
    ("ASSEMBLYAI_API_KEY", "AssemblyAI API Key (폴백용)", True),
    ("VIBEVOICE_MODEL_ID", "VibeVoice 모델 ID", False),
    ("HUGGINGFACE_TOKEN", "HuggingFace 토큰 (선택)", True),
]


class SettingsDialog(ctk.CTkToplevel):
    """API 키와 모델 설정을 입력/저장하는 모달 다이얼로그."""

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent)
        self.title("⚙️ GuruNote 설정")
        self.geometry("620x560")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._entries: dict[str, ctk.CTkEntry] = {}
        self._show_vars: dict[str, bool] = {}

        self._build_ui()
        self.after(100, self.focus_force)

    def _build_ui(self) -> None:
        # 스크롤 가능한 프레임
        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        container.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            container,
            text="API 키 및 모델 설정",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ctk.CTkLabel(
            container,
            text="저장 시 .env 파일에 기록되며, 앱 재시작 없이 즉시 반영됩니다.",
            font=ctk.CTkFont(size=11),
            text_color="gray55",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 12))

        for idx, (env_key, label, is_secret) in enumerate(_SETTINGS_FIELDS, start=2):
            ctk.CTkLabel(
                container, text=label, font=ctk.CTkFont(size=13)
            ).grid(row=idx, column=0, sticky="w", padx=(0, 10), pady=6)

            current_val = os.environ.get(env_key, "")
            entry = ctk.CTkEntry(
                container,
                width=300,
                show="•" if is_secret and current_val else "",
                placeholder_text="미설정" if is_secret else "",
            )
            if current_val:
                entry.insert(0, current_val)
            entry.grid(row=idx, column=1, sticky="ew", pady=6)
            self._entries[env_key] = entry
            self._show_vars[env_key] = False

            if is_secret:
                toggle_btn = ctk.CTkButton(
                    container,
                    text="👁",
                    width=36,
                    height=28,
                    command=lambda k=env_key: self._toggle_show(k),
                )
                toggle_btn.grid(row=idx, column=2, padx=(4, 0), pady=6)

        # 하단 버튼 바
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(4, 16))

        ctk.CTkButton(
            btn_frame, text="취소", width=80, fg_color="gray40", command=self.destroy
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame,
            text="💾 저장",
            width=120,
            font=ctk.CTkFont(weight="bold"),
            command=self._on_save,
        ).pack(side="right")
        ctk.CTkButton(
            btn_frame,
            text="🧪 연결 테스트",
            width=120,
            fg_color="gray30",
            hover_color="gray40",
            command=self._on_test_connection,
        ).pack(side="left")
        ctk.CTkButton(
            btn_frame,
            text="🔄 업데이트",
            width=120,
            fg_color="gray30",
            hover_color="gray40",
            command=self._on_update,
        ).pack(side="left", padx=(8, 0))

    def _toggle_show(self, env_key: str) -> None:
        self._show_vars[env_key] = not self._show_vars[env_key]
        entry = self._entries[env_key]
        entry.configure(show="" if self._show_vars[env_key] else "•")

    def _on_save(self) -> None:
        payload = {
            key: self._entries[key].get().strip()
            for key, _label, _is_secret in _SETTINGS_FIELDS
        }
        changed, backup = save_settings(payload, create_backup=True)

        if changed:
            backup_name = backup.name if backup else "-"
            messagebox.showinfo(
                "설정 저장",
                f"{changed} 개 항목이 저장되었습니다.\n백업: {backup_name}",
            )
        else:
            messagebox.showinfo("설정 저장", "변경된 항목이 없습니다.")
        self.destroy()

    def _on_test_connection(self) -> None:
        provider = self._entries["LLM_PROVIDER"].get().strip() or "openai"
        cfg = LLMConfig.from_env(provider=provider)
        if provider == "anthropic":
            cfg.api_key = self._entries["ANTHROPIC_API_KEY"].get().strip()
            cfg.model = self._entries["ANTHROPIC_MODEL"].get().strip() or cfg.model
        else:
            cfg.api_key = self._entries["OPENAI_API_KEY"].get().strip()
            cfg.base_url = self._entries["OPENAI_BASE_URL"].get().strip()
            cfg.model = self._entries["OPENAI_MODEL"].get().strip() or cfg.model
        try:
            cfg.temperature = float(self._entries["LLM_TEMPERATURE"].get().strip() or "0.2")
            resp = test_connection(cfg)
            messagebox.showinfo("연결 테스트", f"성공: {resp}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("연결 테스트 실패", str(exc))

    def _on_update(self) -> None:
        try:
            logs: list[str] = []
            status = check_updates(logs.append)
            ok = messagebox.askyesno(
                "업데이트 확인",
                f"{status}\n\n업데이트를 실행할까요? (git pull + pip upgrade)",
            )
            if not ok:
                return
            logs = []
            update_project(logs.append, upgrade_deps=True)
            messagebox.showinfo("업데이트 완료", "업데이트가 완료되었습니다.\n앱을 재시작해주세요.")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("업데이트 실패", str(exc))


# =============================================================================
# 메인 애플리케이션 (사이드바 + 카드 레이아웃 리디자인)
# =============================================================================
def _card(parent, **kw):
    d = dict(fg_color=C_SURFACE, corner_radius=12, border_width=1, border_color=C_BORDER)
    d.update(kw)
    return ctk.CTkFrame(parent, **d)


class GuruNoteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1000, 700)
        self.configure(fg_color=C_BG)
        self._worker = None
        self._result = None
        self._local_file_path = ""
        self._step_labels = []
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    # ── 사이드바 ─────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, fg_color=C_SIDEBAR, width=200, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(4, weight=1)
        sb.grid_columnconfigure(0, weight=1)
        brand = ctk.CTkFrame(sb, fg_color="transparent")
        brand.grid(row=0, column=0, padx=16, pady=(24, 4), sticky="ew")
        ctk.CTkLabel(brand, text="🎙️", font=ctk.CTkFont(size=32)).pack(side="left")
        ctk.CTkLabel(brand, text=" GuruNote", font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=C_TEXT).pack(side="left", padx=(4, 0))
        ctk.CTkLabel(sb, text="글로벌 IT/AI 구루의 인사이트",
                     font=ctk.CTkFont(size=11), text_color=C_TEXT_DIM
                     ).grid(row=1, column=0, padx=20, sticky="w", pady=(0, 20))
        for i, (txt, cmd) in enumerate([("⚙️  설정", self._on_settings),
                                         ("🔄  업데이트", self._on_update_sb)]):
            ctk.CTkButton(sb, text=txt, anchor="w", height=36, fg_color="transparent",
                          hover_color=C_SURFACE_HI, text_color=C_TEXT_DIM,
                          font=ctk.CTkFont(size=13), command=cmd
                          ).grid(row=2 + i, column=0, padx=10, pady=2, sticky="ew")
        ctk.CTkLabel(sb, text="v0.2.0", font=ctk.CTkFont(size=10),
                     text_color=C_TEXT_DIM).grid(row=5, column=0, padx=20, pady=(0, 16), sticky="sw")

    # ── 메인 영역 ────────────────────────────────────────────
    def _build_main(self):
        m = ctk.CTkFrame(self, fg_color=C_BG, corner_radius=0)
        m.grid(row=0, column=1, sticky="nsew")
        m.grid_columnconfigure(0, weight=1)
        m.grid_rowconfigure(2, weight=1)
        self._build_input_card(m, 0)
        self._build_progress_card(m, 1)
        self._build_result_card(m, 2)

    def _build_input_card(self, p, r):
        c = _card(p)
        c.grid(row=r, column=0, padx=20, pady=(20, 8), sticky="ew")
        c.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(c, text="오디오 소스", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C_TEXT).grid(row=0, column=0, columnspan=4, padx=16, pady=(14, 8), sticky="w")
        ctk.CTkButton(c, text="📁", width=40, height=40, corner_radius=8,
                      fg_color=C_SURFACE_HI, hover_color=C_BORDER,
                      command=self._on_pick_file).grid(row=1, column=0, padx=(16, 6), pady=(0, 14))
        self._url_entry = ctk.CTkEntry(c, height=40, corner_radius=8,
                                       placeholder_text="유튜브 URL 붙여넣기 또는 📁 로컬 파일 선택",
                                       fg_color=C_BG, border_color=C_BORDER, text_color=C_TEXT)
        self._url_entry.grid(row=1, column=1, padx=4, pady=(0, 14), sticky="ew")
        of = ctk.CTkFrame(c, fg_color="transparent")
        of.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 14), sticky="ew")
        of.grid_columnconfigure(4, weight=1)
        ctk.CTkLabel(of, text="STT", text_color=C_TEXT_DIM, font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 6))
        self._stt_var = ctk.StringVar(value=os.environ.get("GURUNOTE_STT_ENGINE", "auto"))
        ctk.CTkOptionMenu(of, variable=self._stt_var, values=STT_OPTIONS, width=130, height=32,
                          corner_radius=8, fg_color=C_SURFACE_HI, button_color=C_BORDER).grid(row=0, column=1, padx=(0, 16))
        ctk.CTkLabel(of, text="LLM", text_color=C_TEXT_DIM, font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=(0, 6))
        self._llm_var = ctk.StringVar(value=os.environ.get("LLM_PROVIDER", "openai"))
        ctk.CTkOptionMenu(of, variable=self._llm_var, values=LLM_OPTIONS, width=160, height=32,
                          corner_radius=8, fg_color=C_SURFACE_HI, button_color=C_BORDER).grid(row=0, column=3, padx=(0, 16))
        self._run_btn = ctk.CTkButton(of, text="▶  GuruNote 생성하기", height=36, width=200, corner_radius=8,
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      fg_color=C_PRIMARY, hover_color=C_PRIMARY_HO, command=self._on_run)
        self._run_btn.grid(row=0, column=5, padx=(0, 6))
        self._stop_btn = ctk.CTkButton(of, text="⏹", height=36, width=36, corner_radius=8,
                                       fg_color=C_SURFACE_HI, hover_color=C_DANGER, state="disabled", command=self._on_stop)
        self._stop_btn.grid(row=0, column=6)

    def _build_progress_card(self, p, r):
        c = _card(p)
        c.grid(row=r, column=0, padx=20, pady=8, sticky="ew")
        c.grid_columnconfigure(0, weight=1)
        sf = ctk.CTkFrame(c, fg_color="transparent")
        sf.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="ew")
        self._step_labels = []
        for i, lb in enumerate(STEP_LABELS):
            if i > 0:
                ctk.CTkLabel(sf, text="───", text_color=C_BORDER, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
            sl = ctk.CTkLabel(sf, text=f" {i+1}. {lb} ", font=ctk.CTkFont(size=11),
                              text_color=C_TEXT_DIM, fg_color=C_SURFACE_HI, corner_radius=6)
            sl.pack(side="left", padx=2)
            self._step_labels.append(sl)
        pw = ctk.CTkFrame(c, fg_color="transparent")
        pw.grid(row=1, column=0, padx=16, pady=(0, 4), sticky="ew")
        pw.grid_columnconfigure(0, weight=1)
        self._progress = ctk.CTkProgressBar(pw, height=6, corner_radius=3,
                                            fg_color=C_SURFACE_HI, progress_color=C_ACCENT)
        self._progress.grid(row=0, column=0, sticky="ew")
        self._progress.set(0)
        self._progress_label = ctk.CTkLabel(pw, text="대기 중", font=ctk.CTkFont(size=11), text_color=C_TEXT_DIM)
        self._progress_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
        self._last_log_label = ctk.CTkLabel(c, text="", font=ctk.CTkFont(size=11),
                                            text_color=C_TEXT_DIM, anchor="w", wraplength=800)
        self._last_log_label.grid(row=2, column=0, padx=16, pady=(0, 12), sticky="ew")

    def _build_result_card(self, p, r):
        c = _card(p)
        c.grid(row=r, column=0, padx=20, pady=(8, 20), sticky="nsew")
        c.grid_rowconfigure(1, weight=1)
        c.grid_columnconfigure(0, weight=1)
        top = ctk.CTkFrame(c, fg_color="transparent")
        top.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="ew")
        top.grid_columnconfigure(0, weight=1)
        self._title_label = ctk.CTkLabel(top, text="결과", font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT)
        self._title_label.grid(row=0, column=0, sticky="w")
        self._save_btn = ctk.CTkButton(top, text="📥 마크다운 저장", height=32, width=140, corner_radius=8,
                                       fg_color=C_SURFACE_HI, hover_color=C_PRIMARY, state="disabled", command=self._on_save)
        self._save_btn.grid(row=0, column=1, sticky="e")
        self._tabview = ctk.CTkTabview(c, height=300, corner_radius=8, fg_color=C_SURFACE,
                                       segmented_button_fg_color=C_SURFACE_HI,
                                       segmented_button_selected_color=C_PRIMARY,
                                       segmented_button_unselected_color=C_SURFACE_HI)
        self._tabview.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self._tab_summary = self._tabview.add("📌 요약본")
        self._tab_translated = self._tabview.add("🇰🇷 번역")
        self._tab_original = self._tabview.add("🇺🇸 원문")
        self._tab_log = self._tabview.add("📋 로그")
        self._summary_text = self._make_tb(self._tab_summary)
        self._translated_text = self._make_tb(self._tab_translated)
        self._original_text = self._make_tb(self._tab_original)
        self._log_text = self._make_tb(self._tab_log)
        self._set_text(self._summary_text,
                       "🎙️ 유튜브 URL 또는 로컬 파일을 선택하고\n"
                       "'GuruNote 생성하기' 를 눌러주세요.\n\n"
                       "화자 분리된 한국어 요약본이 이 자리에 표시됩니다.")

    @staticmethod
    def _make_tb(parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        tb = ctk.CTkTextbox(parent, font=ctk.CTkFont(size=13), state="disabled",
                            wrap="word", fg_color=C_BG, text_color=C_TEXT, corner_radius=8)
        tb.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        return tb

    def _update_steps(self, pct):
        th = [0.18, 0.55, 0.78, 0.90, 1.0]
        for i, sl in enumerate(self._step_labels):
            if pct >= th[i]:
                sl.configure(fg_color=C_SUCCESS, text_color=C_BG)
            elif i > 0 and pct >= th[i - 1]:
                sl.configure(fg_color=C_PRIMARY, text_color="#FFF")
            elif i == 0 and pct > 0:
                sl.configure(fg_color=C_PRIMARY, text_color="#FFF")
            else:
                sl.configure(fg_color=C_SURFACE_HI, text_color=C_TEXT_DIM)

    # ── 이벤트 핸들러 ────────────────────────────────────────
    def _on_settings(self):
        SettingsDialog(self)

    def _on_update_sb(self):
        try:
            logs = []
            st = check_updates(logs.append)
            if not messagebox.askyesno("업데이트", f"{st}\n\n실행할까요?"):
                return
            update_project(logs.append, upgrade_deps=True)
            messagebox.showinfo("완료", "업데이트 완료. 앱을 재시작하세요.")
        except Exception as e:
            messagebox.showerror("실패", str(e))

    def _on_pick_file(self):
        exts = sorted(SUPPORTED_EXTS)
        path = filedialog.askopenfilename(title="파일 선택",
                                          filetypes=[("미디어", " ".join(f"*{e}" for e in exts)), ("All", "*.*")])
        if not path:
            return
        self._local_file_path = path
        self._url_entry.delete(0, "end")
        self._url_entry.insert(0, f"📁 {Path(path).name}")

    def _check_api_keys(self):
        prov = self._llm_var.get()
        if prov == "openai_compatible":
            if os.environ.get("OPENAI_BASE_URL"):
                return True
            msg = "OPENAI_BASE_URL 이 설정되지 않았습니다.\n설정에서 입력하시겠습니까?"
        else:
            k = "ANTHROPIC_API_KEY" if prov == "anthropic" else "OPENAI_API_KEY"
            if os.environ.get(k):
                return True
            msg = f"{k} 가 설정되지 않았습니다.\n설정에서 입력하시겠습니까?"
        if messagebox.askyesno("설정 필요", msg):
            SettingsDialog(self)
        return False

    def _check_vibevoice_available(self) -> bool:
        """
        VibeVoice 가 필요한 엔진(vibevoice/auto) 선택 시, 패키지 미설치면
        사용자에게 설치 / AssemblyAI 전환 / 취소 중 선택하게 한다.
        Returns True 면 진행 가능, False 면 중단.
        """
        engine = self._stt_var.get()
        if engine == "assemblyai":
            return True  # VibeVoice 필요 없음
        if is_vibevoice_installed():
            return True

        # VibeVoice 미설치 — 3가지 선택지 제공
        choice = messagebox.askyesnocancel(
            "VibeVoice-ASR 미설치",
            "VibeVoice-ASR 패키지가 설치되어 있지 않습니다.\n\n"
            "  [예]    → VibeVoice 를 지금 설치 (git+https, 수 분 소요)\n"
            "  [아니오] → AssemblyAI 클라우드 API 로 전환해서 진행\n"
            "  [취소]  → 작업 취소",
        )
        if choice is None:
            # 취소
            return False
        if choice:
            # 예 → 설치 시도
            self._append_log("📦 VibeVoice-ASR 설치를 시작합니다…")
            ok = install_vibevoice(progress=self._append_log)
            if ok:
                return True
            # 설치 실패 — AssemblyAI 로 전환 제안
            fallback = messagebox.askyesno(
                "설치 실패",
                "VibeVoice 설치에 실패했습니다.\n"
                "AssemblyAI 로 전환해서 진행할까요?",
            )
            if fallback:
                self._stt_var.set("assemblyai")
                self._append_log("🔄 STT 엔진을 AssemblyAI 로 전환했습니다.")
                return True
            return False
        else:
            # 아니오 → AssemblyAI 전환
            self._stt_var.set("assemblyai")
            self._append_log("🔄 STT 엔진을 AssemblyAI 로 전환했습니다.")
            return True

    def _on_run(self):
        txt = self._url_entry.get().strip()
        has_local = bool(self._local_file_path and is_supported_local_file(self._local_file_path))
        use_local = has_local and txt.startswith("📁")
        if not use_local and not is_probably_youtube_url(txt):
            messagebox.showwarning("소스 필요", "유튜브 URL 또는 📁 로컬 파일을 선택해주세요.")
            return
        if not self._check_api_keys():
            return
        if not self._check_vibevoice_available():
            return
        self._run_btn.configure(state="disabled", text="처리 중…")
        self._stop_btn.configure(state="normal")
        self._save_btn.configure(state="disabled")
        self._clear_log()
        self._clear_results()
        self._title_label.configure(text="파이프라인 실행 중…")
        self._set_progress(0.01)
        for sl in self._step_labels:
            sl.configure(fg_color=C_SURFACE_HI, text_color=C_TEXT_DIM)
        kw = dict(engine=self._stt_var.get(), provider=self._llm_var.get())
        if use_local:
            kw["local_file"] = self._local_file_path
        else:
            kw["youtube_url"] = txt
        self._worker = PipelineWorker(**kw)
        self._worker.start()
        self._poll_worker()

    def _poll_worker(self):
        if not self._worker:
            return
        while True:
            try:
                msg = self._worker.msg_queue.get_nowait()
                self._append_log(msg)
                self._last_log_label.configure(text=msg)
            except queue.Empty:
                break
        while True:
            try:
                self._set_progress(self._worker.progress_queue.get_nowait())
            except queue.Empty:
                break
        try:
            self._on_pipeline_done(self._worker.result_queue.get_nowait())
            return
        except queue.Empty:
            pass
        self.after(100, self._poll_worker)

    def _on_pipeline_done(self, result):
        self._run_btn.configure(state="normal", text="▶  GuruNote 생성하기")
        self._stop_btn.configure(state="disabled")
        if not result.get("ok"):
            self._title_label.configure(text="❌ 오류 발생")
            messagebox.showerror("오류", result.get("error", "알 수 없는 오류"))
            return
        self._result = result
        audio = result["audio"]
        transcript = result["transcript"]
        self._title_label.configure(text=f"🎉 {audio.video_title}")
        self._save_btn.configure(state="normal")
        self._set_text(self._summary_text, result["summary_md"])
        self._set_text(self._translated_text, result["translated"])
        lines = [f"[{_format_ts(s.start)}] Speaker {s.speaker}: {s.text}" for s in transcript.segments]
        self._set_text(self._original_text, "\n\n".join(lines))
        self._tabview.set("📌 요약본")
        self._set_progress(1.0)
        self._last_log_label.configure(text="🎉 GuruNote 생성 완료!")

    def _on_stop(self):
        if self._worker:
            self._worker.request_stop()
            self._stop_btn.configure(state="disabled")
            self._append_log("⏹ 중지 요청됨")

    def _on_save(self):
        if not self._result:
            return
        name = f"GuruNote_{sanitize_filename(self._result['audio'].video_title)}.md"
        path = filedialog.asksaveasfilename(title="저장", defaultextension=".md",
                                            filetypes=[("Markdown", "*.md"), ("All", "*.*")], initialfile=name)
        if not path:
            return
        try:
            Path(path).write_text(self._result["full_md"], encoding="utf-8")
            messagebox.showinfo("완료", f"저장됨:\n{path}")
        except Exception as e:
            messagebox.showerror("실패", str(e))

    # ── 유틸 ─────────────────────────────────────────────────
    def _append_log(self, msg):
        self._log_text.configure(state="normal")
        self._log_text.insert("end", msg + "\n")
        self._log_text.see("end")
        self._log_text.configure(state="disabled")

    def _clear_log(self):
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.configure(state="disabled")
        self._last_log_label.configure(text="")

    def _set_progress(self, pct):
        pct = max(0.0, min(1.0, pct))
        self._progress.set(pct)
        self._progress_label.configure(text=f"{int(pct * 100)}%")
        self._update_steps(pct)

    @staticmethod
    def _set_text(tb, content):
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.insert("1.0", content)
        tb.configure(state="disabled")

    def _clear_results(self):
        for tb in (self._summary_text, self._translated_text, self._original_text):
            self._set_text(tb, "")

    def _on_closing(self):
        self.destroy()


# =============================================================================
# 엔트리포인트
# =============================================================================
def main() -> None:
    app = GuruNoteApp()
    app.protocol("WM_DELETE_WINDOW", app._on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
