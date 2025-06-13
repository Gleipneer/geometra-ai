"""Tests for security."""

import pytest
from pathlib import Path
import yaml
import json
from datetime import datetime
import subprocess
from unittest.mock import Mock, patch

def test_security_structure():
    """Test security directory structure."""
    security_dir = Path("security")
    assert security_dir.exists(), "Missing security directory"
    
    required_dirs = [
        "auth",
        "authorization",
        "data"
    ]
    
    for dir_name in required_dirs:
        assert (security_dir / dir_name).exists(), f"Missing directory: {dir_name}"

def test_auth_config():
    """Test authentication configuration."""
    auth_dir = Path("security/auth")
    assert auth_dir.exists(), "Missing auth directory"
    
    required_files = [
        "jwt.py",
        "api_keys.py",
        "oauth.py"
    ]
    
    for file in required_files:
        assert (auth_dir / file).exists(), f"Missing file: {file}"

def test_authorization_config():
    """Test authorization configuration."""
    auth_dir = Path("security/authorization")
    assert auth_dir.exists(), "Missing authorization directory"
    
    required_files = [
        "rbac.py",
        "policies.py",
        "permissions.py"
    ]
    
    for file in required_files:
        assert (auth_dir / file).exists(), f"Missing file: {file}"

def test_data_security():
    """Test data security."""
    data_dir = Path("security/data")
    assert data_dir.exists(), "Missing data directory"
    
    required_files = [
        "encryption.py",
        "sanitization.py",
        "validation.py"
    ]
    
    for file in required_files:
        assert (data_dir / file).exists(), f"Missing file: {file}"

def test_jwt_auth():
    """Test JWT authentication."""
    jwt_file = Path("security/auth/jwt.py")
    assert jwt_file.exists(), "Missing JWT file"
    
    with open(jwt_file) as f:
        content = f.read()
    
    required_functions = [
        "create_token",
        "verify_token",
        "refresh_token"
    ]
    
    for function in required_functions:
        assert function in content, f"Missing function: {function}"

def test_api_keys():
    """Test API keys."""
    api_keys_file = Path("security/auth/api_keys.py")
    assert api_keys_file.exists(), "Missing API keys file"
    
    with open(api_keys_file) as f:
        content = f.read()
    
    required_functions = [
        "generate_key",
        "validate_key",
        "revoke_key"
    ]
    
    for function in required_functions:
        assert function in content, f"Missing function: {function}"

def test_oauth():
    """Test OAuth."""
    oauth_file = Path("security/auth/oauth.py")
    assert oauth_file.exists(), "Missing OAuth file"
    
    with open(oauth_file) as f:
        content = f.read()
    
    required_functions = [
        "authorize",
        "token",
        "refresh"
    ]
    
    for function in required_functions:
        assert function in content, f"Missing function: {function}"

def test_rbac():
    """Test RBAC."""
    rbac_file = Path("security/authorization/rbac.py")
    assert rbac_file.exists(), "Missing RBAC file"
    
    with open(rbac_file) as f:
        content = f.read()
    
    required_classes = [
        "Role",
        "Permission",
        "User"
    ]
    
    for class_name in required_classes:
        assert class_name in content, f"Missing class: {class_name}"

def test_policies():
    """Test policies."""
    policies_file = Path("security/authorization/policies.py")
    assert policies_file.exists(), "Missing policies file"
    
    with open(policies_file) as f:
        content = f.read()
    
    required_classes = [
        "Policy",
        "PolicySet",
        "PolicyEvaluator"
    ]
    
    for class_name in required_classes:
        assert class_name in content, f"Missing class: {class_name}"

def test_encryption():
    """Test encryption."""
    encryption_file = Path("security/data/encryption.py")
    assert encryption_file.exists(), "Missing encryption file"
    
    with open(encryption_file) as f:
        content = f.read()
    
    required_functions = [
        "encrypt",
        "decrypt",
        "generate_key"
    ]
    
    for function in required_functions:
        assert function in content, f"Missing function: {function}"

def test_sanitization():
    """Test sanitization."""
    sanitization_file = Path("security/data/sanitization.py")
    assert sanitization_file.exists(), "Missing sanitization file"
    
    with open(sanitization_file) as f:
        content = f.read()
    
    required_functions = [
        "sanitize_input",
        "sanitize_output",
        "validate_input"
    ]
    
    for function in required_functions:
        assert function in content, f"Missing function: {function}"

def test_validation():
    """Test validation."""
    validation_file = Path("security/data/validation.py")
    assert validation_file.exists(), "Missing validation file"
    
    with open(validation_file) as f:
        content = f.read()
    
    required_functions = [
        "validate_schema",
        "validate_data",
        "validate_format"
    ]
    
    for function in required_functions:
        assert function in content, f"Missing function: {function}"

def test_security_middleware():
    """Test security middleware."""
    middleware_dir = Path("security/middleware")
    assert middleware_dir.exists(), "Missing middleware directory"
    
    required_files = [
        "auth.py",
        "cors.py",
        "rate_limit.py"
    ]
    
    for file in required_files:
        assert (middleware_dir / file).exists(), f"Missing file: {file}"

def test_security_utils():
    """Test security utilities."""
    utils_dir = Path("security/utils")
    assert utils_dir.exists(), "Missing utils directory"
    
    required_files = [
        "crypto.py",
        "hashing.py",
        "logging.py"
    ]
    
    for file in required_files:
        assert (utils_dir / file).exists(), f"Missing file: {file}" 