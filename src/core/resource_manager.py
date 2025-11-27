"""Resource management decorators for time and RAM monitoring.

This module provides decorators to monitor memory usage and execution time,
raising appropriate exceptions when resource limits are exceeded.

Dependencies:
    - functools: Function wrapping utilities
    - psutil: System and process utilities
    - time: Time measurement
    - threading: Thread management for timeout monitoring
    - src.core.exceptions: ResourceExhaustedError, TimeoutError
    - src.config: MAX_MEMORY_BYTES, MAX_TIME_SECONDS constants
"""

import functools
import threading
import time
from typing import Any, Callable

import psutil

from src.config import MAX_MEMORY_BYTES, MAX_TIME_SECONDS
from src.core.exceptions import (
    ResourceExhaustedError,
    TimeoutError as CalculationTimeoutError,
)


def _check_memory_limit() -> None:
    """Check if current memory usage exceeds limit.

    :raises ResourceExhaustedError: If memory usage exceeds 24GB limit
    """
    process = psutil.Process()
    memory_info = process.memory_info()

    if memory_info.rss > MAX_MEMORY_BYTES:
        usage_gb = memory_info.rss / (1024 ** 3)
        raise ResourceExhaustedError(
            f"Memory limit of 24GB exceeded. "
            f"Current usage: {usage_gb:.2f}GB"
        )


def monitor_memory(func: Callable) -> Callable:
    """Decorator to monitor memory usage.

    Checks memory usage before and after function execution.
    Raises ResourceExhaustedError if memory usage exceeds MAX_MEMORY_BYTES
    (24GB).

    :param func: The function to monitor
    :type func: Callable
    :return: Wrapped function with memory monitoring
    :rtype: Callable
    :raises ResourceExhaustedError: If memory usage exceeds 24GB limit
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        _check_memory_limit()
        result = func(*args, **kwargs)
        _check_memory_limit()
        return result

    return wrapper


def _run_with_timeout(
    func: Callable, args: tuple, kwargs: dict, timeout: float
) -> Any:
    """Run function in a thread with timeout monitoring.

    :param func: Function to execute
    :type func: Callable
    :param args: Positional arguments
    :type args: tuple
    :param kwargs: Keyword arguments
    :type kwargs: dict
    :param timeout: Timeout in seconds
    :type timeout: float
    :return: Function result
    :rtype: Any
    :raises CalculationTimeoutError: If execution exceeds timeout
    :raises Exception: Any exception raised by the function
    """
    result_container: dict[str, Any] = {
        'value': None,
        'exception': None,
    }

    def target() -> None:
        try:
            result_container['value'] = func(*args, **kwargs)
        except BaseException as e:  # pylint: disable=broad-exception-caught
            # Intentionally catch all exceptions to propagate them
            # from the thread to the main thread
            result_container['exception'] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        raise CalculationTimeoutError(
            f"Calculation exceeded {MAX_TIME_SECONDS} second "
            f"({MAX_TIME_SECONDS // 60} minute) timeout."
        )

    exception = result_container['exception']
    if exception is not None:
        raise exception

    return result_container['value']


def monitor_timeout(func: Callable) -> Callable:
    """Decorator to monitor execution time.

    Checks execution time and raises CalculationTimeoutError if function
    execution exceeds MAX_TIME_SECONDS (300 seconds / 5 minutes).

    :param func: The function to monitor
    :type func: Callable
    :return: Wrapped function with timeout monitoring
    :rtype: Callable
    :raises CalculationTimeoutError: If execution time exceeds 5 minute limit
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = _run_with_timeout(func, args, kwargs, MAX_TIME_SECONDS)
        elapsed_time = time.time() - start_time

        if elapsed_time > MAX_TIME_SECONDS:
            raise CalculationTimeoutError(
                f"Calculation exceeded {MAX_TIME_SECONDS} second "
                f"({MAX_TIME_SECONDS // 60} minute) timeout. "
                f"Elapsed time: {elapsed_time:.2f} seconds"
            )

        return result

    return wrapper
