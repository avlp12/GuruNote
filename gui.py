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
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk
from dotenv import load_dotenv

from gurunote.audio import (
    SUPPORTED_EXTS,
    AudioDownloadResult,
    cleanup_dir,
    download_audio,
    extract_audio_from_file,
    is_probably_youtube_url,
    is_supported_local_file,
)
from gurunote.exporter import build_gurunote_markdown, sanitize_filename
from gurunote.llm import LLMConfig, summarize_translation, test_connection, translate_transcript
from gurunote.settings import save_settings
from gurunote.stt import transcribe
from gurunote.types import Transcript, _format_ts
from gurunote.updater import check_updates, update_project
from gurunote.reporting import PipelineReport
from gurunote.history import create_history_entry, list_history

# 환경변수 로드
load_dotenv()

# =============================================================================
# 테마 & 상수
# =============================================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_TITLE = "GuruNote 🎙️"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 780

STT_OPTIONS = ["auto", "vibevoice", "assemblyai"]
LLM_OPTIONS = ["openai", "openai_compatible", "anthropic"]


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
        source_label = self.youtube_url or self.local_file or "unknown"
        report = PipelineReport(title="pending", source=source_label)
        report.step("Init", "started", f"파이프라인 시작 (engine={self.engine}, provider={self.provider})")
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
            report.step("Step 1", "done", f"오디오 준비 완료: {audio.video_title}")
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
            report.step("Step 2", "done", f"전사 완료: segments={len(transcript.segments)}, engine={transcript.engine}")
            self._set_progress(0.55)

            # Step 3
            self._log("🌐 [Step 3] LLM 한국어 번역 중…")
            llm_cfg = LLMConfig.from_env(provider=self.provider)
            translated = translate_transcript(
                transcript, config=llm_cfg, progress=self._log
            )
            self._log(f"✅ [Step 3] 번역 완료 ({len(translated):,} chars)")
            report.step("Step 3", "done", f"번역 완료: {len(translated)} chars")
            self._set_progress(0.78)

            # Step 4
            self._log("📝 [Step 4] GuruNote 요약본 생성 중…")
            summary_md = summarize_translation(
                translated,
                title=audio.video_title,
                config=llm_cfg,
                progress=self._log,
            )
            self._log("✅ [Step 4] 요약 완료")
            report.step("Step 4", "done", "요약 완료")
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
            )
            self._log("🎉 GuruNote 생성 완료!")
            report.step("Step 5", "done", "마크다운 조립 완료")
            report.finalize(True, "전체 파이프라인 성공")
            history_meta = create_history_entry(
                title=audio.video_title,
                source=source_label,
                status="success",
                full_md=full_md,
                report_path=str(report.path),
                stt_engine=transcript.engine,
                llm_provider=self.provider,
            )
            self._set_progress(1.0)

            self.result_queue.put(
                {
                    "ok": True,
                    "audio": audio,
                    "transcript": transcript,
                    "translated": translated,
                    "summary_md": summary_md,
                    "full_md": full_md,
                    "report_path": str(report.path),
                    "history_result_path": history_meta.get("result_path", ""),
                }
            )
        except Exception as exc:
            self.msg_queue.put(f"❌ 오류: {exc}")
            report.step("Pipeline", "error", str(exc))
            report.finalize(False, str(exc))
            create_history_entry(
                title="failed_run",
                source=source_label,
                status="failed",
                report_path=str(report.path),
                llm_provider=self.provider,
                error=str(exc),
            )
            self.msg_queue.put(f"🧾 작업 보고서: {report.path}")
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


class HistoryDialog(ctk.CTkToplevel):
    """저장된 작업 이력을 조회하고 결과물/보고서를 열람하는 다이얼로그."""

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent)
        self.title("🗂️ GuruNote 작업 이력")
        self.geometry("900x560")
        self.transient(parent)
        self.grab_set()

        self._entries: list[dict] = []
        self._build_ui()
        self._reload()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(12, 6))
        ctk.CTkButton(top, text="새로고침", width=90, command=self._reload).pack(side="left")

        self._list = tk.Listbox(self, exportselection=False)
        self._list.grid(row=1, column=0, sticky="nsew", padx=(14, 8), pady=(0, 12))
        self._list.bind("<<ListboxSelect>>", lambda _e: self._show_selected())

        right = ctk.CTkFrame(self)
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 14), pady=(0, 12))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        self._meta_label = ctk.CTkLabel(right, text="이력을 선택하세요.", justify="left", anchor="w")
        self._meta_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        self._preview = ctk.CTkTextbox(right, wrap="word")
        self._preview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))

        btns = ctk.CTkFrame(right, fg_color="transparent")
        btns.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self._open_result_btn = ctk.CTkButton(btns, text="결과물 열기", width=100, command=self._open_result)
        self._open_result_btn.pack(side="left")
        self._open_report_btn = ctk.CTkButton(btns, text="보고서 열기", width=100, command=self._open_report)
        self._open_report_btn.pack(side="left", padx=(8, 0))

    def _reload(self) -> None:
        self._entries = list_history(limit=200)
        self._list.delete(0, "end")
        for item in self._entries:
            status = "✅" if item.get("status") == "success" else "❌"
            self._list.insert("end", f"{status} {item.get('created_at', '')} · {item.get('title', 'untitled')}")
        if self._entries:
            self._list.selection_set(0)
            self._show_selected()

    def _selected(self) -> dict | None:
        sel = self._list.curselection()
        if not sel:
            return None
        return self._entries[sel[0]]

    def _show_selected(self) -> None:
        item = self._selected()
        if not item:
            return
        self._meta_label.configure(
            text=(
                f"상태: {item.get('status', '-')}\n"
                f"제목: {item.get('title', '-')}\n"
                f"시각(UTC): {item.get('created_at', '-')}\n"
                f"소스: {item.get('source', '-')}"
            )
        )
        preview = ""
        result_path = item.get("result_path", "")
        if result_path and Path(result_path).exists():
            preview = Path(result_path).read_text(encoding="utf-8")
        elif item.get("error"):
            preview = f"실패 원인:\n{item['error']}"
        self._preview.delete("1.0", "end")
        self._preview.insert("1.0", preview[:20000])

    def _open_result(self) -> None:
        item = self._selected()
        if not item:
            return
        path = item.get("result_path", "")
        if path and Path(path).exists():
            os.startfile(path) if os.name == "nt" else messagebox.showinfo("결과물 경로", path)
        else:
            messagebox.showwarning("결과물 없음", "이 작업은 결과 마크다운이 없습니다.")

    def _open_report(self) -> None:
        item = self._selected()
        if not item:
            return
        path = item.get("report_path", "")
        if path and Path(path).exists():
            os.startfile(path) if os.name == "nt" else messagebox.showinfo("보고서 경로", path)
        else:
            messagebox.showwarning("보고서 없음", "보고서를 찾을 수 없습니다.")


# =============================================================================
# 메인 애플리케이션
# =============================================================================
class GuruNoteApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(900, 650)

        self._worker: Optional[PipelineWorker] = None
        self._result: Optional[dict] = None

        self._build_ui()

    # -------------------------------------------------------------------------
    # UI 구성
    # -------------------------------------------------------------------------
    def _build_ui(self) -> None:
        # Grid 설정 — row 2 (결과 영역) 가 남는 공간을 전부 차지
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()        # row 0
        self._build_controls()      # row 1
        self._build_result_area()   # row 2

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(18, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="GuruNote 🎙️: 글로벌 IT/AI 구루들의 인사이트",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        # ⚙️ 설정 버튼 (헤더 우측)
        ctk.CTkButton(
            header,
            text="⚙️ 설정",
            width=80,
            height=32,
            fg_color="gray30",
            hover_color="gray40",
            command=self._on_settings,
        ).grid(row=0, column=1, sticky="e")
        ctk.CTkButton(
            header,
            text="🗂️ 이력",
            width=80,
            height=32,
            fg_color="gray30",
            hover_color="gray40",
            command=self._on_history,
        ).grid(row=0, column=2, padx=(8, 0), sticky="e")

        ctk.CTkLabel(
            header,
            text="유튜브 링크 하나로 해외 IT/AI 팟캐스트를 화자 분리된 한국어 요약본으로",
            font=ctk.CTkFont(size=13),
            text_color="gray60",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))

    def _build_controls(self) -> None:
        ctl = ctk.CTkFrame(self)
        ctl.grid(row=1, column=0, padx=20, pady=12, sticky="ew")

        # 내부 그리드: 입력 필드가 가변 폭
        ctl.grid_columnconfigure(2, weight=1)

        # 소스 라벨
        ctk.CTkLabel(ctl, text="소스", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=(14, 6), pady=12, sticky="w"
        )

        # 📁 파일 선택 버튼
        self._file_btn = ctk.CTkButton(
            ctl,
            text="📁",
            width=38,
            height=38,
            command=self._on_pick_file,
        )
        self._file_btn.grid(row=0, column=1, padx=(0, 4), pady=12)

        # URL / 파일경로 입력
        self._local_file_path: str = ""  # 로컬 파일이 선택되면 여기 저장
        self._url_entry = ctk.CTkEntry(
            ctl,
            placeholder_text="유튜브 URL 또는 📁 버튼으로 로컬 파일 선택",
            height=38,
        )
        self._url_entry.grid(row=0, column=2, padx=4, pady=12, sticky="ew")

        # STT 엔진
        ctk.CTkLabel(ctl, text="STT").grid(row=0, column=3, padx=(12, 4), pady=12)
        self._stt_var = ctk.StringVar(value="auto")
        ctk.CTkOptionMenu(
            ctl, variable=self._stt_var, values=STT_OPTIONS, width=120
        ).grid(row=0, column=4, padx=4, pady=12)

        # LLM
        ctk.CTkLabel(ctl, text="LLM").grid(row=0, column=5, padx=(12, 4), pady=12)
        self._llm_var = ctk.StringVar(
            value=os.environ.get("LLM_PROVIDER", "openai")
        )
        ctk.CTkOptionMenu(
            ctl, variable=self._llm_var, values=LLM_OPTIONS, width=120
        ).grid(row=0, column=6, padx=4, pady=12)

        # 실행 버튼
        self._run_btn = ctk.CTkButton(
            ctl,
            text="GuruNote 생성하기",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            width=170,
            command=self._on_run,
        )
        self._run_btn.grid(row=0, column=7, padx=(12, 14), pady=12)

        self._stop_btn = ctk.CTkButton(
            ctl,
            text="⏹ 중지",
            height=38,
            width=90,
            state="disabled",
            fg_color="gray35",
            hover_color="gray45",
            command=self._on_stop,
        )
        self._stop_btn.grid(row=0, column=8, padx=(0, 14), pady=12)

    def _build_result_area(self) -> None:
        """결과 영역: 왼쪽 = 진행 로그, 오른쪽 = 결과 탭."""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="nsew")
        container.grid_columnconfigure(0, weight=2)  # 로그
        container.grid_columnconfigure(1, weight=5)  # 결과 탭
        container.grid_rowconfigure(0, weight=1)

        # ---- 진행 로그 (왼쪽) ----
        log_frame = ctk.CTkFrame(container)
        log_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        log_frame.grid_rowconfigure(2, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_frame,
            text="📋 진행 로그",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        prog_wrap = ctk.CTkFrame(log_frame, fg_color="transparent")
        prog_wrap.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="ew")
        prog_wrap.grid_columnconfigure(0, weight=1)
        self._progress = ctk.CTkProgressBar(prog_wrap)
        self._progress.grid(row=0, column=0, sticky="ew")
        self._progress.set(0)
        self._progress_label = ctk.CTkLabel(
            prog_wrap, text="진행률 0%", font=ctk.CTkFont(size=11), text_color="gray60"
        )
        self._progress_label.grid(row=1, column=0, sticky="w", pady=(3, 0))

        self._log_text = ctk.CTkTextbox(
            log_frame, font=ctk.CTkFont(size=12), state="disabled", wrap="word"
        )
        self._log_text.grid(row=2, column=0, padx=8, pady=(0, 8), sticky="nsew")

        # ---- 결과 탭 (오른쪽) ----
        tab_frame = ctk.CTkFrame(container)
        tab_frame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        tab_frame.grid_rowconfigure(1, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)

        # 상단: 다운로드 버튼
        top_bar = ctk.CTkFrame(tab_frame, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        self._title_label = ctk.CTkLabel(
            top_bar,
            text="결과가 여기에 표시됩니다",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._title_label.grid(row=0, column=0, sticky="w")

        self._save_btn = ctk.CTkButton(
            top_bar,
            text="📥 마크다운 저장",
            width=140,
            state="disabled",
            command=self._on_save,
        )
        self._save_btn.grid(row=0, column=1, sticky="e")

        # TabView
        self._tabview = ctk.CTkTabview(tab_frame, height=400)
        self._tabview.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="nsew")

        self._tab_summary = self._tabview.add("📌 요약본")
        self._tab_translated = self._tabview.add("🇰🇷 번역")
        self._tab_original = self._tabview.add("🇺🇸 원문")

        # 각 탭에 텍스트 위젯 배치
        self._summary_text = self._make_tab_textbox(self._tab_summary)
        self._translated_text = self._make_tab_textbox(self._tab_translated)
        self._original_text = self._make_tab_textbox(self._tab_original)

        # 안내 메시지
        self._set_text(
            self._summary_text,
            "유튜브 URL 을 입력하고 'GuruNote 생성하기' 를 눌러주세요.",
        )

    @staticmethod
    def _make_tab_textbox(parent: ctk.CTkFrame) -> ctk.CTkTextbox:
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        tb = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family="Menlo, Consolas, monospace", size=13),
            state="disabled",
            wrap="word",
        )
        tb.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        return tb

    # -------------------------------------------------------------------------
    # 이벤트 핸들러
    # -------------------------------------------------------------------------
    def _on_settings(self) -> None:
        SettingsDialog(self)

    def _on_history(self) -> None:
        HistoryDialog(self)

    def _on_pick_file(self) -> None:
        """네이티브 파일 대화상자로 로컬 동영상/오디오 파일을 선택한다."""
        ext_list = sorted(SUPPORTED_EXTS)
        filetypes = [
            ("미디어 파일", " ".join(f"*{e}" for e in ext_list)),
            ("All Files", "*.*"),
        ]
        path = filedialog.askopenfilename(
            title="오디오/동영상 파일 선택",
            filetypes=filetypes,
        )
        if not path:
            return

        self._local_file_path = path
        # 엔트리에 파일명 표시 (전체 경로 대신 이름만)
        self._url_entry.delete(0, "end")
        self._url_entry.insert(0, f"📁 {Path(path).name}")

    def _check_api_keys(self) -> bool:
        """LLM API 키가 설정돼 있는지 확인. 없으면 설정 다이얼로그 안내."""
        provider = self._llm_var.get()
        key_name = (
            "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        )
        if os.environ.get(key_name):
            return True

        open_settings = messagebox.askyesno(
            "API 키 미설정",
            f"{key_name} 가 설정되어 있지 않습니다.\n"
            "설정 화면을 열어 API 키를 입력하시겠습니까?",
        )
        if open_settings:
            SettingsDialog(self)
        return False

    def _on_run(self) -> None:
        entry_text = self._url_entry.get().strip()
        has_local = bool(self._local_file_path and is_supported_local_file(self._local_file_path))
        has_url = is_probably_youtube_url(entry_text)

        # 로컬 파일이 선택돼 있고 엔트리에 📁 마커가 남아있으면 → 로컬 모드
        use_local = has_local and entry_text.startswith("📁")

        if not use_local and not has_url:
            messagebox.showwarning(
                "소스를 입력해주세요",
                "유튜브 URL 을 입력하거나, 📁 버튼으로 로컬 파일을 선택해주세요.",
            )
            return

        if not self._check_api_keys():
            return

        # UI 잠금
        self._run_btn.configure(state="disabled", text="처리 중…")
        self._stop_btn.configure(state="normal")
        self._save_btn.configure(state="disabled")
        self._clear_log()
        self._clear_results()
        self._title_label.configure(text="파이프라인 실행 중…")
        self._set_progress(0.01)

        # 워커 시작
        if use_local:
            self._worker = PipelineWorker(
                engine=self._stt_var.get(),
                provider=self._llm_var.get(),
                local_file=self._local_file_path,
            )
        else:
            self._worker = PipelineWorker(
                engine=self._stt_var.get(),
                provider=self._llm_var.get(),
                youtube_url=entry_text,
            )
        self._worker.start()
        self._poll_worker()

    def _poll_worker(self) -> None:
        """100ms 간격으로 워커의 메시지/결과 큐를 확인해 UI에 반영."""
        if self._worker is None:
            return

        # 진행 메시지 소비
        while True:
            try:
                msg = self._worker.msg_queue.get_nowait()
                self._append_log(msg)
            except queue.Empty:
                break

        while True:
            try:
                pct = self._worker.progress_queue.get_nowait()
                self._set_progress(pct)
            except queue.Empty:
                break

        # 결과 확인
        try:
            result = self._worker.result_queue.get_nowait()
            self._on_pipeline_done(result)
            return
        except queue.Empty:
            pass

        # 아직 실행 중 → 100ms 후 다시 확인
        self.after(100, self._poll_worker)

    def _on_pipeline_done(self, result: dict) -> None:
        self._run_btn.configure(state="normal", text="GuruNote 생성하기")
        self._stop_btn.configure(state="disabled")

        if not result.get("ok"):
            self._title_label.configure(text="❌ 오류 발생")
            messagebox.showerror("파이프라인 오류", result.get("error", "알 수 없는 오류"))
            return

        self._result = result
        audio: AudioDownloadResult = result["audio"]
        transcript: Transcript = result["transcript"]

        self._title_label.configure(text=f"🎉 {audio.video_title}")
        self._save_btn.configure(state="normal")
        if result.get("report_path"):
            self._append_log(f"🧾 작업 보고서 저장: {result['report_path']}")

        # 탭 채우기
        self._set_text(self._summary_text, result["summary_md"])
        self._set_text(self._translated_text, result["translated"])

        # 영어 원문
        original_lines = []
        for seg in transcript.segments:
            ts = _format_ts(seg.start)
            original_lines.append(f"[{ts}] Speaker {seg.speaker}: {seg.text}")
        self._set_text(self._original_text, "\n\n".join(original_lines))

        # 요약 탭으로 포커스
        self._tabview.set("📌 요약본")
        self._set_progress(1.0)

    def _on_stop(self) -> None:
        if self._worker is None:
            return
        self._worker.request_stop()
        self._stop_btn.configure(state="disabled")
        self._append_log("⏹ 사용자가 작업 중지를 요청했습니다. 안전한 지점에서 중단합니다…")

    def _on_save(self) -> None:
        if not self._result:
            return
        audio: AudioDownloadResult = self._result["audio"]
        default_name = f"GuruNote_{sanitize_filename(audio.video_title)}.md"

        path = filedialog.asksaveasfilename(
            title="GuruNote 마크다운 저장",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All Files", "*.*")],
            initialfile=default_name,
        )
        if not path:
            return

        try:
            Path(path).write_text(self._result["full_md"], encoding="utf-8")
            messagebox.showinfo("저장 완료", f"파일이 저장되었습니다:\n{path}")
        except Exception as exc:
            messagebox.showerror("저장 실패", str(exc))

    # -------------------------------------------------------------------------
    # 유틸
    # -------------------------------------------------------------------------
    def _append_log(self, msg: str) -> None:
        self._log_text.configure(state="normal")
        self._log_text.insert("end", msg + "\n")
        self._log_text.see("end")
        self._log_text.configure(state="disabled")

    def _clear_log(self) -> None:
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.configure(state="disabled")

    def _set_progress(self, pct: float) -> None:
        self._progress.set(max(0.0, min(1.0, pct)))
        self._progress_label.configure(text=f"진행률 {int(pct * 100)}%")

    @staticmethod
    def _set_text(textbox: ctk.CTkTextbox, content: str) -> None:
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", content)
        textbox.configure(state="disabled")

    def _clear_results(self) -> None:
        for tb in (self._summary_text, self._translated_text, self._original_text):
            self._set_text(tb, "")

    def _on_closing(self) -> None:
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
