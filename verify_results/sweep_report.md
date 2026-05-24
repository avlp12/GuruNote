# chunk size 자동 조정 prototype 보고 (5/24)

영상: oE5lNDhz9oo (재분할 309 segments)
모델: Qwen3.6-35B-A3B-oQ6-mtp
HEAD: 599c94b

## Step 1 — chunk size 위치 + segment 평균 길이

chunk size 정의 (`gurunote/llm.py:460`):
- `MAX_SEGMENTS_PER_CHUNK = 15` (segment 수 한도, 1-pass/2-pass 공통)
- `DEFAULT_CHUNK_CHAR_LIMIT = 12_000` (문자 한도 safety net)
- `chunk_segments()` 두 한도 중 먼저 도달 시 분할 — segment 수가 보통 먼저 도달 catch.

segment 평균 text 길이:
- 원본: **56.8 chars** (332 segments)
- 재분할: **61.1 chars** (309 segments)
- 비율: **1.08배** (작음, 의외)
- 최대: 둘 다 249 chars 동일

cs별 chunk 단위 길이 (재분할 segments 기준):

| cs | chunks | 평균 chars | 최대 chars |
|----|--------|----------|----------|
| 15 | 21 | 1341 | 1631 |
| 12 | 26 | 1083 | 1528 |
| 10 | 31 | 908 | 1251 |
| 8 | 39 | 722 | 1042 |

chunk 자체는 매우 작음 (1631 chars ≈ 408 tokens 추정 — 8192 max_tokens 대비 5%). chunk size 자체가 LLM 처리 부담의 직접 원인 부재 추정 — 실제 catch는 측정 필요.

## Step 2 — 1-pass chunk size sweep

| cs | time(s) | body lines | timeouts | length_mismatch | 비고 |
|----|---------|-----------|----------|-----------------|------|
| 15 (기준) | 468.0 | 616 | **2** | **1** | timeout 발동 (cs=15 재분할 측정, 5/24) |
| 12 | **275.2** | 652 | **0** | **0** | **timeout 해소 + 원본 1-pass(266s)와 거의 동일 (3% 차이)** |
| 10 | 320.4 | 616 | 0 | 0 | timeout 해소, 단 chunks ↑로 약간 느림 |
| 8 | 480.7 | 616 | 0 | 0 | chunks 너무 많아 overhead로 느림 |

**catch — cs=12에서 1-pass timeout 0건 + 시간 원본 수준 회복 (275s ≈ 원본 266s)**.

원본 1-pass (재분할 부재, cs=15) = 266s vs 재분할 + cs=12 = 275s (3.4% 증가만). **1-pass 시간 증가 76% → 3.4%로 해소**.

cs=8은 chunks 39개로 늘어나 inter-chunk overhead로 다시 느려짐 (480s) — chunk 수 ↑가 새로운 부담.

## Step 3 — 2-pass chunk_size=12 측정 (정상 완료)

| metric | 원본 cs=15 (이전 측정) | 재분할 cs=15 (이전) | 재분할 cs=12 (본 측정) |
|--------|---------------------|-------------------|---------------------|
| 총 chunks | 23 | 21 | **26** (309/12) |
| 1단계 line==N (정합) | 7/23 (30%) | 12/21 (57%) | **18/26 (69%)** |
| 1단계 line<N (합침) | 16 | 9 | **8** |
| 극단 (1줄, N>5) | 13 | 9 | **8** |
| timeouts | 1 | 1 | **0** |
| 처리 시간 | 419.8s | 361.3s | **352.7s** |
| 본문 line | 662 | 616 | 616 |

**catch — 2-pass cs=12 = 원본 cs=15 대비 1단계 정합 30% → 69% (2.3배), 합침 16 → 8 (50% 감소), 처리 시간 419.8s → 352.7s (16% 단축), timeout 0**.

재분할 cs=15 대비도 정합 57 → 69%, 합침 9 → 8, 시간 361 → 352s (2.4% 단축). chunk size 축소가 **2-pass 이득 추가 + 시간 약간 단축** catch.

## Step 4 — 균형점 + 단일 진실 판정

**catch 정리**:

| 축 | cs=15 재분할 | cs=12 재분할 | 효과 |
|----|------------|-----------|------|
| 1-pass time | 468s (timeout 2건) | **275s (timeout 0)** | 1-pass 시간 회복 ✅ |
| 2-pass 1단계 정합 | 57% | **69%** | 추가 ↑ ✅ |
| 2-pass 1단계 합침 | 43% | **31%** | 추가 ↓ ✅ |
| 2-pass time | 361.3s | **352.7s** | 약간 단축 ✅ |
| 2-pass timeouts | 1 | **0** | timeout 해소 ✅ |
| D leak | 해소 (이미 catch) | 해소 (영향 부재) | ✅ |
| 본문 가독성 | ↑ (이미 catch) | ↑ | ✅ |

**균형점 catch — cs=12가 1-pass timeout 해소 + 2-pass 이득 추가**.

## 자동 조정 공식 — 후보

평균 길이 비례:
- 원본 평균 56.8 → 재분할 61.1 (1.08배). cs 비례 감소 가설 = 15/1.08 ≈ 14 — 본 측정 catch 부재 (cs=14 미측정).
- 평균 비례만으로는 cs=15→12 (1.25배 감소) catch 부재.

실제 원인 catch:
- chunk 단위 LLM 처리 시간이 chunk 크기에 **비선형** catch 가능성 — 일부 chunk(긴 segment 집중)가 폭주.
- 평균 길이는 1.08배인데 timeout 발생 chunk는 segment 길이 분포의 우측 꼬리 catch.

권장 공식 (단순):
- **재분할 시 chunk_size 기본 12 (1-pass/2-pass 공통)**.
- 또는 chunk_size_after_resplit = floor(15 / safety_factor), safety_factor = 1.25.
- 본 영상 1.08배 평균 증가에서 1.25 safety 적용. 다른 영상 측정 필요 (보수적 default).

## daily 영향 + 토글

- prototype 한정 (docs/wip/). stt_mlx.py / llm.py 수정 부재.
- 통합 시: `MAX_SEGMENTS_PER_CHUNK = 15` → 재분할 토글 on 시 12로 자동 조정. envvar `GURUNOTE_RESPLIT_CHUNK_SIZE` 권장 (기본 12, 사용자 조정 catch).
- daily 1-pass + 2-pass 둘 다 catch — 단일 진실 유지.

## 추천

**1차 — chunk_size=12 + 재분할 default on (단일 진실)**:
- 1-pass 시간 거의 원본 수준 회복 (3.4% 증가).
- 2-pass 정합 비율 추가 ↑ (57 → 69%).
- 토글 분기 부재 — 단일 진실 catch.

**자동 조정 공식 단순화**: `chunk_size = 12 (재분할 on 시)`. 보수적 default. 더 정교한 공식은 추후 다영상 측정.

**미완료 catch**:
- cs=14 측정 부재 (1.08배 평균에서 14가 catch 가능성). 단 cs=12 catch가 충분.

## 산출물

- `docs/wip/resplit_chunk_size_sweep.py` (sweep 스크립트)
- `verify_results/sweep_1pass_cs{12,10,8}_{body,log}.{md,txt}` (1-pass 3개)
- `verify_results/sweep_2pass_cs12_{body,log}.{md,txt}` (2-pass)
- `verify_results/sweep_analysis.json` (집계)
- `verify_results/sweep_report.md` (본 보고서)

commit 부재 (prototype 단계).

## 다음 단계 후보

1. **stt_mlx.py + llm.py 통합** — 재분할 + chunk_size 12 default + envvar 토글.
2. **다영상 측정** — 본 영상은 평균 1.08배, 다른 영상은 다를 수 있음. chunk_size 12가 일반화 가능 catch.
