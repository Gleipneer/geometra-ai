# ⚠️ Auto-generated from test: verify before use

"""
Long-term memory implementation using ChromaDB.
Handles semantic storage and retrieval of memories.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np
import re

logger = logging.getLogger(__name__)

class LongTermMemory:
    """Handles long-term memory storage using ChromaDB."""
    
    def __init__(self, chroma_url: str = "http://localhost:8000"):
        """Initialize long-term memory storage.
        
        Args:
            chroma_url: URL for ChromaDB server (e.g. 'http://localhost:8000' or 'localhost:8000')
        """
        try:
            # Parse host and port from chroma_url
            url = chroma_url.replace('http://', '').replace('https://', '')
            if ':' in url:
                host, port = url.split(':')
                port = int(port)
            else:
                host = url
                port = 8000
            logger.info(f"Connecting to ChromaDB at host={host}, port={port}")
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=chromadb.Settings(
                    chroma_api_impl="chromadb.api.fastapi.FastAPI",
                    allow_reset=True
                )
            )
            self.collection = self.client.get_or_create_collection("long_term_memory")
            logger.info(f"Initialized long-term memory with ChromaDB at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise
    
    def store(
        self,
        user_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store memory in ChromaDB.
        
        Args:
            user_id: User identifier
            content: Memory content
            metadata: Optional metadata
            
        Returns:
            Memory ID
            
        Raises:
            ValueError: If user_id or content is None
        """
        if not user_id or not content:
            raise ValueError("user_id and content are required")
        
        # Generate memory ID
        memory_id = f"ltm:{user_id}:{datetime.now().isoformat()}"
        
        # Prepare metadata
        full_metadata = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        try:
            # Store in ChromaDB
            self.collection.add(
                ids=[memory_id],
                documents=[content],
                metadatas=[full_metadata]
            )
            
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get memory by ID.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Memory data or None if not found
        """
        try:
            result = self.collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"]
            )
            
            if not result["ids"]:
                return None
            
            return {
                "id": result["ids"][0],
                "content": result["documents"][0],
                "metadata": result["metadatas"][0]
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory: {e}")
            return None
    
    def search(
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
            results = self.collection.query(
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
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def purge(self, user_id: str) -> None:
        """Purge all memories for user.
        
        Args:
            user_id: User identifier
        """
        try:
            # Get all memory IDs for user
            results = self.collection.get(
                where={"user_id": user_id}
            )
            
            if results["ids"]:
                # Delete memories
                self.collection.delete(
                    ids=results["ids"]
                )
                
        except Exception as e:
            logger.error(f"Failed to purge memories: {e}")
            raise 