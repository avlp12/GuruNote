=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [00:00:59] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [00:00:59] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [00:00:59]    📚 entity cache bootstrap — 5건 사전 추출
  [00:00:59]    ↳ 청크 1/20 번역 중…
  [00:01:05]    ⚠ 길이 미스매치: 12 != 15 (retry 1/3, finish_reason=stop)
  [00:01:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:01:42]    ↳ 청크 2/20 번역 중…
  [00:01:48]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:01:49]    ↳ 청크 3/20 번역 중…
  [00:01:55]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:01:56]    ↳ 청크 4/20 번역 중…
  [00:02:02]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:02:03]    ↳ 청크 5/20 번역 중…
  [00:02:10]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:02:11]    ↳ 청크 6/20 번역 중…
  [00:02:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:02:17]    ↳ 청크 7/20 번역 중…
  [00:02:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:02:23]    ↳ 청크 8/20 번역 중…
  [00:02:29]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:02:30]    ↳ 청크 9/20 번역 중…
  [00:02:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:02:37]    ↳ 청크 10/20 번역 중…
  [00:02:42]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:02:43]    ↳ 청크 11/20 번역 중…
  [00:02:48]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:02:49]    ↳ 청크 12/20 번역 중…
  [00:02:56]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:02:57]    ↳ 청크 13/20 번역 중…
  [00:03:03]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:03:04]    ↳ 청크 14/20 번역 중…
  [00:03:08]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:03:09]    ↳ 청크 15/20 번역 중…
  [00:03:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:03:17]    ↳ 청크 16/20 번역 중…
  [00:03:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:03:25]    ↳ 청크 17/20 번역 중…
  [00:03:32]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:03:33]    ↳ 청크 18/20 번역 중…
  [00:03:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:03:42]    ↳ 청크 19/20 번역 중…
  [00:03:48]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:03:49]    ↳ 청크 20/20 번역 중…
  [00:03:51]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [00:03:51] ✅ 번역 완료
  [00:03:51]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [00:03:51]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 0건, Sub-C fallback 0건
  [00:05:50]    🔧 entity canonicalize 적용 (5건 cache, 줄 수 576 → 576)

=== 결과 (290.6초 = 4.8분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260522_000550.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 288
    ✅ PASS
  Test 2: timestamp 완전성 — expected 271, actual 271, missing 0, extra 0
    ✅ PASS
  Test 3: 번역 누락 marker — 0건
    ✅ PASS
  Test 4: 한자/일본어 잔재 — 0건
    ✅ PASS
  Test 5: chunk 수 — '↳ 청크 X/Y 번역 중…' log 20건, 예상 20
    ✅ PASS
  Test 6: timestamp drift (zip 결정론) — drift 0건
    ✅ PASS
  Test 7: 5/12 누락 사례 [13:35]~[15:45] — expected 32, in result 32
    ✅ PASS
  Test 8: 회사명 영역 일관성
    '슈나이더 일렉트릭': 9회
    '스키에더 일렉트릭': 0회
    '슈나이더 일렉트리': 0회
    '슈나이더일렉트릭': 0회
  Test 9: 화자명 hallucinate 부재
    '티파즈 샤르마': 0회 ✅
    '판카즈 잔젠': 0회 ✅
    '티파니 샤르마': 0회 ✅
    '판카즈 티파니': 0회 ✅
  Test 10: speaker prefix 영역 (가장 자주 catch)
    '판카즈 샤르마': 174회
    '티파니 잔젠': 56회
    'B': 2회
    '티파니 잔젠(Tiffany Janzen)': 1회
    '에너지 사용을 최적화할 수 있습니다.

[02': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 21건
    길이 미스매치 retry: 1건
    fallback path 진입: 0건
    Index Mapping 정합: 20건

=== 자동 검증 종합 ===
  8/8 통과
    ✅ 1. line count
    ✅ 2. timestamp 완전성
    ✅ 3. 번역 누락 marker
    ✅ 4. 한자/일본어 부재
    ✅ 5. chunk 수
    ✅ 6. drift 부재
    ✅ 7. 5/12 누락 회귀 부재
    ✅ 9. 화자명 hallucinate 부재

🎉 real video verify 종료 (4.8분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260522_000550.md
