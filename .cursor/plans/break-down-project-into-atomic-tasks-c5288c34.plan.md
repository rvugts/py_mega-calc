<!-- c5288c34-adb2-4e46-b597-da32f3050153 419f2090-a73e-4b9f-b086-21b1719f2b11 -->
# Break Down Project into Atomic Tasks

## Analysis

Based on the specification, the project needs to be broken down into atomic tasks that:

- Can be completed in a single prompt
- Follow strict TDD (test first, then implementation)
- Are independently testable
- Follow the Red-Green-Refactor cycle

## Task Breakdown

### Phase 1: Core Foundation (5 tasks)

1. **Custom Exceptions** - Implement all 5 custom exception classes with tests

- InputError, CalculationTooLargeError, PrecisionError, ResourceExhaustedError, TimeoutError
- File: `src/core/exceptions.py`, `tests/test_exceptions.py`

2. **ResourceManager - Memory Monitoring** - Implement memory monitoring decorator with tests

- Track RAM usage using psutil, raise ResourceExhaustedError if > 24GB
- File: `src/core/resource_manager.py`, `tests/test_resources.py`

3. **ResourceManager - Timeout** - Implement timeout decorator with tests

- Hard abort at 300 seconds, raise TimeoutError
- File: `src/core/resource_manager.py`, `tests/test_resources.py`

4. **Estimator - Micro-benchmark** - Implement micro-benchmark execution with tests

- Run small calculations to measure baseline performance
- File: `src/core/estimator.py`, `tests/test_estimator.py`

5. **Estimator - Regression Prediction** - Implement regression-based time prediction with tests

- Linear/polynomial regression for Fibonacci, Factorial, Prime calculations
- File: `src/core/estimator.py`, `tests/test_estimator.py`

### Phase 2: Fibonacci Calculator (4 tasks)

6. **Fibonacci - calculate_by_index (Basic)** - Implement Fast Doubling Method with basic tests

- Test cases: F(0)=0, F(1)=1, F(2)=1, F(10), F(20) (OEIS verified)
- File: `src/calculators/fibonacci.py`, `tests/test_fibonacci.py`

7. **Fibonacci - calculate_by_index (Edge Cases)** - Add edge case tests and validation

- Negative inputs (raise InputError), large values, resource limit tests
- File: `tests/test_fibonacci.py`, update `src/calculators/fibonacci.py`

8. **Fibonacci - calculate_by_digits** - Implement and test calculate_by_digits method

- Find first Fibonacci number with at least d digits
- File: `src/calculators/fibonacci.py`, `tests/test_fibonacci.py`

9. **Fibonacci - ResourceManager Integration** - Integrate with ResourceManager decorators

- Apply memory and timeout decorators
- File: `src/calculators/fibonacci.py`

### Phase 3: Factorial Calculator (4 tasks)

10. **Factorial - Benchmark Comparison** - Benchmark math.factorial vs custom Binary Split

- Create benchmark script, decide which to use
- File: `src/calculators/factorial.py`, `tests/test_factorial.py`

11. **Factorial - calculate_by_index** - Implement calculate_by_index with tests

- Test cases: 0!=1, 1!=1, 5!=120, 10! (OEIS verified)
- File: `src/calculators/factorial.py`, `tests/test_factorial.py`

12. **Factorial - calculate_by_digits** - Implement and test calculate_by_digits method

- Find first factorial with at least d digits
- File: `src/calculators/factorial.py`, `tests/test_factorial.py`

13. **Factorial - ResourceManager Integration** - Integrate with ResourceManager decorators

- Apply memory and timeout decorators
- File: `src/calculators/factorial.py`

### Phase 4: Prime Calculator (5 tasks)

14. **Prime - Segmented Sieve (calculate_by_index)** - Implement Segmented Sieve with tests

- Test cases: 1st prime=2, 2nd=3, 10th=29, 100th=541 (OEIS verified)
- File: `src/calculators/primes.py`, `tests/test_primes.py`

15. **Prime - Miller-Rabin Primality Test** - Implement Miller-Rabin test with tests

- Deterministic for n < 3×10²⁴, probabilistic with k=40 rounds
- File: `src/calculators/primes.py`, `tests/test_primes.py`

16. **Prime - Baillie-PSW Test** - Implement Baillie-PSW test with tests

- Combine with Miller-Rabin for robustness
- File: `src/calculators/primes.py`, `tests/test_primes.py`

17. **Prime - calculate_by_digits** - Implement calculate_by_digits using Miller-Rabin/Baillie-PSW

- Start search at 10^(d-1), find first prime with d digits
- File: `src/calculators/primes.py`, `tests/test_primes.py`

18. **Prime - ResourceManager Integration** - Integrate with ResourceManager decorators

- Apply memory and timeout decorators
- File: `src/calculators/primes.py`

### Phase 5: CLI Integration (4 tasks)

19. **CLI - Argument Parsing** - Implement CLI argument parsing with tests

- Type (prime/fib/fact), --index, --min-digits (mutually exclusive)
- File: `src/cli.py`, `tests/test_cli.py`

20. **CLI - Flags** - Implement CLI flags with tests

- --benchmark, --dry-run, --strict
- File: `src/cli.py`, `tests/test_cli.py`

21. **CLI - Output Formatting** - Implement output formatting and file writing with tests

- Console output (< 1000 chars or truncation), file output to results/
- Metadata: time, RAM usage
- File: `src/cli.py`, `tests/test_cli.py`

22. **CLI - Calculator Integration** - Integrate CLI with calculator classes

- Wire up CLI commands to calculator instances
- File: `src/cli.py`, `src/main.py`

### Phase 6: Integration & Polish (2 tasks)

23. **Main Entry Point** - Implement main.py entry point

- Connect CLI to main execution flow
- File: `src/main.py`

24. **End-to-End Testing** - Create end-to-end integration tests

- Test full workflows: CLI → Calculator → Output
- File: `tests/test_integration.py`

## Implementation

Update `docs/IMPLEMENTATION_STATUS.md` to replace the high-level tasks with the detailed 24 atomic tasks listed above, organized by phase. Each task should have:

- Component name
- Specific sub-task description
- Status checkbox [ ]
- Tests Passing checkbox [ ]
- Notes column for implementation details