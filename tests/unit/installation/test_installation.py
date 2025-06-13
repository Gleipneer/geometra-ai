"""Tests for installation process."""

import pytest
import subprocess
import sys
from pathlib import Path
import yaml

def test_python_version():
    """Test Python version requirements."""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    assert current_version >= required_version, f"Python {required_version[0]}.{required_version[1]} or higher required"

def test_virtual_environment():
    """Test virtual environment setup."""
    assert hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix), \
        "Not running in a virtual environment"

def test_required_directories():
    """Test required directory structure."""
    required_dirs = [
        "src",
        "tests",
        "docs",
        "logs",
        "backup",
        "monitoring"
    ]
    
    for dir_name in required_dirs:
        assert Path(dir_name).exists(), f"Missing directory: {dir_name}"

def test_pip_installation():
    """Test pip installation process."""
    # Test pip is available
    result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, text=True)
    assert result.returncode == 0, "pip not available"
    
    # Test pip can install packages
    test_package = "pytest"
    result = subprocess.run([sys.executable, "-m", "pip", "install", test_package],
                          capture_output=True, text=True)
    assert result.returncode == 0, f"Failed to install {test_package}"

def test_environment_variables(mock_env_vars):
    """Test environment variable setup."""
    required_vars = [
        "GEOMETRA_API_KEY",
        "GEOMETRA_DB_PASSWORD",
        "GEOMETRA_AI_MODEL",
        "GEOMETRA_LOG_LEVEL"
    ]
    
    for var in required_vars:
        assert var in mock_env_vars, f"Missing environment variable: {var}"

def test_configuration_files():
    """Test configuration file setup."""
    config_files = [
        "config.yaml",
        "logging.yaml",
        ".env.example"
    ]
    
    for file in config_files:
        assert Path(file).exists(), f"Missing configuration file: {file}"
        
        # Test YAML files are valid
        if file.endswith('.yaml'):
            with open(file, 'r') as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {file}: {str(e)}")

def test_database_connections(mock_redis, mock_chroma):
    """Test database connection setup."""
    # Test Redis connection
    assert mock_redis.set("test_key", "test_value")
    assert mock_redis.get("test_key") == "test_value"
    
    # Test ChromaDB connection
    collection = mock_chroma.create_collection("test_collection")
    assert collection is not None
    assert "test_collection" in mock_chroma.list_collections()

def test_logging_setup(test_logger):
    """Test logging setup."""
    # Test logging levels
    test_logger.debug("Debug message")
    test_logger.info("Info message")
    test_logger.warning("Warning message")
    test_logger.error("Error message")
    
    # Verify logger configuration
    assert test_logger.level == 10  # DEBUG level
    assert len(test_logger.handlers) > 0

def test_security_setup():
    """Test security setup."""
    security_dir = Path("security")
    assert security_dir.exists(), "Missing security directory"
    
    required_security_files = [
        "auth/jwt.py",
        "auth/api_keys.py",
        "authorization/rbac.py",
        "data/encryption.py"
    ]
    
    for file in required_security_files:
        assert (security_dir / file).exists(), f"Missing security file: {file}"

def test_monitoring_setup():
    """Test monitoring setup."""
    monitoring_dir = Path("monitoring")
    assert monitoring_dir.exists(), "Missing monitoring directory"
    
    required_monitoring_files = [
        "logging/config.py",
        "metrics/prometheus.py",
        "alerts/rules.py"
    ]
    
    for file in required_monitoring_files:
        assert (monitoring_dir / file).exists(), f"Missing monitoring file: {file}" 