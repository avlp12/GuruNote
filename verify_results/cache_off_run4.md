=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [09:05:02] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [09:05:02] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [09:05:02]    ↳ 청크 1/20 번역 중…
  [09:05:10]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:05:11]    ↳ 청크 2/20 번역 중…
  [09:09:34]    ⚠ JSON 파싱 부재 (retry 1/3): Expecting ',' delimiter: line 16 column 42 (char 724)
  [09:09:34]    ↳ json_object mode 전환 (xgrammar 우회)
  [09:09:40]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:09:41]    ↳ 청크 3/20 번역 중…
  [09:09:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:09:50]    ↳ 청크 4/20 번역 중…
  [09:09:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:09:58]    ↳ 청크 5/20 번역 중…
  [09:10:06]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:10:07]    ↳ 청크 6/20 번역 중…
  [09:10:17]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:10:18]    ↳ 청크 7/20 번역 중…
  [09:10:25]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:10:26]    ↳ 청크 8/20 번역 중…
  [09:10:32]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:10:33]    ↳ 청크 9/20 번역 중…
  [09:10:39]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:10:40]    ↳ 청크 10/20 번역 중…
  [09:10:47]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:10:48]    ↳ 청크 11/20 번역 중…
  [09:11:02]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:11:03]    ↳ 청크 12/20 번역 중…
  [09:11:10]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:11:11]    ↳ 청크 13/20 번역 중…
  [09:11:17]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:11:18]    ↳ 청크 14/20 번역 중…
  [09:11:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:11:25]    ↳ 청크 15/20 번역 중…
  [09:12:10]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:12:11]    ↳ 청크 16/20 번역 중…
  [09:12:19]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:12:20]    ↳ 청크 17/20 번역 중…
  [09:12:27]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:12:28]    ↳ 청크 18/20 번역 중…
  [09:12:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:12:37]    ↳ 청크 19/20 번역 중…
  [09:12:44]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [09:12:45]    ↳ 청크 20/20 번역 중…
  [09:12:47]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [09:12:47] ✅ 번역 완료

=== 결과 (465.6초 = 7.8분) ===
  결과 file: /tmp/realvideo_verify_result.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 300
    ⚠ MISMATCH
  Test 2: timestamp 완전성 — expected 271, actual 271, missing 0, extra 0
    ✅ PASS
  Test 3: 번역 누락 marker — 0건
    ✅ PASS
  Test 4: 한자/일본어 잔재 — 16건
    ⚠ 잔재: ['取', 'り', '組', 'ん', 'で', 'い', 'る', '考', 'え', 'る']
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
    '판카즈 샤르마': 208회
    '티파니 잔젠': 66회
    '티파니 잔젠(Tiffany Janzen)': 1회
    '티파닌 잔젠': 1회
    '판카즈 슈르마': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 21건
    길이 미스매치 retry: 0건
    fallback path 진입: 0건
    Index Mapping 정합: 20건

=== 자동 검증 종합 ===
  6/8 통과
    ⚠ 1. line count
    ✅ 2. timestamp 완전성
    ✅ 3. 번역 누락 marker
    ⚠ 4. 한자/일본어 부재
    ✅ 5. chunk 수
    ✅ 6. drift 부재
    ✅ 7. 5/12 누락 회귀 부재
    ✅ 9. 화자명 hallucinate 부재

🎉 real video verify 종료 (7.8분, 20 chunks 처리)
   결과 file: /tmp/realvideo_verify_result.md
