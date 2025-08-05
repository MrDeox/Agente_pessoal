#!/usr/bin/env python3
"""
Test script for validation functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.utils.validation import (
    validate_user_id, validate_message_content, validate_rating, 
    validate_feedback_comment, validate_message_id, ValidationError
)


def test_user_id_validation():
    """Test user ID validation."""
    print("Testing user ID validation...")
    
    # Test valid user ID
    try:
        result = validate_user_id("user123")
        assert result == "user123"
        print("✓ Valid user ID test passed")
    except Exception as e:
        print(f"✗ Valid user ID test failed: {e}")
        return False
    
    # Test empty user ID
    try:
        validate_user_id("")
        print("✗ Empty user ID test failed (should have raised exception)")
        return False
    except ValidationError:
        print("✓ Empty user ID validation test passed")
    except Exception as e:
        print(f"✗ Empty user ID test failed with unexpected error: {e}")
        return False
    
    # Test user ID with invalid characters
    try:
        validate_user_id("user<script>")
        print("✗ Invalid characters test failed (should have raised exception)")
        return False
    except ValidationError:
        print("✓ Invalid characters validation test passed")
    except Exception as e:
        print(f"✗ Invalid characters test failed with unexpected error: {e}")
        return False
    
    return True


def test_message_content_validation():
    """Test message content validation."""
    print("\nTesting message content validation...")
    
    # Test valid message content
    try:
        result = validate_message_content("Hello, this is a test message!")
        assert result == "Hello, this is a test message!"
        print("✓ Valid message content test passed")
    except Exception as e:
        print(f"✗ Valid message content test failed: {e}")
        return False
    
    # Test message content with invalid characters
    try:
        result = validate_message_content("Hello <script>alert('test')</script>")
        # Should be sanitized
        # With bleach, script tags are removed entirely
        assert result == "Hello alert(test)"
        print("✓ Message sanitization test passed")
    except Exception as e:
        print(f"✗ Message sanitization test failed: {e}")
        return False
    
    # Test empty message content
    try:
        result = validate_message_content("")
        assert result == ""
        print("✓ Empty message content test passed")
    except Exception as e:
        print(f"✗ Empty message content test failed: {e}")
        return False
    
    # Test None message content
    try:
        validate_message_content(None)
        print("✗ None message content test failed (should have raised exception)")
        return False
    except ValidationError:
        print("✓ None message content validation test passed")
    except Exception as e:
        print(f"✗ None message content test failed with unexpected error: {e}")
        return False
    
    return True


def test_rating_validation():
    """Test rating validation."""
    print("\nTesting rating validation...")
    
    # Test valid rating
    try:
        result = validate_rating(3)
        assert result == 3
        print("✓ Valid rating test passed")
    except Exception as e:
        print(f"✗ Valid rating test failed: {e}")
        return False
    
    # Test invalid rating (too low)
    try:
        validate_rating(0)
        print("✗ Invalid low rating test failed (should have raised exception)")
        return False
    except ValidationError:
        print("✓ Invalid low rating validation test passed")
    except Exception as e:
        print(f"✗ Invalid low rating test failed with unexpected error: {e}")
        return False
    
    # Test invalid rating (too high)
    try:
        validate_rating(6)
        print("✗ Invalid high rating test failed (should have raised exception)")
        return False
    except ValidationError:
        print("✓ Invalid high rating validation test passed")
    except Exception as e:
        print(f"✗ Invalid high rating test failed with unexpected error: {e}")
        return False
    
    return True


def test_feedback_comment_validation():
    """Test feedback comment validation."""
    print("\nTesting feedback comment validation...")
    
    # Test valid comment
    try:
        result = validate_feedback_comment("This is a great feature!")
        assert result == "This is a great feature!"
        print("✓ Valid comment test passed")
    except Exception as e:
        print(f"✗ Valid comment test failed: {e}")
        return False
    
    # Test None comment (should be allowed)
    try:
        result = validate_feedback_comment(None)
        assert result is None
        print("✓ None comment test passed")
    except Exception as e:
        print(f"✗ None comment test failed: {e}")
        return False
    
    # Test comment with invalid characters
    try:
        result = validate_feedback_comment("Great feature! <script>alert('test')</script>")
        # Should be sanitized
        # With bleach, script tags are removed entirely
        assert result == "Great feature! alert(test)"
        print("✓ Comment sanitization test passed")
    except Exception as e:
        print(f"✗ Comment sanitization test failed: {e}")
        return False
    
    return True


def test_enhanced_sanitization():
    """Test enhanced sanitization features."""
    print("\nTesting enhanced sanitization...")
    
    # Test complex HTML sanitization
    try:
        result = validate_message_content("Hello <script>alert('test')</script><img src=x onerror=alert('xss')>")
        # With bleach, script tags and onerror attributes should be removed
        assert result == "Hello alert(test)"
        print("✓ Complex HTML sanitization test passed")
    except Exception as e:
        print(f"✗ Complex HTML sanitization test failed: {e}")
        return False
    
    # Test allowed HTML tags
    try:
        result = validate_message_content("Hello <strong>world</strong>!")
        # Strong tags should be preserved
        assert result == "Hello <strong>world</strong>!"
        print("✓ Allowed HTML tags preservation test passed")
    except Exception as e:
        print(f"✗ Allowed HTML tags preservation test failed: {e}")
        return False
    
    # Test disallowed HTML attributes
    try:
        result = validate_message_content('<a href="http://example.com" onclick="alert(\'xss\')">link</a>')
        # onclick attribute should be removed but href should be preserved
        assert result == '<a href=http://example.com>link</a>'
        print("✓ Disallowed HTML attributes removal test passed")
    except Exception as e:
        print(f"✗ Disallowed HTML attributes removal test failed: {e}")
        return False
    
    return True


def test_message_id_validation():
    """Test message ID validation."""
    print("\nTesting message ID validation...")
    
    # Test valid message ID
    try:
        result = validate_message_id("msg-12345")
        assert result == "msg-12345"
        print("✓ Valid message ID test passed")
    except Exception as e:
        print(f"✗ Valid message ID test failed: {e}")
        return False
    
    # Test empty message ID
    try:
        validate_message_id("")
        print("✗ Empty message ID test failed (should have raised exception)")
        return False
    except ValidationError:
        print("✓ Empty message ID validation test passed")
    except Exception as e:
        print(f"✗ Empty message ID test failed with unexpected error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("Running validation tests...\n")
    
    success = True
    success &= test_user_id_validation()
    success &= test_message_content_validation()
    success &= test_rating_validation()
    success &= test_feedback_comment_validation()
    success &= test_message_id_validation()
    success &= test_enhanced_sanitization()
    
    if success:
        print("\n✓ All validation tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some validation tests failed!")
        sys.exit(1)