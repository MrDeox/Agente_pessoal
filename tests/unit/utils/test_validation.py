"""
Unit tests for validation utilities.

Migrated from scripts/test_validation.py with improvements and constants integration.
"""

import pytest
from src.personal_agent.utils.validation import (
    ValidationError,
    validate_user_id,
    validate_message_content,
    validate_rating,
    validate_feedback_comment,
    validate_message_id,
    sanitize_input,
    validate_and_sanitize_message,
    validate_and_sanitize_feedback
)
from src.personal_agent.config.constants import VALIDATION, FEEDBACK


class TestValidationError:
    """Test ValidationError exception."""
    
    def test_validation_error_creation(self):
        """Test creating ValidationError."""
        error = ValidationError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestUserIdValidation:
    """Test user ID validation."""
    
    def test_valid_user_id(self):
        """Test validation of valid user IDs."""
        assert validate_user_id("user123") == "user123"
        assert validate_user_id("test_user") == "test_user"
        assert validate_user_id("user-456") == "user-456"
        assert validate_user_id("a" * 100) == "a" * 100
    
    def test_user_id_with_whitespace(self):
        """Test user ID validation with whitespace."""
        assert validate_user_id("  user123  ") == "user123"
        assert validate_user_id("\tuser456\n") == "user456"
    
    def test_empty_user_id(self):
        """Test validation of empty user ID."""
        with pytest.raises(ValidationError, match="User ID cannot be empty"):
            validate_user_id("")
        
        with pytest.raises(ValidationError, match="User ID cannot be empty"):
            validate_user_id(None)
    
    def test_non_string_user_id(self):
        """Test validation of non-string user ID."""
        with pytest.raises(ValidationError, match="User ID must be a string"):
            validate_user_id(123)
        
        with pytest.raises(ValidationError, match="User ID must be a string"):
            validate_user_id(["user"])
    
    def test_user_id_too_long(self):
        """Test validation of user ID that's too long."""
        long_id = "a" * (VALIDATION.USER_ID_MAX_LENGTH + 1)
        with pytest.raises(ValidationError, match=f"User ID cannot exceed {VALIDATION.USER_ID_MAX_LENGTH} characters"):
            validate_user_id(long_id)
    
    def test_user_id_invalid_characters(self):
        """Test validation of user ID with invalid characters."""
        with pytest.raises(ValidationError, match="User ID contains invalid characters"):
            validate_user_id("user<script>")
        
        with pytest.raises(ValidationError, match="User ID contains invalid characters"):
            validate_user_id('user"test')
        
        with pytest.raises(ValidationError, match="User ID contains invalid characters"):
            validate_user_id("user'test")


class TestMessageContentValidation:
    """Test message content validation."""
    
    def test_valid_message_content(self):
        """Test validation of valid message content."""
        content = "Hello, how are you?"
        result = validate_message_content(content)
        assert result == content
    
    def test_message_content_sanitization(self):
        """Test message content sanitization."""
        content = "<script>alert('test')</script>Hello"
        result = validate_message_content(content)
        assert "script" not in result
        assert "Hello" in result
    
    def test_empty_message_content(self):
        """Test validation of empty message content."""
        # Empty string should be allowed after sanitization
        result = validate_message_content("")
        assert result == ""
    
    def test_none_message_content(self):
        """Test validation of None message content."""
        with pytest.raises(ValidationError, match="Message content cannot be None"):
            validate_message_content(None)
    
    def test_non_string_message_content(self):
        """Test validation of non-string message content."""
        with pytest.raises(ValidationError, match="Message content must be a string"):
            validate_message_content(123)
    
    def test_message_content_too_long(self):
        """Test validation of message content that's too long."""
        long_content = "a" * (VALIDATION.MESSAGE_CONTENT_MAX_LENGTH + 1)
        with pytest.raises(ValidationError, match=f"Message content cannot exceed {VALIDATION.MESSAGE_CONTENT_MAX_LENGTH:,} characters"):
            validate_message_content(long_content)


class TestRatingValidation:
    """Test rating validation."""
    
    def test_valid_ratings(self):
        """Test validation of valid ratings."""
        for rating in range(FEEDBACK.MIN_RATING, FEEDBACK.MAX_RATING + 1):
            assert validate_rating(rating) == rating
    
    def test_custom_rating_range(self):
        """Test validation with custom rating range."""
        assert validate_rating(3, min_rating=1, max_rating=10) == 3
        assert validate_rating(7, min_rating=1, max_rating=10) == 7
    
    def test_non_integer_rating(self):
        """Test validation of non-integer rating."""
        with pytest.raises(ValidationError, match="Rating must be an integer"):
            validate_rating(3.5)
        
        with pytest.raises(ValidationError, match="Rating must be an integer"):
            validate_rating("3")
    
    def test_rating_out_of_range(self):
        """Test validation of rating out of range."""
        with pytest.raises(ValidationError, match=f"Rating must be between {FEEDBACK.MIN_RATING} and {FEEDBACK.MAX_RATING}"):
            validate_rating(0)
        
        with pytest.raises(ValidationError, match=f"Rating must be between {FEEDBACK.MIN_RATING} and {FEEDBACK.MAX_RATING}"):
            validate_rating(6)
    
    def test_custom_range_out_of_bounds(self):
        """Test validation with custom range out of bounds."""
        with pytest.raises(ValidationError, match="Rating must be between 1 and 10"):
            validate_rating(11, min_rating=1, max_rating=10)


class TestFeedbackCommentValidation:
    """Test feedback comment validation."""
    
    def test_valid_feedback_comment(self):
        """Test validation of valid feedback comment."""
        comment = "This was very helpful, thank you!"
        result = validate_feedback_comment(comment)
        assert result == comment
    
    def test_none_feedback_comment(self):
        """Test validation of None feedback comment."""
        result = validate_feedback_comment(None)
        assert result is None
    
    def test_feedback_comment_sanitization(self):
        """Test feedback comment sanitization."""
        comment = "<b>Great response!</b>"
        result = validate_feedback_comment(comment)
        assert "Great response!" in result
    
    def test_non_string_feedback_comment(self):
        """Test validation of non-string feedback comment."""
        with pytest.raises(ValidationError, match="Feedback comment must be a string"):
            validate_feedback_comment(123)
    
    def test_feedback_comment_too_long(self):
        """Test validation of feedback comment that's too long."""
        long_comment = "a" * (VALIDATION.FEEDBACK_COMMENT_MAX_LENGTH + 1)
        with pytest.raises(ValidationError, match=f"Feedback comment cannot exceed {VALIDATION.FEEDBACK_COMMENT_MAX_LENGTH:,} characters"):
            validate_feedback_comment(long_comment)


class TestMessageIdValidation:
    """Test message ID validation."""
    
    def test_valid_message_id(self):
        """Test validation of valid message IDs."""
        assert validate_message_id("msg_123") == "msg_123"
        assert validate_message_id("message-456") == "message-456"
    
    def test_empty_message_id(self):
        """Test validation of empty message ID."""
        with pytest.raises(ValidationError, match="Message ID cannot be empty"):
            validate_message_id("")
    
    def test_message_id_too_long(self):
        """Test validation of message ID that's too long."""
        long_id = "a" * (VALIDATION.MESSAGE_ID_MAX_LENGTH + 1)
        with pytest.raises(ValidationError, match=f"Message ID cannot exceed {VALIDATION.MESSAGE_ID_MAX_LENGTH} characters"):
            validate_message_id(long_id)


class TestInputSanitization:
    """Test input sanitization."""
    
    def test_basic_sanitization(self):
        """Test basic input sanitization."""
        result = sanitize_input("Hello world")
        assert result == "Hello world"
    
    def test_html_sanitization(self):
        """Test HTML sanitization."""
        result = sanitize_input("<script>alert('xss')</script>Hello")
        assert "script" not in result
        assert "Hello" in result
    
    def test_allowed_html_tags(self):
        """Test that allowed HTML tags are preserved."""
        result = sanitize_input("<p>Hello <strong>world</strong></p>")
        assert "<p>" in result
        assert "<strong>" in result
        assert "Hello" in result
        assert "world" in result
    
    def test_disallowed_html_attributes(self):
        """Test that disallowed HTML attributes are removed."""
        result = sanitize_input('<a href="http://example.com" onclick="alert()">Link</a>')
        assert 'onclick' not in result
        assert 'href' in result  # href is allowed for <a> tags
        assert "Link" in result
    
    def test_quote_removal(self):
        """Test that quotes are removed."""
        result = sanitize_input('Hello "world" and \'test\'')
        assert '"' not in result
        assert "'" not in result
        assert "Hello" in result
        assert "world" in result
        assert "test" in result
    
    def test_length_limiting(self):
        """Test that input length is limited."""
        long_input = "a" * (VALIDATION.MESSAGE_CONTENT_MAX_LENGTH + 1000)
        result = sanitize_input(long_input)
        assert len(result) <= VALIDATION.MESSAGE_CONTENT_MAX_LENGTH
    
    def test_empty_input_sanitization(self):
        """Test sanitization of empty input."""
        assert sanitize_input("") == ""
        assert sanitize_input(None) is None


class TestIntegratedValidation:
    """Test integrated validation functions."""
    
    def test_validate_and_sanitize_message(self):
        """Test integrated message validation and sanitization."""
        content = "<p>Hello <script>alert('test')</script>world</p>"
        result = validate_and_sanitize_message(content)
        assert "Hello" in result
        assert "world" in result
        assert "script" not in result
        assert "alert" not in result
    
    def test_validate_and_sanitize_feedback(self):
        """Test integrated feedback validation and sanitization."""
        comment = "<b>Great job!</b> Really helpful."
        result = validate_and_sanitize_feedback(comment)
        assert "Great job!" in result
        assert "Really helpful" in result