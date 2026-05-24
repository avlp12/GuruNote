=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [10:40:47] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [10:40:47] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [10:40:47]    📚 entity cache bootstrap — 5건 사전 추출
  [10:40:47]    ↳ 청크 1/20 번역 중…
  [10:40:54]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:40:55]    ↳ 청크 2/20 번역 중…
  [10:41:01]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:41:02]    ↳ 청크 3/20 번역 중…
  [10:41:08]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:41:09]    ↳ 청크 4/20 번역 중…
  [10:41:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:41:17]    ↳ 청크 5/20 번역 중…
  [10:41:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:41:24]    ↳ 청크 6/20 번역 중…
  [10:45:12]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [10:45:13]    ↳ 청크 7/20 번역 중…
  [10:45:19]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:45:20]    ↳ 청크 8/20 번역 중…
  [10:45:25]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:45:26]    ↳ 청크 9/20 번역 중…
  [10:45:32]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:45:33]    ↳ 청크 10/20 번역 중…
  [10:49:29]    ⚠ chunk wall-clock timeout — R1 padding 적용 (15 segments, retry 1/3 부재): LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [10:49:30]    ↳ 청크 11/20 번역 중…
  [10:49:35]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:49:36]    ↳ 청크 12/20 번역 중…
  [10:49:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:49:44]    ↳ 청크 13/20 번역 중…
  [10:49:50]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:49:51]    ↳ 청크 14/20 번역 중…
  [10:49:58]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:49:59]    ↳ 청크 15/20 번역 중…
  [10:50:06]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:50:07]    ↳ 청크 16/20 번역 중…
  [10:50:14]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:50:15]    ↳ 청크 17/20 번역 중…
  [10:50:21]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:50:22]    ↳ 청크 18/20 번역 중…
  [10:50:30]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:50:31]    ↳ 청크 19/20 번역 중…
  [10:50:37]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [10:50:38]    ↳ 청크 20/20 번역 중…
  [10:50:40]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [10:50:40] ✅ 번역 완료
  [10:50:40]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [10:50:42]    🔧 Phase 3 후처리 — Sub-A 1건, Sub-B 2건, Sub-C fallback 0건
  [10:52:22]    ⚠ canonicalize entity 외 변경 의심 3건 (canonical 채택, 로그만):
  [10:52:22]   L2: '[00:13] 티파니 잔젠: 저는 티파니 잔젠입니다. 오늘은 슈나이더 일…' → '[00:13] 티파니 잔젠: 저는 티파니 잔젠입니다. 오늘은 슈나이더 일…'
  [10:52:22]   L468: '[13:19] 판카즈 샤르마: 약 2년 전, 모티브에어(Motivair)…' → '[13:19] 판카즈 샤르마: 약 2년 전, 모티브어(Motivair)가…'
  [10:52:22]   L482: '[14:04] 티파니 잔젠:Absolutely.' → '[14:04] 티파니 잔젠: Absolutely.'
  [10:52:22]    🔧 entity canonicalize 적용 (5건 cache, 줄 수 574 → 574)

=== 결과 (695.9초 = 11.6분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_105222.md

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
    '슈나이더 일렉트릭': 7회
    '스키에더 일렉트릭': 0회
    '슈나이더 일렉트리': 0회
    '슈나이더일렉트릭': 0회
  Test 9: 화자명 hallucinate 부재
    '티파즈 샤르마': 0회 ✅
    '판카즈 잔젠': 0회 ✅
    '티파니 샤르마': 0회 ✅
    '판카즈 티파니': 0회 ✅
  Test 10: speaker prefix 영역 (가장 자주 catch)
    '판카즈 샤르마': 184회
    '티파니 잔젠': 65회
    '[⚠ timeout]

[04': 6회
    '[⚠ timeout]

[08': 5회
    '[⚠ timeout]

[05': 2회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 20건
    길이 미스매치 retry: 0건
    fallback path 진입: 0건
    Index Mapping 정합: 18건

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

🎉 real video verify 종료 (11.6분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_105222.md
