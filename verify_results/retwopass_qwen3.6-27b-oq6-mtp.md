=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [16:07:37] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-27B-oQ6-mtp)
  [16:07:37] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [16:07:37]    📚 entity cache bootstrap — 5건 사전 추출
  [16:07:37]    ↳ 청크 1/20 번역 중…
  [16:07:37]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:07:47]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:08:08]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:08:09]    ↳ 청크 2/20 번역 중…
  [16:08:09]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:08:19]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:08:39]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:08:40]    ↳ 청크 3/20 번역 중…
  [16:08:40]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:08:50]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:09:06]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:09:07]    ↳ 청크 4/20 번역 중…
  [16:09:07]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:09:19]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:09:42]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:09:42]    ⚠ 2-pass 빈 output 1건 → [번역 누락] padding
  [16:09:43]    ↳ 청크 5/20 번역 중…
  [16:09:43]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:09:55]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:10:18]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:10:19]    ↳ 청크 6/20 번역 중…
  [16:10:19]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:10:31]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:10:55]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [16:11:21]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:11:21]    ⚠ 2-pass 연속 동일 output 2건 catch — 정상 반복 가능성
  [16:11:22]    ↳ 청크 7/20 번역 중…
  [16:11:22]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:11:34]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:11:54]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:11:55]    ↳ 청크 8/20 번역 중…
  [16:11:55]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:12:05]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:12:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:12:27]    ↳ 청크 9/20 번역 중…
  [16:12:27]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:12:36]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:12:55]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:12:56]    ↳ 청크 10/20 번역 중…
  [16:12:56]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:13:05]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:13:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:13:25]    ↳ 청크 11/20 번역 중…
  [16:13:25]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:13:36]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:13:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:13:58]    ↳ 청크 12/20 번역 중…
  [16:13:58]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:14:10]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:14:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:14:35]    ↳ 청크 13/20 번역 중…
  [16:14:35]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:14:45]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:15:06]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:15:07]    ↳ 청크 14/20 번역 중…
  [16:15:07]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:15:17]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:15:37]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:15:38]    ↳ 청크 15/20 번역 중…
  [16:15:38]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:15:50]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:16:15]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:16:16]    ↳ 청크 16/20 번역 중…
  [16:16:16]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:16:28]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:16:51]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:16:52]    ↳ 청크 17/20 번역 중…
  [16:16:52]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:17:02]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:17:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:17:24]    ↳ 청크 18/20 번역 중…
  [16:17:24]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:17:37]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:18:02]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:18:03]    ↳ 청크 19/20 번역 중…
  [16:18:03]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:18:14]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:18:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:18:37]    ↳ 청크 20/20 번역 중…
  [16:18:37]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [16:18:44]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [16:18:52]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [16:18:52] ✅ 번역 완료
  [16:18:52]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [16:19:04]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 5건, Sub-C fallback 0건
  [16:20:34]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (778.9초 = 13.0분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_162034.md

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
    '판카즈 샤르마': 173회
    '티파니 잔젠': 79회
    '화자 A': 10회
    '화자 B': 5회
    '티파니 잔젠(Tiffany Janzen)': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 21건
    길이 미스매치 retry: 1건
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

🎉 real video verify 종료 (13.0분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_162034.md
