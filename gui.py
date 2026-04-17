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
from gurunote.exporter import autosave_result, build_gurunote_markdown, sanitize_filename
from gurunote.llm import (
    LLMConfig, extract_metadata, summarize_translation,
    test_connection, translate_transcript,
)
from gurunote.settings import save_settings
from gurunote.history import (
    JobLogger, delete_job, get_job_log, get_job_markdown,
    load_index, new_job_id, save_job,
)
from gurunote.hardware import (
    AUTO_KEY, CUSTOM_KEY, PRESETS,
    detect_description, detect_recommended_preset,
    dropdown_options as hw_dropdown_options,
    key_to_label as hw_key_to_label,
    label_to_key as hw_label_to_key,
)
from gurunote.stt import install_whisperx, is_whisperx_installed, transcribe
from gurunote.stt_mlx import is_apple_silicon
from gurunote.types import _format_ts
from gurunote.updater import check_for_update, update_project

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

STT_OPTIONS = ["auto", "whisperx", "mlx", "assemblyai"]
LLM_OPTIONS = ["openai", "openai_compatible", "anthropic", "gemini"]

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
        self.job_id = new_job_id()
        self._job_logger = JobLogger(self.job_id)
        self._start_time: Optional[float] = None
        self.msg_queue: queue.Queue[str] = queue.Queue()
        self.progress_queue: queue.Queue[float] = queue.Queue()
        self.result_queue: queue.Queue[dict] = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _log(self, msg: str) -> None:
        if self._stop_event.is_set():
            raise RuntimeError("사용자가 작업 중지를 요청했습니다.")
        import time as _time
        ts = _time.strftime("%H:%M:%S")
        stamped = f"[{ts}] {msg}"
        self.msg_queue.put(stamped)
        self._job_logger.write(msg)

    def _set_progress(self, pct: float) -> None:
        self.progress_queue.put(max(0.0, min(1.0, pct)))

    def request_stop(self) -> None:
        self._stop_event.set()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        import time as _time
        self._start_time = _time.monotonic()
        tmp_dir = tempfile.mkdtemp(prefix="gurunote_")
        try:
            self._set_progress(0.02)
            # Step 1
            if self.youtube_url:
                self._log("[Step 1] 유튜브 오디오 추출 중...")
                audio = download_audio(self.youtube_url, tmp_dir)
            else:
                self._log("[Step 1] 로컬 파일에서 오디오 추출 중...")
                audio = extract_audio_from_file(self.local_file, tmp_dir)
            audio_size = os.path.getsize(audio.audio_path) / (1024 * 1024)
            self._log(
                f"[Step 1] OK: {audio.video_title} ({audio_size:.1f} MB, "
                f"{int(audio.duration_sec)}s)"
            )
            if audio.upload_date:
                self._log(f"  > 게시일: {audio.upload_date}")
            if audio.chapters:
                self._log(f"  > 공식 챕터 {len(audio.chapters)}개 감지")
            if audio.subtitles_text:
                self._log(
                    f"  > 기존 자막 감지 ({len(audio.subtitles_text):,} chars)"
                )
            video_ctx = audio.to_context_dict()
            self._set_progress(0.18)
            effective_engine = self.engine

            # Step 2 — 서브스텝 진행률 매핑
            # stt 모듈이 _log() 를 호출할 때 메시지 내용으로 서브 진행률 추정
            _stt_substeps = {
                "모델 로딩": 0.22,
                "전사 중": 0.30,
                "타임스탬프 정렬": 0.40,
                "화자 분리": 0.48,
                "AssemblyAI": 0.30,
            }
            def _stt_progress(msg: str) -> None:
                self._log(msg)
                for keyword, pct in _stt_substeps.items():
                    if keyword in msg:
                        self._set_progress(pct)
                        break

            self._log("[Step 2] 화자 분리 STT 중...")
            transcript = transcribe(
                audio.audio_path,
                engine=effective_engine,
                progress=_stt_progress,
                stop_event=self._stop_event,
            )
            self._log(
                f"[Step 2] OK: {len(transcript.segments)} 세그먼트, "
                f"{len(transcript.speakers)} 화자, 엔진={transcript.engine}"
            )
            self._set_progress(0.55)

            # Step 3
            self._log("[Step 3] LLM 한국어 번역 중...")
            llm_cfg = LLMConfig.from_env(provider=self.provider)
            translated = translate_transcript(
                transcript, config=llm_cfg, progress=self._log,
                video_context=video_ctx,
            )
            self._log(f"[Step 3] OK: 번역 완료 ({len(translated):,} chars)")
            self._set_progress(0.78)

            # Step 4
            self._log("[Step 4] GuruNote 요약본 생성 중...")
            summary_md = summarize_translation(
                translated,
                title=audio.video_title,
                config=llm_cfg,
                progress=self._log,
                video_context=video_ctx,
            )
            self._log("[Step 4] OK: 요약 완료")
            self._set_progress(0.88)

            # Step 4.5 — 메타데이터 자동 추출 (제목/분야/태그)
            self._log("[Step 4.5] 분류 메타데이터(제목/분야/태그) 추출 중...")
            video_meta = {
                "title": audio.video_title,
                "uploader": audio.uploader,
                "tags": getattr(audio, "tags", None) or [],
            }
            metadata = extract_metadata(
                translated, video_meta=video_meta,
                config=llm_cfg, log=self._log,
            )
            if metadata:
                self._log(
                    f"[Step 4.5] OK: 분야='{metadata.get('field', '')}', "
                    f"태그={metadata.get('tags', [])}"
                )
            self._set_progress(0.92)

            # Step 5
            self._log("[Step 5] 마크다운 조립 중...")
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
                organized_title=metadata.get("organized_title", ""),
                field=metadata.get("field", ""),
                tags=metadata.get("tags", []),
            )
            self._log("[Done] GuruNote 생성 완료")
            self._set_progress(1.0)

            # 히스토리에 자동 저장 (분류 메타 포함)
            save_job(
                self.job_id,
                title=audio.video_title,
                source_url=audio.webpage_url,
                stt_engine=transcript.engine,
                llm_provider=self.provider,
                status="completed",
                duration_sec=audio.duration_sec,
                num_speakers=len(transcript.speakers),
                full_md=full_md,
                organized_title=metadata.get("organized_title", ""),
                field=metadata.get("field", ""),
                tags=metadata.get("tags", []),
                uploader=audio.uploader or "",
                upload_date=audio.upload_date or "",
            )
            self._log("[Save] 히스토리에 저장됨")

            # autosave
            try:
                saved = autosave_result(full_md, audio.video_title)
                self._log(f"[Autosave] {saved}")
            except Exception:  # noqa: BLE001
                pass

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
            self.msg_queue.put(f"[Error] {exc}")
            # 실패도 히스토리에 기록 (로그 파일은 이미 저장됨)
            save_job(
                self.job_id,
                title=self.youtube_url or self.local_file or "unknown",
                source_url=self.youtube_url or self.local_file,
                stt_engine=self.engine,
                llm_provider=self.provider,
                status="failed",
                error_message=str(exc),
            )
            self.result_queue.put({"ok": False, "error": str(exc)})
        finally:
            self._job_logger.close()
            cleanup_dir(tmp_dir)


# =============================================================================
# 설정 다이얼로그 (API 키 관리)
# =============================================================================
# LLM Provider 드롭다운 선택지
_LLM_PROVIDERS = ["openai", "anthropic", "gemini", "openai_compatible"]

# 설정 필드 정의: (환경변수명, 라벨, 마스킹 여부)
# `LLM_PROVIDER` 는 CTkOptionMenu 로 렌더링되고, 나머지는 CTkEntry.
# 하드웨어 프리셋이 아래 필드들의 값을 일괄 채운다:
#   WHISPERX_MODEL, WHISPERX_BATCH_SIZE, MLX_WHISPER_MODEL,
#   LLM_TEMPERATURE, LLM_TRANSLATION_MAX_TOKENS, LLM_SUMMARY_MAX_TOKENS
_SETTINGS_FIELDS = [
    ("LLM_PROVIDER", "LLM Provider", False),
    ("OPENAI_API_KEY", "OpenAI API Key", True),
    ("OPENAI_BASE_URL", "OpenAI Base URL (Local/Compatible)", False),
    ("OPENAI_MODEL", "OpenAI 모델", False),
    ("ANTHROPIC_API_KEY", "Anthropic API Key", True),
    ("ANTHROPIC_MODEL", "Anthropic 모델", False),
    ("GOOGLE_API_KEY", "Google Gemini API Key", True),
    ("GEMINI_MODEL", "Gemini 모델", False),
    ("LLM_TEMPERATURE", "LLM Temperature", False),
    ("LLM_TRANSLATION_MAX_TOKENS", "번역 Max Tokens", False),
    ("LLM_SUMMARY_MAX_TOKENS", "요약 Max Tokens", False),
    ("ASSEMBLYAI_API_KEY", "AssemblyAI API Key (폴백용)", True),
    ("WHISPERX_MODEL", "WhisperX 모델 (NVIDIA)", False),
    ("WHISPERX_BATCH_SIZE", "WhisperX 배치 사이즈 (NVIDIA)", False),
    ("MLX_WHISPER_MODEL", "MLX Whisper 모델 (Apple Silicon)", False),
    ("HUGGINGFACE_TOKEN", "HuggingFace 토큰 (화자 분리용)", True),
]


class HistoryDialog(ctk.CTkToplevel):
    """완료/실패 작업 목록 + 마크다운 다운로드 + 로그 확인."""

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent)
        self.title("GuruNote History")
        self.geometry("700x520")
        self.transient(parent)
        self.grab_set()
        self._parent = parent
        self._build_ui()
        self.after(100, self.focus_force)

    def _build_ui(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(16, 8))
        ctk.CTkLabel(top, text="작업 히스토리",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(top, text="Refresh", width=100, height=28,
                      command=self._refresh).pack(side="right")

        self._scroll = ctk.CTkScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._scroll.grid_columnconfigure(0, weight=1)
        self._refresh()

    def _refresh(self) -> None:
        for w in self._scroll.winfo_children():
            w.destroy()
        jobs = load_index()
        if not jobs:
            ctk.CTkLabel(self._scroll, text="아직 작업 기록이 없습니다.",
                         text_color="gray55").grid(row=0, column=0, pady=40)
            return
        for i, job in enumerate(jobs):
            self._render_job_row(i, job)

    def _render_job_row(self, row: int, job: dict) -> None:
        status = job.get("status", "unknown")
        icon = "✅" if status == "completed" else "❌"
        title = job.get("title", "제목 없음")
        created = (job.get("created_at") or "")[:16].replace("T", " ")
        engine = job.get("stt_engine", "")
        job_id = job.get("job_id", "")

        frame = ctk.CTkFrame(self._scroll, fg_color=C_SURFACE, corner_radius=8)
        frame.grid(row=row, column=0, sticky="ew", pady=3)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text=icon, font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=(10, 6), pady=8)
        info = f"{title}\n{created}  ·  {engine}"
        if status == "failed":
            err = job.get("error_message", "")
            if err:
                info += f"\n❌ {err[:80]}"
        ctk.CTkLabel(frame, text=info, font=ctk.CTkFont(size=12),
                     anchor="w", justify="left").grid(
            row=0, column=1, sticky="w", padx=4, pady=8)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=(4, 10), pady=8)

        if job.get("has_markdown"):
            ctk.CTkButton(btn_frame, text="Save", width=42, height=28,
                          command=lambda jid=job_id, t=title: self._save_md(jid, t)
                          ).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Log", width=38, height=28,
                      fg_color="gray35",
                      command=lambda jid=job_id: self._show_log(jid)
                      ).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Del", width=38, height=28,
                      fg_color="gray35", hover_color=C_DANGER,
                      command=lambda jid=job_id: self._delete(jid)
                      ).pack(side="left", padx=2)

    def _save_md(self, job_id: str, title: str) -> None:
        md = get_job_markdown(job_id)
        if not md:
            messagebox.showinfo("없음", "마크다운 파일이 없습니다.")
            return
        from gurunote.exporter import sanitize_filename
        path = filedialog.asksaveasfilename(
            title="마크다운 저장", defaultextension=".md",
            filetypes=[("Markdown", "*.md")],
            initialfile=f"GuruNote_{sanitize_filename(title)}.md",
        )
        if path:
            Path(path).write_text(md, encoding="utf-8")
            messagebox.showinfo("완료", f"저장됨:\n{path}")

    def _show_log(self, job_id: str) -> None:
        log = get_job_log(job_id) or "(로그 없음)"
        win = ctk.CTkToplevel(self)
        win.title(f"Log - {job_id}")
        win.geometry("600x400")
        tb = ctk.CTkTextbox(win, font=ctk.CTkFont(size=12), wrap="word")
        tb.pack(fill="both", expand=True, padx=10, pady=10)
        tb.insert("1.0", log)
        tb.configure(state="disabled")

    def _delete(self, job_id: str) -> None:
        if messagebox.askyesno("삭제", "이 작업 기록을 삭제할까요?"):
            delete_job(job_id)
            self._refresh()


class UpdateProgressDialog(ctk.CTkToplevel):
    """업데이트 진행 상황을 실시간 표시하는 다이얼로그."""

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent)
        self.title("GuruNote Update")
        self.geometry("520x340")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._msg_queue: queue.Queue[str] = queue.Queue()
        self._done_queue: queue.Queue[dict] = queue.Queue()

        ctk.CTkLabel(
            self, text="업데이트 진행 중...",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(padx=20, pady=(20, 8), anchor="w")

        self._log_text = ctk.CTkTextbox(self, font=ctk.CTkFont(size=12), state="disabled", wrap="word")
        self._log_text.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self._status_label = ctk.CTkLabel(
            self, text="git fetch...", font=ctk.CTkFont(size=11), text_color=C_TEXT_DIM,
        )
        self._status_label.pack(padx=20, pady=(0, 16), anchor="w")

        # 백그라운드 스레드에서 실행
        self._thread = threading.Thread(target=self._run_update, daemon=True)
        self._thread.start()
        self._poll()

    def _log(self, msg: str) -> None:
        self._msg_queue.put(msg)

    def _run_update(self) -> None:
        try:
            update_project(self._log, upgrade_deps=True)
            self._done_queue.put({"ok": True})
        except Exception as exc:  # noqa: BLE001
            self._done_queue.put({"ok": False, "error": str(exc)})

    def _poll(self) -> None:
        while True:
            try:
                msg = self._msg_queue.get_nowait()
                self._log_text.configure(state="normal")
                self._log_text.insert("end", msg + "\n")
                self._log_text.see("end")
                self._log_text.configure(state="disabled")
                # 마지막 줄을 status 에도 표시
                short = msg.strip()[:60]
                self._status_label.configure(text=short)
            except queue.Empty:
                break

        try:
            result = self._done_queue.get_nowait()
            if result.get("ok"):
                self._status_label.configure(text="업데이트 완료!")
                messagebox.showinfo("완료", "업데이트 완료. 앱을 재시작하세요.")
            else:
                self._status_label.configure(text="업데이트 실패")
                messagebox.showerror("실패", result.get("error", "알 수 없는 오류"))
            self.destroy()
            return
        except queue.Empty:
            pass

        self.after(100, self._poll)


class SettingsDialog(ctk.CTkToplevel):
    """API 키와 모델 설정을 입력/저장하는 모달 다이얼로그.

    하드웨어 프리셋 드롭다운을 상단에 두고, 선택 시 STT/LLM 관련 필드를 일괄
    채운다. LLM Provider 는 드롭다운으로 선택하며, 나머지 필드는 여전히 수동
    수정 가능.
    """

    # 하드웨어 프리셋이 자동으로 채워주는 필드 목록
    _PRESET_DRIVEN_FIELDS = (
        "LLM_TEMPERATURE",
        "LLM_TRANSLATION_MAX_TOKENS",
        "LLM_SUMMARY_MAX_TOKENS",
        "WHISPERX_MODEL",
        "WHISPERX_BATCH_SIZE",
        "MLX_WHISPER_MODEL",
    )

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent)
        self.title("⚙️ GuruNote 설정")
        self.geometry("620x640")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # _entries 는 CTkEntry 또는 CTkOptionMenu (둘 다 .get() / .set() 지원) 보관.
        self._entries: dict[str, object] = {}
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

        # --- 하드웨어 프리셋 섹션 ---
        ctk.CTkLabel(
            container,
            text=f"하드웨어 프리셋  ·  {detect_description()}",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 4))

        self._preset_var = ctk.StringVar(value=hw_key_to_label(AUTO_KEY))
        preset_menu = ctk.CTkOptionMenu(
            container,
            variable=self._preset_var,
            values=hw_dropdown_options(),
            width=580,
            command=self._on_preset_change,
        )
        preset_menu.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 4))

        ctk.CTkLabel(
            container,
            text="프리셋을 고르면 STT/LLM 관련 아래 필드가 자동으로 채워집니다. "
                 "'직접 입력' 또는 개별 필드 수정으로 override 가능.",
            font=ctk.CTkFont(size=10),
            text_color="gray55",
        ).grid(row=4, column=0, columnspan=3, sticky="w", pady=(0, 12))

        # --- 일반 필드 (LLM Provider 는 드롭다운, 그 외 Entry) ---
        _placeholders = {
            "OPENAI_MODEL": "gpt-5.4",
            "OPENAI_BASE_URL": "http://127.0.0.1:8000/v1",
            "ANTHROPIC_MODEL": "claude-sonnet-4-6",
            "GEMINI_MODEL": "gemini-2.5-flash",
            "LLM_TEMPERATURE": "0.2",
            "LLM_TRANSLATION_MAX_TOKENS": "8192",
            "LLM_SUMMARY_MAX_TOKENS": "4096",
            "WHISPERX_MODEL": "distil-large-v3",
            "WHISPERX_BATCH_SIZE": "16",
            "MLX_WHISPER_MODEL": "mlx-community/whisper-large-v3-mlx",
        }

        for idx, (env_key, label, is_secret) in enumerate(_SETTINGS_FIELDS, start=5):
            ctk.CTkLabel(
                container, text=label, font=ctk.CTkFont(size=13)
            ).grid(row=idx, column=0, sticky="w", padx=(0, 10), pady=6)

            current_val = os.environ.get(env_key, "")

            if env_key == "LLM_PROVIDER":
                # 드롭다운 특수 처리
                default_provider = current_val if current_val in _LLM_PROVIDERS else "openai"
                provider_var = ctk.StringVar(value=default_provider)
                menu = ctk.CTkOptionMenu(
                    container,
                    variable=provider_var,
                    values=_LLM_PROVIDERS,
                    width=300,
                )
                menu.grid(row=idx, column=1, sticky="ew", pady=6)
                # _entries 에는 StringVar 를 보관하여 .get()/.set() 인터페이스 통일
                self._entries[env_key] = provider_var
                continue

            ph = "미설정" if is_secret else _placeholders.get(env_key, "")
            entry = ctk.CTkEntry(
                container,
                width=300,
                show="•" if is_secret and current_val else "",
                placeholder_text=ph,
            )
            if current_val:
                entry.insert(0, current_val)
            entry.grid(row=idx, column=1, sticky="ew", pady=6)
            self._entries[env_key] = entry
            self._show_vars[env_key] = False

            if is_secret:
                toggle_btn = ctk.CTkButton(
                    container,
                    text="Show",
                    width=36,
                    height=28,
                    command=lambda k=env_key: self._toggle_show(k),
                )
                toggle_btn.grid(row=idx, column=2, padx=(4, 0), pady=6)

        # 다이얼로그 오픈 시 auto-detect 프리셋 적용 (사용자가 아직 .env 에 값이
        # 없는 필드에만 기본값을 채워주기 위해).
        self._apply_preset(AUTO_KEY, only_empty=True)

        # 하단 버튼 바
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(4, 16))

        ctk.CTkButton(
            btn_frame, text="취소", width=80, fg_color="gray40", command=self.destroy
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame,
            text="Save",
            width=120,
            font=ctk.CTkFont(weight="bold"),
            command=self._on_save,
        ).pack(side="right")
        ctk.CTkButton(
            btn_frame,
            text="Test",
            width=120,
            fg_color="gray30",
            hover_color="gray40",
            command=self._on_test_connection,
        ).pack(side="left")
        ctk.CTkButton(
            btn_frame,
            text="Update",
            width=120,
            fg_color="gray30",
            hover_color="gray40",
            command=self._on_update,
        ).pack(side="left", padx=(8, 0))

    def _toggle_show(self, env_key: str) -> None:
        self._show_vars[env_key] = not self._show_vars[env_key]
        entry = self._entries[env_key]
        entry.configure(show="" if self._show_vars[env_key] else "•")

    # -------------------------------------------------------------------------
    # 하드웨어 프리셋
    # -------------------------------------------------------------------------
    def _on_preset_change(self, label: str) -> None:
        """프리셋 드롭다운 선택 시 필드 일괄 갱신."""
        key = hw_label_to_key(label)
        if key == CUSTOM_KEY:
            return  # 사용자가 직접 입력 — 아무것도 안 건드림
        self._apply_preset(key, only_empty=False)

    def _apply_preset(self, key: str, only_empty: bool) -> None:
        """프리셋 값을 `_PRESET_DRIVEN_FIELDS` 에 채워 넣는다.

        Args:
            key: PRESETS 의 키 또는 AUTO_KEY (자동 감지)
            only_empty: True 면 이미 값이 있는 필드는 건드리지 않음 (다이얼로그
                첫 오픈 시 기존 .env 값 보존). False 면 모두 덮어씀 (사용자가
                드롭다운을 명시적으로 바꾼 경우).
        """
        if key == AUTO_KEY:
            key = detect_recommended_preset()
        profile = PRESETS.get(key)
        if profile is None:
            return

        values = {
            "LLM_TEMPERATURE": str(profile.llm_temperature),
            "LLM_TRANSLATION_MAX_TOKENS": str(profile.translation_max_tokens),
            "LLM_SUMMARY_MAX_TOKENS": str(profile.summary_max_tokens),
            "WHISPERX_MODEL": profile.whisperx_model,
            "WHISPERX_BATCH_SIZE": str(profile.whisperx_batch),
            "MLX_WHISPER_MODEL": profile.mlx_model,
        }
        for env_key in self._PRESET_DRIVEN_FIELDS:
            widget = self._entries.get(env_key)
            if widget is None:
                continue
            # CTkEntry 만 덮어씀 (LLM_PROVIDER 는 _PRESET_DRIVEN_FIELDS 에 없음)
            current = widget.get().strip()
            if only_empty and current:
                continue
            widget.delete(0, "end")
            widget.insert(0, values[env_key])

    # -------------------------------------------------------------------------
    # Save / Test / Update
    # -------------------------------------------------------------------------
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
            info = check_for_update()
            ok = messagebox.askyesno(
                "업데이트 확인",
                f"{info['message']}\n\n업데이트를 실행할까요? (git pull + pip upgrade)",
            )
            if not ok:
                return
            logs: list[str] = []
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


def _install_clipboard_shortcuts(root) -> None:
    """macOS 에서 Cmd+C/V/X/A 가 CTkEntry 에 전달되지 않는 문제 해결.

    Tkinter 의 기본 바인딩은 Linux/Windows 의 Ctrl+C/V/X/A 만 `<<Copy>>`,
    `<<Paste>>`, `<<Cut>>`, `<<SelectAll>>` 가상 이벤트로 자동 매핑한다.
    macOS 의 Command 키는 일부 Tcl/Tk 빌드와 한국어 IME 조합에서 누락되는
    경우가 있어, 루트 윈도우에 `bind_all` 로 명시 바인딩을 걸어 모든 자식
    위젯(CTkEntry 의 내부 tk.Entry 포함) 에서 동작하도록 한다.

    Toplevel(SettingsDialog, HistoryDialog 등) 도 같은 Tk 인터프리터를
    공유하므로 `bind_all` 한 번이면 전역적으로 적용됨.
    """
    import platform
    if platform.system() != "Darwin":
        return  # Linux/Windows 는 기본 바인딩이 이미 Ctrl+V 를 매핑

    def _forward(virtual_event: str):
        def handler(event):
            try:
                focused = root.focus_get()
                if focused is not None:
                    focused.event_generate(virtual_event)
            except Exception:  # noqa: BLE001
                pass
            return "break"  # OS 기본 핸들러가 두 번 처리하지 않게 차단
        return handler

    root.bind_all("<Command-c>", _forward("<<Copy>>"))
    root.bind_all("<Command-v>", _forward("<<Paste>>"))
    root.bind_all("<Command-x>", _forward("<<Cut>>"))
    root.bind_all("<Command-a>", _forward("<<SelectAll>>"))
    # 한국어 키보드에서 Command+ㅊ/ㅍ/ㅌ/ㅁ 도 같은 동작 (KeySym 으로 매핑)
    root.bind_all("<Command-C>", _forward("<<Copy>>"))
    root.bind_all("<Command-V>", _forward("<<Paste>>"))
    root.bind_all("<Command-X>", _forward("<<Cut>>"))
    root.bind_all("<Command-A>", _forward("<<SelectAll>>"))


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
        # macOS Cmd+C/V/X/A 명시 바인딩 (Toplevel 포함 전역 적용)
        _install_clipboard_shortcuts(self)
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    # ── 사이드바 ─────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, fg_color=C_SIDEBAR, width=220, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(5, weight=1)
        sb.grid_columnconfigure(0, weight=1)

        # 브랜드 — 세로 배치 (잘림 방지)
        ctk.CTkLabel(
            sb, text="GuruNote",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=C_TEXT,
        ).grid(row=0, column=0, padx=20, pady=(28, 0), sticky="w")
        ctk.CTkLabel(
            sb, text="IT/AI Podcast Summarizer",
            font=ctk.CTkFont(size=10), text_color=C_TEXT_DIM,
        ).grid(row=1, column=0, padx=20, sticky="w", pady=(2, 20))

        # 네비게이션 — 이모지 대신 텍스트 prefix (Windows 호환)
        nav_items = [
            ("  Settings", self._on_settings),
            ("  History", self._on_history),
            ("  Update", self._on_update_sb),
        ]
        for i, (txt, cmd) in enumerate(nav_items):
            ctk.CTkButton(
                sb, text=txt, anchor="w", height=36,
                fg_color="transparent", hover_color=C_SURFACE_HI,
                text_color=C_TEXT_DIM, font=ctk.CTkFont(size=13),
                command=cmd,
            ).grid(row=2 + i, column=0, padx=10, pady=2, sticky="ew")

        ctk.CTkLabel(
            sb, text="v0.6.0.3", font=ctk.CTkFont(size=10), text_color=C_TEXT_DIM,
        ).grid(row=6, column=0, padx=20, pady=(0, 16), sticky="sw")

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
        ctk.CTkButton(c, text="File", width=44, height=40, corner_radius=8,
                      fg_color=C_SURFACE_HI, hover_color=C_BORDER,
                      command=self._on_pick_file).grid(row=1, column=0, padx=(16, 6), pady=(0, 14))
        self._url_entry = ctk.CTkEntry(c, height=40, corner_radius=8,
                                       placeholder_text="유튜브 URL 붙여넣기 또는 File 버튼으로 로컬 파일 선택",
                                       fg_color=C_BG, border_color=C_BORDER, text_color=C_TEXT)
        self._url_entry.grid(row=1, column=1, padx=4, pady=(0, 14), sticky="ew")
        of = ctk.CTkFrame(c, fg_color="transparent")
        of.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 14), sticky="ew")
        of.grid_columnconfigure(4, weight=1)
        ctk.CTkLabel(of, text="STT", text_color=C_TEXT_DIM, font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 6))
        _env_stt = os.environ.get("GURUNOTE_STT_ENGINE", "auto").lower().strip()
        if _env_stt not in STT_OPTIONS:
            _env_stt = "auto"  # vibevoice 등 삭제된 엔진이 남아있으면 auto 폴백
        self._stt_var = ctk.StringVar(value=_env_stt)
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
        self._save_btn = ctk.CTkButton(top, text="Save .md", height=32, width=120, corner_radius=8,
                                       fg_color=C_SURFACE_HI, hover_color=C_PRIMARY, state="disabled", command=self._on_save)
        self._save_btn.grid(row=0, column=1, sticky="e")
        self._tabview = ctk.CTkTabview(c, height=300, corner_radius=8, fg_color=C_SURFACE,
                                       segmented_button_fg_color=C_SURFACE_HI,
                                       segmented_button_selected_color=C_PRIMARY,
                                       segmented_button_unselected_color=C_SURFACE_HI)
        self._tabview.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self._tab_summary = self._tabview.add("Summary")
        self._tab_translated = self._tabview.add("Korean")
        self._tab_original = self._tabview.add("English")
        self._tab_log = self._tabview.add("Log")
        self._summary_text = self._make_tb(self._tab_summary)
        self._translated_text = self._make_tb(self._tab_translated)
        self._original_text = self._make_tb(self._tab_original)
        self._log_text = self._make_tb(self._tab_log)
        self._set_text(self._summary_text,
                       "유튜브 URL 또는 로컬 파일을 선택하고\n"
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

    def _on_history(self):
        HistoryDialog(self)

    def _on_update_sb(self):
        try:
            info = check_for_update()
        except Exception as e:
            messagebox.showerror("업데이트 확인 실패", str(e))
            return

        if not info["update_available"]:
            messagebox.showinfo("업데이트", info["message"])
            return

        if not messagebox.askyesno(
            "업데이트 가능",
            f"{info['message']}\n\n업데이트를 진행하시겠습니까?",
        ):
            return

        UpdateProgressDialog(self)

    def _on_pick_file(self):
        exts = sorted(SUPPORTED_EXTS)
        path = filedialog.askopenfilename(title="파일 선택",
                                          filetypes=[("미디어", " ".join(f"*{e}" for e in exts)), ("All", "*.*")])
        if not path:
            return
        self._local_file_path = path
        self._url_entry.delete(0, "end")
        self._url_entry.insert(0, f"[File] {Path(path).name}")

    def _check_api_keys(self):
        prov = self._llm_var.get()
        if prov == "openai_compatible":
            if os.environ.get("OPENAI_BASE_URL"):
                return True
            msg = "OPENAI_BASE_URL 이 설정되지 않았습니다.\n설정에서 입력하시겠습니까?"
        else:
            if prov == "anthropic":
                k = "ANTHROPIC_API_KEY"
            elif prov == "gemini":
                k = "GOOGLE_API_KEY"
            else:
                k = "OPENAI_API_KEY"
            if os.environ.get(k):
                return True
            msg = f"{k} 가 설정되지 않았습니다.\n설정에서 입력하시겠습니까?"
        if messagebox.askyesno("설정 필요", msg):
            SettingsDialog(self)
        return False

    def _check_whisperx_available(self) -> bool:
        """WhisperX 미설치 시 설치/AssemblyAI 전환/취소 선택.

        engine 이 mlx/assemblyai 면 WhisperX 가 필요 없고, Apple Silicon 에서는
        auto 라우팅이 MLX 또는 AssemblyAI 로 가므로 WhisperX 설치 안내를 생략한다.
        """
        engine = self._stt_var.get()
        if engine in ("assemblyai", "mlx"):
            return True
        if engine == "auto" and is_apple_silicon():
            # auto 는 macOS arm64 에서 MLX → AssemblyAI 순서로 폴백
            return True
        if is_whisperx_installed():
            return True

        choice = messagebox.askyesnocancel(
            "WhisperX 미설치",
            "WhisperX 패키지가 설치되어 있지 않습니다.\n\n"
            "  [예]    → WhisperX 를 지금 설치 (pip, 수 분 소요)\n"
            "  [아니오] → AssemblyAI 클라우드 API 로 전환\n"
            "  [취소]  → 작업 취소",
        )
        if choice is None:
            return False
        if choice:
            self._append_log("[Install] WhisperX 설치 중...")
            ok = install_whisperx(progress=self._append_log)
            if ok:
                return True
            fallback = messagebox.askyesno(
                "설치 실패",
                "WhisperX 설치에 실패했습니다.\nAssemblyAI 로 전환할까요?",
            )
            if fallback:
                self._stt_var.set("assemblyai")
                self._append_log("[Switch] STT -> AssemblyAI")
                return True
            return False
        else:
            self._stt_var.set("assemblyai")
            self._append_log("[Switch] STT -> AssemblyAI")
            return True

    def _on_run(self):
        txt = self._url_entry.get().strip()
        has_local = bool(self._local_file_path and is_supported_local_file(self._local_file_path))
        use_local = has_local and txt.startswith("[File]")
        if not use_local and not is_probably_youtube_url(txt):
            messagebox.showwarning("소스 필요", "유튜브 URL 또는 [File] 로컬 파일을 선택해주세요.")
            return
        if not self._check_api_keys():
            return
        if not self._check_whisperx_available():
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
        # 경과 시간 실시간 갱신 (progress 업데이트 없어도 라벨은 갱신)
        self._refresh_eta_label()
        self.after(100, self._poll_worker)

    def _on_pipeline_done(self, result):
        self._run_btn.configure(state="normal", text="▶  GuruNote 생성하기")
        self._stop_btn.configure(state="disabled")
        if not result.get("ok"):
            self._title_label.configure(text="[Error] 오류 발생")
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
        self._tabview.set("Summary")
        self._set_progress(1.0)
        self._last_log_label.configure(text="[Done] GuruNote 생성 완료")

    def _on_stop(self):
        if self._worker:
            self._worker.request_stop()
            self._stop_btn.configure(state="disabled")
            self._append_log("[Stop] 중지 요청됨")

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
        import time as _time
        pct = max(0.0, min(1.0, pct))
        self._progress.set(pct)
        self._last_progress_pct = pct
        self._last_progress_time = _time.monotonic()
        self._refresh_eta_label()

    def _refresh_eta_label(self):
        """ETA 라벨을 현재 시점 기준으로 갱신. poll 에서도 호출."""
        import time as _time
        pct = getattr(self, "_last_progress_pct", 0.0)
        if not (self._worker and self._worker._start_time and pct > 0.01):
            return

        elapsed = _time.monotonic() - self._worker._start_time
        em, es = divmod(int(elapsed), 60)
        elapsed_str = f"{em}m {es}s"

        # 진행률이 마지막으로 바뀐 후 경과 시간
        since_update = _time.monotonic() - getattr(self, "_last_progress_time", _time.monotonic())

        if pct >= 1.0:
            self._progress_label.configure(text=f"100%  |  {elapsed_str} total")
        elif since_update > 30:
            # 30초 이상 진행 없음 → ETA 예측 불가, 경과 시간만 표시
            self._progress_label.configure(
                text=f"{int(pct * 100)}%  |  {elapsed_str} elapsed  |  처리 중..."
            )
        elif pct > 0.02:
            total_est = elapsed / pct
            remaining = max(0, total_est - elapsed)
            rm, rs = divmod(int(remaining), 60)
            self._progress_label.configure(
                text=f"{int(pct * 100)}%  |  {elapsed_str} elapsed  |  ~{rm}m {rs}s left"
            )
        else:
            self._progress_label.configure(text=f"{int(pct * 100)}%  |  {elapsed_str} elapsed")
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
