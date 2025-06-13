# ⚠️ Auto-generated from test memory flow: verify before use

"""
Memory manager for handling both short-term and long-term memory.
Coordinates between Redis (STM) and ChromaDB (LTM) storage.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import redis
import chromadb
from chromadb.config import Settings

class MemoryManager:
    """Manages both short-term and long-term memory storage."""
    
    def __init__(self, redis_url: str, chroma_url: str):
        """Initialize memory manager with Redis and ChromaDB connections.
        
        Args:
            redis_url: Redis connection URL
            chroma_url: ChromaDB server URL (e.g. http://localhost:8000)
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis client for short-term memory
        self.redis_client = redis.from_url(redis_url)
        
        # Parse ChromaDB URL
        from urllib.parse import urlparse
        parsed_url = urlparse(chroma_url)
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or 8000
        
        # Initialize ChromaDB client with proper settings
        settings = Settings(
            chroma_api_impl="chromadb.api.fastapi.FastAPI",
            chroma_server_host=host,
            chroma_server_http_port=port
        )
        self.chroma_client = chromadb.Client(settings)
        
        # Create or get collections
        self.short_term_collection = self.chroma_client.get_or_create_collection("short_term")
        self.long_term_collection = self.chroma_client.get_or_create_collection("long_term_memory")
        
        self.logger.info(f"Initialized MemoryManager with Redis ({redis_url}) and ChromaDB ({chroma_url})")
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """Get a specific memory by ID from either Redis or ChromaDB.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Optional[Dict]: Memory data if found, None otherwise
        """
        try:
            # Try Redis first
            memory_data = self.redis_client.hgetall(f"memory:{memory_id}")
            if memory_data:
                import json
                return {
                    "content": memory_data.get(b"content", b"").decode(),
                    "metadata": json.loads(memory_data.get(b"metadata", b"{}").decode()),
                    "created_at": memory_data.get(b"created_at", b"").decode(),
                    "source": "short_term"
                }
            
            # Try ChromaDB if not in Redis
            results = self.long_term_collection.get(
                ids=[memory_id],
                include=["metadatas", "documents"]
            )
            
            if results and results["ids"]:
                metadata = results["metadatas"][0]
                created_at = metadata.get("created_at", datetime.now().isoformat())
                return {
                    "content": results["documents"][0],
                    "metadata": metadata,
                    "created_at": created_at,
                    "source": "long_term"
                }
                
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get memory {memory_id}: {e}")
            return None
    
    def store_memory(self, *args, **kwargs):
        """
        Store a memory in both short-term and long-term storage.
        Accepts either:
          - store_memory(content, metadata)
          - store_memory(memory_data_dict) where dict has 'content' and 'metadata'
        """
        if len(args) == 1 and isinstance(args[0], dict):
            memory_data = args[0]
            content = memory_data.get("content")
            metadata = memory_data.get("metadata", {})
            user_id = memory_data.get("user_id") or metadata.get("user_id")
        elif len(args) == 2:
            content, metadata = args
            user_id = kwargs.get("user_id") or (metadata.get("user_id") if metadata else None)
        else:
            content = kwargs.get("content")
            metadata = kwargs.get("metadata", {})
            user_id = kwargs.get("user_id") or (metadata.get("user_id") if metadata else None)
            if content is None:
                raise ValueError("Missing content for memory storage.")

        # Validate metadata type
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")

        if not user_id:
            user_id = "test_user"

        # Generate memory ID
        memory_id = f"{user_id}_{datetime.now().isoformat()}"
        
        # Store in Redis (STM)
        try:
            import json
            self.redis_client.hset(
                f"memory:{memory_id}",
                mapping={
                    "user_id": user_id,
                    "content": content,
                    "metadata": json.dumps(metadata or {}),
                    "created_at": datetime.now().isoformat()
                }
            )
            self.redis_client.expire(f"memory:{memory_id}", 3600)  # 1 hour TTL
            
            # Explicitly sync to LTM
            self._sync_to_ltm(memory_id, user_id, content, metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to store in Redis: {e}")
            raise
            
        return memory_id

    def _sync_to_ltm(self, memory_id: str, user_id: str, content: str, metadata: dict):
        """Explicitly sync a memory from STM to LTM.
        
        Args:
            memory_id: Memory identifier
            user_id: User identifier
            content: Memory content
            metadata: Memory metadata
        """
        try:
            created_at = datetime.now().isoformat()
            print(f"DEBUG: Syncing to LTM - memory_id: {memory_id}, user_id: {user_id}, content: {content}")
            self.long_term_collection.add(
                ids=[memory_id],
                documents=[content],
                metadatas=[{
                    "user_id": user_id,
                    **(metadata or {}),
                    "created_at": created_at
                }]
            )
            self.logger.info(f"Successfully synced memory {memory_id} to LTM")
        except Exception as e:
            self.logger.error(f"Failed to sync memory {memory_id} to LTM: {e}")
            # Don't raise - LTM is less critical
    
    def retrieve_context(self, user_id: str, limit: int = 5) -> str:
        """Retrieve relevant context for user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of memories to retrieve
            
        Returns:
            Context string combining recent memories
        """
        # Get recent memories from Redis
        recent_memories = []
        try:
            keys = self.redis_client.keys(f"memory:*")
            for key in keys[-limit:]:
                memory = self.redis_client.hgetall(key)
                if memory and memory.get("user_id") == user_id:
                    recent_memories.append(memory)
        except Exception as e:
            self.logger.error(f"Failed to retrieve from Redis: {e}")
        
        # Combine memories into context
        context = "\n".join(
            f"Memory: {m['content']}"
            for m in sorted(
                recent_memories,
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )
        )
        
        return context
    
    def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search memories using semantic search.
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        try:
            results = self.long_term_collection.query(
                query_texts=[query],
                n_results=limit,
                where={"user_id": user_id}
            )
            
            return [
                {
                    "id": id,
                    "content": doc,
                    "metadata": meta
                }
                for id, doc, meta in zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0]
                )
            ]
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []

    def get_chat_context(self, user_id: str, limit: int = 10) -> List[str]:
        """Get the most recent memories for a user to use as context in chat.
        
        Args:
            user_id: The ID of the user to get context for
            limit: Maximum number of memories to return (default: 10)
            
        Returns:
            List of memory contents as strings, sorted by created_at timestamp (newest first)
        """
        try:
            print(f"DEBUG: Getting chat context for user_id: {user_id}")
            results = self.long_term_collection.get(
                where={"user_id": user_id},
                limit=limit * 2  # Fetch more to ensure we have enough after sorting
            )
            print(f"DEBUG: ChromaDB get() results: {results}")
            
            if not results["documents"]:
                return []
                
            # Create list of (document, created_at) tuples
            memory_tuples = []
            for doc, metadata in zip(results["documents"], results["metadatas"]):
                if metadata and "created_at" in metadata:
                    try:
                        created_at = datetime.fromisoformat(metadata["created_at"])
                        memory_tuples.append((doc, created_at))
                    except (ValueError, TypeError) as e:
                        print(f"DEBUG: Failed to parse created_at: {e}")
                        continue
            
            # Sort by created_at (newest first) and take limit
            sorted_memories = sorted(memory_tuples, key=lambda x: x[1], reverse=True)
            return [doc for doc, _ in sorted_memories[:limit]]
            
        except Exception as e:
            print(f"DEBUG: Failed to get chat context: {str(e)}")
            return [] 