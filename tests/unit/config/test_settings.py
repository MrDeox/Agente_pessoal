"""
Unit tests for configuration settings.

Migrated from scripts/test_config.py with improvements.
"""

import os
import tempfile
import pytest
from src.personal_agent.config.settings import Config, LLMConfig, MemoryConfig, AgentConfig


class TestConfig:
    """Test configuration loading and management."""
    
    def test_default_config_creation(self):
        """Test creating a default configuration."""
        config = Config()
        
        assert config.llm.provider == "openrouter"
        assert config.llm.model == "qwen/qwen3-coder:free"
        assert config.llm.temperature == 0.7
        assert config.llm.max_tokens == 1000
        
        assert config.memory.backend == "sqlite"
        assert config.memory.database_path == "data/memory.db"
        
        assert config.agent.name == "PersonalAgent"
        assert config.agent.personality == "helpful"
        
        assert config.debug is False
    
    def test_config_from_environment(self):
        """Test loading configuration from environment variables."""
        # Set environment variables
        original_env = os.environ.copy()
        try:
            os.environ["PA_LLM__PROVIDER"] = "openai"
            os.environ["PA_LLM__MODEL"] = "gpt-4"
            os.environ["PA_LLM__API_KEY"] = "test-key"
            os.environ["PA_LLM__TEMPERATURE"] = "0.5"
            os.environ["PA_MEMORY__DATABASE_PATH"] = "test.db"
            os.environ["PA_DEBUG"] = "true"
            
            config = Config.load()
            
            assert config.llm.provider == "openai"
            assert config.llm.model == "gpt-4"
            assert config.llm.api_key == "test-key"
            assert config.llm.temperature == 0.5
            assert config.memory.database_path == "test.db"
            assert config.debug is True
            
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_llm_config(self):
        """Test LLM configuration."""
        llm_config = LLMConfig()
        
        assert llm_config.provider == "openrouter"
        assert llm_config.model == "qwen/qwen3-coder:free"
        assert llm_config.api_key is None
        assert llm_config.temperature == 0.7
        assert llm_config.max_tokens == 1000
        assert llm_config.rate_limit_requests == 60
        assert llm_config.rate_limit_period == 60
    
    def test_memory_config(self):
        """Test memory configuration."""
        memory_config = MemoryConfig()
        
        assert memory_config.backend == "sqlite"
        assert memory_config.database_path == "data/memory.db"
        assert memory_config.max_memory_items == 1000
    
    def test_agent_config(self):
        """Test agent configuration."""
        agent_config = AgentConfig()
        
        assert agent_config.name == "PersonalAgent"
        assert agent_config.personality == "helpful"
        assert agent_config.max_history_length == 10
    
    def test_config_yaml_loading(self):
        """Test loading configuration from YAML file."""
        # Save original environment variable
        original_provider = os.environ.get("PA_LLM__PROVIDER")
        
        # Temporarily unset the environment variable
        if "PA_LLM__PROVIDER" in os.environ:
            del os.environ["PA_LLM__PROVIDER"]
        
        try:
            # Create temporary YAML config file
            yaml_content = """
llm:
  provider: openai
  model: gpt-3.5-turbo
  temperature: 0.8
  max_tokens: 2000

memory:
  backend: sqlite
  database_path: custom.db

agent:
  name: TestAgent
  personality: friendly

debug: true
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(yaml_content)
                config_path = f.name
            
            try:
                config = Config.load(config_path)
                
                assert config.llm.provider == "openai"
                assert config.llm.model == "gpt-3.5-turbo"
                assert config.llm.temperature == 0.8
                assert config.llm.max_tokens == 2000
                assert config.memory.database_path == "custom.db"
                assert config.agent.name == "TestAgent"
                assert config.agent.personality == "friendly"
                assert config.debug is True
                
            finally:
                os.unlink(config_path)
        finally:
            # Restore original environment variable
            if original_provider is not None:
                os.environ["PA_LLM__PROVIDER"] = original_provider
            elif "PA_LLM__PROVIDER" in os.environ:
                del os.environ["PA_LLM__PROVIDER"]
    
    def test_config_json_loading(self):
        """Test loading configuration from JSON file."""
        # Save original environment variables
        original_provider = os.environ.get("PA_LLM__PROVIDER")
        original_debug = os.environ.get("PA_DEBUG")
        
        # Temporarily unset the environment variables
        if "PA_LLM__PROVIDER" in os.environ:
            del os.environ["PA_LLM__PROVIDER"]
        if "PA_DEBUG" in os.environ:
            del os.environ["PA_DEBUG"]
        
        try:
            # Create temporary JSON config file
            json_content = """{
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.9
        },
        "memory": {
            "database_path": "json_test.db"
        },
        "debug": false
    }"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(json_content)
                config_path = f.name
            
            try:
                config = Config.load(config_path)
                
                assert config.llm.provider == "openai"
                assert config.llm.model == "gpt-4"
                assert config.llm.temperature == 0.9
                assert config.memory.database_path == "json_test.db"
                assert config.debug is False
                
            finally:
                os.unlink(config_path)
        finally:
            # Restore original environment variables
            if original_provider is not None:
                os.environ["PA_LLM__PROVIDER"] = original_provider
            elif "PA_LLM__PROVIDER" in os.environ:
                del os.environ["PA_LLM__PROVIDER"]
            
            if original_debug is not None:
                os.environ["PA_DEBUG"] = original_debug
            elif "PA_DEBUG" in os.environ:
                del os.environ["PA_DEBUG"]