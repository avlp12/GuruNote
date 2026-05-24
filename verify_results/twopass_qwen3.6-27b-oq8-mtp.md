=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [14:37:34] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/Qwen3.6-27B-oQ8-mtp)
  [14:37:34] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [14:37:34]    📚 entity cache bootstrap — 5건 사전 추출
  [14:37:34]    ↳ 청크 1/20 번역 중…
  [14:37:34]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:37:53]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:38:20]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:38:21]    ↳ 청크 2/20 번역 중…
  [14:38:21]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:38:39]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:39:03]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:39:04]    ↳ 청크 3/20 번역 중…
  [14:39:04]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:39:21]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:39:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:39:46]    ↳ 청크 4/20 번역 중…
  [14:39:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:40:04]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:40:30]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [14:41:30]    ⚠ chunk wall-clock timeout — retry 2/3: LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [14:41:30]    ↳ R3-수정: timeout 시 json_object mode 전환 (strict 부담 회피)
  [14:42:30]    ⚠ chunk wall-clock timeout — retry 3/3: LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
  [14:42:30]    ⚠ Index Mapping retry 3회 실패 — fallback (14 → 15, marker='[⚠ timeout]')
  [14:42:31]    ↳ 청크 5/20 번역 중…
  [14:42:31]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:42:58]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:43:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:43:27]    ↳ 청크 6/20 번역 중…
  [14:43:27]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:43:54]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:44:21]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:44:22]    ↳ 청크 7/20 번역 중…
  [14:44:22]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:44:38]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:45:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:45:01]    ↳ 청크 8/20 번역 중…
  [14:45:01]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:45:16]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:45:39]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:45:40]    ↳ 청크 9/20 번역 중…
  [14:45:40]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:45:55]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:46:17]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:46:18]    ↳ 청크 10/20 번역 중…
  [14:46:18]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:46:34]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:46:55]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:46:56]    ↳ 청크 11/20 번역 중…
  [14:46:56]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:47:12]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:47:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:47:35]    ↳ 청크 12/20 번역 중…
  [14:47:35]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:47:53]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:48:18]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [14:48:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:48:46]    ↳ 청크 13/20 번역 중…
  [14:48:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:49:02]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:49:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:49:27]    ↳ 청크 14/20 번역 중…
  [14:49:27]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:49:44]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:50:07]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:50:08]    ↳ 청크 15/20 번역 중…
  [14:50:08]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:50:27]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:50:54]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:50:55]    ↳ 청크 16/20 번역 중…
  [14:50:55]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:51:13]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:51:38]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:51:39]    ↳ 청크 17/20 번역 중…
  [14:51:39]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:51:56]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:52:20]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:52:21]    ↳ 청크 18/20 번역 중…
  [14:52:21]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:52:40]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:53:08]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [14:53:37]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:53:38]    ↳ 청크 19/20 번역 중…
  [14:53:38]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [14:53:55]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [14:54:19]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [14:54:20]    ↳ 청크 20/20 번역 중…
  [14:54:20]    ↳ 2-pass 1단계: 자유 번역 (3 segments)
  [14:54:27]    ↳ 2-pass 2단계: 정렬 (3 outputs schema strict)
  [14:54:36]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [14:54:36] ✅ 번역 완료
  [14:54:36]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [14:54:37]    🔧 Phase 3 후처리 — Sub-A 1건, Sub-B 1건, Sub-C fallback 0건
  [14:56:07]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)

=== 결과 (1115.1초 = 18.6분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_145607.md

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
    '판카즈 샤르마': 187회
    '티파니 잔젠': 95회
    '티파니 잔젠(Tiffany Janzen)': 1회
    '티파니 잔젠(Tiffany Jan젠)': 1회
    '[⚠ timeout]

[03': 1회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 25건
    길이 미스매치 retry: 3건
    fallback path 진입: 1건
    Index Mapping 정합: 19건

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

🎉 real video verify 종료 (18.6분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_145607.md
