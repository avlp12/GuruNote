"""
GuruNote 🎙️ — 글로벌 IT/AI 구루들의 인사이트
============================================

해외 IT/AI 권위자(Guru)들의 유튜브 인터뷰/팟캐스트 링크를 입력하면
오디오 추출 → 화자 분리 STT → 한국어 번역 → 마크다운 요약까지
자동으로 만들어주는 Streamlit 웹 앱.

이 파일은 PRD 의 **Step 1 (오디오 다운로드)** 단계 뼈대 구현이다.
Step 2~5 (AssemblyAI STT, LLM 번역/요약, 결과 내보내기) 는
이후 커밋에서 점진적으로 추가된다.

요구사항:
    - Python 3.10+
    - ffmpeg (yt-dlp 가 오디오 포맷 변환 시 필요한 시스템 의존성)
    - requirements.txt 의 패키지들
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st
import yt_dlp
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# 환경변수 로드 (Step 2~ 에서 API 키 사용 대비)
# -----------------------------------------------------------------------------
load_dotenv()


# -----------------------------------------------------------------------------
# 페이지 설정 & 브랜딩
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="GuruNote 🎙️",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_header() -> None:
    """메인 헤더 + 부제 + 구분선."""
    st.title("GuruNote 🎙️: 글로벌 IT/AI 구루들의 인사이트")
    st.caption(
        "유튜브 링크 하나로 해외 IT/AI 팟캐스트와 인터뷰를 "
        "화자 분리된 한국어 요약본으로 변환합니다."
    )
    st.divider()


def render_sidebar() -> None:
    """사이드바: 앱 소개 + 사용법 + 파이프라인 진행 상태."""
    with st.sidebar:
        st.header("✨ GuruNote 란?")
        st.markdown(
            "- **STT + 화자 분리** (AssemblyAI)\n"
            "- **IT/AI 전문 톤 한국어 번역** (LLM)\n"
            "- **인사이트 / 타임라인 / 전체 스크립트** 마크다운 요약\n"
            "- 결과를 `.md` 파일로 다운로드"
        )
        st.divider()
        st.subheader("📋 사용법")
        st.markdown(
            "1. 유튜브 인터뷰/팟캐스트 URL 입력\n"
            "2. **GuruNote 생성하기** 클릭\n"
            "3. 요약본·번역본·원문 탭에서 결과 확인\n"
            "4. 마크다운 파일 다운로드"
        )
        st.divider()
        st.subheader("🛠️ 파이프라인")
        st.markdown(
            "- ✅ Step 1 — 오디오 추출\n"
            "- ⏳ Step 2 — STT + 화자 분리\n"
            "- ⏳ Step 3 — LLM 번역\n"
            "- ⏳ Step 4 — 요약본 생성\n"
            "- ⏳ Step 5 — 결과 내보내기"
        )


# -----------------------------------------------------------------------------
# Step 1: 오디오 다운로드
# -----------------------------------------------------------------------------
def _is_probably_youtube_url(url: str) -> bool:
    """엄격한 검증은 아니지만, 명백한 오타/빈값을 거른다."""
    if not url:
        return False
    url = url.strip().lower()
    return url.startswith(("http://", "https://")) and (
        "youtube.com" in url or "youtu.be" in url
    )


def download_audio(url: str, out_dir: str) -> tuple[str, str]:
    """
    유튜브 URL 에서 오디오만 추출해 mp3 로 저장한다.

    Args:
        url: 유튜브 영상 URL
        out_dir: 임시 출력 디렉토리

    Returns:
        (audio_path, video_title)
            - audio_path: 다운로드된 mp3 파일의 절대 경로
            - video_title: 영상 제목 (후속 단계의 파일명/요약 헤더에 재사용)

    Raises:
        yt_dlp.utils.DownloadError: 다운로드 실패 시
        FileNotFoundError: 변환 후 mp3 파일을 찾지 못한 경우
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noprogress": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    video_id = info.get("id", "audio")
    video_title = info.get("title", "Untitled")
    audio_path = os.path.join(out_dir, f"{video_id}.mp3")

    if not os.path.exists(audio_path):
        # 일부 케이스에서 확장자가 다르게 떨어질 수 있어 fallback 으로 폴더 스캔
        candidates = list(Path(out_dir).glob(f"{video_id}.*"))
        if not candidates:
            raise FileNotFoundError(
                f"오디오 파일을 찾을 수 없습니다: {out_dir} (id={video_id})"
            )
        audio_path = str(candidates[0])

    return audio_path, video_title


# -----------------------------------------------------------------------------
# 메인 UI
# -----------------------------------------------------------------------------
def main() -> None:
    render_header()
    render_sidebar()

    st.subheader("🔗 유튜브 URL 입력")
    url = st.text_input(
        "유튜브 URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
    )
    submitted = st.button("GuruNote 생성하기", type="primary", use_container_width=False)

    if not submitted:
        st.info("위에 유튜브 링크를 붙여 넣고 **GuruNote 생성하기** 버튼을 눌러주세요.")
        return

    if not _is_probably_youtube_url(url):
        st.error("올바른 유튜브 URL 을 입력해주세요. (예: https://www.youtube.com/watch?v=...)")
        return

    # 임시 폴더 생성 — TODO(Step 5): 파이프라인 종료 후 폴더 정리
    tmp_dir = tempfile.mkdtemp(prefix="gurunote_")

    with st.status("오디오 추출 중...", expanded=True) as status:
        try:
            st.write(f"📁 임시 작업 폴더: `{tmp_dir}`")
            st.write("⬇️ yt-dlp 로 오디오만 다운로드 중...")
            audio_path, video_title = download_audio(url, tmp_dir)
            audio_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            st.write(f"✅ 다운로드 완료: **{video_title}**")
            st.write(f"🎧 파일 경로: `{audio_path}`  ({audio_size_mb:.1f} MB)")
            status.update(label="오디오 추출 완료", state="complete", expanded=False)
        except Exception as exc:  # noqa: BLE001 - UI 상단 표시용
            status.update(label="오디오 추출 실패", state="error")
            st.error(f"오디오 다운로드 중 오류가 발생했습니다: {exc}")
            return

    st.success(f"🎉 **{video_title}** 의 오디오를 성공적으로 추출했습니다.")

    # Step 2~5 placeholder ----------------------------------------------------
    st.divider()
    st.subheader("🚧 다음 단계 (개발 예정)")
    st.info(
        "Step 2 (AssemblyAI 화자 분리 STT), Step 3 (LLM 번역), "
        "Step 4 (요약본 생성), Step 5 (마크다운 다운로드 + 임시파일 정리) 는 "
        "이후 커밋에서 추가됩니다."
    )


# -----------------------------------------------------------------------------
# 푸터
# -----------------------------------------------------------------------------
def render_footer() -> None:
    st.divider()
    st.caption("Powered by AssemblyAI · OpenAI / Anthropic · Streamlit · yt-dlp")


if __name__ == "__main__":
    main()
    render_footer()
