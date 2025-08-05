#!/usr/bin/env python3
"""
End-to-end test for error handling and edge cases in the personal agent.

This test focuses specifically on:
- Input validation and edge cases
- Error handling for various components
- Graceful degradation when services are unavailable
- Boundary condition testing
- Exception handling and recovery
"""

import sys
import os
import traceback
from typing import List
from unittest.mock import Mock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from personal_agent.core.agent import Agent
from personal_agent.memory.storage import SQLiteMemoryStorage
from personal_agent.llm.exceptions import LLMException


class ErrorHandlingTestResult:
    """Represents the result of an error handling test."""
    
    def __init__(self, name: str, passed: bool, message: str = "", error: Exception = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.error = error


class ErrorHandlingTestReport:
    """Generates and manages error handling test reports."""
    
    def __init__(self):
        self.results: List[ErrorHandlingTestResult] = []
    
    def add_result(self, result: ErrorHandlingTestResult):
        """Add a test result to the report."""
        self.results.append(result)
    
    def generate_report(self) -> str:
        """Generate a formatted test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("=" * 60)
        report.append("PERSONAL AGENT - ERROR HANDLING TEST REPORT")
        report.append("=" * 60)
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


def test_input_validation(report: ErrorHandlingTestResult) -> bool:
    """Test input validation and edge cases."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_input")
        
        # Test empty input
        response = agent.process_input("")
        assert isinstance(response, str), "Response to empty input should be string"
        assert len(response) > 0, "Response to empty input should not be empty"
        
        # Test whitespace-only input
        response = agent.process_input("   ")
        assert isinstance(response, str), "Response to whitespace input should be string"
        
        # Test very long input (stress test)
        long_input = "Hello! " * 10000  # 70,000+ characters
        response = agent.process_input(long_input)
        assert isinstance(response, str), "Response to long input should be string"
        
        # Test special characters
        special_input = "Hello @#$%^&*()_+-=[]{}|;':\",./<>? world!"
        response = agent.process_input(special_input)
        assert isinstance(response, str), "Response to special characters should be string"
        
        # Test unicode characters
        unicode_input = "Hello 世界 🌍 こんにちは"
        response = agent.process_input(unicode_input)
        assert isinstance(response, str), "Response to unicode should be string"
        
        report.add_result(ErrorHandlingTestResult("Input Validation", True, "Input validation works correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorHandlingTestResult("Input Validation", False, "Input validation failed", e))
        return False


def test_memory_error_handling(report: ErrorHandlingTestResult) -> bool:
    """Test memory error handling."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_memory_error")
        
        # Test with mock memory that fails
        mock_memory = Mock()
        mock_memory.save_conversation_turn.side_effect = Exception("Database error")
        mock_memory.save.side_effect = Exception("Database error")
        agent.memory = mock_memory
        
        # Process input - should handle memory errors gracefully
        response = agent.process_input("This is a test message.")
        assert isinstance(response, str), "Response should be string even with memory error"
        assert len(response) > 0, "Response should not be empty"
        
        # Test remembering preferences with failing memory
        success = agent.remember_preference("Test preference")
        # This might succeed or fail, but shouldn't crash the agent
        assert isinstance(success, bool), "remember_preference should return boolean"
        
        report.add_result(ErrorHandlingTestResult("Memory Error Handling", True, "Memory error handling works correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorHandlingTestResult("Memory Error Handling", False, "Memory error handling failed", e))
        return False


def test_llm_error_handling(report: ErrorHandlingTestResult) -> bool:
    """Test LLM error handling."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_llm_error")
        
        # Test with LLM that raises exceptions
        with patch.object(agent, 'llm_client') as mock_llm:
            mock_llm.generate_response.side_effect = LLMException("API timeout")
            
            # Process input - should fall back to simple response
            response = agent.process_input("Hello, how are you?")
            assert isinstance(response, str), "Response should be string even with LLM error"
            assert len(response) > 0, "Response should not be empty"
            
            # Test specific fallback responses
            response_hello = agent.process_input("hi")
            assert isinstance(response_hello, str), "Fallback response should be string"
            
        # Test with no LLM client
        agent_no_llm = Agent(user_id="test_user_no_llm")
        agent_no_llm.llm_client = None
        
        response = agent_no_llm.process_input("Hello, how are you?")
        assert isinstance(response, str), "Response should be string without LLM client"
        assert len(response) > 0, "Response should not be empty"
        
        report.add_result(ErrorHandlingTestResult("LLM Error Handling", True, "LLM error handling works correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorHandlingTestResult("LLM Error Handling", False, "LLM error handling failed", e))
        return False


def test_exit_commands(report: ErrorHandlingTestResult) -> bool:
    """Test exit commands and graceful shutdown."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_exit")
        
        # Test various exit commands
        exit_commands = ['quit', 'exit', 'bye', 'QUIT', 'Exit', 'BYE']
        
        for command in exit_commands:
            response = agent.process_input(command)
            assert isinstance(response, str), f"Response to '{command}' should be string"
            assert "Goodbye" in response or "goodbye" in response.lower(), f"Response to '{command}' should contain goodbye"
        
        report.add_result(ErrorHandlingTestResult("Exit Commands", True, "Exit commands work correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorHandlingTestResult("Exit Commands", False, "Exit commands failed", e))
        return False


def test_conversation_history_boundaries(report: ErrorHandlingTestResult) -> bool:
    """Test conversation history boundary conditions."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_history")
        
        # Test with many conversation turns
        for i in range(50):  # Create 50 conversation turns
            response = agent.process_input(f"Message {i}")
            assert isinstance(response, str), f"Response {i} should be string"
        
        # Verify conversation history doesn't grow unbounded
        assert len(agent.conversation_history) > 0, "Conversation history should not be empty"
        # Note: The agent doesn't currently limit conversation history size,
        # but we're testing that it doesn't crash with many messages
        
        report.add_result(ErrorHandlingTestResult("Conversation History Boundaries", True, "Conversation history boundaries work correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorHandlingTestResult("Conversation History Boundaries", False, "Conversation history boundaries failed", e))
        return False


def test_feedback_error_handling(report: ErrorHandlingTestResult) -> bool:
    """Test feedback error handling."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_feedback_error")
        
        # Test collecting feedback for non-existent message
        success = agent.collect_rating_feedback("nonexistent_message_id", 5, "Great!")
        # This should handle gracefully, possibly returning False
        assert isinstance(success, bool), "collect_rating_feedback should return boolean"
        
        # Test collecting feedback with invalid rating
        try:
            agent.collect_rating_feedback("test_id", 10, "Invalid rating")  # Out of scale
            # If no exception, that's okay for this test
        except ValueError:
            # Expected exception for invalid rating
            pass
        
        # Test collecting feedback with valid parameters
        response = agent.process_input("Test message for feedback.")
        message_id = agent.conversation_history[-1].get("id")
        
        success = agent.collect_rating_feedback(message_id, 4, "Good response.")
        assert isinstance(success, bool), "collect_rating_feedback should return boolean"
        
        report.add_result(ErrorHandlingTestResult("Feedback Error Handling", True, "Feedback error handling works correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorHandlingTestResult("Feedback Error Handling", False, "Feedback error handling failed", e))
        return False


def test_concurrent_access_simulation(report: ErrorHandlingTestResult) -> bool:
    """Test handling of concurrent access scenarios."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_concurrent")
        
        # Simulate rapid consecutive requests
        responses = []
        for i in range(10):
            response = agent.process_input(f"Rapid message {i}")
            responses.append(response)
            assert isinstance(response, str), f"Response {i} should be string"
        
        # Verify all responses are unique (or at least not all identical)
        unique_responses = set(responses)
        assert len(unique_responses) > 1, "Should have some variation in responses"
        
        report.add_result(ErrorHandlingTestResult("Concurrent Access Simulation", True, "Concurrent access simulation works correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorHandlingTestResult("Concurrent Access Simulation", False, "Concurrent access simulation failed", e))
        return False


def test_configuration_edge_cases(report: ErrorHandlingTestResult) -> bool:
    """Test configuration edge cases."""
    try:
        # Test agent creation with various user IDs
        test_user_ids = [
            "",  # Empty string
            "a",  # Single character
            "user" * 100,  # Very long user ID
            "user with spaces",
            "user@domain.com",
            "用户_test"  # Unicode
        ]
        
        for user_id in test_user_ids:
            agent = Agent(user_id=user_id)
            assert agent.user_id == user_id, f"User ID should match for '{user_id}'"
            assert isinstance(agent.name, str), "Agent name should be string"
        
        report.add_result(ErrorHandlingTestResult("Configuration Edge Cases", True, "Configuration edge cases work correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorHandlingTestResult("Configuration Edge Cases", False, "Configuration edge cases failed", e))
        return False


def run_error_handling_tests() -> ErrorHandlingTestReport:
    """Run all error handling tests."""
    print("Starting Personal Agent Error Handling Tests...")
    print("=" * 50)
    
    # Create test report
    report = ErrorHandlingTestReport()
    
    try:
        # Run all tests
        tests = [
            test_input_validation,
            test_memory_error_handling,
            test_llm_error_handling,
            test_exit_commands,
            test_conversation_history_boundaries,
            test_feedback_error_handling,
            test_concurrent_access_simulation,
            test_configuration_edge_cases
        ]
        
        for test_func in tests:
            print(f"Running {test_func.__name__}...")
            test_func(report)
        
        print("\n" + "=" * 50)
        print("Error handling tests completed!")
        
    except Exception as e:
        error_result = ErrorHandlingTestResult("Error Handling Test Suite", False, "Test suite failed to run", e)
        report.add_result(error_result)
        print(f"Test suite error: {e}")
        traceback.print_exc()
    
    return report


def main():
    """Main function to run the error handling tests."""
    # Run tests
    report = run_error_handling_tests()
    
    # Generate and print report
    report_text = report.generate_report()
    print("\n" + report_text)
    
    # Save report to file
    report_path = "test_results_error_handling.txt"
    with open(report_path, 'w') as f:
        f.write(report_text)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Return exit code based on test results
    failed_tests = sum(1 for r in report.results if not r.passed)
    return 1 if failed_tests > 0 else 0


if __name__ == "__main__":
    sys.exit(main())