"""
Embedding model implementation for Geometra AI.
Handles text embeddings using OpenAI's embedding models.
"""

from typing import List
import openai
import numpy as np

class EmbeddingModel:
    """Embedding model handler for Geometra AI."""
    
    def __init__(self, model_name: str = "text-embedding-ada-002"):
        """Initialize embedding model.
        
        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name
        self.client = openai.AsyncOpenAI()
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        response = await self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding lists
        """
        response = await self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return [data.embedding for data in response.data]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) 