"""체크포인트 4 real video E2E verify — 288 segments / chunks 분할 + tail drop 빈도 catch.

본 영역: 25-segment verify 의 small-N 한계 catch 영역 외 real-world 영역.
- 288 segments → MAX_SEGMENTS_PER_CHUNK=15 영역 분할 시 ~20 chunks 예상.
- tail drop 패턴이 N 배 잔재 가능성 catch.
- 5/12 누락 사례 ([13:35]~[15:45] window) 영역 회귀 catch.
- 화자명 영역 일관성 (스키에더 vs 슈나이더 영역) 영역 catch.
"""
import sys, os, time, re
sys.path.insert(0, '/Users/gesicht/GuruNote')

for line in open('/Users/gesicht/GuruNote/.env').read().splitlines():
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

from gurunote.llm import LLMConfig, translate_transcript, MAX_SEGMENTS_PER_CHUNK, DEFAULT_CHUNK_CHAR_LIMIT
from gurunote.types import Segment, Transcript

LATEST = "/Users/gesicht/.gurunote/jobs/20260512_120812_9915/result.md"
with open(LATEST) as f:
    md = f.read()

# 영문 원문 섹션 추출
en_section = md.split("# 🇺🇸 원문 스크립트 (English)")[1] if "# 🇺🇸 원문 스크립트" in md else ""
en_pattern = re.compile(r"\*\*\[(\d{1,2}):(\d{2})\] Speaker ([A-Z])\:\*\* (.+)")
segments = []
for line in en_section.split("\n"):
    m = en_pattern.match(line.strip())
    if m:
        mm, ss, speaker, text = m.groups()
        start = int(mm) * 60 + int(ss)
        segments.append(Segment(speaker=speaker, start=float(start), end=float(start+3), text=text))

expected_chunks = (len(segments) + MAX_SEGMENTS_PER_CHUNK - 1) // MAX_SEGMENTS_PER_CHUNK

print(f"=== 체크포인트 4 real video E2E verify ===")
print(f"  reconstructed segments: {len(segments)}")
print(f"  MAX_SEGMENTS_PER_CHUNK: {MAX_SEGMENTS_PER_CHUNK}")
print(f"  DEFAULT_CHUNK_CHAR_LIMIT: {DEFAULT_CHUNK_CHAR_LIMIT}")
print(f"  예상 chunk 수: {expected_chunks}")
print()

transcript = Transcript(segments=segments, language="en", engine="mlx")
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
    print(f"  [{time.strftime('%H:%M:%S')}] {msg}", flush=True)

print(f"=== translate_transcript 실행 (288 segments) ===")
start = time.time()
result = translate_transcript(
    transcript,
    config=cfg,
    progress=capture_log,
    video_context=video_context,
    stop_event=None,
)
elapsed = time.time() - start

# 결과 file 저장 (먼저 — 실패해도 결과 보존).
# 영구 경로 + run-specific 명명으로 verify 마다 덮어쓰기 차단 (5/19 수정).
timestamp = time.strftime("%Y%m%d_%H%M%S")
out_path = f"/Users/gesicht/GuruNote/verify_results/realvideo_body_{timestamp}.md"
with open(out_path, "w") as f:
    f.write(result)

print(f"\n=== 결과 ({elapsed:.1f}초 = {elapsed/60:.1f}분) ===")
print(f"  결과 file: {out_path}")
print()

# === 자동 검증 ===
lines = [l for l in result.split("\n\n") if l.strip()]

# 검증 1: line count = segment count
print(f"=== 자동 검증 ===")
print(f"  Test 1: line count — segments {len(segments)} vs output lines {len(lines)}")
test1_pass = len(lines) == len(segments)
print(f"    {'✅ PASS' if test1_pass else '⚠ MISMATCH'}")

# 검증 2: timestamp 완전성
expected_ts = sorted({(int(s.start//60), int(s.start%60)) for s in segments})
actual_ts_set = set(re.findall(r"\[(\d{2}):(\d{2})\]", result))
actual_ts_int = {(int(m), int(s)) for m, s in actual_ts_set}
missing_ts = set(expected_ts) - actual_ts_int
extra_ts = actual_ts_int - set(expected_ts)
print(f"  Test 2: timestamp 완전성 — expected {len(expected_ts)}, actual {len(actual_ts_int)}, missing {len(missing_ts)}, extra {len(extra_ts)}")
test2_pass = len(missing_ts) == 0
print(f"    {'✅ PASS' if test2_pass else '⚠ missing: ' + str(sorted(missing_ts)[:10])}")

# 검증 3: [번역 누락] marker
marker_count = result.count("[번역 누락]") + result.count("⚠ 번역 누락")
print(f"  Test 3: 번역 누락 marker — {marker_count}건")
test3_pass = marker_count == 0
print(f"    {'✅ PASS' if test3_pass else '⚠ FAIL (' + str(marker_count) + '건)'}")

# 검증 4: 한자/일본어 잔재 부재
asian_chars = re.findall(r'[一-鿿぀-ゟ゠-ヿ]', result)
print(f"  Test 4: 한자/일본어 잔재 — {len(asian_chars)}건")
test4_pass = len(asian_chars) == 0
print(f"    {'✅ PASS' if test4_pass else '⚠ 잔재: ' + str(asian_chars[:10])}")

# 검증 5: chunk 수 catch
chunk_logs = [m for m in log_messages if "청크" in m and "번역 중" in m]
chunk_total_logs = [m for m in log_messages if re.search(r"\d+\s*청크", m) and "시작" in m]
print(f"  Test 5: chunk 수 — '↳ 청크 X/Y 번역 중…' log {len(chunk_logs)}건, 예상 {expected_chunks}")
test5_pass = len(chunk_logs) == expected_chunks
print(f"    {'✅ PASS' if test5_pass else '⚠ MISMATCH'}")

# 검증 6: timestamp drift (zip 결정론)
ts_order = []
for line in lines:
    m = re.match(r"^\[(\d{2}):(\d{2})\]", line.strip())
    if m:
        ts_order.append(int(m.group(1)) * 60 + int(m.group(2)))
expected_ts_order = [int(s.start) for s in segments]
drift_pairs = [(a, b) for a, b in zip(ts_order, expected_ts_order) if a != b]
print(f"  Test 6: timestamp drift (zip 결정론) — drift {len(drift_pairs)}건")
test6_pass = len(drift_pairs) == 0
print(f"    {'✅ PASS' if test6_pass else '⚠ 첫 5: ' + str(drift_pairs[:5])}")

# 검증 7: 5/12 누락 사례 ([13:35]~[15:45] window 2분 10초 영역)
window_start, window_end = 13*60+35, 15*60+45
window_segs = [s for s in segments if window_start <= s.start <= window_end]
window_ts_in_result = sum(
    1 for s in window_segs
    if f"[{int(s.start//60):02d}:{int(s.start%60):02d}]" in result
)
print(f"  Test 7: 5/12 누락 사례 [13:35]~[15:45] — expected {len(window_segs)}, in result {window_ts_in_result}")
test7_pass = window_ts_in_result == len(window_segs)
print(f"    {'✅ PASS' if test7_pass else '⚠ 누락 catch'}")

# 검증 8: 5/13 회귀 사례 — 화자명/회사명 영역 일관성
name_variants = {
    "슈나이더 일렉트릭": result.count("슈나이더 일렉트릭"),
    "스키에더 일렉트릭": result.count("스키에더 일렉트릭"),
    "슈나이더 일렉트리": result.count("슈나이더 일렉트리"),
    "슈나이더일렉트릭": result.count("슈나이더일렉트릭"),
}
print(f"  Test 8: 회사명 영역 일관성")
for k, v in name_variants.items():
    print(f"    '{k}': {v}회")

# 검증 9: 화자명 hallucinate 부재
hallucinate_names = {
    "티파즈 샤르마": result.count("티파즈 샤르마"),
    "판카즈 잔젠": result.count("판카즈 잔젠"),
    "티파니 샤르마": result.count("티파니 샤르마"),
    "판카즈 티파니": result.count("판카즈 티파니"),
}
print(f"  Test 9: 화자명 hallucinate 부재")
test9_pass = True
for k, v in hallucinate_names.items():
    print(f"    '{k}': {v}회 {'⚠' if v > 0 else '✅'}")
    if v > 0:
        test9_pass = False

# 검증 10: speaker prefix 영역 일관성 (각 line 영역 화자 라벨 catch)
speaker_lines = re.findall(r"^\[(\d{2}):(\d{2})\]\s+([^:]+):", result, re.MULTILINE)
speaker_count = {}
for _, _, name in speaker_lines:
    name = name.strip()
    speaker_count[name] = speaker_count.get(name, 0) + 1
print(f"  Test 10: speaker prefix 영역 (가장 자주 catch)")
for k, v in sorted(speaker_count.items(), key=lambda x: -x[1])[:5]:
    print(f"    '{k}': {v}회")

# === 보조 catch — retry / fallback 패턴 ===
print(f"\n=== retry / fallback 패턴 catch ===")
retry_logs = [m for m in log_messages if "retry" in m or "Index Mapping" in m]
print(f"  retry/fallback 영역 log: {len(retry_logs)}건")
mismatch_count = sum(1 for m in retry_logs if "미스매치" in m)
fallback_count = sum(1 for m in retry_logs if "fallback" in m)
match_count = sum(1 for m in retry_logs if "정합" in m)
print(f"    길이 미스매치 retry: {mismatch_count}건")
print(f"    fallback path 진입: {fallback_count}건")
print(f"    Index Mapping 정합: {match_count}건")

# === 종합 ===
print(f"\n=== 자동 검증 종합 ===")
tests = {
    "1. line count": test1_pass,
    "2. timestamp 완전성": test2_pass,
    "3. 번역 누락 marker": test3_pass,
    "4. 한자/일본어 부재": test4_pass,
    "5. chunk 수": test5_pass,
    "6. drift 부재": test6_pass,
    "7. 5/12 누락 회귀 부재": test7_pass,
    "9. 화자명 hallucinate 부재": test9_pass,
}
pass_count = sum(1 for v in tests.values() if v)
total = len(tests)
print(f"  {pass_count}/{total} 통과")
for k, v in tests.items():
    print(f"    {'✅' if v else '⚠'} {k}")

print(f"\n🎉 real video verify 종료 ({elapsed/60:.1f}분, {len(chunk_logs)} chunks 처리)")
print(f"   결과 file: {out_path}")
