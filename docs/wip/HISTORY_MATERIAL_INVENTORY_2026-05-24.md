# GuruNote 역사 재료 수집 (5/24, HEAD 373d5db)

## 1. git 전체 요약

| 항목 | 값 |
|------|-----|
| **최초 commit** | `4bcbee6` (2026-04-11) Initial commit |
| **첫 코드** | `1079431` (2026-04-11 22:55 UTC) "Add Step 1 scaffolding: requirements, env example, and audio download UI" |
| **첫 파이프라인** | `4ecbf77` (2026-04-11 23:10) "Add full 5-step pipeline with VibeVoice-ASR as primary STT engine" |
| **총 commit 수** | **758** |
| **활성 branch** | `redesign/tailwind-v2` (현재 HEAD 373d5db) |
| **tags** | **부재** (릴리스 tag 한 개도 부재 — 버전은 코드 안 `__version__`로만) |

**branches 분류**:
- `main` — production (마지막 push 부재 — feat/webview-ui 이전 시점)
- `redesign/tailwind-v2` — 활성 작업 (현재)
- `feat/webview-ui` — 2026-04-20 PySide6 시도 (폐기, ARCHITECTURE.md 자료)
- `refactor/hf-token-env` — HF_TOKEN 정합 분기
- `archive/commit-2-aborted` — 폐기된 시도 (Phase 2A Commit 2 중단 catch)
- `backup-before-trailer-rewrite-20260423` — 4/23 rewrite 직전 백업
- `backup/pre-tailwind-rewrite-20260425` — 4/25 Tailwind 신축 직전 백업
- `origin/claude/{fix-powershell-syntax,fix-symlink-bypass,setup-cuda-first,setup-insane-search,update-version-check}` — Claude PR 분기 5개

**commit 분포 (집중 일자)**:
- 2026-04-16: **305 commits** (Phase 2B 신축 절정)
- 2026-04-17: **209 commits**
- 2026-04-15: 36
- 2026-04-18: 24
- 2026-04-12: 21
- 그 외: 4월 후반 ~ 5월 4~12건/일

## 2. Phase 전환 commits (시간순 뼈대)

### Phase 0 — 출발 (2026-04-11~12)
```
4bcbee6  04-11  Initial commit
1079431  04-11  Step 1 scaffolding (requirements, env, audio download UI)
4ecbf77  04-11  full 5-step pipeline + VibeVoice-ASR
ab86b9e  04-12  Codex review (hotwords, token budget, env mutation)
30459d9  04-12  v0.1.0 + README/CHANGELOG
5584096  04-12  Gemini review hardening
830cf90  04-12  CustomTkinter GUI (Streamlit 대체)
PR #1~#3 merge
```

### Phase 1 초기 (2026-04-12~22) — v0.x 기능 확장
```
212344b  in-app settings dialog
0c91b28  local video/audio files
664d828  OpenAI-compatible local LLM + in-app settings UX
815fafd  in-app + CLI update workflow
c5a73de  YouTube metadata (date, chapters, captions) as LLM context
93db771  default LLM models 갱신 (gpt-5.4, claude-sonnet-4-6)
136201f  Redesign GUI (sidebar + card layout + step indicators)
PR #4~#14 merge
```

### feat/webview-ui 시도 (2026-04-20) — 폐기
```
0a809cb  feat(webview): settings form 5 sections (CTk parity)
0399c54  settings page route + nav wiring
7201db6  v0.8.0.7 bump
9b6c621  v0.8.0.6 macOS SSL 인증서 fix (마지막 v0.x)
docs/legacy/webview-ui/{ARCHITECTURE.md, TECH_CHOICE.md} 결정 자료
```

### Phase 2A (2026-04-23~25) — Tailwind 신축 진입
```
backup-before-trailer-rewrite-20260423   04-23  4/23 rewrite 직전 백업
backup/pre-tailwind-rewrite-20260425    04-25  4/25 Tailwind 직전 백업
cedae0e  04-24  chore: initialize Phase 2A (Tailwind redesign branch)
4d7222f  04-25  Phase 2A Commit 2: Material 3 sidebar + frameless + MainScreen idle
archive/commit-2-aborted               (폐기)
31f59e3  04-25  Phase 2A Commit 3a Step 3a-1: 자산 복원 + React + Babel
b1cd138  04-25  Phase 2A Commit 3a Step 0: 디자인 자산 재추출
docs/legacy/design/KICKOFF_PHASE_2A.md 결정 자료
```

### Phase 2B 신축 절정 (2026-04-16~17) — 514 commits
```
2160a66  Phase 2B-0: 신축 baseline 준비 (vanilla 폐기 + clean React entry)
6376385  Phase 2B-1: Sidebar + App + 5 화면 placeholder
598ead0  Phase 2B-2: MainScreen — 생성 화면 + 파이프라인 + 결과 4탭
0158942  Phase 2B-3a: HistoryScreen 카드 그리드
646590a  Phase 2B-3b: HistoryScreen 검색 바 + 필터 chips
ebb8f2f  Phase 2B-3c: HistoryScreen 정렬 chips + 카운트
dbe3c79  Phase 2B-3d: HistoryScreen Facet tree + Detail view (Phase 2B-3 완성)
4252cd9  Phase 2B-4a: EditorScreen — 노트 편집 + bridge wiring
5afe8d4  Phase 2B-4b: DashboardScreen — 분석 통계
65b88d8  Phase 2B-4c-1: SettingsScreen — LLM + STT + nav
877ad9f  Phase 2B-4c-2: SettingsScreen — Obsidian + Notion
9ec273c  Phase 2B-4c-3: SettingsScreen 고급 + GuruNote 정보 (Phase 2B-4 완성)
77bb39c  Phase 2B-5a: 라이브러리 wiring
71e7bba  Phase 2B-5b: Stale label 정합
afc7591  Phase 2B-5b-2: EditorScreen 에러 + 복구
e3c9e0c  Phase 2B-6a: 글로벌 TopBar + breadcrumb
4843c66  Phase 2B-6b: EditorScreen split pane + editor-head
a020a44  Phase 2B-6b-2: Sidebar appbar
eb99ce6  Phase 2B-6c: DashboardScreen 재구성 (KPI/태그/검색/추이)
c506376  Phase 2B-6d: ⌘K SearchPalette + HistoryScreen polish
```

### Phase 2B-3-backend Layer 시리즈 (4월 후반 ~ 5월 초)
```
0cc5608  Step 3b-1: 한국어 skip + detected_language
38381db  Step 3b-prep: MainScreen state lifted
db98761  Step 3b-2: delete_history wiring + DeleteConfirmDialog
b1e288f  Step 3b-3: Title 동기화 frontmatter SSOT
d9c5f0b  Layer 1: pyannote max_speakers + embedding clustering
1846098  Layer 5+6: LLM hallucination cascading + STT noise filter
c7e9e1a  Layer 7: ResultPanel 4 tab + EditorScreen 통합
cf4a7bd  Layer 8: 고유명사 한국어 표기법 일관성
c2da2d3  Layer 8 fix-up: Tiffany Janzen (잰슨→잔젠)
a512b12  Layer 9: markdown transcript 가독성
d30c782  Layer 11: Rule 11 한자/일본어 차단 + _SHARED_LANG_RULES
027f243  Layer 13: 화자 표기 한국어 번역 + entity 영문 병기
12e1868  Layer 13 fix-up #2: 화자 라벨 첫 등장 영문 병기
ee8b616  Layer 14: transcript line break 정규화
ece961e  Layer 15: METADATA prompt _SHARED_LANG_RULES inline
d7a726b  Layer 15 fix-up #1: title hallucination 가이드라인
```

### Phase 1~5 (백엔드 품질 — 5월 9일 ~ 5월 24일)
```
c68aab8  Phase 1 Redesign: Index Mapping + json_schema strict + segment cap 15
22927fc  Phase 2 (B01) Step B: entity cache helper + unit test
f9c2da2  Phase 2 (B01) Step C: translate_transcript 통합 + Rule 12
2ed4701  B02: slow chunk wall-clock timeout (ThreadPoolExecutor)
cdbdc67  Phase 3: 한자/일본어 0건 후처리 (Sub-path A + B + C)
47c3448  Phase 3 마무리: unit tests + 의존성
b447a11  Phase 4a-1: xgrammar selective disable + A-3 timeout dead code
09bc6d0  Phase 2B-3 spec: 외래어 표기법 + entity_cache 디스크 저장
88ea485  Phase 2B-3 spec: 본인 결정 5가지 반영
4a8f281  B06 (Phase 2B-3): entity_cache + 외래어 표기법 + 표기 통일
8fdc2a8  B06 verify 통과: 판카지 회귀 차단
8e982ad  GuruNote 운영 개선: backlog + quality 추적 도입
7a397fa  (가) 2-pass 보강: A1 rule 충돌 + A5 prefix strip
6b94a49  (가) 화자 라벨 코드 부착: 식별 1회 + 결정론적 표기
8ecd276  pyannote diarization 모델 변경: 3.1 → community-1
599c94b  2-pass 빈 output 복구 시퀀스 (3단계 안전망)
527d2ea  STT 의미 단위 재분할 + chunk size (5/24)
4f2db79  docs: 옛 UI 작업 문서 legacy 정리 이동 (5/24)
373d5db  docs: Phase 5 검증 산출물 보존 (5/24)
```

## 3. 기존 handoff / 정리 문서 발굴

### docs/legacy/handoff/ (UI 리디자인 handoff, 4/22 추정)
| 파일 | 크기 | 시점 | 요지 |
|------|------|------|------|
| DESIGN_HANDOFF.md | 7.1KB | Phase 2A 시작 전 | Google Workspace 풍 라이트 테마 전환 목표, 비즈니스 로직 보존 |
| DESIGN_TOKENS.md | 4.9KB | 동일 | 색/타이포/여백 토큰 사양 |
| COMPONENT_SPECS.md | 6.5KB | 동일 | 컴포넌트별 사양 |
| APPLY_ALL.md | 5.8KB | 동일 | Phase별 적용 체크리스트 (Phase 1 전역 테마부터) |
| GuruNote Redesign.html | 11.2KB | 동일 | HTML mockup (source of truth) |
| patches/*.py | 5 파일 | 동일 | ui_theme/phase{3,4,5} screen patches |

### docs/legacy/webview-ui/ (PySide6 webview 시도, 4/20)
| 파일 | 크기 | 요지 |
|------|------|------|
| ARCHITECTURE.md | 21KB | feat/webview-ui 브랜치 아키텍처 결정 |
| TECH_CHOICE.md | 12KB | PySide6 catch 결정 + customtkinter 대체 동기 (4/20) |

### docs/legacy/design/ (Phase 2A 신축)
- **KICKOFF_PHASE_2A.md**: Phase 2A 사전 결정 (License 전환 MIT → Elastic, 디자인 자산 선택 등)
- **README.md**: 디자인 자산 README
- **v2-reference.html** (4.5MB): UI source of truth mockup
- `extracted/` — 디자인 자산 추출 (.jsx, .css, raw woff2/js 16개)

### docs/legacy/phase1c/ — phase1c 시점 자료 (2 파일)

### 5월 정전 대비 handoff
- `docs/wip/HANDOFF_POWER_OUTAGE_2026-05-14.md` (4.5KB): 5/14 09:36 KST, HEAD 3f3f04d (Layer 15 fix-up), stash 보존 catch.

### 이전 PR commit_msg 후보 (docs/wip/*.txt, 9개)
- `gurunote_layer{9,11,13,13_fixup2,14,15,15_fixup1}_commit_msg.txt`
- `gurunote_step3b{2,3}_commit_msg.txt`

## 4. docs/ + spec 목록

### docs/ root
- **backlog.md** (112 line, 5/22 마지막 갱신): WIP=1 운영 규칙, B01~B06 추적, Phase 2 entity_cache, B02 timeout, Phase 4 capability_profile 대기.
- **quality.md** (58 line, 5/18 갱신): 모듈별 등급 (STT A, LLM B+, 후처리 A 등).

### docs/research/ (spec 자료)
- `phase1_redesign_research.md` — Phase 1 Redesign 사전 조사
- `phase2_entity_cache_spec.md` (5/14 작성, 5/19 갱신)
- `phase2b_canonical_translation_spec.md` (5/20)
- `phase3_language_purity_spec.md` (5/24 신규)
- `외래어표기법.html` — 문화체육관광부고시 제2017-14호 원본

### docs/wip/ (24 파일)
- prototype .py 13 (오늘 + 이전 verify 스크립트)
- commit_msg.txt 후보 9
- HANDOFF_POWER_OUTAGE
- HISTORY_MATERIAL_INVENTORY (본 문서)

### License
- **Elastic License 2.0** (LICENSE 파일)
- Phase 2A Decision 1에서 MIT → Elastic 전환 결정 (KICKOFF_PHASE_2A.md catch)

## 5. 코드 구조 (현재 도달점)

### gurunote/ 모듈 (총 ~9100 line)

| 모듈 | line | 역할 |
|------|-----|------|
| `llm.py` | (대 — 검증 부재, ~2700 추정) | 번역 핵심 (1-pass/2-pass, chunk_segments, entity_cache, canonicalize) |
| `stt_mlx.py` | 517 | MLX Whisper + pyannote community-1 diarization + 5/24 재분할 |
| `stt.py` | 455 | WhisperX (NVIDIA) + AssemblyAI fallback |
| `updater.py` | 534 | in-app + CLI 업데이트 (SSL 인증서 catch v0.8.0.6) |
| `notion_sync.py` | 465 | Notion 내보내기 |
| `semantic.py` | 413 | 의미 검색 (Step 3.4) |
| `pdf_export.py` | 388 | PDF 출력 |
| `obsidian.py` | 243 | Obsidian sync |
| `ui_components.py` | 236 | UI 컴포넌트 |
| `progress_tee.py` | 234 | 진행 log tee |
| `pdf_installer.py` | 218 | PDF 의존성 설치 |
| `stats.py` | 215 | 통계 대시보드 (Step 3.3) |
| `thumbnails.py` | 177 | 썸네일 |
| `ui_toast.py` | 143 | 토스트 |
| `ui_theme.py` | 144 | 테마 |
| `audio.py` | (catch 부재) | yt-dlp 다운로드 + 자막/메타데이터 |
| `exporter.py` | (catch 부재) | markdown 출력 |
| 기타 | _net, app_icon, hardware, history, log_redirect, nav_tree, search, settings, types, ui_state |

### webui/ (Phase 2B React 신축)
- `bridge.py`, `session.py`, `index.html`, `components/`, `styles/`, `vendor/`

### tests/ (183 passed, 5/24)
- `test_phase2_entity_cache.py` (24/25)
- `test_phase2_slow_chunk_timeout.py` (9/9)
- `test_phase2b_canonical_translation.py`
- `test_phase3_cjk_postprocess.py` (32)
- `test_two_pass_translation.py` (47)
- `test_xgrammar_healthcheck.py`
- `test_segment_resplit.py` (23 신규, 5/24)

## 6. 시간순 뼈대 (Phase 1~5)

| 시기 | Phase | 결정/사건 | 자료 |
|------|-------|---------|------|
| 4/11~12 | 0. 출발 | VibeVoice-ASR + Streamlit/CustomTkinter, 5-step 파이프라인 | git log, README v0.1.0 |
| 4/12~22 | v0.x 기능 | settings dialog, local file, openai_compatible, YouTube metadata, 모델 갱신, GUI redesign | PR #1~#14, CHANGELOG |
| 4/20 | feat/webview-ui | PySide6 webview 시도 (폐기 → Phase 2A 전환 동기) | TECH_CHOICE.md, ARCHITECTURE.md |
| 4/22~23 | UI 리디자인 handoff | Google Workspace 풍 라이트 테마, 토큰 사양 | docs/legacy/handoff/ |
| 4/23 | Phase 2A 사전 결정 | License MIT → Elastic 전환, 디자인 자산 채택 | KICKOFF_PHASE_2A.md, LICENSE |
| 4/24 | Phase 2A 진입 | cedae0e (Tailwind redesign branch) | README "Phase 2A 진입" |
| 4/25 | Phase 2A Commit 2~3 | Material 3, React + Babel, 자산 복원 | Commit 시리즈, archive/commit-2-aborted |
| 4/16~17 | Phase 2B 신축 | 514 commits (Phase 2B-0 ~ 2B-6d), HistoryScreen/EditorScreen/Dashboard/Settings 전부 신축 | git log 시리즈 |
| 4월 후반 ~ 5월 초 | Phase 2B-3-backend | Layer 1/5/6/7/8/9/11/13/14/15 fix 시리즈 | 본문 |
| 5/9 | Phase 1 Redesign | Index Mapping + json_schema strict + segment cap 15 | c68aab8 |
| 5/14 정전 대비 | handoff | stash 보존 | HANDOFF_POWER_OUTAGE_2026-05-14.md |
| 5/14~19 | Phase 2 (B01) | entity_cache + 화자 cache | phase2_entity_cache_spec.md, 22927fc/f9c2da2 |
| 5/16 | Phase 4a-1 | xgrammar selective disable | b447a11 |
| 5/17 | A-3 timeout 시도 실패 | httpx read timeout 한계 | quality.md catch |
| 5/19 | Phase 3 | 한자/일본어 0건 후처리 | cdbdc67, 47c3448 |
| 5/20 | B02 timeout + B06 spec | ThreadPoolExecutor wrap, 외래어 표기법 spec | 2ed4701, 09bc6d0, 88ea485 |
| 5/21 | B06 구현 | entity_cache 디스크 + 외래어 통합 | 4a8f281 |
| 5/22 | B06 verify 통과 | 판카지 회귀 차단, backlog 도입 | 8fdc2a8, 8e982ad |
| 5/23 | 2-pass 보강 | A1 rule 충돌 + A5 prefix strip, 화자 코드 부착, community-1, 빈 복구 | 7a397fa, 6b94a49, 8ecd276, 599c94b |
| 5/24 | Phase 5 | STT 재분할 + chunk size + 검증 산출물 보존 + legacy 정리 | 527d2ea, 4f2db79, 373d5db |

## 7. 빈 곳 (repo에 "왜/갈림길" 부재인 부분)

### 1차 (가장 큰 빈 곳 — 대화/본인 기억으로 채울 부분)

1. **Phase 0~1 초기 결정 동기 (4/11~22)**:
   - 왜 podcast-summarization-app으로 시작 (Codex PR #1 이름이 단서)
   - 왜 VibeVoice-ASR로 시작 → WhisperX/MLX로 전환
   - 왜 Streamlit → CustomTkinter (4/12 GUI 추가)
   - 왜 OpenAI-compatible (local LLM) 도입 (PR #8 시점)
   - 왜 YouTube metadata 컨텍스트 (PR #11)
   - **자료**: README/CHANGELOG에 "무엇" catch — "왜" 부재.

2. **feat/webview-ui 폐기 동기 (4/20~22)**:
   - TECH_CHOICE.md/ARCHITECTURE.md에 "왜 PySide6 선택" catch
   - 단 폐기 결정 시점/동기 → Phase 2A로 전환 catch 부재
   - 어느 PR/이슈/대화에서 폐기 결정

3. **Phase 2A Commit 2 aborted (archive/commit-2-aborted)**:
   - 무엇을 시도 → 왜 폐기 (branch 이름만 catch, 내용 부재)

4. **License MIT → Elastic 2.0 전환 동기**:
   - KICKOFF_PHASE_2A.md Decision 1에 "License 전환" 항목 catch
   - 단 동기 (왜 MIT 부재, 왜 Elastic — 사용자 비공개 의도 등) 부재

5. **Phase 2B 신축 일자 절정 (4/16~17, 514 commits)**:
   - vanilla 폐기 → React 신축 (Phase 2B-0)
   - 5 화면 placeholder → 화면별 완성 → 6 단계 polish
   - **각 화면 결정 동기**: HistoryScreen Facet tree, Dashboard KPI 구성, ⌘K SearchPalette 등 — commit 메시지에 "무엇" catch, "왜 그렇게" 부재.

6. **Phase 2B-3-backend Layer 시리즈 (Layer 1~15)**:
   - 각 Layer 발견 동기 (어떤 실측이 catch했나, 어떤 본인 사용 case에서)
   - Layer 8 "잰슨→잔젠" Tiffany Janzen 표기 catch 동기 등 사용자 catch 시점

7. **Phase 4 capability profile (B05) blocked 동기**:
   - "모델 교체 결정 후 진입" backlog catch
   - 현재 qwen3.6-35b-q5 고정 사용 catch — 어떤 시도 후 catch.

8. **공급망 보안 (osv-scanner / SRI)**:
   - README/CHANGELOG에 v0.8.0.x 시리즈 catch — git log catch 부재 (자세히 catch 필요).
   - 본 catch는 본인 기억 / 사용자 컨텍스트 부재.

### 2차 (보강 catch 부재인 부분)

9. **backup 브랜치 동기**:
   - `backup-before-trailer-rewrite-20260423`: 4/23 무엇 rewrite 직전 backup
   - `backup/pre-tailwind-rewrite-20260425`: 4/25 직전
   - 어느 시점 위험 catch했나

10. **B04 (Phase 1 fix-up #2 — tail attention drop) blocked**:
    - backlog.md "메모리에 정황 부재 — 5/16~17 등록" catch
    - 본인 기억 catch 부재

11. **5/23 화자 라벨 시리즈**:
    - 화자 코드 부착 (6b94a49) 결정 동기
    - pyannote 3.1 → community-1 변경 (8ecd276) 검증
    - 본 commit 메시지에 일부 catch

12. **Phase 5 (5/24 오늘) 추적**:
    - D leak → STT 재분할 → chunk_size → 다영상 → char_limit → 통합 — 본인 결정 시리즈 catch
    - 검증 산출물 (verify_results/*report*.md) 모두 catch
    - 대화 catch는 본인 보고 부재 (오늘 세션 대화)

### 자료 기반 vs 대화 기반

**자료 기반 (repo로 catch 가능)**:
- 모든 commit + 메시지 (758건)
- README/CHANGELOG v0.1.0 ~ v0.8.0.6
- docs/legacy/{handoff, design, webview-ui} 정리 자료
- docs/{backlog, quality}.md
- docs/research/ spec 5개
- docs/wip/ commit_msg 후보 9개
- 본 시점 verify_results/ 보고서 (5/24 Phase 5 자료)

**대화 기반 (본인 기억으로 채울 부분)**:
- 위 "1차 빈 곳" 1~8번 — 동기/갈림길/폐기 동기
- 사용자 catch 시점 (Tiffany Janzen 표기, 판카지 hallucinate 등)
- 본인 평가 시점 ("이거 별로네, 다시")
- 본인 결정 동기 (License 전환, 모델 선택, UI 디자인 방향)

## 본인 결정용 catch

- **자료 풍부 (758 commits + 9100 line + 정리 문서 다수)**, 단 "왜" 맥락은 대화 catch.
- **빈 곳 우선순위**: 1차 1~8번이 역사 문서의 핵심 (출발, 폐기, 전환 동기).
- **다음 단계 후보**:
  1. 본인이 1차 빈 곳 (1~8) 대화 기반 catch → 본인 문서 작성
  2. 또는 자료 기반만으로 1차 뼈대 작성 + 빈 곳 명시
  3. 또는 단계별 (Phase 0/1/2A/2B/2B-3-backend/1~5) 분리 문서

read-only 종료. 수정 부재, commit 부재.
