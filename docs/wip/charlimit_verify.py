"""char_limit=2000 검증 — 기타 1 (F3QDC7HDMyg) timeout 해소 측정 (5/24).

기존 재분할 segments 재사용 (verify_results/mv/F3QDC7HDMyg/resplit.json).
chunk_segments(char_limit=2000, segment_limit=12) 적용 후 1-pass + 2-pass.

비교: 이전 측정 (char_limit=12000, segment_limit=12) → 1p timeout 6, 2p 정합 14/32.
"""
from __future__ import annotations

import os
import sys
import re
import json
import time
import shutil
from pathlib import Path
from typing import List

for line in open("/Users/gesicht/GuruNote/.env").read().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

sys.path.insert(0, "/Users/gesicht/GuruNote")
import gurunote.llm as llm_mod
from gurunote.types import Segment, Transcript
from gurunote.llm import LLMConfig, translate_transcript

VIDEO_ID = "F3QDC7HDMyg"
OUT_DIR = Path("/Users/gesicht/GuruNote/verify_results/mv") / VIDEO_ID
CACHE_DIR = Path.home() / ".gurunote" / "entity_cache"

CHAR_LIMIT = 2000
SEGMENT_LIMIT = 12
MODEL = "Qwen3.6-35B-A3B-oQ6-mtp"


def isolate_cache(label):
    bak = CACHE_DIR.parent / f"entity_cache.bak.{label}"
    if CACHE_DIR.exists():
        shutil.move(str(CACHE_DIR), str(bak))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return bak


def restore_cache(bak):
    if CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)
    if bak.exists():
        shutil.move(str(bak), str(CACHE_DIR))


def patched_run(transcript, two_pass, char_limit, segment_limit, label):
    orig_size = llm_mod.MAX_SEGMENTS_PER_CHUNK
    orig_chunk_fn = llm_mod.chunk_segments
    orig_char = llm_mod.DEFAULT_CHUNK_CHAR_LIMIT
    llm_mod.MAX_SEGMENTS_PER_CHUNK = segment_limit
    llm_mod.DEFAULT_CHUNK_CHAR_LIMIT = char_limit

    def patched(segments, char_limit_=None, segment_limit_=None):
        return orig_chunk_fn(
            segments,
            char_limit=char_limit_ if char_limit_ else char_limit,
            segment_limit=segment_limit_ if segment_limit_ else segment_limit,
        )
    llm_mod.chunk_segments = patched

    try:
        os.environ["GURUNOTE_TWO_PASS"] = "1" if two_pass else "0"
        config = LLMConfig.from_env(provider="openai_compatible")
        config.model = MODEL
        vctx = {"id": VIDEO_ID + ("_2p" if two_pass else "_1p") + "_cl2k",
                 "title": "F3QDC7HDMyg test",
                 "uploader": "", "description": "",
                 "url": f"https://youtu.be/{VIDEO_ID}"}

        log_lines = []
        def log_fn(msg):
            ts = time.strftime("%H:%M:%S")
            log_lines.append(f"[{ts}] {msg}")
            if any(k in msg for k in ["⚠", "🛟"]):
                print(f"    [{label}] {msg[:140]}", flush=True)

        t0 = time.time()
        body = translate_transcript(transcript, config=config, progress=log_fn,
                                     video_context=vctx, stop_event=None)
        elapsed = time.time() - t0
    finally:
        llm_mod.MAX_SEGMENTS_PER_CHUNK = orig_size
        llm_mod.chunk_segments = orig_chunk_fn
        llm_mod.DEFAULT_CHUNK_CHAR_LIMIT = orig_char
    return body, log_lines, elapsed


def analyze_log(log_lines, two_pass):
    timeouts = sum(1 for ln in log_lines if "wall-clock timeout — retry" in ln)
    length_mismatch = sum(1 for ln in log_lines if "길이 미스매치" in ln)
    pattern = re.compile(r"1단계 출력 — (\d+) lines / N=(\d+)")
    lc = [(int(m.group(1)), int(m.group(2)))
           for m in (pattern.search(ln) for ln in log_lines) if m]
    return {
        "timeouts": timeouts,
        "length_mismatch": length_mismatch,
        "total_chunks": len(lc) if two_pass else None,
        "match_exact": sum(1 for ln, n in lc if ln == n) if two_pass else None,
        "match_less": sum(1 for ln, n in lc if ln < n) if two_pass else None,
        "match_extreme": sum(1 for ln, n in lc if ln == 1 and n > 5) if two_pass else None,
    }


def main():
    print(f"char_limit={CHAR_LIMIT} 검증 — {VIDEO_ID}")
    print(f"모델: {MODEL}")
    print()

    resplit = json.load(open(OUT_DIR / "resplit.json"))
    segs = [Segment(speaker=s["speaker"], start=float(s["start"]),
                     end=float(s["end"]), text=s["text"]) for s in resplit]
    tr = Transcript(segments=segs, engine="mlx", language="en",
                     raw={"language": "en", "model": "mlx-whisper-large-v3"})
    print(f"재분할 Transcript: {len(tr.segments)} segments")

    # ---- 1-pass cs=12 + char_limit=2000
    print(f"\n--- 1-pass cs={SEGMENT_LIMIT} char_limit={CHAR_LIMIT} ---")
    bak = isolate_cache(f"{VIDEO_ID}_1p_cl2k")
    try:
        body, log_lines, elapsed = patched_run(tr, two_pass=False,
                                                 char_limit=CHAR_LIMIT,
                                                 segment_limit=SEGMENT_LIMIT,
                                                 label=f"{VIDEO_ID}_1p_cl2k")
        (OUT_DIR / "1pass_cl2k_body.md").write_text(body, encoding="utf-8")
        (OUT_DIR / "1pass_cl2k_log.txt").write_text("\n".join(log_lines), encoding="utf-8")
        an1 = analyze_log(log_lines, two_pass=False)
        print(f"  time: {elapsed:.0f}s, body lines: {body.count(chr(10))}")
        print(f"  timeouts={an1['timeouts']}, length_mismatch={an1['length_mismatch']}")
    finally:
        restore_cache(bak)

    # ---- 2-pass cs=12 + char_limit=2000
    print(f"\n--- 2-pass cs={SEGMENT_LIMIT} char_limit={CHAR_LIMIT} ---")
    bak = isolate_cache(f"{VIDEO_ID}_2p_cl2k")
    try:
        body, log_lines, elapsed = patched_run(tr, two_pass=True,
                                                 char_limit=CHAR_LIMIT,
                                                 segment_limit=SEGMENT_LIMIT,
                                                 label=f"{VIDEO_ID}_2p_cl2k")
        (OUT_DIR / "2pass_cl2k_body.md").write_text(body, encoding="utf-8")
        (OUT_DIR / "2pass_cl2k_log.txt").write_text("\n".join(log_lines), encoding="utf-8")
        an2 = analyze_log(log_lines, two_pass=True)
        print(f"  time: {elapsed:.0f}s, body lines: {body.count(chr(10))}")
        print(f"  timeouts={an2['timeouts']}")
        print(f"  1단계 정합: {an2['match_exact']} / {an2['total_chunks']}")
        print(f"  합침: {an2['match_less']}, 극단(1줄): {an2['match_extreme']}")
    finally:
        restore_cache(bak)

    # ---- 종합 비교
    pct = an2['match_exact'] / an2['total_chunks'] * 100 if an2['total_chunks'] else 0
    print(f"\n{'='*70}")
    print(f"종합 — char_limit 비교 (F3QDC7HDMyg)")
    print(f"{'='*70}")
    print(f"  metric               | cl=12000 (이전)  | cl=2000 (본 측정)")
    print(f"  chunks               | 32              | 35")
    print(f"  chunk_max chars      | 5061            | 1989")
    print(f"  1-pass timeouts      | 6               | {an1['timeouts']}")
    print(f"  1-pass length_mis    | 1               | {an1['length_mismatch']}")
    print(f"  2-pass timeouts      | 0               | {an2['timeouts']}")
    print(f"  2-pass 정합          | 14/32 (44%)     | {an2['match_exact']}/{an2['total_chunks']} ({pct:.0f}%)")
    print(f"  2-pass 합침          | 18              | {an2['match_less']}")
    print(f"  2-pass 극단(1줄)     | 8               | {an2['match_extreme']}")


if __name__ == "__main__":
    main()
