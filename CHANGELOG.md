# Changelog

이 프로젝트의 주요 변경 사항은 이 파일에 기록됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 를 따르며,
버전은 [Semantic Versioning](https://semver.org/lang/ko/) 을 따릅니다.

## [Unreleased]

### Added
- **CustomTkinter 데스크톱 GUI** (`gui.py`) — 브라우저 없이 네이티브 창으로
  GuruNote 파이프라인(Step 1~5) 실행. 백그라운드 스레드 + Queue 기반 비동기
  처리로 UI 블로킹 없음. 탭뷰(요약/번역/원문), 실시간 로그 패널, 네이티브
  파일 저장 대화상자 제공. `pyinstaller --windowed --onefile gui.py` 로
  `.app` / `.exe` 패키징 가능.
- **GUI 설정 다이얼로그** — 헤더의 ⚙️ 버튼으로 모달 창 오픈. OpenAI /
  Anthropic / AssemblyAI API 키와 모델명을 앱 안에서 입력·저장. 비밀번호
  마스킹(•) + 👁 토글, `dotenv.set_key()` 로 `.env` 에 영속 + `os.environ`
  즉시 반영. 파이프라인 실행 전 API 키 미설정 시 설정 화면으로 안내.
- **로컬 동영상/오디오 파일 지원** — 유튜브 URL 외에 로컬 미디어 파일
  (mp4/mkv/avi/mov/webm + mp3/wav/flac/m4a 등 17종)을 직접 입력 소스로
  사용 가능. `extract_audio_from_file()` 이 ffmpeg subprocess 로 mp3 변환
  수행, ffprobe 로 정확한 길이 취득.
  - Streamlit: 탭 UI 로 "🔗 유튜브 URL" / "📁 로컬 파일" 전환 + `st.file_uploader`
  - CustomTkinter: 📁 버튼으로 OS 네이티브 파일 대화상자, 자동 모드 감지

### Changed
- **README 대폭 보강** — Gemini 리뷰 반영
  - GPU VRAM 요구사항 구체화 (최소 16GB VRAM / Apple Silicon 32GB+)
  - OS 별 ffmpeg 설치 명령어 (Mac/Windows/Ubuntu)
  - 60 분 초과 팟캐스트 Edge Case 처리 방식 안내 (v0.1.0 제한 및 AssemblyAI 대안)
  - 최초 실행 시 모델 다운로드 시간(14GB) 경고

### Fixed
- **LLM Rate Limit 방어** (`llm.py`) — `_call_llm` 에 지수 백오프(2s→4s→8s→16s)
  재시도 로직 추가, 청크 번역 사이 1초 쿨다운 삽입으로 분당 요청 제한 회피
- **VRAM 메모리 누수 방지** (`stt.py`) — VibeVoice 추론 완료 후 GPU 텐서 삭제
  (`del inputs, output_ids`) + `torch.cuda.empty_cache()` 호출

## [0.1.0] - 2026-04-11

초판. Step 1~5 의 전체 파이프라인이 한 번의 버튼 클릭으로 동작합니다.

### Added
- **Step 1 — 오디오 추출** (`gurunote/audio.py`)
  - `yt-dlp` 로 유튜브 URL → mp3 다운로드
  - 영상 메타데이터(제목, 채널, 길이, URL) 수집
  - 임시 작업 폴더 자동 생성/정리 헬퍼
- **Step 2 — STT + 화자 분리** (`gurunote/stt.py`)
  - **Microsoft VibeVoice-ASR** (오픈소스, MIT) 을 기본 엔진으로 채택
  - 60 분 장편 오디오를 단일 패스로 처리, 화자/타임스탬프/내용 동시 추출
  - CUDA / MPS / CPU 자동 디바이스 감지, `flash_attention_2` 자동 활성화
  - 모델 싱글톤 lazy-load 로 연속 요청 시 재로딩 비용 제거
  - **IT/AI 도메인 핫워드 64 개** (Sam Altman, Lex Fridman, RLHF,
    Mixture of Experts 등) 를 VibeVoice 프로세서의 `context_info` 로 주입
  - VibeVoice 로딩 실패 시 **AssemblyAI Cloud API** 로 자동 폴백
  - 두 엔진 결과를 공통 `Transcript` 데이터클래스로 정규화
- **Step 3 — 한국어 번역** (`gurunote/llm.py`)
  - OpenAI (`gpt-4o`) / Anthropic (`claude-3-5-sonnet-latest`) 지원
  - "GuruNote 수석 에디터" 페르소나, 화자 실명 추론, 영문 병기, 구어체 정리
  - **청크 분할 번역** (`DEFAULT_CHUNK_CHAR_LIMIT=12_000`,
    `TRANSLATION_MAX_TOKENS=8192`) 으로 장편 영상 토큰 한도 초과 및 mid-script
    truncation 방지
  - 화자 라벨 + 타임스탬프 보존
- **Step 4 — GuruNote 스타일 요약본 생성** (`gurunote/llm.py`)
  - 📌 영상 제목 및 핵심 주제 요약 / 💡 Guru's Insights / ⏱️ 타임라인 구조 강제
  - 본문이 길 경우 부분 요약 → 통합 요약 2 단계 파이프라인
- **Step 5 — 마크다운 조립 + 내보내기** (`gurunote/exporter.py` · `app.py`)
  - 헤더(영상 메타) / 요약 / 전체 번역 / 영어 원문 섹션 조립
  - `GuruNote_<영상제목>.md` 다운로드 버튼
  - 작업 종료 후 임시 오디오 폴더 자동 정리
- **Streamlit UI** (`app.py`)
  - 헤더 `GuruNote 🎙️: 글로벌 IT/AI 구루들의 인사이트`
  - 사이드바에서 STT 엔진 (`auto` / `vibevoice` / `assemblyai`) 과 LLM provider
    (`openai` / `anthropic`) 를 런타임에 선택
  - `st.status` 로 단계별 진행 상황 스트리밍
  - 결과 탭: 📌 GuruNote 요약본 / 🇰🇷 전체 번역 스크립트 / 🇺🇸 영어 원문

### Fixed
- **VibeVoice 핫워드가 전달되지 않던 문제** — `transcribe()` 가 받은
  `hotwords` 인자를 VibeVoice 프로세서의 `context_info` 로 실제 주입하도록 수정.
  (이전에는 선언만 있고 실효 없음)
- **긴 청크에서 한국어 번역이 중간에 잘리던 문제** — 청크 입력 한도를
  24,000 → 12,000 chars 로 축소하고 `max_tokens` 을 4096 → 8192 로 확대.
- **Streamlit 동시 세션에서 LLM provider race condition** — 사이드바 선택을
  `os.environ` 에 쓰던 로직을 제거하고 `LLMConfig.from_env(provider=...)`
  override 로 request-local 하게 주입.

[Unreleased]: https://github.com/avlp12/GuruNote/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/avlp12/GuruNote/releases/tag/v0.1.0
