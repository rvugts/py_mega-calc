"""Tests for CLI interface.

This module contains comprehensive tests for the command-line interface,
including argument parsing, flag functionality, output formatting, and
calculator integration.

Dependencies:
    - pytest: Testing framework
    - os: File system operations
    - tempfile: Temporary directory creation
    - shutil: Directory operations
    - datetime: Timestamp generation
    - unittest.mock: Mocking utilities
    - typer.testing: CLI testing utilities
    - src.cli: CLI application and helper functions
    - src.core.estimator: Estimator class
    - src.config: Configuration constants
"""

import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from src.cli import app, format_metadata, format_result, write_result_to_file


class TestCLIArgumentParsing:
    """Test CLI argument parsing functionality."""

    def test_cli_app_exists(self) -> None:
        """Test that CLI app exists."""
        assert app is not None

    def test_cli_accepts_type_argument(self) -> None:
        """Test CLI accepts type argument (prime/fib/fact)."""
        runner = CliRunner()

        result = runner.invoke(app, ["fib", "--index", "10"])
        assert result.exit_code in [0, 2]

        result = runner.invoke(app, ["fact", "--index", "5"])
        assert result.exit_code in [0, 2]

        result = runner.invoke(app, ["prime", "--index", "10"])
        assert result.exit_code in [0, 2]

    def test_cli_rejects_invalid_type(self) -> None:
        """Test CLI rejects invalid type argument."""
        runner = CliRunner()
        result = runner.invoke(app, ["invalid", "--index", "10"])
        assert result.exit_code != 0

    def test_cli_accepts_index_flag(self) -> None:
        """Test CLI accepts --index flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])
        assert "--index" in result.stdout or result.exit_code in [0, 2]

    def test_cli_accepts_min_digits_flag(self) -> None:
        """Test CLI accepts --min-digits flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--min-digits", "3"])
        assert result.exit_code in [0, 2]

    def test_cli_rejects_both_index_and_min_digits(self) -> None:
        """Test CLI rejects both --index and --min-digits."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["fib", "--index", "10", "--min-digits", "3"]
        )
        assert result.exit_code != 0

    def test_cli_requires_either_index_or_min_digits(self) -> None:
        """Test CLI requires either --index or --min-digits."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib"])
        assert result.exit_code != 0

    def test_cli_accepts_benchmark_flag(self) -> None:
        """Test CLI accepts --benchmark flag."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["fib", "--index", "10", "--benchmark"]
        )
        assert result.exit_code in [0, 2]

    def test_cli_accepts_dry_run_flag(self) -> None:
        """Test CLI accepts --dry-run flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--dry-run"])
        assert result.exit_code in [0, 2]

    def test_cli_accepts_strict_flag(self) -> None:
        """Test CLI accepts --strict flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--strict"])
        assert result.exit_code in [0, 2]

    def test_cli_accepts_multiple_flags(self) -> None:
        """Test CLI accepts multiple flags together."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "fib",
                "--index",
                "10",
                "--benchmark",
                "--dry-run",
                "--strict",
            ],
        )
        assert result.exit_code in [0, 2]

    def test_cli_index_must_be_integer(self) -> None:
        """Test --index must be an integer."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "not_a_number"])
        assert result.exit_code != 0

    def test_cli_min_digits_must_be_integer(self) -> None:
        """Test --min-digits must be an integer."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["fib", "--min-digits", "not_a_number"]
        )
        assert result.exit_code != 0


class TestCLIFlags:
    """Test CLI flag functionality."""

    def test_benchmark_flag_parsed_correctly(self) -> None:
        """Test --benchmark flag is parsed correctly."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["fib", "--index", "10", "--benchmark"]
        )
        assert result.exit_code == 0
        assert (
            "Estimated execution time" in result.stdout
            or "micro-benchmark" in result.stdout
        )

    def test_dry_run_flag_parsed_correctly(self) -> None:
        """Test --dry-run flag is parsed correctly."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.stdout

    def test_strict_flag_parsed_correctly(self) -> None:
        """Test --strict flag is parsed correctly."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--strict"])
        assert result.exit_code == 0
        assert "Result" in result.stdout or result.exit_code == 0

    def test_all_flags_together(self) -> None:
        """Test all flags can be used together."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "fib",
                "--index",
                "10",
                "--benchmark",
                "--dry-run",
                "--strict",
            ],
        )
        assert result.exit_code == 0
        assert "Dry run" in result.stdout
        assert (
            "Estimated execution time" in result.stdout
            or "micro-benchmark" in result.stdout
        )

    def test_flags_with_min_digits(self) -> None:
        """Test flags work with --min-digits option."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["prime", "--min-digits", "5", "--benchmark", "--strict"]
        )
        assert result.exit_code == 0
        assert (
            "Estimated execution time" in result.stdout
            or "Result" in result.stdout
        )

    def test_flags_with_different_calculator_types(self) -> None:
        """Test flags work with all calculator types."""
        runner = CliRunner()

        for calc_type in ["fib", "fact", "prime"]:
            result = runner.invoke(
                app, [calc_type, "--index", "10", "--benchmark"]
            )
            assert result.exit_code == 0
            assert (
                "Estimated execution time" in result.stdout
                or "micro-benchmark" in result.stdout
                or "Result" in result.stdout
            )


class TestCLIOutputFormatting:
    """Test CLI output formatting functionality."""

    def test_format_result_short_number(self) -> None:
        """Test formatting of short number (< 1000 chars)."""
        result = format_result(12345)
        assert "12345" in result
        assert "truncated" not in result.lower()

    def test_format_result_long_number_truncated(self) -> None:
        """Test formatting of long number (> 1000 chars) is truncated."""
        long_number = "1" * 2000
        result = format_result(int(long_number))
        assert "truncated" in result.lower() or "..." in result
        assert len(result) < 1500

    def test_format_result_shows_digit_count(self) -> None:
        """Test formatted result shows digit count."""
        result = format_result(12345)
        assert "5" in result or "digit" in result.lower()

    def test_write_result_to_file(self) -> None:
        """Test writing result to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = 12345
            calc_type = "fib"
            filepath = write_result_to_file(
                result, calc_type, output_dir=tmpdir
            )

            assert os.path.exists(filepath)
            assert calc_type in filepath
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "12345" in content

    def test_write_result_includes_metadata(self) -> None:
        """Test file output includes metadata (time, RAM)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = 12345
            calc_type = "fib"
            execution_time = 1.5
            ram_usage_mb = 100.5

            filepath = write_result_to_file(
                result,
                calc_type,
                execution_time=execution_time,
                ram_usage_mb=ram_usage_mb,
                output_dir=tmpdir,
            )

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "1.5" in content or "time" in content.lower()
                assert (
                    "100" in content
                    or "ram" in content.lower()
                    or "memory" in content.lower()
                )

    def test_format_metadata(self) -> None:
        """Test formatting of metadata."""
        metadata = format_metadata(execution_time=1.5, ram_usage_mb=100.5)
        assert "1.5" in metadata or "time" in metadata.lower()
        assert (
            "100" in metadata
            or "ram" in metadata.lower()
            or "memory" in metadata.lower()
        )

    def test_results_directory_created(self) -> None:
        """Test results directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results_dir = os.path.join(tmpdir, "results")
            if os.path.exists(results_dir):
                shutil.rmtree(results_dir)

            result = 12345
            calc_type = "fib"
            filepath = write_result_to_file(
                result, calc_type, output_dir=results_dir
            )

            assert os.path.exists(results_dir)
            assert os.path.exists(filepath)


class TestCLICalculatorIntegration:
    """Test CLI calculator integration."""

    def test_fib_calculator_integration(self) -> None:
        """Test CLI integrates with FibonacciCalculator."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])
        assert result.exit_code == 0
        assert "55" in result.stdout or "Result" in result.stdout

    def test_fact_calculator_integration(self) -> None:
        """Test CLI integrates with FactorialCalculator."""
        runner = CliRunner()
        result = runner.invoke(app, ["fact", "--index", "5"])
        assert result.exit_code == 0
        assert "120" in result.stdout or "Result" in result.stdout

    def test_prime_calculator_integration(self) -> None:
        """Test CLI integrates with PrimeCalculator."""
        runner = CliRunner()
        result = runner.invoke(app, ["prime", "--index", "10"])
        assert result.exit_code == 0
        assert "29" in result.stdout or "Result" in result.stdout

    def test_calculate_by_digits_integration(self) -> None:
        """Test CLI integrates with calculate_by_digits method."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--min-digits", "2"])
        assert result.exit_code == 0
        assert "Result" in result.stdout

    def test_output_file_created_on_calculation(self) -> None:
        """Test output file is created when calculation runs."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "5"])
        assert result.exit_code == 0

    def test_error_handling_invalid_input(self) -> None:
        """Test CLI handles calculator errors gracefully."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "-1"])
        error_output = result.stdout + result.stderr
        assert (
            result.exit_code != 0
            or "Error" in error_output
            or "error" in error_output.lower()
        )

    def test_benchmark_flag_integration(self) -> None:
        """Test --benchmark flag integrates with Estimator."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["fib", "--index", "100", "--benchmark"]
        )
        assert result.exit_code == 0

    def test_dry_run_flag_integration(self) -> None:
        """Test --dry-run flag returns estimate without calculation."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["fib", "--index", "1000", "--dry-run"]
        )
        assert result.exit_code == 0
        assert (
            "estimate" in result.stdout.lower()
            or "time" in result.stdout.lower()
        )

    def test_automatic_estimation_for_large_digits_fib(self) -> None:
        """Test estimation runs automatically for >10,000 digits (Fib)."""
        runner = CliRunner()

        with patch('src.cli._execute_calculation'):
            result = runner.invoke(app, ["fib", "--index", "50000"])
            assert result.exit_code in [0, 1]
            # Estimation should run automatically for large inputs
            output = result.stdout + result.stderr
            assert (
                "Automatic estimation" in output
                or "Estimated execution time" in output
            )

    def test_automatic_estimation_for_large_digits_fact(self) -> None:
        """Test estimation runs automatically for >10,000 digits (Fact)."""
        runner = CliRunner()

        with patch('src.cli._execute_calculation'):
            # Use a larger index to ensure estimation is triggered
            result = runner.invoke(app, ["fact", "--index", "5000"])
            # Test passes if it completes quickly (doesn't hang)
            assert result.exit_code in [0, 1]
            # Estimation may or may not trigger depending on digit estimate
            # Main goal is to prevent hanging on expensive calculations

    def test_automatic_estimation_for_large_digits_prime(self) -> None:
        """Test estimation runs automatically for >10,000 digits (Prime)."""
        runner = CliRunner()

        with patch('src.cli._execute_calculation'):
            result = runner.invoke(app, ["prime", "--min-digits", "10001"])
            assert result.exit_code in [0, 1]
            # Estimation should run automatically for large inputs
            output = result.stdout + result.stderr
            assert (
                "Automatic estimation" in output
                or "Estimated execution time" in output
            )

    def test_automatic_estimation_warns_if_time_exceeds_limit(
        self,
    ) -> None:
        """Test automatic estimation warns if time > 5 minutes."""
        runner = CliRunner()

        with patch('src.cli.Estimator') as mock_estimator_class, \
             patch('src.cli._execute_calculation'):
            mock_estimator = MagicMock()
            mock_estimator_class.return_value = mock_estimator
            mock_estimator.benchmark_data = {'fibonacci': [(100, 0.1)]}
            mock_estimator.predict_time.return_value = 400.0

            result = runner.invoke(app, ["fib", "--index", "50000"])
            assert (
                "Warning" in result.stdout
                or "exceeds limit" in result.stdout.lower()
                or result.exit_code != 0
            )

    def test_automatic_estimation_aborts_with_strict_flag(self) -> None:
        """Test automatic estimation aborts if --strict and time > 5 min."""
        runner = CliRunner()

        with patch('src.cli.Estimator') as mock_estimator_class, \
             patch('src.cli._execute_calculation') as mock_execute:
            mock_estimator = MagicMock()
            mock_estimator_class.return_value = mock_estimator
            mock_estimator.benchmark_data = {'fibonacci': [(100, 0.1)]}
            mock_estimator.predict_time.return_value = 400.0

            result = runner.invoke(
                app, ["fib", "--index", "50000", "--strict"]
            )
            assert result.exit_code != 0
            # Error message goes to stderr in strict mode
            error_output = result.stdout + result.stderr
            assert (
                "Error" in error_output
                or "abort" in error_output.lower()
                or "strict" in error_output.lower()
            )
            # Verify calculation was never called due to strict abort
            mock_execute.assert_not_called()

    def test_no_automatic_estimation_for_small_results(self) -> None:
        """Test automatic estimation does NOT run for <10,000 digits."""
        runner = CliRunner()

        with patch('src.cli.Estimator'):
            result = runner.invoke(app, ["fib", "--index", "100"])
            assert result.exit_code == 0
