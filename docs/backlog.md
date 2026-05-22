# GuruNote Backlog

마지막 갱신: 2026-05-22 (보완 verify)
운영 규칙: WIP=1 (동시 active 작업 1개 제한)
상태 정의: not_started / active / blocked / passing

## 진행 중 (WIP=1)

없음

## 대기 중

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
