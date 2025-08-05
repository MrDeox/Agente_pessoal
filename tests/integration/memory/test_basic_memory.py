#!/usr/bin/env python3
"""
Simple test script to verify basic memory functionality without encryption.
"""

import sys
import os
import tempfile
import shutil

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.memory.storage import SQLiteMemoryStorage
from personal_agent.memory.models import MemoryItem

def test_basic_memory_functionality():
    """Test basic memory functionality."""
    print("Testing basic memory functionality...")
    
    # Create a temporary directory for test database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_memory.db")
    
    try:
        # Create storage
        storage = SQLiteMemoryStorage(db_path)
        
        # Test saving a memory item
        memory_item = MemoryItem(
            type="test",
            content={"message": "This is a test memory item"},
            metadata={"test": True}
        )
        
        print(f"Saving memory item with ID: {memory_item.id}")
        success = storage.save(memory_item)
        print(f"Save result: {success}")
        
        # Test retrieving the memory item
        print("Retrieving memory item...")
        retrieved_item = storage.retrieve(memory_item.id)
        print(f"Retrieved item: {retrieved_item}")
        
        if retrieved_item:
            print(f"Retrieved content: {retrieved_item.content}")
            print(f"Retrieved metadata: {retrieved_item.metadata}")
            
            # Verify content matches
            if retrieved_item.content == memory_item.content:
                print("✓ Content matches")
            else:
                print("✗ Content mismatch")
                
            if retrieved_item.metadata == memory_item.metadata:
                print("✓ Metadata matches")
            else:
                print("✗ Metadata mismatch")
        
        # Test searching for memory items
        print("Searching for memory items...")
        results = storage.search("test", type="test")
        print(f"Search results: {len(results)} items found")
        
        if results:
            print(f"First result content: {results[0].content}")
        
        # Test updating a memory item
        print("Updating memory item...")
        memory_item.content = {"message": "This is an updated test memory item"}
        success = storage.update(memory_item)
        print(f"Update result: {success}")
        
        # Verify update
        updated_item = storage.retrieve(memory_item.id)
        if updated_item and updated_item.content == memory_item.content:
            print("✓ Update verified")
        else:
            print("✗ Update failed")
        
        # Test deleting a memory item
        print("Deleting memory item...")
        success = storage.delete(memory_item.id)
        print(f"Delete result: {success}")
        
        # Verify deletion
        deleted_item = storage.retrieve(memory_item.id)
        if deleted_item is None:
            print("✓ Deletion verified")
        else:
            print("✗ Deletion failed")
            
        print("Basic memory functionality test completed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
            print("Temporary directory cleaned up")
        except Exception as e:
            print(f"Warning: Failed to clean up temporary directory: {e}")

if __name__ == "__main__":
    test_basic_memory_functionality()