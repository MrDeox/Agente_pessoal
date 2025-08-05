"""
Unit tests for configuration constants.

Tests the new constants module created during refactoring.
"""

import pytest
from src.personal_agent.config.constants import (
    VALIDATION, RETRY, RATE_LIMIT, DATABASE, LLM, FEEDBACK,
    CONTEXT, CONVERSATION, SECURITY, LOGGING, CACHE,
    get_all_constants, get_test_constants
)


class TestValidationConstants:
    """Test validation constants."""
    
    def test_validation_limits(self):
        """Test validation limit constants."""
        assert VALIDATION.USER_ID_MAX_LENGTH == 100
        assert VALIDATION.MESSAGE_ID_MAX_LENGTH == 100
        assert VALIDATION.MESSAGE_CONTENT_MAX_LENGTH == 10000
        assert VALIDATION.FEEDBACK_COMMENT_MAX_LENGTH == 1000
        assert VALIDATION.DEFAULT_SEARCH_LIMIT == 10
        assert VALIDATION.MAX_SEARCH_LIMIT == 100
        assert VALIDATION.MAX_MEMORY_ITEMS == 1000
        assert VALIDATION.MAX_CONVERSATION_HISTORY == 10


class TestRetryConstants:
    """Test retry constants."""
    
    def test_retry_settings(self):
        """Test retry setting constants."""
        assert RETRY.DEFAULT_BASE_DELAY == 1.0
        assert RETRY.DEFAULT_MAX_DELAY == 60.0
        assert RETRY.DEFAULT_EXPONENTIAL_BASE == 2.0
        assert RETRY.DEFAULT_MAX_ATTEMPTS == 3
        assert RETRY.JITTER_MIN_FACTOR == 0.5
        assert RETRY.JITTER_MAX_FACTOR == 1.5
        assert RETRY.LLM_MAX_ATTEMPTS == 5
        assert RETRY.LLM_BASE_DELAY == 2.0
        assert RETRY.LLM_MAX_DELAY == 120.0


class TestRateLimitConstants:
    """Test rate limit constants."""
    
    def test_rate_limit_settings(self):
        """Test rate limit setting constants."""
        assert RATE_LIMIT.DEFAULT_REQUESTS_PER_MINUTE == 60
        assert RATE_LIMIT.DEFAULT_RATE_LIMIT_PERIOD == 60
        assert RATE_LIMIT.OPENAI_REQUESTS_PER_MINUTE == 60
        assert RATE_LIMIT.OPENROUTER_REQUESTS_PER_MINUTE == 200
        assert RATE_LIMIT.DEFAULT_BURST_LIMIT == 10


class TestDatabaseConstants:
    """Test database constants."""
    
    def test_database_settings(self):
        """Test database setting constants."""
        assert DATABASE.DEFAULT_POOL_SIZE == 5
        assert DATABASE.MAX_POOL_SIZE == 20
        assert DATABASE.DEFAULT_QUERY_TIMEOUT == 30
        assert DATABASE.LONG_QUERY_TIMEOUT == 300
        assert DATABASE.DEFAULT_BATCH_SIZE == 100
        assert DATABASE.MAX_BATCH_SIZE == 1000


class TestLLMConstants:
    """Test LLM constants."""
    
    def test_llm_settings(self):
        """Test LLM setting constants."""
        assert LLM.DEFAULT_TEMPERATURE == 0.7
        assert LLM.DEFAULT_MAX_TOKENS == 1000
        assert LLM.DEFAULT_TOP_P == 1.0
        assert LLM.DEFAULT_FREQUENCY_PENALTY == 0.0
        assert LLM.DEFAULT_PRESENCE_PENALTY == 0.0
        assert LLM.DEFAULT_CONTEXT_WINDOW == 4096
        assert LLM.MAX_CONTEXT_WINDOW == 32768
        assert LLM.DEFAULT_TIMEOUT == 30
        assert LLM.LONG_TIMEOUT == 120


class TestFeedbackConstants:
    """Test feedback constants."""
    
    def test_feedback_settings(self):
        """Test feedback setting constants."""
        assert FEEDBACK.MIN_RATING == 1
        assert FEEDBACK.MAX_RATING == 5
        assert FEEDBACK.DEFAULT_RATING_SCALE == 5
        assert FEEDBACK.DEFAULT_ADAPT_THRESHOLD == 3
        assert FEEDBACK.MIN_FEEDBACK_COUNT == 5
        assert FEEDBACK.FEEDBACK_COLLECTION_ENABLED is True


class TestContextConstants:
    """Test context constants."""
    
    def test_context_settings(self):
        """Test context setting constants."""
        assert CONTEXT.MIN_RELEVANCE_SCORE == 0.0
        assert CONTEXT.MAX_RELEVANCE_SCORE == 1.0
        assert CONTEXT.DEFAULT_RELEVANCE_THRESHOLD == 0.5
        assert CONTEXT.MIN_ENTITY_CONFIDENCE == 0.0
        assert CONTEXT.MAX_ENTITY_CONFIDENCE == 1.0
        assert CONTEXT.DEFAULT_ENTITY_THRESHOLD == 0.7
        assert CONTEXT.MIN_RELATIONSHIP_CONFIDENCE == 0.0
        assert CONTEXT.MAX_RELATIONSHIP_CONFIDENCE == 1.0
        assert CONTEXT.DEFAULT_RELATIONSHIP_THRESHOLD == 0.6


class TestConversationConstants:
    """Test conversation constants."""
    
    def test_conversation_settings(self):
        """Test conversation setting constants."""
        assert CONVERSATION.MAX_TURNS_PER_SESSION == 100
        assert CONVERSATION.DEFAULT_HISTORY_WINDOW == 10
        assert CONVERSATION.SESSION_TIMEOUT == 3600
        assert CONVERSATION.IDLE_TIMEOUT == 1800
        assert CONVERSATION.MAX_PARALLEL_CONVERSATIONS == 10


class TestSecurityConstants:
    """Test security constants."""
    
    def test_security_settings(self):
        """Test security setting constants."""
        assert SECURITY.ALLOW_HTML is False
        assert SECURITY.STRIP_WHITESPACE is True
        assert SECURITY.MAX_URL_LENGTH == 2048
        assert SECURITY.MAX_FILE_PATH_LENGTH == 4096
        assert SECURITY.MAX_REQUEST_SIZE == 10 * 1024 * 1024
        assert SECURITY.DEFAULT_CORS_MAX_AGE == 86400


class TestLoggingConstants:
    """Test logging constants."""
    
    def test_logging_settings(self):
        """Test logging setting constants."""
        assert LOGGING.DEFAULT_LOG_LEVEL == "INFO"
        assert LOGGING.DEBUG_LOG_LEVEL == "DEBUG"
        assert LOGGING.MAX_LOG_FILE_SIZE == 10 * 1024 * 1024
        assert LOGGING.MAX_LOG_FILES == 5
        assert LOGGING.LOG_FORMAT == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert LOGGING.DATE_FORMAT == "%Y-%m-%d %H:%M:%S"


class TestCacheConstants:
    """Test cache constants."""
    
    def test_cache_settings(self):
        """Test cache setting constants."""
        assert CACHE.DEFAULT_TTL == 3600
        assert CACHE.SHORT_TTL == 300
        assert CACHE.LONG_TTL == 86400
        assert CACHE.DEFAULT_CACHE_SIZE == 1000
        assert CACHE.MAX_CACHE_SIZE == 10000
        assert CACHE.LLM_CACHE_TTL == 7200
        assert CACHE.LLM_CACHE_SIZE == 500


class TestConstantUtilities:
    """Test constant utility functions."""
    
    def test_get_all_constants(self):
        """Test getting all constants."""
        all_constants = get_all_constants()
        
        assert isinstance(all_constants, dict)
        assert "validation" in all_constants
        assert "retry" in all_constants
        assert "rate_limit" in all_constants
        assert "database" in all_constants
        assert "llm" in all_constants
        assert "feedback" in all_constants
        assert "context" in all_constants
        assert "conversation" in all_constants
        assert "security" in all_constants
        assert "logging" in all_constants
        assert "cache" in all_constants
        
        # Verify the constants are the expected objects
        assert all_constants["validation"] is VALIDATION
        assert all_constants["retry"] is RETRY
        assert all_constants["llm"] is LLM
    
    def test_get_test_constants(self):
        """Test getting test-specific constants."""
        test_constants = get_test_constants()
        
        assert isinstance(test_constants, dict)
        assert "database" in test_constants
        assert "retry" in test_constants
        assert "llm" in test_constants
        
        # Test constants should have different values
        assert test_constants["database"].DEFAULT_POOL_SIZE == 1
        assert test_constants["retry"].DEFAULT_MAX_ATTEMPTS == 1
        assert test_constants["llm"].DEFAULT_TIMEOUT == 5


class TestConstantImmutability:
    """Test that constants are immutable (frozen dataclasses)."""
    
    def test_validation_constants_immutable(self):
        """Test that validation constants cannot be modified."""
        with pytest.raises(AttributeError):
            VALIDATION.USER_ID_MAX_LENGTH = 200
    
    def test_retry_constants_immutable(self):
        """Test that retry constants cannot be modified."""
        with pytest.raises(AttributeError):
            RETRY.DEFAULT_BASE_DELAY = 2.0
    
    def test_llm_constants_immutable(self):
        """Test that LLM constants cannot be modified."""
        with pytest.raises(AttributeError):
            LLM.DEFAULT_TEMPERATURE = 0.5