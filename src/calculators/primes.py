"""Prime calculator with two modes: by index and by minimum digits.

This module implements prime number calculations using the Segmented Sieve
of Eratosthenes for finding primes by index, and Miller-Rabin/Baillie-PSW
primality tests for finding primes by minimum digit count.

Dependencies:
    - math: Mathematical functions
    - random: Random number generation for probabilistic tests
    - src.calculators.base: Calculator abstract base class
    - src.core.exceptions: InputError exception
    - src.core.resource_manager: Memory and timeout monitoring decorators
    - src.core.precision_checker: Precision validation functions
"""

import math
import random
from typing import Optional, Tuple

from src.calculators.base import Calculator
from src.core.exceptions import InputError
from src.core.precision_checker import (
    check_precision,
    validate_calculation_inputs,
)
from src.core.resource_manager import monitor_memory, monitor_timeout

# Constants for Miller-Rabin deterministic bases
DETERMINISTIC_LIMIT: int = 3 * 10 ** 24
MILLER_RABIN_DEFAULT_ROUNDS: int = 40
BAILLIE_PSW_FALLBACK_ROUNDS: int = 10
SEGMENTED_SIEVE_THRESHOLD: int = 100000
JACOBI_SEARCH_LIMIT: int = 20


class PrimeCalculator(Calculator):
    """Prime calculator using Segmented Sieve and probabilistic tests."""

    @monitor_memory
    @monitor_timeout
    def calculate_by_index(self, n: int) -> int:
        """Calculate the nth prime using Segmented Sieve of Eratosthenes.

        :param n: Index of the prime (1-indexed: 1st prime = 2, 2nd = 3)
        :type n: int
        :return: The nth prime number
        :rtype: int
        :raises InputError: If n is less than 1
        """
        validate_calculation_inputs(n)

        if n < 1:
            raise InputError(f"Prime index must be at least 1, got {n}")

        if n == 1:
            result = 2
            check_precision(result, "Prime by_index calculation")
            return result

        upper_bound = self._estimate_upper_bound(n)
        primes = self._segmented_sieve(upper_bound)

        while len(primes) < n:
            upper_bound = int(upper_bound * 1.5) + 100
            primes = self._segmented_sieve(upper_bound)

        result = primes[n - 1]
        check_precision(result, "Prime by_index calculation")
        return result

    def _estimate_upper_bound(self, n: int) -> int:
        """Estimate upper bound for nth prime using prime number theorem.

        :param n: Prime index
        :type n: int
        :return: Estimated upper bound
        :rtype: int
        """
        if n <= 6:
            return 20

        ln_n = math.log(n)
        return int(n * ln_n + n * math.log(ln_n) + n * 1.5) + 100

    def _segmented_sieve(self, limit: int) -> list[int]:
        """Segmented Sieve of Eratosthenes to find all primes up to limit.

        :param limit: Upper bound for prime search
        :type limit: int
        :return: List of all primes up to limit
        :rtype: list[int]
        """
        if limit < 2:
            return []

        if limit < SEGMENTED_SIEVE_THRESHOLD:
            return self._simple_sieve(limit)

        return self._compute_segmented_sieve(limit)

    def _compute_segmented_sieve(self, limit: int) -> list[int]:
        """Compute segmented sieve for large limits.

        :param limit: Upper bound for prime search
        :type limit: int
        :return: List of all primes up to limit
        :rtype: list[int]
        """
        sqrt_limit = int(math.isqrt(limit)) + 1
        base_primes = self._simple_sieve(sqrt_limit)
        primes = base_primes.copy()
        segment_size = sqrt_limit

        for low in range(sqrt_limit, limit + 1, segment_size):
            high = min(low + segment_size - 1, limit)
            segment = [True] * (high - low + 1)

            for prime in base_primes:
                start = max(
                    prime * prime,
                    ((low + prime - 1) // prime) * prime,
                )
                if start > high:
                    continue
                for j in range(start, high + 1, prime):
                    segment[j - low] = False

            for i in range(low, high + 1):
                if i > 1 and segment[i - low]:
                    primes.append(i)

        return primes

    def _simple_sieve(self, limit: int) -> list[int]:
        """Simple Sieve of Eratosthenes for small limits.

        :param limit: Upper bound for prime search
        :type limit: int
        :return: List of all primes up to limit
        :rtype: list[int]
        """
        if limit < 2:
            return []

        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False

        sqrt_limit = int(math.isqrt(limit)) + 1
        for i in range(2, sqrt_limit):
            if sieve[i]:
                for j in range(i * i, limit + 1, i):
                    sieve[j] = False

        return [i for i in range(2, limit + 1) if sieve[i]]

    def miller_rabin(self, n: int, k: int = MILLER_RABIN_DEFAULT_ROUNDS) -> bool:
        """Miller-Rabin primality test.

        Deterministic for n < 3×10²⁴, probabilistic with k rounds for
        larger n.

        :param n: Number to test for primality
        :type n: int
        :param k: Number of rounds for probabilistic testing (default 40)
        :type k: int
        :return: True if n is probably prime, False if n is composite
        :rtype: bool
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False

        if n < DETERMINISTIC_LIMIT:
            return self._miller_rabin_deterministic(n)
        return self._miller_rabin_probabilistic(n, k)

    def _miller_rabin_deterministic(self, n: int) -> bool:
        """Miller-Rabin test with deterministic bases.

        :param n: Number to test (n < 3×10²⁴)
        :type n: int
        :return: True if n is prime, False if composite
        :rtype: bool
        """
        bases = self._get_deterministic_bases(n)

        for a in bases:
            if a >= n:
                continue
            if not self._miller_rabin_witness(n, a):
                return False
        return True

    def _get_deterministic_bases(  # pylint: disable=too-many-return-statements
        self, n: int
    ) -> list[int]:
        """Get deterministic bases for Miller-Rabin test.

        :param n: Number being tested
        :type n: int
        :return: List of bases to use
        :rtype: list[int]
        """
        if n < 2047:
            return [2]
        if n < 1373653:
            return [2, 3]
        if n < 9080191:
            return [31, 73]
        if n < 25326001:
            return [2, 3, 5]
        if n < 3215031751:
            return [2, 3, 5, 7]
        if n < 4759123141:
            return [2, 7, 61]
        if n < 1122004669633:
            return [2, 13, 23, 1662803]
        if n < 2152302898747:
            return [2, 3, 5, 7, 11]
        if n < 3474749660383:
            return [2, 3, 5, 7, 11, 13]
        if n < 341550071728321:
            return [2, 3, 5, 7, 11, 13, 17]

        return [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

    def _miller_rabin_probabilistic(self, n: int, k: int) -> bool:
        """Miller-Rabin test with probabilistic mode.

        :param n: Number to test
        :type n: int
        :param k: Number of rounds
        :type k: int
        :return: True if probably prime, False if composite
        :rtype: bool
        """
        for _ in range(k):
            a = random.randint(2, n - 2)
            if not self._miller_rabin_witness(n, a):
                return False
        return True

    def _miller_rabin_witness(self, n: int, a: int) -> bool:
        """Check if a is a witness for n being composite.

        :param n: Number being tested (must be odd and > 2)
        :type n: int
        :param a: Base to test
        :type a: int
        :return: True if a suggests n might be prime, False if composite
        :rtype: bool
        """
        d, r = self._decompose_n_minus_one(n)

        x = pow(a, d, n)

        if x in (1, n - 1):
            return True

        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return True

        return False

    def _decompose_n_minus_one(self, n: int) -> Tuple[int, int]:
        """Write n-1 as d * 2^r where d is odd.

        :param n: Number to decompose
        :type n: int
        :return: Tuple (d, r) where d is odd and r is the exponent
        :rtype: Tuple[int, int]
        """
        d = n - 1
        r = 0
        while d % 2 == 0:
            d //= 2
            r += 1
        return (d, r)

    def baillie_psw(self, n: int) -> bool:  # pylint: disable=too-many-return-statements
        """Baillie-PSW primality test.

        Combines base-2 strong probable prime test (Miller-Rabin with base 2)
        and strong Lucas probable prime test. No known pseudoprimes.

        :param n: Number to test for primality
        :type n: int
        :return: True if n is probably prime, False if n is composite
        :rtype: bool
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False

        if not self._miller_rabin_witness(n, 2):
            return False

        d = self._find_lucas_d(n)
        if d is None:
            return self.miller_rabin(n, k=BAILLIE_PSW_FALLBACK_ROUNDS)

        p, q = self._compute_lucas_params(d)
        if q is None:
            return self.miller_rabin(n, k=BAILLIE_PSW_FALLBACK_ROUNDS)

        return self._strong_lucas_test(n, p, q)

    def _find_lucas_d(self, n: int) -> Optional[int]:
        """Find D for Lucas test with Jacobi symbol -1.

        :param n: Number being tested
        :type n: int
        :return: D value if found, None otherwise
        :rtype: Optional[int]
        """
        d = 5
        sign = 1
        for _ in range(JACOBI_SEARCH_LIMIT):
            test_d = sign * d
            jacobi = self._jacobi_symbol(test_d, n)
            if jacobi == -1:
                return test_d
            sign = -sign
            if sign == 1:
                d += 2
        return None

    def _compute_lucas_params(self, d: int) -> Tuple[int, Optional[int]]:
        """Compute P and Q parameters for Lucas test.

        :param d: D value from Jacobi symbol search
        :type d: int
        :return: Tuple (P, Q) where Q is None if computation fails
        :rtype: Tuple[int, Optional[int]]
        """
        p = 1
        if (1 - d) % 4 != 0:
            return (p, None)

        if d < 0:
            q = (1 - d) // 4
        else:
            q = (1 - d) // 4

        return (p, q)

    def _strong_lucas_test(self, n: int, p: int, q: int) -> bool:
        """Perform strong Lucas probable prime test.

        :param n: Number being tested
        :type n: int
        :param p: Lucas sequence parameter P
        :type p: int
        :param q: Lucas sequence parameter Q
        :type q: int
        :return: True if n passes strong Lucas test
        :rtype: bool
        """
        d_val, s = self._decompose_n_plus_one(n)

        u, v = self._lucas_sequence_iterative(p, q, d_val, n)

        if u == 0 or v == 0:
            return True

        q_power = pow(q, d_val, n)
        for _ in range(1, s):
            u, v, q_power = self._lucas_double_with_q(
                u, v, p, q, q_power, n
            )
            if v == 0:
                return True

        return False

    def _decompose_n_plus_one(self, n: int) -> Tuple[int, int]:
        """Write n+1 as d' * 2^s where d' is odd.

        :param n: Number to decompose
        :type n: int
        :return: Tuple (d', s) where d' is odd and s is the exponent
        :rtype: Tuple[int, int]
        """
        d_val = n + 1
        s = 0
        while d_val % 2 == 0:
            d_val //= 2
            s += 1
        return (d_val, s)

    def _jacobi_symbol(self, a: int, n: int) -> int:
        """Compute Jacobi symbol (a/n).

        :param a: Numerator
        :type a: int
        :param n: Denominator (must be odd and > 0)
        :type n: int
        :return: Jacobi symbol: -1, 0, or 1
        :rtype: int
        """
        if n <= 0 or n % 2 == 0:
            return 0

        a = a % n
        if a == 0:
            return 0

        result = 1
        while a != 0:
            a, result = self._jacobi_remove_twos(a, n, result)
            a, n = n, a
            if a % 4 == 3 and n % 4 == 3:
                result = -result
            a = a % n

        return result if n == 1 else 0

    def _jacobi_remove_twos(
        self, a: int, n: int, result: int
    ) -> Tuple[int, int]:
        """Remove factors of 2 from a in Jacobi symbol computation.

        :param a: Current value
        :type a: int
        :param n: Modulus
        :type n: int
        :param result: Current result
        :type result: int
        :return: Tuple (a after removing twos, updated result)
        :rtype: Tuple[int, int]
        """
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        return (a, result)

    def _lucas_sequence_iterative(
        self, p: int, q: int, k: int, n: int
    ) -> Tuple[int, int]:
        """Compute Lucas sequence U_k and V_k modulo n.

        More reliable for small values, uses binary method for efficiency.
        Tracks Q^k properly to ensure correct doubling.

        :param p: Lucas sequence parameter P
        :type p: int
        :param q: Lucas sequence parameter Q
        :type q: int
        :param k: Index
        :type k: int
        :param n: Modulus
        :type n: int
        :return: Tuple (U_k mod n, V_k mod n)
        :rtype: Tuple[int, int]
        """
        if k == 0:
            return (0, 2 % n)
        if k == 1:
            return (1 % n, p % n)

        u, v = 1 % n, p % n
        q_power = q % n
        k_bits = bin(k)[3:]

        for bit in k_bits:
            u, v, q_power = self._lucas_double_with_q(
                u, v, p, q, q_power, n
            )

            if bit == '1':
                u, v = self._lucas_next(u, v, p, q, n)
                q_power = (q_power * q) % n

        return (u, v)

    def _lucas_double_with_q(
        self, u: int, v: int, _p: int, _q: int, q_power: int, n: int
    ) -> Tuple[int, int, int]:
        """Double the index with Q^k tracking.

        :param u: Current U_k value
        :type u: int
        :param v: Current V_k value
        :type v: int
        :param _p: Lucas sequence parameter P (unused)
        :type _p: int
        :param _q: Lucas sequence parameter Q (unused)
        :type _q: int
        :param q_power: Current Q^k mod n
        :type q_power: int
        :param n: Modulus
        :type n: int
        :return: Tuple (U_{2k} mod n, V_{2k} mod n, Q^{2k} mod n)
        :rtype: Tuple[int, int, int]
        """
        u2 = (u * v) % n
        v2 = (v * v - 2 * q_power) % n
        q_power_2 = (q_power * q_power) % n
        return (u2, v2, q_power_2)

    def _lucas_sequence(
        self, p: int, q: int, k: int, n: int
    ) -> Tuple[int, int]:
        """Compute Lucas sequence U_k and V_k modulo n using binary method.

        :param p: Lucas sequence parameter P
        :type p: int
        :param q: Lucas sequence parameter Q
        :type q: int
        :param k: Index
        :type k: int
        :param n: Modulus
        :type n: int
        :return: Tuple (U_k mod n, V_k mod n)
        :rtype: Tuple[int, int]
        """
        if k == 0:
            return (0, 2 % n)
        if k == 1:
            return (1, p % n)

        u, v = 1, p % n
        k_bits = bin(k)[3:]

        for bit in k_bits:
            u, v = self._lucas_double(u, v, p, q, n)
            if bit == '1':
                u, v = self._lucas_next(u, v, p, q, n)

        return (u, v)

    def _lucas_double(
        self, u: int, v: int, _p: int, q: int, n: int
    ) -> Tuple[int, int]:
        """Double the index: compute U_{2k} and V_{2k} from U_k and V_k.

        Uses doubling formulas: U_{2k} = U_k * V_k, V_{2k} = V_k^2 - 2*Q.
        Note: This is a simplified version. The full implementation uses
        _lucas_double_with_q which properly tracks Q^k.

        :param u: Current U_k value
        :type u: int
        :param v: Current V_k value
        :type v: int
        :param _p: Lucas sequence parameter P (unused)
        :type _p: int
        :param q: Lucas sequence parameter Q
        :type q: int
        :param n: Modulus
        :type n: int
        :return: Tuple (U_{2k} mod n, V_{2k} mod n)
        :rtype: Tuple[int, int]
        """
        u2 = (u * v) % n
        v2 = (v * v - 2 * q) % n
        return (u2, v2)

    def _lucas_next(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, u: int, v: int, p: int, q: int, n: int
    ) -> Tuple[int, int]:
        """Advance by one: compute U_{k+1} and V_{k+1} from U_k and V_k.

        :param u: Current U_k value
        :type u: int
        :param v: Current V_k value
        :type v: int
        :param p: Lucas sequence parameter P
        :type p: int
        :param q: Lucas sequence parameter Q
        :type q: int
        :param n: Modulus
        :type n: int
        :return: Tuple (U_{k+1} mod n, V_{k+1} mod n)
        :rtype: Tuple[int, int]
        """
        inv_2 = (n + 1) // 2 if n % 2 == 1 else None

        if inv_2 is not None:
            u_next = ((p * u + v) * inv_2) % n
            delta = (p * p - 4 * q) % n
            v_next = ((p * v + u * delta) * inv_2) % n
        else:
            u_next = ((p * u + v) // 2) % n
            delta = (p * p - 4 * q) % n
            v_next = ((p * v + u * delta) // 2) % n

        return (u_next, v_next)

    @monitor_memory
    @monitor_timeout
    def calculate_by_digits(self, d: int) -> int:
        """Calculate the first prime with at least d digits.

        Starts search at 10^(d-1) and uses Miller-Rabin for primality
        testing.

        :param d: Minimum number of digits
        :type d: int
        :return: The first prime with at least d digits
        :rtype: int
        :raises InputError: If d is not a positive integer
        """
        validate_calculation_inputs(d)

        if not isinstance(d, int) or d <= 0:
            raise InputError(
                "Input 'd' (minimum digits) must be a positive integer."
            )

        if d == 1:
            result = 2
            check_precision(result, "Prime by_digits calculation")
            return result

        candidate = self._get_starting_candidate(d)

        while True:
            if len(str(candidate)) < d:
                candidate += 2
                continue

            if self.miller_rabin(candidate):
                check_precision(
                    candidate, "Prime by_digits calculation"
                )
                return candidate

            candidate += 2

    def _get_starting_candidate(self, d: int) -> int:
        """Get starting candidate for prime search.

        :param d: Minimum number of digits
        :type d: int
        :return: Starting candidate (odd number >= 10^(d-1))
        :rtype: int
        """
        start = 10 ** (d - 1)

        if start == 1:
            return 2

        return start + 1 if start % 2 == 0 else start
