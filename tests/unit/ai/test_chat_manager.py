"""Unit tests for ChatManager."""

import pytest
from unittest.mock import Mock, patch
from src.ai.chat.chat_manager import ChatManager
from src.ai.memory.memory_manager import MemoryManager
from src.ai.fallback.fallback_manager import FallbackManager
from src.ai.prompts.prompt_manager import PromptManager

@pytest.fixture
def chat_manager(db_manager, memory_manager, fallback_manager, prompt_manager):
    """Create ChatManager instance for testing."""
    return ChatManager(db_manager, memory_manager, fallback_manager, prompt_manager)

@pytest.mark.asyncio
async def test_process_message(chat_manager):
    """Test processing a chat message."""
    user_id = "test_user"
    message = "Hello, AI!"
    context = {"test": "context"}
    
    # Mock dependencies
    with patch.object(chat_manager.memory_manager, "search_ltm") as mock_search:
        with patch.object(chat_manager.memory_manager, "store_stm") as mock_store:
            with patch.object(chat_manager.fallback_manager, "get_completion") as mock_completion:
                mock_search.return_value = [{"content": "test memory", "metadata": {}}]
                mock_completion.return_value = "AI response"
                
                response = await chat_manager.process_message(user_id, message, context)
                
                assert response["response"] == "AI response"
                assert "memory" in response
                assert "context" in response
                
                # Verify memory operations
                assert mock_search.called
                assert mock_store.call_count == 2  # Store both user message and AI response

@pytest.mark.asyncio
async def test_get_chat_history(chat_manager):
    """Test getting chat history."""
    user_id = "test_user"
    
    # Mock Redis get
    with patch.object(chat_manager.db.redis, "keys") as mock_keys:
        with patch.object(chat_manager.db.redis, "mget") as mock_mget:
            mock_keys.return_value = ["chat:test_user:1", "chat:test_user:2"]
            mock_mget.return_value = [
                '{"message": "Hello", "response": "Hi", "timestamp": "2024-01-01T00:00:00"}',
                '{"message": "How are you?", "response": "Good", "timestamp": "2024-01-01T00:01:00"}'
            ]
            
            history = await chat_manager.get_chat_history(user_id)
            
            assert len(history) == 2
            assert history[0]["message"] == "Hello"
            assert history[0]["response"] == "Hi"
            assert history[1]["message"] == "How are you?"
            assert history[1]["response"] == "Good"

@pytest.mark.asyncio
async def test_analyze_chat(chat_manager):
    """Test chat analysis."""
    user_id = "test_user"
    
    # Mock chat history
    with patch.object(chat_manager, "get_chat_history") as mock_history:
        mock_history.return_value = [
            {"message": "Hello", "response": "Hi there!", "timestamp": "2024-01-01T00:00:00"},
            {"message": "How are you?", "response": "I'm good, thanks!", "timestamp": "2024-01-01T00:01:00"}
        ]
        
        analysis = await chat_manager.analyze_chat(user_id)
        
        assert "total_messages" in analysis
        assert "avg_response_length" in analysis
        assert "top_topics" in analysis
        assert analysis["total_messages"] == 2
        assert analysis["avg_response_length"] > 0
        assert isinstance(analysis["top_topics"], dict) 