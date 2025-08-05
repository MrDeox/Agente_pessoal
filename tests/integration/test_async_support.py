#!/usr/bin/env python3
"""
Test script for asynchronous database operations in the memory storage system.
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import the modules
# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from personal_agent.memory.storage import AsyncSQLiteMemoryStorage, SQLiteMemoryStorage
from personal_agent.memory.models import MemoryItem, Entity, Relationship


async def test_async_storage():
    """Test the asynchronous storage implementation."""
    print("Testing asynchronous storage implementation...")
    
    # Create an async storage instance
    storage = AsyncSQLiteMemoryStorage("data/test_async_memory.db")
    
    # Create a test memory item
    entity = Entity(
        id="entity1",
        type="person",
        value="John Doe",
        confidence=0.9
    )
    
    relationship = Relationship(
        source_entity_id="entity1",
        target_entity_id="entity2",
        relationship_type="knows",
        confidence=0.8
    )
    
    memory_item = MemoryItem(
        id="test_item_1",
        type="conversation",
        content={"message": "Hello, world!"},
        metadata={"test": True},
        entities=[entity],
        relationships=[relationship]
    )
    
    # Test save operation
    print("Testing save operation...")
    result = await storage.save(memory_item)
    assert result, "Failed to save memory item"
    print("Save operation successful")
    
    # Test retrieve operation
    print("Testing retrieve operation...")
    retrieved_item = await storage.retrieve("test_item_1")
    assert retrieved_item is not None, "Failed to retrieve memory item"
    assert retrieved_item.id == "test_item_1", "Retrieved item has wrong ID"
    assert retrieved_item.type == "conversation", "Retrieved item has wrong type"
    assert retrieved_item.content["message"] == "Hello, world!", "Retrieved item has wrong content"
    assert len(retrieved_item.entities) == 1, "Retrieved item has wrong number of entities"
    assert len(retrieved_item.relationships) == 1, "Retrieved item has wrong number of relationships"
    print("Retrieve operation successful")
    
    # Test search operation
    print("Testing search operation...")
    search_results = await storage.search("Hello")
    assert len(search_results) == 1, "Search returned wrong number of results"
    assert search_results[0].id == "test_item_1", "Search returned wrong item"
    print("Search operation successful")
    
    # Test update operation
    print("Testing update operation...")
    memory_item.content["message"] = "Updated message"
    update_result = await storage.update(memory_item)
    assert update_result, "Failed to update memory item"
    
    # Verify update
    updated_item = await storage.retrieve("test_item_1")
    assert updated_item.content["message"] == "Updated message", "Update was not successful"
    print("Update operation successful")
    
    # Test delete operation
    print("Testing delete operation...")
    delete_result = await storage.delete("test_item_1")
    assert delete_result, "Failed to delete memory item"
    
    # Verify deletion
    deleted_item = await storage.retrieve("test_item_1")
    assert deleted_item is None, "Item was not deleted"
    print("Delete operation successful")
    
    print("All asynchronous storage tests passed!")


def test_sync_storage():
    """Test the synchronous storage implementation."""
    print("\nTesting synchronous storage implementation...")
    
    # Create a sync storage instance
    storage = SQLiteMemoryStorage("data/test_sync_memory.db")
    
    # Create a test memory item
    entity = Entity(
        id="entity1",
        type="person",
        value="Jane Doe",
        confidence=0.95
    )
    
    relationship = Relationship(
        source_entity_id="entity1",
        target_entity_id="entity2",
        relationship_type="works_with",
        confidence=0.85
    )
    
    memory_item = MemoryItem(
        id="test_item_2",
        type="knowledge",
        content={"fact": "The sky is blue"},
        metadata={"test": True},
        entities=[entity],
        relationships=[relationship]
    )
    
    # Test save operation
    print("Testing save operation...")
    result = storage.save(memory_item)
    assert result, "Failed to save memory item"
    print("Save operation successful")
    
    # Test retrieve operation
    print("Testing retrieve operation...")
    retrieved_item = storage.retrieve("test_item_2")
    assert retrieved_item is not None, "Failed to retrieve memory item"
    assert retrieved_item.id == "test_item_2", "Retrieved item has wrong ID"
    assert retrieved_item.type == "knowledge", "Retrieved item has wrong type"
    assert retrieved_item.content["fact"] == "The sky is blue", "Retrieved item has wrong content"
    assert len(retrieved_item.entities) == 1, "Retrieved item has wrong number of entities"
    assert len(retrieved_item.relationships) == 1, "Retrieved item has wrong number of relationships"
    print("Retrieve operation successful")
    
    # Test search operation
    print("Testing search operation...")
    search_results = storage.search("sky")
    assert len(search_results) == 1, "Search returned wrong number of results"
    assert search_results[0].id == "test_item_2", "Search returned wrong item"
    print("Search operation successful")
    
    # Test update operation
    print("Testing update operation...")
    memory_item.content["fact"] = "The grass is green"
    update_result = storage.update(memory_item)
    assert update_result, "Failed to update memory item"
    
    # Verify update
    updated_item = storage.retrieve("test_item_2")
    assert updated_item.content["fact"] == "The grass is green", "Update was not successful"
    print("Update operation successful")
    
    # Test delete operation
    print("Testing delete operation...")
    delete_result = storage.delete("test_item_2")
    assert delete_result, "Failed to delete memory item"
    
    # Verify deletion
    deleted_item = storage.retrieve("test_item_2")
    assert deleted_item is None, "Item was not deleted"
    print("Delete operation successful")
    
    print("All synchronous storage tests passed!")


async def main():
    """Main function to run all tests."""
    try:
        # Run async tests
        await test_async_storage()
        
        # Run sync tests
        test_sync_storage()
        
        print("\nAll tests passed successfully!")
        return 0
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)