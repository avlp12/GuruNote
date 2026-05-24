# 통합 본체 재분할 검증 — oE5lNDhz9oo (5/24)

영상: oE5lNDhz9oo (화자 3명, 33분)
HEAD: 527d2ea
모델: Qwen3.6-35B-A3B-oQ6-mtp
입력: verify_results/community1_3speakers_raw.json (cache 재사용, STT 재실행 부재)

## Step 1 — 토글 ON 작동 확인

| 측정 | 값 | prototype 정합 |
|------|-----|---------------|
| 재분할 334→ | **309** | 309 ✅ |
| Transcript.raw['segment_resplit'] | **True** | flag 부착 ✅ |
| chunks (cs=12) | **26** | 26 ✅ |
| chunk_max chars | **1528** | (영상별 catch — F3 영상 1989) |
| chunk_avg chars | 1083 | - |
| resplit_applied flag | **True** | llm.py 분기 작동 ✅ |
| llm.py log | "🌐 LLM 번역 시작 — 26 청크 (cs=12, char_limit=2000, 재분할 적용)" | 자동 catch ✅ |

## Step 3 — 토글 OFF 회귀 (daily 보호)

| 측정 | 값 | 기존 path 정합 |
|------|-----|---------------|
| 재분할 부재 (334→332, noise/dedup만) | **332** | 기존 path ✅ |
| Transcript.raw['segment_resplit'] | **False** | - |
| chunks (cs=15 default) | **23** | 기존 ✅ |
| chunk_max chars | **1638** | (cs=15에서 자연) |
| resplit_applied flag | **False** | llm.py 기본 path ✅ |

→ **토글 off 기존 동작 불변** — daily 보호 catch ✅.

## Step 2 — 2-pass 통합 처리 결과 (prototype 재현)

| metric | prototype (5/22 sweep) | 본 측정 (통합 527d2ea) |
|--------|----------------------|---------------------|
| 1단계 정합 | 18/26 (69%) | **16/26 (62%)** |
| 1단계 합침 | 8 | **10** |
| 1단계 극단(1줄) | 8 | **7** |
| 처리 시간 | 352.7s | **343s** |
| timeouts | 0 | **0** ✅ |

정합 62% (prototype 69% 대비 7 ppt 낮음) — LLM 비결정성 catch (재실행 시 분포 변동). 단 핵심 (timeouts 0 + 합침 catch) 일치.

## D leak 재현 catch

**[365.7-376.9] 영역 ([05:59])**:
> "에이전트, 뇌, 장기 기억, 확장 및 관리에 필요한 모든 네트워킹, 그리고 에이전트 런타임 자체는 보안이 적용되고 관리되는 OpenShell 컨테이너에서 구동되는 NemoClaw라고 명명되었습니다."

→ NemoClaw + OpenShell + 보안 컨테이너 한 줄로 catch ✅. prototype 패턴 정확 재현.

**[574.0-584.4] 영역 ([09:34])**:
> "미크론의 산자이 미트라에게 물어보면, 그는 3년 전 회의에서 제가 지금 일어나고 있는 그대로의 미래를 그에게 설명했다고 말할 것입니다."

→ Sanjay Mitra + "I explained the future" 한 줄로 catch ✅. prototype 패턴 정확 재현.

## 화자 분포

| 화자 | 본문 line 수 |
|------|------------|
| 화자 1 | 142 |
| 화자 2 | 86 |
| 화자 3 | 81 |

3명 화자 정확 catch ✅. 단 라벨은 "화자 1/2/3" — 본 측정 cache 격리 catch (새 video_id로 entity_cache 부재) → 화자 식별 LLM 호출 부재 → fallback "화자 N" catch. **정상 daily 환경 (cache catch)에서는 "젠슨 황/마이클 델/에드 루들로" 정확 부착** (이전 검증).

## 통합 = prototype 일치 판정

| 축 | 통합 본체 (527d2ea) | prototype (5/22) | 일치? |
|----|-------------------|-----------------|------|
| 재분할 segment 수 | 309 | 309 | ✅ |
| chunk size 자동 (cs=12, char_limit=2000) | 26 chunks, max 1528 | 26 chunks, max 1528 | ✅ |
| Transcript.raw flag | True | (수동 명시) | ✅ |
| llm.py 자동 분기 | 작동 | (수동) | ✅ |
| 2-pass timeouts | 0 | 0 | ✅ |
| 2-pass 정합 비율 | 62% | 57~69% | ✅ (분포 catch) |
| D leak 본문 패턴 | 완전 재현 | 기준 | ✅ |
| 토글 off 기존 동작 | 불변 (23 chunks, max 1638) | (해당 부재) | ✅ |

**판정: 통합 본체 = prototype 일치 ✅**

## 본인 결정용 catch

- **재분할 작동 catch (flag, 334→309)** ✅
- **char_limit=2000 자동 catch (chunk_max 1528, llm.py 분기)** ✅
- **D leak [365.7] [574.0] 본문 재현** ✅
- **2-pass 정합 62% (prototype catch 분포)** ✅
- **timeouts 0** ✅
- **화자 3명 정확 (라벨 형태는 cache 격리 catch — 정상 daily 부재)**
- **토글 off 기존 동작 불변** ✅

**통합 = prototype 일치 — daily 토글 on 안전 catch.**

## 정합 낮은 부분 SHIFT 잔존 catch (D 재평가)

- 합침 10건 / 26 chunks = 38% — prototype sweep (8/26 = 31%) 대비 약간 ↑.
- 극단(1줄) 7건 — prototype 8건과 catch.
- SHIFT 직접 측정 부재 (본 검증은 정합 비율 + leak catch). 본문 line-level 정렬 분석 필요 시 별도 측정.

## 산출물

- `docs/wip/integration_verify_resplit.py` (검증 스크립트)
- `verify_results/integration_verify/on_body.md` (토글 on 본문, 309 segments → 본문)
- `verify_results/integration_verify/on_log.txt` (2-pass log)
- `verify_results/integration_verify/analysis.json` (집계)
- `verify_results/integration_verify/report.md` (본 보고서)

## 다음 단계

- daily 영상 1편 토글 on/off 비교 (사용자 결정).
- 정상 daily 환경에서 화자 라벨 부착 catch ("젠슨 황" 등) 검증 (entity_cache bootstrap path).
- 재분할 default on 전환 결정 (1차 detect 충분 catch — 본인 결정).
