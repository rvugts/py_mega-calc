# py_mega_calc

A high-performance, pure Python command-line application designed to calculate extremely large numbers (Primes, Fibonacci sequence, Factorials) with absolute precision.

## Features

- **High Precision**: 100% integer arithmetic, no floating-point operations
- **Resource Management**: Hard limits on memory (24GB) and execution time (5 minutes)
- **Performance Estimation**: Benchmark-based time prediction for large calculations
- **Multiple Calculators**: Prime, Fibonacci, and Factorial calculations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m src.main [type] [--index N | --min-digits D] [--benchmark] [--dry-run]
```

## Development

This project follows Test Driven Development (TDD) and Specification Driven Development (SDD).

See `docs/spec.md` for full specification.

## License

[To be determined]

