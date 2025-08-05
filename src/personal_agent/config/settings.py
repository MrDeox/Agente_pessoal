"""
Configuration Settings for Personal Agent

This module contains the configuration classes and loading logic for the personal agent.
"""

from dataclasses import dataclass, field
from typing import Optional, List
import os
import json
import yaml


@dataclass
class LLMConfig:
    """Configuration for LLM settings."""
    provider: str = "openrouter"
    model: str = "qwen/qwen3-coder:free"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str = "You are a helpful assistant."
    rate_limit_requests: int = 60  # requests per minute
    rate_limit_period: int = 60  # seconds


@dataclass
class MemoryConfig:
    """Configuration for memory settings."""
    backend: str = "sqlite"
    database_path: str = "data/memory.db"
    max_memory_items: int = 1000


@dataclass
class AgentConfig:
    """Configuration for agent settings."""
    name: str = "PersonalAgent"
    personality: str = "helpful"
    max_history_length: int = 10


@dataclass
class FeedbackConfig:
    """Configuration for feedback settings."""
    enabled: bool = True
    rating_scale: int = 5  # 1-5 rating scale
    adapt_threshold: int = 3  # Threshold for adaptation (ratings below this will trigger adaptation)
    collect_feedback: bool = True


@dataclass
class Config:
    """Main configuration class."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    debug: bool = False
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """
        Load configuration from all sources.
        
        Args:
            config_path: Optional path to a specific configuration file
            
        Returns:
            Config: Loaded configuration object
        """
        config = cls()
        
        # Load from configuration files
        config._load_from_file(config_path)
        
        # Load from environment variables
        config._load_from_env()
        
        return config
    
    def _load_from_file(self, config_path: Optional[str] = None):
        """
        Load configuration from YAML/JSON files.
        
        Args:
            config_path: Optional path to a specific configuration file
        """
        # Determine which config file to load
        if config_path is None:
            # Check for environment variable specifying config file
            config_path = os.getenv("PA_CONFIG_PATH")
            
        if config_path is None:
            # Determine environment
            env = os.getenv("PA_ENV", "default")
            # Try YAML first, then JSON
            for ext in ["yaml", "yml", "json"]:
                path = f"config/{env}.{ext}"
                if os.path.exists(path):
                    config_path = path
                    break
            
            # If no environment-specific file found, try default
            if config_path is None:
                for ext in ["yaml", "yml", "json"]:
                    path = f"config/default.{ext}"
                    if os.path.exists(path):
                        config_path = path
                        break
        
        # Load configuration from file if found
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                if config_path.endswith(('.yaml', '.yml')):
                    data = yaml.safe_load(f)
                elif config_path.endswith('.json'):
                    data = json.load(f)
                else:
                    # Try to detect format
                    content = f.read()
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError:
                        data = yaml.safe_load(content)
            
            # Apply configuration data
            if data:
                self._apply_config_data(data)
    
    def _apply_config_data(self, data: dict):
        """
        Apply configuration data to the config object.
        
        Args:
            data: Configuration data dictionary
        """
        if "llm" in data:
            llm_data = data["llm"]
            for key, value in llm_data.items():
                if hasattr(self.llm, key):
                    setattr(self.llm, key, value)
        
        if "memory" in data:
            memory_data = data["memory"]
            for key, value in memory_data.items():
                if hasattr(self.memory, key):
                    setattr(self.memory, key, value)
        
        if "agent" in data:
            agent_data = data["agent"]
            for key, value in agent_data.items():
                if hasattr(self.agent, key):
                    setattr(self.agent, key, value)
        
        if "feedback" in data:
            feedback_data = data["feedback"]
            for key, value in feedback_data.items():
                if hasattr(self.feedback, key):
                    setattr(self.feedback, key, value)
        
        if "debug" in data:
            self.debug = data["debug"]
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # LLM settings
        if os.getenv("PA_LLM__PROVIDER"):
            self.llm.provider = os.getenv("PA_LLM__PROVIDER")
        if os.getenv("PA_LLM__MODEL"):
            self.llm.model = os.getenv("PA_LLM__MODEL")
        if os.getenv("PA_LLM__API_KEY"):
            self.llm.api_key = os.getenv("PA_LLM__API_KEY")
        if os.getenv("PA_LLM__TEMPERATURE"):
            self.llm.temperature = float(os.getenv("PA_LLM__TEMPERATURE"))
        if os.getenv("PA_LLM__MAX_TOKENS"):
            self.llm.max_tokens = int(os.getenv("PA_LLM__MAX_TOKENS"))
        if os.getenv("PA_LLM__SYSTEM_PROMPT"):
            self.llm.system_prompt = os.getenv("PA_LLM__SYSTEM_PROMPT")
        
        # Memory settings
        if os.getenv("PA_MEMORY__DATABASE_PATH"):
            self.memory.database_path = os.getenv("PA_MEMORY__DATABASE_PATH")
        
        # Debug setting
        if os.getenv("PA_DEBUG"):
            self.debug = os.getenv("PA_DEBUG").lower() in ["true", "1", "yes"]