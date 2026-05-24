# 후보 D prototype 측정 보고 (5/24)

표본: 화자 3명 영상 (oE5lNDhz9oo) chunks 7, 11, 12 = 45 segments
모델: Qwen3.6-35B-A3B-oQ6-mtp (약한 모델 대표)
HEAD: 599c94b
omlx: 32 concurrent + Chunked Prefill ON (이전 활성)

## Step 1 — omlx 동시성 실측

짧은 요청 (max_tokens=64, 영문 1줄 → 한국어 1줄):

| n  | wall(s) | 순차환산(s) | speedup | 이론대비 |
|----|---------|-----------|---------|---------|
| 1  | 0.27    | 0.27      | 1.00x   | 100%    |
| 4  | 1.60    | 1.07      | 0.67x   | 17%     |
| 8  | 2.15    | 2.14      | 1.00x   | 12%     |
| 16 | 3.04    | 4.29      | 1.41x   | 9%      |
| 32 | 4.95    | 8.58      | 1.73x   | 5%      |

catch:
- 짧은 요청은 prefill overhead 지배 (요청 자체 0.27s) — continuous batching 이득 작음.
- n=32 wall-clock 4.95s = n=1×8.58s 순차환산 대비 1.73x.
- 메모리상 "8x = 4.14배" 수치는 본 워크로드에서 catch 부재 (요청 길이 차이 추정).
- 이론 32x 대비 5% 효율 — 짧은 prefill 한정.

## Step 2~5 — D prototype 측정

표본: 45 segments
context K = 2 / 3
모드: 순차 / 병렬 (32 concurrent)

| 모드              | wall(s) | per-seg avg | empty | err |
|-------------------|---------|-------------|-------|-----|
| K=2, sequential   | 20.75   | 0.46        | 0     | 0   |
| K=2, parallel     | 13.33   | 7.83(*)     | 0     | 0   |
| K=3, sequential   | 21.04   | 0.47        | 0     | 0   |
| K=3, parallel     | 13.86   | 8.15(*)     | 0     | 0   |

(*) 병렬 per-seg avg는 wall-clock — 32개 동시 시작이므로 의미 부재.

병렬 speedup: K=2 1.56x / K=3 1.52x.

### (1) 정렬 — SHIFT 0 실증

- 입력 45 segments → 출력 45 lines (4 모드 전부).
- timestamp 1:1 매핑 catch — chunk 11 화자 전환 (C 8건 + A 7건), chunk 12 전환 (A 12건 + B 3건) 전부 정확.
- 2-pass에서 chunk 11 합침 catch (15 → 14 lines)이었지만 D는 부재.

### (2) 품질 — leakage / hallucinate

K=2 catch 1건:
- [365.7-373.3] STT 원본: `up, as well as the agent runtime itself, we call it Nemo claw, running in a secu`
- K=2 출력: "...네모 클로(Nemo Claw)가 보안이 강화된 오픈셸이라는 컨테이너 내에서 실행됩니다" — 다음 segment [373.3 `governed container called Open Shell`] 정보 흡수.
- K=3 출력: "업, 그리고 에이전트 런타임 자체인 네모 클로(Nemo Claw)는 안전하고" — STT 원본 그대로 부분 번역 (영어 잘림 그대로 catch).

→ K=3이 K=2보다 leak 차단 측면 우위. 단, STT 잘림 그대로 출력 catch (부자연스러움).

35b-A3B hallucinate 빈도:
- chunk 7 [320.7] "memory," → 두 K 모두 "메모리, 네트워크, 도구 접근, 작업 메모리, 장기 기억 접근" 식 확장 (context segments에 있는 명사들 흡수).
- chunk 11 [574.0] "If you ask Sanjay Mitra over at Micron, he'll tell you three years ago during a" → "그는 3년 전 회의에서 제가 한 말을 기억할 것입니다" / "저에게 이렇게 말했을 것입니다" — 다음 segment 내용 일부 흡수.

→ 두 K 다 약간 hallucinate. K 값 증가가 hallucinate 차단 부재 (오히려 context 정보 흡수 가능성).

### (3) 비용 — 현 2-pass 대비

- 2-pass 전체 영상 25 chunks = 378s → chunk당 평균 15.1s, 45 segments(3 chunks 분) 환산 ≈ 45s.
- D K=2 par 13.3s = 2-pass 대비 **3.4x 빠름**.
- D K=3 par 13.9s = 2-pass 대비 **3.2x 빠름**.

전체 영상 335 segments 환산:
- D K=3 par = 13.86 × (335/45) ≈ **103s** (병렬 32 catch 가정).
- 2-pass = 378s → 3.7x 빠름.

## D vs E 저울질

| 축 | D (segment + context + 병렬) | E (1단계 line==N + 코드 split) |
|----|-----------------------------|-------------------------------|
| 정렬 | 구조적 1:1 (SHIFT impossibility) — 측정 catch | 1단계 line 수 협조 의존 (35b-A3B 17% 극단, 39% 합침) |
| 품질 (hallucinate) | context K leak 위험 (35b-A3B 일부 흡수) | DCCD 자유번역 유지 + 강제 split — 의미 단위 보존 |
| 비용 | 35b-A3B로 103s/영상 (3.7x 우위) | 2-pass 378s 기존 |
| 모델 의존성 | 자기 자신 1건만 보면 됨 — 진짜 모델 비의존 | 1단계 line 수 협조 필요 — 모델 의존 잔존 |
| 화자 코드 부착 | 결정론적 catch | 결정론적 catch |
| 구현 복잡도 | _translate_chunk_two_pass 대체 — 큰 변경 | 1단계 prompt + 코드 split — 작은 변경 |

## 추천 (1차)

**D K=3 병렬** — 정렬 SHIFT 0 실증, 비용 3.7x 우위, 모델 비의존 원칙 부합.

단 보강 필요:
1. **K leak 차단 강화** — context segments를 영문 원본만 노출하고 `[CONTEXT]` 명시 prompt rule 강화 (현재도 "참고이며 번역 부재"인데 약함).
2. **35b-A3B hallucinate** — context segments 명사를 target에 흡수하는 경향. prompt 1줄 추가 (e.g. "context 명사 흡수 부재, 영어 원본 명사만 사용") 시도 후 재측정.
3. **STT 잘림 catch** — [365.7]처럼 영어 자체가 `secu` 로 잘리면 출력도 잘림. 인접 segment 합치는 코드 후처리 (자연어 완결 기준) 별도.

대안:
- D 1차 검증을 전체 335 segments 영상 1편 끝까지 돌려서 SHIFT 0 + hallucinate 분포 catch 후 결정 가능.
- 비용 측면 강한 우위는 catch — 본 검증은 chunk 3개 표본 한정.

## 다음 단계 후보

(가) 전체 영상 1편 D K=3 병렬 + 보강 prompt rule → SHIFT / hallucinate / 비용 종합 측정.
(나) D + E 혼합 — D 기본 + 1단계 line==N catch chunk에서만 E 코드 split (예외 catch 우위).
(다) llm.py 통합 시점은 위 (가) 이후 — 본 prototype 단계는 commit 부재.

## 산출물

- docs/wip/measure_omlx_concurrency.py
- docs/wip/candidate_d_prototype.py
- verify_results/candidate_d_k{2,3}_{seq,par}.md / .json (8개)
- verify_results/candidate_d_report.md (본 보고서)
