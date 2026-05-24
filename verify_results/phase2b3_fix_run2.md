=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [20:44:49] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [20:44:49] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [20:44:49]    📚 entity cache bootstrap — 5건 사전 추출
  [20:44:49]    ↳ 청크 1/20 번역 중…
  [20:44:55]    ⚠ 길이 미스매치: 10 != 15 (retry 1/3, finish_reason=stop)
  [20:45:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:45:35]    ↳ 청크 2/20 번역 중…
  [20:45:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:45:46]    ↳ 청크 3/20 번역 중…
  [20:45:51]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:45:52]    ↳ 청크 4/20 번역 중…
  [20:46:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:46:01]    ↳ 청크 5/20 번역 중…
  [20:46:09]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:46:10]    ↳ 청크 6/20 번역 중…
  [20:46:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:46:17]    ↳ 청크 7/20 번역 중…
  [20:46:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:46:23]    ↳ 청크 8/20 번역 중…
  [20:46:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:46:29]    ↳ 청크 9/20 번역 중…
  [20:46:35]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:46:36]    ↳ 청크 10/20 번역 중…
  [20:46:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:46:42]    ↳ 청크 11/20 번역 중…
  [20:46:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:46:50]    ↳ 청크 12/20 번역 중…
  [20:47:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:47:01]    ↳ 청크 13/20 번역 중…
  [20:47:06]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:47:07]    ↳ 청크 14/20 번역 중…
  [20:47:12]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:47:13]    ↳ 청크 15/20 번역 중…
  [20:47:19]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:47:20]    ↳ 청크 16/20 번역 중…
  [20:47:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:47:27]    ↳ 청크 17/20 번역 중…
  [20:47:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:47:34]    ↳ 청크 18/20 번역 중…
  [20:47:40]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:47:41]    ↳ 청크 19/20 번역 중…
  [20:47:47]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [20:47:48]    ↳ 청크 20/20 번역 중…
  [20:47:49]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [20:47:49] ✅ 번역 완료
  [20:47:49]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [20:47:49]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 0건, Sub-C fallback 0건
  [20:49:59]    ⚠ canonicalize entity 외 변경 의심 1건 (canonical 채택, 로그만):
  [20:49:59]   L2: '[00:13] 티파니 잔젠(Tiffany Janzen): 제 이름은 티파…' → '[00:13] 티파니 잔젠(Tiffany Janzen): 제 이름은 티파…'
  [20:49:59]    🔧 entity canonicalize 적용 (5건 cache, 줄 수 592 → 592)

=== 결과 (310.5초 = 5.2분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260522_204959.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 297
    ⚠ MISMATCH
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
    '판카즈 샤르마': 193회
    '티파니 잔젠': 91회
    '안녕하세요, 여러분. 엔비디아 GTC 스튜디오에 오신 것을 환영합니다.

[00': 1회
    '판카즈 샤르마(Pankaj Sharma)': 1회
    '판카즈 샤르마(Schneider Electric의 판카즈 샤르마)': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 21건
    길이 미스매치 retry: 1건
    fallback path 진입: 0건
    Index Mapping 정합: 20건

=== 자동 검증 종합 ===
  7/8 통과
    ⚠ 1. line count
    ✅ 2. timestamp 완전성
    ✅ 3. 번역 누락 marker
    ✅ 4. 한자/일본어 부재
    ✅ 5. chunk 수
    ✅ 6. drift 부재
    ✅ 7. 5/12 누락 회귀 부재
    ✅ 9. 화자명 hallucinate 부재

🎉 real video verify 종료 (5.2분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260522_204959.md
