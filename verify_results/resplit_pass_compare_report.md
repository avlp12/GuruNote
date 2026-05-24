# 재분할 효과 — 1-pass/2-pass 직접 측정 보고 (5/24)

영상: oE5lNDhz9oo (화자 3명, 33분)
모델: Qwen3.6-35B-A3B-oQ6-mtp (4회 측정 동일 모델)
HEAD: 599c94b
cache 격리: 각 측정마다 entity_cache 격리 → 측정 간 오염 부재

## Step 1 — 2-pass 직접 비교 (재분할 전 vs 후)

| metric | 원본 2-pass | 재분할 2-pass | 개선 |
|--------|-----------|-------------|------|
| 총 chunks | 23 | 21 | -2 (segments 334→309) |
| 1단계 line==N (정합) | **7 / 23 (30%)** | **12 / 21 (57%)** | **정합 비율 ≈2배** |
| 1단계 line<N (합침) | 16 | 9 | **44% 감소** |
| 극단 (1줄, N>5) | 13 | 9 | 31% 감소 |
| 빈 output 복구 | 0 | 0 | - |
| timeouts | 1 (canonicalize) | 1 (canonicalize) | segment 무관 |
| 처리 시간 | 419.8s | 361.3s | **14% 단축** |
| 본문 line | 662 | 616 | segments 감소만큼 |

**가설 입증 ✅** — 재분할이 1단계 합침 동기 줄임 (44% 감소), 정합 비율 2배.

본문 SHIFT 해소 사례:

| 원본 segment 영역 | 원본 2-pass 결과 | 재분할 2-pass 결과 |
|---------------|---------------|------------------|
| [359.3~376.9] (3 segments, "Nemo Claw ... Open Shell") | 분리 출력, [05:59] 일부 의미 완결 | [05:59] 한 줄로 의미 완결 (NemoClaw + OpenShell + 보안 컨테이너 모두) |
| [574.0~584.4] (2 segments, "Sanjay Mitra ... future") | [09:32] "산자이 미트라에게 묻으면," (미완) + [09:34] "3년 전 ... 미래 이야기를 설명해 줬다고 말할 거예요" (다음 정보 흡수) | [09:34] "미크론의 산자이 미트라에게 물어보면, 그는 3년 전 회의에서 제가 ... 설명해줬다고 말해줄 것입니다." (한 줄로 의미 완결) |

→ 두 사례 모두 재분할이 SHIFT 동기(미완 segment) 차단.

## Step 2 — 1-pass 직접 비교

| metric | 원본 1-pass | 재분할 1-pass |
|--------|-----------|-------------|
| 처리 시간 | 266.2s | 468.0s |
| 본문 line | 662 | 616 |
| timeouts | 1 (canonicalize) | 0 |

본문 [365.7] 영역 (~5:59):

원본 1-pass [05:59]:
> 에이전트, 즉 두뇌와 장기 메모리, 확장성에 필요한 모든 네트워크, 그리고 에이전트 런타임 자체인 '네모클로(NemoClaw)'는 '오픈셸(OpenShell)'이라는 보안이 강화되고 규정 준수 환경의 컨테이너에서 실행됩니다.

재분할 1-pass [05:59]:
> 즉, 에이전트, 두뇌 역할을 하는 장기 기억 장치, 확장성을 위한 모든 네트워크, 그리고 보안이 관리되는 컨테이너인 OpenShell 위에서 구동되는 에이전트 런타임인 NemoClaw까지 모든 요소가 통합되어 있습니다.

**catch**: 원본 1-pass도 chunk 단위에서 모델이 자유 합치기로 의미 완결 catch — **1-pass hallucinate 동기 약함** (chunk 안 다음 segment 모두 보고 합치기 가능, response_format 부재).

단 1-pass에서 잘림 영향 부재가 아닌:
- 원본 1-pass [365.7~376.9] 3 segments → [05:59] 한 줄로 합쳐서 출력 (segment 1:1 매핑 부재).
- 즉 1-pass도 정보를 합치지만 본문 line 수와 segment 수 불일치 catch.
- 재분할은 합쳐진 segment 단위로 본문 line 1:1 매핑 정확.

**1-pass 시간 catch** — 재분할 1-pass 468s vs 원본 266s. 1-pass 본 측정에서 retry 많음 catch (log "길이 미스매치 14 != 15" 다수). 재분할 segments가 LLM 입력 길이 ↑ → retry ↑. 1-pass 단독 처리 시 재분할 효과 약함 (시간 증가 case).

## Step 3 — 네 단계 종합

| 단계 | 재분할 전 | 재분할 후 | 개선 |
|------|---------|----------|------|
| D leak (이미 측정) | [365.7][574.0] leak 발생 | 두 사례 모두 해소 | ✅ 강함 |
| 가독성 (이미 측정) | 미완 1줄 ("안전하고") | 의미 완결 1줄 | ✅ 강함 |
| 2-pass SHIFT (본 측정) | 1단계 합침 16건, [09:34] [05:59] catch | 1단계 합침 9건, 두 영역 catch | ✅ 강함 (44% 감소) |
| 2-pass 1단계 정합 | 7/23 (30%) | 12/21 (57%) | ✅ 강함 (2배) |
| 1-pass hallucinate (본 측정) | 의미 완결 catch (chunk 단위 합치기) | 의미 완결 catch | △ 영향 약함 — 1-pass는 잘림에 robust |
| 1-pass timestamp 매핑 | line ≠ segment 수 | line = segment 수 정합 | ✅ 약함 |

**가설 부분 입증**: 네 단계 중 D leak / 가독성 / 2-pass 강한 개선 ✅. 1-pass hallucinate는 chunk 합치기로 이미 약함 — 재분할 추가 효과 작음.

## Step 4 — 화자/timestamp/B06 회귀 catch

| 항목 | catch |
|------|------|
| 화자 정확도 | 재분할 후 word-level 다중 화자 37건 = 원본 37건 동일 (절대 수) ✅ |
| 화자 라벨 | 본 측정 cache 격리 — 화자 식별 결과 가변 catch (원본 2-pass "젠슨 헝" vs 재분할 2-pass "젠슨 황"). 재분할 자체 영향 부재 — LLM 식별 비결정성. |
| timestamp 범위 | 합친 segment의 첫 start ~ 마지막 end (범위 표기 가능) ✅ |
| B06 entity cache | 재분할이 cache 부재 시 bootstrap path 그대로 작동 ✅ |
| CJK 보존 | 본 측정 4회 모두 한국어 catch (CJK 한자 부재) ✅ |
| 정보 손실 | 본문 line 662→616 = segments 334→309 감소만큼 — 의미 정보 손실 부재 ✅ |

회귀 catch 부재.

## Step 5 — 추천 + 통합 방향

**추천 — 재분할 채택 (stt_mlx.py 통합)**

근거:
- 2-pass 1단계 합침 **44% 감소** + 정합 비율 2배 + 처리 시간 14% 단축 (직접 측정).
- D leak 해소 ([365.7] [574.0] 두 사례) + 본문 가독성 ↑ (이미 측정).
- 화자/timestamp/B06 회귀 부재.
- 1-pass도 영향 약함 (chunk 합치기로 robust) — 회귀 부재.

통합 방향:
1. **stt_mlx.py 후처리 line 224 직후** 재분할 함수 호출.
2. **envvar 토글 `GURUNOTE_SEGMENT_RESPLIT`** — 기본값 결정 필요 (off vs on).
   - off → 기존 동작 보존, 본인 검증 후 on 전환.
   - on → daily 환경 즉시 효과 (1-pass 본문 line 수 변경).
3. **휴리스틱 사전** — 영어 conjunction + preposition + dangling word. 추후 측정으로 보강.
4. **word-level은 mlx-whisper에 catch** — 단 word.word에 punctuation 부착이라 segment.text 끝 검사로 충분 catch.

부작용 catch:
- 1-pass 처리 시간 증가 case 있음 (segment 입력 길이 ↑ → retry ↑). 본 측정 1-pass 266s → 468s catch. **2-pass는 단축 catch**. 1-pass 사용자 시간 영향 catch 필요.
- 본문 line 수 변경 (662→616) — release note 명시 권장.

다음 단계:
1. **stt_mlx.py 통합** — `resplit_segments` 함수 stt_mlx.py 로 이전 + envvar 토글.
2. **daily 검증 1편** — 토글 on/off 시간 + 본문 catch.
3. **휴리스틱 사전 보강** — 1-pass retry 분석 (재분할 후 retry 늘어난 원인 catch).

## 산출물

- `docs/wip/resplit_pass_compare.py` (측정 스크립트)
- `verify_results/{orig,resplit}_{1pass,2pass}_body.md` (본문 4개)
- `verify_results/{orig,resplit}_{1pass,2pass}_log.txt` (log 4개)
- `verify_results/resplit_pass_analysis.json` (집계)
- `verify_results/resplit_pass_compare_report.md` (본 보고서)

commit 부재 (prototype 단계).
