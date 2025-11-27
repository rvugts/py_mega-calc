"""Tests for resource management.

This module contains tests for memory and timeout monitoring decorators,
verifying resource limit enforcement and error handling.

Dependencies:
    - pytest: Testing framework
    - time: Time measurement
    - unittest.mock: Mocking utilities
    - src.core.resource_manager: Monitoring decorators
    - src.core.exceptions: Resource exceptions
    - src.config: Configuration constants
"""

import time
from unittest.mock import Mock, patch

import pytest

from src.config import MAX_MEMORY_BYTES, MAX_TIME_SECONDS
from src.core.exceptions import (
    ResourceExhaustedError,
    TimeoutError as CalculationTimeoutError,
)
from src.core.resource_manager import monitor_memory, monitor_timeout


class TestMonitorMemory:
    """Test memory monitoring decorator."""

    def test_monitor_memory_decorator_exists(self) -> None:
        """Test that monitor_memory decorator exists."""
        assert callable(monitor_memory)

    def test_monitor_memory_allows_function_execution_under_limit(
        self,
    ) -> None:
        """Test functions execute normally when memory is under limit."""
        @monitor_memory
        def simple_function() -> int:
            return 42

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            result = simple_function()
            assert result == 42

    def test_monitor_memory_raises_error_when_exceeding_limit(
        self,
    ) -> None:
        """Test ResourceExhaustedError raised when memory exceeds 24GB."""
        @monitor_memory
        def memory_intensive_function() -> str:
            return "should not execute"

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES + 1)
            with pytest.raises(ResourceExhaustedError) as exc_info:
                memory_intensive_function()
            error_msg = str(exc_info.value).lower()
            assert "memory" in error_msg or "24gb" in error_msg

    def test_monitor_memory_checks_before_and_after_execution(
        self,
    ) -> None:
        """Test memory is checked both before and after execution."""
        call_count: list[str] = []

        @monitor_memory
        def tracked_function() -> str:
            call_count.append("executed")
            return "result"

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            result = tracked_function()
            assert result == "result"
            assert "executed" in call_count
            assert mock_memory.called

    def test_monitor_memory_preserves_function_metadata(self) -> None:
        """Test decorator preserves function name and docstring."""
        @monitor_memory
        def documented_function() -> bool:
            """This is a test function."""
            return True

        assert documented_function.__name__ == "documented_function"
        assert "test function" in documented_function.__doc__

    def test_monitor_memory_handles_exceptions_during_execution(
        self,
    ) -> None:
        """Test memory monitoring works when function raises exception."""
        @monitor_memory
        def failing_function() -> None:
            raise ValueError("Test error")

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            with pytest.raises(ValueError, match="Test error"):
                failing_function()

    def test_monitor_memory_exact_limit_boundary(self) -> None:
        """Test behavior at exact memory limit boundary."""
        @monitor_memory
        def boundary_function() -> str:
            return "at limit"

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES)
            result = boundary_function()
            assert result == "at limit"

            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES + 1)
            with pytest.raises(ResourceExhaustedError):
                boundary_function()


class TestMonitorTimeout:
    """Test timeout monitoring decorator."""

    def test_monitor_timeout_decorator_exists(self) -> None:
        """Test that monitor_timeout decorator exists."""
        assert callable(monitor_timeout)

    def test_monitor_timeout_allows_fast_function_execution(
        self,
    ) -> None:
        """Test functions complete quickly without timeout."""
        @monitor_timeout
        def fast_function() -> str:
            return "completed"

        result = fast_function()
        assert result == "completed"

    def test_monitor_timeout_raises_error_when_exceeding_limit(
        self,
    ) -> None:
        """Test CalculationTimeoutError raised when function exceeds 300s."""
        @monitor_timeout
        def slow_function() -> str:
            time.sleep(MAX_TIME_SECONDS + 1)
            return "should not complete"

        with patch('time.sleep'), patch('time.time') as mock_time:
            start_time = 1000.0
            call_count = [0]

            def time_side_effect() -> float:
                call_count[0] += 1
                if call_count[0] == 1:
                    return start_time
                return start_time + MAX_TIME_SECONDS + 1

            mock_time.side_effect = time_side_effect
            with pytest.raises(CalculationTimeoutError) as exc_info:
                slow_function()
            error_msg = str(exc_info.value).lower()
            assert (
                "timeout" in error_msg
                or str(MAX_TIME_SECONDS) in str(exc_info.value)
                or "minute" in error_msg
            )

    def test_monitor_timeout_preserves_function_metadata(self) -> None:
        """Test decorator preserves function name and docstring."""
        @monitor_timeout
        def documented_function() -> bool:
            """This is a test function."""
            return True

        assert documented_function.__name__ == "documented_function"
        assert "test function" in documented_function.__doc__

    def test_monitor_timeout_handles_exceptions_during_execution(
        self,
    ) -> None:
        """Test timeout monitoring works when function raises exception."""
        @monitor_timeout
        def failing_function() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

    def test_monitor_timeout_with_mocked_time(self) -> None:
        """Test timeout behavior using mocked time."""
        @monitor_timeout
        def timed_function() -> str:
            return "result"

        with patch('time.time') as mock_time:
            start_time = 1000.0
            mock_time.side_effect = [
                start_time,
                start_time + MAX_TIME_SECONDS + 1,
            ]
            with pytest.raises(CalculationTimeoutError):
                timed_function()

    def test_monitor_timeout_allows_function_just_under_limit(
        self,
    ) -> None:
        """Test function completes successfully just under timeout limit."""
        @monitor_timeout
        def near_limit_function() -> str:
            return "completed"

        with patch('time.time') as mock_time:
            start_time = 1000.0
            mock_time.side_effect = [
                start_time,
                start_time + MAX_TIME_SECONDS - 1,
            ]
            result = near_limit_function()
            assert result == "completed"
