"""
Plugin Manager for Memory Storage

This module contains the plugin manager that handles dynamic loading of memory storage providers.
"""

import os
from typing import Dict, Type, Optional, List
from .storage import MemoryStorage
from ..utils.plugin_manager_base import BasePluginManager


class MemoryStoragePluginManager(BasePluginManager[MemoryStorage]):
    """
    Manager for dynamically loading memory storage plugins.
    """
    
    def __init__(self):
        """
        Initialize the plugin manager.
        """
        super().__init__("MemoryStorage")
    
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
        return filename.endswith(".py") and filename != "base.py" and filename != "__init__.py" and filename != "plugin_manager.py"
    
    def _get_provider_class_name(self, provider_name: str) -> str:
        """
        Get the expected class name for a provider.
        
        Args:
            provider_name (str): Name of the provider
            
        Returns:
            str: Expected class name for the provider
        """
        return f"{provider_name.capitalize()}Storage"
    
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
            return issubclass(obj, MemoryStorage)
        except TypeError:
            return False
    
    def _load_builtin_provider(self, provider_name: str) -> Optional[Type[MemoryStorage]]:
        """
        Load a built-in provider.
        
        Args:
            provider_name (str): Name of the provider to load
            
        Returns:
            Optional[Type[MemoryStorage]]: Provider class if loaded successfully, None otherwise
        """
        if provider_name == "sqlite":
            from ..memory.storage import SQLiteMemoryStorage
            return SQLiteMemoryStorage
        return None


# Global instance for easy access
_memory_storage_plugin_manager = None


def get_memory_storage_plugin_manager() -> MemoryStoragePluginManager:
    """
    Get the global memory storage plugin manager instance.
    
    Returns:
        MemoryStoragePluginManager: Global memory storage plugin manager instance
    """
    global _memory_storage_plugin_manager
    if _memory_storage_plugin_manager is None:
        _memory_storage_plugin_manager = MemoryStoragePluginManager()
    return _memory_storage_plugin_manager


def load_memory_storage_plugin(provider_name: str) -> Optional[Type[MemoryStorage]]:
    """
    Load a provider plugin by name using the global plugin manager.
    
    Args:
        provider_name (str): Name of the provider to load
        
    Returns:
        Optional[Type[MemoryStorage]]: Provider class if loaded successfully, None otherwise
    """
    manager = get_memory_storage_plugin_manager()
    return manager.load_provider(provider_name)


def get_loaded_memory_storage_provider(provider_name: str) -> Optional[Type[MemoryStorage]]:
    """
    Get a loaded provider class by name using the global plugin manager.
    
    Args:
        provider_name (str): Name of the provider
        
    Returns:
        Optional[Type[MemoryStorage]]: Provider class if loaded, None otherwise
    """
    manager = get_memory_storage_plugin_manager()
    return manager.get_provider(provider_name)