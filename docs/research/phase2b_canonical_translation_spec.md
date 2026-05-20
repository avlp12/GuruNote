# Phase 2B-3 Spec — Canonical Translation (외래어 표기법 + entity_cache 디스크 저장)

**작성일:** 2026-05-20
**작성 단계:** Phase 2 (B01 + B02) commit 완료 후 — 본 spec 은 read-only 분석 + 본인 결정 catch 영역 보류
**대상:** 다음 세션에서 B06 구현 진입 시 본 spec 을 출발점으로 사용

선행 문서:
- `docs/research/phase2_entity_cache_spec.md` (2026-05-14, (e) Entity Cache 본질)
- `docs/research/phase3_language_purity_spec.md` (Phase 3 후처리 — Sub-A/B/C)
- `gurunote/data/loanword_orthography.md` (외래어 표기법 본문, 본 commit)
- `docs/research/외래어표기법.html` (원본, 본 commit)

---

## 1. 배경

### 1.1 5/14 Phase 2 spec 의 (e) Entity Cache 본질

`docs/research/phase2_entity_cache_spec.md` 의 (e) Entity Cache 정의:

> chunk 출력 → speaker line prefix entity 추출 → entity_cache 갱신 → 다음 chunk context 에 prepend.
> 영상 단위 entity/speaker 정보 누적 → chunk 간 일관성 + **다음 영상 재사용**.

본질 두 가지:
1. **chunk 간 일관성** — chunk N 의 표기를 chunk N+1 prompt 에 prepend.
2. **다음 영상 재사용** — 같은 인물/회사가 다음 영상에 등장하면 cache 활용 → bootstrap LLM 호출 부재.

### 1.2 현 구현 catch (2026-05-20 read-only)

`gurunote/llm.py:984` :

```python
entity_cache: dict = {}     # in-memory only
if config.enable_phase2:
    bootstrap = _bootstrap_entity_cache_from_metadata(...)
    if bootstrap:
        entity_cache.update(bootstrap)
```

`translate_transcript` 함수 안의 local variable. 함수 return 시 garbage collect. **디스크 저장 부재**.

확인 (5/20 20:07):
```
$ find /Users/gesicht -name '*entity_cache*' -type f
gurunote/.../tests/test_phase2_entity_cache.py
gurunote/.../docs/research/phase2_entity_cache_spec.md
```

→ disk persist 파일 부재 = 5/14 spec 의 본질 "다음 영상 재사용" 완성 부재.

### 1.3 5/20 추가 발견 — bootstrap 결정론 부재

3회 verify run 의 bootstrap entity 수:
- Run 1: 3건
- Run 2: 4건
- Run 3: 5건

같은 입력에 다른 결과 → **bootstrap LLM 호출 자체가 stochastic**. 표기도 결정론 부재 (Run 1: `판카지`, Run 3: `판카즈`).

### 1.4 외래어 표기법 표준 적용 부재

LLM 의 prompt 에 외래어 표기법 표준 (문화체육관광부고시 제2017-14호) 참조 부재. `TRANSLATION_SYSTEM_PROMPT` Rule 10 은 통용 표기 dict 만 제공 — Pankaj 같은 dict 외부 인명은 LLM 자유 출력 영역.

### 1.5 '판카지' 회귀의 본질

위 두 부재 (디스크 저장 + 외래어 표기법) 의 결합 결과:
- bootstrap stochastic → run 마다 `판카지` 또는 `판카즈`
- chunk 1 표기를 chunk 2+ 가 무시 (entity_cache prepend 부재한 chunk drift)
- 표준 표기 (`판카즈 샤르마`, 외래어 표기법 제4장 인명 표기 원칙) 강제 부재

---

## 2. 목표

본 phase 의 본질 목표 세 가지:

1. **영상 단위 entity_cache 디스크 저장 + 재로드** — 5/14 spec 의 본질 완성.
2. **외래어 표기법 LLM 참조 자료 등록** — 인명/지명 표준 강제.
3. **chunk 간 일관성 + 다음 영상 재사용 + 표준 표기 동시 달성** — '판카지' 회귀 차단.

---

## 3. 본인 결정 catch 영역

본 spec 은 구현 직전 본인 결정이 필요한 영역을 명시. 다음 세션 진입 시 한 항목씩 결정 catch.

### 3.1 cache 저장 위치

| 옵션 | 경로 | 장점 | 단점 |
|------|------|------|------|
| A | `~/.gurunote/entity_cache/<video_id>.json` | 영상별 분리, 부분 손상 isolate | cross-video 검색 path 별도 필요 |
| B | `~/.gurunote/entities.json` (통합) | 단일 파일, cross-video 검색 단순 | 동시 쓰기 race, 부분 손상 영향 큼 |
| C | A + B 양쪽 (영상별 source-of-truth + index 파일) | 분리 + 검색 양립 | 복잡도 증가 |

**본인 결정 catch.**

### 3.2 cache 저장 형식

JSON 자료구조 제안 (옵션 A 기준):

```json
{
  "video_id": "xxxxx",
  "video_title": "NVIDIA GTC ...",
  "created_at": "2026-05-20T20:07:00+09:00",
  "entities": {
    "Pankaj Sharma": "판카즈 샤르마",
    "Tiffany Janzen": "티파니 잔젠",
    "Schneider Electric": "슈나이더 일렉트릭"
  },
  "speakers": {
    "Speaker A": "티파니 잔젠",
    "Speaker B": "판카즈 샤르마"
  },
  "source": "bootstrap | chunk_extract | manual"
}
```

본인 결정 catch:
- `source` 필드 유지 여부 (debug 용)
- `speakers` 와 `entities` 분리 또는 통합
- 영문 표기 다중 (예: `Pankaj` vs `Pankaj Sharma`) 정규화 path

### 3.3 외래어 표기법 LLM 주입 path

LLM context 에 외래어 표기법을 어떻게 주입할지:

| 옵션 | 주입 path | token 부담 | 효과 |
|------|-----------|------------|------|
| R1 | 전체 자료 (62KB, ~22000 token) 모든 chunk prompt | 매우 큼 | 모든 chunk 가 표준 직접 참조 |
| R2 | 인명/지명 부분 (제4장 + 제3장 일부) 모든 chunk prompt | 중간 | 본질 영역만 |
| R3 | bootstrap LLM 호출 시에만 (chunk 처리는 cache 참조) | 작음 | 표준은 bootstrap 시 적용, chunk 는 cache 따름 |
| R4 | R3 + Phase 3 후처리 (Sub-B 표기 통일) 에 외래어 표기법 참조 | 작음 | bootstrap + 후처리 양쪽 보강 |

본인 결정 catch:
- R3 또는 R4 가 token 비용 / 효과 정합 추정. 본인 환경 정합도 결정.
- "제4장 인명·지명 표기의 원칙" 부분만 추출하여 별도 file 분리 여부.

### 3.4 한국 통상 표기 vs 외래어 표기법 충돌

예시:
- `Schneider Electric` → 외래어 표기법: `슈나이더 일렉트릭` (정합)
- `Pankaj Sharma` → 외래어 표기법 (영어 표기 세칙): `판카즈 샤르마` (정합)
- `Schneider` 가 독일계 회사명일 경우 → 독일어 세칙 적용 시 다른 표기 가능

우선순위 본인 결정 catch:
1. 통용 표기 dict (`TRANSLATION_SYSTEM_PROMPT` Rule 10) 우선
2. 외래어 표기법 표준
3. LLM 자유 출력

또는 외래어 표기법 우선 + 통용 표기 충돌 시 통용 표기 채택.

본인 결정 catch.

### 3.5 cache invalidate / 갱신 정책

- 사용자가 cache 의 잘못된 표기를 수정 가능한 path 부재 → CLI 또는 GUI path 추가 여부.
- 같은 영상 재처리 시 cache 강제 갱신 vs cache 활용 우선.
- cache TTL (예: 30일 이후 재bootstrap) 도입 여부.

본인 결정 catch.

---

## 4. 통합 path (구현 phase 시 진입)

### 4.1 bootstrap 단계

```
1. video_id catch
2. cache file (~/.gurunote/entity_cache/<video_id>.json) 존재 확인
   2-a. 존재 시: load → entity_cache dict → return
   2-b. 부재 시: bootstrap LLM 호출 (외래어 표기법 참조 prompt)
3. bootstrap 결과 → cache file save
```

### 4.2 chunk 처리 단계

```
1. chunk N prompt 작성 시 entity_cache 의 표기 표준 prepend
2. chunk N 출력 → speaker line prefix entity 추출 (`_extract_entities`)
3. cache 에 부재한 새 entity → 외래어 표기법 cross-check 후 cache update
   (LLM 자유 출력 표기 그대로 vs 외래어 표기법 표준 강제 — 본인 결정)
```

### 4.3 영상 처리 완료 시

```
1. 최종 entity_cache → cache file 갱신 저장
2. translate_transcript return
```

### 4.4 Phase 3 후처리 통합

`docs/research/phase3_language_purity_spec.md` 의 Sub-B (speaker name canonicalize) :
- 현재: chunk 1 표기를 정답으로 가정.
- B06 진입 시: entity_cache 의 표기를 정답으로 통합 변경.
- 외래어 표기법 표준 추가 검증 (옵션 R4 채택 시).

---

## 5. 검증 path

### 5.1 unit test

`tests/test_phase2b_canonical_translation.py` 추가:

- `test_cache_save_load_roundtrip` — JSON serialize / deserialize 정합
- `test_cache_hit_skips_bootstrap` — cache 존재 시 bootstrap LLM 호출 부재
- `test_cache_miss_triggers_bootstrap` — cache 부재 시 bootstrap 호출 1회
- `test_loanword_orthography_loaded` — 자료 파일 로드 + LLM prompt 주입
- `test_entity_conflict_resolution` — 통용 표기 vs 외래어 표기법 충돌 시 우선순위

### 5.2 integration test

- 같은 영상 두 번 처리 시 LLM 호출 횟수 측정 (cache hit 확인)
- 다른 영상 두 개에 같은 인물 등장 시 cache 재사용 확인

### 5.3 real video verify

`docs/wip/checkpoint4_realvideo_verify.py` 확장 — 다음 회귀 모두 차단 catch:

| 사례 | 영상 | 회귀 | B06 차단 본질 |
|------|------|------|----------------|
| A (5/13) | NVIDIA GTC | 스키에더 vs 슈나이더 | entity_cache 영상별 일관성 |
| B (5/13) | NVIDIA GTC | 티파즈 샤르마 (음소 hallucinate) | bootstrap + entity_cache 표준 강제 |
| C (5/18) | NVIDIA GTC | 샘 올트먼 hallucinate | (B01 통과로 차단 완료, 회귀 부재 확인) |
| D (5/20) | NVIDIA GTC | 판카지 vs 판카즈 (chunk drift) | 외래어 표기법 + entity_cache 디스크 저장 |

→ 본 B06 의 본질 검증 대상은 **D 사례**.

---

## 6. 본인 결정 catch 영역 정리 (다음 세션 진입 시)

1. **3.1** cache 저장 위치 (옵션 A/B/C)
2. **3.2** JSON 자료구조 (source 필드 / speakers·entities 통합 / 정규화)
3. **3.3** 외래어 표기법 LLM 주입 path (R1/R2/R3/R4)
4. **3.4** 통용 표기 vs 외래어 표기법 우선순위
5. **3.5** cache invalidate 정책 (수정 path, 강제 갱신, TTL)

5개 본인 결정 영역 catch 후 구현 진입.

---

## 7. 구현 비용 예상

| 단계 | 비용 |
|------|------|
| 5개 본인 결정 catch | 30분 |
| cache file save/load 구현 | 30분 |
| bootstrap path 통합 | 1시간 |
| chunk prompt 외래어 표기법 주입 | 30분 |
| Phase 3 후처리 통합 (Sub-B 변경) | 30분 |
| unit test + integration test | 1시간 |
| real video verify (3회 + 비교) | 30분 |
| **총** | **약 3~4시간** |
