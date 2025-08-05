"""
Mock LLM Client for Testing

This module provides mock implementations of LLM clients for testing without API keys.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from src.personal_agent.llm.models import Message
from src.personal_agent.llm.client import LLMClient
from src.personal_agent.config.settings import Config, LLMConfig


class MockLLMProvider:
    """Mock LLM provider for testing."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.call_history = []
    
    def generate_response(self, messages: List[Message], **kwargs) -> Message:
        """Generate a mock response."""
        # Record the call for testing
        self.call_history.append({
            'messages': messages,
            'kwargs': kwargs,
            'timestamp': datetime.now()
        })
        
        # Return a predictable response based on input
        if messages:
            last_message = messages[-1]
            if 'planning' in last_message.content.lower():
                response_content = "Here's a planning response: I'll help you plan this task step by step."
            elif 'reasoning' in last_message.content.lower():
                response_content = "Here's a reasoning response: Based on the information provided, I recommend this approach."
            elif 'decision' in last_message.content.lower():
                response_content = "Here's a decision response: After considering the options, the best choice is option A."
            elif 'hello' in last_message.content.lower():
                response_content = "Hello! I'm your personal assistant. How can I help you today?"
            elif 'goodbye' in last_message.content.lower() or 'exit' in last_message.content.lower():
                response_content = "Goodbye! It was nice talking with you."
            else:
                response_content = f"Mock response to: {last_message.content[:50]}..."
        else:
            response_content = "Mock response: I'm a test LLM client."
        
        # Return a Message object
        return Message(role="assistant", content=response_content)


class MockLLMClient(LLMClient):
    """Mock LLM client that doesn't require API keys."""
    
    def __init__(self, config: Config = None):
        if config is None:
            config = Config()
            config.llm.provider = "mock"
            config.llm.api_key = "mock-key"
        
        # Don't call super().__init__() to avoid real LLM initialization
        self.config = config
        self.provider = MockLLMProvider(config.llm)
        self.call_history = []
    
    def generate_response(self, messages: List[Message], **kwargs) -> Message:
        """Generate a mock response."""
        response = self.provider.generate_response(messages, **kwargs)
        
        # Record the call
        self.call_history.append({
            'messages': messages,
            'response': response.content if hasattr(response, 'content') else str(response),
            'timestamp': datetime.now()
        })
        
        return response
    
    def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a mock completion."""
        message = Message(role="user", content=prompt)
        return self.generate_response([message], **kwargs)
    
    def get_call_history(self) -> List[Dict[str, Any]]:
        """Get the history of calls made to this mock client."""
        return self.call_history.copy()
    
    def clear_history(self):
        """Clear the call history."""
        self.call_history.clear()
        if hasattr(self.provider, 'call_history'):
            self.provider.call_history.clear()


def create_mock_llm_client(config: Config = None) -> MockLLMClient:
    """Create a mock LLM client for testing."""
    return MockLLMClient(config)


def create_test_config(api_key: str = "test-key") -> Config:
    """Create a test configuration."""
    config = Config()
    config.llm.api_key = api_key
    config.llm.provider = "mock"
    config.memory.database_path = "data/test_memory.db"
    config.debug = True
    return config