#!/usr/bin/env python3
"""
Test script for LLM integration in Personal Agent

This script tests the LLM integration functionality.
"""

import sys
import os
import traceback

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.config.settings import Config
from personal_agent.llm.client import LLMClient, Message
from personal_agent.llm.exceptions import LLMException


def test_llm_client():
    """Test the LLM client functionality."""
    print("Testing LLM Client...")
    
    try:
        # Load configuration
        config = Config.load()
        
        # Check if API key is set
        if not config.llm.api_key:
            print("Warning: API key not set. Please set PA_LLM__API_KEY environment variable.")
            print("Export it with: export PA_LLM__API_KEY='your-openai-api-key'")
            return False
        
        # Initialize LLM client
        print(f"Initializing LLM client with provider: {config.llm.provider}")
        llm_client = LLMClient(config)
        
        # Test simple message
        print("Sending test message to LLM...")
        messages = [
            Message(role="user", content="Hello, how are you?")
        ]
        
        response = llm_client.generate_response(messages)
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")
        
        return True
        
    except LLMException as e:
        print(f"LLM Error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return False


def test_conversation():
    """Test a simple conversation."""
    print("\nTesting Conversation...")
    
    try:
        # Load configuration
        config = Config.load()
        
        # Check if API key is set
        if not config.llm.api_key:
            print("Warning: API key not set. Please set PA_LLM__API_KEY environment variable.")
            return False
        
        # Initialize LLM client
        llm_client = LLMClient(config)
        
        # Test conversation
        messages = [
            Message(role="user", content="What is the capital of France?"),
        ]
        
        response = llm_client.generate_response(messages)
        print(f"Q: {messages[0].content}")
        print(f"A: {response.content}")
        
        # Continue conversation
        messages.append(Message(role="assistant", content=response.content))
        messages.append(Message(role="user", content="What is the population of that city?"))
        
        response = llm_client.generate_response(messages)
        print(f"Q: {messages[-1].content}")
        print(f"A: {response.content}")
        
        return True
        
    except LLMException as e:
        print(f"LLM Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return False


def main():
    """Main function to run LLM tests."""
    print("Personal Agent - LLM Integration Test")
    print("=" * 40)
    
    # Test LLM client
    success1 = test_llm_client()
    
    # Test conversation
    success2 = test_conversation()
    
    print("\n" + "=" * 40)
    if success1 and success2:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())