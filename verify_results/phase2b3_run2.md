=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [23:56:08] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [23:56:08] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [23:56:10]    📚 entity cache bootstrap — 4건 사전 추출
  [23:56:10]    ↳ 청크 1/20 번역 중…
  [23:56:16]    ⚠ 길이 미스매치: 11 != 15 (retry 1/3, finish_reason=stop)
  [23:56:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:56:24]    📚 entity cache 갱신: +1건 (누적 5건)
  [23:56:25]    ↳ 청크 2/20 번역 중…
  [23:56:31]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:56:32]    ↳ 청크 3/20 번역 중…
  [23:56:38]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:56:39]    ↳ 청크 4/20 번역 중…
  [23:56:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:56:46]    ↳ 청크 5/20 번역 중…
  [23:56:54]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:56:56]    ↳ 청크 6/20 번역 중…
  [23:56:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:00]    ↳ 청크 7/20 번역 중…
  [23:57:05]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:06]    ↳ 청크 8/20 번역 중…
  [23:57:14]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:15]    ↳ 청크 9/20 번역 중…
  [23:57:20]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:21]    ↳ 청크 10/20 번역 중…
  [23:57:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:29]    ↳ 청크 11/20 번역 중…
  [23:57:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:35]    ↳ 청크 12/20 번역 중…
  [23:57:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:44]    ↳ 청크 13/20 번역 중…
  [23:57:50]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:51]    ↳ 청크 14/20 번역 중…
  [23:57:56]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:57]    ↳ 청크 15/20 번역 중…
  [23:58:04]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:58:05]    ↳ 청크 16/20 번역 중…
  [23:58:11]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:58:12]    ↳ 청크 17/20 번역 중…
  [23:58:18]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:58:19]    ↳ 청크 18/20 번역 중…
  [23:58:25]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:58:26]    ↳ 청크 19/20 번역 중…
  [23:58:32]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:58:33]    ↳ 청크 20/20 번역 중…
  [23:58:35]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [23:58:35] ✅ 번역 완료
  [23:58:35]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [23:58:35]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 0건, Sub-C fallback 0건
  [00:00:29]    🔧 entity canonicalize 적용 (5건 cache, 줄 수 582 → 582)

=== 결과 (261.0초 = 4.3분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260522_000029.md

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
    '판카즈 샤르마': 197회
    '티파니 잔젠': 75회
    '[01': 6회
    '[00': 1회
    'outputs_count_check_passed__true__15_items

[08': 1회

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

🎉 real video verify 종료 (4.3분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260522_000029.md
