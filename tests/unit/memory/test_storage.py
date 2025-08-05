"""
Unit tests for memory storage.

Migrated from scripts/test_basic_memory.py with improvements and proper isolation.
"""

import os
import tempfile
import shutil
import pytest
from datetime import datetime
from src.personal_agent.memory.storage import SQLiteMemoryStorage
from src.personal_agent.memory.models import MemoryItem, Entity, Relationship


class TestSQLiteMemoryStorage:
    """Test SQLite memory storage functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_memory.db")
        storage = SQLiteMemoryStorage(db_path=db_path)
        
        yield storage
        
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_memory_item(self):
        """Create a sample memory item for testing."""
        return MemoryItem(
            id="test-memory-item-1",
            type="test",
            content={"message": "This is a test memory item"},
            metadata={"test": True, "created_by": "unit_test"},
            entities=[
                Entity(
                    id="entity-1",
                    type="person",
                    value="John Doe",
                    confidence=0.9,
                    metadata={"source": "test"}
                )
            ],
            relationships=[
                Relationship(
                    source_entity_id="entity-1",
                    target_entity_id="entity-2",
                    relationship_type="knows",
                    confidence=0.8,
                    metadata={"context": "test"}
                )
            ]
        )
    
    def test_storage_initialization(self, temp_storage):
        """Test storage initialization."""
        assert temp_storage is not None
        assert hasattr(temp_storage, 'db_path')
        assert hasattr(temp_storage, 'pool_size')
    
    def test_save_memory_item(self, temp_storage, sample_memory_item):
        """Test saving a memory item."""
        result = temp_storage.save(sample_memory_item)
        assert result is True
    
    def test_retrieve_memory_item(self, temp_storage, sample_memory_item):
        """Test retrieving a memory item."""
        # Save the item first
        save_result = temp_storage.save(sample_memory_item)
        assert save_result is True
        
        # Retrieve the item
        retrieved_item = temp_storage.retrieve(sample_memory_item.id)
        
        assert retrieved_item is not None
        assert retrieved_item.id == sample_memory_item.id
        assert retrieved_item.type == sample_memory_item.type
        assert retrieved_item.content == sample_memory_item.content
        assert retrieved_item.metadata == sample_memory_item.metadata
        
        # Check entities
        assert len(retrieved_item.entities) == len(sample_memory_item.entities)
        if retrieved_item.entities:
            entity = retrieved_item.entities[0]
            original_entity = sample_memory_item.entities[0]
            assert entity.id == original_entity.id
            assert entity.type == original_entity.type
            assert entity.value == original_entity.value
            assert entity.confidence == original_entity.confidence
    
    def test_retrieve_nonexistent_item(self, temp_storage):
        """Test retrieving a nonexistent memory item."""
        result = temp_storage.retrieve("nonexistent-id")
        assert result is None
    
    def test_search_memory_items(self, temp_storage, sample_memory_item):
        """Test searching for memory items."""
        # Save the item first
        temp_storage.save(sample_memory_item)
        
        # Search for it
        results = temp_storage.search("test memory item")
        
        assert len(results) >= 1
        found_item = results[0]
        assert found_item.id == sample_memory_item.id
        assert found_item.content == sample_memory_item.content
    
    def test_search_with_type_filter(self, temp_storage, sample_memory_item):
        """Test searching with type filter."""
        # Save the item first
        temp_storage.save(sample_memory_item)
        
        # Search with correct type
        results = temp_storage.search("test", type="test")
        assert len(results) >= 1
        
        # Search with wrong type
        results = temp_storage.search("test", type="wrong_type")
        assert len(results) == 0
    
    def test_search_with_limit(self, temp_storage):
        """Test searching with limit."""
        # Create multiple items
        for i in range(5):
            item = MemoryItem(
                id=f"test-item-{i}",
                type="test",
                content={"message": f"Test message {i}"},
                metadata={"index": i}
            )
            temp_storage.save(item)
        
        # Search with limit
        results = temp_storage.search("Test message", limit=3)
        assert len(results) <= 3
    
    def test_update_memory_item(self, temp_storage, sample_memory_item):
        """Test updating a memory item."""
        # Save the original item
        temp_storage.save(sample_memory_item)
        
        # Modify the item
        sample_memory_item.content["message"] = "Updated test memory item"
        sample_memory_item.metadata["updated"] = True
        
        # Update the item
        result = temp_storage.update(sample_memory_item)
        assert result is True
        
        # Retrieve and verify the update
        updated_item = temp_storage.retrieve(sample_memory_item.id)
        assert updated_item.content["message"] == "Updated test memory item"
        assert updated_item.metadata["updated"] is True
        assert updated_item.updated_at > updated_item.created_at
    
    def test_delete_memory_item(self, temp_storage, sample_memory_item):
        """Test deleting a memory item."""
        # Save the item first
        temp_storage.save(sample_memory_item)
        
        # Verify it exists
        retrieved_item = temp_storage.retrieve(sample_memory_item.id)
        assert retrieved_item is not None
        
        # Delete the item
        result = temp_storage.delete(sample_memory_item.id)
        assert result is True
        
        # Verify it's gone
        deleted_item = temp_storage.retrieve(sample_memory_item.id)
        assert deleted_item is None
    
    def test_delete_nonexistent_item(self, temp_storage):
        """Test deleting a nonexistent item."""
        result = temp_storage.delete("nonexistent-id")
        assert result is False
    
    def test_database_file_creation(self):
        """Test that database file is created."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_creation.db")
        
        try:
            # Initially, database file shouldn't exist
            assert not os.path.exists(db_path)
            
            # Create storage and save an item
            storage = SQLiteMemoryStorage(db_path=db_path)
            item = MemoryItem(id="test", content={"test": True})
            storage.save(item)
            
            # Now database file should exist
            assert os.path.exists(db_path)
            
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def test_concurrent_operations(self, temp_storage):
        """Test concurrent save/retrieve operations."""
        items = []
        for i in range(10):
            item = MemoryItem(
                id=f"concurrent-test-{i}",
                type="concurrent",
                content={"index": i, "message": f"Concurrent test {i}"}
            )
            items.append(item)
        
        # Save all items
        for item in items:
            result = temp_storage.save(item)
            assert result is True
        
        # Retrieve all items
        for item in items:
            retrieved = temp_storage.retrieve(item.id)
            assert retrieved is not None
            assert retrieved.content["index"] == item.content["index"]
    
    def test_empty_search_query(self, temp_storage, sample_memory_item):
        """Test search with empty query."""
        temp_storage.save(sample_memory_item)
        
        # Empty query should return empty results
        results = temp_storage.search("")
        assert len(results) == 0
    
    def test_storage_with_complex_content(self, temp_storage):
        """Test storage with complex nested content."""
        complex_item = MemoryItem(
            id="complex-test",
            type="complex",
            content={
                "nested": {
                    "data": [1, 2, 3],
                    "info": {"key": "value", "number": 42}
                },
                "list": ["a", "b", "c"],
                "boolean": True,
                "null_value": None
            },
            metadata={
                "complexity": "high",
                "tags": ["test", "complex", "nested"]
            }
        )
        
        # Save and retrieve
        result = temp_storage.save(complex_item)
        assert result is True
        
        retrieved = temp_storage.retrieve(complex_item.id)
        assert retrieved is not None
        assert retrieved.content == complex_item.content
        assert retrieved.metadata == complex_item.metadata


class TestMemoryItemModel:
    """Test MemoryItem model functionality."""
    
    def test_memory_item_creation(self):
        """Test creating a memory item."""
        item = MemoryItem(
            type="test",
            content={"message": "test"},
            metadata={"test": True}
        )
        
        assert item.id is not None  # Should be auto-generated
        assert item.type == "test"
        assert item.content == {"message": "test"}
        assert item.metadata == {"test": True}
        assert item.created_at is not None
        assert item.updated_at is not None
        assert isinstance(item.entities, list)
        assert isinstance(item.relationships, list)
    
    def test_memory_item_with_entities(self):
        """Test creating a memory item with entities."""
        entity = Entity(
            id="test-entity",
            type="person",
            value="Test Person",
            confidence=0.95
        )
        
        item = MemoryItem(
            type="test",
            content={"message": "test"},
            entities=[entity]
        )
        
        assert len(item.entities) == 1
        assert item.entities[0].id == "test-entity"
        assert item.entities[0].type == "person"
        assert item.entities[0].value == "Test Person"
        assert item.entities[0].confidence == 0.95