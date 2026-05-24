=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [16:43:55] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [16:43:55] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [16:43:55]    📚 entity cache bootstrap — 5건 사전 추출
  [16:43:55]    ↳ 청크 1/20 번역 중…
  [16:43:55]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:43:58]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:44:04]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:44:05]    ↳ 청크 2/20 번역 중…
  [16:44:05]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:44:09]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:44:14]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [16:44:38]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:44:39]    ↳ 청크 3/20 번역 중…
  [16:44:39]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:44:43]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:44:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:44:50]    ↳ 청크 4/20 번역 중…
  [16:44:50]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:44:54]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:44:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:44:59]    ⚠ 2-pass 빈 output 2건 → [번역 누락] padding
  [16:45:00]    ↳ 청크 5/20 번역 중…
  [16:45:00]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:45:05]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:45:10]    ⚠ 길이 미스매치: 12 != 15 (retry 1/3, finish_reason=stop)
  [16:45:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:45:36]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [16:45:37]    ↳ 청크 6/20 번역 중…
  [16:45:37]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:45:42]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:45:46]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:45:46]    ⚠ 2-pass 빈 output 4건 → [번역 누락] padding
  [16:45:47]    ↳ 청크 7/20 번역 중…
  [16:45:47]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:45:52]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:45:56]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:45:57]    ↳ 청크 8/20 번역 중…
  [16:45:57]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:46:02]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:46:06]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:46:07]    ↳ 청크 9/20 번역 중…
  [16:46:07]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:46:11]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:46:17]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:46:17]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [16:46:18]    ↳ 청크 10/20 번역 중…
  [16:46:18]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:46:22]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:46:27]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [16:46:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:46:50]    ↳ 청크 11/20 번역 중…
  [16:46:50]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:46:54]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:46:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:47:00]    ↳ 청크 12/20 번역 중…
  [16:47:00]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:47:03]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:47:09]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:47:09]    ⚠ 2-pass 빈 output 5건 → [번역 누락] padding
  [16:47:10]    ↳ 청크 13/20 번역 중…
  [16:47:10]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:47:14]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:47:20]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:47:21]    ↳ 청크 14/20 번역 중…
  [16:47:21]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:47:25]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:47:31]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:47:32]    ↳ 청크 15/20 번역 중…
  [16:47:32]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:47:37]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:47:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:47:46]    ↳ 청크 16/20 번역 중…
  [16:47:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:47:50]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:47:56]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:47:57]    ↳ 청크 17/20 번역 중…
  [16:47:57]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:48:02]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:48:08]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [16:48:14]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:48:15]    ↳ 청크 18/20 번역 중…
  [16:48:15]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:48:20]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:48:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:48:29]    ↳ 청크 19/20 번역 중…
  [16:48:29]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:48:34]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:48:40]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:48:41]    ↳ 청크 20/20 번역 중…
  [16:48:41]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [16:48:43]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [16:48:45]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [16:48:45] ✅ 번역 완료
  [16:48:45]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [16:48:46]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 1건, Sub-C fallback 0건
  [16:50:16]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (383.0초 = 6.4분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_165016.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 288
    ✅ PASS
  Test 2: timestamp 완전성 — expected 271, actual 271, missing 0, extra 0
    ✅ PASS
  Test 3: 번역 누락 marker — 11건
    ⚠ FAIL (11건)
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
    '판카즈 샤르마': 94회
    '티파니 잔젠': 39회
    '[번역 누락]

[05': 2회
    '[번역 누락]

[10': 2회
    '티파니 잔젠(Tiffany Janzen)': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 24건
    길이 미스매치 retry: 4건
    fallback path 진입: 0건
    Index Mapping 정합: 20건

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

🎉 real video verify 종료 (6.4분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_165016.md
