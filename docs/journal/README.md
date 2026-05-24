# GuruNote 개발 일지

> 유튜브 링크 한 줄로 해외 IT/AI **구루(Guru)** 영상을 **화자 분리 + 한국어 영문병기 마크다운 요약**으로 정리하는 데스크톱 앱.

## 한 문단

해외 IT/AI 인사이트(Jensen Huang, Sam Altman, Tiffany Janzen 등)가 매일 쏟아지는데, 한국어로 정리된 자료는 늦거나 부정확하다. GuruNote는 구루들의 유튜브/팟캐스트를 **완전 로컬**(mlx-whisper Mac / WhisperX NVIDIA)로 받아 화자 분리 + 한국어 번역 + 외래어 표기법 표준 + 영문병기 + Obsidian/Notion 출력까지 자동화한다. 2026-04-11 첫 commit, 2026-05-24 현재 758 commit + 183 test 통과.

**정체성 진화**: "IT/AI 구루 요약 앱"(PRD, 4/11) → "24/7 지식 증류기 + Obsidian"(WORK_ORDER) → "**모델 비의존 한국어 지식 정리**"(현재, 5/24).

## 현재 지점 (2026-05-24, HEAD 5c3c240)

### 완료
- **Phase 0~1 (v0.1.0 ~ v0.8.0.6)**: 5-step 파이프라인 → CustomTkinter GUI → openai_compatible local LLM → YouTube metadata → 모델 갱신 → SSL 인증서 fix
- **Phase 2A**: Tailwind redesign 진입, License MIT → Elastic 2.0 전환
- **Phase 2B**: React 신축 (Sidebar/MainScreen/HistoryScreen/EditorScreen/DashboardScreen/SettingsScreen) — 4/27 baseline ~ 5/9 polish
- **Phase 2B-3-backend Layer 1~15**: pyannote drift fix → LLM cascading + STT noise → ResultPanel 통합 → Tiffany Janzen 표기 → markdown 가독성 → CJK 차단 → title 정합
- **백엔드 품질 Phase 1~5 (Mac/MLX)**:
  - Phase 1 Redesign (`c68aab8`): Index Mapping + json_schema strict + segment cap 15
  - Phase 2 entity_cache (`f9c2da2`, `4a8f281` B06): 판카지/샘 올트먼 hallucinate 0
  - Phase 3 CJK (`cdbdc67`): Sub-path A+B+C 한자 0
  - Phase 4a-1 (`b447a11`): xgrammar selective disable
  - B02 timeout (`2ed4701`): ThreadPoolExecutor wall-clock 안전망
  - 2-pass DCCD + 화자 코드 부착 + community-1 + 빈 복구 (`599c94b`)
  - Phase 5 (`527d2ea`, 5/24): STT 의미 단위 재분할 + char_limit 자동 조정

### 진행 중 (없음 — WIP=1)

### Blocked / 대기
- **B03** Phase 1 fix-up #3 (schema text leak) — P2 not_started. xgrammar 외부 의존, 신 버전 대기.
- **B04** Phase 1 fix-up #2 (tail attention drop) — blocked, 정황 확인 필요 (backlog.md 그대로).
- **B05** Phase 4 capability profile — blocked, 모델 교체 결정 후 진입 예정. 2026-05-24 "모델 비의존" 방향 선회로 본 전제 우회한 맥락 catch.

## 문서 안내

| 문서 | 무엇 | 언제 보나 |
|------|------|---------|
| [HISTORY.md](./HISTORY.md) | 시간순 — 시작부터 현재까지 무엇이 일어났나 | "이 프로젝트는 어떻게 발전했나" |
| [DECISIONS.md](./DECISIONS.md) | 결정 — 갈림길에서 무엇을 골랐고 왜 | "왜 PySide6 폐기? 왜 Elastic License?" |
| [DEBUGGING.md](./DEBUGGING.md) | 추적 사슬 — 27b 느림 → 환경 오염 → ... → Phase 5 재분할 | "특정 버그/현상 추적 흐름" |
| [CHANGELOG.md](./CHANGELOG.md) | 버전별 변경 (기존 `CHANGELOG.md` + 백엔드 Phase 연계) | "v0.x.x에 무엇이 바뀌었나" |

저장소 다른 핵심 자료:
- `docs/backlog.md` — WIP=1 운영, B01~B06 추적
- `docs/quality.md` — 모듈별 등급 (STT A / LLM B+ / 후처리 A / 화자 B / UI 확인필요 / 검증 B)
- `docs/research/` — Phase 1~3 spec + 외래어 표기법 원본
- `docs/legacy/handoff/` — Phase 2A 사전 디자인 handoff
- `docs/legacy/webview-ui/{ARCHITECTURE,TECH_CHOICE}.md` — feat/webview-ui (4/20, 폐기) 결정
- `docs/wip/session_history_digest.md` — 18개 세션 사료 (4/19~5/24, 1차 자료)

## 핵심 결정 6개 (자세히 [DECISIONS.md](./DECISIONS.md))

1. **STT 엔진 여정 (VibeVoice → WhisperX → mlx-whisper)**: 초기 VibeVoice-ASR 채택 → RTX5090 32GB **OOM 32분 처리 시간** catch → **v0.4.0 WhisperX 전면교체** → Mac 사용자 위해 **v0.6.0 mlx-whisper 합류** → **AssemblyAI 완전 제거 → 완전 로컬** 결정. (큰 줄기)
2. **PyWebView + React 채택, PySide6 폐기** (4/19~4/27): "경로 C-1: PyWebView + HTML/CSS/JS + gurunote/* 로직 그대로 재사용" → Phase 1-B MVP 성공 → "Phase 2B-0: 신축 baseline 준비 (vanilla 폐기)" — feat/webview-ui 폐기, Phase 2B 진입.
3. **License MIT → Elastic 2.0 전환** (Phase 2A KICKOFF Decision 1): "최초 프로젝트 목적 망각 말고, 내 시간·노력 인정. 남들에게 다 퍼주는 게 마냥 좋은 건 아니다" — 본인 링크 대화 사료.
4. **2-pass DCCD + 화자 코드 부착** (`7a397fa`, `6b94a49`, 5/23): 1단계 자유 번역 (schema 부재) → 2단계 strict 정렬, 화자 라벨은 LLM 식별 1회 + 결정론 부착 — rule 1 prompt 충돌 근본 해소.
5. **STT 직후 의미 단위 재분할 + char_limit=2000 자동** (`527d2ea`, 5/24): Whisper segment 잘림이 D leak + 2-pass SHIFT + 본문 가독성의 공통 원인 → word-level 끝 검사 + 화자 우선 병합. **모델 비의존 하네스** 방향.
6. **Phase 4 capability profile 보류 → "모델 비의존" 우회**: B05 "모델 교체 결정 후 진입" 전제였으나, 5/24 재분할 + char_limit 통합으로 모델 capability 의존 부재 path 발견 → 본 전제 우회 catch.

## 다음 할 일

- **D 재평가**: 재분할 + char_limit 통합 후 2-pass SHIFT 44% 감소 catch — D segment 단독 번역이 여전히 필요한지 재평가.
- **마무리**:
  - 2-pass 토글 `GURUNOTE_TWO_PASS` default on 전환 (검증 catch 후).
  - 재분할 토글 `GURUNOTE_SEGMENT_RESPLIT` default on 결정 (daily 토글 비교 후).
  - README 갱신 (Phase 5 + 모델 비의존 path 반영).
  - `redesign/tailwind-v2` → `main` 머지.
- B03 schema text leak 후처리 (xgrammar 신 버전 도착 시).
- B04 tail attention drop 정황 catch (backlog 미해결 항목 확인).
- B05 capability profile — 모델 비의존 방향과 통합 결정.

---

**참고**: 본 일지는 2차 사료(요약·재구성)이다. 1차 자료는 `docs/wip/session_history_digest.md` (Claude Code 세션, 4/19~5/24) + git log (758 commit) + README/CHANGELOG. Phase 0 (4/11~18) 일부는 본인 기억(2차)으로 보강.
