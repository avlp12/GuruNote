# Power Outage Handoff — 2026-05-14 09:36 KST

정전 30분 전 대비 보존. 복귀 즉시 본 문서로 상태 catch.

---

## 현재 상태 (snapshot)

**Branch**: `redesign/tailwind-v2`
**HEAD**: `3f3f04d` (Phase 2B-3-backend: Log tab user-select)
**Working tree**: clean (변경 부재)
**Origin sync**: up to date

### 핵심 영역 — stash@{0} 안에 모두 안전 보존

```
stash@{0}: POWER-OUTAGE-2026-05-14 — docs 정리 deletions + llm.py Layer 11 followup + docs/research untracked
```

**stash 영역 내용**:
- `gurunote/llm.py` +289 lines — Phase 1 Redesign 영역 완전 catch
  - `_call_llm_once_with_reason` (L897)
  - `_build_index_mapping_prompt` (L936)
  - `_call_llm_with_continuation` (L965)
  - `_call_llm_with_index_mapping` (L1011) — **json_schema strict mode 적용**
  - `translate_chunk_index_mapping_v2` (L1106)
  - 옛 Phase 1 helpers (`_TS_FIND_RE` 등) 제거 catch
  - `translate_transcript` 의 Index Mapping path 통합 catch
- `docs/research/phase1_redesign_research.md` (975 lines) — untracked, 외부 자료 spec
- 39 files docs/ 영역 deletions (docs cleanup work, 정전 전 작업 중 영역)

---

## 진행 중이던 영역

**Phase 1 Redesign — Step 1 (json_schema strict) 결과 verify 직후**:

### Step 1 결과 (5/14 직전 catch)
- 자동 검증 4/4 통과:
  - 25 outputs = 25 inputs (정확)
  - `[번역 누락]` 0건
  - `[00:17]` empty content 부재
  - timestamp 완전성 100%
- Retry 영역: 12 → 20 → 25 (3회 retry 후 정합)
- 처리 시간: 59초 (5/13 의 244초 대비 4배 단축)
- 잔존 quality 이슈:
  - 후반 line 영역의 hallucination (예: `[01:14]` "도자교의 왕도교의 등기")
  - typo (`그맰`, `그걳`, `젦설 황`)
  - 미번역 영문 잔재 (`appearances`)
  - 첫 등장 영문 병기 영역 — 둘째 등장에서도 잔재 (Layer 13 정합 부재)

### 본인 결정 대기 영역 (Q4, Q5)

**Q4. Step 1 결과 영역 평가**:
- (가) Case 1 통과 → Q2 (post-process) 진입 (사용자 spec 정합)
- (나) Case 2 부분 통과 → Step 2 (chunk size 축소) 진입 (Claude Code 추천)
- (다) Case 3 잔존 cause 추가 catch

**Q5. (Q4=가 시) Q2 post-process 영역 우선**:
- (가) 두 번째 이후 영문 병기 제거
- (나) speaker prefix 일관성
- (다) typo fix (별도 trajectory)

---

## 복귀 즉시 진행 순서

```bash
# Step 1. 상태 catch
cd /Users/gesicht/GuruNote
git status
git stash list
cat docs/wip/HANDOFF_POWER_OUTAGE_2026-05-14.md

# Step 2. 본 HANDOFF 가 untracked 영역 (정전 전 working dir clean 영역 외)
ls docs/wip/

# Step 3. Phase 1 Redesign 영역 복원 결정 — 두 path 영역
# (a) stash pop 영역 (전부 복원 — docs deletions 포함):
#     git stash pop stash@{0}
# (b) stash 의 llm.py 영역만 추출 (deletions 무시):
#     git checkout stash@{0} -- gurunote/llm.py
#     git show "stash@{0}^3":docs/research/phase1_redesign_research.md > docs/research/phase1_redesign_research.md
#     git stash drop stash@{0}  # 또는 보존

# Step 4. Q4/Q5 결정 → Step 2 (chunk size) 또는 Q2 (post-process) 진입
```

---

## 산출물 영역 (docs/wip/ 안)

| 파일 | 영역 |
|---|---|
| `HANDOFF_POWER_OUTAGE_2026-05-14.md` | 본 문서 |
| `checkpoint2_verify.py` | 단일 chunk Index Mapping verify (5 segments) |
| `checkpoint3_e2e_verify.py` | E2E translate_transcript verify (25 segments) |
| `phase1_unit_test.py` | 5/12 trajectory 의 unit test (legacy) |
| `gurunote_layer*_commit_msg.txt` | 과거 commit messages (참고용) |
| `gurunote_step3b*_commit_msg.txt` | 과거 commit messages (참고용) |

---

## 본질 영역 catch (복귀 후 정합)

**Phase 1 Redesign 의 본질**:
- Content drift 근본 차단 (zip 결정론 매핑)
- Truncation 검출 (finish_reason='length')
- json_schema strict mode 영역의 minItems/maxItems 강제 (5/14 적용)

**5/14 결과 영역의 진단**:
- Index Mapping path 본질 정합 — drift 부재
- strict mode 영역의 정확 N emit 강제 catch
- 단 모델 영역의 attention 한계 catch 부재 — 후반 영역 quality 부족

**다음 trajectory 영역 (Q4 결정 후)**:
- Step 2 (chunk size 12000 → 6000) — Claude Code 추천 영역
- 또는 Q2 (post-process) — 사용자 spec 정합 영역

---

## 가드레일 영역
- Co-Authored-By: Claude trailer 절대 금지
- 정전 직전 모든 작업 stash@{0} 안전 보존 catch
- 본 HANDOFF 영역은 untracked (정전 후 정합 catch)
