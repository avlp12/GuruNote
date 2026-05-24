=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [02:31:58] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-35B-A3B-oQ6-mtp)
  [02:31:58] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [02:31:58]    📚 entity cache bootstrap — 5건 사전 추출
  [02:31:58]    ↳ 청크 1/20 번역 중…
  [02:36:11]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:36:12]    ↳ 청크 2/20 번역 중…
  [02:37:06]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:37:07]    ↳ 청크 3/20 번역 중…
  [02:38:09]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:38:10]    ↳ 청크 4/20 번역 중…
  [02:39:29]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:39:30]    ↳ 청크 5/20 번역 중…
  [02:40:40]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:40:41]    ↳ 청크 6/20 번역 중…
  [02:41:16]    ⚠ 길이 미스매치: 11 != 15 (retry 1/3, finish_reason=stop)
  [02:42:38]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 2/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:42:39]    ↳ 청크 7/20 번역 중…
  [02:43:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:43:23]    ↳ 청크 8/20 번역 중…
  [02:44:17]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:44:18]    ↳ 청크 9/20 번역 중…
  [02:45:15]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:45:16]    ↳ 청크 10/20 번역 중…
  [02:48:09]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:48:10]    ↳ 청크 11/20 번역 중…
  [02:49:01]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:49:02]    ↳ 청크 12/20 번역 중…
  [02:50:08]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:50:09]    ↳ 청크 13/20 번역 중…
  [02:51:08]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:51:09]    ↳ 청크 14/20 번역 중…
  [02:51:52]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:51:53]    ↳ 청크 15/20 번역 중…
  [02:52:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:52:44]    ↳ 청크 16/20 번역 중…
  [02:53:51]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:53:52]    ↳ 청크 17/20 번역 중…
  [02:55:16]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:55:17]    ↳ 청크 18/20 번역 중…
  [02:56:26]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:56:27]    ↳ 청크 19/20 번역 중…
  [02:57:35]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [02:57:36]    ↳ 청크 20/20 번역 중…
  [02:58:14]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [02:58:14] ✅ 번역 완료
  [02:58:14]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [02:58:14]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 0건, Sub-C fallback 0건
  [03:01:08]    ⚠ canonicalize entity 외 변경 의심 16건 (canonical 채택, 로그만):
  [03:01:08]   L30: '[00:54] 티파니 잔젠(Tiffany Janzen): 성공하기 위해서…' → '[00:54] 티파니 잔젠: 성공하기 위해서는'
  [03:01:08]   L36: '[01:04] 판카즈 샤르마(Pankaj Sharma): 맞습니다. 우선…' → '[01:04] 판카즈 샤르마: 맞습니다. 우선 많은 과제와 기회를 동시에…'
  [03:01:08]   L180: '[05:12] 판카즈 샤르마(Pankaj Sharma): 기술적 손실을 …' → '[05:12] 판카즈 샤르마: 기술적 손실을 몇 퍼센트 포인트까지 낮출 …'
  [03:01:08]   L192: '[05:29] 티파니 잔젠(Tiffany Janzen): 슈나이더 일렉트…' → '[05:29] 티파니 잔젠: 슈나이더 일렉트릭에서는 AI를 활용해 이 분…'
  [03:01:08]   L210: '[06:02] 판카즈 샤르마(Pankaj Sharma): 엔비디아의 컴퓨…' → '[06:02] 판카즈 샤르마: 엔비디아의 컴퓨팅 성능이 훨씬 강력해지면서…'
  [03:01:08]    ⚠ … 외 11건
  [03:01:08]    🔧 entity canonicalize 적용 (5건 cache, 줄 수 574 → 574)

=== 결과 (1750.6초 = 29.2분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_030108.md

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
    '슈나이더 일렉트릭': 2회
    '스키에더 일렉트릭': 0회
    '슈나이더 일렉트리': 0회
    '슈나이더일렉트릭': 0회
  Test 9: 화자명 hallucinate 부재
    '티파즈 샤르마': 0회 ✅
    '판카즈 잔젠': 0회 ✅
    '티파니 샤르마': 0회 ✅
    '판카즈 티파니': 0회 ✅
  Test 10: speaker prefix 영역 (가장 자주 catch)
    '판카즈 샤르마': 96회
    '티파니 잔젠': 24회
    '[⚠ timeout]

[14': 10회
    '[⚠ timeout]

[02': 9회
    '[⚠ timeout]

[04': 9회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 21건
    길이 미스매치 retry: 1건
    fallback path 진입: 0건
    Index Mapping 정합: 9건

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

🎉 real video verify 종료 (29.2분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_030108.md
