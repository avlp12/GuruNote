=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [16:23:54] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-27B-oQ8-mtp)
  [16:23:54] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [16:23:54]    📚 entity cache bootstrap — 5건 사전 추출
  [16:23:54]    ↳ 청크 1/20 번역 중…
  [16:23:54]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:24:08]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:24:31]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [16:24:54]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:24:55]    ↳ 청크 2/20 번역 중…
  [16:24:55]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:25:07]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:25:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:25:27]    ↳ 청크 3/20 번역 중…
  [16:25:27]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:25:39]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:26:02]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:26:03]    ↳ 청크 4/20 번역 중…
  [16:26:03]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:26:16]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:26:43]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [16:27:10]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:27:10]    ⚠ 2-pass 연속 동일 output 2건 catch — 정상 반복 가능성
  [16:27:11]    ↳ 청크 5/20 번역 중…
  [16:27:11]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:27:24]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:27:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:27:49]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [16:27:50]    ↳ 청크 6/20 번역 중…
  [16:27:50]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:28:05]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:28:31]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [16:28:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:29:00]    ↳ 청크 7/20 번역 중…
  [16:29:00]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:29:11]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:29:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:29:35]    ↳ 청크 8/20 번역 중…
  [16:29:35]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:29:46]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:30:09]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:30:10]    ↳ 청크 9/20 번역 중…
  [16:30:10]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:30:23]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:30:46]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:30:47]    ↳ 청크 10/20 번역 중…
  [16:30:47]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:31:00]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:31:24]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [16:31:48]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:31:49]    ↳ 청크 11/20 번역 중…
  [16:31:49]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:31:59]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:32:21]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [16:32:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:32:43]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [16:32:44]    ↳ 청크 12/20 번역 중…
  [16:32:44]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:32:57]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:33:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:33:23]    ↳ 청크 13/20 번역 중…
  [16:33:23]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:33:35]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:33:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:33:58]    ↳ 청크 14/20 번역 중…
  [16:33:58]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:34:10]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:34:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:34:34]    ↳ 청크 15/20 번역 중…
  [16:34:34]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:34:49]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:35:17]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:35:18]    ↳ 청크 16/20 번역 중…
  [16:35:18]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:35:33]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:36:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:36:01]    ↳ 청크 17/20 번역 중…
  [16:36:01]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:36:13]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:36:37]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:36:38]    ↳ 청크 18/20 번역 중…
  [16:36:38]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:36:53]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:37:23]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:37:24]    ↳ 청크 19/20 번역 중…
  [16:37:24]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [16:37:36]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [16:37:55]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [16:37:55]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [16:37:56]    ↳ 청크 20/20 번역 중…
  [16:37:56]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [16:38:03]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [16:38:12]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [16:38:12] ✅ 번역 완료
  [16:38:12]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [16:38:24]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 7건, Sub-C fallback 0건
  [16:39:55]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (962.3초 = 16.0분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_163955.md

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
    '판카즈 샤르마': 168회
    '티파니 잔젠': 74회
    '여러분, 안녕하십니까. 엔비디아(NVIDIA) GTC 스튜디오에 오신 것을 환영합니다.

[00': 1회
    '판카즈 샤르마는 슈나이더 일렉트릭의 소프트웨어 및 서비스 담당 상무이사입니다.

[00': 1회
    '감사합니다, 티파니 잔젠.

[00': 1회

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

🎉 real video verify 종료 (16.0분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_163955.md
