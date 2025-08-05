#!/usr/bin/env python3
"""
Test script for plugin system functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.personal_agent.llm.plugin_manager import LLMPluginManager, get_plugin_manager, load_provider_plugin, get_loaded_provider
from src.personal_agent.llm.providers.base import LLMProvider


def test_plugin_system():
    """Test plugin system functionality."""
    print("Testing plugin system...")
    
    # Test 1: Create plugin manager
    print("\n1. Testing plugin manager creation...")
    manager = LLMPluginManager()
    print(f"Plugin manager created: {type(manager).__name__}")
    
    # Test 2: Discover providers
    print("\n2. Testing provider discovery...")
    discovered = manager.discover_providers()
    print(f"Discovered providers: {discovered}")
    
    # Test 3: Load a provider
    print("\n3. Testing provider loading...")
    if "openai" in discovered:
        openai_provider = manager.load_provider("openai")
        print(f"OpenAI provider loaded: {openai_provider is not None}")
        if openai_provider:
            print(f"OpenAI provider class: {openai_provider.__name__}")
    
    # Test 4: Load another provider
    print("\n4. Testing loading another provider...")
    if "openrouter" in discovered:
        openrouter_provider = manager.load_provider("openrouter")
        print(f"OpenRouter provider loaded: {openrouter_provider is not None}")
        if openrouter_provider:
            print(f"OpenRouter provider class: {openrouter_provider.__name__}")
    
    # Test 5: List loaded providers
    print("\n5. Testing loaded providers listing...")
    loaded = manager.list_providers()
    print(f"Loaded providers: {loaded}")
    
    # Test 6: Get a specific provider
    print("\n6. Testing getting specific provider...")
    if "openai" in loaded:
        openai_class = manager.get_provider("openai")
        print(f"OpenAI provider class retrieved: {openai_class is not None}")
    
    # Test 7: Load all providers
    print("\n7. Testing loading all providers...")
    all_providers = manager.load_all_providers()
    print(f"All providers loaded: {len(all_providers)}")
    for name, cls in all_providers.items():
        print(f"  - {name}: {cls.__name__}")
    
    # Test 8: Global plugin manager
    print("\n8. Testing global plugin manager...")
    global_manager = get_plugin_manager()
    print(f"Global plugin manager: {type(global_manager).__name__}")
    
    # Test 9: Load provider via global function
    print("\n9. Testing global provider loading...")
    if "openai" in discovered:
        global_openai = load_provider_plugin("openai")
        print(f"OpenAI provider loaded via global function: {global_openai is not None}")
    
    # Test 10: Get loaded provider via global function
    print("\n10. Testing global provider retrieval...")
    if "openai" in loaded:
        global_openai_class = get_loaded_provider("openai")
        print(f"OpenAI provider class retrieved via global function: {global_openai_class is not None}")
    
    print("\nPlugin system test completed successfully!")


if __name__ == "__main__":
    test_plugin_system()