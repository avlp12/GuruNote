# GuruNote 결정 기록 (ADR — Architecture Decision Records)

> 갈림길에서 무엇을 골랐고 왜. 맥락(상황) / 결정 / 대안 / 이유 / 결과 구조. 채택된 결정 + 기각된 대안 둘 다 catch.

## 채택된 결정

### ADR-001. AssemblyAI 완전 제거 → 완전 로컬 STT (v0.4.0 ~ v0.6.0)

**맥락**: 초기 v0.1.0 — VibeVoice-ASR primary + AssemblyAI 클라우드 fallback. RTX5090 32GB에서 VibeVoice 처리 시 **OOM (32분 처리)** catch.

**결정**: AssemblyAI 완전 제거 → **완전 로컬 STT** (mlx-whisper Mac + WhisperX NVIDIA).

**대안**:
- A. VibeVoice 유지 + AssemblyAI fallback 적극 — 비용 + 클라우드 의존
- B. WhisperX 전면 교체 — Mac 사용자 부재
- C. (채택) v0.4.0 WhisperX 전면 + v0.6.0 mlx-whisper 합류 → AssemblyAI 제거

**이유**: 클라우드 의존 부재 + 사용자 데이터 외부 전송 부재 + 처리 시간 안정.

**결과**: 완전 로컬 catch. 2개 STT 백엔드 (Mac MLX / NVIDIA CUDA) 정합.

---

### ADR-002. PyWebView 채택, PySide6 폐기 (4/19~4/27)

**맥락**: v0.1.0 Streamlit → PR #4 CustomTkinter ("Tauri는 오버엔지니어링, 백엔드 직접 호출") → 4/19 다음 GUI 선택 시점.

**결정 (4/19 16:05, 본인 사료)**: **"경로 C-1 확정. PyWebView + HTML/CSS/JS + gurunote/* 로직 그대로 재사용"**.

**대안**:
- PySide6 — Python GUI 본격 (heavy)
- Tauri — 오버엔지니어링 catch (PR #4)
- Electron — 메모리/배포 큼
- (채택) PyWebView — Python ↔ JS bridge + 가벼움

**이유**: gurunote/* 로직 그대로 재사용, HTML/CSS/JS 자유, Python 단독 배포.

**결과**: 4/20 Phase 1-B MVP 성공 (PR #107). 단 **4/27 폐기** — ADR-003.

---

### ADR-003. PyWebView vanilla → React 신축 (4/27)

**맥락**: PyWebView Phase 1-B MVP 성공. 단 vanilla JS 신축 시 화면 신규 작업이 많아지고 catch 부족.

**결정 (4/27 07:32, 본인 사료)**: **"Phase 2B-0: 신축 baseline 준비 (미커밋 폐기 + Phase 1-C vanilla 폐기)"** — React 신축 진입.

**대안**:
- A. vanilla 유지 — 매 화면 직접 작성
- B. (채택) React + Material 3 + Babel — 컴포넌트 catch + 재사용
- C. Svelte / Vue — Material 3 catch 부족

**이유**: 5+ 화면 신축에 컴포넌트 catch 강력. React 생태계 자료 풍부.

**결과**: 4/27 ~ 5/2 Phase 2B-1 ~ 2B-6d 시리즈 514 commit + 5/9~11 Layer 1~15 정합.

---

### ADR-004. UI Commit 2 Revert + archive 작성 (4/25)

**맥락**: 4/22 Phase 2A Commit 2 (Material 3 sidebar) 시도. 4/23 02:33 본인 STOP. 4/25 Commit 2 재시도 → `4d7222f`. 단 본인이 검토 후 revert 결정.

**결정 (4/25 13:49, 본인 사료)**: **"Phase 2A — Commit 2 Revert + Commit 3a 준비"** + **"자산 영구 보존 위치 이동 + README + archive push"** (`archive/commit-2-aborted` 브랜치 작성).

**이유**: Commit 2 catch 후 본인이 결과 catch 부족 catch → 자산 보존 + 신축 path 진입.

**결과**: `archive/commit-2-aborted` 브랜치 catch. Commit 3a (자산 복원 + Babel 검증) 재시작.

---

### ADR-005. License MIT → Elastic 2.0 (4/24, Phase 2A KICKOFF Decision 1)

**맥락**: v0.x main MIT License catch. Phase 2A 진입 (Tailwind redesign).

**결정**: **MIT → Elastic License 2.0**.

**이유 (본인 링크 대화 사료)**: **"최초 프로젝트 목적 망각 말고, 내 시간·노력 인정. 남들에게 다 퍼주는 게 마냥 좋은 건 아니다."**

**결과**: LICENSE 파일 Elastic 2.0 catch. 사용자가 GuruNote 코드를 그대로 SaaS 호스팅 / 라이선스 우회 catch 부재.

---

### ADR-006. 2-pass DCCD + 화자 코드 부착 (5/23)

**맥락**: 1-pass에서 LLM이 segment N개를 다른 line 수로 출력 (drift). strict json_schema는 출력 강제 catch이지만 모델이 1줄 본문에 다음 segment 정보 합치는 catch (hallucinate). rule 1 prompt 추가 시 모델 충돌 catch.

**결정 (5/23, `39652c6` ~ `599c94b`)**: **DCCD (Draft-Conditioned Constrained Decoding)** — 1단계 자유 번역 (schema 부재) → 2단계 strict 정렬 (minItems=maxItems=N). 화자 라벨은 LLM 식별 1회 + 코드 결정론 부착 (rule 1 prompt 충돌 해소).

**대안**:
- A. rule 1 prompt 추가 (단일 통과) — 모델 충돌, 강한 모델만 catch
- B. (채택) 2-pass + 화자 코드 부착 — 모델 비의존 path
- C. 정렬을 코드로만 — 가능성 catch이지만 의미 단위 분할 catch 부족

**이유**: 모델 비의존 = 약한 모델에서도 SHIFT 차단. 화자 부착 = LLM 비결정성 catch 차단.

**결과**: 2-pass 1단계 정합 30% → 57~69% (3배). 빈 output 3단계 복구 시퀀스 추가.

---

### ADR-007. pyannote 3.1 → community-1 (5/23)

**맥락**: 화자 라벨 코드 부착 catch했지만 일부 영상에서 같은 화자가 chunk마다 다른 cluster catch (embedding drift). 3-speaker 영상에서 A 라벨에 두 화자 섞임 catch.

**결정 (`8ecd276`)**: pyannote 3.1 → **community-1** (pyannote.audio 4.0+ 정합).

**이유**: community 1 모델이 speaker confusion 마크 catch 감소 (pyannote 공식 catch).

**결과**: oE5lNDhz9oo 검증에서 A=Jensen / B=Michael / C=Ed Ludlow 3명 정확 catch.

---

### ADR-008. STT 직후 의미 단위 재분할 + char_limit=2000 자동 (5/24, Phase 5)

**맥락**: 5/23 화자 코드 + 2-pass catch했으나, 5/24 D segment 단독 번역 prototype catch에서 **context leak** 발견 ([365.7] "secure and" / [574.0] "during a meeting,"). 본질 진단: Whisper segment 잘림 = 음성 신호 기반 (의미 단위 부재). 같은 catch가 1-pass hallucinate + 2-pass SHIFT + 본문 가독성 + D leak 4개 단계 공통 catch.

**결정 (`527d2ea`)**: STT 직후 **word-level 의미 단위 재분할** + 재분할 적용 시 **chunk_size=12 + char_limit=2000** 자동.

**대안**:
- A. D 직전 합치기 (F) — 우회, 다른 단계 catch 부재
- B. (채택) STT 직후 1회 재분할 — 단일 진실 (단일 위치, 모든 단계 영향)
- C. context 모델 비의존 차단 (한국어 context 등) — 병렬 손실

**이유**: 모델 비의존 catch — Whisper segment 잘림 동기 (음성 기반)을 코드로 차단. 4개 단계 (D leak / 2-pass SHIFT / 1-pass hallucinate / 가독성) 동시 catch.

**결과**:
- D leak 해소 ([365.7] [574.0] 두 사례)
- 2-pass 1단계 합침 16 → 9 (44% 감소), 정합 30→57~69%
- 1-pass timeout 6 → 1 (긴 영상 catch)
- 다영상 6개 검증 + 통합 본체 검증 (HEAD 527d2ea catch)

**토글**: `GURUNOTE_SEGMENT_RESPLIT` 기본 off — daily 검증 후 default on 결정.

---

### ADR-009. Phase 4 capability profile 보류 → "모델 비의존" 우회 (5/24)

**맥락**: backlog B05 — Phase 4 capability profile (모델별 max_ctx, supports_tool_call, korean_quality 추적) — "모델 교체 결정 후 진입" blocked 상태. 현재 qwen3.6-35b-q5 고정.

**결정 (5/24)**: **B05 본 전제 (모델 교체) 우회** — Phase 5 (재분할 + char_limit)이 모델 capability 의존 부재 path catch. capability profile 본 시점 진입 부재.

**이유**: 모델별 catch (max_ctx, korean_quality 등)에 처리 결과를 맞추는 게 아닌, **입력(segment)을 정제해서 모델 편차를 줄이는** path catch. 약한 모델 (35b-A3B)에서도 catch.

**결과**: B05 blocked 유지. "모델 비의존" 방향과 통합 결정은 추후.

---

## 기각된 대안

### REJ-001. VibeVoice / Nemotron Omni 통합 모델 (시점 기록 부재)

**평가**: 한국어 ASR 정확도 + 로컬 실행 + 화자 분리 분리성 catch.

**기각 이유**: 셋 다 catch 부족.

**재평가**: 2026-10 (Appendix B, 본인 기억).

---

### REJ-002. dense 모델 가설 (5/22 시점 추정)

**맥락**: MoE (qwen3.6-35b-A3B-oQ6) catch 부족 의심 — dense 모델 (qwen3.6-35b-q5)으로 fallback 평가.

**기각 이유**: 다영상 검증에서 둘 다 catch + 2-pass + 재분할 catch path가 모델 종류 비의존 catch. dense 가설 부재.

---

### REJ-003. rule 1 prompt 조정 (5/23 직전)

**맥락**: 2-pass 2단계 정렬 prompt에 rule 1 (drift 차단) 추가 시도.

**기각 이유**: 모델 충돌 catch — 강한 모델만 catch, 약한 모델 출력 부재 위험. **모델 비의존 path 부재** — 본인 결정 (5/23 보강 시리즈 catch).

**대체**: A1 (rule 1 강화) + A5 (prefix strip) 보강 (`7a397fa`).

---

### REJ-004. 모델 자동 감지 (5/24, Phase 5 진단)

**맥락**: 재분할 후 1-pass timeout 증가 catch (긴 영상). 토글 / 모델 capability 자동 감지 후보.

**기각 이유**: 모델 capability 자동 감지 = 추정 위험 + 복잡. **단일 진실 (재분할 + char_limit=2000 default on)** path 채택.

**대체**: char_limit=2000 자동 적용 (`527d2ea`).

---

### REJ-005. (시점 부재 - 본인 기억) Streamlit 유지

**기각 이유**: 데스크톱 앱 catch 부족 — 백엔드 직접 호출 path 부재. PR #4에서 CustomTkinter로 전환.

---

## 결정 영향 catch 표

| 결정 | 영향 모듈 | 시간 |
|------|---------|------|
| ADR-001 완전 로컬 | gurunote/stt.py, stt_mlx.py | v0.4.0 ~ v0.6.0 |
| ADR-002 PyWebView | gurunote/webui/ (신규) | 4/19~ |
| ADR-003 React 신축 | webui/components/* | 4/27~5/2 |
| ADR-004 Commit 2 Revert | archive/commit-2-aborted | 4/25 |
| ADR-005 Elastic 2.0 | LICENSE | 4/24 |
| ADR-006 2-pass DCCD | gurunote/llm.py | 5/23 |
| ADR-007 community-1 | gurunote/stt_mlx.py | 5/23 |
| ADR-008 STT 재분할 | gurunote/stt_mlx.py, llm.py, tests/test_segment_resplit.py | 5/24 |
| ADR-009 Phase 4 보류 | backlog.md (B05 blocked 유지) | 5/24 |

---

**자료 한계 명시**: REJ-001/REJ-002/REJ-005 시점 일부 본인 기억 2차 사료. ADR-001/004/006/007/008은 commit hash + session_history_digest 1차 사료.
