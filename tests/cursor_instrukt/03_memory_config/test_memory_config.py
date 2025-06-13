"""Test suite for memory configuration.

This module contains tests to validate the memory configuration
as specified in 03_KONFIGURERA_MINNE.md.
"""

import pytest
from memory.memory_manager import MemoryManager
from memory.config import MemorySettings
import redis
from chromadb import Client

@pytest.fixture
def memory_settings():
    """Create memory settings for testing."""
    return MemorySettings()

@pytest.fixture
def memory_manager(memory_settings):
    """Create a memory manager instance for testing."""
    return MemoryManager(
        chroma_host=memory_settings.CHROMA_HOST,
        chroma_port=memory_settings.CHROMA_PORT,
        redis_url=memory_settings.REDIS_URL
    )

def test_chroma_connection(memory_manager):
    """Test ChromaDB connection."""
    # Verify ChromaDB collection exists
    assert memory_manager.ltm.collection is not None
    # Test adding a document
    memory_manager.store_memory(
        text="Test memory",
        metadata={"type": "test", "timestamp": "2024-03-12"}
    )
    # Test querying
    results = memory_manager.query_memory("Test memory", n_results=1)
    assert len(results["documents"]) > 0

def test_redis_connection(memory_manager):
    """Test Redis connection."""
    # Test setting context
    session_id = "test_session"
    context = "Test context"
    memory_manager.stm.set_context(session_id, context)
    # Test getting context
    retrieved = memory_manager.stm.get_context(session_id)
    assert retrieved == context

def test_memory_integration(memory_manager):
    """Test integration between ChromaDB and Redis."""
    # Store in LTM
    memory_manager.store_memory(
        text="Integration test",
        metadata={"type": "integration", "timestamp": "2024-03-12"}
    )
    # Cache in STM
    session_id = "integration_test"
    memory_manager.stm.set_context(session_id, "Integration context")
    # Verify both
    ltm_results = memory_manager.query_memory("Integration test", n_results=1)
    stm_context = memory_manager.stm.get_context(session_id)
    assert len(ltm_results["documents"]) > 0
    assert stm_context == "Integration context" 