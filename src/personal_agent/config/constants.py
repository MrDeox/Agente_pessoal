"""
Configuration Constants for Personal Agent

This module centralizes all magic numbers and configuration constants
to improve maintainability and consistency across the application.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ValidationLimits:
    """Validation limits for various inputs."""
    
    # User and Message ID limits
    USER_ID_MAX_LENGTH: int = 100
    MESSAGE_ID_MAX_LENGTH: int = 100
    
    # Content limits
    MESSAGE_CONTENT_MAX_LENGTH: int = 10000
    FEEDBACK_COMMENT_MAX_LENGTH: int = 1000
    
    # Search and pagination limits
    DEFAULT_SEARCH_LIMIT: int = 10
    MAX_SEARCH_LIMIT: int = 100
    
    # Memory limits
    MAX_MEMORY_ITEMS: int = 1000
    MAX_CONVERSATION_HISTORY: int = 10


@dataclass(frozen=True)
class RetrySettings:
    """Retry mechanism settings."""
    
    # Base retry settings
    DEFAULT_BASE_DELAY: float = 1.0
    DEFAULT_MAX_DELAY: float = 60.0
    DEFAULT_EXPONENTIAL_BASE: float = 2.0
    DEFAULT_MAX_ATTEMPTS: int = 3
    
    # Jitter settings
    JITTER_MIN_FACTOR: float = 0.5
    JITTER_MAX_FACTOR: float = 1.5
    
    # LLM specific retry settings
    LLM_MAX_ATTEMPTS: int = 5
    LLM_BASE_DELAY: float = 2.0
    LLM_MAX_DELAY: float = 120.0


@dataclass(frozen=True)
class RateLimitSettings:
    """Rate limiting settings."""
    
    # Default rate limits
    DEFAULT_REQUESTS_PER_MINUTE: int = 60
    DEFAULT_RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # LLM provider rate limits
    OPENAI_REQUESTS_PER_MINUTE: int = 60
    OPENROUTER_REQUESTS_PER_MINUTE: int = 200
    
    # Burst limits
    DEFAULT_BURST_LIMIT: int = 10


@dataclass(frozen=True)
class DatabaseSettings:
    """Database configuration settings."""
    
    # Connection pool settings
    DEFAULT_POOL_SIZE: int = 5
    MAX_POOL_SIZE: int = 20
    
    # Query timeouts (seconds)
    DEFAULT_QUERY_TIMEOUT: int = 30
    LONG_QUERY_TIMEOUT: int = 300
    
    # Batch processing
    DEFAULT_BATCH_SIZE: int = 100
    MAX_BATCH_SIZE: int = 1000


@dataclass(frozen=True)
class LLMSettings:
    """LLM configuration settings."""
    
    # Default model parameters
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 1000
    DEFAULT_TOP_P: float = 1.0
    DEFAULT_FREQUENCY_PENALTY: float = 0.0
    DEFAULT_PRESENCE_PENALTY: float = 0.0
    
    # Context limits
    DEFAULT_CONTEXT_WINDOW: int = 4096
    MAX_CONTEXT_WINDOW: int = 32768
    
    # Timeout settings
    DEFAULT_TIMEOUT: int = 30  # seconds
    LONG_TIMEOUT: int = 120    # seconds


@dataclass(frozen=True)
class FeedbackSettings:
    """Feedback system settings."""
    
    # Rating scale
    MIN_RATING: int = 1
    MAX_RATING: int = 5
    DEFAULT_RATING_SCALE: int = 5
    
    # Adaptation thresholds
    DEFAULT_ADAPT_THRESHOLD: int = 3
    MIN_FEEDBACK_COUNT: int = 5  # Minimum feedback before adaptation
    
    # Collection settings
    FEEDBACK_COLLECTION_ENABLED: bool = True


@dataclass(frozen=True)
class ContextSettings:
    """Context processing settings."""
    
    # Relevance scoring
    MIN_RELEVANCE_SCORE: float = 0.0
    MAX_RELEVANCE_SCORE: float = 1.0
    DEFAULT_RELEVANCE_THRESHOLD: float = 0.5
    
    # Entity extraction confidence
    MIN_ENTITY_CONFIDENCE: float = 0.0
    MAX_ENTITY_CONFIDENCE: float = 1.0
    DEFAULT_ENTITY_THRESHOLD: float = 0.7
    
    # Relationship confidence
    MIN_RELATIONSHIP_CONFIDENCE: float = 0.0
    MAX_RELATIONSHIP_CONFIDENCE: float = 1.0
    DEFAULT_RELATIONSHIP_THRESHOLD: float = 0.6


@dataclass(frozen=True)
class ConversationSettings:
    """Conversation management settings."""
    
    # Turn limits
    MAX_TURNS_PER_SESSION: int = 100
    DEFAULT_HISTORY_WINDOW: int = 10
    
    # Timeout settings
    SESSION_TIMEOUT: int = 3600  # 1 hour in seconds
    IDLE_TIMEOUT: int = 1800     # 30 minutes in seconds
    
    # Processing limits
    MAX_PARALLEL_CONVERSATIONS: int = 10


@dataclass(frozen=True)
class SecuritySettings:
    """Security and validation settings."""
    
    # Input sanitization
    ALLOW_HTML: bool = False
    STRIP_WHITESPACE: bool = True
    
    # Content filtering
    MAX_URL_LENGTH: int = 2048
    MAX_FILE_PATH_LENGTH: int = 4096
    
    # API security
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    DEFAULT_CORS_MAX_AGE: int = 86400         # 24 hours


@dataclass(frozen=True)
class LoggingSettings:
    """Logging configuration settings."""
    
    # Log levels
    DEFAULT_LOG_LEVEL: str = "INFO"
    DEBUG_LOG_LEVEL: str = "DEBUG"
    
    # File settings
    MAX_LOG_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_LOG_FILES: int = 5
    
    # Format settings
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class CacheSettings:
    """Cache configuration settings."""
    
    # TTL settings (seconds)
    DEFAULT_TTL: int = 3600      # 1 hour
    SHORT_TTL: int = 300         # 5 minutes
    LONG_TTL: int = 86400        # 24 hours
    
    # Size limits
    DEFAULT_CACHE_SIZE: int = 1000
    MAX_CACHE_SIZE: int = 10000
    
    # LLM cache specific
    LLM_CACHE_TTL: int = 7200    # 2 hours
    LLM_CACHE_SIZE: int = 500


# Global constants instance - use these throughout the application
VALIDATION = ValidationLimits()
RETRY = RetrySettings()
RATE_LIMIT = RateLimitSettings()
DATABASE = DatabaseSettings()
LLM = LLMSettings()
FEEDBACK = FeedbackSettings()
CONTEXT = ContextSettings()
CONVERSATION = ConversationSettings()
SECURITY = SecuritySettings()
LOGGING = LoggingSettings()
CACHE = CacheSettings()


# Utility function to get all constants as a dictionary
def get_all_constants() -> Dict[str, Any]:
    """
    Get all configuration constants as a dictionary.
    
    Returns:
        Dictionary containing all configuration constants
    """
    return {
        "validation": VALIDATION,
        "retry": RETRY,
        "rate_limit": RATE_LIMIT,
        "database": DATABASE,
        "llm": LLM,
        "feedback": FEEDBACK,
        "context": CONTEXT,
        "conversation": CONVERSATION,
        "security": SECURITY,
        "logging": LOGGING,
        "cache": CACHE,
    }


# Environment-specific overrides (for testing, development, etc.)
def get_test_constants() -> Dict[str, Any]:
    """
    Get test-specific constant overrides.
    
    Returns:
        Dictionary with test-specific values
    """
    return {
        "database": DatabaseSettings(
            DEFAULT_POOL_SIZE=1,
            DEFAULT_QUERY_TIMEOUT=5
        ),
        "retry": RetrySettings(
            DEFAULT_MAX_ATTEMPTS=1,
            DEFAULT_BASE_DELAY=0.1,
            DEFAULT_MAX_DELAY=1.0
        ),
        "llm": LLMSettings(
            DEFAULT_TIMEOUT=5,
            DEFAULT_MAX_TOKENS=100
        )
    }