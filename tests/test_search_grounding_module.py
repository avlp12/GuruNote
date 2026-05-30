"""gurunote/search_grounding.py 단위 테스트 — _pick_correction (순수 함수) 중심.

※ 기존 tests/test_search_grounding.py 는 llm.py 의 _verify_entities_with_search/
   load_stt_corrections (mock 통합) 을 테스트한다. 이 파일은 **새 모듈**
   gurunote/search_grounding.py 의 검색 결과 → 정답 인명 추출 로직만 검증한다.

네트워크 의존(_searxng_query 라이브) 테스트는 두지 않는다 — 라이브 확인은 스모크로만.
단정은 전체명/성씨 어느 쪽을 반환하든 깨지지 않게: "정답 포함 & 오인식 미포함".
"""
from __future__ import annotations

import json
from pathlib import Path

from gurunote.search_grounding import (
    _build_query,
    _pick_correction,
    build_search_fn,
    context_from_video,
)

_FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> list:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def test_wurst_fixture_corrects_to_warsh():
    """실제 SearXNG 결과(Wurst 질의)에서 정답 Warsh 로 교정 — 오인식 Wurst 에서 벗어남."""
    out = _pick_correction("Kevin Wurst", _load("searxng_wurst.json"))
    assert out is not None
    assert "Warsh" in out
    assert "Wurst" not in out


def test_besson_fixture_corrects_to_bessent():
    """실제 SearXNG 결과(Besson 질의)에서 정답 Bessent 로 교정 — 오인식 Besson 에서 벗어남."""
    out = _pick_correction("Besson", _load("searxng_besson.json"))
    assert out is not None
    assert "Bessent" in out
    assert "Besson" not in out


def test_noise_only_returns_none():
    """misheard 와 안 닮은 잡음 title 뿐이면 None (과교정 부재)."""
    results = [
        {"title": "Federal Reserve Latest Policy News"},
        {"title": "US Economy Outlook 2026 Report"},
        {"title": "Interest Rates And Inflation Update"},
    ]
    assert _pick_correction("Kevin Wurst", results) is None


def test_echo_only_returns_none():
    """결과가 입력 이름만 echo 하면 None (바꿀 게 없음)."""
    results = [
        {"title": "Kevin Wurst on Markets"},
        {"title": "Kevin Wurst Interview Highlights"},
        {"title": "A Talk With Kevin Wurst"},
    ]
    assert _pick_correction("Kevin Wurst", results) is None


def test_unrelated_returns_none():
    """misheard 와 무관한 인물 결과면 None (엉뚱한 교정 방지)."""
    results = [
        {"title": "Taylor Swift Announces World Tour"},
        {"title": "Taylor Swift Breaks Streaming Record"},
        {"title": "Taylor Swift New Album Review"},
    ]
    assert _pick_correction("Kevin Wurst", results) is None


def test_frequency_gate_single_occurrence_ignored():
    """빈도 1회 후보는 채택 안 함 (지배적 이름만) — 1회뿐인 유사명은 무시."""
    results = [
        {"title": "Kevin Warsh Speaks"},          # Warsh 1회
        {"title": "Markets React To Fed News"},
        {"title": "Economy Watch Weekly"},
    ]
    # Warsh 가 1회뿐 → freq<2 게이트로 None.
    assert _pick_correction("Kevin Wurst", results) is None


def test_empty_results_returns_none():
    assert _pick_correction("Kevin Wurst", []) is None


def test_build_search_fn_returns_callable_without_network():
    """build_search_fn 은 네트워크 호출 없이 callable 을 돌려준다 (주입용)."""
    fn = build_search_fn(base_url="http://localhost:8080")
    assert callable(fn)


# =============================================================================
# 동명이인 가드 — 후보 성씨가 오인식 성씨와 동일하면 기각 (철자 교정이면 성씨가 바뀐다)
# =============================================================================
def test_homonym_guard_rejects_same_surname_only():
    """결과에 동명이인(Luc Besson)만 있으면 None — 성씨 Besson 동일이라 교정 아님."""
    results = [
        {"title": "Luc Besson new film premiere"},
        {"title": "Luc Besson interview at Cannes"},
        {"title": "Director Luc Besson profile"},
    ]
    assert _pick_correction("Besson", results) is None


def test_homonym_guard_prefers_changed_surname_over_higher_score():
    """핵심: Bessent·Luc Besson 둘 다일 때, Luc Besson 의 difflib 점수(성씨 1.0)가 더
    높아도 성씨 동일이라 기각되고, 성씨가 바뀐 Bessent 가 채택된다."""
    results = [
        {"title": "Scott Bessent Treasury Secretary testifies"},
        {"title": "Scott Bessent on the economy outlook"},
        {"title": "Luc Besson new film premiere"},
        {"title": "Luc Besson interview at Cannes"},
    ]
    out = _pick_correction("Besson", results)
    assert out is not None
    assert "Bessent" in out
    assert "Besson" not in out  # Luc Besson 안 뽑힘


def test_homonym_guard_does_not_affect_besson_fixture():
    """회귀: 기존 besson fixture(Luc Besson 없음) → 여전히 Bessent (가드 무영향)."""
    out = _pick_correction("Besson", _load("searxng_besson.json"))
    assert out is not None and "Bessent" in out and "Besson" not in out


def test_homonym_guard_does_not_affect_wurst_fixture():
    """회귀: 기존 wurst fixture → 여전히 Warsh (성씨 Warsh≠Wurst 라 가드 무관, None 아님)."""
    out = _pick_correction("Kevin Wurst", _load("searxng_wurst.json"))
    assert out is not None and "Warsh" in out and "Wurst" not in out


# =============================================================================
# 영상 맥락 주입 — _build_query / context_from_video (네트워크 없이 질의 구성)
# =============================================================================
def test_build_query_includes_context():
    """질의에 name + hint + 영상 맥락이 모두 들어간다."""
    q = _build_query("Besson", "person", "Stan Druckenmiller economy markets")
    assert q == "Besson person Stan Druckenmiller economy markets"


def test_build_query_empty_context_fallback():
    """빈 맥락이면 기존 'name hint' 형태로 fallback (안 깨짐)."""
    assert _build_query("Besson", "person", "") == "Besson person"


def test_build_query_empty_hint_and_context_is_name_only():
    """hint·맥락 둘 다 비면 name 단독."""
    assert _build_query("Besson", "", "") == "Besson"


def test_context_from_video_builds_from_meta():
    """title·tags·description 을 합친 맥락 문자열 (도메인 앵커용)."""
    ctx = context_from_video({
        "title": "Stan Druckenmiller on the economy",
        "tags": ["macro", "markets"],
        "description": "A conversation about the Fed and markets.",
    })
    assert "Druckenmiller" in ctx and "macro" in ctx


def test_context_from_video_caps_length():
    """max_chars 로 절단 — 질의가 과도하게 길어지지 않게."""
    ctx = context_from_video({"title": "x" * 500, "tags": [], "description": ""}, max_chars=50)
    assert len(ctx) <= 50


def test_context_from_video_empty_when_no_meta():
    """맥락 재료 없으면 빈 문자열 (질의는 name+hint fallback)."""
    assert context_from_video(None) == ""
    assert context_from_video({}) == ""


def test_build_search_fn_accepts_context_without_network():
    """build_search_fn(context=...) 는 네트워크 없이 callable 반환."""
    fn = build_search_fn(context="Druckenmiller economy", base_url="http://localhost:8080")
    assert callable(fn)


def test_built_search_fn_integrates_with_verify(monkeypatch):
    """배선 경로 통합: build_search_fn 의 search_fn 을 llm._verify_entities_with_search 에
    주입하면 entity_cache 가 교정된다 (네트워크는 _searxng_query mock 으로 차단).

    gui.py 가 실제로 하는 일(search_fn 생성 → _verify 주입)을 영상·네트워크 없이 검증.
    """
    import gurunote.search_grounding as sg
    from gurunote.llm import _verify_entities_with_search

    besson_results = _load("searxng_besson.json")
    monkeypatch.setattr(sg, "_searxng_query", lambda *a, **k: besson_results)
    fn = sg.build_search_fn(context="Stan Druckenmiller economy markets")

    cache = {"Besson": {"korean": "베송", "type": "person", "source": "bootstrap"}}
    corr = _verify_entities_with_search(cache, fn)

    assert corr.get("Besson") == "Bessent"
    assert "Besson" not in cache and "Bessent" in cache
    assert cache["Bessent"]["original_english"] == "Besson"
    assert cache["Bessent"]["source"] == "search"
