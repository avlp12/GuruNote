# GuruNote Quality Doc

마지막 갱신: 2026-05-18
용도: 모듈별 품질 등급으로 다음 작업 우선순위 catch

## 등급 정의

- A: 안정 운영, 회귀 위험 작음
- B: 작동, 알려진 약점 있음
- C: 작동하지만 본질 결함 catch
- D: 부재 또는 작동 부재

## 모듈별 등급

### STT 단계 (Quality: A)

- 구성: mlx-whisper (Mac) + WhisperX (NVIDIA GPU) + AssemblyAI Cloud (fallback)
- 안정성: 안정 운영
- 검증: README 5단계 파이프라인 정합
- 약점 부재

### LLM 번역 (gurunote/llm.py) (Quality: B+)

- 구성: openai_compatible (qwen3.6-35b-q5) + OpenAI + Anthropic + Gemini
- 완료: Phase 1 Redesign (Index Mapping + json_schema strict + segment cap 15)
- 완료: Phase 4a-1 (xgrammar selective disable)
- 알려진 약점:
  - 옵션 A loose mode 줄 수 실패 위험 (5/18 catch)
  - slow chunk 처리 시간 폭주 (chunk 9/14 250초+ 케이스)
  - entity hallucinate (샘 올트먼 5회 사례)
- 검증: `tests/test_phase3_cjk_postprocess.py` 32 통과

### 한자/일본어 후처리 (post_process_cjk) (Quality: A)

- 완료: Phase 3 cdbdc67
- 검증: 32 test (mock + integration) 모두 통과
- 약점:
  - 사전 미적중 시 LLM mapping retry 3회 의존 (처리 시간 영향)
  - Sub-C fallback 시 영문 원문 + inline 태그

### 화자 분리 (pyannote 통합) (Quality: B)

- 동작: 영상별 speaker A/B/C 라벨
- 약점:
  - 외부 인물 hallucinate 회귀 (샘 올트먼 사례)
  - Phase 2 entity cache 로 catch 예정

### UI (Quality: 본인 확인 필요)

- `gui.py` (customtkinter 데스크톱, 180KB)
- `app.py` (streamlit 웹, 32KB)
- `app_webview.py` (pywebview, redesign/tailwind-v2 브랜치)
- redesign/tailwind-v2 브랜치 진행 중 (Phase 2A Tailwind 리디자인)

### 검증 인프라 (Quality: B)

- 완료: `tests/` + `pytest.ini` + `pyproject.toml` (5/18 도입)
- 약점: Phase 3 외 다른 작업에 검증 인프라 부재
