# Tester

Detta dokument beskriver hur man implementerar och kör tester för Geometra AI-systemet.

## Översikt

Testsystemet innehåller:

1. **Enhetstester**
   - Backend-tester
   - Frontend-tester
   - Utilitetstester

2. **Integrationstester**
   - API-tester
   - Databastester
   - Minnestester

3. **Prestandatester**
   - Belastningstester
   - Stresstester
   - Skalningstester

## Installation

1. Installera testverktyg för backend:
```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-env
```

2. Installera testverktyg för frontend:
```bash
cd frontend
pnpm add -D jest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

## Konfiguration

### Backend-tester

1. Skapa `tests/conftest.py`:
```python
"""Backend test configuration."""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from memory.chroma.manager import ChromaManager
from memory.redis.manager import RedisManager

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def chroma_manager():
    """Create ChromaDB manager."""
    return ChromaManager()

@pytest.fixture
def redis_manager():
    """Create Redis manager."""
    return RedisManager()
```

2. Skapa `tests/test_api.py`:
```python
"""API tests."""

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_endpoint(client):
    """Test chat endpoint."""
    response = client.post(
        "/chat",
        json={"message": "Test message"}
    )
    assert response.status_code == 200
    assert "response" in response.json()

def test_system_status(client):
    """Test system status endpoint."""
    response = client.get("/system/status")
    assert response.status_code == 200
    assert "version" in response.json()
```

3. Skapa `tests/test_memory.py`:
```python
"""Memory tests."""

def test_chroma_add_memory(chroma_manager):
    """Test adding memory to ChromaDB."""
    memory = {
        "text": "Test memory",
        "metadata": {"type": "test"}
    }
    result = chroma_manager.add_memory(memory)
    assert result is not None

def test_redis_set_context(redis_manager):
    """Test setting context in Redis."""
    context = {
        "session_id": "test",
        "data": {"key": "value"}
    }
    result = redis_manager.set_context(context)
    assert result is True
```

### Frontend-tester

1. Skapa `frontend/jest.config.js`:
```javascript
/** Frontend test configuration. */

module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
  },
};
```

2. Skapa `frontend/src/components/__tests__/ChatInterface.test.tsx`:
```typescript
/** Chat interface tests. */

import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInterface } from '../Chat/ChatInterface';

describe('ChatInterface', () => {
  it('renders chat interface', () => {
    render(<ChatInterface />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('sends message', async () => {
    render(<ChatInterface />);
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(button);

    expect(await screen.findByText('Test message')).toBeInTheDocument();
  });
});
```

3. Skapa `frontend/src/components/__tests__/GeometryCanvas.test.tsx`:
```typescript
/** Geometry canvas tests. */

import { render, screen } from '@testing-library/react';
import { GeometryCanvas } from '../Visualization/GeometryCanvas';

describe('GeometryCanvas', () => {
  it('renders canvas', () => {
    render(<GeometryCanvas />);
    expect(screen.getByRole('canvas')).toBeInTheDocument();
  });

  it('draws shapes', () => {
    render(<GeometryCanvas />);
    const canvas = screen.getByRole('canvas');
    const ctx = canvas.getContext('2d');
    
    // Draw test shape
    ctx.beginPath();
    ctx.rect(10, 10, 100, 100);
    ctx.stroke();
    
    // Verify drawing
    const imageData = ctx.getImageData(10, 10, 1, 1);
    expect(imageData.data[3]).toBeGreaterThan(0);
  });
});
```

### Prestandatester

1. Skapa `tests/performance/test_load.py`:
```python
"""Load testing."""

import locust
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    """Simulate chat user."""
    wait_time = between(1, 5)

    @task
    def send_message(self):
        """Send chat message."""
        self.client.post(
            "/chat",
            json={"message": "Test message"}
        )

    @task
    def get_status(self):
        """Get system status."""
        self.client.get("/system/status")
```

2. Skapa `tests/performance/test_stress.py`:
```python
"""Stress testing."""

import pytest
import asyncio
from api.main import app
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test concurrent requests."""
    client = TestClient(app)
    tasks = []

    for _ in range(100):
        tasks.append(
            asyncio.create_task(
                client.post(
                    "/chat",
                    json={"message": "Test message"}
                )
            )
        )

    responses = await asyncio.gather(*tasks)
    assert all(r.status_code == 200 for r in responses)
```

## Validering

1. Kör backend-tester:
```bash
pytest tests/ -v --cov=api --cov=memory
```

2. Kör frontend-tester:
```bash
cd frontend
pnpm test
```

3. Kör prestandatester:
```bash
locust -f tests/performance/test_load.py
```

## Felsökning

### Testproblem

1. **Backend-problem**
   - Kontrollera fixtures
   - Verifiera mockar
   - Validera assertions

2. **Frontend-problem**
   - Kontrollera render
   - Verifiera events
   - Validera state

3. **Prestandaproblem**
   - Kontrollera belastning
   - Verifiera resurser
   - Validera svarstider

## Loggning

1. Konfigurera loggning i `tests/utils/logging.py`:
```python
"""Test logging configuration."""

import logging
import os
from datetime import datetime

def setup_test_logging():
    """Configure logging for tests."""
    log_dir = "logs/tests"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"tests_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
```

## Nästa steg

1. Konfigurera [Övervakning](12_ÖVERVAKNING.md)
2. Skapa [Arkitekturdiagram](13_ARKITEKTUR.md)
3. Implementera [CI/CD](14_CI_CD.md) 