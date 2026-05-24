# STT 직후 의미 단위 재분할 prototype 보고 (5/24)

검증 영상: oE5lNDhz9oo (화자 3명, 33분)
HEAD: 599c94b
prototype: `docs/wip/stt_raw_dump.py` + `docs/wip/resplit_prototype.py`

## Step 1 — word-level 출력 (방법 4/3 결정)

mlx-whisper `word_timestamps=True` 출력:
- `result["segments"][i]["words"]` 키 catch.
- word 형식: `{"word", "start", "end", "probability"}`
- **word 자체에 구두점 부착**: `{"word": " Michael,", ...}` — `append_punctuations='".。,，!！?？:："”)]}、'` 기본값.

**→ 방법 4 (word-level 구두점 + 끝 검사) 채택.**
단 prototype 1차는 segment.text 끝 검사로 충분 catch (word.endswith catch 부재) — word 구두점이 그대로 segment.text 끝에 catch.

## Step 2 — 재분할 함수 prototype

`resplit_segments()` 메커니즘:
1. noise 필터 (stt_mlx.py:198 동일).
2. segment 화자 부착 (overlap 1차).
3. greedy 정방향: 미완 끝 catch 시 다음 segment와 병합.
4. 화자 우선 — 다르면 병합 부재.
5. 시간 갭 5초 초과 / 합친 길이 30초 초과 시 병합 부재.
6. 병합 후 화자 재할당 (합친 범위 overlap).

끝 검사 사전:
- 완결: `. ? !`
- 미완: `, : ; - —` (mid_punct), `and/or/but/nor/so/yet/for/because/while/when/if/though/although/as/than/that` (conjunction), `to/of/in/on/at/by/from/with/for/about/into/during/over/under/between/...` (preposition), `the/a/an/is/are/was/were/be/.../my/your/.../this/that/these/those/more/less/...` (dangling).

## Step 3 — 재분할 분포 + 정합

| 측정 | 값 |
|------|-----|
| raw segments | 334 |
| 재분할 segments | **309** (-25, -7.5%) |
| 병합 건수 | 17 |
| 병합 평균 합친 개수 | 2.35 |
| 병합 사유 | mid_punct 15, no_punct 7, conjunction 1 |
| 병합 중단 사유 | 없음 (모두 완결까지 catch) |

화자 우선 catch:
- 원본 word-level 다중 화자 (1 segment 안 word들이 화자 다른 case): **37 / 332 (11.1%)**
- 재분할 word-level 다중 화자: **37 / 309 (12.0%)**
- **절대 수 동일 (37) — 재분할이 화자 다중 catch 추가 부재.** 비율 증가는 분모 감소 효과.
- 즉 합치는 동안 화자 다른 segment는 분리 유지 catch.

핵심 case (D leak 사례) 합쳐졌나:

| 원본 segment | 재분할 결과 | 합쳐진 segments |
|-----------|-----------|---------------|
| [320.7-333.1] "It puts a harness ..." | [320.2-333.1] 그대로 (이미 완결) | 1 |
| [359.3-365.7] "...all of the networking necessary t<u>p</u>" + [365.7-373.3] "up, ..., we call it Nemo claw, running in a secure and" + [373.3-376.9] "governed container called Open Shell." | **[359.3-377.0] 한 줄로 합쳐짐** | 3 |
| [574.0-581.4] "If you ask Sanjay Mitra ... during a meeting," + [581.5-584.4] "I explained the future ..." | **[574.2-584.4] 한 줄로 합쳐짐** | 2 |

## Step 4 — 네 단계 개선 검증

### (1) D 번역 — leak 해소 직접 측정

같은 chunks 7/11/12 영역, K=3 par, 35b-A3B 모델:

**[365.7] case**:

| 모드 | 출력 |
|------|------|
| 재분할 부재 (원본) | `[365.7] ...네모 클로(Nemo Claw)는 안전하고` (미완 출력) + `[373.3] 오픈셸이라는 보안 컨테이너에서 실행됩니다.` (분리 1줄) |
| **재분할 적용** | `[359.3-377.0] 따라서 에이전트, 두뇌, 장기 기억, 확장성을 위한 모든 네트워크, 그리고 에이전트 런타임 자체를 우리는 OpenShell이라는 보안이 강화되고 관리되는 컨테이너에서 실행되는 NemoClaw라고 부릅니다.` |

→ 의미 완결 + leak 동기 부재. NemoClaw + OpenShell + governed container 모두 정확히 한 줄.

**[574.0] case**:

| 모드 | 출력 |
|------|------|
| 재분할 부재 (원본) | `[574.0-581.4] ...3년 전 회의에서 저에게 이렇게 말했을 것입니다` (다음 segment 정보 흡수 = leak) + `[581.5-584.4] 그에게 지금 일어나고 있는 그대로의 미래를 설명해 주었습니다.` (분리 1줄) |
| **재분할 적용** | `[574.2-584.4] 미크론의 산자이 미트라에게 물어보면, 그는 3년 전 회의에서 제가 지금 일어나고 있는 그대로 미래를 그에게 설명했다고 말할 것입니다.` |

→ 의미 완결 + leak 해소.

비용: D K=3 par 13.86s (재분할 부재) → 14.05s (재분할 적용, target 45 → 39). 거의 동일.

### (2) 본문 가독성 — 미완 1줄 사라짐

- 재분할 부재: "[365.7] 안전하고" / "[574.0] 저에게 이렇게 말했을 것입니다" 같은 미완 / 부정확 1줄.
- 재분할 적용: 의미 완결 1줄로 통합. 사용자 대면 본문 자연스러움 ↑.

### (3) 1-pass hallucinate

본 prototype 직접 측정 부재 (전체 영상 1-pass 처리 ~6분 추가). 단 메커니즘 catch:
- 원본 1-pass: "secure and" 같은 미완 input을 모델이 의미 완결하려 hallucinate.
- 재분할 후: input이 의미 완결 → hallucinate 동기 부재.
- 추정 효과 강함 (D K=3 par 측정과 동일 메커니즘).

### (4) 2-pass SHIFT

본 prototype 직접 측정 부재. 단 메커니즘 catch:
- 원본 2-pass 1단계 합침 분포 39% catch (chunk 11 14/15 등) — 이 합침의 일부는 의미 미완 segment 자연 합치기.
- 재분할 후: 의미 단위 segment 입력 → 1단계 line==N 정합 분포 증가 추정 (자연 합치기 동기 부재).
- 2단계 SHIFT (pos 13 집중)는 1단계 line < N 부재시 동기 부재.
- 추정 효과 강함.

직접 측정은 본 영상에 재분할 segment로 2-pass 재처리 필요 (~6분). 본 보고는 메커니즘 catch + 다음 단계 권장.

## Step 5 — daily(1-pass) 안전 + 토글

prototype 한정 상태:
- 본 prototype은 `docs/wip/` 한정. **stt_mlx.py 수정 부재.**
- daily 1-pass 회귀 부재 (재분할 코드가 production 경로 부재).

본 통합 권장 (검증 후 본인 결정):
- envvar 토글 `GURUNOTE_SEGMENT_RESPLIT` (기본 off) 권장.
- 토글 on 시 stt_mlx.py 후처리 line 224 직후 재분할 적용.
- daily 검증 영상 1편 1-pass 토글 on/off 비교 후 default on 결정.

## 휴리스틱 부족 잔존

병합 catch 부재 case 잔존 가능성:
- 자연 끝인데 의미 미완 (e.g. "I think." + "they should ...") — 사전 catch 부재 → 분리 유지. 비용은 D leak 동기 약함 (target 자체는 완결).
- 17건 / 334 segments = 5% catch — 잔존 미완 catch 표면적 매우 작음.
- 한국어 끝 검사 동치 부재 (영어 한정) — 한국어 영상 영향 부재 (target language 영어).

## 추천

**재분할 채택 — STT 직후 1회 의미 단위 재구성**.

근거:
- D leak 해소 직접 측정 catch ([365.7], [574.0] 두 사례 모두).
- 화자 정확도 유지 (절대 수 동일).
- 본문 가독성 ↑ (미완 1줄 사라짐).
- 1-pass/2-pass 메커니즘 catch — 추정 효과 강함.
- F (D 직전 합치기) 통합 — 별도 구현 부재.

다음 단계:
1. **1-pass / 2-pass 직접 측정** — 본 영상 재분할 segment로 1-pass + 2-pass 재처리. SHIFT 분포 / hallucinate 비교.
2. **stt_mlx.py 통합** — envvar 토글 `GURUNOTE_SEGMENT_RESPLIT`. daily 검증 1편 토글 on/off 본문 line 수 + 가독성 비교.
3. **daily 사용자 대면 본문 line 수 변경** (335 → 309 같은 영역) — release note 명시 권장.

## 산출물

- `docs/wip/stt_raw_dump.py` (STT raw + words + diarization dump)
- `docs/wip/resplit_prototype.py` (재분할 함수 + D 재측정)
- `verify_results/community1_3speakers_raw.json` (raw + words, 316 KB)
- `verify_results/community1_3speakers_resplit.json` (재분할 309 segments)
- `verify_results/candidate_d_resplit_k3_par.{md,json}` (D 재분할 결과)
- `verify_results/resplit_report.md` (본 보고서)

commit 부재 (prototype 단계).
