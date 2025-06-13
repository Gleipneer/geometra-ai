"""Tests for API setup."""

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
    
    required_dirs = [
        "routes",
        "models",
        "services",
        "middleware",
        "utils",
        "security"
    ]
    
    for dir_name in required_dirs:
        assert (api_dir / dir_name).exists(), f"Missing API directory: {dir_name}"

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
    
    # Test user routes
    response = client.post("/api/users", json={
        "username": "test_user",
        "email": "test@example.com"
    })
    assert response.status_code == 201
    
    # Test project routes
    response = client.post("/api/projects", json={
        "name": "test_project",
        "description": "Test project"
    })
    assert response.status_code == 201
    
    # Test document routes
    response = client.post("/api/documents", json={
        "title": "test_document",
        "content": "Test content"
    })
    assert response.status_code == 201

def test_api_models():
    """Test API models."""
    from src.api.models import (
        UserCreate,
        UserResponse,
        ProjectCreate,
        ProjectResponse,
        DocumentCreate,
        DocumentResponse
    )
    
    # Test user models
    user_create = UserCreate(
        username="test_user",
        email="test@example.com"
    )
    assert user_create.username == "test_user"
    assert user_create.email == "test@example.com"
    
    # Test project models
    project_create = ProjectCreate(
        name="test_project",
        description="Test project"
    )
    assert project_create.name == "test_project"
    assert project_create.description == "Test project"
    
    # Test document models
    document_create = DocumentCreate(
        title="test_document",
        content="Test content"
    )
    assert document_create.title == "test_document"
    assert document_create.content == "Test content"

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
    
    # Test document service
    document_service = DocumentService(mock_chroma)
    document = document_service.create_document("test_document", "Test content", project.id)
    assert document.title == "test_document"
    assert document.project_id == project.id

def test_api_middleware(client):
    """Test API middleware."""
    # Test authentication middleware
    response = client.get("/api/protected")
    assert response.status_code == 401
    
    # Test with valid token
    headers = {"Authorization": "Bearer test_token"}
    response = client.get("/api/protected", headers=headers)
    assert response.status_code == 200
    
    # Test rate limiting
    for _ in range(100):
        response = client.get("/api/rate-limited")
    assert response.status_code == 429
    
    # Test CORS
    headers = {"Origin": "http://localhost:3000"}
    response = client.get("/api/cors", headers=headers)
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

def test_api_error_handling(client):
    """Test API error handling."""
    # Test 404
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert "error" in response.json()
    
    # Test 500
    response = client.get("/error")
    assert response.status_code == 500
    assert "error" in response.json()
    
    # Test validation error
    response = client.post("/api/users", json={
        "username": "",  # Invalid username
        "email": "invalid-email"  # Invalid email
    })
    assert response.status_code == 422
    assert "detail" in response.json()

def test_api_security():
    """Test API security."""
    from src.api.security import (
        JWTManager,
        PasswordManager,
        APISecurity
    )
    
    # Test JWT
    jwt_manager = JWTManager()
    token = jwt_manager.create_token({"user_id": 1})
    payload = jwt_manager.verify_token(token)
    assert payload["user_id"] == 1
    
    # Test password hashing
    password_manager = PasswordManager()
    hashed = password_manager.hash_password("test_password")
    assert password_manager.verify_password("test_password", hashed)
    
    # Test API security
    security = APISecurity()
    assert security.validate_api_key("test_key")
    assert not security.validate_api_key("invalid_key")

def test_api_documentation():
    """Test API documentation."""
    # Test OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    
    # Test Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    
    # Test ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200

def test_api_logging(test_logger):
    """Test API logging."""
    # Test request logging
    test_logger.info("API request: GET /test")
    test_logger.error("API error: Invalid input")
    
    # Verify logger configuration
    assert test_logger.level == 10  # DEBUG level
    assert len(test_logger.handlers) > 0

def test_api_metrics():
    """Test API metrics."""
    from src.api.metrics import APIMetrics
    
    metrics = APIMetrics()
    
    # Test request metrics
    metrics.record_request("GET", "/test", 200, 0.1)
    request_metrics = metrics.get_request_metrics()
    assert "GET" in request_metrics
    assert "/test" in request_metrics["GET"]
    
    # Test error metrics
    metrics.record_error("GET", "/test", 500)
    error_metrics = metrics.get_error_metrics()
    assert "GET" in error_metrics
    assert "/test" in error_metrics["GET"] 