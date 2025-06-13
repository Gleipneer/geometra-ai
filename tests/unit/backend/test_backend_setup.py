"""Tests for backend setup."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import json
from pathlib import Path

@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    from src.api.main import app
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)

def test_api_structure():
    """Test API directory structure."""
    api_dir = Path("src/api")
    assert api_dir.exists(), "Missing API directory"
    
    required_files = [
        "main.py",
        "routes/__init__.py",
        "models/__init__.py",
        "services/__init__.py",
        "utils/__init__.py"
    ]
    
    for file in required_files:
        assert (api_dir / file).exists(), f"Missing API file: {file}"

def test_api_routes(client):
    """Test API routes."""
    # Test health check
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    # Test API version
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()

def test_api_models():
    """Test API models."""
    from src.api.models import (
        User,
        Project,
        Document,
        Analysis
    )
    
    # Test model attributes
    user = User(
        id=1,
        username="test_user",
        email="test@example.com"
    )
    assert user.id == 1
    assert user.username == "test_user"
    assert user.email == "test@example.com"
    
    # Test model validation
    with pytest.raises(ValueError):
        User(id=1, username="", email="invalid")

def test_api_services(mock_redis, mock_chroma):
    """Test API services."""
    from src.api.services import (
        UserService,
        ProjectService,
        DocumentService,
        AnalysisService
    )
    
    # Test user service
    user_service = UserService(mock_redis)
    user = user_service.create_user("test_user", "test@example.com")
    assert user.username == "test_user"
    assert user.email == "test@example.com"
    
    # Test project service
    project_service = ProjectService(mock_redis)
    project = project_service.create_project("test_project", user.id)
    assert project.name == "test_project"
    assert project.user_id == user.id

def test_api_middleware(client):
    """Test API middleware."""
    # Test authentication middleware
    response = client.get("/api/protected")
    assert response.status_code == 401
    
    # Test with valid token
    headers = {"Authorization": "Bearer test_token"}
    response = client.get("/api/protected", headers=headers)
    assert response.status_code == 200

def test_api_error_handling(client):
    """Test API error handling."""
    # Test 404
    response = client.get("/nonexistent")
    assert response.status_code == 404
    
    # Test 500
    response = client.get("/error")
    assert response.status_code == 500
    assert "error" in response.json()

def test_api_database_connections(mock_redis, mock_chroma):
    """Test API database connections."""
    # Test Redis connection
    assert mock_redis.set("test_key", "test_value")
    assert mock_redis.get("test_key") == "test_value"
    
    # Test ChromaDB connection
    collection = mock_chroma.create_collection("test_collection")
    assert collection is not None
    assert "test_collection" in mock_chroma.list_collections()

def test_api_logging(test_logger):
    """Test API logging."""
    # Test request logging
    test_logger.info("API request: GET /test")
    test_logger.error("API error: Invalid input")
    
    # Verify logger configuration
    assert test_logger.level == 10  # DEBUG level
    assert len(test_logger.handlers) > 0

def test_api_security():
    """Test API security."""
    security_dir = Path("src/api/security")
    assert security_dir.exists(), "Missing API security directory"
    
    required_security_files = [
        "auth.py",
        "middleware.py",
        "validation.py"
    ]
    
    for file in required_security_files:
        assert (security_dir / file).exists(), f"Missing API security file: {file}"

def test_api_documentation():
    """Test API documentation."""
    docs_dir = Path("docs/api")
    assert docs_dir.exists(), "Missing API documentation directory"
    
    required_docs = [
        "openapi.json",
        "swagger.json",
        "redoc.html"
    ]
    
    for doc in required_docs:
        assert (docs_dir / doc).exists(), f"Missing API documentation: {doc}" 