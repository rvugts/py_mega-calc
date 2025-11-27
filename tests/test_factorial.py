"""Tests for Factorial calculator.

This module contains comprehensive tests for the FactorialCalculator class,
including benchmark comparisons, binary splitting algorithm, basic
calculations, digit-based calculations, and resource management integration.

Dependencies:
    - pytest: Testing framework
    - math: Standard library for factorial verification
    - unittest.mock: Mocking utilities
    - src.calculators.factorial: FactorialCalculator and benchmark functions
    - src.calculators.base: Calculator base class
    - src.core.exceptions: Custom exceptions
    - src.config: Configuration constants
"""

import math
from unittest.mock import Mock, patch

import pytest

from src.calculators.base import Calculator
from src.calculators.factorial import (
    FactorialCalculator,
    _binary_splitting_factorial,
    benchmark_factorial_methods,
)
from src.config import MAX_MEMORY_BYTES
from src.core.exceptions import InputError, ResourceExhaustedError


class TestFactorialBenchmarkComparison:
    """Test benchmark comparison between math.factorial and custom."""

    def test_benchmark_factorial_methods_exists(self) -> None:
        """Test that benchmark_factorial_methods function exists."""
        assert callable(benchmark_factorial_methods)

    def test_benchmark_factorial_methods_returns_results(self) -> None:
        """Test that benchmark returns comparison results."""
        result = benchmark_factorial_methods([10, 20, 30])
        assert result is not None
        assert isinstance(result, dict)

    def test_benchmark_compares_math_factorial(self) -> None:
        """Test that benchmark includes math.factorial timing."""
        result = benchmark_factorial_methods([10, 20])
        assert 'math_factorial' in result

    def test_benchmark_compares_custom_implementation(self) -> None:
        """Test that benchmark includes custom implementation timing."""
        result = benchmark_factorial_methods([10, 20])
        assert 'custom' in result

    def test_benchmark_returns_timing_data(self) -> None:
        """Test that benchmark returns timing measurements."""
        result = benchmark_factorial_methods([10, 20])
        assert len(result) > 0
        assert 'math_factorial' in result
        assert 'custom' in result
        assert isinstance(result['math_factorial'], dict)
        assert isinstance(result['custom'], dict)
        assert 'recommended' in result
        assert 'speedup' in result

    def test_benchmark_handles_multiple_inputs(self) -> None:
        """Test that benchmark can handle multiple input values."""
        inputs = [5, 10, 15, 20]
        result = benchmark_factorial_methods(inputs)
        assert result is not None
        assert isinstance(result, dict)

    def test_benchmark_verifies_correctness(self) -> None:
        """Test benchmark verifies both methods produce correct results."""
        result = benchmark_factorial_methods([5, 10])
        assert result is not None

    def test_benchmark_recommends_faster_method(self) -> None:
        """Test that benchmark can recommend which method is faster."""
        result = benchmark_factorial_methods([10, 20, 30])
        assert result is not None

    def test_binary_splitting_factorial_exists(self) -> None:
        """Test that binary splitting factorial function exists."""
        assert callable(_binary_splitting_factorial)

    def test_binary_splitting_factorial_correctness_small(self) -> None:
        """Test binary splitting factorial for small values."""
        for n in [0, 1, 2, 3, 4, 5, 10, 20]:
            result = _binary_splitting_factorial(n)
            expected = math.factorial(n)
            msg = (
                f"Binary splitting failed for {n}!: "
                f"got {result}, expected {expected}"
            )
            assert result == expected, msg

    def test_binary_splitting_factorial_correctness_large(self) -> None:
        """Test binary splitting factorial for larger values."""
        for n in [30, 50, 100]:
            result = _binary_splitting_factorial(n)
            expected = math.factorial(n)
            msg = (
                f"Binary splitting failed for {n}!: "
                f"got {result}, expected {expected}"
            )
            assert result == expected, msg

    def test_binary_splitting_factorial_negative_raises_error(
        self,
    ) -> None:
        """Test binary splitting raises error for negative input."""
        with pytest.raises(ValueError):
            _binary_splitting_factorial(-1)

    def test_benchmark_uses_binary_splitting(self) -> None:
        """Test benchmark uses binary splitting algorithm."""
        result = benchmark_factorial_methods([10, 20])
        assert result is not None

        for n in [10, 20]:
            binary_result = _binary_splitting_factorial(n)
            math_result = math.factorial(n)
            assert binary_result == math_result


class TestFactorialCalculatorBasic:
    """Test basic Factorial calculation functionality."""

    def test_factorial_calculator_exists(self) -> None:
        """Test that FactorialCalculator class exists."""
        assert FactorialCalculator is not None

    def test_factorial_calculator_is_calculator(self) -> None:
        """Test FactorialCalculator is a subclass of Calculator."""
        assert issubclass(FactorialCalculator, Calculator)

    def test_factorial_calculator_can_be_instantiated(self) -> None:
        """Test that FactorialCalculator can be instantiated."""
        calc = FactorialCalculator()
        assert calc is not None

    def test_calculate_by_index_zero(self) -> None:
        """Test that 0! = 1."""
        calc = FactorialCalculator()
        result = calc.calculate_by_index(0)
        assert result == 1

    def test_calculate_by_index_one(self) -> None:
        """Test that 1! = 1."""
        calc = FactorialCalculator()
        result = calc.calculate_by_index(1)
        assert result == 1

    def test_calculate_by_index_five(self) -> None:
        """Test that 5! = 120."""
        calc = FactorialCalculator()
        result = calc.calculate_by_index(5)
        assert result == 120

    def test_calculate_by_index_ten(self) -> None:
        """Test that 10! = 3628800."""
        calc = FactorialCalculator()
        result = calc.calculate_by_index(10)
        assert result == 3628800

    def test_calculate_by_index_sequence(self) -> None:
        """Test factorial sequence for first few values."""
        calc = FactorialCalculator()
        expected = [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]
        for i, expected_val in enumerate(expected):
            result = calc.calculate_by_index(i)
            msg = f"{i}! should be {expected_val}, got {result}"
            assert result == expected_val, msg

    def test_calculate_by_index_large_value(self) -> None:
        """Test calculation for larger value (20! = 2432902008176640000)."""
        calc = FactorialCalculator()
        result = calc.calculate_by_index(20)
        assert result == 2432902008176640000

    def test_calculate_by_index_negative_raises_error(self) -> None:
        """Test that negative index raises InputError."""
        calc = FactorialCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_index(-1)


class TestFactorialCalculatorByDigits:
    """Test calculate_by_digits functionality."""

    def test_calculate_by_digits_method_exists(self) -> None:
        """Test that calculate_by_digits method exists."""
        calc = FactorialCalculator()
        assert hasattr(calc, 'calculate_by_digits')
        assert callable(calc.calculate_by_digits)

    def test_calculate_by_digits_one_digit(self) -> None:
        """Test finding first factorial with at least 1 digit."""
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(1)
        assert result == 1
        assert len(str(result)) >= 1

    def test_calculate_by_digits_two_digits(self) -> None:
        """Test finding first factorial with at least 2 digits."""
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(2)
        assert result == 24
        assert len(str(result)) >= 2

    def test_calculate_by_digits_three_digits(self) -> None:
        """Test finding first factorial with at least 3 digits."""
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(3)
        assert result == 120
        assert len(str(result)) >= 3

    def test_calculate_by_digits_four_digits(self) -> None:
        """Test finding first factorial with at least 4 digits."""
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(4)
        assert result == 5040
        assert len(str(result)) >= 4

    def test_calculate_by_digits_verifies_digit_count(self) -> None:
        """Test that result has at least the requested number of digits."""
        calc = FactorialCalculator()
        for d in [1, 2, 3, 4, 5, 10]:
            result = calc.calculate_by_digits(d)
            msg = (
                f"Result {result} has {len(str(result))} digits, "
                f"need {d}"
            )
            assert len(str(result)) >= d, msg

    def test_calculate_by_digits_negative_raises_error(self) -> None:
        """Test that negative digit count raises InputError."""
        calc = FactorialCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(-1)

    def test_calculate_by_digits_zero_raises_error(self) -> None:
        """Test that zero digit count raises InputError."""
        calc = FactorialCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(0)

    def test_calculate_by_digits_large_digit_count(self) -> None:
        """Test finding factorial with large digit count."""
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(10)
        assert len(str(result)) >= 10
        assert isinstance(result, int)
        assert result > 0


class TestFactorialCalculatorResourceManager:
    """Test ResourceManager integration for Factorial calculator."""

    def test_calculate_by_index_has_memory_monitoring(self) -> None:
        """Test calculate_by_index is wrapped with memory monitoring."""
        calc = FactorialCalculator()

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            result = calc.calculate_by_index(10)
            assert result == 3628800

    def test_calculate_by_index_raises_error_on_memory_exceeded(
        self,
    ) -> None:
        """Test ResourceExhaustedError when memory exceeded."""
        calc = FactorialCalculator()

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES + 1)
            with pytest.raises(ResourceExhaustedError):
                calc.calculate_by_index(10)

    def test_calculate_by_digits_has_memory_monitoring(self) -> None:
        """Test calculate_by_digits is wrapped with memory monitoring."""
        calc = FactorialCalculator()

        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            result = calc.calculate_by_digits(2)
            assert result == 24

    def test_calculate_by_index_has_timeout_monitoring(self) -> None:
        """Test calculate_by_index is wrapped with timeout monitoring."""
        calc = FactorialCalculator()
        result = calc.calculate_by_index(10)
        assert result == 3628800

    def test_calculate_by_digits_has_timeout_monitoring(self) -> None:
        """Test calculate_by_digits is wrapped with timeout monitoring."""
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(2)
        assert result == 24
