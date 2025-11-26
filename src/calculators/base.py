"""Abstract base class for calculators."""

from abc import ABC, abstractmethod


class Calculator(ABC):
    """Abstract base class defining the calculator interface."""
    
    @abstractmethod
    def calculate_by_index(self, n: int) -> int:
        """Calculate the nth value in the sequence.
        
        Args:
            n: Index in the sequence (0-indexed or 1-indexed as per implementation)
            
        Returns:
            The calculated value
        """
        pass
    
    @abstractmethod
    def calculate_by_digits(self, d: int) -> int:
        """Calculate the first value with at least d digits.
        
        Args:
            d: Minimum number of digits
            
        Returns:
            The calculated value with at least d digits
        """
        pass

