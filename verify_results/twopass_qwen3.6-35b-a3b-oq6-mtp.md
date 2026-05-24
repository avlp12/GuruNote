=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [15:09:21] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-35B-A3B-oQ6-mtp)
  [15:09:21] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [15:09:21]    📚 entity cache bootstrap — 5건 사전 추출
  [15:09:21]    ↳ 청크 1/20 번역 중…
  [15:09:21]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:09:26]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:09:32]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:09:33]    ↳ 청크 2/20 번역 중…
  [15:09:33]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:09:38]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:09:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:09:46]    ↳ 청크 3/20 번역 중…
  [15:09:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:09:51]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:09:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:09:58]    ↳ 청크 4/20 번역 중…
  [15:09:58]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:10:03]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:10:09]    ⚠ 길이 미스매치: 11 != 15 (retry 1/3, finish_reason=stop)
  [15:10:51]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:10:52]    ↳ 청크 5/20 번역 중…
  [15:10:52]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:10:58]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:11:06]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:11:07]    ↳ 청크 6/20 번역 중…
  [15:11:07]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:11:12]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:11:20]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:11:21]    ↳ 청크 7/20 번역 중…
  [15:11:21]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:11:26]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:11:32]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:11:33]    ↳ 청크 8/20 번역 중…
  [15:11:33]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:11:38]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:11:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:11:44]    ↳ 청크 9/20 번역 중…
  [15:11:44]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:11:49]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:11:55]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [15:12:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:12:29]    ↳ 청크 10/20 번역 중…
  [15:12:29]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:12:34]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:12:39]    ⚠ 길이 미스매치: 12 != 15 (retry 1/3, finish_reason=stop)
  [15:12:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:12:46]    ↳ 청크 11/20 번역 중…
  [15:12:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:12:50]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:12:56]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [15:13:01]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:13:02]    ↳ 청크 12/20 번역 중…
  [15:13:02]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:13:07]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:13:14]    ⚠ 길이 미스매치: 11 != 15 (retry 1/3, finish_reason=stop)
  [15:13:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:14:00]    ↳ 청크 13/20 번역 중…
  [15:14:00]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:14:05]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:14:11]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:14:12]    ↳ 청크 14/20 번역 중…
  [15:14:12]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:14:17]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:14:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:14:23]    ↳ 청크 15/20 번역 중…
  [15:14:23]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:14:30]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:14:37]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:14:38]    ↳ 청크 16/20 번역 중…
  [15:14:38]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:14:45]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:14:52]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:14:53]    ↳ 청크 17/20 번역 중…
  [15:14:53]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:14:59]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:15:07]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:15:08]    ↳ 청크 18/20 번역 중…
  [15:15:08]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:15:14]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:15:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:15:24]    ↳ 청크 19/20 번역 중…
  [15:15:24]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [15:15:30]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [15:15:37]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [15:15:38]    ↳ 청크 20/20 번역 중…
  [15:15:38]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [15:15:40]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [15:15:41]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [15:15:41] ✅ 번역 완료
  [15:15:41]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [15:15:42]    🔧 Phase 3 후처리 — Sub-A 1건, Sub-B 1건, Sub-C fallback 0건
  [15:17:12]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (472.6초 = 7.9분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_151712.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 288
    ✅ PASS
  Test 2: timestamp 완전성 — expected 271, actual 284, missing 0, extra 13
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
    '슈나이더 일렉트릭': 6회
    '스키에더 일렉트릭': 0회
    '슈나이더 일렉트리': 1회
    '슈나이더일렉트릭': 0회
  Test 9: 화자명 hallucinate 부재
    '티파즈 샤르마': 0회 ✅
    '판카즈 잔젠': 0회 ✅
    '티파니 샤르마': 0회 ✅
    '판카즈 티파니': 0회 ✅
  Test 10: speaker prefix 영역 (가장 자주 catch)
    '판카즈 샤르마': 171회
    '티파니 잔젠': 96회
    '[01': 11회
    '[00': 5회
    'A': 2회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 25건
    길이 미스매치 retry: 5건
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

🎉 real video verify 종료 (7.9분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_151712.md
