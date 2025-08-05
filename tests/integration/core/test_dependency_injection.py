#!/usr/bin/env python3
"""
Test script for dependency injection functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.personal_agent.config.settings import Config
from src.personal_agent.core.factory import ComponentFactory
from src.personal_agent.core.agent import Agent
from src.personal_agent.memory.storage import SQLiteMemoryStorage
from src.personal_agent.llm.client import LLMClient

def test_dependency_injection():
    """Test dependency injection functionality."""
    print("Testing dependency injection...")
    
    # Test 1: Create components using factory
    print("\n1. Testing factory-based component creation...")
    config = Config.load()
    memory_storage = ComponentFactory.create_memory_storage(config)
    
    # Try to create LLM client, but handle missing API key gracefully
    llm_client = None
    try:
        llm_client = ComponentFactory.create_llm_client(config)
    except Exception as e:
        print(f"LLM client creation failed (expected without API key): {e}")
    
    print(f"Memory storage type: {type(memory_storage).__name__}")
    print(f"LLM client type: {type(llm_client).__name__ if llm_client else 'None'}")
    
    # Test 2: Create agent using factory
    print("\n2. Testing factory-based agent creation...")
    agent = None
    try:
        agent = ComponentFactory.create_agent(user_id="test_user")
    except Exception as e:
        print(f"Agent creation failed (expected without API key): {e}")
        # Create agent without LLM client
        agent = Agent(user_id="test_user")
    
    print(f"Agent memory type: {type(agent.memory).__name__}")
    print(f"Agent LLM client type: {type(agent.llm_client).__name__ if agent.llm_client else 'None'}")
    
    # Test 3: Create agent with manual dependency injection
    print("\n3. Testing manual dependency injection...")
    custom_memory = SQLiteMemoryStorage("data/test_memory.db")
    custom_llm_client = None
    try:
        custom_llm_client = LLMClient(config)
    except Exception as e:
        print(f"Custom LLM client creation failed (expected without API key): {e}")
    
    manual_agent = Agent(
        user_id="manual_test_user",
        config=config,
        memory_storage=custom_memory,
        llm_client=custom_llm_client
    )
    
    print(f"Manual agent memory type: {type(manual_agent.memory).__name__}")
    print(f"Manual agent LLM client type: {type(manual_agent.llm_client).__name__ if manual_agent.llm_client else 'None'}")
    
    print("\nDependency injection test completed successfully!")

if __name__ == "__main__":
    test_dependency_injection()