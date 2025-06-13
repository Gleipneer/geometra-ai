#!/usr/bin/env python3
"""
Test cases for the model router implementation.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from ai.model_router import route_model, get_completion, GPT4OMNI, GPT35

# Test data
TEST_PROMPT = "This is a test prompt"
LONG_PROMPT = "test " * 2000  # Creates a long prompt

@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses."""
    with patch('openai.ChatCompletion.create') as mock:
        mock.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        yield mock

class TestModelRouter:
    """Test cases for model routing functionality."""
    
    def test_route_model_summarization(self):
        """Test routing for summarization intent."""
        context = {"intent": "summarization", "token_length": 100}
        model = route_model(TEST_PROMPT, context)
        assert model == GPT35
        
    def test_route_model_long_prompt(self):
        """Test routing for long prompts."""
        context = {"intent": "general_dialogue", "token_length": 7000}
        model = route_model(TEST_PROMPT, context)
        assert model == GPT35
        
    def test_route_model_complex_task(self):
        """Test routing for complex tasks."""
        context = {"intent": "complex_analysis", "token_length": 100}
        model = route_model(TEST_PROMPT, context)
        assert model == GPT4OMNI
        
    def test_route_model_fallback(self):
        """Test fallback to GPT-3.5 on error."""
        context = {"intent": None, "token_length": None}
        model = route_model(TEST_PROMPT, context)
        assert model == GPT35

class TestGetCompletion:
    """Test cases for completion functionality."""
    
    def test_get_completion_success(self, mock_openai):
        """Test successful completion request."""
        context = {"intent": "general_dialogue", "token_length": 100}
        response = get_completion(TEST_PROMPT, context)
        assert response == "Test response"
        mock_openai.assert_called_once()
        
    def test_get_completion_error(self, mock_openai):
        """Test error handling in completion request."""
        mock_openai.side_effect = Exception("API Error")
        context = {"intent": "general_dialogue", "token_length": 100}
        response = get_completion(TEST_PROMPT, context)
        assert "❌ Model call failed" in response
        
    def test_get_completion_model_selection(self, mock_openai):
        """Test correct model selection for different intents."""
        # Test summarization
        context = {"intent": "summarization", "token_length": 100}
        get_completion(TEST_PROMPT, context)
        mock_openai.assert_called_with(
            model=GPT35,
            messages=[{"role": "user", "content": TEST_PROMPT}]
        )
        
        # Test complex task
        context = {"intent": "complex_analysis", "token_length": 100}
        get_completion(TEST_PROMPT, context)
        mock_openai.assert_called_with(
            model=GPT4OMNI,
            messages=[{"role": "user", "content": TEST_PROMPT}]
        ) 