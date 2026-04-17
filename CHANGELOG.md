# Changelog

이 프로젝트의 주요 변경 사항은 이 파일에 기록됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 를 따르며,
버전은 [Semantic Versioning](https://semver.org/lang/ko/) 을 따릅니다.

## [Unreleased]

## [0.6.0.7] - 2026-04-17

> "지식 증류기" 로드맵 **Phase C — 깔끔한 PDF 출력**.

### Added
- **결과 마크다운 → 렌더링된 PDF 변환** (`gurunote/pdf_export.py` 신규,
  `requirements-pdf.txt` 신규) — `markdown` (pure Python) 으로 MD → HTML,
  `weasyprint` 로 HTML → PDF. YAML frontmatter 를 자체 파서로 추출해 PDF 첫
  페이지 메타 테이블 (업로더/게시일/원본 URL/분야/STT 엔진/태그 pill) 로
  렌더링. 본문은 A4 페이지에 한국어 친화 폰트 스택 (Noto Sans KR → Apple SD
  Gothic Neo → 맑은 고딕 → Pretendard → system-ui) 으로 출력. 페이지 하단
  `N / M` 페이지 번호, 블록쿼트/코드블록/테이블/수평선 스타일 포함.
- **GUI "Save PDF" 버튼** (`gui.py`) — 결과 카드 우상단에 `.md` 옆에 추가,
  HistoryDialog 의 각 카드에도 `.md` / **PDF** 버튼 병치. weasyprint 미설치
  시 OS 별 시스템 의존성 (macOS: `brew install cairo pango gdk-pixbuf libffi`
  / Ubuntu: `apt install libpango-1.0-0 libpangoft2-1.0-0`) + `pip install
  -r requirements-pdf.txt` 명령을 담은 친절한 안내 다이얼로그 표시.
- **선택 설치 의존성 분리** — `requirements-pdf.txt` 신설. 기본 `.md` 저장은
  이 패키지 없이도 동작하므로 PDF 가 필요한 사용자만 설치.

### Fixed
- **Settings 연결 테스트에서 Gemini 분기 누락** (`gui.py::_on_test_connection`)
  — 이전에는 `anthropic` 외의 모든 provider 가 `else` 분기로 빠져 OPENAI_*
  키를 사용했기 때문에 `gemini` 를 선택한 사용자의 "Test" 버튼이 항상 실패.
  `elif provider == "gemini"` 분기 추가 (`GOOGLE_API_KEY` + `GEMINI_MODEL`).
  PR #65 에서 도입된 드롭다운 선택지가 실제 동작과 정합되도록 수정.

## [0.6.0.6] - 2026-04-17

> "지식 증류기" 로드맵 **Phase B — History 일괄 뷰**.
> Phase A 에서 저장한 분류 메타데이터(제목/분야/태그) 를 실제 UI 에서 활용.

### Added
- **History 카드 그리드 뷰** (`gui.py::HistoryDialog`) — 기존 단순 세로 리스트
  를 3열 카드 그리드로 재구성. 각 카드는 YouTube 썸네일 (mqdefault 320x180) +
  정리된 제목 + 업로더/게시일 + 길이/엔진/화자수 + 분야 + 태그 + 상태/에러를
  한눈에 보여준다. 카드 하단에 Save .md / Log / Del 액션 버튼.
- **필터 바** — 검색창 (제목/업로더/태그 실시간 fuzzy), 분야 드롭다운
  (히스토리의 실제 분야 목록에서 자동 생성), 정렬 드롭다운 (최신순 / 오래된순 /
  길이 긴 순 / 길이 짧은 순 / 제목 A-Z), 필터 초기화 버튼. 필터 상태는
  다이얼로그가 살아있는 동안 유지.
- **YouTube 썸네일 캐시** (`gurunote/thumbnails.py` 신규) — 표준 YouTube URL
  패턴 5종 (watch?v= / youtu.be/ / embed/ / v/ / shorts/) 에서 11자리 비디오
  ID 추출. `~/.gurunote/thumbnails/<id>.jpg` 에 1회만 다운로드 후 캐시.
  `download_thumbnail_async()` 로 첫 그리드 렌더링을 차단하지 않음 —
  플레이스홀더 (⏳) 표시 후 완료 시 메인 스레드 `after()` 폴링으로 교체.
  YouTube 가 "영상 없음" placeholder 를 반환하는 경우 (&lt; 2KB) 를 실패로 간주.
- **썸네일 폴백 아이콘** — 로컬 파일 소스는 🎵, URL 없음 / YouTube 아님은 🎙️,
  다운로드 실패는 🎬 로 시각적으로 구분.

## [0.6.0.5] - 2026-04-17

### Added
- **GUI 실시간 백엔드 진행률** (`gurunote/progress_tee.py` 신규, `gui.py`,
  `app.py`) — HuggingFace 모델 다운로드 / mlx-whisper / whisperx 의 tqdm
  진행률이 이전에는 CLI stderr 에만 찍혀 GUI 로그 패널에서는 보이지 않았다.
  새 `install_tee()` 컨텍스트 매니저가 파이프라인 실행 동안 `sys.stderr` 를
  tee 로 감싸 원본에는 그대로 쓰면서, 한 줄 단위로 파싱해 압축된 요약을
  GUI 로그 콜백에 전달한다.

  감지 + 압축 패턴:
  - `39%|...| 239370/619235 [05:14<09:37, 657.42frames/s]`
    → `[STT] 39% (239370/619235) · 05:14 경과 · ~09:37 남음 · 657.42 frames/s`
  - `Fetching 4 files: 100%|...| 4/4 [00:44<00:00, 11.06s/it]`
    → `[모델] Fetching 4 files — 4/4 (100%) · 남음 ~00:00`
  - `Download complete: : 3.08GB [00:44, 255MB/s]`
    → `[모델] 다운로드 완료 (3.08GB, 00:44 · 255 MB/s)`
  - `Detected language: English` → `[언어] English 감지`
  - HF 토큰 미설정 경고는 1회만 표시 (중복 억제)
  - ANSI 컬러 escape 제거, 500ms 스로틀링으로 GUI 로그 flood 방지

  **Streamlit(`app.py`) 에는 적용하지 않음** — `st.empty()` 등 Streamlit
  위젯은 `ScriptRunContext` 가 바인딩된 메인 스레드에서만 안전하게 업데이트
  가능하고, 백엔드 워커(mlx-whisper, whisperx)가 stderr 로 tqdm 을 찍는
  스레드에서 위젯 업데이트 콜백이 호출되면 `MissingScriptRunContext` 경고가
  발생하며 최악의 경우 경고 메시지 자체가 tee 로 재유입되는 재귀 위험이
  있어서. Streamlit 은 Step 완료마다 `st.write` 로 표시되므로 실용상 충분.
  데스크톱 GUI 에만 tee 적용.

  **방어적 restore** — `install_tee` 종료 시 `sys.stderr is tee_err` 인 경우
  에만 원본 복원해서, nested 컨텍스트 엣지케이스에서 stderr 가 영구 오염되는
  footgun 방지.

## [0.6.0.4] - 2026-04-17

### Fixed
- **메타 추출 품질 이슈 2건** (`gurunote/llm.py`) — PR #68 코드 리뷰 후속:
  - `_parse_metadata_json` 의 태그 필터를 `isinstance(t, str)` 기반으로 강화.
    이전: `str(t).strip()` 이 `None`/`{}` 등을 `"None"`/`"{}"` 문자열로 저장해
    쓰레기 태그가 영속화될 가능성. 이후: 문자열만 통과, 나머지 드롭.
    `organized_title` / `field` 도 동일하게 `isinstance(str)` 가드 추가.
  - `extract_metadata` 의 하드코딩된 `max_tokens=512` 를 `max(1024,
    config.summary_max_tokens // 4)` 로 변경. 긴 한국어 제목/태그 조합에서
    응답이 잘려 빈 결과가 반환되는 경우 방지.

## [0.6.0.3] - 2026-04-17

> "지식 증류기" 로드맵 **Phase A — 메타데이터 자동 추출**.
> 이후 Phase B (History 일괄 뷰) / C (PDF 출력) / D (Obsidian) / E (Notion) /
> F (검색) 의 기반.

### Added
- **분류용 메타데이터 자동 추출** (`gurunote/llm.py::extract_metadata`) —
  파이프라인에 새 Step 4.5 단계 삽입. 번역된 한국어 스크립트 + YouTube 메타
  (제목/업로더/태그) 를 LLM 으로 보내 다음 3개를 JSON 으로 추출:
  - `organized_title` — 사람이 보기 쉬운 한국어 제목 (60자 이내, [화자]: [핵심 주제] 패턴)
  - `field` — 분야 분류 (예: "AI/ML", "AI 하드웨어", "스타트업", "철학")
  - `tags` — 정확히 5개 키워드 (YouTube 원본 태그 우선 활용 + 본문 보완)
  실패 시 빈 dict 반환하여 파이프라인 진행 방해 안 함. JSON 파싱은 코드블록
  래핑 / 앞뒤 텍스트 모두 허용.
- **`gurunote/history.py::save_job` 스키마 확장** — `organized_title`, `field`,
  `tags`, `uploader`, `upload_date` 5개 필드 추가. `~/.gurunote/history.json`
  인덱스에 누적되어 향후 Phase B (필터/검색) 에서 활용.
- **Obsidian / Notion 호환 YAML frontmatter** (`gurunote/exporter.py`) —
  결과 마크다운 최상단에 frontmatter 자동 삽입:
  - `title`, `original_title`, `uploader`, `upload_date`, `source_url`
  - `field`, `tags` (Obsidian 태그 시스템 호환 — 공백→`_`, `#` prefix 제거)
  - `stt_engine`, `duration_sec`, `num_speakers`, `created`
  Obsidian vault 또는 Notion import 에 그대로 사용 가능.
- **마크다운 헤더 강화** (`gurunote/exporter.py`) — 제목을 `organized_title`
  로 표시, 원본 제목과 다르면 `원본 제목:` 라인 추가, `분야:` / `태그:` (인라인
  `#tag` 표시) 항목 표시.

### Changed
- **파이프라인 진행률 재배분** (`gui.py`, `app.py`) — Step 4 88% → Step 4.5
  92% → Step 5 100% 로 새 단계 반영.

## [0.6.0.2] - 2026-04-17

### Fixed
- **macOS 입력창에서 Cmd+C/V/X/A 미동작** (`gui.py`) — macOS 의 CTkEntry /
  CTkTextbox 에서 `Cmd+V` 로 붙여넣기가 되지 않던 문제 (Settings, 오디오 URL
  입력 등 모든 입력창). Tkinter 기본 바인딩이 Linux/Windows 의 `Ctrl+V` 는
  `<<Paste>>` 가상 이벤트로 매핑하지만 일부 Tcl/Tk 빌드에서 macOS 의 `Command`
  키 누락. 루트 윈도우에 `_install_clipboard_shortcuts()` 를 통해 `bind_all`
  로 `<Command-c/v/x/a>` (대소문자 모두) 를 명시 바인딩 → 포커스된 위젯에
  `<<Copy>>` / `<<Paste>>` / `<<Cut>>` / `<<SelectAll>>` 가상 이벤트를
  전파하도록 수정. `Toplevel` (SettingsDialog, HistoryDialog 등) 도 같은
  Tk 인터프리터를 공유하므로 한 번의 `bind_all` 로 전역 적용.
  Linux/Windows 는 no-op (기본 바인딩이 이미 Ctrl+V 처리).

## [0.6.0.1] - 2026-04-17

> v0.6.0 이후 머지된 UX/버그 수정 PR (#59~#66) 을 REVISION 단위로 묶은 릴리스.
> 앱 내장 업데이트 체크가 이 변경들을 감지할 수 있도록 `X.Y.Z.W` 4자리 버전
> 정책을 신규 도입 (`CLAUDE.md`). 이후 모든 코드 변경 PR 은 REVISION (`W`) 자리를
> +1 로 올린다.

### Added
- **4자리 버전 정책 `MAJOR.MINOR.PATCH.REVISION`** (`CLAUDE.md`) — 모든 코드
  변경 PR 마다 REVISION (`W`) 자리를 +1. `gurunote/updater.py` 의 업데이트 체크
  (`local == remote` 문자열 비교) 가 매 PR 의 변경을 감지 가능하도록 하는 목적.
  PEP 440 `N.N.N.N` 호환. 상위 자리 변경 시 하위는 0 리셋.
- **하드웨어 프리셋 자동 감지** (`gurunote/hardware.py` 신규) —
  NVIDIA GPU VRAM (`torch.cuda.get_device_properties`) 와 Apple Silicon
  Unified Memory (`sysctl hw.memsize`) 를 감지해 8개 프리셋 중 가장 적합한
  것을 추천 (NVIDIA 24/12/8/6GB · Apple Silicon Ultra/Pro-Max/base · Cloud only).
  각 프리셋이 WhisperX 모델/배치 크기, MLX 모델, LLM Temperature, 번역/요약
  Max Tokens 를 권장값으로 묶어 제공.
- **Settings 다이얼로그 하드웨어 프리셋 드롭다운** (`gui.py`) — 상단에 "하드웨어
  프리셋" 드롭다운 추가. 선택 시 STT/LLM 필드 일괄 자동 채움. "자동 감지 (권장)"
  또는 "직접 입력 (custom)" 옵션 지원. 현재 환경 감지 결과를 드롭다운 옆
  라벨에 표시 (예: "Apple Silicon 감지됨 (Unified Memory ~128GB)"). 개별 필드는
  드롭다운 이후에도 수동 override 가능.
- **MLX Whisper 모델 설정 필드** (`gui.py`) — Apple Silicon 사용자를 위한
  `MLX_WHISPER_MODEL` 환경변수를 Settings 다이얼로그에 추가. 기본값
  `mlx-community/whisper-large-v3-mlx`.
- **실행 래퍼 스크립트** — `run_desktop.sh` / `run_web.sh` (macOS/Linux) +
  `run_desktop.bat` / `run_web.bat` (Windows). `.venv` 를 activate 없이 직접
  호출해 macOS 의 `command not found: python` / `streamlit` 문제를 근본 차단.
  `.venv` 미존재 시 친절한 에러 메시지로 `setup.sh` 실행 안내. setup.sh/bat
  의 최종 메시지도 래퍼 스크립트를 1순위로 안내하도록 갱신.
- **README "🗑️ 제거" 섹션** — 프로젝트 폴더 / `~/.gurunote/` / HuggingFace
  모델 캐시의 OS 별 삭제 명령과 경로별 용량 요약. `.env` API 키 백업/폐기
  보안 안내, 공유 HuggingFace 캐시 조심 경고, 임시 파일 정책 설명 포함.
- **README Troubleshooting FAQ** — macOS 에서 `python` / `streamlit` 명령을
  찾지 못하는 상황과 해결법 명시. "▶️ 실행" 섹션에 래퍼 스크립트 + venv
  activate 대안을 모두 제시.

### Changed
- **Settings 다이얼로그 LLM Provider 드롭다운화** (`gui.py`) — 이전엔 자유
  텍스트 입력이었던 "LLM Provider" 를 CTkOptionMenu 로 변경해 오타/오설정을
  방지. 선택지: `openai` / `anthropic` / `gemini` / `openai_compatible`.
  `_entries` 딕셔너리가 CTkEntry 와 CTkOptionMenu(StringVar) 를 혼재하여 보관
  하도록 타입 확장 (`.get()` 인터페이스 통일).
- **데스크톱 배포 패키지 OS별 분리 + CI 의존성 정합성 수정**
  (`.github/workflows/release-desktop.yml`, `scripts/package_desktop.py`,
  `README.md`) — Release 아티팩트 이름에 플랫폼 suffix 추가
  (`GuruNote-Windows.exe`, `GuruNote-Windows-Installer.exe`,
  `GuruNote-macOS.dmg`, `GuruNote-macOS.pkg`). CI 의 hardcoded pip 리스트를
  `pip install -r requirements.txt` 로 교체해 v0.5.0 추가된 `google-genai`
  누락 문제 해결 (Gemini 선택 시 ImportError 방지). README 에 "데스크톱 패키지
  vs 소스 실행" 비교 표 추가 — 번들 패키지는 UI + 클라우드 STT(AssemblyAI)
  전용, 로컬 GPU STT(WhisperX/MLX) 가 필요하면 소스 실행 안내.

### Fixed
- **ffmpeg/ffprobe 누락 감지 + 친절한 에러** (`gurunote/audio.py`,
  `setup.sh`, `setup.bat`) — yt-dlp 오디오 추출에 ffmpeg 가 필요하지만 macOS 기본
  환경엔 없어 Step 1 에서 `ERROR: Postprocessing: ffprobe and ffmpeg not found`
  (ANSI 컬러 escape 포함) 로 파이프라인이 실패. 새 `ensure_ffmpeg_available()`
  pre-flight 가 `download_audio()` / `extract_audio_from_file()` 시작부에서
  `shutil.which` 로 감지 → 누락 시 OS 별 설치 명령 (`brew install ffmpeg` /
  `winget install ffmpeg` / `apt install ffmpeg`) 을 포함한 한국어 RuntimeError
  발생. setup.sh / setup.bat 에도 같은 감지 단계(`[0/4]`)를 추가해 setup 단계에서
  자동 설치 제안(brew/winget 감지 시) 또는 명확한 실패 메시지 출력.
- **Apple Silicon 세대 표기 M5 반영** — README / `requirements-mac.txt` / `stt.py`
  / `stt_mlx.py` 의 "M1/M2/M3/M4", "M1~M4" 표기 9곳을 M5 포함으로 갱신. 실제
  코드는 `platform.machine() == "arm64"` 로 세대 무관 동작하나 문서 표기는
  최신 세대 반영이 맞음.
- **README "🚀 설치" 모순 제거** — "빠른 시작" 은 `bash setup.sh` 바로 실행을
  안내하는데 "🚀 설치" 는 `python -m venv .venv && source .venv/bin/activate`
  수동 단계를 추가로 요구해 모순됐고, macOS 의 `python` 명령 부재로 이 수동
  단계가 실제로 실패하는 원인이 됨. setup.sh 가 이미 `.venv` 를 자체 생성하므로
  "🚀 설치" 섹션에서 수동 venv 단계를 제거하고, 대신 setup 스크립트가 자동
  수행하는 5단계 (venv 생성 → 플랫폼 감지 → 공통 의존성 → 플랫폼별 STT → 검증)
  를 명시적으로 문서화.
- **업데이트 다이얼로그 NameError** (`gui.py`) — `SettingsDialog._on_update` 가
  import 되지 않은 `check_updates(...)` 를 호출해 NameError 발생. 다른 위치
  (`_on_update_sb`) 와 동일하게 `check_for_update()` 호출 후 `info["message"]`
  사용하도록 수정. 사이드바 ⚙️ 설정 다이얼로그에서 "업데이트 확인" 버튼이 정상
  동작.
- **README VibeVoice 잔재 정리** — STT 섹션, 파이프라인 다이어그램, 60분 제한
  안내, GPU/VRAM 요구사항 표, 환경변수 예시, 사용 흐름, 최초 실행 안내, 프로젝트
  구조, FAQ 4개 항목 등 ~15곳을 현재 코드 (WhisperX + MLX + AssemblyAI 라우터)
  와 일치시킴. v0.4.x 의 WhisperX 전환 + v0.6.0 의 MLX 추가가 README 에 누락돼
  있던 부분을 일괄 갱신.

## [0.6.0] - 2026-04-16

### Added
- **macOS Apple Silicon 로컬 GPU STT** (`gurunote/stt_mlx.py`) — `mlx-whisper` 로
  Whisper 추론을 Apple GPU/Neural Engine 에서 native 실행, `pyannote.audio` 화자
  분리를 MPS 디바이스에서 수행. 단어 레벨 타임스탬프, IT/AI 핫워드 `initial_prompt`
  주입, SPEAKER_NN→A/B/C 오버랩 기반 화자 할당. `engine="mlx"` 로 명시 선택 또는
  `auto` 라우팅에서 자동 선택. `HUGGINGFACE_TOKEN` 미설정 시 단일 화자(A) 폴백.
  `MLX_WHISPER_MODEL` / `PYANNOTE_DIARIZATION_MODEL` 환경변수로 모델 오버라이드.
- **STT `auto` 라우팅 확장** (`gurunote/stt.py`) — 우선순위:
  CUDA WhisperX → Apple Silicon MLX → AssemblyAI Cloud. Apple Silicon 인데
  mlx-whisper 미설치 시 안내 메시지 (`pip install -r requirements-mac.txt`).
- **GUI / Streamlit STT 엔진 선택지에 `mlx` 추가** (`gui.py`, `app.py`) —
  드롭다운에 노출, help 텍스트 갱신. macOS arm64 + `auto` 또는 `mlx` 선택 시
  WhisperX 설치 강요 다이얼로그 우회.
- **플랫폼별 의존성 분리** — `requirements.txt` 는 공통 의존성만 유지,
  `requirements-mac.txt` (mlx-whisper, pyannote.audio, onnxruntime) 와
  `requirements-gpu.txt` (whisperx) 신설. `setup.sh` 가 `uname -s/-m` 으로
  Darwin arm64 를 감지해 MLX 스택을 자동 설치, `setup.bat` 는 NVIDIA 감지 시에만
  `requirements-gpu.txt` 추가 설치. 검증 단계가 MPS 가용성도 함께 출력.
- **README** — 빠른 시작에 `bash setup.sh` 안내, Apple Silicon FAQ 항목,
  기술 스택 표에 mlx-whisper + pyannote.audio 명시.

## [0.5.0] - 2026-04-16

### Added
- **Google Gemini API 지원** (`gurunote/llm.py`) — `LLM_PROVIDER=gemini` 으로
  Google Gemini 모델 사용 가능. `GOOGLE_API_KEY`, `GEMINI_MODEL` 환경변수 추가.
  `google-genai>=1.0` 의존성 추가. GUI/Streamlit Settings 에 Gemini 옵션 반영.

### Fixed
- **업데이트 체크 원격 버전 감지 실패 수정** (`gurunote/updater.py`) — remote 이름과
  기본 브랜치를 자동 감지(`_detect_remote_and_branch`)하여 `origin/main` 이 아닌
  환경에서도 동작. `git ls-remote` 폴백 추가. 실패 시 네트워크/remote 설정 안내 메시지.

## [0.4.1] - 2026-04-16

### Fixed
- WhisperX `DiarizationPipeline` API 변경 대응 (v3.8.5+: `whisperx.diarize.DiarizationPipeline`)
- AssemblyAI `speech_model` → `speech_models` (복수형 리스트) API 변경
- Windows symlink 없이 모델 다운로드 (`~/.gurunote/models/`)
- WhisperX `initial_prompt` → `load_model(asr_options=)` 로 이동
- setup.bat CUDA torch 버전 핀 (`torch==2.8.0+cu128`, whisperx 호환)
- GPU 미감지 시 CPU whisperx 거부 → AssemblyAI 직행
- 경고 억제 확대 (torchcodec, pyannote, huggingface_hub)

### Added
- 버전 비교 기반 업데이트 체크 (local vs remote `__version__` 비교)
- 업데이트 진행 다이얼로그 (백그라운드 스레드 + 실시간 로그)
- Semantic Versioning 정책 (`CLAUDE.md`)

### Changed
- STT 엔진: VibeVoice-ASR → **WhisperX** (Distil-Whisper + pyannote)
- setup.bat/sh: CUDA torch 먼저 설치 → whisperx "already satisfied"

## [0.4.0] - 2026-04-16

### Added
- **작업 히스토리** (`gurunote/history.py`) — 완료/실패 작업이 `~/.gurunote/jobs/`
  에 자동 저장. 마크다운 재다운로드, 파이프라인 로그 확인, 에러 진단 가능.
  데스크톱 History 다이얼로그 + Streamlit 히스토리 탭.
- **영속 파이프라인 로그** — 모든 `_log()` 호출이 `pipeline.log` 파일에 타임스탬프와
  함께 기록되어 실패 원인을 사후 분석 가능.
- **로그 타임스탬프** — `[HH:MM:SS]` prefix 자동 추가.
- **진행 바 ETA** — 경과 시간 + 남은 예상 시간 계산 표시.
- **4-bit/8-bit 자동 양자화** — VRAM 기반 자동 선택 (48GB+→bf16, 24GB+→8bit,
  기타→4bit NF4). `VIBEVOICE_QUANTIZATION` 환경변수로 오버라이드 가능.
- **CUDA OOM 방어** — 토큰 축소 재시도 (32768→16384→8192), 실패 시 모델 자동
  언로드 + GPU 메모리 반환.
- **VibeVoice 미설치 안내** — 설치/AssemblyAI 전환 선택 다이얼로그.

### Changed
- **GUI 텍스트 라벨 정비** — 이모지 → 텍스트 (Windows 렌더링 호환), 사이드바
  브랜드 잘림 수정 (200→220px, 세로 배치).
- **Windows 경고 억제** — `expandable_segments` 미지원 경고 + 무해한 토크나이저/
  preprocessor 경고를 `warnings.filterwarnings` 로 억제.

## [0.2.0] - 2026-04-16

### Added
- **유튜브 메타데이터 컨텍스트 주입** (`gurunote/audio.py`, `llm.py`, `exporter.py`)
  - `yt-dlp` 호출 시 수동/자동 자막(VTT)까지 함께 다운로드
  - `AudioDownloadResult` 에 `upload_date`, `description`, `chapters`,
    `subtitles_text`, `subtitles_source`, `tags` 필드 추가
  - 설명에 챕터가 없어도 `"MM:SS 제목"` 패턴을 정규식으로 파싱해 자동 추출
  - 새 헬퍼 `build_video_context_block()` 가 영상 제목/채널/게시일/챕터/
    자막 발췌를 `"### 영상 컨텍스트"` 블록으로 조립해 LLM user 메시지에 주입
  - 번역/요약 시스템 프롬프트가 컨텍스트를 활용하도록 규칙 추가
    (화자 이름 추론, 공식 챕터를 타임라인 뼈대로 사용)
  - `build_gurunote_markdown()` 이 게시일을 헤더에, 챕터를 새 `⏱️ 원본
    영상 챕터` 섹션으로 렌더링
  - Streamlit / CustomTkinter UI 가 게시일·챕터·자막 감지 결과를 진행
    로그에 표시
- **로컬 LLM(OpenAI-compatible) 지원 강화** (`gurunote/llm.py`)
  - `LLM_PROVIDER=openai_compatible` 추가
  - `OPENAI_BASE_URL` 지원으로 로컬/사설 OpenAI-compatible 엔드포인트 사용 가능
  - Temperature / 번역·요약 Max Tokens 환경변수(`LLM_TEMPERATURE`,
    `LLM_TRANSLATION_MAX_TOKENS`, `LLM_SUMMARY_MAX_TOKENS`) 반영
- **앱 내 Settings UX 확장**
  - Streamlit: 별도 `⚙️ Settings` 탭 추가 (`app.py`)
  - Desktop GUI: 설정 다이얼로그에 LLM Provider, Base URL, 고급 옵션,
    연결 테스트 버튼 추가 (`gui.py`)
  - 저장 시 `.env` 자동 백업 + 즉시 적용 (`gurunote/settings.py`)
- **실행 진행률 UX 개선** (`app.py`, `gui.py`)
  - Streamlit 파이프라인 단계별 퍼센트 진행률 바 추가
  - Desktop GUI에 진행률 바(%) 및 `⏹ 중지` 버튼 추가
- **업데이트 UX 추가** (`gurunote/updater.py`, `scripts/update_gurunote.py`, `app.py`, `gui.py`)
  - 재설치 없이 `git pull + requirements 업그레이드`를 수행하는 업데이트 유틸 추가
  - Streamlit/GUI 설정 화면에 업데이트 확인·실행 버튼 추가
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
- **데스크톱 배포 패키징 스크립트** (`scripts/package_desktop.py`)
  - Windows: `dist/GuruNote.exe` (단일 실행 파일) 생성 자동화
  - Windows(선택): Inno Setup(ISCC) 감지 시 `dist/GuruNote-Installer.exe` 생성
  - macOS: `dist/GuruNote.app` 생성 + 옵션으로 `dist/GuruNote.dmg` /
    `dist/GuruNote.pkg` 생성 자동화
- **GitHub Actions 릴리스 워크플로우** (`.github/workflows/release-desktop.yml`)
  - `v*` 태그 푸시 시 Windows/macOS 패키지를 CI에서 자동 빌드
  - 생성물(`.exe`, 설치형 `.exe`, `.dmg`, `.pkg`)을 GitHub Release assets로 자동 업로드
- **태그 릴리스 리허설 체크 스크립트** (`scripts/release_rehearsal_check.py`)
  - 태그 형식, 워크플로우 핵심 항목, 필수 파일, 패키징 스크립트 스모크 테스트를
    릴리스 전 자동 점검
  - 실패 시 즉시 원인 출력 + 종료 코드 1 반환 (fail-fast)

- **GUI 전면 리디자인** (`gui.py`) — Clova Note 등 SaaS 도구를 참고.
  좌측 사이드바(브랜드 로고 + 설정/업데이트 네비게이션) + 메인 영역을
  입력 카드 → 진행 카드 → 결과 카드 3단 구조로 재편. 커스텀 브랜드 팔레트
  (네이비 `#1A1B2E`, 보라 CTA `#6C63FF`, 시안 진행바 `#22D3EE`), 5단계
  뱃지 인디케이터(dim→보라→초록), 로그를 결과 탭 안 📋 로그 탭으로 이동.

### Changed
- **LLM 기본 모델 최신화** — OpenAI `gpt-4o` → `gpt-5.4`, Anthropic
  `claude-3-5-sonnet-latest` → `claude-sonnet-4-6`. 코드 기본값(`llm.py` 의
  `openai`/`openai_compatible`/`anthropic` 3개 분기 모두), `.env.example`,
  Streamlit Settings 탭 placeholder, README, app.py 사이드바 텍스트 일괄 변경.
  기존 `.env` 에 `OPENAI_MODEL` / `ANTHROPIC_MODEL` 을 직접 설정한 사용자는
  영향 없음.
- **README 대폭 보강** — Gemini 리뷰 반영
  - GPU VRAM 요구사항 구체화 (최소 16GB VRAM / Apple Silicon 32GB+)
  - OS 별 ffmpeg 설치 명령어 (Mac/Windows/Ubuntu)
  - 60 분 초과 팟캐스트 Edge Case 처리 방식 안내 (v0.1.0 제한 및 AssemblyAI 대안)
  - 최초 실행 시 모델 다운로드 시간(14GB) 경고
  - Windows 설치형 exe / macOS dmg·pkg 배포 워크플로우 추가
  - 태그 기반 GitHub Actions 릴리스 자동화 안내 추가
  - 태그 릴리스 리허설 체크 스크립트 사용법 추가
- **긴 영상 STT 라우팅 보강** (`app.py`, `gui.py`) — 입력 오디오가 60분을
  넘고 STT 엔진이 `auto` 인 경우 AssemblyAI 로 자동 전환해 장편 콘텐츠의
  전사 누락 가능성을 기본 설정에서 완화.

### Fixed
- **LLM Rate Limit 방어** (`llm.py`) — `_call_llm` 에 지수 백오프(2s→4s→8s→16s)
  재시도 로직 추가, 청크 번역 사이 1초 쿨다운 삽입으로 분당 요청 제한 회피
- **VRAM 메모리 누수 방지** (`stt.py`) — VibeVoice 추론 완료 후 GPU 텐서 삭제
  (`del inputs, output_ids`) + `torch.cuda.empty_cache()` 호출
- **빈 전사 결과 조기 차단** (`stt.py`) — 세그먼트/텍스트가 비어 있으면 즉시
  예외를 발생시켜 후속 LLM 호출 낭비와 품질 저하를 방지.

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

[Unreleased]: https://github.com/avlp12/GuruNote/compare/v0.6.0.7...HEAD
[0.6.0.7]: https://github.com/avlp12/GuruNote/compare/v0.6.0.6...v0.6.0.7
[0.6.0.6]: https://github.com/avlp12/GuruNote/compare/v0.6.0.5...v0.6.0.6
[0.6.0.5]: https://github.com/avlp12/GuruNote/compare/v0.6.0.4...v0.6.0.5
[0.6.0.4]: https://github.com/avlp12/GuruNote/compare/v0.6.0.3...v0.6.0.4
[0.6.0.3]: https://github.com/avlp12/GuruNote/compare/v0.6.0.2...v0.6.0.3
[0.6.0.2]: https://github.com/avlp12/GuruNote/compare/v0.6.0.1...v0.6.0.2
[0.6.0.1]: https://github.com/avlp12/GuruNote/compare/v0.6.0...v0.6.0.1
[0.6.0]: https://github.com/avlp12/GuruNote/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/avlp12/GuruNote/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/avlp12/GuruNote/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/avlp12/GuruNote/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/avlp12/GuruNote/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/avlp12/GuruNote/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/avlp12/GuruNote/releases/tag/v0.1.0
