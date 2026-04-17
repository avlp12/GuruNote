# GuruNote 🎙️

> 유튜브 링크 한 줄로 해외 IT/AI 팟캐스트를 **화자 분리된 한국어 마크다운 요약본**으로.

```bash
$ python gui.py                    # 데스크톱 앱 실행
# 또는
$ streamlit run app.py             # 웹 앱 실행

# 실행 결과 (파이프라인 로그 — 타임스탬프 + ETA 포함):
[14:23:05] [Step 1] 유튜브 오디오 추출 중...
[14:23:18] [Step 1] OK: GPT-5 and the Future of AI (42.3 MB, 6150s)
[14:23:18]   > 게시일: 2025-09-15
[14:23:18]   > 공식 챕터 8개 감지
[14:23:20] [Step 2] 화자 분리 STT 중...             # 18%  |  0m 15s elapsed
[14:25:41] [Step 2] OK: 847 세그먼트, 2 화자        # 55%  |  2m 36s  |  ~2m left
[14:25:42] [Step 3] LLM 한국어 번역 중...
[14:27:10] [Step 3] OK: 번역 완료 (18,420 chars)    # 78%
[14:27:30] [Step 4] OK: 요약 완료                    # 90%
[14:27:32] [Step 5] OK: 마크다운 조립                # 100%
[14:27:32] [Done] GuruNote 생성 완료
[14:27:32] [Save] 히스토리에 저장됨
```

---

## 📦 선행 조건 (필수 사전 설치)

`setup.sh` / `setup.bat` 를 돌리기 **전에** 다음 3가지가 OS 에 설치돼 있어야
합니다. 하나라도 빠지면 첫 단계에서 `'git' 용어가 ... 인식되지 않습니다` /
`python: command not found` 같은 에러가 발생합니다.

| 도구 | 용도 | Windows | macOS | Linux (Debian/Ubuntu) |
|---|---|---|---|---|
| **Git** | 저장소 clone · 앱 내 업데이트 (`git pull`) | `winget install --id Git.Git -e` · [공식 다운로드](https://git-scm.com/download/win) | `brew install git` (또는 Xcode CLT 자동 설치) | `sudo apt install -y git` |
| **Python 3.10+** | GuruNote 런타임 | `winget install --id Python.Python.3.12 -e` · [python.org](https://www.python.org/downloads/windows/) | `brew install python@3.12` · [python.org](https://www.python.org/downloads/macos/) | `sudo apt install -y python3 python3-venv python3-pip` |
| **ffmpeg** | `yt-dlp` 오디오 추출 (Step 1) | `winget install --id Gyan.FFmpeg -e` · [공식 사이트](https://ffmpeg.org/download.html) | `brew install ffmpeg` · [Homebrew](https://brew.sh/) | `sudo apt install -y ffmpeg` |

> ⚠️ **Windows 사용자**: `winget` 으로 Git / Python 을 설치한 뒤에는 **PowerShell 창을
> 새로 열어야** `PATH` 가 갱신됩니다. 또한 Python 설치 시 "Add python.exe to PATH"
> 체크박스를 반드시 켜두세요 (설치 마법사 첫 화면).
>
> ⚠️ **Windows PowerShell 5.1 주의**: 기본 탑재된 PowerShell 5.1 은 유닉스식 명령
> 연결자 `&&` 를 지원하지 않습니다 (`'&&' 토큰은 이 버전에서 올바른 문 구분 기호가
> 아닙니다`). 아래 빠른 시작은 이를 피해 **한 줄에 하나씩** 실행하는 형태로
> 기술돼 있습니다. PowerShell 7+ (`winget install Microsoft.PowerShell`) 에서는
> `&&` 가 정상 동작합니다.

설치 확인 (버전이 표시되면 OK):

```bash
# Windows (PowerShell / cmd) · macOS · Linux 공통
git --version
python --version      # macOS 는 python3 --version
ffmpeg -version
```

---

## ⚡ 빠른 시작 (3단계)

```bash
# 1. 저장소 clone & 이동 (PowerShell 5.1 호환: && 를 쓰지 않고 한 줄씩)
git clone https://github.com/avlp12/GuruNote.git
cd GuruNote

# 2. 설치 (플랫폼 자동 감지 + STT 엔진 자동 설치 + .venv 자동 생성)
bash setup.sh        # macOS / Linux  (Windows 는 setup.bat)
# 자동 감지 + 설치:
#   - NVIDIA GPU (Linux/Windows) → CUDA PyTorch + WhisperX
#   - Apple Silicon Mac (M1~M5)  → MLX Whisper + pyannote (Metal/MPS GPU 가속)
#   - 그 외                       → AssemblyAI Cloud API 만 사용 가능

# 3. API 키 설정 (OpenAI / Anthropic / Google Gemini 중 하나)
cp .env.example .env
# .env 를 열어 OPENAI_API_KEY=sk-... 입력
# (Windows PowerShell 은 cp 대신 Copy-Item .env.example .env)

# 4. 실행 (venv activate 불필요 — 래퍼 스크립트가 .venv 의 Python/Streamlit 을 직접 호출)
bash run_desktop.sh      # 데스크톱 앱 (macOS/Linux)
bash run_web.sh          # 웹 앱   (macOS/Linux)
# Windows: run_desktop.bat / run_web.bat
```

> 💡 **macOS 주의**: macOS 12+ 는 `python` 명령이 없고 `python3` 만 있습니다.
> 또한 venv 를 activate 하지 않으면 `streamlit` 같은 venv 전용 명령은
> `command not found` 로 실패합니다. 위 래퍼 스크립트를 쓰면 이런 문제가
> 발생하지 않습니다.

> 앱 안의 **⚙️ 설정** 에서도 API 키를 입력할 수 있어 `.env` 를 직접 편집하지 않아도 됩니다.

---

## ✨ 주요 기능

- 🎧 **오디오 자동 추출** — `yt-dlp` 로 유튜브 영상의 오디오만 mp3 로 로컬 임시 폴더에 다운로드
- 📅 **유튜브 메타데이터 활용** — 영상 게시일, 채널, 설명, **공식 챕터**,
  **기존 자막**(수동/자동) 을 함께 수집해 LLM 번역·요약 단계에 컨텍스트로 주입.
  화자 실명 추론과 챕터 경계 유지 정확도가 향상되고, 최종 마크다운에는
  게시일/챕터 섹션이 자동으로 삽입됨.
- 🗣️ **화자 분리 STT** — 플랫폼별 로컬 GPU 엔진 + 클라우드 폴백
  - **NVIDIA GPU** (Linux/Windows): **WhisperX** (Distil-Whisper + pyannote, 청크 분할 처리, VRAM ~6GB)
  - **Apple Silicon Mac** (M1~M5): **MLX Whisper** + pyannote (Metal/MPS GPU 가속)
  - **GPU 없음**: **AssemblyAI Cloud API** 자동 폴백
  - 화자(Who) + 타임스탬프(When) + 내용(What) 을 동시 추출
  - IT/AI 도메인 핫워드 64 개 (Sam Altman, RLHF, Mixture of Experts …) 를 `initial_prompt` 로 주입해 고유명사/약어 인식률 향상
- 🌐 **IT/AI 전문 톤 한국어 번역** — OpenAI `gpt-5.4` / Anthropic `claude-sonnet-4-6` / Google Gemini `gemini-2.5-flash`
  - 화자 실명(진행자/게스트) 자동 추론
  - LLM / RAG / Fine-tuning 등 전문 용어 영문 병기
  - 구어체 추임새 정리, 가독성 높은 인터뷰 톤
  - **청크 분할 번역**으로 장편(1 시간+) 영상의 토큰 한도 초과 방지
- 📝 **GuruNote 스타일 마크다운 요약**
  - 📌 영상 제목 및 핵심 주제 요약
  - 💡 Guru's Insights (3~5 개)
  - ⏱️ 타임라인별 주요 내용 요약
  - 📝 전체 스크립트 번역본 + 🇺🇸 영어 원문
- 📥 **`.md` 파일 다운로드** (`GuruNote_<영상제목>.md`)
- 📂 **작업 히스토리** — 완료/실패 모든 작업이 `~/.gurunote/jobs/` 에 자동 저장.
  마크다운 재다운로드, 파이프라인 로그 확인, 에러 원인 진단 가능.
- ⏱ **실시간 진행 표시** — 5단계 뱃지 인디케이터 + ETA (경과 시간 + 남은 예상 시간)
- 📦 **WhisperX 미설치 시 안내** (NVIDIA 환경) — 설치 또는 AssemblyAI 전환 선택 다이얼로그.
  Apple Silicon 환경에서는 `setup.sh` 가 MLX 스택을 자동 설치.
- 🧹 **임시 파일 자동 정리**

---

## 📋 출력 예시

GuruNote 가 생성하는 마크다운 요약본의 실제 모습:

```markdown
# 🎙️ GuruNote — Sam Altman: GPT-5 and the Future of AI

- **채널:** Lex Fridman
- **게시일:** 2025-09-15
- **STT 엔진:** `whisperx`
- **화자 수:** 2
- **재생 시간:** 01:42:30

# 📌 영상 제목 및 핵심 주제 요약
OpenAI CEO Sam Altman 이 Lex Fridman 팟캐스트에 출연해
GPT-5 의 아키텍처, AGI 로드맵, AI 안전성 연구 방향을 심층 논의.

# 💡 Guru's Insights (핵심 인사이트)
- **스케일링 법칙은 아직 유효하다** — ...
- **멀티모달 통합이 다음 도약의 열쇠** — ...
- **AI Alignment 연구에 수익의 20% 를 투자** — ...

# ⏱️ 타임라인별 주요 내용 요약
- [00:00] 인사 및 GPT-5 발표 배경
- [12:30] 아키텍처 변화 — Transformer 를 넘어서
- [35:00] AGI 정의와 실현 시점에 대한 견해
- ...

# 📝 전체 스크립트 번역본
[00:00] Speaker A (Lex Fridman): 오늘 특별한 게스트를 모셨습니다...
[00:15] Speaker B (Sam Altman): 초대해주셔서 감사합니다...
```

---

## 🧱 파이프라인

```
유튜브 URL
   │
   ▼  [Step 1] yt-dlp — 오디오 추출 (mp3)
   │
   ▼  [Step 2] WhisperX (NVIDIA) / MLX (Apple Silicon) / AssemblyAI — 화자 분리 전사
   │          └ IT/AI 핫워드를 initial_prompt 로 주입
   │          └ 청크 분할 처리 (영상 길이 제한 없음)
   │
   ▼  [Step 3] LLM 청크 분할 번역 (gpt-5.4 / claude-sonnet-4-6)
   │          └ 화자 라벨 + 타임스탬프 보존
   │
   ▼  [Step 4] LLM 요약본 생성 (GuruNote 스타일)
   │
   ▼  [Step 5] 마크다운 조립 + 다운로드 + 임시 폴더 정리
   │
   ▼
GuruNote_<영상제목>.md
```

---

## ⚙️ 요구사항

상세 설치 명령은 위 [📦 선행 조건](#-선행-조건-필수-사전-설치) 섹션 참고.

- **Git** ([git-scm.com](https://git-scm.com/downloads)) — 저장소 clone + 앱 내 업데이트
- **Python** 3.10 이상 ([python.org](https://www.python.org/downloads/))
- **ffmpeg** ([ffmpeg.org](https://ffmpeg.org/download.html)) — 오디오 추출에 필수적인 시스템 패키지
  - Mac: `brew install ffmpeg`
  - Windows: `winget install --id Gyan.FFmpeg -e` (또는 공식 사이트 다운로드)
  - Ubuntu/Debian: `sudo apt install ffmpeg`
- **로컬 STT GPU (선택)** — `setup.sh` 가 자동 감지/설치
  - **NVIDIA (Linux/Windows)** — WhisperX, VRAM ~6GB 권장 (Distil-Whisper + 청크 분할)
  - **Apple Silicon (M1~M5)** — MLX Whisper, 16GB+ Unified Memory 권장
  - **GPU 없음** — `GURUNOTE_STT_ENGINE=assemblyai` 로 클라우드 API 사용
- **API Key** (최소 하나씩)
  - LLM: `OPENAI_API_KEY` **또는** `ANTHROPIC_API_KEY`
  - STT 폴백용(선택): `ASSEMBLYAI_API_KEY`

---

## 🚀 설치

`bash setup.sh` (macOS/Linux) 또는 `setup.bat` (Windows) 단일 명령으로
가상환경 생성부터 플랫폼별 STT 엔진 설치까지 모두 자동 처리됩니다.

```bash
git clone https://github.com/avlp12/GuruNote.git
cd GuruNote

# macOS / Linux
bash setup.sh

# Windows
setup.bat
```

setup 스크립트가 순서대로 수행하는 작업:

1. `.venv/` 가상환경 생성 (이미 있으면 재사용) — `python3 -m venv .venv`
2. 플랫폼 감지: `nvidia-smi` 존재 여부 + `uname -s/-m`
3. 공통 의존성(`requirements.txt`) 설치 (UI / audio / LLM / AssemblyAI 폴백)
4. 플랫폼별 STT 엔진 추가 설치:
   - **NVIDIA GPU** → CUDA PyTorch 2.8.0 + `requirements-gpu.txt` (WhisperX)
   - **Apple Silicon** → `requirements-mac.txt` (MLX Whisper + pyannote + onnxruntime)
   - **감지 실패** → 추가 설치 없음 (AssemblyAI Cloud API 만 사용 가능)
5. 환경 검증 — PyTorch 버전, CUDA/MPS 가용성, 핵심 라이브러리 import 확인

> 💡 **venv 를 수동으로 만들 필요 없음** — setup 스크립트가 이미 `.venv` 를
> 만들고 그 안에 모든 의존성을 설치합니다. 실행은 `bash run_desktop.sh` /
> `run_web.sh` 래퍼가 `.venv/bin/python` 을 직접 호출하므로 `source activate`
> 없이 동작합니다 (macOS 의 `command not found: python` / `streamlit` 문제 회피).

### 📦 데스크톱 패키지 vs 소스 실행

| | 데스크톱 패키지 (.exe / .dmg / .pkg) | 소스 실행 (`bash setup.sh`) |
|---|---|---|
| **포함 STT 엔진** | AssemblyAI (클라우드만) | WhisperX (NVIDIA) / MLX (Apple Silicon) / AssemblyAI |
| **로컬 GPU 가속** | ❌ (PyInstaller 번들 한계) | ✅ |
| **인터넷 필요** | STT 마다 필요 | 로컬 STT 는 최초 모델 다운로드만 |
| **설치 난이도** | 더블클릭 | 가상환경 + setup 스크립트 |
| **추천 대상** | 클라우드 STT 만 쓰는 사용자 | 로컬 GPU 보유 사용자, 개발자 |

> 🔍 **왜 번들에 로컬 STT 가 빠지나요?**
> WhisperX(+CUDA PyTorch) ~3GB, MLX(+pyannote+torch) ~2GB 의 native binary 가
> 필요하고, CUDA 빌드는 GPU 러너가 있어야 합니다. 단일 실행 파일로 묶으면
> 다운로드 크기가 비현실적이고 시작 시간도 길어집니다. 번들된 venv 는
> 사후 `pip install` 도 불가능하므로, 로컬 GPU STT 가 필요하면 소스에서
> 실행하는 것이 현실적인 유일한 선택지입니다.

---

## 🔑 환경변수 설정

```bash
cp .env.example .env
```

그 뒤 `.env` 를 열어 필요한 값을 채웁니다. 최소 설정 예:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
# 로컬 OpenAI-compatible 서버 (선택)
# 예: oMLX / vLLM / Ollama / LM Studio / llama.cpp server
OPENAI_BASE_URL=http://127.0.0.1:8000/v1
# STT 엔진 기본값 auto: NVIDIA → WhisperX, Apple Silicon → MLX, 그 외 → AssemblyAI
GURUNOTE_STT_ENGINE=auto
```

> `.env` 는 `.gitignore` 에 의해 절대 커밋되지 않습니다.

---

## ▶️ 실행

### 데스크톱 앱 (권장)

```bash
# macOS / Linux
bash run_desktop.sh

# Windows
run_desktop.bat

# 또는 venv activate 후 직접 실행
source .venv/bin/activate     # Windows: .venv\Scripts\activate
python gui.py
```

| 기능 | 설명 |
|---|---|
| **사이드바** | GuruNote 브랜드 + Settings / History / Update |
| **입력 카드** | 유튜브 URL 또는 로컬 파일 선택, STT/LLM 엔진 선택 |
| **진행 카드** | 5단계 뱃지 (dim→보라→초록) + 진행 바 + **ETA (경과/남은 시간)** |
| **결과 카드** | Summary / Korean / English / Log 탭 + Save .md |
| **히스토리** | 과거 작업 목록 + 마크다운 재다운로드 + 실패 로그 확인 |
| **중지** | ⏹ 버튼으로 안전한 지점에서 중단 |

### 웹 앱 (Streamlit)

```bash
# macOS / Linux
bash run_web.sh

# Windows
run_web.bat

# 또는 venv activate 후 직접 실행
source .venv/bin/activate
streamlit run app.py
```

브라우저에서 동일한 파이프라인을 실행합니다.
⚙️ Settings 탭에서 API 키, 모델, Temperature 등을 저장/테스트할 수 있습니다.

### 사용 흐름

```
1. 유튜브 URL 입력 (또는 📁 로컬 파일 선택)
       ↓
2. STT 엔진 (auto / whisperx / mlx / assemblyai)
   LLM 제공자 (openai / anthropic / gemini / openai_compatible) 선택
       ↓
3. "▶ GuruNote 생성하기" 클릭
       ↓
4. 진행 상황을 5단계 인디케이터 + 로그로 실시간 확인
       ↓
5. 📌 요약본 / 🇰🇷 번역 / 🇺🇸 원문 탭에서 결과 확인
       ↓
6. 📥 마크다운 저장 → GuruNote_<영상제목>.md 다운로드
```

> **최초 실행 안내:**
> WhisperX (Distil-Whisper large-v3, ~1.5GB) 또는 MLX Whisper (large-v3, ~3GB)
> 모델 가중치를 Hugging Face Hub 에서 다운로드합니다. 네트워크 속도에 따라
> **수 분이 소요**될 수 있으며, 터미널에 진행 상황이 표시됩니다. 이후 실행부터는
> 로컬 캐시(`~/.gurunote/models/` 또는 `~/.cache/huggingface/`)를 사용합니다.

<details>
<summary><strong>🔧 고급: 패키징 / CI / 업데이트</strong></summary>

### 독립 실행 파일 패키징

```bash
pip install pyinstaller
pyinstaller --windowed --onefile gui.py
# dist/gui.app (Mac) 또는 dist/gui.exe (Windows)
```

또는 `scripts/package_desktop.py` 로 Windows `.exe`/설치형, macOS `.app`/`.dmg`/`.pkg` 를 자동 생성:

```bash
python scripts/package_desktop.py --target windows              # .exe
python scripts/package_desktop.py --target windows --formats installer  # 설치형
python scripts/package_desktop.py --target macos                # .app
python scripts/package_desktop.py --target macos --formats dmg  # .dmg
```

### GitHub Actions 릴리스 자동화

`.github/workflows/release-desktop.yml` — `v*` 태그 푸시 시 Windows/macOS 패키지를
CI 에서 자동 빌드하고 GitHub Release 에 업로드합니다.

### 업데이트 (재설치 없이)

```bash
python scripts/update_gurunote.py --check   # 상태 확인
python scripts/update_gurunote.py --update  # git pull + pip upgrade
```

앱 내 ⚙️ 설정에도 동일한 업데이트 버튼이 있습니다.

### 릴리스 리허설 체크

```bash
python scripts/release_rehearsal_check.py --tag v0.1.1
python scripts/release_rehearsal_check.py --tag v0.1.1 --local-tools  # 로컬 도구까지 검사
```

</details>

---

## 🗂️ 프로젝트 구조

```
GuruNote/
├── app.py                      # Streamlit 웹 UI
├── gui.py                      # CustomTkinter 데스크톱 GUI
├── requirements.txt
├── .env.example
├── README.md
├── CHANGELOG.md
├── gurunote/
│   ├── __init__.py
│   ├── types.py                # Segment / Transcript 공통 데이터클래스
│   ├── audio.py                # Step 1 — yt-dlp + 로컬 파일 오디오 추출
│   ├── stt.py                  # Step 2 — WhisperX (NVIDIA) + AssemblyAI 폴백 라우터
│   ├── stt_mlx.py              # Step 2 — MLX Whisper + pyannote (Apple Silicon)
│   ├── llm.py                  # Step 3~4 — 번역 + 요약 (청크/재시도)
│   ├── exporter.py             # Step 4~5 — GuruNote 마크다운 조립
│   ├── history.py              # 작업 히스토리 + 영속 로그 (~/.gurunote/)
│   ├── settings.py             # `.env` 저장/로드 + 백업 유틸
│   └── updater.py              # git pull + pip upgrade 자동 업데이트 유틸
├── scripts/
│   ├── package_desktop.py      # Windows/macOS 배포 패키지 자동 생성
│   ├── update_gurunote.py      # CLI 업데이트 진입점
│   └── release_rehearsal_check.py  # 태그 푸시 전 릴리스 준비 체크
└── .github/workflows/
    └── release-desktop.yml     # 태그 푸시 시 데스크톱 패키지 자동 빌드
```

---

## 🛠️ 기술 스택

| 영역 | 사용 기술 |
|---|---|
| 데스크톱 UI | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (사이드바 + 카드 레이아웃) |
| 웹 UI | [Streamlit](https://streamlit.io/) |
| 오디오 추출 | [yt-dlp](https://github.com/yt-dlp/yt-dlp) · ffmpeg |
| STT + 화자 분리 | [WhisperX](https://github.com/m-bain/whisperX) (NVIDIA CUDA) · [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) + [pyannote.audio](https://github.com/pyannote/pyannote-audio) (Apple Silicon, Metal/MPS) · [AssemblyAI](https://www.assemblyai.com/) (Cloud fallback) |
| 번역 / 요약 | [OpenAI](https://platform.openai.com/) `gpt-5.4` · [Anthropic](https://docs.anthropic.com/) `claude-sonnet-4-6` · [Google Gemini](https://aistudio.google.com/) `gemini-2.5-flash` · OpenAI-compatible (로컬 LLM) |
| 환경 설정 | [python-dotenv](https://pypi.org/project/python-dotenv/) · 앱 내 ⚙️ 설정 다이얼로그 |

---

## 📜 버전 기록

주요 변경 사항은 [CHANGELOG.md](./CHANGELOG.md) 에 [Keep a Changelog](https://keepachangelog.com/)
형식으로 기록되며 버전은 [Semantic Versioning](https://semver.org/) 을 따릅니다.

현재 버전: **v0.6.0.7** — README 선행 조건(Git/Python/ffmpeg) 명시 + Windows PowerShell 5.1 `&&` 호환 가이드.

---

## ❓ 자주 묻는 질문 (FAQ)

| 질문 | 답변 |
|---|---|
| **`'git' 용어가 ... 인식되지 않습니다` (Windows)** | Git 이 설치되지 않았습니다. `winget install --id Git.Git -e` 실행 후 **새 PowerShell 창**을 열어 재시도하세요. winget 이 없는 구형 Windows 는 [git-scm.com/download/win](https://git-scm.com/download/win) 에서 인스톨러를 받아 설치. 자세한 내용은 위 [📦 선행 조건](#-선행-조건-필수-사전-설치) 참고. |
| **`'&&' 토큰은 이 버전에서 올바른 문 구분 기호가 아닙니다` (Windows PowerShell)** | Windows 기본 탑재된 PowerShell 5.1 은 `&&` 를 지원하지 않습니다. 명령을 **한 줄에 하나씩** 실행하거나 (`git clone ...` 한 줄 → `cd GuruNote` 한 줄), PowerShell 7+ 로 업그레이드(`winget install Microsoft.PowerShell`) 또는 `cmd.exe` 를 사용하세요. |
| **`python: command not found` / `'python' 용어가 인식되지 않습니다`** | Python 3.10+ 이 설치되지 않았거나 PATH 에 없습니다. Windows: `winget install --id Python.Python.3.12 -e` (설치 마법사의 "Add python.exe to PATH" 체크 필수). macOS 는 `python3` 명령을 사용하세요. Linux: `sudo apt install python3 python3-venv`. |
| **`command not found: python` / `streamlit` (macOS)** | macOS 12+ 는 `python` 명령이 없고 `python3` 만 있으며, `streamlit` 은 venv 내부에만 설치됩니다. `bash run_desktop.sh` / `bash run_web.sh` 를 쓰면 venv activate 없이 실행됩니다. 직접 실행하려면 먼저 `source .venv/bin/activate` 로 venv 를 활성화하세요. |
| **GPU 없이 쓸 수 있나요?** | `.env` 에서 `GURUNOTE_STT_ENGINE=assemblyai` 로 설정하면 클라우드 API 로 동작합니다 (AssemblyAI 키 필요). |
| **Apple Silicon Mac (M1~M5) 에서 GPU 로컬 STT 가 되나요?** | 네. v0.6.0 부터 `setup.sh` 가 Apple Silicon 을 자동 감지해 `mlx-whisper` + `pyannote.audio` 를 설치합니다. STT 엔진을 `auto` 로 두면 Metal/MPS GPU 가속으로 로컬 전사 + 화자 분리가 동작합니다. 화자 분리에는 `HUGGINGFACE_TOKEN` + [pyannote 모델 동의](https://huggingface.co/pyannote/speaker-diarization-3.1) 가 필요합니다. |
| **1시간 넘는 영상은?** | WhisperX / MLX 모두 청크 분할 처리라 길이 제한이 없습니다. AssemblyAI 도 길이 제한 없음. |
| **로컬 LLM 을 쓰고 싶어요** | `.env` 에서 `LLM_PROVIDER=openai_compatible` + `OPENAI_BASE_URL=http://127.0.0.1:8000/v1` 설정. Ollama, vLLM, LM Studio 등 OpenAI-compatible 서버라면 모두 가능합니다. |
| **"ffmpeg not found" 에러** | Mac: `brew install ffmpeg` / Windows: `winget install ffmpeg` / Ubuntu: `sudo apt install ffmpeg` |
| **모델 가중치 다운로드가 오래 걸려요** | WhisperX Distil-Whisper (~1.5GB) / MLX Whisper large-v3 (~3GB) 는 최초 1회만 다운로드됩니다. 이후는 로컬 캐시 (`~/.gurunote/models/` 또는 `~/.cache/huggingface/`) 를 사용합니다. |
| **API 키를 어디에 넣나요?** | 앱 실행 후 Settings → 입력 → Save. `.env` 파일에 자동 기록됩니다. |
| **CUDA Out of Memory 에러** | v0.3.0 부터 자동으로 토큰 수를 줄여 재시도합니다 (32768→16384→8192). 그래도 실패하면 모델을 자동 언로드하고 에러 메시지에 해결 방법을 안내합니다. |
| **WhisperX 가 설치 안 됐다고 떠요** (NVIDIA) | "GuruNote 생성하기" 클릭 시 설치/AssemblyAI 전환 선택 다이얼로그가 뜹니다. Apple Silicon 에선 MLX 자동 사용. |
| **과거 작업을 다시 보고 싶어요** | 사이드바 History → 목록에서 Save (마크다운 재다운로드) 또는 Log (파이프라인 로그 확인). |

---

## 🗑️ 제거 (Uninstall)

GuruNote 는 시스템 레벨 설치를 하지 않고 `.venv` + 프로젝트 폴더 + 홈의 데이터
폴더에만 파일을 남깁니다. 단계별로 지우면 깔끔하게 제거됩니다.

### macOS / Linux

```bash
# 1. ⚠️ API 키 백업 또는 완전 삭제 (.env 에 저장됨)
cat GuruNote/.env                 # 필요하면 내용 복사 후 보관
# (따로 보관할 필요 없으면 다음 단계에서 함께 삭제됨)

# 2. 프로젝트 폴더 통째로 삭제 (.venv/ + autosave/ + .env 모두 포함)
rm -rf GuruNote

# 3. 사용자 홈의 GuruNote 데이터 삭제
#    - ~/.gurunote/jobs/       작업 히스토리 (메타 + 결과 마크다운 + pipeline.log)
#    - ~/.gurunote/history.json  히스토리 인덱스
#    - ~/.gurunote/models/      WhisperX 모델 (NVIDIA 로 썼던 경우, ~1.5GB)
rm -rf ~/.gurunote

# 4. (선택) HuggingFace 모델 캐시 — MLX / pyannote 가 다운받은 모델
#    ⚠️ 이 폴더는 다른 프로젝트 (transformers 직접 사용, ComfyUI 등) 도
#       공유하므로, GuruNote 전용이었던 경우에만 삭제.
ls ~/.cache/huggingface/hub/      # 먼저 확인
rm -rf ~/.cache/huggingface/hub/models--mlx-community--whisper-*
rm -rf ~/.cache/huggingface/hub/models--pyannote--*
rm -rf ~/.cache/huggingface/hub/models--Systran--faster-whisper-*
# 또는 HuggingFace 캐시 자체를 통째로:
# rm -rf ~/.cache/huggingface
```

### Windows (PowerShell)

```powershell
# 1. ⚠️ API 키 백업 (GuruNote\.env)
Get-Content GuruNote\.env         # 내용 확인

# 2. 프로젝트 폴더 통째로 삭제
Remove-Item -Recurse -Force GuruNote

# 3. 사용자 홈의 GuruNote 데이터 삭제
Remove-Item -Recurse -Force "$env:USERPROFILE\.gurunote"

# 4. (선택) HuggingFace 모델 캐시
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface\hub\models--mlx-community--whisper-*"
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface\hub\models--pyannote--*"
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface\hub\models--Systran--faster-whisper-*"
```

### 삭제 대상 요약

| 경로 | 내용 | 크기 (대략) |
|---|---|---|
| `GuruNote/` (프로젝트 폴더) | 소스 + `.venv/` + `autosave/` + `.env` | **2~5 GB** (의존성 포함) |
| `~/.gurunote/jobs/` | 작업 히스토리 메타 + 결과 마크다운 + 로그 | 수 MB (작업 수에 따라) |
| `~/.gurunote/models/` | WhisperX 모델 (NVIDIA 로 사용 시) | **~1.5 GB** |
| `~/.gurunote/history.json` | 히스토리 인덱스 | 수 KB |
| `~/.cache/huggingface/hub/` (일부) | MLX Whisper, pyannote diarization 모델 | **~3~4 GB** |

> 🔒 **보안 주의**: `.env` 에는 OpenAI / Anthropic / Gemini / AssemblyAI API 키
> 가 평문 저장됩니다. 프로젝트 폴더 삭제 전에 안전한 위치로 백업하거나,
> API 제공자 대시보드에서 키를 폐기(revoke) 하세요.

> 📁 **임시 파일**: 파이프라인 실행 중 `/tmp/gurunote_*` (Windows: `%TEMP%\gurunote_*`)
> 에 임시 오디오 파일이 생성되며 작업 완료 시 자동 정리됩니다. 비정상 종료로
> 남아있다면 OS 재부팅 또는 수동 삭제로 제거됩니다.

---

## 📄 License

MIT License. 자세한 내용은 [LICENSE](./LICENSE) 참고.
