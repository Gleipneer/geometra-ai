"""Database manager for Geometra AI system."""

import os
from typing import Optional
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize database connections."""
        # Redis connection
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True
        )
        
        # PostgreSQL connection parameters
        self.pg_params = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", 5432)),
            "database": os.getenv("POSTGRES_DB", "geometra"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "")
        }
    
    @contextmanager
    def get_postgres_connection(self):
        """Get PostgreSQL connection with context manager."""
        conn = None
        try:
            conn = psycopg2.connect(**self.pg_params, cursor_factory=RealDictCursor)
            yield conn
        finally:
            if conn is not None:
                conn.close()
    
    def get_redis_connection(self) -> redis.Redis:
        """Get Redis connection."""
        return self.redis_client
    
    def test_connections(self) -> bool:
        """Test database connections."""
        try:
            # Test Redis
            self.redis_client.ping()
            
            # Test PostgreSQL
            with self.get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            
            return True
        except Exception as e:
            print(f"Database connection test failed: {str(e)}")
            return False 