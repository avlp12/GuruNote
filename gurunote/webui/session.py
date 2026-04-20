"""Pipeline session adapter — bridges PipelineWorker queues to the JS event bus.

Each ``PipelineSession`` owns a single ``gui.PipelineWorker`` (imported at first
use) and a recurring ``threading.Timer`` poller. The poller drains the worker's
three queues (msg / progress / result) every 100 ms and emits events into the
webview via ``window.evaluate_js("window.__emit(...)")``.

Event shapes
------------
- ``log``       : ``{"line": str}``                           — single line
- ``log_batch`` : ``{"lines": list[str]}``                    — batched (>= 50)
- ``progress``  : ``{"job_id": str, "pct": float}``           — 0.0 – 1.0
- ``result``    : ``{"job_id": str, "ok": bool, "full_md": str,
                     "full_html": str, "summary_md": str,
                     "video_title": str}``  (ok=False → also ``"error": str``)

The log batching threshold (50) is intentional: per-line ``evaluate_js``
calls are fine at normal pipeline log rates (a few per second) but get
expensive under tqdm bursts from HuggingFace / WhisperX model download.
Above the threshold we ship a single event; the JS bus handler knows both.
"""
from __future__ import annotations

import json
import queue
import sys
import threading
from typing import Any

_ACTIVE: dict[str, "PipelineSession"] = {}

_LOG_BATCH_THRESHOLD = 50
_POLL_INTERVAL_SEC = 0.1  # matches gui.py's self.after(100, ...)


def get_session(job_id: str) -> "PipelineSession | None":
    return _ACTIVE.get(job_id)


class PipelineSession:
    """Thin adapter on top of gui.PipelineWorker.

    Source dict shape (validated by Api.start_pipeline before this is called)::

        {
          "kind": "youtube" | "local",
          "value": str,                 # URL or absolute path
          "engine": "auto" | "whisperx" | "mlx" | "assemblyai",
          "provider": "openai" | "anthropic" | "gemini" | "openai_compatible",
        }
    """

    def __init__(self, window: Any, source: dict) -> None:
        # Deferred import — ``gui`` has module-level side effects
        # (log_redirect, ctk theme) that we accept but want to delay until the
        # first pipeline run rather than import-time of this module.
        from gui import PipelineWorker  # noqa: PLC0415

        kind = source["kind"]
        value = source["value"]

        self.window = window
        self.source = source
        self.worker = PipelineWorker(
            engine=source["engine"],
            provider=source["provider"],
            youtube_url=value if kind == "youtube" else "",
            local_file=value if kind == "local" else "",
        )
        self.job_id = self.worker.job_id
        self._done = False
        self._timer: threading.Timer | None = None

    # ---- public

    def start(self) -> None:
        _ACTIVE[self.job_id] = self
        self.worker.start()
        self._schedule_poll()

    def request_stop(self) -> None:
        self.worker.request_stop()

    # ---- internal

    def _schedule_poll(self) -> None:
        if self._done:
            return
        self._timer = threading.Timer(_POLL_INTERVAL_SEC, self._poll)
        self._timer.daemon = True
        self._timer.start()

    def _poll(self) -> None:
        # 1) Drain msg_queue — batch or per-line per user spec
        lines: list[str] = []
        while True:
            try:
                lines.append(self.worker.msg_queue.get_nowait())
            except queue.Empty:
                break
        if len(lines) >= _LOG_BATCH_THRESHOLD:
            self._emit("log_batch", {"lines": lines})
        else:
            for line in lines:
                self._emit("log", {"line": line})

        # 2) Drain progress_queue — always per-event (low frequency)
        while True:
            try:
                pct = self.worker.progress_queue.get_nowait()
                self._emit("progress", {"job_id": self.job_id, "pct": pct})
            except queue.Empty:
                break

        # 3) Check result_queue (at most one per job → terminal)
        try:
            raw = self.worker.result_queue.get_nowait()
            self._done = True
            self._emit("result", self._normalize_result(raw))
            _ACTIVE.pop(self.job_id, None)
            return
        except queue.Empty:
            pass

        self._schedule_poll()

    def _normalize_result(self, result: dict) -> dict:
        """Convert worker's result dict (containing Python objects) to JSON-safe shape."""
        if not result.get("ok"):
            return {
                "job_id": self.job_id,
                "ok": False,
                "error": str(result.get("error", "알 수 없는 오류")),
            }

        full_md = result.get("full_md", "")
        audio = result.get("audio")
        video_title = getattr(audio, "video_title", "") if audio is not None else ""

        return {
            "job_id": self.job_id,
            "ok": True,
            "video_title": video_title,
            "full_md": full_md,
            "full_html": _md_to_html(full_md),
            "summary_md": result.get("summary_md", ""),
        }

    def _emit(self, event: str, payload: dict) -> None:
        """Push an event to JS. Swallows errors (window may be closed)."""
        try:
            js_event = json.dumps(event)
            js_payload = json.dumps(payload, ensure_ascii=False, default=str)
            self.window.evaluate_js(f"window.__emit({js_event}, {js_payload})")
        except Exception as e:  # noqa: BLE001
            print(f"[webui] emit failed: {event}: {e!r}", file=sys.stderr)


def _md_to_html(md_text: str) -> str:
    """Markdown → HTML via the ``markdown`` package. Escaped <pre> on ImportError."""
    if not md_text:
        return ""
    try:
        import markdown  # noqa: PLC0415
        return markdown.markdown(md_text, extensions=["extra"])
    except ImportError:
        import html  # noqa: PLC0415
        return f"<pre>{html.escape(md_text)}</pre>"
