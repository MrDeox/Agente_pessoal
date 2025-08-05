"""
Error Recovery Module for Personal Agent

This module contains strategies for handling and recovering from different types of errors.
"""

from typing import Dict, Any, Optional, Callable
from ..llm.exceptions import (
    LLMException, AuthenticationError, RateLimitError, ModelError,
    NetworkError, InvalidRequestError, ServiceUnavailableError, TimeoutError,
    ContentPolicyError, QuotaExceededError, ConfigurationError, ProviderError,
    ContextLengthError, ParseError
)
from ..utils.logging import get_logger
from .error_metrics import error_metrics_collector


class ErrorRecoveryStrategy:
    """Base class for error recovery strategies."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger()
    
    def can_handle(self, exception: Exception) -> bool:
        """Check if this strategy can handle the given exception."""
        raise NotImplementedError
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> str:
        """Recover from the exception and return a user-friendly response."""
        raise NotImplementedError


class AuthenticationRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for authentication errors."""
    
    def __init__(self):
        super().__init__("authentication_recovery", "Recovery strategy for authentication errors")
    
    def can_handle(self, exception: Exception) -> bool:
        return isinstance(exception, AuthenticationError)
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> str:
        self.logger.warning(f"Authentication error: {exception}")
        return exception.user_message if hasattr(exception, 'user_message') else (
            "I'm having trouble authenticating with the AI service. "
            "Please check your API credentials or try again later."
        )


class RateLimitRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for rate limit errors."""
    
    def __init__(self):
        super().__init__("rate_limit_recovery", "Recovery strategy for rate limit errors")
    
    def can_handle(self, exception: Exception) -> bool:
        return isinstance(exception, (RateLimitError, QuotaExceededError))
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> str:
        self.logger.warning(f"Rate limit error: {exception}")
        return exception.user_message if hasattr(exception, 'user_message') else (
            "I'm temporarily busy. Please wait a moment before sending another message. "
            "This helps me manage my resources effectively."
        )


class NetworkRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for network errors."""
    
    def __init__(self):
        super().__init__("network_recovery", "Recovery strategy for network errors")
    
    def can_handle(self, exception: Exception) -> bool:
        return isinstance(exception, (NetworkError, TimeoutError, ServiceUnavailableError))
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> str:
        self.logger.warning(f"Network error: {exception}")
        return exception.user_message if hasattr(exception, 'user_message') else (
            "I'm having trouble connecting to the AI service. "
            "Please check your internet connection and try again."
        )


class ModelRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for model errors."""
    
    def __init__(self):
        super().__init__("model_recovery", "Recovery strategy for model errors")
    
    def can_handle(self, exception: Exception) -> bool:
        return isinstance(exception, (ModelError, ContextLengthError))
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> str:
        self.logger.warning(f"Model error: {exception}")
        if isinstance(exception, ContextLengthError):
            return exception.user_message if hasattr(exception, 'user_message') else (
                "Your message is too long for me to process. "
                "Please shorten it and try again."
            )
        return exception.user_message if hasattr(exception, 'user_message') else (
            "I'm having trouble with the AI model. "
            "This might be a temporary issue. Please try again later."
        )


class RequestRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for request errors."""
    
    def __init__(self):
        super().__init__("request_recovery", "Recovery strategy for request errors")
    
    def can_handle(self, exception: Exception) -> bool:
        return isinstance(exception, (InvalidRequestError, ContentPolicyError, ParseError))
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> str:
        self.logger.warning(f"Request error: {exception}")
        if isinstance(exception, ContentPolicyError):
            return exception.user_message if hasattr(exception, 'user_message') else (
                "Your request contains content that violates our usage policies. "
                "Please modify your request and try again."
            )
        elif isinstance(exception, ParseError):
            return exception.user_message if hasattr(exception, 'user_message') else (
                "I had trouble understanding the AI service's response. "
                "Please try again or rephrase your message."
            )
        return exception.user_message if hasattr(exception, 'user_message') else (
            "There was an issue with your request. "
            "Please try rephrasing your message and try again."
        )


class ConfigurationRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for configuration errors."""
    
    def __init__(self):
        super().__init__("configuration_recovery", "Recovery strategy for configuration errors")
    
    def can_handle(self, exception: Exception) -> bool:
        return isinstance(exception, (ConfigurationError, ProviderError))
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> str:
        self.logger.warning(f"Configuration error: {exception}")
        return exception.user_message if hasattr(exception, 'user_message') else (
            "There's an issue with my configuration. "
            "Please contact support or check your settings."
        )


class GenericRecoveryStrategy(ErrorRecoveryStrategy):
    """Generic recovery strategy for unhandled errors."""
    
    def __init__(self):
        super().__init__("generic_recovery", "Generic recovery strategy for unhandled errors")
    
    def can_handle(self, exception: Exception) -> bool:
        return isinstance(exception, LLMException)
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> str:
        self.logger.warning(f"Unhandled LLM error: {exception}")
        return exception.user_message if hasattr(exception, 'user_message') else (
            "I encountered an unexpected error. "
            "Please try again or rephrase your message."
        )


class ErrorRecoveryManager:
    """Manager for handling error recovery strategies."""
    
    def __init__(self):
        self.strategies = [
            AuthenticationRecoveryStrategy(),
            RateLimitRecoveryStrategy(),
            NetworkRecoveryStrategy(),
            ModelRecoveryStrategy(),
            RequestRecoveryStrategy(),
            ConfigurationRecoveryStrategy(),
            GenericRecoveryStrategy()
        ]
        self.logger = get_logger()
    
    def add_strategy(self, strategy: ErrorRecoveryStrategy):
        """Add a new recovery strategy."""
        self.strategies.append(strategy)
    
    def remove_strategy(self, strategy_name: str):
        """Remove a recovery strategy by name."""
        self.strategies = [s for s in self.strategies if s.name != strategy_name]
    
    def recover_from_error(self, exception: Exception, context: Dict[str, Any] = None) -> str:
        """
        Recover from an error using the appropriate strategy.
        
        Args:
            exception (Exception): The exception that occurred
            context (Dict[str, Any]): Additional context for recovery
            
        Returns:
            str: User-friendly error message
        """
        context = context or {}
        
        # Record the error in metrics collector
        error_metrics_collector.record_error(
            error_type=type(exception).__name__,
            error_message=str(exception),
            context=context
        )
        
        # Try to find a specific strategy for this exception
        for strategy in self.strategies:
            if strategy.can_handle(exception):
                try:
                    return strategy.recover(exception, context)
                except Exception as recovery_error:
                    self.logger.error(f"Error in recovery strategy {strategy.name}: {recovery_error}")
                    # Fall back to generic recovery
                    break
        
        # If no specific strategy found or recovery failed, use generic approach
        return self._generic_recovery(exception, context)
    
    def _generic_recovery(self, exception: Exception, context: Dict[str, Any]) -> str:
        """Generic recovery approach."""
        self.logger.error(f"Generic recovery for unhandled exception: {exception}")
        
        # Try to get user message from exception
        if hasattr(exception, 'user_message') and exception.user_message:
            return exception.user_message
        
        # Fallback to generic message
        return (
            "I encountered an unexpected error while processing your request. "
            "Please try again later or contact support if the issue persists."
        )


# Global error recovery manager instance
error_recovery_manager = ErrorRecoveryManager()