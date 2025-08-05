#!/usr/bin/env python3
"""
Test script for advanced reasoning and decision-making capabilities.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.core.agent import Agent
from personal_agent.config.settings import Config


def test_planning_capability():
    """Test the planning capability."""
    print("=== Testing Planning Capability ===")
    
    # Create an agent
    agent = Agent(user_id="test_user")
    
    # Test creating a plan
    task_description = "Plan a birthday party for my friend"
    print(f"Creating plan for: {task_description}")
    
    plan = agent.create_plan(task_description)
    print(f"Plan created with ID: {plan.id}")
    print(f"Plan description: {plan.description}")
    print("Subtasks:")
    for i, subtask in enumerate(plan.subtasks, 1):
        print(f"  {i}. {subtask.description}")
    
    # Test getting plan status
    status = agent.get_plan_status(plan.id)
    print(f"Plan status: {status}")
    
    print()


def test_reasoning_capability():
    """Test the reasoning capability."""
    print("=== Testing Reasoning Capability ===")
    
    # Create an agent
    agent = Agent(user_id="test_user")
    
    # Test reasoning
    premises = [
        "All mammals are warm-blooded",
        "All dogs are mammals",
        "My pet is a dog"
    ]
    
    print("Reasoning with premises:")
    for premise in premises:
        print(f"  - {premise}")
    
    conclusion = agent.reason(premises, "deductive")
    print(f"Conclusion: {conclusion}")
    
    print()


def test_decision_making_capability():
    """Test the decision making capability."""
    print("=== Testing Decision Making Capability ===")
    
    # Create an agent
    agent = Agent(user_id="test_user")
    
    # Test making a decision
    problem = "Which programming language should I learn next?"
    options = [
        "Python - Great for data science and machine learning",
        "JavaScript - Essential for web development",
        "Rust - High performance and memory safety",
        "Go - Excellent for cloud and network services"
    ]
    constraints = [
        "Limited time to learn (2 hours per week)",
        "Want to focus on career growth"
    ]
    preferences = [
        "Interested in web development",
        "Want good job prospects"
    ]
    
    print(f"Problem: {problem}")
    print("Options:")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print("Constraints:")
    for constraint in constraints:
        print(f"  - {constraint}")
    print("Preferences:")
    for preference in preferences:
        print(f"  - {preference}")
    
    decision = agent.make_decision(problem, options, constraints, preferences)
    print(f"Decision: {decision}")
    
    print()


def test_decision_tree_capability():
    """Test the decision tree capability."""
    print("=== Testing Decision Tree Capability ===")
    
    # Create an agent
    agent = Agent(user_id="test_user")
    
    # List available decision trees
    trees = agent.list_decision_trees()
    print("Available decision trees:")
    for tree in trees:
        print(f"  - {tree['name']} (ID: {tree['id']})")
    
    if trees:
        # Test executing a decision tree
        tree_id = trees[0]["id"]
        print(f"\nExecuting decision tree: {trees[0]['name']}")
        
        # For this test, we'll provide some answers
        # In a real scenario, these would come from user input
        answers = ["Yes"]  # Example answer to the first question
        
        result = agent.execute_decision_tree(tree_id, answers)
        print(f"Decision tree result: {result}")
    
    print()


def test_user_input_processing():
    """Test processing user input with advanced capabilities."""
    print("=== Testing User Input Processing ===")
    
    # Create an agent
    agent = Agent(user_id="test_user")
    
    # Test inputs that should trigger different capabilities
    test_inputs = [
        "I need to plan a vacation to Europe",
        "If all birds can fly and penguins are birds, can penguins fly?",
        "I need to decide between two job offers",
        "Hello, how are you today?"
    ]
    
    for user_input in test_inputs:
        print(f"User input: {user_input}")
        response = agent.process_input(user_input)
        print(f"Agent response: {response}")
        print()


def main():
    """Main function to run all tests."""
    print("Testing Advanced Reasoning and Decision-Making Capabilities")
    print("=" * 60)
    
    try:
        test_planning_capability()
        test_reasoning_capability()
        test_decision_making_capability()
        test_decision_tree_capability()
        test_user_input_processing()
        
        print("All tests completed successfully!")
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()