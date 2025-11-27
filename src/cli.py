"""CLI interface for py_mega_calc using Typer.

This module provides the command-line interface for the py_mega_calc
application, handling user input, validation, estimation, and calculation
execution.

Dependencies:
    - os: File system operations
    - sys: System-specific parameters
    - time: Time measurement
    - math: Mathematical operations for digit estimation
    - datetime: Timestamp generation
    - pathlib: Path operations
    - functools: Function decorators
    - enum: Enumeration support
    - typing: Type hints
    - typer: CLI framework (third-party)
    - psutil: System and process utilities (third-party)
    - src.calculators: Calculator implementations
    - src.core.estimator: Time estimation
    - src.core.exceptions: Custom exceptions
    - src.config: Configuration constants
"""

import math
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import psutil
import typer

from src.calculators.factorial import FactorialCalculator
from src.calculators.fibonacci import FibonacciCalculator
from src.calculators.primes import PrimeCalculator
from src.config import LARGE_DIGIT_THRESHOLD, MAX_TIME_SECONDS
from src.core.estimator import Estimator
from src.core.exceptions import (
    CalculationTooLargeError,
    InputError,
    ResourceExhaustedError,
    TimeoutError as CalculationTimeoutError,
)

# Set int max str digits to handle large numbers (10,000+ digits as per spec)
# Default limit is 4300, we need at least 10,000
# Set to 1,000,000 to handle extremely large numbers
sys.set_int_max_str_digits(1000000)

app = typer.Typer()

# Module-level constants
DEFAULT_MAX_DISPLAY_CHARS = 1000
MEMORY_UNIT_MB = 1024 * 1024
HALF_DISPLAY = DEFAULT_MAX_DISPLAY_CHARS // 2

# Benchmark input values by calculator type
BENCHMARK_INPUTS: Dict[str, Dict[str, List[int]]] = {
    "primes": {
        "by_index": [100, 500, 1000, 2000, 5000],
        "by_digits": [2, 3, 4, 5, 6],
    },
    "fibonacci": {
        "by_index": [100, 500, 1000, 2000, 5000],
        "by_digits": [100, 500, 1000, 2000, 5000],
    },
    "factorial": {
        "by_index": [50, 100, 200, 500, 1000],
        "by_digits": [50, 100, 200, 500, 1000],
    },
}


def handle_calculation_errors(func: Callable) -> Callable:
    """Decorator to handle calculator errors uniformly.

    :param func: Function to wrap with error handling
    :type func: Callable
    :return: Wrapped function
    :rtype: Callable
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except InputError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)
        except (
            CalculationTooLargeError,
            ResourceExhaustedError,
            CalculationTimeoutError,
        ) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)
        except Exception as e:
            typer.echo(f"Unexpected error: {e}", err=True)
            raise typer.Exit(code=1)
    return wrapper


class CalculatorType(str, Enum):
    """Supported calculator types."""

    PRIME = "prime"
    FIB = "fib"
    FACT = "fact"


@dataclass
class EstimationContext:
    """Context object for estimation parameters.

    Groups related estimation parameters to reduce function argument count.

    :param needs_automatic_estimation: Whether auto-estimation triggered
    :type needs_automatic_estimation: bool
    :param estimated_digits: Estimated digit count
    :type estimated_digits: int
    :param benchmark: Whether benchmark flag is set
    :type benchmark: bool
    :param dry_run: Whether dry-run flag is set
    :type dry_run: bool
    :param strict: Whether strict flag is set
    :type strict: bool
    """

    needs_automatic_estimation: bool
    estimated_digits: int
    benchmark: bool
    dry_run: bool
    strict: bool


@dataclass
class CalculationRequest:
    """Request object for calculation parameters.

    Groups calculation-related parameters to reduce argument count.

    :param input_value: Input value for calculation
    :type input_value: int
    :param estimator_calc_type: Type string for estimator
    :type estimator_calc_type: str
    :param use_by_index: Whether using --index mode
    :type use_by_index: bool
    """

    input_value: int
    estimator_calc_type: str
    use_by_index: bool


def _validate_inputs(
    index: Optional[int], min_digits: Optional[int]
) -> None:
    """Validate CLI input arguments.

    :param index: Index value if provided
    :type index: Optional[int]
    :param min_digits: Minimum digits value if provided
    :type min_digits: Optional[int]
    :raises typer.Exit: If validation fails
    """
    if index is not None and min_digits is not None:
        typer.echo(
            "Error: --index and --min-digits are mutually exclusive. "
            "Use only one.",
            err=True,
        )
        raise typer.Exit(code=1)

    if index is None and min_digits is None:
        typer.echo(
            "Error: Either --index or --min-digits must be provided.",
            err=True,
        )
        raise typer.Exit(code=1)

    if index is not None and index < 0:
        typer.echo(
            "Error: --index must be a non-negative integer.",
            err=True,
        )
        raise typer.Exit(code=1)

    if min_digits is not None and min_digits <= 0:
        typer.echo(
            "Error: --min-digits must be a positive integer.",
            err=True,
        )
        raise typer.Exit(code=1)


def _initialize_calculator(
    calculator_type: CalculatorType,
) -> Tuple[Any, str, str]:
    """Initialize calculator and return calculator, type strings.

    :param calculator_type: Type of calculator to create
    :type calculator_type: CalculatorType
    :return: Tuple of (calculator, calc_type_str, estimator_calc_type)
    :rtype: Tuple[Any, str, str]
    :raises typer.Exit: If calculator type is unknown
    """
    if calculator_type == CalculatorType.FIB:
        return (FibonacciCalculator(), "fib", "fibonacci")
    if calculator_type == CalculatorType.FACT:
        return (FactorialCalculator(), "fact", "factorial")
    if calculator_type == CalculatorType.PRIME:
        return (PrimeCalculator(), "prime", "primes")

    typer.echo(
        f"Error: Unknown calculator type: {calculator_type}",
        err=True,
    )
    raise typer.Exit(code=1)


def _get_benchmark_inputs(
    estimator_calc_type: str, use_by_index: bool
) -> List[int]:
    """Get appropriate benchmark input values for calculation type.

    :param estimator_calc_type: Type of calculation for estimator
    :type estimator_calc_type: str
    :param use_by_index: Whether using --index mode
    :type use_by_index: bool
    :return: List of input values for benchmarking
    :rtype: List[int]
    """
    mode = "by_index" if use_by_index else "by_digits"
    inputs = BENCHMARK_INPUTS.get(estimator_calc_type, {})
    return inputs.get(mode, [1, 5, 10, 20, 50])


def _run_benchmark_if_needed(
    estimator: Estimator,
    calculator: Any,
    estimator_calc_type: str,
    use_by_index: bool,
) -> None:
    """Run micro-benchmark if benchmark data is missing.

    :param estimator: Estimator instance
    :type estimator: Estimator
    :param calculator: Calculator instance
    :type calculator: Any
    :param estimator_calc_type: Type string for estimator
    :type estimator_calc_type: str
    :param use_by_index: Whether using --index mode
    :type use_by_index: bool
    """
    if (
        estimator_calc_type not in estimator.benchmark_data
        or not estimator.benchmark_data[estimator_calc_type]
    ):
        typer.echo("Running micro-benchmark...")
        test_inputs = _get_benchmark_inputs(
            estimator_calc_type, use_by_index
        )

        calc_func: Callable[[int], Any] = (
            calculator.calculate_by_index
            if use_by_index
            else calculator.calculate_by_digits
        )

        benchmark_results = estimator.run_micro_benchmark(
            calc_func, test_inputs
        )
        estimator.benchmark_data[estimator_calc_type] = benchmark_results


def _display_automatic_estimation(context: EstimationContext) -> None:
    """Display automatic estimation message if needed.

    :param context: Estimation context with display parameters
    :type context: EstimationContext
    """
    show = context.needs_automatic_estimation and not (
        context.benchmark or context.dry_run
    )
    if show:
        typer.echo(
            f"Automatic estimation: Result expected to have "
            f"~{context.estimated_digits} digits (>10,000 threshold)."
        )


def _predict_estimation_time(
    estimator: Estimator, input_value: int, estimator_calc_type: str
) -> float:
    """Predict execution time using estimator.

    :param estimator: Estimator instance
    :type estimator: Estimator
    :param input_value: Input value for calculation
    :type input_value: int
    :param estimator_calc_type: Type string for estimator
    :type estimator_calc_type: str
    :return: Estimated time in seconds or infinity if prediction failed
    :rtype: float
    """
    try:
        estimated_time = estimator.predict_time(
            input_value, estimator_calc_type
        )
        typer.echo(
            f"Estimated execution time: {estimated_time:.3f} seconds"
        )
        return estimated_time
    except (ValueError, KeyError) as e:
        typer.echo(f"Warning: Could not predict time accurately: {e}")
        typer.echo(
            "Estimated execution time: Unknown "
            "(benchmark data insufficient)"
        )
        return float('inf')


def _check_time_limit(
    estimated_time: float, strict: bool
) -> None:
    """Check if estimated time exceeds limit and handle accordingly.

    :param estimated_time: Estimated execution time in seconds
    :type estimated_time: float
    :param strict: Whether to abort on limit exceeded
    :type strict: bool
    :raises typer.Exit: If strict mode and time exceeds limit
    """
    if estimated_time <= MAX_TIME_SECONDS:
        return

    msg = (
        f"Estimated time ({estimated_time:.3f}s) exceeds limit "
        f"({MAX_TIME_SECONDS}s)."
    )

    if strict:
        typer.echo(f"Error: {msg} Aborting (--strict).", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Warning: {msg}")


def _handle_estimation(
    estimator: Estimator,
    input_value: int,
    estimator_calc_type: str,
    context: EstimationContext,
) -> Optional[float]:
    """Handle time estimation and warnings.

    :param estimator: Estimator instance
    :type estimator: Estimator
    :param input_value: Input value for calculation
    :type input_value: int
    :param estimator_calc_type: Type string for estimator
    :type estimator_calc_type: str
    :param context: Estimation context with flags
    :type context: EstimationContext
    :return: Estimated time, or None if estimation failed
    :rtype: Optional[float]
    :raises typer.Exit: If strict mode and time exceeds limit
    """
    _display_automatic_estimation(context)

    estimated_time = _predict_estimation_time(
        estimator, input_value, estimator_calc_type
    )

    _check_time_limit(estimated_time, context.strict)
    return estimated_time


def _measure_calculation(
    calculator: Any, input_value: int, use_by_index: bool
) -> Tuple[int, float, float]:
    """Execute calculation and measure performance metrics.

    :param calculator: Calculator instance
    :type calculator: Any
    :param input_value: Input value for calculation
    :type input_value: int
    :param use_by_index: Whether using --index mode
    :type use_by_index: bool
    :return: Tuple of (result, execution_time, ram_usage_mb)
    :rtype: Tuple[int, float, float]
    """
    start_time = time.perf_counter()
    process = psutil.Process()
    memory_before = process.memory_info().rss / MEMORY_UNIT_MB

    result = (
        calculator.calculate_by_index(input_value)
        if use_by_index
        else calculator.calculate_by_digits(input_value)
    )

    execution_time = time.perf_counter() - start_time
    memory_after = process.memory_info().rss / MEMORY_UNIT_MB
    ram_usage = max(0.0, memory_after - memory_before)

    return result, execution_time, ram_usage


def _display_calculation_results(
    result: int,
    execution_time: float,
    ram_usage: float,
    calc_type_str: str,
) -> None:
    """Display calculation results and save to file.

    :param result: Calculated result
    :type result: int
    :param execution_time: Execution time in seconds
    :type execution_time: float
    :param ram_usage: RAM usage in MB
    :type ram_usage: float
    :param calc_type_str: Calculator type string
    :type calc_type_str: str
    """
    formatted_result = format_result(result)
    typer.echo(formatted_result)

    metadata = format_metadata(execution_time, ram_usage)
    typer.echo(metadata)

    filepath = write_result_to_file(
        result,
        calc_type_str,
        execution_time=execution_time,
        ram_usage_mb=ram_usage,
    )
    typer.echo(f"\nFull result saved to: {filepath}")


@handle_calculation_errors
def _execute_calculation(
    calculator: Any,
    input_value: int,
    use_by_index: bool,
    calc_type_str: str,
) -> None:
    """Execute the calculation and display results.

    :param calculator: Calculator instance
    :type calculator: Any
    :param input_value: Input value for calculation
    :type input_value: int
    :param use_by_index: Whether using --index mode
    :type use_by_index: bool
    :param calc_type_str: Calculator type string
    :type calc_type_str: str
    :raises typer.Exit: On any error during calculation
    """
    result, execution_time, ram_usage = _measure_calculation(
        calculator, input_value, use_by_index
    )
    _display_calculation_results(
        result, execution_time, ram_usage, calc_type_str
    )


def _should_run_estimation(
    benchmark: bool, dry_run: bool, needs_automatic_estimation: bool
) -> bool:
    """Determine if estimation should be run.

    :param benchmark: Whether benchmark flag is set
    :type benchmark: bool
    :param dry_run: Whether dry-run flag is set
    :type dry_run: bool
    :param needs_automatic_estimation: Whether auto-estimation triggered
    :type needs_automatic_estimation: bool
    :return: True if estimation should run
    :rtype: bool
    """
    return benchmark or dry_run or needs_automatic_estimation


def _run_estimation_workflow(
    estimator: Estimator,
    calculator: Any,
    request: CalculationRequest,
    context: EstimationContext,
) -> None:
    """Run complete estimation workflow.

    :param estimator: Estimator instance
    :type estimator: Estimator
    :param calculator: Calculator instance
    :type calculator: Any
    :param request: Calculation request parameters
    :type request: CalculationRequest
    :param context: Estimation context with flags
    :type context: EstimationContext
    """
    _run_benchmark_if_needed(
        estimator,
        calculator,
        request.estimator_calc_type,
        request.use_by_index,
    )

    _handle_estimation(
        estimator,
        request.input_value,
        request.estimator_calc_type,
        context,
    )


@app.command()
def main(  # pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments
    calculator_type: CalculatorType = typer.Argument(
        ..., help="Calculator type: prime, fib, or fact"
    ),
    index: Optional[int] = typer.Option(
        None, "--index", "-i", help="Calculate by index (nth number)"
    ),
    min_digits: Optional[int] = typer.Option(
        None,
        "--min-digits",
        "-d",
        help="Calculate by minimum digits",
    ),
    benchmark: bool = typer.Option(
        False, "--benchmark", help="Run estimation benchmark"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Return estimated time without calculating",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Abort if estimated time exceeds limit",
    ),
) -> None:
    """Calculate large numbers with absolute precision.

    Examples:
        py_mega_calc fib --index 100
        py_mega_calc prime --min-digits 10
        py_mega_calc fact --index 50 --benchmark

    :param calculator_type: Type of calculator to use
    :type calculator_type: CalculatorType
    :param index: Index value (nth number)
    :type index: Optional[int]
    :param min_digits: Minimum number of digits
    :type min_digits: Optional[int]
    :param benchmark: Whether to run benchmark
    :type benchmark: bool
    :param dry_run: Whether to only estimate (no calculation)
    :type dry_run: bool
    :param strict: Whether to abort if time exceeds limit
    :type strict: bool
    """
    _validate_inputs(index, min_digits)

    calculator, calc_type_str, estimator_calc_type = (
        _initialize_calculator(calculator_type)
    )

    input_value = index if index is not None else min_digits
    use_by_index = index is not None

    estimated_digits = estimate_digit_count(
        calc_type_str, input_value, use_by_index
    )
    needs_automatic_estimation = (
        estimated_digits > LARGE_DIGIT_THRESHOLD
    )

    context = EstimationContext(
        needs_automatic_estimation=needs_automatic_estimation,
        estimated_digits=estimated_digits,
        benchmark=benchmark,
        dry_run=dry_run,
        strict=strict,
    )

    request = CalculationRequest(
        input_value=input_value,
        estimator_calc_type=estimator_calc_type,
        use_by_index=use_by_index,
    )

    if _should_run_estimation(benchmark, dry_run, needs_automatic_estimation):
        estimator = Estimator()
        _run_estimation_workflow(
            estimator,
            calculator,
            request,
            context,
        )

        if dry_run:
            typer.echo("Dry run: No calculation performed.")
            return

    _execute_calculation(
        calculator, input_value, use_by_index, calc_type_str
    )


def format_result(
    result: int, max_chars: int = DEFAULT_MAX_DISPLAY_CHARS
) -> str:
    """Format calculation result for console output.

    :param result: The calculated number
    :type result: int
    :param max_chars: Maximum characters to display
    :type max_chars: int
    :return: Formatted string with result (truncated if necessary)
    :rtype: str
    """
    result_str = str(result)
    digit_count = len(result_str)

    if len(result_str) <= max_chars:
        return f"Result ({digit_count} digits):\n{result_str}"

    half = max_chars // 2
    return (
        f"Result ({digit_count} digits, truncated):\n"
        f"{result_str[:half]}...{result_str[-half:]}"
    )


def format_metadata(execution_time: float, ram_usage_mb: float) -> str:
    """Format metadata for output.

    :param execution_time: Execution time in seconds
    :type execution_time: float
    :param ram_usage_mb: Peak RAM usage in MB
    :type ram_usage_mb: float
    :return: Formatted metadata string
    :rtype: str
    """
    return (
        f"\nMetadata:\n  Execution time: {execution_time:.3f} seconds\n"
        f"  Peak RAM usage: {ram_usage_mb:.2f} MB"
    )


def write_result_to_file(
    result: int,
    calc_type: str,
    execution_time: Optional[float] = None,
    ram_usage_mb: Optional[float] = None,
    output_dir: str = "results",
) -> str:
    """Write calculation result to file.

    :param result: The calculated number
    :type result: int
    :param calc_type: Calculator type (prime/fib/fact)
    :type calc_type: str
    :param execution_time: Execution time in seconds (optional)
    :type execution_time: Optional[float]
    :param ram_usage_mb: Peak RAM usage in MB (optional)
    :type ram_usage_mb: Optional[float]
    :param output_dir: Output directory (default: "results")
    :type output_dir: str
    :return: Path to the written file
    :rtype: str
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{calc_type}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("Calculation Result\n")
        f.write(f"Type: {calc_type}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        result_str = str(result)
        f.write(f"\nResult ({len(result_str)} digits):\n")
        f.write(result_str)
        f.write("\n")

        if execution_time is not None:
            f.write(f"\nExecution time: {execution_time:.3f} seconds\n")
        if ram_usage_mb is not None:
            f.write(f"Peak RAM usage: {ram_usage_mb:.2f} MB\n")

    return filepath


def _estimate_fibonacci_digits(n: int) -> int:
    """Estimate digits in the nth Fibonacci number.

    Uses Binet's formula approximation.

    :param n: Fibonacci index
    :type n: int
    :return: Estimated digit count
    :rtype: int
    """
    phi = (1 + math.sqrt(5)) / 2
    log10_phi = math.log10(phi)
    log10_sqrt5 = math.log10(math.sqrt(5))
    estimated_digits = int(n * log10_phi - log10_sqrt5 + 1)
    return max(1, estimated_digits)


def _estimate_factorial_digits(n: int) -> int:
    """Estimate digits in n! (factorial).

    Uses Stirling's approximation.

    :param n: Factorial input
    :type n: int
    :return: Estimated digit count
    :rtype: int
    """
    if n in (0, 1):
        return 1

    log10_n = math.log10(n)
    log10_e = math.log10(math.e)
    log10_term = math.log10(math.sqrt(2 * math.pi * n))
    estimated_digits = int(
        n * log10_n - n * log10_e + log10_term + 1
    )
    return max(1, estimated_digits)


def _estimate_prime_digits(n: int) -> int:
    """Estimate digits in the nth prime number.

    Uses prime number theorem approximation.

    :param n: Prime index
    :type n: int
    :return: Estimated digit count
    :rtype: int
    """
    if n == 1:
        return 1

    ln_n = math.log(n)
    if ln_n > 0:
        estimated_prime = n * ln_n + n * math.log(ln_n)
    else:
        estimated_prime = n

    estimated_digits = int(math.log10(max(2, estimated_prime)) + 1)
    return max(1, estimated_digits)


def estimate_digit_count(
    calc_type: str, input_value: int, use_by_index: bool
) -> int:
    """Estimate the number of digits the result will have.

    Uses mathematical approximations to estimate digit count without
    performing the full calculation.

    :param calc_type: Calculator type ('fib', 'fact', 'prime')
    :type calc_type: str
    :param input_value: Input value (index or min_digits)
    :type input_value: int
    :param use_by_index: True if using --index, False if --min-digits
    :type use_by_index: bool
    :return: Estimated number of digits
    :rtype: int
    """
    if not use_by_index:
        return input_value

    estimators = {
        "fib": _estimate_fibonacci_digits,
        "fact": _estimate_factorial_digits,
        "prime": _estimate_prime_digits,
    }

    estimator = estimators.get(calc_type)
    return estimator(input_value) if estimator else 1


if __name__ == "__main__":
    app()
