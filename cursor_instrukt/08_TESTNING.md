# 🧪 08: Testning

## 🎯 Syfte
Implementera omfattande testning av:
- Unit-tester
- Integrationstester
- E2E-tester
- Prestandatester

## 📦 Komponenter

### 1. Unit Tests
- API endpoints
- Minneshantering
- Fallback-logik
- Promptbuilder

### 2. Integration Tests
- API + Minne
- Minne + Fallback
- API + Fallback
- Full stack

### 3. E2E Tests
- Chat-flöde
- Minneshantering
- Fallback-scenarion
- Error handling

## 🛠️ Installation

1. **Skapa Test-struktur**
```bash
mkdir -p tests/{unit,integration,e2e,fixtures}
touch tests/{__init__.py,conftest.py}
```

2. **Implementera Unit Tests**
```python
# tests/unit/test_api.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_endpoint():
    response = client.post(
        "/chat",
        json={"user_id": "test", "message": "Hej!"}
    )
    assert response.status_code == 200
    assert "response" in response.json()

def test_memory_endpoint():
    response = client.post(
        "/memory",
        json={"user_id": "test", "content": "Testminne"}
    )
    assert response.status_code == 200
    assert "stored" in response.json()
```

3. **Implementera Integration Tests**
```python
# tests/integration/test_memory_api.py
import pytest
from api.main import app
from memory.manager import MemoryManager

@pytest.fixture
def memory_manager():
    return MemoryManager()

def test_chat_with_memory(memory_manager):
    # Spara minne
    memory_manager.store(
        user_id="test",
        content="Viktig information",
        metadata={"type": "note"}
    )
    
    # Testa chat med minne
    response = app.post(
        "/chat",
        json={
            "user_id": "test",
            "message": "Vad sa jag senast?"
        }
    )
    assert response.status_code == 200
    assert "Viktig information" in response.json()["response"]
```

4. **Implementera E2E Tests**
```python
# tests/e2e/test_full_flow.py
import pytest
import requests
import time

def test_full_chat_flow():
    # Starta systemet
    system = start_system()
    assert system.is_running()
    
    # Skicka chat
    response = send_chat("Hej!", "test_user")
    assert response.status_code == 200
    
    # Verifiera minne
    memory = check_memory("test_user")
    assert "Hej!" in memory
    
    # Testa fallback
    response = send_chat("Komplex fråga", "test_user")
    assert response.status_code == 200
    assert response.json()["model"] == "gpt-3.5-turbo"
```

5. **Skapa Test Fixtures**
```python
# tests/fixtures/test_data.py
TEST_MESSAGES = [
    "Hej!",
    "Vad är Geometra?",
    "Hur funkar minnet?",
    "Vad sa jag senast?"
]

TEST_MEMORY = [
    {
        "user_id": "test",
        "content": "Viktig information",
        "metadata": {"type": "note"}
    },
    {
        "user_id": "test",
        "content": "Budget: 1000kr",
        "metadata": {"type": "budget"}
    }
]
```

## 🔧 Konfiguration

1. **Skapa pytest.ini**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=api --cov=memory --cov=ai
```

2. **Skapa conftest.py**
```python
# tests/conftest.py
import pytest
import os
from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def load_env():
    load_dotenv()

@pytest.fixture
def test_client():
    from api.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture
def memory_manager():
    from memory.manager import MemoryManager
    return MemoryManager()
```

## ✅ Validering

Kör följande för att verifiera tester:

```bash
# Kör alla tester
pytest

# Kör med coverage
pytest --cov

# Kör specifika tester
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## 🔍 Felsökning

### Vanliga problem

1. **Tester failar**
```bash
# Kör med debug
pytest -vv --pdb

# Kontrollera loggar
cat logs/test.log
```

2. **Coverage för låg**
```bash
# Generera coverage rapport
pytest --cov --cov-report=html

# Öppna rapport
open htmlcov/index.html
```

3. **Integrationstester failar**
```bash
# Verifiera dependencies
python scripts/check_dependencies.py

# Kontrollera miljövariabler
cat .env
```

## 📝 Loggning

```bash
echo "$(date) - 08_TESTNING: Tester konfigurerade" >> bootstrap_status.log
```

## 🔄 Rollback

Om tester behöver återställas:

```bash
# Återställ till senaste version
git checkout -- tests/

# Rensa cache
pytest --cache-clear
```

## 🧪 Ytterligare Testfall

### 1. GPT-4 Failure
```python
def test_gpt4_failure():
    with patch('openai.ChatCompletion.create', side_effect=Exception):
        response = client.post(
            "/chat",
            json={"user_id": "test", "message": "Komplex fråga"}
        )
        assert response.json()["model"] == "gpt-3.5-turbo"
```

### 2. Memory Miss
```python
def test_memory_miss():
    with patch('redis.Redis.get', side_effect=Exception):
        response = client.post(
            "/memory",
            json={"user_id": "test", "content": "Test"}
        )
        assert response.status_code == 500
```

### 3. API Timeout
```python
def test_api_timeout():
    with patch('requests.post', side_effect=Timeout):
        response = client.post(
            "/chat",
            json={"user_id": "test", "message": "Test"}
        )
        assert response.status_code == 504
```

### 4. Invalid Input
```python
def test_invalid_input():
    response = client.post(
        "/chat",
        json={"invalid": "data"}
    )
    assert response.status_code == 422
```

## 📊 Prestandatester

```python
def test_performance():
    start_time = time.time()
    
    # Kör 100 requests
    for _ in range(100):
        response = client.post(
            "/chat",
            json={"user_id": "test", "message": "Test"}
        )
        assert response.status_code == 200
    
    # Verifiera prestanda
    total_time = time.time() - start_time
    assert total_time < 10  # Max 10 sekunder
```