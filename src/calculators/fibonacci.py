"""Fibonacci calculator using Fast Doubling Method.

This module implements a Fibonacci calculator using the Fast Doubling Method,
which provides O(log n) complexity for calculating Fibonacci numbers.

Dependencies:
    - src.calculators.base: Calculator abstract base class
    - src.core.exceptions: InputError exception
    - src.core.resource_manager: Memory and timeout monitoring decorators
    - src.core.precision_checker: Precision validation functions
"""

from src.calculators.base import Calculator
from src.core.exceptions import InputError
from src.core.precision_checker import (
    check_precision,
    validate_calculation_inputs,
)
from src.core.resource_manager import monitor_memory, monitor_timeout


class FibonacciCalculator(Calculator):
    """Fibonacci calculator using Fast Doubling Method.

    Implements O(log n) algorithm for calculating Fibonacci numbers.
    Uses the fast doubling identities:
    - F(2k) = F(k) * (2*F(k+1) - F(k))
    - F(2k+1) = F(k+1)^2 + F(k)^2
    """

    @monitor_memory
    @monitor_timeout
    def calculate_by_index(self, n: int) -> int:
        """Calculate the nth Fibonacci number using Fast Doubling Method.

        :param n: Index in the sequence (0-indexed: F(0)=0, F(1)=1)
        :type n: int
        :return: The nth Fibonacci number
        :rtype: int
        :raises InputError: If n is negative
        :raises PrecisionError: If float is detected in calculation
        """
        validate_calculation_inputs(n)

        if n < 0:
            raise InputError(
                f"Fibonacci index must be non-negative, got {n}"
            )

        if n == 0:
            return 0
        if n == 1:
            return 1

        return self._fast_doubling(n)

    def _fast_doubling(self, n: int) -> int:
        """Compute Fibonacci number using fast doubling method.

        :param n: Index in the sequence (n >= 2)
        :type n: int
        :return: The nth Fibonacci number
        :rtype: int
        """
        k = n.bit_length() - 1
        a, b = 1, 1  # F(1) and F(2)

        for i in range(k - 1, -1, -1):
            c = a * (2 * b - a)  # F(2k)
            d = a * a + b * b    # F(2k+1)

            if (n >> i) & 1:  # If bit is set
                a, b = d, c + d  # F(2k+1), F(2k+2)
            else:
                a, b = c, d  # F(2k), F(2k+1)

        check_precision(a, "Fibonacci calculation")
        return a

    @monitor_memory
    @monitor_timeout
    def calculate_by_digits(self, d: int) -> int:
        """Calculate the first Fibonacci number with at least d digits.

        :param d: Minimum number of digits
        :type d: int
        :return: The first Fibonacci number with at least d digits
        :rtype: int
        :raises InputError: If d is less than 1
        """
        validate_calculation_inputs(d)

        if d < 1:
            raise InputError(f"Digit count must be at least 1, got {d}")

        n = 0
        while True:
            fib_value = self.calculate_by_index(n)
            num_digits = len(str(fib_value))
            if num_digits >= d:
                check_precision(
                    fib_value, "Fibonacci by_digits calculation"
                )
                return fib_value
            n += 1
