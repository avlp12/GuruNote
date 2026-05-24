=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [18:23:18] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-35B-A3B-oQ6-mtp)
  [18:23:18] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [18:23:18]    📚 entity cache bootstrap — 4건 사전 추출
  [18:23:18]    🎤 speaker cache bootstrap — 1명 식별
  [18:23:18]    ↳ 청크 1/20 번역 중…
  [18:23:18]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:23:23]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:23:28]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [18:23:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:23:34]    ⚠ 2-pass 빈 output 2건 → [번역 누락] padding
  [18:23:35]    ↳ 청크 2/20 번역 중…
  [18:23:35]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:23:38]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:23:43]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:23:48]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:23:48]    ⚠ 2-pass 빈 output 1건 → [번역 누락] padding
  [18:23:49]    ↳ 청크 3/20 번역 중…
  [18:23:49]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:23:53]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:23:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:23:58]    ↳ 청크 4/20 번역 중…
  [18:23:58]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:24:03]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:24:08]    ⚠ 길이 미스매치: 12 != 15 (retry 1/3, finish_reason=stop)
  [18:24:13]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:24:14]    ↳ 청크 5/20 번역 중…
  [18:24:14]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:24:18]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:24:23]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:24:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:24:29]    ↳ 청크 6/20 번역 중…
  [18:24:29]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:24:33]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:24:38]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [18:24:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:24:44]    ↳ 청크 7/20 번역 중…
  [18:24:44]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:24:48]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:24:53]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:24:54]    ↳ 청크 8/20 번역 중…
  [18:24:54]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:24:57]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:25:01]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:25:02]    ↳ 청크 9/20 번역 중…
  [18:25:02]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:25:06]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:25:11]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:25:11]    ⚠ 2-pass 빈 output 3건 → [번역 누락] padding
  [18:25:12]    ↳ 청크 10/20 번역 중…
  [18:25:12]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:25:16]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:25:21]    ⚠ 길이 미스매치: 12 != 15 (retry 1/3, finish_reason=stop)
  [18:25:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:25:27]    ↳ 청크 11/20 번역 중…
  [18:25:27]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:25:31]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:25:35]    ⚠ 길이 미스매치: 16 != 15 (retry 1/3, finish_reason=stop)
  [18:25:55]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:25:55]    ⚠ 2-pass 빈 output 3건 → [번역 누락] padding
  [18:25:56]    ↳ 청크 12/20 번역 중…
  [18:25:56]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:26:00]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:26:05]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:26:06]    ↳ 청크 13/20 번역 중…
  [18:26:06]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:26:10]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:26:15]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:26:16]    ↳ 청크 14/20 번역 중…
  [18:26:16]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:26:19]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:26:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:26:25]    ↳ 청크 15/20 번역 중…
  [18:26:25]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:26:30]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:26:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:26:37]    ↳ 청크 16/20 번역 중…
  [18:26:37]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:26:42]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:26:48]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:26:49]    ↳ 청크 17/20 번역 중…
  [18:26:49]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:26:53]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:26:58]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:27:03]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:27:03]    ⚠ 2-pass 빈 output 1건 → [번역 누락] padding
  [18:27:04]    ↳ 청크 18/20 번역 중…
  [18:27:04]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:27:09]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:27:15]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:27:16]    ↳ 청크 19/20 번역 중…
  [18:27:16]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:27:20]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:27:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:27:27]    ↳ 청크 20/20 번역 중…
  [18:27:27]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [18:27:28]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [18:27:30]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [18:27:30] ✅ 번역 완료
  [18:27:30]    💾 entity cache 저장: 4건 / speakers 1명 → title_9374256ae7e318fc
  [18:27:33]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 3건, Sub-C fallback 0건
  [18:29:03]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (345.6초 = 5.8분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_182903.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 288
    ✅ PASS
  Test 2: timestamp 완전성 — expected 271, actual 271, missing 0, extra 0
    ✅ PASS
  Test 3: 번역 누락 marker — 10건
    ⚠ FAIL (10건)
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
    '화자 2': 206회
    '판카즈 샤르마': 81회
    '판카즈 샤르마(Pankaj Sharma)': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 28건
    길이 미스매치 retry: 8건
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

🎉 real video verify 종료 (5.8분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_182903.md
