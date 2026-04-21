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
from typing import Any, Optional

# pywebview is imported lazily inside methods that need it so that this module
# can be imported (e.g., for type checking, docs generation) without the GUI
# dependency. The bound ``window`` reference is what we actually use at runtime.


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
                "Audio/Video (*.mp3;*.wav;*.flac;*.m4a;*.aac;*.ogg;*.wma;*.opus;"
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

    # ============================================================ settings (TODO)

    def get_settings(self) -> dict:
        """Return current settings. API-key fields are exposed as ``*_set: bool`` only."""
        raise NotImplementedError("get_settings: wired in Phase 4")

    def save_settings(self, patch: dict) -> dict:
        """Persist a partial settings patch via gurunote.settings.save_settings."""
        raise NotImplementedError("save_settings: wired in Phase 4")

    def test_connection(self, provider: str) -> dict:
        """Probe the given LLM provider with a minimal call."""
        raise NotImplementedError("test_connection: wired in Phase 4")

    # ============================================================ history (TODO)

    def list_history(self, limit: Optional[int] = None, offset: int = 0) -> dict:
        """Return a slice of the history index."""
        raise NotImplementedError("list_history: wired in Phase 2")

    def get_history_detail(self, job_id: str) -> dict:
        """Return ``{markdown, meta, log_excerpt?}`` for one job."""
        raise NotImplementedError("get_history_detail: wired in Phase 2")

    def delete_history(self, job_id: str) -> dict:
        raise NotImplementedError("delete_history: wired in Phase 2")

    def rebuild_index(self) -> dict:
        """Rebuild the semantic index. Long-running → returns job_id."""
        raise NotImplementedError("rebuild_index: wired in Phase 2")

    # ============================================================ note edit (TODO)

    def update_note(self, job_id: str, markdown: str) -> dict:
        """Persist edited markdown back to disk."""
        raise NotImplementedError("update_note: wired in Phase 5")

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
