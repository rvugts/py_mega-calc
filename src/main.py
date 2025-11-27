"""Entry point for py_mega_calc application.

This module provides the main entry point for the py_mega_calc CLI application.

Dependencies:
    - src.cli: CLI application instance
"""

from src.cli import app


def main() -> None:
    """Main entry point for the application.

    :return: None
    :rtype: None
    """
    app()


if __name__ == "__main__":
    main()
