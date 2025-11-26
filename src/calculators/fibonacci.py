"""Fibonacci calculator using Fast Doubling Method."""

from .base import Calculator
from src.core.exceptions import InputError
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
        
        Args:
            n: Index in the sequence (0-indexed: F(0)=0, F(1)=1)
            
        Returns:
            The nth Fibonacci number
            
        Raises:
            InputError: If n is negative
        """
        if n < 0:
            raise InputError(f"Fibonacci index must be non-negative, got {n}")
        
        if n == 0:
            return 0
        if n == 1:
            return 1
        
        # Fast Doubling Method
        # Find the highest bit position
        k = n.bit_length() - 1
        
        # Start with F(1) and F(2)
        a, b = 1, 1  # F(1) and F(2)
        
        # Process bits from highest to lowest
        for i in range(k - 1, -1, -1):
            # Calculate F(2k) and F(2k+1) from F(k) and F(k+1)
            c = a * (2 * b - a)  # F(2k)
            d = a * a + b * b    # F(2k+1)
            
            if (n >> i) & 1:  # If bit is set
                a, b = d, c + d  # F(2k+1), F(2k+2)
            else:
                a, b = c, d  # F(2k), F(2k+1)
        
        return a
    
    @monitor_memory
    @monitor_timeout
    def calculate_by_digits(self, d: int) -> int:
        """Calculate the first Fibonacci number with at least d digits.
        
        Args:
            d: Minimum number of digits
            
        Returns:
            The first Fibonacci number with at least d digits
            
        Raises:
            InputError: If d is less than 1
        """
        if d < 1:
            raise InputError(f"Digit count must be at least 1, got {d}")
        
        # Start from F(0) and iterate until we find one with at least d digits
        n = 0
        while True:
            fib_value = self.calculate_by_index(n)
            num_digits = len(str(fib_value))
            if num_digits >= d:
                return fib_value
            n += 1

