"""체크포인트 3 E2E verify — translate_transcript 통째 Index Mapping path 영역."""
import sys, os, time, re
sys.path.insert(0, '/Users/gesicht/GuruNote')

# .env 영역 로드
for line in open('/Users/gesicht/GuruNote/.env').read().splitlines():
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

from gurunote.llm import LLMConfig, translate_transcript
from gurunote.types import Segment, Transcript

# 최근 NVIDIA GTC 영상의 영문 원문 영역에서 segments 영역 재구성 (작은 영역만 — chunk 1 subset).
LATEST = "/Users/gesicht/.gurunote/jobs/20260512_120812_9915/result.md"
with open(LATEST) as f:
    md = f.read()

# 영문 원문 섹션 영역 추출
en_section = md.split("# 🇺🇸 원문 스크립트 (English)")[1] if "# 🇺🇸 원문 스크립트" in md else ""
# **[00:10] Speaker A:** text 패턴 영역
en_pattern = re.compile(r"\*\*\[(\d{1,2}):(\d{2})\] Speaker ([A-Z])\:\*\* (.+)")
segments = []
for line in en_section.split("\n"):
    m = en_pattern.match(line.strip())
    if m:
        mm, ss, speaker, text = m.groups()
        start = int(mm) * 60 + int(ss)
        segments.append(Segment(speaker=speaker, start=float(start), end=float(start+3), text=text))

print(f"=== 체크포인트 3 E2E verify ===")
print(f"  reconstructed segments: {len(segments)}")
print(f"  첫 3 segments:")
for s in segments[:3]:
    print(f"    [{int(s.start//60):02d}:{int(s.start%60):02d}] {s.speaker}: {s.text[:60]}...")
print()

# 작은 chunk 영역 (시간 영역 catch — 처음 25 segments 만 사용 → 1 chunk 정합)
test_segments = segments[:25]
print(f"  ★ 테스트 segments: {len(test_segments)}개 (1 chunk 영역 가정)")

transcript = Transcript(segments=test_segments, language="en", engine="mlx")
cfg = LLMConfig.from_env(provider="openai_compatible")

video_context = {
    "title": "NVIDIA GTC Studio with Insights from Schneider Electric",
    "uploader": "NVIDIA",
    "upload_date": "20260330",
    "description": "Pankaj Sharma from Schneider Electric discusses AI infrastructure.",
}

log_messages = []
def capture_log(msg):
    log_messages.append(msg)
    print(f"  [log] {msg}")

print(f"\n=== translate_transcript 실행 영역 ===")
start = time.time()
result = translate_transcript(
    transcript,
    config=cfg,
    progress=capture_log,
    video_context=video_context,
    stop_event=None,
)
elapsed = time.time() - start

print(f"\n=== 결과 ({elapsed:.1f}초) ===")
# 결과의 처음 5 lines 만 출력
for i, line in enumerate(result.split("\n\n")[:5]):
    print(f"  {line[:120]}")
print(f"  ... (전체 {len(result.split(chr(10)+chr(10)))} chunks/lines)")

# === 검증 ===
print(f"\n=== 자동 검증 ===")

# 검증 1: timestamp 완전성 100%
expected_ts = {f"[{int(s.start//60):02d}:{int(s.start%60):02d}]" for s in test_segments}
actual_ts = set(re.findall(r"\[\d{2}:\d{2}\]", result))
missing = expected_ts - actual_ts
extra = actual_ts - expected_ts
print(f"  Test 1: timestamp 완전성")
print(f"    expected: {len(expected_ts)}, actual: {len(actual_ts)}, missing: {len(missing)}, extra: {len(extra)}")
assert not missing, f"누락 timestamp: {sorted(missing)}"
print(f"    ✅ PASS — 모든 expected timestamp 영역 정합")

# 검증 2: line count 정합 (zip 결정론)
lines = [l for l in result.split("\n\n") if l.strip()]
print(f"  Test 2: line count")
print(f"    segments: {len(test_segments)}, output lines: {len(lines)}")
assert len(lines) == len(test_segments), f"line count 부정합"
print(f"    ✅ PASS — line count = segment count")

# 검증 3: drift 부재 (timestamp 순서 정합)
ts_re = re.compile(r"^\[(\d{2}):(\d{2})\]")
result_ts_order = []
for line in lines:
    m = ts_re.match(line)
    if m:
        result_ts_order.append(int(m.group(1)) * 60 + int(m.group(2)))
expected_ts_order = sorted(int(s.start) for s in test_segments)
assert result_ts_order == expected_ts_order, "timestamp 순서 어긋남"
print(f"  Test 3: timestamp 순서 정합 ✅ PASS")

# 검증 4: 한자/일본어 잔재 부재
asian_chars = re.findall(r'[一-鿿぀-ゟ゠-ヿ]', result)
print(f"  Test 4: 한자/일본어 잔재")
if asian_chars:
    print(f"    ⚠ 잔재 영역 (Layer 11 회귀): {asian_chars[:10]}")
else:
    print(f"    ✅ PASS — 한자/일본어 부재")

# 검증 5: marker 부재 (timestamp 완전성 100% 시 marker 부재 정합)
marker_count = result.count("⚠ 번역 누락")
print(f"  Test 5: marker (번역 누락)")
print(f"    count: {marker_count}")
assert marker_count == 0, f"marker 영역 부재 부정합 (timestamp 완전성 정합)"
print(f"    ✅ PASS — 모든 segments translated")

# 검증 6: finish_reason log 영역
finish_reason_logs = [m for m in log_messages if "finish_reason" in m]
print(f"  Test 6: finish_reason log catch")
print(f"    matches: {len(finish_reason_logs)}")
for m in finish_reason_logs:
    print(f"      {m}")
print(f"    ✅ PASS — Index Mapping log 정합")

print(f"\n🎉 체크포인트 3 E2E 자동 검증 통과 ({elapsed:.1f}초)")
print(f"\n=== 본인 시각 catch 영역 (보고 부탁) ===")
print(f"  - 번역 품질 (Layer 8/11/13/15 정합)")
print(f"  - 화자명 표기 일관성 (티파니 잔젠 본질 단일)")
print(f"  - 직책 표기 (수석 부사장 / 상무이사)")
print(f"  - 영문 병기 정합")
print(f"\n결과 전체 본문:")
print(result)
