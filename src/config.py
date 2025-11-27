"""Configuration constants for py_mega_calc.

This module defines all configuration constants used throughout the application,
including resource limits, output settings, and estimation thresholds.

Dependencies:
    None (pure constants module)
"""

# Resource limits
MAX_MEMORY_GB: int = 24
MAX_MEMORY_BYTES: int = MAX_MEMORY_GB * 1024 * 1024 * 1024
MAX_TIME_SECONDS: int = 300  # 5 minutes

# Output settings
MAX_DISPLAY_CHARS: int = 1000
RESULTS_DIR: str = "results"

# Estimation thresholds
LARGE_DIGIT_THRESHOLD: int = 10000
