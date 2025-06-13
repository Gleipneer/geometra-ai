"""Integration tests for AI system."""

import pytest
from src.ai.memory.memory_manager import MemoryManager
from src.ai.prompts.prompt_manager import PromptManager
from src.ai.fallback.fallback_manager import FallbackManager
from src.ai.chat.chat_manager import ChatManager
from src.db.manager import DatabaseManager
from unittest.mock import patch, Mock

@pytest.fixture
async def ai_system(db_manager, chroma_client):
    """Create complete AI system with all components."""
    memory_manager = MemoryManager(db_manager, chroma_client)
    prompt_manager = PromptManager()
    fallback_manager = FallbackManager()
    chat_manager = ChatManager(db_manager, memory_manager, fallback_manager, prompt_manager)
    
    return {
        "memory_manager": memory_manager,
        "prompt_manager": prompt_manager,
        "fallback_manager": fallback_manager,
        "chat_manager": chat_manager
    }

@pytest.mark.asyncio
async def test_complete_ai_flow(ai_system):
    """Test complete AI interaction flow."""
    # Get components
    memory_manager = ai_system["memory_manager"]
    prompt_manager = ai_system["prompt_manager"]
    chat_manager = ai_system["chat_manager"]
    
    # Test user
    user_id = "test_user"
    
    # 1. Store some long-term memory
    await memory_manager.store_ltm(
        "The user is interested in AI and machine learning",
        {"type": "interest", "topic": "AI"}
    )
    
    # 2. Process initial message
    response1 = await chat_manager.process_message(
        user_id,
        "Tell me about AI",
        {"context": "initial query"}
    )
    
    assert "response" in response1
    assert "memory" in response1
    assert "context" in response1
    
    # 3. Process follow-up message
    response2 = await chat_manager.process_message(
        user_id,
        "What about machine learning?",
        {"context": "follow-up"}
    )
    
    assert "response" in response2
    assert "memory" in response2
    assert "context" in response2
    
    # 4. Verify memory storage
    stm = await memory_manager.get_stm(user_id)
    assert len(stm) >= 2  # At least 2 user messages
    
    # 5. Verify chat history
    history = await chat_manager.get_chat_history(user_id)
    assert len(history) >= 2
    assert "message" in history[0]
    assert "response" in history[0]
    
    # 6. Analyze chat
    analysis = await chat_manager.analyze_chat(user_id)
    assert "total_messages" in analysis
    assert "avg_response_length" in analysis
    assert "top_topics" in analysis

@pytest.mark.asyncio
async def test_fallback_handling(ai_system):
    """Test fallback handling in AI system."""
    chat_manager = ai_system["chat_manager"]
    user_id = "test_user"
    
    # Mock primary model failure and secondary success
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Simulate rate limit error
        mock_instance.chat.completions.create.side_effect = [
            Exception("Rate limit exceeded"),
            Mock(choices=[Mock(message=Mock(content="Fallback response"))])
        ]
        
        response = await chat_manager.process_message(
            user_id,
            "Test message"
        )
        
        assert "response" in response
        assert response["response"] == "Fallback response"

@pytest.mark.asyncio
async def test_memory_integration(ai_system):
    """Test memory integration in AI system."""
    memory_manager = ai_system["memory_manager"]
    chat_manager = ai_system["chat_manager"]
    user_id = "test_user"
    
    # Store relevant memory
    await memory_manager.store_ltm(
        "The user's name is John and they like programming",
        {"type": "user_info", "name": "John"}
    )
    
    # Process message that should use memory
    response = await chat_manager.process_message(
        user_id,
        "What do you know about me?",
        {"context": "memory test"}
    )
    
    assert "response" in response
    assert "memory" in response
    assert len(response["memory"]["long_term"]) > 0

@pytest.mark.asyncio
async def test_prompt_integration(ai_system):
    """Test prompt integration in AI system."""
    prompt_manager = ai_system["prompt_manager"]
    chat_manager = ai_system["chat_manager"]
    user_id = "test_user"
    
    # Process message with custom context
    response = await chat_manager.process_message(
        user_id,
        "Test message",
        {
            "context": "test context",
            "temperature": 0.7,
            "max_tokens": 100
        }
    )
    
    assert "response" in response
    assert "memory" in response
    assert "context" in response 