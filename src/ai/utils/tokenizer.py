"""
Tokenizer implementation for Geometra AI.
Handles text tokenization and token counting.
"""

from typing import List, Dict
import tiktoken

class Tokenizer:
    """Tokenizer for Geometra AI."""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize tokenizer.
        
        Args:
            model_name: Name of the model to use for tokenization
        """
        self.encoding = tiktoken.encoding_for_model(model_name)
    
    def encode(self, text: str) -> List[int]:
        """Encode text to tokens.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of token IDs
        """
        return self.encoding.encode(text)
    
    def decode(self, tokens: List[int]) -> str:
        """Decode tokens to text.
        
        Args:
            tokens: List of token IDs
            
        Returns:
            Decoded text
        """
        return self.encoding.decode(tokens)
    
    def count_tokens(self, text: str) -> int:
        """Count number of tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        return len(self.encode(text))
    
    def truncate(self, text: str, max_tokens: int) -> str:
        """Truncate text to maximum number of tokens.
        
        Args:
            text: Input text
            max_tokens: Maximum number of tokens
            
        Returns:
            Truncated text
        """
        tokens = self.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return self.decode(tokens[:max_tokens]) 