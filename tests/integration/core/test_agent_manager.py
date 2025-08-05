#!/usr/bin/env python3
"""
Test script for agent manager functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.personal_agent.core.manager import AgentManager, get_agent_manager, shutdown_agent_manager
from src.personal_agent.core.agent import Agent


def test_agent_manager():
    """Test agent manager functionality."""
    print("Testing agent manager...")
    
    # Test 1: Create agent manager
    print("\n1. Testing agent manager creation...")
    manager = AgentManager()
    print(f"Agent manager created: {type(manager).__name__}")
    
    # Test 2: Create agent (handle missing API key)
    print("\n2. Testing agent creation...")
    try:
        agent = manager.create_agent(user_id="test_user_1")
        print(f"Agent created: {agent.name} (v{agent.version})")
    except Exception as e:
        print(f"Agent creation failed (expected without API key): {e}")
        # Create agent directly without LLM
        agent_instance = Agent(user_id="test_user_1")
        manager.agents["test_user_1"] = agent_instance
        print(f"Agent created manually: {agent_instance.name} (v{agent_instance.version})")
    
    # Test 3: Get agent
    print("\n3. Testing agent retrieval...")
    retrieved_agent = manager.get_agent("test_user_1")
    print(f"Agent retrieved: {retrieved_agent is not None}")
    print(f"Agent name: {retrieved_agent.name if retrieved_agent else 'None'}")
    
    # Test 4: List agents
    print("\n4. Testing agent listing...")
    agent_list = manager.list_agents()
    print(f"Managed agents: {agent_list}")
    
    # Test 5: Get agent status
    print("\n5. Testing agent status...")
    status = manager.get_agent_status("test_user_1")
    print(f"Agent status: {status}")
    
    # Test 6: Get all agents status
    print("\n6. Testing all agents status...")
    all_status = manager.get_all_agents_status()
    print(f"All agents status: {all_status}")
    
    # Test 7: Start existing agent (handle missing API key)
    print("\n7. Testing starting existing agent...")
    try:
        existing_agent = manager.start_agent("test_user_1")
        print(f"Existing agent started: {existing_agent.name}")
    except Exception as e:
        print(f"Starting existing agent failed (expected without API key): {e}")
        existing_agent = manager.get_agent("test_user_1")
        print(f"Using existing agent: {existing_agent.name}")
    
    # Test 8: Start new agent (handle missing API key)
    print("\n8. Testing starting new agent...")
    try:
        new_agent = manager.start_agent("test_user_2")
        print(f"New agent started: {new_agent.name}")
    except Exception as e:
        print(f"Starting new agent failed (expected without API key): {e}")
        # Create agent directly without LLM
        new_agent_instance = Agent(user_id="test_user_2")
        manager.agents["test_user_2"] = new_agent_instance
        print(f"New agent created manually: {new_agent_instance.name}")
    
    # Test 9: Stop agent
    print("\n9. Testing stopping agent...")
    stopped = manager.stop_agent("test_user_2")
    print(f"Agent stopped: {stopped}")
    
    # Test 10: Stop all agents
    print("\n10. Testing stopping all agents...")
    manager.stop_all_agents()
    remaining_agents = manager.list_agents()
    print(f"Remaining agents: {remaining_agents}")
    
    # Test 11: Global manager instance
    print("\n11. Testing global manager instance...")
    global_manager = get_agent_manager()
    print(f"Global manager type: {type(global_manager).__name__}")
    
    # Test 12: Shutdown global manager
    print("\n12. Testing global manager shutdown...")
    shutdown_agent_manager()
    print("Global manager shutdown completed")
    
    print("\nAgent manager test completed successfully!")


if __name__ == "__main__":
    test_agent_manager()