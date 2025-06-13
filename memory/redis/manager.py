"""Redis manager for short-term memory storage."""

import redis
from typing import Optional

class RedisManager:
    """Manages Redis operations for short-term memory."""
    
    def __init__(self, url: str):
        """Initialize Redis client.
        
        Args:
            url: Redis connection URL
        """
        self.client = redis.from_url(url)
    
    def set_context(self, session_id: str, context: str):
        """Store context for a session.
        
        Args:
            session_id: Unique session identifier
            context: Context to store
        """
        self.client.set(f"context:{session_id}", context)
    
    def get_context(self, session_id: str) -> Optional[str]:
        """Retrieve context for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Stored context or None if not found
        """
        return self.client.get(f"context:{session_id}") 