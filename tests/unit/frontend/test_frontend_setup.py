"""Tests for frontend setup."""

import pytest
from pathlib import Path
import json
import yaml

def test_frontend_structure():
    """Test frontend directory structure."""
    frontend_dir = Path("src/frontend")
    assert frontend_dir.exists(), "Missing frontend directory"
    
    required_dirs = [
        "components",
        "pages",
        "styles",
        "utils",
        "hooks",
        "context",
        "api"
    ]
    
    for dir_name in required_dirs:
        assert (frontend_dir / dir_name).exists(), f"Missing frontend directory: {dir_name}"

def test_frontend_dependencies():
    """Test frontend dependencies."""
    package_json = Path("src/frontend/package.json")
    assert package_json.exists(), "Missing package.json"
    
    with open(package_json) as f:
        data = json.load(f)
    
    required_dependencies = [
        "react",
        "react-dom",
        "next",
        "typescript",
        "@emotion/react",
        "@emotion/styled",
        "@mui/material",
        "@mui/icons-material"
    ]
    
    for dep in required_dependencies:
        assert dep in data["dependencies"], f"Missing dependency: {dep}"

def test_frontend_configuration():
    """Test frontend configuration."""
    # Test Next.js config
    next_config = Path("src/frontend/next.config.js")
    assert next_config.exists(), "Missing next.config.js"
    
    # Test TypeScript config
    ts_config = Path("src/frontend/tsconfig.json")
    assert ts_config.exists(), "Missing tsconfig.json"
    
    with open(ts_config) as f:
        data = json.load(f)
    
    assert "compilerOptions" in data
    assert "strict" in data["compilerOptions"]
    assert data["compilerOptions"]["strict"] is True

def test_frontend_components():
    """Test frontend components."""
    components_dir = Path("src/frontend/components")
    assert components_dir.exists(), "Missing components directory"
    
    required_components = [
        "Layout",
        "Header",
        "Footer",
        "Sidebar",
        "Button",
        "Input",
        "Card",
        "Table"
    ]
    
    for component in required_components:
        assert (components_dir / f"{component}.tsx").exists(), f"Missing component: {component}"

def test_frontend_pages():
    """Test frontend pages."""
    pages_dir = Path("src/frontend/pages")
    assert pages_dir.exists(), "Missing pages directory"
    
    required_pages = [
        "index",
        "login",
        "register",
        "dashboard",
        "projects",
        "documents",
        "analysis"
    ]
    
    for page in required_pages:
        assert (pages_dir / f"{page}.tsx").exists(), f"Missing page: {page}"

def test_frontend_styles():
    """Test frontend styles."""
    styles_dir = Path("src/frontend/styles")
    assert styles_dir.exists(), "Missing styles directory"
    
    required_styles = [
        "globals.css",
        "theme.ts",
        "variables.css"
    ]
    
    for style in required_styles:
        assert (styles_dir / style).exists(), f"Missing style: {style}"

def test_frontend_utils():
    """Test frontend utilities."""
    utils_dir = Path("src/frontend/utils")
    assert utils_dir.exists(), "Missing utils directory"
    
    required_utils = [
        "api.ts",
        "auth.ts",
        "validation.ts",
        "formatting.ts"
    ]
    
    for util in required_utils:
        assert (utils_dir / util).exists(), f"Missing utility: {util}"

def test_frontend_hooks():
    """Test frontend hooks."""
    hooks_dir = Path("src/frontend/hooks")
    assert hooks_dir.exists(), "Missing hooks directory"
    
    required_hooks = [
        "useAuth.ts",
        "useApi.ts",
        "useForm.ts",
        "useTheme.ts"
    ]
    
    for hook in required_hooks:
        assert (hooks_dir / hook).exists(), f"Missing hook: {hook}"

def test_frontend_context():
    """Test frontend context."""
    context_dir = Path("src/frontend/context")
    assert context_dir.exists(), "Missing context directory"
    
    required_contexts = [
        "AuthContext.tsx",
        "ThemeContext.tsx",
        "ApiContext.tsx"
    ]
    
    for context in required_contexts:
        assert (context_dir / context).exists(), f"Missing context: {context}"

def test_frontend_api():
    """Test frontend API integration."""
    api_dir = Path("src/frontend/api")
    assert api_dir.exists(), "Missing API directory"
    
    required_api_files = [
        "client.ts",
        "endpoints.ts",
        "types.ts"
    ]
    
    for file in required_api_files:
        assert (api_dir / file).exists(), f"Missing API file: {file}"

def test_frontend_tests():
    """Test frontend test setup."""
    tests_dir = Path("src/frontend/__tests__")
    assert tests_dir.exists(), "Missing tests directory"
    
    required_test_files = [
        "setup.ts",
        "utils.ts",
        "mocks.ts"
    ]
    
    for file in required_test_files:
        assert (tests_dir / file).exists(), f"Missing test file: {file}" 