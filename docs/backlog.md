# GuruNote Backlog

마지막 갱신: 2026-05-20
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
- 5/20 발견:
  - entity_cache 가 in-memory 만 존재 — 5/14 Phase 2 spec 의 (e) Entity Cache 본질 부재
  - 외래어 표기법 표준 적용 부재
  - '판카지' 회귀 (3회 verify run 중 표기 결정론 부재) 가 본 두 부재의 결합 결과
- spec: `docs/research/phase2b_canonical_translation_spec.md` (5/20 작성)
- 자료:
  - `gurunote/data/loanword_orthography.md` (외래어 표기법 본문, LLM 참조 정합)
  - `docs/research/외래어표기법.html` (원본 자료 영구 보존)
- 본인 결정 catch 영역 (다음 세션 진입 시):
  1. cache 저장 위치 (영상별 / 통합 / 양쪽)
  2. JSON 자료구조 (source 필드, speakers·entities 통합)
  3. 외래어 표기법 LLM 주입 path (R1 전체 / R2 인명·지명만 / R3 bootstrap 한정 / R4 R3 + Phase 3 통합)
  4. 통용 표기 vs 외래어 표기법 우선순위
  5. cache invalidate 정책
- 검증:
  - `tests/test_phase2b_canonical_translation.py` (작성 필요)
  - cache hit/miss test
  - real video verify 에서 5/20 '판카지' 사례 차단
- 상태: not_started (spec 작성 완료, 구현 다음 세션)
- 우선순위: P0 (5/20 발견의 본질 catch + 5/14 spec 의 본질 완성)
- 비용: 큼 (~3~4 시간)

## 별도 추적

### Schema description leak (xgrammar 0.2.0 한계)

- xgrammar 외부 의존이라 본 저장소에서 본질 해결 부재
- B03 (Phase 1 fix-up #3) 에서 후처리로 부분 catch
- xgrammar 신 버전 대기 또는 omlx 측 변경 요청 별 trajectory

## 정리 기록 (2026-05-20)

- 샘 올트먼 hallucinate stochastic → B01 (Phase 2 entity cache) 통과로 5/17~5/20 verify run 4회 모두 0회. 별도 추적 제거.
- 판카지 회귀 stochastic → B06 (Phase 2B-3) 로 통합. 별도 추적 부재 (B06 spec 의 D 사례).
