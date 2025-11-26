"""Factorial calculator using Binary Splitting or math.factorial wrapper."""

import math
import time
from typing import List, Dict, Tuple
from .base import Calculator
from src.core.resource_manager import monitor_memory, monitor_timeout


def _custom_factorial_simple(n: int) -> int:
    """Simple iterative factorial implementation for benchmarking.
    
    Args:
        n: Input value
        
    Returns:
        n!
    """
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def benchmark_factorial_methods(input_values: List[int]) -> Dict[str, any]:
    """Benchmark math.factorial vs custom implementation.
    
    Runs timing comparisons between math.factorial (C-optimized) and
    a custom implementation to determine which is faster.
    
    Args:
        input_values: List of input values to benchmark
        
    Returns:
        Dictionary with timing results and recommendation
    """
    math_times = []
    custom_times = []
    
    for n in input_values:
        # Benchmark math.factorial
        start = time.perf_counter()
        math_result = math.factorial(n)
        math_time = time.perf_counter() - start
        math_times.append((n, math_time))
        
        # Benchmark custom implementation
        start = time.perf_counter()
        custom_result = _custom_factorial_simple(n)
        custom_time = time.perf_counter() - start
        custom_times.append((n, custom_time))
        
        # Verify correctness
        if math_result != custom_result:
            raise ValueError(f"Results differ for n={n}: math={math_result}, custom={custom_result}")
    
    # Calculate average times
    avg_math_time = sum(t for _, t in math_times) / len(math_times)
    avg_custom_time = sum(t for _, t in custom_times) / len(custom_times)
    
    # Determine recommendation
    if avg_math_time < avg_custom_time:
        recommended = 'math_factorial'
        speedup = avg_custom_time / avg_math_time if avg_math_time > 0 else float('inf')
    else:
        recommended = 'custom'
        speedup = avg_math_time / avg_custom_time if avg_custom_time > 0 else float('inf')
    
    return {
        'math_factorial': {
            'times': math_times,
            'average_time': avg_math_time
        },
        'custom': {
            'times': custom_times,
            'average_time': avg_custom_time
        },
        'recommended': recommended,
        'speedup': speedup
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
        
        Args:
            n: Input value (must be non-negative integer)
            
        Returns:
            n! (n factorial)
            
        Raises:
            InputError: If n is negative
        """
        if n < 0:
            from src.core.exceptions import InputError
            raise InputError(f"Factorial is not defined for negative numbers, got {n}")
        
        return math.factorial(n)
    
    @monitor_memory
    @monitor_timeout
    def calculate_by_digits(self, d: int) -> int:
        """Calculate the first factorial with at least d digits.
        
        Args:
            d: Minimum number of digits
            
        Returns:
            The first factorial with at least d digits
            
        Raises:
            InputError: If d is less than 1
        """
        from src.core.exceptions import InputError
        
        if d < 1:
            raise InputError(f"Digit count must be at least 1, got {d}")
        
        # Start from 0! and iterate until we find one with at least d digits
        n = 0
        while True:
            fact_value = self.calculate_by_index(n)
            num_digits = len(str(fact_value))
            if num_digits >= d:
                return fact_value
            n += 1

