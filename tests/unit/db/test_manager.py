"""Unit tests for database manager."""

import pytest
from src.db.manager import DatabaseManager
import os

@pytest.fixture
def db_manager():
    """Create database manager fixture."""
    return DatabaseManager()

def test_redis_connection(db_manager):
    """Test Redis connection."""
    redis_client = db_manager.get_redis_connection()
    assert redis_client.ping()

def test_postgres_connection(db_manager):
    """Test PostgreSQL connection."""
    with db_manager.get_postgres_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS result")
            result = cur.fetchone()
            assert result["result"] == 1

def test_connection_test(db_manager):
    """Test connection test method."""
    assert db_manager.test_connections() 