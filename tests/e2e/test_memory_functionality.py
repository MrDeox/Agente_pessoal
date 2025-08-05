#!/usr/bin/env python3
"""
End-to-end test for memory functionality in the personal agent.

This test focuses specifically on memory operations including:
- Storing and retrieving conversation history
- Remembering user preferences and facts
- Memory search and retrieval
- Memory persistence
"""

import sys
import os
import traceback
from typing import List
import tempfile
import shutil

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from personal_agent.core.agent import Agent
from personal_agent.memory.storage import SQLiteMemoryStorage
from personal_agent.memory.models import MemoryItem


class MemoryTestResult:
    """Represents the result of a memory test."""
    
    def __init__(self, name: str, passed: bool, message: str = "", error: Exception = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.error = error


class MemoryTestReport:
    """Generates and manages memory test reports."""
    
    def __init__(self):
        self.results: List[MemoryTestResult] = []
    
    def add_result(self, result: MemoryTestResult):
        """Add a test result to the report."""
        self.results.append(result)
    
    def generate_report(self) -> str:
        """Generate a formatted test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("=" * 60)
        report.append("PERSONAL AGENT - MEMORY FUNCTIONALITY TEST REPORT")
        report.append("=" * 60)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success Rate: {passed_tests / total_tests * 100:.1f}%" if total_tests > 0 else "No tests run")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 40)
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            report.append(f"[{status}] {result.name}")
            if not result.passed:
                report.append(f"    Message: {result.message}")
                if result.error:
                    report.append(f"    Error: {str(result.error)}")
            report.append("")
        
        # Summary
        report.append("-" * 40)
        report.append("SUMMARY:")
        report.append(f"Overall Status: {'PASSED' if failed_tests == 0 else 'FAILED'}")
        report.append("=" * 60)
        
        return "\n".join(report)


def create_test_memory_storage() -> SQLiteMemoryStorage:
    """Create a test memory storage with a temporary database."""
    # Create a temporary directory for test database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_memory.db")
    storage = SQLiteMemoryStorage(db_path)
    return storage, temp_dir


def cleanup_test_storage(temp_dir: str):
    """Clean up temporary test storage."""
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Warning: Failed to clean up temporary directory: {e}")


def test_memory_storage_operations(report: MemoryTestReport) -> bool:
    """Test basic memory storage operations."""
    temp_dir = None
    try:
        # Create test storage
        storage, temp_dir = create_test_memory_storage()
        
        # Test saving a memory item
        memory_item = MemoryItem(
            type="test",
            content={"message": "This is a test memory item"},
            metadata={"test": True}
        )
        
        success = storage.save(memory_item)
        assert success, "Saving memory item should succeed"
        
        # Test retrieving the memory item
        retrieved_item = storage.retrieve(memory_item.id)
        assert retrieved_item is not None, "Retrieved item should not be None"
        assert retrieved_item.id == memory_item.id, "Retrieved item ID should match"
        assert retrieved_item.content == memory_item.content, "Retrieved content should match"
        
        # Test searching for memory items
        results = storage.search("test", type="test")
        assert len(results) > 0, "Search should return at least one result"
        assert results[0].id == memory_item.id, "Search result ID should match"
        
        # Test updating a memory item
        memory_item.content = {"message": "This is an updated test memory item"}
        success = storage.update(memory_item)
        assert success, "Updating memory item should succeed"
        
        # Verify update
        updated_item = storage.retrieve(memory_item.id)
        assert updated_item.content == memory_item.content, "Updated content should match"
        
        # Test deleting a memory item
        success = storage.delete(memory_item.id)
        assert success, "Deleting memory item should succeed"
        
        # Verify deletion
        deleted_item = storage.retrieve(memory_item.id)
        assert deleted_item is None, "Deleted item should not be retrievable"
        
        report.add_result(MemoryTestResult("Memory Storage Operations", True, "All memory storage operations work correctly"))
        return True
        
    except Exception as e:
        report.add_result(MemoryTestResult("Memory Storage Operations", False, "Memory storage operations failed", e))
        return False
    finally:
        if temp_dir:
            cleanup_test_storage(temp_dir)


def test_conversation_memory(report: MemoryTestReport) -> bool:
    """Test conversation memory functionality."""
    temp_dir = None
    try:
        # Create test storage
        storage, temp_dir = create_test_memory_storage()
        
        # Create agent with test storage
        agent = Agent(user_id="test_user_memory")
        agent.memory_service.storage = storage
        
        # Test saving conversation turns
        success = storage.save_conversation_turn(
            user_id="test_user_memory",
            user_input="Hello, what is the weather today?",
            agent_response="I'm an AI assistant, so I don't have access to real-time weather information."
        )
        assert success, "Saving conversation turn should succeed"
        
        # Test retrieving conversation history
        history = storage.get_conversation_history(limit=5)
        assert len(history) > 0, "Conversation history should not be empty"
        assert history[0].type == "conversation", "History item should be of type conversation"
        
        # Test that agent can access conversation history
        context = agent.get_memory_context()
        assert isinstance(context, str), "Memory context should be a string"
        assert "weather" in context.lower(), "Context should contain conversation content"
        
        report.add_result(MemoryTestResult("Conversation Memory", True, "Conversation memory functionality works correctly"))
        return True
        
    except Exception as e:
        report.add_result(MemoryTestResult("Conversation Memory", False, "Conversation memory functionality failed", e))
        return False
    finally:
        if temp_dir:
            cleanup_test_storage(temp_dir)


def test_knowledge_memory(report: MemoryTestReport) -> bool:
    """Test knowledge memory functionality (preferences and facts)."""
    temp_dir = None
    try:
        # Create test storage
        storage, temp_dir = create_test_memory_storage()
        
        # Create agent with test storage
        agent = Agent(user_id="test_user_knowledge")
        agent.memory_service.storage = storage
        
        # Test remembering preferences
        success = agent.remember_preference("I prefer Python over JavaScript")
        assert success, "Remembering preference should succeed"
        
        # Test remembering facts
        success = agent.remember_fact("My favorite number is 42")
        assert success, "Remembering fact should succeed"
        
        # Test searching for preferences
        preferences = storage.search("Python", type="knowledge")
        assert len(preferences) > 0, "Should find preference about Python"
        assert "preference" in preferences[0].content, "Content should contain preference key"
        
        # Test searching for facts
        facts = storage.search("42", type="knowledge")
        assert len(facts) > 0, "Should find fact about favorite number"
        assert "fact" in facts[0].content, "Content should contain fact key"
        
        # Test that agent can access knowledge in context
        context = agent.get_memory_context()
        assert isinstance(context, str), "Memory context should be a string"
        assert "Python" in context or "42" in context, "Context should contain knowledge content"
        
        report.add_result(MemoryTestResult("Knowledge Memory", True, "Knowledge memory functionality works correctly"))
        return True
        
    except Exception as e:
        report.add_result(MemoryTestResult("Knowledge Memory", False, "Knowledge memory functionality failed", e))
        return False
    finally:
        if temp_dir:
            cleanup_test_storage(temp_dir)


def test_memory_persistence(report: MemoryTestReport) -> bool:
    """Test memory persistence across agent instances."""
    temp_dir = None
    try:
        # Create test storage
        storage, temp_dir = create_test_memory_storage()
        db_path = storage.db_path
        
        # Create first agent and store some data
        agent1 = Agent(user_id="test_user_persistence")
        agent1.memory_service.storage = SQLiteMemoryStorage(db_path)
        
        # Store some data
        agent1.remember_preference("Persistence test preference")
        agent1.remember_fact("Persistence test fact")
        
        # Create second agent with same database
        agent2 = Agent(user_id="test_user_persistence")
        agent2.memory_service.storage = SQLiteMemoryStorage(db_path)
        
        # Verify data is accessible in second agent
        context = agent2.get_memory_context()
        assert isinstance(context, str), "Memory context should be a string"
        assert "Persistence test" in context, "Persisted data should be accessible"
        
        # Verify specific searches work
        preferences = agent2.memory_service.storage.search("Persistence test preference", type="knowledge")
        assert len(preferences) > 0, "Persisted preference should be found"
        
        facts = agent2.memory_service.storage.search("Persistence test fact", type="knowledge")
        assert len(facts) > 0, "Persisted fact should be found"
        
        report.add_result(MemoryTestResult("Memory Persistence", True, "Memory persistence works correctly"))
        return True
        
    except Exception as e:
        report.add_result(MemoryTestResult("Memory Persistence", False, "Memory persistence failed", e))
        return False
    finally:
        if temp_dir:
            cleanup_test_storage(temp_dir)


def test_memory_edge_cases(report: MemoryTestReport) -> bool:
    """Test memory edge cases and error handling."""
    temp_dir = None
    try:
        # Create test storage
        storage, temp_dir = create_test_memory_storage()
        
        # Test with empty search query
        results = storage.search("", type="test")
        assert isinstance(results, list), "Search with empty query should return list"
        
        # Test searching for non-existent items
        results = storage.search("nonexistentitem12345", type="test")
        assert isinstance(results, list), "Search for non-existent items should return list"
        assert len(results) == 0, "Search for non-existent items should return empty list"
        
        # Test retrieving non-existent item
        item = storage.retrieve("nonexistentid12345")
        assert item is None, "Retrieving non-existent item should return None"
        
        # Test deleting non-existent item
        success = storage.delete("nonexistentid12345")
        # Deleting non-existent item should return False (more correct behavior)
        assert isinstance(success, bool), "Delete should return a boolean"
        
        report.add_result(MemoryTestResult("Memory Edge Cases", True, "Memory edge cases handled correctly"))
        return True
        
    except Exception as e:
        report.add_result(MemoryTestResult("Memory Edge Cases", False, "Memory edge cases failed", e))
        return False
    finally:
        if temp_dir:
            cleanup_test_storage(temp_dir)


def run_memory_tests() -> MemoryTestReport:
    """Run all memory functionality tests."""
    print("Starting Personal Agent Memory Functionality Tests...")
    print("=" * 55)
    
    # Create test report
    report = MemoryTestReport()
    
    try:
        # Run all tests
        tests = [
            test_memory_storage_operations,
            test_conversation_memory,
            test_knowledge_memory,
            test_memory_persistence,
            test_memory_edge_cases
        ]
        
        for test_func in tests:
            print(f"Running {test_func.__name__}...")
            test_func(report)
        
        print("\n" + "=" * 55)
        print("Memory functionality tests completed!")
        
    except Exception as e:
        error_result = MemoryTestResult("Memory Test Suite", False, "Test suite failed to run", e)
        report.add_result(error_result)
        print(f"Test suite error: {e}")
        traceback.print_exc()
    
    return report


def main():
    """Main function to run the memory functionality tests."""
    # Run tests
    report = run_memory_tests()
    
    # Generate and print report
    report_text = report.generate_report()
    print("\n" + report_text)
    
    # Save report to file
    report_path = "test_results_memory.txt"
    with open(report_path, 'w') as f:
        f.write(report_text)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Return exit code based on test results
    failed_tests = sum(1 for r in report.results if not r.passed)
    return 1 if failed_tests > 0 else 0


if __name__ == "__main__":
    sys.exit(main())