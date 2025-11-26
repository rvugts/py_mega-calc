"""Tests for custom exceptions."""

import pytest
from src.core.exceptions import (
    InputError,
    CalculationTooLargeError,
    PrecisionError,
    ResourceExhaustedError,
    TimeoutError,
)


class TestInputError:
    """Test InputError exception."""
    
    def test_input_error_is_exception(self):
        """Test that InputError is a subclass of Exception."""
        assert issubclass(InputError, Exception)
    
    def test_input_error_can_be_raised(self):
        """Test that InputError can be raised and caught."""
        with pytest.raises(InputError):
            raise InputError("Invalid input")
    
    def test_input_error_message(self):
        """Test that InputError preserves the error message."""
        message = "Negative numbers are not allowed"
        with pytest.raises(InputError) as exc_info:
            raise InputError(message)
        assert str(exc_info.value) == message


class TestCalculationTooLargeError:
    """Test CalculationTooLargeError exception."""
    
    def test_calculation_too_large_error_is_exception(self):
        """Test that CalculationTooLargeError is a subclass of Exception."""
        assert issubclass(CalculationTooLargeError, Exception)
    
    def test_calculation_too_large_error_can_be_raised(self):
        """Test that CalculationTooLargeError can be raised and caught."""
        with pytest.raises(CalculationTooLargeError):
            raise CalculationTooLargeError("Calculation too large")
    
    def test_calculation_too_large_error_message(self):
        """Test that CalculationTooLargeError preserves the error message."""
        message = "Estimated time exceeds 5 minutes"
        with pytest.raises(CalculationTooLargeError) as exc_info:
            raise CalculationTooLargeError(message)
        assert str(exc_info.value) == message


class TestPrecisionError:
    """Test PrecisionError exception."""
    
    def test_precision_error_is_exception(self):
        """Test that PrecisionError is a subclass of Exception."""
        assert issubclass(PrecisionError, Exception)
    
    def test_precision_error_can_be_raised(self):
        """Test that PrecisionError can be raised and caught."""
        with pytest.raises(PrecisionError):
            raise PrecisionError("Precision error")
    
    def test_precision_error_message(self):
        """Test that PrecisionError preserves the error message."""
        message = "Floating point arithmetic detected"
        with pytest.raises(PrecisionError) as exc_info:
            raise PrecisionError(message)
        assert str(exc_info.value) == message


class TestResourceExhaustedError:
    """Test ResourceExhaustedError exception."""
    
    def test_resource_exhausted_error_is_exception(self):
        """Test that ResourceExhaustedError is a subclass of Exception."""
        assert issubclass(ResourceExhaustedError, Exception)
    
    def test_resource_exhausted_error_can_be_raised(self):
        """Test that ResourceExhaustedError can be raised and caught."""
        with pytest.raises(ResourceExhaustedError):
            raise ResourceExhaustedError("Resource exhausted")
    
    def test_resource_exhausted_error_message(self):
        """Test that ResourceExhaustedError preserves the error message."""
        message = "Memory limit of 24GB exceeded"
        with pytest.raises(ResourceExhaustedError) as exc_info:
            raise ResourceExhaustedError(message)
        assert str(exc_info.value) == message


class TestTimeoutError:
    """Test TimeoutError exception."""
    
    def test_timeout_error_is_exception(self):
        """Test that TimeoutError is a subclass of Exception."""
        assert issubclass(TimeoutError, Exception)
    
    def test_timeout_error_can_be_raised(self):
        """Test that TimeoutError can be raised and caught."""
        with pytest.raises(TimeoutError):
            raise TimeoutError("Timeout error")
    
    def test_timeout_error_message(self):
        """Test that TimeoutError preserves the error message."""
        message = "Calculation exceeded 5 minute timeout"
        with pytest.raises(TimeoutError) as exc_info:
            raise TimeoutError(message)
        assert str(exc_info.value) == message

