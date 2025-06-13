"""OpenAI embeddings utility."""

from openai import OpenAI
from typing import List

def get_embeddings(texts: List[str], api_key: str) -> List[List[float]]:
    """Get embeddings for a list of texts using OpenAI.
    
    Args:
        texts: List of texts to embed
        api_key: OpenAI API key
        
    Returns:
        List of embedding vectors
    """
    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-ada-002"
    )
    return [data.embedding for data in response.data] 