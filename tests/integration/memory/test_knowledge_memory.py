#!/usr/bin/env python3
"""
Test script to verify knowledge memory functionality without encryption.
"""

import sys
import os
import tempfile
import shutil

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from personal_agent.memory.storage import SQLiteMemoryStorage
from personal_agent.memory.models import MemoryItem
from personal_agent.core.agent import Agent

def test_knowledge_memory_functionality():
    """Test knowledge memory functionality."""
    print("Testing knowledge memory functionality...")
    
    # Create a temporary directory for test database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_memory.db")
    
    try:
        # Create storage
        storage = SQLiteMemoryStorage(db_path)
        
        # Create agent with test storage
        agent = Agent(user_id="test_user_knowledge")
        agent.memory_service.storage = storage
        
        # Test remembering preferences
        print("Testing preference storage...")
        success = agent.remember_preference("I prefer Python over JavaScript")
        print(f"Preference storage result: {success}")
        
        # Test remembering facts
        print("Testing fact storage...")
        success = agent.remember_fact("My favorite number is 42")
        print(f"Fact storage result: {success}")
        
        # Test searching for preferences
        print("Searching for preferences...")
        preferences = storage.search("Python", type="knowledge")
        print(f"Preferences found: {len(preferences)}")
        
        if preferences:
            print(f"First preference content: {preferences[0].content}")
            if "preference" in preferences[0].content:
                print("✓ Preference content structure is correct")
            else:
                print("✗ Preference content structure is incorrect")
        
        # Test searching for facts
        print("Searching for facts...")
        facts = storage.search("42", type="knowledge")
        print(f"Facts found: {len(facts)}")
        
        if facts:
            print(f"First fact content: {facts[0].content}")
            if "fact" in facts[0].content:
                print("✓ Fact content structure is correct")
            else:
                print("✗ Fact content structure is incorrect")
        
        # Test that agent can access knowledge in context
        print("Testing memory context retrieval...")
        context = agent.get_memory_context()
        print(f"Context type: {type(context)}")
        print(f"Context length: {len(context)}")
        print(f"Context preview: {context[:100]}...")
        
        if isinstance(context, str):
            print("✓ Context is a string")
        else:
            print("✗ Context is not a string")
            
        if "Python" in context or "42" in context:
            print("✓ Context contains knowledge content")
        else:
            print("✗ Context does not contain knowledge content")
        
        print("Knowledge memory functionality test completed!")
        
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

def test_memory_persistence():
    """Test memory persistence across agent instances."""
    print("\nTesting memory persistence...")
    
    # Create a temporary directory for test database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_memory.db")
    
    try:
        # Create first agent and store some data
        agent1 = Agent(user_id="test_user_persistence")
        agent1.memory_service.storage = SQLiteMemoryStorage(db_path)
        
        # Store some data
        print("Storing data with first agent...")
        success1 = agent1.remember_preference("Persistence test preference")
        success2 = agent1.remember_fact("Persistence test fact")
        print(f"Preference storage: {success1}")
        print(f"Fact storage: {success2}")
        
        # Create second agent with same database
        print("Creating second agent with same database...")
        agent2 = Agent(user_id="test_user_persistence")
        agent2.memory_service.storage = SQLiteMemoryStorage(db_path)
        
        # Verify data is accessible in second agent
        print("Retrieving context with second agent...")
        context = agent2.get_memory_context()
        print(f"Context length: {len(context)}")
        print(f"Context preview: {context[:100]}...")
        
        if isinstance(context, str):
            print("✓ Context is a string")
        else:
            print("✗ Context is not a string")
            
        if "Persistence test" in context:
            print("✓ Persisted data is accessible")
        else:
            print("✗ Persisted data is not accessible")
        
        # Verify specific searches work
        print("Searching for persisted preference...")
        preferences = agent2.memory_service.storage.search("Persistence test preference", type="knowledge")
        print(f"Preferences found: {len(preferences)}")
        
        if len(preferences) > 0:
            print("✓ Persisted preference found")
        else:
            print("✗ Persisted preference not found")
        
        print("Searching for persisted fact...")
        facts = agent2.memory_service.storage.search("Persistence test fact", type="knowledge")
        print(f"Facts found: {len(facts)}")
        
        if len(facts) > 0:
            print("✓ Persisted fact found")
        else:
            print("✗ Persisted fact not found")
            
        print("Memory persistence test completed!")
        
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
    test_knowledge_memory_functionality()
    test_memory_persistence()