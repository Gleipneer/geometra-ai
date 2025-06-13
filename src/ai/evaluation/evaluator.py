"""
Evaluator implementation for Geometra AI.
Handles model evaluation and performance analysis.
"""

from typing import List, Dict, Any
import time
from .metrics import (
    calculate_metrics,
    calculate_embedding_similarity,
    calculate_response_time,
    calculate_token_usage
)

class Evaluator:
    """Evaluator for Geometra AI."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.metrics_history = []
    
    def evaluate_classification(
        self,
        y_true: List[int],
        y_pred: List[int]
    ) -> Dict[str, float]:
        """Evaluate classification performance.
        
        Args:
            y_true: List of true labels
            y_pred: List of predicted labels
            
        Returns:
            Dictionary of evaluation metrics
        """
        metrics = calculate_metrics(y_true, y_pred)
        self.metrics_history.append(metrics)
        return metrics
    
    def evaluate_embeddings(
        self,
        reference_emb: List[float],
        test_emb: List[float]
    ) -> float:
        """Evaluate embedding similarity.
        
        Args:
            reference_emb: Reference embedding
            test_emb: Test embedding
            
        Returns:
            Similarity score
        """
        return calculate_embedding_similarity(reference_emb, test_emb)
    
    def evaluate_response(
        self,
        start_time: float,
        end_time: float,
        prompt_tokens: int,
        completion_tokens: int
    ) -> Dict[str, Any]:
        """Evaluate response performance.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            
        Returns:
            Dictionary of performance metrics
        """
        return {
            'response_time': calculate_response_time(start_time, end_time),
            'token_usage': calculate_token_usage(prompt_tokens, completion_tokens)
        }
    
    def get_metrics_history(self) -> List[Dict[str, float]]:
        """Get history of evaluation metrics.
        
        Returns:
            List of metric dictionaries
        """
        return self.metrics_history
    
    def clear_history(self):
        """Clear metrics history."""
        self.metrics_history = [] 