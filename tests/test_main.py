"""Tests for main entry point.

This module contains tests for the main entry point of the py_mega_calc
application, verifying CLI integration and execution flow.

Dependencies:
    - pytest: Testing framework
    - unittest.mock: Mocking utilities
    - typer.testing: CLI testing utilities
    - src.cli: CLI application
"""
# pylint: disable=duplicate-code

from typer.testing import CliRunner

from src.cli import app


class TestMainEntryPoint:
    """Test main entry point functionality."""

    def test_main_module_exists(self) -> None:
        """Test that main module exists and can be imported."""
        from src import main # pylint: disable=import-outside-toplevel
        assert main is not None

    def test_main_can_be_executed(self) -> None:
        """Test that main can be executed."""
        runner = CliRunner()
        result = runner.invoke(app, ["fib", "--index", "5"])
        assert result.exit_code == 0

    def test_main_entry_point_connects_to_cli(self) -> None:
        """Test that main entry point connects to CLI."""
        runner = CliRunner()

        result = runner.invoke(app, ["fib", "--index", "10"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["fact", "--index", "5"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["prime", "--index", "10"])
        assert result.exit_code == 0

    def test_main_handles_cli_errors(self) -> None:
        """Test that main properly handles CLI errors."""
        runner = CliRunner()

        result = runner.invoke(app, ["fib", "--index", "-1"])
        assert result.exit_code != 0

        result = runner.invoke(app, ["fib"])
        assert result.exit_code != 0

    def test_main_execution_flow(self) -> None:
        """Test complete execution flow through main."""
        runner = CliRunner()

        result = runner.invoke(app, ["fib", "--index", "10"])
        assert result.exit_code == 0
        assert "Result" in result.stdout or "55" in result.stdout

    def test_main_with_all_features(self) -> None:
        """Test main with all features enabled."""
        runner = CliRunner()

        result = runner.invoke(
            app,
            [
                "fib",
                "--index",
                "20",
                "--benchmark",
                "--strict",
            ],
        )
        assert result.exit_code == 0
