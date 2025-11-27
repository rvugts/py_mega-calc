# Specification Deviations Analysis

This document lists all deviations from the specification found in the current implementation.

## 1. Factorial Algorithm - Binary Splitting Not Implemented

**Spec Requirement (4.2):**
- **Algorithm:** **Binary Splitting** (or Prime Swing if feasible in pure Python).
- The implementation should benchmark `math.factorial` vs. a custom recursive Binary Split.

**Current Implementation:**
- Uses `math.factorial` wrapper (correct)
- Benchmark function exists but uses **simple iterative multiplication** (`_custom_factorial_simple`) instead of Binary Splitting
- The custom implementation is `O(n)` iterative, not `O(n (\log n)^2)` Binary Splitting

**Deviation:** ~~The spec requires Binary Splitting algorithm for benchmarking, but the implementation uses simple iterative multiplication. While `math.factorial` is correctly used for production, the benchmark comparison doesn't use the specified algorithm.~~

**Status:** ✅ **RESOLVED** - Binary Splitting algorithm (`_binary_splitting_factorial`) has been implemented with O(n (log n)^2) complexity. The benchmark function now uses Binary Splitting instead of simple iteration.

**Location:** `src/calculators/factorial.py` - `_binary_splitting_factorial()` function

---

## 2. Automatic Estimation for Large Numbers (>10,000 digits)

**Spec Requirement (5.3):**
- **Estimation:** Before starting a calculation expected to produce $>10,000$ digits, run the `Estimator`. If the extrapolated time > 5 minutes, warn the user (or abort if `--strict` flag is on).

**Current Implementation:**
- Estimation only runs when `--benchmark` or `--dry-run` flags are explicitly provided
- No automatic estimation before calculations that would produce >10,000 digits

**Deviation:** ~~The spec requires automatic estimation for calculations expected to produce >10,000 digits, but the current implementation only estimates when explicitly requested via flags.~~

**Status:** ✅ **RESOLVED** - Automatic estimation now runs when `estimate_digit_count()` predicts >10,000 digits. The CLI automatically triggers estimation and warns/aborts based on `--strict` flag.

**Location:** `src/cli.py` - `estimate_digit_count()` function and automatic estimation logic

---

## 3. PrecisionError Not Used

**Spec Requirement (5.4):**
- **`PrecisionError`:** Explicit checks to ensure no floats were used in the pipeline.

**Current Implementation:**
- `PrecisionError` exception class exists in `src/core/exceptions.py`
- **No actual checks are performed** to detect float usage in core logic
- The exception is never raised anywhere in the codebase

**Deviation:** ~~The spec requires explicit checks to ensure no floats are used, but no such validation is implemented.~~

**Status:** ✅ **RESOLVED** - Precision checking functions (`validate_no_floats`, `check_precision`, `validate_calculation_inputs`) have been implemented and integrated into all calculator methods. PrecisionError is now raised when floats are detected.

**Location:** `src/core/precision_checker.py` - New module with precision checking functions

---

## 4. Baillie-PSW Implementation Incomplete

**Spec Requirement (4.3):**
- **Primality Test:** **Miller-Rabin** (deterministic for $n < 3 \times 10^{24}$, probabilistic with $k=40$ rounds for larger $n$) combined with **Lucas-Lehmer** or **Baillie-PSW** for robustness.

**Current Implementation:**
- Miller-Rabin is correctly implemented with deterministic bases and k=40 rounds
- Baillie-PSW exists but **falls back to Miller-Rabin** due to known issues with Lucas sequence computation
- Comment in code: "Current implementation has known issues with Lucas sequence computation for some primes. Falls back to Miller-Rabin for reliability."

**Deviation:** ~~Baillie-PSW is not fully functional - it doesn't actually perform the Lucas test, just uses Miller-Rabin with 10 rounds instead of the full Baillie-PSW test.~~

**Status:** ✅ **RESOLVED** - Full Baillie-PSW implementation with working Lucas sequence computation. The method now performs both base-2 Miller-Rabin test and strong Lucas probable prime test. Fixed Lucas sequence computation to properly track Q^k for correct doubling.

**Location:** `src/calculators/primes.py` - `baillie_psw()` method with `_lucas_sequence_iterative()` and `_lucas_double_with_q()`

---

## 5. Type Hinting (mypy strict) Not Configured

**Spec Requirement (6):**
- **Code Quality:** PEP 8 compliance, Type Hinting (`mypy` strict), Docstrings (Google style).

**Current Implementation:**
- `mypy>=1.5.0` is in `requirements.txt`
- **No `mypy.ini` or `pyproject.toml` configuration** for strict type checking
- Type hints are present but not enforced via mypy strict mode

**Deviation:** ~~While type hints exist, there's no mypy configuration to enforce strict type checking as required by the spec.~~

**Status:** ✅ **RESOLVED** - `mypy.ini` configuration file created with strict type checking enabled. All strict flags are configured including `disallow_untyped_defs`, `check_untyped_defs`, `warn_return_any`, etc.

**Location:** `mypy.ini` - Root directory configuration file

---

## 6. Code Coverage Not 100%

**Spec Requirement (6):**
- **Testing:** 100% Code Coverage for logic.

**Current Implementation:**
- Current overall coverage is **76%** (579 statements, 140 missed)
- Many calculator methods have low coverage (e.g., primes.py at ~21%, factorial.py at ~25%)

**Deviation:** The spec requires 100% code coverage for logic, but current coverage is 76%, significantly below the threshold.

**Location:** Coverage report shows missing coverage across multiple files, particularly in calculator implementations

---

## Summary Table

| # | Deviation | Spec Section | Severity | Status |
|---|-----------|--------------|-----------|--------|
| 1 | Binary Splitting not implemented for factorial benchmark | 4.2 | Medium | ✅ **RESOLVED** - Binary Splitting algorithm implemented with O(n (log n)^2) complexity |
| 2 | No automatic estimation for >10,000 digits | 5.3 | Medium | ✅ **RESOLVED** - Automatic estimation now runs for calculations expected to produce >10,000 digits |
| 3 | PrecisionError never raised/checked | 5.4 | Low | ✅ **RESOLVED** - Precision checks implemented, validate_no_floats and check_precision functions added |
| 4 | Baillie-PSW incomplete (falls back to Miller-Rabin) | 4.3 | Medium | ✅ **RESOLVED** - Full Baillie-PSW implementation with working Lucas sequence computation |
| 5 | No mypy strict configuration | 6 | Low | ✅ **RESOLVED** - mypy.ini created with strict type checking configuration |
| 6 | Code coverage < 100% | 6 | Medium | ⚠️ **PARTIAL** - Coverage improved but not yet at 100%. Requires additional test cases |

## Notes

- Most deviations are related to completeness rather than correctness
- Core functionality works correctly (Fibonacci, Factorial, Primes calculations)
- Resource management and CLI integration are fully functional
- The deviations are primarily in:
  - Algorithm implementation details (Binary Splitting)
  - Automatic feature triggers (estimation)
  - Validation checks (PrecisionError)
  - Code quality enforcement (mypy strict, 100% coverage)

