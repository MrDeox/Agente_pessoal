"""
Factory module for creating instances of core components with dependency injection.
"""

from typing import Optional, Dict, Any
from ..config.settings import Config
from ..memory.storage import MemoryStorage
from ..memory.plugin_manager import load_memory_storage_plugin, get_loaded_memory_storage_provider
from ..llm.client import LLMClient
from ..llm.client_plugin_manager import load_llm_client_plugin, get_loaded_llm_client_provider
from .agent import Agent
from .feedback import FeedbackSystem


class ComponentFactory:
    """
    Factory class for creating instances of core components with dependency injection.
    """
    
    @staticmethod
    def create_memory_storage(config: Config) -> MemoryStorage:
        """
        Create a memory storage instance based on configuration.
        
        Args:
            config (Config): Configuration object
            
        Returns:
            MemoryStorage: Memory storage instance
            
        Raises:
            ValueError: If the storage backend is not supported
        """
        backend = config.memory.backend
        # Try to load the provider using the plugin system
        provider_class = load_memory_storage_plugin(backend)
        
        if provider_class:
            # For SQLite provider, we need to pass the database path
            if backend == "sqlite":  # This is our SQLite provider
                return provider_class(config.memory.database_path)
            else:
                return provider_class()
        else:
            raise ValueError(f"Unsupported memory backend: {backend}")
    
    @staticmethod
    def create_llm_client(config: Config) -> LLMClient:
        """
        Create an LLM client instance.
        
        Args:
            config (Config): Configuration object
            
        Returns:
            LLMClient: LLM client instance
        """
        # Try to load the provider using the plugin system
        provider_class = load_llm_client_plugin("client")
        
        if provider_class:
            return provider_class(config)
        else:
            # Fallback to direct import
            from ..llm.client import LLMClient
            return LLMClient(config)
    
    @staticmethod
    def create_feedback_system(user_id: str = "default_user", config: Optional[Config] = None) -> FeedbackSystem:
        """
        Create a feedback system instance.
        
        Args:
            user_id (str): ID of the user interacting with the agent
            config (Optional[Config]): Configuration object. If None, will load default config.
            
        Returns:
            FeedbackSystem: Feedback system instance
        """
        if config is None:
            config = Config.load()
        
        return FeedbackSystem(user_id=user_id)
    
    @staticmethod
    def create_agent(user_id: str = "default_user", config: Optional[Config] = None) -> Agent:
        """
        Create an agent instance with injected dependencies.
        
        Args:
            user_id (str): ID of the user interacting with the agent
            config (Optional[Config]): Configuration object. If None, will load default config.
            
        Returns:
            Agent: Agent instance with injected dependencies
        """
        if config is None:
            config = Config.load()
        
        # Create dependencies
        memory_storage = ComponentFactory.create_memory_storage(config)
        llm_client = ComponentFactory.create_llm_client(config)
        feedback_system = ComponentFactory.create_feedback_system(user_id, config)
        
        # Create agent with injected dependencies
        agent = Agent(
            user_id=user_id,
            config=config,
            memory_storage=memory_storage,
            llm_client=llm_client,
            feedback_system=feedback_system
        )
        
        return agent