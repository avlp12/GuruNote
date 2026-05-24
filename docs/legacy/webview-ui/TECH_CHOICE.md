# GuruNote WebView UI — 기술 스택 결정

**결정일:** 2026-04-20
**브랜치:** `feat/webview-ui` (from `main`)
**대체 대상:** 현재 `gui.py` 의 customtkinter 기반 UI

---

## 1. 결정 요약

GuruNote 의 UI 레이어를 **PyWebView + HTML/CSS/JS** 로 교체한다.
도메인 로직(`gurunote/*` 패키지)은 **한 줄도 수정하지 않고** 그대로 재사용한다.

```
[Browser-style UI]                  [Existing Python core]
HTML / CSS / JS  ←──── PyWebView ────→  PipelineWorker
                                         gurunote/audio
                                         gurunote/llm
                                         gurunote/stt, stt_mlx
                                         gurunote/history
                                         gurunote/exporter
                                         gurunote/obsidian
                                         gurunote/notion_sync
                                         ... 등 22개 모듈
```

---

## 2. 결정 근거

세 단계 검증을 거쳐 결정.

### 2.1 후보 경로

| 코드명 | 내용 | 평가 |
|---|---|---|
| **A** | CTk 유지, 핸드오프 패치 그대로 복붙 | 패치에 실제 버그(예: `ctk.CTkLabel(padx=...)` 인자 오류, segmented 클릭 시 시각 갱신 누락), 토큰 원칙 위반 → **기각** |
| **B** | CTk 유지, 패치 버그 수정 + 누락 상호작용 구현 + 토큰 준수 | 공수 3~5일, 도달 가능 품질은 HTML 원본의 70~75% — CTk 자체가 box-shadow / transition / gradient 미지원 → **기각** |
| **C-1** | **PyWebView + HTML/CSS/JS, gurunote/* 재사용** | 공수 1~1.5주, HTML 원본의 95%+ 도달 가능, Python 100% 유지 → **채택** |
| C-2 | PyWebView + FastAPI 내부 서버 + 프런트엔드 프레임워크 | C-1의 상위호환이지만 백엔드 1단 추가, 현재 단계엔 오버스펙 → 향후 옵션 |
| C-3 | Tauri + Python sidecar (FastAPI) | Rust 학습 + 이중 빌드 파이프라인 + WhisperX dylib 패키징 난도 → 비용 대비 이득 부족 → **기각** |
| C-4 | Electron + Python sidecar | Chromium 100MB 오버헤드 + WhisperX 모델 3GB 와 합쳐 번들 비대화, flat UI 에선 렌더 차이 미미 → **기각** |
| C-5 | FastAPI + 시스템 브라우저 | 데스크탑 앱 경험 상실 (Dock 없음, 윈도우 라이프사이클 불명확) → **기각** |

### 2.2 C-1 선정 핵심 근거

**기술적 적합성 (PyWebView 가 GuruNote 와 맞아떨어지는 지점):**

1. **메인 스레드 강제 (Cocoa 제약)**
   `webview.start()` 가 메인 스레드를 블록한다. 기존 GuruNote 의
   `PipelineWorker` 는 이미 `threading.Thread(daemon=True)` 위에서 돌고
   진행률은 `queue.Queue` 로 전달한다 (`gui.py:155–217`). PyWebView 의
   권장 패턴과 **정확히 일치** — 아키텍처 재설계 0.

2. **WhisperX 수 분 전사 처리**
   현재 CTk 의 `widget.after(200, self._poll_worker)` 폴링 (`gui.py:3219`)
   을 메인 스레드에서 `queue` 비우기 + `window.evaluate_js("bus.emit(...)")`
   로 1:1 대체. 폴링 주기는 그대로 200ms.

3. **네이티브 통합 — 필요한 기능 모두 커버**
   - 파일 다이얼로그: `window.create_file_dialog(OPEN_DIALOG, ...)` — 네이티브, 경로 튜플 리턴
   - 드래그앤드롭: `event.dataTransfer.files[0].pywebviewFullPath` — **실제 파일시스템 절대경로 제공** (브라우저 기본 API와 달리 path 노출). WhisperX 가 경로 기반이라 그대로 호환
   - 클립보드: JS Clipboard API 표준 동작. CTk 전용 `_install_clipboard_shortcuts` (gui.py:2851) 폐기 가능

4. **macOS Apple Silicon 안정성**
   - 백엔드: `webview/platforms/cocoa.py` → PyObjC → WKWebView (네이티브 ARM64)
   - Python.org framework 빌드 (`/Library/Frameworks/Python.framework/...`) 사용 시 venv 키보드 포커스 이슈 회피 (FAQ 명시)
   - WKWebView 인쇄 미지원 한계 → GuruNote 는 `gurunote.pdf_export` 가 서버사이드 PDF 렌더링이라 무관

5. **Tauri/Electron 대비 우위**
   - **Python 100%** — Rust 학습 / 두 빌드 파이프라인 불필요
   - **WhisperX in-process** — sidecar IPC 오버헤드 0
   - **macOS 렌더 동일** — Tauri 도 WKWebView 사용. Electron 만 Chromium 번들이지만 Google Workspace 풍 flat UI 에선 차이 체감 어려움
   - **번들 크기**: PyWebView ~5MB vs Electron ~120MB (WhisperX 모델 ~3GB 와 합쳐도 의미 있는 차이)

### 2.3 도메인 로직 분리도 검증

`gui.py` 가 import 하는 `gurunote.*` 모듈 (gui.py:30–98):

```
audio, exporter, llm, progress_tee, settings, history, hardware,
stt, stt_mlx, thumbnails, pdf_export, pdf_installer, obsidian,
notion_sync, search, stats, semantic, nav_tree, ui_state, types,
updater, app_icon, log_redirect
```

**모든 도메인 로직이 `gurunote/` 패키지에 분리되어 있음.** `gui.py` 는
순수 UI 레이어 + `PipelineWorker` 클래스만 보유. PipelineWorker 도
CTk 의존성 0 (큐 기반). → 새 UI 가 동일한 모듈을 그대로 import 하면 됨.

---

## 3. 기술 핀(Pin) & 의존성

### 3.1 PyWebView 버전

```
pywebview>=4.4,<5.0
```

- 4.x 라인은 2~3년 누적 안정화. WKWebView/WebView2 백엔드 표준화.
- 5.x 가 출시될 때까지 4.x 메이저 라인 고정.
- macOS 최소 요구: 10.13+ (WKWebView). GuruNote 의 다른 의존성(MLX) 이
  Apple Silicon 만 정식 지원하므로 실질 macOS 11+.

### 3.2 프런트엔드 빌드 체인

**MVP 단계: 빌드 체인 없음.**

- HTML, CSS, JS 를 손으로 작성 (vanilla)
- 의존성 0, npm 0, webpack 0
- 이유: 현재 디자인 핸드오프(`docs/handoff/GuruNote Redesign.html`) 가
  이미 단일 HTML 파일에 인라인 CSS/JS 로 작성되어 있음. 그대로 split 하면
  됨. React/Vue 도입은 화면 수가 5+ 로 늘고 상태 관리 복잡도가 임계 넘을
  때 재평가.

**향후 전환 옵션 (확정 아님):**
- 화면 7개 + 폼 상태가 복잡해지면 Vite + Svelte 검토
- 빌드 산출물을 `gurunote/webui/static/dist/` 에 배치, Python 은 그대로 정적 파일 서빙

---

## 4. 기술 제약 (반드시 준수)

### 4.1 드래그앤드롭은 HTML5 native 만 사용

**금지 라이브러리:** Vue Draggable, Sortable.js, react-dnd 등
**이유:** PyWebView 이슈 #311 — vue-draggable / sortable.js 가 PyWebView 에서
정상 동작하지 않음. 라이브러리들이 DataTransfer 객체를 자기네 추상화로
래핑하면서 PyWebView 가 주입하는 `pywebviewFullPath` 속성을 잃어버림.

**대신:** 표준 HTML5 drop event + `event.dataTransfer.files[i].pywebviewFullPath`
직접 사용. 디바운스가 필요하면 `lodash.debounce` 같은 micro 유틸만 추가.

### 4.2 메인 스레드 블로킹 금지

**`window.pywebview.api.*` 메서드는 즉시 리턴해야 함.**
- 파이프라인 등 긴 작업은 `start_pipeline()` 호출 시 `threading.Thread` 즉시 spawn 후 `job_id` 만 리턴
- 진행률은 백엔드가 `window.evaluate_js(...)` 로 푸시
- 동기 결과가 필요한 빠른 작업(예: `get_settings()`) 만 직접 리턴

**예외:** pywebview 의 `before_show` / `before_load` 이벤트 핸들러는 동기.
이건 안 쓰면 됨.

### 4.3 토큰 일원화

**모든 색/간격/반경은 `gurunote/webui/static/css/tokens.css` 의
CSS variables 에서만 가져온다.**

- 토큰 출처: `docs/handoff/DESIGN_TOKENS.md`
- 인라인 hex 리터럴 금지 (디자인 핸드오프 §2.1 정신 계승)
- 새 토큰 필요 시 tokens.css 에 먼저 추가 후 사용

### 4.4 클립보드는 표준 JS API

CTk 시절의 `_install_clipboard_shortcuts` (gui.py:2851) 같은 Tk 우회
코드는 폐기. 브라우저 기본 Cmd/Ctrl+C/V 가 동작하므로 별도 구현 불필요.

---

## 5. 저장소 구조 (브랜치 전략)

```
main                             ← 안정 버전 (CTk UI, 0.7.2.1)
  │
  ├─ redesign/handoff-phase1     ← CTk + light theme phase 1 (보존, 미머지)
  │     · 4c33d15 feat(ui): apply phase 1 - design tokens & theme foundation
  │     · 66ec60a docs: add design handoff reference (phase 1-5)
  │
  └─ feat/webview-ui             ← (현재 활성) PyWebView UI 개발 라인
        · 1659231 docs: add design handoff reference (phase 1-5)   [cherry-pick]
        · ... 이후 추가
```

**선택 근거:**

- `feat/webview-ui` 는 `main` 에서 분기. CTk Phase 1 작업 (`4c33d15`) 은
  PyWebView 에서 재사용 가치가 없어 의도적으로 누락.
- 핸드오프 레퍼런스 문서 (`docs/handoff/`) 는 양쪽 브랜치 모두에서 유용
  하므로 docs 커밋만 cherry-pick.
- `redesign/handoff-phase1` 은 **삭제 안 함**. 향후 PyWebView 전환이
  실패하거나 CTk 폴백이 필요하면 머지 또는 재참조 가능.

**머지 정책 (예정):**
- `feat/webview-ui` 가 기능 parity 도달 시 PR → `main` 머지
- 머지 시 기존 `gui.py` 와 customtkinter 의존성을 어떻게 할지는 별도 결정
  (Open Question § 6 참고)

---

## 6. Open Questions (Phase 1-B 이후 결정)

1. **`gui.py` 와 customtkinter 제거 시점**
   - 옵션 A: WebView UI 가 기능 parity 도달 시 즉시 제거
   - 옵션 B: 1~2 릴리스 동안 `--legacy-ui` 플래그로 두 UI 공존 후 제거
   - 옵션 C: 영구 공존 (CTk 를 fallback / accessibility 옵션으로)
   - 결정 기준: 사용자 피드백, 패키지 사이즈 영향, 유지보수 비용

2. **프런트엔드 프레임워크 도입 시점**
   - 화면 5개 (Main / History / Settings / Note Editor / Dashboard) 중
     상태 복잡도가 임계 넘을 때 Vite + Svelte 검토
   - 시점: Phase 4 (Settings) 또는 Phase 5 (Note Editor) 작업 중 평가

3. **패키징 (`scripts/package_desktop.py`) 변경 범위**
   - PyInstaller spec 에 `gurunote/webui/static/` 포함 추가
   - Inno Setup / pkgbuild 에 webview 런타임 의존성 명시 (실제로 추가 작업
     필요한지는 PyInstaller hook 확인 후 판단)
   - 시점: Phase 1-B 또는 Phase 2 끝에 검증

4. **버전 bump 정책**
   - WebView UI 전환은 MAJOR 또는 MINOR? CLAUDE.md 정책상 1.0.0 전까지
     MINOR 로 대체이므로 0.8.0.0 (MINOR) 가 자연스러움
   - Phase 5 끝에 단일 bump (CLAUDE.md 메모리 참조)

---

## 7. 비-목표 (Out of Scope)

- 다크 모드 토글 (Phase 1 에선 라이트만)
- 모바일 / 반응형 (1280+ 데스크탑 고정)
- 오프라인 PWA 모드 (PyWebView 안에서 의미 없음)
- 다중 윈도우 (Settings/History 도 같은 윈도우 내 SPA 라우팅)
- 실시간 협업 (단일 사용자 데스크탑 앱)

---

## Sources

웹 검색 (2026-04-19~20):

- [pywebview macOS Implementation — DeepWiki](https://deepwiki.com/r0x0r/pywebview/4.3-macos-implementation)
- [pywebview FAQ](https://pywebview.idepy.com/en/guide/faq)
- [Issue #1251 — Why must pywebview run on a main thread?](https://github.com/r0x0r/pywebview/issues/1251)
- [Issue #627 — Stop freezing Main thread](https://github.com/r0x0r/pywebview/issues/627)
- [Issue #877 — Drag'n'drop](https://github.com/r0x0r/pywebview/issues/877)
- [Issue #311 — Unable to drag and drop with vue-draggable / sortable.js](https://github.com/r0x0r/pywebview/issues/311)
- [pywebview API reference](https://pywebview.flowrl.com/api/)
- [webview-drops — pywebview drag-drop reference example](https://github.com/CakeBrewery/webview-drops)
- [NiceGUI native file drag-and-drop via pywebview](https://gist.github.com/NewComer00/0e88e60b571aeeaf1bb54aec3bae5be6)

Tauri / Electron 비교 (사용 안 함, 결정 근거용):

- [Tauri v2 — Embedding External Binaries (sidecar)](https://v2.tauri.app/develop/sidecar/)
- [pytauri — Tauri binding for Python through PyO3](https://github.com/pytauri/pytauri)
- [tauri-plugin-python (RustPython/PyO3)](https://github.com/marcomq/tauri-plugin-python)
- [example-tauri-v2-python-server-sidecar](https://github.com/dieharders/example-tauri-v2-python-server-sidecar)
