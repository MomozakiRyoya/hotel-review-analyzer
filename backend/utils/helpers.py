"""
Helper utility functions.
"""
import asyncio
from typing import TypeVar, Callable, Any
from functools import wraps
from loguru import logger
from backend.config import settings


T = TypeVar('T')


async def retry_async(
    func: Callable[..., T],
    max_retries: int = None,
    backoff_factor: float = None,
    exceptions: tuple = (Exception,)
) -> T:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        backoff_factor: Backoff multiplier for retry delay
        exceptions: Tuple of exceptions to catch

    Returns:
        Result of the function call

    Raises:
        Last exception if all retries fail
    """
    max_retries = max_retries or settings.max_retries
    backoff_factor = backoff_factor or settings.retry_backoff_factor

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                delay = backoff_factor ** attempt
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed")

    raise last_exception


def rate_limit(delay: float = None):
    """
    Decorator to add rate limiting to async functions.

    Args:
        delay: Delay in seconds between calls
    """
    delay_seconds = delay or settings.request_delay_seconds

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await asyncio.sleep(delay_seconds)
            return result
        return wrapper
    return decorator


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
