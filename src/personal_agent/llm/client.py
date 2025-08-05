"""
LLM Client for Personal Agent

This module contains the main LLM client interface and implementation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .providers.base import LLMProvider
from ..config.settings import Config
from .models import Message, LLMResponse
from ..utils.logging import get_logger, log_exception
from .plugin_manager import load_provider_plugin, get_loaded_provider
from .cache import get_llm_cache, LLmCache


class LLMClient:
    """Main interface for interacting with LLMs."""
    
    def __init__(self, config: Config, cache: Optional[LLmCache] = None):
        """
        Initialize the LLM client.
        
        Args:
            config (Config): Configuration object containing LLM settings
            cache (Optional[LLmCache]): Cache instance. If None, uses global cache.
        """
        self.config = config
        self.provider = self._initialize_provider()
        self.cache = cache or get_llm_cache()
    
    def _initialize_provider(self) -> LLMProvider:
        """
        Initialize the appropriate provider based on configuration.
        
        Returns:
            LLMProvider: Initialized provider instance
            
        Raises:
            ValueError: If the provider is not supported
        """
        provider_name = self.config.llm.provider
        logger = get_logger()
        
        try:
            # Try to load the provider using the plugin system
            provider_class = load_provider_plugin(provider_name)
            
            if provider_class:
                logger.info(f"Initializing {provider_name} provider via plugin system")
                return provider_class(self.config.llm)
            else:
                # Fallback to direct import for built-in providers
                if provider_name == "openai":
                    from .providers.openai import OpenAIProvider
                    logger.info("Initializing OpenAI provider")
                    return OpenAIProvider(self.config.llm)
                elif provider_name == "openrouter":
                    from .providers.openrouter import OpenRouterProvider
                    logger.info("Initializing OpenRouter provider")
                    return OpenRouterProvider(self.config.llm)
                elif provider_name == "mock":
                    # For testing, we'll dynamically import the mock provider
                    try:
                        from tests.fixtures.mock_llm import MockLLMProvider
                        logger.info("Initializing Mock provider")
                        return MockLLMProvider(self.config.llm)
                    except ImportError:
                        error_msg = f"Mock provider not available: {provider_name}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                else:
                    error_msg = f"Unsupported provider: {provider_name}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
        except Exception as e:
            log_exception(e, "LLM provider initialization")
            raise
    
    def generate_response(self, messages: List[Message], use_cache: bool = True, **kwargs) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            use_cache (bool): Whether to use caching (default: True)
            **kwargs: Additional arguments to pass to the provider
            
        Returns:
            LLMResponse: Response from the LLM
        """
        # Add system message if not present
        if not any(m.role == "system" for m in messages):
            messages.insert(0, Message(
                role="system",
                content=self.config.llm.system_prompt or "You are a helpful assistant."
            ))
        
        # Try to get from cache first
        if use_cache:
            cached_response = self.cache.get(messages, **kwargs)
            if cached_response is not None:
                return cached_response
        
        # Generate response
        logger = get_logger()
        try:
            logger.info(f"Generating response with {len(messages)} messages")
            response = self.provider.generate_response(messages, **kwargs)
            logger.info("Response generated successfully")
            
            # Cache the response
            if use_cache:
                ttl = kwargs.get("cache_ttl", None)
                self.cache.set(messages, response, ttl, **kwargs)
            
            return response
        except Exception as e:
            log_exception(e, "LLM response generation")
            raise
    
    async def generate_response_async(self, messages: List[Message], use_cache: bool = True, **kwargs) -> LLMResponse:
        """
        Generate a response from the LLM asynchronously.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            use_cache (bool): Whether to use caching (default: True)
            **kwargs: Additional arguments to pass to the provider
            
        Returns:
            LLMResponse: Response from the LLM
        """
        # Add system message if not present
        if not any(m.role == "system" for m in messages):
            messages.insert(0, Message(
                role="system",
                content=self.config.llm.system_prompt or "You are a helpful assistant."
            ))
        
        # Try to get from cache first
        if use_cache:
            cached_response = self.cache.get(messages, **kwargs)
            if cached_response is not None:
                return cached_response
        
        # Generate response
        logger = get_logger()
        try:
            logger.info(f"Generating async response with {len(messages)} messages")
            # Check if provider has async method, otherwise use sync method
            if hasattr(self.provider, 'generate_response_async'):
                response = await self.provider.generate_response_async(messages, **kwargs)
            else:
                response = self.provider.generate_response(messages, **kwargs)
            logger.info("Async response generated successfully")
            
            # Cache the response
            if use_cache:
                ttl = kwargs.get("cache_ttl", None)
                self.cache.set(messages, response, ttl, **kwargs)
            
            return response
        except Exception as e:
            log_exception(e, "LLM async response generation")
            raise
    
    def stream_response(self, messages: List[Message], **kwargs):
        """
        Stream a response from the LLM.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments to pass to the provider
            
        Yields:
            str: Chunks of the response
        """
        # Add system message if not present
        if not any(m.role == "system" for m in messages):
            messages.insert(0, Message(
                role="system",
                content=self.config.llm.system_prompt or "You are a helpful assistant."
            ))
        
        # Stream response
        logger = get_logger()
        try:
            logger.info(f"Streaming response with {len(messages)} messages")
            response = self.provider.stream_response(messages, **kwargs)
            logger.info("Response streaming started successfully")
            return response
        except Exception as e:
            log_exception(e, "LLM response streaming")
            raise
    
    async def stream_response_async(self, messages: List[Message], **kwargs):
        """
        Stream a response from the LLM asynchronously.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments to pass to the provider
            
        Yields:
            str: Chunks of the response
        """
        # Add system message if not present
        if not any(m.role == "system" for m in messages):
            messages.insert(0, Message(
                role="system",
                content=self.config.llm.system_prompt or "You are a helpful assistant."
            ))
        
        # Stream response
        logger = get_logger()
        try:
            logger.info(f"Streaming async response with {len(messages)} messages")
            # Check if provider has async method, otherwise use sync method
            if hasattr(self.provider, 'stream_response_async'):
                response = await self.provider.stream_response_async(messages, **kwargs)
            else:
                response = self.provider.stream_response(messages, **kwargs)
            logger.info("Async response streaming started successfully")
            return response
        except Exception as e:
            log_exception(e, "LLM async response streaming")
            raise