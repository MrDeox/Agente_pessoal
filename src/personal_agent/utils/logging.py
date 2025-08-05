"""
Logging utilities for Personal Agent

This module contains logging configuration and utility functions.
"""

import logging
import os
from typing import Optional
from datetime import datetime


class PersonalAgentLogger:
    """Custom logger for the Personal Agent."""
    
    def __init__(self, name: str = "PersonalAgent", log_file: Optional[str] = None):
        """
        Initialize the logger.
        
        Args:
            name (str): Name of the logger
            log_file (str): Path to log file (optional)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Prevent adding multiple handlers if logger already exists
        if not self.logger.handlers:
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Add console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # Add file handler if specified
            if log_file:
                # Create directory if it doesn't exist
                log_dir = os.path.dirname(log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log a critical message."""
        self.logger.critical(message)


# Global logger instance
_logger = None


def get_logger() -> PersonalAgentLogger:
    """
    Get the global logger instance.
    
    Returns:
        PersonalAgentLogger: Logger instance
    """
    global _logger
    if _logger is None:
        # Create logs directory
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file path with timestamp
        log_file = os.path.join(log_dir, f"personal_agent_{datetime.now().strftime('%Y%m%d')}.log")
        _logger = PersonalAgentLogger("PersonalAgent", log_file)
    return _logger


def log_exception(exception: Exception, context: str = ""):
    """
    Log an exception with context.
    
    Args:
        exception (Exception): The exception to log
        context (str): Additional context information
    """
    logger = get_logger()
    error_message = f"Exception in {context}: {type(exception).__name__}: {str(exception)}"
    logger.error(error_message)


def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None):
    """
    Log a function call.
    
    Args:
        func_name (str): Name of the function
        args (tuple): Positional arguments
        kwargs (dict): Keyword arguments
    """
    logger = get_logger()
    args_str = ", ".join(map(str, args))
    kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()]) if kwargs else ""
    all_args = ", ".join(filter(None, [args_str, kwargs_str]))
    logger.debug(f"Calling {func_name}({all_args})")


def log_function_return(func_name: str, result):
    """
    Log a function return value.
    
    Args:
        func_name (str): Name of the function
        result: Return value
    """
    logger = get_logger()
    logger.debug(f"{func_name} returned: {result}")