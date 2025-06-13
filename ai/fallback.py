# ⚠️ Auto-generated from test fallback: verify before use

"""
Fallback chain for handling GPT-4 failures and falling back to GPT-3.5.
Handles rate limits, timeouts, and other errors with retry mechanism.
"""

import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
import openai

@dataclass
class FallbackResponse:
    """Response from fallback chain."""
    model: str
    content: str
    fallback_used: bool
    original_error: Optional[str] = None
    performance_metrics: Optional[Dict[str, float]] = None
    context: Optional[str] = None

class FallbackChain:
    """Handles fallback from GPT-4 to GPT-3.5 with retries."""
    
    def __init__(
        self,
        max_retries: int = 3,
        timeout: int = 5,
        fallback_threshold: float = 2.0
    ):
        """Initialize fallback chain.
        
        Args:
            max_retries: Maximum number of retries before fallback
            timeout: Timeout in seconds for each request
            fallback_threshold: Time threshold for fallback in seconds
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.fallback_threshold = fallback_threshold
        self.logger = logging.getLogger(__name__)
    
    def process_request(
        self,
        user_id: str,
        message: str,
        context: str,
        prompt_builder: Any,
        memory_manager: Any
    ) -> FallbackResponse:
        """Process request with fallback mechanism.
        
        Args:
            user_id: User identifier
            message: User message
            context: Conversation context
            prompt_builder: Prompt builder instance
            memory_manager: Memory manager instance
            
        Returns:
            FallbackResponse with model, content and fallback info
        """
        start_time = time.time()
        retries = 0
        
        while retries < self.max_retries:
            try:
                # Try GPT-4 first
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=prompt_builder.build_messages(message, context),
                    timeout=self.timeout
                )
                
                # Check response time
                elapsed = time.time() - start_time
                if elapsed > self.fallback_threshold:
                    raise TimeoutError(f"Response time {elapsed:.2f}s exceeds threshold")
                
                return FallbackResponse(
                    model="gpt-4",
                    content=response.choices[0].message.content,
                    fallback_used=False,
                    performance_metrics={"total_time": elapsed}
                )
                
            except Exception as e:
                retries += 1
                self.logger.error(f"GPT-4 attempt {retries} failed: {str(e)}")
                
                if retries == self.max_retries:
                    # Fall back to GPT-3.5
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=prompt_builder.build_messages(
                                message,
                                context,
                                memory_manager.retrieve_context(user_id)
                            ),
                            timeout=self.timeout
                        )
                        
                        return FallbackResponse(
                            model="gpt-3.5-turbo",
                            content=response.choices[0].message.content,
                            fallback_used=True,
                            original_error=str(e),
                            performance_metrics={"total_time": time.time() - start_time},
                            context=context
                        )
                        
                    except Exception as fallback_error:
                        self.logger.error(f"GPT-3.5 fallback failed: {str(fallback_error)}")
                        raise 