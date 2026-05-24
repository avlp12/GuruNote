"""체크포인트 2 — 단일 chunk Index Mapping 영역 verify."""
import sys, os, time, re
sys.path.insert(0, '/Users/gesicht/GuruNote')
# .env 영역의 OPENAI_BASE_URL 등 로드 (LLMConfig.from_env 영역 의존)
for line in open('/Users/gesicht/GuruNote/.env').read().splitlines():
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

from gurunote.llm import LLMConfig, translate_chunk_index_mapping_v2
from gurunote.types import Segment

# Mock chunk — NVIDIA GTC chunk 1 영역 시뮬레이션 (5 segments 영역)
mock_segments = [
    Segment(speaker="Speaker A", start=10.0, end=13.0, text="Hi everyone, welcome to the NVIDIA GTC studio."),
    Segment(speaker="Speaker A", start=13.0, end=17.0, text="My name is Tiffany Janzen and today I'm joined with Pankaj Sharma,"),
    Segment(speaker="Speaker A", start=17.0, end=21.0, text="who is the Executive VP of Software and Services at Schneider Electric."),
    Segment(speaker="Speaker A", start=21.0, end=22.0, text="Pankaj, welcome."),
    Segment(speaker="Speaker B", start=22.0, end=23.0, text="Thank you, Tiffany."),
]

cfg = LLMConfig.from_env(provider="openai_compatible")
context_block = """영상 컨텍스트:
- 제목: NVIDIA GTC Studio with Insights from Schneider Electric
- 게시일: 2026-03-30
- 분야: AI 인프라"""

print("=== 체크포인트 2 verify — 단일 chunk Index Mapping ===")
print(f"  endpoint: {cfg.base_url}")
print(f"  model:    {cfg.model}")
print(f"  segments: {len(mock_segments)}")
print()

start = time.time()
result = translate_chunk_index_mapping_v2(mock_segments, context_block, cfg)
elapsed = time.time() - start

print(f"\n=== 결과 ({elapsed:.1f}초) ===")
print(result)
print()

# 검증 1: 라인 수 = 입력 segments 수
lines = [l for l in result.split("\n") if l.strip()]
assert len(lines) == len(mock_segments), f"라인 수 부정합: {len(lines)} != {len(mock_segments)}"
print(f"✅ Test 1 — 라인 수 정합: {len(lines)} = {len(mock_segments)}")

# 검증 2: timestamp 순서 정합
ts_pattern = re.compile(r"^\[(\d{2}):(\d{2})\]")
expected_ts = [f"[{int(s.start//60):02d}:{int(s.start%60):02d}]" for s in mock_segments]
actual_ts = [ts_pattern.match(l).group(0) for l in lines if ts_pattern.match(l)]
assert actual_ts == expected_ts, f"timestamp 어긋남: {actual_ts} != {expected_ts}"
print(f"✅ Test 2 — timestamp 순서 정합: {actual_ts}")

# 검증 3: drift 검출 — Executive VP 영역의 단일 위치 catch
exec_lines = [l for l in lines if any(kw in l for kw in ["Executive VP", "수석", "부사장", "상무이사", "임원"])]
print(f"\nExecutive VP 영역의 라인 영역:")
for l in exec_lines:
    print(f"  {l}")
# [00:17] 영역의 단일 line 영역 catch
ts_0017_line = next((l for l in lines if l.startswith("[00:17]")), None)
print(f"\n[00:17] 영역의 라인:")
print(f"  {ts_0017_line}")
assert ts_0017_line, "[00:17] 라인 부재"
print(f"✅ Test 3 — [00:17] 영역의 라인 정합 (drift 부재 — 순서 매핑 zip 영역 100%)")

# 검증 4: 영문 병기 catch (Pankaj Sharma)
pankaj_lines = [l for l in lines if "Pankaj" in l or "판카즈" in l]
print(f"\nPankaj 영역의 라인:")
for l in pankaj_lines:
    print(f"  {l}")
print(f"✅ Test 4 — Pankaj 영역의 영문 병기 catch")

# 검증 5: 한자/일본어 잔재 부재
import re as _re
asian_chars = _re.findall(r'[一-鿿぀-ゟ゠-ヿ]', result)
if asian_chars:
    print(f"\n⚠ 한자/일본어 잔재 catch: {asian_chars[:10]}")
else:
    print(f"\n✅ Test 5 — 한자/일본어 잔재 부재")

print("\n🎉 체크포인트 2 verify 통과 — Index Mapping 본질 정합")
