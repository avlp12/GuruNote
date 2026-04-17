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
from gurunote.progress_tee import install_tee
from gurunote.settings import save_settings
from gurunote.history import (
    JobLogger, delete_job, get_job_log, get_job_markdown,
    load_index, new_job_id, rebuild_index, save_job,
    update_job_markdown,
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
from gurunote.thumbnails import (
    cached_thumbnail_path, download_thumbnail_async, extract_youtube_id,
)
from gurunote.pdf_export import (
    is_pdf_export_available,
    markdown_to_pdf,
    missing_packages_hint as pdf_missing_hint,
)
from gurunote.obsidian import (
    is_obsidian_vault,
    resolve_subfolder as obsidian_subfolder,
    resolve_vault_path as obsidian_vault,
    save_to_vault as obsidian_save,
)
from gurunote.notion_sync import (
    is_notion_sync_available,
    missing_packages_hint as notion_missing_hint,
    save_to_notion as notion_save,
)
from gurunote.search import (
    clear_cache as search_clear_cache,
    match_body as search_match_body,
)
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
        # 파이프라인 실행 동안 stderr 를 tee 로 감싸 tqdm 진행률 (HF 모델 다운로드,
        # mlx-whisper / whisperx 전사) 을 GUI 로그 패널에 압축해서 전달.
        with install_tee(self._log):
            self._run_pipeline(tmp_dir)

    def _run_pipeline(self, tmp_dir: str) -> None:
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
    # Phase D — Obsidian vault 연동
    ("OBSIDIAN_VAULT_PATH", "Obsidian Vault 경로", False),
    ("OBSIDIAN_SUBFOLDER", "Obsidian 하위 폴더 (기본 GuruNote)", False),
    # Phase E — Notion API 연동
    ("NOTION_TOKEN", "Notion Integration Token", True),
    ("NOTION_PARENT_ID", "Notion Parent ID (database/page UUID)", False),
    ("NOTION_PARENT_TYPE", "Notion Parent Type (database/page)", False),
]


class NoteEditorDialog(ctk.CTkToplevel):
    """
    저장된 결과 마크다운 인라인 편집기 (Step 3.2).

    LLM 요약/번역 결과는 종종 교정이 필요하다 (오타, 화자 이름 오인식, 태그
    수정 등). 별도 에디터 앱을 쓰지 않고 앱 안에서 바로 고쳐 `result.md` 에
    되저장할 수 있게 한다. frontmatter 포함 전체 마크다운을 단일 textbox 로
    노출 — 사용자가 필요한 부분만 수정.

    저장 시 `history.update_job_markdown()` 로 atomic write. 저장 후 콜백
    (`on_saved`) 이 HistoryDialog 의 그리드를 재로드해 스니펫/카드 갱신.
    """

    def __init__(
        self,
        parent: ctk.CTkToplevel,
        job_id: str,
        title: str,
        initial_md: str,
        on_saved=None,
    ) -> None:
        super().__init__(parent)
        self.title(f"편집 — {title[:60]}")
        self.geometry("900x680")
        self.transient(parent)
        self.grab_set()
        self._job_id = job_id
        self._initial_md = initial_md
        self._on_saved = on_saved
        self._build_ui()
        # 닫기(X) 도 dirty 체크 거치도록
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        self.after(100, self.focus_force)

    def _build_ui(self) -> None:
        # 헤더
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 6))
        ctk.CTkLabel(
            header, text="result.md 편집",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT,
        ).pack(side="left")
        ctk.CTkButton(
            header, text="💾 저장", width=96, height=32,
            fg_color=C_PRIMARY, hover_color=C_PRIMARY_HO,
            command=self._on_save_click,
        ).pack(side="right")
        ctk.CTkButton(
            header, text="취소", width=72, height=32,
            fg_color="gray35", hover_color="gray45",
            command=self._on_close_attempt,
        ).pack(side="right", padx=6)

        # 안내
        ctk.CTkLabel(
            self,
            text="YAML frontmatter 포함 전체 마크다운을 직접 수정할 수 있습니다. "
                 "저장 시 ~/.gurunote/jobs/<id>/result.md 가 덮어쓰여집니다.",
            font=ctk.CTkFont(size=11), text_color=C_TEXT_DIM,
            anchor="w", justify="left",
        ).pack(fill="x", padx=16, pady=(0, 8))

        # Textbox
        self._tb = ctk.CTkTextbox(
            self, wrap="word",
            font=ctk.CTkFont(family="Menlo", size=12),
            fg_color=C_BG, text_color=C_TEXT,
            corner_radius=8,
        )
        self._tb.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._tb.insert("1.0", self._initial_md)

        # 키 바인딩: Cmd/Ctrl+S 로 저장
        import platform as _p
        save_key = "<Command-s>" if _p.system() == "Darwin" else "<Control-s>"
        self.bind(save_key, lambda _e: self._on_save_click())

    def _current_md(self) -> str:
        return self._tb.get("1.0", "end-1c")

    def _is_dirty(self) -> bool:
        return self._current_md() != self._initial_md

    def _on_close_attempt(self) -> None:
        if self._is_dirty():
            if not messagebox.askyesno(
                "편집 취소",
                "저장하지 않은 변경 사항이 있습니다. 버리고 닫을까요?",
            ):
                return
        self.destroy()

    def _on_save_click(self) -> None:
        new_md = self._current_md()
        if new_md == self._initial_md:
            messagebox.showinfo("변경 사항 없음", "수정된 내용이 없습니다.")
            return
        try:
            update_job_markdown(self._job_id, new_md)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("저장 실패", str(exc))
            return
        self._initial_md = new_md
        messagebox.showinfo("저장 완료", "노트가 업데이트됐습니다.")
        if self._on_saved is not None:
            try:
                self._on_saved()
            except Exception:  # noqa: BLE001
                pass
        self.destroy()


class HistoryDialog(ctk.CTkToplevel):
    """완료/실패 작업 목록 — 필터바 + 카드 그리드 (Phase B)."""

    # 카드 레이아웃
    _COLUMNS = 3
    _THUMB_W, _THUMB_H = 256, 144  # mqdefault 비율 유지 (16:9)
    _CARD_W = 280

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent)
        self.title("GuruNote History")
        self.geometry("960x660")
        self.transient(parent)
        self.grab_set()
        self._parent = parent

        # 데이터 모델 + 필터 상태
        self._all_jobs: list[dict] = []
        self._filtered_jobs: list[dict] = []
        self._search_var = ctk.StringVar(value="")
        self._field_var = ctk.StringVar(value="모든 분야")
        self._sort_var = ctk.StringVar(value="최신순")
        # Phase F — 본문 전문 검색 토글. 켜면 result.md 본문도 매칭 대상.
        self._search_body_var = ctk.BooleanVar(value=False)

        # PIL 이미지 참조 유지 (GC 방지) + 렌더링 중 썸네일 요청 중복 방지
        self._thumb_refs: dict[str, object] = {}
        self._pending_thumb_ids: set[str] = set()
        # 메인 스레드에서 받아 처리할 썸네일 완성 알림
        self._thumb_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        # 검색 debounce — 다량 히스토리에서 키 입력마다 full re-render 방지
        self._search_after_id: Optional[str] = None

        self._build_ui()
        self.after(100, self.focus_force)
        self.after(120, self._poll_thumb_queue)

    # =========================================================================
    # UI
    # =========================================================================
    def _build_ui(self) -> None:
        # 상단 헤더
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 4))
        ctk.CTkLabel(
            header, text="작업 히스토리",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(
            header, text="Refresh", width=90, height=28,
            command=self._reload_and_refresh,
        ).pack(side="right")
        ctk.CTkButton(
            header, text="Rebuild", width=90, height=28,
            fg_color="gray35", hover_color="gray45",
            command=self._on_rebuild_index,
        ).pack(side="right", padx=(0, 6))
        self._count_label = ctk.CTkLabel(
            header, text="", text_color=C_TEXT_DIM, font=ctk.CTkFont(size=11),
        )
        self._count_label.pack(side="right", padx=(0, 12))

        # 필터 바
        fbar = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=8)
        fbar.pack(fill="x", padx=16, pady=(4, 8))

        ctk.CTkLabel(fbar, text="검색", font=ctk.CTkFont(size=12)).pack(
            side="left", padx=(12, 6), pady=10)
        search_entry = ctk.CTkEntry(
            fbar, textvariable=self._search_var, width=200,
            placeholder_text="제목 / 업로더 / 태그 / (옵션)본문",
        )
        search_entry.pack(side="left", pady=10)
        # 검색 debounce: 200ms 간격으로만 re-render — 빠른 타이핑 중 UI 프리즈 방지
        self._search_var.trace_add("write", lambda *_: self._schedule_refresh())

        # Phase F — 본문 검색 토글 (result.md 본문 lazy load + lru_cache)
        ctk.CTkCheckBox(
            fbar, text="📄 본문 포함", variable=self._search_body_var,
            command=self._refresh_grid,
            font=ctk.CTkFont(size=11),
        ).pack(side="left", padx=(8, 0), pady=10)

        ctk.CTkLabel(fbar, text="분야", font=ctk.CTkFont(size=12)).pack(
            side="left", padx=(16, 6), pady=10)
        self._field_menu = ctk.CTkOptionMenu(
            fbar, variable=self._field_var, values=["모든 분야"],
            width=150, command=lambda _: self._refresh_grid(),
        )
        self._field_menu.pack(side="left", pady=10)

        ctk.CTkLabel(fbar, text="정렬", font=ctk.CTkFont(size=12)).pack(
            side="left", padx=(16, 6), pady=10)
        ctk.CTkOptionMenu(
            fbar, variable=self._sort_var,
            values=["최신순", "오래된순", "길이 긴 순", "길이 짧은 순", "제목 A-Z"],
            width=130, command=lambda _: self._refresh_grid(),
        ).pack(side="left", pady=10)

        ctk.CTkButton(
            fbar, text="필터 초기화", width=90, height=28,
            fg_color="gray35", hover_color="gray45",
            command=self._reset_filters,
        ).pack(side="right", padx=12, pady=10)

        # 그리드 스크롤 영역
        # 컬럼 minsize 로 고정 폭 보장 — 카드는 grid_propagate 로 높이 자동화.
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=C_BG)
        self._scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        for c in range(self._COLUMNS):
            self._scroll.grid_columnconfigure(
                c, weight=1, minsize=self._CARD_W, uniform="card"
            )

        self._reload_and_refresh()

    # =========================================================================
    # Data flow
    # =========================================================================
    def _reload_and_refresh(self) -> None:
        """인덱스 재로드 + 분야 드롭다운 재구성 + 그리드 재렌더.

        검색 본문 캐시도 함께 무효화해 삭제/신규 작업이 반영되도록 한다.
        """
        search_clear_cache()
        self._all_jobs = load_index()

        # 분야 드롭다운 재구성
        fields = sorted({
            (j.get("field") or "").strip()
            for j in self._all_jobs if (j.get("field") or "").strip()
        })
        self._field_menu.configure(values=["모든 분야", *fields])
        if self._field_var.get() not in ["모든 분야", *fields]:
            self._field_var.set("모든 분야")

        self._refresh_grid()

    def _refresh_grid(self) -> None:
        # 기존 카드 제거
        for w in self._scroll.winfo_children():
            w.destroy()

        filtered = self._apply_filters(self._all_jobs)
        self._filtered_jobs = filtered
        self._count_label.configure(
            text=f"{len(filtered)} / {len(self._all_jobs)} 건"
        )

        if not filtered:
            ctk.CTkLabel(
                self._scroll,
                text="조건에 맞는 작업이 없습니다." if self._all_jobs
                     else "아직 작업 기록이 없습니다.",
                text_color="gray55",
            ).grid(row=0, column=0, columnspan=self._COLUMNS, pady=60)
            return

        for i, job in enumerate(filtered):
            r, c = divmod(i, self._COLUMNS)
            self._render_card(r, c, job)

    def _apply_filters(self, jobs: list[dict]) -> list[dict]:
        """검색어 + 분야 + (옵션)본문 검색 + 정렬 적용 (Phase F).

        본문 검색이 켜진 경우 메타 불일치 잡도 본문 매칭이 있으면 포함.
        매칭된 잡에는 `_body_snippet` 키가 추가되어 카드가 스니펫을 렌더링.
        """
        q = self._search_var.get().strip().lower()
        field = self._field_var.get().strip()
        search_body = bool(self._search_body_var.get())

        def meta_match(j: dict) -> bool:
            if not q:
                return True
            hay = " ".join([
                j.get("organized_title") or "",
                j.get("title") or "",
                j.get("uploader") or "",
                " ".join(j.get("tags") or []),
            ]).lower()
            return q in hay

        def passes_filters(j: dict) -> Optional[dict]:
            """매치하면 job 사본 (스니펫 포함 가능) 반환, 아니면 None."""
            if field and field != "모든 분야" and (j.get("field") or "") != field:
                return None
            if not q:
                return j
            if meta_match(j):
                return j
            # 본문 검색이 켜져 있으면 result.md 에서도 찾아본다
            if search_body and j.get("has_markdown"):
                snippet = search_match_body(j.get("job_id", ""), q)
                if snippet:
                    copy = dict(j)
                    copy["_body_snippet"] = snippet
                    return copy
            return None

        out: list[dict] = []
        for j in jobs:
            res = passes_filters(j)
            if res is not None:
                out.append(res)

        sort_mode = self._sort_var.get()
        if sort_mode == "최신순":
            out.sort(key=lambda j: j.get("created_at") or "", reverse=True)
        elif sort_mode == "오래된순":
            out.sort(key=lambda j: j.get("created_at") or "")
        elif sort_mode == "길이 긴 순":
            out.sort(key=lambda j: j.get("duration_sec") or 0, reverse=True)
        elif sort_mode == "길이 짧은 순":
            out.sort(key=lambda j: j.get("duration_sec") or 0)
        elif sort_mode == "제목 A-Z":
            out.sort(key=lambda j: (j.get("organized_title") or j.get("title") or "").lower())
        return out

    def _reset_filters(self) -> None:
        # trace 가 발동해 _schedule_refresh 가 예약되므로 직접 호출은 불필요
        self._search_var.set("")
        self._field_var.set("모든 분야")
        self._sort_var.set("최신순")
        self._refresh_grid()

    def _schedule_refresh(self) -> None:
        """debounce: 타이핑이 빠르면 이전 예약을 취소하고 마지막 키 이후 200ms 에만 re-render."""
        if self._search_after_id is not None:
            try:
                self.after_cancel(self._search_after_id)
            except Exception:  # noqa: BLE001
                pass
        self._search_after_id = self.after(200, self._refresh_grid)

    # =========================================================================
    # Card rendering
    # =========================================================================
    def _render_card(self, row: int, col: int, job: dict) -> None:
        # 카드 크기는 grid 의 컬럼 minsize 로 보장 — grid_propagate 를 풀어
        # 길이 다른 제목/태그에서도 클리핑 없이 높이가 자연스럽게 확장되게.
        card = ctk.CTkFrame(
            self._scroll, fg_color=C_SURFACE, corner_radius=10,
            border_width=1, border_color=C_BORDER,
        )
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        # 썸네일 자리 (비동기 로딩)
        thumb_holder = ctk.CTkFrame(
            card, fg_color=C_BG, corner_radius=6,
            width=self._THUMB_W, height=self._THUMB_H,
        )
        thumb_holder.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="ew")
        thumb_holder.grid_propagate(False)
        self._attach_thumbnail(thumb_holder, job)

        # 상태 뱃지 (좌상단 오버레이 대신 제목 옆 아이콘으로)
        status = job.get("status", "unknown")
        status_icon = "✅" if status == "completed" else "❌"

        # 제목 (정리된 제목 우선)
        title = job.get("organized_title") or job.get("title") or "제목 없음"
        ctk.CTkLabel(
            card, text=f"{status_icon}  {title}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w", justify="left", wraplength=self._CARD_W - 30,
            text_color=C_TEXT,
        ).grid(row=1, column=0, padx=10, pady=(2, 2), sticky="w")

        # 메타 라인 1: 업로더 · 날짜
        uploader = (job.get("uploader") or "").strip()
        created = (job.get("created_at") or "")[:10]
        upload_date = (job.get("upload_date") or "").strip()
        date_part = upload_date or created
        meta1 = " · ".join(filter(None, [uploader, date_part]))
        if meta1:
            ctk.CTkLabel(
                card, text=meta1, font=ctk.CTkFont(size=11),
                anchor="w", text_color=C_TEXT_DIM,
                wraplength=self._CARD_W - 30,
            ).grid(row=2, column=0, padx=10, pady=0, sticky="w")

        # 메타 라인 2: 길이 · STT 엔진 · 화자 수
        dur_s = job.get("duration_sec") or 0
        if dur_s:
            h, rem = divmod(int(dur_s), 3600)
            m, s = divmod(rem, 60)
            dur_str = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
        else:
            dur_str = ""
        n_sp = job.get("num_speakers") or 0
        engine = job.get("stt_engine") or ""
        meta2 = " · ".join(filter(None, [
            dur_str, engine, f"화자 {n_sp}" if n_sp else "",
        ]))
        if meta2:
            ctk.CTkLabel(
                card, text=meta2, font=ctk.CTkFont(size=11),
                anchor="w", text_color=C_TEXT_DIM,
            ).grid(row=3, column=0, padx=10, pady=(0, 2), sticky="w")

        # 분야 + 태그
        field = (job.get("field") or "").strip()
        tags = job.get("tags") or []
        badge_line = ""
        if field:
            badge_line += f"📁 {field}"
        if tags:
            badge_line += ("   " if badge_line else "") + " ".join(f"#{t}" for t in tags[:5])
        if badge_line:
            ctk.CTkLabel(
                card, text=badge_line, font=ctk.CTkFont(size=10),
                anchor="w", text_color=C_PRIMARY,
                wraplength=self._CARD_W - 30, justify="left",
            ).grid(row=4, column=0, padx=10, pady=(2, 4), sticky="w")

        # 실패 시 에러 메시지
        if status == "failed":
            err = (job.get("error_message") or "").strip()
            if err:
                ctk.CTkLabel(
                    card, text=f"❌ {err[:120]}",
                    font=ctk.CTkFont(size=10), text_color=C_DANGER,
                    wraplength=self._CARD_W - 30, anchor="w", justify="left",
                ).grid(row=5, column=0, padx=10, pady=(2, 4), sticky="w")

        # Phase F — 본문 검색 매칭 시 스니펫 표시
        snippet = job.get("_body_snippet")
        if snippet:
            ctk.CTkLabel(
                card, text=f"🔍 {snippet[:200]}",
                font=ctk.CTkFont(size=10, slant="italic"),
                text_color=C_TEXT_DIM,
                wraplength=self._CARD_W - 30, anchor="w", justify="left",
            ).grid(row=5, column=0, padx=10, pady=(2, 4), sticky="w")

        # 액션 버튼 바
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=6, column=0, padx=8, pady=(4, 10), sticky="ew")
        job_id = job.get("job_id", "")
        # 7버튼 레이아웃 (카드 inner ~264px, 7×32+6×2=236 ← 여유 28px)
        #   .md · Edit | PDF · Obs · Ntn | Log · Del
        if job.get("has_markdown"):
            ctk.CTkButton(
                btn_row, text=".md", width=32, height=28,
                command=lambda jid=job_id, t=title: self._save_md(jid, t),
            ).pack(side="left", padx=(0, 2))
            ctk.CTkButton(
                btn_row, text="Edit", width=36, height=28,
                fg_color=C_SURFACE_HI, hover_color=C_PRIMARY,
                command=lambda jid=job_id, t=title: self._edit_note(jid, t),
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btn_row, text="PDF", width=32, height=28,
                command=lambda jid=job_id, t=title: self._save_pdf(jid, t),
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btn_row, text="Obs", width=32, height=28,
                fg_color=C_PRIMARY, hover_color=C_PRIMARY_HO,
                command=lambda jid=job_id, t=title: self._save_obsidian(jid, t),
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btn_row, text="Ntn", width=32, height=28,
                fg_color=C_PRIMARY, hover_color=C_PRIMARY_HO,
                command=lambda jid=job_id, t=title: self._save_notion(jid, t),
            ).pack(side="left", padx=2)
        ctk.CTkButton(
            btn_row, text="Log", width=32, height=28,
            fg_color="gray35",
            command=lambda jid=job_id: self._show_log(jid),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            btn_row, text="Del", width=32, height=28,
            fg_color="gray35", hover_color=C_DANGER,
            command=lambda jid=job_id: self._delete(jid),
        ).pack(side="right", padx=2)

    def _attach_thumbnail(self, holder: ctk.CTkFrame, job: dict) -> None:
        """
        썸네일 이미지 로드 (캐시 즉시, 미캐시 시 비동기 다운로드).
        실패 / 로컬파일 소스 시 회색 플레이스홀더 + 아이콘 라벨.
        """
        url = job.get("source_url") or ""
        video_id = extract_youtube_id(url) if url else None

        if not video_id:
            # 로컬 파일 또는 YouTube 아님
            ctk.CTkLabel(
                holder, text="🎵\n(로컬 파일)" if url else "🎙️",
                font=ctk.CTkFont(size=22), text_color=C_TEXT_DIM,
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        cache_path = cached_thumbnail_path(video_id)
        if cache_path.exists():
            self._place_thumbnail(holder, cache_path, video_id)
            return

        # 플레이스홀더 먼저 표시
        placeholder = ctk.CTkLabel(
            holder, text="⏳", font=ctk.CTkFont(size=22),
            text_color=C_TEXT_DIM,
        )
        placeholder.place(relx=0.5, rely=0.5, anchor="center")

        # 비동기 다운로드 요청 (중복 방지)
        if video_id not in self._pending_thumb_ids:
            self._pending_thumb_ids.add(video_id)
            def _on_complete(path):
                self._thumb_queue.put((video_id, path))
            download_thumbnail_async(video_id, _on_complete)

        # holder 를 video_id 로 기억해 나중에 찾음
        holder._gurunote_thumb_video_id = video_id  # type: ignore[attr-defined]
        holder._gurunote_placeholder = placeholder  # type: ignore[attr-defined]

    def _place_thumbnail(self, holder: ctk.CTkFrame, image_path, video_id: str) -> None:
        """PIL 로 이미지 로드해 CTkImage 로 holder 에 표시."""
        try:
            from PIL import Image  # type: ignore
            img = Image.open(image_path)
            ctk_img = ctk.CTkImage(
                light_image=img, dark_image=img,
                size=(self._THUMB_W, self._THUMB_H),
            )
            # GC 방지용 참조 유지
            self._thumb_refs[video_id] = ctk_img
            label = ctk.CTkLabel(holder, text="", image=ctk_img)
            label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:  # noqa: BLE001
            ctk.CTkLabel(
                holder, text="🎬", font=ctk.CTkFont(size=22),
                text_color=C_TEXT_DIM,
            ).place(relx=0.5, rely=0.5, anchor="center")

    def _poll_thumb_queue(self) -> None:
        """비동기 다운로드 완료 메시지를 메인 스레드에서 처리.

        다이얼로그가 destroyed 된 뒤 pending `after()` 콜백이 한 번 더 실행되면
        `self._scroll.winfo_children()` 이 `_tkinter.TclError` 를 낼 수 있어
        전체 블록을 try/except 로 감싼다.
        """
        try:
            try:
                while True:
                    video_id, path = self._thumb_queue.get_nowait()
                    self._pending_thumb_ids.discard(video_id)
                    if path is None:
                        continue
                    self._apply_thumbnail_to_cards(video_id, path)
            except queue.Empty:
                pass
        except Exception:  # noqa: BLE001 — TclError 등 widget-destroyed 경로
            return
        # 다이얼로그가 살아있을 때만 다음 poll 예약
        try:
            if self.winfo_exists():
                self.after(200, self._poll_thumb_queue)
        except Exception:  # noqa: BLE001
            pass

    def _apply_thumbnail_to_cards(self, video_id: str, path) -> None:
        """현재 그리드에서 해당 video_id 의 holder 들을 찾아 이미지 삽입."""
        for card in self._scroll.winfo_children():
            for child in card.winfo_children() if hasattr(card, "winfo_children") else []:
                vid = getattr(child, "_gurunote_thumb_video_id", None)
                if vid == video_id:
                    # 플레이스홀더 제거
                    ph = getattr(child, "_gurunote_placeholder", None)
                    if ph is not None:
                        try:
                            ph.destroy()
                        except Exception:  # noqa: BLE001
                            pass
                    self._place_thumbnail(child, path, video_id)

    # =========================================================================
    # Actions (기존과 동일)
    # =========================================================================
    def _edit_note(self, job_id: str, title: str) -> None:
        """HistoryDialog 의 Edit 버튼 → 인라인 마크다운 편집기 다이얼로그."""
        md = get_job_markdown(job_id)
        if md is None:
            messagebox.showinfo("없음", "마크다운 파일이 없습니다.")
            return

        def _on_saved() -> None:
            # 저장 후 검색 캐시 무효화 + 그리드 재로드 (스니펫/카드 갱신)
            search_clear_cache()
            self._reload_and_refresh()

        NoteEditorDialog(self, job_id, title, md, on_saved=_on_saved)

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

    def _save_pdf(self, job_id: str, title: str) -> None:
        """저장된 마크다운을 PDF 로 내보낸다 (Phase C)."""
        md = get_job_markdown(job_id)
        if not md:
            messagebox.showinfo("없음", "마크다운 파일이 없습니다.")
            return
        if not is_pdf_export_available():
            messagebox.showwarning("PDF 미지원", pdf_missing_hint())
            return
        from gurunote.exporter import sanitize_filename
        path = filedialog.asksaveasfilename(
            title="PDF 저장", defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"GuruNote_{sanitize_filename(title)}.pdf",
        )
        if not path:
            return
        try:
            markdown_to_pdf(md, Path(path), title=title)
            messagebox.showinfo("완료", f"PDF 저장됨:\n{path}")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("PDF 저장 실패", str(e))

    def _save_obsidian(self, job_id: str, title: str) -> None:
        """저장된 마크다운을 Obsidian vault 로 전송 (Phase D)."""
        md = get_job_markdown(job_id)
        if not md:
            messagebox.showinfo("없음", "마크다운 파일이 없습니다.")
            return
        vault = obsidian_vault()
        if vault is None:
            messagebox.showwarning(
                "Obsidian 미설정",
                "Settings 다이얼로그에서 `OBSIDIAN_VAULT_PATH` 를 지정해주세요.",
            )
            return
        if not is_obsidian_vault(vault):
            if not messagebox.askyesno(
                "Obsidian vault 확인",
                f"경로에 `.obsidian/` 폴더가 없습니다:\n{vault}\n\n"
                "그래도 이 폴더에 저장할까요?",
            ):
                return
        from gurunote.exporter import sanitize_filename
        filename = f"GuruNote_{sanitize_filename(title)}.md"
        try:
            out = obsidian_save(
                md, filename=filename, vault_path=vault,
                subfolder=obsidian_subfolder(),
            )
            messagebox.showinfo("Obsidian 저장 완료", f"{out}")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Obsidian 저장 실패", str(e))

    def _save_notion(self, job_id: str, title: str) -> None:
        """저장된 마크다운을 Notion 으로 전송 (Phase E).

        API 호출은 worker thread 로 던지고 `after()` 로 결과 폴링 — 히스토리
        다이얼로그가 freeze 되지 않음.
        """
        md = get_job_markdown(job_id)
        if not md:
            messagebox.showinfo("없음", "마크다운 파일이 없습니다.")
            return
        if not is_notion_sync_available():
            messagebox.showwarning("Notion 미지원", notion_missing_hint())
            return
        token = os.environ.get("NOTION_TOKEN", "").strip()
        parent_id = os.environ.get("NOTION_PARENT_ID", "").strip()
        parent_type = (os.environ.get("NOTION_PARENT_TYPE", "database") or "database").strip().lower()
        if not token or not parent_id:
            messagebox.showwarning(
                "Notion 미설정",
                "Settings 에서 `NOTION_TOKEN` 과 `NOTION_PARENT_ID` 를 지정하세요.",
            )
            return

        result_q: queue.Queue = queue.Queue()
        is_db = (parent_type == "database")

        def _worker():
            try:
                url = notion_save(md, title=title, token=token,
                                  parent_id=parent_id, is_database=is_db)
                result_q.put(("ok", url))
            except Exception as exc:  # noqa: BLE001
                result_q.put(("err", str(exc)))

        # 즉시 피드백 다이얼로그 없이 기본 cursor 를 "watch" 로 바꿔 진행 중임을 표시
        self.configure(cursor="watch")
        threading.Thread(target=_worker, daemon=True).start()
        self._poll_notion_from_history(result_q)

    def _poll_notion_from_history(self, q: "queue.Queue") -> None:
        """HistoryDialog 의 Notion 버튼 전용 결과 폴링 (200ms).

        다이얼로그 destroyed 후에도 stale `after()` 가 한 번 더 실행될 수
        있어 `winfo_exists` / `after` / `configure` 모두 TclError 방어.
        """
        try:
            status, payload = q.get_nowait()
        except queue.Empty:
            try:
                if self.winfo_exists():
                    self.after(200, lambda: self._poll_notion_from_history(q))
            except Exception:  # noqa: BLE001
                pass
            return
        try:
            self.configure(cursor="")
        except Exception:  # noqa: BLE001
            pass
        if status == "ok":
            if messagebox.askyesno("Notion 전송 완료", f"{payload}\n\n브라우저에서 열까요?"):
                import webbrowser
                webbrowser.open(payload)
        else:
            messagebox.showerror("Notion 전송 실패", payload)

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
            self._reload_and_refresh()

    def _on_rebuild_index(self) -> None:
        """
        `~/.gurunote/jobs/` 폴더 스캔 → `history.json` 재생성.

        사용 케이스:
          - history.json 삭제/손상 복구
          - 다른 머신에서 jobs/ 폴더만 복사해 왔을 때 마이그레이션
        """
        if not messagebox.askyesno(
            "히스토리 인덱스 재생성",
            "~/.gurunote/jobs/ 폴더를 스캔해 history.json 을 다시 만듭니다.\n"
            "기존 인덱스는 덮어쓰여지며 잡 파일들은 건드리지 않습니다.\n\n"
            "계속할까요?",
        ):
            return
        try:
            result = rebuild_index()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("인덱스 재생성 실패", str(exc))
            return

        msg = (
            f"스캔: {result['total_scanned']} 폴더\n"
            f"인덱스 등록: {result['indexed']} 건"
        )
        if result["errors"]:
            msg += f"\n손상/누락 (건너뜀): {len(result['errors'])}"
            if len(result["errors"]) <= 5:
                msg += "\n  " + "\n  ".join(result["errors"])
        if result["missing_md"]:
            msg += f"\nmetadata 에만 있고 result.md 없음: {len(result['missing_md'])}"
        messagebox.showinfo("인덱스 재생성 완료", msg)
        # 검색 캐시도 함께 클리어하고 다시 그리기
        search_clear_cache()
        self._reload_and_refresh()


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
            "OBSIDIAN_VAULT_PATH": "/Users/me/Documents/MyVault",
            "OBSIDIAN_SUBFOLDER": "GuruNote",
            "NOTION_PARENT_ID": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
            "NOTION_PARENT_TYPE": "database",
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
        # Provider 별 올바른 API 키/모델 필드 사용
        #   - anthropic → ANTHROPIC_API_KEY + ANTHROPIC_MODEL
        #   - gemini    → GOOGLE_API_KEY + GEMINI_MODEL  (이전 버전에서 누락돼
        #                  OPENAI_API_KEY 를 잘못 읽던 버그 수정)
        #   - openai / openai_compatible → OPENAI_API_KEY + OPENAI_BASE_URL +
        #                                   OPENAI_MODEL
        if provider == "anthropic":
            cfg.api_key = self._entries["ANTHROPIC_API_KEY"].get().strip()
            cfg.model = self._entries["ANTHROPIC_MODEL"].get().strip() or cfg.model
        elif provider == "gemini":
            cfg.api_key = self._entries["GOOGLE_API_KEY"].get().strip()
            cfg.model = self._entries["GEMINI_MODEL"].get().strip() or cfg.model
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
            sb, text="v0.6.0.15", font=ctk.CTkFont(size=10), text_color=C_TEXT_DIM,
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
        self._save_btn = ctk.CTkButton(top, text="Save .md", height=32, width=90, corner_radius=8,
                                       fg_color=C_SURFACE_HI, hover_color=C_PRIMARY, state="disabled", command=self._on_save)
        self._save_btn.grid(row=0, column=1, sticky="e", padx=(0, 4))
        self._save_pdf_btn = ctk.CTkButton(top, text="Save PDF", height=32, width=90, corner_radius=8,
                                           fg_color=C_SURFACE_HI, hover_color=C_PRIMARY, state="disabled",
                                           command=self._on_save_pdf)
        self._save_pdf_btn.grid(row=0, column=2, sticky="e", padx=(0, 4))
        self._save_obsidian_btn = ctk.CTkButton(top, text="→ Obsidian", height=32, width=100, corner_radius=8,
                                                fg_color=C_SURFACE_HI, hover_color=C_PRIMARY, state="disabled",
                                                command=self._on_save_obsidian)
        self._save_obsidian_btn.grid(row=0, column=3, sticky="e", padx=(0, 4))
        self._save_notion_btn = ctk.CTkButton(top, text="→ Notion", height=32, width=100, corner_radius=8,
                                              fg_color=C_SURFACE_HI, hover_color=C_PRIMARY, state="disabled",
                                              command=self._on_save_notion)
        self._save_notion_btn.grid(row=0, column=4, sticky="e")
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
        self._save_pdf_btn.configure(state="disabled")
        self._save_obsidian_btn.configure(state="disabled")
        self._save_notion_btn.configure(state="disabled")
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
        self._save_pdf_btn.configure(state="normal")
        self._save_obsidian_btn.configure(state="normal")
        self._save_notion_btn.configure(state="normal")
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

    def _on_save_pdf(self):
        """결과 마크다운을 렌더링된 PDF 로 저장 (Phase C)."""
        if not self._result:
            return
        if not is_pdf_export_available():
            messagebox.showwarning("PDF 미지원", pdf_missing_hint())
            return
        title = self._result["audio"].video_title
        name = f"GuruNote_{sanitize_filename(title)}.pdf"
        path = filedialog.asksaveasfilename(
            title="PDF 저장", defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("All", "*.*")], initialfile=name,
        )
        if not path:
            return
        try:
            markdown_to_pdf(self._result["full_md"], Path(path), title=title)
            messagebox.showinfo("완료", f"PDF 저장됨:\n{path}")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("PDF 저장 실패", str(e))

    def _on_save_obsidian(self):
        """결과 마크다운을 Obsidian vault 로 직접 저장 (Phase D)."""
        if not self._result:
            return
        vault = obsidian_vault()
        if vault is None:
            messagebox.showwarning(
                "Obsidian 미설정",
                "Settings 다이얼로그에서 `OBSIDIAN_VAULT_PATH` 를 지정해주세요.\n"
                "(Obsidian 앱의 vault 폴더 루트 경로 — `.obsidian/` 폴더가 있는 곳)",
            )
            return
        if not is_obsidian_vault(vault):
            if not messagebox.askyesno(
                "Obsidian vault 확인",
                f"경로에 `.obsidian/` 폴더가 없습니다:\n{vault}\n\n"
                "그래도 이 폴더에 저장할까요?",
            ):
                return
        title = self._result["audio"].video_title
        filename = f"GuruNote_{sanitize_filename(title)}.md"
        try:
            out = obsidian_save(
                self._result["full_md"],
                filename=filename,
                vault_path=vault,
                subfolder=obsidian_subfolder(),
            )
            messagebox.showinfo("Obsidian 저장 완료", f"{out}")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Obsidian 저장 실패", str(e))

    def _on_save_notion(self):
        """결과 마크다운을 Notion 페이지로 전송 (Phase E).

        Notion API 호출은 2-10초 블로킹이라 worker thread 로 던지고 main thread
        에선 `after()` 로 결과를 폴링해 UI freeze 회피.
        """
        if not self._result:
            return
        if not is_notion_sync_available():
            messagebox.showwarning("Notion 미지원", notion_missing_hint())
            return
        token = os.environ.get("NOTION_TOKEN", "").strip()
        parent_id = os.environ.get("NOTION_PARENT_ID", "").strip()
        parent_type = (os.environ.get("NOTION_PARENT_TYPE", "database") or "database").strip().lower()
        if not token or not parent_id:
            messagebox.showwarning(
                "Notion 미설정",
                "Settings 에서 `NOTION_TOKEN` 과 `NOTION_PARENT_ID` 를 지정하세요.\n"
                "Integration: https://www.notion.so/my-integrations\n"
                "parent page/DB 에서 해당 Integration 을 Share 해야 접근 가능합니다.",
            )
            return

        title = self._result["audio"].video_title
        md = self._result["full_md"]
        is_db = (parent_type == "database")

        # 전송 중 버튼 비활성화 + 라벨 변경
        self._save_notion_btn.configure(state="disabled", text="전송 중…")
        result_q: queue.Queue = queue.Queue()

        def _worker():
            try:
                url = notion_save(md, title=title, token=token,
                                  parent_id=parent_id, is_database=is_db)
                result_q.put(("ok", url))
            except Exception as exc:  # noqa: BLE001
                result_q.put(("err", str(exc)))

        threading.Thread(target=_worker, daemon=True).start()
        self._poll_notion_result(result_q)

    def _poll_notion_result(self, q: "queue.Queue") -> None:
        """result-card 의 Notion 버튼 전용 결과 폴링 (200ms 주기)."""
        try:
            status, payload = q.get_nowait()
        except queue.Empty:
            self.after(200, lambda: self._poll_notion_result(q))
            return
        # 완료: 버튼 복구 + 결과 다이얼로그
        self._save_notion_btn.configure(state="normal", text="→ Notion")
        if status == "ok":
            if messagebox.askyesno("Notion 전송 완료", f"{payload}\n\n브라우저에서 열까요?"):
                import webbrowser
                webbrowser.open(payload)
        else:
            messagebox.showerror("Notion 전송 실패", payload)

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
