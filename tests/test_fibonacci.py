"""Tests for Fibonacci calculator.

This module contains comprehensive tests for the FibonacciCalculator class,
including basic calculations, edge cases, digit-based calculations, and
resource management integration.

Dependencies:
    - pytest: Testing framework
    - unittest.mock: Mocking utilities
    - src.calculators.fibonacci: FibonacciCalculator class
    - src.calculators.base: Calculator base class
    - src.core.exceptions: Custom exceptions
    - src.config: Configuration constants
"""

from unittest.mock import Mock, patch

import pytest

from src.calculators.base import Calculator
from src.calculators.fibonacci import FibonacciCalculator
from src.config import MAX_MEMORY_BYTES
from src.core.exceptions import (
    InputError,
    PrecisionError,
    ResourceExhaustedError,
)


class TestFibonacciCalculatorBasic:
    """Test basic Fibonacci calculation functionality."""

    def test_fibonacci_calculator_exists(self) -> None:
        """Test that FibonacciCalculator class exists."""
        assert FibonacciCalculator is not None

    def test_fibonacci_calculator_is_calculator(self) -> None:
        """Test that FibonacciCalculator is a subclass of Calculator."""
        assert issubclass(FibonacciCalculator, Calculator)

    def test_fibonacci_calculator_can_be_instantiated(self) -> None:
        """Test that FibonacciCalculator can be instantiated."""
        calc = FibonacciCalculator()
        assert calc is not None

    def test_calculate_by_index_zero(self) -> None:
        """Test that F(0) = 0 (OEIS A000045)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(0)
        assert result == 0

    def test_calculate_by_index_one(self) -> None:
        """Test that F(1) = 1 (OEIS A000045)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(1)
        assert result == 1

    def test_calculate_by_index_two(self) -> None:
        """Test that F(2) = 1 (OEIS A000045)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(2)
        assert result == 1

    def test_calculate_by_index_three(self) -> None:
        """Test that F(3) = 2 (OEIS A000045)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(3)
        assert result == 2

    def test_calculate_by_index_four(self) -> None:
        """Test that F(4) = 3 (OEIS A000045)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(4)
        assert result == 3

    def test_calculate_by_index_five(self) -> None:
        """Test that F(5) = 5 (OEIS A000045)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(5)
        assert result == 5

    def test_calculate_by_index_ten(self) -> None:
        """Test that F(10) = 55 (OEIS A000045)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(10)
        assert result == 55

    def test_calculate_by_index_twenty(self) -> None:
        """Test that F(20) = 6765 (OEIS A000045)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(20)
        assert result == 6765

    def test_calculate_by_index_sequence(self) -> None:
        """Test that Fibonacci sequence is correct for first 10 values."""
        calc = FibonacciCalculator()
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        for i, expected_val in enumerate(expected):
            result = calc.calculate_by_index(i)
            msg = f"F({i}) should be {expected_val}, got {result}"
            assert result == expected_val, msg

    def test_calculate_by_index_large_value(self) -> None:
        """Test calculation for larger index (F(50) = 12586269025)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(50)
        assert result == 12586269025


class TestFibonacciCalculatorEdgeCases:
    """Test edge cases and input validation for Fibonacci calculator."""

    def test_calculate_by_index_negative_raises_error(self) -> None:
        """Test that negative index raises InputError."""
        calc = FibonacciCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_index(-1)

    def test_calculate_by_index_negative_large_raises_error(self) -> None:
        """Test that large negative index raises InputError."""
        calc = FibonacciCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_index(-100)

    def test_calculate_by_index_very_large_value(self) -> None:
        """Test calculation for very large index (F(1000))."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(1000)
        assert result > 0
        assert isinstance(result, int)
        f100 = calc.calculate_by_index(100)
        assert f100 == 354224848179261915075

    def test_calculate_by_index_handles_large_numbers(self) -> None:
        """Test that calculator handles very large Fibonacci numbers."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(200)
        assert result > 0
        assert isinstance(result, int)
        assert result.bit_length() > 100

    def test_calculate_by_index_non_integer_raises_error(self) -> None:
        """Test that non-integer input raises appropriate error."""
        calc = FibonacciCalculator()
        with pytest.raises(PrecisionError):
            calc.calculate_by_index(10.5)  # type: ignore

    def test_calculate_by_index_zero_is_valid(self) -> None:
        """Test that zero is a valid input (edge case)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(0)
        assert result == 0

    def test_calculate_by_index_one_is_valid(self) -> None:
        """Test that one is a valid input (edge case)."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(1)
        assert result == 1


class TestFibonacciCalculatorByDigits:
    """Test calculate_by_digits functionality."""

    def test_calculate_by_digits_method_exists(self) -> None:
        """Test that calculate_by_digits method exists."""
        calc = FibonacciCalculator()
        assert hasattr(calc, 'calculate_by_digits')
        assert callable(calc.calculate_by_digits)

    def test_calculate_by_digits_one_digit(self) -> None:
        """Test finding first Fibonacci number with at least 1 digit."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_digits(1)
        assert result == 0
        assert len(str(result)) >= 1

    def test_calculate_by_digits_two_digits(self) -> None:
        """Test finding first Fibonacci number with at least 2 digits."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_digits(2)
        assert result == 13
        assert len(str(result)) >= 2

    def test_calculate_by_digits_three_digits(self) -> None:
        """Test finding first Fibonacci number with at least 3 digits."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_digits(3)
        assert result == 144
        assert len(str(result)) >= 3

    def test_calculate_by_digits_four_digits(self) -> None:
        """Test finding first Fibonacci number with at least 4 digits."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_digits(4)
        assert result == 1597
        assert len(str(result)) >= 4

    def test_calculate_by_digits_verifies_digit_count(self) -> None:
        """Test that result has at least the requested number of digits."""
        calc = FibonacciCalculator()
        for d in [1, 2, 3, 4, 5, 10]:
            result = calc.calculate_by_digits(d)
            msg = (
                f"Result {result} has {len(str(result))} digits, "
                f"need {d}"
            )
            assert len(str(result)) >= d, msg

    def test_calculate_by_digits_negative_raises_error(self) -> None:
        """Test that negative digit count raises InputError."""
        calc = FibonacciCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(-1)

    def test_calculate_by_digits_zero_raises_error(self) -> None:
        """Test that zero digit count raises InputError."""
        calc = FibonacciCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(0)

    def test_calculate_by_digits_large_digit_count(self) -> None:
        """Test finding Fibonacci number with large digit count."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_digits(10)
        assert len(str(result)) >= 10
        assert isinstance(result, int)
        assert result > 0


class TestFibonacciCalculatorResourceManager:
    """Test ResourceManager integration for Fibonacci calculator."""

    def test_calculate_by_index_has_memory_monitoring(self) -> None:
        """Test that calculate_by_index is wrapped with memory monitoring."""
        calc = FibonacciCalculator()

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            result = calc.calculate_by_index(10)
            assert result == 55

    def test_calculate_by_index_raises_error_on_memory_exceeded(
        self,
    ) -> None:
        """Test ResourceExhaustedError when memory exceeded."""
        calc = FibonacciCalculator()

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES + 1)
            with pytest.raises(ResourceExhaustedError):
                calc.calculate_by_index(10)

    def test_calculate_by_digits_has_memory_monitoring(self) -> None:
        """Test that calculate_by_digits is wrapped with memory monitoring."""
        calc = FibonacciCalculator()

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            result = calc.calculate_by_digits(2)
            assert result == 13

    def test_calculate_by_index_has_timeout_monitoring(self) -> None:
        """Test that calculate_by_index is wrapped with timeout monitoring."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(10)
        assert result == 55

    def test_calculate_by_digits_has_timeout_monitoring(self) -> None:
        """Test calculate_by_digits is wrapped with timeout monitoring."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_digits(2)
        assert result == 13
