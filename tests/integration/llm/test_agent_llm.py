#!/usr/bin/env python3
"""
Test script for Agent with LLM integration in Personal Agent

This script tests the agent's ability to use LLM functionality.
"""

import sys
import os
import traceback

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from personal_agent.core.agent import Agent
from personal_agent.config.settings import Config


def test_agent_llm():
    """Test the agent with LLM functionality."""
    print("Testing Agent with LLM Integration...")
    
    try:
        # Create an agent instance
        agent = Agent(user_id="test_user")
        
        # Check if LLM client is available
        if not agent.llm_client:
            print("Warning: LLM client not available. Please set PA_LLM__API_KEY environment variable.")
            print("Export it with: export PA_LLM__API_KEY='your-openai-api-key'")
            return False
        
        print(f"LLM client initialized with provider: {agent.config.llm.provider}")
        print(f"Model: {agent.config.llm.model}")
        
        # Test simple interaction
        print("\nTesting simple interaction...")
        response = agent.process_input("Hello, how are you?")
        print(f"Agent: {response}")
        
        # Test with memory context
        print("\nTesting with memory context...")
        response = agent.process_input("What did I say in my first message?")
        print(f"Agent: {response}")
        
        # Test remembering preferences
        print("\nTesting preference remembering...")
        agent.remember_preference("I like Python programming")
        
        # Test with preference context
        response = agent.process_input("What do you know about my preferences?")
        print(f"Agent: {response}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return False


def main():
    """Main function to run agent LLM tests."""
    print("Personal Agent - Agent with LLM Integration Test")
    print("=" * 50)
    
    # Test agent with LLM
    success = test_agent_llm()
    
    print("\n" + "=" * 50)
    if success:
        print("Agent LLM integration test passed!")
        return 0
    else:
        print("Agent LLM integration test failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())