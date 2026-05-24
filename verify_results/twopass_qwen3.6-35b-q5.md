=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [15:00:16] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [15:00:16] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [15:00:16]    📚 entity cache bootstrap — 5건 사전 추출
  [15:00:16]    ↳ 청크 1/20 번역 중…
  [15:00:16]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:00:21]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:00:27]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:00:28]    ↳ 청크 2/20 번역 중…
  [15:00:28]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:00:32]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:00:40]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:00:41]    ↳ 청크 3/20 번역 중…
  [15:00:41]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:00:46]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:00:52]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:00:53]    ↳ 청크 4/20 번역 중…
  [15:00:53]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:00:59]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:01:05]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [15:01:37]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:01:38]    ↳ 청크 5/20 번역 중…
  [15:01:38]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:01:43]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:01:49]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [15:02:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:02:17]    ↳ 청크 6/20 번역 중…
  [15:02:17]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:02:22]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:02:28]    ⚠ 길이 미스매치: 10 != 15 (retry 1/3, finish_reason=stop)
  [15:03:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:03:01]    ↳ 청크 7/20 번역 중…
  [15:03:01]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:03:06]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:03:12]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:03:13]    ↳ 청크 8/20 번역 중…
  [15:03:13]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:03:17]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:03:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:03:24]    ↳ 청크 9/20 번역 중…
  [15:03:24]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:03:29]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:03:35]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [15:03:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:04:00]    ↳ 청크 10/20 번역 중…
  [15:04:00]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:04:02]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:04:07]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:04:08]    ↳ 청크 11/20 번역 중…
  [15:04:08]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:04:12]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:04:18]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [15:04:44]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:04:45]    ↳ 청크 12/20 번역 중…
  [15:04:45]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:04:50]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:04:55]    ⚠ 길이 미스매치: 8 != 15 (retry 1/3, finish_reason=stop)
  [15:05:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:05:24]    ↳ 청크 13/20 번역 중…
  [15:05:24]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:05:29]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:05:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:05:35]    ↳ 청크 14/20 번역 중…
  [15:05:35]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:05:40]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:05:47]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:05:48]    ↳ 청크 15/20 번역 중…
  [15:05:48]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:05:54]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:06:01]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:06:02]    ↳ 청크 16/20 번역 중…
  [15:06:02]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:06:07]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:06:13]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:06:14]    ↳ 청크 17/20 번역 중…
  [15:06:14]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:06:20]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:06:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:06:29]    ↳ 청크 18/20 번역 중…
  [15:06:29]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:06:34]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:06:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:06:42]    ↳ 청크 19/20 번역 중…
  [15:06:42]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:06:47]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:06:53]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:06:54]    ↳ 청크 20/20 번역 중…
  [15:06:54]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [15:06:55]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [15:06:57]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [15:06:57] ✅ 번역 완료
  [15:06:57]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [15:06:58]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 1건, Sub-C fallback 0건
  [15:08:30]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (494.8초 = 8.2분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_150830.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 295
    ⚠ MISMATCH
  Test 2: timestamp 완전성 — expected 271, actual 289, missing 0, extra 18
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
    '판카즈 샤르마': 162회
    '티파니 잔젠': 34회
    '[00': 29회
    'B': 17회
    'A': 13회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 26건
    길이 미스매치 retry: 6건
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

🎉 real video verify 종료 (8.2분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_150830.md
