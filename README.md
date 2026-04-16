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

## ⚡ 빠른 시작 (3단계)

```bash
# 1. 설치
git clone https://github.com/avlp12/GuruNote.git && cd GuruNote
python -m venv .venv && source .venv/bin/activate

bash setup.sh        # macOS / Linux  (Windows 는 setup.bat)
# 자동 감지 + 설치:
#   - NVIDIA GPU (Linux/Windows) → CUDA PyTorch + WhisperX
#   - Apple Silicon Mac (M1~M4)  → MLX Whisper + pyannote (Metal/MPS GPU 가속)
#   - 그 외                       → AssemblyAI Cloud API 만 사용 가능

# 2. API 키 설정 (OpenAI / Anthropic / Google Gemini 중 하나)
cp .env.example .env
# .env 를 열어 OPENAI_API_KEY=sk-... 입력

# 3. 실행
python gui.py          # 데스크톱 앱
# 또는
streamlit run app.py   # 웹 앱
```

> 앱 안의 **⚙️ 설정** 에서도 API 키를 입력할 수 있어 `.env` 를 직접 편집하지 않아도 됩니다.

---

## ✨ 주요 기능

- 🎧 **오디오 자동 추출** — `yt-dlp` 로 유튜브 영상의 오디오만 mp3 로 로컬 임시 폴더에 다운로드
- 📅 **유튜브 메타데이터 활용** — 영상 게시일, 채널, 설명, **공식 챕터**,
  **기존 자막**(수동/자동) 을 함께 수집해 LLM 번역·요약 단계에 컨텍스트로 주입.
  화자 실명 추론과 챕터 경계 유지 정확도가 향상되고, 최종 마크다운에는
  게시일/챕터 섹션이 자동으로 삽입됨.
- 🗣️ **화자 분리 STT** — Microsoft VibeVoice-ASR (오픈소스, MIT) 를 기본 엔진으로 채택
  - 60 분 장편 오디오를 단일 패스로 처리
  - 화자(Who) + 타임스탬프(When) + 내용(What) 을 동시 추출
  - IT/AI 도메인 핫워드 64 개 (Sam Altman, RLHF, Mixture of Experts …) 를 `context_info` 로 주입해 고유명사/약어 인식률 향상
  - GPU 미가용 환경에서는 **AssemblyAI Cloud API** 로 자동 폴백
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
- 🔧 **VRAM 자동 최적화** — GPU 메모리에 맞춰 4-bit/8-bit 양자화 자동 선택.
  CUDA OOM 발생 시 토큰 축소 재시도 + 모델 자동 언로드.
- 📦 **VibeVoice 미설치 시 안내** — 설치 또는 AssemblyAI 전환 선택 다이얼로그
- 🧹 **임시 파일 자동 정리**

---

## 📋 출력 예시

GuruNote 가 생성하는 마크다운 요약본의 실제 모습:

```markdown
# 🎙️ GuruNote — Sam Altman: GPT-5 and the Future of AI

- **채널:** Lex Fridman
- **게시일:** 2025-09-15
- **STT 엔진:** `vibevoice`
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
   ▼  [Step 2] VibeVoice-ASR (or AssemblyAI) — 화자 분리 전사
   │          └ IT/AI 핫워드를 context_info 로 주입
   │          └ ⚠️ 최대 60분 단일 패스 (초과 시 auto→AssemblyAI 전환)
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

> **60분 초과 팟캐스트 (Edge Case)**
> VibeVoice-ASR 은 최대 60분 오디오를 단일 패스로 처리합니다. Lex Fridman
> 인터뷰처럼 2~3시간짜리 장편 영상의 경우 VibeVoice 단독 모드에서는 **처음 60분만
> 전사될 수 있습니다**. 향후 오디오를 60분 단위로 분할 → STT → 병합하는
> 자동 청킹 기능을 추가할 예정입니다. 지금은 60분 이하의 영상에서 최적의
> 결과를 얻을 수 있으며, 긴 영상은 `GURUNOTE_STT_ENGINE=assemblyai` 로
> AssemblyAI 를 사용하면 길이 제한 없이 처리됩니다.
>
> ✅ **현재 앱 동작 보완**: `STT 엔진=auto` 인 경우 60분 초과 오디오는
> AssemblyAI 로 자동 라우팅해, 기본 설정에서도 긴 영상 누락을 줄입니다.

---

## ⚙️ 요구사항

- **Python** 3.10 이상
- **ffmpeg** (오디오 추출에 필수적인 시스템 패키지)
  - Mac: `brew install ffmpeg`
  - Windows: `winget install ffmpeg` (또는 [공식 사이트](https://ffmpeg.org/download.html) 다운로드)
  - Ubuntu/Debian: `sudo apt install ffmpeg`
- **GPU (VibeVoice-ASR 구동 시)**
  > v0.3.0 부터 VRAM 에 맞는 **4-bit/8-bit 양자화를 자동 선택**합니다:
  >
  > | VRAM | 양자화 | 모델 크기 |
  > |---|---|---|
  > | 48GB+ | bf16 | ~14GB |
  > | 24GB+ | 8-bit | ~7GB |
  > | 16GB+ | **4-bit NF4** | **~4GB** (기본) |
  >
  > `.env` 에서 `VIBEVOICE_QUANTIZATION=4bit` 으로 강제 지정도 가능합니다.
  > GPU 가 아예 없다면 `GURUNOTE_STT_ENGINE=assemblyai` 로 클라우드 API 를 사용하세요.
- **API Key** (최소 하나씩)
  - LLM: `OPENAI_API_KEY` **또는** `ANTHROPIC_API_KEY`
  - STT 폴백용(선택): `ASSEMBLYAI_API_KEY`

---

## 🚀 설치

```bash
git clone https://github.com/avlp12/GuruNote.git
cd GuruNote

# (권장) 가상환경
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 패키지 설치 (vibevoice 는 git+https 로 설치됨 — 수 분 소요 가능)
pip install -r requirements.txt
```

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
# STT 엔진은 기본값 auto 로 두면 VibeVoice → AssemblyAI 순서로 시도
GURUNOTE_STT_ENGINE=auto
```

> `.env` 는 `.gitignore` 에 의해 절대 커밋되지 않습니다.

---

## ▶️ 실행

### 데스크톱 앱 (권장)

```bash
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
streamlit run app.py
```

브라우저에서 동일한 파이프라인을 실행합니다.
⚙️ Settings 탭에서 API 키, 모델, Temperature 등을 저장/테스트할 수 있습니다.

### 사용 흐름

```
1. 유튜브 URL 입력 (또는 📁 로컬 파일 선택)
       ↓
2. STT 엔진 (auto/vibevoice/assemblyai)
   LLM 제공자 (openai/anthropic/openai_compatible) 선택
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
> VibeVoice-ASR 엔진을 처음 사용할 때 Hugging Face Hub 에서 모델 가중치(약
> 14GB)를 다운로드합니다. 네트워크 속도에 따라 **수 분~수십 분이 소요**될 수
> 있으며, 터미널에 진행 상황이 표시됩니다. 이후 실행부터는 로컬 캐시를
> 사용하므로 대기 시간이 없습니다.

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
│   ├── stt.py                  # Step 2 — VibeVoice-ASR + AssemblyAI 폴백
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

현재 버전: **v0.6.0** — macOS Apple Silicon 로컬 GPU STT (MLX Whisper + pyannote MPS).

---

## ❓ 자주 묻는 질문 (FAQ)

| 질문 | 답변 |
|---|---|
| **GPU 없이 쓸 수 있나요?** | `.env` 에서 `GURUNOTE_STT_ENGINE=assemblyai` 로 설정하면 클라우드 API 로 동작합니다 (AssemblyAI 키 필요). |
| **Apple Silicon Mac (M1~M4) 에서 GPU 로컬 STT 가 되나요?** | 네. v0.6.0 부터 `setup.sh` 가 Apple Silicon 을 자동 감지해 `mlx-whisper` + `pyannote.audio` 를 설치합니다. STT 엔진을 `auto` 로 두면 Metal/MPS GPU 가속으로 로컬 전사 + 화자 분리가 동작합니다. 화자 분리에는 `HUGGINGFACE_TOKEN` + [pyannote 모델 동의](https://huggingface.co/pyannote/speaker-diarization-3.1) 가 필요합니다. |
| **1시간 넘는 영상은?** | STT 엔진이 `auto` 면 60분 초과 시 자동으로 AssemblyAI 로 전환됩니다. `vibevoice` 고정 시 처음 60분만 전사될 수 있습니다. |
| **로컬 LLM 을 쓰고 싶어요** | `.env` 에서 `LLM_PROVIDER=openai_compatible` + `OPENAI_BASE_URL=http://127.0.0.1:8000/v1` 설정. Ollama, vLLM, LM Studio 등 OpenAI-compatible 서버라면 모두 가능합니다. |
| **"ffmpeg not found" 에러** | Mac: `brew install ffmpeg` / Windows: `winget install ffmpeg` / Ubuntu: `sudo apt install ffmpeg` |
| **모델 가중치 다운로드가 오래 걸려요** | VibeVoice-ASR 7B (약 14GB) 는 최초 1회만 다운로드됩니다. 이후는 `~/.cache/huggingface/` 캐시를 사용합니다. |
| **API 키를 어디에 넣나요?** | 앱 실행 후 Settings → 입력 → Save. `.env` 파일에 자동 기록됩니다. |
| **CUDA Out of Memory 에러** | v0.3.0 부터 자동으로 토큰 수를 줄여 재시도합니다 (32768→16384→8192). 그래도 실패하면 모델을 자동 언로드하고 에러 메시지에 해결 방법을 안내합니다. |
| **VibeVoice 가 설치 안 됐다고 떠요** | "GuruNote 생성하기" 클릭 시 설치/AssemblyAI 전환 선택 다이얼로그가 뜹니다. |
| **과거 작업을 다시 보고 싶어요** | 사이드바 History → 목록에서 Save (마크다운 재다운로드) 또는 Log (파이프라인 로그 확인). |

---

## 📄 License

MIT License. 자세한 내용은 [LICENSE](./LICENSE) 참고.
