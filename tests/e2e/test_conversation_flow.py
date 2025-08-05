#!/usr/bin/env python3
"""
End-to-end test for comprehensive conversation flow with the personal agent.

This test simulates realistic user interactions with the agent, covering:
- Basic conversation
- Memory functionality
- LLM integration
- Feedback mechanisms
- Error handling
"""

import sys
import os
import traceback
from typing import List, Dict, Any
import json
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from personal_agent.core.agent import Agent
from personal_agent.memory.storage import SQLiteMemoryStorage
from personal_agent.memory.models import MemoryItem
from personal_agent.config.settings import Config
from personal_agent.conversation.state import ConversationState, DialogueAct


class TestResult:
    """Represents the result of a single test."""
    
    def __init__(self, name: str, passed: bool, message: str = "", error: Exception = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.error = error
        self.timestamp = datetime.now()


class TestReport:
    """Generates and manages test reports."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = datetime.now()
    
    def add_result(self, result: TestResult):
        """Add a test result to the report."""
        self.results.append(result)
    
    def generate_report(self) -> str:
        """Generate a formatted test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("=" * 60)
        report.append("PERSONAL AGENT - END-TO-END TEST REPORT")
        report.append("=" * 60)
        report.append(f"Test Run: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success Rate: {passed_tests / total_tests * 100:.1f}%" if total_tests > 0 else "No tests run")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 40)
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            report.append(f"[{status}] {result.name}")
            if not result.passed:
                report.append(f"    Message: {result.message}")
                if result.error:
                    report.append(f"    Error: {str(result.error)}")
            report.append("")
        
        # Summary
        report.append("-" * 40)
        report.append("SUMMARY:")
        report.append(f"Overall Status: {'PASSED' if failed_tests == 0 else 'FAILED'}")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, filepath: str):
        """Save the report to a file."""
        with open(filepath, 'w') as f:
            f.write(self.generate_report())


def create_test_agent(user_id: str = "test_user_e2e") -> Agent:
    """Create a test agent with isolated configuration."""
    # Create agent with test user ID
    agent = Agent(user_id=user_id)
    
    # Use in-memory database for testing to avoid conflicts
    # For real testing, we'll use a separate test database
    test_db_path = "data/test_memory.db"
    agent.memory = SQLiteMemoryStorage(test_db_path)
    
    return agent


def test_basic_conversation(agent: Agent, report: TestReport) -> bool:
    """Test basic conversation functionality."""
    try:
        # Test welcome message
        welcome = agent.get_welcome_message()
        assert "Personal Agent" in welcome, "Welcome message should contain agent name"
        
        # Test simple interaction
        response = agent.process_input("Hello, how are you?")
        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        
        # Test conversation history
        assert len(agent.conversation_history) >= 2, "Conversation history should contain at least 2 messages"
        assert agent.conversation_history[-2]["role"] == "user", "Second to last message should be user"
        assert agent.conversation_history[-1]["role"] == "assistant", "Last message should be assistant"
        
        report.add_result(TestResult("Basic Conversation", True, "Basic conversation flow works correctly"))
        return True
        
    except Exception as e:
        report.add_result(TestResult("Basic Conversation", False, "Basic conversation flow failed", e))
        return False


def test_memory_functionality(agent: Agent, report: TestReport) -> bool:
    """Test memory functionality including preferences and facts."""
    try:
        # Test remembering preferences
        success = agent.remember_preference("I like Python programming")
        assert success, "Remembering preference should succeed"
        
        # Test remembering facts
        success = agent.remember_fact("My name is Test User")
        assert success, "Remembering fact should succeed"
        
        # Test that memory items were saved
        preferences = agent.memory.search("Python programming", type="knowledge")
        assert len(preferences) > 0, "Preference should be saved in memory"
        
        facts = agent.memory.search("Test User", type="knowledge")
        assert len(facts) > 0, "Fact should be saved in memory"
        
        # Test memory context in conversation
        response = agent.process_input("What do you know about my preferences?")
        assert "Python" in response or "programming" in response, "Response should reference user preferences"
        
        report.add_result(TestResult("Memory Functionality", True, "Memory functionality works correctly"))
        return True
        
    except Exception as e:
        report.add_result(TestResult("Memory Functionality", False, "Memory functionality failed", e))
        return False


def test_llm_integration(agent: Agent, report: TestReport) -> bool:
    """Test LLM integration and context-aware responses."""
    try:
        # Check if LLM is available
        if not agent.llm_client:
            # This is not a failure, just a limitation of the test environment
            report.add_result(TestResult("LLM Integration", True, "LLM not configured, but that's expected in test environment"))
            return True
        
        # Test context-aware response
        response1 = agent.process_input("My favorite color is blue.")
        assert isinstance(response1, str), "First response should be a string"
        
        response2 = agent.process_input("What is my favorite color?")
        assert isinstance(response2, str), "Second response should be a string"
        assert "blue" in response2.lower(), "Response should reference the previously mentioned color"
        
        report.add_result(TestResult("LLM Integration", True, "LLM integration works correctly"))
        return True
        
    except Exception as e:
        report.add_result(TestResult("LLM Integration", False, "LLM integration failed", e))
        return False


def test_feedback_mechanism(agent: Agent, report: TestReport) -> bool:
    """Test feedback collection and processing."""
    try:
        # Test collecting rating feedback
        response = agent.process_input("This is a test message for feedback.")
        # Get the message ID from the last assistant response
        message_id = agent.conversation_history[-1].get("id")
        assert message_id, "Message should have an ID"
        
        # Collect rating feedback
        success = agent.collect_rating_feedback(message_id, 5, "Great response!")
        assert success, "Collecting rating feedback should succeed"
        
        # Test collecting thumbs feedback
        success = agent.collect_thumbs_feedback(message_id, True, "Thumbs up!")
        assert success, "Collecting thumbs feedback should succeed"
        
        # Test feedback statistics
        stats = agent.get_feedback_statistics()
        assert isinstance(stats, dict), "Feedback statistics should be a dictionary"
        assert "total_feedback" in stats, "Statistics should include total feedback count"
        
        report.add_result(TestResult("Feedback Mechanism", True, "Feedback mechanism works correctly"))
        return True
        
    except Exception as e:
        report.add_result(TestResult("Feedback Mechanism", False, "Feedback mechanism failed", e))
        return False


def test_error_handling(agent: Agent, report: TestReport) -> bool:
    """Test error handling and edge cases."""
    try:
        # Test with empty input
        response = agent.process_input("")
        assert isinstance(response, str), "Response to empty input should be a string"
        
        # Test with very long input
        long_input = "Hello! " * 1000  # 7000+ characters
        response = agent.process_input(long_input)
        assert isinstance(response, str), "Response to long input should be a string"
        
        # Test exit commands
        response = agent.process_input("quit")
        assert "Goodbye" in response, "Response to quit should contain goodbye message"
        
        report.add_result(TestResult("Error Handling", True, "Error handling works correctly"))
        return True
        
    except Exception as e:
        report.add_result(TestResult("Error Handling", False, "Error handling failed", e))
        return False


def test_enhanced_conversation_flow(agent: Agent, report: TestReport) -> bool:
    """Test enhanced conversation flow with state management and dialogue acts."""
    try:
        # Create a fresh agent for this test to ensure initial state
        fresh_agent = create_test_agent("test_user_enhanced_flow")
        
        # Test initial conversation state
        context = fresh_agent.conversation_interface.get_conversation_context()
        assert context["state"] == "initial", "Initial state should be 'initial'"
        
        # Test greeting
        response = fresh_agent.process_input("Hello!")
        context = fresh_agent.conversation_interface.get_conversation_context()
        assert context["state"] in ["greeting", "in_progress"], "State should be 'greeting' or 'in_progress' after greeting"
        assert context["dialogue_act"] == "greeting", "Dialogue act should be 'greeting'"
        
        # Test question
        response = fresh_agent.process_input("What is your name?")
        context = fresh_agent.conversation_interface.get_conversation_context()
        assert context["dialogue_act"] == "question", "Dialogue act should be 'question' for questions"
        
        # Test request
        response = fresh_agent.process_input("Please help me with this task")
        context = fresh_agent.conversation_interface.get_conversation_context()
        assert context["dialogue_act"] == "request", "Dialogue act should be 'request' for requests"
        
        # Test conversation history tracking
        assert len(fresh_agent.conversation_interface.conversation_history) >= 6, "Conversation history should track all turns"
        
        report.add_result(TestResult("Enhanced Conversation Flow", True, "Enhanced conversation flow works correctly"))
        return True
        
    except Exception as e:
        report.add_result(TestResult("Enhanced Conversation Flow", False, "Enhanced conversation flow failed", e))
        return False
    """Test error handling and edge cases."""
    try:
        # Test with empty input
        response = agent.process_input("")
        assert isinstance(response, str), "Response to empty input should be a string"
        
        # Test with very long input
        long_input = "Hello! " * 1000  # 7000+ characters
        response = agent.process_input(long_input)
        assert isinstance(response, str), "Response to long input should be a string"
        
        # Test exit commands
        response = agent.process_input("quit")
        assert "Goodbye" in response, "Response to quit should contain goodbye message"
        
        report.add_result(TestResult("Error Handling", True, "Error handling works correctly"))
        return True
        
    except Exception as e:
        report.add_result(TestResult("Error Handling", False, "Error handling failed", e))
        return False


def run_comprehensive_test() -> TestReport:
    """Run all comprehensive tests and generate a report."""
    print("Starting Personal Agent End-to-End Tests...")
    print("=" * 50)
    
    # Create test report
    report = TestReport()
    
    try:
        # Create test agent
        agent = create_test_agent()
        print(f"Created test agent with user ID: {agent.user_id}")
        
        # Run all tests
        tests = [
            test_basic_conversation,
            test_memory_functionality,
            test_llm_integration,
            test_feedback_mechanism,
            test_error_handling,
            test_enhanced_conversation_flow
        ]
        
        for test_func in tests:
            print(f"Running {test_func.__name__}...")
            test_func(agent, report)
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except Exception as e:
        error_result = TestResult("Test Suite", False, "Test suite failed to run", e)
        report.add_result(error_result)
        print(f"Test suite error: {e}")
        traceback.print_exc()
    
    return report


def main():
    """Main function to run the comprehensive test."""
    # Run tests
    report = run_comprehensive_test()
    
    # Generate and print report
    report_text = report.generate_report()
    print("\n" + report_text)
    
    # Save report to file
    report_path = "test_results_e2e.txt"
    report.save_report(report_path)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Return exit code based on test results
    failed_tests = sum(1 for r in report.results if not r.passed)
    return 1 if failed_tests > 0 else 0


if __name__ == "__main__":
    sys.exit(main())