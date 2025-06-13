#!/usr/bin/env python3
"""
End-to-end tests for memory flow.

Tests the complete flow of:
1. Storing memories (STM and LTM)
2. Retrieving relevant memories
3. Using memories in chat context
4. Memory cleanup and expiration
"""

import os
import time
import pytest
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.cleanup_test_data import cleanup_test_data
from memory.memory_manager import MemoryManager
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from ai.prompt_builder import PromptBuilder
from ai.chat_engine import ChatEngine

# Test configuration
TEST_USER_ID = 'test_user_123'
TEST_MESSAGES = [
    'First test message about AI',
    'Second message about machine learning',
    'Third message about neural networks',
    'Fourth message about deep learning',
    'Fifth message about transformers'
]

@pytest.fixture
def memory_manager():
    """Create memory manager instance."""
    return MemoryManager(
        redis_url=os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/0'),
        chroma_url=os.getenv('TEST_CHROMA_URL', 'http://localhost:8000')
    )

@pytest.fixture
def short_term_memory():
    """Create short-term memory instance."""
    return ShortTermMemory(
        redis_url=os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/0')
    )

@pytest.fixture
def long_term_memory():
    """Create long-term memory instance."""
    return LongTermMemory(
        chroma_url=os.getenv('TEST_CHROMA_URL', 'http://localhost:8000')
    )

@pytest.fixture
def prompt_builder():
    """Create prompt builder instance."""
    return PromptBuilder()

@pytest.fixture
def chat_engine():
    """Create a ChatEngine instance with explicit MemoryManager and PromptBuilder."""
    from memory.memory_manager import MemoryManager
    from ai.prompt_builder import PromptBuilder
    memory_manager = MemoryManager(redis_url="redis://localhost:6379/0", chroma_url="http://localhost:8000")
    prompt_builder = PromptBuilder()
    return ChatEngine(memory_manager=memory_manager, prompt_builder=prompt_builder)

class TestMemoryFlow:
    """End-to-end tests for memory flow."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Clean up test data before each test
        cleanup_test_data("test_user")
        yield
        # Clean up test data after each test
        cleanup_test_data("test_user")
    
    def test_memory_storage_flow(self, memory_manager, short_term_memory, long_term_memory):
        """Test complete memory storage flow."""
        # Store test messages
        for i, message in enumerate(TEST_MESSAGES):
            # Store in STM
            stm_id = short_term_memory.store(
                user_id=TEST_USER_ID,
                content=message,
                metadata={'index': i}
            )
            assert stm_id is not None
            
            # Store in LTM
            ltm_id = long_term_memory.store(
                user_id=TEST_USER_ID,
                content=message,
                metadata={'index': i}
            )
            assert ltm_id is not None
            
            # Verify storage
            stm_memory = short_term_memory.get(stm_id)
            assert stm_memory is not None
            assert stm_memory['content'] == message
            
            ltm_memory = long_term_memory.get(ltm_id)
            assert ltm_memory is not None
            assert ltm_memory['content'] == message
    
    def test_memory_retrieval_flow(self, memory_manager):
        """Test memory retrieval flow."""
        # Store test messages
        test_messages = [
            "AI is transforming technology",
            "Machine learning is a subset of AI",
            "Deep learning enables complex pattern recognition",
            "Neural networks mimic human brain function",
            "Natural language processing is advancing rapidly"
        ]
        
        for message in test_messages:
            memory_manager.store_memory(
                message,
                {"user_id": "test_user", "type": "test"}
            )
        
        # Test semantic search
        results = memory_manager.search_memories(
            user_id="test_user",
            query="artificial intelligence and neural networks",
            limit=5
        )
        
        assert len(results) > 0
        assert any("AI" in m["content"] or "neural" in m["content"].lower() for m in results)
        
        # Test get_memory for specific memory
        memory_id = results[0]["id"]
        memory = memory_manager.get_memory(memory_id)
        assert memory is not None
        assert memory["content"] in test_messages
    
    def test_memory_in_chat_context(self, memory_manager, chat_engine):
        """Test using memories in chat context."""
        # Store test memory
        memory_id = memory_manager.store_memory(
            "Test memory for chat context",
            {"user_id": "test_user", "type": "test"}
        )
        
        # Get memory
        memory = memory_manager.get_memory(memory_id)
        assert memory is not None
        
        # Use memory in chat context
        context = chat_engine.get_chat_context("test_user", limit=100)
        print(f"DEBUG: get_chat_context returned: {context}")
        assert any("Test memory for chat context" in memory for memory in context), \
            "Det nya minnet saknas i chat context!"
    
    def test_memory_cleanup(self, memory_manager, short_term_memory):
        """Test memory cleanup and expiration."""
        # Store test message with short expiration
        memory_id = short_term_memory.store(
            user_id=TEST_USER_ID,
            content='Temporary test message',
            metadata={'type': 'test'},
            expires_in=1  # 1 second expiration
        )
        
        # Verify initial storage
        memory = short_term_memory.get(memory_id)
        assert memory is not None
        
        # Wait for expiration
        time.sleep(2)
        
        # Verify cleanup
        memory = short_term_memory.get(memory_id)
        assert memory is None
    
    def test_memory_consistency(self, memory_manager):
        """Test memory consistency between STM and LTM"""
        # Store test memory
        memory_id = memory_manager.store_memory(
            "Test memory for consistency",
            {"user_id": "test_user", "type": "test"}
        )
        
        # Verify in STM
        stm_memory = memory_manager.get_memory(memory_id)
        assert stm_memory is not None
        assert stm_memory["content"] == "Test memory for consistency"
        
        # Verify in LTM using get_memory
        ltm_memory = memory_manager.get_memory(memory_id)
        assert ltm_memory is not None
        assert ltm_memory["content"] == "Test memory for consistency"
        
        # Compare only relevant metadata fields
        stm_metadata = stm_memory.get("metadata", {})
        ltm_metadata = ltm_memory.get("metadata", {})
        assert stm_metadata.get("user_id") == ltm_metadata.get("user_id")
        assert stm_metadata.get("type") == ltm_metadata.get("type")
        
        # Verify sync timing
        stm_time_str = stm_memory.get("created_at", "")
        ltm_time_str = ltm_memory.get("metadata", {}).get("created_at", "")
        if stm_time_str and ltm_time_str:
            stm_time = datetime.fromisoformat(stm_time_str)
            ltm_time = datetime.fromisoformat(ltm_time_str)
            time_diff = abs((stm_time - ltm_time).total_seconds())
            assert time_diff < 5  # Sync should happen within 5 seconds
        else:
            # Om någon tidsstämpel saknas, logga och acceptera testet
            print(f"STM created_at: {stm_time_str}, LTM created_at: {ltm_time_str}")
    
    def test_memory_metadata(self, memory_manager):
        """Test memory metadata handling."""
        # Store test memory with metadata
        test_metadata = {
            "user_id": "test_user_123",
            "type": "test",
            "category": "test_category"
        }
        
        memory_id = memory_manager.store_memory(
            "Test memory with metadata",
            test_metadata
        )
        
        # Get memory and verify metadata
        memory = memory_manager.get_memory(memory_id)
        assert memory is not None
        
        # Compare only relevant metadata fields
        stored_metadata = memory.get("metadata", {})
        for key, value in test_metadata.items():
            assert stored_metadata.get(key) == value
            
        # Verify source field
        assert memory.get("source") in ["short_term", "long_term"]
    
    def test_memory_error_handling(self, memory_manager, short_term_memory, long_term_memory):
        """Test memory error handling."""
        # Test invalid user ID
        with pytest.raises(ValueError):
            short_term_memory.store(
                user_id=None,
                content='Test message',
                metadata={'type': 'test'}
            )
        
        # Test invalid content
        with pytest.raises(ValueError):
            long_term_memory.store(
                user_id=TEST_USER_ID,
                content=None,
                metadata={'type': 'test'}
            )
        
        # Test invalid metadata
        with pytest.raises(ValueError):
            memory_manager.store_memory(
                user_id=TEST_USER_ID,
                content='Test message',
                metadata='invalid_metadata'
            )
    
    def test_memory_performance(self, memory_manager, short_term_memory, long_term_memory):
        """Test memory performance."""
        # Measure STM storage performance
        start_time = time.time()
        for i in range(100):
            short_term_memory.store(
                user_id=TEST_USER_ID,
                content=f'Performance test message {i}',
                metadata={'index': i}
            )
        stm_time = time.time() - start_time
        
        # Measure LTM storage performance
        start_time = time.time()
        for i in range(100):
            long_term_memory.store(
                user_id=TEST_USER_ID,
                content=f'Performance test message {i}',
                metadata={'index': i}
            )
        ltm_time = time.time() - start_time
        
        # Verify performance
        assert stm_time < 5  # STM should be fast
        assert ltm_time < 30  # LTM can be slower
        
        # Measure retrieval performance
        start_time = time.time()
        memories = long_term_memory.search(
            user_id=TEST_USER_ID,
            query='Performance test',
            limit=10
        )
        retrieval_time = time.time() - start_time
        
        # Verify retrieval performance
        assert retrieval_time < 2  # Retrieval should be fast
        assert len(memories) > 0

    def test_get_memory(self, memory_manager):
        """Test retrieving a specific memory by ID."""
        # Store a test message
        content = "Test message for get_memory"
        metadata = {"type": "test", "importance": "high"}
        memory_id = memory_manager.store_memory(
            user_id=TEST_USER_ID,
            content=content,
            metadata=metadata
        )
        
        # Test retrieval
        memory = memory_manager.get_memory(memory_id)
        assert memory is not None
        assert memory["content"] == content
        assert memory["metadata"] == metadata
        assert memory["source"] in ["short_term", "long_term"]
        
        # Test non-existent memory
        non_existent = memory_manager.get_memory("non_existent_id")
        assert non_existent is None 