"""
Evaluation metrics implementation for Geometra AI.
Handles calculation of various performance metrics.
"""

from typing import List, Dict
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def calculate_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    """Calculate classification metrics.
    
    Args:
        y_true: List of true labels
        y_pred: List of predicted labels
        
    Returns:
        Dictionary of metric scores
    """
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'f1_score': f1_score(y_true, y_pred, average='weighted')
    }

def calculate_embedding_similarity(emb1: List[float], emb2: List[float]) -> float:
    """Calculate cosine similarity between embeddings.
    
    Args:
        emb1: First embedding vector
        emb2: Second embedding vector
        
    Returns:
        Similarity score
    """
    vec1 = np.array(emb1)
    vec2 = np.array(emb2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def calculate_response_time(start_time: float, end_time: float) -> float:
    """Calculate response time in seconds.
    
    Args:
        start_time: Start timestamp
        end_time: End timestamp
        
    Returns:
        Response time in seconds
    """
    return end_time - start_time

def calculate_token_usage(prompt_tokens: int, completion_tokens: int) -> Dict[str, int]:
    """Calculate token usage statistics.
    
    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        
    Returns:
        Dictionary of token usage
    """
    return {
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': prompt_tokens + completion_tokens
    } 