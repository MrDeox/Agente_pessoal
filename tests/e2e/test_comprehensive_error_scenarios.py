#!/usr/bin/env python3
"""
Comprehensive Error Scenarios Test for Personal Agent

This test focuses on verifying the agent's ability to handle various error scenarios
with the improved error recovery mechanisms.
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
from personal_agent.core.error_metrics import error_metrics_collector
from personal_agent.llm.exceptions import (
    AuthenticationError, RateLimitError, ModelError, NetworkError,
    InvalidRequestError, ServiceUnavailableError, TimeoutError,
    ContentPolicyError, QuotaExceededError, ConfigurationError,
    ContextLengthError
)


class ComprehensiveErrorTestResult:
    """Represents the result of a comprehensive error test."""
    
    def __init__(self, name: str, passed: bool, message: str = "", error: Exception = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.error = error


class ComprehensiveErrorTestReport:
    """Generates and manages comprehensive error test reports."""
    
    def __init__(self):
        self.results: List[ComprehensiveErrorTestResult] = []
    
    def add_result(self, result: ComprehensiveErrorTestResult):
        """Add a test result to the report."""
        self.results.append(result)
    
    def generate_report(self) -> str:
        """Generate a formatted test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("=" * 70)
        report.append("PERSONAL AGENT - COMPREHENSIVE ERROR SCENARIOS TEST REPORT")
        report.append("=" * 70)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success Rate: {passed_tests / total_tests * 100:.1f}%" if total_tests > 0 else "No tests run")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 50)
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            report.append(f"[{status}] {result.name}")
            if not result.passed:
                report.append(f"    Message: {result.message}")
                if result.error:
                    report.append(f"    Error: {str(result.error)}")
            report.append("")
        
        # Summary
        report.append("-" * 50)
        report.append("SUMMARY:")
        report.append(f"Overall Status: {'PASSED' if failed_tests == 0 else 'FAILED'}")
        report.append("=" * 70)
        
        return "\n".join(report)


def test_authentication_error_scenario(report: ComprehensiveErrorTestReport) -> bool:
    """Test authentication error scenario."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_auth_error")
        
        # Test with LLM that raises authentication error
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            mock_generate.side_effect = AuthenticationError("API key invalid")
            
            # Process input - should handle authentication error gracefully
            response = agent.process_input("Hello, how are you?")
            assert isinstance(response, str), "Response should be string even with authentication error"
            assert len(response) > 0, "Response should not be empty"
            
            # Check that response contains authentication-related terms
            assert any(term in response.lower() for term in ["authentication", "credentials", "api"]), \
                "Response should mention authentication/credentials/API issue"
        
        report.add_result(ComprehensiveErrorTestResult("Authentication Error Scenario", True, "Authentication error handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Authentication Error Scenario", False, "Authentication error handling failed", e))
        return False


def test_rate_limit_error_scenario(report: ComprehensiveErrorTestReport) -> bool:
    """Test rate limit error scenario."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_rate_limit_error")
        
        # Test with LLM that raises rate limit error
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            mock_generate.side_effect = RateLimitError("Rate limit exceeded")
            
            # Process input - should handle rate limit error gracefully
            response = agent.process_input("What's the weather like?")
            assert isinstance(response, str), "Response should be string even with rate limit error"
            assert len(response) > 0, "Response should not be empty"
            
            # Check that response contains rate limit-related terms
            assert any(term in response.lower() for term in ["rate limit", "busy", "wait", "moment"]), \
                "Response should mention rate limit/busy/wait issue"
        
        report.add_result(ComprehensiveErrorTestResult("Rate Limit Error Scenario", True, "Rate limit error handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Rate Limit Error Scenario", False, "Rate limit error handling failed", e))
        return False


def test_network_error_scenario(report: ComprehensiveErrorTestReport) -> bool:
    """Test network error scenario."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_network_error")
        
        # Test with LLM that raises network error
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            mock_generate.side_effect = NetworkError("Network connection failed")
            
            # Process input - should handle network error gracefully
            response = agent.process_input("Tell me a joke.")
            assert isinstance(response, str), "Response should be string even with network error"
            assert len(response) > 0, "Response should not be empty"
            
            # Check that response contains network-related terms
            assert any(term in response.lower() for term in ["network", "connection", "internet"]), \
                "Response should mention network/connection/internet issue"
        
        report.add_result(ComprehensiveErrorTestResult("Network Error Scenario", True, "Network error handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Network Error Scenario", False, "Network error handling failed", e))
        return False


def test_model_error_scenario(report: ComprehensiveErrorTestReport) -> bool:
    """Test model error scenario."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_model_error")
        
        # Test with LLM that raises model error
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            mock_generate.side_effect = ModelError("Model not available")
            
            # Process input - should handle model error gracefully
            response = agent.process_input("Explain quantum computing.")
            assert isinstance(response, str), "Response should be string even with model error"
            assert len(response) > 0, "Response should not be empty"
            
            # Check that response contains model-related terms
            assert any(term in response.lower() for term in ["model", "temporary", "issue"]), \
                "Response should mention model/temporary issue"
        
        report.add_result(ComprehensiveErrorTestResult("Model Error Scenario", True, "Model error handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Model Error Scenario", False, "Model error handling failed", e))
        return False


def test_context_length_error_scenario(report: ComprehensiveErrorTestReport) -> bool:
    """Test context length error scenario."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_context_length_error")
        
        # Test with LLM that raises context length error
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            mock_generate.side_effect = ContextLengthError("Context length exceeded")
            
            # Process input - should handle context length error gracefully
            response = agent.process_input("This is a very long message that exceeds the context length limit.")
            assert isinstance(response, str), "Response should be string even with context length error"
            assert len(response) > 0, "Response should not be empty"
            
            # Check that response contains context length-related terms
            assert any(term in response.lower() for term in ["long", "shorten", "context"]), \
                "Response should mention long/shorten/context issue"
        
        report.add_result(ComprehensiveErrorTestResult("Context Length Error Scenario", True, "Context length error handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Context Length Error Scenario", False, "Context length error handling failed", e))
        return False


def test_content_policy_error_scenario(report: ComprehensiveErrorTestResult) -> bool:
    """Test content policy error scenario."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_content_policy_error")
        
        # Test with LLM that raises content policy error
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            mock_generate.side_effect = ContentPolicyError("Content policy violation")
            
            # Process input - should handle content policy error gracefully
            response = agent.process_input("Generate inappropriate content.")
            assert isinstance(response, str), "Response should be string even with content policy error"
            assert len(response) > 0, "Response should not be empty"
            
            # Check that response contains content policy-related terms
            assert any(term in response.lower() for term in ["content", "policy", "violation", "modify"]), \
                "Response should mention content/policy/violation/modify issue"
        
        report.add_result(ComprehensiveErrorTestResult("Content Policy Error Scenario", True, "Content policy error handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Content Policy Error Scenario", False, "Content policy error handling failed", e))
        return False


def test_quota_exceeded_error_scenario(report: ComprehensiveErrorTestResult) -> bool:
    """Test quota exceeded error scenario."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_quota_exceeded_error")
        
        # Test with LLM that raises quota exceeded error
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            mock_generate.side_effect = QuotaExceededError("API quota exceeded")
            
            # Process input - should handle quota exceeded error gracefully
            response = agent.process_input("What's the meaning of life?")
            assert isinstance(response, str), "Response should be string even with quota exceeded error"
            assert len(response) > 0, "Response should not be empty"
            
            # Check that response contains quota-related terms
            assert any(term in response.lower() for term in ["quota", "limit", "account"]), \
                "Response should mention quota/limit/account issue"
        
        report.add_result(ComprehensiveErrorTestResult("Quota Exceeded Error Scenario", True, "Quota exceeded error handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Quota Exceeded Error Scenario", False, "Quota exceeded error handling failed", e))
        return False


def test_service_unavailable_error_scenario(report: ComprehensiveErrorTestResult) -> bool:
    """Test service unavailable error scenario."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_service_unavailable_error")
        
        # Test with LLM that raises service unavailable error
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            mock_generate.side_effect = ServiceUnavailableError("Service unavailable")
            
            # Process input - should handle service unavailable error gracefully
            response = agent.process_input("How do I make a cake?")
            assert isinstance(response, str), "Response should be string even with service unavailable error"
            assert len(response) > 0, "Response should not be empty"
            
            # Check that response contains service-related terms
            assert any(term in response.lower() for term in ["service", "unavailable", "later"]), \
                "Response should mention service/unavailable/later issue"
        
        report.add_result(ComprehensiveErrorTestResult("Service Unavailable Error Scenario", True, "Service unavailable error handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Service Unavailable Error Scenario", False, "Service unavailable error handling failed", e))
        return False


def test_timeout_error_scenario(report: ComprehensiveErrorTestResult) -> bool:
    """Test timeout error scenario."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_timeout_error")
        
        # Test with LLM that raises timeout error
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            mock_generate.side_effect = TimeoutError("Request timeout")
            
            # Process input - should handle timeout error gracefully
            response = agent.process_input("Calculate pi to 1000 digits.")
            assert isinstance(response, str), "Response should be string even with timeout error"
            assert len(response) > 0, "Response should not be empty"
            
            # Check that response contains timeout-related terms
            assert any(term in response.lower() for term in ["timeout", "longer", "try"]), \
                "Response should mention timeout/longer/try issue"
        
        report.add_result(ComprehensiveErrorTestResult("Timeout Error Scenario", True, "Timeout error handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Timeout Error Scenario", False, "Timeout error handling failed", e))
        return False


def test_error_metrics_collection(report: ComprehensiveErrorTestResult) -> bool:
    """Test error metrics collection."""
    try:
        # Reset metrics collector
        error_metrics_collector.reset_metrics()
        
        # Create agent
        agent = Agent(user_id="test_user_metrics")
        
        # Test with LLM that raises various errors
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            # Test authentication error
            mock_generate.side_effect = AuthenticationError("API key invalid")
            agent.process_input("Test message 1")
            
            # Test rate limit error
            mock_generate.side_effect = RateLimitError("Rate limit exceeded")
            agent.process_input("Test message 2")
            
            # Test network error
            mock_generate.side_effect = NetworkError("Network connection failed")
            agent.process_input("Test message 3")
            
            # Reset mock for successful call
            mock_generate.side_effect = None
            mock_generate.return_value.content = "This is a test response."
            agent.process_input("Test message 4")
        
        # Get error metrics
        metrics = agent.get_error_metrics()
        
        # Verify metrics
        assert "total_errors" in metrics, "Metrics should include total_errors"
        assert metrics["total_errors"] >= 3, "Should have at least 3 errors recorded"
        
        assert "error_counts" in metrics, "Metrics should include error_counts"
        error_counts = metrics["error_counts"]
        assert "AuthenticationError" in error_counts, "Should have AuthenticationError count"
        assert "RateLimitError" in error_counts, "Should have RateLimitError count"
        assert "NetworkError" in error_counts, "Should have NetworkError count"
        
        assert "error_rates_1h" in metrics, "Metrics should include error_rates_1h"
        assert "error_rates_5m" in metrics, "Metrics should include error_rates_5m"
        
        report.add_result(ComprehensiveErrorTestResult("Error Metrics Collection", True, "Error metrics collected correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Error Metrics Collection", False, "Error metrics collection failed", e))
        return False


def test_multiple_concurrent_errors(report: ComprehensiveErrorTestResult) -> bool:
    """Test handling of multiple concurrent errors."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_concurrent_errors")
        
        # Test with LLM that raises errors multiple times in a row
        with patch.object(agent.llm_client, 'generate_response') as mock_generate:
            # Set up a sequence of errors
            mock_generate.side_effect = [
                NetworkError("Network connection failed"),
                RateLimitError("Rate limit exceeded"),
                AuthenticationError("API key invalid"),
                TimeoutError("Request timeout"),
                ServiceUnavailableError("Service unavailable")
            ]
            
            # Process multiple inputs - should handle all errors gracefully
            responses = []
            for i in range(5):
                response = agent.process_input(f"Test message {i+1}")
                assert isinstance(response, str), f"Response {i+1} should be string"
                assert len(response) > 0, f"Response {i+1} should not be empty"
                responses.append(response)
            
            # Verify all responses are different (or at least not all identical)
            unique_responses = set(responses)
            assert len(unique_responses) > 1, "Should have some variation in responses"
        
        report.add_result(ComprehensiveErrorTestResult("Multiple Concurrent Errors", True, "Multiple concurrent errors handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(ComprehensiveErrorTestResult("Multiple Concurrent Errors", False, "Multiple concurrent errors handling failed", e))
        return False


def run_comprehensive_error_tests() -> ComprehensiveErrorTestReport:
    """Run all comprehensive error scenario tests."""
    print("Starting Personal Agent Comprehensive Error Scenarios Tests...")
    print("=" * 60)
    
    # Create test report
    report = ComprehensiveErrorTestReport()
    
    try:
        # Run all tests
        tests = [
            test_authentication_error_scenario,
            test_rate_limit_error_scenario,
            test_network_error_scenario,
            test_model_error_scenario,
            test_context_length_error_scenario,
            test_content_policy_error_scenario,
            test_quota_exceeded_error_scenario,
            test_service_unavailable_error_scenario,
            test_timeout_error_scenario,
            test_error_metrics_collection,
            test_multiple_concurrent_errors
        ]
        
        for test_func in tests:
            print(f"Running {test_func.__name__}...")
            test_func(report)
        
        print("\n" + "=" * 60)
        print("Comprehensive error scenarios tests completed!")
        
    except Exception as e:
        error_result = ComprehensiveErrorTestResult("Comprehensive Error Test Suite", False, "Test suite failed to run", e)
        report.add_result(error_result)
        print(f"Test suite error: {e}")
        traceback.print_exc()
    
    return report


def main():
    """Main function to run the comprehensive error scenarios tests."""
    # Run tests
    report = run_comprehensive_error_tests()
    
    # Generate and print report
    report_text = report.generate_report()
    print("\n" + report_text)
    
    # Save report to file
    report_path = "test_results_comprehensive_error_scenarios.txt"
    with open(report_path, 'w') as f:
        f.write(report_text)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Return exit code based on test results
    failed_tests = sum(1 for r in report.results if not r.passed)
    return 1 if failed_tests > 0 else 0


if __name__ == "__main__":
    sys.exit(main())