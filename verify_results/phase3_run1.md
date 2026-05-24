=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [17:05:50] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [17:05:50] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [17:05:50]    ↳ 청크 1/20 번역 중…
  [17:06:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:06:01]    ↳ 청크 2/20 번역 중…
  [17:06:10]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:06:11]    ↳ 청크 3/20 번역 중…
  [17:06:17]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:06:18]    ↳ 청크 4/20 번역 중…
  [17:06:25]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:06:26]    ↳ 청크 5/20 번역 중…
  [17:06:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:06:35]    ↳ 청크 6/20 번역 중…
  [17:06:42]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:06:43]    ↳ 청크 7/20 번역 중…
  [17:06:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:06:50]    ↳ 청크 8/20 번역 중…
  [17:06:58]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:06:59]    ↳ 청크 9/20 번역 중…
  [17:11:19]    ⚠ JSON 파싱 부재 (retry 1/3): Expecting ',' delimiter: line 14 column 53 (char 674)
  [17:11:19]    ↳ json_object mode 전환 (xgrammar 우회)
  [17:11:24]    ⚠ 길이 미스매치: 14 != 15 (retry 2/3, finish_reason=stop)
  [17:11:30]    ⚠ 길이 미스매치: 14 != 15 (retry 3/3, finish_reason=stop)
  [17:11:30]    ⚠ Index Mapping retry 3회 실패 — fallback (14 → 15)
  [17:11:31]    ↳ 청크 10/20 번역 중…
  [17:15:33]    ⚠ JSON 파싱 부재 (retry 1/3): Expecting ',' delimiter: line 15 column 19 (char 713)
  [17:15:33]    ↳ json_object mode 전환 (xgrammar 우회)
  [17:15:38]    ⚠ 길이 미스매치: 12 != 15 (retry 2/3, finish_reason=stop)
  [17:16:07]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:16:08]    ↳ 청크 11/20 번역 중…
  [17:16:14]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:16:15]    ↳ 청크 12/20 번역 중…
  [17:16:21]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:16:22]    ↳ 청크 13/20 번역 중…
  [17:16:29]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:16:30]    ↳ 청크 14/20 번역 중…
  [17:16:35]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:16:36]    ↳ 청크 15/20 번역 중…
  [17:16:44]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:16:45]    ↳ 청크 16/20 번역 중…
  [17:16:52]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:16:53]    ↳ 청크 17/20 번역 중…
  [17:17:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:17:01]    ↳ 청크 18/20 번역 중…
  [17:17:07]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:17:08]    ↳ 청크 19/20 번역 중…
  [17:17:13]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:17:14]    ↳ 청크 20/20 번역 중…
  [17:17:16]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [17:17:16] ✅ 번역 완료
  [17:17:16]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 0건, Sub-C fallback 0건

=== 결과 (686.3초 = 11.4분) ===
  결과 file: /tmp/realvideo_verify_result.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 288
    ✅ PASS
  Test 2: timestamp 완전성 — expected 271, actual 271, missing 0, extra 0
    ✅ PASS
  Test 3: 번역 누락 marker — 1건
    ⚠ FAIL (1건)
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
    '티파니 잔젠': 58회
    '샘 올트먼': 5회
    '젠슨 황': 4회
    '[05': 2회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 25건
    길이 미스매치 retry: 3건
    fallback path 진입: 1건
    Index Mapping 정합: 19건

=== 자동 검증 종합 ===
  7/8 통과
    ✅ 1. line count
    ✅ 2. timestamp 완전성
    ⚠ 3. 번역 누락 marker
    ✅ 4. 한자/일본어 부재
    ✅ 5. chunk 수
    ✅ 6. drift 부재
    ✅ 7. 5/12 누락 회귀 부재
    ✅ 9. 화자명 hallucinate 부재

🎉 real video verify 종료 (11.4분, 20 chunks 처리)
   결과 file: /tmp/realvideo_verify_result.md
