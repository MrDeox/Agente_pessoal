"""
Standardized Error Handling for Personal Agent

This module provides consistent error handling patterns across the application.
"""

import json
import logging
from typing import Any, Callable, Dict, Optional, Type, Union
from functools import wraps
from ..utils.logging import get_logger


class ErrorHandlingMixin:
    """Mixin class to provide standardized error handling methods."""
    
    def __init__(self):
        self._logger = get_logger()
    
    def handle_json_error(self, data: str, context: str = "JSON parsing") -> Optional[Dict[str, Any]]:
        """
        Standardized JSON parsing with error handling.
        
        Args:
            data: JSON string to parse
            context: Context for error logging
            
        Returns:
            Parsed JSON data or None if parsing failed
        """
        if not data:
            return None
            
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            self._logger.error(f"JSON decode error in {context}: {e}")
            return None
        except Exception as e:
            self._logger.error(f"Unexpected error in {context}: {e}")
            return None
    
    def handle_database_error(self, operation: str, error: Exception) -> bool:
        """
        Standardized database error handling.
        
        Args:
            operation: Description of the database operation
            error: The exception that occurred
            
        Returns:
            False to indicate operation failed
        """
        error_type = type(error).__name__
        self._logger.error(f"Database error in {operation}: {error_type} - {error}")
        return False
    
    def handle_validation_error(self, field: str, value: Any, constraint: str) -> None:
        """
        Standardized validation error handling.
        
        Args:
            field: Field name that failed validation
            value: The invalid value
            constraint: Description of the validation constraint
        """
        from ..utils.validation import ValidationError
        error_msg = f"Validation failed for {field}: {constraint}. Got: {value}"
        self._logger.error(error_msg)
        raise ValidationError(error_msg)
    
    def handle_llm_error(self, error: Exception, operation: str) -> Optional[str]:
        """
        Standardized LLM error handling with fallback.
        
        Args:
            error: The LLM exception
            operation: Description of the LLM operation
            
        Returns:
            Fallback response or None
        """
        from ..llm.exceptions import LLMException
        
        error_type = type(error).__name__
        self._logger.error(f"LLM error in {operation}: {error_type} - {error}")
        
        if isinstance(error, LLMException):
            # Provide context-appropriate fallback responses
            if "generate" in operation.lower():
                return "I apologize, but I'm experiencing technical difficulties. Please try again."
            elif "summarize" in operation.lower():
                return "Unable to summarize at this time."
        
        return None


def handle_errors(
    default_return: Any = None,
    log_context: str = None,
    reraise: bool = False,
    fallback_fn: Optional[Callable] = None
):
    """
    Decorator for standardized error handling.
    
    Args:
        default_return: Value to return if error occurs
        log_context: Context for error logging
        reraise: Whether to reraise exceptions after logging
        fallback_fn: Optional fallback function to call on error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            context = log_context or f"{func.__name__}"
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type = type(e).__name__
                logger.error(f"Error in {context}: {error_type} - {e}")
                
                if fallback_fn:
                    try:
                        return fallback_fn(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback function failed in {context}: {fallback_error}")
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def handle_async_errors(
    default_return: Any = None,
    log_context: str = None,
    reraise: bool = False,
    fallback_fn: Optional[Callable] = None
):
    """
    Async version of handle_errors decorator.
    
    Args:
        default_return: Value to return if error occurs
        log_context: Context for error logging
        reraise: Whether to reraise exceptions after logging
        fallback_fn: Optional async fallback function to call on error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger()
            context = log_context or f"{func.__name__}"
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_type = type(e).__name__
                logger.error(f"Error in {context}: {error_type} - {e}")
                
                if fallback_fn:
                    try:
                        return await fallback_fn(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback function failed in {context}: {fallback_error}")
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


class ErrorContext:
    """Context manager for error handling with automatic logging."""
    
    def __init__(self, operation: str, logger: Optional[logging.Logger] = None):
        self.operation = operation
        self.logger = logger or get_logger()
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            error_type = exc_type.__name__
            self.logger.error(f"Error in {self.operation}: {error_type} - {exc_val}")
        return False  # Don't suppress exceptions
    
    def success(self) -> bool:
        """Check if the operation was successful (no exceptions)."""
        return self.error is None


# Common error handling patterns as utility functions

def safe_json_loads(data: str, default: Any = None, logger: Optional[logging.Logger] = None) -> Any:
    """
    Safely parse JSON with consistent error handling.
    
    Args:
        data: JSON string to parse
        default: Default value if parsing fails
        logger: Optional logger for error reporting
        
    Returns:
        Parsed JSON data or default value
    """
    if not data:
        return default
    
    log = logger or get_logger()
    
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        log.error(f"JSON decode error: {e}")
        return default
    except Exception as e:
        log.error(f"Unexpected error parsing JSON: {e}")
        return default


def safe_json_dumps(data: Any, default: str = "{}", logger: Optional[logging.Logger] = None) -> str:
    """
    Safely serialize to JSON with consistent error handling.
    
    Args:
        data: Data to serialize
        default: Default JSON string if serialization fails
        logger: Optional logger for error reporting
        
    Returns:
        JSON string or default value
    """
    log = logger or get_logger()
    
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        log.error(f"JSON encode error: {e}")
        return default
    except Exception as e:
        log.error(f"Unexpected error serializing JSON: {e}")
        return default


def safe_cast(value: Any, target_type: Type, default: Any = None, logger: Optional[logging.Logger] = None) -> Any:
    """
    Safely cast a value to target type with error handling.
    
    Args:
        value: Value to cast
        target_type: Target type for casting
        default: Default value if casting fails
        logger: Optional logger for error reporting
        
    Returns:
        Casted value or default
    """
    log = logger or get_logger()
    
    try:
        return target_type(value)
    except (ValueError, TypeError) as e:
        log.error(f"Type casting error: {e}")
        return default
    except Exception as e:
        log.error(f"Unexpected error casting to {target_type.__name__}: {e}")
        return default