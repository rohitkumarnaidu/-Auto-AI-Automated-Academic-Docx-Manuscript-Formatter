"""
circuit_breaker.py - pybreaker-backed circuit breaker decorator.

Replaces non-thread-safe function-attribute state with pybreaker.

Backward-compatible public API:
  circuit_breaker(failure_threshold, recovery_timeout, fallback_function)
  CircuitBreakerOpenException
"""
import logging
import functools
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

try:
    import pybreaker
    _PYBREAKER = True
except ImportError:
    _PYBREAKER = False
    logger.warning("pybreaker not installed - legacy circuit breaker active. pip install pybreaker")


class CircuitBreakerOpenException(Exception):
    """Raised when the circuit is open and calls are blocked."""
    pass


def circuit_breaker(
    failure_threshold: int = 3,
    recovery_timeout: int = 60,
    fallback_function: Optional[Callable] = None,
):
    """Thread-safe circuit breaker decorator (pybreaker-powered when available)."""
    if _PYBREAKER:
        def decorator(func: Callable) -> Callable:
            class _Log(pybreaker.CircuitBreakerListener):
                def state_change(self, cb, old, new):
                    logger.warning("CircuitBreaker '%s': %s -> %s", func.__name__, old.name, new.name)
                def failure(self, cb, exc):
                    logger.warning("CircuitBreaker '%s': failure %d/%d - %s", func.__name__, cb.fail_counter, failure_threshold, exc)

            _cb = pybreaker.CircuitBreaker(
                fail_max=failure_threshold,
                reset_timeout=recovery_timeout,
                listeners=[_Log()],
            )

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    return _cb.call(func, *args, **kwargs)
                except pybreaker.CircuitBreakerError as exc:
                    logger.error("CircuitBreaker OPEN for '%s': %s", func.__name__, exc)
                    if fallback_function:
                        try:
                            return fallback_function(*args, **kwargs)
                        except Exception as fb:
                            logger.error("Fallback also failed: %s", fb)
                            return {}
                    raise CircuitBreakerOpenException(f"Circuit Breaker is OPEN for {func.__name__}") from exc
                except Exception as exc:
                    if fallback_function:
                        try:
                            return fallback_function(*args, **kwargs)
                        except Exception as fb:
                            logger.error("Fallback also failed: %s", fb)
                            return {}
                    raise
            return wrapper
        return decorator

    # --- Legacy fallback (original non-thread-safe implementation) ---
    import time

    def decorator(func: Callable) -> Callable:
        func.failures = 0
        func.last_failure_time = 0.0
        func.state = "CLOSED"

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()
            if func.state == "OPEN":
                if now - func.last_failure_time > recovery_timeout:
                    func.state = "HALF_OPEN"
                else:
                    logger.warning("CircuitBreaker OPEN for %s. Using fallback.", func.__name__)
                    if fallback_function:
                        return fallback_function(*args, **kwargs)
                    raise CircuitBreakerOpenException(f"Circuit Breaker is OPEN for {func.__name__}")
            try:
                result = func(*args, **kwargs)
                if func.state == "HALF_OPEN":
                    logger.info("CircuitBreaker RECOVERED for %s.", func.__name__)
                func.failures = 0
                func.state = "CLOSED"
                return result
            except Exception as exc:
                func.failures += 1
                func.last_failure_time = now
                logger.warning("CircuitBreaker: %s failed (%d/%d): %s", func.__name__, func.failures, failure_threshold, exc)
                if func.failures >= failure_threshold:
                    func.state = "OPEN"
                    logger.error("CircuitBreaker TRIPPED for %s. Blocking %ds.", func.__name__, recovery_timeout)
                if fallback_function:
                    try:
                        return fallback_function(*args, **kwargs)
                    except Exception as fb:
                        logger.error("Fallback also failed: %s", fb)
                        return {}
                raise
        return wrapper
    return decorator
