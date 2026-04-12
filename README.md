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

---

## ⚙️ 요구사항

- **Python** 3.10 이상
- **ffmpeg** (시스템 패키지, yt-dlp 의 mp3 변환에 필요)
- **GPU 권장** — VibeVoice-ASR 7B 추론에 CUDA / MPS / XPU 중 하나. GPU 가 없으면 `engine=auto` 가 자동으로 AssemblyAI 폴백으로 전환됩니다.
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

```bash
streamlit run app.py
```

브라우저가 열리면 유튜브 URL 을 입력하고 **GuruNote 생성하기** 버튼을 누릅니다.
사이드바에서 STT 엔진(`auto` / `vibevoice` / `assemblyai`)과 LLM provider
(`openai` / `anthropic`) 를 런타임에 선택할 수 있습니다.

---

## 🗂️ 프로젝트 구조

```
GuruNote/
├── app.py                   # Streamlit UI — 5 단계 파이프라인 오케스트레이션
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
