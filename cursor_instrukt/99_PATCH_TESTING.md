# Testning och Kvalitetssäkring Implementation

## 1. Implementera Backend-tester

### tests/conftest.py
```python
"""Test configuration."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..api.database import Base, get_db
from ..api.main import app
import os

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Database fixture."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Test client fixture."""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db):
    """Test user fixture."""
    from ..api.models.user import UserInDB
    from ..api.utils.auth import get_password_hash
    
    user = UserInDB(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_token(client, test_user):
    """Test token fixture."""
    response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": "testpass"
        }
    )
    return response.json()["access_token"]
```

### tests/test_auth.py
```python
"""Authentication tests."""
import pytest
from fastapi import status

def test_register(client):
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "hashed_password" not in data

def test_login(client, test_user):
    """Test user login."""
    response = client.post(
        "/auth/token",
        data={
            "username": test_user.username,
            "password": "testpass"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client, test_token):
    """Test get current user."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
```

### tests/test_ai.py
```python
"""AI endpoint tests."""
import pytest
from fastapi import status

def test_chat(client, test_token):
    """Test chat endpoint."""
    response = client.post(
        "/ai/chat",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "message": "Test message",
            "context": "Test context"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "response" in data
    assert "metadata" in data

def test_memory_operations(client, test_token):
    """Test memory operations."""
    # Store memory
    store_response = client.post(
        "/ai/memory",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "content": "Test memory",
            "metadata": {
                "source": "test",
                "timestamp": "2024-01-01T00:00:00Z",
                "user_id": "test"
            },
            "tags": ["test"]
        }
    )
    assert store_response.status_code == status.HTTP_200_OK
    memory_id = store_response.json()["id"]

    # Query memory
    query_response = client.get(
        "/ai/memory",
        headers={"Authorization": f"Bearer {test_token}"},
        params={"query": "Test memory"}
    )
    assert query_response.status_code == status.HTTP_200_OK
    data = query_response.json()
    assert len(data) > 0
    assert data[0]["content"] == "Test memory"

    # Delete memory
    delete_response = client.delete(
        f"/ai/memory/{memory_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert delete_response.status_code == status.HTTP_200_OK
```

## 2. Implementera Frontend-tester

### src/frontend/components/__tests__/Login.test.tsx
```typescript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Login } from '../Login';
import { useAuth } from '../../hooks/useAuth';
import { MemoryRouter } from 'react-router-dom';

// Mock useAuth hook
jest.mock('../../hooks/useAuth');

describe('Login Component', () => {
  const mockLogin = jest.fn();
  const mockNavigate = jest.fn();

  beforeEach(() => {
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
    });
  });

  it('renders login form', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/användarnamn/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/lösenord/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /logga in/i })).toBeInTheDocument();
  });

  it('handles login submission', async () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/användarnamn/i), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByLabelText(/lösenord/i), {
      target: { value: 'testpass' },
    });

    fireEvent.click(screen.getByRole('button', { name: /logga in/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('testuser', 'testpass');
    });
  });

  it('displays error message on login failure', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'));

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/användarnamn/i), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByLabelText(/lösenord/i), {
      target: { value: 'wrongpass' },
    });

    fireEvent.click(screen.getByRole('button', { name: /logga in/i }));

    await waitFor(() => {
      expect(screen.getByText(/felaktigt användarnamn eller lösenord/i)).toBeInTheDocument();
    });
  });
});
```

### src/frontend/hooks/__tests__/useAuth.test.ts
```typescript
import { renderHook, act } from '@testing-library/react-hooks';
import { useAuth } from '../useAuth';
import { useApi } from '../useApi';

// Mock useApi hook
jest.mock('../useApi');

describe('useAuth Hook', () => {
  const mockPost = jest.fn();
  const mockNavigate = jest.fn();

  beforeEach(() => {
    (useApi as jest.Mock).mockReturnValue({
      post: mockPost,
    });
    localStorage.clear();
  });

  it('initializes with no user', () => {
    const { result } = renderHook(() => useAuth());
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });

  it('handles successful login', async () => {
    const mockResponse = {
      access_token: 'test-token',
      user: {
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
      },
    };

    mockPost.mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login('testuser', 'testpass');
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockResponse.user);
    expect(localStorage.getItem('token')).toBe('test-token');
  });

  it('handles logout', async () => {
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('user', JSON.stringify({ id: '1', username: 'testuser' }));

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });
});
```

## 3. Implementera Integrationstester

### tests/integration/test_api_integration.py
```python
"""API integration tests."""
import pytest
from fastapi import status
import time

def test_chat_flow(client, test_token):
    """Test complete chat flow."""
    # Send initial message
    response = client.post(
        "/ai/chat",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "message": "Hej, kan du hjälpa mig med en geometrisk beräkning?",
            "context": "Geometrisk beräkning"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    initial_response = response.json()
    assert "response" in initial_response

    # Store memory
    memory_response = client.post(
        "/ai/memory",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "content": initial_response["response"],
            "metadata": {
                "source": "chat",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "user_id": "test"
            },
            "tags": ["geometri", "beräkning"]
        }
    )
    assert memory_response.status_code == status.HTTP_200_OK
    memory_id = memory_response.json()["id"]

    # Query memory
    query_response = client.get(
        "/ai/memory",
        headers={"Authorization": f"Bearer {test_token}"},
        params={"query": "geometrisk beräkning"}
    )
    assert query_response.status_code == status.HTTP_200_OK
    memories = query_response.json()
    assert len(memories) > 0
    assert any(m["id"] == memory_id for m in memories)

    # Follow-up message with context
    followup_response = client.post(
        "/ai/chat",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "message": "Kan du förklara mer detaljerat?",
            "context": "Följdfråga om geometrisk beräkning"
        }
    )
    assert followup_response.status_code == status.HTTP_200_OK
    followup_data = followup_response.json()
    assert "response" in followup_data
    assert len(followup_data["response"]) > 0
```

## 4. Implementera Prestandatester

### tests/performance/test_performance.py
```python
"""Performance tests."""
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi import status

def test_chat_response_time(client, test_token):
    """Test chat response time."""
    start_time = time.time()
    
    response = client.post(
        "/ai/chat",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "message": "Test message",
            "context": "Test context"
        }
    )
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == status.HTTP_200_OK
    assert response_time < 2.0  # Max 2 sekunder svarstid

def test_concurrent_requests(client, test_token):
    """Test concurrent requests."""
    def make_request():
        return client.post(
            "/ai/chat",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "message": "Test message",
                "context": "Test context"
            }
        )
    
    # Gör 10 samtidiga requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        start_time = time.time()
        responses = list(executor.map(make_request, range(10)))
        end_time = time.time()
    
    total_time = end_time - start_time
    
    # Verifiera alla svar
    for response in responses:
        assert response.status_code == status.HTTP_200_OK
    
    # Verifiera total tid
    assert total_time < 5.0  # Max 5 sekunder för alla requests
```

## 5. Implementera Kodkvalitetskontroller

### .pre-commit-config.yaml
```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        language_version: python3.9

-   repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        additional_dependencies: [flake8-docstrings]

-   repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
    -   id: isort

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        additional_dependencies: [types-all]
```

### .eslintrc.js
```javascript
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:prettier/recommended',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: ['react', '@typescript-eslint', 'prettier'],
  rules: {
    'prettier/prettier': 'error',
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
```

## 6. Verifiera Implementation

```bash
# Installera pre-commit hooks
pre-commit install

# Kör backend-tester
pytest

# Kör frontend-tester
cd frontend
npm test

# Kör kodkvalitetskontroller
pre-commit run --all-files
cd frontend
npm run lint
```

## 7. Nästa steg

Efter att ha implementerat testning och kvalitetssäkring, kör:

```bash
# Generera testrapport
pytest --cov=src --cov-report=html

# Kör prestandatester
pytest tests/performance/

# Verifiera kodtäckning
coverage report
```

Detta implementerar:
- Enhetstester för backend
- Enhetstester för frontend
- Integrationstester
- Prestandatester
- Kodkvalitetskontroller
- Automatiserad testning
- Kodtäckningsrapporter
- Pre-commit hooks

Nästa steg är att implementera deployment och CI/CD. 