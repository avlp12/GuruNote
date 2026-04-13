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
- 🌐 **IT/AI 전문 톤 한국어 번역** — OpenAI `gpt-4.1` 또는 Anthropic `claude-sonnet-4-6`
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
   ▼  [Step 3] LLM 청크 분할 번역 (gpt-4.1 / claude-sonnet-4-6)
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

### 방법 B — CustomTkinter 데스크톱 앱

```bash
python gui.py
```

브라우저 없이 네이티브 창으로 동일한 파이프라인을 실행합니다.
결과를 탭(요약/번역/원문)으로 확인하고, **파일 → 저장** 대화상자로 `.md` 를 내보냅니다.

```bash
# (선택) 독립 실행 파일로 패키징
pip install pyinstaller
pyinstaller --windowed --onefile gui.py
# dist/gui.app (Mac) 또는 dist/gui.exe (Windows) 생성
```

두 방식 모두 사이드바/상단에서 STT 엔진(`auto` / `vibevoice` / `assemblyai`)과
LLM provider(`openai` / `anthropic`) 를 런타임에 선택할 수 있습니다.

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
| 번역 / 요약 | [OpenAI](https://platform.openai.com/) `gpt-4.1` · [Anthropic](https://docs.anthropic.com/) `claude-sonnet-4-6` |
| 환경 설정 | [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## 📜 버전 기록

주요 변경 사항은 [CHANGELOG.md](./CHANGELOG.md) 에 [Keep a Changelog](https://keepachangelog.com/)
형식으로 기록되며 버전은 [Semantic Versioning](https://semver.org/) 을 따릅니다.

현재 버전: **v0.1.0** — VibeVoice-ASR 기반 Step 1~5 전체 파이프라인 초판.

---

## 📄 License

MIT License. 자세한 내용은 [LICENSE](./LICENSE) 참고.
