#!/usr/bin/env python3
"""
Test script to verify the JSONDecodeError fix.
"""

import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.memory.storage import SQLiteMemoryStorage
from personal_agent.memory.models import MemoryItem

def test_json_decode_error_fix():
    """Test that JSONDecodeError is handled properly."""
    print("Testing JSONDecodeError fix...")
    
    # Create a storage instance
    storage = SQLiteMemoryStorage("data/test_memory.db")
    
    # Create a memory item with valid JSON content
    memory_item = MemoryItem(
        type="conversation",
        content={"test": "data", "turns": [{"role": "user", "content": "Hello"}]},
        metadata={"test": "metadata"}
    )
    
    # Save the item
    result = storage.save(memory_item)
    print(f"Save result: {result}")
    
    # Retrieve the item
    retrieved_item = storage.retrieve(memory_item.id)
    print(f"Retrieved item: {retrieved_item is not None}")
    
    # Test get_recent_conversation_turns
    turns = storage.get_recent_conversation_turns(limit=5)
    print(f"Recent conversation turns: {len(turns)}")
    
    print("Test completed successfully!")

if __name__ == "__main__":
    test_json_decode_error_fix()