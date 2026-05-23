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
    _post_process_two_pass_outputs,
    _strip_input_speaker_prefix,
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
        assert "재배치" in prompt or "정렬" in prompt
        assert '{"outputs"' in prompt
        # 1단계 자유 번역이 prompt 안에 포함
        assert "[자유 번역 본문]" in prompt
        # 5/23 보강 — 빈/반복 차단 + 새 번역 부재 명시
        assert "빈 string" in prompt or "빈 칸" in prompt
        assert "반복" in prompt and ("부재" in prompt or "절대" in prompt)
        # rule 1 강화 — 새 번역 생성 부재
        assert "새 번역" in prompt or "새로 번역" in prompt


# =============================================================================
# _translate_chunk_two_pass — 통합 동작
# =============================================================================
class TestTwoPassIntegration:
    def test_normal_two_pass_returns_outputs(self, mock_cfg, sample_chunk):
        freeform_text = "티파니: 안녕\n\n판카즈: 잘 지내?\n\n티파니: 좋아"
        # 2단계가 정상 한국어 화자명 형식으로 반환 시 A5 strip 영향 부재
        aligned_outputs = ["티파니: 안녕", "판카즈: 잘 지내?", "티파니: 좋아"]
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
        freeform_text = "티파니: 안녕\n\n판카즈: 안녕\n\n티파니: 좋아"
        # 2단계 prefix 잔존 시 A5 가 strip → "[00:10] 안녕" 등으로 출력 (test 의도 catch)
        aligned_json = json.dumps({"outputs": ["A: 안녕", "B: 안녕", "A: 좋아"]}, ensure_ascii=False)
        with patch("gurunote.llm._call_llm") as mock_freeform, \
             patch("gurunote.llm._call_llm_with_continuation") as mock_align:
            mock_freeform.return_value = freeform_text
            mock_align.return_value = (aligned_json, "stop")
            result = translate_chunk_index_mapping_v2(sample_chunk, "", mock_cfg)
        # 2-pass — 1단계 + 2단계 각 1회
        assert mock_freeform.call_count == 1
        assert mock_align.call_count == 1
        # A5 strip 후 client zip — timestamp + prefix 없는 본문
        assert "[00:10] 안녕" in result
        assert "[00:10] A: 안녕" not in result   # prefix strip catch
        assert "[00:13] 안녕" in result

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


# =============================================================================
# A5 (5/23) — deterministic 후처리 (prefix strip + 빈 검출 + 반복 경고)
# =============================================================================
class TestStripSpeakerPrefix:
    def test_strips_single_uppercase_prefix(self):
        # "A: " "B: " 단일 대문자 + 콜론 + 공백 strip
        assert _strip_input_speaker_prefix("A: 티파니 잔젠: 안녕하세요") == "티파니 잔젠: 안녕하세요"
        assert _strip_input_speaker_prefix("B: 판카즈 샤르마: 본문") == "판카즈 샤르마: 본문"
        assert _strip_input_speaker_prefix("Z: 한국어 화자명: 본문") == "한국어 화자명: 본문"

    def test_preserves_normal_korean_label(self):
        # 정상 한국어 화자 라벨 보존 (단일 대문자 부재)
        assert _strip_input_speaker_prefix("티파니 잔젠: 본문") == "티파니 잔젠: 본문"
        assert _strip_input_speaker_prefix("판카즈 샤르마: 본문") == "판카즈 샤르마: 본문"

    def test_preserves_english_annotation(self):
        # 영문 병기 보존 — line 시작이 한국어이므로 매치 부재
        assert (
            _strip_input_speaker_prefix("티파니 잔젠(Tiffany Janzen): 본문")
            == "티파니 잔젠(Tiffany Janzen): 본문"
        )

    def test_preserves_english_name_starting_word(self):
        # 영문 단어로 시작 — 다음 글자가 소문자 → 매치 부재 ("Jensen Huang: " 등)
        assert _strip_input_speaker_prefix("Jensen Huang: 본문") == "Jensen Huang: 본문"
        assert _strip_input_speaker_prefix("Pankaj Sharma: 안녕") == "Pankaj Sharma: 안녕"

    def test_preserves_multi_letter_uppercase(self):
        # "AI: ..." 같은 대문자 약어 다음에 콜론 — 매치 부재 (단일 대문자만 catch)
        assert _strip_input_speaker_prefix("AI: 이것은 매핑 부재") == "AI: 이것은 매핑 부재"
        assert _strip_input_speaker_prefix("CEO: 본문") == "CEO: 본문"

    def test_preserves_empty_and_none_safe(self):
        # 빈 string 안전
        assert _strip_input_speaker_prefix("") == ""

    def test_only_strips_line_start_prefix(self):
        # 본문 중간의 "A: " 패턴은 보존 (line 시작 영문 대문자만)
        assert (
            _strip_input_speaker_prefix("티파니 잔젠: A: 인용 본문")
            == "티파니 잔젠: A: 인용 본문"
        )


class TestPostProcessTwoPassOutputs:
    def test_empty_output_replaced_with_translation_missing(self):
        # 빈 string → [번역 누락] 교체
        outputs = ["정상 본문 1", "", "정상 본문 2"]
        log_messages = []
        result = _post_process_two_pass_outputs(outputs, 3, log_messages.append)
        assert result == ["정상 본문 1", "[번역 누락]", "정상 본문 2"]
        # log 경고 catch
        assert any("빈 output" in m for m in log_messages)

    def test_whitespace_only_output_replaced(self):
        # whitespace 만 있는 output 도 빈 catch → [번역 누락]
        outputs = ["정상", "   ", "\n\n", "정상2"]
        result = _post_process_two_pass_outputs(outputs, 4)
        assert result[1] == "[번역 누락]"
        assert result[2] == "[번역 누락]"

    def test_prefix_strip_applied_to_all_outputs(self):
        # 모든 output 에 prefix strip 적용
        outputs = ["A: 티파니 잔젠: 본문 1", "B: 판카즈 샤르마: 본문 2", "정상: 본문 3"]
        result = _post_process_two_pass_outputs(outputs, 3)
        assert result == [
            "티파니 잔젠: 본문 1",
            "판카즈 샤르마: 본문 2",
            "정상: 본문 3",
        ]

    def test_consecutive_repeat_log_warning(self):
        # 연속 동일 output → log 경고 (자동 제거 부재)
        outputs = ["본문 X", "본문 Y", "본문 Y", "본문 Z"]
        log_messages = []
        result = _post_process_two_pass_outputs(outputs, 4, log_messages.append)
        # 자동 제거 부재 — 원본 그대로 (단 prefix strip 적용)
        assert result == ["본문 X", "본문 Y", "본문 Y", "본문 Z"]
        # 경고 log catch
        assert any("연속 동일 output" in m for m in log_messages)

    def test_no_repeat_no_warning(self):
        # 반복 부재 시 경고 부재
        outputs = ["본문 1", "본문 2", "본문 3"]
        log_messages = []
        _post_process_two_pass_outputs(outputs, 3, log_messages.append)
        assert not any("연속 동일 output" in m for m in log_messages)

    def test_translation_missing_repeat_not_warned(self):
        # 연속 [번역 누락] 은 정상 fallback 패턴 — 경고 부재 (조건: != "[번역 누락]")
        outputs = ["[번역 누락]", "[번역 누락]", "정상"]
        log_messages = []
        _post_process_two_pass_outputs(outputs, 3, log_messages.append)
        assert not any("연속 동일 output" in m for m in log_messages)

    def test_preserves_output_length(self):
        # 후처리가 길이 변경 부재 catch (expected_count 보존)
        outputs = ["A: x", "", "Y: y", ""]
        result = _post_process_two_pass_outputs(outputs, 4)
        assert len(result) == 4


class TestTwoPassWithPostProcess:
    def test_two_pass_strips_prefix_in_final_outputs(self, mock_cfg, sample_chunk):
        # _translate_chunk_two_pass 의 최종 outputs 에 prefix strip 적용 확인
        freeform_text = "A: 티파니 잔젠: 안녕\n\nB: 판카즈 샤르마: 인사\n\nA: 티파니 잔젠: 답변"
        # 2단계가 1단계 prefix 잔존 출력했을 case
        aligned_json = json.dumps({
            "outputs": [
                "A: 티파니 잔젠: 안녕",
                "B: 판카즈 샤르마: 인사",
                "A: 티파니 잔젠: 답변",
            ]
        }, ensure_ascii=False)
        with patch("gurunote.llm._call_llm") as mock_freeform, \
             patch("gurunote.llm._call_llm_with_continuation") as mock_align:
            mock_freeform.return_value = freeform_text
            mock_align.return_value = (aligned_json, "stop")
            outputs = _translate_chunk_two_pass(sample_chunk, "", mock_cfg)
        # 모든 output 에서 A:/B: 제거 catch
        assert outputs == ["티파니 잔젠: 안녕", "판카즈 샤르마: 인사", "티파니 잔젠: 답변"]

    def test_two_pass_empty_segment_replaced(self, mock_cfg, sample_chunk):
        # 2단계가 빈 segment 반환 시 [번역 누락] 교체
        aligned_json = json.dumps({
            "outputs": ["정상 본문 1", "", "정상 본문 3"]
        }, ensure_ascii=False)
        with patch("gurunote.llm._call_llm") as mock_freeform, \
             patch("gurunote.llm._call_llm_with_continuation") as mock_align:
            mock_freeform.return_value = "정상 1\n\n정상 2\n\n정상 3"
            mock_align.return_value = (aligned_json, "stop")
            outputs = _translate_chunk_two_pass(sample_chunk, "", mock_cfg)
        assert outputs[1] == "[번역 누락]"
