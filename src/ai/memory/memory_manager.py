"""
Memory manager implementation for Geometra AI.
Handles both short-term and long-term memory storage.
"""

from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime
import chromadb
from chromadb.config import Settings
from src.db.manager import DatabaseManager

class MemoryManager:
    """Memory manager for Geometra AI."""
    
    def __init__(self, db_manager: DatabaseManager, chroma_client: Optional[chromadb.Client] = None):
        """Initialize memory manager.
        
        Args:
            db_manager: Database manager instance
            chroma_client: ChromaDB client instance
        """
        self.db = db_manager
        self.chroma = chroma_client or chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=".chroma"
        ))
        self.collection = self.chroma.get_or_create_collection(
            name="geometra_memory",
            metadata={"description": "Long-term memory storage for Geometra AI"}
        )
    
    async def store_stm(self, user_id: str, content: str, metadata: Dict = None):
        """Store content in short-term memory.
        
        Args:
            user_id: User identifier
            content: Content to store
            metadata: Optional metadata
        """
        key = f"stm:{user_id}:{int(time.time())}"
        data = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        await self.db.redis.setex(key, 3600, json.dumps(data))
    
    async def store_ltm(self, content: str, metadata: Dict = None):
        """Store content in long-term memory.
        
        Args:
            content: Content to store
            metadata: Optional metadata
        """
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[f"ltm:{int(time.time())}"]
        )
    
    async def get_stm(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent short-term memory entries.
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of memory entries
        """
        pattern = f"stm:{user_id}:*"
        keys = await self.db.redis.keys(pattern)
        keys.sort(reverse=True)
        keys = keys[:limit]
        
        if not keys:
            return []
        
        values = await self.db.redis.mget(keys)
        return [json.loads(v) for v in values if v]
    
    async def search_ltm(self, query: str, limit: int = 5) -> List[Dict]:
        """Search long-term memory.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching entries
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        return [
            {
                "content": doc,
                "metadata": meta,
                "id": id_
            }
            for doc, meta, id_ in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["ids"][0]
            )
        ]
    
    async def cleanup_stm(self):
        """Clean up expired short-term memory entries."""
        pattern = "stm:*"
        keys = await self.db.redis.keys(pattern)
        if keys:
            await self.db.redis.delete(*keys) 