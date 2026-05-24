"""omlx 동시 요청 처리 시간 실측 (5/24).

같은 짧은 요청을 1/4/8/16/32 동시 보내 처리 시간 측정.
모델: 35b-a3b-oq6-mtp (daily 후보)
목적: 후보 D (segment 단위 LLM 호출) 병렬 이득 배수 catch.
"""
import os
import sys
import time
import asyncio
from typing import List

# .env 로드
for line in open("/Users/gesicht/GuruNote/.env").read().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# 검증 모델 (daily 후보)
TEST_MODEL = "Qwen3.6-35B-A3B-oQ6-mtp"
BASE_URL = os.environ["OPENAI_BASE_URL"]
API_KEY = os.environ["OPENAI_API_KEY"]

# 테스트 요청 (실제 segment 번역 유사 — 짧은 영어 → 한국어)
TEST_PROMPT = (
    "다음 영어 발화 1건을 자연스러운 한국어로 번역하라. "
    "본문 한국어만 출력.\n\n"
    "Input: 'This is a test sentence for measuring concurrency.'\n\n"
    "Output:"
)


def make_payload():
    return {
        "model": TEST_MODEL,
        "messages": [{"role": "user", "content": TEST_PROMPT}],
        "max_tokens": 64,
        "temperature": 0.2,
        "extra_body": {"thinking_budget": 0},
    }


async def one_call(client) -> float:
    """단일 호출 — 시간 반환."""
    t0 = time.time()
    payload = make_payload()
    # extra_body 는 openai SDK async 도 catch
    body = {k: v for k, v in payload.items() if k != "extra_body"}
    body["thinking_budget"] = payload["extra_body"]["thinking_budget"]
    try:
        await client.chat.completions.create(
            model=body["model"],
            messages=body["messages"],
            max_tokens=body["max_tokens"],
            temperature=body["temperature"],
            extra_body={"thinking_budget": 0},
            timeout=90,
        )
    except Exception as exc:
        return -1.0
    return time.time() - t0


async def measure_concurrency(n: int, warmup: bool = False) -> dict:
    """N개 동시 요청 처리 시간."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
    if warmup:
        # 모델 로드 warmup (cold start 차단)
        await one_call(client)
    t0 = time.time()
    times = await asyncio.gather(*[one_call(client) for _ in range(n)])
    total = time.time() - t0
    await client.close()
    valid = [t for t in times if t > 0]
    return {
        "n": n,
        "total_wall_clock": total,
        "per_request_avg": sum(valid) / len(valid) if valid else 0,
        "per_request_min": min(valid) if valid else 0,
        "per_request_max": max(valid) if valid else 0,
        "valid_count": len(valid),
    }


async def main() -> None:
    print(f"omlx 동시성 실측 — 모델: {TEST_MODEL}")
    print(f"endpoint: {BASE_URL}")
    print("=" * 70)

    # warmup (모델 cold start 영향 차단)
    print("\n[warmup] 모델 cold start 차단 호출...")
    await measure_concurrency(1, warmup=True)
    print("warmup done.")
    print()

    results = []
    for n in [1, 4, 8, 16, 32]:
        print(f"[{n} 동시 요청] 시작…")
        r = await measure_concurrency(n)
        results.append(r)
        print(f"  total wall-clock: {r['total_wall_clock']:.2f}s")
        print(f"  per-request: avg={r['per_request_avg']:.2f}s, "
              f"min={r['per_request_min']:.2f}s, max={r['per_request_max']:.2f}s")
        print(f"  valid: {r['valid_count']}/{n}")
        print()
        await asyncio.sleep(2)   # 서버 정리

    # speedup 비교 (n=1 vs n=N)
    print("=" * 70)
    print("Speedup 분석 (n=1 wall-clock 기준):")
    n1_wall = results[0]["total_wall_clock"]
    print(f"  n=1 wall-clock: {n1_wall:.2f}s")
    print()
    print(f"{'n':>4} {'wall(s)':>10} {'순차환산(s)':>12} {'speedup':>10} {'이론대비':>10}")
    print(f"{'-':>4} {'-------':>10} {'-----------':>12} {'-------':>10} {'-------':>10}")
    for r in results:
        n = r["n"]
        sequential = n1_wall * n
        speedup = sequential / r["total_wall_clock"] if r["total_wall_clock"] > 0 else 0
        theoretical = speedup / n * 100
        print(f"{n:>4} {r['total_wall_clock']:>10.2f} {sequential:>12.2f} "
              f"{speedup:>9.2f}x {theoretical:>9.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
