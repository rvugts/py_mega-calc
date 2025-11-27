"""Factorial calculator using Binary Splitting or math.factorial wrapper.

This module provides factorial calculation using Python's optimized math.factorial
and includes binary splitting implementation for benchmarking purposes.

Dependencies:
    - math: Standard library for factorial calculation
    - time: Standard library for benchmarking
    - typing: Type hints
    - src.calculators.base: Calculator abstract base class
    - src.core.resource_manager: Memory and timeout monitoring decorators
    - src.core.precision_checker: Precision validation functions
"""

import math
import time
from typing import Any, Dict, List, Tuple

from src.calculators.base import Calculator
from src.core.exceptions import InputError
from src.core.precision_checker import (
    check_precision,
    validate_calculation_inputs,
)
from src.core.resource_manager import monitor_memory, monitor_timeout


def _product_range(a: int, b: int) -> int:
    """Compute product of integers from a to b using binary splitting.

    :param a: Start value (inclusive)
    :type a: int
    :param b: End value (inclusive)
    :type b: int
    :return: Product of all integers from a to b
    :rtype: int
    """
    if a > b:
        return 1
    if a == b:
        return a
    if b - a == 1:
        return a * b

    mid = (a + b) // 2
    return _product_range(a, mid) * _product_range(mid + 1, b)


def _binary_splitting_factorial(n: int) -> int:
    """Binary splitting factorial implementation for benchmarking.

    Uses recursive binary splitting to compute n! with O(n (log n)^2)
    complexity. More efficient than simple iteration for large numbers.

    :param n: Input value
    :type n: int
    :return: n!
    :rtype: int
    :raises ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n in (0, 1):
        return 1

    return _product_range(1, n)


def _custom_factorial_simple(n: int) -> int:
    """Simple iterative factorial implementation for benchmarking.

    :param n: Input value
    :type n: int
    :return: n!
    :rtype: int
    :raises ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n in (0, 1):
        return 1

    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def _benchmark_single_value(
    n: int, math_func: Any, custom_func: Any
) -> Tuple[Tuple[int, float], Tuple[int, float]]:
    """Benchmark a single input value for both methods.

    :param n: Input value to benchmark
    :type n: int
    :param math_func: math.factorial function
    :type math_func: Any
    :param custom_func: Custom factorial function
    :type custom_func: Any
    :return: Tuple of (math_time, custom_time) tuples
    :rtype: Tuple[Tuple[int, float], Tuple[int, float]]
    :raises ValueError: If results differ between methods
    """
    start = time.perf_counter()
    math_result = math_func(n)
    math_time = time.perf_counter() - start

    start = time.perf_counter()
    custom_result = custom_func(n)
    custom_time = time.perf_counter() - start

    if math_result != custom_result:
        raise ValueError(
            f"Results differ for n={n}: "
            f"math={math_result}, custom={custom_result}"
        )

    return ((n, math_time), (n, custom_time))


def _calculate_averages(
    math_times: List[Tuple[int, float]],
    custom_times: List[Tuple[int, float]],
) -> Tuple[float, float]:
    """Calculate average execution times for both methods.

    :param math_times: List of (input, time) tuples for math.factorial
    :type math_times: List[Tuple[int, float]]
    :param custom_times: List of (input, time) tuples for custom method
    :type custom_times: List[Tuple[int, float]]
    :return: Tuple of (avg_math_time, avg_custom_time)
    :rtype: Tuple[float, float]
    """
    avg_math = sum(t for _, t in math_times) / len(math_times)
    avg_custom = sum(t for _, t in custom_times) / len(custom_times)
    return (avg_math, avg_custom)


def _determine_recommendation(
    avg_math_time: float, avg_custom_time: float
) -> Tuple[str, float]:
    """Determine which method is faster and calculate speedup.

    :param avg_math_time: Average time for math.factorial
    :type avg_math_time: float
    :param avg_custom_time: Average time for custom method
    :type avg_custom_time: float
    :return: Tuple of (recommended_method, speedup_factor)
    :rtype: Tuple[str, float]
    """
    if avg_math_time < avg_custom_time:
        recommended = 'math_factorial'
        speedup = (
            avg_custom_time / avg_math_time
            if avg_math_time > 0
            else float('inf')
        )
    else:
        recommended = 'custom'
        speedup = (
            avg_math_time / avg_custom_time
            if avg_custom_time > 0
            else float('inf')
        )
    return (recommended, speedup)


def benchmark_factorial_methods(
    input_values: List[int],
) -> Dict[str, Any]:
    """Benchmark math.factorial vs custom implementation.

    Runs timing comparisons between math.factorial (C-optimized) and
    a custom implementation to determine which is faster.

    :param input_values: List of input values to benchmark
    :type input_values: List[int]
    :return: Dictionary with timing results and recommendation
    :rtype: Dict[str, Any]
    """
    math_times: List[Tuple[int, float]] = []
    custom_times: List[Tuple[int, float]] = []

    for n in input_values:
        math_time, custom_time = _benchmark_single_value(
            n, math.factorial, _binary_splitting_factorial
        )
        math_times.append(math_time)
        custom_times.append(custom_time)

    avg_math, avg_custom = _calculate_averages(math_times, custom_times)
    recommended, speedup = _determine_recommendation(avg_math, avg_custom)

    return {
        'math_factorial': {
            'times': math_times,
            'average_time': avg_math,
        },
        'custom': {
            'times': custom_times,
            'average_time': avg_custom,
        },
        'recommended': recommended,
        'speedup': speedup,
    }


class FactorialCalculator(Calculator):
    """Factorial calculator using math.factorial (C-optimized).

    Uses Python's built-in math.factorial which is C-optimized in CPython
    and provides excellent performance for large factorials.
    """

    @monitor_memory
    @monitor_timeout
    def calculate_by_index(self, n: int) -> int:
        """Calculate n! (n factorial) using math.factorial.

        :param n: Input value (must be non-negative integer)
        :type n: int
        :return: n! (n factorial)
        :rtype: int
        :raises InputError: If n is negative
        """
        validate_calculation_inputs(n)

        if n < 0:
            raise InputError(
                f"Factorial is not defined for negative numbers, got {n}"
            )

        result = math.factorial(n)
        check_precision(result, "Factorial calculation")
        return result

    @monitor_memory
    @monitor_timeout
    def calculate_by_digits(self, d: int) -> int:
        """Calculate the first factorial with at least d digits.

        :param d: Minimum number of digits
        :type d: int
        :return: The first factorial with at least d digits
        :rtype: int
        :raises InputError: If d is less than 1
        """
        validate_calculation_inputs(d)

        if d < 1:
            raise InputError(f"Digit count must be at least 1, got {d}")

        n = 0
        while True:
            fact_value = self.calculate_by_index(n)
            num_digits = len(str(fact_value))
            if num_digits >= d:
                check_precision(
                    fact_value, "Factorial by_digits calculation"
                )
                return fact_value
            n += 1
