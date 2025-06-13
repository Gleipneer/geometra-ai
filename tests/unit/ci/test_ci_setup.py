"""Tests for CI setup."""

import pytest
from pathlib import Path
import yaml
import json
from datetime import datetime
import subprocess
from unittest.mock import Mock, patch

def test_ci_structure():
    """Test CI directory structure."""
    ci_dir = Path(".github/workflows")
    assert ci_dir.exists(), "Missing CI directory"
    
    required_files = [
        "ci.yml",
        "cd.yml",
        "test.yml",
        "security.yml"
    ]
    
    for file in required_files:
        assert (ci_dir / file).exists(), f"Missing CI file: {file}"

def test_ci_configuration():
    """Test CI configuration."""
    ci_file = Path(".github/workflows/ci.yml")
    assert ci_file.exists(), "Missing CI configuration"
    
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    required_config = [
        "name",
        "on",
        "jobs",
        "steps"
    ]
    
    for key in required_config:
        assert key in config, f"Missing configuration key: {key}"

def test_ci_jobs():
    """Test CI jobs."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    required_jobs = [
        "test",
        "lint",
        "security",
        "build"
    ]
    
    for job in required_jobs:
        assert job in config["jobs"], f"Missing job: {job}"

def test_ci_steps():
    """Test CI steps."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    test_job = config["jobs"]["test"]
    required_steps = [
        "checkout",
        "setup-python",
        "install-dependencies",
        "run-tests"
    ]
    
    for step in required_steps:
        assert any(s["name"] == step for s in test_job["steps"]), f"Missing step: {step}"

def test_ci_dependencies():
    """Test CI dependencies."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    setup_step = next(s for s in config["jobs"]["test"]["steps"] if s["name"] == "setup-python")
    assert "python-version" in setup_step["with"]
    
    install_step = next(s for s in config["jobs"]["test"]["steps"] if s["name"] == "install-dependencies")
    assert "pip install" in install_step["run"]

def test_ci_testing():
    """Test CI testing."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    test_step = next(s for s in config["jobs"]["test"]["steps"] if s["name"] == "run-tests")
    assert "pytest" in test_step["run"]
    assert "--cov" in test_step["run"]

def test_ci_linting():
    """Test CI linting."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    lint_job = config["jobs"]["lint"]
    required_linters = [
        "flake8",
        "black",
        "isort",
        "mypy"
    ]
    
    for linter in required_linters:
        assert any(linter in s["run"] for s in lint_job["steps"]), f"Missing linter: {linter}"

def test_ci_security():
    """Test CI security."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    security_job = config["jobs"]["security"]
    required_checks = [
        "bandit",
        "safety",
        "dependency-check"
    ]
    
    for check in required_checks:
        assert any(check in s["run"] for s in security_job["steps"]), f"Missing security check: {check}"

def test_ci_build():
    """Test CI build."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    build_job = config["jobs"]["build"]
    required_steps = [
        "build-backend",
        "build-frontend",
        "build-docker"
    ]
    
    for step in required_steps:
        assert any(step in s["name"] for s in build_job["steps"]), f"Missing build step: {step}"

def test_ci_artifacts():
    """Test CI artifacts."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    build_job = config["jobs"]["build"]
    assert any("actions/upload-artifact" in s["uses"] for s in build_job["steps"])

def test_ci_notifications():
    """Test CI notifications."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    assert "notifications" in config
    assert "email" in config["notifications"]
    assert "slack" in config["notifications"]

def test_ci_environment():
    """Test CI environment."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    required_env = [
        "PYTHONPATH",
        "DATABASE_URL",
        "REDIS_URL",
        "OPENAI_API_KEY"
    ]
    
    for env in required_env:
        assert env in config["env"], f"Missing environment variable: {env}"

def test_ci_caching():
    """Test CI caching."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    assert any("actions/cache" in s["uses"] for s in config["jobs"]["test"]["steps"])
    assert any("actions/cache" in s["uses"] for s in config["jobs"]["build"]["steps"])

def test_ci_matrix():
    """Test CI matrix."""
    ci_file = Path(".github/workflows/ci.yml")
    with open(ci_file) as f:
        config = yaml.safe_load(f)
    
    test_job = config["jobs"]["test"]
    assert "matrix" in test_job["strategy"]
    assert "python-version" in test_job["strategy"]["matrix"]
    assert "os" in test_job["strategy"]["matrix"] 