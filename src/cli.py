"""CLI interface for py_mega_calc using Typer."""

import os
import time
import typer
import psutil
from typing import Optional
from enum import Enum
from datetime import datetime
from pathlib import Path

from src.calculators.fibonacci import FibonacciCalculator
from src.calculators.factorial import FactorialCalculator
from src.calculators.primes import PrimeCalculator
from src.core.estimator import Estimator
from src.core.exceptions import InputError, CalculationTooLargeError, ResourceExhaustedError, TimeoutError
from src.config import MAX_TIME_SECONDS

app = typer.Typer()


class CalculatorType(str, Enum):
    """Supported calculator types."""
    prime = "prime"
    fib = "fib"
    fact = "fact"


@app.command()
def main(
    calculator_type: CalculatorType = typer.Argument(..., help="Calculator type: prime, fib, or fact"),
    index: Optional[int] = typer.Option(None, "--index", "-i", help="Calculate by index (nth number)"),
    min_digits: Optional[int] = typer.Option(None, "--min-digits", "-d", help="Calculate by minimum digits"),
    benchmark: bool = typer.Option(False, "--benchmark", help="Run estimation benchmark"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Return estimated time without calculating"),
    strict: bool = typer.Option(False, "--strict", help="Abort if estimated time exceeds limit"),
) -> None:
    """Calculate large numbers (Primes, Fibonacci, Factorials) with absolute precision.
    
    Examples:
        py_mega_calc fib --index 100
        py_mega_calc prime --min-digits 10
        py_mega_calc fact --index 50 --benchmark
    """
    # Validate mutually exclusive options
    if index is not None and min_digits is not None:
        typer.echo("Error: --index and --min-digits are mutually exclusive. Use only one.", err=True)
        raise typer.Exit(code=1)
    
    if index is None and min_digits is None:
        typer.echo("Error: Either --index or --min-digits must be provided.", err=True)
        raise typer.Exit(code=1)
    
    # Validate input values
    if index is not None and index < 0:
        typer.echo("Error: --index must be a non-negative integer.", err=True)
        raise typer.Exit(code=1)
    
    if min_digits is not None and min_digits <= 0:
        typer.echo("Error: --min-digits must be a positive integer.", err=True)
        raise typer.Exit(code=1)
    
    # Initialize calculator
    if calculator_type == CalculatorType.fib:
        calculator = FibonacciCalculator()
        calc_type_str = "fib"
    elif calculator_type == CalculatorType.fact:
        calculator = FactorialCalculator()
        calc_type_str = "fact"
    elif calculator_type == CalculatorType.prime:
        calculator = PrimeCalculator()
        calc_type_str = "prime"
    else:
        typer.echo(f"Error: Unknown calculator type: {calculator_type}", err=True)
        raise typer.Exit(code=1)
    
    # Initialize estimator if needed
    estimator = None
    if benchmark or dry_run:
        estimator = Estimator()
    
    # Determine input value and calculation type
    if index is not None:
        input_value = index
        use_by_index = True
    else:
        input_value = min_digits
        use_by_index = False
    
    # Estimate time if requested
    if dry_run or benchmark:
        if estimator:
            # Run micro-benchmark if needed
            if calc_type_str not in estimator.benchmark_data or not estimator.benchmark_data[calc_type_str]:
                typer.echo("Running micro-benchmark...")
                # Run small benchmarks
                test_inputs = [1, 5, 10, 20, 50]
                if use_by_index:
                    def calc_func(n: int):
                        return calculator.calculate_by_index(n)
                else:
                    def calc_func(d: int):
                        return calculator.calculate_by_digits(d)
                benchmark_results = estimator.run_micro_benchmark(calc_func, test_inputs)
                # Store results in benchmark_data
                estimator.benchmark_data[calc_type_str] = benchmark_results
            
            # Predict time
            estimated_time = estimator.predict_time(input_value, calc_type_str)
            typer.echo(f"Estimated execution time: {estimated_time:.3f} seconds")
            
            if estimated_time > MAX_TIME_SECONDS:
                if strict:
                    typer.echo(f"Error: Estimated time ({estimated_time:.3f}s) exceeds limit ({MAX_TIME_SECONDS}s). Aborting (--strict).", err=True)
                    raise typer.Exit(code=1)
                else:
                    typer.echo(f"Warning: Estimated time ({estimated_time:.3f}s) exceeds limit ({MAX_TIME_SECONDS}s).", err=True)
            
            if dry_run:
                typer.echo("Dry run: No calculation performed.")
                return
    
    # Perform calculation
    try:
        start_time = time.perf_counter()
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        if use_by_index:
            result = calculator.calculate_by_index(input_value)
        else:
            result = calculator.calculate_by_digits(input_value)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        ram_usage = memory_after - memory_before
        
        # Format and display result
        formatted_result = format_result(result)
        typer.echo(formatted_result)
        
        # Display metadata
        metadata = format_metadata(execution_time, ram_usage)
        typer.echo(metadata)
        
        # Write to file
        filepath = write_result_to_file(
            result, calc_type_str,
            execution_time=execution_time,
            ram_usage_mb=ram_usage
        )
        typer.echo(f"\nFull result saved to: {filepath}")
        
    except InputError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    except CalculationTooLargeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    except ResourceExhaustedError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    except TimeoutError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(code=1)


def format_result(result: int, max_chars: int = 1000) -> str:
    """Format calculation result for console output.
    
    Args:
        result: The calculated number
        max_chars: Maximum characters to display (default 1000)
        
    Returns:
        Formatted string with result (truncated if necessary)
    """
    result_str = str(result)
    digit_count = len(result_str)
    
    if len(result_str) <= max_chars:
        return f"Result ({digit_count} digits):\n{result_str}"
    else:
        # Truncate and show first and last parts
        first_part = result_str[:max_chars // 2]
        last_part = result_str[-max_chars // 2:]
        return f"Result ({digit_count} digits, truncated):\n{first_part}...{last_part}"


def format_metadata(execution_time: float, ram_usage_mb: float) -> str:
    """Format metadata for output.
    
    Args:
        execution_time: Execution time in seconds
        ram_usage_mb: Peak RAM usage in MB
        
    Returns:
        Formatted metadata string
    """
    return f"\nMetadata:\n  Execution time: {execution_time:.3f} seconds\n  Peak RAM usage: {ram_usage_mb:.2f} MB"


def write_result_to_file(
    result: int,
    calc_type: str,
    execution_time: Optional[float] = None,
    ram_usage_mb: Optional[float] = None,
    output_dir: str = "results"
) -> str:
    """Write calculation result to file.
    
    Args:
        result: The calculated number
        calc_type: Calculator type (prime/fib/fact)
        execution_time: Execution time in seconds (optional)
        ram_usage_mb: Peak RAM usage in MB (optional)
        output_dir: Output directory (default: "results")
        
    Returns:
        Path to the written file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{calc_type}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # Write result and metadata
    with open(filepath, 'w') as f:
        f.write(f"Calculation Result\n")
        f.write(f"Type: {calc_type}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"\nResult ({len(str(result))} digits):\n")
        f.write(str(result))
        f.write("\n")
        
        if execution_time is not None:
            f.write(f"\nExecution time: {execution_time:.3f} seconds\n")
        if ram_usage_mb is not None:
            f.write(f"Peak RAM usage: {ram_usage_mb:.2f} MB\n")
    
    return filepath


if __name__ == "__main__":
    app()

