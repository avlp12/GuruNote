"""B02 slow chunk wall-clock timeout 단위 테스트.

Phase 4a-1 httpx read timeout 의 한계 (streaming read 시 wall-clock 부재) 차단.
ThreadPoolExecutor + future.result(timeout) 으로 sync 함수의 wall-clock 강제 catch.
"""
from __future__ import annotations

import time

import pytest

from gurunote.llm import (
    DEFAULT_LLM_CHUNK_TIMEOUT_SEC,
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
