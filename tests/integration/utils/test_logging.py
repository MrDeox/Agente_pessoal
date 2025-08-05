#!/usr/bin/env python3
"""
Test script for logging functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.utils.logging import get_logger, log_exception, log_function_call, log_function_return


def test_logger():
    """Test the logger functionality."""
    print("Testing logger functionality...")
    
    # Get logger instance
    logger = get_logger()
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    print("✓ Logger test completed")
    return True


def test_exception_logging():
    """Test exception logging."""
    print("\nTesting exception logging...")
    
    try:
        # Raise an exception to test logging
        raise ValueError("This is a test exception")
    except Exception as e:
        log_exception(e, "test_exception_logging")
    
    print("✓ Exception logging test completed")
    return True


def test_function_logging():
    """Test function call and return logging."""
    print("\nTesting function logging...")
    
    # Test function call logging
    log_function_call("test_function", (1, 2, 3), {"key": "value"})
    
    # Test function return logging
    log_function_return("test_function", "result_value")
    
    print("✓ Function logging test completed")
    return True


if __name__ == "__main__":
    print("Running logging tests...\n")
    
    success = True
    success &= test_logger()
    success &= test_exception_logging()
    success &= test_function_logging()
    
    if success:
        print("\n✓ All logging tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some logging tests failed!")
        sys.exit(1)