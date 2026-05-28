"""전체 스크립트 타임스탬프 표시 토글 (5/28) — exporter presentation 레이어.

GURUNOTE_SHOW_TIMESTAMPS 가 "0" 일 때만 본문(번역본·한국어 원본) 라인 머리의
`[MM:SS] ` prefix 제거 + 영어 원문 조립 시 `**[MM:SS]**` 생략. 기본(미설정/그 외)은
현 동작 유지. 번역/STT path 무변 — exporter 문자열 처리만. marker·영문 병기는 보존.
타임라인 요약(summary_md)은 별개 경로라 본 토글과 무관.
"""
from __future__ import annotations

import pytest

from gurunote.exporter import (
    _strip_timestamp_prefix,
    build_full_script_section,
    build_original_script_section,
)
from gurunote.types import Segment, Transcript


@pytest.fixture
def _ts_on(monkeypatch):
    monkeypatch.setenv("GURUNOTE_SHOW_TIMESTAMPS", "1")


@pytest.fixture
def _ts_off(monkeypatch):
    monkeypatch.setenv("GURUNOTE_SHOW_TIMESTAMPS", "0")


@pytest.fixture
def _ts_unset(monkeypatch):
    monkeypatch.delenv("GURUNOTE_SHOW_TIMESTAMPS", raising=False)


# === strip helper (순수 함수) ===

def test_strip_removes_mmss_prefix():
    assert _strip_timestamp_prefix("[01:23] 화자 1: 안녕하세요") == "화자 1: 안녕하세요"


def test_strip_removes_hhmmss_prefix():
    assert _strip_timestamp_prefix("[1:02:03] 화자 1: 본문") == "화자 1: 본문"


def test_strip_preserves_annotation():
    """영문 병기는 prefix 만 제거하고 `(English)` 보존."""
    out = _strip_timestamp_prefix("[00:05] 팔머 럭키(Palmer Luckey): 안두릴")
    assert out == "팔머 럭키(Palmer Luckey): 안두릴"


def test_strip_preserves_marker():
    """marker(`[번역 누락]`)는 `\\d` 불일치라 보존."""
    assert _strip_timestamp_prefix("[번역 누락] 구간") == "[번역 누락] 구간"
    assert _strip_timestamp_prefix("[⚠ timeout] 구간") == "[⚠ timeout] 구간"


def test_strip_multiline_double_and_single_newline():
    """본문 ①(\\n\\n join)·②(\\n join) 둘 다 각 라인 prefix 제거."""
    txt = "[00:01] A: 첫 줄\n\n[00:05] B: 둘째 줄"
    assert _strip_timestamp_prefix(txt) == "A: 첫 줄\n\nB: 둘째 줄"


# === build_full_script_section (①② 번역본/한국어 원본) ===

def test_full_script_keeps_ts_when_on(_ts_on):
    out = build_full_script_section("[00:01] 화자 1: 본문")
    assert "[00:01] 화자 1: 본문" in out


def test_full_script_keeps_ts_when_unset(_ts_unset):
    """미설정 = 기본 켜짐(현 동작 유지)."""
    out = build_full_script_section("[00:01] 화자 1: 본문")
    assert "[00:01]" in out


def test_full_script_strips_ts_when_off(_ts_off):
    out = build_full_script_section("[00:01] 화자 1: 본문\n\n[00:09] 화자 2: 답변")
    assert "[00:01]" not in out and "[00:09]" not in out
    assert "화자 1: 본문" in out and "화자 2: 답변" in out


# === build_original_script_section (③ 영어 원문) ===

def _en_transcript():
    return Transcript(
        segments=[
            Segment(speaker="A", start=1.0, end=3.0, text="Hello there."),
            Segment(speaker="B", start=5.0, end=7.0, text="Hi."),
        ],
        language="en",
        engine="whisperx",
    )


def test_original_script_keeps_ts_when_on(_ts_on):
    out = build_original_script_section(_en_transcript(), language="en")
    assert "**[00:01] Speaker A:** Hello there." in out


def test_original_script_strips_ts_when_off(_ts_off):
    out = build_original_script_section(_en_transcript(), language="en")
    assert "[00:01]" not in out and "[00:05]" not in out
    assert "**Speaker A:** Hello there." in out
    assert "**Speaker B:** Hi." in out
