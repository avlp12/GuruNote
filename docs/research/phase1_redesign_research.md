# GuruNote Phase 1 Redesign — 외부 연구 자료

**작성일:** 2026-05-12
**목적:** Phase 1 (chunk timestamp validation + retry) 의 본질적 한계를 외부 자료를 기반으로 재진단하고, 가능한 redesign 경로들을 비교 분석한다.
**대상:** Claude Code 가 GuruNote 현재 코드 + 본 spec + 다른 채널의 RLM Phase 2 spec 을 종합 분석하여 적용 방향을 추천한다.

---

## 1. 문제 정의

### 1.1 5/12 verify 에서 확인된 두 가지 증상

**증상 A — Truncation (응답 잘림):**

NVIDIA GTC 17분 영상 처리 시 pipeline.log:

```
[21:09:52]    ↳ 청크 1/3 번역 중…
[21:10:23]    ⚠ 청크 1 timestamp 107개 누락 — retry 1/3
[21:11:01]    ⚠ 청크 1 timestamp 4개 누락 — retry 2/3
[21:11:03]    ↳ 청크 2/3 번역 중…
[21:14:37]    ⚠ 청크 2 timestamp 72개 누락 — retry 1/3
[21:15:07]    ↳ 청크 3/3 번역 중…
[21:15:15]    ⚠ 청크 3 timestamp 1개 누락 — retry 1/3
```

| chunk | 입력 segments | LLM 1차 응답 | retry 후 |
|-------|---------------|---------------|----------|
| 1 | ~140 | ~33 (~23%) | 4 missing |
| 2 | ~120 | ~48 (~40%) | 0 missing |
| 3 | ~30 | ~29 (~97%) | 0 missing |

**패턴:** chunk 가 클수록 truncation 비율이 증가. chunk 3 은 거의 정상.

**증상 B — Content drift (내용 어긋남):**

retry 로 누락된 timestamp 가 채워졌지만, 결과 markdown 에서:

```
[02:10] 판카즈 샤르마: 몇 가지 예를 들 수 있습니다. 우선 대형 데이터 센터의 경우...
        ← 영어 [03:10] "Multiple examples I can give you" 의 번역

[02:16] 판카즈 샤르마: 이 열을 제거하기 위해 냉각 시스템이 필요하죠...
        ← 영어 [03:22] "So you need to take out the heat..." 의 번역

[00:23] 판카즈 샤르마: 아주 좋습니다. 지난 이틀간은 매우 분주했지만...
[00:25] 판카즈 샤르마: 훌륭합니다. 지난 이틀간 정말 바쁘고, 많은 정보가 있었지만...
        ← 같은 영어 [00:25] "Excellent. It's been the last two days, super busy."
           의 번역이 두 timestamp 에 등장
```

**패턴:** timestamp 는 정합 (Phase 1 의 strict filter 통과), 그러나 번역 내용이 다른 segment 의 것 또는 중복.

### 1.2 현재 Phase 1 의 본질적 한계

5/12 push 한 Phase 1 (3f3f04d) 의 작동:
- timestamp 완전성 검증 (모든 expected timestamp 가 응답에 있는지)
- 누락 시 retry (최대 3회)
- strict filter merge (original 우선, missing_ts 외 drop)
- 3회 실패 시 marker insert

**Phase 1 이 잡는 것:** timestamp 완전성 (정보 손실 방지)

**Phase 1 이 잡지 못하는 것:** content 정합성
- LLM 이 timestamp 와 content 의 매핑을 자유롭게 출력함
- timestamp 가 맞다고 해서 content 도 맞다는 보장 없음
- strict filter 는 timestamp 존재 여부만 검증하고, content 정확성은 검증하지 못함

### 1.3 5/12 진단 결과 (Claude Code)

본질 cause 세 가지가 확정됨:

1. **LLM truncation 패턴**
   - chunk 1 의 1차 응답: ~33 segments 만 응답하고 멈춤
   - chunk 가 클수록 truncation 비율이 증가
   - 원인: chunk 크기 자체가 LLM 의 attention 한계에 부담을 줌

2. **Retry merge 의 strict filter 한계**
   - timestamp 존재 여부만 catch
   - content 정합성은 검증하지 못함
   - LLM 1차 응답의 content drift 도 catch 하지 못함

3. **MAX_TOKENS 의 한계**
   - 이미 16384 (default 의 2배)
   - 더 키워도 LLM 의 attention 한계는 해결되지 않음

---

## 2. 외부 검색 결과 — 6가지 핵심 패턴

사용자 의도 ("LLM/AI 논문, 커뮤니티, SNS, 뉴스, 참고서적 모두 찾아서 이 문제 해결할 아이디어")에 정합하게 6가지 출처 카테고리에서 수집:

1. **Vimeo Engineering Blog** — 실무 production 사례
2. **OpenAI/Azure docs + Google ADK issue tracker** — LLM API 의 본질적 동작
3. **arXiv + Qwen 기술 보고서** — 학술 논문
4. **rockbenben/subtitle-translator** — 오픈소스 프로젝트
5. **Instructor + Outlines + OpenRouter** — Structured output 도구
6. **Cerlancism/chatgpt-subtitle-translator** — 오픈소스 패턴

---

### 패턴 1: Vimeo 3-Phase Split-Brain Architecture ★★★

**출처:**
- Vimeo Engineering Blog (Tanushree Nori, 2026-01-16): https://medium.com/vimeo-engineering-blog/how-we-built-ai-powered-subtitles-at-vimeo-ff11f1d64b2a
- ByteByteGo 분석 (2026-03-11): https://blog.bytebytego.com/p/how-vimeo-implemented-ai-powered
- MLOps World Field Notes (2025-12-23): https://mlopsworld.com/post/beyond-just-call-an-llm-vimeos-production-subtitle-engine/

**Vimeo 가 발견한 본질:**

> "Vimeo's key architectural insight was that asking a single LLM prompt to both translate fluently and preserve the exact line count was a losing battle. Fluency and timing are competing objectives, and when you optimize for both in a single pass, you compromise both."

→ **번역 품질과 timing 보존은 서로 경쟁하는 목표라서, 한 번의 LLM 호출에서 둘 다 최적화하려고 하면 둘 다 망친다.**

**Vimeo 의 3-Phase 아키텍처:**

```
Phase 1: Smart Chunking (코드, LLM 없음)
  - 문장 경계 (10가지 구두점 시스템) + 화자 경계 + 언어 동질성
  - 3~5 라인의 logical thought blocks 로 분할
  - 핵심: "LLM 이 complete thought 를 보기 전에는 번역을 시작하지 않음"

Phase 2: Creative Translation (LLM 호출 1회)
  - 단일 지시: "translate for meaning"
  - 라인 수 제약 없음, 구조 제약 없음
  - 출력: 자연스러운 번역 블록 (구조 변경 가능)
  - 핵심: 의미 정확성 + 자연스러움에만 집중

Phase 3: Line Mapping (LLM 호출 2회)
  - 입력: 원본 N라인 + timestamps + Phase 2 의 번역 블록
  - 단일 지시: "Break it back into N lines to match the source rhythm"
  - 라인 수만 enforcement, 의미 검증 없음
  - 핵심: timing 정확성 + 라인 수 보존
```

**Phase 3 의 작동:**
- 첫 시도에서 95% 성공
- 실패한 5% → correction loop (mismatch feedback 과 함께 retry) → 32% 추가 회복
- 그래도 실패 → rule-based deterministic splitter (LLM 호출 없이)
  - 빈 라인은 마지막 valid content 로 채움
  - 단순 character-based 분할 fallback

**Vimeo 의 핵심 통찰:**

> "We stopped asking, 'How do we make the LLM get it right the first time?' and started asking, 'What happens when it doesn't?'"

→ **LLM 이 실패할 것을 가정하고 시스템을 설계한다.**

**Phase 2 vs Phase 3 의 단일 책임 분리:**

| Phase | 책임 | 제약 | 검증 |
|-------|------|------|------|
| 2 | 의미 정확성 + 자연스러움 | 없음 | LLM-as-judge (선택) |
| 3 | 라인 수 + timing | 정확히 N개 라인 | 라인 수 매칭 |

**GuruNote 적용 시뮬레이션:**

```python
def translate_chunk_vimeo_pattern(chunk: List[Segment], context: str) -> str:
    """3단계 번역: chunking → 의미 → 라인 매핑."""

    # Phase 1: Smart Chunking
    # GuruNote 의 chunk_segments 가 이 역할을 함

    # Phase 2: Creative Translation (라인 수 제약 없음)
    source_text = "\n".join(f"{s.speaker}: {s.text}" for s in chunk)
    phase2_prompt = f"""다음 영어 transcript 를 한국어로 번역하세요.
의미와 자연스러운 한국어에 집중하세요. 라인 구조를 유지할 필요 없습니다.
자연스러운 한국어를 위해 문장을 합치거나 분리해도 됩니다.

원본:
{source_text}

번역 (한국어만, 주석 없이):"""
    fluent_korean = _call_llm(config, phase2_prompt)

    # Phase 3: Line Mapping (라인 수 강제)
    target_count = len(chunk)
    phase3_prompt = f"""이 한국어 번역을 정확히 {target_count}개 라인으로
나눠서 원본 라인 구조에 맞추세요.

원본 ({target_count}개 라인):
{chr(10).join(f"{i+1}. {s.speaker}: {s.text}" for i, s in enumerate(chunk))}

자연스러운 한국어 번역:
{fluent_korean}

정확히 {target_count}개 라인으로 출력 (번호 매김):
1. [화자]: [한국어 텍스트]
2. [화자]: [한국어 텍스트]
..."""
    mapped = _call_llm(config, phase3_prompt)

    # 검증: 라인 수 매칭
    lines = parse_numbered_lines(mapped)
    if len(lines) != target_count:
        # Correction loop with feedback
        for retry in range(3):
            feedback = f"이전 출력이 {len(lines)}개 라인이었습니다. " \
                       f"정확히 {target_count}개가 필요합니다."
            mapped = _call_llm(config, phase3_prompt + "\n" + feedback)
            lines = parse_numbered_lines(mapped)
            if len(lines) == target_count:
                break

    # 그래도 실패 시 deterministic fallback
    if len(lines) != target_count:
        lines = deterministic_split(fluent_korean, target_count)

    # timestamp 부착 (클라이언트 측, LLM 없음)
    result = []
    for segment, korean_line in zip(chunk, lines):
        ts = f"[{_format_ts(segment.start)}]"
        result.append(f"{ts} {segment.speaker}: {korean_line}")
    return "\n".join(result)
```

**현재 GuruNote 와의 차이:**

| 항목 | 현재 | Vimeo 패턴 적용 |
|------|------|-----------------|
| LLM 호출 수 / chunk | 1 (+ retry up to 3) | 2 (Phase 2 + Phase 3, + retry up to 3) |
| timestamp 출력 주체 | LLM | 클라이언트 (zip) |
| 라인 수 enforcement | 없음 (timestamp 매칭만) | Phase 3 에서 직접 enforcement |
| Content drift 차단 | 없음 (strict filter 는 presence 만 catch) | Phase 3 의 라인 수 매칭 + 순서 매핑 |
| Fallback | marker insert | deterministic split |
| 코드 분량 | 현재 ~145L (Phase 1 helpers) | 추정 ~150~200L |

**GuruNote 적용 가능성: ★★★ 매우 높음**

장점:
- Content drift 의 근본 원인 (LLM 의 timestamp+content 자유 출력) 을 차단
- timestamp 는 클라이언트가 결정론적으로 부착하므로 drift 가 불가능
- Correction loop 가 사용자 RULE 5 에 정합 (판단이 필요한 작업만 모델 사용)
- Deterministic fallback 이 RULE 12 에 정합 (크게 실패)

단점:
- LLM 호출이 2배로 증가 (Phase 2 + Phase 3)
- chunk 당 처리 시간이 2배 증가
- 17분 영상이 12~14분 처리 (현재 7분)
- 비용 증가 (qwen self-host 시 무료지만 Claude/Gemini 사용 시 영향)

---

### 패턴 2: finish_reason Continuation 패턴 ★★★

**출처:**
- OpenAI API docs: https://apxml.com/courses/intro-large-language-models/chapter-5-using-pre-trained-llms/interpreting-llm-responses
- Azure OpenAI guide (Ankit Marwaha, 2024-12-28): https://medium.com/@ankitmarwaha18/overcoming-response-truncation-in-azure-openai-a-comprehensive-guide-cb85249cf007
- Google ADK Issue #4482 (LiteLLM streaming silently drops): https://github.com/google/adk-python/issues/4482
- LiteLLM docs: https://docs.litellm.ai/docs/completion/input
- LangGraph state machine 패턴 (Durgaprasad Gopi, 2025-06-14): https://medium.com/@gopidurgaprasad762/overcoming-output-token-limits-a-smarter-way-to-generate-long-llm-responses-efe297857a76

**핵심:**

LLM API 는 응답이 max_tokens 에 도달하면 `finish_reason = "length"` 라는 명시적 신호를 보낸다. 이 신호를 받아서 continuation 을 돌리는 것이 production 표준 패턴이다.

> "Important: when using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message... the message content may be partially cut off if finish_reason='length', which indicates the generation exceeded max_tokens or the conversation exceeded the max context length." — LiteLLM docs

**LangGraph state machine 패턴:**

```python
def initial_generation(state):
    response = llm.invoke(messages)
    return {
        "generated_text": response.content,
        "finish_reason": response.response_metadata['finish_reason']
    }

def continue_generation(state):
    """출력이 잘렸으면 이어서 생성."""
    partial_text = "\n".join(state["generated_text"].split('\n')[:-1])  # 마지막 라인 제거
    messages = [
        SystemMessage(content=state['system_prompt']),
        AIMessage(content=partial_text),
        SystemMessage(content="Continue")
    ]
    response = llm.invoke(messages)
    return {...}

# State machine: length → continue, stop → END
```

**GuruNote 적용 시뮬레이션:**

```python
def _call_llm_with_continuation(config, system, user, max_tokens):
    """finish_reason='length' 시 자동 continuation."""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    accumulated = ""
    max_continuations = 3

    for cont in range(max_continuations + 1):
        response = _call_llm_once(config, messages, max_tokens)
        accumulated += response.content
        finish_reason = response.finish_reason

        if finish_reason == "stop":
            return accumulated
        elif finish_reason == "length":
            # 마지막 incomplete 라인 제거 (불완전 timestamp 차단)
            lines = accumulated.split("\n")
            if lines and not _TS_LINE_PREFIX_RE.match(lines[-1]):
                accumulated = "\n".join(lines[:-1])
            # Continuation prompt
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
                {"role": "assistant", "content": accumulated},
                {"role": "user", "content": "Continue from the last complete [timestamp] line. Do not repeat previous content."},
            ]
        else:
            log(f"⚠ unexpected finish_reason: {finish_reason}")
            break

    return accumulated
```

**현재 GuruNote 와의 차이:**

| 항목 | 현재 | finish_reason 적용 |
|------|------|---------------------|
| Truncation 검출 | timestamp 누락 비율 (간접 추정) | finish_reason='length' (직접 신호) |
| Continuation | 누락된 segment 로 retry | 이어서 생성 (continuation) |
| Content drift 위험 | 있음 (retry 가 다른 content 가져올 수 있음) | 낮음 (이어쓰기는 새로 시작이 아님) |
| 코드 분량 | ~30L retry loop | ~25L continuation loop |

**GuruNote 적용 가능성: ★★★ 매우 높음**

장점:
- Truncation 의 명시적 신호를 catch (간접 추정이 아님)
- Content drift 차단 (continuation 은 이어쓰기, 새로 시작이 아님)
- 단순 (코드 ~25L)

단점:
- OpenAI-compatible API 가 finish_reason 을 정확히 노출해야 함
- 사용자의 qwen3.6-35b 의 OpenAI compat endpoint 가 이를 지원하지 않으면 작동하지 않음

**확인이 필요한 것:**
- 사용자의 LLM endpoint 가 finish_reason 을 정확히 반환하는지
- 만약 지원하지 않으면, max_tokens 와 response length 비교로 추정 가능

---

### 패턴 3: Qwen Long-Context Critical Threshold ★★

**출처:**
- arXiv 2601.15300 "Intelligence Degradation in Long-Context LLMs" (2026): https://arxiv.org/pdf/2601.15300
- Qwen2.5-1M Technical Report (arXiv 2501.15383): https://arxiv.org/pdf/2501.15383
- arXiv 2505.20276 "Does quantization affect models' performance on long-context tasks?" (2025)

**핵심 발견:**

> "Through comprehensive experiments on a mixed dataset (1,000 samples covering 5%-95% of context length), we precisely identify the critical threshold for Qwen2.5-7B at 40-50% of maximum context length, where F1 scores drop catastrophically from 0.55-0.56 to 0.3—a 45.5% performance degradation."

→ **Qwen 계열 모델은 max context 의 40~50% 지점에서 attention 이 catastrophic 하게 떨어진다.**

이 현상을 "shallow long-context adaptation" 이라 부른다 — 모델이 짧은 컨텍스트에 주로 적응되어, 임계 길이에 도달하면 성능이 급격히 떨어진다.

**추가 사실:**
- 4-bit quantization 시 long-context tasks 에서 최대 59% 성능 손실
- 영어가 아닌 언어 (한국어 등) 에서는 손실이 더 큼
- Qwen 2.5 72B 는 BNB-nf4 에서 robust 하지만, 7B/35B 는 변동성이 큼

**GuruNote 관련:**
- 현재 모델: qwen3.6-35b-q5 (5-bit quantization)
- Quantization + multilingual translation 의 본질적 위험
- chunk 12000 chars ≈ 4000~5000 tokens (context window 262144 의 ~2%)
- 입력 절대량은 작지만, **출력의 attention 한계**는 별개 문제

**GuruNote 적용 시뮬레이션:**

```python
# Option A: chunk 크기 축소 (단순)
DEFAULT_CHUNK_CHAR_LIMIT = 6000  # 12000 → 6000
# 효과: LLM attention 정합, output truncation 부재
# 단점: 컨텍스트 손실 (entity 일관성 회귀)

# Option B: 청크 내부에서 다시 분할
def translate_chunk_split_output(chunk, max_output_segments=30):
    """청크 내부를 30 segments 단위로 다시 분할 후 LLM 호출."""
    sub_chunks = [chunk[i:i+max_output_segments]
                  for i in range(0, len(chunk), max_output_segments)]
    results = []
    for sub in sub_chunks:
        result = _call_llm(...)
        results.append(result)
    return "\n".join(results)
```

**GuruNote 적용 가능성: ★★ 높음 (단점 있음)**

장점:
- 학술 근거 명확 (40~50% 임계)
- 단순 fix (1줄 변경)

단점:
- Chunk 축소는 컨텍스트 손실 (entity 일관성 회귀)
- 사용자 5/11 통찰 "GuruNote = LLM 하네스" 본질에서, chunk 축소는 Phase 2 (entity cache) 의 문제를 가속화
- 패턴 1/2 와 결합하면 chunk 크기 축소가 불필요해질 수 있음

---

### 패턴 4: Adjacent Context Injection ★★

**출처:**
- rockbenben/subtitle-translator: https://github.com/rockbenben/subtitle-translator
- machinewrapped/llm-subtrans: https://github.com/machinewrapped/llm-subtrans
- Cerlancism/chatgpt-subtitle-translator: https://github.com/Cerlancism/chatgpt-subtitle-translator

**핵심:**

> "Context-Aware Translation (AI models only) sends subtitles to the LLM in batches with preceding and succeeding context, ensuring more coherent character dialogue and natural tone."
>
> "Concurrent Lines: Maximum lines translated simultaneously (default: 20)
> Context Lines: Lines included per batch for context (default: 50). Higher values improve coherence but may exceed token limits."
>
> "⚠️ Tip: Models under 70B parameters may produce misaligned output. Mainstream online large models are recommended."

→ **각 chunk 에 인접 chunk 의 context lines (~50개) 를 prepend 함으로써 화자/entity/톤 일관성을 보장.**
→ **70B 미만 모델은 misalignment 위험이 있다고 명시 (qwen3.6-35b 도 위험권).**

**GuruNote 적용 시뮬레이션:**

```python
def translate_chunk_with_context(chunks: List[List[Segment]], chunk_idx: int):
    """이전 chunk 의 마지막 ~10 segments 를 context 로 prepend."""
    current = chunks[chunk_idx]
    context_segments = []

    # 이전 chunk 의 마지막 N segments (context only, 번역 대상 아님)
    if chunk_idx > 0:
        prev = chunks[chunk_idx - 1]
        context_segments = prev[-10:]  # 마지막 10 segments

    if context_segments:
        context_text = "\n".join(
            f"[{_format_ts(s.start)}] {s.speaker}: {s.text}"
            for s in context_segments
        )
        translate_text = "\n".join(
            f"[{_format_ts(s.start)}] {s.speaker}: {s.text}"
            for s in current
        )

        prompt = f"""이전 컨텍스트 (번역하지 마세요, 참고용입니다):
{context_text}

아래만 한국어로 번역하세요:
{translate_text}"""
    else:
        prompt = ...

    return _call_llm(prompt)
```

**현재 GuruNote 와의 차이:**

| 항목 | 현재 | Adjacent Context 적용 |
|------|------|------------------------|
| Chunk 간 컨텍스트 | 영상 메타 (게시일/챕터/자막) | 영상 메타 + 인접 chunk |
| Entity 일관성 | Layer 13 첫 등장 영문 병기 | + 인접 chunk 의 실제 표기 참조 |
| 화자 표기 일관성 | Layer 11 prompt 강화 | + 인접 chunk 의 실제 표기 참조 |
| 코드 분량 | 영상 메타만 catch | + ~15L |

**GuruNote 적용 가능성: ★★ 높음**

장점:
- 화자/entity 표기 일관성 (스키에더 vs 슈나이더, 티파니 vs 티파즈) 차단
- Phase 2 (RLM entity cache) 와 부분 정합
- 단순한 코드 추가 (~15L)

단점:
- Context lines 증가 → chunk 크기 증가 → 본질 cause 가속화 위험
- Phase 2 (RLM) 가 더 본질적 해결책 → Adjacent context 가 의미 없어질 수 있음

---

### 패턴 5: Structured Output (JSON Array Index Mapping) ★★★

**출처:**
- Cerlancism/chatgpt-subtitle-translator: https://github.com/Cerlancism/chatgpt-subtitle-translator
- Instructor library: https://tutorials.technology/tutorials/tutorials/structured-output-llm-python-2026.html.html
- Outlines (FSM-based constrained decoding, 2026-03-07): https://dev.to/shrsv/taming-llms-how-to-get-structured-output-every-time-even-for-big-responses-445c
- OpenRouter response-healing (2026-03-25): https://dev.to/lovanaut55/openrouter-structured-output-broke-before-translation-quality-did-3-layers-of-defense-for-1cdb
- LM Studio Structured Output: https://lmstudio.ai/docs/developer/openai-compat/structured-output

**Cerlancism 의 입출력 형식:**

```json
// LLM 입력 (timestamp 없음, 순서만)
{
  "inputs": [
    "おはようございます。",
    "お元気ですか？",
    "はい、元気です。",
    "今日は天気がいいですね。"
  ]
}

// LLM 출력 (같은 길이 JSON 배열)
{
  "outputs": [
    "Good morning.",
    "How are you?",
    "Yes, I'm fine.",
    "The weather is nice today."
  ]
}

// 클라이언트 측: zip(timestamps, outputs) 으로 결정론적 매핑
```

**핵심 통찰:**

> "SRT indices and timestamps are stripped or simplified before sending to the model, reducing tokens. Lines are batched together into a single prompt - removing repeated per-entry overhead."
>
> "Structured output modes enforce a schema so the model returns only the translated text."

→ **LLM 이 timestamp 를 출력하지 않으므로 drift 가 불가능하다.**

**Outlines (FSM 기반 constrained decoding) 의 추가 강점:**

> "Resuming on truncation: If an LLM's output is cut off (e.g., due to token limits), Outlines saves the FSM state and resumes generation, ensuring the final output stays valid."

→ Truncation 시 FSM state 를 저장하고 resume 가능. JSON 구조 보장 + truncation 안전.

**GuruNote 적용 시뮬레이션:**

```python
import json

def translate_chunk_index_mapping(chunk: List[Segment], context: str) -> List[str]:
    """timestamp 없이 순서만 매개로 매핑."""
    # 1. LLM 에 inputs 배열만 전달 (timestamps 없음)
    inputs = [f"{s.speaker}: {s.text}" for s in chunk]
    request = {"inputs": inputs}

    # 2. JSON schema 강제
    response_schema = {
        "type": "object",
        "properties": {
            "outputs": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": len(inputs),
                "maxItems": len(inputs),
            }
        },
        "required": ["outputs"]
    }

    prompt = f"""각 input 을 한국어로 번역하세요.
JSON 으로 반환: {{"outputs": [korean1, korean2, ...]}}
출력 배열은 반드시 정확히 {len(inputs)}개 항목을 같은 순서로 포함해야 합니다.

{context}

Input:
{json.dumps(request, ensure_ascii=False, indent=2)}

Output:"""

    response_text = _call_llm_with_schema(prompt, response_schema)
    parsed = json.loads(response_text)
    outputs = parsed["outputs"]

    # 3. 길이 검증 (drift 차단의 핵심)
    if len(outputs) != len(inputs):
        for retry in range(3):
            feedback = f"이전 출력은 {len(outputs)}개 항목이었습니다. " \
                       f"{len(inputs)}개가 필요합니다."
            response_text = _call_llm_with_schema(prompt + feedback, response_schema)
            parsed = json.loads(response_text)
            outputs = parsed["outputs"]
            if len(outputs) == len(inputs):
                break

    if len(outputs) != len(inputs):
        # Fallback: 길이 맞추기
        if len(outputs) < len(inputs):
            outputs += ["[번역 누락]"] * (len(inputs) - len(outputs))
        else:
            outputs = outputs[:len(inputs)]

    return outputs

def translate_transcript_index_mapping(...):
    """전체 transcript 의 index mapping 변환."""
    for i, chunk in enumerate(chunks):
        outputs = translate_chunk_index_mapping(chunk, context_block)

        # 4. 클라이언트 측 timestamp 부착 (LLM 없음)
        for segment, korean_text in zip(chunk, outputs):
            ts = f"[{_format_ts(segment.start)}]"
            translated_parts.append(f"{ts} {korean_text}")
```

**현재 GuruNote 와의 차이:**

| 항목 | 현재 | Structured Output 적용 |
|------|------|-------------------------|
| LLM 입력 형식 | "[ts] speaker: text" 라인 | JSON {"inputs": [...]} |
| LLM 출력 형식 | "[ts] speaker: text" 라인 | JSON {"outputs": [...]} |
| Timestamp 출력 주체 | LLM | 클라이언트 (zip) |
| 검증 | timestamp presence | 배열 길이 |
| Drift 차단 | timestamp 매칭 (부분) | 순서 매핑 (완전) |
| 코드 분량 변경 | ~50L 추가 (prompt + parsing 재설계) | ~50L |
| 기존 Phase 1 코드 | 대부분 무의미해짐 | retry/fallback 로직만 보존 |

**GuruNote 적용 가능성: ★★★ 매우 높음**

장점:
- Content drift 의 근본 원인 (LLM 의 timestamp+content 자유 출력) 을 근본 차단
- 사용자 RULE 5 에 정합 (코드로 답할 수 있는 것은 코드로)
- 사용자 user_preferences "외부 변수로 취급" 에 정합 (timestamp 가 LLM 컨텍스트에 없음)
- Truncation 시 길이 미스매치라는 명확한 신호

단점:
- 현재 Phase 1 코드의 ~80% 가 대체됨 (strict filter 등 무의미)
- Prompt 재설계 필요 (TRANSLATION_SYSTEM_PROMPT)
- 출력 parser 재작성 (collect_blocks 등)
- qwen3.6-35b 의 JSON mode 지원 여부 확인 필요 (LM Studio 는 strict 지원 안 할 수 있음)
- 패턴 1 (Vimeo) 의 Phase 3 와 정합 → 결합 가능

---

### 패턴 6: Two-Stage Planning + Translation ★

**출처:**
- Cerlancism/chatgpt-subtitle-translator: https://github.com/Cerlancism/chatgpt-subtitle-translator
- Vimeo 7-Layer Architecture: https://tmlsinsights.substack.com/p/beyond-just-call-an-llm-vimeos-7

**Cerlancism 패턴:**

> "Each window produces a batch summary (characters, locations, events, tone). Summaries are consolidated and used to generate a refined translation instruction. Translation - Translates using the enriched instruction. After the first batch, a sample of the output is checked to confirm the target language before proceeding."

→ **두 단계: (1) 인물/장소/이벤트/톤 요약 생성 → (2) 정제된 instruction 으로 번역.**

**Vimeo 7-Layer 의 추가 통찰:**

> "Vimeo client had a company name 'Aeron' that the speech-to-text model sometimes rendered as 'AERON,' 'Aeron,' and 'A-R-O-N.' Without intervention, the Spanish subtitles had three different variations. Adding Aeron to the custom vocabulary fixed it at transcription and reinforced it at translation."

→ **사전 정의된 glossary + 화자 표기 일관성이 핵심.**

**GuruNote 적용 시뮬레이션:**

```python
def translate_with_planning(transcript: Transcript):
    chunks = chunk_segments(transcript.segments)

    # Stage 1: Planning Pass (chunk 별)
    chunk_summaries = []
    for chunk in chunks:
        summary_prompt = f"""다음 transcript chunk 를 분석하세요.
다음을 추출하세요:
- 인물 (역할/직책 포함)
- 조직 / 고유명사
- 주제 / 이벤트
- 톤 (formal / casual / technical)

JSON 으로 반환: {{"characters": [...], "organizations": [...], "topics": [...], "tone": "..."}}

{chunk_text}"""
        summary = _call_llm(summary_prompt)
        chunk_summaries.append(summary)

    # Stage 2: Consolidation (단일 LLM 호출)
    consolidate_prompt = f"""이 chunk 요약들을 통합된 glossary 로 정리하세요.

Chunk 요약들:
{chunk_summaries}

JSON 으로 반환: {{
  "glossary": {{
    "<영문 용어>": "<한국어 번역>"
  }},
  "speakers": {{
    "<Speaker A>": "<영문 병기된 한국어 이름>"
  }},
  "tone": "..."
}}"""
    glossary = _call_llm(consolidate_prompt)

    # Stage 3: Translation (정제된 instruction 으로)
    for i, chunk in enumerate(chunks):
        translate_prompt = f"""다음 glossary 를 사용하여 한국어로 번역하세요:
{glossary}

{chunk_text}"""
        translated = _call_llm(translate_prompt)
```

**현재 GuruNote 와의 차이:**

| 항목 | 현재 | Two-Stage Planning 적용 |
|------|------|--------------------------|
| Pre-translation 단계 | 영상 메타만 | + 인물/조직/톤 요약 |
| Entity 표기 일관성 | Layer 13 prompt | + glossary |
| LLM 호출 수 | N chunks × (1+retry) | (N planning) + 1 consolidate + (N translation) |
| 코드 분량 | — | + ~100L |

**GuruNote 적용 가능성: ★ 중간**

장점:
- Entity 표기 일관성 (Phase 2 의 본질) 차단
- 다른 채널 RLM Phase 2 spec 과 정합

단점:
- LLM 호출 수가 크게 증가 (N → 2N+1)
- 처리 시간 증가 (큰 trade-off)
- 비용 증가
- 사용자 RULE 2 (단순함이 먼저) 위반 가능성

---

## 3. 종합 비교

### 3.1 패턴별 본질 요약

| # | 패턴 | 무엇을 잡는가 | 적용 가능성 | 코드 분량 | LLM 호출 영향 |
|---|------|---------------|-------------|-----------|---------------|
| 1 | Vimeo 3-Phase Split-Brain | content drift + 라인 수 | ★★★ | ~150~200L | 2× per chunk |
| 2 | finish_reason Continuation | truncation 명시적 검출 | ★★★ | ~25L | 1~3× per chunk |
| 3 | Chunk 크기 축소 (40-50% 임계) | LLM attention 한계 회피 | ★★ | 1L | 2× chunks |
| 4 | Adjacent Context Injection | entity 일관성 부분 catch | ★★ | ~15L | 변경 없음 |
| 5 | Structured Output Index Mapping | content drift 근본 차단 | ★★★ | ~50L | 1~2× per chunk |
| 6 | Two-Stage Planning | entity 일관성 본질 차단 | ★ | ~100L | 2N+1 |

### 3.2 본질 cause 별 매핑

| 본질 cause | 차단 가능 패턴 |
|------------|----------------|
| LLM truncation | 2 (finish_reason), 3 (chunk 축소), 1 (Vimeo Phase 3 의 라인 수) |
| Content drift (timestamp/content 미스매치) | **1 (Vimeo Phase 3), 5 (Index mapping) ★ 가장 직접적** |
| Entity 일관성 (스키에더 vs 슈나이더) | 4 (Adjacent context), 6 (Two-stage planning), RLM Phase 2 (별도 spec) |

### 3.3 패턴 결합 분석

**결합 A: Vimeo 3-Phase (#1) + finish_reason (#2) — 가장 robust ★★★**
- Phase 2 (creative translation) 의 truncation → finish_reason 으로 continuation
- Phase 3 (line mapping) 의 라인 수 → drift 근본 차단
- 가장 robust 한 결합

**결합 B: Structured Output (#5) + finish_reason (#2) — 가장 단순 + 본질 ★★★**
- Index mapping 의 길이 검증 → drift 근본 차단
- finish_reason 으로 truncation 검출
- 코드 분량 작음 (~75L 합산)
- 가장 단순한 본질 해결

**결합 C: Adjacent Context (#4) + Two-Stage Planning (#6) — RLM Phase 2 와 정합**
- 다른 채널 RLM Phase 2 spec 의 본질과 정합
- 단 entity 일관성만 잡고, truncation/drift 본질 cause 는 그대로

### 3.4 사용자 user_preferences 와 코드베이스 정합성

사용자의 5/10 영구 명령 ("외부 변수로 취급"):

| 패턴 | "외부 변수" 정합 | "RULE 5 (판단 필요한 작업만 모델)" 정합 |
|------|------------------|----------------------------------|
| 1 (Vimeo) | △ — LLM 이 두 번 호출, 단 라인 수는 코드 검증 | ★ — Phase 3 은 사실상 코드 작업 |
| 2 (finish_reason) | ★ — 메타정보 catch | ★★★ — finish_reason 은 100% 코드 |
| 3 (Chunk 축소) | ★ — 외부 변수 | ★★★ — 결정론적 |
| 4 (Adjacent Context) | △ — context 도 LLM 입력 | ★ — 결정론적 |
| 5 (Structured Output) | ★★★ — timestamp 가 외부 변수 | ★★★ — 매핑은 100% 코드 |
| 6 (Two-Stage Planning) | △ — LLM 호출 많음 | △ — 의미 부분 LLM |

→ **사용자 user_preferences 와 가장 정합하는 패턴: 5 (Structured Output Index Mapping).**

사용자 RULE 5: "코드가 답할 수 있다면, 코드가 답합니다."
→ Timestamp 매핑은 코드가 답할 수 있다 (zip 함수).
→ 현재는 LLM 이 답하고 있다.
→ 패턴 5 가 RULE 5 의 핵심을 정확히 반영한다.

---

## 4. 다른 채널 RLM Phase 2 spec 과의 정합/충돌 분석

### 4.1 RLM Phase 2 spec 의 본질

받은 spec (다른 채널, RLM 논문 기반):
- **대상:** Entity 일관성 (스키에더 vs 슈나이더 같은 표기 불일치)
- **방법:** find_suspects (코드, 결정론적) + resolve_via_subcall (RLM, 인접 chunk 원문 sub-call)
- **본질 목표:** chunk 경계의 entity referent 단절 해결
- **다루지 않는 것:** truncation + content drift (5/12 catch 한 본질 cause)

### 4.2 정합/충돌

| 항목 | Phase 1 redesign (본 spec) | RLM Phase 2 spec |
|------|----------------------------|-------------------|
| 대상 본질 | truncation + content drift | entity 일관성 |
| 본질 cause | LLM 의 timestamp/content 자유 출력 | chunk 경계의 referent 단절 |
| 작업 위치 | translate_transcript (LLM 호출 단계) | distill/entity_resolution (post-process 단계) |
| 의존성 | Phase 1 본질 fix | Phase 1 (timestamp validation) |

→ **두 spec 의 목표가 본질적으로 다름 — 독립적으로 적용 가능.**

### 4.3 의존성

RLM Phase 2 spec 의 가정 A4:

> "A4. Phase 1(timestamp validation)이 먼저 들어가 있어 청크 경계가 신뢰 가능하다. → 의존성."

→ **현재 Phase 1 (5/12 push 3f3f04d) 의 timestamp validation 이 RLM Phase 2 의 의존성이다.**
→ 본 spec 의 redesign 후에도 timestamp 완전성은 보존되어야 한다.

### 4.4 작업 순서

**Path A: 본 spec (Phase 1 redesign) 먼저, 그다음 RLM Phase 2**
- Phase 1 의 본질 cause (truncation + drift) 완전 차단 후 RLM Phase 2
- RLM Phase 2 의 의존성과 정합
- 가장 robust 한 순서

**Path B: RLM Phase 2 먼저, 그다음 Phase 1 redesign**
- Entity 일관성 먼저 차단
- 단 truncation + drift 본질 cause 는 그대로
- 사용자 daily 사용에서 drift 가 계속 발생

**Path C: 통합 진행**
- 본 spec 의 패턴 + RLM Phase 2 동시 진입
- 사용자 RULE 2 (단순함이 먼저) + RULE 3 (외과적 변경) 위반 위험

→ **Path A 추천.**

---

## 5. 종합 추천

### 5.1 추천: 결합 B (Structured Output + finish_reason) ★★★

**근거:**
1. **사용자 user_preferences 와 가장 정합** — timestamp 가 외부 변수, RULE 5 정합
2. **두 본질 cause 모두 차단** — content drift (근본 차단) + truncation (명시적 검출)
3. **코드 분량 작음** — ~75L 합산 (현재 Phase 1 ~145L 보다 작음)
4. **RLM Phase 2 의존성 정합** — timestamp 완전성 보존
5. **사용자 RULE 2 (단순함) + RULE 3 (외과적 변경) 정합**

**제안 코드 구조:**

```python
# gurunote/llm.py — Phase 1 redesign

def translate_transcript_v2(transcript, context, config):
    """Index mapping + finish_reason continuation."""
    chunks = chunk_segments(transcript.segments)
    translated_parts = []

    for i, chunk in enumerate(chunks):
        # 1. Index mapping: timestamp 없이 순서만 전달
        inputs = [f"{s.speaker}: {s.text}" for s in chunk]
        prompt = _build_index_mapping_prompt(inputs, context)

        # 2. JSON schema 강제 + finish_reason continuation
        outputs = _call_llm_with_index_mapping(
            config, prompt,
            expected_count=len(inputs),
            max_retries=3,
        )

        # 3. 클라이언트 측 timestamp 부착 (zip)
        for segment, korean in zip(chunk, outputs):
            ts = f"[{_format_ts(segment.start)}]"
            translated_parts.append(f"{ts} {segment.speaker}: {korean}")

    return "\n\n".join(translated_parts)

def _call_llm_with_index_mapping(config, prompt, expected_count, max_retries):
    """JSON schema + finish_reason continuation."""
    for retry in range(max_retries):
        response = _call_llm_with_schema(config, prompt, expected_count)
        finish_reason = response.finish_reason

        if finish_reason == "length":
            # Truncation — continuation
            response = _continue_generation(config, response)

        try:
            outputs = json.loads(response.content)["outputs"]
        except (json.JSONDecodeError, KeyError):
            continue

        if len(outputs) == expected_count:
            return outputs

        # 길이 미스매치 — feedback 으로 retry
        prompt += f"\n\n이전 출력은 {len(outputs)}개 항목이었습니다. {expected_count}개가 필요합니다."

    # 3 retries 모두 실패 — fallback
    outputs = outputs[:expected_count] if len(outputs) > expected_count else \
             outputs + ["[번역 누락]"] * (expected_count - len(outputs))
    return outputs
```

### 5.2 보조 패턴

**Adjacent Context Injection (#4):** Phase 2 (RLM) 진입 전까지 화자 표기 일관성을 부분 catch
- ~15L 추가
- 본 redesign 후 별도 layer 로 추가 가능
- RLM Phase 2 완성 시 의미 없어질 수 있음 (단 코드 분량이 작아서 위험 작음)

### 5.3 본 spec 이 추천하지 않는 것

- **Chunk 크기 축소 (#3):** 본질 cause 의 일부만 catch, 컨텍스트 손실 trade-off 큼
- **Two-Stage Planning (#6):** RLM Phase 2 spec 과 범위 중복, 더 복잡
- **Vimeo 3-Phase (#1) 단독:** 결합 B (#5+#2) 가 더 단순하면서 본질 정합

---

## 6. 본 spec 의 가정과 한계

### 6.1 가정

- A1. qwen3.6-35b-q5 endpoint 가 OpenAI-compat JSON mode 를 지원 (json_object 또는 json_schema)
- A2. finish_reason 을 정확히 반환 (LM Studio + qwen)
- A3. JSON schema strict 미지원 시 response_format json_object + 길이 검증으로 대체 가능
- A4. 처리 시간 증가를 사용자가 수용 가능

가정 위반 시 본 spec 의 해결책이 작동하지 않을 수 있다. 별도 진단이 필요하다.

### 6.2 위험

1. **현재 Phase 1 코드의 ~80% 대체** — strict filter, bracket fix, _merge_retry_into_chunk 등이 무의미해짐
2. **5/12 trajectory 의 sunk cost** — bracket fix + strict filter 작업 후 redesign
3. **Prompt 재설계** — TRANSLATION_SYSTEM_PROMPT 본질 변경
4. **Production verify 위험** — 큰 redesign 의 회귀 위험 (5/12 bracket fix 같은 cascading 가능성)

### 6.3 한계

- Entity 일관성 (스키에더 vs 슈나이더) 은 RLM Phase 2 spec 의 담당 범위
- 본 spec 은 truncation + content drift 만 catch
- 두 spec 의 결합이 GuruNote = "LLM 하네스" 의 본질 완성

---

## 7. 결론

### 7.1 핵심 메시지

**현재 Phase 1 의 본질적 한계:**
- timestamp 존재 여부만 검증, 내용 정합성 검증 없음
- LLM 의 timestamp+content 자유 출력이 근본 원인
- 5/12 의 bracket fix + strict filter 는 부분적 해결

**본 spec 의 추천:**
- 결합 B (Structured Output Index Mapping + finish_reason Continuation)
- ~75L 코드로 본질 cause 두 가지 모두 차단
- 사용자 user_preferences + RULE 5 와 정합
- RLM Phase 2 spec 과 의존성 정합

**사용자 결정사항:**
- 본 spec 의 추천 path 채택 여부
- 다른 path (결합 A, C, 또는 새로운 path) 선택
- 본 spec 을 Claude Code 에게 paste 하여 분석 진행

### 7.2 사용자 5/11 통찰과의 정합

사용자가 5/11에 통찰하신 정의:

> "GuruNote = LLM 하네스 — 다양한 LLM 모델의 본질적 변동성을 흡수하는 강건한 layer"

본 spec 의 추천은 이 통찰과 정확히 정합한다:
- LLM 의 변동성 (truncation + drift) 을 시스템이 흡수
- 코드가 결정론적 매핑 (timestamp zip) 을 담당
- LLM 은 의미 부분 (번역) 만 담당, 구조 부분 (timestamp + 라인 수) 은 코드
- 사용자 RULE 5 "코드가 답할 수 있다면, 코드가 답합니다" 의 핵심 그대로

**Phase 1 redesign + RLM Phase 2 = GuruNote 하네스의 본질 layer 완성.**

---

_본 spec 은 사용자 결정 후 Claude Code 에게 paste 하기 위한 참고 자료이다._
_가드레일: Co-Authored-By: Claude trailer 절대 금지._
