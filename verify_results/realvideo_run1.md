=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [20:56:55] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [20:56:55] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [20:56:55]    ↳ 청크 1/20 번역 중…
  [20:57:05]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:57:06]    ↳ 청크 2/20 번역 중…
  [20:57:12]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:57:13]    ↳ 청크 3/20 번역 중…
  [20:57:20]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:57:21]    ↳ 청크 4/20 번역 중…
  [20:57:27]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:57:28]    ↳ 청크 5/20 번역 중…
  [20:57:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:57:37]    ↳ 청크 6/20 번역 중…
  [20:57:47]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:57:48]    ↳ 청크 7/20 번역 중…
  [20:57:53]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:57:54]    ↳ 청크 8/20 번역 중…
  [20:58:03]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:58:04]    ↳ 청크 9/20 번역 중…
  [20:58:09]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:58:10]    ↳ 청크 10/20 번역 중…
  [20:58:17]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:58:18]    ↳ 청크 11/20 번역 중…
  [20:58:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:58:24]    ↳ 청크 12/20 번역 중…
  [20:58:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:58:34]    ↳ 청크 13/20 번역 중…
  [20:58:39]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:58:41]    ↳ 청크 14/20 번역 중…
  [20:58:46]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:58:47]    ↳ 청크 15/20 번역 중…
  [20:58:54]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:58:55]    ↳ 청크 16/20 번역 중…
  [20:59:01]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:59:02]    ↳ 청크 17/20 번역 중…
  [20:59:08]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:59:09]    ↳ 청크 18/20 번역 중…
  [20:59:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:59:17]    ↳ 청크 19/20 번역 중…
  [20:59:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:59:23]    ↳ 청크 20/20 번역 중…
  [20:59:25]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [20:59:25] ✅ 번역 완료

=== 결과 (149.5초 = 2.5분) ===
  결과 file: /tmp/realvideo_verify_result.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 288
    ✅ PASS
  Test 2: timestamp 완전성 — expected 271, actual 271, missing 0, extra 0
    ✅ PASS
  Test 3: 번역 누락 marker — 0건
    ✅ PASS
  Test 4: 한자/일본어 잔재 — 3건
    ⚠ 잔재: ['这', '正', '是']
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
    '판카즈 샤르마': 196회
    '티파니 잔젠': 73회
    '티파니 잔젠(Tiffany Janzen)': 1회
    'inputs_length_check_failed': 1회
    'outputs_length_check_failed': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 20건
    길이 미스매치 retry: 0건
    fallback path 진입: 0건
    Index Mapping 정합: 20건

=== 자동 검증 종합 ===
  7/8 통과
    ✅ 1. line count
    ✅ 2. timestamp 완전성
    ✅ 3. 번역 누락 marker
    ⚠ 4. 한자/일본어 부재
    ✅ 5. chunk 수
    ✅ 6. drift 부재
    ✅ 7. 5/12 누락 회귀 부재
    ✅ 9. 화자명 hallucinate 부재

🎉 real video verify 종료 (2.5분, 20 chunks 처리)
   결과 file: /tmp/realvideo_verify_result.md
