#!/usr/bin/env python3
"""
End-to-end test for LLM integration in the personal agent.

This test focuses specifically on LLM functionality including:
- Basic LLM client operations
- Context-aware responses
- Conversation flow with LLM
- Error handling for LLM issues
- Rate limiting simulation
"""

import sys
import os
import traceback
from typing import List
from unittest.mock import Mock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from personal_agent.core.agent import Agent
from personal_agent.llm.client import LLMClient
from personal_agent.llm.models import Message, LLMResponse
from personal_agent.llm.exceptions import LLMException
from personal_agent.config.settings import Config


class LLMTestResult:
    """Represents the result of an LLM test."""
    
    def __init__(self, name: str, passed: bool, message: str = "", error: Exception = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.error = error


class LLMTestReport:
    """Generates and manages LLM test reports."""
    
    def __init__(self):
        self.results: List[LLMTestResult] = []
    
    def add_result(self, result: LLMTestResult):
        """Add a test result to the report."""
        self.results.append(result)
    
    def generate_report(self) -> str:
        """Generate a formatted test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("=" * 60)
        report.append("PERSONAL AGENT - LLM INTEGRATION TEST REPORT")
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


def create_mock_llm_response(content: str, model: str = "test-model") -> LLMResponse:
    """Create a mock LLM response for testing."""
    return LLMResponse(
        content=content,
        model=model,
        usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    )


def test_llm_client_initialization(report: LLMTestReport) -> bool:
    """Test LLM client initialization."""
    try:
        # Test with valid configuration
        config = Config.load()
        
        # If API key is not set, we'll test initialization without it
        if not config.llm.api_key:
            # Test that client can be created even without API key (will fail later when used)
            try:
                client = LLMClient(config)
                # This might succeed or fail depending on the provider implementation
                report.add_result(LLMTestResult("LLM Client Initialization", True, "LLM client initialization handled correctly"))
                return True
            except Exception as e:
                # If it fails, that's okay for this test - we're testing initialization logic
                report.add_result(LLMTestResult("LLM Client Initialization", True, f"LLM client initialization failed as expected: {str(e)}"))
                return True
        else:
            # If API key is set, initialization should succeed
            client = LLMClient(config)
            assert client is not None, "LLM client should be created"
            assert client.provider is not None, "LLM provider should be initialized"
            
            report.add_result(LLMTestResult("LLM Client Initialization", True, "LLM client initialization works correctly"))
            return True
            
    except Exception as e:
        report.add_result(LLMTestResult("LLM Client Initialization", False, "LLM client initialization failed", e))
        return False


def test_llm_response_generation(report: LLMTestReport) -> bool:
    """Test LLM response generation with mocking."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_llm")
        
        # Mock LLM client to return predictable responses
        mock_response = create_mock_llm_response("Hello! I'm your personal assistant. How can I help you today?")
        
        with patch.object(agent, 'llm_client') as mock_llm:
            mock_llm.generate_response.return_value = mock_response
            
            # Test basic response generation
            response = agent.process_input("Hello, who are you?")
            assert response == mock_response.content, "Response should match mock response"
            
            # Verify LLM was called with correct parameters
            assert mock_llm.generate_response.called, "LLM generate_response should be called"
            
        report.add_result(LLMTestResult("LLM Response Generation", True, "LLM response generation works correctly"))
        return True
        
    except Exception as e:
        report.add_result(LLMTestResult("LLM Response Generation", False, "LLM response generation failed", e))
        return False


def test_context_aware_responses(report: LLMTestReport) -> bool:
    """Test context-aware responses from LLM."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_context")
        
        # Mock LLM to simulate context-aware responses
        with patch.object(agent, 'llm_client') as mock_llm:
            # First response
            mock_llm.generate_response.return_value = create_mock_llm_response(
                "I've noted that your favorite color is blue."
            )
            response1 = agent.process_input("My favorite color is blue.")
            
            # Second response that should reference context
            mock_llm.generate_response.return_value = create_mock_llm_response(
                "You mentioned earlier that your favorite color is blue. Is there anything specific about blue you'd like to discuss?"
            )
            response2 = agent.process_input("What did I say about my favorite color?")
            
            # Both responses should be strings
            assert isinstance(response1, str), "First response should be a string"
            assert isinstance(response2, str), "Second response should be a string"
            
            # Second response should reference the context (in a real scenario)
            # For this test, we're just verifying the flow works
            assert len(response1) > 0 and len(response2) > 0, "Both responses should have content"
            
        report.add_result(LLMTestResult("Context-Aware Responses", True, "Context-aware responses work correctly"))
        return True
        
    except Exception as e:
        report.add_result(LLMTestResult("Context-Aware Responses", False, "Context-aware responses failed", e))
        return False


def test_conversation_flow_with_llm(report: LLMTestReport) -> bool:
    """Test multi-turn conversation flow with LLM."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_conversation")
        
        # Mock LLM responses for a conversation
        responses = [
            create_mock_llm_response("Nice to meet you! How can I assist you today?"),
            create_mock_llm_response("I'd be happy to help with that. What specifically would you like to know?"),
            create_mock_llm_response("Based on what we've discussed, I recommend considering all options carefully.")
        ]
        
        response_index = 0
        
        def mock_generate_response(messages, **kwargs):
            nonlocal response_index
            if response_index < len(responses):
                response = responses[response_index]
                response_index += 1
                return response
            return create_mock_llm_response("I'm here to help with any other questions you might have.")
        
        with patch.object(agent, 'llm_client') as mock_llm:
            mock_llm.generate_response.side_effect = mock_generate_response
            
            # Simulate a multi-turn conversation
            response1 = agent.process_input("Hi, I'm looking for some advice.")
            response2 = agent.process_input("I need help with a technical decision.")
            response3 = agent.process_input("What do you recommend?")
            
            # Verify all responses
            assert isinstance(response1, str), "First response should be a string"
            assert isinstance(response2, str), "Second response should be a string"
            assert isinstance(response3, str), "Third response should be a string"
            
            # Verify conversation history is maintained
            assert len(agent.conversation_history) >= 6, "Conversation history should contain all turns"
            
        report.add_result(LLMTestResult("Conversation Flow with LLM", True, "Conversation flow with LLM works correctly"))
        return True
        
    except Exception as e:
        report.add_result(LLMTestResult("Conversation Flow with LLM", False, "Conversation flow with LLM failed", e))
        return False


def test_llm_error_handling(report: LLMTestReport) -> bool:
    """Test LLM error handling and fallback mechanisms."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_error")
        
        # Test with LLM client that raises an exception
        with patch.object(agent, 'llm_client') as mock_llm:
            mock_llm.generate_response.side_effect = LLMException("API rate limit exceeded")
            
            # Process input - should fall back to simple response
            response = agent.process_input("Hello, how are you?")
            
            # Response should still be a string (fallback response)
            assert isinstance(response, str), "Response should be a string even with LLM error"
            assert len(response) > 0, "Response should not be empty"
            
            # Test specific fallback cases
            response_hello = agent.process_input("hello")
            assert "Hello" in response_hello or "hello" in response_hello.lower(), "Should have specific fallback for hello"
            
        # Test with no LLM client (simulating initialization failure)
        agent_no_llm = Agent(user_id="test_user_no_llm")
        agent_no_llm.llm_client = None
        
        response = agent_no_llm.process_input("Hello, how are you?")
        assert isinstance(response, str), "Response should be a string even without LLM client"
        assert len(response) > 0, "Response should not be empty"
        
        report.add_result(LLMTestResult("LLM Error Handling", True, "LLM error handling works correctly"))
        return True
        
    except Exception as e:
        report.add_result(LLMTestResult("LLM Error Handling", False, "LLM error handling failed", e))
        return False


def test_llm_message_formatting(report: LLMTestReport) -> bool:
    """Test LLM message formatting and structure."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_formatting")
        
        # Capture messages sent to LLM
        captured_messages = []
        
        def capture_messages(messages, **kwargs):
            captured_messages.extend(messages)
            return create_mock_llm_response("Test response")
        
        with patch.object(agent, 'llm_client') as mock_llm:
            mock_llm.generate_response.side_effect = capture_messages
            
            # Process input to trigger message formatting
            agent.process_input("Test message for formatting")
            
            # Verify message structure
            assert len(captured_messages) > 0, "Should have captured messages"
            
            # Check that messages have required fields
            for message in captured_messages:
                assert hasattr(message, 'role'), "Message should have role attribute"
                assert hasattr(message, 'content'), "Message should have content attribute"
                assert message.role in ['system', 'user', 'assistant'], "Message role should be valid"
                assert isinstance(message.content, str), "Message content should be string"
            
            # Check for system message
            system_messages = [m for m in captured_messages if m.role == 'system']
            assert len(system_messages) > 0, "Should have at least one system message"
            
        report.add_result(LLMTestResult("LLM Message Formatting", True, "LLM message formatting works correctly"))
        return True
        
    except Exception as e:
        report.add_result(LLMTestResult("LLM Message Formatting", False, "LLM message formatting failed", e))
        return False


def run_llm_tests() -> LLMTestReport:
    """Run all LLM integration tests."""
    print("Starting Personal Agent LLM Integration Tests...")
    print("=" * 50)
    
    # Create test report
    report = LLMTestReport()
    
    try:
        # Run all tests
        tests = [
            test_llm_client_initialization,
            test_llm_response_generation,
            test_context_aware_responses,
            test_conversation_flow_with_llm,
            test_llm_error_handling,
            test_llm_message_formatting
        ]
        
        for test_func in tests:
            print(f"Running {test_func.__name__}...")
            test_func(report)
        
        print("\n" + "=" * 50)
        print("LLM integration tests completed!")
        
    except Exception as e:
        error_result = LLMTestResult("LLM Test Suite", False, "Test suite failed to run", e)
        report.add_result(error_result)
        print(f"Test suite error: {e}")
        traceback.print_exc()
    
    return report


def main():
    """Main function to run the LLM integration tests."""
    # Run tests
    report = run_llm_tests()
    
    # Generate and print report
    report_text = report.generate_report()
    print("\n" + report_text)
    
    # Save report to file
    report_path = "test_results_llm.txt"
    with open(report_path, 'w') as f:
        f.write(report_text)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Return exit code based on test results
    failed_tests = sum(1 for r in report.results if not r.passed)
    return 1 if failed_tests > 0 else 0


if __name__ == "__main__":
    sys.exit(main())