"""Custom exceptions for py_mega_calc.

This module defines all custom exception classes used throughout the application
for error handling and validation.

Dependencies:
    None (pure exception definitions)
"""


class InputError(Exception):
    """Raised when input validation fails.

    Used for negative numbers, non-integers, or mutually exclusive flags.

    :param message: Error message describing the validation failure
    """


class CalculationTooLargeError(Exception):
    """Raised when a calculation is estimated to be too large.

    Used when estimation predicts weeks of processing or exceeds practical limits.

    :param message: Error message describing why the calculation is too large
    """


class PrecisionError(Exception):
    """Raised when floating-point arithmetic is detected.

    Used to ensure no floats were used in the pipeline
    (100% integer arithmetic required).

    :param message: Error message describing the precision violation
    """


class ResourceExhaustedError(Exception):
    """Raised when resource limits are exceeded.

    Used when memory usage exceeds 24GB limit.

    :param message: Error message describing the resource exhaustion
    """


class TimeoutError(Exception):  # pylint: disable=redefined-builtin
    """Raised when a calculation exceeds the time limit.

    Used when calculation exceeds 5 minute (300 second) timeout.

    :param message: Error message describing the timeout
    """
