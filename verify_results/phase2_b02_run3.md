=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [17:36:02] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [17:36:02] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [17:36:03]    📚 entity cache bootstrap — 5건 사전 추출
  [17:36:03]    ↳ 청크 1/20 번역 중…
  [17:36:09]    ⚠ 길이 미스매치: 12 != 15 (retry 1/3, finish_reason=stop)
  [17:36:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:36:16]    📚 entity cache 갱신: +1건 (누적 6건)
  [17:36:17]    ↳ 청크 2/20 번역 중…
  [17:36:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:36:24]    ↳ 청크 3/20 번역 중…
  [17:36:30]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:36:31]    ↳ 청크 4/20 번역 중…
  [17:36:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:36:37]    ↳ 청크 5/20 번역 중…
  [17:36:44]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:36:45]    ↳ 청크 6/20 번역 중…
  [17:36:53]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:36:54]    ↳ 청크 7/20 번역 중…
  [17:37:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:37:01]    ↳ 청크 8/20 번역 중…
  [17:37:08]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:37:09]    ↳ 청크 9/20 번역 중…
  [17:37:14]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:37:15]    ↳ 청크 10/20 번역 중…
  [17:37:21]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:37:22]    ↳ 청크 11/20 번역 중…
  [17:37:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:37:29]    ↳ 청크 12/20 번역 중…
  [17:37:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:37:37]    ↳ 청크 13/20 번역 중…
  [17:37:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:37:44]    ↳ 청크 14/20 번역 중…
  [17:37:50]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:37:51]    ↳ 청크 15/20 번역 중…
  [17:37:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:37:58]    ↳ 청크 16/20 번역 중…
  [17:38:05]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:38:06]    ↳ 청크 17/20 번역 중…
  [17:38:13]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:38:14]    ↳ 청크 18/20 번역 중…
  [17:38:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:38:23]    ↳ 청크 19/20 번역 중…
  [17:38:29]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:38:30]    ↳ 청크 20/20 번역 중…
  [17:38:32]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [17:38:32] ✅ 번역 완료
  [17:38:33]    🔧 Phase 3 후처리 — Sub-A 1건, Sub-B 1건, Sub-C fallback 0건

=== 결과 (151.3초 = 2.5분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260520_173833.md

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
    '판카지 샤르마': 184회
    '티파니 잔젠': 69회
    '판카지 샤르르': 5회
    '판카즈 샤르마': 2회
    '[07': 2회

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

🎉 real video verify 종료 (2.5분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260520_173833.md
