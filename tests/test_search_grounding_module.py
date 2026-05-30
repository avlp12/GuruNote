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

from gurunote.search_grounding import _pick_correction, build_search_fn

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
