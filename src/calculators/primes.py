"""Prime calculator with two modes: by index and by minimum digits."""

import math
import random
from .base import Calculator
from src.core.exceptions import InputError
from src.core.resource_manager import monitor_memory, monitor_timeout


class PrimeCalculator(Calculator):
    """Prime calculator using Segmented Sieve and probabilistic primality tests."""
    
    @monitor_memory
    @monitor_timeout
    def calculate_by_index(self, n: int) -> int:
        """Calculate the nth prime using Segmented Sieve of Eratosthenes.
        
        Args:
            n: Index of the prime (1-indexed: 1st prime = 2, 2nd = 3, etc.)
            
        Returns:
            The nth prime number
            
        Raises:
            InputError: If n is less than 1
        """
        if n < 1:
            raise InputError(f"Prime index must be at least 1, got {n}")
        
        if n == 1:
            return 2
        
        # Estimate upper bound for nth prime using prime number theorem
        # p_n ≈ n * ln(n) + n * ln(ln(n))
        # Add safety margin
        if n <= 6:
            upper_bound = 20
        else:
            ln_n = math.log(n)
            upper_bound = int(n * ln_n + n * math.log(ln_n) + n * 1.5) + 100
        
        # Use segmented sieve to find primes
        primes = self._segmented_sieve(upper_bound)
        
        # If we don't have enough primes, extend the search
        while len(primes) < n:
            upper_bound = int(upper_bound * 1.5) + 100
            primes = self._segmented_sieve(upper_bound)
        
        return primes[n - 1]
    
    def _segmented_sieve(self, limit: int) -> list[int]:
        """Segmented Sieve of Eratosthenes to find all primes up to limit.
        
        Args:
            limit: Upper bound for prime search
            
        Returns:
            List of all primes up to limit
        """
        if limit < 2:
            return []
        
        # Simple sieve for small limits (more efficient)
        if limit < 100000:
            return self._simple_sieve(limit)
        
        # Segmented sieve for larger limits
        sqrt_limit = int(math.isqrt(limit)) + 1
        base_primes = self._simple_sieve(sqrt_limit)
        
        primes = base_primes.copy()
        segment_size = sqrt_limit
        
        for low in range(sqrt_limit, limit + 1, segment_size):
            high = min(low + segment_size - 1, limit)
            segment = [True] * (high - low + 1)
            
            for prime in base_primes:
                # Find the first multiple of prime >= low
                start = max(prime * prime, ((low + prime - 1) // prime) * prime)
                if start > high:
                    continue
                # Mark multiples as composite
                for j in range(start, high + 1, prime):
                    segment[j - low] = False
            
            # Collect primes from this segment
            for i in range(low, high + 1):
                if i > 1 and segment[i - low]:
                    primes.append(i)
        
        return primes
    
    def _simple_sieve(self, limit: int) -> list[int]:
        """Simple Sieve of Eratosthenes for small limits.
        
        Args:
            limit: Upper bound for prime search
            
        Returns:
            List of all primes up to limit
        """
        if limit < 2:
            return []
        
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        
        for i in range(2, int(math.isqrt(limit)) + 1):
            if sieve[i]:
                for j in range(i * i, limit + 1, i):
                    sieve[j] = False
        
        return [i for i in range(2, limit + 1) if sieve[i]]
    
    def miller_rabin(self, n: int, k: int = 40) -> bool:
        """Miller-Rabin primality test.
        
        Deterministic for n < 3×10²⁴, probabilistic with k rounds for larger n.
        
        Args:
            n: Number to test for primality
            k: Number of rounds for probabilistic testing (default 40)
            
        Returns:
            True if n is probably prime, False if n is composite
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # Deterministic bases for n < 3×10²⁴
        DETERMINISTIC_LIMIT = 3 * 10**24
        if n < DETERMINISTIC_LIMIT:
            # Use deterministic bases
            if n < 2047:
                bases = [2]
            elif n < 1373653:
                bases = [2, 3]
            elif n < 9080191:
                bases = [31, 73]
            elif n < 25326001:
                bases = [2, 3, 5]
            elif n < 3215031751:
                bases = [2, 3, 5, 7]
            elif n < 4759123141:
                bases = [2, 7, 61]
            elif n < 1122004669633:
                bases = [2, 13, 23, 1662803]
            elif n < 2152302898747:
                bases = [2, 3, 5, 7, 11]
            elif n < 3474749660383:
                bases = [2, 3, 5, 7, 11, 13]
            elif n < 341550071728321:
                bases = [2, 3, 5, 7, 11, 13, 17]
            else:
                # For very large numbers in deterministic range, use more bases
                bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
            
            for a in bases:
                if a >= n:
                    continue
                if not self._miller_rabin_witness(n, a):
                    return False
            return True
        else:
            # Probabilistic mode with k rounds
            for _ in range(k):
                a = random.randint(2, n - 2)
                if not self._miller_rabin_witness(n, a):
                    return False
            return True
    
    def _miller_rabin_witness(self, n: int, a: int) -> bool:
        """Check if a is a witness for n being composite.
        
        Args:
            n: Number being tested (must be odd and > 2)
            a: Base to test
            
        Returns:
            True if a suggests n might be prime, False if n is definitely composite
        """
        # Write n-1 as d * 2^r where d is odd
        d = n - 1
        r = 0
        while d % 2 == 0:
            d //= 2
            r += 1
        
        # Compute a^d mod n
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            return True
        
        # Check a^(d*2^i) mod n for i = 1 to r-1
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return True
        
        return False
    
    def baillie_psw(self, n: int) -> bool:
        """Baillie-PSW primality test.
        
        Combines base-2 strong probable prime test (Miller-Rabin with base 2)
        and strong Lucas probable prime test. No known pseudoprimes.
        
        NOTE: Current implementation has known issues with Lucas sequence
        computation for some primes. Falls back to Miller-Rabin for reliability.
        This is a known limitation to be refined in future iterations.
        
        Args:
            n: Number to test for primality
            
        Returns:
            True if n is probably prime, False if n is composite
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # Step 1: Base-2 strong probable prime test (Miller-Rabin with base 2)
        if not self._miller_rabin_witness(n, 2):
            return False
        
        # For now, use Miller-Rabin as the primary test since Lucas test has issues
        # TODO: Fix Lucas sequence computation for full Baillie-PSW implementation
        return self.miller_rabin(n, k=10)  # Use Miller-Rabin with 10 rounds for reliability
        
        # Step 2: Find D for Lucas test
        # Find first D in sequence 5, -7, 9, -11, 13, -15, ... where (D/n) = -1
        d = 5
        sign = 1
        for _ in range(20):  # Limit search
            test_d = sign * d
            jacobi = self._jacobi_symbol(test_d, n)
            if jacobi == -1:
                d = test_d
                break
            sign = -sign
            if sign == 1:
                d += 2
        
        # Step 3: Strong Lucas probable prime test
        # For Baillie-PSW, we use P=1 and Q=(1-D)/4
        # Handle negative D correctly
        p = 1
        if d < 0:
            q = (1 - d) // 4  # This will be positive
        else:
            q = (1 - d) // 4
        
        # Write n+1 as d' * 2^s where d' is odd
        d_val = n + 1
        s = 0
        while d_val % 2 == 0:
            d_val //= 2
            s += 1
        
        # Compute Lucas sequence U_d' and V_d' using iterative method for accuracy
        u, v = self._lucas_sequence_iterative(p, q, d_val, n)
        
        # Check conditions for strong Lucas probable prime
        # n is a strong Lucas probable prime if:
        # 1. U_d' ≡ 0 (mod n), OR
        # 2. V_{d'*2^i} ≡ 0 (mod n) for some i in [0, s-1)
        if u == 0:
            return True
        
        # Check V_{d'*2^i} for i = 0 to s-1
        # We already have V_d' in v, check it first
        if v == 0:
            return True
        
        # Now compute V_{d'*2}, V_{d'*4}, ..., V_{d'*2^(s-1)}
        for i in range(1, s):
            u, v = self._lucas_double(u, v, p, q, n)
            if v == 0:
                return True
        
        return False
    
    def _jacobi_symbol(self, a: int, n: int) -> int:
        """Compute Jacobi symbol (a/n).
        
        Args:
            a: Numerator
            n: Denominator (must be odd and > 0)
            
        Returns:
            Jacobi symbol: -1, 0, or 1
        """
        if n <= 0 or n % 2 == 0:
            return 0
        
        a = a % n
        if a == 0:
            return 0
        
        result = 1
        while a != 0:
            # Remove factors of 2
            while a % 2 == 0:
                a //= 2
                if n % 8 in (3, 5):
                    result = -result
            
            # Swap a and n
            a, n = n, a
            
            # Apply quadratic reciprocity
            if a % 4 == 3 and n % 4 == 3:
                result = -result
            
            a = a % n
        
        if n == 1:
            return result
        return 0
    
    def _lucas_sequence_iterative(self, p: int, q: int, k: int, n: int) -> tuple[int, int]:
        """Compute Lucas sequence U_k and V_k modulo n using iterative method.
        
        More reliable for small values, uses binary method for efficiency.
        
        Args:
            p, q: Lucas sequence parameters
            k: Index
            n: Modulus
            
        Returns:
            Tuple (U_k mod n, V_k mod n)
        """
        if k == 0:
            return (0, 2 % n)
        if k == 1:
            return (1 % n, p % n)
        
        # Use binary method for efficiency
        u, v = 1 % n, p % n
        k_bits = bin(k)[3:]  # Skip '0b1', process remaining bits
        
        for bit in k_bits:
            # Double: (U_k, V_k) -> (U_{2k}, V_{2k})
            u, v = self._lucas_double(u, v, p, q, n)
            
            # If bit is 1, advance: (U_{2k}, V_{2k}) -> (U_{2k+1}, V_{2k+1})
            if bit == '1':
                u, v = self._lucas_next(u, v, p, q, n)
        
        return (u, v)
    
    def _lucas_sequence(self, p: int, q: int, k: int, n: int) -> tuple[int, int]:
        """Compute Lucas sequence U_k and V_k modulo n using binary method.
        
        Args:
            p, q: Lucas sequence parameters
            k: Index
            n: Modulus
            
        Returns:
            Tuple (U_k mod n, V_k mod n)
        """
        if k == 0:
            return (0, 2 % n)
        if k == 1:
            return (1, p % n)
        
        # Binary method for computing Lucas sequence
        u, v = 1, p % n
        k_bits = bin(k)[3:]  # Binary representation without '0b1'
        
        for bit in k_bits:
            u, v = self._lucas_double(u, v, p, q, n)
            if bit == '1':
                u, v = self._lucas_next(u, v, p, q, n)
        
        return (u, v)
    
    def _lucas_double(self, u: int, v: int, p: int, q: int, n: int) -> tuple[int, int]:
        """Double the index: compute U_{2k} and V_{2k} from U_k and V_k.
        
        Args:
            u, v: Current U_k and V_k
            p, q: Lucas sequence parameters
            n: Modulus
            
        Returns:
            Tuple (U_{2k} mod n, V_{2k} mod n)
        """
        u2 = (u * v) % n
        v2 = (v * v - 2 * q) % n
        return (u2, v2)
    
    def _lucas_next(self, u: int, v: int, p: int, q: int, n: int) -> tuple[int, int]:
        """Advance by one: compute U_{k+1} and V_{k+1} from U_k and V_k.
        
        Args:
            u, v: Current U_k and V_k
            p, q: Lucas sequence parameters
            n: Modulus
            
        Returns:
            Tuple (U_{k+1} mod n, V_{k+1} mod n)
        """
        # U_{k+1} = (P*U_k + V_k) / 2
        # V_{k+1} = (P*V_k + U_k*(P^2 - 4*Q)) / 2
        # Handle division by 2 in modular arithmetic using modular inverse of 2
        # For odd n, 2^(-1) mod n = (n+1)//2
        inv_2 = (n + 1) // 2 if n % 2 == 1 else None
        
        if inv_2 is not None:
            u_next = ((p * u + v) * inv_2) % n
            delta = (p * p - 4 * q) % n
            v_next = ((p * v + u * delta) * inv_2) % n
        else:
            # Fallback for even n (shouldn't happen in practice)
            u_next = ((p * u + v) // 2) % n
            delta = (p * p - 4 * q) % n
            v_next = ((p * v + u * delta) // 2) % n
        
        return (u_next, v_next)
    
    @monitor_memory
    @monitor_timeout
    def calculate_by_digits(self, d: int) -> int:
        """Calculate the first prime with at least d digits.
        
        Starts search at 10^(d-1) and uses Miller-Rabin/Baillie-PSW for primality testing.
        
        Args:
            d: Minimum number of digits
            
        Returns:
            The first prime with at least d digits
            
        Raises:
            InputError: If d is not a positive integer
        """
        if not isinstance(d, int) or d <= 0:
            raise InputError("Input 'd' (minimum digits) must be a positive integer.")
        
        if d == 1:
            return 2  # First 1-digit prime
        
        # Start search at 10^(d-1)
        start = 10 ** (d - 1)
        
        # Search for first prime with at least d digits
        # Check odd numbers only (except for 2)
        if start == 1:
            # Special case: d=1, but we already handled it
            return 2
        
        # If start is even, start from start+1
        if start % 2 == 0:
            candidate = start + 1
        else:
            candidate = start
        
        while True:
            # Check if candidate has at least d digits
            if len(str(candidate)) < d:
                candidate += 2
                continue
            
            # Use Miller-Rabin for primality testing
            if self.miller_rabin(candidate):
                return candidate
            
            candidate += 2  # Only check odd numbers

