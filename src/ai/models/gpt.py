"""
GPT model implementation for Geometra AI.
Handles interactions with OpenAI's GPT models.
"""

from typing import Dict, List, Optional
import openai

class GPTModel:
    """GPT model handler for Geometra AI."""
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """Initialize GPT model.
        
        Args:
            model_name: Name of the GPT model to use
            temperature: Sampling temperature (0-1)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.client = openai.AsyncOpenAI()
    
    async def get_completion(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        max_tokens: int = 2000
    ) -> str:
        """Get completion from GPT model.
        
        Args:
            prompt: Input prompt
            context: Optional context dictionary
            max_tokens: Maximum tokens in response
            
        Returns:
            Model's response text
        """
        messages = [
            {"role": "system", "content": context.get("system", "You are a helpful AI assistant.")},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content 