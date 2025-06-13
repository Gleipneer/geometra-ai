# ⚠️ Auto-generated from test: verify before use

"""
Short-term memory implementation using Redis.
Handles temporary storage of user interactions with TTL.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import redis

class ShortTermMemory:
    """Handles short-term memory storage using Redis."""
    
    def __init__(
        self,
        redis_url: str = 'redis://localhost:6379/0',
        redis_client: Optional[redis.Redis] = None
    ):
        """Initialize short-term memory.
        
        Args:
            redis_url: Redis connection URL
            redis_client: Optional Redis client instance for dependency injection
        """
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis_client or redis.from_url(redis_url)
    
    def store(
        self,
        user_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        expires_in: Optional[int] = None
    ) -> str:
        """Store memory in Redis.
        
        Args:
            user_id: User identifier
            content: Memory content
            metadata: Optional metadata
            expires_in: Optional TTL in seconds
            
        Returns:
            Memory ID
            
        Raises:
            ValueError: If user_id or content is None
        """
        if not user_id or not content:
            raise ValueError("user_id and content are required")
        
        # Generate memory ID
        memory_id = f"stm:{user_id}:{datetime.now().isoformat()}"
        
        # Prepare memory data
        memory_data = {
            "user_id": user_id,
            "content": content,
            "metadata": json.dumps(metadata or {}),
            "created_at": datetime.now().isoformat()
        }
        
        try:
            # Store in Redis
            self.redis_client.hset(
                memory_id,
                mapping=memory_data
            )
            
            # Set expiration if specified
            if expires_in:
                self.redis_client.expire(memory_id, expires_in)
            
            # Add to user's recent memories list
            self.redis_client.lpush(f"user:{user_id}:recent", memory_id)
            self.redis_client.ltrim(f"user:{user_id}:recent", 0, 99)  # Keep last 100
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}")
            raise
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get memory by ID.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Memory data or None if not found
        """
        try:
            memory = self.redis_client.hgetall(memory_id)
            if not memory:
                return None
            # Convert bytes to str if needed
            memory = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in memory.items()}
            # Deserialize metadata
            if "metadata" in memory:
                memory["metadata"] = json.loads(memory["metadata"])
            return memory
        except Exception as e:
            self.logger.error(f"Failed to get memory: {e}")
            return None
    
    def get_recent(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent memories for user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of recent memories
        """
        try:
            # Get recent memory IDs
            memory_ids = self.redis_client.lrange(
                f"user:{user_id}:recent",
                0,
                limit - 1
            )
            
            # Get memory data
            memories = []
            for memory_id in memory_ids:
                memory = self.get(memory_id.decode() if isinstance(memory_id, bytes) else memory_id)
                if memory:
                    memories.append(memory)
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed to get recent memories: {e}")
            return []
    
    def clear(self, user_id: str) -> None:
        """Clear all memories for user.
        
        Args:
            user_id: User identifier
        """
        try:
            # Get all memory IDs
            memory_ids = self.redis_client.lrange(
                f"user:{user_id}:recent",
                0,
                -1
            )
            
            # Delete memories
            if memory_ids:
                self.redis_client.delete(*memory_ids)
            
            # Delete user's recent list
            self.redis_client.delete(f"user:{user_id}:recent")
            
        except Exception as e:
            self.logger.error(f"Failed to clear memories: {e}")
            raise 