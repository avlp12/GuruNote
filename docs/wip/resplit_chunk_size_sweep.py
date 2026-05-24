"""재분할 + chunk size 자동 조정 prototype (5/24).

목적: 1-pass timeout 해소 chunk size + 2-pass 이득 유지 확인.
재분할 segments(309)로 chunk_size 12/10/8 1-pass + 선택 size 2-pass.

monkey-patch: gurunote.llm.MAX_SEGMENTS_PER_CHUNK 만 변경 (코드 변경 부재, prototype).
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

VIDEO_ID = "oE5lNDhz9oo"
OUT_DIR = Path("/Users/gesicht/GuruNote/verify_results")
CACHE_DIR = Path.home() / ".gurunote" / "entity_cache"
RESPLIT_JSON = OUT_DIR / "community1_3speakers_resplit.json"


def build_transcript(resplit: List[dict]) -> Transcript:
    segs = [Segment(speaker=s["speaker"], start=float(s["start"]),
                     end=float(s["end"]), text=s["text"]) for s in resplit]
    return Transcript(segments=segs, engine="mlx", language="en",
                       raw={"language": "en", "model": "mlx-whisper-large-v3"})


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


def collect_log(label):
    lines = []
    def fn(msg):
        ts = time.strftime("%H:%M:%S")
        lines.append(f"[{ts}] {msg}")
        if any(k in msg for k in ["⚠", "🛟", "1단계", "complete"]):
            print(f"    [{label}] {msg[:140]}", flush=True)
    return fn, lines


def run_once(transcript, two_pass, chunk_size, label, video_id):
    """chunk_size 임시 변경 + translate_transcript 호출.

    monkey-patch: chunk_segments default arg는 module load 시점에 bound 되어
    `MAX_SEGMENTS_PER_CHUNK` 변경만으로는 부재. 함수 자체를 wrapper로 교체.
    """
    orig_size = llm_mod.MAX_SEGMENTS_PER_CHUNK
    orig_chunk_fn = llm_mod.chunk_segments
    llm_mod.MAX_SEGMENTS_PER_CHUNK = chunk_size

    def patched_chunk_segments(segments, char_limit=llm_mod.DEFAULT_CHUNK_CHAR_LIMIT,
                                segment_limit=None):
        # segment_limit 명시 부재 시 chunk_size 사용 (translate_transcript default 호출 catch)
        return orig_chunk_fn(segments, char_limit=char_limit,
                              segment_limit=segment_limit if segment_limit else chunk_size)

    llm_mod.chunk_segments = patched_chunk_segments
    try:
        os.environ["GURUNOTE_TWO_PASS"] = "1" if two_pass else "0"
        config = LLMConfig.from_env(provider="openai_compatible")
        config.model = "Qwen3.6-35B-A3B-oQ6-mtp"
        vctx = {"id": video_id, "title": "NVIDIA Dell interview",
                "uploader": "Bloomberg Television",
                "description": "Jensen Huang, Michael Dell, Ed Ludlow",
                "url": f"https://youtu.be/{video_id}"}
        log_fn, log_lines = collect_log(label)
        t0 = time.time()
        body = translate_transcript(transcript, config=config, progress=log_fn,
                                     video_context=vctx, stop_event=None)
        elapsed = time.time() - t0
    finally:
        llm_mod.MAX_SEGMENTS_PER_CHUNK = orig_size
        llm_mod.chunk_segments = orig_chunk_fn
    return body, log_lines, elapsed


def analyze_1pass(log_lines):
    timeouts = sum(1 for ln in log_lines if "wall-clock timeout — retry" in ln)
    length_mismatch = sum(1 for ln in log_lines if "길이 미스매치" in ln)
    other = sum(1 for ln in log_lines if "retry" in ln and "wall-clock" not in ln and "길이 미스" not in ln)
    return {"timeouts": timeouts, "length_mismatch": length_mismatch, "other_retry": other}


def analyze_2pass(log_lines):
    pattern = re.compile(r"1단계 출력 — (\d+) lines / N=(\d+)")
    lc = [(int(m.group(1)), int(m.group(2)))
           for m in (pattern.search(ln) for ln in log_lines) if m]
    return {
        "total_chunks": len(lc),
        "match_exact": sum(1 for ln, n in lc if ln == n),
        "match_less": sum(1 for ln, n in lc if ln < n),
        "match_extreme": sum(1 for ln, n in lc if ln == 1 and n > 5),
        "timeouts": sum(1 for ln in log_lines if "wall-clock timeout — retry" in ln),
    }


def main():
    resplit = json.load(open(RESPLIT_JSON))
    tr = build_transcript(resplit)
    print(f"재분할 Transcript: {len(tr.segments)} segments")

    results_1pass = {}
    # ---- Step 2: 1-pass chunk size sweep
    for cs in [12, 10, 8]:
        print(f"\n--- 1-pass chunk_size={cs} ---")
        bak = isolate_cache(f"1p_cs{cs}")
        try:
            body, log_lines, elapsed = run_once(tr, two_pass=False, chunk_size=cs,
                                                  label=f"1p_cs{cs}",
                                                  video_id=f"{VIDEO_ID}_1p_cs{cs}")
            (OUT_DIR / f"sweep_1pass_cs{cs}_body.md").write_text(body, encoding="utf-8")
            (OUT_DIR / f"sweep_1pass_cs{cs}_log.txt").write_text("\n".join(log_lines), encoding="utf-8")
            an = analyze_1pass(log_lines)
            results_1pass[cs] = {"elapsed": elapsed, "body_lines": body.count("\n"), **an}
            print(f"  time: {elapsed:.1f}s, body lines: {body.count(chr(10))}")
            print(f"  retry: timeouts={an['timeouts']}, length_mismatch={an['length_mismatch']}, other={an['other_retry']}")
        finally:
            restore_cache(bak)

    # ---- Step 3: timeout 0 chunk size로 2-pass
    # timeout 0 부재 시 가장 작은 timeout
    best_cs = None
    for cs in [12, 10, 8]:
        if results_1pass[cs]["timeouts"] == 0:
            best_cs = cs
            break
    if best_cs is None:
        best_cs = min(results_1pass.keys(), key=lambda c: results_1pass[c]["timeouts"])
        print(f"\n⚠ 어느 chunk size에서도 timeout 0 부재 — 최소 ({best_cs}, {results_1pass[best_cs]['timeouts']}건)")

    print(f"\n--- 2-pass chunk_size={best_cs} ---")
    bak = isolate_cache(f"2p_cs{best_cs}")
    try:
        body, log_lines, elapsed = run_once(tr, two_pass=True, chunk_size=best_cs,
                                              label=f"2p_cs{best_cs}",
                                              video_id=f"{VIDEO_ID}_2p_cs{best_cs}")
        (OUT_DIR / f"sweep_2pass_cs{best_cs}_body.md").write_text(body, encoding="utf-8")
        (OUT_DIR / f"sweep_2pass_cs{best_cs}_log.txt").write_text("\n".join(log_lines), encoding="utf-8")
        an2 = analyze_2pass(log_lines)
        results_2pass = {"chunk_size": best_cs, "elapsed": elapsed,
                          "body_lines": body.count("\n"), **an2}
        print(f"  time: {elapsed:.1f}s, body lines: {body.count(chr(10))}")
        print(f"  1단계 정합 (line==N): {an2['match_exact']} / {an2['total_chunks']}")
        print(f"  합침 (line<N): {an2['match_less']}, 극단 (1줄, N>5): {an2['match_extreme']}")
        print(f"  timeouts: {an2['timeouts']}")
    finally:
        restore_cache(bak)

    # ---- 종합
    print("\n" + "=" * 70)
    print("종합 — 1-pass chunk size sweep")
    print(f"{'cs':<5} {'time(s)':>10} {'lines':>7} {'timeout':>8} {'len_mis':>8}")
    for cs in [15, 12, 10, 8]:
        if cs == 15:
            # 기존 측정 (468s, 2 timeout, 1 length mismatch)
            print(f"{15:<5} {'468.0':>10} {'616':>7} {'2':>8} {'1':>8}  (이전 측정)")
        else:
            r = results_1pass[cs]
            print(f"{cs:<5} {r['elapsed']:>10.1f} {r['body_lines']:>7} {r['timeouts']:>8} {r['length_mismatch']:>8}")

    print(f"\n2-pass chunk_size={best_cs} catch:")
    print(f"  time: {results_2pass['elapsed']:.1f}s (재분할 cs=15 기준 361.3s)")
    print(f"  1단계 정합: {results_2pass['match_exact']} / {results_2pass['total_chunks']} "
          f"(재분할 cs=15 기준 12/21=57%)")
    print(f"  합침: {results_2pass['match_less']}, 극단: {results_2pass['match_extreme']}")
    print(f"  timeouts: {results_2pass['timeouts']}")

    # save
    (OUT_DIR / "sweep_analysis.json").write_text(
        json.dumps({"1pass": results_1pass, "2pass": results_2pass},
                   ensure_ascii=False, indent=1), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
