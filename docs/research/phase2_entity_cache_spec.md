# Phase 2 Spec — Entity Cache + 화자 라벨 Cache (Chunk 간 일관성)

**작성일:** 2026-05-14
**작성 단계:** Phase 1 Redesign 진행 중 (트랙 A: Step 2 chunk size 축소 중) — 본 spec 은 read-only 분석 + 코드 부재 spec 작성
**대상:** Phase 1 완료 후 즉시 Phase 2 진입 시 Claude Code 가 본 spec 을 출발점으로 사용

---

## 1. 문제 정의

### 1.1 5/13 trajectory 에서 catch 한 회귀 4건 분류

NVIDIA GTC 17분 영상 E2E 후 catch 한 회귀:

| 번호 | 회귀 | Phase 영역 | 본질 cause |
|------|------|------------|------------|
| 1 | 화자명 표기 일관성 부재 (스키에더 vs 슈나이더) | **Phase 2** | chunk 경계의 entity referent 단절 |
| 2 | 화자명 hallucinate (티파즈 샤르마) | **Phase 2** | chunk 1 에서 학습한 표기 부재 영역의 LLM 자유 출력 |
| 3 | 두 번째 등장 영문 병기 (Layer 13 위반) | Layer 13 + **Phase 2** | first-occurrence reset 부재 |
| 4 | "Executive VP" → "집행 임원" (Layer 15 권장 "수석 부사장" 부재) | Layer 15 prompt | system prompt dict 영역 |

→ **회귀 1, 2, 3 모두 chunk 간 entity 표기 일관성 영역 — Phase 2 의 본질 대상.**

### 1.2 실제 사례 catch

**사례 A — 스키에더 vs 슈나이더:**

```
chunk 1 출력 (5건):
[01:23] 스키에더 일렉트릭(Schneider Electric): ...
[01:45] 스키에더 일렉트릭: ...
[02:01] 스키에더 일렉트릭: ...

chunk 2 출력 (정합):
[05:12] 슈나이더 일렉트릭: ...
[05:30] 슈나이더 일렉트릭: ...
```

**진단:**
- `TRANSLATION_SYSTEM_PROMPT` Rule 10 통용 표기 dict 에 `Schneider Electric→슈나이더 일렉트릭` 명시.
- chunk 1 에서 LLM 이 dict 정합 부재 (스키에더 hallucinate).
- chunk 2 부터 정합 회복 — 영상 컨텍스트 의 subtitles_text 영역 또는 chunk 내부 cue 가 catch 가능했을 추정.
- **chunk 1 의 잘못된 표기가 chunk 2+ 로 전파 부재** — 다행이지만 영상 전체의 표기 일관성은 부재.

**사례 B — 티파즈 샤르마:**

```
chunk N 출력:
[12:34] 티파즈 샤르마: ...
```

**진단:**
- 영상에는 `Pankaj Sharma` 만 등장 — `Tiffany Janzen` + `Pankaj Sharma` 두 화자.
- `티파즈` = 두 이름의 음소 혼합 hallucinate — LLM 의 chunk 내부 referent 단절.
- system prompt dict 에 `Pankaj Sharma→판카즈 샤르마`, `Tiffany Janzen→티파니 잔젠` 모두 명시 영역.
- **dict 만으로 chunk 간 hallucinate 차단 부재** catch 완료.

**사례 C — 샘 올트먼 (Sam Altman) 5회 (5/18 Phase 3 verify run 1, 추가):**

```
phase3_run1.md 보고서 Test 10 결과 (5/18):
  '판카즈 샤르마': 198회
  '티파니 잔젠': 58회
  '샘 올트먼': 5회   ← 영상 context 부재 인물
  '젠슨 황': 4회
```

**진단:**
- 영상 context: NVIDIA GTC Studio + Schneider Electric (Pankaj Sharma + Tiffany Janzen).
- Sam Altman / OpenAI 는 영상 영문 원문에 부재 — 완전 외부 hallucinate.
- system prompt dict 영역 부재 (dict 외부 entity).
- stochastic 변동: run 2, run 3 에서는 0회 — run 1 시점만 발생.
- 사례 B (티파즈 음소 혼합) 와 달리 사례 C 는 **완전 외부 인물** hallucinate.
- (e) Entity Cache 의 한계 1 (chunk 1 차단 부재) 노출 catch — chunk 1 에서 hallucinate 진입 시 entity_cache 영역 부재로 chunk 2+ 도 일관성 유지하며 회귀 전파 위험.

### 1.3 현재 코드 영역의 chunk 간 전파 상태

읽기 결과 (2026-05-14 read-only):

| 영역 | 현재 상태 | 전파 여부 |
|------|-----------|-----------|
| `translate_transcript` chunk loop (`gurunote/llm.py:594`) | for 루프, chunk 독립 처리 | 부재 |
| `context_block` (`build_video_context_block`, 480) | 영상 메타 (title/uploader/chapters/subtitles/tags) | 영상 메타 만, entity 표기 부재 |
| `_build_index_mapping_prompt` (936) | `inputs` + `context` (영상 메타) | 영상 메타 만 |
| `translate_chunk_index_mapping_v2` (1106) | `chunk` + `context_block` + `config` | 단일 chunk + 영상 메타 |
| `previous` / `entity_cache` / `speaker_cache` 키워드 | 1건 (line 1002, continuation API 영역) | 완전 부재 |

→ **chunk 간 entity 표기 정보 전파 메커니즘 완전 부재.** Phase 2 의 본질 작업 영역.

---

## 2. 본질 cause 분석

### 2.1 LLM 의 chunk 독립 처리 가정

현재 `translate_transcript` 의 loop:

```python
for i, chunk in enumerate(chunks, start=1):
    translated = translate_chunk_index_mapping_v2(chunk, context_block, config, log)
    translated_parts.append(translated)
```

→ 각 chunk 는 **system prompt + 영상 메타 + chunk 내부 inputs** 만 받는다.
→ chunk i 의 entity 표기 결정이 chunk i+1 에 전파 부재.

### 2.2 system prompt dict 의 한계

`TRANSLATION_SYSTEM_PROMPT` Rule 10 통용 표기 dict:

```
- 인명: Jensen Huang→젠슨 황, Tiffany Janzen→티파니 잔젠,
        Pankaj Sharma→판카즈 샤르마, ...
- 회사: NVIDIA→엔비디아, Schneider Electric→슈나이더 일렉트릭, ...
```

**한계 분류:**

1. **Dict 외부 entity 영역** — 5/13 사례 B (`티파즈 샤르마`) 는 hallucinate 이라 dict 영역 부재. dict 갱신만으로 차단 부재.
2. **Dict 정합 영역 LLM 변동** — 5/13 사례 A (`스키에더` chunk 1) 는 dict 정합 영역인데도 LLM 변동. dict 만으로 100% 일관성 부재.
3. **chunk 경계의 first-occurrence reset** — Rule 2 의 "chunk 분할 reset 절대 부재, 영상 전체 한 번만 영문 병기" 영역이 LLM 의 chunk 독립 처리로 자연스럽게 위반.

### 2.3 본질 진단

→ **chunk 간 entity 표기 cache 메커니즘 부재** 가 본질 cause.
→ dict 갱신은 보조 수단 — 본질 차단 부재.

---

## 3. 해결책 후보 (외부 자료 정합)

### 3.1 후보 (a) — Vimeo 7-Layer: Client-Provided Glossaries

**개요:** Vimeo 의 6번째 layer 인 client-provided glossaries 영역. 사전 정의 dict 을 prompt 에 inline.

**GuruNote 현 상태:** TRANSLATION_SYSTEM_PROMPT Rule 10 이 이미 client-provided glossaries 의 정합 영역. **현 회귀 분석 영역 부재 (이미 적용).**

**한계:** 위 2.2 한계 1, 2, 3 모두 catch 부재.

### 3.2 후보 (b) — Cerlancism Two-Stage Planning

**개요:** Stage 1 = 인물/장소 요약 (LLM 호출 1회), Stage 2 = 정제 instruction 영역의 번역.

**GuruNote 적용 시:**
- Stage 1: 전체 transcript 의 entity 요약 (1회 LLM 호출, 전체 텍스트 입력 → entity dict 출력).
- Stage 2: 각 chunk 번역 시 entity dict 을 context 에 inject.

**장점:**
- chunk 간 entity 일관성 100% 차단 (dict 결정론).
- system prompt dict 의 한계 2 (LLM 변동) 도 차단 — chunk 1 부터 정합 dict 영역.

**단점:**
- LLM 호출 1회 증가 (전체 transcript Stage 1).
- 전체 transcript 가 길면 (NVIDIA GTC 17분 영상 ≈ 25 segments × 20단어 ≈ 500단어 영역, 영문) Stage 1 자체가 chunk 분할 필요 영역 — 복잡성 증가.
- research spec 의 패턴 6 단점 ("LLM 호출 수가 크게 증가", "사용자 RULE 2 단순함이 먼저 위반 가능성") 정합.

### 3.3 후보 (c) — Adjacent Context Injection (~50 lines)

**개요:** rockbenben/subtitle-translator 패턴. 직전 chunk 의 출력 일부를 다음 chunk 의 context 에 prepend.

**GuruNote 적용 시:**
- chunk 1 처리 후, chunk 1 의 마지막 N segments 의 한국어 출력을 변수 저장.
- chunk 2 처리 시 prompt 에 "이전 chunk 의 마지막 N segments" inject.

**장점:**
- 코드 분량 작음 (~15L research spec 추정).
- LLM 호출 수 변경 부재.
- chunk 경계의 entity referent 단절 차단.

**단점:**
- chunk 1 자체의 잘못된 표기 (5/13 사례 A) 차단 부재 — chunk 1 은 prev_chunk 영역 부재라 dict 만 의존.
- Context lines 증가 → chunk 크기 증가 → Phase 1 truncation 본질 cause 가속화 위험 (research spec 패턴 4 단점).
- Phase 1 Step 2 가 chunk size 축소 중 — context 증가는 Step 2 와 본질 충돌.

### 3.4 후보 (d) — RLM (Reference-Less Mapping): find_suspects + resolve_via_subcall

**개요:** 다른 채널의 RLM Phase 2 spec.
- `find_suspects`: 코드 결정론 entity 추출 (정규식).
- `resolve_via_subcall`: 인접 chunk 원문 sub-call 로 RLM (Reference-Less Mapping) 적용.

**GuruNote 적용 시:**
- 1차 chunk 처리 → entity 후보 추출 (정규식 또는 LLM 호출).
- 2차 chunk 처리 전, suspect entity 의 표기를 인접 chunk 원문 cross-check → 정합 dict 갱신.

**장점:**
- Reference-Less (외부 dict 없이) entity 일관성 차단 가능.
- chunk 1 의 잘못된 표기도 chunk 2 에서 catch + 정정 가능.

**단점:**
- 복잡성 매우 큼 (~100L 영역 추정, sub-call mechanism).
- Phase 1 Index Mapping path 와의 통합 영역 catch 부재 (sub-call 의 timestamp 정합).
- 사용자 RULE 2 (단순함) + RULE 3 (외과적 변경) 위반 가능성 — research spec 패턴 6 단점 정합.

### 3.5 후보 (e) — Entity Cache (chunk 1 entity 표기 → chunk 2+ context prepend)

**개요:** 본 spec 작성자 (Claude Code) 의 합성 패턴. (c) Adjacent Context 의 단순화 + (b) Two-Stage 의 정합.

**GuruNote 적용 시:**

```python
# (코드 부재, 구조 영역 만)
entity_cache: dict[str, str] = {}  # English Name → 한국어 표기

for i, chunk in enumerate(chunks, start=1):
    # 1. context_block 에 entity_cache 영역 prepend
    extended_context = context_block + _build_entity_cache_block(entity_cache)

    # 2. chunk 번역
    translated = translate_chunk_index_mapping_v2(chunk, extended_context, config, log)
    translated_parts.append(translated)

    # 3. translated 영역에서 entity 추출 + cache 갱신
    new_entities = _extract_entities(translated)
    entity_cache.update(new_entities)
```

**장점:**
- chunk 간 entity 표기 일관성 100% 차단 (chunk 1 표기 → chunk 2+ context).
- 코드 분량 작음 (~30~50L 추정 — `_extract_entities` + `_build_entity_cache_block`).
- LLM 호출 수 변경 부재.
- Phase 1 Index Mapping path 와의 정합 (context_block 영역 만 확장, 출력 형식 영역 부재).
- 사용자 RULE 2 (단순함) + RULE 3 (외과적 변경) 정합.

**한계:**
- chunk 1 자체의 잘못된 표기 차단 부재 — chunk 1 은 cache 영역 부재.
- entity 추출이 정규식이면 false positive / negative 가능 — `_extract_entities` 구현 신중 필요.

---

## 4. 각 후보의 GuruNote 적용 가능성 비교

| 항목 | (a) glossaries | (b) Two-Stage | (c) Adjacent | (d) RLM | (e) Entity Cache |
|------|----------------|---------------|--------------|---------|------------------|
| 코드 분량 | 0 (적용 영역) | ~70L | ~15L | ~100L | ~30~50L |
| LLM 호출 영향 | 0 | +1 (Stage 1) | 0 | +N (sub-call) | 0 |
| chunk 1 차단 | 부재 | 차단 | 부재 | 차단 | 부재 |
| chunk 2+ 차단 | 부재 | 차단 | 차단 | 차단 | 차단 |
| dict 외부 entity | 부재 | 차단 | 차단 | 차단 | 차단 |
| RULE 2 (단순함) | 정합 | 위반 가능 | 정합 | 위반 | 정합 |
| RULE 3 (외과적) | 정합 | 위반 가능 | 정합 | 위반 | 정합 |
| Phase 1 정합 | 정합 | 정합 | **충돌** (chunk 크기) | catch 부재 | 정합 |
| 처리 시간 영향 | 0 | +Stage 1 시간 | 0 | +N sub-call 시간 | 0 |

**핵심 catch:**
- (a) 는 이미 적용 영역 — 본 회귀 차단 부재.
- (c) 는 Phase 1 Step 2 와 본질 충돌.
- (b), (d) 는 복잡성 큼.
- **(e) 가 단순함 + Phase 1 정합 + chunk 2+ 차단 영역의 정합.**

---

## 5. 추천 path (예비)

### 5.1 1차 추천: (e) Entity Cache + (a) glossaries 결합

**구조:**
- (a) glossaries: 현 system prompt Rule 10 영역 유지 — chunk 1 의 dict 정합 영역 catch.
- (e) Entity Cache: chunk 1 의 출력 → chunk 2+ context 영역 prepend — chunk 간 일관성 차단.

**근거:**
1. **단순함** — 코드 분량 ~30~50L, LLM 호출 수 변경 부재.
2. **Phase 1 정합** — Index Mapping path 와 독립적 (context_block 영역 만 확장).
3. **회귀 1, 2, 3 차단** — 5/13 사례 A, B 모두 chunk 2+ 영역 catch.
4. **사용자 RULE 2, 3 정합.**

**한계 catch:**
- chunk 1 자체의 LLM 변동 (사례 A 의 `스키에더`) 영역 차단 부재.
- → chunk 1 영역은 Layer 15 prompt 강화 또는 (b) Two-Stage 영역의 부분 적용으로 별도 catch.

### 5.2 2차 추천 (Phase 2 완료 후 회귀 catch 시): (b) Two-Stage 의 부분 적용

**구조:**
- chunk 1 처리 전, 영상 메타 + subtitles_text 영역의 entity 사전 추출 (1회 LLM 호출, 짧은 prompt).
- 추출 결과를 entity_cache 초기 영역에 inject → chunk 1 부터 정합 dict.

**근거:**
- (e) 의 한계 (chunk 1 차단 부재) 보완.
- LLM 호출 1회 증가 영역만 (research spec 패턴 6 의 +N 영역 부재).

**적용 시점:** Phase 2 (e) 적용 후 회귀 verify → chunk 1 회귀 catch 시 진입.

**5/18 추가 catch — (b) 우선순위 재고려:**

5/18 phase3_run1 의 사례 C (샘 올트먼 5회) 는 영상 context 부재 인물의 완전 외부 hallucinate. (e) Entity Cache 의 한계 1 (chunk 1 차단 부재) 가 production 에서 실제 발생할 수 있는 사례임이 catch.

따라서 (b) Two-Stage 의 진입 시점을 다음과 같이 재고려 가치 catch:
- 종전: Phase 2 (e) 완료 후 회귀 verify → chunk 1 회귀 catch 시 진입
- 갱신 후보: Phase 2 (e) + (b) 부분 동시 진입 — 영상 메타 + subtitles_text 에서 사전 entity 추출 → entity_cache 초기 영역 채움 → chunk 1 부터 정합 dict 영역 catch

비용 비교:
- 종전: LLM 호출 수 변경 부재, 단 chunk 1 차단 부재
- 갱신 후보: LLM 호출 +1 (약 7초 추가), chunk 1 차단 가능

본인 결정 항목 — 다음 세션 진입 시 path 선택.

---

## 6. 작업 spec (예비, 코드 부재)

### 6.1 신규 함수 영역

```python
# (gurunote/llm.py 예상 위치: translate_chunk_index_mapping_v2 직전)

def _build_entity_cache_block(entity_cache: dict[str, str]) -> str:
    """entity_cache 를 LLM context 영역의 markdown block 으로 변환.

    Args:
        entity_cache: {English Name: 한국어 표기} dict.
            예: {"Schneider Electric": "슈나이더 일렉트릭",
                 "Pankaj Sharma": "판카즈 샤르마"}

    Returns:
        "### 영상 entity 표기 일관 영역\n- Schneider Electric → 슈나이더 일렉트릭\n..."
        비어 있으면 "".
    """
    ...

def _extract_entities(translated_chunk: str) -> dict[str, str]:
    """translated_chunk 영역에서 "한국어 표기(English Name)" 패턴 추출.

    Phase 1 redesign 의 출력 형식 정합:
        "한국어 화자명(English Name): 본문"  (첫 등장)
        "한국어 화자명: 본문"                  (이후)

    정규식 패턴: r'([\\uAC00-\\uD7AF]+(?:\\s+[\\uAC00-\\uD7AF]+)*)\\(([A-Za-z\\s]+)\\)'

    Returns:
        {English Name: 한국어 표기} dict.
    """
    ...
```

### 6.2 translate_transcript 영역 수정

**통합 위치 (5/19 갱신, Phase 3 완료 후):**

- Phase 2 (entity cache + 화자 cache) 통합 위치: chunk loop 안 (5/19 시점 `gurunote/llm.py:652` 영역).
- Phase 3 (post_process_cjk) 통합 위치: chunk loop 종료 후 `result = "\n\n".join(...)` 다음 (5/19 시점 line 676 직전, cdbdc67 commit).
- 두 phase 는 **직렬** — Phase 2 가 chunk loop 안에서 entity 일관성 유지 → chunk loop 종료 → Phase 3 가 전체 result text 에서 한자/일본어 후처리.
- 두 phase 의 입출력 자료구조 충돌 부재 — Phase 2 는 chunk-level translated string 만 다루고, Phase 3 는 join 된 전체 result string 입력으로 받음.

```python
# (gurunote/llm.py 5/14 시점 line 594 영역 → 5/19 시점 line 652 영역)

entity_cache: dict[str, str] = {}

for i, chunk in enumerate(chunks, start=1):
    ...
    # context_block + entity_cache 결합
    cache_block = _build_entity_cache_block(entity_cache)
    extended_context = f"{context_block}\n\n{cache_block}" if cache_block else context_block

    translated = translate_chunk_index_mapping_v2(chunk, extended_context, config, log)
    translated_parts.append(translated)

    # entity 추출 + cache 갱신
    new_entities = _extract_entities(translated)
    if new_entities:
        log(f"   📚 entity cache 갱신: +{len(new_entities)}건 (누적 {len(entity_cache) + len(new_entities)}건)")
        entity_cache.update(new_entities)
```

### 6.3 TRANSLATION_SYSTEM_PROMPT 영역 추가 룰

```
## Rule 12 — Entity 표기 일관 영역 (Phase 2)
- context 영역의 "### 영상 entity 표기 일관 영역" 블록이 있으면,
  해당 dict 의 한국어 표기를 **반드시** 사용 (LLM 변동 절대 부재).
- dict 외부의 신규 entity 는 Rule 10 통용 표기 dict 정합 표기 사용.
- 첫 등장 영문 병기 = dict 영역 entity 는 부재 (이전 chunk 에서 이미 병기 완료),
  dict 외부 신규 entity 만 첫 등장 영문 병기.
```

### 6.4 verify spec

**pytest 인프라 통합 (5/18 도입, 47c3448 commit, 5/19 갱신):**

`tests/` + `pytest.ini` + `pyproject.toml` 도입 후 Phase 2 verify 는 다음 패턴으로 통합:

- 신규 파일: `tests/test_phase2_entity_cache.py`
- 패턴 정합: `tests/test_phase3_cjk_postprocess.py` 의 mock + integration 분리 구조
- mock test: `_build_entity_cache_block`, `_extract_entities`, entity_cache 갱신 흐름 결정론 검증
- integration test (`@pytest.mark.slow`): 실제 omlx 호출로 chunk 2+ 의 entity 일관성 검증

**자동 verify (NVIDIA GTC 25 segments) — pytest 통합:**
1. chunk 1 entity 추출: `entity_cache` 가 비어 있던 상태에서 `Schneider Electric → 슈나이더 일렉트릭`, `Pankaj Sharma → 판카즈 샤르마` 등 추출 (mock test 결정론).
2. chunk 2+ context inject: `_build_entity_cache_block` 출력이 chunk 2+ 의 prompt 영역에 포함 (mock test 결정론).
3. chunk 2+ 출력에서 dict 영역 entity 의 한국어 표기 100% 정합 (integration test, slow marker).
4. dict 외부 신규 entity 의 첫 등장 영문 병기 정합 (integration test).
5. chunk 2+ 출력에서 dict 영역 entity 의 영문 병기 부재 (Rule 12 정합).

**실측 검증 (`docs/wip/checkpoint4_realvideo_verify.py`):**
- 5/13 trajectory 회귀 1 (스키에더 vs 슈나이더): chunk 2+ 영역 100% 정합.
- 5/13 trajectory 회귀 2 (티파즈 hallucinate): chunk 2+ 영역에서 `판카즈 샤르마` 로 catch (단 chunk 1 차단 부재).
- 5/18 trajectory 회귀 C (샘 올트먼): (b) Two-Stage 부분 적용 시 chunk 1 차단 가능.

**verify 본문 보존 (5/19 catch):**
- checkpoint4 의 본문 출력 path 가 `/tmp/realvideo_verify_result.md` → `~/GuruNote/verify_results/realvideo_body_<timestamp>.md` 로 수정.
- run 마다 덮어쓰기 차단 → 본문 영구 보존 + 본인 직접 grep 검증 path 확보.

---

## 7. 가정과 한계

### 7.1 가정

1. **Phase 1 redesign 완료** — Index Mapping path 의 출력 형식 (`한국어 화자명(English Name): 본문`) 이 안정.
2. **timestamp 완전성 보존** — Phase 1 의 zip 결정론 매핑이 Phase 2 영역 변경 부재.
3. **entity 추출 정규식 정합** — 한글 + 영문 괄호 패턴이 false positive 영역 부재 (단 verify 필요).

### 7.2 한계

1. **chunk 1 차단 부재** — 5/13 사례 A 영역의 chunk 1 LLM 변동 (`스키에더`) 은 Phase 2 (e) 만으로 차단 부재.
2. **entity 추출의 false positive** — `한국어(영문)` 패턴이 entity 외 영역에서도 매칭 가능 (예: `AI 네이티브(AI Native)` 같은 기술 용어도 entity_cache 영역 진입).
3. **cache 크기 증가** — 영상이 길면 entity_cache 가 커져 context_block 크기 증가 → Phase 1 truncation 본질 cause 영향. 단 entity 개수가 영상 당 10~30 영역 추정이라 한계 작음.

### 7.3 의존성

- **Phase 1 (timestamp validation + Index Mapping path) 의존** — research spec 의 A4 가정 정합.
- **Phase 1 Step 2 (chunk size 축소) 완료 후 진입** — entity_cache context 추가가 chunk 크기 증가 영역이라 Step 2 완료 후 영향 verify.

---

## 8. Phase 1 redesign 과의 관계

| Phase | 책임 | 범위 | 본질 cause 차단 |
|-------|------|------|------------------|
| Phase 1 | chunk 내부 정확성 | timestamp 완전성 + content drift 차단 | Index Mapping path (zip 결정론) + finish_reason continuation |
| Phase 2 | chunk 간 일관성 | entity 표기 일관 | entity_cache prepend + Rule 12 |

→ **두 Phase 가 본질적으로 다른 본질 cause 영역 — 독립 적용 가능, 통합 시 본인 5/11 통찰 ("GuruNote = LLM 하네스") 본질 완성.**

### 8.1 Phase 1 Step 2 가정 폐기 (5/19 갱신)

**5/14 가정 (DEFAULT_CHUNK_CHAR_LIMIT 12000 → 6000) 폐기:**

5/14 spec 작성 시점에는 트랙 A 의 Step 2 가 chunk size 축소 (12000 → 6000) 진행 중이었으나, 5/14 22:55 시점에 본 가설이 반증되어 다음 path 로 변경:

- 실제 적용 (Phase 1 Redesign, c68aab8):
  - `DEFAULT_CHUNK_CHAR_LIMIT` **12000 유지** (축소 부재)
  - `MAX_SEGMENTS_PER_CHUNK=15` 추가 (segment 수 cap)
  - Index Mapping + json_schema strict + finish_reason continuation

- 즉 본 spec 의 section 8.1 ~ 9.2 의 "Step 2 완료 후 진입" 본문은 outdated. 현재 path 는 Phase 1 Redesign 완료 후 Phase 2 진입.

**현재 chunk size 환경 (5/19 시점):**
- `DEFAULT_CHUNK_CHAR_LIMIT = 12000`
- `MAX_SEGMENTS_PER_CHUNK = 15`
- NVIDIA GTC 17분 영상 → 288 segments → 20 chunks (segment cap 결정론)

회귀 영향 verify 는 5/17~5/18 의 12회 verify 보고서로 catch 가능 — chunk 1 차단 부재 한계 (사례 C 샘 올트먼) 외에는 entity 회귀 잔존 부재 (단 본문 손실로 본인 직접 grep 부재 — 5/19 본문 보존 path 도입 후 재verify 가치).

---

## 9. 추정 작업 분량 + 시점

### 9.1 코드 분량 추정

| 영역 | 추정 분량 |
|------|-----------|
| `_build_entity_cache_block` | ~15L |
| `_extract_entities` | ~20L (정규식 + edge case) |
| `translate_transcript` 영역 수정 | ~10L (entity_cache var + loop 내부) |
| `TRANSLATION_SYSTEM_PROMPT` Rule 12 추가 | ~10L |
| **총합** | **~55L** |

### 9.2 진입 시점 갱신 (5/19)

**5/14 추정 시점 outdated:**

5/14 spec 작성 시 추정한 진입 시점 (5/15~5/16) 은 outdated. 실제 진행:

| 작업 | 완료 시점 | commit |
|------|-----------|--------|
| Phase 1 Redesign (Index Mapping + json_schema strict + segment cap 15) | 5/15 영역 | c68aab8 |
| Phase 4a-1 (xgrammar selective disable) | 5/17 | b447a11 |
| Phase 3 (한자/일본어 0건 후처리 Sub-path A+B+C) | 5/18 | cdbdc67 |
| Phase 3 unit tests + pyproject.toml | 5/18 | 47c3448 |
| backlog + quality docs | 5/19 | 8e982ad |

**Phase 2 (B01) 진입 시점 (5/19 갱신):**
- 완료된 선행 작업: 위 표의 5건.
- 진입 조건 정합: Phase 1 Redesign 완료 + Phase 3 후처리 통합 위치 명확.
- 다음 세션 진입 예정 (`docs/backlog.md` B01).
- spec 본문 (e) Entity Cache + (a) glossaries 결합 path 유효.
- 5/18 사례 C (샘 올트먼) catch 로 (b) Two-Stage 부분 적용 진입 시점 재고려 가치 (section 5.2 갱신 정합).

---

## 10. 본 spec 의 위치

- **본 spec = read-only 분석 + 코드 부재 spec 작성.**
- gurunote/llm.py 등 코드 파일 변경 부재.
- 본 spec 은 Phase 1 완료 후 Claude Code 가 Phase 2 진입 시 출발점.
- 본 spec 의 추천 path (e) Entity Cache 가 Phase 2 의 1차 적용 영역 — 단 Phase 1 verify 결과에 따라 (b) Two-Stage 부분 적용 영역 진입 가능.

---

## 11. 결론

### 11.1 핵심 메시지

- 5/13 trajectory 회귀 4건 중 1, 2, 3 = Phase 2 영역 (entity 일관성).
- 본질 cause = chunk 간 entity 표기 cache 메커니즘 부재.
- 추천 path = **(e) Entity Cache** — 단순함 + Phase 1 정합 + chunk 2+ 차단.
- 한계 = chunk 1 자체 차단 부재 — Phase 2 완료 후 회귀 catch 시 (b) Two-Stage 부분 적용 진입.

### 11.2 사용자 RULE 정합

- **RULE 2 (단순함이 먼저):** ~55L 코드, LLM 호출 수 변경 부재 — 정합.
- **RULE 3 (외과적 변경):** Index Mapping path 영역 부재, context_block 만 확장 — 정합.
- **RULE 5 (timestamp 가 외부 변수):** Phase 1 zip 결정론 매핑 영역 변경 부재 — 정합.

### 11.3 Phase 1 redesign 과의 정합

- 의존성 정합 (research spec A4).
- 독립 적용 가능.
- 통합 시 본인 5/11 통찰 ("GuruNote = LLM 하네스") 본질 완성.
