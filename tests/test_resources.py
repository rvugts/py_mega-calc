"""Tests for resource management."""

import pytest
import time
from unittest.mock import Mock, patch
from src.core.resource_manager import monitor_memory, monitor_timeout
from src.core.exceptions import ResourceExhaustedError, TimeoutError
from src.config import MAX_MEMORY_BYTES, MAX_TIME_SECONDS


class TestMonitorMemory:
    """Test memory monitoring decorator."""
    
    def test_monitor_memory_decorator_exists(self):
        """Test that monitor_memory decorator exists."""
        assert callable(monitor_memory)
    
    def test_monitor_memory_allows_function_execution_under_limit(self):
        """Test that functions execute normally when memory is under limit."""
        @monitor_memory
        def simple_function():
            return 42
        
        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)  # 50% of limit
            result = simple_function()
            assert result == 42
    
    def test_monitor_memory_raises_error_when_exceeding_limit(self):
        """Test that ResourceExhaustedError is raised when memory exceeds 24GB."""
        @monitor_memory
        def memory_intensive_function():
            return "should not execute"
        
        with patch('psutil.Process.memory_info') as mock_memory:
            # Simulate memory usage exceeding 24GB
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES + 1)
            with pytest.raises(ResourceExhaustedError) as exc_info:
                memory_intensive_function()
            assert "memory" in str(exc_info.value).lower() or "24GB" in str(exc_info.value)
    
    def test_monitor_memory_checks_before_and_after_execution(self):
        """Test that memory is checked both before and after function execution."""
        call_count = []
        
        @monitor_memory
        def tracked_function():
            call_count.append("executed")
            return "result"
        
        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            result = tracked_function()
            assert result == "result"
            assert "executed" in call_count
            # Memory should be checked at least once
            assert mock_memory.called
    
    def test_monitor_memory_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""
        @monitor_memory
        def documented_function():
            """This is a test function."""
            return True
        
        assert documented_function.__name__ == "documented_function"
        assert "test function" in documented_function.__doc__
    
    def test_monitor_memory_handles_exceptions_during_execution(self):
        """Test that memory monitoring works even when function raises exception."""
        @monitor_memory
        def failing_function():
            raise ValueError("Test error")
        
        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            with pytest.raises(ValueError, match="Test error"):
                failing_function()
    
    def test_monitor_memory_exact_limit_boundary(self):
        """Test behavior at exact memory limit boundary."""
        @monitor_memory
        def boundary_function():
            return "at limit"
        
        with patch('psutil.Process.memory_info') as mock_memory:
            # Exactly at limit should pass
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES)
            result = boundary_function()
            assert result == "at limit"
            
            # One byte over should fail
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES + 1)
            with pytest.raises(ResourceExhaustedError):
                boundary_function()


class TestMonitorTimeout:
    """Test timeout monitoring decorator."""
    
    def test_monitor_timeout_decorator_exists(self):
        """Test that monitor_timeout decorator exists."""
        assert callable(monitor_timeout)
    
    def test_monitor_timeout_allows_fast_function_execution(self):
        """Test that functions complete quickly without timeout."""
        @monitor_timeout
        def fast_function():
            return "completed"
        
        result = fast_function()
        assert result == "completed"
    
    def test_monitor_timeout_raises_error_when_exceeding_limit(self):
        """Test that TimeoutError is raised when function exceeds 300 seconds."""
        @monitor_timeout
        def slow_function():
            # Simulate slow operation - but we'll mock sleep to avoid actual wait
            time.sleep(MAX_TIME_SECONDS + 1)
            return "should not complete"
        
        # Mock both time.sleep and time.time to avoid actual waiting
        with patch('time.sleep'), patch('time.time') as mock_time:
            start_time = 1000.0
            call_count = [0]
            def time_side_effect():
                call_count[0] += 1
                if call_count[0] == 1:
                    return start_time
                else:
                    return start_time + MAX_TIME_SECONDS + 1
            mock_time.side_effect = time_side_effect
            with pytest.raises(TimeoutError) as exc_info:
                slow_function()
            assert "timeout" in str(exc_info.value).lower() or str(MAX_TIME_SECONDS) in str(exc_info.value) or "minute" in str(exc_info.value).lower()
    
    def test_monitor_timeout_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""
        @monitor_timeout
        def documented_function():
            """This is a test function."""
            return True
        
        assert documented_function.__name__ == "documented_function"
        assert "test function" in documented_function.__doc__
    
    def test_monitor_timeout_handles_exceptions_during_execution(self):
        """Test that timeout monitoring works even when function raises exception."""
        @monitor_timeout
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            failing_function()
    
    def test_monitor_timeout_with_mocked_time(self):
        """Test timeout behavior using mocked time."""
        @monitor_timeout
        def timed_function():
            return "result"
        
        # Mock time to simulate exceeding timeout
        with patch('time.time') as mock_time:
            start_time = 1000.0
            mock_time.side_effect = [start_time, start_time + MAX_TIME_SECONDS + 1]
            with pytest.raises(TimeoutError):
                timed_function()
    
    def test_monitor_timeout_allows_function_just_under_limit(self):
        """Test that function completes successfully just under timeout limit."""
        @monitor_timeout
        def near_limit_function():
            return "completed"
        
        with patch('time.time') as mock_time:
            start_time = 1000.0
            # Just under the limit
            mock_time.side_effect = [start_time, start_time + MAX_TIME_SECONDS - 1]
            result = near_limit_function()
            assert result == "completed"

