"""
Dataset implementation for Geometra AI.
Handles training data management and preprocessing.
"""

from typing import List, Dict, Any, Optional
import json
import random
from pathlib import Path

class Dataset:
    """Dataset handler for Geometra AI."""
    
    def __init__(self, data: List[Dict[str, Any]] = None):
        """Initialize dataset.
        
        Args:
            data: Optional initial data
        """
        self.data = data or []
        self.metadata = {
            'size': len(self.data),
            'created_at': None,
            'updated_at': None
        }
    
    def add_example(self, example: Dict[str, Any]):
        """Add a training example.
        
        Args:
            example: Training example dictionary
        """
        self.data.append(example)
        self.metadata['size'] = len(self.data)
        self.metadata['updated_at'] = None  # Will be set on save
    
    def add_examples(self, examples: List[Dict[str, Any]]):
        """Add multiple training examples.
        
        Args:
            examples: List of training example dictionaries
        """
        self.data.extend(examples)
        self.metadata['size'] = len(self.data)
        self.metadata['updated_at'] = None  # Will be set on save
    
    def get_example(self, index: int) -> Dict[str, Any]:
        """Get a training example.
        
        Args:
            index: Example index
            
        Returns:
            Training example dictionary
        """
        return self.data[index]
    
    def get_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """Get a random batch of examples.
        
        Args:
            batch_size: Size of batch
            
        Returns:
            List of training example dictionaries
        """
        return random.sample(self.data, min(batch_size, len(self.data)))
    
    def split(self, train_ratio: float = 0.8) -> tuple:
        """Split dataset into train and validation sets.
        
        Args:
            train_ratio: Ratio of training data
            
        Returns:
            Tuple of (train_dataset, val_dataset)
        """
        random.shuffle(self.data)
        split_idx = int(len(self.data) * train_ratio)
        
        train_data = self.data[:split_idx]
        val_data = self.data[split_idx:]
        
        return Dataset(train_data), Dataset(val_data)
    
    def save(self, path: str):
        """Save dataset to file.
        
        Args:
            path: Path to save dataset
        """
        data = {
            'data': self.data,
            'metadata': self.metadata
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'Dataset':
        """Load dataset from file.
        
        Args:
            path: Path to load dataset from
            
        Returns:
            Loaded dataset
        """
        with open(path, 'r') as f:
            data = json.load(f)
        
        dataset = cls(data['data'])
        dataset.metadata = data['metadata']
        return dataset
    
    def __len__(self) -> int:
        """Get dataset size.
        
        Returns:
            Number of examples
        """
        return len(self.data)
    
    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Get example by index.
        
        Args:
            index: Example index
            
        Returns:
            Training example dictionary
        """
        return self.data[index] 