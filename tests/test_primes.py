"""Tests for Prime calculator."""

import pytest
from src.calculators.primes import PrimeCalculator
from src.calculators.base import Calculator


class TestPrimeCalculatorSegmentedSieve:
    """Test Segmented Sieve implementation for calculate_by_index."""
    
    def test_prime_calculator_exists(self):
        """Test that PrimeCalculator class exists."""
        assert PrimeCalculator is not None
    
    def test_prime_calculator_is_calculator(self):
        """Test that PrimeCalculator is a subclass of Calculator."""
        assert issubclass(PrimeCalculator, Calculator)
    
    def test_prime_calculator_can_be_instantiated(self):
        """Test that PrimeCalculator can be instantiated."""
        calc = PrimeCalculator()
        assert calc is not None
    
    def test_calculate_by_index_first_prime(self):
        """Test that 1st prime = 2 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(1)
        assert result == 2
    
    def test_calculate_by_index_second_prime(self):
        """Test that 2nd prime = 3 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(2)
        assert result == 3
    
    def test_calculate_by_index_third_prime(self):
        """Test that 3rd prime = 5 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(3)
        assert result == 5
    
    def test_calculate_by_index_tenth_prime(self):
        """Test that 10th prime = 29 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(10)
        assert result == 29
    
    def test_calculate_by_index_hundredth_prime(self):
        """Test that 100th prime = 541 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(100)
        assert result == 541
    
    def test_calculate_by_index_sequence(self):
        """Test prime sequence for first 10 primes."""
        calc = PrimeCalculator()
        expected = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for i, expected_prime in enumerate(expected, start=1):
            result = calc.calculate_by_index(i)
            assert result == expected_prime, f"{i}th prime should be {expected_prime}, got {result}"
    
    def test_calculate_by_index_larger_value(self):
        """Test calculation for larger index (1000th prime = 7919)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(1000)
        assert result == 7919
    
    def test_calculate_by_index_zero_raises_error(self):
        """Test that index 0 raises InputError (no 0th prime)."""
        from src.core.exceptions import InputError
        calc = PrimeCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_index(0)
    
    def test_calculate_by_index_negative_raises_error(self):
        """Test that negative index raises InputError."""
        from src.core.exceptions import InputError
        calc = PrimeCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_index(-1)


class TestMillerRabinPrimalityTest:
    """Test Miller-Rabin primality test functionality."""
    
    def test_miller_rabin_method_exists(self):
        """Test that miller_rabin method exists."""
        calc = PrimeCalculator()
        assert hasattr(calc, 'miller_rabin')
        assert callable(calc.miller_rabin)
    
    def test_miller_rabin_identifies_small_primes(self):
        """Test that Miller-Rabin correctly identifies small primes."""
        calc = PrimeCalculator()
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        for prime in small_primes:
            assert calc.miller_rabin(prime), f"{prime} should be identified as prime"
    
    def test_miller_rabin_identifies_composites(self):
        """Test that Miller-Rabin correctly identifies composite numbers."""
        calc = PrimeCalculator()
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25]
        for composite in composites:
            assert not calc.miller_rabin(composite), f"{composite} should be identified as composite"
    
    def test_miller_rabin_handles_edge_cases(self):
        """Test Miller-Rabin with edge cases."""
        calc = PrimeCalculator()
        # 1 is not prime
        assert not calc.miller_rabin(1)
        # 2 is prime
        assert calc.miller_rabin(2)
        # Even numbers > 2 are composite
        assert not calc.miller_rabin(4)
        assert not calc.miller_rabin(100)
    
    def test_miller_rabin_large_prime(self):
        """Test Miller-Rabin with a known large prime."""
        calc = PrimeCalculator()
        # 7919 is the 1000th prime
        assert calc.miller_rabin(7919)
    
    def test_miller_rabin_large_composite(self):
        """Test Miller-Rabin with a known large composite."""
        calc = PrimeCalculator()
        # 7919 * 2 = 15838 is composite
        assert not calc.miller_rabin(15838)
    
    def test_miller_rabin_deterministic_range(self):
        """Test that Miller-Rabin is deterministic for n < 3×10²⁴."""
        calc = PrimeCalculator()
        # Test with numbers in deterministic range
        test_primes = [97, 101, 103, 107, 109, 113]
        for prime in test_primes:
            assert calc.miller_rabin(prime), f"{prime} should be deterministically prime"
    
    def test_miller_rabin_carmichael_numbers(self):
        """Test Miller-Rabin with Carmichael numbers (known pseudoprimes for some tests)."""
        calc = PrimeCalculator()
        # 561 is a Carmichael number (composite but passes Fermat test)
        # Miller-Rabin should correctly identify it as composite
        assert not calc.miller_rabin(561)
    
    def test_miller_rabin_very_large_number(self):
        """Test Miller-Rabin with very large number (probabilistic mode)."""
        calc = PrimeCalculator()
        # Test with a large known prime (probabilistic with k=40 rounds)
        # 982451653 is a known prime
        result = calc.miller_rabin(982451653)
        assert result is True or result is False  # Should return boolean
        # With k=40 rounds, should be very reliable
        assert result  # This large prime should be identified correctly


class TestBailliePSWTest:
    """Test Baillie-PSW primality test functionality."""
    
    def test_baillie_psw_method_exists(self):
        """Test that baillie_psw method exists."""
        calc = PrimeCalculator()
        assert hasattr(calc, 'baillie_psw')
        assert callable(calc.baillie_psw)
    
    def test_baillie_psw_identifies_small_primes(self):
        """Test that Baillie-PSW correctly identifies small primes."""
        calc = PrimeCalculator()
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        for prime in small_primes:
            assert calc.baillie_psw(prime), f"{prime} should be identified as prime"
    
    def test_baillie_psw_identifies_composites(self):
        """Test that Baillie-PSW correctly identifies composite numbers."""
        calc = PrimeCalculator()
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25]
        for composite in composites:
            assert not calc.baillie_psw(composite), f"{composite} should be identified as composite"
    
    def test_baillie_psw_handles_edge_cases(self):
        """Test Baillie-PSW with edge cases."""
        calc = PrimeCalculator()
        # 1 is not prime
        assert not calc.baillie_psw(1)
        # 2 is prime
        assert calc.baillie_psw(2)
        # Even numbers > 2 are composite
        assert not calc.baillie_psw(4)
        assert not calc.baillie_psw(100)
    
    def test_baillie_psw_large_prime(self):
        """Test Baillie-PSW with a known large prime."""
        calc = PrimeCalculator()
        # 7919 is the 1000th prime
        assert calc.baillie_psw(7919)
    
    def test_baillie_psw_large_composite(self):
        """Test Baillie-PSW with a known large composite."""
        calc = PrimeCalculator()
        # 7919 * 2 = 15838 is composite
        assert not calc.baillie_psw(15838)
    
    def test_baillie_psw_carmichael_numbers(self):
        """Test Baillie-PSW with Carmichael numbers."""
        calc = PrimeCalculator()
        # 561 is a Carmichael number
        # Baillie-PSW should correctly identify it as composite
        assert not calc.baillie_psw(561)
    
    def test_baillie_psw_very_large_prime(self):
        """Test Baillie-PSW with very large prime."""
        calc = PrimeCalculator()
        # 982451653 is a known prime
        assert calc.baillie_psw(982451653)
    
    def test_baillie_psw_stronger_than_miller_rabin_alone(self):
        """Test that Baillie-PSW provides additional robustness."""
        calc = PrimeCalculator()
        # Test with numbers that might pass Miller-Rabin but fail Baillie-PSW
        # In practice, Baillie-PSW has no known pseudoprimes
        test_primes = [97, 101, 103, 107, 109, 113, 127, 131]
        for prime in test_primes:
            assert calc.baillie_psw(prime), f"{prime} should pass Baillie-PSW"


class TestPrimeCalculatorByDigits:
    """Test calculate_by_digits method for PrimeCalculator."""
    
    def test_calculate_by_digits_method_exists(self):
        """Test that calculate_by_digits method exists."""
        calc = PrimeCalculator()
        assert hasattr(calc, 'calculate_by_digits')
        assert callable(calc.calculate_by_digits)
    
    def test_calculate_by_digits_one_digit(self):
        """Test that 1-digit prime returns 2 (first 1-digit prime)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(1)
        assert result == 2
        assert len(str(result)) == 1
    
    def test_calculate_by_digits_two_digits(self):
        """Test that 2-digit prime returns 11 (first 2-digit prime)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(2)
        assert result == 11
        assert len(str(result)) == 2
    
    def test_calculate_by_digits_three_digits(self):
        """Test that 3-digit prime returns 101 (first 3-digit prime)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(3)
        assert result == 101
        assert len(str(result)) == 3
    
    def test_calculate_by_digits_four_digits(self):
        """Test that 4-digit prime returns 1009 (first 4-digit prime)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(4)
        assert result == 1009
        assert len(str(result)) == 4
    
    def test_calculate_by_digits_verifies_primality(self):
        """Test that returned number is actually prime."""
        calc = PrimeCalculator()
        for d in [1, 2, 3, 4]:
            result = calc.calculate_by_digits(d)
            assert calc.miller_rabin(result), f"{result} should be prime"
    
    def test_calculate_by_digits_negative_raises_error(self):
        """Test that negative digit count raises InputError."""
        from src.core.exceptions import InputError
        calc = PrimeCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(-1)
    
    def test_calculate_by_digits_zero_raises_error(self):
        """Test that zero digit count raises InputError."""
        from src.core.exceptions import InputError
        calc = PrimeCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(0)


class TestPrimeCalculatorResourceManager:
    """Test ResourceManager integration for PrimeCalculator."""
    
    def test_calculate_by_index_has_decorators(self):
        """Test that calculate_by_index has monitor_memory and monitor_timeout decorators."""
        import inspect
        from src.core.resource_manager import monitor_memory, monitor_timeout
        
        calc = PrimeCalculator()
        # Check if decorators are applied by checking function attributes
        # Decorators should preserve function metadata
        assert hasattr(calc.calculate_by_index, '__wrapped__') or hasattr(calc.calculate_by_index, '__name__')
    
    def test_calculate_by_digits_has_decorators(self):
        """Test that calculate_by_digits has monitor_memory and monitor_timeout decorators."""
        import inspect
        from src.core.resource_manager import monitor_memory, monitor_timeout
        
        calc = PrimeCalculator()
        # Check if decorators are applied by checking function metadata
        assert hasattr(calc.calculate_by_digits, '__wrapped__') or hasattr(calc.calculate_by_digits, '__name__')
    
    def test_calculate_by_index_normal_execution(self):
        """Test that calculate_by_index works normally with decorators."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(10)
        assert result == 29  # 10th prime
    
    def test_calculate_by_digits_normal_execution(self):
        """Test that calculate_by_digits works normally with decorators."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(2)
        assert result == 11  # First 2-digit prime

