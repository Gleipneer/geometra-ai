"""Component health check module for Geometra AI system."""

from typing import Dict, Any
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

class ComponentChecker:
    """Handles health checks for various system components."""
    
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        self.db_engine = create_engine(os.getenv("DATABASE_URL", "postgresql://localhost/geometra"))
        self.Session = sessionmaker(bind=self.db_engine)
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connection and basic operations."""
        try:
            with self.Session() as session:
                # Test query
                result = session.execute(text("SELECT 1")).scalar()
                if result != 1:
                    raise Exception("Database test query failed")
                
                return {
                    "status": "healthy",
                    "latency_ms": self._measure_latency(lambda: session.execute(text("SELECT 1"))),
                    "last_check": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def check_cache(self) -> Dict[str, Any]:
        """Check Redis cache connection and basic operations."""
        try:
            # Test set/get
            test_key = "health_check_test"
            test_value = datetime.utcnow().isoformat()
            
            self.redis_client.set(test_key, test_value)
            retrieved = self.redis_client.get(test_key)
            
            if retrieved.decode() != test_value:
                raise Exception("Cache test set/get failed")
            
            return {
                "status": "healthy",
                "latency_ms": self._measure_latency(lambda: self.redis_client.ping()),
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def check_storage(self) -> Dict[str, Any]:
        """Check storage system (e.g., file system or S3)."""
        try:
            # Implement storage check based on your storage solution
            # This is a placeholder that checks local file system
            test_dir = "storage_test"
            test_file = f"{test_dir}/test.txt"
            
            os.makedirs(test_dir, exist_ok=True)
            with open(test_file, "w") as f:
                f.write("test")
            
            with open(test_file, "r") as f:
                content = f.read()
            
            os.remove(test_file)
            os.rmdir(test_dir)
            
            if content != "test":
                raise Exception("Storage test failed")
            
            return {
                "status": "healthy",
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _measure_latency(self, operation) -> float:
        """Measure operation latency in milliseconds."""
        import time
        start = time.time()
        operation()
        return round((time.time() - start) * 1000, 2) 