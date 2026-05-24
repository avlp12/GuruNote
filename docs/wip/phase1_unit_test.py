"""Phase 1 unit test (5/12 본질 fix — strict filter + original 우선 + bracket 형식 통일)."""
import sys
sys.path.insert(0, '/Users/gesicht/GuruNote')

from gurunote.llm import (
    _extract_timestamps, _ts_to_seconds, _build_retry_block,
    _merge_retry_into_chunk, _MAX_TS_RETRY,
)
from gurunote.types import Segment, _format_ts

# Test 1: _extract_timestamps
print("=== Test 1: _extract_timestamps ===")
text1 = "[00:10] A: 안녕\n[00:13] B: 오늘\n[01:23:45] C: 한 시간\n비-[ts] line\n[02:30] A: 다음"
ts1 = _extract_timestamps(text1)
assert ts1 == {"[00:10]", "[00:13]", "[01:23:45]", "[02:30]"}
print("  ✅ PASS")

# Test 2: _ts_to_seconds
print("\n=== Test 2: _ts_to_seconds ===")
assert _ts_to_seconds("[00:10]") == 10
assert _ts_to_seconds("[01:30]") == 90
assert _ts_to_seconds("[01:23:45]") == 1*3600 + 23*60 + 45
assert _ts_to_seconds("invalid") == 0.0
print("  ✅ PASS")

# Test 3: _build_retry_block
print("\n=== Test 3: _build_retry_block ===")
missing_segs = [
    Segment(speaker="A", start=782.0, end=785.0, text="missing 1"),
    Segment(speaker="B", start=790.0, end=795.0, text="missing 2"),
]
block = _build_retry_block(missing_segs)
assert "누락 보충" in block
assert "[13:02] Speaker A: missing 1" in block
assert "[13:10] Speaker B: missing 2" in block
print("  ✅ PASS")

# Test 4: 정상 merge (missing_ts 정합 영역만 insert)
print("\n=== Test 4: _merge_retry_into_chunk — 정상 ===")
original = "[00:10] A: hello\n[00:30] B: world\n[01:00] A: bye"
retry = "[00:20] B: missing middle"
merged = _merge_retry_into_chunk(original, retry, missing_ts={"[00:20]"})
expected_order = ["[00:10]", "[00:20]", "[00:30]", "[01:00]"]
prev_idx = -1
for ts in expected_order:
    idx = merged.index(ts)
    assert idx > prev_idx, f"{ts} 순서 오류"
    prev_idx = idx
print(f"  merged: {merged!r}")
print("  ✅ PASS")

# Test 5: HH:MM:SS sort
print("\n=== Test 5: HH:MM:SS sort ===")
original2 = "[00:30] A: short\n[01:30:00] A: hour"
retry2 = "[00:50] B: between\n[02:00:00] C: late"
merged2 = _merge_retry_into_chunk(original2, retry2, missing_ts={"[00:50]", "[02:00:00]"})
order = ["[00:30]", "[00:50]", "[01:30:00]", "[02:00:00]"]
prev_idx = -1
for ts in order:
    idx = merged2.index(ts)
    assert idx > prev_idx
    prev_idx = idx
print("  ✅ PASS")

# Test 6: marker insertion
print("\n=== Test 6: marker insertion ===")
original3 = "[00:10] A: 안녕\n[00:30] B: 마지막"
marker_text = "[00:20] ⚠ 번역 누락\n[00:25] ⚠ 번역 누락"
merged3 = _merge_retry_into_chunk(original3, marker_text, missing_ts={"[00:20]", "[00:25]"})
ord1 = merged3.index("[00:10]")
ord2 = merged3.index("[00:20]")
ord3 = merged3.index("[00:25]")
ord4 = merged3.index("[00:30]")
assert ord1 < ord2 < ord3 < ord4
print("  ✅ PASS")

# Test 7: _MAX_TS_RETRY
print("\n=== Test 7: _MAX_TS_RETRY ===")
assert _MAX_TS_RETRY == 3
print("  ✅ PASS")

# === 신규 Tests — strict filter ===

# Test 8: retry 가 missing_ts 외 영역 echo → drop
print("\n=== Test 8: missing_ts 외 영역 drop ===")
orig8 = "[00:10] A: 원본 1\n[00:30] B: 원본 2"
# Retry tries to echo [00:10] (in orig) + [00:50] (not in missing) + [00:20] (in missing — accepted)
retry8 = "[00:10] A: WRONG REWRITE\n[00:20] A: 합법 누락 보충\n[00:50] A: 인접 영역 echo (drop)"
log_calls = []
def fake_log(msg):
    log_calls.append(msg)

merged8 = _merge_retry_into_chunk(orig8, retry8, missing_ts={"[00:20]"}, log=fake_log)
print(f"  merged: {merged8!r}")
print(f"  log calls: {log_calls}")

# Original [00:10] 보호 (WRONG REWRITE 부재)
assert "원본 1" in merged8
assert "WRONG REWRITE" not in merged8
# [00:20] 정합 영역만 insert
assert "[00:20] A: 합법 누락 보충" in merged8
# [00:50] drop 정합
assert "[00:50]" not in merged8
assert "인접 영역 echo" not in merged8
# WARNING log 영역 정합
assert len(log_calls) == 1
assert "drop" in log_calls[0]
assert "[00:10]" in log_calls[0] or "[00:50]" in log_calls[0]
print("  ✅ PASS — original 보호 + missing_ts 외 drop + log")

# Test 9: retry 가 original 의 [ts] overwrite 시도 → original 우선
print("\n=== Test 9: original 우선 (overwrite 차단) ===")
orig9 = "[00:10] A: 원본 번역"
# Retry 가 같은 [00:10] 영역에 다른 번역 echo (missing_ts 에도 포함 시도)
retry9 = "[00:10] A: OVERWRITTEN BY RETRY"
log_calls9 = []
merged9 = _merge_retry_into_chunk(
    orig9, retry9,
    missing_ts={"[00:10]"},  # 가설적 missing 영역 시도
    log=lambda m: log_calls9.append(m)
)
# Original 보호 (overwrite 부재)
assert "원본 번역" in merged9
assert "OVERWRITTEN BY RETRY" not in merged9
assert len(log_calls9) == 1
assert "[00:10]" in log_calls9[0]
print(f"  merged: {merged9!r}")
print("  ✅ PASS — original overwrite 차단")

# Test 10: translate_transcript expected_ts 영역의 bracket 형식 통일
print("\n=== Test 10: expected_ts bracket 형식 (5/12 본질 fix) ===")
# Mock chunk segments
chunk = [
    Segment(speaker="A", start=10.0, end=15.0, text="hello"),
    Segment(speaker="B", start=130.0, end=135.0, text="world"),  # [02:10]
]
# translate_transcript L716 의 expected_ts 영역 시뮬레이션
expected_ts = {f"[{_format_ts(s.start)}]" for s in chunk}
assert expected_ts == {"[00:10]", "[02:10]"}, f"bracket 형식 부정합: {expected_ts}"

# _extract_timestamps 결과와 정합 catch
sample_response = "[00:10] A: hello world\n[02:10] B: foo bar"
actual_ts = _extract_timestamps(sample_response)
assert actual_ts == expected_ts, f"expected_ts({expected_ts}) != actual_ts({actual_ts})"

# 정상 응답: missing 부재
missing_normal = expected_ts - actual_ts
assert missing_normal == set(), f"정상 응답 시 missing 부재 부정합: {missing_normal}"

# Incomplete 응답: missing 검출
incomplete = "[00:10] A: hello world"  # [02:10] 누락
actual_incomplete = _extract_timestamps(incomplete)
missing = expected_ts - actual_incomplete
assert missing == {"[02:10]"}, f"missing 영역 부정합: {missing}"

# L723 의 missing_segments 영역 시뮬레이션
missing_segments = [s for s in chunk if f"[{_format_ts(s.start)}]" in missing]
assert len(missing_segments) == 1
assert missing_segments[0].start == 130.0  # [02:10]
print("  ✅ PASS — bracket 형식 통일 + missing 검출 정합 + missing_segments 영역")

print(f"\n🎉 모든 unit test 통과 (10/10)")
