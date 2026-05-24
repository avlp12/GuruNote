=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [18:04:40] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-27B-oQ6-mtp)
  [18:04:40] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [18:04:46]    📚 entity cache bootstrap — 4건 사전 추출
  [18:04:46]    🎤 speaker cache bootstrap — 1명 식별
  [18:04:46]    ↳ 청크 1/20 번역 중…
  [18:04:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:05:00]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:05:18]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:05:35]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:05:36]    ↳ 청크 2/20 번역 중…
  [18:05:36]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:05:47]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:06:02]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:06:14]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:06:15]    ↳ 청크 3/20 번역 중…
  [18:06:15]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:06:27]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:06:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:06:46]    ↳ 청크 4/20 번역 중…
  [18:06:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:07:00]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:07:19]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:07:38]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:07:39]    ↳ 청크 5/20 번역 중…
  [18:07:39]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:07:51]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:08:09]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:08:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:08:25]    ↳ 청크 6/20 번역 중…
  [18:08:25]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:08:38]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:08:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:08:57]    ⚠ 2-pass 빈 output 2건 → [번역 누락] padding
  [18:08:58]    ↳ 청크 7/20 번역 중…
  [18:08:58]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:09:10]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:09:27]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:09:28]    ↳ 청크 8/20 번역 중…
  [18:09:28]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:09:40]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:09:55]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:09:56]    ↳ 청크 9/20 번역 중…
  [18:09:56]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:10:08]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:10:24]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:10:40]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:10:41]    ↳ 청크 10/20 번역 중…
  [18:10:41]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:10:53]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:11:09]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:11:10]    ↳ 청크 11/20 번역 중…
  [18:11:10]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:11:22]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:11:38]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:11:51]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:11:51]    ⚠ 2-pass 빈 output 1건 → [번역 누락] padding
  [18:11:52]    ↳ 청크 12/20 번역 중…
  [18:11:52]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:12:06]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:12:25]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:12:26]    ↳ 청크 13/20 번역 중…
  [18:12:26]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:12:38]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:12:54]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:12:55]    ↳ 청크 14/20 번역 중…
  [18:12:55]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:13:06]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:13:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:13:23]    ↳ 청크 15/20 번역 중…
  [18:13:23]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:13:37]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:13:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:13:58]    ↳ 청크 16/20 번역 중…
  [18:13:58]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:14:11]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:14:29]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:14:30]    ↳ 청크 17/20 번역 중…
  [18:14:30]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:14:44]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:15:02]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [18:16:02]    ⚠ chunk wall-clock timeout — retry 2/3: LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [18:16:02]    ↳ R3-수정: timeout 시 json_object mode 전환 (strict 부담 회피)
  [18:17:02]    ⚠ chunk wall-clock timeout — retry 3/3: LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [18:17:02]    ⚠ Index Mapping retry 3회 실패 — fallback (14 → 15, marker='[⚠ timeout]')
  [18:17:03]    ↳ 청크 18/20 번역 중…
  [18:17:03]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:17:24]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:17:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:17:46]    ↳ 청크 19/20 번역 중…
  [18:17:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [18:17:59]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [18:18:16]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [18:18:16]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [18:18:17]    ↳ 청크 20/20 번역 중…
  [18:18:17]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [18:18:24]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [18:18:31]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [18:18:31] ✅ 번역 완료
  [18:18:31]    💾 entity cache 저장: 4건 / speakers 1명 → title_9374256ae7e318fc
  [18:18:34]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 2건, Sub-C fallback 0건
  [18:20:04]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (926.0초 = 15.4분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_182004.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 288
    ✅ PASS
  Test 2: timestamp 완전성 — expected 271, actual 271, missing 0, extra 0
    ✅ PASS
  Test 3: 번역 누락 marker — 3건
    ⚠ FAIL (3건)
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
  retry/fallback 영역 log: 29건
    길이 미스매치 retry: 7건
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

🎉 real video verify 종료 (15.4분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_182004.md
