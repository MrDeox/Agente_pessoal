#!/usr/bin/env python3
"""
Test script for common utility functions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.personal_agent.utils.common import generate_id, find_conversation_id


def test_generate_id():
    """Test the generate_id function."""
    print("Testing generate_id function...")
    
    # Generate two IDs and make sure they're different
    id1 = generate_id()
    id2 = generate_id()
    
    print(f"Generated ID 1: {id1}")
    print(f"Generated ID 2: {id2}")
    
    assert id1 != id2, "Generated IDs should be unique"
    assert isinstance(id1, str), "Generated ID should be a string"
    assert len(id1) > 0, "Generated ID should not be empty"
    
    print("generate_id test passed!")


def test_find_conversation_id():
    """Test the find_conversation_id function."""
    print("\nTesting find_conversation_id function...")
    
    # Test with empty conversation history
    conversation_history = []
    message_id = "test_message_id"
    result = find_conversation_id(conversation_history, message_id)
    assert result is None, "Should return None for empty conversation history"
    
    # Test with conversation history that doesn't contain the message
    conversation_history = [
        {"id": "msg1", "conversation_id": "conv1"},
        {"id": "msg2", "conversation_id": "conv2"}
    ]
    result = find_conversation_id(conversation_history, "msg3")
    assert result is None, "Should return None when message not found"
    
    # Test with conversation history that contains the message
    conversation_history = [
        {"id": "msg1", "conversation_id": "conv1"},
        {"id": "msg2", "conversation_id": "conv2"},
        {"id": "msg3", "conversation_id": "conv3"}
    ]
    result = find_conversation_id(conversation_history, "msg2")
    assert result == "conv2", f"Should return 'conv2', got {result}"
    
    # Test with conversation history where message has no conversation_id
    conversation_history = [
        {"id": "msg1", "conversation_id": "conv1"},
        {"id": "msg2"},  # No conversation_id
        {"id": "msg3", "conversation_id": "conv3"}
    ]
    result = find_conversation_id(conversation_history, "msg2")
    assert result is None, f"Should return None, got {result}"
    
    print("find_conversation_id test passed!")


def main():
    """Run all tests."""
    print("Testing common utility functions...")
    
    test_generate_id()
    test_find_conversation_id()
    
    print("\nAll tests passed!")


if __name__ == "__main__":
    main()