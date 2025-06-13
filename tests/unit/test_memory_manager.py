"""
Unit tests for the MemoryManager class.
Tests both short-term and long-term memory operations.
"""

import pytest
import os
from datetime import datetime
from memory.memory_manager import MemoryManager

@pytest.fixture
def memory_manager():
    """Create memory manager instance for testing."""
    return MemoryManager(
        redis_url=os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/0'),
        chroma_url=os.getenv('TEST_CHROMA_URL', 'http://localhost:8000')
    )

def test_store_memory(memory_manager):
    """Test storing memory in both short-term and long-term storage."""
    # Test data
    memory_data = {
        "content": "Test memory content",
        "metadata": {"source": "test", "timestamp": datetime.now().isoformat()}
    }
    
    # Store memory
    memory_id = memory_manager.store_memory(memory_data)
    assert memory_id is not None
    
    # Verify in short-term storage
    stm_memory = memory_manager.get_memory(memory_id)
    assert stm_memory is not None
    assert stm_memory["content"] == memory_data["content"]
    
    # Verify in long-term storage
    ltm_memory = memory_manager.get_memory(memory_id, long_term=True)
    assert ltm_memory is not None
    assert ltm_memory["content"] == memory_data["content"]

def test_search_memories(memory_manager):
    """Test searching memories by content."""
    # Store test memories
    memories = [
        {"content": "First test memory", "metadata": {"source": "test"}},
        {"content": "Second test memory", "metadata": {"source": "test"}},
        {"content": "Third test memory", "metadata": {"source": "test"}}
    ]
    
    for memory in memories:
        memory_manager.store_memory(memory)
    
    # Search memories
    results = memory_manager.search_memories("test memory")
    assert len(results) >= 3
    
    # Verify search results
    for result in results:
        assert "test memory" in result["content"].lower()

def test_clear_memories(memory_manager):
    """Test clearing memories from storage."""
    # Store test memory
    memory_data = {
        "content": "Memory to be cleared",
        "metadata": {"source": "test"}
    }
    memory_id = memory_manager.store_memory(memory_data)
    
    # Clear memory
    memory_manager.clear_memory(memory_id)
    
    # Verify memory is cleared
    assert memory_manager.get_memory(memory_id) is None
    assert memory_manager.get_memory(memory_id, long_term=True) is None

def test_memory_metadata(memory_manager):
    """Test memory metadata handling."""
    # Test data with metadata
    metadata = {
        "source": "test",
        "timestamp": datetime.now().isoformat(),
        "tags": ["test", "unit"],
        "priority": 1
    }
    memory_data = {
        "content": "Memory with metadata",
        "metadata": metadata
    }
    
    # Store memory
    memory_id = memory_manager.store_memory(memory_data)
    
    # Verify metadata
    stored_memory = memory_manager.get_memory(memory_id)
    assert stored_memory["metadata"] == metadata

def test_error_handling(memory_manager):
    """Test error handling for invalid operations."""
    # Test invalid memory ID
    with pytest.raises(ValueError):
        memory_manager.get_memory("invalid_id")
    
    # Test invalid memory data
    with pytest.raises(ValueError):
        memory_manager.store_memory({"invalid": "data"})
    
    # Test clearing non-existent memory
    with pytest.raises(ValueError):
        memory_manager.clear_memory("non_existent_id") 