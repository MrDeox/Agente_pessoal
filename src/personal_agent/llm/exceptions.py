"""
LLM Exceptions for Personal Agent

This module contains custom exceptions for LLM-related errors with comprehensive categorization.
"""

from ..utils.retry import RetryableException


class LLMException(RetryableException):
    """Base exception for LLM-related errors."""
    
    def __init__(self, message: str = None, error_code: str = None, user_message: str = None):
        """
        Initialize the LLM exception.
        
        Args:
            message (str): Technical error message
            error_code (str): Error code for categorization
            user_message (str): User-friendly error message
        """
        super().__init__(message or "LLM error occurred")
        self.error_code = error_code
        self.user_message = user_message or "An error occurred with the AI service."


class AuthenticationError(LLMException):
    """Raised when API authentication fails."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "API authentication failed",
            error_code="AUTH_FAILED",
            user_message="I'm having trouble authenticating with the AI service. Please check your API credentials."
        )


class RateLimitError(LLMException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "API rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            user_message="I'm temporarily busy. Please wait a moment before sending another message."
        )


class ModelError(LLMException):
    """Raised when there's an issue with the model."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "Model error occurred",
            error_code="MODEL_ERROR",
            user_message="I'm having trouble with the AI model. This might be a temporary issue. Please try again later."
        )


class NetworkError(LLMException):
    """Raised when there's a network connectivity issue."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "Network connectivity issue",
            error_code="NETWORK_ERROR",
            user_message="I'm having trouble connecting to the AI service. Please check your internet connection."
        )


class InvalidRequestError(LLMException):
    """Raised when the request to the API is invalid."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "Invalid request to API",
            error_code="INVALID_REQUEST",
            user_message="There was an issue with your request. Please try rephrasing your message."
        )


class ServiceUnavailableError(LLMException):
    """Raised when the API service is unavailable."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "API service unavailable",
            error_code="SERVICE_UNAVAILABLE",
            user_message="The AI service is currently unavailable. Please try again later."
        )


class TimeoutError(LLMException):
    """Raised when the API request times out."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "API request timeout",
            error_code="TIMEOUT",
            user_message="The AI service is taking longer than expected to respond. Please try again."
        )


class ContentPolicyError(LLMException):
    """Raised when content violates API policies."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "Content policy violation",
            error_code="CONTENT_POLICY_VIOLATION",
            user_message="Your request contains content that violates our usage policies. Please modify your request."
        )


class QuotaExceededError(LLMException):
    """Raised when API quota is exceeded."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "API quota exceeded",
            error_code="QUOTA_EXCEEDED",
            user_message="I've reached my usage limit for the AI service. Please try again later or check your account."
        )


class ConfigurationError(LLMException):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "Configuration error",
            error_code="CONFIGURATION_ERROR",
            user_message="There's an issue with my configuration. Please contact support."
        )


class ProviderError(LLMException):
    """Raised when there's a provider-specific error."""
    
    def __init__(self, message: str = None, provider: str = None):
        provider_info = f" from {provider}" if provider else ""
        super().__init__(
            message=message or f"Provider error{provider_info}",
            error_code="PROVIDER_ERROR",
            user_message=f"I encountered an error with the AI provider{provider_info}. This might be temporary."
        )


class ContextLengthError(LLMException):
    """Raised when the context length exceeds model limits."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "Context length exceeded",
            error_code="CONTEXT_LENGTH_EXCEEDED",
            user_message="Your message is too long for me to process. Please shorten it and try again."
        )


class ParseError(LLMException):
    """Raised when there's an error parsing the response."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or "Response parsing error",
            error_code="PARSE_ERROR",
            user_message="I had trouble understanding the AI service's response. Please try again."
        )


# Error categories for grouping and handling
ERROR_CATEGORIES = {
    "AUTHENTICATION": [AuthenticationError],
    "RATE_LIMITING": [RateLimitError, QuotaExceededError],
    "NETWORK": [NetworkError, TimeoutError, ServiceUnavailableError],
    "MODEL": [ModelError, ContextLengthError],
    "REQUEST": [InvalidRequestError, ContentPolicyError, ParseError],
    "CONFIGURATION": [ConfigurationError, ProviderError]
}