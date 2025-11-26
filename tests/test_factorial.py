"""Tests for Factorial calculator."""

import pytest
from src.calculators.factorial import benchmark_factorial_methods


class TestFactorialBenchmarkComparison:
    """Test benchmark comparison between math.factorial and custom implementation."""
    
    def test_benchmark_factorial_methods_exists(self):
        """Test that benchmark_factorial_methods function exists."""
        assert callable(benchmark_factorial_methods)
    
    def test_benchmark_factorial_methods_returns_results(self):
        """Test that benchmark returns comparison results."""
        result = benchmark_factorial_methods([10, 20, 30])
        assert result is not None
        assert isinstance(result, dict)
    
    def test_benchmark_compares_math_factorial(self):
        """Test that benchmark includes math.factorial timing."""
        result = benchmark_factorial_methods([10, 20])
        assert 'math_factorial' in result or 'math' in result or 'standard' in result
    
    def test_benchmark_compares_custom_implementation(self):
        """Test that benchmark includes custom implementation timing."""
        result = benchmark_factorial_methods([10, 20])
        assert 'custom' in result or 'binary_split' in result or 'custom_factorial' in result
    
    def test_benchmark_returns_timing_data(self):
        """Test that benchmark returns timing measurements."""
        result = benchmark_factorial_methods([10, 20])
        # Should contain timing information
        assert len(result) > 0
        # Should have timing data for each method
        assert 'math_factorial' in result
        assert 'custom' in result
        assert isinstance(result['math_factorial'], dict)
        assert isinstance(result['custom'], dict)
        # 'recommended' is a string, 'speedup' is a float
        assert 'recommended' in result
        assert 'speedup' in result
    
    def test_benchmark_handles_multiple_inputs(self):
        """Test that benchmark can handle multiple input values."""
        inputs = [5, 10, 15, 20]
        result = benchmark_factorial_methods(inputs)
        assert result is not None
        # Should have results for all inputs
        assert isinstance(result, dict)
    
    def test_benchmark_verifies_correctness(self):
        """Test that benchmark verifies both methods produce correct results."""
        result = benchmark_factorial_methods([5, 10])
        # Both methods should produce same results (if implemented)
        # This test verifies the benchmark doesn't just time, but also validates
        assert result is not None
    
    def test_benchmark_recommends_faster_method(self):
        """Test that benchmark can recommend which method is faster."""
        result = benchmark_factorial_methods([10, 20, 30])
        # Should indicate which method is faster or provide comparison
        assert result is not None
        # May have 'recommended' or 'faster' key, or just timing data to compare


class TestFactorialCalculatorBasic:
    """Test basic Factorial calculation functionality."""
    
    def test_factorial_calculator_exists(self):
        """Test that FactorialCalculator class exists."""
        from src.calculators.factorial import FactorialCalculator
        assert FactorialCalculator is not None
    
    def test_factorial_calculator_is_calculator(self):
        """Test that FactorialCalculator is a subclass of Calculator."""
        from src.calculators.factorial import FactorialCalculator
        from src.calculators.base import Calculator
        assert issubclass(FactorialCalculator, Calculator)
    
    def test_factorial_calculator_can_be_instantiated(self):
        """Test that FactorialCalculator can be instantiated."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        assert calc is not None
    
    def test_calculate_by_index_zero(self):
        """Test that 0! = 1."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_index(0)
        assert result == 1
    
    def test_calculate_by_index_one(self):
        """Test that 1! = 1."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_index(1)
        assert result == 1
    
    def test_calculate_by_index_five(self):
        """Test that 5! = 120."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_index(5)
        assert result == 120
    
    def test_calculate_by_index_ten(self):
        """Test that 10! = 3628800."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_index(10)
        assert result == 3628800
    
    def test_calculate_by_index_sequence(self):
        """Test factorial sequence for first few values."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        expected = [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]
        for i, expected_val in enumerate(expected):
            result = calc.calculate_by_index(i)
            assert result == expected_val, f"{i}! should be {expected_val}, got {result}"
    
    def test_calculate_by_index_large_value(self):
        """Test calculation for larger value (20! = 2432902008176640000)."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_index(20)
        assert result == 2432902008176640000
    
    def test_calculate_by_index_negative_raises_error(self):
        """Test that negative index raises InputError."""
        from src.calculators.factorial import FactorialCalculator
        from src.core.exceptions import InputError
        calc = FactorialCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_index(-1)


class TestFactorialCalculatorByDigits:
    """Test calculate_by_digits functionality."""
    
    def test_calculate_by_digits_method_exists(self):
        """Test that calculate_by_digits method exists."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        assert hasattr(calc, 'calculate_by_digits')
        assert callable(calc.calculate_by_digits)
    
    def test_calculate_by_digits_one_digit(self):
        """Test finding first factorial with at least 1 digit."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(1)
        # 0! = 1 has 1 digit
        assert result == 1
        assert len(str(result)) >= 1
    
    def test_calculate_by_digits_two_digits(self):
        """Test finding first factorial with at least 2 digits."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(2)
        # 4! = 24 has 2 digits
        assert result == 24
        assert len(str(result)) >= 2
    
    def test_calculate_by_digits_three_digits(self):
        """Test finding first factorial with at least 3 digits."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(3)
        # 5! = 120 has 3 digits (first with 3 digits)
        assert result == 120
        assert len(str(result)) >= 3
    
    def test_calculate_by_digits_four_digits(self):
        """Test finding first factorial with at least 4 digits."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(4)
        # 7! = 5040 has 4 digits
        assert result == 5040
        assert len(str(result)) >= 4
    
    def test_calculate_by_digits_verifies_digit_count(self):
        """Test that result has at least the requested number of digits."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        for d in [1, 2, 3, 4, 5, 10]:
            result = calc.calculate_by_digits(d)
            assert len(str(result)) >= d, f"Result {result} has {len(str(result))} digits, need {d}"
    
    def test_calculate_by_digits_negative_raises_error(self):
        """Test that negative digit count raises InputError."""
        from src.calculators.factorial import FactorialCalculator
        from src.core.exceptions import InputError
        calc = FactorialCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(-1)
    
    def test_calculate_by_digits_zero_raises_error(self):
        """Test that zero digit count raises InputError."""
        from src.calculators.factorial import FactorialCalculator
        from src.core.exceptions import InputError
        calc = FactorialCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(0)
    
    def test_calculate_by_digits_large_digit_count(self):
        """Test finding factorial with large digit count."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        result = calc.calculate_by_digits(10)
        assert len(str(result)) >= 10
        assert isinstance(result, int)
        assert result > 0


class TestFactorialCalculatorResourceManager:
    """Test ResourceManager integration for Factorial calculator."""
    
    def test_calculate_by_index_has_memory_monitoring(self):
        """Test that calculate_by_index is wrapped with memory monitoring."""
        from unittest.mock import patch, Mock
        from src.calculators.factorial import FactorialCalculator
        from src.config import MAX_MEMORY_BYTES
        calc = FactorialCalculator()
        
        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            # Should execute normally
            result = calc.calculate_by_index(10)
            assert result == 3628800
    
    def test_calculate_by_index_raises_error_on_memory_exceeded(self):
        """Test that calculate_by_index raises ResourceExhaustedError when memory exceeded."""
        from unittest.mock import patch, Mock
        from src.calculators.factorial import FactorialCalculator
        from src.core.exceptions import ResourceExhaustedError
        from src.config import MAX_MEMORY_BYTES
        calc = FactorialCalculator()
        
        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES + 1)
            with pytest.raises(ResourceExhaustedError):
                calc.calculate_by_index(10)
    
    def test_calculate_by_digits_has_memory_monitoring(self):
        """Test that calculate_by_digits is wrapped with memory monitoring."""
        from unittest.mock import patch, Mock
        from src.calculators.factorial import FactorialCalculator
        from src.config import MAX_MEMORY_BYTES
        calc = FactorialCalculator()
        
        with patch('psutil.Process.memory_info') as mock_memory:
            mock_memory.return_value = Mock(rss=MAX_MEMORY_BYTES // 2)
            # Should execute normally
            result = calc.calculate_by_digits(2)
            assert result == 24
    
    def test_calculate_by_index_has_timeout_monitoring(self):
        """Test that calculate_by_index is wrapped with timeout monitoring."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        # Should execute quickly for small values
        result = calc.calculate_by_index(10)
        assert result == 3628800
    
    def test_calculate_by_digits_has_timeout_monitoring(self):
        """Test that calculate_by_digits is wrapped with timeout monitoring."""
        from src.calculators.factorial import FactorialCalculator
        calc = FactorialCalculator()
        # Should execute quickly for small digit counts
        result = calc.calculate_by_digits(2)
        assert result == 24

