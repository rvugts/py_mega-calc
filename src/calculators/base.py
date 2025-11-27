"""Abstract base class for calculators.

This module defines the abstract base class that all calculator implementations
must inherit from, providing a consistent interface for calculations.

Dependencies:
    - abc: Abstract base class support
"""

from abc import ABC, abstractmethod


class Calculator(ABC):
    """Abstract base class defining the calculator interface.

    All calculator implementations must provide methods for calculating by index
    and by minimum digit count.
    """

    @abstractmethod
    def calculate_by_index(self, n: int) -> int:
        """Calculate the nth value in the sequence.

        :param n: Index in the sequence (0-indexed or 1-indexed as per
                  implementation)
        :type n: int
        :return: The calculated value
        :rtype: int
        :raises InputError: If n is invalid (e.g., negative)
        """

    @abstractmethod
    def calculate_by_digits(self, d: int) -> int:
        """Calculate the first value with at least d digits.

        :param d: Minimum number of digits
        :type d: int
        :return: The calculated value with at least d digits
        :rtype: int
        :raises InputError: If d is invalid (e.g., less than 1)
        """
