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
    SUPPORTED_EXTS,
    AudioDownloadResult,
    cleanup_dir,
    download_audio,
    extract_audio_from_file,
    is_probably_youtube_url,
)
from gurunote.exporter import build_gurunote_markdown, sanitize_filename
from gurunote.llm import LLMConfig, summarize_translation, test_connection, translate_transcript
from gurunote.settings import save_settings
from gurunote.stt import transcribe
from gurunote.types import Transcript, _format_ts
from gurunote.updater import check_updates, update_project

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
            "- **IT/AI 전문 톤 한국어 번역** — gpt-5.4 / claude-sonnet-4-6\n"
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
            options=["openai", "openai_compatible", "anthropic"],
            index=0 if env_provider == "openai" else (2 if env_provider == "anthropic" else 1),
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


def render_settings_tab(default_provider: str) -> None:
    st.subheader("⚙️ Settings")
    st.caption("`.env` 를 직접 열지 않아도 이 탭에서 LLM 설정을 저장/테스트할 수 있습니다.")

    with st.form("settings_form"):
        provider = st.selectbox(
            "LLM Provider",
            options=["openai", "openai_compatible", "anthropic"],
            index=0 if default_provider == "openai" else (2 if default_provider == "anthropic" else 1),
            help="openai_compatible: oMLX / vLLM / Ollama / LM Studio / llama.cpp 서버 등",
        )
        openai_key = st.text_input(
            "OpenAI API Key",
            value=os.environ.get("OPENAI_API_KEY", ""),
            type="password",
        )
        openai_base_url = st.text_input(
            "OpenAI Base URL (Local/Compatible)",
            value=os.environ.get("OPENAI_BASE_URL", ""),
            disabled=provider == "anthropic",
            placeholder="예: http://127.0.0.1:8000/v1",
        )
        openai_model = st.text_input(
            "OpenAI/Compatible Model",
            value=os.environ.get("OPENAI_MODEL", "gpt-5.4"),
        )
        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=os.environ.get("ANTHROPIC_API_KEY", ""),
            type="password",
        )
        anthropic_model = st.text_input(
            "Anthropic Model",
            value=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        )
        c1, c2, _ = st.columns([1, 1, 2])
        temperature = c1.number_input(
            "Temperature", min_value=0.0, max_value=2.0, step=0.1,
            value=float(os.environ.get("LLM_TEMPERATURE", "0.2") or 0.2),
        )
        tr_max = c2.number_input(
            "번역 Max Tokens", min_value=256, max_value=32768, step=256,
            value=int(os.environ.get("LLM_TRANSLATION_MAX_TOKENS", "8192") or 8192),
        )
        sum_max = st.number_input(
            "요약 Max Tokens", min_value=128, max_value=16384, step=128,
            value=int(os.environ.get("LLM_SUMMARY_MAX_TOKENS", "4096") or 4096),
        )

        save = st.form_submit_button("💾 Save Settings", type="primary")
        test = st.form_submit_button("🧪 Test Connection")

    settings_payload = {
        "LLM_PROVIDER": provider,
        "OPENAI_API_KEY": openai_key,
        "OPENAI_BASE_URL": openai_base_url,
        "OPENAI_MODEL": openai_model,
        "ANTHROPIC_API_KEY": anthropic_key,
        "ANTHROPIC_MODEL": anthropic_model,
        "LLM_TEMPERATURE": str(temperature),
        "LLM_TRANSLATION_MAX_TOKENS": str(int(tr_max)),
        "LLM_SUMMARY_MAX_TOKENS": str(int(sum_max)),
    }

    if save:
        changed, backup = save_settings(settings_payload, create_backup=True)
        st.success(
            f"설정 저장 완료 (변경 {changed}개)"
            + (f" · 백업: `{backup.name}`" if backup else "")
        )

    if test:
        try:
            # 저장하지 않아도 현재 폼 값으로 즉시 테스트
            tmp_cfg = LLMConfig.from_env(provider=provider)
            tmp_cfg.api_key = (openai_key if provider != "anthropic" else anthropic_key).strip()
            tmp_cfg.base_url = openai_base_url.strip()
            tmp_cfg.model = openai_model.strip() if provider != "anthropic" else anthropic_model.strip()
            tmp_cfg.temperature = float(temperature)
            resp = test_connection(tmp_cfg)
            st.success(f"연결 성공: {resp}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"연결 실패: {exc}")

    st.divider()
    st.markdown("#### 🔄 업데이트")
    u1, u2 = st.columns(2)
    if u1.button("업데이트 상태 확인", use_container_width=True):
        try:
            lines: list[str] = []
            status = check_updates(lines.append)
            st.code("\n".join(lines + [status]) if lines else status, language="bash")
        except Exception as exc:  # noqa: BLE001
            st.error(f"업데이트 확인 실패: {exc}")
    if u2.button("업데이트 실행", use_container_width=True):
        try:
            lines: list[str] = []
            with st.status("업데이트 실행 중...", expanded=True):
                update_project(lines.append, upgrade_deps=True)
                for line in lines:
                    st.write(line)
            st.success("업데이트 완료. 앱을 재실행하면 최신 버전이 반영됩니다.")
        except Exception as exc:  # noqa: BLE001
            st.error(f"업데이트 실패: {exc}")


# -----------------------------------------------------------------------------
# 파이프라인 실행
# -----------------------------------------------------------------------------
def run_pipeline(
    engine: str,
    provider: str,
    *,
    youtube_url: str = "",
    local_file_path: str = "",
) -> None:
    """Step 1 → Step 5 실행 + 세션 상태 저장."""
    if not youtube_url and not local_file_path:
        st.error("유튜브 URL 또는 로컬 파일을 입력해주세요.")
        return

    tmp_dir = tempfile.mkdtemp(prefix="gurunote_")

    try:
        with st.status("GuruNote 파이프라인 실행 중...", expanded=True) as status:
            progress_bar = st.progress(0, text="진행률 0%")
            def set_progress(pct: int, label: str) -> None:
                progress_bar.progress(max(0, min(100, pct)), text=f"{label} ({pct}%)")

            log = lambda msg: st.write(msg)  # noqa: E731

            # ----- Step 1: 오디오 준비 -----
            set_progress(5, "Step 1 오디오 준비 중")
            st.write(f"📁 작업 폴더: `{tmp_dir}`")
            if youtube_url:
                st.write("⬇️ **Step 1.** yt-dlp 로 오디오 추출 중…")
                audio: AudioDownloadResult = download_audio(youtube_url, tmp_dir)
            else:
                st.write("🎵 **Step 1.** 로컬 파일에서 오디오 추출 중…")
                audio = extract_audio_from_file(local_file_path, tmp_dir)
            audio_size_mb = os.path.getsize(audio.audio_path) / (1024 * 1024)
            st.write(
                f"✅ `{audio.video_title}` ({audio_size_mb:.1f} MB, "
                f"{int(audio.duration_sec)}s)"
            )
            set_progress(20, "Step 1 완료")
            effective_engine = engine
            if audio.duration_sec > 3600 and engine == "auto":
                effective_engine = "assemblyai"
                st.info(
                    "ℹ️ 60분 초과 오디오는 `auto` 모드에서 AssemblyAI 로 자동 전환합니다."
                )
            elif audio.duration_sec > 3600 and engine == "vibevoice":
                st.warning(
                    "⚠️ 현재 VibeVoice 단일 패스는 최대 60분 처리에 최적화되어 있어, "
                    "긴 영상은 일부만 전사될 수 있습니다."
                )

            # 유튜브 메타데이터 로그 (로컬 파일에는 대부분 비어있음)
            if audio.upload_date:
                st.write(f"📅 게시일: `{audio.upload_date}`")
            if audio.chapters:
                st.write(f"⏱️ 공식 챕터 {len(audio.chapters)} 개 감지")
            if audio.subtitles_text:
                st.write(
                    f"💬 기존 자막 감지 ({len(audio.subtitles_text):,} chars) — "
                    "화자 이름 추론과 챕터 유지에 활용됩니다."
                )

            video_ctx = audio.to_context_dict()

            # ----- Step 2: STT + 화자 분리 -----
            set_progress(25, "Step 2 STT 진행 중")
            st.write("🎙️ **Step 2.** 화자 분리 STT (VibeVoice-ASR) …")
            transcript: Transcript = transcribe(
                audio.audio_path, engine=effective_engine, progress=log
            )
            st.write(
                f"✅ {len(transcript.segments)} 세그먼트, "
                f"{len(transcript.speakers)} 화자, "
                f"엔진=`{transcript.engine}`"
            )
            set_progress(55, "Step 2 완료")

            # ----- Step 3: LLM 번역 -----
            set_progress(60, "Step 3 번역 진행 중")
            st.write("🌐 **Step 3.** LLM 한국어 번역 (청크 분할)…")
            # 사이드바 선택을 request-local 하게 주입 (process env 는 절대 건드리지
            # 않음 — Streamlit 동시 세션에서 race 가 나지 않도록).
            llm_cfg = LLMConfig.from_env(provider=provider)
            translated = translate_transcript(
                transcript, config=llm_cfg, progress=log, video_context=video_ctx
            )
            st.write(f"✅ 번역 완료 ({len(translated):,} chars)")
            set_progress(82, "Step 3 완료")

            # ----- Step 4: 요약본 생성 -----
            set_progress(86, "Step 4 요약 진행 중")
            st.write("📝 **Step 4.** GuruNote 스타일 요약본 생성…")
            summary_md = summarize_translation(
                translated,
                title=audio.video_title,
                config=llm_cfg,
                progress=log,
                video_context=video_ctx,
            )
            st.write("✅ 요약 완료")
            set_progress(94, "Step 4 완료")

            # ----- Step 5: 마크다운 조립 -----
            set_progress(96, "Step 5 마크다운 조립 중")
            st.write("📦 **Step 5.** 마크다운 조립…")
            full_md = build_gurunote_markdown(
                title=audio.video_title,
                webpage_url=audio.webpage_url,
                summary_md=summary_md,
                translated_text=translated,
                transcript=transcript,
                uploader=audio.uploader,
                stt_engine=transcript.engine,
                upload_date=audio.upload_date,
                chapters=audio.chapters,
                subtitles_source=audio.subtitles_source,
            )
            st.write("✅ 완료")
            set_progress(100, "모든 단계 완료")

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
    tab_run, tab_settings = st.tabs(["🎧 GuruNote 생성", "⚙️ Settings"])

    with tab_run:
        st.subheader("🎧 오디오 소스 선택")
        input_tab_yt, input_tab_local = st.tabs(["🔗 유튜브 URL", "📁 로컬 파일"])

        with input_tab_yt:
            url = st.text_input(
                "유튜브 URL",
                placeholder="https://www.youtube.com/watch?v=...",
                label_visibility="collapsed",
            )
            yt_submitted = st.button(
                "GuruNote 생성하기", type="primary", key="btn_yt"
            )

        with input_tab_local:
            uploaded = st.file_uploader(
                "동영상 또는 오디오 파일을 업로드하세요",
                type=[ext.lstrip(".") for ext in sorted(SUPPORTED_EXTS)],
                help=f"지원 형식: {', '.join(sorted(SUPPORTED_EXTS))}",
            )
            local_submitted = st.button(
                "GuruNote 생성하기", type="primary", key="btn_local"
            )

        if yt_submitted:
            if not is_probably_youtube_url(url):
                st.error("올바른 유튜브 URL 을 입력해주세요.")
            else:
                run_pipeline(
                    engine=settings["engine"],
                    provider=settings["provider"],
                    youtube_url=url,
                )

        if local_submitted:
            if not uploaded:
                st.error("파일을 먼저 업로드해주세요.")
            else:
                # Streamlit UploadedFile → 임시 파일로 저장
                tmp_upload = tempfile.mkdtemp(prefix="gurunote_upload_")
                local_path = os.path.join(tmp_upload, uploaded.name)
                with open(local_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                run_pipeline(
                    engine=settings["engine"],
                    provider=settings["provider"],
                    local_file_path=local_path,
                )
                cleanup_dir(tmp_upload)

        render_results()

    with tab_settings:
        render_settings_tab(settings["provider"])

    st.divider()
    st.caption(
        "Powered by **Microsoft VibeVoice-ASR** · OpenAI / Anthropic · yt-dlp · Streamlit"
    )


if __name__ == "__main__":
    main()
