"""Unit tests for FallbackManager."""

import pytest
from unittest.mock import Mock, patch
from src.ai.fallback.fallback_manager import FallbackManager

@pytest.fixture
def fallback_manager():
    """Create FallbackManager instance for testing."""
    return FallbackManager()

@pytest.mark.asyncio
async def test_get_completion_primary_success(fallback_manager):
    """Test successful completion from primary model."""
    prompt = "Test prompt"
    context = {"system": "Test system", "temperature": 0.7}
    
    # Mock OpenAI client
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        mock_instance.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Primary response"))]
        )
        
        response = await fallback_manager.get_completion(prompt, context)
        
        assert response == "Primary response"
        mock_instance.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_fallback(fallback_manager):
    """Test fallback to secondary model."""
    prompt = "Test prompt"
    context = {"system": "Test system", "temperature": 0.7}
    
    # Mock OpenAI client
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Simulate primary model failure
        mock_instance.chat.completions.create.side_effect = [
            Exception("Rate limit exceeded"),
            Mock(choices=[Mock(message=Mock(content="Fallback response"))])
        ]
        
        response = await fallback_manager.get_completion(prompt, context)
        
        assert response == "Fallback response"
        assert mock_instance.chat.completions.create.call_count == 2

@pytest.mark.asyncio
async def test_get_completion_retry(fallback_manager):
    """Test retry logic."""
    prompt = "Test prompt"
    context = {"system": "Test system", "temperature": 0.7}
    
    # Mock OpenAI client
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Simulate temporary failure then success
        mock_instance.chat.completions.create.side_effect = [
            Exception("Timeout"),
            Mock(choices=[Mock(message=Mock(content="Retry response"))])
        ]
        
        response = await fallback_manager.get_completion(prompt, context)
        
        assert response == "Retry response"
        assert mock_instance.chat.completions.create.call_count == 2

@pytest.mark.asyncio
async def test_get_completion_max_retries(fallback_manager):
    """Test maximum retries exceeded."""
    prompt = "Test prompt"
    context = {"system": "Test system", "temperature": 0.7}
    
    # Mock OpenAI client
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Simulate consistent failures
        mock_instance.chat.completions.create.side_effect = [
            Exception("Timeout"),
            Exception("Timeout"),
            Exception("Timeout"),
            Exception("Timeout")
        ]
        
        with pytest.raises(Exception) as exc_info:
            await fallback_manager.get_completion(prompt, context)
        
        assert "Both models failed" in str(exc_info.value)
        assert mock_instance.chat.completions.create.call_count == 4

def test_should_fallback(fallback_manager):
    """Test fallback decision logic."""
    # Test rate limit
    assert fallback_manager._should_fallback(Exception("Rate limit exceeded"))
    
    # Test timeout
    assert fallback_manager._should_fallback(Exception("Request timeout"))
    
    # Test other error
    assert not fallback_manager._should_fallback(Exception("Other error"))

def test_get_fallback_strategy(fallback_manager):
    """Test fallback strategy selection."""
    # Test rate limit strategy
    strategy = fallback_manager.get_fallback_strategy(Exception("Rate limit exceeded"))
    assert strategy["action"] == "wait_and_retry"
    assert strategy["wait_time"] == 60
    
    # Test timeout strategy
    strategy = fallback_manager.get_fallback_strategy(Exception("Request timeout"))
    assert strategy["action"] == "immediate_fallback"
    
    # Test default strategy
    strategy = fallback_manager.get_fallback_strategy(Exception("Other error"))
    assert strategy["action"] == "retry_with_backoff"
    assert strategy["max_wait"] == 30 