"""
Step 3 & 4: LLM 기반 한국어 번역 + GuruNote 스타일 마크다운 요약.

- Provider: OpenAI (gpt-5.4) 또는 Anthropic (claude-sonnet-4-6)
- 긴 영상 대응: 세그먼트를 토큰 한도에 맞춰 청크 분할 → 청크별 번역 → 병합
- 번역 결과를 다시 요약 단계에 통째로 넣어 최종 마크다운을 만든다.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

import yaml

from gurunote.types import Segment, Transcript, _format_ts

ProgressFn = Callable[[str], None]


# =============================================================================
# 시스템 프롬프트 (PRD §3 - "매우 중요한 시스템 프롬프트 지시사항")
# =============================================================================

# Layer 11: TRANSLATION + SUMMARY (+ 향후 신규) prompt 공통 룰. 한자/일본어 차단,
# 첫 등장 영문 병기, 통용 표기 dict 핵심 — 양쪽 prompt 끝부분에 inline (DRY).
_SHARED_LANG_RULES = """

[출력 언어 + 표기 — 양쪽 prompt 공통 룰]

## 출력 언어 — 한국어 + 영문 병기만 허용
- 한국어 본문: 한국어 + 영문 병기 (필요 시).
- 영어 원문 영역: 영문 그대로.
- **금지 — 출력에 다음 문자/단어 절대 부재:**
  * 한자 (CJK Unified Ideographs): 这, 是, 因, 此, 也, 但, 这正是, 因此 등
  * 일본어 히라가나/가타카나: い, う, え, お, か, き, ため, には 등
  * 일본어 한자 어휘: 取り組み, 取り組んでいる, ためには, 場合, 仕組み 등
  * 중국어 간체/번체: 着, 过, 这, 那 등
- **모두 한국어 번역 또는 영문 그대로**:
  * 부정합: "슈나이더가 取り組んでいる 일" ✗ → 정합: "슈나이더가 추진하고 있는 일" ✓
  * 부정합: "这正是 우리가 하는 일" ✗ → 정합: "바로 이것이 우리가 하는 일" ✓
  * 부정합: "ためには 인프라가 필요" ✗ → 정합: "이를 위해서는 인프라가 필요" ✓

## 고유명사 첫 등장 영문 병기 (영상 전체 catch)
- 인명/지명/회사명/상품명/기술용어 첫 등장: `한국어 표기(English Name)` 형식.
  예) 슈나이더 일렉트릭(Schneider Electric), 판카즈 샤르마(Pankaj Sharma),
     젠슨 황(Jensen Huang)
- 이후 등장: 한국어만 (영문 병기 부재).
- chunk 분할 reset 절대 부재 — 영상 전체 한 번만 영문 병기.

## 통용 표기 dict (요약/타임라인 영역 정합 핵심)
- 인명: Jensen Huang→젠슨 황, Tiffany Janzen→티파니 잔젠,
        Pankaj Sharma→판카즈 샤르마, Sam Altman→샘 올트먼,
        Elon Musk→일론 머스크, Mark Zuckerberg→마크 저커버그,
        Dario Amodei→다리오 아모데이
- 회사: NVIDIA→엔비디아, Schneider Electric→슈나이더 일렉트릭,
        Motivair→모티브에어, OpenAI→OpenAI, Anthropic→앤트로픽
- AI/기술: AI Native→AI 네이티브, Energy Intelligence→에너지 인텔리전스,
          Digital Twin→디지털 트윈, SimReady→심레디,
          Brownfield→브라운필드, Liquid Cooling→액체 냉각

## 한국어 중복 출력 절대 금지 (괄호 안은 영문 원본 전용)
- 정합: 슈나이더 일렉트릭(Schneider Electric) ✓ / 판카즈 샤르마(Pankaj Sharma) ✓
- 부정합: 슈나이더 일렉트릭(슈나이더 일렉트릭) ✗ / 판카즈 샤르마(판카즈 샤르마) ✗
"""


TRANSLATION_SYSTEM_PROMPT = """\
너는 GuruNote 의 수석 에디터이자 세계 최고 수준의 IT/AI 테크 저널리스트야.

다음 규칙을 반드시 지켜:
1. 입력은 영어 인터뷰/팟캐스트 스크립트이며 화자 라벨(Speaker A, Speaker B …)
   과 타임스탬프가 포함돼 있어. 화자 라벨과 타임스탬프 형식은 그대로 보존해.
2. **화자 표기 — 한국어 스크립트 vs 영어 원문 분리:**

   [첫 등장 정의 — 영상 전체 catch — 절대 원칙]
   - "첫 등장" = 영상 전체에서 해당 화자/entity 가 처음 등장하는 시점 한 번.
   - chunk 분할 내에서 reset 절대 부재 — 한 영상 내 한 번만 영문 병기.
   - 첫 등장 영문 병기 누락 절대 금지 (화자 라벨 + 본문 entity 동일 패턴, Rule 10 정합).

   [한국어 스크립트 영역]
   - 첫 등장 (★ 영문 병기 필수): `[HH:MM] 한국어 화자명(English Name): 본문`
     예) `[00:10] 티파니 잔젠(Tiffany Janzen): 안녕하세요...`
     예) `[00:21] 판카즈 샤르마(Pankaj Sharma): 감사합니다.`
   - 이후 등장: `[HH:MM] 한국어 화자명: 본문` (영문 병기 부재)
     예) `[00:13] 티파니 잔젠: 그 다음에...`
   - **"Speaker A/B/C" 메타 라벨은 한국어 스크립트에 출력 부재** —
     영상 컨텍스트(채널명/제목/챕터/자막)에서 화자 실명을 추론할 수
     있으면 한국어 화자명을 직접 사용.
   - 한국어 화자명은 Rule 10 통용 표기 dict 정합
     (예: Tiffany Janzen → 티파니 잔젠, Pankaj Sharma → 판카즈 샤르마,
     Jensen Huang → 젠슨 황).
   - 화자 실명 추론 부재 시 "화자 1", "화자 2" 등 한국어 라벨 또는
     Speaker A/B/C 그대로 사용.
   - **금지 사례 — 화자 라벨의 한국어 중복 출력 절대 부재:**
     * `[HH:MM] 판카즈 샤르마(판카즈 샤르마): ...` ✗ (한국어를 영문 자리에 중복)
     * `[HH:MM] 판카즈 샤르마(Pankaj Sharma): ...` ✓ (영문 원본만 병기)
     * 영문 원본 부재 entity → 영문 병기 부재 → `[HH:MM] 화자 1: ...`

   [영어 원문 스크립트 영역]
   - 형식: `**[HH:MM] Speaker A:** 본문` (Speaker A/B/C 라벨 그대로 보존).
   - 영문 화자 실명 부재 — Speaker A/B/C 라벨만 사용.

   [본문 영역 — 화자/entity 인용 처리]
   - 본문에서 화자 이름 또는 entity 인용 시 Rule 10 영문 병기 룰 정합:
     * 첫 등장 (★ 영문 병기 필수): `한국어 이름(English Name)` 형식
       예) "...담당 상무이사 판카즈 샤르마(Pankaj Sharma)께서 함께해 주셨습니다."
     * 이후 등장: 한국어 이름만 (영문 병기 부재)
   - 화자 라벨 + 본문 entity 모두 영상 전체 첫 등장 catch 동일 적용.
   - 본문에 영문 그대로만 출력 부재 — 한국어 표기 누락 절대 금지.
3. **메시지 앞에 "### 영상 컨텍스트" 섹션이 있으면** 거기 실린 업로드 날짜,
   채널명, 영상 제목/설명, 챕터 목록, 기존 자막 발췌를 **화자 이름 추론과
   챕터 경계 유지의 근거로 적극 활용**해. 설명에 진행자/게스트 이름이 있으면
   Speaker A, B 매핑을 거기에 맞춰.
4. LLM, RAG, Fine-tuning, Transformer, Embedding, Inference, Diffusion 등
   IT/AI 전문 용어는 직역하지 말고 영문을 병기하거나 업계 통용어로 자연스럽게
   번역해. (예: "파인튜닝(Fine-tuning)", "검색 증강 생성(RAG)")
5. "you know", "I mean", "kind of", "like" 같은 구어체 추임새는 빼고,
   가독성 높은 자연스러운 한국어 인터뷰 톤으로 다듬어.
6. 출력은 오직 번역된 스크립트만. 설명/머리말/끝맺음 문장 금지.
7. **"### 영상 컨텍스트" 섹션은 화자/챕터 추론용 참고 메타데이터일 뿐 — 출력에
   그대로 포함하지 마. 컨텍스트의 제목/채널/게시일/태그/챕터/자막 발췌 등을
   본문에 echo 하지 마. 이미 있던 "### 영상 컨텍스트" / "### 번역 대상 스크립트"
   머리말 자체도 출력하지 마.**
8. **추론 과정·메타 분석은 출력 부재.** 다음 표현은 모두 금지:
   - "**참고 화자 매핑**:", "**추론된 화자 매핑**:", "**화자 매핑 근거**:",
     "**번역 노트**:", "**번역 의도**:", "**※ 분석**", "**※ 주의**" 등
     reasoning / commentary 섹션
   - 화자 매핑 결과는 규칙 2 형식으로만 표기 (한국어=한국어 실명, 영어=Speaker A/B/C).
9. **빈 content 영역의 timestamp + Speaker line 은 출력하지 마.**
   같은 timestamp + 같은 Speaker 가 연속 반복되면 1회만.
10. **고유명사(인명/지명/회사명/상품명) 한국어 표기 일관성:**

    [핵심 원칙 — 국립국어원 외래어 표기법 정합]
    - 자음: [k] → ㅋ(어두), ㄱ(받침) / [t] → ㅌ(어두), ㅅ(받침) /
      [tʃ] → 치(어두), ㅊ(어말) / [ʃ](sh) → 슈(모음 앞), 시(어말) /
      [n](어말) → ㄴ
    - 모음: [æ] → 애, [ʌ] → 어, [ə] → 어/이; 장모음은 한국어 정합.
    - [r]: 어두 → ㄹ, 어말 → 생략 또는 ㅡ

    [자주 등장 통용 표기 — 필수 정합]

    회사 (글로벌):
      NVIDIA→엔비디아, OpenAI→OpenAI, Anthropic→앤트로픽,
      Microsoft→마이크로소프트, Google→구글, Meta→메타, Apple→애플,
      Schneider Electric→슈나이더 일렉트릭, Samsung→삼성, AMD→AMD,
      Intel→인텔, Qualcomm→퀄컴, TSMC→TSMC, Tesla→테슬라, Amazon→아마존,
      Motivair→모티브에어, IBM→IBM, Oracle→오라클, Salesforce→세일즈포스,
      Adobe→어도비, Netflix→넷플릭스, ByteDance→바이트댄스, Alibaba→알리바바,
      Tencent→텐센트, SoftBank→소프트뱅크, Foxconn→폭스콘, Cisco→시스코,
      Dell→델, HP→HP, Sony→소니, LG→LG, NASA→미국 항공 우주국,
      Stripe→스트라이프, Rocket Lab→로켓랩, 1X→1X

    회사 (한국):
      Hyundai→현대, Kia→기아, POSCO→포스코, Hanwha→한화,
      SK Hynix→SK 하이닉스, Naver→네이버, Kakao→카카오,
      Innospace→이노스페이스, Lotte Chemical→롯데케미칼,
      ROBOTIS→로보티즈, SPHERE→스피어, Maeil Dairy→매일유업

    인명:
      Jensen Huang→젠슨 황, Sam Altman→샘 올트먼, Elon Musk→일론 머스크,
      Mark Zuckerberg→마크 저커버그, Satya Nadella→사티아 나델라,
      Sundar Pichai→순다르 피차이, Tim Cook→팀 쿡, Dario Amodei→다리오 아모데이,
      Lex Fridman→렉스 프리드먼, Andrej Karpathy→안드레 카파시,
      Yann LeCun→얀 르쿤, Geoffrey Hinton→제프리 힌턴,
      Demis Hassabis→데미스 허사비스, Ilya Sutskever→일리야 수츠케버,
      Greg Brockman→그렉 브록먼, Bill Gates→빌 게이츠,
      Pankaj Sharma→판카즈 샤르마, Tiffany Janzen→티파니 잔젠,
      Andrew Ross Sorkin→앤드루 로스 소킨, Jamie Dimon→제이미 다이먼,
      Lisa Su→리사 수, Pat Gelsinger→팻 겔싱어,
      Cristiano Amon→크리스티아노 아몬

    AI 제품/모델:
      Claude→클로드, Gemini→제미나이, ChatGPT→챗GPT, Copilot→코파일럿,
      DALL-E→달리; GPT/Llama/Mistral 등 모델명은 영문 그대로.

    기술 용어:
      HBM→HBM, DRAM→DRAM, NAND→NAND, HVAC→HVAC,
      Brownfield→브라운필드, Liquid Cooling→액체 냉각,
      Digital Twin→디지털 트윈, SimReady→심레디, Foundry→파운드리,
      AI Native→AI 네이티브, AI Factory→AI 팩토리,
      AI for Energy→AI for Energy (영문 유지),
      Energy for AI→Energy for AI (영문 유지),
      Energy Intelligence→에너지 인텔리전스

    [영문 병기 + 일관성 룰]
    - **첫 등장 = 영상 전체에서 해당 entity 가 처음 등장하는 시점 한 번** —
      chunk 분할 내에서 reset 절대 부재 (한 영상 내 한 번만 영문 병기).
    - 첫 등장 시 영문 병기: "슈나이더 일렉트릭(Schneider Electric)" — 이후 한국어만.
    - **첫 등장 영문 병기 누락 절대 금지** — 화자 라벨 + 본문 entity 동일 패턴
      (Rule 2 정합).
    - 영문 유지 entity (예: OpenAI) 는 첫 등장 시 "OpenAI(오픈AI)" 병기 후
      이후 영문만 — 한국어 표기를 다시 본문에 노출하지 마.
    - 같은 영상 내 같은 entity = 같은 표기 (chunk 별 변동 절대 금지).
    - dict 부재 entity + unsure → 음운 정합 한국어 또는 영문 그대로.
    - **한국어 중복 출력 절대 금지 (괄호 안은 영문 원본 전용):**
      * 정합: 슈나이더 일렉트릭(Schneider Electric) ✓ / 판카즈 샤르마(Pankaj Sharma) ✓
      * 부정합: 슈나이더 일렉트릭(슈나이더 일렉트릭) ✗ / 판카즈 샤르마(판카즈 샤르마) ✗
      * 영문 원본 미상 entity → 영문 병기 부재 (한국어만).
11. **출력 언어 — 한자/일본어/중국어 mix 절대 금지:**
    - 아래 [출력 언어 + 표기 — 양쪽 prompt 공통 룰] 섹션의 "출력 언어" 정합.
    - 본 룰 위반 시 LLM 출력 폐기 + 재생성 (daily quality bar 부정합).
""" + _SHARED_LANG_RULES


SUMMARY_SYSTEM_PROMPT = """\
너는 GuruNote 의 수석 에디터야. 아래 한국어 인터뷰 번역본을 바탕으로
다음 마크다운 구조에 정확히 맞춰 GuruNote 요약본을 작성해.

# 📌 영상 제목 및 핵심 주제 요약
- 영상 제목: {title}
- 핵심 주제를 **3줄 내외**로 요약.

# 💡 Guru's Insights (핵심 인사이트)
- **3~5개**의 굵은 불릿 포인트.
- 각 인사이트는 한 문장으로 압축한 뒤, 그 아래 1~2줄로 부연 설명.

# ⏱️ 타임라인별 주요 내용 요약
- `[MM:SS] 또는 [HH:MM:SS]` 형식의 타임스탬프 + 한 줄 요약 형태로 5~10개.
- 인터뷰 흐름이 잘 보이도록 시간 순서대로.
- **메시지 앞에 "### 영상 컨텍스트" 가 있고 그 안에 공식 챕터 목록이 주어졌다면,
  챕터 경계를 무시하지 말고 챕터 제목을 타임라인 항목의 뼈대로 삼아.**

규칙:
- 출력은 위 3개 섹션의 마크다운만. 다른 머리말/끝맺음 금지.
- 전문 용어는 영문 병기.
- "전체 스크립트 번역본" 섹션은 호출자가 별도로 붙이므로 여기에 포함하지 마.
- **공통 룰**: 한자/일본어 mix 절대 부재 + 통용 표기 dict 정합 + 첫 등장 영문 병기.
  아래 [출력 언어 + 표기 — 양쪽 prompt 공통 룰] 섹션 정합.
""" + _SHARED_LANG_RULES


# =============================================================================
# Provider 추상화
# =============================================================================
@dataclass
class LLMConfig:
    provider: str            # "openai" | "openai_compatible" | "anthropic" | "gemini"
    model: str
    api_key: str
    base_url: str = ""
    temperature: float = 0.2
    translation_max_tokens: int = 8192
    summary_max_tokens: int = 4096

    @classmethod
    def from_env(cls, provider: Optional[str] = None) -> "LLMConfig":
        """
        환경변수에서 LLMConfig 를 생성한다.

        provider 인자를 명시하면 그 값이 우선이고, 없으면 LLM_PROVIDER 환경변수를
        쓴다. 이 인자 덕분에 호출자는 process-wide `os.environ` 을 건드리지
        않고도 요청별로 provider 를 바꿀 수 있다 (Streamlit 같은 멀티 세션
        환경에서 race condition 회피).
        """
        provider = (provider or os.environ.get("LLM_PROVIDER", "openai")).lower().strip()
        temp = _float_env("LLM_TEMPERATURE", 0.2)
        translation_max_tokens = _int_env("LLM_TRANSLATION_MAX_TOKENS", 8192)
        summary_max_tokens = _int_env("LLM_SUMMARY_MAX_TOKENS", 4096)
        if provider == "anthropic":
            return cls(
                provider="anthropic",
                model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
                api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
                temperature=temp,
                translation_max_tokens=translation_max_tokens,
                summary_max_tokens=summary_max_tokens,
            )
        if provider == "gemini":
            return cls(
                provider="gemini",
                model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                api_key=os.environ.get("GOOGLE_API_KEY", ""),
                temperature=temp,
                translation_max_tokens=translation_max_tokens,
                summary_max_tokens=summary_max_tokens,
            )
        if provider == "openai_compatible":
            return cls(
                provider="openai_compatible",
                model=os.environ.get("OPENAI_MODEL", "gpt-5.4"),
                api_key=os.environ.get("OPENAI_API_KEY", "local"),
                base_url=os.environ.get("OPENAI_BASE_URL", ""),
                temperature=temp,
                translation_max_tokens=translation_max_tokens,
                summary_max_tokens=summary_max_tokens,
            )
        # 'openai' provider intentionally ignores OPENAI_BASE_URL — that env
        # is only honored by 'openai_compatible'. Otherwise selecting "openai"
        # in the UI while OPENAI_BASE_URL points at oMLX/vLLM would silently
        # route through the local server, defeating the pill's meaning.
        return cls(
            provider="openai",
            model=os.environ.get("OPENAI_MODEL", "gpt-5.4"),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            temperature=temp,
            translation_max_tokens=translation_max_tokens,
            summary_max_tokens=summary_max_tokens,
        )


def _int_env(key: str, default: int) -> int:
    try:
        val = int(os.environ.get(key, "").strip())
        return val if val > 0 else default
    except Exception:  # noqa: BLE001
        return default


def _float_env(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, "").strip())
    except Exception:  # noqa: BLE001
        return default


_log = logging.getLogger(__name__)

# Rate Limit 재시도 설정
_MAX_RETRIES = 4
_INITIAL_BACKOFF = 2.0  # 초

# 청크 번역 사이 지연 — API 분당 요청 제한(RPM) 에 걸리지 않기 위한 최소 쿨다운.
CHUNK_DELAY_SEC = 1.0


def _call_llm(config: LLMConfig, system: str, user: str, max_tokens: int = 4096) -> str:
    """
    단일 LLM 호출 — provider 에 맞춰 디스패치.

    Rate Limit(HTTP 429 / overloaded) 발생 시 지수 백오프(2s → 4s → 8s → 16s)로
    최대 _MAX_RETRIES 회 자동 재시도한다.
    """
    if config.provider in {"openai", "anthropic", "gemini"} and not config.api_key:
        raise RuntimeError(
            f"{config.provider.upper()}_API_KEY 가 .env 에 설정돼 있지 않습니다."
        )

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            return _call_llm_once(config, system, user, max_tokens)
        except Exception as exc:  # noqa: BLE001
            # Rate Limit / Overloaded 에러만 재시도, 나머지는 즉시 raise
            err_str = str(exc).lower()
            is_retryable = any(
                kw in err_str
                for kw in ("rate limit", "429", "overloaded", "too many requests")
            )
            if not is_retryable or attempt == _MAX_RETRIES:
                raise
            wait = _INITIAL_BACKOFF * (2 ** attempt)
            _log.warning("Rate limit hit (attempt %d/%d). %.1fs 후 재시도…", attempt + 1, _MAX_RETRIES, wait)
            last_exc = exc
            time.sleep(wait)

    # unreachable, but for type checker
    raise last_exc  # type: ignore[misc]


def _call_llm_once(config: LLMConfig, system: str, user: str, max_tokens: int) -> str:
    """실제 1 회 LLM 호출."""
    if config.provider == "anthropic":
        from anthropic import Anthropic  # type: ignore

        client = Anthropic(api_key=config.api_key)
        msg = client.messages.create(
            model=config.model,
            max_tokens=max_tokens,
            temperature=config.temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(
            getattr(b, "text", "") for b in msg.content if getattr(b, "type", "") == "text"
        ).strip()

    if config.provider == "gemini":
        from google import genai  # type: ignore

        client = genai.Client(api_key=config.api_key)
        resp = client.models.generate_content(
            model=config.model,
            contents=f"{system}\n\n{user}",
            config=genai.types.GenerateContentConfig(
                temperature=config.temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return (resp.text or "").strip()

    # default: openai
    from openai import OpenAI  # type: ignore

    openai_kwargs: dict = {"api_key": (config.api_key or "local")}
    if config.base_url:
        openai_kwargs["base_url"] = config.base_url
    client = OpenAI(**openai_kwargs)
    resp = client.chat.completions.create(
        model=config.model,
        max_tokens=max_tokens,
        temperature=config.temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (resp.choices[0].message.content or "").strip()


# =============================================================================
# 청크 분할 (PRD §5 - 토큰 제한 방지)
# =============================================================================
# 토큰 예산 ----------------------------------------------------------------
# 1 token ≈ 4 chars (영어 기준 보수적 추정).
# 한국어 번역은 보통 영어 입력보다 토큰을 1.0~1.3배 더 쓴다는 점, 그리고
# gpt-5.4 / claude-sonnet-4-6 의 응답 한도 안에 안전하게 들어와야 한다는
# 점을 같이 고려해 청크 입력을 ~12000 chars (≈ 3000 토큰) 로 잡는다.
# 이러면 출력은 최대 ~4000 토큰 수준에서 형성되며 TRANSLATION_MAX_TOKENS=8192
# 안에 충분히 들어와 mid-script truncation 위험이 사라진다.
DEFAULT_CHUNK_CHAR_LIMIT = 12_000  # 5/10 본인 설계 복원 (5/14 6000 가설 오류 revert)

# Phase 1 Redesign Step 2 정정 (5/14): 본질 cause = segment count (chunk char
# size 부재). 첫 시도 (12000 → 6000) 가설 catch:
#   - 25-segment E2E verify 결과 두 chunk limit 모두 1 chunk 정합 → chunk
#     size 변경 미작동
#   - gibberish 패턴 동일 (후반 line [01:14] [01:15] [01:23]) → cause 부재
# 진짜 cause: strict JSON schema 의 N 강제 + 모델 tail 위치 attention drop.
# 모델이 K<N 만 emit → fallback padding (의미 부재 한국어) = gibberish 정체.
# 차단: segment count cap — 모델 영역 attention 한계 직접 catch (15 = tail
# 안전 영역). char limit = LLM 토큰 한도 보조 safety net (요약 path 보존).
MAX_SEGMENTS_PER_CHUNK = 15

# 번역/요약 호출의 응답 토큰 상한 (gpt-5.4 / claude-sonnet-4-6 둘 다
# 수용 가능한 안전한 값).
TRANSLATION_MAX_TOKENS = 8192
SUMMARY_MAX_TOKENS = 4096


def chunk_segments(
    segments: List[Segment],
    char_limit: int = DEFAULT_CHUNK_CHAR_LIMIT,
    segment_limit: int = MAX_SEGMENTS_PER_CHUNK,
) -> List[List[Segment]]:
    """char_limit + segment_limit 둘 중 먼저 도달 시 chunk 분할.

    char_limit  — LLM 입력 토큰 한도 보조 safety net (long-seg edge case).
    segment_limit — 모델 tail attention drop 차단 (본질 cause, 5/14 정정).

    한 세그먼트는 분할하지 않는다.
    """
    chunks: List[List[Segment]] = []
    current: List[Segment] = []
    current_size = 0

    for seg in segments:
        seg_text = seg.text or ""
        # 화자 라벨/타임스탬프 오버헤드까지 대략 30자 더해 추정
        seg_size = len(seg_text) + 30
        if current and (
            len(current) >= segment_limit
            or current_size + seg_size > char_limit
        ):
            chunks.append(current)
            current = []
            current_size = 0
        current.append(seg)
        current_size += seg_size

    if current:
        chunks.append(current)
    return chunks


def _segments_to_user_block(segments: List[Segment]) -> str:
    lines = []
    for seg in segments:
        ts = _format_ts(seg.start)
        lines.append(f"[{ts}] Speaker {seg.speaker}: {seg.text}")
    return "\n".join(lines)


# Phase 1 redesign — 5/12 trajectory 영역의 timestamp validation + retry helpers
# (_TS_FIND_RE / _TS_LINE_PREFIX_RE / _TS_PARSE_RE / _MAX_TS_RETRY / _extract_timestamps
# / _ts_to_seconds / _build_retry_block / _merge_retry_into_chunk) 모두 제거.
# 본질 cause 차단: Index Mapping path (translate_chunk_index_mapping_v2) 의 zip
# 결정론 매핑 + finish_reason continuation 으로 두 cause (content drift + truncation)
# 모두 근본 차단. helpers 영역은 본 파일 끝의 Phase 1 Redesign 섹션 참고.


# =============================================================================
# 영상 컨텍스트 빌더 (YouTube 메타데이터 → LLM user 메시지 머리말)
# =============================================================================
# 자막/설명이 너무 길면 LLM 토큰 예산을 압박하므로 적절히 잘라 쓴다.
_MAX_CONTEXT_DESCRIPTION = 1500   # chars
_MAX_CONTEXT_SUBTITLE = 2000      # chars


def build_video_context_block(video_context: Optional[dict]) -> str:
    """
    AudioDownloadResult 에서 파생된 dict 를 LLM 에 주입할 컨텍스트 블록으로 변환.

    Args:
        video_context: 다음 키를 가진 dict (모두 선택):
            - title, uploader, upload_date, webpage_url
            - description (str)
            - chapters (list[dict] with start/end/title 또는 Chapter 객체 리스트)
            - subtitles_text (str), subtitles_source (str)
            - tags (list[str])

    Returns:
        `"### 영상 컨텍스트\\n..."` 로 시작하는 멀티라인 문자열. 컨텍스트가 없으면 "".
    """
    if not video_context:
        return ""

    lines: List[str] = ["### 영상 컨텍스트"]

    title = (video_context.get("title") or "").strip()
    if title:
        lines.append(f"- 제목: {title}")

    uploader = (video_context.get("uploader") or "").strip()
    if uploader:
        lines.append(f"- 채널: {uploader}")

    upload_date = (video_context.get("upload_date") or "").strip()
    if upload_date:
        lines.append(f"- 게시일: {upload_date}")

    webpage_url = (video_context.get("webpage_url") or "").strip()
    if webpage_url:
        lines.append(f"- 원본 URL: {webpage_url}")

    tags = video_context.get("tags") or []
    if tags:
        lines.append(f"- 태그: {', '.join(tags[:10])}")

    description = (video_context.get("description") or "").strip()
    if description:
        if len(description) > _MAX_CONTEXT_DESCRIPTION:
            description = description[:_MAX_CONTEXT_DESCRIPTION] + "… (truncated)"
        lines.append("")
        lines.append("#### 영상 설명")
        lines.append(description)

    chapters = video_context.get("chapters") or []
    if chapters:
        lines.append("")
        lines.append("#### 공식 챕터")
        for ch in chapters:
            # Chapter 객체 또는 dict 둘 다 지원
            if hasattr(ch, "start"):
                start, title_ch = ch.start, ch.title  # type: ignore[union-attr]
            else:
                start, title_ch = ch.get("start", 0), ch.get("title", "")  # type: ignore[union-attr]
            lines.append(f"- [{_format_ts(float(start))}] {title_ch}")

    subtitle = (video_context.get("subtitles_text") or "").strip()
    if subtitle:
        source = video_context.get("subtitles_source") or "unknown"
        sub_snippet = subtitle
        if len(sub_snippet) > _MAX_CONTEXT_SUBTITLE:
            sub_snippet = sub_snippet[:_MAX_CONTEXT_SUBTITLE] + "… (truncated)"
        lines.append("")
        lines.append(f"#### 영상 기본 자막 발췌 ({source})")
        lines.append(sub_snippet)

    lines.append("")
    lines.append(
        "※ 위 정보를 화자 이름 추론과 챕터 경계 유지의 참고 자료로 사용해. "
        "아래부터 이어지는 스크립트가 실제 번역/요약 대상이야."
    )
    lines.append("")
    return "\n".join(lines)


# =============================================================================
# Post-process — 영문 병기 dedup (Layer 13 정합)
# =============================================================================
# 본질: 모델 prompt Rule 2 영역 "첫 등장만 영문 병기" 지시 — chunk 경계 영역
# memory 부재로 chunk 마다 첫 등장 catch (영상 단위 부재). 본 post-process 영역
# 결정론 dedup (LLM 호출 부재, RULE 5 정합).
#
# 정규식 영역 본질: Korean lookbehind 영역 (?<=[가-힣]) — 한국어 직후 (English)
# 영역만 catch. dedup key = English annotation 영역만 — prefix Korean text 영역
# 영향 본질 부재 (entity 본체 영역 prefix 영역 합쳐짐 catch 부재).
#   "...오늘 슈나이더 일렉트릭(Schneider Electric)..." 첫 catch
#   "...에서 슈나이더 일렉트릭(Schneider Electric)..." 두 번째 → 영문 영역 제거
_REPEATED_ANNOTATION_RE = re.compile(r"(?<=[가-힣])\s?\(([A-Za-z][^()]*?)\)")


def _strip_repeated_annotations(text: str) -> str:
    """첫 등장 후 영문 병기 영역 제거 (Layer 13 정합).

    "판카즈 샤르마(Pankaj Sharma)" → 첫 등장 보존.
    "판카즈 샤르마(Pankaj Sharma)" 두 번째 이후 → "판카즈 샤르마" (괄호 영역 제거).

    Lookbehind (?<=[가-힣]) — 한국어 직후 영역만 catch.
    한국어 prefix 영역 영향 본질 부재 (English key dedup, regex prefix bug 차단).
    """
    seen: set[str] = set()

    def _replace(match: re.Match) -> str:
        english = match.group(1).strip()
        if english in seen:
            return ""  # 두 번째 이후: 괄호 영역 영역 제거
        seen.add(english)
        return match.group(0)  # 첫 등장: 보존

    return _REPEATED_ANNOTATION_RE.sub(_replace, text)


# =============================================================================
# Post-process — Phase 3 한자/일본어 잔재 제거 (Sub-path A + B + C)
# =============================================================================
# 원인: Qwen3.6-35B-A3B-5bit 의 decoder-level collapse 로 한국어 출력 중 한자/
# 일본어 토큰이 간헐적 잔재. prompt rule 만으로 결정적 차단 부재.
# omlx 가 logit_bias 미지원 (5/18 catch) — token-level 차단 path 봉쇄.
#
# 처리 흐름:
#   1) 검출 (괄호 안 한자 표기 예외)
#   2) Sub-path A: gurunote/data/cjk_lookup.yaml 사전 lookup (긴 매칭 우선)
#   3) Sub-path B: LLM 재매핑 (chunk 단위, retry 최대 3회)
#   4) Sub-path C: 영문 원문 fallback + inline [⚠ fallback] 태그

_CJK_LOOKUP_PATH = Path(__file__).parent / "data" / "cjk_lookup.yaml"
_CJK_LOOKUP_CACHE: Optional[dict] = None

# CJK Unified Ideographs + 일본어 히라가나/가타카나
_CJK_DETECT_RE = re.compile(r"[一-鿿぀-ヿ]")
# 괄호 안 한자 표기 — 예외 (예: "양자역학(量子力學)")
_BRACKETED_CJK_RE = re.compile(r"\([^)]*[一-鿿぀-ヿ][^)]*\)")
# segment 라인 prefix: [MM:SS] Speaker label:
_SEGMENT_PREFIX_RE = re.compile(r"^\[(\d{1,2}):(\d{2})\]\s+([^:]+):\s*(.*)$")


def _load_cjk_lookup() -> dict:
    """yaml 사전 로드 + 캐시. 긴 매칭 우선을 위해 multi-char 를 길이순 정렬.

    Returns:
        {'multi': [(pat, repl), ...], 'single': [(pat, repl), ...]}
    """
    global _CJK_LOOKUP_CACHE
    if _CJK_LOOKUP_CACHE is not None:
        return _CJK_LOOKUP_CACHE
    with open(_CJK_LOOKUP_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    multi: List[tuple] = []
    for section in ("chinese", "japanese"):
        for k, v in (data.get(section) or {}).items():
            multi.append((str(k), str(v)))
    multi.sort(key=lambda x: -len(x[0]))  # 긴 매칭 우선
    single: List[tuple] = [
        (str(k), str(v)) for k, v in (data.get("single_char") or {}).items()
    ]
    _CJK_LOOKUP_CACHE = {"multi": multi, "single": single}
    return _CJK_LOOKUP_CACHE


def _detect_cjk_outside_brackets(text: str) -> List[str]:
    """괄호 밖 CJK 잔재 catch. 빈 리스트면 통과."""
    masked = _BRACKETED_CJK_RE.sub("[BRACKETED]", text)
    return _CJK_DETECT_RE.findall(masked)


def _apply_cjk_dict_lookup(text: str, lookup: dict) -> str:
    """Sub-path A — 사전 lookup. 괄호 안 한자 표기는 보존.

    multi 사전을 긴 매칭 우선으로 적용 후 single 사전 적용.
    """
    # 괄호 영역 보호 — placeholder 로 치환
    bracketed: List[str] = []

    def _save(m: re.Match) -> str:
        bracketed.append(m.group(0))
        return f"\x00BR{len(bracketed)-1}\x00"

    masked = _BRACKETED_CJK_RE.sub(_save, text)
    for pat, repl in lookup["multi"]:
        if pat in masked:
            masked = masked.replace(pat, repl)
    for pat, repl in lookup["single"]:
        if pat in masked:
            masked = masked.replace(pat, repl)
    # 괄호 영역 복원
    return re.sub(r"\x00BR(\d+)\x00", lambda m: bracketed[int(m.group(1))], masked)


def _llm_remap_cjk(
    text: str,
    config: "LLMConfig",
    max_retries: int = 3,
) -> Optional[str]:
    """Sub-path B — LLM 재매핑 retry max_retries회.

    성공 (잔재 0건) 시 결과 반환, 모두 실패 시 None.
    """
    system = (
        "다음 한국어 문장에 한자 또는 일본어 토큰이 남아있다. "
        "본 토큰을 자연스러운 한국어로 모두 치환한 결과만 출력하라. "
        "괄호 안 한자 표기 (예: '양자역학(量子力學)') 는 그대로 둔다. "
        "원문의 화자 라벨과 [MM:SS] 타임스탬프는 보존한다. "
        "설명이나 메타 텍스트 없이 치환된 본문만 한 줄로 출력하라."
    )
    for _ in range(max_retries):
        try:
            result = _call_llm(config, system, text, max_tokens=2048)
        except Exception:
            continue
        if result and not _detect_cjk_outside_brackets(result):
            return result.strip()
    return None


def post_process_cjk(
    result: str,
    segments: List[Segment],
    config: "LLMConfig",
    log: Optional[ProgressFn] = None,
) -> str:
    """Phase 3 후처리 — 한자/일본어 0건 보장 (Sub-path A → B → C).

    Args:
        result: translate_transcript 결과 본문 (segment 라인 \\n\\n join)
        segments: 원본 영문 segments (Sub-path C fallback 시 영문 원문 lookup)
        config: LLMConfig (Sub-path B LLM 호출용)
        log: 진행 콜백

    Returns:
        후처리된 result. 한자/일본어 0건 (Sub-path C fallback 적용된 segment 는
        영문 원문 + [⚠ fallback] 태그) 보장.
    """
    log_fn = log or (lambda _msg: None)
    lookup = _load_cjk_lookup()

    # segments 를 (mm, ss) 키로 인덱싱 — Sub-path C 의 영문 원문 lookup
    seg_by_ts: dict = {}
    for seg in segments:
        mm = int(seg.start) // 60
        ss = int(seg.start) % 60
        seg_by_ts[(mm, ss)] = seg

    sub_a_hits = 0
    sub_b_hits = 0
    sub_c_fallbacks: List[tuple] = []  # (mm, ss)

    parts = result.split("\n\n")
    processed: List[str] = []

    for part in parts:
        if not _detect_cjk_outside_brackets(part):
            processed.append(part)
            continue

        # Sub-path A
        after_a = _apply_cjk_dict_lookup(part, lookup)
        if not _detect_cjk_outside_brackets(after_a):
            sub_a_hits += 1
            processed.append(after_a)
            continue

        # Sub-path B — LLM 재매핑 (Sub-path A 결과를 입력으로)
        after_b = _llm_remap_cjk(after_a, config, max_retries=3)
        if after_b is not None:
            sub_b_hits += 1
            processed.append(after_b)
            continue

        # Sub-path C — 영문 fallback
        m = _SEGMENT_PREFIX_RE.match(part)
        if m:
            mm, ss = int(m.group(1)), int(m.group(2))
            speaker = m.group(3).strip()
            seg = seg_by_ts.get((mm, ss))
            if seg is not None:
                fallback_text = (
                    f"[{mm:02d}:{ss:02d}] {speaker}: {seg.text} [⚠ fallback]"
                )
                sub_c_fallbacks.append((mm, ss))
                processed.append(fallback_text)
                continue

        # segment 매핑 실패 — 잔재 그대로 (검증 단계에서 catch)
        processed.append(part)

    log_fn(
        f"   🔧 Phase 3 후처리 — Sub-A {sub_a_hits}건, "
        f"Sub-B {sub_b_hits}건, Sub-C fallback {len(sub_c_fallbacks)}건"
    )
    if sub_c_fallbacks:
        ts_list = ", ".join(f"[{mm:02d}:{ss:02d}]" for mm, ss in sub_c_fallbacks[:10])
        log_fn(f"   ⚠ Sub-C fallback timestamps: {ts_list}")

    return "\n\n".join(processed)


# =============================================================================
# Step 3: 번역
# =============================================================================
def translate_transcript(
    transcript: Transcript,
    config: Optional[LLMConfig] = None,
    progress: Optional[ProgressFn] = None,
    video_context: Optional[dict] = None,
    stop_event=None,  # threading.Event — chunk 사이 polling
) -> str:
    """
    Transcript → 한국어로 번역된 스크립트 (문자열).
    화자 라벨과 타임스탬프는 보존된다.

    Args:
        transcript: STT 결과
        config: LLM 설정
        progress: 진행 콜백
        video_context: YouTube 메타데이터 dict (AudioDownloadResult.to_context_dict()
            형태). 제공되면 LLM 의 화자 이름 추론과 챕터 유지에 활용된다.
        stop_event: threading.Event — set 되면 청크 사이에 RuntimeError raise.
            gui.PipelineWorker._stop_event 와 같은 인스턴스를 넘겨 사용자
            중지 요청을 단계 내부에서 catch.
    """
    log = progress or (lambda _msg: None)
    config = config or LLMConfig.from_env()

    chunks = chunk_segments(transcript.segments)
    log(f"🌐 LLM 번역 시작 — {len(chunks)} 청크 ({config.provider}/{config.model})")

    context_block = build_video_context_block(video_context)
    if context_block:
        log("📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.")

    translated_parts: List[str] = []
    for i, chunk in enumerate(chunks, start=1):
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("사용자가 작업 중지를 요청했습니다.")
        # 청크 간 쿨다운 — API Rate Limit 방지 (첫 청크는 건너뜀)
        if i > 1:
            time.sleep(CHUNK_DELAY_SEC)
        log(f"   ↳ 청크 {i}/{len(chunks)} 번역 중…")

        # Phase 1 Redesign — Structured Output Index Mapping + finish_reason Continuation.
        # 본질 cause 차단: (1) Content drift — LLM 이 timestamp 출력 부재 → 순서만 매핑
        # (zip 100% 결정론). (2) Truncation — finish_reason='length' 명시 catch + retry.
        # 기존 Phase 1 retry/marker 로직 (5/12 trajectory) 영역 제거 — Index Mapping path
        # 가 두 본질 cause 모두 근본 차단.
        translated = translate_chunk_index_mapping_v2(chunk, context_block, config, log)
        translated_parts.append(translated)

    log("✅ 번역 완료")
    # Index Mapping path 의 출력은 결정론적 \n\n 정합 — Layer 14 lookahead regex
    # 정규화 영역 부재 (chunk join 만으로 충분).
    normalized_parts = translated_parts
    result = "\n\n".join(normalized_parts).strip()
    # Phase 3 — 한자/일본어 잔재 후처리 (Sub-path A → B → C).
    # Sub-path A 사전 lookup → 미적중 시 Sub-path B LLM 재매핑 → 그래도 잔재 시
    # Sub-path C 영문 원문 fallback. 본 단계로 한자/일본어 0건 보장.
    result = post_process_cjk(result, transcript.segments, config, log)
    # Q2 영역 — 영상 단위 영문 병기 첫 등장 catch (Layer 13 정합).
    # chunk 단위 영역 부재 — chunk 경계 memory 부재로 매 chunk 첫 등장 catch
    # 영역 패턴 영역 dedup.
    return _strip_repeated_annotations(result)


# =============================================================================
# Step 4: 요약 (GuruNote 스타일)
# =============================================================================
def summarize_translation(
    translated_text: str,
    title: str,
    config: Optional[LLMConfig] = None,
    progress: Optional[ProgressFn] = None,
    video_context: Optional[dict] = None,
    stop_event=None,  # threading.Event — partial 사이 polling
) -> str:
    """
    번역본 → 마크다운 요약 (영상 제목/인사이트/타임라인 섹션).
    전체 스크립트는 포함하지 않으며 호출자가 별도로 붙인다.

    video_context 가 제공되면 공식 챕터 목록을 타임라인 섹션의 뼈대로
    사용하도록 LLM 에 주입한다.

    stop_event: threading.Event — set 되면 partial 요약 사이 / 최종 통합 직전에
    RuntimeError raise. translate_transcript 와 같은 패턴.
    """
    log = progress or (lambda _msg: None)
    config = config or LLMConfig.from_env()

    def _check_stop() -> None:
        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("사용자가 작업 중지를 요청했습니다.")

    system = SUMMARY_SYSTEM_PROMPT.format(title=title)
    context_block = build_video_context_block(video_context)
    if context_block:
        translated_text = (
            f"{context_block}\n### 번역본\n{translated_text}"
        )

    # 요약 단계도 본문이 매우 길면 1차 요약 → 합치기 → 최종 요약 두 단계.
    if len(translated_text) > DEFAULT_CHUNK_CHAR_LIMIT:
        log("🧪 번역본이 길어 청크별 요약 후 최종 통합합니다…")
        partials: List[str] = []
        # 청크 분할은 빈 줄 기준 단순 분할로 충분
        paragraphs = translated_text.split("\n\n")
        buf: List[str] = []
        size = 0
        for p in paragraphs:
            if size + len(p) > DEFAULT_CHUNK_CHAR_LIMIT and buf:
                _check_stop()
                partial = _call_llm(
                    config,
                    system=system,
                    user="다음 부분 번역본의 핵심 인사이트와 타임라인만 요약해:\n\n"
                    + "\n\n".join(buf),
                    max_tokens=config.summary_max_tokens or SUMMARY_MAX_TOKENS,
                )
                partials.append(partial)
                buf = []
                size = 0
            buf.append(p)
            size += len(p)
        if buf:
            _check_stop()
            partials.append(
                _call_llm(
                    config,
                    system=system,
                    user="다음 부분 번역본의 핵심 인사이트와 타임라인만 요약해:\n\n"
                    + "\n\n".join(buf),
                    max_tokens=config.summary_max_tokens or SUMMARY_MAX_TOKENS,
                )
            )
        merged_user = (
            "아래는 같은 영상의 부분 요약본들이야. 이를 통합해 GuruNote 스타일의 "
            "최종 요약본을 한 번 더 정리해 줘.\n\n" + "\n\n---\n\n".join(partials)
        )
        log("📝 부분 요약 통합 중…")
        _check_stop()
        return _call_llm(
            config,
            system=system,
            user=merged_user,
            max_tokens=config.summary_max_tokens or SUMMARY_MAX_TOKENS,
        ).strip()

    log("📝 GuruNote 요약본 생성 중…")
    _check_stop()
    return _call_llm(
        config,
        system=system,
        user=translated_text,
        max_tokens=config.summary_max_tokens or SUMMARY_MAX_TOKENS,
    ).strip()


# =============================================================================
# 메타데이터 자동 추출 (Phase A — 지식 증류기)
# =============================================================================
METADATA_SYSTEM_PROMPT = """당신은 IT/AI 컨텐츠 큐레이터입니다.
주어진 한국어로 번역된 인터뷰/팟캐스트 스크립트와 영상 메타데이터를 보고,
지식 증류 노트를 분류·검색하기 위한 메타데이터를 JSON 형식으로 추출합니다.

추출 항목:
1. organized_title: 사람이 보기 쉬운 한국어 제목 (60자 이내)
   - ★ 우선순위: 원본 영상 제목이 충분히 명확하면 그대로 사용 또는 단순 한국어 번역.
   - 영어/너무 김/광고문구 포함되어 있으면 핵심 주제로 새로 작성.
   - ★ title 등장 인물 룰 (Layer 15 fix-up #1 — hallucination 차단):
     * 영상의 실제 화자 + 영상의 핵심 주제만 포함.
     * 본문에서 단순 인용된 인물 (키노트 발표자, 언급된 학자, 화자가 인용한
       다른 사람 등) 은 title 등장 절대 부재.
     * 영상의 실제 화자는 transcript 의 화자 라벨에서 확인 — 인용 인물과 구분.
   - 형식 예시 (다양 패턴 — 영상 성격에 맞게 선택):
     * 단순 번역: "엔비디아 GTC 스튜디오: 슈나이더 일렉트릭의 AI 인프라 인사이트"
     * 화자 + 주제: "판카즈 샤르마(Pankaj Sharma): AI 팩토리의 에너지 인텔리전스"
     * 주제 중심: "AI 팩토리 에너지 인프라: Energy for AI vs AI for Energy"
   - 부정합 사례: 본문에서 단순 인용된 인물을 title 화자로 배치 ✗
2. field: 분야 (한국어, 1~3단어)
   - 예: "AI/ML", "AI 하드웨어", "스타트업", "철학", "양자 컴퓨팅", "정치"
3. tags: 정확히 5개의 짧은 키워드 (한글 또는 영문 약어)
   - YouTube 의 원본 태그가 주어지면 적합한 것을 우선 활용
   - 부족하면 본문 내용에서 핵심 주제어 추가
   - 예: ["NVIDIA", "스케일링 법칙", "GPU", "젠슨 황", "AGI"]
""" + _SHARED_LANG_RULES + """

[중요 — title + tags 영역의 표기 룰 (Layer 15)]
- title 영역: 본문과 동일 패턴 — 첫 등장 entity 영문 병기 적용.
  예: "슈나이더 일렉트릭(Schneider Electric): AI 팩토리 인프라"
  예: "젠슨 황(Jensen Huang): NVIDIA - 4조 달러 기업"
  부정합: "슈나이더일렉트릭" (띄어쓰기 누락) ✗
- tags 영역: 통용 표기 dict 정합 (한국어 표기). 영문 병기 부재 (hashtag 부자연).
  정합: ["슈나이더 일렉트릭", "AI 팩토리", "에너지 효율"]
  부정합: ["슈나이더_일렉트릭(Schneider_Electric)"] ✗ (영문 병기 hashtag)
- title 60자 제한 — 영문 병기 추가해도 일반 entity 빈도 영역 50자 안쪽 안전.

오로지 다음 JSON 만 출력하세요. 다른 설명/마크다운 없이 순수 JSON:
{
  "organized_title": "...",
  "field": "...",
  "tags": ["...", "...", "...", "...", "..."]
}
"""


def extract_metadata(
    translated_text: str,
    video_meta: Optional[dict] = None,
    config: Optional[LLMConfig] = None,
    log: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    번역된 스크립트 + 영상 메타데이터에서 분류용 메타데이터를 추출.

    Args:
        translated_text: `translate_transcript` 의 결과 (전체 또는 앞부분 발췌)
        video_meta: yt-dlp 의 영상 메타 (title, uploader, tags, description 등)
        config: LLMConfig
        log: 진행 로그 콜백

    Returns:
        {
            "organized_title": str,
            "field": str,
            "tags": list[str] (5개),
        }
        실패 시 빈 dict 반환 (파이프라인 진행 방해 안 함).
    """
    log = log or (lambda _msg: None)
    config = config or LLMConfig.from_env()
    video_meta = video_meta or {}

    # LLM 입력 분량 제한 — 앞부분 + 뒷부분 발췌로 토큰 절감
    excerpt = _excerpt_for_metadata(translated_text)

    youtube_title = video_meta.get("title", "") or ""
    uploader = video_meta.get("uploader", "") or ""
    youtube_tags = video_meta.get("tags") or []
    youtube_tag_block = (
        f"\n원본 YouTube 태그: {', '.join(youtube_tags[:15])}" if youtube_tags else ""
    )

    user = (
        f"### 영상 메타\n"
        f"- 제목: {youtube_title}\n"
        f"- 업로더: {uploader}{youtube_tag_block}\n\n"
        f"### 한국어 번역 발췌\n{excerpt}\n"
    )

    log("🏷️  메타데이터(제목/분야/태그) 추출 중…")
    # JSON 은 짧지만 한국어 제목/태그가 길 수 있으므로 config.summary_max_tokens 를
    # 기준으로 여유를 두되, 하한 1024 로 최소 응답 공간 보장.
    metadata_max_tokens = max(1024, (config.summary_max_tokens or 4096) // 4)
    try:
        raw = _call_llm(
            config,
            system=METADATA_SYSTEM_PROMPT,
            user=user,
            max_tokens=metadata_max_tokens,
        )
        return _parse_metadata_json(raw)
    except Exception as exc:  # noqa: BLE001
        log(f"  메타데이터 추출 실패 (무시하고 계속): {exc}")
        return {}


def _excerpt_for_metadata(text: str, max_chars: int = 6000) -> str:
    """메타 추출용 발췌 — 앞 70% / 뒤 30% 비율로 자른다."""
    if len(text) <= max_chars:
        return text
    head = int(max_chars * 0.7)
    tail = max_chars - head
    return text[:head] + "\n\n[…중간 생략…]\n\n" + text[-tail:]


def _parse_metadata_json(raw: str) -> dict:
    """LLM 응답에서 JSON 객체를 추출 (마크다운 코드블록 래핑 허용)."""
    import json
    import re

    if not raw or not raw.strip():
        return {}

    # ```json ... ``` 또는 ``` ... ``` 코드블록 제거
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    payload = fence.group(1) if fence else raw

    # JSON 객체 첫 등장 부분만 추출 (LLM 이 앞뒤로 텍스트 붙이는 경우)
    obj_match = re.search(r"\{.*\}", payload, re.DOTALL)
    if not obj_match:
        return {}

    try:
        data = json.loads(obj_match.group(0))
    except json.JSONDecodeError:
        return {}

    # 스키마 검증 + 정규화
    title_raw = data.get("organized_title")
    field_raw = data.get("field")
    title = title_raw.strip() if isinstance(title_raw, str) else ""
    field = field_raw.strip() if isinstance(field_raw, str) else ""

    tags_raw = data.get("tags") or []
    if not isinstance(tags_raw, list):
        tags_raw = []
    # 문자열만 허용 — `None` / `{}` / 숫자 등이 `str(None)` 거쳐 "None" 같은
    # 쓰레기 태그로 저장되는 것을 방지.
    tags = [t.strip() for t in tags_raw if isinstance(t, str) and t.strip()][:5]

    if not (title or field or tags):
        return {}

    return {
        "organized_title": title,
        "field": field,
        "tags": tags,
    }


def test_connection(config: Optional[LLMConfig] = None) -> str:
    """현재 설정으로 LLM API 연결을 테스트한다."""
    cfg = config or LLMConfig.from_env()
    text = _call_llm(
        cfg,
        system="You are a connection tester. Reply only with: OK",
        user="ping",
        max_tokens=16,
    )
    if not text.strip():
        raise RuntimeError("LLM 응답이 비어 있습니다.")
    return text.strip()


# =============================================================================
# Phase 1 Redesign — Structured Output Index Mapping + finish_reason Continuation
# =============================================================================
# 본질 cause 차단 (체크포인트 2 — 단일 chunk 영역 verify):
#   1. Content drift — LLM 이 timestamp 출력 부재 → 순서만 매핑 (zip 영역 100%)
#   2. Truncation — finish_reason='length' 명시 catch + continuation 영역
# 본 spec: docs/research/phase1_redesign_research.md
# 5/12 endpoint verify: qwen3.6-35b-q5 — finish_reason + json_object + json_schema 모두 정합.
# 기존 Phase 1 helpers (5/12 trajectory) 영역 보존 — 체크포인트 3 시 통합 결정.


def _call_llm_once_with_reason(
    config: LLMConfig,
    messages: list,
    max_tokens: int,
    response_format: Optional[dict] = None,
    timeout: Optional[float] = None,
) -> tuple:
    """단일 LLM 호출 — (content, finish_reason) tuple 반환.

    기존 `_call_llm_once` 는 content string 만 반환 (Layer 13 / Layer 14 / Step 3b-3
    등 다른 호출자가 finish_reason 불필요). 본 함수는 Index Mapping path 전용 —
    truncation 명시적 catch + JSON 응답 길이 검증을 위해 finish_reason 노출.

    openai / openai_compatible provider 만 지원 (anthropic / gemini 는 별도 mapping
    필요 — 본 path 의 endpoint 가 OpenAI compat 영역).

    Args:
        timeout: request-level timeout (초). None 이면 SDK 기본값 사용. Phase 4a-1
            에서 xgrammar grammar-recovery loop 조기 차단용으로 사용 (첫 시도 strict
            mode 에 30초 적용). timeout 초과 시 openai.APITimeoutError 발생.

    Returns:
        tuple[str, str]: (content, finish_reason ∈ {"stop", "length", "content_filter", ...})
    """
    from openai import OpenAI  # noqa: PLC0415

    openai_kwargs: dict = {"api_key": (config.api_key or "local")}
    if config.base_url:
        openai_kwargs["base_url"] = config.base_url
    client = OpenAI(**openai_kwargs)

    kwargs: dict = {
        "model": config.model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": config.temperature,
    }
    if response_format:
        kwargs["response_format"] = response_format
    if timeout is not None:
        kwargs["timeout"] = timeout

    resp = client.chat.completions.create(**kwargs)
    choice = resp.choices[0]
    return (choice.message.content or ""), (choice.finish_reason or "unknown")


def _build_index_mapping_prompt(inputs: list, context: str) -> str:
    """Index Mapping 영역의 user prompt — TRANSLATION_SYSTEM_PROMPT 가 system 영역
    이라 가정. 본 user prompt 는 출력 형식 override 만 명시 (entity / Layer 8/11/13/15
    규칙은 system 에서 catch).

    Rule 1, 2 (timestamp 보존 / [HH:MM] 형식) override:
      - 출력 형식 = JSON {"outputs": [...]}
      - timestamp 영역 부재 (클라이언트가 zip 으로 별도 부착)
      - speaker label 영역 = Rule 2 의 한국어 화자명 정합 (예: "판카즈 샤르마(Pankaj Sharma): 본문")
    """
    return f"""[출력 형식 영역 — Rule 1, 2 의 timestamp 부분 override]

이번 호출은 Index Mapping path 영역. 출력 형식을 다음과 같이 변경한다:

1. 응답은 반드시 JSON 형식: {{"outputs": [str, str, ...]}}
2. outputs 배열은 정확히 {len(inputs)}개 항목 (같은 순서)
3. timestamp 출력 절대 부재 (클라이언트가 별도 부착)
4. 각 output string 형식: "한국어 화자명(English Name): 본문" (첫 등장) 또는 "한국어 화자명: 본문" (이후)
5. "Speaker A/B/C" 영문 라벨 출력 절대 부재 — Rule 2 정합 한국어 화자명
6. 다른 모든 규칙 (Rule 3~11 + _SHARED_LANG_RULES) 정합 유지

{context}

Input ({len(inputs)}개 항목, 각 "Speaker X: 영어 text" 형식):
{json.dumps({"inputs": inputs}, ensure_ascii=False, indent=2)}

Output (JSON 만, 다른 텍스트 부재):"""


def _call_llm_with_continuation(
    config: LLMConfig,
    messages: list,
    max_tokens: int,
    response_format: Optional[dict] = None,
    max_continuations: int = 3,
    timeout: Optional[float] = None,
) -> tuple:
    """finish_reason='length' 시 자동 continuation.

    truncation 명시 검출 + 이어쓰기 (drift 차단). JSON mode 영역의 continuation
    은 구조 보존 영역에서 본질 한계 영역 — 체크포인트 2 영역은 작은 chunk
    영역 → truncation 부재 가정. 진짜 truncation 시 _call_llm_with_index_mapping
    의 outer retry 영역에서 길이 미스매치 영역 catch + feedback retry.

    Args:
        timeout: request-level timeout (초). None 이면 SDK 기본값. Phase 4a-1 의
            xgrammar grammar-recovery loop 조기 차단용으로 inner 호출에 forward.

    Returns:
        tuple[str, str]: (accumulated_content, last_finish_reason)
    """
    accumulated = ""
    last_finish_reason = "unknown"
    current_messages = list(messages)

    for _cont in range(max_continuations + 1):
        content, finish_reason = _call_llm_once_with_reason(
            config, current_messages, max_tokens, response_format, timeout=timeout
        )
        accumulated += content
        last_finish_reason = finish_reason

        if finish_reason == "stop":
            return accumulated, finish_reason
        if finish_reason == "length":
            # JSON mode 영역의 continuation 은 본질 한계 영역 — outer retry 영역에서 처리
            if response_format and response_format.get("type", "").startswith("json"):
                return accumulated, finish_reason
            # Non-JSON 영역만 continuation
            current_messages = current_messages + [
                {"role": "assistant", "content": accumulated},
                {"role": "user", "content": "Continue from where you stopped. Do not repeat previous content."},
            ]
            continue
        # content_filter 등 — break
        break

    return accumulated, last_finish_reason


def _call_llm_with_index_mapping(
    config: LLMConfig,
    prompt: str,
    expected_count: int,
    max_retries: int = 3,
    log: Optional[ProgressFn] = None,
) -> list:
    """Index Mapping + 길이 검증 + retry feedback.

    Returns:
        List[str]: outputs 배열 (길이 = expected_count 보장, fallback 시 [번역 누락] padding)
    """
    log_fn = log or print
    # System = TRANSLATION_SYSTEM_PROMPT (Layer 8/11/13/15 entity 규칙 포함).
    # User = _build_index_mapping_prompt 의 출력 형식 override (JSON outputs 배열).
    messages: list = [
        {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    # json_schema strict 모드 — minItems/maxItems 로 정확히 N개 강제.
    # 5/13 E2E 결과의 길이 미스매치 (23/22 outputs vs 25 expected) 근본 차단.
    # 5/12 endpoint verify: qwen3.6-35b-q5 의 json_schema strict + additionalProperties=False 정합.
    strict_response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "translation_outputs",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "outputs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": expected_count,
                        "maxItems": expected_count,
                    },
                },
                "required": ["outputs"],
                "additionalProperties": False,
            },
        },
    }
    # Phase 4a-1 — xgrammar grammar-recovery loop 회피용 fallback mode.
    # 5/16 진단: xgrammar 0.2.0 + strict schema 에서 일부 입력이 grammar-recovery
    # loop 진입 → 8192 tokens 까지 rejected token 재샘플링 (slow chunk 245~281초).
    # 첫 시도 strict, 실패 시 json_object mode 로 전환:
    #   - JSON parse fail 또는 finish_reason=length → loose mode 전환 후 retry
    #   - json_object 는 JSON 구문만 강제, 스키마 길이 강제 없음 → grammar 복잡도 낮음
    #   - 기존 length mismatch retry 가 결과 검증 담당 (양 환경 safety net)
    #
    # 5/17 시도 (실패, dead code 제거됨):
    #   - A-3 (strict 첫 시도 + 30초 timeout): httpx read timeout 한계로 wall-clock
    #     강제 불가 (chunk 9 가 281초 소비했지만 timeout 미발동). retry loop 의
    #     try/except APITimeoutError 블록은 dead code 가 되어 제거. helper 함수
    #     timeout 파라미터 시그니처는 future hook (wall-clock timeout 도입 시
    #     재활용) 으로 유지.
    loose_response_format = {"type": "json_object"}
    max_tokens = config.translation_max_tokens or TRANSLATION_MAX_TOKENS
    outputs: list = []
    use_strict_mode = True

    for retry in range(max_retries):
        active_response_format = strict_response_format if use_strict_mode else loose_response_format
        content, finish_reason = _call_llm_with_continuation(
            config, messages, max_tokens, response_format=active_response_format
        )
        # JSON 파싱
        try:
            parsed = json.loads(content)
            outputs = parsed.get("outputs", []) or []
        except json.JSONDecodeError as exc:
            log_fn(f"   ⚠ JSON 파싱 부재 (retry {retry + 1}/{max_retries}): {exc}")
            # 첫 실패 시 loose mode 전환 (xgrammar grammar-recovery loop 회피)
            if use_strict_mode:
                log_fn(f"   ↳ json_object mode 전환 (xgrammar 우회)")
                use_strict_mode = False
            messages.append({
                "role": "user",
                "content": (
                    f"Previous response was not valid JSON. Return only "
                    f'{{"outputs": [...]}} with exactly {expected_count} items.'
                ),
            })
            continue

        # 길이 검증 — drift 근본 차단
        if len(outputs) == expected_count:
            log_fn(f"   ✅ Index Mapping 정합 — {len(outputs)} outputs (finish_reason={finish_reason})")
            return outputs

        # finish_reason=length + strict mode → grammar-recovery loop 가능성 → mode 전환
        if finish_reason == "length" and use_strict_mode:
            log_fn(f"   ↳ finish_reason=length 감지, json_object mode 전환 (xgrammar 우회)")
            use_strict_mode = False

        log_fn(
            f"   ⚠ 길이 미스매치: {len(outputs)} != {expected_count} "
            f"(retry {retry + 1}/{max_retries}, finish_reason={finish_reason})"
        )
        messages.append({"role": "assistant", "content": content})
        messages.append({
            "role": "user",
            "content": (
                f"Previous output had {len(outputs)} items. Need exactly "
                f"{expected_count} items in same order. Return complete JSON: "
                '{"outputs": [...]}.'
            ),
        })

    # 3 retries 모두 실패 — fallback (padding 또는 truncate)
    log_fn(
        f"   ⚠ Index Mapping retry {max_retries}회 실패 — fallback "
        f"({len(outputs)} → {expected_count})"
    )
    if len(outputs) < expected_count:
        outputs = list(outputs) + ["[번역 누락]"] * (expected_count - len(outputs))
    else:
        outputs = list(outputs)[:expected_count]
    return outputs


def translate_chunk_index_mapping_v2(
    chunk: List[Segment],
    context_block: str,
    config: LLMConfig,
    log: Optional[ProgressFn] = None,
) -> str:
    """단일 chunk 영역의 Index Mapping 적용 — 체크포인트 2 verify 영역.

    체크포인트 3 시 translate_transcript 영역 통합 결정.
    """
    inputs = [f"{s.speaker}: {s.text}" for s in chunk]
    prompt = _build_index_mapping_prompt(inputs, context_block)

    outputs = _call_llm_with_index_mapping(
        config, prompt, expected_count=len(inputs), max_retries=3, log=log,
    )

    # 클라이언트 측 timestamp 부착 — zip 으로 결정론적 매핑 (drift 불가능).
    # Output 의 korean 영역에 화자 라벨 (예: "판카즈 샤르마(Pankaj Sharma): 본문")
    # 이 이미 포함되어 있어 segment.speaker prefix 영역 부재 — korean 그대로 사용.
    # Line break = \n\n (Layer 14 정합 — Index Mapping 영역 결정론적 정합).
    result_lines: List[str] = []
    for segment, korean in zip(chunk, outputs):
        ts = f"[{_format_ts(segment.start)}]"
        result_lines.append(f"{ts} {korean}")
    return "\n\n".join(result_lines)
