#!/usr/bin/env python3
"""
Test script for optimized database queries.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.personal_agent.memory.storage import SQLiteMemoryStorage
from src.personal_agent.memory.models import MemoryItem


def test_optimized_queries():
    """Test optimized database queries."""
    print("Testing optimized database queries...")
    
    # Test 1: Create storage
    print("\n1. Testing storage creation...")
    storage = SQLiteMemoryStorage("data/test_memory.db")
    print(f"Storage created: {type(storage).__name__}")
    
    # Test 2: Create test data
    print("\n2. Creating test data...")
    # Create a conversation memory item
    conversation_content = {
        "conversation_id": "test_conv_1",
        "user_id": "test_user",
        "turns": [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"},
            {"role": "user", "content": "What's the weather like today?"},
            {"role": "assistant", "content": "I don't have access to real-time weather data."}
        ]
    }
    
    memory_item = MemoryItem(
        type="conversation",
        content=conversation_content
    )
    
    # Save the item
    result = storage.save(memory_item)
    print(f"Memory item saved: {result}")
    
    # Test 3: Test original method
    print("\n3. Testing original get_conversation_history method...")
    original_result = storage.get_conversation_history(limit=5)
    print(f"Original method returned {len(original_result)} items")
    if original_result:
        print(f"First item type: {original_result[0].type}")
        print(f"First item turns: {len(original_result[0].content.get('turns', []))}")
    
    # Test 4: Test optimized method
    print("\n4. Testing optimized get_recent_conversation_turns method...")
    optimized_result = storage.get_recent_conversation_turns(limit=10)
    print(f"Optimized method returned {len(optimized_result)} turns")
    if optimized_result:
        print(f"First turn role: {optimized_result[0]['role']}")
        print(f"First turn content: {optimized_result[0]['content']}")
    
    # Test 5: Compare results
    print("\n5. Comparing results...")
    if original_result and optimized_result:
        original_turns = []
        for item in original_result:
            original_turns.extend(item.content.get("turns", []))
        
        print(f"Original method extracted {len(original_turns)} turns")
        print(f"Optimized method extracted {len(optimized_result)} turns")
        print(f"Results match: {original_turns == optimized_result}")
    
    print("\nOptimized database queries test completed successfully!")


if __name__ == "__main__":
    test_optimized_queries()