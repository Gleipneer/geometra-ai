"""Unit tests for PromptManager."""

import pytest
from unittest.mock import Mock, patch
from src.ai.prompts.prompt_manager import PromptManager

@pytest.fixture
def prompt_manager():
    """Create PromptManager instance for testing."""
    return PromptManager()

def test_init(prompt_manager):
    """Test initialization."""
    assert prompt_manager.env is not None
    assert prompt_manager.config is not None
    assert prompt_manager.templates is not None
    assert "system" in prompt_manager.templates
    assert "user" in prompt_manager.templates
    assert "assistant" in prompt_manager.templates

def test_get_prompt(prompt_manager):
    """Test getting rendered prompt."""
    template_name = "user"
    context = {
        "message": "Test message",
        "memory": [{"content": "Test memory"}]
    }
    
    prompt = prompt_manager.get_prompt(template_name, context)
    
    assert isinstance(prompt, str)
    assert "Test message" in prompt
    assert "Test memory" in prompt

def test_get_system_prompt(prompt_manager):
    """Test getting system prompt."""
    context = {
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    prompt = prompt_manager.get_system_prompt(context)
    
    assert isinstance(prompt, str)
    assert "temperature" in prompt
    assert "max_tokens" in prompt

def test_get_user_prompt(prompt_manager):
    """Test getting user prompt."""
    message = "Test message"
    context = {
        "memory": [{"content": "Test memory"}],
        "timestamp": "2024-01-01T00:00:00"
    }
    
    prompt = prompt_manager.get_user_prompt(message, context)
    
    assert isinstance(prompt, str)
    assert message in prompt
    assert "Test memory" in prompt
    assert "timestamp" in prompt

def test_get_assistant_prompt(prompt_manager):
    """Test getting assistant prompt."""
    response = "Test response"
    context = {
        "memory": [{"content": "Test memory"}],
        "timestamp": "2024-01-01T00:00:00"
    }
    
    prompt = prompt_manager.get_assistant_prompt(response, context)
    
    assert isinstance(prompt, str)
    assert response in prompt
    assert "Test memory" in prompt
    assert "timestamp" in prompt

def test_get_chat_context(prompt_manager):
    """Test getting chat context."""
    user_id = "test_user"
    message = "Test message"
    memory = {
        "short_term": [{"content": "Recent memory"}],
        "long_term": [{"content": "Long-term memory"}]
    }
    
    context = prompt_manager.get_chat_context(user_id, message, memory)
    
    assert isinstance(context, dict)
    assert context["user_id"] == user_id
    assert context["message"] == message
    assert context["memory"] == memory
    assert "config" in context

def test_missing_template(prompt_manager):
    """Test handling of missing template."""
    with pytest.raises(ValueError) as exc_info:
        prompt_manager.get_prompt("nonexistent", {})
    
    assert "Template nonexistent not found" in str(exc_info.value) 