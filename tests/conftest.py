"""Common test fixtures for Geometra AI system."""

import pytest
import os
import sys
from pathlib import Path
from src.db.manager import DatabaseManager
import chromadb
from src.ai.memory.memory_manager import MemoryManager
from src.ai.fallback.fallback_manager import FallbackManager
from src.ai.prompt.prompt_manager import PromptManager
from src.ai.chat.chat_manager import ChatManager

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_PORT"] = "5432"
    os.environ["POSTGRES_DB"] = "geometra_test"
    os.environ["POSTGRES_USER"] = "postgres"
    os.environ["POSTGRES_PASSWORD"] = "postgres"
    
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_DB"] = "0"

@pytest.fixture
def db_manager():
    """Create database manager for testing."""
    return DatabaseManager(
        redis_host="localhost",
        redis_port=6379,
        redis_db=0,
        postgres_host="localhost",
        postgres_port=5432,
        postgres_db="geometra_test",
        postgres_user="postgres",
        postgres_password="postgres"
    )

@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return {
        "api": {
            "host": "localhost",
            "port": 8000,
            "debug": True
        },
        "ai": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "db": {
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            },
            "chroma": {
                "host": "localhost",
                "port": 8001
            }
        }
    }

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    env_vars = {
        "GEOMETRA_API_KEY": "test_api_key",
        "GEOMETRA_DB_PASSWORD": "test_password",
        "GEOMETRA_AI_MODEL": "gpt-4",
        "GEOMETRA_LOG_LEVEL": "DEBUG"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars

@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis connection."""
    class MockRedis:
        def __init__(self, *args, **kwargs):
            self.data = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value):
            self.data[key] = value
            return True
        
        def delete(self, key):
            if key in self.data:
                del self.data[key]
                return 1
            return 0
    
    monkeypatch.setattr("redis.Redis", MockRedis)
    return MockRedis()

@pytest.fixture
def mock_chroma(monkeypatch):
    """Mock ChromaDB connection."""
    class MockChroma:
        def __init__(self, *args, **kwargs):
            self.collections = {}
        
        def create_collection(self, name, **kwargs):
            self.collections[name] = {}
            return self.collections[name]
        
        def get_collection(self, name):
            return self.collections.get(name)
        
        def list_collections(self):
            return list(self.collections.keys())
    
    monkeypatch.setattr("chromadb.HttpClient", MockChroma)
    return MockChroma()

@pytest.fixture
def mock_requests(monkeypatch):
    """Mock requests library."""
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self.json_data = json_data
            self.status_code = status_code
        
        def json(self):
            return self.json_data
    
    def mock_get(*args, **kwargs):
        return MockResponse({"status": "ok"})
    
    def mock_post(*args, **kwargs):
        return MockResponse({"status": "ok"})
    
    monkeypatch.setattr("requests.get", mock_get)
    monkeypatch.setattr("requests.post", mock_post)
    return {"get": mock_get, "post": mock_post}

@pytest.fixture
def test_logger():
    """Test logger fixture."""
    import logging
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    return logger

@pytest.fixture
def chroma_client():
    """Create ChromaDB client for testing."""
    return chromadb.Client()

@pytest.fixture
def memory_manager(db_manager, chroma_client):
    """Create memory manager for testing."""
    return MemoryManager(db_manager, chroma_client)

@pytest.fixture
def fallback_manager():
    """Create fallback manager for testing."""
    return FallbackManager()

@pytest.fixture
def prompt_manager():
    """Create prompt manager for testing."""
    return PromptManager()

@pytest.fixture
def chat_manager(memory_manager, fallback_manager, prompt_manager):
    """Create chat manager for testing."""
    return ChatManager(memory_manager, fallback_manager, prompt_manager) 