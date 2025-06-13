"""
Fallback manager implementation for Geometra AI.
Handles fallback logic between different AI models.
"""

from typing import Dict, Optional
import asyncio
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

class FallbackManager:
    """Fallback manager for Geometra AI."""
    
    def __init__(
        self,
        primary_model: str = "gpt-4",
        secondary_model: str = "gpt-3.5-turbo",
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        """Initialize fallback manager.
        
        Args:
            primary_model: Primary model name
            secondary_model: Secondary model name
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        self.primary_model = primary_model
        self.secondary_model = secondary_model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = AsyncOpenAI()
    
    async def get_completion(
        self,
        prompt: str,
        context: Optional[Dict] = None
    ) -> str:
        """Get completion from AI model with fallback.
        
        Args:
            prompt: Input prompt
            context: Optional context dictionary
            
        Returns:
            Model's response text
        """
        # Try primary model first
        try:
            return await self._get_completion(
                self.primary_model,
                prompt,
                context
            )
        except Exception as e:
            if not self._should_fallback(e):
                raise
            
            # Try secondary model
            try:
                return await self._get_completion(
                    self.secondary_model,
                    prompt,
                    context
                )
            except Exception as e2:
                raise Exception("Both models failed") from e2
    
    async def _get_completion(
        self,
        model: str,
        prompt: str,
        context: Dict
    ) -> str:
        """Get completion from a specific model.
        
        Args:
            model: Model name
            prompt: Input prompt
            context: Context dictionary
            
        Returns:
            Model's response text
        """
        messages = [
            {"role": "system", "content": context.get("system", "You are a helpful AI assistant.")},
            {"role": "user", "content": prompt}
        ]
        
        for attempt in range(self.max_retries):
            try:
                response: ChatCompletion = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=context.get("temperature", 0.7),
                    max_tokens=context.get("max_tokens", 2000)
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
    
    def _should_fallback(self, error: Exception) -> bool:
        """Determine if fallback should be triggered.
        
        Args:
            error: Exception to check
            
        Returns:
            True if fallback should be triggered
        """
        error_str = str(error).lower()
        return any(x in error_str for x in [
            "rate limit",
            "timeout",
            "overloaded",
            "capacity"
        ])
    
    def get_fallback_strategy(self, error: Exception) -> Dict:
        """Get fallback strategy for error.
        
        Args:
            error: Exception to get strategy for
            
        Returns:
            Fallback strategy dictionary
        """
        error_str = str(error).lower()
        
        if "rate limit" in error_str:
            return {
                "action": "wait_and_retry",
                "wait_time": 60
            }
        elif "timeout" in error_str:
            return {
                "action": "immediate_fallback"
            }
        else:
            return {
                "action": "retry_with_backoff",
                "max_wait": 30
            } 