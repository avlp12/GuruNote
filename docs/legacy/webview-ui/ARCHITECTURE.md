# GuruNote WebView UI — 아키텍처

**대상 브랜치:** `feat/webview-ui`
**상위 결정 문서:** [`TECH_CHOICE.md`](./TECH_CHOICE.md)
**최종 수정:** 2026-04-20

---

## 1. 프로세스 모델

```
┌─────────────────────────────────────────────────────────────┐
│                  Single Python Process                       │
│                                                              │
│  ┌────────────────┐         ┌─────────────────────────┐    │
│  │  Main Thread   │         │   Worker Thread(s)       │    │
│  │                │         │                          │    │
│  │  pywebview     │  queue  │  PipelineWorker          │    │
│  │  event loop    │ ◄─────  │   (gurunote.audio,       │    │
│  │  (WKWebView)   │         │    .stt, .llm, ...)      │    │
│  │                │         │                          │    │
│  │  poll dispatch │         │  Index rebuild           │    │
│  │  evaluate_js() │         │  Thumbnail download      │    │
│  └───────┬────────┘         │  Notion / Obsidian sync  │    │
│          │                  └─────────────────────────┘    │
│          │ js bridge                                         │
│          ▼                                                   │
│  ┌────────────────────────────────────────┐                 │
│  │  WKWebView (HTML / CSS / JS UI)         │                │
│  │   window.pywebview.api.*  ──► Python    │                │
│  │   window.bus  ◄────────  evaluate_js()  │                │
│  └────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

**핵심 불변식:**
- 프로세스는 **1개** (Python). Tauri/Electron 의 sidecar 패턴과 다름.
- pywebview event loop 는 **메인 스레드**에서 돈다 (Cocoa 강제).
- 모든 블로킹 작업은 **워커 스레드** + `queue.Queue` (기존 패턴 그대로).
- 메인 스레드의 폴러가 큐를 비우고 `window.evaluate_js()` 로 JS 측에 push.

---

## 2. 디렉토리 구조 (제안)

```
GuruNote/
├── app_webview.py                # 새 엔트리포인트 (기존 app.py 와 공존)
├── gurunote/
│   ├── webui/                    # ← 신규 패키지
│   │   ├── __init__.py
│   │   ├── bridge.py             # class Api: pywebview js_api 클래스
│   │   ├── events.py             # 이벤트 버스 헬퍼 (Py → JS push 직렬화)
│   │   ├── pipeline_session.py   # PipelineWorker 래퍼 (job_id 추적)
│   │   └── static/
│   │       ├── index.html        # 단일 SPA shell (모든 화면이 라우팅됨)
│   │       ├── css/
│   │       │   ├── tokens.css    # CSS variables (DESIGN_TOKENS.md 출처)
│   │       │   ├── base.css      # reset, typography
│   │       │   ├── components.css # button, card, chip, input
│   │       │   └── screens/
│   │       │       ├── main.css
│   │       │       ├── history.css
│   │       │       ├── settings.css
│   │       │       └── note_editor.css
│   │       └── js/
│   │           ├── bus.js        # EventTarget 기반 이벤트 버스
│   │           ├── api.js        # window.pywebview.api 래퍼 (await/Promise 보정)
│   │           ├── router.js     # 단순 hash router
│   │           ├── app.js        # 진입점, DOM ready 후 router 시작
│   │           └── screens/
│   │               ├── main.js
│   │               ├── history.js
│   │               ├── settings.js
│   │               └── note_editor.js
│   └── ... (기존 모듈 22개, 무수정)
├── gui.py                        # 기존 CTk UI (병존, 무수정)
└── app.py                        # 기존 엔트리 (병존, 무수정)
```

**파일 명명 규칙:**
- 기존 코드와의 충돌 방지를 위해 새 엔트리는 `app_webview.py` (기존 `app.py` 보존)
- 새 패키지는 `gurunote/webui/` 하위로 격리
- 정적 자원은 `static/` 하위 (PyInstaller bundle 기준 표준 위치)

---

## 3. Bridge API (Python ↔ JS 호출 계약)

`gurunote/webui/bridge.py` 의 `class Api` 가 pywebview 의 `js_api` 인자로 전달됨.
JS 에서는 `window.pywebview.api.<method_name>(...)` 으로 호출. pywebview 가
자동으로 메서드 이름을 그대로 노출 (snake_case 유지 권장 — Python 관습).

### 3.1 메서드 카탈로그

| 카테고리 | 메서드 | 인자 | 리턴 (에러는 예외 raise — § 3.2) | 동작 시간 |
|---|---|---|---|---|
| **파일 선택** | `pick_file()` | — | `{path: str}` 또는 `{cancelled: True}` | 즉시 (다이얼로그 동기) |
| **파이프라인** | `start_pipeline(source)` | `source: {kind: 'youtube'\|'local', value: str, engine: str, provider: str}` | `{job_id: str}` | 즉시 (워커 spawn 후 리턴) |
| | `stop_pipeline(job_id)` | `job_id: str` | `{ok: True}` | 즉시 (이벤트 set) |
| | `get_pipeline_status(job_id)` | `job_id: str` | `{stage: str, pct: float, status: 'running'\|'done'\|'error'\|'stopped'}` | 즉시 |
| **설정** | `get_settings()` | — | `{stt_engine, llm_provider, llm_model, openai_api_key_set, ...}` (env 키는 `_set: bool` 만 노출, 값 비공개) | 즉시 |
| | `save_settings(patch)` | `patch: dict` (변경 키만) | `{ok: True, written: int}` 또는 `{ok: False, error: str}` | 즉시 |
| | `test_connection(provider)` | `provider: str` | `{ok: bool, latency_ms: float, error?: str}` | 1~5초 (워커로 위임 권장) |
| **히스토리** | `list_history(limit?, offset?)` | optional | `{jobs: [{job_id, title, created_at, duration_sec, ...}], total: int}` | 즉시 |
| | `get_history_detail(job_id)` | `job_id: str` | `{markdown: str, meta: dict, log_excerpt?: str}` | 즉시 (디스크 read) |
| | `delete_history(job_id)` | `job_id: str` | `{ok: True}` | 즉시 |
| | `rebuild_index()` | — | `{job_id: str}` (긴 작업 → 워커, 진행률은 이벤트로) | 즉시 |
| **노트 편집** | `update_note(job_id, markdown)` | — | `{ok: True}` | 즉시 (디스크 write) |
| **내보내기** | `save_markdown(job_id, target_path?)` | optional path | `{path: str}` (path 없으면 다이얼로그 띄움) | 즉시 |
| | `save_pdf(job_id, target_path?)` | optional path | `{path: str}` 또는 `{ok: False, reason: 'pdf_unavailable', hint: str}` | 1~5초 |
| | `send_obsidian(job_id)` | — | `{path: str}` 또는 `{ok: False, reason: 'no_vault'\|'error', hint: str}` | 즉시 |
| | `send_notion(job_id)` | — | `{job_id: str}` (긴 작업 → 워커, 결과는 이벤트로) | 즉시 |
| **앱 정보** | `get_app_info()` | — | `{version, platform, hardware: {is_apple_silicon, ram_gb}, paths: {history_dir, ...}}` | 즉시 |
| | `check_update()` | — | `{current, latest, update_available: bool, notes?: str}` | 1~3초 |
| **다이얼로그** | `show_message(title, body, kind?)` | `kind: 'info'\|'warning'\|'error'` | `{ok: True}` | 즉시 |

**원칙:**
- **즉시 리턴** 가능한 메서드는 동기 호출 + 결과 즉시 리턴
- **긴 작업**(파이프라인, 인덱스 빌드, Notion 전송)은 워커 spawn → `job_id` 리턴 → 이벤트로 진행/결과 통보
- 메서드 이름은 snake_case (Python 관습 유지). JS 측에서 `window.pywebview.api.start_pipeline(...)` 그대로 호출.

### 3.2 에러 처리 — **확정**

**성공 시**: 메서드는 JSON-직렬화 가능한 dict(또는 없을 때 `None`)를 그대로
리턴. 봉투 없음.

**실패 시**: Python 측에서 일반 `Exception` / `ValueError` / `RuntimeError`
을 `raise`. pywebview 의 JS bridge 가 이를 자동으로 **Promise reject** 로
전달하므로 JS 쪽에서는 `await / try-catch` 패턴이 그대로 먹힘.

```python
# Python — bridge method
def start_pipeline(self, source: dict) -> dict:
    if not is_probably_youtube_url(source["value"]):
        raise RuntimeError("INVALID_URL:유튜브 URL 형식이 아닙니다.")
    # ... on success
    return {"job_id": session.job_id}
```

```js
// JS — caller
try {
  const { job_id } = await window.pywebview.api.start_pipeline(source);
  // success branch
} catch (e) {
  // e is a plain Error; e.message is the original Python exception string.
  toast(humanizeError(e), "error");
}
```

**구조화 에러 코드**: `RuntimeError` 메시지는 `<CODE>:<detail>` 관례를 따름.
JS 쪽 `humanizeError()` 가 code 로 분기해 사용자 친화 문구로 변환.

현재 사용 중인 코드:

| CODE | 발생 | 사용자에게 보여지는 문구 |
|---|---|---|
| `INVALID_URL` | youtube 변별 실패 | "유튜브 URL 형식이 아닙니다." |
| `INVALID_LOCAL_FILE` | 파일 없음 / 지원 확장자 아님 | "지원되지 않는 파일입니다: {path}" |
| `API_KEY_MISSING:<ENV>` | LLM provider 환경변수 부재 | "API 키가 설정되지 않았습니다: {ENV}. 설정에서 입력하세요." |
| `NO_ACTIVE_SESSION` | `stop_pipeline(job_id)` 에 해당 세션 없음 | "실행 중인 작업이 없습니다." |

---

## 4. 이벤트 버스 (Python → JS push)

### 4.1 채널 / 이벤트 이름

| Event | Payload | 설명 |
|---|---|---|
| `progress` | `{job_id, stage: 'audio'\|'stt'\|'translate'\|'summary'\|'assemble', pct: float}` | 5단계 진행률 |
| `log` | `{job_id, ts: str, line: str}` | 라인 단위 로그 |
| `stage_change` | `{job_id, stage: str, status: 'started'\|'completed'\|'failed'}` | 단계 전환 |
| `result` | `{job_id, ok: bool, markdown?: str, meta?: dict, error?: str}` | 파이프라인 종료 |
| `notion_progress` | `{job_id, page_id?: str, status: str}` | Notion 전송 진행 |
| `index_progress` | `{job_id, processed, total}` | semantic 인덱스 빌드 |
| `update_available` | `{current, latest, notes}` | 업데이트 감지 (자동 polling) |

### 4.2 JS 측 패턴

`gurunote/webui/static/js/bus.js` (의사 코드):

```js
// EventTarget 표준 사용 (외부 의존성 0)
window.bus = new EventTarget();

// 백엔드가 호출하는 단일 진입점
window.__emit = function (eventName, payload) {
  window.bus.dispatchEvent(
    new CustomEvent(eventName, { detail: payload })
  );
};

// 사용처 (예: main.js)
window.bus.addEventListener("progress", (e) => {
  const { job_id, stage, pct } = e.detail;
  document.querySelector("#progress-bar").style.width = `${pct * 100}%`;
});
```

### 4.3 Python 측 push

Phase 1-B 에서 별도 `events.py` 를 만들지 않고 `PipelineSession._emit()`
메서드에 통합. 구현은 § 5.1 참조.

```python
# 요약 (session.py)
def _emit(self, event: str, payload: dict) -> None:
    js_event = json.dumps(event)
    js_payload = json.dumps(payload, ensure_ascii=False, default=str)
    self.window.evaluate_js(f"window.__emit({js_event}, {js_payload})")
```

Phase 2+ 에서 여러 세션 타입이 추가되면 (예: NotionSyncSession) 공통
`emit()` 함수로 리팩토링 예정.

### 4.4 폴링 주기

**100ms** — `gui.py:4012` 의 `self.after(100, self._poll_worker)` 와 동일.
`PipelineSession._schedule_poll()` 이 `threading.Timer(0.1, self._poll)` 로
재진입.

### 4.5 로그 이벤트 배칭

기본은 **per-line** `log` 이벤트. 한 tick 에서 `msg_queue` 에 쌓인 라인이
**50 개 이상**이면 단일 `log_batch` 이벤트로 묶어서 전송.

```python
# session.py 의 실제 구현
lines = []
while not self.worker.msg_queue.empty():
    lines.append(self.worker.msg_queue.get_nowait())
if len(lines) >= 50:
    self._emit("log_batch", {"lines": lines})
else:
    for line in lines:
        self._emit("log", {"line": line})
```

이유: 평상시(초당 수 건) per-line 이 단순하고 UI 즉시성 좋음. WhisperX 첫
실행 시 HuggingFace 다운로드 tqdm 이 수십~수백 라인을 버스트로 쏟아낼 때만
배칭해서 `evaluate_js` 오버헤드 컷.

JS 쪽은 두 이벤트 모두 구독해 동일한 `appendLogLine()` 을 호출.

---

## 5. 스레드 / 큐 모델

### 5.1 `PipelineSession` — 실제 구현 요약

**파일**: `gurunote/webui/session.py`

**책임**:
- `gui.PipelineWorker` 한 개 소유 (지연 import — `gui` 모듈 부작용 회피)
- 100 ms 주기 `threading.Timer` 폴러
- 3 queue(msg / progress / result) 드레인 후 JS 이벤트 emit
- `result` 받으면 `_ACTIVE` 레지스트리에서 제거 + 폴링 종료

**레지스트리**:
```python
_ACTIVE: dict[str, PipelineSession] = {}   # job_id → session
```

`Bridge.stop_pipeline(job_id)` 가 이 dict 로 조회.

**이벤트 emit shape (최종):**

| 이벤트 | payload | 메모 |
|---|---|---|
| `progress` | `{job_id, pct}` | `pct` ∈ [0.0, 1.0] |
| `log` | `{line}` | 50 미만일 때 |
| `log_batch` | `{lines}` | 50 이상일 때 |
| `result` | `{job_id, ok, video_title, full_md, full_html, summary_md}` (ok=False 면 `error` 포함) | `full_html` = Python markdown.markdown(…, extensions=['extra']) |

**evaluate_js 호출**:

```python
def _emit(self, event, payload):
    js_event = json.dumps(event)
    js_payload = json.dumps(payload, ensure_ascii=False, default=str)
    self.window.evaluate_js(f"window.__emit({js_event}, {js_payload})")
```

- `default=str` 로 Python 객체(예: `Path`, `datetime`) 을 안전하게 문자열화.
- `ensure_ascii=False` 로 한글 로그 라인 직렬화 보존.
- 예외 catch — 윈도우 닫힘 등.

**결과 정규화 (`_normalize_result`)**:

PipelineWorker 의 raw result 는 `audio` (AudioMeta 객체), `transcript`
(Transcript dataclass) 등 Python 객체를 포함. JS 로 보내려면 pure dict
로 변환 필요:
- `video_title` = `result["audio"].video_title`
- `full_html` = `markdown.markdown(result["full_md"], extensions=["extra"])`
- transcript segments 는 Phase 1-B 범위 밖 (다음 페이즈에서 렌더 추가)

### 5.2 thread safety 주의

- `pywebview` 의 `window.evaluate_js()` 는 내부적으로 메인 스레드에 dispatch
  되므로 워커에서 직접 호출해도 안전 (큐로 우회할 필요 없음).
  단, 호출 횟수가 잦으면(>10/sec) 디스패치 오버헤드 누적.
- **권장**: 워커는 큐에만 쓰고, 메인 스레드 폴러가 batch 로 evaluate_js 호출.
- `queue.Queue` 는 thread-safe.

---

## 6. 네이티브 기능 매핑

| 기능 | CTk 시절 (gui.py) | WebView UI (이번 설계) |
|---|---|---|
| **파일 열기 다이얼로그** | `tkinter.filedialog.askopenfilename(...)` | `window.create_file_dialog(webview.OPEN_DIALOG, file_types=("Audio/Video", "*.mp3 *.mp4 *.wav *.m4a *.webm"))` — Bridge `pick_file()` 메서드가 래핑 |
| **저장 다이얼로그** | `tkinter.filedialog.asksaveasfilename(...)` | `window.create_file_dialog(webview.SAVE_DIALOG, save_filename="...")` |
| **드래그앤드롭** | (미구현) | HTML5 `dragover` + `drop` 이벤트, `event.dataTransfer.files[i].pywebviewFullPath` 사용. **Vue Sortable / draggable 류 금지** (TECH_CHOICE § 4.1) |
| **클립보드** | `_install_clipboard_shortcuts` (gui.py:2851) — Tk 우회 | 표준 JS Clipboard API (`navigator.clipboard.writeText(...)`). Cmd/Ctrl+C/V 자동 동작 → CTk 우회 코드 폐기 |
| **메시지 박스** | `tkinter.messagebox.showwarning/.showerror` | Bridge `show_message()` → 내부에서 HTML 모달 또는 `window.create_confirmation_dialog()` |
| **앱 아이콘** | `gurunote.app_icon.get_app_icon_path()` → CTk 윈도우 아이콘 | pywebview `webview.create_window(..., icon=...)` 인자에 동일 path 사용 |
| **윈도우 close 처리** | `_on_closing` 에서 dirty check | pywebview `window.events.closing` (sync, return False 로 close 취소 가능) |
| **메뉴바** | (없음) | 필요시 `webview.menu.Menu` (네이티브 macOS 메뉴) — Phase 후반 평가 |

---

## 7. 화면 라우팅 (단일 SPA)

**모든 화면은 같은 윈도우 내 hash routing.** Multi-window 회피.

| URL hash | 화면 | 대응 (CTk 시절) |
|---|---|---|
| `#/` 또는 `#/main` | 메인 (생성) | `GuruNoteApp._build_main` |
| `#/history` | 히스토리 그리드 | `HistoryDialog` |
| `#/history/:job_id` | 히스토리 상세 | (CTk 에선 별도 dialog) |
| `#/note/:job_id` | 노트 편집기 | `NoteEditorDialog` |
| `#/settings` | 설정 | `SettingsDialog` |
| `#/dashboard` | 대시보드 | `DashboardDialog` |

**라우팅 라이브러리 없음.** `window.addEventListener("hashchange", ...)` 으로
직접 처리. 화면 5개에 라우터 라이브러리 도입할 가치 없음.

---

## 8. gui.py 와의 공존 (마이그레이션 기간)

**원칙: 양쪽이 같은 `gurunote/*` 모듈을 공유. 절대 fork 하지 않음.**

- 사용자는 `python app.py` (CTk) 또는 `python app_webview.py` (WebView) 중
  선택해서 실행
- `requirements.txt` 는 양쪽 의존성 모두 포함 (pywebview + customtkinter)
- 패키지 빌드 시점에 어느 쪽을 기본 엔트리로 할지는 **§ 9.2** 의 Open Question

**기존 코드 무수정 보장:**
- `gui.py`, `app.py`, `gurunote/*` 모든 파일 수정 금지 (가드레일)
- 새 코드는 모두 `gurunote/webui/`, `app_webview.py`, `docs/webview-ui/` 하위
- 기존 모듈에 새 메서드 추가가 필요한 상황이 발생하면 **즉시 멈추고
  사용자 결정** (HANDOFF_MORNING.md 에 기록)

---

## 9. Open Questions (Phase 1-B 이후 결정)

### 9.1 Bridge 응답 봉투 형식 — ✅ **확정** (Phase 1-B)

§ 3.2 참조. 성공 시 데이터 dict 그대로, 실패 시 Python 예외 raise →
pywebview 가 JS Promise reject 로 자동 전달. 구조화 에러 코드
`<CODE>:<detail>` 관례.

결정 근거:
- pywebview 의 기본 메커니즘을 그대로 활용 → 봉투 커스텀 코드 0
- JS 쪽 `await / try-catch` 가 자연스러움
- Python 쪽도 일반 예외 패턴 유지, 방어 코드 최소화

영향 범위: 이미 `start_pipeline` / `stop_pipeline` / `get_pipeline_status`
에 반영됨. Phase 2+ 신규 메서드도 동일 규칙 적용.

### 9.2 패키지 엔트리 결정

WebView UI 가 기능 parity 도달 후:
- Inno Setup / pkgbuild 의 기본 실행 명령을 `app.py` → `app_webview.py` 로 교체할지
- 두 엔트리 모두 패키징해서 사용자 선택 옵션으로 둘지
- `app.py` 자체를 `app_webview.py` 로 교체하고 CTk 엔트리는 제거할지

### 9.3 React/Vue/Svelte 도입 시점

화면 5개 중 상태 복잡도(특히 Settings 의 provider grid + Note Editor
dirty check) 가 임계 넘을 때 재평가. Phase 4 또는 Phase 5 에서 판단.

### 9.4 단축키 / 키보드 네비게이션

CTk 시절의 `_install_clipboard_shortcuts` 외에 다른 단축키가 있는지 확인 필요:
- ⌘S 저장 (NoteEditor)
- ⌘W 윈도우 닫기
- 검색바 포커스 (⌘F?)
브라우저 표준 동작이 GuruNote 의도와 충돌할 가능성 있음 (예: ⌘W 가 윈도우 close).

---

## Appendix A — 최소 동작 코드 (참고용)

```python
# app_webview.py — 가장 단순한 형태
import webview
from gurunote.webui.bridge import Api

if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        title="GuruNote",
        url="gurunote/webui/static/index.html",
        js_api=api,
        width=1280,
        height=820,
        min_size=(960, 600),
    )
    api.bind_window(window)  # bridge 가 evaluate_js 호출하려면 window 필요
    webview.start()  # 메인 스레드 블록. 모든 워커는 webview 시작 후 spawn.
```

```python
# gurunote/webui/bridge.py 골격
class Api:
    def __init__(self):
        self._window = None  # bind_window 로 주입

    def bind_window(self, window):
        self._window = window

    def pick_file(self) -> dict:
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=("Audio/Video (*.mp3 *.mp4 *.wav *.m4a *.webm)",),
        )
        if not result:
            return {"cancelled": True}
        return {"path": result[0]}

    def start_pipeline(self, source: dict) -> dict:
        from gurunote.webui.pipeline_session import PipelineSession
        session = PipelineSession(self._window, source)
        session.start()
        return {"job_id": session.job_id}

    # ... 나머지 메서드는 NotImplementedError 또는 stub
```
