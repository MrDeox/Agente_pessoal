#!/usr/bin/env python3
"""
Simple test script for configuration loading.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.personal_agent.config.settings import Config

def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    
    # Test default loading
    config = Config.load()
    print(f"LLM Provider: {config.llm.provider}")
    print(f"Memory Backend: {config.memory.backend}")
    print(f"Agent Name: {config.agent.name}")
    print(f"Debug Mode: {config.debug}")
    
    print("\nConfiguration loading test completed successfully!")

if __name__ == "__main__":
    test_config_loading()