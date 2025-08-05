#!/usr/bin/env python3
"""
Test script for retry functionality
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.utils.retry import RetryConfig, retry_function, retry_with_backoff, RetryableException


class TestRetryableException(RetryableException):
    """Test retryable exception."""
    pass


def failing_function(attempt_threshold: int = 3):
    """
    Function that fails until a certain attempt threshold.
    
    Args:
        attempt_threshold (int): Number of attempts before succeeding
        
    Returns:
        str: Success message
    """
    # Keep track of attempts using a function attribute
    if not hasattr(failing_function, "attempts"):
        failing_function.attempts = 0
    
    failing_function.attempts += 1
    
    if failing_function.attempts < attempt_threshold:
        raise TestRetryableException(f"Attempt {failing_function.attempts} failed")
    
    # Reset attempts for next test
    result = f"Success on attempt {failing_function.attempts}"
    failing_function.attempts = 0
    return result


def test_retry_function():
    """Test the retry_function utility."""
    print("Testing retry_function...")
    
    # Test successful retry
    config = RetryConfig(max_retries=5, base_delay=0.1, max_delay=0.5)
    
    try:
        result = retry_function(
            failing_function,
            config,
            3,  # attempt_threshold
            retryable_exceptions=(TestRetryableException,),
        )
        print(f"✓ Retry function test passed: {result}")
        return True
    except Exception as e:
        print(f"✗ Retry function test failed: {e}")
        return False


@retry_with_backoff(
    RetryConfig(max_retries=5, base_delay=0.1, max_delay=0.5),
    retryable_exceptions=(TestRetryableException,)
)
def decorated_failing_function(attempt_threshold: int = 3):
    """
    Decorated function that fails until a certain attempt threshold.
    
    Args:
        attempt_threshold (int): Number of attempts before succeeding
        
    Returns:
        str: Success message
    """
    # Keep track of attempts using a function attribute
    if not hasattr(decorated_failing_function, "attempts"):
        decorated_failing_function.attempts = 0
    
    decorated_failing_function.attempts += 1
    
    if decorated_failing_function.attempts < attempt_threshold:
        raise TestRetryableException(f"Attempt {decorated_failing_function.attempts} failed")
    
    # Reset attempts for next test
    result = f"Success on attempt {decorated_failing_function.attempts}"
    decorated_failing_function.attempts = 0
    return result


def test_retry_decorator():
    """Test the retry decorator."""
    print("\nTesting retry decorator...")
    
    try:
        result = decorated_failing_function(3)
        print(f"✓ Retry decorator test passed: {result}")
        return True
    except Exception as e:
        print(f"✗ Retry decorator test failed: {e}")
        return False


def test_retry_failure():
    """Test retry with ultimate failure."""
    print("\nTesting retry with ultimate failure...")
    
    config = RetryConfig(max_retries=2, base_delay=0.1, max_delay=0.5)
    
    try:
        retry_function(
            failing_function,
            config,
            5,  # attempt_threshold higher than max_retries
            retryable_exceptions=(TestRetryableException,),
        )
        print("✗ Retry failure test failed (should have raised exception)")
        return False
    except TestRetryableException:
        print("✓ Retry failure test passed (exception raised as expected)")
        return True
    except Exception as e:
        print(f"✗ Retry failure test failed with unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("Running retry tests...\n")
    
    success = True
    success &= test_retry_function()
    success &= test_retry_decorator()
    success &= test_retry_failure()
    
    if success:
        print("\n✓ All retry tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some retry tests failed!")
        sys.exit(1)