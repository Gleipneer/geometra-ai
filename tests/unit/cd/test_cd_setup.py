"""Tests for CD setup."""

import pytest
from pathlib import Path
import yaml
import json
from datetime import datetime
import subprocess
from unittest.mock import Mock, patch

def test_cd_structure():
    """Test CD directory structure."""
    cd_dir = Path(".github/workflows")
    assert cd_dir.exists(), "Missing CD directory"
    
    required_files = [
        "cd.yml",
        "deploy-staging.yml",
        "deploy-production.yml"
    ]
    
    for file in required_files:
        assert (cd_dir / file).exists(), f"Missing CD file: {file}"

def test_cd_configuration():
    """Test CD configuration."""
    cd_file = Path(".github/workflows/cd.yml")
    assert cd_file.exists(), "Missing CD configuration"
    
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    required_config = [
        "name",
        "on",
        "jobs",
        "steps"
    ]
    
    for key in required_config:
        assert key in config, f"Missing configuration key: {key}"

def test_cd_jobs():
    """Test CD jobs."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    required_jobs = [
        "deploy-staging",
        "deploy-production",
        "rollback"
    ]
    
    for job in required_jobs:
        assert job in config["jobs"], f"Missing job: {job}"

def test_cd_steps():
    """Test CD steps."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    deploy_job = config["jobs"]["deploy-staging"]
    required_steps = [
        "checkout",
        "setup-python",
        "configure-aws",
        "deploy"
    ]
    
    for step in required_steps:
        assert any(s["name"] == step for s in deploy_job["steps"]), f"Missing step: {step}"

def test_cd_aws_config():
    """Test CD AWS configuration."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    aws_step = next(s for s in config["jobs"]["deploy-staging"]["steps"] if s["name"] == "configure-aws")
    assert "aws-actions/configure-aws-credentials" in aws_step["uses"]
    assert "aws-region" in aws_step["with"]

def test_cd_deployment():
    """Test CD deployment."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    deploy_step = next(s for s in config["jobs"]["deploy-staging"]["steps"] if s["name"] == "deploy")
    assert "serverless deploy" in deploy_step["run"]
    assert "--stage staging" in deploy_step["run"]

def test_cd_rollback():
    """Test CD rollback."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    rollback_job = config["jobs"]["rollback"]
    assert "serverless rollback" in rollback_job["steps"][-1]["run"]

def test_cd_environment():
    """Test CD environment."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    required_env = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "STAGE"
    ]
    
    for env in required_env:
        assert env in config["env"], f"Missing environment variable: {env}"

def test_cd_secrets():
    """Test CD secrets."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    required_secrets = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "DOCKER_USERNAME",
        "DOCKER_PASSWORD"
    ]
    
    for secret in required_secrets:
        assert secret in config["env"], f"Missing secret: {secret}"

def test_cd_conditions():
    """Test CD conditions."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    deploy_job = config["jobs"]["deploy-production"]
    assert "if" in deploy_job
    assert "github.ref == 'refs/heads/main'" in deploy_job["if"]

def test_cd_notifications():
    """Test CD notifications."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    assert "notifications" in config
    assert "email" in config["notifications"]
    assert "slack" in config["notifications"]

def test_cd_timeouts():
    """Test CD timeouts."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    deploy_job = config["jobs"]["deploy-staging"]
    assert "timeout-minutes" in deploy_job

def test_cd_artifacts():
    """Test CD artifacts."""
    cd_file = Path(".github/workflows/cd.yml")
    with open(cd_file) as f:
        config = yaml.safe_load(f)
    
    deploy_job = config["jobs"]["deploy-staging"]
    assert any("actions/upload-artifact" in s["uses"] for s in deploy_job["steps"]) 