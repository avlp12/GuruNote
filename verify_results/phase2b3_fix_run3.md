=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [20:50:29] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [20:50:29] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [20:50:29]    📚 entity cache bootstrap — 5건 사전 추출
  [20:50:29]    ↳ 청크 1/20 번역 중…
  [20:50:55]    ⚠ 길이 미스매치: 56 != 15 (retry 1/3, finish_reason=stop)
  [20:51:39]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:51:40]    ↳ 청크 2/20 번역 중…
  [20:51:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:51:46]    ↳ 청크 3/20 번역 중…
  [20:51:52]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:51:53]    ↳ 청크 4/20 번역 중…
  [20:51:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:52:00]    ↳ 청크 5/20 번역 중…
  [20:52:09]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:52:10]    ↳ 청크 6/20 번역 중…
  [20:52:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:52:17]    ↳ 청크 7/20 번역 중…
  [20:52:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:52:23]    ↳ 청크 8/20 번역 중…
  [20:52:30]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:52:31]    ↳ 청크 9/20 번역 중…
  [20:52:37]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:52:38]    ↳ 청크 10/20 번역 중…
  [20:52:42]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:52:43]    ↳ 청크 11/20 번역 중…
  [20:52:51]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:52:52]    ↳ 청크 12/20 번역 중…
  [20:52:58]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:52:59]    ↳ 청크 13/20 번역 중…
  [20:53:04]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:53:05]    ↳ 청크 14/20 번역 중…
  [20:53:11]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:53:12]    ↳ 청크 15/20 번역 중…
  [20:53:19]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:53:20]    ↳ 청크 16/20 번역 중…
  [20:53:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:53:27]    ↳ 청크 17/20 번역 중…
  [20:53:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:53:34]    ↳ 청크 18/20 번역 중…
  [20:53:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:53:42]    ↳ 청크 19/20 번역 중…
  [20:53:47]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:53:48]    ↳ 청크 20/20 번역 중…
  [20:53:50]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [20:53:50] ✅ 번역 완료
  [20:53:50]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [20:53:51]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 2건, Sub-C fallback 0건
  [20:55:56]    ⚠ canonicalize entity 외 변경 의심 5건 (canonical 채택, 로그만):
  [20:55:56]   L2: '[00:13] 티파니 잔젠: 티파니 잔젠입니다. 오늘 저희와 함께해 주실…' → '[00:13] 티파니 잔젠: 티파니 잔젠입니다. 오늘 저희와 함께해 주실…'
  [20:55:56]   L16: '[00:31] 티파니 잔젠: 사실 오늘 이 대화를 가지게 될 예정이라는 …' → '[00:31] 티파니 잔젠: 사실 오늘 이 대화를 가지게 될 예정이라는 …'
  [20:55:56]   L20: '[00:34] 판카즈 샤르마: 맞습니다. 그리고 이 과제는 단순히 기술적…' → '[00:34] 판카즈 샤르마: 맞습니다. 그리고 이 과제는 단순히 기술적…'
  [20:55:56]   L22: '[00:39] 판카즈 샤르마: AI가 하나로 할 때 따라 이 에너지 인텔…' → '[00:39] 판카즈 샤르마: AI가 하나로 할 때 따라 이 에너지 인텔…'
  [20:55:56]   L26: '[00:48] 판카즈 샤르마: AI 인프라를 위한 에너지는 제품처럼 잘 …' → '[00:48] 판카즈 샤르마: AI 인프라를 위한 에너지는 제품처럼 잘 …'
  [20:55:56]    🔧 entity canonicalize 적용 (5건 cache, 줄 수 574 → 574)

=== 결과 (326.5초 = 5.4분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260522_205556.md

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
    '슈나이더 일렉트릭': 8회
    '스키에더 일렉트릭': 0회
    '슈나이더 일렉트리': 0회
    '슈나이더일렉트릭': 0회
  Test 9: 화자명 hallucinate 부재
    '티파즈 샤르마': 0회 ✅
    '판카즈 잔젠': 0회 ✅
    '티파니 샤르마': 0회 ✅
    '판카즈 티파니': 0회 ✅
  Test 10: speaker prefix 영역 (가장 자주 catch)
    '판카즈 샤르마': 198회
    '티파니 잔젠': 55회
    'Pankaj Sharma': 14회
    'outputs_english_original_15_items_separately

[09': 2회
    'outputs_english_original_15_items_separately

[10': 2회

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

🎉 real video verify 종료 (5.4분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260522_205556.md
