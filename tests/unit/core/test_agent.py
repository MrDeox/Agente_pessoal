"""
Unit tests for core Agent class.

Tests Agent functionality with proper mocking to avoid external dependencies.
"""

import os
import tempfile
import shutil
import pytest
from unittest.mock import Mock, patch
from src.personal_agent.core.agent import Agent
from src.personal_agent.config.settings import Config
from src.personal_agent.memory.storage import SQLiteMemoryStorage
from tests.fixtures.mock_llm import create_mock_llm_client, create_test_config


class TestAgent:
    """Test Agent class functionality."""
    
    @pytest.fixture
    def test_config(self):
        """Create a test configuration."""
        return create_test_config()
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return create_mock_llm_client()
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_agent.db")
        storage = SQLiteMemoryStorage(db_path=db_path)
        
        yield storage
        
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_agent_initialization_with_defaults(self):
        """Test agent initialization with default parameters."""
        with patch('src.personal_agent.llm.client.LLMClient') as mock_llm:
            mock_llm.return_value = create_mock_llm_client()
            
            agent = Agent(user_id="test_user")
            
            assert agent.user_id == "test_user"
            assert agent.config is not None
            assert agent.memory_service is not None
            assert agent.llm_service is not None
            assert agent.conversation_manager is not None
    
    def test_agent_initialization_with_custom_config(self, test_config, mock_llm_client, temp_storage):
        """Test agent initialization with custom configuration."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        assert agent.user_id == "test_user"
        assert agent.config is test_config
        assert agent.memory_service is not None
        assert agent.llm_service is not None
        assert agent.conversation_manager is not None
        assert agent.response_processor is not None
    
    def test_generate_welcome_message(self, test_config, mock_llm_client, temp_storage):
        """Test welcome message generation."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        welcome_message = agent.get_welcome_message()
        
        assert isinstance(welcome_message, str)
        assert len(welcome_message) > 0
        # Should contain greeting-like content
        assert any(word in welcome_message.lower() for word in ['hello', 'welcome', 'help', 'assistant'])
    
    def test_process_input_basic(self, test_config, mock_llm_client, temp_storage):
        """Test basic input processing."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        response = agent.process_input("Hello, how are you?")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain clarification request or greeting
        assert any(phrase in response.lower() for phrase in [
            "mock response",
            "hello",
            "how can i help you",
            "what would you like me to help you with",
            "i want to make sure i understand correctly",
            "to better assist you",
            "could you clarify",
            "could you elaborate"
        ])
    
    def test_process_input_planning_request(self, test_config, mock_llm_client, temp_storage):
        """Test processing planning requests."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        response = agent.process_input("I need help planning my project")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain planning-related response
        assert "planning" in response.lower()
    
    def test_process_input_reasoning_request(self, test_config, mock_llm_client, temp_storage):
        """Test processing reasoning requests."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        response = agent.process_input("Help me reason through this decision")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain clarification request or reasoning-related content
        assert any(phrase in response.lower() for phrase in [
            "reasoning",
            "could you be more specific",
            "what specifically are you referring to",
            "to provide the best response",
            "i need a bit more information"
        ])
    
    def test_process_input_decision_request(self, test_config, mock_llm_client, temp_storage):
        """Test processing decision tree requests."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        response = agent.process_input("I need to make a decision between options")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain decision-related response
        assert "decision" in response.lower()
    
    def test_process_exit_command(self, test_config, mock_llm_client, temp_storage):
        """Test processing exit commands."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        # Test various exit commands
        exit_commands = ["exit", "quit", "goodbye", "bye"]
        
        for command in exit_commands:
            response = agent.process_input(command)
            assert isinstance(response, str)
            # Should contain farewell message
            assert any(word in response.lower() for word in ['goodbye', 'bye', 'farewell', 'have a great day'])
    
    def test_save_user_preference(self, test_config, mock_llm_client, temp_storage):
        """Test saving user preferences."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        result = agent.remember_preference("language", "English")
        assert result is True
    
    def test_save_user_fact(self, test_config, mock_llm_client, temp_storage):
        """Test saving user facts."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        result = agent.remember_fact("birthday", "January 1st")
        assert result is True
    
    def test_collect_feedback(self, test_config, mock_llm_client, temp_storage):
        """Test feedback collection."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        # Process a message first to have something to give feedback on
        agent.process_input("Test message")
        
        # Collect feedback
        result = agent.collect_rating_feedback(
            message_id="test_message",
            rating=5,
            comment="Great response!"
        )
        
        assert result is True
    
    def test_get_feedback_statistics(self, test_config, mock_llm_client, temp_storage):
        """Test getting feedback statistics."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        # Add some feedback
        agent.collect_rating_feedback("test_message_1", 5, "Great!")
        agent.collect_rating_feedback("test_message_2", 4, "Good!")
        
        stats = agent.get_feedback_statistics()
        
        assert isinstance(stats, dict)
        assert "average_rating" in stats
        assert "total_feedback" in stats
        assert stats["total_feedback"] >= 2
    
    def test_agent_with_invalid_input(self, test_config, mock_llm_client, temp_storage):
        """Test agent behavior with invalid input."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        # Test with None input
        response = agent.process_input(None)
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Test with empty string
        response = agent.process_input("")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_agent_conversation_history(self, test_config, mock_llm_client, temp_storage):
        """Test that agent maintains conversation history."""
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=mock_llm_client
        )
        
        # Process multiple inputs
        agent.process_input("Hello")
        agent.process_input("How are you?")
        agent.process_input("What's the weather like?")
        
        # The mock LLM client should have recorded these calls
        history = mock_llm_client.get_call_history()
        assert len(history) >= 3
    
    def test_agent_error_handling(self, test_config, temp_storage):
        """Test agent error handling with failing LLM client."""
        # Create a mock LLM client that raises exceptions
        failing_llm = Mock()
        failing_llm.generate_response.side_effect = Exception("LLM Error")
        
        agent = Agent(
            user_id="test_user",
            config=test_config,
            memory_storage=temp_storage,
            llm_client=failing_llm
        )
        
        # Should handle the error gracefully
        response = agent.process_input("Test message")
        assert isinstance(response, str)
        # Should contain some error message or fallback
        assert len(response) > 0


class TestAgentConfiguration:
    """Test Agent configuration handling."""
    
    def test_agent_config_loading(self):
        """Test agent configuration loading."""
        with patch('src.personal_agent.core.agent.LLMClient') as mock_llm:
            mock_llm.return_value = create_mock_llm_client()
            
            agent = Agent(user_id="test_user")
            
            assert agent.config.agent.name == "PersonalAgent"
            assert agent.config.agent.personality == "helpful"
            assert agent.config.memory.backend == "sqlite"
    
    def test_agent_custom_config(self):
        """Test agent with custom configuration."""
        config = create_test_config()
        config.agent.name = "CustomAgent"
        config.agent.personality = "friendly"
        
        with patch('src.personal_agent.core.agent.LLMClient') as mock_llm:
            mock_llm.return_value = create_mock_llm_client()
            
            agent = Agent(user_id="test_user", config=config)
            
            assert agent.config.agent.name == "CustomAgent"
            assert agent.config.agent.personality == "friendly"