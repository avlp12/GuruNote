"""
GuruNote 🎙️ — 글로벌 IT/AI 구루들의 인사이트
============================================

해외 IT/AI 권위자(Guru)들의 유튜브 인터뷰/팟캐스트 링크를 입력하면
오디오 추출 → **VibeVoice-ASR** 화자 분리 STT → LLM 한국어 번역 →
GuruNote 스타일 마크다운 요약까지 단번에 만들어주는 Streamlit 웹 앱.

요구사항:
    - Python 3.10+
    - ffmpeg (yt-dlp 의 mp3 변환)
    - GPU (VibeVoice-ASR 7B 추론에 권장. 없으면 AssemblyAI 폴백)
    - requirements.txt 의 패키지들

실행:
    streamlit run app.py
"""

from __future__ import annotations

import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from gurunote.audio import (
    AudioDownloadResult,
    cleanup_dir,
    download_audio,
    is_probably_youtube_url,
)
from gurunote.exporter import build_gurunote_markdown, sanitize_filename
from gurunote.llm import LLMConfig, summarize_translation, translate_transcript
from gurunote.stt import transcribe
from gurunote.types import Transcript, _format_ts

# -----------------------------------------------------------------------------
# 부팅
# -----------------------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="GuruNote 🎙️",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# 헤더 & 사이드바
# -----------------------------------------------------------------------------
def render_header() -> None:
    st.title("GuruNote 🎙️: 글로벌 IT/AI 구루들의 인사이트")
    st.caption(
        "유튜브 링크 하나로 해외 IT/AI 팟캐스트와 인터뷰를 "
        "**화자 분리된 한국어 요약본**으로 변환합니다."
    )
    st.divider()


def render_sidebar() -> dict:
    """사이드바 — 설정값을 dict 로 반환."""
    with st.sidebar:
        st.header("✨ GuruNote 란?")
        st.markdown(
            "- **STT + 화자 분리** — Microsoft VibeVoice-ASR (오픈소스)\n"
            "- **IT/AI 전문 톤 한국어 번역** — gpt-4o / claude-3.5-sonnet\n"
            "- **인사이트 / 타임라인 / 전체 스크립트** 마크다운 요약\n"
            "- 결과를 `.md` 파일로 다운로드"
        )
        st.divider()

        st.subheader("⚙️ 설정")
        engine_label = st.selectbox(
            "STT 엔진",
            options=["auto", "vibevoice", "assemblyai"],
            index=0,
            help=(
                "auto: VibeVoice 가 가능하면 사용, 안되면 AssemblyAI 폴백 (권장).\n"
                "vibevoice: 항상 VibeVoice-ASR (오픈소스, GPU 권장).\n"
                "assemblyai: 항상 AssemblyAI Cloud API."
            ),
        )

        env_provider = os.environ.get("LLM_PROVIDER", "openai")
        provider = st.selectbox(
            "LLM Provider",
            options=["openai", "anthropic"],
            index=0 if env_provider == "openai" else 1,
        )

        st.divider()
        st.subheader("📋 사용법")
        st.markdown(
            "1. 유튜브 인터뷰/팟캐스트 URL 입력\n"
            "2. **GuruNote 생성하기** 클릭\n"
            "3. 결과 탭에서 요약/번역/원문 확인\n"
            "4. `.md` 파일 다운로드"
        )

        st.divider()
        st.caption("Powered by VibeVoice-ASR · yt-dlp · Streamlit")

        return {"engine": engine_label, "provider": provider}


# -----------------------------------------------------------------------------
# 파이프라인 실행
# -----------------------------------------------------------------------------
def run_pipeline(url: str, engine: str, provider: str) -> None:
    """Step 1 → Step 5 실행 + 세션 상태 저장."""
    if not is_probably_youtube_url(url):
        st.error("올바른 유튜브 URL 을 입력해주세요. (예: https://www.youtube.com/watch?v=...)")
        return

    tmp_dir = tempfile.mkdtemp(prefix="gurunote_")

    try:
        with st.status("GuruNote 파이프라인 실행 중...", expanded=True) as status:
            log = lambda msg: st.write(msg)  # noqa: E731

            # ----- Step 1: 오디오 다운로드 -----
            st.write(f"📁 작업 폴더: `{tmp_dir}`")
            st.write("⬇️ **Step 1.** yt-dlp 로 오디오 추출 중…")
            audio: AudioDownloadResult = download_audio(url, tmp_dir)
            audio_size_mb = os.path.getsize(audio.audio_path) / (1024 * 1024)
            st.write(
                f"✅ `{audio.video_title}` ({audio_size_mb:.1f} MB, "
                f"{int(audio.duration_sec)}s)"
            )

            # ----- Step 2: STT + 화자 분리 -----
            st.write("🎙️ **Step 2.** 화자 분리 STT (VibeVoice-ASR) …")
            transcript: Transcript = transcribe(
                audio.audio_path, engine=engine, progress=log
            )
            st.write(
                f"✅ {len(transcript.segments)} 세그먼트, "
                f"{len(transcript.speakers)} 화자, "
                f"엔진=`{transcript.engine}`"
            )

            # ----- Step 3: LLM 번역 -----
            st.write("🌐 **Step 3.** LLM 한국어 번역 (청크 분할)…")
            # 사이드바 선택을 request-local 하게 주입 (process env 는 절대 건드리지
            # 않음 — Streamlit 동시 세션에서 race 가 나지 않도록).
            llm_cfg = LLMConfig.from_env(provider=provider)
            translated = translate_transcript(transcript, config=llm_cfg, progress=log)
            st.write(f"✅ 번역 완료 ({len(translated):,} chars)")

            # ----- Step 4: 요약본 생성 -----
            st.write("📝 **Step 4.** GuruNote 스타일 요약본 생성…")
            summary_md = summarize_translation(
                translated, title=audio.video_title, config=llm_cfg, progress=log
            )
            st.write("✅ 요약 완료")

            # ----- Step 5: 마크다운 조립 -----
            st.write("📦 **Step 5.** 마크다운 조립…")
            full_md = build_gurunote_markdown(
                title=audio.video_title,
                webpage_url=audio.webpage_url,
                summary_md=summary_md,
                translated_text=translated,
                transcript=transcript,
                uploader=audio.uploader,
                stt_engine=transcript.engine,
            )
            st.write("✅ 완료")

            status.update(label="GuruNote 생성 완료 🎉", state="complete", expanded=False)

        # 세션 상태에 저장 → 탭 렌더링에서 사용
        st.session_state["result"] = {
            "audio": audio,
            "transcript": transcript,
            "translated": translated,
            "summary_md": summary_md,
            "full_md": full_md,
        }
    except Exception as exc:  # noqa: BLE001
        st.error(f"파이프라인 실행 중 오류: {exc}")
        st.exception(exc)
    finally:
        # PRD §5 - 작업 완료 후 임시 오디오 파일 삭제
        cleanup_dir(tmp_dir)


# -----------------------------------------------------------------------------
# 결과 렌더링
# -----------------------------------------------------------------------------
def render_results() -> None:
    result = st.session_state.get("result")
    if not result:
        return

    audio: AudioDownloadResult = result["audio"]
    transcript: Transcript = result["transcript"]
    translated: str = result["translated"]
    summary_md: str = result["summary_md"]
    full_md: str = result["full_md"]

    st.divider()
    st.subheader(f"🎉 결과: {audio.video_title}")

    file_name = f"GuruNote_{sanitize_filename(audio.video_title)}.md"
    st.download_button(
        label="📥 GuruNote 마크다운 다운로드",
        data=full_md.encode("utf-8"),
        file_name=file_name,
        mime="text/markdown",
        type="primary",
    )

    tab_summary, tab_translation, tab_original = st.tabs(
        ["📌 GuruNote 요약본", "🇰🇷 전체 번역 스크립트", "🇺🇸 영어 원문"]
    )

    with tab_summary:
        st.markdown(summary_md)

    with tab_translation:
        st.markdown(translated)

    with tab_original:
        for seg in transcript.segments:
            ts = _format_ts(seg.start)
            st.markdown(f"**[{ts}] Speaker {seg.speaker}:** {seg.text}")


# -----------------------------------------------------------------------------
# 메인
# -----------------------------------------------------------------------------
def main() -> None:
    render_header()
    settings = render_sidebar()

    st.subheader("🔗 유튜브 URL 입력")
    url = st.text_input(
        "유튜브 URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
    )
    submitted = st.button("GuruNote 생성하기", type="primary")

    if submitted:
        run_pipeline(url, engine=settings["engine"], provider=settings["provider"])

    render_results()

    st.divider()
    st.caption(
        "Powered by **Microsoft VibeVoice-ASR** · OpenAI / Anthropic · yt-dlp · Streamlit"
    )


if __name__ == "__main__":
    main()
