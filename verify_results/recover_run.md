======================================================================
community-1 + (가) 2-pass 검증 — 화자 3명 자막 영상
URL: https://youtu.be/oE5lNDhz9oo
DEFAULT_DIARIZATION_MODEL: default(community-1)
GURUNOTE_TWO_PASS: 1
======================================================================

[1/3] download_audio (yt-dlp + 자막)…
  audio_path: /var/folders/8f/yykrhnsj0fxfxs4nt7vr6x1h0000gn/T/gn_verify_4n8k8qrc/oE5lNDhz9oo.wav
  video_id: oE5lNDhz9oo
  video_title: "Nvidia's Huang, Michael Dell on Agentic AI, Memory Demand and China"
  uploader: 'Bloomberg Television'
  duration: 1229.0s
  description (앞 200자): "Nvidia CEO Jensen Huang and Dell CEO Michael Dell discuss agentic AI, the demand for memory and the outlook for the China market with Bloomberg's Ed Ludlow on the sidelines of the Dell World event in "
  subtitles_source: 'auto_or_manual'
  subtitles_text length: 18913 chars
  download 시간: 5.9s

[2/3] transcribe (MLX Whisper + community-1)…
  [23:52:30] MLX Whisper 모델 로딩 (mlx-community/whisper-large-v3-mlx)...
  [23:52:30] 전사 중 (Apple GPU 가속, 단어 레벨 타임스탬프)...
Fetching 4 files:   0%|          | 0/4 [00:00<?, ?it/s]Fetching 4 files: 100%|██████████| 4/4 [00:00<00:00, 110376.42it/s]
Detected language: English
  0%|          | 0/122847 [00:00<?, ?frames/s]  2%|▏         | 2472/122847 [00:01<01:23, 1445.72frames/s]  4%|▍         | 5198/122847 [00:03<01:07, 1742.51frames/s]  7%|▋         | 8198/122847 [00:04<01:02, 1846.13frames/s]  9%|▉         | 11198/122847 [00:05<00:56, 1993.42frames/s] 12%|█▏        | 14136/122847 [00:07<00:55, 1974.01frames/s] 14%|█▍        | 17136/122847 [00:08<00:52, 2005.94frames/s] 16%|█▋        | 20136/122847 [00:10<00:47, 2175.01frames/s] 19%|█▉        | 23136/122847 [00:11<00:47, 2099.31frames/s] 19%|█▉        | 23136/122847 [00:29<00:47, 2099.31frames/s] 21%|██        | 26066/122847 [00:31<04:00, 402.03frames/s]  24%|██▎       | 29066/122847 [00:33<02:55, 534.53frames/s] 26%|██▌       | 32066/122847 [00:34<02:10, 697.17frames/s] 29%|██▊       | 35066/122847 [00:36<01:39, 881.15frames/s] 31%|███       | 37890/122847 [00:37<01:20, 1056.11frames/s] 33%|███▎      | 40890/122847 [00:39<01:05, 1254.41frames/s] 36%|███▌      | 43888/122847 [00:42<01:14, 1061.43frames/s] 38%|███▊      | 46886/122847 [00:44<01:01, 1231.06frames/s] 41%|████      | 49884/122847 [00:45<00:53, 1370.71frames/s] 43%|████▎     | 52884/122847 [00:47<00:46, 1502.83frames/s] 45%|████▌     | 55848/122847 [00:49<00:42, 1584.29frames/s] 48%|████▊     | 58848/122847 [00:50<00:38, 1653.54frames/s] 50%|█████     | 61796/122847 [00:52<00:35, 1742.94frames/s] 53%|█████▎    | 64656/122847 [00:53<00:31, 1838.23frames/s] 55%|█████▍    | 67554/122847 [00:55<00:30, 1799.22frames/s] 57%|█████▋    | 70444/122847 [00:56<00:29, 1787.25frames/s] 60%|█████▉    | 73444/122847 [00:58<00:27, 1804.87frames/s] 62%|██████▏   | 76444/122847 [01:00<00:25, 1831.19frames/s] 65%|██████▍   | 79444/122847 [01:01<00:23, 1865.64frames/s] 67%|██████▋   | 82344/122847 [01:03<00:21, 1925.65frames/s] 69%|██████▉   | 85342/122847 [01:04<00:18, 1990.05frames/s] 72%|███████▏  | 88342/122847 [01:06<00:17, 1957.80frames/s] 74%|███████▍  | 91276/122847 [01:07<00:15, 2061.07frames/s] 77%|███████▋  | 94068/122847 [01:08<00:13, 2145.23frames/s] 79%|███████▉  | 96946/122847 [01:09<00:12, 2133.32frames/s] 81%|████████▏ | 99946/122847 [01:11<00:10, 2129.81frames/s] 84%|████████▍ | 102946/122847 [01:12<00:09, 2089.91frames/s] 86%|████████▌ | 105946/122847 [01:14<00:08, 1968.20frames/s] 89%|████████▊ | 108746/122847 [01:15<00:07, 1978.14frames/s] 91%|█████████ | 111678/122847 [01:17<00:05, 1913.71frames/s] 93%|█████████▎| 114550/122847 [01:19<00:04, 1841.69frames/s] 96%|█████████▌| 117530/122847 [01:20<00:02, 1834.72frames/s] 98%|█████████▊| 120530/122847 [01:22<00:01, 1768.41frames/s]100%|██████████| 122847/122847 [01:23<00:00, 1826.12frames/s]100%|██████████| 122847/122847 [01:23<00:00, 1465.03frames/s]
  [23:53:55] 전사 완료 — 387 세그먼트, 언어=en
  [23:53:55] 화자 분리 중 (pyannote, MPS 가속)...
  [23:54:30] 화자 분리 완료 — 110 발화 구간
  [23:54:30] 세그먼트 필터링 — empty/noise 52, duplicate 0 제거 (387 → 335)
  [23:54:30] MLX 전사 완료 — 335 세그먼트, 3 화자
  transcribe 시간: 121.4s
  segments: 335
  language: en
  engine: mlx
  화자 분포: {'A': 149, 'B': 91, 'C': 95}

[3/3] translate_transcript (2-pass + 화자 코드 부착)…
  [23:54:32] 🌐 LLM 번역 시작 — 23 청크 (openai_compatible/qwen3.6-35b-q5)
  [23:54:32] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [23:54:32]    📚 entity cache bootstrap — 36건 사전 추출
  [23:54:32]    🎤 speaker cache bootstrap — 3명 식별
  [23:54:32]    ↳ 청크 1/23 번역 중…
  [23:54:32]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:54:35]    📝 2-pass 1단계 출력 — 15 lines / N=15, empty lines: 0
  [23:54:35]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:54:40]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:54:41]    ↳ 청크 2/23 번역 중…
  [23:54:41]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:54:45]    📝 2-pass 1단계 출력 — 13 lines / N=15, empty lines: 0
  [23:54:45]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:54:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:54:50]    ↳ 청크 3/23 번역 중…
  [23:54:50]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:54:54]    📝 2-pass 1단계 출력 — 14 lines / N=15, empty lines: 0
  [23:54:54]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:54:59]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [23:55:28]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:55:29]    ↳ 청크 4/23 번역 중…
  [23:55:29]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:55:32]    📝 2-pass 1단계 출력 — 14 lines / N=15, empty lines: 0
  [23:55:32]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:55:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:55:34]    ⚠ 2-pass 연속 동일 output 5건 catch — 정상 반복 가능성
  [23:55:35]    ↳ 청크 5/23 번역 중…
  [23:55:35]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:55:37]    📝 2-pass 1단계 출력 — 15 lines / N=15, empty lines: 0
  [23:55:37]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:55:40]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:55:40]    ⚠ 2-pass 연속 동일 output 14건 catch — 정상 반복 가능성
  [23:55:41]    ↳ 청크 6/23 번역 중…
  [23:55:41]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:55:44]    📝 2-pass 1단계 출력 — 15 lines / N=15, empty lines: 0
  [23:55:44]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:55:49]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:55:50]    ↳ 청크 7/23 번역 중…
  [23:55:50]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:55:55]    📝 2-pass 1단계 출력 — 13 lines / N=15, empty lines: 0
  [23:55:55]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:56:00]    ⚠ 빈 output 2건 catch (idx=[13, 14], retry 1/3)
  [23:56:00]    ↳ 빈 output retry — json_object mode 전환
  [23:56:31]    ⚠ 빈 output 1건 catch (idx=[14], retry 2/3)
  [23:57:05]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:05]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [23:57:06]    ↳ 청크 8/23 번역 중…
  [23:57:06]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:57:09]    📝 2-pass 1단계 출력 — 15 lines / N=15, empty lines: 0
  [23:57:09]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:57:13]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:14]    ↳ 청크 9/23 번역 중…
  [23:57:14]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:57:18]    📝 2-pass 1단계 출력 — 15 lines / N=15, empty lines: 0
  [23:57:18]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:57:22]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:23]    ↳ 청크 10/23 번역 중…
  [23:57:23]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:57:27]    📝 2-pass 1단계 출력 — 15 lines / N=15, empty lines: 0
  [23:57:27]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:57:32]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:33]    ↳ 청크 11/23 번역 중…
  [23:57:33]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:57:36]    📝 2-pass 1단계 출력 — 11 lines / N=15, empty lines: 0
  [23:57:36]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:57:41]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [23:57:45]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:46]    ↳ 청크 12/23 번역 중…
  [23:57:46]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:57:50]    📝 2-pass 1단계 출력 — 1 lines / N=15, empty lines: 0
  [23:57:50]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:57:55]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:57:56]    ↳ 청크 13/23 번역 중…
  [23:57:56]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:58:00]    📝 2-pass 1단계 출력 — 13 lines / N=15, empty lines: 0
  [23:58:00]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:58:04]    ⚠ 길이 미스매치: 12 != 15 (retry 1/3, finish_reason=stop)
  [23:58:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:58:27]    ↳ 청크 14/23 번역 중…
  [23:58:27]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:58:30]    📝 2-pass 1단계 출력 — 15 lines / N=15, empty lines: 0
  [23:58:30]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:58:35]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:58:36]    ↳ 청크 15/23 번역 중…
  [23:58:36]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:58:40]    📝 2-pass 1단계 출력 — 13 lines / N=15, empty lines: 0
  [23:58:40]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:58:45]    ⚠ 길이 미스매치: 13 != 15 (retry 1/3, finish_reason=stop)
  [23:59:07]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:59:08]    ↳ 청크 16/23 번역 중…
  [23:59:08]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:59:13]    📝 2-pass 1단계 출력 — 1 lines / N=15, empty lines: 0
  [23:59:13]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:59:18]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:59:19]    ↳ 청크 17/23 번역 중…
  [23:59:19]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [23:59:24]    📝 2-pass 1단계 출력 — 14 lines / N=15, empty lines: 0
  [23:59:24]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [23:59:29]    ⚠ 길이 미스매치: 14 != 15 (retry 1/3, finish_reason=stop)
  [23:59:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [23:59:58]    ↳ 청크 18/23 번역 중…
  [23:59:58]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [00:00:02]    📝 2-pass 1단계 출력 — 1 lines / N=15, empty lines: 0
  [00:00:02]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [00:00:07]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:00:08]    ↳ 청크 19/23 번역 중…
  [00:00:08]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [00:00:11]    📝 2-pass 1단계 출력 — 14 lines / N=15, empty lines: 0
  [00:00:11]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [00:00:15]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:00:16]    ↳ 청크 20/23 번역 중…
  [00:00:16]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [00:00:19]    📝 2-pass 1단계 출력 — 15 lines / N=15, empty lines: 0
  [00:00:19]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [00:00:24]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:00:25]    ↳ 청크 21/23 번역 중…
  [00:00:25]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [00:00:28]    📝 2-pass 1단계 출력 — 1 lines / N=15, empty lines: 0
  [00:00:28]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [00:00:32]    ⚠ 길이 미스매치: 11 != 15 (retry 1/3, finish_reason=stop)
  [00:00:36]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:00:36]    ⚠ 2-pass 연속 동일 output 1건 catch — 정상 반복 가능성
  [00:00:37]    ↳ 청크 22/23 번역 중…
  [00:00:37]    ↳ 2-pass 1단계: 자유 번역 (15 segments)
  [00:00:40]    📝 2-pass 1단계 출력 — 15 lines / N=15, empty lines: 0
  [00:00:40]    ↳ 2-pass 2단계: 정렬 (15 outputs schema strict)
  [00:00:44]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [00:00:45]    ↳ 청크 23/23 번역 중…
  [00:00:45]    ↳ 2-pass 1단계: 자유 번역 (5 segments)
  [00:00:49]    📝 2-pass 1단계 출력 — 5 lines / N=5, empty lines: 0
  [00:00:49]    ↳ 2-pass 2단계: 정렬 (5 outputs schema strict)
  [00:00:52]    ✅ Index Mapping 정합 — 5 outputs (finish_reason=stop)
  [00:00:52] ✅ 번역 완료
  [00:00:52]    💾 entity cache 저장: 36건 / speakers 3명 → oE5lNDhz9oo
  [00:00:52]    🔧 Phase 3 후처리 — Sub-A 0건, Sub-B 0건, Sub-C fallback 0건
  [00:02:24]    ⚠ canonicalize LLM 실패 (원본 유지): LLM 호출 wall-clock timeout — 90.0초 초과 (B02)
  translate 시간: 473.6s
  result 본문 길이: 16044 chars

결과 저장: /Users/gesicht/GuruNote/verify_results/community1_3speakers_body.md
segments dump: /Users/gesicht/GuruNote/verify_results/community1_3speakers_segments.json
