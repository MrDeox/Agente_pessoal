"""
OpenAI Provider for LLM Integration

This module contains the OpenAI provider implementation.
"""

from typing import List
from .base import LLMProvider
from ..models import Message, LLMResponse
from ..exceptions import LLMException, AuthenticationError, RateLimitError, ModelError, InvalidRequestError, NetworkError, ServiceUnavailableError, TimeoutError, ContextLengthError, ContentPolicyError, QuotaExceededError
from ...utils.logging import get_logger, log_exception
from ...utils.retry import RetryConfig, retry_function

# Try to import openai, but handle if it's not available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, config):
        """
        Initialize the OpenAI provider.
        
        Args:
            config: Configuration object for the provider
            
        Raises:
            LLMException: If openai library is not available
        """
        super().__init__(config)
        
        if not OPENAI_AVAILABLE:
            raise LLMException("OpenAI library not available. Please install it with 'pip install openai'")
        
        # Initialize the OpenAI client
        self.client = openai.OpenAI(api_key=config.api_key)
    
    def _convert_messages(self, messages: List[Message]) -> List[dict]:
        """
        Convert internal messages to OpenAI format.
        
        Args:
            messages (List[Message]): Internal message format
            
        Returns:
            List[dict]: OpenAI message format
        """
        return [{"role": m.role, "content": m.content} for m in messages]
    
    def _handle_openai_exception(self, e: Exception) -> Exception:
        """
        Convert OpenAI API exceptions to our specific exception types.
        
        Args:
            e: The original exception
            
        Returns:
            Exception: The appropriate exception type
        """
        # Handle OpenAI-specific exceptions if available
        if hasattr(openai, 'AuthenticationError') and isinstance(e, openai.AuthenticationError):
            return AuthenticationError(f"OpenAI API authentication failed: {str(e)}")
        elif hasattr(openai, 'RateLimitError') and isinstance(e, openai.RateLimitError):
            return RateLimitError(f"OpenAI API rate limit exceeded: {str(e)}")
        elif hasattr(openai, 'NotFoundError') and isinstance(e, openai.NotFoundError):
            return ModelError(f"OpenAI model not found: {str(e)}")
        elif hasattr(openai, 'BadRequestError') and isinstance(e, openai.BadRequestError):
            # Check if it's a context length error
            if "context_length" in str(e).lower() or "too long" in str(e).lower():
                return ContextLengthError(f"OpenAI API context length exceeded: {str(e)}")
            return InvalidRequestError(f"Invalid request to OpenAI API: {str(e)}")
        elif hasattr(openai, 'PermissionDeniedError') and isinstance(e, openai.PermissionDeniedError):
            return ContentPolicyError(f"OpenAI API content policy violation: {str(e)}")
        elif hasattr(openai, 'APIConnectionError') and isinstance(e, openai.APIConnectionError):
            return NetworkError(f"Network error connecting to OpenAI API: {str(e)}")
        elif hasattr(openai, 'APIStatusError') and isinstance(e, openai.APIStatusError):
            status_code = getattr(e, 'status_code', 0)
            if status_code == 503:
                return ServiceUnavailableError(f"OpenAI API service unavailable: {str(e)}")
            elif status_code == 408:
                return TimeoutError(f"OpenAI API request timeout: {str(e)}")
            elif status_code == 429:
                return QuotaExceededError(f"OpenAI API quota exceeded: {str(e)}")
            else:
                return LLMException(f"OpenAI API error (status {status_code}): {str(e)}")
        else:
            # Generic error handling
            error_str = str(e).lower()
            if "authentication" in error_str or "api key" in error_str:
                return AuthenticationError(f"OpenAI API authentication failed: {str(e)}")
            elif "rate limit" in error_str or "quota" in error_str:
                if "quota" in error_str:
                    return QuotaExceededError(f"OpenAI API quota exceeded: {str(e)}")
                return RateLimitError(f"OpenAI API rate limit exceeded: {str(e)}")
            elif "not found" in error_str or "model" in error_str:
                return ModelError(f"OpenAI model error: {str(e)}")
            elif "bad request" in error_str or "invalid" in error_str:
                # Check if it's a context length error
                if "context_length" in error_str or "too long" in error_str:
                    return ContextLengthError(f"OpenAI API context length exceeded: {str(e)}")
                return InvalidRequestError(f"Invalid request to OpenAI API: {str(e)}")
            elif "permission denied" in error_str or "content policy" in error_str:
                return ContentPolicyError(f"OpenAI API content policy violation: {str(e)}")
            elif "connection" in error_str or "network" in error_str:
                return NetworkError(f"Network error connecting to OpenAI API: {str(e)}")
            elif "timeout" in error_str:
                return TimeoutError(f"OpenAI API request timeout: {str(e)}")
            else:
                return LLMException(f"OpenAI API error: {str(e)}")
    
    def generate_response(self, messages: List[Message], **kwargs) -> LLMResponse:
        """
        Generate a response from OpenAI.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            LLMResponse: Response from OpenAI
            
        Raises:
            LLMException: If there's an error with the OpenAI API
        """
        logger = get_logger()
        
        # Configure retry mechanism
        retry_config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0,
            jitter=True
        )
        
        def _make_api_call():
            logger.info(f"Calling OpenAI API with model: {self.config.model or 'gpt-3.5-turbo'}")
            response = self.client.chat.completions.create(
                model=self.config.model or "gpt-3.5-turbo",
                messages=self._convert_messages(messages),
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs
            )
            logger.info("OpenAI API call successful")
            return response
        
        try:
            response = retry_function(
                _make_api_call,
                retry_config,
                retryable_exceptions=(LLMException, RateLimitError, NetworkError, ServiceUnavailableError, TimeoutError),
                logger=logger
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                finish_reason=response.choices[0].finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model=response.model
            )
        except RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            raise
        except AuthenticationError:
            logger.error("OpenAI API authentication failed")
            raise
        except ModelError:
            logger.error("OpenAI API model error")
            raise
        except Exception as e:
            log_exception(e, "OpenAI API call")
            raise self._handle_openai_exception(e)
    
    def stream_response(self, messages: List[Message], **kwargs):
        """
        Stream a response from OpenAI.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments to pass to the API
            
        Yields:
            str: Chunks of the response
            
        Raises:
            LLMException: If there's an error with the OpenAI API
        """
        logger = get_logger()
        
        # Configure retry mechanism
        retry_config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0,
            jitter=True
        )
        
        def _make_streaming_api_call():
            logger.info(f"Streaming from OpenAI API with model: {self.config.model or 'gpt-3.5-turbo'}")
            response = self.client.chat.completions.create(
                model=self.config.model or "gpt-3.5-turbo",
                messages=self._convert_messages(messages),
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True,
                **kwargs
            )
            return response
        
        try:
            response = retry_function(
                _make_streaming_api_call,
                retry_config,
                retryable_exceptions=(LLMException, RateLimitError, NetworkError, ServiceUnavailableError, TimeoutError),
                logger=logger
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.info("OpenAI API streaming completed successfully")
        except RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            raise
        except AuthenticationError:
            logger.error("OpenAI API authentication failed")
            raise
        except ModelError:
            logger.error("OpenAI API model error")
            raise
        except Exception as e:
            log_exception(e, "OpenAI API streaming")
            raise self._handle_openai_exception(e)
    
    async def generate_response_async(self, messages: List[Message], **kwargs) -> LLMResponse:
        """
        Generate a response from OpenAI asynchronously.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            LLMResponse: Response from OpenAI
            
        Raises:
            LLMException: If there's an error with the OpenAI API
        """
        logger = get_logger()
        
        try:
            # For now, we'll use the sync method since the OpenAI library doesn't have native async support
            # In a real implementation, you would use the async version of the OpenAI library
            return self.generate_response(messages, **kwargs)
        except Exception as e:
            log_exception(e, "OpenAI async API call")
            raise self._handle_openai_exception(e)
    
    async def stream_response_async(self, messages: List[Message], **kwargs):
        """
        Stream a response from OpenAI asynchronously.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments to pass to the API
            
        Yields:
            str: Chunks of the response
            
        Raises:
            LLMException: If there's an error with the OpenAI API
        """
        logger = get_logger()
        
        try:
            # For now, we'll use the sync method since the OpenAI library doesn't have native async support
            # In a real implementation, you would use the async version of the OpenAI library
            response = self.stream_response(messages, **kwargs)
            for chunk in response:
                yield chunk
        except Exception as e:
            log_exception(e, "OpenAI async API streaming")
            raise self._handle_openai_exception(e)