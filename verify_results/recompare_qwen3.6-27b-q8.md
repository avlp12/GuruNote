=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [09:53:45] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-27b-q8)
  [09:53:45] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [09:53:45]    📚 entity cache bootstrap — 5건 사전 추출
  [09:53:45]    ↳ 청크 1/20 번역 중…
  [09:54:12]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:54:13]    ↳ 청크 2/20 번역 중…
  [09:54:38]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:54:39]    ↳ 청크 3/20 번역 중…
  [09:55:04]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:55:05]    ↳ 청크 4/20 번역 중…
  [09:55:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:55:35]    ↳ 청크 5/20 번역 중…
  [09:56:03]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:56:04]    ↳ 청크 6/20 번역 중…
  [09:56:32]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:56:33]    ↳ 청크 7/20 번역 중…
  [09:56:58]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:56:59]    ↳ 청크 8/20 번역 중…
  [09:57:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:57:25]    ↳ 청크 9/20 번역 중…
  [09:57:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:57:50]    ↳ 청크 10/20 번역 중…
  [10:13:54]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [10:13:55]    ↳ 청크 11/20 번역 중…
  [10:14:20]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:14:21]    ↳ 청크 12/20 번역 중…
  [10:14:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:14:50]    ↳ 청크 13/20 번역 중…
  [10:15:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:15:17]    ↳ 청크 14/20 번역 중…
  [10:15:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:15:42]    ↳ 청크 15/20 번역 중…
  [10:16:12]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:16:13]    ↳ 청크 16/20 번역 중…
  [10:16:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:16:42]    ↳ 청크 17/20 번역 중…
  [10:17:08]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:17:09]    ↳ 청크 18/20 번역 중…
  [10:17:40]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:17:41]    ↳ 청크 19/20 번역 중…
  [10:18:06]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:18:07]    ↳ 청크 20/20 번역 중…
  [10:18:17]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [10:18:17] ✅ 번역 완료
  [10:18:17]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [10:18:26]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 3건, Sub-C fallback 0건
  [10:26:05]    ⚠ canonicalize entity 외 변경 의심 32건 (canonical 채택, 로그만):
  [10:26:05]   L0: '[00:10] 티파니 잔젠(Tiffany Janzen): 여러분, 엔비디…' → '[00:10] 티파니 잔젠: 여러분, 엔비디아 지티씨 스튜디오에 오신 것…'
  [10:26:05]   L2: '[00:13] 티파니 잔젠: 저는 티파니 잔젠이며, 오늘 슈나이더 일렉트…' → '[00:13] 티파니 잔젠: 저는 티파니 잔젠이며, 오늘 슈나이더 일렉트…'
  [10:26:05]   L4: '[00:17] 티파니 잔젠: 소프트웨어 및 서비스 부문 책임자 판카즈 샤…' → '[00:17] 티파니 잔젠: 소프트웨어 및 서비스 부문 책임자 판카즈 샤…'
  [10:26:05]   L10: '[00:23] 티파니 잔젠: 오늘까지 지티씨(GTC) 일정은 어떠셨나요?' → '[00:23] 티파니 잔젠: 오늘까지 지티씨 일정은 어떠셨나요?'
  [10:26:05]   L36: '[01:04] 판카즈 샤르마(Pankaj Sharma): 우선 많은 도전…' → '[01:04] 판카즈 샤르마: 우선 많은 도전 과제와 기회를 가져옵니다.'
  [10:26:05]    ⚠ … 외 27건
  [10:26:05]    🔧 entity canonicalize 적용 (5건 cache, 줄 수 574 → 574)

=== 결과 (1942.1초 = 32.4분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_102605.md

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
    '슈나이더 일렉트릭': 6회
    '스키에더 일렉트릭': 0회
    '슈나이더 일렉트리': 0회
    '슈나이더일렉트릭': 0회
  Test 9: 화자명 hallucinate 부재
    '티파즈 샤르마': 0회 ✅
    '판카즈 잔젠': 0회 ✅
    '티파니 샤르마': 0회 ✅
    '판카즈 티파니': 0회 ✅
  Test 10: speaker prefix 영역 (가장 자주 catch)
    '판카즈 샤르마': 181회
    '티파니 잔젠': 72회
    '화자 1': 14회
    '[⚠ timeout]

[08': 5회
    '화자 2': 5회

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

🎉 real video verify 종료 (32.4분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_102605.md
