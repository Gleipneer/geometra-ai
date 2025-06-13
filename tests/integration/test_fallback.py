#!/usr/bin/env python3
"""
Integration tests for fallback system.

Tests the fallback mechanism from GPT-4 to GPT-3.5 when:
- GPT-4 is unavailable
- Rate limits are exceeded
- Response times are too high
- Errors occur
"""

import os
import time
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from ai.fallback import FallbackChain
from ai.prompt_builder import PromptBuilder
from memory.memory_manager import MemoryManager

# Test configuration
TEST_USER_ID = 'test_user_123'
TEST_MESSAGE = 'Test message for fallback verification'
TEST_CONTEXT = 'Test context for fallback verification'

@pytest.fixture
def memory_manager():
    """Create memory manager instance."""
    return MemoryManager(
        redis_url=os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/0'),
        chroma_url=os.getenv('TEST_CHROMA_URL', 'http://localhost:8000')
    )

@pytest.fixture
def prompt_builder():
    """Create prompt builder instance."""
    return PromptBuilder()

@pytest.fixture
def fallback_chain():
    """Create fallback chain instance."""
    return FallbackChain(
        max_retries=3,
        timeout=5,
        fallback_threshold=2.0
    )

class TestFallbackIntegration:
    """Integration tests for fallback system."""
    
    def test_gpt4_unavailable_fallback(self, fallback_chain, prompt_builder, memory_manager):
        """Test fallback when GPT-4 is unavailable."""
        # Mock GPT-4 to simulate unavailability
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.side_effect = Exception('GPT-4 unavailable')
            
            # Attempt request
            response = fallback_chain.process_request(
                user_id=TEST_USER_ID,
                message=TEST_MESSAGE,
                context=TEST_CONTEXT,
                prompt_builder=prompt_builder,
                memory_manager=memory_manager
            )
            
            # Verify fallback to GPT-3.5
            assert response.model == 'gpt-3.5-turbo'
            assert response.fallback_used
            assert response.original_error == 'GPT-4 unavailable'
    
    def test_rate_limit_fallback(self, fallback_chain, prompt_builder, memory_manager):
        """Test fallback when rate limit is exceeded."""
        # Mock GPT-4 to simulate rate limit
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.side_effect = Exception('Rate limit exceeded')
            
            # Attempt request
            response = fallback_chain.process_request(
                user_id=TEST_USER_ID,
                message=TEST_MESSAGE,
                context=TEST_CONTEXT,
                prompt_builder=prompt_builder,
                memory_manager=memory_manager
            )
            
            # Verify fallback to GPT-3.5
            assert response.model == 'gpt-3.5-turbo'
            assert response.fallback_used
            assert 'rate limit' in response.original_error.lower()
    
    def test_timeout_fallback(self, fallback_chain, prompt_builder, memory_manager):
        """Test fallback when response time exceeds threshold."""
        # Mock GPT-4 to simulate slow response
        with patch('openai.ChatCompletion.create') as mock_create:
            def slow_response(*args, **kwargs):
                time.sleep(3)  # Simulate slow response
                return MagicMock(
                    choices=[MagicMock(message=MagicMock(content='Slow response'))]
                )
            mock_create.side_effect = slow_response
            
            # Attempt request
            response = fallback_chain.process_request(
                user_id=TEST_USER_ID,
                message=TEST_MESSAGE,
                context=TEST_CONTEXT,
                prompt_builder=prompt_builder,
                memory_manager=memory_manager
            )
            
            # Verify fallback to GPT-3.5
            assert response.model == 'gpt-3.5-turbo'
            assert response.fallback_used
            assert 'timeout' in response.original_error.lower()
    
    def test_memory_integration(self, fallback_chain, prompt_builder, memory_manager):
        """Test fallback with memory integration."""
        # Store test memory
        memory_manager.store_memory(
            user_id=TEST_USER_ID,
            content='Test memory for fallback',
            metadata={'type': 'test'}
        )
        
        # Mock GPT-4 to simulate error
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.side_effect = Exception('GPT-4 error')
            
            # Attempt request
            response = fallback_chain.process_request(
                user_id=TEST_USER_ID,
                message=TEST_MESSAGE,
                context=TEST_CONTEXT,
                prompt_builder=prompt_builder,
                memory_manager=memory_manager
            )
            
            # Verify memory was used in fallback
            assert response.model == 'gpt-3.5-turbo'
            assert response.fallback_used
            assert 'memory' in response.context.lower()
    
    def test_retry_mechanism(self, fallback_chain, prompt_builder, memory_manager):
        """Test retry mechanism before fallback."""
        # Mock GPT-4 to fail twice then succeed
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.side_effect = [
                Exception('First failure'),
                Exception('Second failure'),
                MagicMock(choices=[MagicMock(message=MagicMock(content='Success'))])
            ]
            
            # Attempt request
            response = fallback_chain.process_request(
                user_id=TEST_USER_ID,
                message=TEST_MESSAGE,
                context=TEST_CONTEXT,
                prompt_builder=prompt_builder,
                memory_manager=memory_manager
            )
            
            # Verify retries and eventual success
            assert response.model == 'gpt-4'
            assert not response.fallback_used
            assert mock_create.call_count == 3
    
    def test_error_logging(self, fallback_chain, prompt_builder, memory_manager):
        """Test error logging during fallback."""
        # Mock GPT-4 to simulate error
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.side_effect = Exception('Test error')
            
            # Mock logger
            with patch('logging.error') as mock_logger:
                # Attempt request
                response = fallback_chain.process_request(
                    user_id=TEST_USER_ID,
                    message=TEST_MESSAGE,
                    context=TEST_CONTEXT,
                    prompt_builder=prompt_builder,
                    memory_manager=memory_manager
                )
                
                # Verify error was logged
                assert mock_logger.called
                assert 'Test error' in mock_logger.call_args[0][0]
    
    def test_performance_metrics(self, fallback_chain, prompt_builder, memory_manager):
        """Test performance metrics during fallback."""
        # Mock GPT-4 to simulate error
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.side_effect = Exception('Performance test error')
            
            # Attempt request
            start_time = time.time()
            response = fallback_chain.process_request(
                user_id=TEST_USER_ID,
                message=TEST_MESSAGE,
                context=TEST_CONTEXT,
                prompt_builder=prompt_builder,
                memory_manager=memory_manager
            )
            end_time = time.time()
            
            # Verify performance metrics
            assert response.model == 'gpt-3.5-turbo'
            assert response.fallback_used
            assert response.performance_metrics is not None
            assert 'total_time' in response.performance_metrics
            assert end_time - start_time < 10  # Should complete within 10 seconds 