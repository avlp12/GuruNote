"""검색 그라운딩 — SearXNG 조회 + difflib 인명 교정 (search_fn 실구현).

인명·회사명 STT 오인식(예: Kevin Wurst → Kevin Warsh, Besson → Bessent)을 외부 검색으로
교정하기 위한 모듈. `llm._verify_entities_with_search` 가 의존성 주입으로 받는 `search_fn`
의 실제 구현을 `build_search_fn` 으로 만든다.

search_fn 계약 (llm.py:1696 정합):
    search_fn(name, hint) -> 교정 english | None
      - name : STT 가 들은 영문 표기 (entity_cache 의 key).
      - hint : 엔티티 타입 ("person"/"company"). _verify 가 meta["type"] 를 넘김.
              (직책/역할이 아니라 타입 — 질의 보강은 단계 3에서 재검토.)
      - 반환 : 교정된 english (입력과 다를 때만) / 교정 불필요·결과 부재면 None.
      - 예외 : 네트워크 실패·타임아웃·비200 은 **올린다**(raise). _verify 가 엔티티별로
              catch 해 graceful skip(다음 기회 재시도) → SearXNG 다운 시 안전.

두 층 + 팩토리:
    _searxng_query  : 네트워크 (실패 시 raise)
    _pick_correction: 순수 함수 (네트워크 없음, 결과 title 에서 정답 인명 추출)
    build_search_fn : 둘을 합친 클로저 반환 (gui 가 단계 3에서 주입)

PROVISIONAL (인명·회사명 좁은 검증 기준 — 대상 넓힐 때 재검토):
    - 후보는 결과 **title 만** 사용 (content 미사용). q2/q3 fixture 로 title-only 로 충분 확인.
    - 빈도 게이트 ≥2 (잡음 1회성 제거).
    - difflib threshold 0.6 — q2/q3 실측: 정답 0.769~0.818, 잡음 ≤0.364 (여유 큰 분리).
    - 동점 tie-break: 입력과 토큰 수 가까운 쪽 우선(최소 교정) → freq → 사전순. 즉 "Besson"
      은 "Bessent"(성씨 교정)을 반환하고 "Scott Bessent"(전체명 확장)은 안 함. 전체명 확장
      여부는 단계 3 정책 결정 사항.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import urllib.parse
import urllib.request
from collections import Counter
from typing import Callable, List, Optional

_DEFAULT_BASE_URL = "http://localhost:8080"
_DEFAULT_THRESHOLD = 0.6
_DEFAULT_TIMEOUT = 5.0

# title 후보에서 거를 흔한 대문자 토큰 (PROVISIONAL — difflib gate 가 주된 필터, 보조 방어).
_STOPWORDS = frozenset({
    "The", "A", "An", "In", "On", "Of", "To", "For", "And", "Or", "Is", "Are",
    "New", "Who", "What", "Why", "How", "When", "Where", "News", "Live",
})

# 대문자로 시작하는 영문 토큰 (고유명사 후보).
_CAP_TOKEN_RE = re.compile(r"[A-Z][A-Za-z]+(?:'[A-Za-z]+)?")


def _searxng_query(
    name: str,
    hint: Optional[str],
    base_url: str,
    timeout: float,
) -> List[dict]:
    """SearXNG `format=json` 조회 → results 리스트 반환.

    연결 실패·타임아웃·비200 은 예외를 **올린다** (호출자 search_fn 을 거쳐 _verify 의 예외
    분기 = graceful skip 으로 전파). 성공이면 `data["results"]` (없으면 빈 리스트).

    localhost 평문 GET 이라 SSL context 불필요 — 표준 urllib 만 사용(새 의존성 없음).
    """
    query = f"{name} {hint}".strip() if hint else name.strip()
    url = base_url.rstrip("/") + "/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": "GuruNote-search-grounding"})
    # urlopen 은 연결 거부→URLError, 4xx/5xx→HTTPError, 타임아웃→socket.timeout 을 올림.
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (localhost 평문)
        status = getattr(resp, "status", 200)
        if status != 200:
            raise RuntimeError(f"SearXNG HTTP {status}")
        payload = resp.read().decode("utf-8")
    data = json.loads(payload)
    results = data.get("results")
    return results if isinstance(results, list) else []


def _name_similarity(candidate: str, misheard: str) -> float:
    """전체명·성씨(마지막 토큰) 비교 중 **높은 쪽** 유사도 (대소문자 무시).

    "Kevin Warsh"~"Kevin Wurst"(전체명) 와 "Warsh"~"Wurst"(성씨) 둘 다 잡기 위함.
    """
    c, m = candidate.lower().strip(), misheard.lower().strip()
    full = difflib.SequenceMatcher(None, c, m).ratio()
    c_sur, m_sur = c.split()[-1] if c else c, m.split()[-1] if m else m
    sur = difflib.SequenceMatcher(None, c_sur, m_sur).ratio()
    return max(full, sur)


def _candidate_counts(results: List[dict]) -> Counter:
    """결과 title 들에서 고유명사 후보(대문자 1·2그램) 빈도 집계. content 미사용(PROVISIONAL)."""
    cnt: Counter = Counter()
    for r in results:
        title = (r.get("title") or "") if isinstance(r, dict) else ""
        toks = _CAP_TOKEN_RE.findall(title)
        for w in toks:
            if w not in _STOPWORDS:
                cnt[w] += 1
        # title 등장 순서의 연속 대문자 토큰을 2그램으로 (전체명 후보).
        for a, b in zip(toks, toks[1:]):
            cnt[f"{a} {b}"] += 1
    return cnt


def _pick_correction(
    misheard: str,
    results: List[dict],
    threshold: float = _DEFAULT_THRESHOLD,
) -> Optional[str]:
    """결과 title 에서 misheard 에 가장 가까운 지배적 고유명사를 정답으로 채택 (순수 함수).

    절차: title 후보 추출 → 빈도 ≥2 게이트 → misheard 와 difflib 유사도 최댓값 → threshold
    이상이고 입력과 다른 후보 중, 입력과 토큰 수 가까운 쪽(최소 교정)·고빈도·사전순으로 선택.
    조건 미달이면 None (교정 없음 — _verify 가 무교정으로 처리).
    """
    if not misheard or not results:
        return None
    misheard = misheard.strip()
    m_token_list = misheard.split()
    m_tokens = len(m_token_list)
    misheard_set = {t.lower() for t in m_token_list}
    counts = _candidate_counts(results)
    best_key = None
    best_cand: Optional[str] = None
    for cand, freq in counts.items():
        if freq < 2:
            continue
        # echo/부분 거르기 — 후보 토큰이 전부 입력에 이미 있으면 교정이 아님 (예: 입력
        # "Kevin Wurst" 의 성씨 "Wurst" 나 "Kevin" 단독은 철자를 안 바꾸므로 제외).
        if all(t.lower() in misheard_set for t in cand.split()):
            continue
        # 동명이인 가드 — 철자 교정이면 성씨(마지막 토큰)가 바뀌어야 한다. 후보 성씨가
        # 오인식 성씨와 완전 동일하면(예: misheard "Besson" vs 후보 "Luc Besson") 철자 교정이
        # 아니라 같은 성씨의 다른 인물 → 점수(성씨 1.0)와 무관하게 기각. echo 가드와 분리:
        # 저쪽은 "모든 토큰이 입력에 있음", 이쪽은 "마지막 토큰만 동일".
        # PROVISIONAL — 성은 맞고 이름만 틀린 동명이인(예: 다른 "Kevin Wurst")은 못 거른다(허용).
        if cand.split()[-1].lower() == m_token_list[-1].lower():
            continue
        score = _name_similarity(cand, misheard)
        if score < threshold:
            continue
        # tie-break: 점수 → 토큰 수 근접(최소 교정, 작을수록 우선=음수로) → 빈도 → 사전 역순.
        key = (score, -abs(len(cand.split()) - m_tokens), freq, cand)
        if best_key is None or key > best_key:
            best_key = key
            best_cand = cand
    return best_cand


def build_search_fn(
    base_url: Optional[str] = None,
    threshold: float = _DEFAULT_THRESHOLD,
    timeout: float = _DEFAULT_TIMEOUT,
) -> Callable[[str, Optional[str]], Optional[str]]:
    """`search_fn(name, hint) -> 교정 english | None` 클로저 생성 (gui 가 단계 3에서 주입).

    base_url 기본 = env `GURUNOTE_SEARXNG_URL` → 없으면 `http://localhost:8080`.
    네트워크 실패는 search_fn 밖으로 전파(= _verify graceful skip). 검색은 성공했으나 정답
    후보 부재면 None(= _verify 가 무교정 마킹).
    """
    resolved = (base_url or os.environ.get("GURUNOTE_SEARXNG_URL") or _DEFAULT_BASE_URL)

    def search_fn(name: str, hint: Optional[str] = None) -> Optional[str]:
        results = _searxng_query(name, hint, resolved, timeout)  # 실패 시 raise → graceful skip
        return _pick_correction(name, results, threshold)

    return search_fn
