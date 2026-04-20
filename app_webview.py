"""GuruNote WebView UI — entrypoint.

Coexists with the existing CTk entrypoint (``app.py``). Run either::

    python3 app.py            # legacy CustomTkinter UI
    python3 app_webview.py    # new PyWebView UI (this file)

This is the Phase 1 MVP skeleton. The pipeline wiring is intentionally not
hooked up yet — clicking '생성하기' shows a stub alert. Phase 1-B will wire
``Api.start_pipeline`` to the existing ``PipelineWorker``.

See:
- ``docs/webview-ui/TECH_CHOICE.md`` — why PyWebView
- ``docs/webview-ui/ARCHITECTURE.md`` — process model, bridge, event bus
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    try:
        import webview
    except ImportError:
        sys.stderr.write(
            "pywebview is not installed.\n"
            "Install with:  pip install 'pywebview>=4.4,<5.0'\n"
            "(Or run setup.sh / setup.bat to install all GuruNote deps.)\n"
        )
        return 1

    from gurunote.webui.bridge import Api

    # Resolve index.html relative to this file so it works both in dev
    # (running from source) and once packaged by PyInstaller (where __file__
    # is inside the bundle).
    here = Path(__file__).resolve().parent
    index_path = here / "gurunote" / "webui" / "index.html"
    if not index_path.exists():
        sys.stderr.write(f"index.html not found at {index_path}\n")
        return 2

    api = Api()
    window = webview.create_window(
        title="GuruNote",
        url=str(index_path),
        js_api=api,
        width=1280,
        height=820,
        min_size=(960, 600),
        # frameless=False, easy_drag=False — keep native window chrome on macOS
    )
    api.bind_window(window)

    # webview.start() blocks the main thread until the window is closed.
    # All long-running work (PipelineWorker etc.) must be spawned on
    # background threads from within Bridge methods.
    webview.start(debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
