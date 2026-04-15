"""
Step 3 & 4: LLM 기반 한국어 번역 + GuruNote 스타일 마크다운 요약.

- Provider: OpenAI (gpt-4o) 또는 Anthropic (claude-3-5-sonnet)
- 긴 영상 대응: 세그먼트를 토큰 한도에 맞춰 청크 분할 → 청크별 번역 → 병합
- 번역 결과를 다시 요약 단계에 통째로 넣어 최종 마크다운을 만든다.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Callable, List, Optional

from gurunote.types import Segment, Transcript, _format_ts

ProgressFn = Callable[[str], None]


# =============================================================================
# 시스템 프롬프트 (PRD §3 - "매우 중요한 시스템 프롬프트 지시사항")
# =============================================================================
TRANSLATION_SYSTEM_PROMPT = """\
너는 GuruNote 의 수석 에디터이자 세계 최고 수준의 IT/AI 테크 저널리스트야.

다음 규칙을 반드시 지켜:
1. 입력은 영어 인터뷰/팟캐스트 스크립트이며 화자 라벨(Speaker A, Speaker B …)
   과 타임스탬프가 포함돼 있어. 화자 라벨과 타임스탬프 형식은 그대로 보존해.
2. 문맥을 파악해 Speaker A, B 가 진행자(Host)와 게스트(Guest) 중 누구인지
   추론하고, 등장 인물의 실명(예: Lex Fridman, Sam Altman, Dario Amodei 등)이
   명확하면 화자 라벨 옆에 실명을 함께 표기해.
   예) [00:01:23] Speaker A (Lex Fridman): ...
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
"""


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
"""


# =============================================================================
# Provider 추상화
# =============================================================================
@dataclass
class LLMConfig:
    provider: str            # "openai" | "openai_compatible" | "anthropic"
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
                model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
                api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
                temperature=temp,
                translation_max_tokens=translation_max_tokens,
                summary_max_tokens=summary_max_tokens,
            )
        if provider == "openai_compatible":
            return cls(
                provider="openai_compatible",
                model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
                api_key=os.environ.get("OPENAI_API_KEY", "local"),
                base_url=os.environ.get("OPENAI_BASE_URL", ""),
                temperature=temp,
                translation_max_tokens=translation_max_tokens,
                summary_max_tokens=summary_max_tokens,
            )
        return cls(
            provider="openai",
            model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_BASE_URL", ""),
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
    if config.provider in {"openai", "anthropic"} and not config.api_key:
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
# gpt-4o / claude-3.5-sonnet 의 응답 한도(8192) 안에 안전하게 들어와야 한다는
# 점을 같이 고려해 청크 입력을 ~12000 chars (≈ 3000 토큰) 로 잡는다.
# 이러면 출력은 최대 ~4000 토큰 수준에서 형성되며 TRANSLATION_MAX_TOKENS=8192
# 안에 충분히 들어와 mid-script truncation 위험이 사라진다.
DEFAULT_CHUNK_CHAR_LIMIT = 12_000

# 번역/요약 호출의 응답 토큰 상한 (gpt-4o 16384, claude-3.5-sonnet 8192 둘 다
# 수용 가능한 안전한 값).
TRANSLATION_MAX_TOKENS = 8192
SUMMARY_MAX_TOKENS = 4096


def chunk_segments(
    segments: List[Segment], char_limit: int = DEFAULT_CHUNK_CHAR_LIMIT
) -> List[List[Segment]]:
    """세그먼트 리스트를 글자수 기준으로 그룹핑. 한 세그먼트는 분할하지 않는다."""
    chunks: List[List[Segment]] = []
    current: List[Segment] = []
    current_size = 0

    for seg in segments:
        seg_text = seg.text or ""
        # 화자 라벨/타임스탬프 오버헤드까지 대략 30자 더해 추정
        seg_size = len(seg_text) + 30
        if current and current_size + seg_size > char_limit:
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
# Step 3: 번역
# =============================================================================
def translate_transcript(
    transcript: Transcript,
    config: Optional[LLMConfig] = None,
    progress: Optional[ProgressFn] = None,
    video_context: Optional[dict] = None,
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
        # 청크 간 쿨다운 — API Rate Limit 방지 (첫 청크는 건너뜀)
        if i > 1:
            time.sleep(CHUNK_DELAY_SEC)
        log(f"   ↳ 청크 {i}/{len(chunks)} 번역 중…")
        segments_block = _segments_to_user_block(chunk)
        # 영상 컨텍스트는 첫 청크에만 붙여도 일반적으로 충분하지만, 청크 번역이
        # 독립 실행되기 때문에 모든 청크에 동일한 컨텍스트를 동봉해야 화자 매핑이
        # 일관되게 유지된다.
        user_block = (
            f"{context_block}\n### 번역 대상 스크립트\n{segments_block}"
            if context_block
            else segments_block
        )
        translated = _call_llm(
            config,
            system=TRANSLATION_SYSTEM_PROMPT,
            user=user_block,
            max_tokens=config.translation_max_tokens or TRANSLATION_MAX_TOKENS,
        )
        translated_parts.append(translated)

    log("✅ 번역 완료")
    return "\n\n".join(translated_parts).strip()


# =============================================================================
# Step 4: 요약 (GuruNote 스타일)
# =============================================================================
def summarize_translation(
    translated_text: str,
    title: str,
    config: Optional[LLMConfig] = None,
    progress: Optional[ProgressFn] = None,
    video_context: Optional[dict] = None,
) -> str:
    """
    번역본 → 마크다운 요약 (영상 제목/인사이트/타임라인 섹션).
    전체 스크립트는 포함하지 않으며 호출자가 별도로 붙인다.

    video_context 가 제공되면 공식 챕터 목록을 타임라인 섹션의 뼈대로
    사용하도록 LLM 에 주입한다.
    """
    log = progress or (lambda _msg: None)
    config = config or LLMConfig.from_env()

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
        return _call_llm(
            config,
            system=system,
            user=merged_user,
            max_tokens=config.summary_max_tokens or SUMMARY_MAX_TOKENS,
        ).strip()

    log("📝 GuruNote 요약본 생성 중…")
    return _call_llm(
        config,
        system=system,
        user=translated_text,
        max_tokens=config.summary_max_tokens or SUMMARY_MAX_TOKENS,
    ).strip()


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
