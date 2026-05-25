# GuruNote Backlog

마지막 갱신: 2026-05-25 (B11 다운로드 wiring + 출처 링크 완료, B12 등록)
운영 규칙: WIP=1 (동시 active 작업 1개 제한)
상태 정의: not_started / active / blocked / passing

## 진행 중 (WIP=1)

없음

## 대기 중

### Phase 5: STT 의미 단위 재분할 + 2-pass default on

- 상태: **완료** (5/24, commit `527d2ea` + default on `feat: Phase 5 재분할 + 2-pass default on`)
- 요약: GURUNOTE_SEGMENT_RESPLIT + GURUNOTE_TWO_PASS 기본값을 on으로 전환. daily 검증 2개 영상 통과 (영상1 96→49 segments, 영상2 586→294 segments, timeout 0, CJK 0, 화자 이름 정상 부착).
- 토글 off 안전망 유지: GURUNOTE_SEGMENT_RESPLIT=0 / GURUNOTE_TWO_PASS=0 으로 기존 동작 복원 가능.

### B01: Phase 2 — entity cache + 화자 cache

- 동작: 영상 단위 entity/speaker 정보 캐시로 외부 인물 hallucinate 차단
- path 결정: (e) Entity Cache + (b) Two-Stage 결합 (5/19)
- 검증:
  - `tests/test_phase2_entity_cache.py` 통과 (24/25, 1 slow integration) — 5/19 작성
  - real video verify 에서 5/18 샘 올트먼 사례 재현 부재 (구현 후)
- 상태: **passing** (Step B + Step C 모두 완료, verify 통과)
- 우선순위: P0 (사용자 경험 가장 큰 개선)
- spec: `docs/research/phase2_entity_cache_spec.md` (5/14 작성, 5/19 갱신)
- 진행 catch:
  - Step B 완료 (5/19): helper 함수 3개 (`_extract_entities`, `_build_entity_cache_block`, `_bootstrap_entity_cache_from_metadata`) + unit test 24건 통과
  - Step C 완료 (5/19): translate_transcript 통합 + Rule 12 추가 + verify 통과 (150.3초, 8/8, 5/13+5/18 사례 3건 모두 차단)
- 상태 갱신: active → passing
- 비용: 큼 (~2~3 세션)

### B02: slow chunk wall-clock timeout

- 동작: chunk 당 60초 hard limit 으로 grammar-recovery loop 진입 시 즉시 종료
- path 결정 (5/20): (f) ThreadPoolExecutor + future.result(timeout) wrap
- 검증:
  - `tests/test_phase2_slow_chunk_timeout.py` 9/9 통과 (5/20 작성)
  - 실측 verify (phase2_b02_run1): 8/8 통과, slow chunk 자연 발생 부재 (timeout 미발동)
- 상태: **passing** (코드 + unit test 정합, production slow chunk 발생 시 catch 가능 상태)
- 우선순위: P1 (간헐적 처리 시간 폭주 차단)
- 참고: 5/17 A-3 timeout 시도 실패 (httpx read timeout 이 wall-clock 강제 부재)
- 한계: production 에서 slow chunk 자연 발생 시까지 wall-clock timeout 발동 검증 부재
- 비용: 중간 (~1 세션)

### B07: D segment 단독 번역 재평가

- 동작: context leak 의 원인이 된 D segment를 청크에서 분리해 단독 번역하는 방안
- 배경: Phase 5 의미 단위 재분할이 D leak 동기(Whisper 경계 잘림)를 간접 차단함. 현재 D 단독 번역 경로는 별도로 만들지 않음.
- 재검토 조건: 정합이 낮은 영상에서 SHIFT 재발 시. 재분할만으로 해소 여부 영상 수 누적 후 판단.
- 상태: not_started
- 우선순위: P3 (Phase 5 이후 대기)

### B08: 화자 bootstrap 식별 한계 후속

- 동작: 메타데이터 기반 bootstrap 화자 식별이 영상 내 전체 화자를 커버하지 못하는 경우 처리
- 배경: Phase 5 daily 검증 영상1 (Boston Dynamics) — 5명 화자 중 3명만 bootstrap 식별. 나머지는 "화자 N" fallback. 메타데이터에 이름이 부재한 화자가 있는 구조적 한계.
- 재검토 조건: 식별 이름 수 < 전체 화자 수인 영상 빈도 증가 시. B01 entity cache 와 연계 가능성 검토.
- 상태: not_started
- 우선순위: P3

### B09: PipelineWorker 를 gui.py 에서 별도 모듈로 분리

- 동작: 파이프라인 워커 로직 (`PipelineWorker` 클래스) 을 CustomTkinter UI 파일 (`gui.py`) 에서 떼어내 `gurunote/pipeline_worker.py` 신규 모듈로 이동
- 배경: v1.0 React/PyWebView UI (`app_webview.py`) 가 `gurunote/webui/session.py:67` 에서 `from gui import PipelineWorker` 로 옛 CustomTkinter UI 파일에 의존. `gui.py` 를 legacy 로 정리 부재 — React 가 깨짐. 기술 부채.
- 작업 범위: `gui.py` 안 `PipelineWorker` 클래스 추출, import 갱신 (`webui/session.py`, `gui.py` 자체), test 통과 확인
- 재검토 조건: 옛 진입점 (`gui.py`/`app.py`) 폐기 시점 또는 React 진입점 단일화 결정 시
- 상태: not_started
- 우선순위: P3 (1.0 후 정리)
- 비용: 중간 (~1 세션, 코드 이동 + import 갱신 + 회귀 테스트)

### B10: setup.sh / setup.bat 안내 문구 갱신

- 동작: setup 스크립트 종료 시 echo 안내가 옛 진입점 (`gui.py`, `streamlit run app.py`) 만 가리킴. v1.0 React 진입점 (`app_webview.py`, `run_webview.command`) 우선 안내로 갱신
- 위치: `setup.sh:120~121`, `setup.bat:96~97`
- 상태: not_started
- 우선순위: P3 (사용자 경험 정합 — README 와 일관성)
- 비용: 작음 (~0.1 세션, echo 문구 갱신)

### B11: HistoryScreen 다운로드 wiring + 노트 상세 출처 링크

- 동작: 노트 상세 화면 두 가지 불편 해소 — (1) HistoryScreen 다운로드 버튼이 stub (`showToast('Phase 2B-4 다운로드 wiring 예정')`) 이라 동작 부재, (2) 출처 URL 이 텍스트만이라 클릭/복사 불가
- 배경: v1.0 daily 사용에서 발견. EditorScreen 다운로드는 `save_result_as` 로 이미 동작했으나 HistoryScreen (목록 카드 + 상세 패널) 다운로드 버튼 2개는 Phase 2B-4 화면 신축 때 stub 로 남았음 (조사 obs 817).
- 작업 범위:
  - `bridge.py` — `open_external(url)` 신규 (webbrowser.open, http(s) 만 허용). save_result_as 는 재사용 (로직 불변).
  - `HistoryScreen.jsx` — top-level helper 3개 (`historyOpenExternal`, `historyCopyText`, `historyDownloadJob`). 다운로드 stub 2곳 → 실저장 연결 (상세 패널은 로드된 `detail.markdown` 재사용, 목록 카드는 `get_history_detail` 로 본문 로드 후 저장). 출처 행 → 클릭(브라우저) + 복사 버튼.
- 검증: 전체 test 통과 (회귀 부재). 수동 확인은 본인 GUI.
- 상태: **완료** (5/25)
- 우선순위: P2 (v1.0 사용성 — 다운로드 미동작이 미완성으로 보임)

### B12: semantic.py React 재배선 (RAG / 의미 검색)

- 동작: 기존 `gurunote/semantic.py` (413행, sentence-transformers 임베딩 + 코사인 유사도 + 인덱스 빌드, 옛 gui.py/app.py 에서 동작) 을 React UI 에 재연결
- 배경: 백엔드는 완성돼 있으나 React 전환 (Phase 2B) 때 포팅 부재. 현재 비활성 — `bridge.py:995` `rebuild_index` → `NotImplementedError`, DashboardScreen "의미 검색 인덱스" 카드 placeholder, HistoryScreen "연관 노트" 버튼 toast.
- 작업 범위: `bridge.py` `rebuild_index` 구현 + 검색 메서드 노출 → DashboardScreen 카드 + "연관 노트" 연결. 선택 의존성 (`requirements-search.txt`) 미설치 시 `is_available()` False 안내. **신규 알고리즘 부재 — 배선 작업.**
- 상태: **완료** (5/25)
- 우선순위: P2
- 완료 내용:
  - bridge.py 4개 메서드 구현 (`rebuild_index` / `semantic_index_stats` / `semantic_search` / `semantic_available`) — semantic.py 호출만, 로직 불변
  - DashboardScreen "의미 검색 인덱스" 카드 실데이터 연결 + Semantic Rebuild 버튼
  - HistoryScreen "의미 검색" 칩 (쿼리 검색 오버레이) + 노트 상세 "연관 노트" (top-K 유사)
  - 의존성 미설치 시 카드 자체에 설치 안내, README 선택 의존성 안내 추가
- 검증 한계: sentence-transformers 가 개발 환경에 미설치 → 미설치 경로(에러 안내)만 검증. 실제 임베딩/검색 경로는 deps 설치 후 본인 GUI 확인 필요.
- 잔여(별도): History 툴바 "본문 포함" 칩은 substring full-text 검색으로 RAG 와 별개 — 미구현 유지 (이번 범위 밖).

### B13: Obsidian 내보내기 + RAG 유사 노트 wikilink (방향 3)

- 동작: 기존 `gurunote/obsidian.py` (`save_to_vault`, 옛 gui.py 에서 동작) 을 React 에 재연결 + 내보낼 때 RAG 유사 노트를 wikilink 로 삽입해 Obsidian 그래프 연결
- 배경: 카드 hub 아이콘이 B12 때 "상세 열기" 중복으로 잘못 배선됨. 본인 의도 = Obsidian 내보내기 (hub = Obsidian, 설정 화면 Obsidian 섹션 아이콘과 정합). `bridge.send_obsidian(1217)` 은 `NotImplementedError` stub 이었음.
- 설계 확정: 유사 노트 top5 + 유사도 ≥ 0.5 / 본문 "## 연관 노트" 섹션 + frontmatter `related` 둘 다 / 표시 `[[GuruNote_<제목>|제목]] (78%)` (alias 로 그래프 연결 + 제목 표시) / 미내보낸 노트는 미래 링크 허용
- 상태: **완료** (5/25)
- 우선순위: P2
- 완료 내용:
  - `bridge.send_obsidian` 구현 (obsidian.py `save_to_vault` + semantic.py `search` 호출만, 로직 불변). vault 미설정 시 `NO_VAULT` 안내.
  - module helper `_inject_related_notes` / `_obsidian_note_stem` — vault 사본에만 wikilink 삽입, 저장된 result.md 불변 (기존 frontmatter 필드 보존).
  - 카드 hub → Obsidian 내보내기 (중복 "열기" 제거). 노트 상세에 Obsidian 버튼 추가, RAG "연관 노트"는 `device_hub` 아이콘으로 유지.
- 검증: 임시 vault 로 end-to-end 확인 — 파일 생성 + ## 연관 노트 섹션 + frontmatter related + wikilink alias, related_count=5, 자기 제외. NO_VAULT 경로 확인. (사용자 vault 무관)
- 역할 구분: 다운로드(.md 로컬 저장) / Obsidian(vault 내보내기 + wikilink) / 연관 노트(앱 내 RAG 검색).
- 잔여(별도): bridge `save_pdf` / `send_notion` 은 여전히 stub (이번 범위 밖). 사용자 vault 에 OBSIDIAN_VAULT_PATH 설정 시 실 그래프 검증은 본인 GUI.

### B03: Phase 1 fix-up #3 — schema text leak

- 동작: xgrammar 0.2.0 description 누설 후처리 필터
- 검증:
  - `tests/test_schema_leak_filter.py` 통과 (작성 필요)
  - 5/18 verify 의 `outputs_count_mismatch_warning_detected_as_false_positive_due_to_json_formatting` 케이스 재현 부재
- 상태: not_started
- 우선순위: P2
- 비용: 작음 (~0.5 세션)

### B04: Phase 1 fix-up #2 — tail attention drop

- 동작: (메모리에 정황 부재 — 5/16~17 에 등록된 항목, 자세한 내용 catch 필요)
- 검증: 미정
- 상태: blocked (정황 확인 필요)
- 비용: 미정

### B05: Phase 4 — capability profile

- 동작: 모델별 (max_ctx, supports_tool_call, korean_quality_score) JSON 추적
- 검증: `jsonschema -i model_capability_profile.json schemas/mcp.schema.json`
- 상태: blocked (모델 교체 결정 후 진입)
- 우선순위: P3 (현재 qwen3.6-35b-q5 고정 사용 중)
- 비용: 큼

### B06: Phase 2B-3 — Canonical Translation (외래어 표기법 + entity_cache 디스크 저장)

- 동작: 외래어 표기법 (문화체육관광부고시 제2017-14호) LLM 참조 + entity_cache 영구 저장으로 인명·지명 표기 표준 강제
- spec: `docs/research/phase2b_canonical_translation_spec.md` (5/20 작성)
- 자료:
  - `gurunote/data/loanword_orthography.md` (외래어 표기법 본문, LLM 참조 정합)
  - `docs/research/외래어표기법.html` (원본 자료 영구 보존)
- 구현 commits:
  - `09bc6d0` (5/20) — spec 자료
  - `88ea485` (5/20) — 본인 결정 5가지 반영
  - `4a8f281` (5/21) — 코드 + tests (21건 신규 + 12건 리팩토링, 84 passed)
- 검증 결과 (5/22 real video verify 3회, NVIDIA GTC 288 segments):
  - Run 1: rc=1, 청크 5 B02 wall-clock timeout (B06 외부 원인, LLM grammar-recovery)
  - Run 2: 8/8 통과 (261s) — bootstrap 4건 → 5건, canonicalize 줄 수 582→582
  - Run 3: 8/8 통과 (291s, cache hit) — canonicalize 줄 수 576→576
  - **'판카지' count: 0건 (Run 2, Run 3 모두)** vs 5/20 baseline 191~192건 → 회귀 100% 차단
  - 판카즈 샤르마 (정 표기): 206~207건 / Run 2, 179~181건 / Run 3
  - cache 파일 `title_<hash>.json` 정합 (Pankaj Sharma → 판카즈 샤르마 source=bootstrap)
- 상태: **passing** (5/22 verify 통과, '판카지' 회귀 차단 확인 + 보완 verify 통과)
- 우선순위: P0 (5/20 발견의 본질 catch + 5/14 spec 의 본질 완성)
- 보완 commits (5/22):
  - `9afcc93` — 한계 2: canonicalize prompt 강화 + `_detect_unexpected_changes` (P-다 — 의심 변경 로그, canonical 채택)
  - `988b4c1` — B02 한계 1: `TIMEOUT_PADDING_MARKER = "[⚠ timeout]"` + retry loop R1 padding fallback
- 보완 verify 결과 (5/22 20:39~20:55, 3회):
  - Run 1: rc=0 / 280s / 8/8 / 판카지 0건 / 판카즈 샤르마 206건 / 줄 수 580→580 / 의심 1건 (젠슨→젠슨 황, 외래어 표기법 적용)
  - Run 2: rc=0 / 311s / 8/8 / 판카지 0건 / 판카즈 샤르마 204건 / 줄 수 592→592 / 의심 1건
  - Run 3: rc=0 / 327s / 8/8 / 판카지 0건 / 판카즈 샤르마 202건 / 줄 수 574→574 / 의심 5건
  - '소프트웤어' (5/22 baseline Run 3 변형): 3 run 모두 **0건** — prompt 강화 효과 catch
  - `[⚠ timeout]` 마커: 3 run 모두 0건 — timeout 자연 발생 부재, R1 효과는 production 대기 (unit test 검증 상태)
- 한계 (잔존):
  - canonicalize LLM 호출 1회 추가 — 처리 시간 +20~36s 보완 verify (5/22 baseline 261~291s → 5/22+ 280~327s)
  - `_detect_unexpected_changes` 한계: 한 줄에 entity 변경 + 일반 단어 변경 함께 있으면 의심 catch 부재 (P-다 정합, daily 빈도 수집 목적)
- 비용: 실제 ~5~6 시간 (5/20 spec, 5/21 구현+tests, 5/22 verify + 보완 commits + 보완 verify)

## 별도 추적

### Schema description leak (xgrammar 0.2.0 한계)

- xgrammar 외부 의존이라 본 저장소에서 본질 해결 부재
- B03 (Phase 1 fix-up #3) 에서 후처리로 부분 catch
- xgrammar 신 버전 대기 또는 omlx 측 변경 요청 별 trajectory

## 정리 기록 (2026-05-20)

- 샘 올트먼 hallucinate stochastic → B01 (Phase 2 entity cache) 통과로 5/17~5/20 verify run 4회 모두 0회. 별도 추적 제거.
- 판카지 회귀 stochastic → B06 (Phase 2B-3) 로 통합. 별도 추적 부재 (B06 spec 의 D 사례).
