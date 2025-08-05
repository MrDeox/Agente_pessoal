#!/usr/bin/env python3
"""
End-to-end test for feedback mechanism in the personal agent.

This test focuses specifically on feedback functionality including:
- Rating feedback collection
- Thumbs up/down feedback collection
- Feedback storage and retrieval
- Feedback statistics
- Response adaptation based on feedback
"""

import sys
import os
import traceback
from typing import List
from unittest.mock import patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from personal_agent.core.agent import Agent
from personal_agent.core.feedback import FeedbackSystem
from personal_agent.memory.models import Feedback


class FeedbackTestResult:
    """Represents the result of a feedback test."""
    
    def __init__(self, name: str, passed: bool, message: str = "", error: Exception = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.error = error


class FeedbackTestReport:
    """Generates and manages feedback test reports."""
    
    def __init__(self):
        self.results: List[FeedbackTestResult] = []
    
    def add_result(self, result: FeedbackTestResult):
        """Add a test result to the report."""
        self.results.append(result)
    
    def generate_report(self) -> str:
        """Generate a formatted test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("=" * 60)
        report.append("PERSONAL AGENT - FEEDBACK MECHANISM TEST REPORT")
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


def test_feedback_system_initialization(report: FeedbackTestReport) -> bool:
    """Test feedback system initialization."""
    try:
        # Create feedback system
        feedback_system = FeedbackSystem(user_id="test_user_feedback_init")
        
        # Verify initialization
        assert feedback_system.user_id == "test_user_feedback_init", "User ID should match"
        assert feedback_system.storage is not None, "Storage should be initialized"
        assert feedback_system.config is not None, "Config should be loaded"
        
        report.add_result(FeedbackTestResult("Feedback System Initialization", True, "Feedback system initialization works correctly"))
        return True
        
    except Exception as e:
        report.add_result(FeedbackTestResult("Feedback System Initialization", False, "Feedback system initialization failed", e))
        return False


def test_rating_feedback_collection(report: FeedbackTestResult) -> bool:
    """Test rating feedback collection."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_rating")
        
        # Process a message to get a response with ID
        response = agent.process_input("This is a test message for rating feedback.")
        message_id = agent.conversation_history[-1].get("id")
        
        # Collect rating feedback
        success = agent.collect_rating_feedback(message_id, 4, "Good response, but could be better.")
        assert success, "Collecting rating feedback should succeed"
        
        # Verify feedback was stored
        feedback = agent.feedback_system.get_feedback_for_message(message_id)
        assert feedback is not None, "Feedback should be retrievable"
        assert feedback.rating == 4, "Rating should match"
        assert feedback.comment == "Good response, but could be better.", "Comment should match"
        assert feedback.feedback_type == "rating", "Feedback type should be rating"
        
        # Test invalid rating
        try:
            agent.collect_rating_feedback("test_id", 10, "Invalid rating")  # Rating out of scale
            # If no exception was raised, that's an issue
            report.add_result(FeedbackTestResult("Rating Feedback Collection", False, "Should have rejected invalid rating"))
            return False
        except ValueError:
            # This is expected
            pass
        
        report.add_result(FeedbackTestResult("Rating Feedback Collection", True, "Rating feedback collection works correctly"))
        return True
        
    except Exception as e:
        report.add_result(FeedbackTestResult("Rating Feedback Collection", False, "Rating feedback collection failed", e))
        return False


def test_thumbs_feedback_collection(report: FeedbackTestResult) -> bool:
    """Test thumbs up/down feedback collection."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_thumbs")
        
        # Process a message to get a response with ID
        response = agent.process_input("This is a test message for thumbs feedback.")
        message_id = agent.conversation_history[-1].get("id")
        
        # Collect thumbs up feedback
        success = agent.collect_thumbs_feedback(message_id, True, "Great response!")
        assert success, "Collecting thumbs up feedback should succeed"
        
        # Verify feedback was stored
        feedback = agent.feedback_system.get_feedback_for_message(message_id)
        assert feedback is not None, "Feedback should be retrievable"
        assert feedback.rating == 5, "Thumbs up should convert to rating 5"
        assert feedback.comment == "Great response!", "Comment should match"
        assert feedback.feedback_type == "thumbs_up_down", "Feedback type should be thumbs_up_down"
        
        # Collect thumbs down feedback (on a different message)
        response2 = agent.process_input("This is another test message.")
        message_id2 = agent.conversation_history[-1].get("id")
        
        success = agent.collect_thumbs_feedback(message_id2, False, "Not helpful.")
        assert success, "Collecting thumbs down feedback should succeed"
        
        # Verify feedback was stored
        feedback2 = agent.feedback_system.get_feedback_for_message(message_id2)
        assert feedback2 is not None, "Feedback should be retrievable"
        assert feedback2.rating == 1, "Thumbs down should convert to rating 1"
        assert feedback2.comment == "Not helpful.", "Comment should match"
        
        report.add_result(FeedbackTestResult("Thumbs Feedback Collection", True, "Thumbs feedback collection works correctly"))
        return True
        
    except Exception as e:
        report.add_result(FeedbackTestResult("Thumbs Feedback Collection", False, "Thumbs feedback collection failed", e))
        return False


def test_feedback_storage_and_retrieval(report: FeedbackTestResult) -> bool:
    """Test feedback storage and retrieval."""
    try:
        # Create feedback system
        feedback_system = FeedbackSystem(user_id="test_user_storage")
        
        # Create and store multiple feedback items
        feedback_items = [
            Feedback(
                user_id="test_user_storage",
                message_id="msg1",
                rating=5,
                feedback_type="rating",
                comment="Excellent response"
            ),
            Feedback(
                user_id="test_user_storage",
                message_id="msg2",
                rating=3,
                feedback_type="rating",
                comment="Average response"
            ),
            Feedback(
                user_id="test_user_storage",
                message_id="msg3",
                rating=1,
                feedback_type="thumbs_up_down",
                comment="Poor response"
            )
        ]
        
        # Store feedback items
        for feedback in feedback_items:
            success = feedback_system.storage.save_feedback(feedback)
            assert success, f"Storing feedback {feedback.message_id} should succeed"
        
        # Retrieve individual feedback
        retrieved_feedback = feedback_system.get_feedback_for_message("msg1")
        assert retrieved_feedback is not None, "Feedback should be retrievable"
        assert retrieved_feedback.rating == 5, "Rating should match"
        assert retrieved_feedback.comment == "Excellent response", "Comment should match"
        
        # Retrieve user feedback history
        history = feedback_system.get_user_feedback_history()
        assert isinstance(history, list), "History should be a list"
        assert len(history) >= 3, "Should have at least 3 feedback items"
        
        # Verify history contains our items
        message_ids = [f.message_id for f in history]
        assert "msg1" in message_ids, "History should contain msg1"
        assert "msg2" in message_ids, "History should contain msg2"
        assert "msg3" in message_ids, "History should contain msg3"
        
        report.add_result(FeedbackTestResult("Feedback Storage and Retrieval", True, "Feedback storage and retrieval works correctly"))
        return True
        
    except Exception as e:
        report.add_result(FeedbackTestResult("Feedback Storage and Retrieval", False, "Feedback storage and retrieval failed", e))
        return False


def test_feedback_statistics(report: FeedbackTestResult) -> bool:
    """Test feedback statistics calculation."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_stats")
        
        # Collect various feedback items
        test_messages = [
            ("Message 1", 5, "Great!"),
            ("Message 2", 4, "Good"),
            ("Message 3", 3, "Average"),
            ("Message 4", 2, "Below average"),
            ("Message 5", 1, "Poor")
        ]
        
        for msg_content, rating, comment in test_messages:
            # Process message
            agent.process_input(msg_content)
            message_id = agent.conversation_history[-1].get("id")
            
            # Collect feedback
            success = agent.collect_rating_feedback(message_id, rating, comment)
            assert success, f"Collecting feedback for {msg_content} should succeed"
        
        # Get feedback statistics
        stats = agent.get_feedback_statistics()
        
        # Verify statistics structure
        assert isinstance(stats, dict), "Statistics should be a dictionary"
        assert "total_feedback" in stats, "Should include total feedback count"
        assert "average_rating" in stats, "Should include average rating"
        assert "positive_feedback" in stats, "Should include positive feedback count"
        assert "negative_feedback" in stats, "Should include negative feedback count"
        
        # Verify specific values
        assert stats["total_feedback"] == 5, "Should have 5 total feedback items"
        assert abs(stats["average_rating"] - 3.0) < 0.1, "Average should be 3.0"
        assert stats["positive_feedback"] == 2, "Should have 2 positive feedback items (ratings 4-5)"
        assert stats["negative_feedback"] == 2, "Should have 2 negative feedback items (ratings 1-2)"
        
        report.add_result(FeedbackTestResult("Feedback Statistics", True, "Feedback statistics calculation works correctly"))
        return True
        
    except Exception as e:
        report.add_result(FeedbackTestResult("Feedback Statistics", False, "Feedback statistics calculation failed", e))
        return False


def test_response_adaptation(report: FeedbackTestResult) -> bool:
    """Test response adaptation based on feedback."""
    try:
        # Create agent
        agent = Agent(user_id="test_user_adaptation")
        
        # Process a message
        response1 = agent.process_input("Tell me a joke.")
        message_id = agent.conversation_history[-1].get("id")
        
        # Collect low rating feedback to trigger adaptation
        success = agent.collect_rating_feedback(message_id, 2, "That joke wasn't funny.")
        assert success, "Collecting low rating feedback should succeed"
        
        # Check if adaptation is triggered
        should_adapt = agent.feedback_system.should_adapt_response(message_id)
        assert should_adapt, "Should adapt response for low rating"
        
        # Get adaptation suggestion
        adaptation_suggestion = agent.feedback_system.get_adaptation_suggestion(message_id)
        assert adaptation_suggestion is not None, "Should have adaptation suggestion"
        assert isinstance(adaptation_suggestion, str), "Adaptation suggestion should be string"
        assert len(adaptation_suggestion) > 0, "Adaptation suggestion should not be empty"
        
        # Test with high rating (should not adapt)
        response2 = agent.process_input("Tell me another joke.")
        message_id2 = agent.conversation_history[-1].get("id")
        
        success = agent.collect_rating_feedback(message_id2, 5, "That was hilarious!")
        assert success, "Collecting high rating feedback should succeed"
        
        should_adapt2 = agent.feedback_system.should_adapt_response(message_id2)
        assert not should_adapt2, "Should not adapt response for high rating"
        
        report.add_result(FeedbackTestResult("Response Adaptation", True, "Response adaptation works correctly"))
        return True
        
    except Exception as e:
        report.add_result(FeedbackTestResult("Response Adaptation", False, "Response adaptation failed", e))
        return False


def test_feedback_edge_cases(report: FeedbackTestResult) -> bool:
    """Test feedback edge cases and error handling."""
    try:
        # Create feedback system
        feedback_system = FeedbackSystem(user_id="test_user_edge")
        
        # Test retrieving feedback for non-existent message
        feedback = feedback_system.get_feedback_for_message("nonexistent_message_id")
        assert feedback is None, "Should return None for non-existent feedback"
        
        # Test getting history for user with no feedback
        history = feedback_system.get_user_feedback_history()
        assert isinstance(history, list), "History should be a list"
        assert len(history) == 0, "History should be empty for new user"
        
        # Test statistics for user with no feedback
        stats = feedback_system.get_feedback_statistics()
        assert isinstance(stats, dict), "Statistics should be a dictionary"
        assert stats["total_feedback"] == 0, "Should have 0 total feedback"
        assert stats["average_rating"] == 0, "Should have 0 average rating"
        
        # Test adaptation check for non-existent message
        should_adapt = feedback_system.should_adapt_response("nonexistent_message_id")
        assert not should_adapt, "Should not adapt for non-existent message"
        
        # Test adaptation suggestion for non-existent message
        adaptation_suggestion = feedback_system.get_adaptation_suggestion("nonexistent_message_id")
        assert adaptation_suggestion is None, "Should return None for non-existent message"
        
        report.add_result(FeedbackTestResult("Feedback Edge Cases", True, "Feedback edge cases handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(FeedbackTestResult("Feedback Edge Cases", False, "Feedback edge cases failed", e))
        return False


def run_feedback_tests() -> FeedbackTestReport:
    """Run all feedback mechanism tests."""
    print("Starting Personal Agent Feedback Mechanism Tests...")
    print("=" * 55)
    
    # Create test report
    report = FeedbackTestReport()
    
    try:
        # Run all tests
        tests = [
            test_feedback_system_initialization,
            test_rating_feedback_collection,
            test_thumbs_feedback_collection,
            test_feedback_storage_and_retrieval,
            test_feedback_statistics,
            test_response_adaptation,
            test_feedback_edge_cases
        ]
        
        for test_func in tests:
            print(f"Running {test_func.__name__}...")
            test_func(report)
        
        print("\n" + "=" * 55)
        print("Feedback mechanism tests completed!")
        
    except Exception as e:
        error_result = FeedbackTestResult("Feedback Test Suite", False, "Test suite failed to run", e)
        report.add_result(error_result)
        print(f"Test suite error: {e}")
        traceback.print_exc()
    
    return report


def main():
    """Main function to run the feedback mechanism tests."""
    # Run tests
    report = run_feedback_tests()
    
    # Generate and print report
    report_text = report.generate_report()
    print("\n" + report_text)
    
    # Save report to file
    report_path = "test_results_feedback.txt"
    with open(report_path, 'w') as f:
        f.write(report_text)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Return exit code based on test results
    failed_tests = sum(1 for r in report.results if not r.passed)
    return 1 if failed_tests > 0 else 0


if __name__ == "__main__":
    sys.exit(main())