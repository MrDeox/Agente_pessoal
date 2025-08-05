"""
Plugin Manager for LLM Providers

This module contains the plugin manager that handles dynamic loading of LLM providers.
"""

import os
from typing import Dict, Type, Optional, List
from .providers.base import LLMProvider
from ..utils.plugin_manager_base import BasePluginManager


class LLMPluginManager(BasePluginManager[LLMProvider]):
    """
    Manager for dynamically loading LLM provider plugins.
    """
    
    def __init__(self):
        """
        Initialize the plugin manager.
        """
        super().__init__("LLM")
    
    def _get_default_providers_dir(self) -> str:
        """
        Get the default providers directory.
        
        Returns:
            str: Path to the default providers directory
        """
        # Get the directory where this module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "providers")
    
    def _is_valid_provider_file(self, filename: str) -> bool:
        """
        Check if a file is a valid provider file.
        
        Args:
            filename (str): Name of the file to check
            
        Returns:
            bool: True if the file is a valid provider file, False otherwise
        """
        return filename.endswith(".py") and filename != "base.py" and filename != "__init__.py"
    
    def _get_provider_class_name(self, provider_name: str) -> str:
        """
        Get the expected class name for a provider.
        
        Args:
            provider_name (str): Name of the provider
            
        Returns:
            str: Expected class name for the provider
        """
        return f"{provider_name.capitalize()}Provider"
    
    def _is_provider_subclass(self, obj, provider_class) -> bool:
        """
        Check if an object is a subclass of the provider class.
        
        Args:
            obj: Object to check
            provider_class: Provider class to check against
            
        Returns:
            bool: True if obj is a subclass of provider_class, False otherwise
        """
        try:
            return issubclass(obj, LLMProvider)
        except TypeError:
            return False
    
    def _load_builtin_provider(self, provider_name: str) -> Optional[Type[LLMProvider]]:
        """
        Load a built-in provider.
        
        Args:
            provider_name (str): Name of the provider to load
            
        Returns:
            Optional[Type[LLMProvider]]: Provider class if loaded successfully, None otherwise
        """
        if provider_name in ["openai", "openrouter"]:
            if provider_name == "openai":
                from ..llm.providers.openai import OpenAIProvider
                return OpenAIProvider
            elif provider_name == "openrouter":
                from ..llm.providers.openrouter import OpenRouterProvider
                return OpenRouterProvider
        return None


# Global instance for easy access
_plugin_manager = None


def get_plugin_manager() -> LLMPluginManager:
    """
    Get the global plugin manager instance.
    
    Returns:
        LLMPluginManager: Global plugin manager instance
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = LLMPluginManager()
    return _plugin_manager


def load_provider_plugin(provider_name: str) -> Optional[Type[LLMProvider]]:
    """
    Load a provider plugin by name using the global plugin manager.
    
    Args:
        provider_name (str): Name of the provider to load
        
    Returns:
        Optional[Type[LLMProvider]]: Provider class if loaded successfully, None otherwise
    """
    manager = get_plugin_manager()
    return manager.load_provider(provider_name)


def get_loaded_provider(provider_name: str) -> Optional[Type[LLMProvider]]:
    """
    Get a loaded provider class by name using the global plugin manager.
    
    Args:
        provider_name (str): Name of the provider
        
    Returns:
        Optional[Type[LLMProvider]]: Provider class if loaded, None otherwise
    """
    manager = get_plugin_manager()
    return manager.get_provider(provider_name)