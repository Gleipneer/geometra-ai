"""Tests for documentation."""

import pytest
from pathlib import Path
import yaml
import json
from datetime import datetime
import subprocess
from unittest.mock import Mock, patch

def test_docs_structure():
    """Test documentation directory structure."""
    docs_dir = Path("docs")
    assert docs_dir.exists(), "Missing docs directory"
    
    required_dirs = [
        "api",
        "user",
        "developer"
    ]
    
    for dir_name in required_dirs:
        assert (docs_dir / dir_name).exists(), f"Missing directory: {dir_name}"

def test_api_docs():
    """Test API documentation."""
    api_dir = Path("docs/api")
    assert api_dir.exists(), "Missing API docs directory"
    
    required_files = [
        "index.rst",
        "backend.rst",
        "frontend.rst"
    ]
    
    for file in required_files:
        assert (api_dir / file).exists(), f"Missing file: {file}"

def test_user_docs():
    """Test user documentation."""
    user_dir = Path("docs/user")
    assert user_dir.exists(), "Missing user docs directory"
    
    required_files = [
        "index.rst",
        "installation.rst",
        "usage.rst"
    ]
    
    for file in required_files:
        assert (user_dir / file).exists(), f"Missing file: {file}"

def test_developer_docs():
    """Test developer documentation."""
    dev_dir = Path("docs/developer")
    assert dev_dir.exists(), "Missing developer docs directory"
    
    required_files = [
        "index.rst",
        "setup.rst",
        "contributing.rst"
    ]
    
    for file in required_files:
        assert (dev_dir / file).exists(), f"Missing file: {file}"

def test_sphinx_config():
    """Test Sphinx configuration."""
    conf_file = Path("docs/conf.py")
    assert conf_file.exists(), "Missing Sphinx config file"
    
    with open(conf_file) as f:
        content = f.read()
    
    required_settings = [
        "project",
        "copyright",
        "author",
        "extensions",
        "html_theme"
    ]
    
    for setting in required_settings:
        assert setting in content, f"Missing setting: {setting}"

def test_api_docs_content():
    """Test API documentation content."""
    api_index = Path("docs/api/index.rst")
    assert api_index.exists(), "Missing API index file"
    
    with open(api_index) as f:
        content = f.read()
    
    required_sections = [
        "API Reference",
        "Backend API",
        "Frontend API"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section: {section}"

def test_user_docs_content():
    """Test user documentation content."""
    user_index = Path("docs/user/index.rst")
    assert user_index.exists(), "Missing user index file"
    
    with open(user_index) as f:
        content = f.read()
    
    required_sections = [
        "User Guide",
        "Installation",
        "Usage"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section: {section}"

def test_developer_docs_content():
    """Test developer documentation content."""
    dev_index = Path("docs/developer/index.rst")
    assert dev_index.exists(), "Missing developer index file"
    
    with open(dev_index) as f:
        content = f.read()
    
    required_sections = [
        "Developer Guide",
        "Setup",
        "Contributing"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section: {section}"

def test_docs_links():
    """Test documentation links."""
    index_file = Path("docs/index.rst")
    assert index_file.exists(), "Missing main index file"
    
    with open(index_file) as f:
        content = f.read()
    
    required_links = [
        "api/index",
        "user/index",
        "developer/index"
    ]
    
    for link in required_links:
        assert link in content, f"Missing link: {link}"

def test_docs_theme():
    """Test documentation theme."""
    conf_file = Path("docs/conf.py")
    assert conf_file.exists(), "Missing Sphinx config file"
    
    with open(conf_file) as f:
        content = f.read()
    
    assert "sphinx_rtd_theme" in content, "Missing RTD theme"

def test_docs_extensions():
    """Test documentation extensions."""
    conf_file = Path("docs/conf.py")
    assert conf_file.exists(), "Missing Sphinx config file"
    
    with open(conf_file) as f:
        content = f.read()
    
    required_extensions = [
        "sphinx.ext.autodoc",
        "sphinx.ext.napoleon",
        "sphinx.ext.viewcode"
    ]
    
    for extension in required_extensions:
        assert extension in content, f"Missing extension: {extension}"

def test_docs_build():
    """Test documentation build."""
    build_dir = Path("docs/_build")
    assert build_dir.exists(), "Missing build directory"
    
    required_dirs = [
        "html",
        "doctrees"
    ]
    
    for dir_name in required_dirs:
        assert (build_dir / dir_name).exists(), f"Missing directory: {dir_name}"

def test_docs_assets():
    """Test documentation assets."""
    static_dir = Path("docs/_static")
    assert static_dir.exists(), "Missing static directory"
    
    required_files = [
        "css",
        "js",
        "images"
    ]
    
    for file in required_files:
        assert (static_dir / file).exists(), f"Missing file: {file}"

def test_docs_templates():
    """Test documentation templates."""
    templates_dir = Path("docs/_templates")
    assert templates_dir.exists(), "Missing templates directory"
    
    required_files = [
        "layout.html",
        "page.html"
    ]
    
    for file in required_files:
        assert (templates_dir / file).exists(), f"Missing file: {file}" 