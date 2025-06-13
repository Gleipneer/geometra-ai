"""Unit tests for MemoryManager."""

import pytest
from unittest.mock import Mock, patch
from src.ai.memory.memory_manager import MemoryManager

@pytest.fixture
def memory_manager(db_manager, chroma_client):
    """Create MemoryManager instance for testing."""
    return MemoryManager(db_manager, chroma_client)

@pytest.mark.asyncio
async def test_store_stm(memory_manager):
    """Test storing short-term memory."""
    user_id = "test_user"
    content = "Test content"
    metadata = {"type": "test"}
    
    # Mock Redis setex
    with patch.object(memory_manager.db.redis, "setex") as mock_setex:
        await memory_manager.store_stm(user_id, content, metadata)
        
        # Verify Redis call
        assert mock_setex.called
        args = mock_setex.call_args[0]
        assert args[0].startswith(f"stm:{user_id}:")
        assert "content" in args[1]
        assert "metadata" in args[1]
        assert "timestamp" in args[1]

@pytest.mark.asyncio
async def test_store_ltm(memory_manager):
    """Test storing long-term memory."""
    content = "Test content"
    metadata = {"type": "test"}
    
    # Mock ChromaDB add
    with patch.object(memory_manager.collection, "add") as mock_add:
        await memory_manager.store_ltm(content, metadata)
        
        # Verify ChromaDB call
        assert mock_add.called
        args = mock_add.call_args[1]
        assert args["documents"] == [content]
        assert args["metadatas"] == [metadata]
        assert len(args["ids"]) == 1
        assert args["ids"][0].startswith("ltm:")

@pytest.mark.asyncio
async def test_get_stm(memory_manager):
    """Test getting short-term memory."""
    user_id = "test_user"
    
    # Mock Redis operations
    with patch.object(memory_manager.db.redis, "keys") as mock_keys:
        with patch.object(memory_manager.db.redis, "mget") as mock_mget:
            mock_keys.return_value = ["stm:test_user:1", "stm:test_user:2"]
            mock_mget.return_value = [
                '{"content": "Test 1", "metadata": {}, "timestamp": "2024-01-01T00:00:00"}',
                '{"content": "Test 2", "metadata": {}, "timestamp": "2024-01-01T00:01:00"}'
            ]
            
            memories = await memory_manager.get_stm(user_id)
            
            assert len(memories) == 2
            assert memories[0]["content"] == "Test 1"
            assert memories[1]["content"] == "Test 2"

@pytest.mark.asyncio
async def test_search_ltm(memory_manager):
    """Test searching long-term memory."""
    query = "test query"
    
    # Mock ChromaDB query
    with patch.object(memory_manager.collection, "query") as mock_query:
        mock_query.return_value = {
            "documents": [["Test content"]],
            "metadatas": [[{"type": "test"}]],
            "ids": [["ltm:1"]]
        }
        
        results = await memory_manager.search_ltm(query)
        
        assert len(results) == 1
        assert results[0]["content"] == "Test content"
        assert results[0]["metadata"] == {"type": "test"}
        assert results[0]["id"] == "ltm:1"

@pytest.mark.asyncio
async def test_cleanup_stm(memory_manager):
    """Test cleaning up short-term memory."""
    # Mock Redis operations
    with patch.object(memory_manager.db.redis, "keys") as mock_keys:
        with patch.object(memory_manager.db.redis, "delete") as mock_delete:
            mock_keys.return_value = ["stm:user1:1", "stm:user2:1"]
            
            await memory_manager.cleanup_stm()
            
            assert mock_delete.called
            assert mock_delete.call_args[0][0] == ["stm:user1:1", "stm:user2:1"] 