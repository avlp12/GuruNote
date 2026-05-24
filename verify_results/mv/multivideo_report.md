# 다영상 cs=12 견고성 측정 보고 (5/24)

영상: 6개 (TED 2 / 인터뷰 2 / 기타 2)
모델: Qwen3.6-35B-A3B-oQ6-mtp
재분할: word-level 방법 4 (구두점 + 끝 검사)
chunk size: 12 (고정)
HEAD: 599c94b

## 6개 영상 특성표

| 영상 | 특성 | dur(s) | 화자 | 원본→재분할 | 평균 chars | 최대 chars | chunk_max | 1p_t | 1p_timeout | 2p_t | 2p_timeout | 2p_정합 |
|------|------|-------|-----|------------|---------|---------|-----------|------|----------|------|----------|---------|
| C18aaP4lvUk | TED 1 | 723 | 1 | 234→143 | 69 | 206 | 1541 | 168s | **0** | 200s | 0 | 7/12 (58%) |
| g3M3WaixeOw | TED 2 | 1092 | 2 | 377→260 | 51 | 194 | 1166 | 353s | **1** | 576s | 0 | 7/22 (32%) |
| 7ZFh7qI1xyg | 인터뷰 1 | 732 | 4 | -→275 | 43 | 280 | 1359 | 251s | **0** | 366s | 0 | 8/23 (35%) |
| adgbH9FixW0 | 인터뷰 2 | 1560 | 3 | -→300 | 69 | 313 | 1716 | 363s | **1** | 608s | 0 | 14/25 (56%) |
| **F3QDC7HDMyg** | **기타 1** | **2315** | **2** | **634→377** | **105** | **662** | **5061** | **838s** | **6** | **644s** | **0** | **14/32 (44%)** |
| FG5JsLHPW_I | 기타 2 | 322 | 4 | 88→71 | 78 | 229 | 1562 | 114s | **0** | 100s | 0 | 4/6 (67%) |

## Step 2 — 1-pass cs=12 견고성

| 영상 | 1p timeouts |
|------|-----------|
| 5/6 영상 (TED 1, TED 2, 인터뷰 1, 인터뷰 2, 기타 2) | 0~1 (catch) |
| **F3QDC7HDMyg (기타 1)** | **6** (cs=12 부족) |

**catch — cs=12 고정 부족 사례 발견 ❌**

기타 1 영상 특성 (cs=12에서 timeout 6 발생):
- duration 2315s (38분, 가장 긴 영상)
- segment 평균 105 chars (다른 영상 43~78 대비 1.3~2.4배)
- segment 최대 **662 chars** (다른 영상 194~313 대비 2.1~3.4배)
- **chunk_max 5061 chars** (다른 영상 1166~1716 대비 2.9~4.3배)

`F3QDC7HDMyg`는 segment 자체가 매우 긴 영상 catch (긴 발화 끝 검사 미완 패턴이 적음 + 자연 길이 → 재분할이 더 합쳐서 더 김). chunk_max 5061 = ~1265 토큰. cs=12에서 LLM 처리 시간 60s 초과 catch.

## Step 3 — 2-pass cs=12 견고성

| 영상 | 2p timeouts | 정합 비율 |
|------|-----------|----------|
| 모든 영상 (6/6) | **0** ✅ | 32~67% (평균 ~48%) |

**catch — 2-pass는 cs=12에서 모든 영상 timeout 0 ✅**

2-pass가 1-pass보다 더 견고 — 1단계 자유 번역은 schema 부재라 LLM 부담 작음 (의미 합치기 자유). 2단계 정렬은 1단계 결과 기반이라 grammar-recovery loop 적음.

기타 1 (F3QDC7HDMyg)도 2-pass timeout 0 — 1-pass만 timeout 발동.

2-pass 정합 비율 (cs=12):
- 평균 **~48%** (oE5lNDhz9oo cs=12 = 69% 대비 낮음)
- 단일 영상 vs 다영상 차이 — oE5lNDhz9oo는 화자 코드 부착 catch 영상 (인터뷰 자연 길이).
- 본 다영상 catch는 영상 특성 다양 (TED 독백, 인터뷰 다수 화자, 긴 발화 영상).

## Step 4 — 견고성 판정 + 동적 조정 기준

**cs=12 고정 견고성 — 부분 견고** (5/6 영상 catch, 1/6 부족).

**catch — chunk_max chars 임계가 동적 조정 기준**:

| 영상 | chunk_max | 1p_timeout |
|------|-----------|------------|
| TED 2 (catch) | 1166 | 1 |
| 인터뷰 1 (catch) | 1359 | 0 |
| TED 1 (catch) | 1541 | 0 |
| 기타 2 (catch) | 1562 | 0 |
| 인터뷰 2 (catch) | 1716 | 1 |
| **기타 1 (catch 부족)** | **5061** | **6** |

**임계 catch — chunk_max ~2000 chars 경계**:
- chunk_max ≤ 1716 → 1-pass timeout 0~1 (catch)
- chunk_max = 5061 → 1-pass timeout 6 (catch 부족)

segment 평균 길이는 약한 catch:
- TED 2 (avg 51) timeout 1 / 인터뷰 1 (avg 43) timeout 0 — 평균이 적은데도 1건 발생
- 기타 1 (avg 105) timeout 6 — 평균 + max + chunk_max 모두 큰 case
- 핵심 = **분포 우측 꼬리 (긴 segment 집중 chunk)** = chunk_max

## 동적 조정 공식 후보

**catch — char_limit 활용 (chunk_segments의 2번째 한도)**:

기존 `chunk_segments(segments, char_limit=12_000, segment_limit=15)` 두 한도 catch.
- 현재 char_limit=12000은 LLM 토큰 한도 보조 — segment_limit이 먼저 도달 catch.
- **char_limit을 ~2000으로 축소** 시 chunk_max 자동 제한 → 긴 segment 집중 chunk 자동 분할.

권장:
```python
DEFAULT_CHUNK_CHAR_LIMIT = 2000   # 5/24 — chunk LLM 처리 부담 catch
MAX_SEGMENTS_PER_CHUNK = 12       # 재분할 default
```

기타 1 (F3QDC7HDMyg) 적용 시 추정:
- segment 평균 135 chars × 12 = 1620 chars (정상 chunk)
- 단 일부 chunk가 5061 chars catch → char_limit=2000 도달 시 일부 segment에서 분할
- chunk 수 증가 + chunk_max 제한 → timeout 회피

대안: cs=12 default + 영상별 1단계 후 chunk_max catch → 임계 초과 시 자동 재처리 (cs 감소). 복잡.

## 본인 결정용 catch

- **cs=12 고정 부분 견고** — 5/6 영상 catch, 1/6 (긴 발화 영상)에서 1-pass timeout 6 발동.
- **2-pass는 모든 영상 timeout 0** — 재분할 + cs=12 catch.
- **chunk_max chars 임계 ≈ 2000** catch 동적 조정 기준.
- **char_limit 축소 (12000 → 2000)이 가장 단순 + 효과적 path** — chunk_segments 기존 메커니즘 활용.
- 화자/정보 손실 catch 부재 (6개 영상 전부 정상 처리).

## 추천

**1차 — 재분할 + cs=12 + char_limit=2000 통합** (단일 진실 catch).

근거:
- 단일 영상 cs=12 catch (oE5lNDhz9oo): 1-pass timeout 0, 2-pass 정합 69%.
- 다영상 5/6 catch: cs=12 + chunk_max ≤ 1716이면 timeout 0~1.
- char_limit=2000 추가 시 긴 segment 영상도 catch (chunk_max 자동 제한).
- 2-pass는 모든 영상 catch — daily 사용자 cs=12 안전.

통합 방향:
1. **stt_mlx.py 후처리 line 224 직후** 재분할 함수 추가 (envvar 토글 `GURUNOTE_SEGMENT_RESPLIT=1`).
2. **llm.py**:
   - `MAX_SEGMENTS_PER_CHUNK = 15` → 재분할 활성 시 12 자동 적용 (또는 envvar `GURUNOTE_CHUNK_SIZE` 기본 12).
   - `DEFAULT_CHUNK_CHAR_LIMIT = 12000` → 2000 또는 envvar `GURUNOTE_CHUNK_CHAR_LIMIT`.
3. **char_limit=2000 검증 필요** — 기타 1 영상으로 단일 측정 권장 (1-pass timeout 해소 catch).

**2차 (1차 검증 후 부족 시) — 동적 조정**:
- 1차 chunk 분할 후 chunk_max chars catch → 임계 초과 시 해당 chunk 추가 분할.
- 또는 chunk_size를 segment 평균에 비례.

## 산출물

- `docs/wip/multivideo_sweep.py` (sweep 스크립트)
- `verify_results/mv/<video_id>/raw.json` (STT raw + words + diarization, 6개)
- `verify_results/mv/<video_id>/resplit.json` (재분할 segments, 6개)
- `verify_results/mv/<video_id>/{1,2}pass_{body,log}.{md,txt}` (각 영상별 본문 + log, 24개)
- `verify_results/mv/summary.json` (집계)
- `verify_results/mv/multivideo_report.md` (본 보고서)

commit 부재 (prototype 단계).

## 다음 단계

1. **기타 1 (F3QDC7HDMyg) char_limit=2000 검증** — 1-pass timeout 해소 catch.
2. **stt_mlx.py + llm.py 통합** — 재분할 + cs=12 + char_limit=2000 + envvar 토글.
3. **daily 1편 검증** — 통합 후 토글 on/off 비교.
