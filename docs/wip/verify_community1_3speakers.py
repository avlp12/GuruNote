"""community-1 + (가) 2-pass 검증 — 화자 3명 자막 영상 (5/23).

영상: https://youtu.be/oE5lNDhz9oo (화자 3명, 자막 있음)
처리: download_audio (yt-dlp + 자막) → transcribe (MLX Whisper + community-1 diarization)
       → translate_transcript (GURUNOTE_TWO_PASS=1, 2-pass + 화자 코드 부착)
"""
from __future__ import annotations

import os
import sys
import time
import tempfile
import json
from pathlib import Path

# .env 로드
for line in open("/Users/gesicht/GuruNote/.env").read().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# GURUNOTE_TWO_PASS 토글 활성화
os.environ["GURUNOTE_TWO_PASS"] = "1"

sys.path.insert(0, "/Users/gesicht/GuruNote")
from gurunote.audio import download_audio
from gurunote.stt import transcribe
from gurunote.llm import LLMConfig, translate_transcript

VIDEO_URL = "https://youtu.be/oE5lNDhz9oo"
OUT_DIR = Path("/Users/gesicht/GuruNote/verify_results")
OUT_DIR.mkdir(exist_ok=True)


def log_progress(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"  [{ts}] {msg}", flush=True)


def main() -> None:
    print("=" * 70)
    print("community-1 + (가) 2-pass 검증 — 화자 3명 자막 영상")
    print(f"URL: {VIDEO_URL}")
    print(f"DEFAULT_DIARIZATION_MODEL: {os.environ.get('PYANNOTE_DIARIZATION_MODEL', 'default(community-1)')}")
    print(f"GURUNOTE_TWO_PASS: {os.environ.get('GURUNOTE_TWO_PASS')}")
    print("=" * 70)

    with tempfile.TemporaryDirectory(prefix="gn_verify_") as tmp_dir:
        # === 1. download (오디오 + 자막) ===
        print("\n[1/3] download_audio (yt-dlp + 자막)…")
        t0 = time.time()
        audio = download_audio(VIDEO_URL, tmp_dir)
        print(f"  audio_path: {audio.audio_path}")
        print(f"  video_id: {audio.video_id}")
        print(f"  video_title: {audio.video_title!r}")
        print(f"  uploader: {audio.uploader!r}")
        print(f"  duration: {audio.duration_sec:.1f}s")
        print(f"  description (앞 200자): {(audio.description or '')[:200]!r}")
        print(f"  subtitles_source: {audio.subtitles_source!r}")
        print(f"  subtitles_text length: {len(audio.subtitles_text or '')} chars")
        print(f"  download 시간: {time.time()-t0:.1f}s")

        # === 2. transcribe (STT + community-1 diarization) ===
        print("\n[2/3] transcribe (MLX Whisper + community-1)…")
        t0 = time.time()
        transcript = transcribe(audio.audio_path, engine="mlx", progress=log_progress)
        elapsed = time.time() - t0
        print(f"  transcribe 시간: {elapsed:.1f}s")
        print(f"  segments: {len(transcript.segments)}")
        print(f"  language: {transcript.language}")
        print(f"  engine: {transcript.engine}")

        from collections import Counter
        sp_dist = Counter(s.speaker for s in transcript.segments)
        print(f"  화자 분포: {dict(sorted(sp_dist.items()))}")

        # === 3. translate_transcript (2-pass + community-1 화자 부착) ===
        print("\n[3/3] translate_transcript (2-pass + 화자 코드 부착)…")
        video_context = audio.to_context_dict()
        # video_id 추가 (audio.py to_context_dict 가 video_id 포함 부재 — bootstrap cache key용)
        video_context["id"] = audio.video_id

        config = LLMConfig.from_env(provider="openai_compatible")
        t0 = time.time()
        result = translate_transcript(
            transcript,
            config=config,
            progress=log_progress,
            video_context=video_context,
            stop_event=None,
        )
        elapsed = time.time() - t0
        print(f"  translate 시간: {elapsed:.1f}s")
        print(f"  result 본문 길이: {len(result)} chars")

        # 결과 저장
        out_body = OUT_DIR / "community1_3speakers_body.md"
        out_body.write_text(result, encoding="utf-8")
        print(f"\n결과 저장: {out_body}")

        # transcript dump (디버그용 — 화자 분포 별 분석)
        out_seg = OUT_DIR / "community1_3speakers_segments.json"
        with open(out_seg, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {"speaker": s.speaker, "start": s.start, "end": s.end, "text": s.text}
                    for s in transcript.segments
                ],
                f,
                ensure_ascii=False,
                indent=1,
            )
        print(f"segments dump: {out_seg}")


if __name__ == "__main__":
    main()
