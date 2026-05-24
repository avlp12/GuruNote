======================================================================
community-1 + (가) 2-pass 검증 — 화자 3명 자막 영상
URL: https://youtu.be/oE5lNDhz9oo
DEFAULT_DIARIZATION_MODEL: default(community-1)
GURUNOTE_TWO_PASS: 1
======================================================================

[1/3] download_audio (yt-dlp + 자막)…
  audio_path: /var/folders/8f/yykrhnsj0fxfxs4nt7vr6x1h0000gn/T/gn_verify_lg5_ztwn/oE5lNDhz9oo.wav
  video_id: oE5lNDhz9oo
  video_title: "Nvidia's Huang, Michael Dell on Agentic AI, Memory Demand and China"
  uploader: 'Bloomberg Television'
  duration: 1229.0s
  description (앞 200자): "Nvidia CEO Jensen Huang and Dell CEO Michael Dell discuss agentic AI, the demand for memory and the outlook for the China market with Bloomberg's Ed Ludlow on the sidelines of the Dell World event in "
  subtitles_source: 'auto_or_manual'
  subtitles_text length: 18913 chars
  download 시간: 5.9s

[2/3] transcribe (MLX Whisper + community-1)…
  [22:55:44] MLX Whisper 모델 로딩 (mlx-community/whisper-large-v3-mlx)...
  [22:55:44] 전사 중 (Apple GPU 가속, 단어 레벨 타임스탬프)...
Fetching 4 files:   0%|          | 0/4 [00:00<?, ?it/s]Fetching 4 files: 100%|██████████| 4/4 [00:00<00:00, 59705.40it/s]
Detected language: English
  0%|          | 0/122847 [00:00<?, ?frames/s]  2%|▏         | 2472/122847 [00:02<01:38, 1216.55frames/s]  4%|▍         | 5198/122847 [00:03<01:14, 1589.31frames/s]  7%|▋         | 8198/122847 [00:04<01:04, 1787.11frames/s]  9%|▉         | 11198/122847 [00:06<00:56, 1980.80frames/s] 12%|█▏        | 14136/122847 [00:07<00:54, 2001.90frames/s] 14%|█▍        | 17136/122847 [00:08<00:51, 2067.49frames/s] 16%|█▋        | 20136/122847 [00:10<00:45, 2257.57frames/s] 19%|█▉        | 23136/122847 [00:11<00:45, 2205.07frames/s] 21%|██▏       | 26136/122847 [00:18<01:38, 981.38frames/s]  24%|██▎       | 29136/122847 [00:19<01:19, 1173.80frames/s] 26%|██▌       | 32090/122847 [00:21<01:07, 1351.19frames/s] 29%|██▊       | 35090/122847 [00:22<00:57, 1532.26frames/s] 31%|███       | 38090/122847 [00:24<00:55, 1520.48frames/s] 33%|███▎      | 41090/122847 [00:25<00:49, 1662.92frames/s] 36%|███▌      | 43882/122847 [00:26<00:43, 1836.20frames/s] 38%|███▊      | 46880/122847 [00:30<00:59, 1278.92frames/s] 41%|████      | 49880/122847 [00:32<00:51, 1426.39frames/s] 43%|████▎     | 52880/122847 [00:33<00:44, 1566.37frames/s] 45%|████▌     | 55880/122847 [00:35<00:40, 1659.89frames/s] 48%|████▊     | 58880/122847 [00:37<00:37, 1725.24frames/s] 50%|█████     | 61796/122847 [00:38<00:33, 1805.65frames/s] 53%|█████▎    | 64656/122847 [00:39<00:30, 1897.79frames/s] 55%|█████▍    | 67554/122847 [00:41<00:30, 1807.51frames/s] 57%|█████▋    | 70444/122847 [00:43<00:29, 1806.30frames/s] 60%|█████▉    | 73444/122847 [00:44<00:26, 1832.34frames/s] 62%|██████▏   | 76444/122847 [00:46<00:24, 1863.78frames/s] 65%|██████▍   | 79444/122847 [00:47<00:22, 1903.28frames/s] 67%|██████▋   | 82344/122847 [00:49<00:20, 1961.25frames/s] 69%|██████▉   | 85342/122847 [00:50<00:18, 2028.21frames/s] 72%|███████▏  | 88342/122847 [00:52<00:17, 2000.09frames/s] 74%|███████▍  | 91276/122847 [00:53<00:14, 2106.92frames/s] 77%|███████▋  | 94068/122847 [00:54<00:13, 2194.85frames/s] 79%|███████▉  | 96946/122847 [00:55<00:11, 2184.14frames/s] 81%|████████▏ | 99946/122847 [00:57<00:10, 2180.34frames/s] 84%|████████▍ | 102946/122847 [00:58<00:09, 2140.45frames/s] 86%|████████▌ | 105946/122847 [01:00<00:08, 2018.94frames/s] 89%|████████▊ | 108746/122847 [01:01<00:06, 2028.28frames/s] 91%|█████████ | 111678/122847 [01:03<00:05, 1964.12frames/s] 93%|█████████▎| 114550/122847 [01:05<00:04, 1888.29frames/s] 96%|█████████▌| 117530/122847 [01:06<00:02, 1884.26frames/s] 98%|█████████▊| 120530/122847 [01:08<00:01, 1819.15frames/s]100%|██████████| 122847/122847 [01:09<00:00, 1877.00frames/s]100%|██████████| 122847/122847 [01:09<00:00, 1767.43frames/s]
  [22:56:56] 전사 완료 — 342 세그먼트, 언어=en
  [22:56:56] 화자 분리 중 (pyannote, MPS 가속)...
  [22:57:38] 화자 분리 완료 — 110 발화 구간
  [22:57:38] 세그먼트 필터링 — empty/noise 21, duplicate 0 제거 (342 → 321)
  [22:57:38] MLX 전사 완료 — 321 세그먼트, 3 화자
  transcribe 시간: 114.6s
  segments: 321
  language: en
  engine: mlx
  화자 분포: {'A': 151, 'B': 90, 'C': 80}

[3/3] translate_transcript (2-pass + 화자 코드 부착)…
  [22:57:39] 🌐 LLM 번역 시작 — 22 청크 (openai_compatible/qwen3.6-35b-q5)
  [22:57:39] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [22:57:46]    📚 entity cache bootstrap — 36건 사전 추출
  [22:57:46]    🎤 speaker cache bootstrap — 3명 식별
  [22:57:46]    ↳ 청크 1/22 번역 중…
  [22:57:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:57:51]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:57:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [22:57:58]    ↳ 청크 2/22 번역 중…
  [22:57:58]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:58:02]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:58:07]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [22:58:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [22:58:34]    ↳ 청크 3/22 번역 중…
  [22:58:34]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:58:38]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:58:43]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [22:58:48]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [22:58:49]    ↳ 청크 4/22 번역 중…
  [22:58:49]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:58:54]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:58:59]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [22:59:00]    ↳ 청크 5/22 번역 중…
  [22:59:00]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:59:03]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:59:08]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [22:59:09]    ↳ 청크 6/22 번역 중…
  [22:59:09]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:59:13]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:59:18]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [22:59:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [22:59:22]    ⚠ 2-pass 빈 output 1건 → [번역 누락] padding
  [22:59:23]    ↳ 청크 7/22 번역 중…
  [22:59:23]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:59:26]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:59:31]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [22:59:32]    ↳ 청크 8/22 번역 중…
  [22:59:32]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:59:36]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:59:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [22:59:42]    ↳ 청크 9/22 번역 중…
  [22:59:42]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:59:45]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:59:50]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [22:59:51]    ↳ 청크 10/22 번역 중…
  [22:59:51]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [22:59:55]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [22:59:59]    ⚠ 길이 미스매치: 11 != 15 (retry 1/3, finish_reason=stop)
  [23:00:04]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:00:04]    ⚠ 2-pass 빈 output 1건 → [번역 누락] padding
  [23:00:05]    ↳ 청크 11/22 번역 중…
  [23:00:05]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:00:09]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:00:14]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:00:14]    ⚠ 2-pass 빈 output 1건 → [번역 누락] padding
  [23:00:15]    ↳ 청크 12/22 번역 중…
  [23:00:15]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:00:19]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:00:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:00:25]    ↳ 청크 13/22 번역 중…
  [23:00:25]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:00:29]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:00:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:00:35]    ↳ 청크 14/22 번역 중…
  [23:00:35]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:00:39]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:00:45]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [23:01:07]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:01:07]    ⚠ 2-pass 빈 output 1건 → [번역 누락] padding
  [23:01:08]    ↳ 청크 15/22 번역 중…
  [23:01:08]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:01:12]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:01:18]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:01:19]    ↳ 청크 16/22 번역 중…
  [23:01:19]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:01:23]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:01:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:01:29]    ↳ 청크 17/22 번역 중…
  [23:01:29]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:01:33]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:01:38]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:01:39]    ↳ 청크 18/22 번역 중…
  [23:01:39]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:01:42]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:01:47]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [23:01:51]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:01:51]    ⚠ 2-pass 빈 output 1건 → [번역 누락] padding
  [23:01:52]    ↳ 청크 19/22 번역 중…
  [23:01:52]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:01:55]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:02:00]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:02:01]    ↳ 청크 20/22 번역 중…
  [23:02:01]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:02:04]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:02:08]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:02:08]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [23:02:09]    ↳ 청크 21/22 번역 중…
  [23:02:09]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:02:13]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:02:17]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:02:18]    ↳ 청크 22/22 번역 중…
  [23:02:18]    ↳ 2-pass 1단계: 자유 번역 (6 segments)
  [23:02:22]    ↳ 2-pass 2단계: 정렬 (6 outputs schema strict)
  [23:02:25]    ✅ Index Mapping 정합 — 6 outputs (finish_reason=stop)
  [23:02:25] ✅ 번역 완료
  [23:02:25]    💾 entity cache 저장: 36건 / speakers 3명 → oE5lNDhz9oo
  [23:02:27]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 2건, Sub-C fallback 0건
  [23:03:57]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)
  translate 시간: 378.8s
  result 본문 길이: 15754 chars

결과 저장: /Users/gesicht/GuruNote/verify_results/community1_3speakers_body.md
segments dump: /Users/gesicht/GuruNote/verify_results/community1_3speakers_segments.json
