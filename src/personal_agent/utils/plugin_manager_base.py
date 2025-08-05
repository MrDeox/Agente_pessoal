"""
Generic Base Plugin Manager
This module contains the generic base class for plugin managers.
"""

import os
import importlib
import importlib.util
from typing import Dict, Type, Optional, List, TypeVar, Generic
from abc import ABC
from .logging import get_logger, log_exception

# Type variable for generic plugin manager
T = TypeVar('T')

class BasePluginManager(Generic[T], ABC):
    """
    Generic base class for plugin managers.
    """
    
    def __init__(self, plugin_type_name: str):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_type_name (str): Name of the plugin type for logging purposes
        """
        self.plugin_type_name = plugin_type_name
        self.logger = get_logger()
        self.providers: Dict[str, Type[T]] = {}
        self.logger.info(f"{plugin_type_name}PluginManager initialized")
    
    def discover_providers(self, providers_dir: str = None) -> List[str]:
        """
        Discover available provider plugins in the providers directory.
        
        Args:
            providers_dir (str): Path to the providers directory. 
                                If None, uses the default providers directory.
                                
        Returns:
            List[str]: List of discovered provider names
        """
        if providers_dir is None:
            providers_dir = self._get_default_providers_dir()
        
        self.logger.info(f"Discovering {self.plugin_type_name} providers in: {providers_dir}")
        
        discovered = []
        if os.path.exists(providers_dir):
            for filename in os.listdir(providers_dir):
                if self._is_valid_provider_file(filename):
                    provider_name = filename[:-3]  # Remove .py extension
                    discovered.append(provider_name)
                    self.logger.info(f"Discovered {self.plugin_type_name} provider: {provider_name}")
        
        return discovered
    
    def _get_default_providers_dir(self) -> str:
        """
        Get the default providers directory.
        This method should be overridden by subclasses.
        
        Returns:
            str: Path to the default providers directory
        """
        raise NotImplementedError
    
    def _is_valid_provider_file(self, filename: str) -> bool:
        """
        Check if a file is a valid provider file.
        This method should be overridden by subclasses.
        
        Args:
            filename (str): Name of the file to check
            
        Returns:
            bool: True if the file is a valid provider file, False otherwise
        """
        raise NotImplementedError
    
    def _get_provider_class_name(self, provider_name: str) -> str:
        """
        Get the expected class name for a provider.
        This method should be overridden by subclasses.
        
        Args:
            provider_name (str): Name of the provider
            
        Returns:
            str: Expected class name for the provider
        """
        raise NotImplementedError
    
    def _is_provider_subclass(self, obj, provider_class) -> bool:
        """
        Check if an object is a subclass of the provider class.
        This method should be overridden by subclasses.
        
        Args:
            obj: Object to check
            provider_class: Provider class to check against
            
        Returns:
            bool: True if obj is a subclass of provider_class, False otherwise
        """
        raise NotImplementedError
    
    def load_provider(self, provider_name: str, providers_dir: str = None) -> Optional[Type[T]]:
        """
        Load a provider plugin by name.
        
        Args:
            provider_name (str): Name of the provider to load
            providers_dir (str): Path to the providers directory
            
        Returns:
            Optional[Type[T]]: Provider class if loaded successfully, None otherwise
        """
        if provider_name in self.providers:
            self.logger.info(f"{self.plugin_type_name} provider {provider_name} already loaded")
            return self.providers[provider_name]
        
        if providers_dir is None:
            providers_dir = self._get_default_providers_dir()
        
        provider_file = os.path.join(providers_dir, f"{provider_name}.py")
        
        if not os.path.exists(provider_file):
            self.logger.error(f"{self.plugin_type_name} provider file not found: {provider_file}")
            return None
        
        try:
            self.logger.info(f"Loading {self.plugin_type_name} provider: {provider_name}")
            
            # Try to load built-in providers first
            builtin_provider = self._load_builtin_provider(provider_name)
            if builtin_provider:
                self.providers[provider_name] = builtin_provider
                self.logger.info(f"Built-in {self.plugin_type_name} provider {provider_name} loaded successfully")
                return builtin_provider
            
            # For external providers, use dynamic loading
            # Load the module
            spec = importlib.util.spec_from_file_location(provider_name, provider_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the provider class
            provider_class_name = self._get_provider_class_name(provider_name)
            if hasattr(module, provider_class_name):
                provider_class = getattr(module, provider_class_name)
                if self._is_provider_subclass(provider_class, T):
                    self.providers[provider_name] = provider_class
                    self.logger.info(f"{self.plugin_type_name} provider {provider_name} loaded successfully")
                    return provider_class
                else:
                    self.logger.error(f"Class {provider_class_name} is not a valid subclass")
            else:
                # Try to find any class that inherits from the provider type
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and self._is_provider_subclass(obj, T) and obj != T:
                        self.providers[provider_name] = obj
                        self.logger.info(f"{self.plugin_type_name} provider {provider_name} loaded successfully with class {name}")
                        return obj
                
                self.logger.error(f"No {self.plugin_type_name} provider class found in {provider_name}")
                
        except Exception as e:
            log_exception(e, f"Loading {self.plugin_type_name} provider {provider_name}")
            self.logger.error(f"Failed to load {self.plugin_type_name} provider {provider_name}: {str(e)}")
        
        return None
    
    def _load_builtin_provider(self, provider_name: str) -> Optional[Type[T]]:
        """
        Load a built-in provider.
        This method should be overridden by subclasses.
        
        Args:
            provider_name (str): Name of the provider to load
            
        Returns:
            Optional[Type[T]]: Provider class if loaded successfully, None otherwise
        """
        return None
    
    def get_provider(self, provider_name: str) -> Optional[Type[T]]:
        """
        Get a loaded provider class by name.
        
        Args:
            provider_name (str): Name of the provider
            
        Returns:
            Optional[Type[T]]: Provider class if loaded, None otherwise
        """
        return self.providers.get(provider_name)
    
    def list_providers(self) -> List[str]:
        """
        List all loaded providers.
        
        Returns:
            List[str]: List of loaded provider names
        """
        return list(self.providers.keys())
    
    def load_all_providers(self, providers_dir: str = None) -> Dict[str, Type[T]]:
        """
        Load all available providers.
        
        Args:
            providers_dir (str): Path to the providers directory
            
        Returns:
            Dict[str, Type[T]]: Dictionary of loaded providers
        """
        discovered = self.discover_providers(providers_dir)
        loaded = {}
        
        for provider_name in discovered:
            provider_class = self.load_provider(provider_name, providers_dir)
            if provider_class:
                loaded[provider_name] = provider_class
        
        return loaded