"""GuruNote WebView UI — JavaScript Bridge (pywebview js_api).

Exposes a single ``Api`` class to the front-end via pywebview's ``js_api``
parameter. The browser calls ``window.pywebview.api.<method_name>(...)``;
pywebview marshals arguments and return values as JSON.

**Phase 1 MVP status: skeleton.**

- Most methods raise ``NotImplementedError`` and are wired up incrementally
  in Phase 1-B → Phase 5.
- Only ``get_app_info`` and ``pick_file`` return real data — they are the
  minimum needed to demonstrate that the bridge round-trips correctly.

See ``docs/webview-ui/ARCHITECTURE.md`` § 3 for the full method catalog and
response envelope policy.

Open question (deferred — see ``HANDOFF_MORNING.md``): response envelope
shape (raw dict vs. ``{ok, data, error}`` wrapper vs. raise-and-reject).
The skeleton uses raw dicts on success and ``{ok: False, error: str}`` on
failure as a placeholder. Final shape will be settled before broad wiring.
"""
from __future__ import annotations

import platform
import re
from pathlib import Path
from typing import Any, Optional

# pywebview is imported lazily inside methods that need it so that this module
# can be imported (e.g., for type checking, docs generation) without the GUI
# dependency. The bound ``window`` reference is what we actually use at runtime.

# ----------------------------------------------------------------------------
# Settings allow-list — Mask-2 policy (Phase 1-C #3)
# ----------------------------------------------------------------------------
# Only keys in _KNOWN_SETTINGS are exposed by get_settings / accepted by
# save_settings. This protects the JS bridge from being used to mutate
# arbitrary process environment variables.
#
# _SECRET_KEYS classifies which fields are sensitive — their values are
# returned as a presence-bool only, never as plaintext, and the UI shows
# "●●●●● [저장됨]" placeholders instead of the raw value.
#
# When adding a new env-driven config, list it here AND in the form section
# layout (gurunote/webui/index.html, Settings card — Phase 1-C #3 commits).
_KNOWN_SETTINGS: tuple[str, ...] = (
    # LLM provider routing + tunables
    "LLM_PROVIDER",
    "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL",
    "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL",
    "GOOGLE_API_KEY", "GEMINI_MODEL",
    "LLM_TEMPERATURE",
    "LLM_TRANSLATION_MAX_TOKENS", "LLM_SUMMARY_MAX_TOKENS",
    # STT engines + diarization
    "GURUNOTE_STT_ENGINE",
    "WHISPERX_MODEL", "WHISPERX_BATCH_SIZE",
    "MLX_WHISPER_MODEL",
    "HF_TOKEN", "HUGGINGFACE_TOKEN",  # canonical + legacy alias
    "ASSEMBLYAI_API_KEY",
    # Integrations (Obsidian, Notion)
    "OBSIDIAN_VAULT_PATH", "OBSIDIAN_SUBFOLDER",
    "NOTION_TOKEN", "NOTION_PARENT_ID", "NOTION_PARENT_TYPE",
)

_SECRET_KEYS: frozenset[str] = frozenset({
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "ASSEMBLYAI_API_KEY",
    "HF_TOKEN",
    "HUGGINGFACE_TOKEN",
    "NOTION_TOKEN",
})


# === thumbnail enrichment helpers (Phase 2B-3) ===

_YT_VIDEO_ID = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/)([a-zA-Z0-9_-]{11})")


def _extract_youtube_video_id(url: Optional[str]) -> Optional[str]:
    """YouTube URL 에서 11-char video ID 추출. 비-YouTube URL → None."""
    if not url:
        return None
    m = _YT_VIDEO_ID.search(url)
    return m.group(1) if m else None


def _resolve_thumbnail_url(video_id: Optional[str]) -> Optional[str]:
    """video_id 기반 thumbnail URL.

    1순위: ``~/.gurunote/thumbnails/{video_id}.jpg`` cached → ``file://`` URI
    2순위: ``https://img.youtube.com/vi/{video_id}/hqdefault.jpg``
    None 입력 → None
    """
    if not video_id:
        return None
    cached = Path.home() / ".gurunote" / "thumbnails" / f"{video_id}.jpg"
    if cached.exists():
        return cached.as_uri()
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


class Api:
    """JavaScript-facing bridge.

    Lifecycle:
        1. ``Api()`` is instantiated before ``webview.create_window``.
        2. The instance is passed as ``js_api=`` to ``create_window``.
        3. After ``create_window`` returns the ``Window``, call
           ``api.bind_window(window)`` so subsequent methods can use
           ``window.create_file_dialog`` and ``window.evaluate_js``.
    """

    # ------------------------------------------------------------------ setup

    def __init__(self) -> None:
        self._window = None  # set via bind_window()

    def bind_window(self, window: Any) -> None:
        """Attach the pywebview Window so the bridge can call its methods."""
        self._window = window

    # ------------------------------------------------------------------ helpers

    def _err(self, code: str, message: str) -> dict:
        return {"ok": False, "error": message, "code": code}

    def _require_window(self) -> Any:
        if self._window is None:
            raise RuntimeError(
                "Api.bind_window() not called — bridge is not ready yet"
            )
        return self._window

    # ============================================================ app info

    def get_app_info(self) -> dict:
        """Return version, platform, and basic hardware info.

        Used by the front-end on initial load to populate the sidebar
        version label and conditionally show Apple Silicon-only options.
        """
        try:
            from gurunote import __version__
        except ImportError:
            __version__ = "unknown"

        return {
            "version": __version__,
            "platform": platform.system(),
            "machine": platform.machine(),
            "is_apple_silicon": (
                platform.system() == "Darwin" and platform.machine() == "arm64"
            ),
        }

    # ============================================================ file picker

    def pick_file(self) -> dict:
        """Open native file-open dialog. Returns ``{path, size}`` or ``{cancelled}``.

        The file_types filter mirrors ``gurunote.audio.SUPPORTED_EXTS``
        (8 audio + 9 video = 17 extensions) so users cannot pick a file
        via the dialog's audio/video filter that would subsequently fail
        ``is_supported_local_file`` in ``start_pipeline``.

        ``size`` is the file's byte count (``Path.stat().st_size``), or
        ``None`` if the stat call fails. The front-end uses this for the
        selected-file badge and can still function without it.
        """
        import webview  # local import — only needed at runtime
        from pathlib import Path

        window = self._require_window()
        result = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=(
                # pywebview 4.x label regex `[\w ]+` rejects '/' — keep label
                # ASCII word chars + spaces only. See webview/util.py
                # parse_file_type → "is not a valid file filter" otherwise.
                "Audio Video Files (*.mp3;*.wav;*.flac;*.m4a;*.aac;*.ogg;*.wma;*.opus;"
                "*.mp4;*.mkv;*.avi;*.mov;*.webm;*.wmv;*.flv;*.ts;*.m4v)",
                "All files (*.*)",
            ),
        )
        if not result:
            return {"cancelled": True}
        path = result[0]
        try:
            size = Path(path).stat().st_size
        except OSError:
            size = None
        return {"path": path, "size": size}

    # ============================================================ pipeline

    def start_pipeline(self, source: dict) -> dict:
        """Validate, then spawn a ``PipelineSession`` on a background thread.

        ``source`` shape::

            {
              "kind": "youtube" | "local",
              "value": str,                 # URL or absolute file path
              "engine": "auto" | "whisperx" | "mlx" | "assemblyai",
              "provider": "openai" | "anthropic" | "gemini" | "openai_compatible",
            }

        Returns ``{"job_id": str}`` on success. Raises on any validation or
        preflight failure; pywebview forwards the exception to JS as a
        Promise reject so callers ``await`` with ``try/catch``.

        Raised ``RuntimeError`` ``args[0]`` uses a ``<CODE>:<detail>`` convention so
        the front-end can switch on structured codes:
            INVALID_URL:<detail>
            INVALID_LOCAL_FILE:<path>
            API_KEY_MISSING:<env_var_name>

        Progress / log / result are delivered via the JS event bus.
        """
        window = self._require_window()

        # ---- shape validation
        if not isinstance(source, dict):
            raise ValueError(f"source must be a dict, got {type(source).__name__}")
        for key in ("kind", "value", "engine", "provider"):
            if key not in source:
                raise ValueError(f"source missing required key: {key!r}")

        kind = source["kind"]
        value = (source.get("value") or "").strip()
        provider = source["provider"]

        # ---- source validation (import from gurunote.audio lazily to avoid
        # pulling in yt-dlp / ffmpeg checks at bridge import time)
        if kind == "youtube":
            from gurunote.audio import is_probably_youtube_url  # noqa: PLC0415
            if not is_probably_youtube_url(value):
                raise RuntimeError("INVALID_URL:유튜브 URL 형식이 아닙니다.")
        elif kind == "local":
            from pathlib import Path  # noqa: PLC0415
            from gurunote.audio import is_supported_local_file  # noqa: PLC0415
            if not value or not Path(value).is_file() or not is_supported_local_file(value):
                raise RuntimeError(f"INVALID_LOCAL_FILE:{value}")
        else:
            raise ValueError(f"source.kind must be 'youtube' or 'local', got {kind!r}")

        # ---- API key preflight (mirrors gui.py _check_api_keys; does NOT launch
        # the settings dialog — JS caller shows a toast with the missing key code)
        import os  # noqa: PLC0415
        key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY",
            "openai_compatible": "OPENAI_BASE_URL",
        }
        required_env = key_map.get(provider)
        if required_env and not os.environ.get(required_env):
            raise RuntimeError(f"API_KEY_MISSING:{required_env}")

        # ---- launch
        from gurunote.webui.session import PipelineSession  # noqa: PLC0415
        session = PipelineSession(window, {
            "kind": kind,
            "value": value,
            "engine": source["engine"],
            "provider": provider,
        })
        session.start()
        return {"job_id": session.job_id}

    def stop_pipeline(self, job_id: str) -> dict:
        """Signal the worker for ``job_id`` to stop. Returns ``{"stopped": True}``.

        Raises ``RuntimeError("NO_ACTIVE_SESSION:<job_id>")`` if the job is
        unknown or already completed.
        """
        from gurunote.webui.session import get_session  # noqa: PLC0415
        session = get_session(job_id)
        if session is None:
            raise RuntimeError(f"NO_ACTIVE_SESSION:{job_id}")
        session.request_stop()
        return {"stopped": True}

    def get_pipeline_status(self, job_id: str) -> dict:
        """Poll fallback: returns whether a session is still active for ``job_id``.

        Not normally needed — events push progress. Useful if the front-end
        reloads and loses event-bus state.
        """
        from gurunote.webui.session import get_session  # noqa: PLC0415
        return {"active": get_session(job_id) is not None}

    # ============================================================ settings

    def get_settings(self) -> dict:
        """Return current settings.

        Response shape::

            {
              "ok": True,
              "values": { non_secret_KEY: current str value (possibly "") },
              "secrets_set": { secret_KEY: bool },
            }

        Plaintext secret values are NEVER returned — only a boolean
        presence flag. The UI renders "●●●●● [저장됨]" placeholders for
        keys whose ``secrets_set[key]`` is ``True`` and prompts for new
        input on the rest.
        """
        import os  # noqa: PLC0415

        try:
            values: dict[str, str] = {}
            secrets_set: dict[str, bool] = {}
            for key in _KNOWN_SETTINGS:
                current = os.environ.get(key, "")
                if key in _SECRET_KEYS:
                    secrets_set[key] = bool(current)
                else:
                    values[key] = current
            return {"ok": True, "values": values, "secrets_set": secrets_set}
        except Exception as exc:  # noqa: BLE001
            return self._err(
                "SETTINGS_LOAD_FAILED", f"{type(exc).__name__}: {exc}"
            )

    def save_settings(self, patch: dict) -> dict:
        """Persist a partial settings patch via gurunote.settings.save_settings.

        Behaviors:

        - Only keys in ``_KNOWN_SETTINGS`` are accepted; unknown keys
          short-circuit with ``UNKNOWN_KEYS`` so the JS surface cannot
          mutate arbitrary env vars.
        - Empty-string values trigger the explicit-delete path in
          ``gurunote.settings.save_settings`` (``os.environ.pop`` plus a
          ``KEY=""`` line in ``.env``). JSON ``null`` is coerced to the
          same empty string so a UI sending ``{KEY: null}`` deletes too.
          Unspecified keys are untouched.
        - All values are coerced to ``str`` so JS numbers (e.g.
          ``LLM_TEMPERATURE``) round-trip correctly.

        Response::

            { "ok": True, "changed": int, "backup": str | null }
        """
        from gurunote.settings import save_settings as _save_settings  # noqa: PLC0415

        if not isinstance(patch, dict):
            return self._err(
                "INVALID_PATCH",
                f"patch must be dict, got {type(patch).__name__}",
            )
        unknown = sorted(k for k in patch if k not in _KNOWN_SETTINGS)
        if unknown:
            return self._err(
                "UNKNOWN_KEYS", f"unknown setting keys: {', '.join(unknown)}"
            )
        coerced: dict[str, str] = {
            k: ("" if v is None else str(v)) for k, v in patch.items()
        }
        try:
            changed, backup_path = _save_settings(coerced, create_backup=True)
            return {
                "ok": True,
                "changed": changed,
                "backup": str(backup_path) if backup_path else None,
            }
        except Exception as exc:  # noqa: BLE001
            return self._err(
                "SETTINGS_SAVE_FAILED", f"{type(exc).__name__}: {exc}"
            )

    def test_connection(self, provider: str) -> dict:
        """Probe the given LLM provider with a minimal call."""
        raise NotImplementedError("test_connection: wired in Phase 4")

    # ============================================================ history (TODO)

    def list_history(self, payload: Any = None, *, limit: Optional[int] = None, offset: int = 0) -> dict:
        """Return a slice of the history index.

        Backed by ``gurunote.history.load_index`` — the same store that the
        legacy CTk/Streamlit UIs read. WebView pipeline runs land here too
        because ``gui.PipelineWorker`` already calls ``save_job`` on
        completion (success and failure paths).

        Phase 2B-3: each item is enriched with ``video_id`` + ``thumbnail_url``
        so the React JobCard can render thumbnails without round-tripping
        again. Resolution priority: cached ``~/.gurunote/thumbnails/`` →
        YouTube hqdefault → ``None`` (front-end gradient fallback).

        Calling conventions (pywebview 4.x JS bridge marshals JS args
        positionally, so a JS object becomes a single positional dict):

          - JS:     ``api.list_history({limit: 100, offset: 0})``
          - JS:     ``api.list_history()``
          - Python: ``api.list_history(limit=100)``  (kwarg form preserved)
        """
        from gurunote.history import load_index  # noqa: PLC0415

        # Normalize JS-style ``{limit, offset}`` payload, while preserving the
        # original keyword-only form that Python callers may use.
        if isinstance(payload, dict):
            limit = payload.get("limit", limit)
            offset = payload.get("offset", offset)
        elif isinstance(payload, int):
            # Legacy positional ``api.list_history(100)``.
            limit = payload
        # Type guards — protect against malformed JS values reaching slice().
        if not isinstance(offset, int):
            offset = 0
        if limit is not None and not isinstance(limit, int):
            limit = None

        try:
            items = load_index()
            total = len(items)
            if offset:
                items = items[offset:]
            if limit is not None:
                items = items[:limit]
            for item in items:
                video_id = _extract_youtube_video_id(item.get("source_url"))
                item["video_id"] = video_id
                item["thumbnail_url"] = _resolve_thumbnail_url(video_id)
            return {"ok": True, "total": total, "items": items}
        except Exception as exc:  # noqa: BLE001
            return self._err("HISTORY_LIST_FAILED", f"{type(exc).__name__}: {exc}")

    def get_history_detail(self, payload: Any = None, *, job_id: Optional[str] = None) -> dict:
        """Return ``{markdown, full_html, meta, filename}`` for one job.

        ``full_html`` is server-side rendered with the same markdown
        extensions used by the live pipeline so the front-end's existing
        ``renderResult()`` can consume it without branching.

        pywebview JS bridge marshals JS objects as a single positional dict —
        accepts ``api.get_history_detail({job_id})`` and ``api.get_history_detail(job_id)``.
        """
        import markdown as _markdown  # noqa: PLC0415
        from gurunote.history import get_job_markdown, load_index  # noqa: PLC0415

        # Normalize payload (dict / str positional / kwarg).
        if isinstance(payload, dict):
            job_id = payload.get("job_id", job_id)
        elif isinstance(payload, str):
            job_id = payload

        if not isinstance(job_id, str) or not job_id:
            return self._err("INVALID_ID", "job_id must be a non-empty string")
        if "/" in job_id or "\\" in job_id or ".." in job_id:
            return self._err("INVALID_ID", "job_id contains path separators")

        try:
            md = get_job_markdown(job_id)
            if md is None:
                return self._err("HISTORY_NOT_FOUND", f"no result.md for job {job_id}")
            meta = next(
                (e for e in load_index() if e.get("job_id") == job_id),
                {},
            )
            full_html = _markdown.markdown(
                md, extensions=["fenced_code", "tables", "toc"]
            )
            return {
                "ok": True,
                "job_id": job_id,
                "markdown": md,
                "full_html": full_html,
                "meta": meta,
                "filename": "result.md",
            }
        except Exception as exc:  # noqa: BLE001
            return self._err("READ_FAILED", f"{type(exc).__name__}: {exc}")

    def delete_history(self, job_id: str) -> dict:
        raise NotImplementedError("delete_history: wired in Phase 2")

    def rebuild_index(self) -> dict:
        """Rebuild the semantic index. Long-running → returns job_id."""
        raise NotImplementedError("rebuild_index: wired in Phase 2")

    # ============================================================ note edit (TODO)

    def update_note(self, payload: Any = None, *, job_id: Optional[str] = None, markdown: Optional[str] = None) -> dict:
        """Persist edited markdown back to ``~/.gurunote/jobs/<job_id>/result.md``.

        pywebview JS bridge marshals JS objects as a single positional dict.
        Accepts ``api.update_note({job_id, markdown})`` (JS) and
        ``api.update_note(job_id, markdown)`` (Python positional).

        Returns ``{ok: True, path: str}`` or ``{ok: False, error, code}``.
        """
        # Normalize payload shapes.
        if isinstance(payload, dict):
            job_id = payload.get("job_id", job_id)
            markdown = payload.get("markdown", markdown)
        elif isinstance(payload, str) and not isinstance(markdown, str):
            # Python positional: update_note(job_id, markdown)
            # If only one str passed, treat as job_id (markdown must be set via kwarg).
            job_id = payload

        if not isinstance(job_id, str) or not job_id:
            return self._err("INVALID_ID", "job_id must be a non-empty string")
        if "/" in job_id or "\\" in job_id or ".." in job_id:
            return self._err("INVALID_ID", "job_id contains path separators")
        if not isinstance(markdown, str):
            return self._err("INVALID_MARKDOWN", "markdown must be a string")

        try:
            from gurunote.history import JOBS_DIR  # noqa: PLC0415
            job_dir = JOBS_DIR / job_id
            if not job_dir.exists():
                return self._err("HISTORY_NOT_FOUND", f"no job dir for {job_id}")
            result_path = job_dir / "result.md"
            result_path.write_text(markdown, encoding="utf-8")
            return {"ok": True, "path": str(result_path)}
        except OSError as exc:
            return self._err("WRITE_FAILED", f"{type(exc).__name__}: {exc}")

    # ============================================================ exporters

    def save_result_as(self, payload: Any = None, default_filename: Any = None, *,
                       markdown: Optional[str] = None) -> dict:
        """Open native Save dialog and write ``markdown`` to the chosen path.

        Used by the result card's "저장" button and ⌘S shortcut. The caller
        passes the markdown currently rendered in the UI (``result.full_md``)
        plus a suggested filename (autosave basename, or ``GuruNote_<title>.md``
        as fallback).

        pywebview JS bridge marshals JS objects as a single positional dict.
        Accepts:
          - JS object: ``api.save_result_as({markdown, default_filename})``
          - JS positional: ``api.save_result_as(markdown_str, default_filename_str)``
          - Python kwargs: ``api.save_result_as(markdown=..., default_filename=...)``

        Returns:
            ``{"path": str, "cancelled": False}`` on success,
            ``{"cancelled": True}`` if the user dismissed the dialog,
            ``{"ok": False, "error": str, "code": "SAVE_FAILED"}`` on I/O error.

        The default directory is ``~/Documents`` (intentionally distinct from
        the autosave folder so user-initiated saves land somewhere the user
        actively chose, not alongside the auto-captured copies).
        """
        import webview  # noqa: PLC0415

        # Normalize payload shapes.
        if isinstance(payload, dict):
            markdown = payload.get("markdown", markdown)
            default_filename = payload.get("default_filename", default_filename)
        elif isinstance(payload, str):
            # Legacy positional: save_result_as(markdown, default_filename)
            markdown = payload

        if not isinstance(markdown, str):
            return self._err("SAVE_FAILED", f"markdown must be str, got {type(markdown).__name__}")
        if not isinstance(default_filename, str) or not default_filename.strip():
            default_filename = "GuruNote.md"

        window = self._require_window()
        default_dir = str(Path.home() / "Documents")
        try:
            result = window.create_file_dialog(
                webview.SAVE_DIALOG,
                directory=default_dir,
                save_filename=default_filename,
                file_types=("Markdown (*.md)", "All files (*.*)"),
            )
        except Exception as exc:  # noqa: BLE001 — native dialog errors are opaque; normalize
            return self._err("SAVE_FAILED", f"dialog: {type(exc).__name__}: {exc}")
        # pywebview SAVE_DIALOG: returns a string path, a tuple/list with one
        # path, or a falsy value on cancel. Normalize.
        if not result:
            return {"cancelled": True}
        path = result[0] if isinstance(result, (list, tuple)) else result
        if not path:
            return {"cancelled": True}

        try:
            Path(path).write_text(markdown, encoding="utf-8")
        except OSError as exc:
            return self._err("SAVE_FAILED", f"{type(exc).__name__}: {exc}")
        return {"path": str(path), "cancelled": False}

    # ============================================================ exporters (TODO)

    def save_markdown(self, job_id: str, target_path: Optional[str] = None) -> dict:
        raise NotImplementedError("save_markdown: wired in Phase 2-B")

    def save_pdf(self, job_id: str, target_path: Optional[str] = None) -> dict:
        raise NotImplementedError("save_pdf: wired in Phase 2-B")

    def send_obsidian(self, job_id: str) -> dict:
        raise NotImplementedError("send_obsidian: wired in Phase 2-B")

    def send_notion(self, job_id: str) -> dict:
        """Long-running → returns job_id; result via ``notion_progress`` event."""
        raise NotImplementedError("send_notion: wired in Phase 2-B")

    # ============================================================ updater (TODO)

    def check_update(self) -> dict:
        raise NotImplementedError("check_update: wired in Phase 4-B")

    # ============================================================ misc

    def show_message(self, title: str, body: str, kind: str = "info") -> dict:
        """Show a simple modal. ``kind`` ∈ {info, warning, error}.

        Phase 1 MVP: routed to JS-side ``alert()`` (no native chrome).
        Phase 2+: proper styled modal in HTML.
        """
        raise NotImplementedError("show_message: wired in Phase 2")
