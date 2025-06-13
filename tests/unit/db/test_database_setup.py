"""Tests for database setup."""

import pytest
from pathlib import Path
import json
import yaml
from datetime import datetime

def test_database_structure():
    """Test database directory structure."""
    db_dir = Path("src/db")
    assert db_dir.exists(), "Missing database directory"
    
    required_dirs = [
        "redis",
        "chroma",
        "postgres",
        "migrations",
        "models"
    ]
    
    for dir_name in required_dirs:
        assert (db_dir / dir_name).exists(), f"Missing database directory: {dir_name}"

def test_redis_setup(mock_redis):
    """Test Redis setup."""
    # Test basic operations
    assert mock_redis.set("test_key", "test_value")
    assert mock_redis.get("test_key") == "test_value"
    
    # Test data types
    mock_redis.set("int_key", "123")
    mock_redis.set("float_key", "123.45")
    mock_redis.set("json_key", json.dumps({"test": "value"}))
    
    assert mock_redis.get("int_key") == "123"
    assert mock_redis.get("float_key") == "123.45"
    assert json.loads(mock_redis.get("json_key")) == {"test": "value"}
    
    # Test expiration
    mock_redis.set("expire_key", "value", ex=60)
    assert mock_redis.get("expire_key") == "value"

def test_chroma_setup(mock_chroma):
    """Test ChromaDB setup."""
    # Test collection operations
    collection = mock_chroma.create_collection("test_collection")
    assert collection is not None
    
    # Test document operations
    collection.add(
        documents=["Test document"],
        metadatas=[{"source": "test"}],
        ids=["1"]
    )
    
    # Test query operations
    results = collection.query(
        query_texts=["Test"],
        n_results=1
    )
    assert len(results["documents"]) > 0

def test_postgres_setup():
    """Test PostgreSQL setup."""
    from src.db.postgres.models import Base, User, Project, Document
    
    # Test model definitions
    assert hasattr(User, "__tablename__")
    assert hasattr(Project, "__tablename__")
    assert hasattr(Document, "__tablename__")
    
    # Test relationships
    assert hasattr(User, "projects")
    assert hasattr(Project, "documents")
    assert hasattr(Document, "project")

def test_database_migrations():
    """Test database migrations."""
    migrations_dir = Path("src/db/migrations")
    assert migrations_dir.exists(), "Missing migrations directory"
    
    # Test migration files
    migration_files = list(migrations_dir.glob("*.py"))
    assert len(migration_files) > 0
    
    # Test migration structure
    for file in migration_files:
        with open(file) as f:
            content = f.read()
            assert "def upgrade" in content
            assert "def downgrade" in content

def test_database_models():
    """Test database models."""
    models_dir = Path("src/db/models")
    assert models_dir.exists(), "Missing models directory"
    
    required_models = [
        "user.py",
        "project.py",
        "document.py",
        "analysis.py"
    ]
    
    for model in required_models:
        assert (models_dir / model).exists(), f"Missing model: {model}"

def test_database_connections(mock_redis, mock_chroma):
    """Test database connections."""
    from src.db.connection import DatabaseConnection
    
    db = DatabaseConnection()
    
    # Test Redis connection
    assert db.redis is not None
    assert db.redis.set("test_key", "test_value")
    
    # Test ChromaDB connection
    assert db.chroma is not None
    collection = db.chroma.create_collection("test_collection")
    assert collection is not None

def test_database_backup():
    """Test database backup functionality."""
    from src.db.backup import DatabaseBackup
    
    backup = DatabaseBackup()
    
    # Test Redis backup
    redis_backup = backup.backup_redis()
    assert redis_backup is not None
    assert Path(redis_backup).exists()
    
    # Test ChromaDB backup
    chroma_backup = backup.backup_chroma()
    assert chroma_backup is not None
    assert Path(chroma_backup).exists()

def test_database_restore():
    """Test database restore functionality."""
    from src.db.backup import DatabaseBackup
    
    backup = DatabaseBackup()
    
    # Test Redis restore
    redis_restore = backup.restore_redis("test_backup")
    assert redis_restore is True
    
    # Test ChromaDB restore
    chroma_restore = backup.restore_chroma("test_backup")
    assert chroma_restore is True

def test_database_monitoring():
    """Test database monitoring."""
    from src.db.monitoring import DatabaseMonitoring
    
    monitoring = DatabaseMonitoring()
    
    # Test metrics collection
    metrics = monitoring.collect_metrics()
    assert "redis" in metrics
    assert "chroma" in metrics
    assert "postgres" in metrics
    
    # Test health checks
    health = monitoring.check_health()
    assert health["status"] == "healthy"
    assert "redis" in health["components"]
    assert "chroma" in health["components"]
    assert "postgres" in health["components"]

def test_database_security():
    """Test database security."""
    from src.db.security import DatabaseSecurity
    
    security = DatabaseSecurity()
    
    # Test encryption
    encrypted = security.encrypt("test_data")
    decrypted = security.decrypt(encrypted)
    assert decrypted == "test_data"
    
    # Test access control
    assert security.check_access("user1", "read", "document1")
    assert not security.check_access("user2", "write", "document1") 