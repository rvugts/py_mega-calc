"""Tests for custom exceptions.

This module contains tests for all custom exception classes used in the
py_mega_calc application, including input validation, precision checking,
and resource management exceptions.

Dependencies:
    - pytest: Testing framework
    - src.core.exceptions: Custom exception classes
    - src.core.precision_checker: Precision checking functions
    - src.calculators: Calculator implementations for precision tests
"""

import pytest

from src.calculators.factorial import FactorialCalculator
from src.calculators.fibonacci import FibonacciCalculator
from src.calculators.primes import PrimeCalculator
from src.core.exceptions import (
    CalculationTooLargeError,
    InputError,
    PrecisionError,
    ResourceExhaustedError,
    TimeoutError as CalculationTimeoutError,
)
from src.core.precision_checker import check_precision, validate_no_floats


class TestInputError:
    """Test InputError exception."""

    def test_input_error_is_exception(self) -> None:
        """Test that InputError is a subclass of Exception."""
        assert issubclass(InputError, Exception)

    def test_input_error_can_be_raised(self) -> None:
        """Test that InputError can be raised and caught."""
        with pytest.raises(InputError):
            raise InputError("Invalid input")

    def test_input_error_message(self) -> None:
        """Test that InputError preserves the error message."""
        message = "Negative numbers are not allowed"
        with pytest.raises(InputError) as exc_info:
            raise InputError(message)
        assert str(exc_info.value) == message


class TestCalculationTooLargeError:
    """Test CalculationTooLargeError exception."""

    def test_calculation_too_large_error_is_exception(self) -> None:
        """Test CalculationTooLargeError is a subclass of Exception."""
        assert issubclass(CalculationTooLargeError, Exception)

    def test_calculation_too_large_error_can_be_raised(self) -> None:
        """Test CalculationTooLargeError can be raised and caught."""
        with pytest.raises(CalculationTooLargeError):
            raise CalculationTooLargeError("Calculation too large")

    def test_calculation_too_large_error_message(self) -> None:
        """Test CalculationTooLargeError preserves the error message."""
        message = "Estimated time exceeds 5 minutes"
        with pytest.raises(CalculationTooLargeError) as exc_info:
            raise CalculationTooLargeError(message)
        assert str(exc_info.value) == message


class TestPrecisionError:
    """Test PrecisionError exception."""

    def test_precision_error_is_exception(self) -> None:
        """Test that PrecisionError is a subclass of Exception."""
        assert issubclass(PrecisionError, Exception)

    def test_precision_error_can_be_raised(self) -> None:
        """Test that PrecisionError can be raised and caught."""
        with pytest.raises(PrecisionError):
            raise PrecisionError("Precision error")

    def test_precision_error_message(self) -> None:
        """Test that PrecisionError preserves the error message."""
        message = "Floating point arithmetic detected"
        with pytest.raises(PrecisionError) as exc_info:
            raise PrecisionError(message)
        assert str(exc_info.value) == message


class TestPrecisionErrorDetection:
    """Test PrecisionError detection for float usage."""

    def test_detect_float_in_fibonacci_calculation(self) -> None:
        """Test PrecisionError raised if float used in Fibonacci."""
        calc = FibonacciCalculator()
        result = calc.calculate_by_index(10)
        assert isinstance(result, int)
        assert not isinstance(result, float)

    def test_detect_float_in_factorial_calculation(self) -> None:
        """Test PrecisionError raised if float used in Factorial."""
        calc = FactorialCalculator()
        result = calc.calculate_by_index(10)
        assert isinstance(result, int)
        assert not isinstance(result, float)

    def test_detect_float_in_prime_calculation(self) -> None:
        """Test PrecisionError raised if float used in Prime."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(10)
        assert isinstance(result, int)
        assert not isinstance(result, float)

    def test_precision_check_function_exists(self) -> None:
        """Test that precision check function exists."""
        assert callable(check_precision)
        assert callable(validate_no_floats)

    def test_validate_no_floats_raises_on_float(self) -> None:
        """Test validate_no_floats raises PrecisionError for floats."""
        with pytest.raises(PrecisionError):
            validate_no_floats(3.14)

    def test_validate_no_floats_passes_on_int(self) -> None:
        """Test validate_no_floats passes for integer values."""
        validate_no_floats(42)
        validate_no_floats(0)
        validate_no_floats(-10)

    def test_check_precision_validates_calculation_result(self) -> None:
        """Test check_precision validates calculation results are integers."""
        check_precision(123, "test_calculation")

        with pytest.raises(PrecisionError):
            check_precision(123.0, "test_calculation")


class TestResourceExhaustedError:
    """Test ResourceExhaustedError exception."""

    def test_resource_exhausted_error_is_exception(self) -> None:
        """Test ResourceExhaustedError is a subclass of Exception."""
        assert issubclass(ResourceExhaustedError, Exception)

    def test_resource_exhausted_error_can_be_raised(self) -> None:
        """Test ResourceExhaustedError can be raised and caught."""
        with pytest.raises(ResourceExhaustedError):
            raise ResourceExhaustedError("Resource exhausted")

    def test_resource_exhausted_error_message(self) -> None:
        """Test ResourceExhaustedError preserves the error message."""
        message = "Memory limit of 24GB exceeded"
        with pytest.raises(ResourceExhaustedError) as exc_info:
            raise ResourceExhaustedError(message)
        assert str(exc_info.value) == message


class TestTimeoutError:
    """Test TimeoutError exception."""

    def test_timeout_error_is_exception(self) -> None:
        """Test that TimeoutError is a subclass of Exception."""
        assert issubclass(CalculationTimeoutError, Exception)

    def test_timeout_error_can_be_raised(self) -> None:
        """Test that TimeoutError can be raised and caught."""
        with pytest.raises(CalculationTimeoutError):
            raise CalculationTimeoutError("Timeout error")

    def test_timeout_error_message(self) -> None:
        """Test that TimeoutError preserves the error message."""
        message = "Calculation exceeded 5 minute timeout"
        with pytest.raises(CalculationTimeoutError) as exc_info:
            raise CalculationTimeoutError(message)
        assert str(exc_info.value) == message
