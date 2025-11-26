"""Resource management decorators for time and RAM monitoring."""

import functools
import psutil
import time
import threading
from typing import Callable, Any
from src.core.exceptions import ResourceExhaustedError, TimeoutError
from src.config import MAX_MEMORY_BYTES, MAX_TIME_SECONDS


def monitor_memory(func: Callable) -> Callable:
    """Decorator to monitor memory usage and raise ResourceExhaustedError if limit exceeded.
    
    Checks memory usage before and after function execution.
    Raises ResourceExhaustedError if memory usage exceeds MAX_MEMORY_BYTES (24GB).
    
    Args:
        func: The function to monitor
        
    Returns:
        Wrapped function with memory monitoring
        
    Raises:
        ResourceExhaustedError: If memory usage exceeds 24GB limit
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        if memory_info.rss > MAX_MEMORY_BYTES:
            raise ResourceExhaustedError(
                f"Memory limit of 24GB exceeded. Current usage: {memory_info.rss / (1024**3):.2f}GB"
            )
        
        result = func(*args, **kwargs)
        
        # Check memory again after execution
        memory_info = process.memory_info()
        if memory_info.rss > MAX_MEMORY_BYTES:
            raise ResourceExhaustedError(
                f"Memory limit of 24GB exceeded after execution. Current usage: {memory_info.rss / (1024**3):.2f}GB"
            )
        
        return result
    
    return wrapper


def monitor_timeout(func: Callable) -> Callable:
    """Decorator to monitor execution time and raise TimeoutError if limit exceeded.
    
    Checks execution time and raises TimeoutError if function execution exceeds
    MAX_TIME_SECONDS (300 seconds / 5 minutes).
    
    Args:
        func: The function to monitor
        
    Returns:
        Wrapped function with timeout monitoring
        
    Raises:
        TimeoutError: If execution time exceeds 5 minute limit
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        timeout_occurred = threading.Event()
        result_container = {'value': None, 'exception': None}
        
        def target():
            try:
                result_container['value'] = func(*args, **kwargs)
            except Exception as e:
                result_container['exception'] = e
        
        # Run function in a thread
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=MAX_TIME_SECONDS)
        
        elapsed_time = time.time() - start_time
        
        if thread.is_alive():
            # Thread is still running, timeout occurred
            raise TimeoutError(
                f"Calculation exceeded {MAX_TIME_SECONDS} second ({MAX_TIME_SECONDS // 60} minute) timeout. "
                f"Elapsed time: {elapsed_time:.2f} seconds"
            )
        
        if result_container['exception']:
            raise result_container['exception']
        
        if elapsed_time > MAX_TIME_SECONDS:
            raise TimeoutError(
                f"Calculation exceeded {MAX_TIME_SECONDS} second ({MAX_TIME_SECONDS // 60} minute) timeout. "
                f"Elapsed time: {elapsed_time:.2f} seconds"
            )
        
        return result_container['value']
    
    return wrapper

