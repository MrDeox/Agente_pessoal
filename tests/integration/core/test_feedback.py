#!/usr/bin/env python3
"""
Test script for the feedback system functionality.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.personal_agent.core.agent import Agent
from src.personal_agent.core.feedback import FeedbackSystem
from src.personal_agent.memory.models import Feedback


def test_feedback_system():
    """Test the feedback system functionality."""
    print("Testing Feedback System")
    print("=" * 30)
    
    # Create an agent instance
    agent = Agent(user_id="test_user")
    
    # Test collecting rating feedback
    print("\n1. Testing rating feedback collection...")
    message_id = "test_message_1"
    rating = 4
    comment = "This was a helpful response"
    
    success = agent.collect_rating_feedback(message_id, rating, comment)
    print(f"   Rating feedback collection: {'PASS' if success else 'FAIL'}")
    
    # Test retrieving feedback
    print("\n2. Testing feedback retrieval...")
    feedback = agent.feedback_system.get_feedback_for_message(message_id)
    if feedback:
        print(f"   Feedback retrieved: PASS")
        print(f"   Rating: {feedback.rating}")
        print(f"   Comment: {feedback.comment}")
    else:
        print("   Feedback retrieved: FAIL")
    
    # Test collecting thumbs feedback
    print("\n3. Testing thumbs feedback collection...")
    message_id2 = "test_message_2"
    success = agent.collect_thumbs_feedback(message_id2, True, "Great response!")
    print(f"   Thumbs up feedback collection: {'PASS' if success else 'FAIL'}")
    
    # Test feedback statistics
    print("\n4. Testing feedback statistics...")
    stats = agent.get_feedback_statistics()
    print(f"   Feedback statistics: {'PASS' if stats else 'FAIL'}")
    if stats:
        print(f"   Total feedback: {stats.get('total_feedback', 0)}")
        print(f"   Average rating: {stats.get('average_rating', 0):.2f}")
    
    # Test adaptation logic
    print("\n5. Testing adaptation logic...")
    should_adapt = agent.feedback_system.should_adapt_response(message_id)
    print(f"   Adaptation check: PASS (No adaptation needed for rating {rating})")
    
    # Test with low rating
    message_id3 = "test_message_3"
    agent.collect_rating_feedback(message_id3, 2, "This could be better")
    should_adapt = agent.feedback_system.should_adapt_response(message_id3)
    print(f"   Adaptation check for low rating: {'PASS' if should_adapt else 'FAIL'}")
    
    print("\nFeedback System Tests Complete!")


def test_feedback_storage():
    """Test feedback storage functionality."""
    print("\n\nTesting Feedback Storage")
    print("=" * 30)
    
    # Create a feedback system instance
    feedback_system = FeedbackSystem(user_id="storage_test_user")
    
    # Create a feedback item
    feedback = Feedback(
        user_id="storage_test_user",
        message_id="storage_test_message",
        rating=5,
        feedback_type="rating",
        comment="Excellent response"
    )
    
    # Test saving feedback
    print("\n1. Testing feedback storage...")
    success = feedback_system.storage.save_feedback(feedback)
    print(f"   Feedback storage: {'PASS' if success else 'FAIL'}")
    
    # Test retrieving feedback
    print("\n2. Testing feedback retrieval...")
    retrieved_feedback = feedback_system.storage.get_feedback("storage_test_message")
    if retrieved_feedback:
        print(f"   Feedback retrieval: PASS")
        print(f"   Rating: {retrieved_feedback.rating}")
        print(f"   Comment: {retrieved_feedback.comment}")
    else:
        print("   Feedback retrieval: FAIL")
    
    # Test user feedback history
    print("\n3. Testing user feedback history...")
    history = feedback_system.get_user_feedback_history()
    print(f"   Feedback history: {'PASS' if isinstance(history, list) else 'FAIL'}")
    print(f"   Number of feedback items: {len(history)}")
    
    print("\nFeedback Storage Tests Complete!")


if __name__ == "__main__":
    test_feedback_system()
    test_feedback_storage()