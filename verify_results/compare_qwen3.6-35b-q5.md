=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [02:24:07] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [02:24:07] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [02:24:07]    📚 entity cache bootstrap — 4건 사전 추출
  [02:24:07]    ↳ 청크 1/20 번역 중…
  [02:24:13]    ⚠ 길이 미스매치: 11 != 15 (retry 1/3, finish_reason=stop)
  [02:24:38]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:24:38]    📚 entity cache 갱신: +1건 (누적 5건)
  [02:24:39]    ↳ 청크 2/20 번역 중…
  [02:24:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:24:46]    ↳ 청크 3/20 번역 중…
  [02:24:51]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [02:24:56]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:24:57]    ↳ 청크 4/20 번역 중…
  [02:25:02]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [02:25:07]    ⚠ 길이 미스매치: 13 != 15 (retry 2/3, finish_reason=stop)
  [02:25:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:25:34]    ↳ 청크 5/20 번역 중…
  [02:25:40]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:25:41]    ↳ 청크 6/20 번역 중…
  [02:25:45]    ⚠ 길이 미스매치: 10 != 15 (retry 1/3, finish_reason=stop)
  [02:26:10]    ⚠ 길이 미스매치: 14 != 15 (retry 2/3, finish_reason=stop)
  [02:26:38]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:26:39]    ↳ 청크 7/20 번역 중…
  [02:26:44]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:26:45]    ↳ 청크 8/20 번역 중…
  [02:26:49]    ⚠ 길이 미스매치: 12 != 15 (retry 1/3, finish_reason=stop)
  [02:26:54]    ⚠ 길이 미스매치: 12 != 15 (retry 2/3, finish_reason=stop)
  [02:27:18]    ⚠ JSON 파싱 부재 (retry 3/3): Invalid \uXXXX escape: line 1 column 1109 (char 1108)
  [02:27:18]    ↳ json_object mode 전환 (xgrammar 우회)
  [02:27:18]    ⚠ Index Mapping retry 3회 실패 — fallback (12 → 15)
  [02:27:19]    ↳ 청크 9/20 번역 중…
  [02:27:24]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [02:27:29]    ⚠ 길이 미스매치: 13 != 15 (retry 2/3, finish_reason=stop)
  [02:27:34]    ⚠ 길이 미스매치: 13 != 15 (retry 3/3, finish_reason=stop)
  [02:27:34]    ⚠ Index Mapping retry 3회 실패 — fallback (13 → 15)
  [02:27:35]    ↳ 청크 10/20 번역 중…
  [02:27:39]    ⚠ 길이 미스매치: 12 != 15 (retry 1/3, finish_reason=stop)
  [02:27:44]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:27:45]    ↳ 청크 11/20 번역 중…
  [02:27:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:27:50]    ↳ 청크 12/20 번역 중…
  [02:27:54]    ⚠ 길이 미스매치: 8 != 15 (retry 1/3, finish_reason=stop)
  [02:27:58]    ⚠ 길이 미스매치: 8 != 15 (retry 2/3, finish_reason=stop)
  [02:28:19]    ⚠ 길이 미스매치: 8 != 15 (retry 3/3, finish_reason=stop)
  [02:28:19]    ⚠ Index Mapping retry 3회 실패 — fallback (8 → 15)
  [02:28:20]    ↳ 청크 13/20 번역 중…
  [02:28:25]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:28:26]    ↳ 청크 14/20 번역 중…
  [02:28:30]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:28:31]    ↳ 청크 15/20 번역 중…
  [02:28:37]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:28:38]    ↳ 청크 16/20 번역 중…
  [02:28:43]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:28:44]    ↳ 청크 17/20 번역 중…
  [02:28:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:28:50]    ↳ 청크 18/20 번역 중…
  [02:28:56]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [02:29:03]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:29:04]    ↳ 청크 19/20 번역 중…
  [02:29:08]    ⚠ 길이 미스매치: 10 != 15 (retry 1/3, finish_reason=stop)
  [02:29:13]    ⚠ 길이 미스매치: 14 != 15 (retry 2/3, finish_reason=stop)
  [02:29:39]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [02:29:40]    ↳ 청크 20/20 번역 중…
  [02:29:43]    ✅ Index Mapping 정합 — 3 outputs (finish_reason=stop)
  [02:29:43] ✅ 번역 완료
  [02:29:43]    💾 entity cache 저장: 5건 → title_9374256ae7e318fc
  [02:29:43]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 1건, Sub-C fallback 0건
  [02:31:27]    ⚠ canonicalize entity 외 변경 의심 2건 (canonical 채택, 로그만):
  [02:31:27]   L118: '[03:22] 판카즈 샤르마: 시스템을 나뉔 시스템, 시스템 내 대안을 …' → '[03:22] 판카즈 샤르마: 시스템을 나뉘 시스템, 시스템 내 대안을 …'
  [02:31:27]   L468: '[13:19] 판카즈 샤르마: 약 2년 전 모티브에어(Motivair)가…' → '[13:19] 판카즈 샤르마: 약 2년 전 모티브어(Motivair)가 …'
  [02:31:27]    🔧 entity canonicalize 적용 (5건 cache, 줄 수 574 → 574)

=== 결과 (440.3초 = 7.3분) ===
  결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_023127.md

=== 자동 검증 ===
  Test 1: line count — segments 288 vs output lines 288
    ✅ PASS
  Test 2: timestamp 완전성 — expected 271, actual 271, missing 0, extra 0
    ✅ PASS
  Test 3: 번역 누락 marker — 12건
    ⚠ FAIL (12건)
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
    '판카즈 샤르마': 192회
    '티파니 잔젠': 65회
    '[번역 누락]

[06': 2회
    '[번역 누락]

[09': 2회
    '[번역 누락]

[10': 2회

=== retry / fallback 패턴 catch ===
  retry/fallback 영역 log: 39건
    길이 미스매치 retry: 18건
    fallback path 진입: 3건
    Index Mapping 정합: 17건

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

🎉 real video verify 종료 (7.3분, 20 chunks 처리)
   결과 file: /Users/gesicht/GuruNote/verify_results/realvideo_body_20260523_023127.md
