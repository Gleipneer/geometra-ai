#!/usr/bin/env python3
"""Cleanup script for test data in Redis and ChromaDB.

This script removes all test data from both Redis and ChromaDB collections.
It should be run before running tests to ensure a clean state.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.memory_manager import MemoryManager
from config.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_test_data(user_id: Optional[str] = None) -> None:
    """Clean up test data from Redis and ChromaDB.
    
    Args:
        user_id: Optional user ID to clean up specific test data.
                 If None, cleans up all test data.
    """
    try:
        settings = get_settings()
        memory_manager = MemoryManager(
            redis_url=settings["redis_url"],
            chroma_url=settings["chroma_url"]
        )
        
        # Clean up Redis
        logger.info("Cleaning up Redis test data...")
        if user_id:
            memory_manager.redis_client.delete(f"memory:{user_id}")
        else:
            # Delete all test-related keys
            for key in memory_manager.redis_client.keys("memory:test_*"):
                memory_manager.redis_client.delete(key)
        
        # Clean up ChromaDB
        logger.info("Cleaning up ChromaDB test data...")
        if user_id:
            # Delete specific user's memories
            memory_manager.long_term_collection.delete(
                where={"user_id": user_id}
            )
            memory_manager.short_term_collection.delete(
                where={"user_id": user_id}
            )
        else:
            # Delete all test memories
            memory_manager.long_term_collection.delete(
                where={"user_id": {"$regex": "^test_"}}
            )
            memory_manager.short_term_collection.delete(
                where={"user_id": {"$regex": "^test_"}}
            )
        
        logger.info("Cleanup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up test data from Redis and ChromaDB")
    parser.add_argument("--user-id", help="Specific user ID to clean up")
    args = parser.parse_args()
    
    cleanup_test_data(args.user_id) 