"""Custom exceptions for py_mega_calc."""


class InputError(Exception):
    """Raised when input validation fails.
    
    Used for negative numbers, non-integers, or mutually exclusive flags.
    """
    pass


class CalculationTooLargeError(Exception):
    """Raised when a calculation is estimated to be too large.
    
    Used when estimation predicts weeks of processing or exceeds practical limits.
    """
    pass


class PrecisionError(Exception):
    """Raised when floating-point arithmetic is detected.
    
    Used to ensure no floats were used in the pipeline (100% integer arithmetic required).
    """
    pass


class ResourceExhaustedError(Exception):
    """Raised when resource limits are exceeded.
    
    Used when memory usage exceeds 24GB limit.
    """
    pass


class TimeoutError(Exception):
    """Raised when a calculation exceeds the time limit.
    
    Used when calculation exceeds 5 minute (300 second) timeout.
    """
    pass

