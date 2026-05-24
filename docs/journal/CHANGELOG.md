# GuruNote 변경 기록 (저장소 CHANGELOG + 백엔드 Phase 연계)

> 저장소 `CHANGELOG.md` (Keep a Changelog 형식)은 main 브랜치 v0.x 기준. 본 문서는 main(v0.x) + redesign/tailwind-v2 (Phase 2A/2B/백엔드 Phase 1~5) 통합. 백엔드 Phase는 main에 미머지 catch.

## main 브랜치 v0.x (PRD ~ v0.8.0.6)

### [0.1.0] - 2026-04-12

- 5-step 파이프라인 + VibeVoice-ASR primary STT (`4ecbf77`)
- Streamlit UI
- yt-dlp + AssemblyAI fallback + OpenAI/Anthropic

### [PR #4] - 2026-04-12

- **CustomTkinter desktop GUI** 추가 (Streamlit 대체) — "Tauri는 오버엔지니어링" 본인 결정

### [PR #5] - 2026-04-13

- in-app settings dialog (API 키 catch)

### [PR #6] - 2026-04-13

- 로컬 video/audio 파일 입력 catch

### [PR #8] - 2026-04-14

- **OpenAI-compatible local LLM** (qwen3.6 등) + in-app settings UX

### [PR #9] - 2026-04-15

- in-app + CLI update workflow (Codex review 후속)

### [PR #11] - 2026-04-16

- **YouTube metadata catch** (date, chapters, captions) LLM 컨텍스트 catch

### [PR #12] - 2026-04-16

- 기본 LLM 모델 갱신 (gpt-5.4, claude-sonnet-4-6)

### [PR #14] - 2026-04-17

- GUI redesign (sidebar + card layout + step indicators)

### [Unknown] - v0.4.0

- **WhisperX 전면 교체** (NVIDIA GPU 정합, VibeVoice-ASR 폐기) — 시점 기록 부재 (본인 기억 2차 사료)

### [Unknown] - v0.6.0

- **mlx-whisper 합류** (Mac Apple Silicon) — 시점 기록 부재. AssemblyAI 완전 제거 → 완전 로컬 catch.

### [0.8.0.0~5] - 2026-04 후반

- v0.8.0.4 Provider 조건부 필드 + secret 지우기
- v0.8.0.5 History 카드 Del 버튼 잘림 fix (grid uniform 컬럼)

### [0.8.0.6] - 2026-04-19

**Fixed**: macOS python.org Python에서 YouTube 썸네일 + 업데이트 체크 실패 (SSL 인증서) — `gurunote/_net.py` 신규 (certifi 번들 기반 SSL context).

### [0.8.0.7] - 2026-04-20 (feat/webview-ui 분기, 폐기)

- PyWebView UI Phase 1-B MVP (PR #107 draft)
- 4/27 vanilla 폐기 + Phase 2B-0 React 신축 진입

---

## redesign/tailwind-v2 브랜치 (Phase 2A/2B/백엔드 Phase 1~5)

> main 미머지. 4/24 ~ 5/24 현재.

### Phase 2A — Tailwind redesign (4/24~25)

- `cedae0e` (4/24) chore: initialize Phase 2A
- `4d7222f` (4/25) Phase 2A Commit 2: Material 3 sidebar + frameless titlebar → **Revert (4/25 13:49)** → `archive/commit-2-aborted`
- `b1cd138` / `31f59e3` (4/25) Phase 2A Commit 3a: 자산 복원 + React + Babel 검증
- **License MIT → Elastic 2.0** (KICKOFF Decision 1)

### Phase 2B — React 신축 (4/27~5/2, 514 commits 절정)

- `2160a66` (4/27) **Phase 2B-0**: 신축 baseline (vanilla 폐기 + clean React entry)
- `6376385` Phase 2B-1: Sidebar + App + 5 화면 placeholder
- `598ead0` Phase 2B-2: MainScreen (생성 + 결과 4탭)
- 2B-3a~3d: HistoryScreen (카드 그리드, 검색·필터, 정렬, Facet tree + Detail)
- 2B-4a~4c: EditorScreen, DashboardScreen, SettingsScreen
- 2B-5a/5b: 라이브러리 wiring, 에러 + 복구
- 2B-6a~6d: 글로벌 TopBar, EditorScreen split, Dashboard 재구성, ⌘K SearchPalette

### Phase 2B-3-backend Step 시리즈 (4월 후반)

- `0cc5608` Step 3b-1: 한국어 skip + detected_language
- `38381db` Step 3b-prep: MainScreen state lifted
- `db98761` Step 3b-2: delete_history wiring
- `b1e288f` Step 3b-3: Title 동기화 frontmatter SSOT

### Phase 2B-3-backend Layer 1~15 (5/9~5/11)

- `d9c5f0b` (5/9) Layer 1: pyannote max_speakers + embedding clustering
- `1846098` (5/9) Layer 5+6: LLM hallucination cascading + STT noise filter
- `c7e9e1a` (5/9) Layer 7: ResultPanel 4 tab DetailPanel + EditorScreen 통합
- `cf4a7bd` (5/9) Layer 8: 고유명사 한국어 표기법 일관성
- `c2da2d3` (5/9) **Layer 8 fix-up**: Tiffany Janzen 표준 표기 (잰슨→잔젠)
- `a512b12` (5/10) Layer 9: markdown transcript 가독성
- `027f243` (5/10) Layer 13: 화자 표기 한국어 + entity 영문 병기
- `12e1868` (5/10) Layer 13 fix-up #2: 화자 라벨 첫 등장 영문 병기
- `d30c782` (5/10) Layer 11: Rule 11 한자/일본어 차단 + _SHARED_LANG_RULES
- `ee8b616` (5/10) Layer 14: transcript line break 정규화
- `ece961e` (5/11) Layer 15: METADATA prompt _SHARED_LANG_RULES inline
- `d7a726b` (5/11) Layer 15 fix-up #1: title hallucination 가이드라인

### 백엔드 품질 Phase 1~5 (5/16~5/24)

- `c68aab8` (5/16) **Phase 1 Redesign**: Index Mapping + json_schema strict + segment cap 15
- `b447a11` (5/17) **Phase 4a-1**: xgrammar selective disable + A-3 timeout dead code
- `cdbdc67` (5/18) **Phase 3**: 한자/일본어 0건 후처리 (Sub-path A+B+C)
- `47c3448` (5/18) Phase 3 마무리 unit tests
- `22927fc` (5/19) **Phase 2 (B01) Step B**: entity_cache helper + unit test
- `f9c2da2` (5/19) Phase 2 (B01) Step C: translate_transcript 통합 + Rule 12
- `2ed4701` (5/20) **B02**: slow chunk wall-clock timeout (ThreadPoolExecutor)
- `4a8f281` (5/21) **B06 (Phase 2B-3)**: entity_cache 디스크 + 외래어 표기법 + 표기 통일
- `8fdc2a8` (5/22) B06 verify: 판카지 회귀 차단
- `9afcc93` (5/22) B06 한계 2: canonicalize 미세 변경 차단
- `988b4c1` (5/22) B02 한계 1: R1 padding fallback
- `f58d5f2` (5/22) B06 보완 verify 통과
- `f314d6e` (5/23) B02 수정: ThreadPoolExecutor 결함 + 전 경로 통합
- `97855bd` (5/23) B02 R2: 즉시 padding → strict retry → fallback
- `39652c6` (5/23) **2-pass DCCD prototype**: 자유 번역 → 정렬 토글
- `7a397fa` (5/23) 2-pass 보강: A1 rule 충돌 + A5 prefix strip
- `6b94a49` (5/23) **화자 라벨 코드 부착**: 식별 1회 + 결정론
- `8ecd276` (5/23) **pyannote 3.1 → community-1**
- `599c94b` (5/23) 2-pass 빈 output 복구 시퀀스 (3단계 안전망)
- `2ed4701` (5/24 직전 보강 외) ...
- `527d2ea` (5/24) **Phase 5**: STT 의미 단위 재분할 + chunk_size 자동 (토글)

### docs 정리 (5/24)

- `4f2db79` docs: 옛 UI 작업 문서 legacy 정리 (37 rename)
- `373d5db` docs: Phase 5 검증 산출물 보존
- `5c3c240` docs: 18개 세션 사료화

---

## 통합 view — UI Phase vs 백엔드 품질 Phase

| 시기 | UI/frontend Phase | 백엔드 품질 Phase |
|------|------------------|---------------|
| 4/11~4/19 | v0.1.0 ~ v0.8.0.6 (Streamlit → CustomTkinter → 다수 PR) | — |
| 4/19~4/22 | UI Phase 1-B (PyWebView MVP) | — |
| 4/24~4/25 | Phase 2A (Tailwind, Commit 2 Revert) | — |
| 4/27~5/2 | Phase 2B (React 신축, 514 commit 절정) | — |
| 4/30~5/2 | Phase 2B-3-backend Step 3b-1~3b-3 | — |
| 5/9~5/11 | Phase 2B-3-backend Layer 1~15 (UI 정책 + LLM prompt) | — |
| 5/12~5/15 | (gap, 정전 대비 catch) | — |
| 5/16~5/24 | — | **Phase 1 → 4a-1 → 3 → 2(B01) → B02 → B06 → 2-pass DCCD → 화자 코드 → community-1 → 빈 복구 → Phase 5 재분할** |

## 상호 관계

- **Layer = UI/frontend + LLM prompt** (출력 표기, 화자 라벨, 가독성, 한자 차단 등)
- **Phase 1~5 = 번역 본체 (LLM 호출 path, chunk 분할, entity_cache, 후처리, STT 재분할)**
- Layer 시리즈 (5/9~11) 후 일주일 catch (5/14 정전 대비 catch) → 5/16~ 백엔드 본체 catch 진입.

---

**참고**: 저장소 `CHANGELOG.md`는 Keep a Changelog 형식 — main 브랜치 v0.x catch. 본 문서는 두 브랜치 통합 catch. v0.x 일부 (v0.4.0/0.6.0) 본인 기억 2차 사료.
