import time
import functools
from typing import Callable, Any, Optional

class CircuitBreakerOpenException(Exception):
    """Raised when the circuit is open and calls are blocked."""
    pass

def circuit_breaker(
    failure_threshold: int = 3,
    recovery_timeout: int = 60,
    fallback_function: Optional[Callable] = None
):
    """
    Decorator that implements the Circuit Breaker pattern.
    
    Args:
        failure_threshold: Number of failures before opening the circuit.
        recovery_timeout: Seconds to wait before attempting recovery (Half-Open state).
        fallback_function: Function to call when circuit is open or execution fails.
    """
    def decorator(func: Callable) -> Callable:
        # State stored in function attributes (simple in-memory storage)
        func.failures = 0
        func.last_failure_time = 0
        func.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()
            
            # Check CLOSED/OPEN state
            if func.state == "OPEN":
                if current_time - func.last_failure_time > recovery_timeout:
                    func.state = "HALF_OPEN"
                    # Allow *one* trial call
                else:
                    # Circuit is OPEN, return fallback or raise
                    print(f"🛑 Circuit Breaker OPEN for {func.__name__}. Using fallback.")
                    if fallback_function:
                        return fallback_function(*args, **kwargs)
                    raise CircuitBreakerOpenException(f"Circuit Breaker is OPEN for {func.__name__}")

            try:
                # Attempt execution
                result = func(*args, **kwargs)
                
                # Success! Reset state
                if func.state == "HALF_OPEN":
                    print(f"✅ Circuit Breaker RECOVERED for {func.__name__}.")
                
                func.failures = 0
                func.state = "CLOSED"
                return result
            
            except Exception as e:
                # Failure logic
                func.failures += 1
                func.last_failure_time = current_time
                print(f"⚠️ Circuit Breaker Warning: {func.__name__} failed ({func.failures}/{failure_threshold}). Error: {e}")
                
                if func.failures >= failure_threshold:
                    func.state = "OPEN"
                    print(f"🔥 Circuit Breaker TRIPPED for {func.__name__}. Blocking calls for {recovery_timeout}s.")
                
                if fallback_function:
                    try:
                        return fallback_function(*args, **kwargs)
                    except Exception as fallback_error:
                        print(f"☠️ Critical: Fallback also failed: {fallback_error}")
                        # Last resort: return None or empty dict to prevent crash
                        return {}
                
                # If no fallback, re-raise (or catch if you want pure 0-crash policy)
                # Ideally, fallback should be mandatory for 0-crash.
                raise e 

        return wrapper
    return decorator
