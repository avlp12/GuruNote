# Phase 3 — Language Purity (한자/일본어 0건) Spec

작성일: 2026-05-18
HEAD 기준: `b447a11` (Phase 4a-1 부분 성공)
선행 작업: Phase 4a-1 옵션 A (xgrammar selective disable), Q2 post-process 패턴

---

## 1. 배경

본인 사용 모델 `Qwen3.6-35B-A3B-5bit` 의 한국어 출력 중 한자/일본어 토큰이
간헐적으로 잔재하는 현상이 7회+5회 검증으로 확인됐다.

### 1.1 실측 데이터 (캐시 ON 4회, 5/17)

| 회차 | 시간 | 한자/일본어 건수 | 잔재 패턴 |
|---|---|---|---|
| run 1 | 149.5초 | 3 | `这, 正, 是` (중국어) |
| run 2 | 142.7초 | 10 | `我认为很重要叠加叠加` (중국어) |
| run 3 | 145.7초 | 7 | `的挑战对吧对吧` (중국어) |
| run 4 | 144.9초 | 3 | `ず, っ, と` (일본어 히라가나) |

평균 5.75건, 범위 3~10, 캐시 OFF 환경에서도 유사 분포 (5회 평균 7.4건, 0~16).

### 1.2 사용자 영향

- 한국어 출력 안에서 한자/일본어 mix 가 가독성을 저해한다.
- daily 사용에서 다른 영상에서도 동일 패턴이 재현될 가능성이 높다.
- `_SHARED_LANG_RULES` 와 `TRANSLATION_SYSTEM_PROMPT Rule 11` 의 prompt-level
  지시는 효과 부분적이며 결정적 차단을 제공하지 못한다.

---

## 2. 원인 진단

### 2.1 Decoder-level collapse

Qwen3.6-35B 의 디코더가 한국어 컨텍스트에서 한자/일본어 토큰을 간헐적으로
생성하는 현상은 모델 자체의 토큰 분포에 기인한다 (SCD/GI-DLE 논문 계열에서
"language collapse" 로 분류). 본 현상은 prompt 강도와 무관하게 sampling
과정에서 발생한다.

### 2.2 검토한 해결책과 채택 부재 이유

| 해결책 | 채택 여부 | 이유 |
|---|---|---|
| temperature 0 (deterministic) | 부적합 | decoder-level collapse 는 sampling temperature 와 무관하게 발생. 추가로 다른 stochastic 효과 (자연스러운 paraphrase 등) 도 함께 잃음 |
| logit_bias 로 CJK 토큰 차단 | 사용 불가 | omlx 가 OpenAI 호환 logit_bias 파라미터를 지원하지 않음 (5/18 catch) |
| Smoothie Qwen 3.6 모델 교체 | 사용 불가 | 해당 모델 fine-tune 변종이 부재 (5/18 catch) |
| xgrammar 한국어 전용 grammar | 검토 보류 | grammar 정의 비용 + 한국어 다양성 손실 risk |
| omlx 캐시 OFF | 효과 부재 | 5/18 cache-off 5회 검증에서 한자 평균이 오히려 약간 증가 (5.75 → 7.4) |

### 2.3 결론

모델 측 / 서버 측 / sampling 측 차단 path 가 모두 봉쇄됐다. **출력 후처리만이
잔존 path** 가 된다.

---

## 3. 후처리 path 설계

### 3.1 전체 흐름

```
LLM 응답 (chunk)
    │
    ▼
[검출] CJK 정규식 + 예외 룰 적용
    │
    ├─ 한자/일본어 0건 → 그대로 통과
    │
    └─ 한자/일본어 N건 검출
            │
            ▼
       [Sub-path A] 사전 lookup
            │
            ├─ 모든 패턴 매핑 성공 → 치환 후 통과
            │
            └─ 일부 패턴 미등록
                    │
                    ▼
               [Sub-path B] LLM mapping (chunk 단위 retry)
                    │
                    ├─ retry 1회 통과 → 통과
                    ├─ retry 2회 통과 → 통과
                    ├─ retry 3회 통과 → 통과
                    │
                    └─ retry 3회 모두 실패
                            │
                            ▼
                       [Sub-path C] Fallback
                            ─ 해당 segment 의 영어 원문 그대로 출력
```

### 3.2 Sub-path A — 사전 lookup

#### 3.2.1 위치
- 새 파일: `gurunote/data/cjk_lookup.yaml`
- 디렉토리 신규 생성: `gurunote/data/`

#### 3.2.2 구조
```yaml
# CJK → 한국어 매핑 사전
# - 실측 회귀 패턴 우선 등록
# - 신규 패턴 catch 시 본 파일에 추가
chinese:
  "正是": "정확히"
  "对吧": "맞죠"
  "叠加": "중첩"
  "挑战": "도전"
  "认为": "생각하다"
  "重要": "중요"
  "我们": "우리"
  "需要": "필요"
  "因此": "그러므로"
  "这": "이것"
  "是": "이다"
japanese:
  "取り組んでいる": "다루고 있다"
  "取り組み": "노력"
  "ためには": "위해서는"
  "場合": "경우"
  "仕組み": "구조"
single_char_fallback:
  # 단일 한자가 한국어 한자어의 일부일 수 있어 위험.
  # 본 섹션은 LLM mapping (Sub-path B) 에 넘기는 것을 우선.
  # 단 명백히 한국어에서 사용하지 않는 단일 한자만 등록.
  "这": "이것"
  "正": "정"
  "着": "착"
```

#### 3.2.3 매칭 우선순위
1. 다어절 패턴 우선 (긴 매칭 우선)
2. 단어 단위 패턴
3. 단일 문자는 `single_char_fallback` 에서만 처리, 그 외는 Sub-path B 로 위임

#### 3.2.4 처리 비용
- 정규식 + dict lookup 만 사용. chunk 당 1ms 미만 예상.

### 3.3 Sub-path B — LLM mapping

#### 3.3.1 트리거 조건
사전 lookup 후에도 한자/일본어가 남은 경우 진입.

#### 3.3.2 호출 형식
```python
# prompt:
system = (
    "다음 한국어 문장에 한자 또는 일본어 토큰이 남아있다. "
    "본 토큰을 자연스러운 한국어로 모두 치환한 결과만 반환하라. "
    "괄호 안 한자 표기 (예: '양자역학(量子力學)') 는 그대로 둔다."
)
user = problematic_chunk_text
response_format = {"type": "text"}  # JSON 강제 부재
```

#### 3.3.3 retry 정책
- chunk 단위로 최대 3회 retry
- 각 retry 후 다시 CJK 검출 진행
- 3회 후에도 잔재 시 Sub-path C 진입

#### 3.3.4 처리 비용
- 1회 LLM 호출 ≈ chunk 평균 7~10초 추가
- 4회 검증 평균에서 30~60% chunk 가 한자 잔재 가능성 → daily 사용 최악 시
  처리 시간 1.3~3배 증가 risk
- 본인 우선순위 P1 (처리 시간 영향 최소화) 와 trade-off 명시 필요

### 3.4 Sub-path C — Fallback (영어 원문 출력)

#### 3.4.1 트리거 조건
Sub-path B retry 3회 모두 실패.

#### 3.4.2 동작
해당 segment 의 영어 원문을 그대로 출력한다.

```
[12:34] Speaker A: <영어 원문 그대로>
```

#### 3.4.3 사용자 경험
- 한국어 번역이 부재한 segment 는 영문으로 보이게 된다.
- 한자/일본어 mix 보다 영문 그대로가 가독성에서 우위.
- daily 사용에서 회귀를 결정적으로 차단한다.

---

## 4. 검출 룰

### 4.1 정규식

```python
import re

# CJK Unified Ideographs + 일본어 히라가나/가타카나
CJK_DETECT_RE = re.compile(r'[一-鿿぀-ヿ]')

# 괄호 안 한자 표기 (예외)
BRACKETED_CJK_RE = re.compile(r'\([^)]*[一-鿿぀-ヿ][^)]*\)')
```

### 4.2 검출 알고리즘

```python
def detect_cjk_residue(text: str) -> list[str]:
    """괄호 안 한자 표기를 제외한 CJK 잔재 catch.

    Returns:
        잔재 CJK 토큰 리스트. 빈 리스트면 통과.
    """
    # 괄호 안 한자 표기를 임시 placeholder 로 치환
    masked = BRACKETED_CJK_RE.sub("[BRACKETED]", text)
    return CJK_DETECT_RE.findall(masked)
```

### 4.3 예외 처리 catch

- `양자역학(量子力學)` 같은 한국어(한자) 병기 표기는 보존
- `슈나이더 일렉트릭(Schneider Electric)` 같은 영문 furigana 는 무관 (한자 부재)
- 본인 memory `feedback_first_occurrence_furigana.md` 와 정합

---

## 5. 단위 결정

| 처리 단계 | 단위 | 이유 |
|---|---|---|
| 검출 | chunk 단위 | LLM 응답이 chunk 단위로 도착 |
| Sub-path A (사전 lookup) | chunk 단위 | 비용 매우 낮음, 전체 적용 가능 |
| Sub-path B (LLM mapping) retry | chunk 단위 | 본인 결정사항. segment 단위는 호출 수 폭증 |
| Sub-path C (Fallback) | **segment 단위** | chunk 통째 fallback 은 손실 과대, segment 만 영문 |

---

## 6. 통합 위치

### 6.1 호출 흐름

```
translate_transcript() [line 620]
    │
    ▼ chunk_segments() 로 chunk 분할
    │
    ▼ 각 chunk 별 _call_llm_with_index_mapping() 호출 [line 1086]
    │
    ▼ chunk 응답 모임
    │
    ▼ <신규> post_process_cjk(chunk_outputs)  ← 본 spec 의 처리 위치
    │
    ▼ _strip_repeated_annotations() [line 596, 기존 Q2 post-process]
    │
    ▼ return [line 676]
```

### 6.2 신규 함수 시그니처

```python
def post_process_cjk(
    chunk_outputs: list[str],
    segments: list[Segment],
    config: LLMConfig,
    log: Optional[ProgressFn] = None,
) -> list[str]:
    """한자/일본어 후처리 — Sub-path A + B + C 순차 적용.

    Args:
        chunk_outputs: chunk 별 번역 결과
        segments: 원본 segments (Sub-path C fallback 시 영어 원문 참조)
        config: LLMConfig (Sub-path B LLM 호출용)
        log: 진행 로그 함수

    Returns:
        후처리된 chunk_outputs (한자/일본어 0건 보장 또는 영문 fallback)
    """
```

### 6.3 사전 파일 로딩

```python
# gurunote/llm.py 상단
import yaml
from pathlib import Path

_CJK_LOOKUP_PATH = Path(__file__).parent / "data" / "cjk_lookup.yaml"
_CJK_LOOKUP_CACHE = None

def _load_cjk_lookup() -> dict:
    global _CJK_LOOKUP_CACHE
    if _CJK_LOOKUP_CACHE is None:
        with open(_CJK_LOOKUP_PATH) as f:
            _CJK_LOOKUP_CACHE = yaml.safe_load(f)
    return _CJK_LOOKUP_CACHE
```

---

## 7. 처리 시간 영향 catch

### 7.1 시나리오별 예상

| 시나리오 | chunk 당 추가 비용 | 전체 처리 시간 영향 |
|---|---|---|
| Sub-path A 만 적용 (잔재 패턴이 사전에 모두 등록된 경우) | <1ms | 무시 가능 |
| Sub-path B 1회 추가 호출 (chunk 1개) | ~7초 | +5% |
| Sub-path B 모든 chunk 호출 (최악) | ~7초 × 20 | +96% (약 2배) |
| Sub-path C fallback (LLM 호출 부재) | 0 | 무시 가능 |

### 7.2 trade-off

- 사전 lookup 의 적중률이 핵심 변수. 5/17 4회 검증의 잔재 패턴 (`正是, 对吧, 叠加, 挑战, 我们, 需要, 取り組んでいる` 등) 을 우선 등록 시 70~80% 적중 기대.
- 본인 우선순위 P0 (한자 0건) 와 P1 (처리 시간 최소화) trade-off 명시.

---

## 8. 검증 계획

### 8.1 자동 검증

`docs/wip/checkpoint4_realvideo_verify.py` 의 Test 4 (한자/일본어 잔재) 가 그대로 사용 가능.
구현 후 4회 검증 진행하여 다음 catch:
- Test 4: 모든 회차 0건 달성 여부
- 처리 시간: 캐시 ON 145.7초 baseline 대비 증가율
- Sub-path 별 발동 빈도 (로그 catch)

### 8.2 사전 적중률 catch

각 검증 회차에서 다음 로그 catch:
```
[CJK post-process] chunk N: A-path 적중 X건, B-path retry Y회, C-fallback Z segments
```

### 8.3 회귀 검증

- line count 정합 유지 (288)
- timestamp 완전성 유지
- furigana 표기 보존 (Sub-path A 가 괄호 안 한자 제외 확인)
- 한국어(영문) 첫 등장 병기 보존

---

## 9. 미해결 사항 + 후속 trajectory

### 9.1 미해결

- Sub-path A 사전의 초기 등록 패턴 결정 (어떤 패턴이 충분한지)
- Sub-path B 의 retry 가 결정적 수렴 보장 부재 (3회 모두 실패 가능성)
- Sub-path C fallback 발동 시 사용자 영향 측정 부재

### 9.2 후속 trajectory

- Phase 3-후속 ①: 사전 누적 (daily 사용에서 신규 패턴 발견 시 추가)
- Phase 3-후속 ②: 자동 사전 보강 (LLM 으로 새 패턴 자동 등록)
- Phase 3-후속 ③: omlx logit_bias 지원 추가 시 path 전환 (token-level 차단)

---

## 10. 미적용 결정사항

본 spec 은 **구현 진입 결정 부재** 상태이다. 본인 검토 후 다음 결정 필요:

1. 본 spec 의 path A+B+C 구성 정합 여부
2. 사전 초기 등록 패턴 범위 (5/17 잔재 패턴만 vs 더 확대)
3. Sub-path B 의 LLM mapping 진입 여부 (처리 시간 trade-off)
4. Sub-path C fallback 의 사용자 경험 수용 여부

본인 검토 결과를 받은 뒤 구현 commit 진입.
