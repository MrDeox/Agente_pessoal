#!/usr/bin/env python3
"""
Test script for the enhanced conversation flow capabilities.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.personal_agent.core.agent import Agent
from src.personal_agent.conversation.state import ConversationState, DialogueAct
from src.personal_agent.conversation.dialogue_act import DialogueActRecognizer


def test_dialogue_act_recognition():
    """Test dialogue act recognition functionality."""
    print("Testing Dialogue Act Recognition...")
    
    recognizer = DialogueActRecognizer()
    
    test_cases = [
        ("Hello, how are you?", DialogueAct.GREETING),
        ("What is the weather like today?", DialogueAct.QUESTION),
        ("Please help me with this task", DialogueAct.REQUEST),
        ("Yes, that's correct", DialogueAct.CONFIRMATION),
        ("No, that's not right", DialogueAct.CONFIRMATION),
        ("I don't understand what you mean", DialogueAct.CLARIFICATION),
        ("Thanks for your help", DialogueAct.ACKNOWLEDGMENT),
        ("Goodbye, see you later", DialogueAct.CLOSING),
        ("This is just a statement", DialogueAct.STATEMENT)
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, expected_act in test_cases:
        recognized_act, confidence = recognizer.recognize_act(text)
        if recognized_act == expected_act:
            print(f"✓ '{text}' -> {recognized_act.value} (confidence: {confidence:.2f})")
            passed += 1
        else:
            print(f"✗ '{text}' -> {recognized_act.value} (expected: {expected_act.value}, confidence: {confidence:.2f})")
    
    print(f"\nDialogue Act Recognition: {passed}/{total} tests passed")
    return passed == total


def test_conversation_state_management():
    """Test conversation state management functionality."""
    print("\nTesting Conversation State Management...")
    
    user_id = "test_user"
    agent = Agent(user_id=user_id)
    
    # Test initial state
    context = agent.conversation_interface.get_conversation_context()
    if context["state"] == "initial":
        print("✓ Initial state is correct")
        passed_initial = True
    else:
        print(f"✗ Initial state is {context['state']}, expected 'initial'")
        passed_initial = False
    
    # Test processing a greeting
    agent.process_input("Hello there!")
    context = agent.conversation_interface.get_conversation_context()
    if context["state"] == "greeting" or context["state"] == "in_progress":
        print("✓ State transitioned correctly after greeting")
        passed_greeting = True
    else:
        print(f"✗ State is {context['state']} after greeting, expected 'greeting' or 'in_progress'")
        passed_greeting = False
    
    # Test processing a question
    agent.process_input("What is your name?")
    context = agent.conversation_interface.get_conversation_context()
    if context["dialogue_act"] == "question":
        print("✓ Dialogue act recognized correctly for question")
        passed_question = True
    else:
        print(f"✗ Dialogue act is {context['dialogue_act']} for question, expected 'question'")
        passed_question = False
    
    # Test processing a closing statement
    agent.process_input("Goodbye!")
    context = agent.conversation_interface.get_conversation_context()
    if context["state"] == "closing":
        print("✓ State transitioned correctly for closing")
        passed_closing = True
    else:
        print(f"✗ State is {context['state']} for closing, expected 'closing'")
        passed_closing = False
    
    passed = sum([passed_initial, passed_greeting, passed_question, passed_closing])
    total = 4
    print(f"\nConversation State Management: {passed}/{total} tests passed")
    return passed == total


def test_response_generation():
    """Test enhanced response generation functionality."""
    print("\nTesting Enhanced Response Generation...")
    
    user_id = "test_user"
    agent = Agent(user_id=user_id)
    
    # Test greeting response
    response = agent.process_input("Hello!")
    if isinstance(response, str) and len(response) > 0:
        print("✓ Greeting response generated successfully")
        passed_greeting = True
    else:
        print("✗ Greeting response failed")
        passed_greeting = False
    
    # Test question response
    response = agent.process_input("What can you help me with?")
    if isinstance(response, str) and len(response) > 0:
        print("✓ Question response generated successfully")
        passed_question = True
    else:
        print("✗ Question response failed")
        passed_question = False
    
    # Test request response
    response = agent.process_input("Please tell me a joke")
    if isinstance(response, str) and len(response) > 0:
        print("✓ Request response generated successfully")
        passed_request = True
    else:
        print("✗ Request response failed")
        passed_request = False
    
    passed = sum([passed_greeting, passed_question, passed_request])
    total = 3
    print(f"\nEnhanced Response Generation: {passed}/{total} tests passed")
    return passed == total


def test_integration():
    """Test integration of all conversation flow components."""
    print("\nTesting Integration of Conversation Flow Components...")
    
    user_id = "test_user"
    agent = Agent(user_id=user_id)
    
    # Simulate a complete conversation flow
    conversation = [
        "Hello!",
        "What is your name?",
        "Can you help me with something?",
        "I don't understand that",
        "Thanks for explaining",
        "Goodbye!"
    ]
    
    all_passed = True
    for i, message in enumerate(conversation):
        response = agent.process_input(message)
        context = agent.conversation_interface.get_conversation_context()
        
        if isinstance(response, str) and len(response) > 0:
            print(f"✓ Turn {i+1}: '{message}' -> Response generated (State: {context['state']}, Act: {context['dialogue_act']})")
        else:
            print(f"✗ Turn {i+1}: '{message}' -> Response failed")
            all_passed = False
    
    if all_passed:
        print("✓ Complete conversation flow test passed")
    else:
        print("✗ Complete conversation flow test failed")
    
    return all_passed


def main():
    """Main function to run all tests."""
    print("Running Enhanced Conversation Flow Tests")
    print("=" * 40)
    
    tests = [
        test_dialogue_act_recognition,
        test_conversation_state_management,
        test_response_generation,
        test_integration
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        if test():
            passed_tests += 1
        print()  # Add spacing between tests
    
    print("=" * 40)
    print(f"Overall Results: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("All tests passed! 🎉")
        return 0
    else:
        print("Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())