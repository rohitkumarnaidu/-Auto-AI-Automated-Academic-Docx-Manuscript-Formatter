import time
import functools
import random
from typing import Callable, Any, Type, Union, Tuple

def retry_guard(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (Exception,)
):
    """
    Decorator for robust retries with exponential backoff and jitter.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            current_delay = base_delay
            
            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_retries:
                        print(f"❌ Retry Guard: {func.__name__} failed after {max_retries} attempts. Last error: {e}")
                        raise e # Propagate final error for Circuit Breaker to handle
                    
                    # Calculate delay with jitter
                    jitter = random.uniform(0, 0.1 * current_delay)
                    sleep_time = min(current_delay + jitter, max_delay)
                    
                    print(f"🔄 Retry Guard: {func.__name__} failed (Attempt {attempt}/{max_retries}). Retrying in {sleep_time:.2f}s... Error: {e}")
                    time.sleep(sleep_time)
                    current_delay *= backoff_factor
            return None # Should not reach here
        return wrapper
    return decorator
