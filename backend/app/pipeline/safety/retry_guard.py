"""
retry_guard.py - Tenacity-backed retry decorator.

Backward-compatible public API:
  retry_guard(max_retries, base_delay, max_delay, backoff_factor, exceptions)
  retry_on_failure  <- alias
"""
import logging
from typing import Type, Tuple, Union

logger = logging.getLogger(__name__)

try:
    from tenacity import (
        retry, stop_after_attempt, wait_exponential_jitter,
        retry_if_exception_type, before_sleep_log,
    )
    _TENACITY = True
except ImportError:
    _TENACITY = False
    logger.warning("tenacity not installed - legacy retry active. pip install tenacity")


def retry_guard(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (Exception,),
):
    """Decorator: exponential backoff retries (tenacity-powered when available)."""
    if _TENACITY:
        exc_t = exceptions if isinstance(exceptions, tuple) else (exceptions,)
        def decorator(func):
            return retry(
                stop=stop_after_attempt(max_retries),
                wait=wait_exponential_jitter(
                    initial=base_delay, max=max_delay,
                    exp_base=backoff_factor, jitter=base_delay * 0.1,
                ),
                retry=retry_if_exception_type(exc_t),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            )(func)
        return decorator

    # --- Legacy fallback ---
    import time, random, functools
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt, delay = 0, base_delay
            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    attempt += 1
                    if attempt >= max_retries:
                        logger.error("%s failed after %d attempts: %s", func.__name__, max_retries, exc)
                        raise
                    sleep = min(delay + random.uniform(0, 0.1 * delay), max_delay)
                    logger.warning("%s attempt %d/%d, retry in %.2fs: %s", func.__name__, attempt, max_retries, sleep, exc)
                    time.sleep(sleep)
                    delay *= backoff_factor
        return wrapper
    return decorator


retry_on_failure = retry_guard  # backward-compat alias
