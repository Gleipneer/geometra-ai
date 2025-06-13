"""
Training configuration implementation for Geometra AI.
Handles training parameters and settings.
"""

from typing import Dict, Any
import yaml
from pathlib import Path

class TrainingConfig:
    """Training configuration for Geometra AI."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize training configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {
            'model': {
                'name': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 2000
            },
            'training': {
                'learning_rate': 1e-5,
                'batch_size': 32,
                'epochs': 3,
                'validation_split': 0.2
            },
            'optimizer': {
                'type': 'adam',
                'beta1': 0.9,
                'beta2': 0.999,
                'epsilon': 1e-8
            },
            'scheduler': {
                'type': 'cosine',
                'warmup_steps': 100,
                'max_steps': 1000
            },
            'regularization': {
                'dropout': 0.1,
                'weight_decay': 0.01
            }
        }
    
    def update(self, updates: Dict[str, Any]):
        """Update configuration.
        
        Args:
            updates: Dictionary of updates
        """
        def _update_dict(d: Dict, u: Dict):
            for k, v in u.items():
                if isinstance(v, dict) and k in d:
                    _update_dict(d[k], v)
                else:
                    d[k] = v
        
        _update_dict(self.config, updates)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def save(self, path: str):
        """Save configuration to file.
        
        Args:
            path: Path to save configuration
        """
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    @classmethod
    def load(cls, path: str) -> 'TrainingConfig':
        """Load configuration from file.
        
        Args:
            path: Path to load configuration from
            
        Returns:
            Loaded configuration
        """
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        return cls(config)
    
    def __str__(self) -> str:
        """Get string representation of configuration.
        
        Returns:
            Configuration string
        """
        return yaml.dump(self.config, default_flow_style=False) 