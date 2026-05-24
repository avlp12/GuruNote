# GuruNote 역사 — 시간순

> 2026-04-11 첫 commit ~ 2026-05-24 v1.0.0.0 선언 + main 통합. 통합 main 트리 412 commit + archive/main-pre-cli 211 commit + 183 test 통과. 1차 사료는 `docs/wip/session_history_digest.md` (Claude Code 세션 18개, 4/19~5/24) + git log + README/CHANGELOG. **Phase 0 (4/11~18) 일부는 본인 기억 기반 2차 사료** — 본 문서에서 명시.

## 0. 시작 (2026-04-11, 2차 사료)

### PRD — 본인 메모

해외 IT/AI **구루(Guru)** 인사이트(Jensen Huang, Sam Altman 등)가 매일 쏟아지는데 한국어로 정리된 자료는 늦거나 부정확. 구루 영상/팟캐스트를 한국어 노트로 자동 정리하는 데스크톱 앱을 만든다.

- **이름 유래**: 구루들의 인사이트 노트
- **초기 스택**: Streamlit + yt-dlp + AssemblyAI + OpenAI/Anthropic
- **프롬프트 4원칙**:
  1. GuruNote 수석 에디터 페르소나
  2. 화자 실명 추론
  3. 전문 용어 영문 병기
  4. 구어체 다듬기
- **첫 commit 사고**: `1079431` push 시 GitHub 403 권한 catch — 본인 catch 후 해결

### 첫 commit 흐름

```
4bcbee6  04-11 07:42  Initial commit
1079431  04-11 22:55  Step 1 scaffolding: requirements, env, audio download UI
4ecbf77  04-11 23:10  full 5-step pipeline + VibeVoice-ASR
ab86b9e  04-12 08:46  Codex review (hotwords, token budget, env mutation)
30459d9  04-12        v0.1.0 README + CHANGELOG
5584096  04-12        Gemini review hardening
830cf90  04-12        CustomTkinter desktop GUI (Streamlit 대체)
```

## 1. STT 엔진 여정 (4/11~v0.6)

| 시기 | 엔진 | 사건 |
|------|-----|------|
| 4/11 v0.1.0 | **VibeVoice-ASR** | "적극 도입" — 5-step 파이프라인 primary STT |
| ~ v0.3 | VibeVoice + AssemblyAI fallback | RTX5090 32GB **OOM (32분 처리)** catch |
| **v0.4.0** | **WhisperX 전면교체** | NVIDIA GPU 정합 (faster-whisper + diarization) |
| **v0.6.0** | **mlx-whisper 합류** | Mac MLX (Apple Silicon GPU) 추가 |
| 5/24 (현재) | mlx-whisper (Mac) + WhisperX (NVIDIA) + pyannote community-1 | **AssemblyAI 완전 제거 = 완전 로컬** |

**VibeVoice / Nemotron Omni 통합 모델 평가** (시점 기록 부재 — 본인 기억 2차 사료):
- 한국어 ASR 정확도 / 로컬 실행 / 화자 분리 분리성 catch 부족 → 기각
- 재평가 예정: **2026-10** (Appendix B catch)

## 2. GUI 여정 (Streamlit → CustomTkinter → PySide6 폐기 → pywebview + React)

| 시기 | GUI | 사건 |
|------|-----|------|
| v0.1.0 | Streamlit | 초기 5-step UI |
| **v0.1.1** (PR #4) | **CustomTkinter** | "백엔드 직접 호출, Tauri는 오버엔지니어링" — PR #4 자료 |
| 4/19~20 | **PySide6 + PyWebView 시도** | `feat/webview-ui` 브랜치, "경로 C-1: PyWebView + HTML/CSS/JS + gurunote/* 로직 그대로 재사용" (4/19 16:05 본인 결정) |
| 4/20 14:43 | (계속) | "Phase 1-B MVP 완전 성공. end-to-end 검증 완료" |
| 4/20 15:11 | (계속) | PR #107 (PyWebView UI Phase 1-B) draft |
| 4/27 07:32 | **PySide6 폐기 → pywebview + React 신축** | "Phase 2B-0: 신축 baseline 준비 (미커밋 폐기 + Phase 1-C vanilla 폐기)" — vanilla→React 전환 동기 |
| 4/27 ~ 5/9 | Phase 2B-1 ~ 2B-6d | React 신축 시리즈 (Sidebar/MainScreen/HistoryScreen/EditorScreen/DashboardScreen/SettingsScreen) |
| 현재 | pywebview + React + Material 3 | gurunote/webui/ |

**GUI 기술 여러 번 재고** (Python GUI ↔ 웹 GUI 왕복) — 1년에 4번 전환 (Streamlit / CustomTkinter / PySide6 / pywebview+React).

## 3. 정체성 진화

| 시기 | 정체성 | 사료 |
|------|--------|-----|
| 4/11 PRD | **"IT/AI 구루 요약 앱"** | PRD 본인 메모 (2차) |
| 시점 부재 | **"24/7 지식 증류기 + Obsidian"** | WORK_ORDER (시점 기록 부재, 본인 기억 2차) |
| 5/24 (현재) | **"모델 비의존 한국어 지식 정리"** | Phase 5 통합 후 본인 결정 — STT 재분할 + char_limit이 모델 capability 의존 부재 path catch |

## 4. Phase 시간순 (UI Phase 0~2B + 백엔드 품질 Phase 1~5)

### Phase 0 — v0.1.0 ~ v0.8.0.6 (4/11~19, 2차 사료 일부)

| 시기 | 일/commit | 사건 |
|------|----------|------|
| 4/11 | 4bcbee6 | Initial commit |
| 4/11 22:55 | 1079431 | Step 1 scaffolding (yt-dlp + audio download UI) |
| 4/11 23:10 | 4ecbf77 | 5-step pipeline + VibeVoice-ASR |
| 4/12 | 830cf90 (PR #4) | CustomTkinter 추가 (Streamlit 대체) |
| 4/13~17 | 다수 PR | settings dialog (#5), local file (#6), openai_compatible LLM (#8), update workflow (#9), YouTube metadata (#11), 모델 갱신 (#12), GUI redesign (#14) |
| 4/19 | 9b6c621 | v0.8.0.6 macOS SSL 인증서 fix (certifi context) — **main 브랜치 마지막 v0.x** |

### Phase 1 (UI Phase 1-A/B/C) — feat/webview-ui (4/19~4/22)

| 시기 | commit/사건 | 사료 (1차 — session_history_digest) |
|------|------------|----------------------------------|
| 4/19 13:59 | 본인: "이 프로젝트를 https://github.com/avlp12/GuruNote 에 커밋/PR 할 예정" | 세션 1 첫 메시지 |
| 4/19 15:50 | 본인: "Phase 2 시작하기 전에 멈춰줘" | 본인 신중함 |
| 4/19 15:53 | 본인: "PyWebView 현실적 제약도 같이 조사" | webview 채택 동기 |
| 4/19 16:05 | 본인: **"경로 C-1 확정. PyWebView + HTML/CSS/JS + gurunote/* 로직 그대로 재사용"** | Phase 1 결정 |
| 4/20 11:03 | 본인: "Phase 1-B 진입 전 외부 11 commit 정체 확인 먼저" | 본인 신중함 |
| 4/20 14:43 | 본인: **"Phase 1-B MVP 완전 성공. end-to-end 검증 완료"** | Phase 1-B 완료 |
| 4/20 15:11 | 본인: PR #107 작성 (PyWebView UI Phase 1-B draft) | |
| 4/22 05:59 | 본인: "A. UI Commit 시작. 다만 Commit 2 (목록 view) 만. Commit 3 (detail) 은 오늘 안 함" | Phase 2A Commit 2 시작 (Tailwind redesign 첫 시도) |
| 4/23 02:33 | 본인: **"[Request interrupted by user for tool use] STOP. 진행 중단. 3번 (No) 선택"** | **Commit 2 aborted** ❗ |

### Phase 2A — Tailwind redesign 진입 (4/24~25)

| 시기 | commit/사건 | 사료 |
|------|------------|-----|
| 4/24 | `cedae0e` | chore: initialize Phase 2A (Tailwind redesign branch) |
| 4/24 | docs/legacy/design/KICKOFF_PHASE_2A.md | Decision 1: License 전환 (MIT → Elastic 2.0), Decision 2~4 디자인 자산 |
| 4/25 00:33 | 본인: "Commit 2 시작. 옵션 C (Tailwind CDN + 기본 layout + 생성 화면 idle)" | Commit 2 재시작 |
| 4/25 01:24 ~ 13:01 | Commit 2 — Step 1 자산 / Step 2 Material 3 CSS / Step 3a~3c | |
| 4/25 13:13 | `4d7222f` | Phase 2A Commit 2: Material 3 sidebar + frameless titlebar + MainScreen idle |
| 4/25 **13:49** | 본인: **"Phase 2A — Commit 2 Revert + Commit 3a 준비"** | **Commit 2 Revert 결정** |
| 4/25 13:58 | 본인: "Commit 2 Revert 후속: 자산 영구 보존 위치 이동 + README + **archive push**" | `archive/commit-2-aborted` 브랜치 작성 |
| 4/25 14:11 | `31f59e3` | Phase 2A Commit 3a Step 3a-1: 자산 복원 + Babel 검증 |
| 4/25 | `5f8f1da`, `b1cd138` | Step 3a-2, Step 0 (어제 누락분 보강) |

### Phase 2B — React 신축 (4/27~5/2, 514 commits 절정)

| 시기 | commit/사건 |
|------|------------|
| 4/27 07:32 | `2160a66` Phase 2B-0: 신축 baseline 준비 (vanilla 폐기 + clean React entry) |
| 4/27 07:47 | `6376385` Phase 2B-1: Sidebar + App + 5 화면 placeholder |
| 4/27 08:16 | 본인: "Phase 2B-1 재시작: Sidebar 우리 코드로 신축 (cp 폐기)" |
| 4/27 08:38 | `598ead0` Phase 2B-2: MainScreen — 생성 화면 + 파이프라인 + 결과 4탭 |
| 4/27 10:41~12:38 | `0158942` 2B-3a HistoryScreen 카드 그리드 / 2B-3b 검색·필터 |
| 4/28 | `ebb8f2f` 2B-3c HistoryScreen 정렬+카운트 / `dbe3c79` 2B-3d Facet tree + Detail |
| 4/29~5/2 | 2B-4a EditorScreen / 2B-4b DashboardScreen / 2B-4c SettingsScreen (LLM/STT, Obsidian/Notion, 고급) |
| 5/2 | 2B-5a 라이브러리 wiring / 2B-5b Stale 라벨 / 2B-5b-2 EditorScreen 에러 + 복구 |
| 5/2~ | 2B-6a TopBar + breadcrumb / 2B-6b EditorScreen split / 2B-6b-2 Sidebar appbar / 2B-6c DashboardScreen 재구성 / 2B-6d ⌘K SearchPalette |

### Phase 2B-3-backend Layer 1~15 (5/9~11) — UI/문구 표기 fix

> Layer = **frontend + LLM prompt + 화자 다듬기** (UI 정책 자료). 백엔드 번역 본체 Phase 1~5보다 **선행**.

| 시기 | commit | Layer 사건 |
|------|--------|----------|
| 5/8 15:43 | 본인 세션 | "Phase 2B-3-backend Step 3b-2 보류 + 본질 진단 진입" — Layer 작업 진입 |
| 5/8 16:09 | 본인 세션 | Layer 1 fix 진입 |
| 5/9 00:58 | 본인 세션 | "본질 catch 정정 — 라이브러리 vs 모델 영역 분리" |
| 5/9 16:30 | `d9c5f0b` | Layer 1: pyannote max_speakers + embedding clustering |
| 5/9 18:31 | `1846098` | Layer 5+6: LLM hallucination cascading + STT noise filter |
| 5/9 23:27 | `c7e9e1a` | Layer 7: ResultPanel 4 tab DetailPanel + EditorScreen 통합 |
| 5/9 23:30 | `cf4a7bd` | Layer 8: 고유명사 한국어 표기법 일관성 |
| 5/9 23:39 | `c2da2d3` | **Layer 8 fix-up: Tiffany Janzen 표준 표기 (잰슨→잔젠)** ⭐ |
| 5/9 14:35 (세션) | 본인 사료 | **"티파니 잰슨이 아니라 티파니 잔젠 (Tiffany Janzen). 외국인 인명 표준 표기법에 따를 것"** — Layer 8 사용자 catch 시점 |
| 5/10 00:09 | `a512b12` | Layer 9: markdown transcript 가독성 정합 |
| 5/10 00:58 | `027f243` | Layer 13: 화자 표기 한국어 번역 + entity 영문 병기 명확화 |
| 5/10 01:59 | `12e1868` | Layer 13 fix-up #2: 화자 라벨 첫 등장 영문 병기 누락 fix |
| 5/10 19:01 | `d30c782` | Layer 11: Rule 11 한자/일본어 차단 + _SHARED_LANG_RULES |
| 5/10 20:27 | `ee8b616` | Layer 14: transcript line break 정규화 |
| 5/11 00:34 | `ece961e` | Layer 15: METADATA prompt _SHARED_LANG_RULES inline + title 정합 |
| 5/11 21:41 | `d7a726b` | Layer 15 fix-up #1: title hallucination 가이드라인 강화 |

### 백엔드 품질 Phase 1~5 (5/16~24) — 번역 본체

> Layer 시리즈 후 일주일 gap (5/12~15 정전 대비 catch). Layer = UI 정책, **본 Phase = 번역 LLM 본체 품질**.

| 시기 | commit | 사건 |
|------|--------|-----|
| 5/14 09:36 | (HANDOFF) | `HANDOFF_POWER_OUTAGE_2026-05-14.md` 작성 (정전 대비, HEAD 3f3f04d, stash 보존) |
| 5/16 01:00 | `c68aab8` | **Phase 1 Redesign: Index Mapping + json_schema strict + segment cap 15 + post-process** |
| 5/17 20:08 | `b447a11` | **Phase 4a-1: xgrammar selective disable + A-3 timeout dead code revert** |
| 5/18 19:00 | `cdbdc67` | **Phase 3: 한자/일본어 0건 후처리 (Sub-path A+B+C)** |
| 5/18 21:25 | `47c3448` | Phase 3 마무리: unit tests + 의존성 등록 |
| 5/19 23:27 | `22927fc` | **Phase 2 (B01) Step B: entity cache helper + unit test** |
| 5/19 23:47 | `f9c2da2` | **Phase 2 (B01) Step C: translate_transcript 통합 + Rule 12** |
| 5/20 08:20 (세션) | 본인 사료 | **"판카지 샤르마 회귀 진단 우선"** — B06 동기 catch |
| 5/20 16:25 | `2ed4701` | **B02: slow chunk wall-clock timeout (ThreadPoolExecutor wrap)** |
| 5/21 21:03 | `4a8f281` | **B06 (Phase 2B-3): entity_cache 디스크 + 외래어 표기법 + 표기 통일** |
| 5/22 00:08 | `8fdc2a8` | B06 verify 통과: 판카지 회귀 차단 + 캐시 적중 |
| 5/22 17:23 | `9afcc93` | B06 한계 2: canonicalize 미세 본문 변경 차단 |
| 5/22 17:26 | `988b4c1` | B02 한계 1: R1 padding fallback |
| 5/22 20:57 | `f58d5f2` | B06 보완 verify 통과 |
| 5/23 12:07 | `f314d6e` | B02 wall-clock timeout 수정 (ThreadPoolExecutor with 결함 fix) |
| 5/23 13:11 | `97855bd` | B02 R2: 즉시 padding → strict retry → fallback |
| 5/23 14:11 | `39652c6` | (가) 옵션 A prototype: 2-pass 분리 (자유 번역 → 정렬) |
| 5/23 16:01 | `7a397fa` | **(가) 2-pass 보강: A1 rule 충돌 해소 + A5 prefix strip** |
| 5/23 (later) | `6b94a49` | **(가) 화자 라벨 코드 부착: 식별 1회 + 결정론 부착** |
| 5/23 (later) | `8ecd276` | pyannote diarization 모델 변경: 3.1 → community-1 (speaker confusion 감소) |
| 5/23 23:42 | `599c94b` | 2-pass 빈 output 복구 시퀀스 (3단계 안전망) |
| 5/24 12:28 | `527d2ea` | **Phase 5: STT 의미 단위 재분할 + chunk size 자동 (재분할 토글)** |

### docs 정리 (5/24)

| 시기 | commit | 사건 |
|------|--------|-----|
| 5/24 | `4f2db79` | docs: 옛 UI 작업 문서 legacy로 정리 이동 (37 rename) |
| 5/24 | `373d5db` | docs: Phase 5 검증 산출물 보존 (prototype + 보고서) |
| 5/24 | `5c3c240` | docs: 18개 세션 사료화 (역사 1차 자료) |
| 5/24 | `41745e6` | docs: GuruNote 역사 기록 (통합 일지 + HISTORY/DECISIONS/DEBUGGING/CHANGELOG 첫 작성) |

### Phase 5 마무리 + v1.0.0.0 선언 + main 통합 (5/24 저녁)

| 시기 | commit | 사건 |
|------|--------|-----|
| 5/24 | `6dc9934` | **Phase 5 default on**: `GURUNOTE_SEGMENT_RESPLIT` + `GURUNOTE_TWO_PASS` 기본값 off → on. daily 검증 영상 2개 통과 — xKK5ze3FukQ (Boston Dynamics, 5.7 분) 96→49 segments / zNuOOMM20Tk (NVIDIA Podcast, 33.4 분) 586→294 segments. timeout 0, CJK 0, 화자 이름 정상 부착. 토글 off 안전망 유지 (`=0` 명시 시 기존 동작). 신규 백로그 B07 (D 재평가) + B08 (화자 bootstrap 한계). |
| 5/24 | `2971939` | **release: v1.0.0.0** — 버전 0.8.0.6 → 1.0.0.0 (7 곳 갱신: `__init__.py`, `gui.py` 사이드바, `package_desktop.py` Inno Setup + pkgbuild, `SettingsScreen.jsx` fallback, README "현재 버전", CHANGELOG entry). CLAUDE.md 체크리스트 5-file → 6-file (React UI fallback 추가). 신규 `run_webview.command` (React/PyWebView 진입점 wrapper). README 약 60% 재작성 — 진입점 `app_webview.py` 권장 + 옛 진입점 호환 표기, React/Mac/MLX 위주. backlog B09 (PipelineWorker 분리) + B10 (setup 스크립트 echo 갱신) 신규. test 183 passed. |
| 5/24 | (브랜치 작업) | **main 통합 — unrelated histories 처리**. 옛 main 트리 (root `4bcbee6`, HEAD `9b6c621` v0.8.0.6) 와 redesign 트리 (root `af50c2e`, HEAD `2971939` v1.0.0.0) 가 공통 조상 부재 사실 확인 (4/19 직후 웹 Claude → 로컬 CLI Claude Code 전환 시 별도 init 한 결과). 옛 main 211 commit 을 `archive/main-pre-cli` 로 origin 보존 → `git push origin main --force-with-lease` 로 redesign 트리를 main 으로 통일. origin/main: `9b6c621` → `2971939`. |

## 5. 현재 (2026-05-24 22시 GMT+9 기준, HEAD 2971939, v1.0.0.0)

### 코드 상태
- gurunote/ ~9100 line (llm.py 2700+ / stt_mlx.py 517 / stt.py 455 / updater.py 534 / 등)
- webui/ React 신축 (Phase 2B, 10 컴포넌트)
- tests/ 183 passed
- License: Elastic 2.0
- 통합 main 트리: 412 commit (root `af50c2e`)
- 보존: `archive/main-pre-cli` 211 commit (root `4bcbee6`, 옛 main v0.x 전체)

### 진입점 (v1.0.0.0)

| 진입점 | 위치 | 상태 |
|---|---|---|
| **React/PyWebView** (권장) | `app_webview.py`, `run_webview.command` | v1.0+ |
| **CustomTkinter** (호환 유지) | `gui.py`, `run_gui.command`, `run_desktop.{sh,bat}` | `PipelineWorker` 클래스 보유 — React UI 가 의존 (B09 분리 작업 백로그) |
| **Streamlit** (호환 유지) | `app.py`, `run_web.{sh,bat}` | 단독 사용 가능 |

### backlog 미해결

| ID | 상태 | 내용 |
|----|------|-----|
| B03 | not_started | Phase 1 fix-up #3 schema text leak — xgrammar 외부 의존, 신 버전 대기 |
| B04 | blocked | Phase 1 fix-up #2 tail attention drop — 정황 확인 필요 |
| B05 | blocked | Phase 4 capability profile — 모델 교체 결정 후 진입 (5/24 "모델 비의존" 방향으로 본 전제 우회) |
| B07 | not_started | D segment 단독 번역 재평가 — Phase 5 후속, 정합 낮은 영상에서 SHIFT 재발 시 |
| B08 | not_started | 화자 bootstrap 식별 한계 후속 — 5/24 영상1 5명 중 3명만 식별, 메타데이터 한계 |
| B09 | not_started | PipelineWorker 를 gui.py 에서 별도 모듈로 분리 — React 가 옛 CustomTkinter UI 파일에 의존하는 기술 부채 |
| B10 | not_started | setup.sh / setup.bat echo 갱신 — README v1.0 진입점과 일관성 |

## 6. 다음 — 본 문서 작성 시점 기준

- 역사 문서 주기적 갱신 (본 commit 이 첫 갱신 적용 사례).
- `docs/wip/daily_verify_phase5.py` / `verify_results/daily_phase5/` 운명 (커밋 / .gitignore / 삭제).
- GitHub release 태그 `v1.0.0.0` 생성 여부.
- B07/B08/B09/B10 각 결정.
- B03/B04/B05 각 결정.

---

**자료 한계 명시**:
- Phase 0 (4/11~18 첫 commit ~ v0.8.0.6) — 본인 메모/기억 2차 사료. session_history_digest 시작이 4/19.
- VibeVoice OOM 32분 / Nemotron Omni 평가 / 정체성 진화 시점 일부 — 본인 기억 2차 사료.
- License MIT → Elastic 전환 동기 — 본인 링크 대화 (DECISIONS.md 확장).
- main 트리 / redesign 트리 unrelated histories 사실 — 5/24 통합 시점에 사후 확인. 별도 init 가 정확히 어느 commit 인지는 기록 부재 (양쪽 모두 "Initial commit" 메시지, 4/11 같은 날, hash `4bcbee6` vs `af50c2e`). 본인 기억으로는 4/19 직후 로컬 CLI Claude Code 도입 시 환경 변경.
