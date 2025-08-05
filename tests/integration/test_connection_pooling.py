#!/usr/bin/env python3
"""
Test script for connection pooling functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.personal_agent.memory.storage import SQLiteMemoryStorage
from src.personal_agent.memory.models import MemoryItem


def test_connection_pooling():
    """Test connection pooling functionality."""
    print("Testing connection pooling...")
    
    # Test 1: Create storage with connection pooling
    print("\n1. Testing storage creation with connection pooling...")
    storage = SQLiteMemoryStorage("data/test_memory.db", pool_size=3)
    print(f"Storage created: {type(storage).__name__}")
    print(f"Pool size: {storage.pool_size}")
    
    # Test 2: Create test data
    print("\n2. Creating test data...")
    # Create a memory item
    memory_item = MemoryItem(
        type="test",
        content={"message": "Hello, connection pooling!"}
    )
    
    # Save the item
    result = storage.save(memory_item)
    print(f"Memory item saved: {result}")
    
    # Test 3: Retrieve the item
    print("\n3. Testing item retrieval...")
    retrieved_item = storage.retrieve(memory_item.id)
    if retrieved_item:
        print(f"Item retrieved successfully")
        print(f"Item content: {retrieved_item.content}")
    else:
        print("Item retrieval failed")
    
    # Test 4: Test search functionality
    print("\n4. Testing search functionality...")
    search_results = storage.search("Hello", limit=5)
    print(f"Search returned {len(search_results)} items")
    
    # Test 5: Test delete functionality
    print("\n5. Testing delete functionality...")
    delete_result = storage.delete(memory_item.id)
    print(f"Item deleted: {delete_result}")
    
    # Verify deletion
    deleted_item = storage.retrieve(memory_item.id)
    if deleted_item is None:
        print("Item successfully deleted")
    else:
        print("Item deletion failed")
    
    print("\nConnection pooling test completed successfully!")


if __name__ == "__main__":
    test_connection_pooling()