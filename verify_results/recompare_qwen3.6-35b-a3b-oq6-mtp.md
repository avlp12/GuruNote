=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [10:52:53] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-35B-A3B-oQ6-mtp)
  [10:52:53] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [10:52:53]    📚 entity cache bootstrap — 5건 사전 추출
  [10:52:53]    ↳ 청크 1/20 번역 중…
  [10:57:32]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [10:57:33]    ↳ 청크 2/20 번역 중…
  [10:57:38]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:57:39]    ↳ 청크 3/20 번역 중…
  [10:57:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:57:46]    ↳ 청크 4/20 번역 중…
  [10:57:54]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:57:55]    ↳ 청크 5/20 번역 중…
  [10:58:02]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:58:03]    ↳ 청크 6/20 번역 중…
  [10:58:11]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:58:12]    ↳ 청크 7/20 번역 중…
  [10:58:19]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:58:20]    ↳ 청크 8/20 번역 중…
  [10:58:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:58:29]    ↳ 청크 9/20 번역 중…
  [10:58:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:58:37]    ↳ 청크 10/20 번역 중…
  [10:58:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:58:44]    ↳ 청크 11/20 번역 중…
  [10:58:51]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:58:52]    ↳ 청크 12/20 번역 중…
  [10:58:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:59:00]    ↳ 청크 13/20 번역 중…
  [10:59:07]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:59:08]    ↳ 청크 14/20 번역 중…
  [10:59:14]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:59:15]    ↳ 청크 15/20 번역 중…
  [10:59:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:59:24]    ↳ 청크 16/20 번역 중…
  [10:59:31]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:59:32]    ↳ 청크 17/20 번역 중…
  [10:59:39]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:59:40]    ↳ 청크 18/20 번역 중…
  [10:59:47]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:59:48]    ↳ 청크 19/20 번역 중…
  [10:59:55]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:59:56]    ↳ 청크 20/20 번역 중…
  [10:59:58]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [10:59:58] ✅ 번역 완료
  [10:59:58]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [11:00:00]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 3건, Sub-C fallback 0건
  [11:01:45]    🔧 entity canonicalize 적용 (5건 cache, 줄 수 574 → 574)

=== 결과 (533.7초 = 8.9분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_110145.md

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
    '슈나이더 일렉트릭': 5회
    '스키에더 일렉트릭': 0회
    '슈나이더 일렉트리': 0회
    '슈나이더일렉트릭': 0회
  Test 9: 화자명 hallucinate 부재
    '티파즈 샤르마': 0회 ✅
    '판카즈 잔젠': 0회 ✅
    '티파니 샤르마': 0회 ✅
    '판카즈 티파니': 0회 ✅
  Test 10: speaker prefix 영역 (가장 자주 catch)
    '판카즈 샤르마': 190회
    '티파니 잔젠': 60회
    '[⚠ timeout]

[00': 8회
    '엄청난 전력이 필요합니다.

[00': 1회
    '물론 많은 기회와 과제를 동시에 안겨줍니다.

[01': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 20건
    길이 미스매치 retry: 0건
    fallback path 진입: 0건
    Index Mapping 정합: 19건

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

🎉 real video verify 종료 (8.9분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_110145.md
