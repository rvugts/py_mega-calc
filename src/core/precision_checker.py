"""Precision checking utilities to ensure no floats are used in calculations.

This module provides functions to validate that calculations use 100% integer
arithmetic and raise PrecisionError when floating-point values are detected.

Dependencies:
    - src.core.exceptions: PrecisionError exception class
"""

from typing import Any

from src.core.exceptions import PrecisionError


def validate_no_floats(value: Any) -> None:
    """Validate that a value is not a float.

    Raises PrecisionError if the value is a float, ensuring 100% integer
    arithmetic.

    :param value: Value to check
    :type value: Any
    :raises PrecisionError: If value is a float
    """
    if isinstance(value, float):
        raise PrecisionError(
            f"Floating-point value detected: {value}. "
            "All calculations must use 100% integer arithmetic."
        )


def check_precision(
    result: Any, calculation_name: str = "calculation"
) -> None:
    """Check that a calculation result is an integer (not a float).

    Validates that calculation results maintain precision by ensuring they are
    integers, not floats.

    :param result: Calculation result to validate
    :type result: Any
    :param calculation_name: Name of the calculation for error messages
    :type calculation_name: str
    :raises PrecisionError: If result is a float or complex number
    """
    if isinstance(result, float):
        raise PrecisionError(
            f"Floating-point result detected in {calculation_name}: {result}. "
            "All calculations must produce integer results."
        )

    if isinstance(result, complex):
        raise PrecisionError(
            f"Complex number result detected in {calculation_name}: {result}. "
            "All calculations must produce integer results."
        )


def validate_calculation_inputs(*args: Any) -> None:
    """Validate that all calculation inputs are integers (not floats).

    :param args: Input values to validate
    :type args: Any
    :raises PrecisionError: If any input is a float
    """
    for i, arg in enumerate(args):
        if isinstance(arg, float):
            raise PrecisionError(
                f"Floating-point input detected at position {i}: {arg}. "
                "All calculation inputs must be integers."
            )
