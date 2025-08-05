"""
Input validation utilities for Personal Agent

This module contains functions for validating and sanitizing user inputs.
"""

import re
import bleach
from typing import Optional, Tuple
from ..config.constants import VALIDATION, SECURITY


class ValidationError(Exception):
    """Exception raised for input validation errors."""
    pass


def validate_user_id(user_id: str) -> str:
    """
    Validate a user ID.
    
    Args:
        user_id (str): User ID to validate
        
    Returns:
        str: Validated user ID
        
    Raises:
        ValidationError: If the user ID is invalid
    """
    if not user_id:
        raise ValidationError("User ID cannot be empty")
    
    if not isinstance(user_id, str):
        raise ValidationError("User ID must be a string")
    
    if len(user_id) > VALIDATION.USER_ID_MAX_LENGTH:
        raise ValidationError(f"User ID cannot exceed {VALIDATION.USER_ID_MAX_LENGTH} characters")
    
    # Check for potentially harmful characters
    if re.search(r'[<>"\']', user_id):
        raise ValidationError("User ID contains invalid characters")
    
    return user_id.strip()


def validate_message_content(content: str) -> str:
    """
    Validate message content with backward compatibility.
    
    Args:
        content (str): Message content to validate
        
    Returns:
        str: Validated message content
        
    Raises:
        ValidationError: If the message content is invalid
    """
    return validate_and_sanitize_message(content)


def validate_rating(rating: int, min_rating: int = 1, max_rating: int = 5) -> int:
    """
    Validate a rating value.
    
    Args:
        rating (int): Rating to validate
        min_rating (int): Minimum allowed rating
        max_rating (int): Maximum allowed rating
        
    Returns:
        int: Validated rating
        
    Raises:
        ValidationError: If the rating is invalid
    """
    if not isinstance(rating, int):
        raise ValidationError("Rating must be an integer")
    
    if not (min_rating <= rating <= max_rating):
        raise ValidationError(f"Rating must be between {min_rating} and {max_rating}")
    
    return rating


def validate_feedback_comment(comment: str) -> str:
    """
    Validate feedback comment with backward compatibility.
    
    Args:
        comment (str): Feedback comment to validate
        
    Returns:
        str: Validated feedback comment
        
    Raises:
        ValidationError: If the feedback comment is invalid
    """
    return validate_and_sanitize_feedback(comment)


def validate_message_id(message_id: str) -> str:
    """
    Validate a message ID.
    
    Args:
        message_id (str): Message ID to validate
        
    Returns:
        str: Validated message ID
        
    Raises:
        ValidationError: If the message ID is invalid
    """
    if not message_id:
        raise ValidationError("Message ID cannot be empty")
    
    if not isinstance(message_id, str):
        raise ValidationError("Message ID must be a string")
    
    if len(message_id) > VALIDATION.MESSAGE_ID_MAX_LENGTH:
        raise ValidationError(f"Message ID cannot exceed {VALIDATION.MESSAGE_ID_MAX_LENGTH} characters")
    
    # Check for potentially harmful characters
    if re.search(r'[<>"\']', message_id):
        raise ValidationError("Message ID contains invalid characters")
    
    return message_id.strip()


def sanitize_input(text: str) -> str:
    """
    Sanitize input text using comprehensive HTML sanitization.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return text
    
    # Use bleach to clean HTML tags and attributes
    # Allow only safe tags and attributes
    safe_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a']
    safe_attrs = {
        'a': ['href', 'title'],
    }
    sanitized = bleach.clean(text, tags=safe_tags, attributes=safe_attrs, strip=True)
    
    # Additional sanitization for any remaining harmful patterns
    # Remove potentially harmful quote characters that might have been missed
    sanitized = re.sub(r'["\']', '', sanitized)
    
    # Remove potentially harmful JavaScript keywords and function calls
    js_patterns = [
        r'\b(alert|prompt|confirm|eval|setTimeout|setInterval)\s*\([^)]*\)',
        r'\b(alert|prompt|confirm|eval|setTimeout|setInterval)\b'
    ]
    for pattern in js_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    # Limit length to prevent abuse
    if len(sanitized) > VALIDATION.MESSAGE_CONTENT_MAX_LENGTH:
        sanitized = sanitized[:VALIDATION.MESSAGE_CONTENT_MAX_LENGTH]
    
    return sanitized.strip()


def validate_and_sanitize_message(content: str) -> str:
    """
    Validate and sanitize message content with comprehensive protection.
    
    Args:
        content (str): Message content to validate and sanitize
        
    Returns:
        str: Validated and sanitized message content
        
    Raises:
        ValidationError: If the message content is invalid
    """
    if content is None:
        raise ValidationError("Message content cannot be None")
    
    if not isinstance(content, str):
        raise ValidationError("Message content must be a string")
    
    # Limit message length (adjust as needed)
    if len(content) > VALIDATION.MESSAGE_CONTENT_MAX_LENGTH:
        raise ValidationError(f"Message content cannot exceed {VALIDATION.MESSAGE_CONTENT_MAX_LENGTH:,} characters")
    
    # Use comprehensive sanitization
    sanitized = sanitize_input(content)
    
    return sanitized.strip()


def validate_and_sanitize_feedback(comment: str) -> str:
    """
    Validate and sanitize feedback comment with comprehensive protection.
    
    Args:
        comment (str): Feedback comment to validate and sanitize
        
    Returns:
        str: Validated and sanitized feedback comment
        
    Raises:
        ValidationError: If the feedback comment is invalid
    """
    if comment is None:
        return comment
    
    if not isinstance(comment, str):
        raise ValidationError("Feedback comment must be a string")
    
    # Limit comment length
    if len(comment) > VALIDATION.FEEDBACK_COMMENT_MAX_LENGTH:
        raise ValidationError(f"Feedback comment cannot exceed {VALIDATION.FEEDBACK_COMMENT_MAX_LENGTH:,} characters")
    
    # Use comprehensive sanitization
    sanitized = sanitize_input(comment)
    
    return sanitized.strip()