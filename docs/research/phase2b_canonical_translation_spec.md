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

## 3. 본인 확정 결정 (2026-05-20)

본 5개 결정은 다음 세션의 구현 진입 직전 동일 그대로 사용. 결정 catch 부재.

### 3.1 cache 저장 위치 — 옵션 A 확정

**결정:** `~/.gurunote/entity_cache/<video_id>.json` 영상별 분리.

근거:
- daily 사용 path 가 영상 단위 처리 — 영상별 분리가 자연스러움.
- 부분 손상 isolate (영상 하나의 cache 깨짐이 다른 영상에 부재 영향).
- 본인 RULE 2 (단순함) 정합.
- cross-video 재사용 우선순위 낮음 — 같은 인물이 다음 영상에 등장 시에도 bootstrap 다시 수행 가능 (5/14 spec 의 "다음 영상 재사용" 본질은 보류, 영상별 분리 우선).

### 3.2 cache 저장 형식 — entities 통합 + type + loanword_spec_version 확정

**결정:** speakers / entities 분리 부재. 단일 `entities` dict + `type` 필드로 구분.

JSON 자료구조:

```json
{
  "video_id": "xxxxx",
  "video_title": "NVIDIA GTC ...",
  "created_at": "2026-05-20T20:07:00+09:00",
  "loanword_spec_version": "2017-14",
  "entities": [
    {"english": "Pankaj Sharma", "korean": "판카즈 샤르마", "type": "person", "source": "bootstrap"},
    {"english": "Tiffany Janzen", "korean": "티파니 잔젠", "type": "person", "source": "bootstrap"},
    {"english": "Schneider Electric", "korean": "슈나이더 일렉트릭", "type": "company", "source": "bootstrap"},
    {"english": "Speaker A", "korean": "티파니 잔젠", "type": "speaker", "source": "chunk_extract"}
  ]
}
```

근거:
- speakers vs entities 의 LLM 출력 구분이 항상 명확 부재 (예: "Speaker A" 가 person 이기도 함).
- `type` ∈ {person, company, place, product, speaker} 로 통합 dict 안에서 분류.
- `source` ∈ {bootstrap, chunk_extract, manual} 로 debug + Phase 3 후처리 path 결정.
- `loanword_spec_version` 으로 외래어 표기법 본문 버전 추적 (3.5 invalidate 정책의 자동 트리거).
- 영문 표기 다중 정규화 (예: `Pankaj` vs `Pankaj Sharma`) 는 첫 등장 영문 병기 기준으로 entries 가산. 다음 세션 구현 시 helper 함수에서 처리.

### 3.3 외래어 표기법 LLM 주입 path — R4 확정

**결정:** bootstrap LLM 호출 + Phase 3 후처리 양쪽에 외래어 표기법 참조 주입.

근거:
- 본인 daily 영상 길이 catch (10~60분) — chunk prompt 모든 호출에 자료 주입 (R1/R2) 은 token 비용 큼.
- bootstrap 의 입력 (영상 메타 + 자막 첫 3000자) 만으로는 영상 후반 등장 인물·회사 누락 가능.
- Phase 3 후처리 가 영상 전체 번역 결과를 보고 표기 통일 — bootstrap 의 한계 보완.
- chunk 처리 prompt 는 cache 의 표기 표준만 prepend (현재 Rule 12 path 정합).

R4 구체 path:
- **Bootstrap LLM 호출 prompt**: `gurunote/data/loanword_orthography.md` 의 "제4장 인명·지명 표기의 원칙" 부분 + 표 1 (영어 자모 한글 대조표) 부분 inline 주입.
- **Chunk 처리 prompt**: 외래어 표기법 자료 부재 (cache 의 표기만 Rule 12 path 로 prepend).
- **Phase 3 후처리 (Sub-B 표기 통일)**: 외래어 표기법 전체 본문을 LLM 참조 자료로 주입하여 cache + 영상 전체 결과 cross-check.

자료 분할:
- 전체 본문은 `gurunote/data/loanword_orthography.md` 유지.
- bootstrap 용 short version 은 코드에서 string slice 로 추출 (별 file 부재).

### 3.4 통용 표기 vs 외래어 표기법 우선순위 — 통용 우선 확정

**결정:** 통용 표기 우선. 외래어 표기법은 통용 부재 시 적용.

우선순위:
1. `TRANSLATION_SYSTEM_PROMPT` Rule 10 통용 표기 dict (예: Schneider Electric → 슈나이더 일렉트릭)
2. cache 의 영상별 entity 표기 (chunk_extract source)
3. 외래어 표기법 표준 (loanword_orthography.md)
4. LLM 자유 출력

근거:
- 본인 가정의학과 daily 사용 가치 = 통용 표기 정합 (예: Schneider Electric 의 통용 표기 = 슈나이더 일렉트릭, 외래어 표기법 영어 세칙 적용 시도 같지만, 충돌 시 통용 우선).
- 외래어 표기법 영어 세칙은 음운 한 가지 기준 — 영상 도메인 (의학·기술·기업) 의 통용 표기와 미세 충돌 가능.
- 통용 표기 부재 entity 만 외래어 표기법 표준 적용 (예: Pankaj Sharma — 통용 표기 dict 부재, 외래어 표기법 영어 세칙 적용 → 판카즈 샤르마).

### 3.5 cache invalidate 정책 — 수동 + spec_version 자동 확정

**결정:** 수동 (CLI 또는 GUI path) + `loanword_spec_version` 변경 시 자동.

invalidate 트리거:
- **수동**: 사용자가 cache 파일 직접 삭제. 다음 세션 구현 시 GUI 또는 CLI helper 추가 검토 (B06 본질 부재, 옵션).
- **자동**: cache 파일의 `loanword_spec_version` 과 `gurunote/data/loanword_orthography.md` 의 표시 버전 (`문화체육관광부고시 제2017-14호` → `"2017-14"`) 비교, 부재 또는 다름 시 자동 재bootstrap.

TTL 부재 — 영상별 cache 는 stale 가능성 낮음 (영상 자체가 immutable).

같은 영상 재처리:
- 기본 cache 활용 (cache hit → bootstrap LLM 호출 부재).
- 강제 재bootstrap path 부재 (필요 시 사용자가 cache 파일 삭제 = 수동 invalidate).

근거:
- 본인 RULE 11 (코드베이스 관행) — `gurunote/data/cjk_lookup.yaml` 의 본인 path 정합 (수동 갱신 + 코드에서 lookup).
- spec_version 자동 invalidate 는 외래어 표기법 본문 갱신 시 (정부 고시 개정) 자동 적응.

---

## 4. 통합 path (R4 확정 + 4단계 흐름)

### 4.1 Bootstrap 단계

```
1. video_id catch (video_context.id)
2. cache file (~/.gurunote/entity_cache/<video_id>.json) 존재 + spec_version 정합 확인
   2-a. 존재 + spec_version 정합: load → entities list → in-memory dict 변환 → return (LLM 호출 부재)
   2-b. 부재 또는 spec_version 다름:
      → bootstrap LLM 호출 prompt 구성
        - 영상 메타 (title / uploader / description)
        - 자막 첫 3000자
        - 외래어 표기법 short version (제4장 인명·지명 + 표 1 영어 자모 inline)
        - 우선순위 명시 (통용 표기 dict → 외래어 표기법 → LLM 자유 출력)
      → 호출 결과 parse → entities list 생성 (source=bootstrap)
      → cache file save (loanword_spec_version 기록)
3. in-memory entity_cache dict 영역으로 chunk loop 진입
```

### 4.2 Chunk 처리 단계 (현 path 정합 — 외래어 표기법 자료 주입 부재)

```
1. chunk N prompt 작성 시 cache 의 표기 표준 prepend (현 `_build_entity_cache_block` 정합)
2. chunk N LLM 호출 (외래어 표기법 자료 주입 부재 — token 비용 catch)
3. chunk N 출력 → speaker line prefix entity 추출 (`_extract_entities`)
4. cache 에 부재한 entity → in-memory dict update (source=chunk_extract)
```

R4 path 의 chunk 처리는 현 코드와 동일. 외래어 표기법 자료 주입은 bootstrap + Phase 3 후처리 양쪽만.

### 4.3 Phase 3 후처리 통합 (R4 의 본질 보강)

`docs/research/phase3_language_purity_spec.md` 의 Sub-B (speaker name canonicalize) 변경:

- 현재 path: chunk 1 표기를 정답으로 가정.
- B06 path: entity_cache + 외래어 표기법 전체 본문 LLM 참조로 cross-check.

구체 흐름:
```
1. 영상 전체 번역 결과 + entity_cache 를 LLM 에 주입
2. 외래어 표기법 전체 본문 `gurunote/data/loanword_orthography.md` 를 참조 자료로 추가
3. LLM 이 entity 표기 통일 (우선순위 정합)
   - 통용 표기 dict 부재 entity 의 표기 외래어 표기법 적용 검증
   - chunk drift (예: chunk 1 의 판카즈 → chunk 2+ 판카지) 통일
4. 통일 결과로 본문 갱신 + entity_cache 갱신 (source=chunk_extract 의 표기 변경 시 manual 으로 승격)
```

### 4.4 영상 처리 완료 단계

```
1. Phase 3 후처리 결과의 최종 entity_cache → cache file 갱신 저장
   - loanword_spec_version 기록 (현재 본문의 "2017-14")
   - entities list 갱신
2. translate_transcript return
3. 다음 영상 처리 시: 같은 video_id 면 cache hit (cross-video 재사용 부재 — 영상별 분리)
```

---

## 5. 검증 path

### 5.1 unit test

`tests/test_phase2b_canonical_translation.py` 추가:

- `test_cache_save_load_roundtrip` — JSON serialize / deserialize 정합 (entities list 구조 + loanword_spec_version)
- `test_cache_hit_skips_bootstrap` — cache 존재 + spec_version 정합 시 bootstrap LLM 호출 부재
- `test_cache_miss_triggers_bootstrap` — cache 부재 시 bootstrap 호출 1회
- `test_spec_version_mismatch_invalidates_cache` — cache 의 spec_version 이 본문 버전과 다를 때 자동 재bootstrap 트리거
- `test_loanword_orthography_loaded` — 자료 파일 로드 + LLM prompt 주입 (bootstrap 용 short version slice 정합)
- `test_loanword_full_body_in_phase3` — Phase 3 후처리 prompt 에 전체 본문 주입 정합
- `test_entity_conflict_resolution` — 통용 표기 dict 우선, cache 우선, 외래어 표기법 마지막 (4단계 우선순위)
- `test_entity_type_field_classification` — type ∈ {person, company, place, product, speaker} 분류 정합

### 5.2 integration test

- 같은 영상 두 번 처리 시 LLM 호출 횟수 측정 (cache hit → bootstrap 호출 0회 확인)
- 영상별 cache 분리 확인 (영상 A 의 cache 가 영상 B 처리에 부재 영향)
- Phase 3 후처리에서 chunk drift 통일 확인 (chunk 1 판카즈 + chunk 2+ 판카지 → 영상 전체 판카즈)
- spec_version 변경 시뮬레이션 (cache 파일 spec_version 수동 변경) 시 자동 재bootstrap 확인

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

## 6. 본인 확정 결정 요약 (2026-05-20)

| # | 영역 | 결정 |
|---|------|------|
| 3.1 | cache 저장 위치 | A — `~/.gurunote/entity_cache/<video_id>.json` 영상별 분리 |
| 3.2 | JSON 자료구조 | entities 통합 list (english/korean/type/source) + loanword_spec_version |
| 3.3 | 외래어 표기법 LLM 주입 | R4 — bootstrap (short version) + Phase 3 후처리 (전체 본문) |
| 3.4 | 충돌 우선순위 | 통용 표기 dict → cache → 외래어 표기법 → LLM 자유 출력 |
| 3.5 | cache invalidate | 수동 (사용자 파일 삭제) + spec_version 변경 시 자동 재bootstrap |

다음 세션 진입 시 결정 catch 부재 — 즉시 구현 진입 가능.

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
