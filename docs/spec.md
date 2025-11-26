# Project Specification: `py_mega_calc`

## 1. Overview
`py_mega_calc` is a high-performance, pure Python command-line application designed to calculate extremely large numbers (Primes, Fibonacci sequence, Factorials) with absolute precision. The system strictly adheres to Test Driven Development (TDD) and Specification Driven Development (SDD).

The application is optimized for outputs exceeding 10,000 digits, enforcing strict resource constraints (24GB RAM, 5-minute timeout) and providing execution time estimates based on hardware benchmarking.

## 2. Technical Stack
*   **Language:** Python 3.11+ (Leveraging optimizations in integer arithmetic).
*   **Core Libraries:**
    *   `math`, `itertools`, `functools` (Standard Library).
    *   `psutil` (System resource monitoring).
    *   `typer` or `argparse` (CLI interaction).
    *   `pytest` (Testing framework).
*   **Constraints:**
    *   **No C-extensions** that require compilation (e.g., `gmpy2` is banned unless pre-installed in the environment, assume standard Python environment).
    *   Arbitrary-precision integers (Python's native `int`).

## 3. Architecture

### 3.1. Design Pattern
The application follows a **Strategy Pattern** for the calculators and a **Decorator/Proxy Pattern** for resource management (timeouts and memory guards).

### 3.2. Core Components
1.  **`Calculator` (Abstract Base Class):** Defines the interface `calculate_by_index(n)` and `calculate_by_digits(d)`.
2.  **`ConcreteCalculators`:**
    *   `PrimeCalculator`
    *   `FibonacciCalculator`
    *   `FactorialCalculator`
3.  **`ResourceManager`:** A monitoring layer that tracks RAM usage and execution time, raising `ResourceExhaustedError` or `TimeoutError` if limits are breached.
4.  **`Estimator`:** A regression-based benchmarking utility that runs micro-benchmarks on startup (or on demand) to predict calculation time for large inputs.

## 4. Algorithms & Implementation Details

To meet the "fast as possible" requirement using only Python:

### 4.1. Fibonacci Calculator
*   **Algorithm:** **Fast Doubling Method** (Iterative).
    *   Complexity: $O(\log n)$.
    *   Significantly faster than Matrix Exponentiation due to fewer arithmetic operations.
    *   *Note:* Binet’s formula is forbidden due to floating-point precision loss.

### 4.2. Factorial Calculator
*   **Algorithm:** **Binary Splitting** (or Prime Swing if feasible in pure Python).
    *   Comparison: The standard `math.factorial` is C-optimized in CPython. The implementation should benchmark `math.factorial` vs. a custom recursive Binary Split. If `math.factorial` is faster (likely), wrap it.
    *   Complexity: $O(n (\log n)^2)$.

### 4.3. Prime Calculator
*   **Mode A (By Index - Nth Prime):**
    *   **Algorithm:** **Segmented Sieve of Eratosthenes** (for N up to $\approx 10^9$).
    *   *Constraint:* Calculating the Nth prime where the *result* has 10,000 digits is mathematically impossible in 5 minutes (as N would be $\approx 10^{9996}$). The spec limits "By Index" to reasonable bounds (e.g., N < 100,000,000).
*   **Mode B (By Min Digits - First Prime with D digits):**
    *   **Algorithm:** Start search at $10^{D-1}$.
    *   **Primality Test:** **Miller-Rabin** (deterministic for $n < 3 \times 10^{24}$, probabilistic with $k=40$ rounds for larger $n$) combined with **Lucas-Lehmer** or **Baillie-PSW** for robustness.
    *   To satisfy "Precise": Baillie-PSW is generally accepted as precise for practical engineering (no known pseudoprimes).

## 5. Functional Requirements

### 5.1. Inputs
The CLI must accept:
1.  **Type:** `prime`, `fib`, `fact`
2.  **Mode:** `--index [int]` OR `--min-digits [int]`
3.  **Flags:** `--benchmark` (to run estimation), `--dry-run` (returns estimated time without calculating).

### 5.2. Outputs
*   **Standard Output:** The resulting number (if < 1000 chars) or a truncation.
*   **File Output:** Full result saved to `results/{timestamp}_{type}.txt`.
*   **Metadata:** Calculation time (seconds), RAM peak usage (MB).

### 5.3. Resource Guard Rails
*   **Time Limit:** Hard abort at 300 seconds (5 minutes).
*   **Memory Limit:** Hard abort if process memory > 24 GB.
*   **Estimation:** Before starting a calculation expected to produce $>10,000$ digits, run the `Estimator`. If the extrapolated time > 5 minutes, warn the user (or abort if `--strict` flag is on).

### 5.4. Error Handling
*   **`InputError`:** Negative numbers, non-integers, or mutually exclusive flags.
*   **`CalculationTooLargeError`:** If the estimation predicts weeks of processing.
*   **`PrecisionError`:** Explicit checks to ensure no floats were used in the pipeline.

## 6. Non-Functional Requirements
*   **Precision:** 100% integer arithmetic. No floats allowed in core logic.
*   **Code Quality:** PEP 8 compliance, Type Hinting (`mypy` strict), Docstrings (Google style).
*   **Testing:** 100% Code Coverage for logic. Tests must include "Gold Standard" values for known large numbers (e.g., verified from OEIS).

## 7. Development Roadmap (TDD)
1.  **Skeleton:** Set up project structure and abstract classes.
2.  **Benchmarker:** Implement the `Estimator` logic first.
3.  **Factorial:** Implement `math.factorial` wrapper + Tests.
4.  **Fibonacci:** Implement Fast Doubling + Tests.
5.  **Prime:** Implement Sieve/Miller-Rabin + Tests.
6.  **CLI:** Integration of all components.

## 8. Directory Structure

```text
py_mega_calc/
├── docs/
│   ├── spec.md               # This file
│   ├── algorithms.md         # Math explanations
│   └── IMPLEMENTATION_STATUS.md # Progress tracker
├── results/                  # Generated output files
├── src/
│   ├── __init__.py
│   ├── main.py               # Entry point
│   ├── cli.py                # Typer/Argparse logic
│   ├── config.py             # Constants (24GB limit, etc.)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── resource_manager.py # Decorators for time/RAM
│   │   └── estimator.py      # Benchmarking logic
│   └── calculators/
│       ├── __init__.py
│       ├── base.py           # Abstract Base Class
│       ├── fibonacci.py
│       ├── factorial.py
│       └── primes.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_fibonacci.py
│   ├── test_factorial.py
│   ├── test_primes.py
│   ├── test_resources.py
│   └── test_estimator.py
├── .cursor/rules             # AI context rules
├── .gitignore
├── requirements.txt
├── pytest.ini
└── README.md
```

## 9. Implementation Status Template
*(To be created in `docs/IMPLEMENTATION_STATUS.md`)*

```markdown
# Implementation Status

| Component | Sub-task | Status | Tests Passing | Notes |
|-----------|----------|--------|---------------|-------|
| **Core**  | Architecture Setup | [ ] | N/A | |
|           | Resource Manager | [ ] | [ ] | Needs psutil integration |
|           | Estimator | [ ] | [ ] | Linear/Poly regression logic |
| **Fib**   | Fast Doubling Algo | [ ] | [ ] | |
| **Fact**  | Binary Split/Math | [ ] | [ ] | |
| **Prime** | Sieve (Index) | [ ] | [ ] | |
|           | Miller-Rabin (Digits)| [ ] | [ ] | |
| **CLI**   | Typer Integration | [ ] | [ ] | |
```

## 10. Constraints Validation Logic
*   **Memory Estimation:** Python `int` size $\approx (bits / 30) \times 4$ bytes.
    *   10,000 digits $\approx$ 33,220 bits $\approx$ 4.4 KB. (Memory is not a concern for the result storage, only for the algorithm's intermediate states).
    *   24GB allows for handling numbers with $\approx 6$ billion digits. The bottleneck will be CPU/Time, not RAM, unless inefficient recursion is used.
*   **Time Estimation:**
    *   The `Estimator` must run a micro-benchmark (calculate small N) and extrapolate.
    *   Fibonacci: $T(n) \propto \log n$
    *   Factorial: $T(n) \propto n (\log n)^2$
    *   Primes: Probabilistic, highly variance-dependent. Estimate based on average density $1/\ln(N)$.