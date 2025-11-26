# py_mega_calc

A high-performance, pure Python command-line application designed to calculate extremely large numbers (Primes, Fibonacci sequence, Factorials) with absolute precision.

## Features

- **Pure Python**: No C-extensions required (uses Python 3.11+ native integer arithmetic)
- **High Performance**: Optimized algorithms for large number calculations
  - Fibonacci: Fast Doubling Method (O(log n))
  - Factorial: C-optimized `math.factorial`
  - Primes: Segmented Sieve (by index) and Miller-Rabin/Baillie-PSW (by digits)
- **Resource Management**: Automatic monitoring of RAM (24GB limit) and execution time (5-minute limit)
- **Precision**: 100% integer arithmetic, no floating-point errors
- **Benchmarking**: Built-in estimator for predicting calculation times
- **Comprehensive Testing**: 208 tests with 77% code coverage

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd py_mega_calc

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python -m src.main [calculator_type] [options]
```

### Calculator Types

- `fib` - Fibonacci sequence
- `fact` - Factorial
- `prime` - Prime numbers

### Options

- `--index, -i <n>` - Calculate the nth number (mutually exclusive with --min-digits)
- `--min-digits, -d <d>` - Find first number with at least d digits (mutually exclusive with --index)
- `--benchmark` - Run estimation benchmark before calculation
- `--dry-run` - Show estimated time without performing calculation
- `--strict` - Abort if estimated time exceeds 5-minute limit

## Examples

### Fibonacci Calculations

```bash
# Calculate 10th Fibonacci number (F(10) = 55)
python -m src.main fib --index 10

# Find first Fibonacci number with 3 digits
python -m src.main fib --min-digits 3

# Calculate with benchmark estimation
python -m src.main fib --index 100 --benchmark

# Dry run to estimate time without calculating
python -m src.main fib --index 1000 --dry-run
```

### Factorial Calculations

```bash
# Calculate 5! = 120
python -m src.main fact --index 5

# Find first factorial with 4 digits
python -m src.main fact --min-digits 4

# Calculate with strict time limit enforcement
python -m src.main fact --index 1000 --strict
```

### Prime Number Calculations

```bash
# Calculate 10th prime number (29)
python -m src.main prime --index 10

# Find first prime with 5 digits (10007)
python -m src.main prime --min-digits 5

# Calculate with benchmark and strict mode
python -m src.main prime --index 1000 --benchmark --strict
```

### Combined Flags

```bash
# Run benchmark, estimate time, and enforce strict limits
python -m src.main fib --index 500 --benchmark --strict

# Dry run with benchmark for large calculation
python -m src.main fact --index 10000 --benchmark --dry-run
```

## Output

The application provides:

1. **Console Output**: 
   - Result (truncated if > 1000 characters)
   - Metadata (execution time, RAM usage)

2. **File Output**: 
   - Full result saved to `results/{timestamp}_{type}.txt`
   - Includes metadata and complete number

### Example Output

```
Result (2 digits):
55

Metadata:
  Execution time: 0.000 seconds
  Peak RAM usage: 0.00 MB

Full result saved to: results/20251126_164945_fib.txt
```

## Resource Limits

- **Memory**: 24 GB maximum
- **Time**: 5 minutes (300 seconds) maximum
- **Precision**: 100% integer arithmetic (no floats in core logic)

## Project Structure

```
py_mega_calc/
├── docs/
│   ├── spec.md                    # Project specification
│   ├── algorithms.md              # Algorithm explanations
│   └── IMPLEMENTATION_STATUS.md  # Progress tracker
├── results/                       # Generated output files
├── src/
│   ├── main.py                    # Entry point
│   ├── cli.py                     # CLI interface (Typer)
│   ├── config.py                  # Configuration constants
│   ├── core/
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── resource_manager.py    # Resource monitoring
│   │   └── estimator.py           # Benchmarking utility
│   └── calculators/
│       ├── base.py                # Abstract base class
│       ├── fibonacci.py           # Fibonacci calculator
│       ├── factorial.py           # Factorial calculator
│       └── primes.py              # Prime calculator
└── tests/                         # Test suite (208 tests)
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_fibonacci.py -v
```

## Development

This project follows strict **Test-Driven Development (TDD)** principles:

1. Write failing test (RED)
2. Implement minimum code to pass (GREEN)
3. Refactor and optimize (REFACTOR)

All code changes must include comprehensive tests.

See `docs/spec.md` for full specification.

## License

[To be determined]
