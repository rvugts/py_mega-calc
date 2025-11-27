"""End-to-end integration tests for py_mega_calc.

This module contains end-to-end integration tests that verify complete
workflows from CLI input through calculator execution to output generation.

Dependencies:
    - pytest: Testing framework
    - os: File system operations
    - typer.testing: CLI testing utilities
    - src.cli: CLI application
"""

import os

from typer.testing import CliRunner

from src.cli import app


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows: CLI → Calculator → Output."""

    def test_fibonacci_by_index_workflow(self) -> None:
        """Test complete workflow for Fibonacci calculation by index."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])

        assert result.exit_code == 0
        assert "55" in result.stdout
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout
        assert "Full result saved to" in result.stdout

    def test_fibonacci_by_digits_workflow(self) -> None:
        """Test complete workflow for Fibonacci calculation by digits."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--min-digits", "2"])

        assert result.exit_code == 0
        assert "Result" in result.stdout
        assert "digits" in result.stdout
        assert "11" in result.stdout or "13" in result.stdout

    def test_factorial_by_index_workflow(self) -> None:
        """Test complete workflow for Factorial calculation by index."""
        runner = CliRunner()
        result = runner.invoke(app, ["fact", "--index", "5"])

        assert result.exit_code == 0
        assert "120" in result.stdout
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout

    def test_factorial_by_digits_workflow(self) -> None:
        """Test complete workflow for Factorial calculation by digits."""
        runner = CliRunner()
        result = runner.invoke(app, ["fact", "--min-digits", "3"])

        assert result.exit_code == 0
        assert "Result" in result.stdout
        assert "digits" in result.stdout

    def test_prime_by_index_workflow(self) -> None:
        """Test complete workflow for Prime calculation by index."""
        runner = CliRunner()
        result = runner.invoke(app, ["prime", "--index", "10"])

        assert result.exit_code == 0
        assert "29" in result.stdout
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout

    def test_prime_by_digits_workflow(self) -> None:
        """Test complete workflow for Prime calculation by digits."""
        runner = CliRunner()
        result = runner.invoke(app, ["prime", "--min-digits", "3"])

        assert result.exit_code == 0
        assert "101" in result.stdout
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout

    def test_workflow_with_benchmark_flag(self) -> None:
        """Test complete workflow with --benchmark flag."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["fib", "--index", "100", "--benchmark"]
        )

        assert result.exit_code == 0
        assert (
            "Estimated execution time" in result.stdout
            or "micro-benchmark" in result.stdout
        )
        assert "Result" in result.stdout

    def test_workflow_with_dry_run_flag(self) -> None:
        """Test complete workflow with --dry-run flag."""
        runner = CliRunner()
        result = runner.invoke(
            app, ["fib", "--index", "1000", "--dry-run"]
        )

        assert result.exit_code == 0
        assert (
            "Estimated execution time" in result.stdout
            or "micro-benchmark" in result.stdout
        )
        assert "Dry run" in result.stdout

    def test_workflow_with_strict_flag(self) -> None:
        """Test complete workflow with --strict flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10", "--strict"])

        assert result.exit_code == 0
        assert "Result" in result.stdout

    def test_workflow_file_output(self) -> None:
        """Test that workflow creates output file."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])

        assert result.exit_code == 0
        assert "Full result saved to" in result.stdout

        filepath_lines = [
            line
            for line in result.stdout.split('\n')
            if 'Full result saved to' in line
        ]
        if filepath_lines:
            filepath = filepath_lines[0].split(': ')[-1].strip()
            assert os.path.exists(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "55" in content or "Result" in content

    def test_workflow_error_handling(self) -> None:
        """Test that workflow handles errors gracefully."""
        runner = CliRunner()

        result = runner.invoke(app, ["fib", "--index", "-1"])
        assert result.exit_code != 0
        error_output = result.stdout + result.stderr
        assert "Error" in error_output or "error" in error_output.lower()

        result = runner.invoke(app, ["fib"])
        assert result.exit_code != 0

    def test_workflow_with_all_flags(self) -> None:
        """Test complete workflow with all flags enabled."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "fib",
                "--index",
                "50",
                "--benchmark",
                "--strict",
            ],
        )

        assert result.exit_code == 0
        assert "Result" in result.stdout

    def test_workflow_large_calculation(self) -> None:
        """Test workflow with larger calculation."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "100"])

        assert result.exit_code == 0
        assert "Result" in result.stdout
        assert "Metadata" in result.stdout

    def test_workflow_output_formatting(self) -> None:
        """Test that workflow formats output correctly."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "10"])

        assert result.exit_code == 0
        assert "Result" in result.stdout
        assert "digits" in result.stdout
        assert "Metadata" in result.stdout
        assert "Execution time" in result.stdout
        assert "RAM usage" in result.stdout or "Peak RAM" in result.stdout
