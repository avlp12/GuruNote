=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [16:50:50] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-35B-A3B-oQ6-mtp)
  [16:50:50] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [16:50:50]    📚 entity cache bootstrap — 5건 사전 추출
  [16:50:50]    ↳ 청크 1/20 번역 중…
  [16:50:50]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:50:54]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:51:01]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:51:02]    ↳ 청크 2/20 번역 중…
  [16:51:02]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:51:07]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:51:12]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:51:13]    ↳ 청크 3/20 번역 중…
  [16:51:13]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:51:18]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:51:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:51:24]    ↳ 청크 4/20 번역 중…
  [16:51:24]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:51:28]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:51:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:51:33]    ⚠ 2-pass 빈 output 4건 → [번역 누락] padding
  [16:51:34]    ↳ 청크 5/20 번역 중…
  [16:51:34]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:51:39]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:51:46]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:51:47]    ↳ 청크 6/20 번역 중…
  [16:51:47]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:51:51]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:51:56]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:51:57]    ↳ 청크 7/20 번역 중…
  [16:51:57]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:52:01]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:52:06]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [16:52:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:52:23]    ↳ 청크 8/20 번역 중…
  [16:52:23]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:52:27]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:52:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:52:34]    ↳ 청크 9/20 번역 중…
  [16:52:34]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:52:38]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:52:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:52:45]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [16:52:46]    ↳ 청크 10/20 번역 중…
  [16:52:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:52:50]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:52:56]    ⚠ 길이 미스매치: 11 != 15 (retry 1/3, finish_reason=stop)
  [16:53:21]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:53:21]    ⚠ 2-pass 빈 output 4건 → [번역 누락] padding
  [16:53:22]    ↳ 청크 11/20 번역 중…
  [16:53:22]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:53:26]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:53:32]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:53:33]    ↳ 청크 12/20 번역 중…
  [16:53:33]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:53:37]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:53:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:53:44]    ↳ 청크 13/20 번역 중…
  [16:53:44]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:53:48]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:53:53]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:53:54]    ↳ 청크 14/20 번역 중…
  [16:53:54]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:53:58]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:54:04]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:54:05]    ↳ 청크 15/20 번역 중…
  [16:54:05]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:54:11]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:54:19]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:54:20]    ↳ 청크 16/20 번역 중…
  [16:54:20]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:54:25]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:54:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:54:34]    ↳ 청크 17/20 번역 중…
  [16:54:34]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:54:38]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:54:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:54:46]    ↳ 청크 18/20 번역 중…
  [16:54:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:54:51]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:54:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:55:00]    ↳ 청크 19/20 번역 중…
  [16:55:00]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:55:04]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:55:10]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [16:55:15]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:55:16]    ↳ 청크 20/20 번역 중…
  [16:55:16]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [16:55:18]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [16:55:20]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [16:55:20] ✅ 번역 완료
  [16:55:20]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [16:55:21]    🔧 Phase 3 후처리 — Sub-A 1건, Sub-B 1건, Sub-C fallback 0건
  [16:56:51]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (362.9초 = 6.0분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_165651.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 288
    ✅ PASS
  Test 2: timestamp 완전성 — expected 271, actual 271, missing 0, extra 0
    ✅ PASS
  Test 3: 번역 누락 marker — 8건
    ⚠ FAIL (8건)
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
    '슈나이더 일렉트리': 1회
    '슈나이더일렉트릭': 0회
  Test 9: 화자명 hallucinate 부재
    '티파즈 샤르마': 0회 ✅
    '판카즈 잔젠': 0회 ✅
    '티파니 샤르마': 0회 ✅
    '판카즈 티파니': 0회 ✅
  Test 10: speaker prefix 영역 (가장 자주 catch)
    '판카즈 샤르마': 121회
    '티파니 잔젠': 40회
    '[번역 누락]

[03': 2회
    '[번역 누락]

[08': 2회
    '티파니 잔젠(Tiffany Janzen)': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 23건
    길이 미스매치 retry: 3건
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

🎉 real video verify 종료 (6.0분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_165651.md
