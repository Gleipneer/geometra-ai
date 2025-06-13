"""Tests for system overview functionality."""

import pytest
from pathlib import Path
import yaml
import json
import logging
from src.logging.config import setup_logging

@pytest.fixture
def test_logger():
    """Fixture that provides a configured test logger."""
    # Setup logging before test
    setup_logging()
    
    # Get the test logger
    logger = logging.getLogger("test_logger")
    
    # Verify logger is configured
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) > 0, "Logger has no handlers"
    
    return logger

def test_system_components_exist():
    """Test that all required system components exist."""
    required_components = [
        "api",
        "ai",
        "db",
        "frontend",
        "monitoring",
        "security",
        "backup",
        "dr"
    ]
    
    for component in required_components:
        assert Path(f"src/{component}").exists(), f"Missing component: {component}"

def test_config_files_exist():
    """Test that all required configuration files exist."""
    required_configs = [
        "config.yaml",
        "logging.yaml",
        ".env.example"
    ]
    
    for config in required_configs:
        assert Path(config).exists(), f"Missing config file: {config}"

def test_documentation_files_exist():
    """Test that all required documentation files exist."""
    required_docs = [
        "01_ÖVERSIKT.md",
        "02_INSTALLATION.md",
        "03_BACKEND_SETUP.md",
        "04_FRONTEND_SETUP.md",
        "05_AI_SETUP.md"
    ]
    
    for doc in required_docs:
        assert Path(f"meta_docs/{doc}").exists(), f"Missing documentation: {doc}"

def test_system_architecture(test_config):
    """Test system architecture configuration."""
    # Test API configuration
    assert "api" in test_config
    assert "host" in test_config["api"]
    assert "port" in test_config["api"]
    assert "debug" in test_config["api"]
    
    # Test AI configuration
    assert "ai" in test_config
    assert "model" in test_config["ai"]
    assert "temperature" in test_config["ai"]
    assert "max_tokens" in test_config["ai"]
    
    # Test database configuration
    assert "db" in test_config
    assert "redis" in test_config["db"]
    assert "chroma" in test_config["db"]

def test_system_dependencies():
    """Test that all required dependencies are installed."""
    import pkg_resources
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "redis",
        "chromadb",
        "openai",
        "pytest",
        "pytest-cov"
    ]
    
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    
    for package in required_packages:
        assert package.lower() in installed_packages, f"Missing package: {package}"

def test_system_logging(test_logger):
    """Test system logging configuration."""
    test_logger.info("Test info message")
    test_logger.warning("Test warning message")
    test_logger.error("Test error message")
    
    # Verify logger is configured
    assert test_logger.level == 10  # DEBUG level
    assert len(test_logger.handlers) > 0

def test_system_security(mock_env_vars):
    """Test system security configuration."""
    required_env_vars = [
        "GEOMETRA_API_KEY",
        "GEOMETRA_DB_PASSWORD",
        "GEOMETRA_AI_MODEL",
        "GEOMETRA_LOG_LEVEL"
    ]
    
    for var in required_env_vars:
        assert var in mock_env_vars, f"Missing environment variable: {var}"

def test_system_backup():
    """Test system backup configuration."""
    backup_dir = Path("backup")
    assert backup_dir.exists(), "Missing backup directory"
    
    required_backup_dirs = [
        "db",
        "files",
        "code"
    ]
    
    for dir_name in required_backup_dirs:
        assert (backup_dir / dir_name).exists(), f"Missing backup directory: {dir_name}"

def test_system_monitoring():
    """Test system monitoring configuration."""
    monitoring_dir = Path("monitoring")
    assert monitoring_dir.exists(), "Missing monitoring directory"
    
    required_monitoring_dirs = [
        "logging",
        "metrics",
        "alerts"
    ]
    
    for dir_name in required_monitoring_dirs:
        assert (monitoring_dir / dir_name).exists(), f"Missing monitoring directory: {dir_name}" 