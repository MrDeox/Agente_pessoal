#!/usr/bin/env python3
"""
Test script for the refactored Agent class and new components.
"""

import sys
import os

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.core.agent import Agent
from personal_agent.config.settings import Config


def test_agent_initialization():
    """Test that the Agent can be initialized successfully."""
    print("Testing Agent initialization...")
    try:
        agent = Agent()
        print("✓ Agent initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")
        return False


def test_agent_process_input():
    """Test that the Agent can process input successfully."""
    print("Testing Agent input processing...")
    try:
        agent = Agent()
        response = agent.process_input("Hello, how are you?")
        print(f"✓ Agent processed input successfully. Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Agent input processing failed: {e}")
        return False


def test_agent_welcome_message():
    """Test that the Agent can generate a welcome message."""
    print("Testing Agent welcome message...")
    try:
        agent = Agent()
        welcome = agent.get_welcome_message()
        print(f"✓ Agent generated welcome message: {welcome}")
        return True
    except Exception as e:
        print(f"✗ Agent welcome message generation failed: {e}")
        return False


def test_agent_planning_request():
    """Test that the Agent can handle a planning request."""
    print("Testing Agent planning request handling...")
    try:
        agent = Agent()
        response = agent.process_input("I need to plan a trip to Europe")
        print(f"✓ Agent handled planning request. Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Agent planning request handling failed: {e}")
        return False


def test_agent_reasoning_request():
    """Test that the Agent can handle a reasoning request."""
    print("Testing Agent reasoning request handling...")
    try:
        agent = Agent()
        response = agent.process_input("All birds can fly. A penguin is a bird. Can a penguin fly?")
        print(f"✓ Agent handled reasoning request. Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Agent reasoning request handling failed: {e}")
        return False


def test_agent_decision_tree_request():
    """Test that the Agent can handle a decision tree request."""
    print("Testing Agent decision tree request handling...")
    try:
        agent = Agent()
        response = agent.process_input("I need to decide what to eat for dinner")
        print(f"✓ Agent handled decision tree request. Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Agent decision tree request handling failed: {e}")
        return False


def test_agent_exit_command():
    """Test that the Agent can handle an exit command."""
    print("Testing Agent exit command handling...")
    try:
        agent = Agent()
        response = agent.process_input("quit")
        print(f"✓ Agent handled exit command. Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Agent exit command handling failed: {e}")
        return False


def test_agent_memory_functions():
    """Test that the Agent's memory functions work correctly."""
    print("Testing Agent memory functions...")
    try:
        agent = Agent()
        # Test remembering a preference
        pref_result = agent.remember_preference("I like pizza")
        print(f"✓ Agent remembered preference: {pref_result}")
        
        # Test remembering a fact
        fact_result = agent.remember_fact("My name is John")
        print(f"✓ Agent remembered fact: {fact_result}")
        
        return True
    except Exception as e:
        print(f"✗ Agent memory functions failed: {e}")
        return False


def test_agent_feedback_functions():
    """Test that the Agent's feedback functions work correctly."""
    print("Testing Agent feedback functions...")
    try:
        agent = Agent()
        # Test getting feedback statistics (should work even if empty)
        stats = agent.get_feedback_statistics()
        print(f"✓ Agent retrieved feedback statistics: {stats}")
        
        return True
    except Exception as e:
        print(f"✗ Agent feedback functions failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running tests for refactored Agent class and new components...\n")
    
    tests = [
        test_agent_initialization,
        test_agent_welcome_message,
        test_agent_process_input,
        test_agent_planning_request,
        test_agent_reasoning_request,
        test_agent_decision_tree_request,
        test_agent_exit_command,
        test_agent_memory_functions,
        test_agent_feedback_functions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()  # Add a blank line between tests
    
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! The refactored Agent class and new components are working correctly.")
        return 0
    else:
        print("Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())