"""
Retry utilities for Personal Agent

This module contains retry mechanisms with exponential backoff for external service calls.
"""

import time
import random
import logging
from typing import Callable, Any, Tuple, Optional
from functools import wraps
from ..config.constants import RETRY


class RetryConfig:
    """Configuration for retry mechanism."""
    
    def __init__(
        self,
        max_retries: int = RETRY.DEFAULT_MAX_ATTEMPTS,
        base_delay: float = RETRY.DEFAULT_BASE_DELAY,
        max_delay: float = RETRY.DEFAULT_MAX_DELAY,
        exponential_base: float = RETRY.DEFAULT_EXPONENTIAL_BASE,
        jitter: bool = True
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries (int): Maximum number of retry attempts
            base_delay (float): Base delay in seconds
            max_delay (float): Maximum delay in seconds
            exponential_base (float): Base for exponential backoff
            jitter (bool): Whether to add jitter to delays
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class RetryableException(Exception):
    """Exception that can be retried."""
    pass


class NonRetryableException(Exception):
    """Exception that should not be retried."""
    pass


def calculate_delay(config: RetryConfig, attempt: int) -> float:
    """
    Calculate delay for a retry attempt.
    
    Args:
        config (RetryConfig): Retry configuration
        attempt (int): Current attempt number (0-based)
        
    Returns:
        float: Delay in seconds
    """
    # Calculate exponential delay
    delay = min(
        config.base_delay * (config.exponential_base ** attempt),
        config.max_delay
    )
    
    # Add jitter if enabled
    if config.jitter:
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay


def retry_with_backoff(
    config: RetryConfig,
    retryable_exceptions: Tuple[type, ...] = (RetryableException,),
    logger: Optional[logging.Logger] = None
):
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        config (RetryConfig): Retry configuration
        retryable_exceptions (Tuple[type, ...]): Exceptions that should trigger a retry
        logger (logging.Logger): Logger to use for logging retry attempts
        
    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    # If this was the last attempt, re-raise the exception
                    if attempt == config.max_retries:
                        if logger:
                            logger.error(f"Function {func.__name__} failed after {config.max_retries + 1} attempts: {e}")
                        raise
                    
                    # Calculate and apply delay
                    delay = calculate_delay(config, attempt)
                    if logger:
                        logger.warning(
                            f"Attempt {attempt + 1} of {func.__name__} failed: {e}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                    
                    time.sleep(delay)
                except Exception as e:
                    # Non-retryable exception, re-raise immediately
                    if logger:
                        logger.error(f"Non-retryable exception in {func.__name__}: {e}")
                    raise
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def retry_function(
    func: Callable,
    config: RetryConfig,
    *args,
    retryable_exceptions: Tuple[type, ...] = (RetryableException,),
    logger: Optional[logging.Logger] = None,
    **kwargs
) -> Any:
    """
    Retry a function with exponential backoff.
    
    Args:
        func (Callable): Function to retry
        config (RetryConfig): Retry configuration
        *args: Positional arguments to pass to the function
        retryable_exceptions (Tuple[type, ...]): Exceptions that should trigger a retry
        logger (logging.Logger): Logger to use for logging retry attempts
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Any: Result of the function call
    """
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retryable_exceptions as e:
            last_exception = e
            
            # If this was the last attempt, re-raise the exception
            if attempt == config.max_retries:
                if logger:
                    logger.error(f"Function {func.__name__} failed after {config.max_retries + 1} attempts: {e}")
                raise
            
            # Calculate and apply delay
            delay = calculate_delay(config, attempt)
            if logger:
                logger.warning(
                    f"Attempt {attempt + 1} of {func.__name__} failed: {e}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
            
            time.sleep(delay)
        except Exception as e:
            # Non-retryable exception, re-raise immediately
            if logger:
                logger.error(f"Non-retryable exception in {func.__name__}: {e}")
            raise
    
    # This should never be reached, but just in case
    raise last_exception