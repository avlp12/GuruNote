# char_limit=2000 검증 보고 (F3QDC7HDMyg, 5/24)

영상: F3QDC7HDMyg (38분, 화자 2, 재분할 377 segments, segment max 662 chars)
모델: Qwen3.6-35B-A3B-oQ6-mtp
HEAD: 599c94b

## chunk 분포

| 설정 | chunks | chunk_max chars | chunk_avg chars |
|------|--------|-----------------|-----------------|
| char_limit=12000 (cs=12 default) | 32 | **5061** | 1588 |
| char_limit=2000 (cs=12) | 35 | **1989** | 1452 |
| char_limit=1500 (cs=12) | 39 | 1494 | 1303 |
| char_limit=1000 (cs=12) | 58 | 992 | 876 |

char_limit=2000: chunks 32→35 (+3, +9%), chunk_max **5061→1989 (61% 감소)** ✅ 임계 내.

## 1-pass + 2-pass 비교

| metric | cl=12000 (이전) | cl=2000 (본 측정) | 개선 |
|--------|---------------|-------------------|------|
| chunks | 32 | 35 | +3 |
| chunk_max chars | 5061 | 1989 | -61% |
| **1-pass time** | 838s | **475s** | **-43%** ✅ |
| **1-pass timeouts** | 6 | **1** | -83% ✅ |
| 1-pass length_mismatch | 1 | 0 | -100% ✅ |
| **2-pass time** | 644s | **511s** | -21% ✅ |
| 2-pass timeouts | 0 | **0** | 동일 ✅ |
| 2-pass 정합 | 14/32 (44%) | 14/35 (40%) | -4 ppt (감소) |
| 2-pass 합침 | 18 | 20 | +2 |
| 2-pass 극단(1줄) | 8 | 11 | +3 |

## 핵심 catch

1. **1-pass timeout 6→1 (83% 감소)** ✅ — chunk_max 5061→1989로 LLM 처리 부담 catch.
2. **1-pass 시간 838s→475s (43% 단축)** ✅ — retry 5건 회피.
3. **1-pass length_mismatch 1→0** ✅.
4. **2-pass timeout 0 유지** ✅ — 영향 부재.
5. **2-pass 시간 644s→511s (21% 단축)** ✅ — 빈 output 복구 시퀀스 영향 작음.
6. **2-pass 정합 약간 감소** (44%→40%) — chunks 더 쪼개진 영향, 단 본 영상 자체 정합 비율 낮음 (다른 영상 32~67%).
7. **timeout 완전 해소 부재** — 1건 잔존. char_limit=1500/1000 더 작은 값 필요 가능.

## char_limit=2000 확정 여부

**부분 확정** — 1-pass에서 timeout 83% 감소, 시간 43% 단축으로 catch 큰 개선. 단 완전 해소 부재 (1건 잔존).

- timeout 1건은 잔존 catch — chunk_max 1989 chars인데도 LLM이 60초 초과.
- 원인 추정: chunk 안 segment 내용 자체 복잡 (긴 영어 + 전문 용어 + 35b-A3B 약한 모델 grammar-recovery loop 가능).
- char_limit 더 축소 (1500 또는 1000)으로 추가 해소 catch 가능, 단 chunk 수 증가 부담.

다른 5개 영상 부작용:
- 이전 측정 chunk_max ≤ 1716 (모두 2000 이하) → char_limit=2000 자동 적용 영향 부재 catch.
- 영상 4 (인터뷰 2): chunk_max 1716 ≈ 2000 경계 — char_limit=2000 적용 시 1~2 chunk 추가 분할 가능. 효과는 미미.

## 추천

**1차 — 재분할 + cs=12 + char_limit=2000 통합** (단일 진실, 1건 잔존 허용):
- 6/6 영상 모두 1-pass timeout ≤ 1로 catch.
- F3QDC7HDMyg에서 timeout 6→1로 83% 감소 — 큰 catch.
- 2-pass 모든 영상 timeout 0 유지.
- daily 사용자 영향 작음 (chunk_max ≤ 1716 영상에 영향 부재, 긴 영상에서만 chunks 약간 ↑).

**2차 (1건 잔존 catch 필요 시) — char_limit=1500 또는 timeout 60→90s 증가**:
- char_limit=1500: chunk_max 1494, chunks 39 — 추가 timeout 해소 가능, 단 chunk 수 30% ↑.
- timeout 60→90s: 정상 chunk 영향 부재, 폭주 chunk catch 늦음.

**모델 비의존 catch**:
- char_limit=2000은 chunk 부담 일정 catch (외부 분포 robust).
- 단 35b-A3B 약한 모델 grammar-recovery loop 잔존 case — 모델 측면 catch 부족.
- 더 강한 모델(q5)에서는 char_limit=2000 충분 추정 — 35b-A3B만의 한계 가능.

## 산출물

- `docs/wip/charlimit_verify.py` (측정 스크립트)
- `verify_results/mv/F3QDC7HDMyg/{1,2}pass_cl2k_{body,log}.{md,txt}` (본문 + log)
- `verify_results/mv/F3QDC7HDMyg/cl2k_run.log` (실행 log)
- `verify_results/mv/F3QDC7HDMyg/charlimit_report.md` (본 보고서)

commit 부재 (prototype 단계).

## 다음 단계

1. **stt_mlx.py + llm.py 통합** — 재분할 + cs=12 + char_limit=2000 + envvar 토글.
2. **daily 검증 1편** — 통합 후 토글 on/off 비교.
3. **(선택) timeout 1건 잔존 catch** — 더 강한 모델 (q5) catch 또는 char_limit=1500 추가 측정.
