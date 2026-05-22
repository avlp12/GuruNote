"""B02 slow chunk wall-clock timeout 단위 테스트.

Phase 4a-1 httpx read timeout 의 한계 (streaming read 시 wall-clock 부재) 차단.
ThreadPoolExecutor + future.result(timeout) 으로 sync 함수의 wall-clock 강제 catch.
B02 한계 1 보완 (5/22): timeout 후 R1 padding fallback — TIMEOUT_PADDING_MARKER.
"""
from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from gurunote.llm import (
    DEFAULT_LLM_CHUNK_TIMEOUT_SEC,
    TIMEOUT_PADDING_MARKER,
    _call_llm_with_index_mapping,
    _call_with_wall_clock_timeout,
)


class TestDefaultTimeout:
    def test_default_value_is_60(self):
        assert DEFAULT_LLM_CHUNK_TIMEOUT_SEC == 60.0


class TestWallClockTimeout:
    def test_fast_call_returns_normally(self):
        # 빠른 호출 → 정상 return
        result = _call_with_wall_clock_timeout(lambda x: x * 2, 1.0, 21)
        assert result == 42

    def test_slow_call_raises_timeout(self):
        # 2초 sleep + 0.3초 timeout → TimeoutError raise
        with pytest.raises(TimeoutError) as exc_info:
            _call_with_wall_clock_timeout(time.sleep, 0.3, 2.0)
        # 메시지에 timeout 값 catch
        assert "0.3" in str(exc_info.value)
        assert "B02" in str(exc_info.value)

    def test_timeout_message_includes_seconds(self):
        with pytest.raises(TimeoutError) as exc_info:
            _call_with_wall_clock_timeout(time.sleep, 0.1, 1.0)
        msg = str(exc_info.value)
        assert "wall-clock timeout" in msg
        assert "0.1초" in msg

    def test_function_exception_propagates(self):
        # fn 자체가 raise → 본 exception 그대로 propagate (TimeoutError 부재)
        def raising_fn():
            raise ValueError("inner error")

        with pytest.raises(ValueError) as exc_info:
            _call_with_wall_clock_timeout(raising_fn, 1.0)
        assert "inner error" in str(exc_info.value)

    def test_args_kwargs_passed_correctly(self):
        # *args + **kwargs 모두 fn 에 전달
        def fn(a, b, c=None, d=None):
            return (a, b, c, d)

        result = _call_with_wall_clock_timeout(fn, 1.0, 1, 2, c=3, d=4)
        assert result == (1, 2, 3, 4)

    def test_return_value_passthrough(self):
        # complex return (dict, list 등) 그대로 통과
        complex_obj = {"key": [1, 2, {"nested": True}]}
        result = _call_with_wall_clock_timeout(lambda: complex_obj, 1.0)
        assert result == complex_obj

    def test_zero_timeout_raises_immediately(self):
        # 매우 짧은 timeout → 즉시 TimeoutError
        with pytest.raises(TimeoutError):
            _call_with_wall_clock_timeout(time.sleep, 0.01, 1.0)

    def test_long_timeout_allows_completion(self):
        # 긴 timeout → 짧은 sleep 완료 catch
        start = time.time()
        result = _call_with_wall_clock_timeout(
            lambda: (time.sleep(0.05), "done")[1], 5.0
        )
        elapsed = time.time() - start
        assert result == "done"
        assert elapsed < 1.0  # 5초 기다리지 않음


# =============================================================================
# B02 한계 1 보완 (5/22) — R1 padding fallback (TimeoutError 시 즉시 padding)
# =============================================================================
class TestTimeoutPaddingFallback:
    def _mock_cfg(self):
        from gurunote.llm import LLMConfig
        return LLMConfig(
            provider="openai_compatible",
            model="mock-model",
            api_key="mock-key",
            base_url="http://mock.local/v1",
        )

    def test_timeout_triggers_padding(self):
        # _call_llm_with_continuation 이 TimeoutError raise → padding 반환
        cfg = self._mock_cfg()
        with patch("gurunote.llm._call_llm_with_continuation") as mock_call:
            mock_call.side_effect = TimeoutError("LLM 호출 wall-clock timeout — 60.0초 초과 (B02)")
            outputs = _call_llm_with_index_mapping(
                cfg, "prompt", expected_count=15, max_retries=3
            )
        # 모두 TIMEOUT_PADDING_MARKER 로 padding
        assert all(o == TIMEOUT_PADDING_MARKER for o in outputs)

    def test_timeout_padding_segment_count(self):
        # padding 수 = expected_count 정합
        cfg = self._mock_cfg()
        with patch("gurunote.llm._call_llm_with_continuation") as mock_call:
            mock_call.side_effect = TimeoutError("timeout")
            outputs = _call_llm_with_index_mapping(
                cfg, "prompt", expected_count=7, max_retries=3
            )
        assert len(outputs) == 7

    def test_timeout_no_retry(self):
        # R1 — timeout 후 retry 부재 (mock 호출 1회만)
        cfg = self._mock_cfg()
        with patch("gurunote.llm._call_llm_with_continuation") as mock_call:
            mock_call.side_effect = TimeoutError("timeout")
            _call_llm_with_index_mapping(
                cfg, "prompt", expected_count=10, max_retries=3
            )
        # max_retries=3 이지만 timeout 즉시 padding 으로 1회 호출만
        assert mock_call.call_count == 1

    def test_timeout_marker_distinct_from_translation_missing(self):
        # TIMEOUT_PADDING_MARKER 가 일반 "[번역 누락]" 과 구분
        assert TIMEOUT_PADDING_MARKER != "[번역 누락]"
        assert TIMEOUT_PADDING_MARKER == "[⚠ timeout]"
