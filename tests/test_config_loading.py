"""
Tests for configuration loading functionality.
"""

import os
import tempfile
import json
import yaml
import pytest
from src.personal_agent.config.settings import Config


def test_load_default_config():
    """Test loading default configuration."""
    config = Config.load()
    assert config is not None
    assert config.llm.provider == "openrouter"
    assert config.memory.backend == "sqlite"
    assert config.agent.name == "PersonalAgent"


def test_load_from_yaml_file():
    """Test loading configuration from YAML file."""
    # Create a temporary YAML config file
    yaml_config = {
        "llm": {
            "provider": "test_provider",
            "model": "test_model"
        },
        "memory": {
            "backend": "test_backend"
        },
        "agent": {
            "name": "TestAgent"
        },
        "debug": True
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_config, f)
        config_path = f.name
    
    try:
        config = Config.load(config_path)
        assert config.llm.provider == "test_provider"
        assert config.llm.model == "test_model"
        assert config.memory.backend == "test_backend"
        assert config.agent.name == "TestAgent"
        assert config.debug is True
    finally:
        os.unlink(config_path)


def test_load_from_json_file():
    """Test loading configuration from JSON file."""
    # Create a temporary JSON config file
    json_config = {
        "llm": {
            "provider": "json_provider",
            "model": "json_model"
        },
        "memory": {
            "backend": "json_backend"
        },
        "agent": {
            "name": "JsonAgent"
        },
        "debug": False
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_config, f)
        config_path = f.name
    
    try:
        config = Config.load(config_path)
        assert config.llm.provider == "json_provider"
        assert config.llm.model == "json_model"
        assert config.memory.backend == "json_backend"
        assert config.agent.name == "JsonAgent"
        assert config.debug is False
    finally:
        os.unlink(config_path)


def test_env_override():
    """Test that environment variables override config file values."""
    # Create a temporary config file
    yaml_config = {
        "llm": {
            "provider": "file_provider",
            "model": "file_model"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_config, f)
        config_path = f.name
    
    # Set environment variable to override
    original_env = os.environ.get("PA_LLM__PROVIDER")
    os.environ["PA_LLM__PROVIDER"] = "env_provider"
    
    try:
        config = Config.load(config_path)
        # Environment variable should override file value
        assert config.llm.provider == "env_provider"
        assert config.llm.model == "file_model"  # Should remain from file
    finally:
        os.unlink(config_path)
        # Restore original environment
        if original_env is not None:
            os.environ["PA_LLM__PROVIDER"] = original_env
        elif "PA_LLM__PROVIDER" in os.environ:
            del os.environ["PA_LLM__PROVIDER"]


if __name__ == "__main__":
    pytest.main([__file__])