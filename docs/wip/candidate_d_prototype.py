"""후보 D prototype — segment 별 1:1 번역 + context K + 병렬 (5/24).

표본: chunks 7, 11, 12 (총 45 segments)
모델: Qwen3.6-35B-A3B-oQ6-mtp (약한 모델 대표)
세팅:
  - context K = 2 / 3 (앞·뒤 각 K개 segment 추가)
  - 순차 / 병렬 (asyncio.gather, omlx 32 concurrent)
측정:
  - 정렬: 1:1 매핑 SHIFT 0 실증 (출력 1줄 catch)
  - 품질: 빈 출력 / 반복 / hallucination
  - 비용: wall-clock + per-segment 시간 + 병렬 speedup

원본 segments: verify_results/community1_3speakers_segments.json (3-speaker community-1 verify)
2-pass 비교 본문: verify_results/community1_3speakers_body.md
"""
from __future__ import annotations

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

# .env 로드
for line in open("/Users/gesicht/GuruNote/.env").read().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

TEST_MODEL = "Qwen3.6-35B-A3B-oQ6-mtp"
BASE_URL = os.environ["OPENAI_BASE_URL"]
API_KEY = os.environ["OPENAI_API_KEY"]

SEG_JSON = Path("/Users/gesicht/GuruNote/verify_results/community1_3speakers_segments.json")
OUT_DIR = Path("/Users/gesicht/GuruNote/verify_results")

CHUNK_SIZE = 15
TARGET_CHUNKS = [7, 11, 12]   # 표본 — 5/23 verify에서 정렬 catch 한 chunk 후보

# 알려진 인물 (3-speaker 영상 화자 — 본 verify에서 식별 catch)
SPEAKER_MAP = {
    "A": "젠슨 황(Jensen Huang)",
    "B": "마이클 델(Michael Dell)",
    "C": "에드 러들로(Ed Ludlow)",
}


def load_target_segments() -> List[Dict[str, Any]]:
    """chunk 7/11/12 segments 추출 + chunk index 부착."""
    all_segs = json.load(open(SEG_JSON))
    out = []
    for ci in TARGET_CHUNKS:
        s = (ci - 1) * CHUNK_SIZE
        e = s + CHUNK_SIZE
        for i, seg in enumerate(all_segs[s:e]):
            seg = dict(seg)
            seg["chunk"] = ci
            seg["chunk_pos"] = i
            seg["global_idx"] = s + i
            out.append(seg)
    return out


def build_prompt(target: Dict[str, Any], context_before: List[Dict[str, Any]],
                  context_after: List[Dict[str, Any]]) -> str:
    """D segment prompt — 1줄 번역 + context.

    target: 번역 대상 1건
    context_before / context_after: 앞·뒤 K개 (영문 원본, 화자만 포함)
    """
    def fmt_ctx(seg):
        sp = seg.get("speaker") or "-"
        return f"  [{sp}] {seg['text']}"

    speaker = target.get("speaker") or "-"
    target_label = SPEAKER_MAP.get(speaker, f"화자 {speaker}")

    parts = [
        "다음은 영어 인터뷰 발화 1건을 한국어로 번역하는 작업이다.",
        "",
        "규칙:",
        "1. 입력은 [TARGET] 1건이다. 본 1건만 번역하라.",
        "2. [CONTEXT-BEFORE] / [CONTEXT-AFTER] 는 흐름 catch 용 참고이며, 번역 대상 부재.",
        "3. 출력은 한국어 문장 1줄. 화자 라벨 출력 부재. 본문 부재인 경우 빈 줄.",
        "4. 한국어 출력에 한자 / 일본어 / 중국어 문자 부재. 외래어 표기법 표준.",
        "5. 본문 내용 추가 / 누락 / 변경 부재. 영어 원본 의미 그대로.",
        "",
    ]

    if context_before:
        parts.append("[CONTEXT-BEFORE]")
        for seg in context_before:
            parts.append(fmt_ctx(seg))
        parts.append("")

    parts.append("[TARGET]")
    parts.append(f"  화자: {target_label}")
    parts.append(f"  영어: {target['text']}")
    parts.append("")

    if context_after:
        parts.append("[CONTEXT-AFTER]")
        for seg in context_after:
            parts.append(fmt_ctx(seg))
        parts.append("")

    parts.append("위 [TARGET] 1건만 한국어로 번역하라. 한국어 본문 1줄만 출력:")
    return "\n".join(parts)


def get_context(all_segs: List[Dict[str, Any]], idx: int, k: int) -> tuple:
    """전체 segment 리스트 기준 idx의 앞·뒤 K개 catch (chunk 경계 무시)."""
    before = all_segs[max(0, idx - k):idx]
    after = all_segs[idx + 1:idx + 1 + k]
    return before, after


async def translate_segment(client, target: Dict[str, Any],
                              ctx_before: List[Dict[str, Any]],
                              ctx_after: List[Dict[str, Any]]) -> Dict[str, Any]:
    """단일 segment 번역 — 결과 dict 반환."""
    prompt = build_prompt(target, ctx_before, ctx_after)
    t0 = time.time()
    try:
        resp = await client.chat.completions.create(
            model=TEST_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.2,
            extra_body={"thinking_budget": 0},
            timeout=90,
        )
        text = resp.choices[0].message.content or ""
        text = text.strip()
        # 화자 prefix 잔재 strip (A:, B:, C: 등)
        for sp in ["A:", "B:", "C:", "화자 A:", "화자 B:", "화자 C:"]:
            if text.startswith(sp):
                text = text[len(sp):].strip()
        return {
            "global_idx": target["global_idx"],
            "chunk": target["chunk"],
            "chunk_pos": target["chunk_pos"],
            "speaker": target.get("speaker"),
            "start": target["start"],
            "end": target["end"],
            "original": target["text"],
            "translated": text,
            "elapsed": time.time() - t0,
            "error": None,
        }
    except Exception as exc:
        return {
            "global_idx": target["global_idx"],
            "chunk": target["chunk"],
            "chunk_pos": target["chunk_pos"],
            "speaker": target.get("speaker"),
            "start": target["start"],
            "end": target["end"],
            "original": target["text"],
            "translated": "",
            "elapsed": time.time() - t0,
            "error": str(exc),
        }


async def run_one(all_segs: List[Dict[str, Any]], targets: List[Dict[str, Any]],
                   k: int, parallel: bool, concurrency: int = 32) -> Dict[str, Any]:
    """전체 표본 처리 — 한 모드 (k, parallel)."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

    # context K = 전체 segment에서 catch (chunk 경계 부재)
    tasks = []
    for tgt in targets:
        before, after = get_context(all_segs, tgt["global_idx"], k)
        tasks.append((tgt, before, after))

    t0 = time.time()
    results = []
    if parallel:
        sem = asyncio.Semaphore(concurrency)
        async def bounded(tgt, b, a):
            async with sem:
                return await translate_segment(client, tgt, b, a)
        results = await asyncio.gather(*[bounded(t, b, a) for (t, b, a) in tasks])
    else:
        for tgt, b, a in tasks:
            r = await translate_segment(client, tgt, b, a)
            results.append(r)
    total = time.time() - t0
    await client.close()

    return {
        "mode": f"K={k}, {'parallel' if parallel else 'sequential'}",
        "k": k,
        "parallel": parallel,
        "total_wall_clock": total,
        "per_segment_avg": sum(r["elapsed"] for r in results) / len(results),
        "per_segment_min": min(r["elapsed"] for r in results),
        "per_segment_max": max(r["elapsed"] for r in results),
        "empty_count": sum(1 for r in results if not r["translated"]),
        "error_count": sum(1 for r in results if r["error"]),
        "results": results,
    }


def render_md(run: Dict[str, Any]) -> str:
    """결과 본문 markdown — 2-pass 결과와 비교용."""
    lines = [f"# D prototype — {run['mode']}", ""]
    cur_chunk = None
    for r in run["results"]:
        if r["chunk"] != cur_chunk:
            lines.append(f"\n## chunk #{r['chunk']}\n")
            cur_chunk = r["chunk"]
        sp = SPEAKER_MAP.get(r["speaker"] or "", r["speaker"] or "-")
        t = r["translated"] or "[빈]"
        lines.append(f"[{r['start']:.1f}-{r['end']:.1f}] {sp}: {t}")
    return "\n".join(lines)


async def main() -> None:
    print("=" * 70)
    print(f"D prototype — chunks {TARGET_CHUNKS} (45 segments)")
    print(f"모델: {TEST_MODEL}")
    print("=" * 70)

    all_segs_raw = json.load(open(SEG_JSON))
    # global_idx 부착
    for i, s in enumerate(all_segs_raw):
        s["global_idx"] = i
        s["chunk"] = (i // CHUNK_SIZE) + 1
        s["chunk_pos"] = i % CHUNK_SIZE
    targets = load_target_segments()
    print(f"표본 segments: {len(targets)}")
    print()

    runs = []
    for k in [2, 3]:
        for parallel in [False, True]:
            mode = f"K={k}, {'parallel' if parallel else 'sequential'}"
            print(f"[run] {mode}…")
            r = await run_one(all_segs_raw, targets, k=k, parallel=parallel)
            print(f"  total: {r['total_wall_clock']:.2f}s")
            print(f"  per-segment: avg={r['per_segment_avg']:.2f}s, "
                  f"min={r['per_segment_min']:.2f}s, max={r['per_segment_max']:.2f}s")
            print(f"  empty: {r['empty_count']} / errors: {r['error_count']}")
            runs.append(r)

            # 본문 저장
            tag = f"k{k}_{'par' if parallel else 'seq'}"
            (OUT_DIR / f"candidate_d_{tag}.md").write_text(render_md(r), encoding="utf-8")
            (OUT_DIR / f"candidate_d_{tag}.json").write_text(
                json.dumps(r["results"], ensure_ascii=False, indent=1), encoding="utf-8"
            )
            print(f"  saved: candidate_d_{tag}.md / .json")
            print()
            await asyncio.sleep(2)

    # 정리
    print("=" * 70)
    print("정리 — 비용 + 품질")
    print(f"{'mode':<22} {'wall(s)':>10} {'avg/seg':>10} {'empty':>7} {'err':>5}")
    print(f"{'-':<22} {'-':>10} {'-':>10} {'-':>7} {'-':>5}")
    for r in runs:
        print(f"{r['mode']:<22} {r['total_wall_clock']:>10.2f} "
              f"{r['per_segment_avg']:>10.2f} {r['empty_count']:>7} {r['error_count']:>5}")

    # 병렬 speedup
    print()
    seq_k2 = next(r for r in runs if r["k"] == 2 and not r["parallel"])
    par_k2 = next(r for r in runs if r["k"] == 2 and r["parallel"])
    seq_k3 = next(r for r in runs if r["k"] == 3 and not r["parallel"])
    par_k3 = next(r for r in runs if r["k"] == 3 and r["parallel"])
    print(f"K=2 speedup (seq→par): {seq_k2['total_wall_clock']/par_k2['total_wall_clock']:.2f}x")
    print(f"K=3 speedup (seq→par): {seq_k3['total_wall_clock']/par_k3['total_wall_clock']:.2f}x")

    # 정렬 (1:1 확인)
    print()
    print("정렬 (1:1 catch):")
    for r in runs:
        seg_count = len(r["results"])
        line_count = sum(1 for x in r["results"] if x["translated"])
        empty = r["empty_count"]
        print(f"  {r['mode']:<22} segments={seg_count}, 번역된={line_count}, 빈={empty}")


if __name__ == "__main__":
    asyncio.run(main())
