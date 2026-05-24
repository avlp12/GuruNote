# GuruNote 18개 세션 정리 보고 (5/24)

산출물:
- `docs/wip/session_history_digest.md` (45KB) — 세션별 user 메시지 timeline + 마스킹
- `docs/wip/_session_digest.py` — 처리 스크립트

세션 위치: `~/.claude/projects/-Users-gesicht-GuruNote/` (18개 jsonl)
기간: **04/19 13:59 ~ 05/24 08:18** (1개월+)
처리: 세션별 독립 파싱, user 메시지만 추출, 토큰/키 마스킹 (hf_/sk-/Bearer/ghp_/AKIA)

## 18개 세션 시간순 요약

| # | 일자 | 크기 | UUID 앞 8자 | 브랜치 | user msg | 작업 catch |
|---|------|-----|-----------|--------|---------|----------|
| 1 | 04/19~21 | 2.9MB | 403f391c | feat/webview-ui, main, redesign/handoff-phase1, refactor/hf-token-env | 42 | PyWebView 진단 + Phase 1-B MVP + PR #107 + 외부 11 commit 정체 확인 |
| 2 | 04/21~22 | 511KB | 503df718 | 추적 부재 | (소량) | UI 작업 catch 도중 |
| 3 | 04/22 | 190KB | 66f6b5aa | 추적 부재 | 19 | (4/22 새 세션 catch) |
| 4 | 04/22~23 | 3.0MB | 0a6d4ad3 | 추적 부재 | 다수 | UI Commit 1~2 + 4/23 02:33 "STOP. 진행 중단. 3번 No" |
| 5 | 04/24 | 80KB | 1d359be2 | 추적 부재 | 소량 | Phase 2A 공식 시작 + HANDOFF_MORNING |
| 6 | 04/25 | 386KB | 4d218049 | 추적 부재 | 다수 | Phase 2A Commit 2 → Revert + Commit 3a 준비 |
| 7 | 04/29 | 5.4MB | b89370f2 | 추적 부재 | 다수 | Phase 2B 시리즈 (Layer 8 catch 추정 시기) |
| 8 | 05/02 | 5.9MB | a43a7d33 | 추적 부재 | 다수 | Phase 2B-3-backend Step 시리즈 |
| 9 | 05/08~10 | 5.8MB | a69c00cb | 추적 부재 | 다수 | **Layer 1~7 fix 진입** (본질 진단 시점) |
| 10 | 05/10 | 738KB | f931e0a1 | 추적 부재 | 다수 | Layer 13~14 후속 |
| 11 | 05/14 09:25 | 1.3MB | 8182332f | 추적 부재 | 다수 | 5/14 정전 대비 + Phase 1 Redesign 시작 |
| 12 | 05/14 09:38 | 5.9MB | a69c00cb (dup ID) | 추적 부재 | 다수 | Phase 1 Redesign 본격 |
| 13 | 05/14 16:18 | 45KB | f8ea8213 | 추적 부재 | 소량 | 후속 |
| 14 | 05/15 | 594KB | 9ec081ef | 추적 부재 | 다수 | Phase 2 entity_cache 시작 |
| 15 | 05/17 | 2.0MB | 4e1f874a | 추적 부재 | 다수 | **Phase 4a-1 xgrammar verify 4회** |
| 16 | 05/17 | 71KB | d4ef55d7 | 추적 부재 | 소량 | 후속 |
| 17 | 05/20 | 2.7MB | 5271e092 | 추적 부재 | 다수 | **판카지 회귀 + B02 + B06** |
| 18 | 05/20 18:03 | 6KB | f55eac0b | 추적 부재 | 소량 | 단기 |
| 19 | 05/24 (오늘) | 12.4MB | 1524869f | redesign/tailwind-v2 | 다수 | **Phase 5 재분할 시리즈** |

*(18개 = 16개 활성 + 2개 짧은 break catch — 본 표는 19개 행 catch이지만 두 세션이 UUID dup 카운트 catch)*

## 빈 곳 8개 메움 현황

### ✅ 1차 빈 곳 1: Phase 0~1 초기 결정 — **부분 catch**

- 최초 세션 4/19 13:59 — **Phase 0 (4/11~12)는 본 catch 부재** (Claude Code 도구 사용 부재 또는 별도 세션)
- 4/19 13:59 "이 프로젝트를 https://github.com/avlp12/GuruNote 에 커밋/PR 할 예정" — repo 첫 catch 시점
- **4/19 15:53 "PyWebView 현실적 제약도 같이 조사"** + **4/19 16:05 "경로 C-1 확정. PyWebView + HTML/CSS/JS + gurunote/* 로직 그대로 재사용"** — webview 채택 동기 ✅

→ Phase 0~1 v0.x (4/11~17)는 본 세션 부재. README/CHANGELOG/git log 자료만.

### ✅ 1차 빈 곳 2: feat/webview-ui 폐기 동기 — **catch**

- 4/19 16:05 — PyWebView 채택 결정
- 4/20 11:03 "Phase 1-B 진입 전 외부 11 commit 정체 확인 먼저" — 본인 신중함 catch
- **4/20 14:43 "Phase 1-B MVP 완전 성공. end-to-end 검증 완료"** — MVP 성공 catch
- 4/20 15:11 — PR #107 (PyWebView UI Phase 1-B) 작성
- **4/27 07:32 "Phase 2B-0: 신축 baseline 준비 (미커밋 폐기 + Phase 1-C vanilla 폐기)"** — vanilla 폐기 시점 catch ✅
- 폐기 동기 본 catch 명확: vanilla→React 전환, 신축 baseline 진입

### ✅ 1차 빈 곳 3: Commit 2 aborted — **catch**

- 4/22 05:59 "A. UI Commit 시작. 다만 Commit 2 (목록 view) 만. Commit 3 (detail) 은 오늘 안 함" — Commit 2 catch
- 4/23 02:33 "[Request interrupted by user] STOP. 진행 중단. 3번 (No) 선택" — 4/23 중단 시점 ✅
- 4/25 13:49 "Phase 2A — Commit 2 Revert + Commit 3a 준비" — **Commit 2 revert 시점 catch** ✅
- 4/25 13:58 "Commit 2 Revert 후속: 자산 영구 보존 위치 이동 + README + archive push" — **archive/commit-2-aborted 브랜치 작성** ✅
- 4/25 14:11 "Phase 2A Commit 3a — Step 3a-1: 자산 복원 + Babel 검증" — 재시작

### △ 1차 빈 곳 4: License MIT → Elastic — **catch 부재**

- user 메시지에 License/Elastic/MIT 직접 catch 부재
- KICKOFF_PHASE_2A.md에 "Decision 1: License 전환" 항목 catch (자료만)
- 동기는 자료 + 세션 모두 부재 — 본인 결정 catch (대화 외 자료에 catch 가능, 별도 sources)

### ✅ 1차 빈 곳 5: Phase 2B 신축 결정 — **catch**

- 4/27 07:32 — **Phase 2B-0 baseline 준비 (vanilla 폐기)**
- 4/27 07:47 — Phase 2B-1 Sidebar + App + 5 화면 placeholder
- 4/27 08:16 — **"Phase 2B-1 재시작: Sidebar 우리 코드로 신축 (cp 폐기)"** — cp 폐기 catch ✅
- 4/27 08:38 — Phase 2B-2 MainScreen
- 4/27 10:41 — Phase 2B-3 HistoryScreen
- 4/27 11:17 — Phase 2B-3a-fix list_history pywebview dict-arg 호환 (실제 catch 시점)
- 4/27 12:38 — Phase 2B-3b 검색 바 + 필터
- 시리즈 timeline catch ✅

### ✅ 1차 빈 곳 6: Layer 1~15 발견 동기 — **catch (Layer 1~7 catch, Layer 8~15 부분)**

- 5/8 15:43 — **"Phase 2B-3-backend Step 3b-2 보류 + 본질 진단 진입"** — Layer 작업 진입 시점 ✅
- 5/8 16:09 — Layer 1 fix 진입
- 5/9 00:12 — **"Layer 1 fix 작동 부재 — 진단 진입"** — 본인 catch
- 5/9 00:58 — **"본질 catch 정정 — 라이브러리 vs 모델 영역 분리"** — Layer 1 동기 catch
- 5/9 07:58 — Layer 5 fix 진입 (LLM hallucination cascading 진단)
- 5/9 08:08 — Layer 5 추가 진단 (A/B/C 옵션)
- 5/9 08:27 — Layer 5 + Layer 6 fix spec 결정
- 5/9 09:45 — Layer 7 fix 진입
- 5/9 10:10 — Layer 7 fix spec 정정 (History 미리보기 + CreateScreen)
- **5/9 14:35 "티파니 잰슨이 아니라 티파니 잔젠 (Tiffany Janzen). 내가 실수했거나 클로드가 실수한 것 같다. 특별한 지정 없는 한 외국인 인명 표준 표기법에 따를 것"** — Layer 8 동기 catch ✅ (사용자 실측 catch 시점)
- Layer 8~15는 본 세션 9 (a69c00cb) + 10 (f931e0a1) catch — 추가 세션 깊이 catch 필요

### △ 1차 빈 곳 7: Phase 4 capability profile — **catch 부재**

- **Phase 4a-1 (xgrammar selective disable)** catch: 5/16 18:18 마무리 + 5/17 00:51 commit 보류 + verify 4회 반복
- **Phase 4 (B05 capability profile)** blocked 동기 catch **부재** — backlog "모델 교체 결정 후 진입" catch만

### △ 1차 빈 곳 8: 공급망 보안 (osv-scanner/SRI) — **catch 부재**

- user 메시지에 osv/SRI/supply 매칭 부재
- README/CHANGELOG v0.8.0.x 자료 catch — 본 세션 catch 부재 가능성 (다른 세션 또는 외부 작업)

### 추가 catch (보너스)

- **5/20 08:20 "판카지 샤르마 회귀 진단 우선"** — B06 entity_cache 회귀 catch 시점 ✅
- 5/20 09:13 "두 사안 진단 — 판카지 회귀 원인 + B02 복구 path 옵션" — 본인 결정 흐름 catch
- 5/17 13:58 "티파니 잔젠 hallucinate 여부 재검증" — Layer 8 후속 검증
- 5/14 정전 대비 시점 (HANDOFF_POWER_OUTAGE_2026-05-14.md 자료 catch)

## 통합 timeline (4/19 ~ 5/24)

```
04/19   PyWebView 채택 (경로 C-1) + repo 첫 push
04/20   Phase 1-B MVP 성공 + PR #107
04/21   refactor/hf-token-env + UI 폐기 후보 분기
04/22   UI Commit 1~2 시작 (Tailwind 신축 시도)
04/23   STOP. 진행 중단 (Commit 2 aborted catch)
04/24   Phase 2A 공식 시작
04/25   Commit 2 → Revert → archive/commit-2-aborted + Commit 3a 재시작
04/27   Phase 2B-0 baseline (vanilla 폐기) → 2B-1/2/3a/3b 신축 시리즈
04/29   Phase 2B-3 후속 (5.4MB 세션)
05/02   Phase 2B-3 Step 시리즈 (5.9MB 세션)
05/08   Phase 2B-3-backend Step 3b-2 보류 → Layer 1 fix 진입 (본질 진단)
05/09   Layer 1 작동 부재 → 본질 catch 정정 → Layer 5+6+7 시리즈
        + 14:35 "Tiffany Janzen 표기 catch" (사용자 catch — Layer 8 동기) ✅
05/10   Layer 13~14 후속
05/14   정전 대비 + Phase 1 Redesign 시작
05/15   Phase 2 entity_cache 시작
05/17   Phase 4a-1 xgrammar verify 4회 반복 + 본질 cause 분석
05/20   '판카지 샤르마' 회귀 catch (B06 동기) + B02 timeout 진단
05/24   Phase 5 (재분할 + chunk_size + 다영상 + 통합)
```

## 본인 결정용 catch

- **자료 수집 catch ✅** — 4/19 ~ 5/24, 18개 세션, user 메시지 timeline.
- **빈 곳 1/2/3/5/6 catch ✅** — PyWebView 채택/폐기, Commit 2 aborted, Phase 2B 신축, Layer 1~7 발견 동기, Tiffany Janzen catch 시점.
- **빈 곳 4 (License), 7 (Phase 4 blocked), 8 (공급망 보안) 부분 catch 또는 부재** — 본인 추가 자료 catch 필요 (다른 세션 또는 외부 자료).
- **Phase 0~1 초기 (4/11~17)** — 본 세션 부재. README/CHANGELOG/git log 자료만 catch.

## 출력 파일

- `docs/wip/session_history_digest.md` (45KB, 18 세션 × user 메시지 catch + 마스킹)
- `docs/wip/SESSION_HISTORY_REPORT_2026-05-24.md` (본 보고서)
- `docs/wip/_session_digest.py` (처리 스크립트)

## 토큰 마스킹 검증 ✅

- 출력 안 hf_/sk-/Bearer/ghp_/AKIA 잔재: **0건** (정밀 grep catch)
- MASKED 패턴 catch: 1건 (실제 본문 catch 위치)
- 안전 catch — daily 노출 부재.

read-only 종료. 출력 파일 commit 부재 (본인 결정 catch 후 별도).
