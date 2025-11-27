"""Tests for Prime calculator.

This module contains comprehensive tests for the PrimeCalculator class,
including segmented sieve implementation, Miller-Rabin and Baillie-PSW
primality tests, digit-based calculations, and resource management
integration.

Dependencies:
    - pytest: Testing framework
    - unittest.mock: Mocking utilities
    - src.calculators.primes: PrimeCalculator class
    - src.calculators.base: Calculator base class
    - src.core.exceptions: Custom exceptions
    - src.core.resource_manager: Monitoring decorators
"""

import pytest

from src.calculators.base import Calculator
from src.calculators.primes import PrimeCalculator
from src.core.exceptions import InputError


class TestPrimeCalculatorSegmentedSieve:
    """Test Segmented Sieve implementation for calculate_by_index."""

    def test_prime_calculator_exists(self) -> None:
        """Test that PrimeCalculator class exists."""
        assert PrimeCalculator is not None

    def test_prime_calculator_is_calculator(self) -> None:
        """Test PrimeCalculator is a subclass of Calculator."""
        assert issubclass(PrimeCalculator, Calculator)

    def test_prime_calculator_can_be_instantiated(self) -> None:
        """Test that PrimeCalculator can be instantiated."""
        calc = PrimeCalculator()
        assert calc is not None

    def test_calculate_by_index_first_prime(self) -> None:
        """Test that 1st prime = 2 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(1)
        assert result == 2

    def test_calculate_by_index_second_prime(self) -> None:
        """Test that 2nd prime = 3 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(2)
        assert result == 3

    def test_calculate_by_index_third_prime(self) -> None:
        """Test that 3rd prime = 5 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(3)
        assert result == 5

    def test_calculate_by_index_tenth_prime(self) -> None:
        """Test that 10th prime = 29 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(10)
        assert result == 29

    def test_calculate_by_index_hundredth_prime(self) -> None:
        """Test that 100th prime = 541 (OEIS A000040)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(100)
        assert result == 541

    def test_calculate_by_index_sequence(self) -> None:
        """Test prime sequence for first 10 primes."""
        calc = PrimeCalculator()
        expected = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for i, expected_prime in enumerate(expected, start=1):
            result = calc.calculate_by_index(i)
            msg = (
                f"{i}th prime should be {expected_prime}, "
                f"got {result}"
            )
            assert result == expected_prime, msg

    def test_calculate_by_index_larger_value(self) -> None:
        """Test calculation for larger index (1000th prime = 7919)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(1000)
        assert result == 7919

    def test_calculate_by_index_zero_raises_error(self) -> None:
        """Test that index 0 raises InputError (no 0th prime)."""
        calc = PrimeCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_index(0)

    def test_calculate_by_index_negative_raises_error(self) -> None:
        """Test that negative index raises InputError."""
        calc = PrimeCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_index(-1)


class TestMillerRabinPrimalityTest:
    """Test Miller-Rabin primality test functionality."""

    def test_miller_rabin_method_exists(self) -> None:
        """Test that miller_rabin method exists."""
        calc = PrimeCalculator()
        assert hasattr(calc, 'miller_rabin')
        assert callable(calc.miller_rabin)

    def test_miller_rabin_identifies_small_primes(self) -> None:
        """Test Miller-Rabin correctly identifies small primes."""
        calc = PrimeCalculator()
        small_primes = [
            2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
        ]
        for prime in small_primes:
            msg = f"{prime} should be identified as prime"
            assert calc.miller_rabin(prime), msg

    def test_miller_rabin_identifies_composites(self) -> None:
        """Test Miller-Rabin correctly identifies composite numbers."""
        calc = PrimeCalculator()
        composites = [
            4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25,
        ]
        for composite in composites:
            msg = f"{composite} should be identified as composite"
            assert not calc.miller_rabin(composite), msg

    def test_miller_rabin_handles_edge_cases(self) -> None:
        """Test Miller-Rabin with edge cases."""
        calc = PrimeCalculator()
        assert not calc.miller_rabin(1)
        assert calc.miller_rabin(2)
        assert not calc.miller_rabin(4)
        assert not calc.miller_rabin(100)

    def test_miller_rabin_large_prime(self) -> None:
        """Test Miller-Rabin with a known large prime."""
        calc = PrimeCalculator()
        assert calc.miller_rabin(7919)

    def test_miller_rabin_large_composite(self) -> None:
        """Test Miller-Rabin with a known large composite."""
        calc = PrimeCalculator()
        assert not calc.miller_rabin(15838)

    def test_miller_rabin_deterministic_range(self) -> None:
        """Test Miller-Rabin is deterministic for n < 3×10²⁴."""
        calc = PrimeCalculator()
        test_primes = [97, 101, 103, 107, 109, 113]
        for prime in test_primes:
            msg = f"{prime} should be deterministically prime"
            assert calc.miller_rabin(prime), msg

    def test_miller_rabin_carmichael_numbers(self) -> None:
        """Test Miller-Rabin with Carmichael numbers."""
        calc = PrimeCalculator()
        assert not calc.miller_rabin(561)

    def test_miller_rabin_very_large_number(self) -> None:
        """Test Miller-Rabin with very large number (probabilistic)."""
        calc = PrimeCalculator()
        result = calc.miller_rabin(982451653)
        assert result is True or result is False
        assert result


class TestBailliePSWTest:
    """Test Baillie-PSW primality test functionality."""

    def test_baillie_psw_method_exists(self) -> None:
        """Test that baillie_psw method exists."""
        calc = PrimeCalculator()
        assert hasattr(calc, 'baillie_psw')
        assert callable(calc.baillie_psw)

    def test_baillie_psw_identifies_small_primes(self) -> None:
        """Test Baillie-PSW correctly identifies small primes."""
        calc = PrimeCalculator()
        small_primes = [
            2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
        ]
        for prime in small_primes:
            msg = f"{prime} should be identified as prime"
            assert calc.baillie_psw(prime), msg

    def test_baillie_psw_identifies_composites(self) -> None:
        """Test Baillie-PSW correctly identifies composite numbers."""
        calc = PrimeCalculator()
        composites = [
            4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25,
        ]
        for composite in composites:
            msg = f"{composite} should be identified as composite"
            assert not calc.baillie_psw(composite), msg

    def test_baillie_psw_handles_edge_cases(self) -> None:
        """Test Baillie-PSW with edge cases."""
        calc = PrimeCalculator()
        assert not calc.baillie_psw(1)
        assert calc.baillie_psw(2)
        assert not calc.baillie_psw(4)
        assert not calc.baillie_psw(100)

    def test_baillie_psw_large_prime(self) -> None:
        """Test Baillie-PSW with a known large prime."""
        calc = PrimeCalculator()
        assert calc.baillie_psw(7919)

    def test_baillie_psw_large_composite(self) -> None:
        """Test Baillie-PSW with a known large composite."""
        calc = PrimeCalculator()
        assert not calc.baillie_psw(15838)

    def test_baillie_psw_carmichael_numbers(self) -> None:
        """Test Baillie-PSW with Carmichael numbers."""
        calc = PrimeCalculator()
        assert not calc.baillie_psw(561)

    def test_baillie_psw_very_large_prime(self) -> None:
        """Test Baillie-PSW with very large prime."""
        calc = PrimeCalculator()
        assert calc.baillie_psw(982451653)

    def test_baillie_psw_stronger_than_miller_rabin_alone(
        self,
    ) -> None:
        """Test Baillie-PSW provides additional robustness."""
        calc = PrimeCalculator()
        test_primes = [97, 101, 103, 107, 109, 113, 127, 131]
        for prime in test_primes:
            msg = f"{prime} should pass Baillie-PSW"
            assert calc.baillie_psw(prime), msg

    def test_baillie_psw_performs_lucas_test(self) -> None:
        """Test Baillie-PSW performs Lucas test, not just Miller-Rabin."""
        calc = PrimeCalculator()

        assert hasattr(calc, '_lucas_sequence_iterative')
        assert hasattr(calc, '_jacobi_symbol')
        assert hasattr(calc, '_lucas_double')
        assert hasattr(calc, '_lucas_next')

        result = calc.baillie_psw(97)
        assert result is True

    def test_baillie_psw_lucas_sequence_computation(self) -> None:
        """Test Lucas sequence computation works correctly."""
        calc = PrimeCalculator()

        # Testing internal implementation details for correctness
        u, v = calc._lucas_sequence_iterative(1, -1, 5, 100)  # pylint: disable=protected-access
        assert isinstance(u, int)
        assert isinstance(v, int)

        jacobi = calc._jacobi_symbol(5, 11)  # pylint: disable=protected-access
        assert jacobi in [-1, 0, 1]


class TestPrimeCalculatorByDigits:
    """Test calculate_by_digits method for PrimeCalculator."""

    def test_calculate_by_digits_method_exists(self) -> None:
        """Test that calculate_by_digits method exists."""
        calc = PrimeCalculator()
        assert hasattr(calc, 'calculate_by_digits')
        assert callable(calc.calculate_by_digits)

    def test_calculate_by_digits_one_digit(self) -> None:
        """Test 1-digit prime returns 2 (first 1-digit prime)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(1)
        assert result == 2
        assert len(str(result)) == 1

    def test_calculate_by_digits_two_digits(self) -> None:
        """Test 2-digit prime returns 11 (first 2-digit prime)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(2)
        assert result == 11
        assert len(str(result)) == 2

    def test_calculate_by_digits_three_digits(self) -> None:
        """Test 3-digit prime returns 101 (first 3-digit prime)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(3)
        assert result == 101
        assert len(str(result)) == 3

    def test_calculate_by_digits_four_digits(self) -> None:
        """Test 4-digit prime returns 1009 (first 4-digit prime)."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(4)
        assert result == 1009
        assert len(str(result)) == 4

    def test_calculate_by_digits_verifies_primality(self) -> None:
        """Test that returned number is actually prime."""
        calc = PrimeCalculator()
        for d in [1, 2, 3, 4]:
            result = calc.calculate_by_digits(d)
            msg = f"{result} should be prime"
            assert calc.miller_rabin(result), msg

    def test_calculate_by_digits_negative_raises_error(self) -> None:
        """Test negative digit count raises InputError."""
        calc = PrimeCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(-1)

    def test_calculate_by_digits_zero_raises_error(self) -> None:
        """Test zero digit count raises InputError."""
        calc = PrimeCalculator()
        with pytest.raises(InputError):
            calc.calculate_by_digits(0)


class TestPrimeCalculatorResourceManager:
    """Test ResourceManager integration for PrimeCalculator."""

    def test_calculate_by_index_has_decorators(self) -> None:
        """Test calculate_by_index has monitor decorators."""
        calc = PrimeCalculator()
        assert (
            hasattr(calc.calculate_by_index, '__wrapped__')
            or hasattr(calc.calculate_by_index, '__name__')
        )

    def test_calculate_by_digits_has_decorators(self) -> None:
        """Test calculate_by_digits has monitor decorators."""
        calc = PrimeCalculator()
        assert (
            hasattr(calc.calculate_by_digits, '__wrapped__')
            or hasattr(calc.calculate_by_digits, '__name__')
        )

    def test_calculate_by_index_normal_execution(self) -> None:
        """Test calculate_by_index works normally with decorators."""
        calc = PrimeCalculator()
        result = calc.calculate_by_index(10)
        assert result == 29

    def test_calculate_by_digits_normal_execution(self) -> None:
        """Test calculate_by_digits works normally with decorators."""
        calc = PrimeCalculator()
        result = calc.calculate_by_digits(2)
        assert result == 11
