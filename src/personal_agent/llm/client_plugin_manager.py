"""
Plugin Manager for LLM Clients

This module contains the plugin manager that handles dynamic loading of LLM client implementations.
"""

import os
from typing import Dict, Type, Optional, List
from .client import LLMClient
from ..utils.plugin_manager_base import BasePluginManager


class LLMClientPluginManager(BasePluginManager[LLMClient]):
    """
    Manager for dynamically loading LLM client plugins.
    """
    
    def __init__(self):
        """
        Initialize the plugin manager.
        """
        super().__init__("LLMClient")
    
    def _get_default_providers_dir(self) -> str:
        """
        Get the default providers directory.
        
        Returns:
            str: Path to the default providers directory
        """
        # Get the directory where this module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return current_dir
    
    def _is_valid_provider_file(self, filename: str) -> bool:
        """
        Check if a file is a valid provider file.
        
        Args:
            filename (str): Name of the file to check
            
        Returns:
            bool: True if the file is a valid provider file, False otherwise
        """
        return filename.endswith(".py") and filename != "base.py" and filename != "__init__.py" and filename != "plugin_manager.py" and filename != "client_plugin_manager.py"
    
    def _get_provider_class_name(self, provider_name: str) -> str:
        """
        Get the expected class name for a provider.
        
        Args:
            provider_name (str): Name of the provider
            
        Returns:
            str: Expected class name for the provider
        """
        return f"{provider_name.capitalize()}Client"
    
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
            return issubclass(obj, LLMClient)
        except TypeError:
            return False
    
    def _load_builtin_provider(self, provider_name: str) -> Optional[Type[LLMClient]]:
        """
        Load a built-in provider.
        
        Args:
            provider_name (str): Name of the provider to load
            
        Returns:
            Optional[Type[LLMClient]]: Provider class if loaded successfully, None otherwise
        """
        if provider_name == "client":
            from ..llm.client import LLMClient
            return LLMClient
        return None


# Global instance for easy access
_llm_client_plugin_manager = None


def get_llm_client_plugin_manager() -> LLMClientPluginManager:
    """
    Get the global LLM client plugin manager instance.
    
    Returns:
        LLMClientPluginManager: Global LLM client plugin manager instance
    """
    global _llm_client_plugin_manager
    if _llm_client_plugin_manager is None:
        _llm_client_plugin_manager = LLMClientPluginManager()
    return _llm_client_plugin_manager


def load_llm_client_plugin(provider_name: str) -> Optional[Type[LLMClient]]:
    """
    Load a provider plugin by name using the global plugin manager.
    
    Args:
        provider_name (str): Name of the provider to load
        
    Returns:
        Optional[Type[LLMClient]]: Provider class if loaded successfully, None otherwise
    """
    manager = get_llm_client_plugin_manager()
    return manager.load_provider(provider_name)


def get_loaded_llm_client_provider(provider_name: str) -> Optional[Type[LLMClient]]:
    """
    Get a loaded provider class by name using the global plugin manager.
    
    Args:
        provider_name (str): Name of the provider
        
    Returns:
        Optional[Type[LLMClient]]: Provider class if loaded, None otherwise
    """
    manager = get_llm_client_plugin_manager()
    return manager.get_provider(provider_name)