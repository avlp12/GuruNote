# GuruNote 🎙️

> 글로벌 IT/AI 구루들의 인사이트를 — 유튜브 링크 한 줄로 **화자 분리된 한국어 마크다운 요약본**으로.

GuruNote 는 해외 IT/AI 권위자(Guru)들의 유튜브 인터뷰/팟캐스트 URL 을 입력받아
오디오를 추출하고, **Microsoft VibeVoice-ASR** 로 화자 분리 + 타임스탬프
전사를 수행한 뒤, LLM 으로 IT/AI 전문 톤의 한국어 번역과 GuruNote 스타일의
마크다운 요약본을 자동 생성하는 Streamlit 웹 앱입니다.

---

## ✨ 주요 기능

- 🎧 **오디오 자동 추출** — `yt-dlp` 로 유튜브 영상의 오디오만 mp3 로 로컬 임시 폴더에 다운로드
- 🗣️ **화자 분리 STT** — Microsoft VibeVoice-ASR (오픈소스, MIT) 를 기본 엔진으로 채택
  - 60 분 장편 오디오를 단일 패스로 처리
  - 화자(Who) + 타임스탬프(When) + 내용(What) 을 동시 추출
  - IT/AI 도메인 핫워드 64 개 (Sam Altman, RLHF, Mixture of Experts …) 를 `context_info` 로 주입해 고유명사/약어 인식률 향상
  - GPU 미가용 환경에서는 **AssemblyAI Cloud API** 로 자동 폴백
- 🌐 **IT/AI 전문 톤 한국어 번역** — OpenAI `gpt-4o` 또는 Anthropic `claude-3-5-sonnet`
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
- 🧹 **임시 파일 자동 정리**

---

## 🧱 파이프라인

```
유튜브 URL
   │
   ▼  [Step 1] yt-dlp — 오디오 추출 (mp3)
   │
   ▼  [Step 2] VibeVoice-ASR (or AssemblyAI) — 화자 분리 전사
   │          └ IT/AI 핫워드를 context_info 로 주입
   │          └ ⚠️ v0.1.0: 최대 60분 단일 패스 (초과 시 아래 참고)
   │
   ▼  [Step 3] LLM 청크 분할 번역 (gpt-4o / claude-3.5-sonnet)
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
> 인터뷰처럼 2~3시간짜리 장편 영상의 경우 현재 v0.1.0 에서는 **처음 60분만
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
  > ⚠️ VibeVoice-ASR 7B 는 bfloat16 로딩 시 **약 14GB VRAM** 을 사용합니다.
  > **최소 16GB 이상의 VRAM** (NVIDIA: RTX 4090, A100 등) 또는
  > **Apple Silicon 32GB 이상 통합 메모리** (M2 Pro/Max, M3 등) 를 권장합니다.
  > VRAM 이 부족하다면 `.env` 에서 `GURUNOTE_STT_ENGINE=assemblyai` 로 설정해
  > 클라우드 API 를 사용하세요.
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

### 방법 A — Streamlit 웹 앱

```bash
streamlit run app.py
```

브라우저가 열리면 유튜브 URL 을 입력하고 **GuruNote 생성하기** 버튼을 누릅니다.
실행 중에는 단계별 로그와 함께 **퍼센트 진행률 바**가 표시됩니다.

> Streamlit 앱에는 **⚙️ Settings 탭**이 포함되어 있어 `.env` 수동 편집 없이
> LLM Provider(`openai` / `openai_compatible` / `anthropic`), API Key,
> Base URL, 모델명, Temperature, Max Tokens 저장/연결 테스트가 가능합니다.

> Streamlit 앱에는 **⚙️ Settings 탭**이 포함되어 있어 `.env` 수동 편집 없이
> LLM Provider(`openai` / `openai_compatible` / `anthropic`), API Key,
> Base URL, 모델명, Temperature, Max Tokens 저장/연결 테스트가 가능합니다.

### 방법 B — CustomTkinter 데스크톱 앱

```bash
python gui.py
```

브라우저 없이 네이티브 창으로 동일한 파이프라인을 실행합니다.
결과를 탭(요약/번역/원문)으로 확인하고, **파일 → 저장** 대화상자로 `.md` 를 내보냅니다.
상단 **⚙️ 설정**에서 동일하게 LLM Provider / Base URL / 모델 / 토큰 설정과
연결 테스트를 수행할 수 있습니다.
실행 중에는 좌측 로그 패널에서 **진행률(%)**을 확인할 수 있으며, `⏹ 중지` 버튼으로
현재 작업을 안전한 지점에서 중단할 수 있습니다.

```bash
# (선택) 독립 실행 파일로 패키징
pip install pyinstaller
pyinstaller --windowed --onefile gui.py
# dist/gui.app (Mac) 또는 dist/gui.exe (Windows) 생성
```

### 방법 C — 설치 패키지까지 자동 생성 (권장, 배포용)

반복적인 패키징 명령을 줄이기 위해 `scripts/package_desktop.py` 를 제공합니다.

```bash
# 공통 사전 준비
pip install pyinstaller
```

#### Windows

```bash
# 1) 단일 실행 파일(.exe)
python scripts/package_desktop.py --target windows

# 2) 설치형 exe까지 생성 (Inno Setup 필요)
python scripts/package_desktop.py --target windows --formats installer
```

- 출력:
  - `dist/GuruNote.exe` (단일 파일 실행형)
  - `dist/GuruNote-Installer.exe` (설치형, `--formats installer` 사용 시)
- 설치형 exe를 만들려면 [Inno Setup](https://jrsoftware.org/isdl.php) 의
  `ISCC.exe` 가 필요합니다.

#### macOS

```bash
# 1) .app 번들
python scripts/package_desktop.py --target macos

# 2) DMG 생성 (create-dmg 필요)
python scripts/package_desktop.py --target macos --formats dmg

# 3) PKG 생성 (macOS 기본 pkgbuild 사용)
python scripts/package_desktop.py --target macos --formats pkg
```

- 출력:
  - `dist/GuruNote.app`
  - `dist/GuruNote.dmg` (`--formats dmg`)
  - `dist/GuruNote.pkg` (`--formats pkg`)
- DMG를 만들려면 `brew install create-dmg` 가 필요합니다.

### GitHub Actions 릴리스 자동화

저장소에는 태그 푸시 시 데스크톱 패키지를 자동 빌드/업로드하는 워크플로우가
포함되어 있습니다.

- 워크플로우 파일: `.github/workflows/release-desktop.yml`
- 트리거:
  - `git push origin v0.1.1` 같은 `v*` 태그 푸시
  - 수동 실행 (`workflow_dispatch`)
- 결과:
  - Windows: `GuruNote.exe`, `GuruNote-Installer.exe`
  - macOS: `GuruNote.dmg`, `GuruNote.pkg` (그리고 빌드 산출물 `GuruNote.app`)
- 태그 이벤트에서는 위 파일을 GitHub Release assets 로 자동 첨부

### 업데이트 (재설치 없이)

소스 설치 사용자는 아래 명령으로 삭제/재설치 없이 업데이트할 수 있습니다.

```bash
# 업데이트 가능 상태 확인
python scripts/update_gurunote.py --check

# 코드 pull + 의존성 업그레이드
python scripts/update_gurunote.py --update
```

- Streamlit `⚙️ Settings` 탭과 Desktop GUI `⚙️ 설정`에도 **업데이트 버튼**이 있어
  앱 안에서 동일한 업데이트를 실행할 수 있습니다.

### 태그 릴리스 리허설 체크 (실패 시 즉시 원인 출력)

태그 푸시 전에 아래 스크립트로 릴리스 준비 상태를 점검할 수 있습니다.

```bash
# 기본: 태그 형식 + 필수 파일 + 워크플로우 핵심 항목 + 패키징 스크립트 스모크 테스트
python scripts/release_rehearsal_check.py --tag v0.1.1

# 선택: 현재 PC의 로컬 도구(pyinstaller/create-dmg/iscc 등)까지 검사
python scripts/release_rehearsal_check.py --tag v0.1.1 --local-tools
```

- 실패 시 `❌`와 함께 원인을 즉시 출력하고 종료 코드 1로 종료합니다.
- 통과 시 바로 실행할 태그 푸시 명령을 출력합니다.

두 방식 모두 사이드바/상단에서 STT 엔진(`auto` / `vibevoice` / `assemblyai`)과
LLM provider(`openai` / `openai_compatible` / `anthropic`) 를 런타임에 선택할 수 있습니다.

> **최초 실행 안내:**
> VibeVoice-ASR 엔진을 처음 사용할 때 Hugging Face Hub 에서 모델 가중치(약
> 14GB)를 다운로드합니다. 네트워크 속도에 따라 **수 분~수십 분이 소요**될 수
> 있으며, 터미널에 진행 상황이 표시됩니다. 이후 실행부터는 로컬 캐시를
> 사용하므로 대기 시간이 없습니다.

---

## 🗂️ 프로젝트 구조

```
GuruNote/
├── app.py                   # Streamlit 웹 UI
├── gui.py                   # CustomTkinter 데스크톱 GUI
├── requirements.txt
├── .env.example
├── README.md
├── CHANGELOG.md
└── gurunote/
    ├── __init__.py
    ├── types.py             # Segment / Transcript 공통 데이터클래스
    ├── audio.py             # Step 1 — yt-dlp 다운로드 + 임시폴더 정리
    ├── stt.py               # Step 2 — VibeVoice-ASR (primary) + AssemblyAI (fallback)
    ├── llm.py               # Step 3~4 — 번역 + 요약 (청크 분할)
    └── exporter.py          # Step 4~5 — GuruNote 마크다운 조립
```

---

## 🛠️ 기술 스택

| 영역 | 사용 기술 |
|---|---|
| UI | [Streamlit](https://streamlit.io/) |
| 오디오 추출 | [yt-dlp](https://github.com/yt-dlp/yt-dlp) · ffmpeg |
| STT + 화자 분리 | [Microsoft VibeVoice-ASR](https://github.com/microsoft/VibeVoice) (primary) · [AssemblyAI](https://www.assemblyai.com/) (fallback) |
| 번역 / 요약 | [OpenAI](https://platform.openai.com/) `gpt-4o` · [Anthropic](https://docs.anthropic.com/) `claude-3-5-sonnet` |
| 환경 설정 | [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## 📜 버전 기록

주요 변경 사항은 [CHANGELOG.md](./CHANGELOG.md) 에 [Keep a Changelog](https://keepachangelog.com/)
형식으로 기록되며 버전은 [Semantic Versioning](https://semver.org/) 을 따릅니다.

현재 버전: **v0.1.0** — VibeVoice-ASR 기반 Step 1~5 전체 파이프라인 초판.

---

## 📄 License

MIT License. 자세한 내용은 [LICENSE](./LICENSE) 참고.
