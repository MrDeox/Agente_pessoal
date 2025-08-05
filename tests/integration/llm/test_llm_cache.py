#!/usr/bin/env python3
"""
Test script for LLM cache functionality.
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.personal_agent.llm.cache import LLmCache, get_llm_cache, clear_llm_cache
from src.personal_agent.llm.models import Message, LLMResponse


def test_llm_cache():
    """Test LLM cache functionality."""
    print("Testing LLM cache...")
    
    # Test 1: Create cache
    print("\n1. Testing cache creation...")
    cache = LLmCache(default_ttl=5)  # 5 seconds TTL for testing
    print(f"Cache created with default TTL: {cache.default_ttl}s")
    
    # Test 2: Create test data
    print("\n2. Creating test data...")
    messages = [
        Message(role="user", content="Hello, how are you?"),
        Message(role="assistant", content="I'm doing well, thank you for asking!")
    ]
    
    response = LLMResponse(
        content="I'm doing well, thank you for asking!",
        finish_reason="stop",
        usage={"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
        model="test-model"
    )
    
    print("Test data created")
    
    # Test 3: Set and get from cache
    print("\n3. Testing cache set and get...")
    cache.set(messages, response, ttl=10)  # 10 seconds TTL
    cached_response = cache.get(messages)
    
    if cached_response:
        print("Cache hit successful")
        print(f"Cached response content: {cached_response.content}")
        print(f"Cached response model: {cached_response.model}")
    else:
        print("Cache miss - unexpected")
    
    # Test 4: Test cache key generation
    print("\n4. Testing cache key generation...")
    # Same messages should generate same key
    key1 = cache._generate_key(messages)
    key2 = cache._generate_key(messages)
    print(f"Key 1: {key1}")
    print(f"Key 2: {key2}")
    print(f"Keys match: {key1 == key2}")
    
    # Different messages should generate different keys
    different_messages = [
        Message(role="user", content="What's the weather like today?")
    ]
    key3 = cache._generate_key(different_messages)
    print(f"Key 3 (different messages): {key3}")
    print(f"Keys differ: {key1 != key3}")
    
    # Test 5: Test cache expiration
    print("\n5. Testing cache expiration...")
    cache.set(messages, response, ttl=1)  # 1 second TTL
    print("Set response with 1s TTL")
    
    # Wait for expiration
    time.sleep(2)
    
    expired_response = cache.get(messages)
    if expired_response is None:
        print("Expired cache entry correctly returned None")
    else:
        print("ERROR: Expired cache entry should have returned None")
    
    # Test 6: Test cache size
    print("\n6. Testing cache size...")
    cache.clear()
    print("Cache cleared")
    
    size = cache.size()
    print(f"Cache size after clear: {size}")
    
    # Add some entries
    cache.set(messages, response, ttl=10)
    cache.set(different_messages, response, ttl=10)
    
    size = cache.size()
    print(f"Cache size after adding 2 entries: {size}")
    
    # Test 7: Test global cache
    print("\n7. Testing global cache...")
    global_cache = get_llm_cache()
    print(f"Global cache type: {type(global_cache).__name__}")
    
    global_cache.set(messages, response)
    global_response = global_cache.get(messages)
    
    if global_response:
        print("Global cache hit successful")
    else:
        print("Global cache miss - unexpected")
    
    # Test 8: Test cache cleanup
    print("\n8. Testing cache cleanup...")
    # Add an expired entry
    cache.set(messages, response, ttl=1)
    time.sleep(2)
    
    # Add a valid entry
    cache.set(different_messages, response, ttl=10)
    
    print(f"Cache size before cleanup: {cache.size()}")
    cache.cleanup()
    print(f"Cache size after cleanup: {cache.size()}")
    
    # Test 9: Test clear cache
    print("\n9. Testing cache clear...")
    clear_llm_cache()
    global_cache_size = get_llm_cache().size()
    print(f"Global cache size after clear: {global_cache_size}")
    
    print("\nLLM cache test completed successfully!")


if __name__ == "__main__":
    test_llm_cache()