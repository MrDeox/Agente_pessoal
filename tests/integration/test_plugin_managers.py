#!/usr/bin/env python3
"""
Test script for plugin managers to verify refactored implementation works correctly.
"""

import sys
import os

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

def test_llm_plugin_manager():
    """Test the LLM plugin manager."""
    print("Testing LLM Plugin Manager...")
    
    try:
        from personal_agent.llm.plugin_manager import load_provider_plugin, get_loaded_provider, get_plugin_manager
        
        # Test getting the plugin manager instance
        manager = get_plugin_manager()
        print(f"Plugin manager instance: {manager}")
        
        # Test discovering providers
        providers = manager.discover_providers()
        print(f"Discovered providers: {providers}")
        
        # Test loading a built-in provider
        openai_provider = load_provider_plugin("openai")
        print(f"Loaded OpenAI provider: {openai_provider}")
        
        # Test getting a loaded provider
        loaded_openai = get_loaded_provider("openai")
        print(f"Retrieved loaded OpenAI provider: {loaded_openai}")
        
        # Test listing providers
        provider_list = manager.list_providers()
        print(f"Loaded providers: {provider_list}")
        
        print("LLM Plugin Manager test passed!\n")
        return True
    except Exception as e:
        print(f"LLM Plugin Manager test failed: {e}")
        return False

def test_memory_plugin_manager():
    """Test the memory storage plugin manager."""
    print("Testing Memory Storage Plugin Manager...")
    
    try:
        from personal_agent.memory.plugin_manager import load_memory_storage_plugin, get_loaded_memory_storage_provider, get_memory_storage_plugin_manager
        
        # Test getting the plugin manager instance
        manager = get_memory_storage_plugin_manager()
        print(f"Plugin manager instance: {manager}")
        
        # Test discovering providers
        providers = manager.discover_providers()
        print(f"Discovered providers: {providers}")
        
        # Test loading a built-in provider
        storage_provider = load_memory_storage_plugin("storage")
        print(f"Loaded storage provider: {storage_provider}")
        
        # Test getting a loaded provider
        loaded_storage = get_loaded_memory_storage_provider("storage")
        print(f"Retrieved loaded storage provider: {loaded_storage}")
        
        # Test listing providers
        provider_list = manager.list_providers()
        print(f"Loaded providers: {provider_list}")
        
        print("Memory Storage Plugin Manager test passed!\n")
        return True
    except Exception as e:
        print(f"Memory Storage Plugin Manager test failed: {e}")
        return False

def test_llm_client_plugin_manager():
    """Test the LLM client plugin manager."""
    print("Testing LLM Client Plugin Manager...")
    
    try:
        from personal_agent.llm.client_plugin_manager import load_llm_client_plugin, get_loaded_llm_client_provider, get_llm_client_plugin_manager
        
        # Test getting the plugin manager instance
        manager = get_llm_client_plugin_manager()
        print(f"Plugin manager instance: {manager}")
        
        # Test discovering providers
        providers = manager.discover_providers()
        print(f"Discovered providers: {providers}")
        
        # Test loading a built-in provider
        client_provider = load_llm_client_plugin("client")
        print(f"Loaded client provider: {client_provider}")
        
        # Test getting a loaded provider
        loaded_client = get_loaded_llm_client_provider("client")
        print(f"Retrieved loaded client provider: {loaded_client}")
        
        # Test listing providers
        provider_list = manager.list_providers()
        print(f"Loaded providers: {provider_list}")
        
        print("LLM Client Plugin Manager test passed!\n")
        return True
    except Exception as e:
        print(f"LLM Client Plugin Manager test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running Plugin Manager Tests...\n")
    
    results = []
    results.append(test_llm_plugin_manager())
    results.append(test_memory_plugin_manager())
    results.append(test_llm_client_plugin_manager())
    
    if all(results):
        print("All plugin manager tests passed!")
        return 0
    else:
        print("Some plugin manager tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())