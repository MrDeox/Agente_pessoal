"""
Error Handler for Personal Agent

This module contains the ErrorHandler class that manages error recovery,
metrics collection, and error reporting.
"""

from typing import Dict, Any, Optional, Callable
from ..llm.exceptions import LLMException
from .error_metrics import error_metrics_collector
from ..utils.logging import get_logger, log_exception


class ErrorHandler:
    """
    Manages error recovery, metrics collection, and error reporting.
    """
    
    def __init__(self):
        """
        Initialize the error handler.
        """
        self.logger = get_logger()
        self.metrics_collector = error_metrics_collector
    
    def handle_llm_exception(self, exception: LLMException, context: Dict[str, Any]) -> str:
        """
        Handle LLM exceptions with appropriate recovery strategies.
        
        Args:
            exception (LLMException): The LLM exception that occurred
            context (Dict[str, Any]): Context information for error recovery
            
        Returns:
            str: Recovery response or error message
        """
        # Log the exception
        log_exception(exception, "LLM response generation")
        
        # Collect error metrics
        self.metrics_collector.record_error("llm_exception", str(exception))
        
        # Try to recover using error recovery manager
        try:
            from .error_recovery import error_recovery_manager
            return error_recovery_manager.recover_from_error(exception, context)
        except Exception as recovery_error:
            self.logger.error(f"Error recovery failed: {recovery_error}")
            # Fallback response
            return "I'm sorry, but I encountered an error while processing your request. Please try again."
    
    def handle_unexpected_exception(self, exception: Exception, context: Dict[str, Any]) -> str:
        """
        Handle unexpected exceptions with appropriate recovery strategies.
        
        Args:
            exception (Exception): The unexpected exception that occurred
            context (Dict[str, Any]): Context information for error recovery
            
        Returns:
            str: Recovery response or error message
        """
        # Log the exception
        log_exception(exception, "Unexpected error in response generation")
        
        # Collect error metrics
        self.metrics_collector.record_error("unexpected_exception", str(exception))
        
        # Try to recover using error recovery manager
        try:
            from .error_recovery import error_recovery_manager
            # Wrap in LLMException for consistency with recovery manager
            llm_exception = LLMException(str(exception))
            return error_recovery_manager.recover_from_error(llm_exception, context)
        except Exception as recovery_error:
            self.logger.error(f"Error recovery failed: {recovery_error}")
            # Fallback response
            return "I'm sorry, but I encountered an unexpected error. Please try again."
    
    def get_error_metrics(self) -> Dict[str, Any]:
        """
        Get error metrics for monitoring and analysis.
        
        Returns:
            Dict[str, Any]: Error metrics summary
        """
        return self.metrics_collector.get_error_summary()
    
    def wrap_with_error_handling(self, func: Callable, *args, **kwargs) -> Any:
        """
        Wrap a function with error handling.
        
        Args:
            func (Callable): The function to wrap
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: The result of the function or None if an error occurred
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in {func.__name__}: {e}")
            self.metrics_collector.record_error(func.__name__, str(e))
            return None
    
    def record_error(self, error_type: str, error_message: str) -> None:
        """
        Record an error in the metrics collector.
        
        Args:
            error_type (str): Type of error
            error_message (str): Error message
        """
        self.metrics_collector.record_error(error_type, error_message)