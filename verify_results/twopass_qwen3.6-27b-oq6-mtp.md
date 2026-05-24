=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [14:19:31] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-27B-oQ6-mtp)
  [14:19:31] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [14:19:31]    📚 entity cache bootstrap — 5건 사전 추출
  [14:19:31]    ↳ 청크 1/20 번역 중…
  [14:19:31]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:19:52]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:20:14]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:20:15]    ↳ 청크 2/20 번역 중…
  [14:20:15]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:20:30]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:20:50]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:20:51]    ↳ 청크 3/20 번역 중…
  [14:20:51]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:21:06]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:21:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:21:27]    ↳ 청크 4/20 번역 중…
  [14:21:27]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:21:43]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:22:02]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:22:03]    ↳ 청크 5/20 번역 중…
  [14:22:03]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:22:19]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:22:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:22:42]    ↳ 청크 6/20 번역 중…
  [14:22:42]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:22:57]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:23:16]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [14:23:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:23:37]    ↳ 청크 7/20 번역 중…
  [14:23:37]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:23:52]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:24:12]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:24:13]    ↳ 청크 8/20 번역 중…
  [14:24:13]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:24:27]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:24:47]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:24:48]    ↳ 청크 9/20 번역 중…
  [14:24:48]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:25:03]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:25:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:25:24]    ↳ 청크 10/20 번역 중…
  [14:25:24]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:25:39]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:25:58]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [14:26:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:26:17]    ↳ 청크 11/20 번역 중…
  [14:26:17]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:26:31]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:26:50]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:26:51]    ↳ 청크 12/20 번역 중…
  [14:26:51]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:27:07]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:27:28]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [14:27:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:27:50]    ↳ 청크 13/20 번역 중…
  [14:27:50]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:28:05]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:28:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:28:25]    ↳ 청크 14/20 번역 중…
  [14:28:25]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:28:41]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:29:01]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:29:02]    ↳ 청크 15/20 번역 중…
  [14:29:02]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:29:20]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:29:44]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:29:45]    ↳ 청크 16/20 번역 중…
  [14:29:45]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:30:00]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:30:21]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:30:22]    ↳ 청크 17/20 번역 중…
  [14:30:22]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:30:39]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:31:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:31:01]    ↳ 청크 18/20 번역 중…
  [14:31:01]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:31:18]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:31:42]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:31:43]    ↳ 청크 19/20 번역 중…
  [14:31:43]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:31:58]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:32:20]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:32:21]    ↳ 청크 20/20 번역 중…
  [14:32:21]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [14:32:28]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [14:32:36]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [14:32:36] ✅ 번역 완료
  [14:32:36]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [14:32:43]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 4건, Sub-C fallback 0건
  [14:34:13]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (883.7초 = 14.7분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_143413.md

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
    '판카즈 샤르마': 212회
    '티파니 잔젠': 68회
    '티파니 잔젠(Tiffany Janzen)': 1회
    '티파니 잔젠(Tiffany Jan젠)': 1회
    '[02': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 23건
    길이 미스매치 retry: 3건
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

🎉 real video verify 종료 (14.7분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_143413.md
