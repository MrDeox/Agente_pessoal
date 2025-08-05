"""
Base Provider for LLM Integration

This module contains the abstract base class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import List
from ..models import Message, LLMResponse


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config):
        """
        Initialize the provider with configuration.
        
        Args:
            config: Configuration object for the provider
        """
        self.config = config
    
    @abstractmethod
    def generate_response(self, messages: List[Message], **kwargs) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments
            
        Returns:
            LLMResponse: Response from the LLM
        """
        pass
    
    @abstractmethod
    def stream_response(self, messages: List[Message], **kwargs):
        """
        Stream a response from the LLM.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments
            
        Yields:
            str: Chunks of the response
        """
        pass
    
    async def generate_response_async(self, messages: List[Message], **kwargs) -> LLMResponse:
        """
        Generate a response from the LLM asynchronously.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments
            
        Returns:
            LLMResponse: Response from the LLM
            
        Raises:
            NotImplementedError: If not implemented by the provider
        """
        raise NotImplementedError
    
    async def stream_response_async(self, messages: List[Message], **kwargs):
        """
        Stream a response from the LLM asynchronously.
        
        Args:
            messages (List[Message]): List of messages in the conversation
            **kwargs: Additional arguments
            
        Yields:
            str: Chunks of the response
            
        Raises:
            NotImplementedError: If not implemented by the provider
        """
        raise NotImplementedError