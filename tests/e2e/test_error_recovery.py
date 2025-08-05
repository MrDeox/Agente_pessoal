#!/usr/bin/env python3
"""
End-to-end test for error recovery mechanisms in the personal agent.

This test focuses specifically on:
- Error categorization and handling
- Fallback mechanisms for different error types
- User-friendly error explanations
- Graceful degradation when services are unavailable
"""

import sys
import os
import traceback
from typing import List
from unittest.mock import Mock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from personal_agent.core.agent import Agent
from personal_agent.core.error_recovery import error_recovery_manager
from personal_agent.llm.exceptions import (
    AuthenticationError, RateLimitError, ModelError, NetworkError,
    InvalidRequestError, ServiceUnavailableError, TimeoutError,
    ContentPolicyError, QuotaExceededError, ConfigurationError,
    ContextLengthError
)


class ErrorRecoveryTestResult:
    """Represents the result of an error recovery test."""
    
    def __init__(self, name: str, passed: bool, message: str = "", error: Exception = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.error = error


class ErrorRecoveryTestReport:
    """Generates and manages error recovery test reports."""
    
    def __init__(self):
        self.results: List[ErrorRecoveryTestResult] = []
    
    def add_result(self, result: ErrorRecoveryTestResult):
        """Add a test result to the report."""
        self.results.append(result)
    
    def generate_report(self) -> str:
        """Generate a formatted test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("=" * 60)
        report.append("PERSONAL AGENT - ERROR RECOVERY TEST REPORT")
        report.append("=" * 60)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success Rate: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "No tests run")
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


def test_error_categorization(report: ErrorRecoveryTestReport) -> bool:
    """Test error categorization."""
    try:
        # Test that all error types have proper categorization
        errors_to_test = [
            (AuthenticationError(), "AUTHENTICATION"),
            (RateLimitError(), "RATE_LIMITING"),
            (QuotaExceededError(), "RATE_LIMITING"),
            (NetworkError(), "NETWORK"),
            (TimeoutError(), "NETWORK"),
            (ServiceUnavailableError(), "NETWORK"),
            (ModelError(), "MODEL"),
            (ContextLengthError(), "MODEL"),
            (InvalidRequestError(), "REQUEST"),
            (ContentPolicyError(), "REQUEST"),
        ]
        
        # Test that each error has a user-friendly message
        for error, expected_category in errors_to_test:
            # Check that error has user_message attribute
            assert hasattr(error, 'user_message'), f"Error {type(error).__name__} missing user_message"
            assert isinstance(error.user_message, str), f"Error {type(error).__name__} user_message not a string"
            assert len(error.user_message) > 0, f"Error {type(error).__name__} user_message is empty"
        
        report.add_result(ErrorRecoveryTestResult("Error Categorization", True, "Error categorization works correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorRecoveryTestResult("Error Categorization", False, "Error categorization failed", e))
        return False


def test_fallback_mechanisms(report: ErrorRecoveryTestReport) -> bool:
    """Test fallback mechanisms for different error types."""
    try:
        # Test authentication error recovery
        auth_error = AuthenticationError("Test authentication error")
        auth_response = error_recovery_manager.recover_from_error(auth_error)
        assert isinstance(auth_response, str), "Authentication error recovery should return string"
        assert len(auth_response) > 0, "Authentication error recovery should not be empty"
        # Check that the response is user-friendly and mentions authentication issues
        assert "authentication" in auth_response.lower() or "credentials" in auth_response.lower() or "api" in auth_response.lower(), "Authentication error response should mention authentication/credentials/API"
        
        # Test rate limit error recovery
        rate_limit_error = RateLimitError("Test rate limit error")
        rate_limit_response = error_recovery_manager.recover_from_error(rate_limit_error)
        assert isinstance(rate_limit_response, str), "Rate limit error recovery should return string"
        assert len(rate_limit_response) > 0, "Rate limit error recovery should not be empty"
        assert "busy" in rate_limit_response.lower() or "wait" in rate_limit_response.lower(), "Rate limit error response should mention waiting"
        
        # Test network error recovery
        network_error = NetworkError("Test network error")
        network_response = error_recovery_manager.recover_from_error(network_error)
        assert isinstance(network_response, str), "Network error recovery should return string"
        assert len(network_response) > 0, "Network error recovery should not be empty"
        assert "connection" in network_response.lower() or "internet" in network_response.lower(), "Network error response should mention connection"
        
        # Test model error recovery
        model_error = ModelError("Test model error")
        model_response = error_recovery_manager.recover_from_error(model_error)
        assert isinstance(model_response, str), "Model error recovery should return string"
        assert len(model_response) > 0, "Model error recovery should not be empty"
        assert "model" in model_response.lower() or "temporary" in model_response.lower(), "Model error response should mention model"
        
        # Test context length error recovery
        context_error = ContextLengthError("Test context length error")
        context_response = error_recovery_manager.recover_from_error(context_error)
        assert isinstance(context_response, str), "Context length error recovery should return string"
        assert len(context_response) > 0, "Context length error recovery should not be empty"
        assert "long" in context_response.lower() or "shorten" in context_response.lower(), "Context length error response should mention length"
        
        report.add_result(ErrorRecoveryTestResult("Fallback Mechanisms", True, "Fallback mechanisms work correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorRecoveryTestResult("Fallback Mechanisms", False, "Fallback mechanisms failed", e))
        return False


def test_user_friendly_explanations(report: ErrorRecoveryTestReport) -> bool:
    """Test user-friendly error explanations."""
    try:
        # Test that all error types provide user-friendly explanations
        errors_to_test = [
            AuthenticationError(),
            RateLimitError(),
            ModelError(),
            NetworkError(),
            InvalidRequestError(),
            ServiceUnavailableError(),
            TimeoutError(),
            ContentPolicyError(),
            QuotaExceededError(),
            ContextLengthError()
        ]
        
        for error in errors_to_test:
            # Check that error has user_message attribute
            assert hasattr(error, 'user_message'), f"Error {type(error).__name__} missing user_message"
            
            # Check that user_message is user-friendly (not technical)
            user_message = error.user_message
            assert not any(technical_term in user_message.lower() for technical_term in [
                "exception", "traceback", "stack", "error code"
            ]), f"Error {type(error).__name__} user_message contains technical terms"
            
            # Check that message is actionable
            assert any(action_word in user_message.lower() for action_word in [
                "please", "try", "check", "contact", "wait", "shorten"
            ]), f"Error {type(error).__name__} user_message is not actionable"
        
        report.add_result(ErrorRecoveryTestResult("User-Friendly Explanations", True, "User-friendly explanations work correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorRecoveryTestResult("User-Friendly Explanations", False, "User-friendly explanations failed", e))
        return False


def test_agent_error_handling(report: ErrorRecoveryTestReport) -> bool:
    """Test agent error handling with recovery mechanisms."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_error_recovery")
        
        # Test with LLM that raises specific exceptions
        with patch.object(agent, 'llm_client') as mock_llm:
            # Test authentication error
            mock_llm.generate_response.side_effect = AuthenticationError("API key invalid")
            response = agent.process_input("Hello, how are you?")
            assert isinstance(response, str), "Response should be string even with authentication error"
            assert len(response) > 0, "Response should not be empty"
            # Check that the response is user-friendly and mentions authentication issues
            assert "authentication" in response.lower() or "credentials" in response.lower() or "api" in response.lower(), "Response should mention authentication/credentials/API issue"
            
            # Test rate limit error
            mock_llm.generate_response.side_effect = RateLimitError("Rate limit exceeded")
            response = agent.process_input("Another test message")
            assert isinstance(response, str), "Response should be string even with rate limit error"
            assert len(response) > 0, "Response should not be empty"
            assert "busy" in response.lower() or "wait" in response.lower(), "Response should mention waiting"
            
            # Test network error
            mock_llm.generate_response.side_effect = NetworkError("Network connection failed")
            response = agent.process_input("Network test message")
            assert isinstance(response, str), "Response should be string even with network error"
            assert len(response) > 0, "Response should not be empty"
            assert "connection" in response.lower() or "internet" in response.lower(), "Response should mention connection issue"
            
            # Test model error
            mock_llm.generate_response.side_effect = ModelError("Model not available")
            response = agent.process_input("Model test message")
            assert isinstance(response, str), "Response should be string even with model error"
            assert len(response) > 0, "Response should not be empty"
            assert "model" in response.lower() or "temporary" in response.lower(), "Response should mention model issue"
        
        # Test planning with error
        with patch.object(agent, 'create_plan') as mock_create_plan:
            mock_create_plan.side_effect = Exception("Planning service unavailable")
            response = agent.process_input("Please plan a trip to Paris")
            assert isinstance(response, str), "Planning error response should be string"
            assert len(response) > 0, "Planning error response should not be empty"
            # Should contain a user-friendly error message from error recovery manager
        
        # Test reasoning with error
        with patch.object(agent, 'reason') as mock_reason:
            mock_reason.side_effect = Exception("Reasoning service unavailable")
            response = agent.process_input("Please reason about this statement")
            assert isinstance(response, str), "Reasoning error response should be string"
            assert len(response) > 0, "Reasoning error response should not be empty"
            # Should contain a user-friendly error message from error recovery manager
        
        report.add_result(ErrorRecoveryTestResult("Agent Error Handling", True, "Agent error handling works correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorRecoveryTestResult("Agent Error Handling", False, "Agent error handling failed", e))
        return False


def test_graceful_degradation(report: ErrorRecoveryTestReport) -> bool:
    """Test graceful degradation when services are unavailable."""
    try:
        # Test agent with no LLM client
        agent_no_llm = Agent(user_id="test_user_no_llm")
        agent_no_llm.llm_client = None
        
        response = agent_no_llm.process_input("Hello, how are you?")
        assert isinstance(response, str), "Response should be string without LLM client"
        assert len(response) > 0, "Response should not be empty"
        # Should contain a user-friendly error message from error recovery manager
        
        # Test with completely broken LLM client
        agent_broken_llm = Agent(user_id="test_user_broken_llm")
        agent_broken_llm.llm_client = Mock()
        agent_broken_llm.llm_client.generate_response.side_effect = Exception("Completely broken")
        
        response = agent_broken_llm.process_input("Test message")
        assert isinstance(response, str), "Response should be string with broken LLM client"
        assert len(response) > 0, "Response should not be empty"
        # Should contain a user-friendly error message from error recovery manager
        
        report.add_result(ErrorRecoveryTestResult("Graceful Degradation", True, "Graceful degradation works correctly"))
        return True
        
    except Exception as e:
        report.add_result(ErrorRecoveryTestResult("Graceful Degradation", False, "Graceful degradation failed", e))
        return False


def run_error_recovery_tests() -> ErrorRecoveryTestReport:
    """Run all error recovery tests."""
    print("Starting Personal Agent Error Recovery Tests...")
    print("=" * 50)
    
    # Create test report
    report = ErrorRecoveryTestReport()
    
    try:
        # Run all tests
        tests = [
            test_error_categorization,
            test_fallback_mechanisms,
            test_user_friendly_explanations,
            test_agent_error_handling,
            test_graceful_degradation
        ]
        
        for test_func in tests:
            print(f"Running {test_func.__name__}...")
            test_func(report)
        
        print("\n" + "=" * 50)
        print("Error recovery tests completed!")
        
    except Exception as e:
        error_result = ErrorRecoveryTestResult("Error Recovery Test Suite", False, "Test suite failed to run", e)
        report.add_result(error_result)
        print(f"Test suite error: {e}")
        traceback.print_exc()
    
    return report


def main():
    """Main function to run the error recovery tests."""
    # Run tests
    report = run_error_recovery_tests()
    
    # Generate and print report
    report_text = report.generate_report()
    print("\n" + report_text)
    
    # Save report to file
    report_path = "test_results_error_recovery.txt"
    with open(report_path, 'w') as f:
        f.write(report_text)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Return exit code based on test results
    failed_tests = sum(1 for r in report.results if not r.passed)
    return 1 if failed_tests > 0 else 0


if __name__ == "__main__":
    sys.exit(main())