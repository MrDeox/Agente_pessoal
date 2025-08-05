#!/usr/bin/env python3
"""
Test script for OpenRouter integration.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.llm.client import LLMClient
from personal_agent.llm.models import Message
from personal_agent.config.settings import Config


def test_openrouter():
    """Test OpenRouter integration."""
    print("Testing OpenRouter Integration")
    print("=" * 35)
    
    # Create a configuration for OpenRouter
    config = Config()
    config.llm.provider = "openrouter"
    config.llm.model = "qwen/qwen3-coder:free"
    config.llm.api_key = os.getenv("PA_LLM__API_KEY", "test-key-placeholder")
    config.llm.temperature = 0.7
    
    try:
        # Initialize the LLM client
        client = LLMClient(config)
        print("✓ LLM client initialized successfully")
        
        # Create a test message
        messages = [
            Message(role="user", content="Hello, what model are you?")
        ]
        
        # Generate a response
        print("Generating response...")
        response = client.generate_response(messages)
        print(f"✓ Response generated successfully")
        print(f"Model: {response.model}")
        print(f"Response: {response.content}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    test_openrouter()