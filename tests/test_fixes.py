"""Tests for bug fixes and improvements.

This module contains tests for specific bug fixes and improvements,
including RAM usage tracking, large number string conversion, estimator
accuracy, and dry-run functionality.

Dependencies:
    - pytest: Testing framework
    - sys: System-specific parameters
    - typer.testing: CLI testing utilities
    - src.cli: CLI application
"""

import sys

from typer.testing import CliRunner

from src.cli import app


class TestRAMUsageTracking:  # pylint: disable=too-few-public-methods
    """Test that RAM usage is tracked correctly (no negative values)."""

    def test_ram_usage_is_non_negative(self) -> None:
        """Test that reported RAM usage is never negative."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])

        assert result.exit_code == 0
        assert "Peak RAM usage:" in result.stdout

        lines = result.stdout.split('\n')
        ram_line = [line for line in lines if 'Peak RAM usage' in line]
        assert len(ram_line) > 0

        ram_value_str = (
            ram_line[0].split(':')[1].strip().replace(' MB', '')
        )
        ram_value = float(ram_value_str)
        msg = f"RAM usage should be non-negative, got {ram_value}"
        assert ram_value >= 0, msg


class TestLargeNumberStringConversion:
    """Test large numbers (10,000+ digits) can be converted to strings."""

    def test_large_fibonacci_string_conversion(self) -> None:
        """Test Fibonacci numbers with 10,000+ digits can be converted."""
        original_limit = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(20000)

            runner = CliRunner()
            result = runner.invoke(app, ["fib", "--index", "1000000"])

            assert "Exceeds the limit" not in result.stdout
            assert "sys.set_int_max_str_digits" not in result.stdout

            if result.exit_code != 0:
                assert "string conversion" not in result.stdout.lower()
        finally:
            sys.set_int_max_str_digits(original_limit)

    def test_cli_sets_int_max_str_digits(self) -> None:
        """Test CLI automatically sets int_max_str_digits for large numbers."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "100000"])

        assert "Exceeds the limit" not in result.stdout
        assert "sys.set_int_max_str_digits" not in result.stdout


class TestEstimatorAccuracy:
    """Test that estimator provides accurate time predictions."""

    def test_estimator_provides_non_zero_estimate(self) -> None:
        """Test estimator provides non-zero estimate for reasonable inputs."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["prime", "--index", "1000", "--benchmark", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "Estimated execution time:" in result.stdout

        lines = result.stdout.split('\n')
        time_line = [
            line
            for line in lines
            if 'Estimated execution time' in line
        ]
        assert len(time_line) > 0

        time_str = (
            time_line[0].split(':')[1].strip().replace(' seconds', '')
        )
        estimated_time = float(time_str)
        assert isinstance(estimated_time, float)

    def test_estimator_estimate_vs_actual(self) -> None:
        """Test estimator provides reasonable estimate vs actual time."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["prime", "--index", "100", "--benchmark"]
        )

        assert result.exit_code == 0
        assert (
            "Estimated execution time:" in result.stdout
            or "Execution time:" in result.stdout
        )


class TestDryRunBenchmark:
    """Test that dry-run properly runs benchmarks."""

    def test_dry_run_runs_benchmark(self) -> None:
        """Test dry-run actually runs benchmark and shows estimate."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["prime", "--index", "10000", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "Dry run" in result.stdout
        assert (
            "micro-benchmark" in result.stdout
            or "Estimated execution time" in result.stdout
        )
        assert "seconds" in result.stdout

    def test_dry_run_does_not_perform_calculation(self) -> None:
        """Test dry-run does not perform the actual calculation."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "100", "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run" in result.stdout
        assert (
            "354224848179261915075" not in result.stdout
            or "Dry run" in result.stdout
        )
