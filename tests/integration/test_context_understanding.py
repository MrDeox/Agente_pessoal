#!/usr/bin/env python3
"""
Test script for the improved context understanding capabilities.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.core.agent import Agent
from personal_agent.config.settings import Config


def test_context_understanding():
    """Test the improved context understanding capabilities."""
    print("Testing improved context understanding capabilities...")
    
    # Create an agent instance
    config = Config.load()
    agent = Agent(user_id="test_user", config=config)
    
    print(f"Agent initialized: {agent.name} v{agent.version}")
    print()
    
    # Test 1: Basic conversation with entity extraction
    print("Test 1: Basic conversation with entity extraction")
    print("-" * 50)
    
    user_input = "My name is John Smith and I live in New York City. I work at ABC Corporation."
    response = agent.process_input(user_input)
    print(f"User: {user_input}")
    print(f"Agent: {response}")
    print()
    
    # Test 2: Follow-up question that requires context
    print("Test 2: Follow-up question that requires context")
    print("-" * 50)
    
    user_input = "Where do I work?"
    response = agent.process_input(user_input)
    print(f"User: {user_input}")
    print(f"Agent: {response}")
    print()
    
    # Test 3: Context relevance scoring
    print("Test 3: Context relevance scoring")
    print("-" * 50)
    
    # Add some knowledge items
    agent.remember_fact("John Smith is a software engineer")
    agent.remember_fact("ABC Corporation is a technology company")
    agent.remember_preference("John Smith prefers Python programming language")
    
    user_input = "What programming language does John prefer?"
    response = agent.process_input(user_input)
    print(f"User: {user_input}")
    print(f"Agent: {response}")
    print()
    
    # Test 4: Complex context with relationships
    print("Test 4: Complex context with relationships")
    print("-" * 50)
    
    user_input = "Tell me about my job and the company I work for."
    response = agent.process_input(user_input)
    print(f"User: {user_input}")
    print(f"Agent: {response}")
    print()
    
    # Test 5: Context-aware prompt engineering
    print("Test 5: Context-aware prompt engineering")
    print("-" * 50)
    
    user_input = "Based on our conversation, what can you tell me about myself?"
    response = agent.process_input(user_input)
    print(f"User: {user_input}")
    print(f"Agent: {response}")
    print()
    
    print("Context understanding tests completed!")


if __name__ == "__main__":
    test_context_understanding()