"""(가) 옵션 A prototype — 2-pass 분리 unit test (5/23).

토글:
    GURUNOTE_TWO_PASS=1 환경변수 시 2-pass (자유 번역 → 정렬).
    기본 off 시 기존 1-pass — daily 환경 보존.

검증:
    - 1단계/2단계 prompt 형식
    - 2-pass 통합 (mock 1단계 자유 → mock 2단계 정렬 → N개 출력)
    - 토글 off 시 1-pass 경로 통과 (기존 동작 보존)
    - 1단계 timeout fallback
    - R3-수정 (enable_loose_on_timeout) 2단계 적용
"""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from gurunote.llm import (
    TIMEOUT_PADDING_MARKER,
    _build_alignment_prompt,
    _build_freeform_translation_prompt,
    _call_llm_with_index_mapping,
    _translate_chunk_two_pass,
    translate_chunk_index_mapping_v2,
)
from gurunote.types import Segment


@pytest.fixture
def mock_cfg():
    from gurunote.llm import LLMConfig
    return LLMConfig(
        provider="openai_compatible",
        model="mock-model",
        api_key="mock-key",
        base_url="http://mock.local/v1",
    )


@pytest.fixture
def sample_chunk():
    return [
        Segment(speaker="Speaker A", start=10.0, end=12.0, text="Hello world"),
        Segment(speaker="Speaker B", start=13.0, end=15.0, text="How are you"),
        Segment(speaker="Speaker A", start=16.0, end=18.0, text="I am fine"),
    ]


# =============================================================================
# Prompt 구조 — 1단계/2단계 형식
# =============================================================================
class TestPromptBuild:
    def test_freeform_prompt_has_no_schema_marker(self):
        inputs = ["Speaker A: hello", "Speaker B: hi"]
        prompt = _build_freeform_translation_prompt(inputs, "")
        # 자유 번역 영역 명시
        assert "자유 번역" in prompt or "자유롭게" in prompt
        # JSON outputs 형식 강제 부재 (1단계는 schema 부담 부재)
        assert '{"outputs"' not in prompt
        # N개 강제는 prompt 차원 (segment 합치기/나누기 방지)
        assert "2 개" in prompt or "정확히 2" in prompt

    def test_alignment_prompt_has_schema_format(self):
        inputs = ["Speaker A: hello", "Speaker B: hi"]
        freeform = "[자유 번역 본문]"
        prompt = _build_alignment_prompt(inputs, freeform)
        # 정렬 영역 + N개 outputs 명시
        assert "정렬" in prompt
        assert '{"outputs"' in prompt
        # 1단계 자유 번역이 prompt 안에 포함
        assert "[자유 번역 본문]" in prompt
        # 번역 내용 변경 부재 명시
        assert "변경" in prompt and ("부재" in prompt or "절대" in prompt)


# =============================================================================
# _translate_chunk_two_pass — 통합 동작
# =============================================================================
class TestTwoPassIntegration:
    def test_normal_two_pass_returns_outputs(self, mock_cfg, sample_chunk):
        freeform_text = "Speaker A: 안녕\n\nSpeaker B: 잘 지내?\n\nSpeaker A: 좋아"
        aligned_outputs = ["A: 안녕", "B: 잘 지내?", "A: 좋아"]
        aligned_json = json.dumps({"outputs": aligned_outputs}, ensure_ascii=False)
        with patch("gurunote.llm._call_llm") as mock_freeform, \
             patch("gurunote.llm._call_llm_with_continuation") as mock_align:
            mock_freeform.return_value = freeform_text
            mock_align.return_value = (aligned_json, "stop")
            outputs = _translate_chunk_two_pass(sample_chunk, "", mock_cfg)
        assert outputs == aligned_outputs
        # 1단계 1회, 2단계 1회
        assert mock_freeform.call_count == 1
        assert mock_align.call_count == 1

    def test_freeform_timeout_returns_timeout_padding(self, mock_cfg, sample_chunk):
        # 1단계 timeout → 2단계 진입 부재, 즉시 [⚠ timeout] padding
        with patch("gurunote.llm._call_llm") as mock_freeform, \
             patch("gurunote.llm._call_llm_with_continuation") as mock_align:
            mock_freeform.side_effect = TimeoutError("freeform timeout")
            outputs = _translate_chunk_two_pass(sample_chunk, "", mock_cfg)
        assert outputs == [TIMEOUT_PADDING_MARKER] * 3
        # 2단계 호출 부재
        assert mock_align.call_count == 0

    def test_freeform_empty_returns_translation_missing_padding(self, mock_cfg, sample_chunk):
        # 1단계 빈 응답 → [번역 누락] padding
        with patch("gurunote.llm._call_llm") as mock_freeform, \
             patch("gurunote.llm._call_llm_with_continuation") as mock_align:
            mock_freeform.return_value = ""
            outputs = _translate_chunk_two_pass(sample_chunk, "", mock_cfg)
        assert outputs == ["[번역 누락]"] * 3
        assert mock_align.call_count == 0


# =============================================================================
# 토글 — GURUNOTE_TWO_PASS 환경변수
# =============================================================================
class TestToggle:
    def test_default_off_uses_one_pass(self, mock_cfg, sample_chunk, monkeypatch):
        # 환경변수 부재 → 1-pass (기존 동작)
        monkeypatch.delenv("GURUNOTE_TWO_PASS", raising=False)
        outputs_json = json.dumps({"outputs": ["a", "b", "c"]}, ensure_ascii=False)
        with patch("gurunote.llm._call_llm") as mock_freeform, \
             patch("gurunote.llm._call_llm_with_continuation") as mock_one_pass:
            mock_one_pass.return_value = (outputs_json, "stop")
            result = translate_chunk_index_mapping_v2(sample_chunk, "", mock_cfg)
        # 1-pass 경로 — _call_llm (freeform) 호출 부재
        assert mock_freeform.call_count == 0
        # _call_llm_with_continuation 1회 (1-pass)
        assert mock_one_pass.call_count == 1
        # client zip timestamp 부착 catch
        assert "[00:10]" in result and "[00:13]" in result and "[00:16]" in result

    def test_toggle_on_uses_two_pass(self, mock_cfg, sample_chunk, monkeypatch):
        monkeypatch.setenv("GURUNOTE_TWO_PASS", "1")
        freeform_text = "A: 안녕\n\nB: 안녕\n\nA: 좋아"
        aligned_json = json.dumps({"outputs": ["A: 안녕", "B: 안녕", "A: 좋아"]}, ensure_ascii=False)
        with patch("gurunote.llm._call_llm") as mock_freeform, \
             patch("gurunote.llm._call_llm_with_continuation") as mock_align:
            mock_freeform.return_value = freeform_text
            mock_align.return_value = (aligned_json, "stop")
            result = translate_chunk_index_mapping_v2(sample_chunk, "", mock_cfg)
        # 2-pass — 1단계 + 2단계 각 1회
        assert mock_freeform.call_count == 1
        assert mock_align.call_count == 1
        assert "[00:10]" in result

    def test_toggle_value_other_than_one_uses_one_pass(self, mock_cfg, sample_chunk, monkeypatch):
        # "0", "false", 임의 값 모두 1-pass (오로지 "1"만 활성)
        for v in ["0", "false", "yes", ""]:
            monkeypatch.setenv("GURUNOTE_TWO_PASS", v)
            outputs_json = json.dumps({"outputs": ["x", "y", "z"]}, ensure_ascii=False)
            with patch("gurunote.llm._call_llm") as mock_freeform, \
                 patch("gurunote.llm._call_llm_with_continuation") as mock_one_pass:
                mock_one_pass.return_value = (outputs_json, "stop")
                translate_chunk_index_mapping_v2(sample_chunk, "", mock_cfg)
            assert mock_freeform.call_count == 0, f"v={v!r} 시 1-pass 진입 부재"


# =============================================================================
# R3-수정 — enable_loose_on_timeout=True 시 strict → loose 전환
# =============================================================================
class TestR3LooseOnTimeout:
    def test_default_disabled_keeps_strict_on_timeout(self, mock_cfg):
        # 기본 enable_loose_on_timeout=False — 1-pass 동작 보존
        cfg = mock_cfg
        with patch("gurunote.llm._call_llm_with_continuation") as mock_call:
            # 3회 모두 timeout
            mock_call.side_effect = TimeoutError("timeout")
            outputs = _call_llm_with_index_mapping(
                cfg, "prompt", expected_count=5, max_retries=3
            )
        # 3회 retry catch, strict 유지 (loose 전환 log 부재)
        assert mock_call.call_count == 3
        assert all(o == TIMEOUT_PADDING_MARKER for o in outputs)

    def test_enabled_switches_to_loose_on_timeout(self, mock_cfg):
        # enable_loose_on_timeout=True — 2단계 전용 — timeout 시 loose 전환
        cfg = mock_cfg
        log_messages = []
        with patch("gurunote.llm._call_llm_with_continuation") as mock_call:
            mock_call.side_effect = TimeoutError("timeout")
            _call_llm_with_index_mapping(
                cfg, "prompt", expected_count=5, max_retries=3,
                log=log_messages.append,
                enable_loose_on_timeout=True,
            )
        # R3-수정 log catch
        assert any("R3-수정" in m or "json_object mode 전환" in m for m in log_messages), (
            f"loose 전환 log 부재 — log={log_messages!r}"
        )
