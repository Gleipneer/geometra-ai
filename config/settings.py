"""Configuration settings for the application."""

import os
from typing import Dict, Any

def get_settings() -> Dict[str, Any]:
    """Get application settings.
    
    Returns:
        Dict containing application settings
    """
    return {
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        "chroma_url": os.getenv("CHROMA_URL", "http://localhost:8000"),
    } 