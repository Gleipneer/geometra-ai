# AI-komponenter och tester

## 1. Skapa AI-teststruktur
```bash
# Skapa testkataloger
mkdir -p tests/unit/ai/{prompt,chat,fallback,memory}
mkdir -p tests/integration/ai
```

## 2. Implementera prompt-tester
```python
# tests/unit/ai/prompt/test_prompt_manager.py
import pytest
from src.ai.prompt import PromptManager

@pytest.fixture
def prompt_manager():
    return PromptManager()

def test_prompt_template_loading(prompt_manager):
    """Test loading prompt templates."""
    template = "Hello {name}!"
    prompt_manager.load_template("greeting", template)
    assert prompt_manager.get_template("greeting") == template

def test_prompt_formatting(prompt_manager):
    """Test prompt formatting with variables."""
    template = "Hello {name}!"
    prompt_manager.load_template("greeting", template)
    formatted = prompt_manager.format_prompt("greeting", name="World")
    assert formatted == "Hello World!"

def test_prompt_validation(prompt_manager):
    """Test prompt validation."""
    template = "Hello {name}!"
    prompt_manager.load_template("greeting", template)
    assert prompt_manager.validate_prompt("greeting", {"name": "World"})
    assert not prompt_manager.validate_prompt("greeting", {})
```

## 3. Implementera chat-tester
```python
# tests/unit/ai/chat/test_chat_manager.py
import pytest
from src.ai.chat import ChatManager

@pytest.fixture
def chat_manager():
    return ChatManager()

def test_chat_history(chat_manager):
    """Test chat history management."""
    chat_manager.add_message("user", "Hello")
    chat_manager.add_message("assistant", "Hi there!")
    history = chat_manager.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

def test_chat_context(chat_manager):
    """Test chat context management."""
    chat_manager.set_context({"user_id": "123"})
    assert chat_manager.get_context()["user_id"] == "123"
```

## 4. Implementera fallback-tester
```python
# tests/unit/ai/fallback/test_fallback_manager.py
import pytest
from src.ai.fallback import FallbackManager

@pytest.fixture
def fallback_manager():
    return FallbackManager()

def test_fallback_trigger(fallback_manager):
    """Test fallback trigger conditions."""
    assert fallback_manager.should_trigger({"error": "timeout"})
    assert not fallback_manager.should_trigger({"status": "success"})

def test_fallback_strategy(fallback_manager):
    """Test fallback strategy selection."""
    strategy = fallback_manager.select_strategy({"error": "timeout"})
    assert strategy in ["retry", "simplify", "fallback"]
```

## 5. Implementera minnes-tester
```python
# tests/unit/ai/memory/test_memory_manager.py
import pytest
from src.ai.memory import MemoryManager

@pytest.fixture
def memory_manager():
    return MemoryManager()

def test_memory_storage(memory_manager):
    """Test memory storage and retrieval."""
    memory_manager.store("user_123", "key", "value")
    assert memory_manager.retrieve("user_123", "key") == "value"

def test_memory_expiration(memory_manager):
    """Test memory expiration."""
    memory_manager.store("user_123", "key", "value", ttl=1)
    import time
    time.sleep(2)
    assert memory_manager.retrieve("user_123", "key") is None
```

## 6. Implementera integrationstester
```python
# tests/integration/ai/test_ai_integration.py
import pytest
from src.ai import AIService
from src.ai.prompt import PromptManager
from src.ai.chat import ChatManager
from src.ai.fallback import FallbackManager
from src.ai.memory import MemoryManager

@pytest.fixture
def ai_service():
    return AIService(
        prompt_manager=PromptManager(),
        chat_manager=ChatManager(),
        fallback_manager=FallbackManager(),
        memory_manager=MemoryManager()
    )

def test_complete_ai_flow(ai_service):
    """Test complete AI interaction flow."""
    # Setup
    ai_service.prompt_manager.load_template("greeting", "Hello {name}!")
    ai_service.chat_manager.set_context({"user_id": "123"})
    
    # Test flow
    response = ai_service.process_request({
        "prompt": "greeting",
        "variables": {"name": "World"},
        "context": {"user_id": "123"}
    })
    
    assert response["status"] == "success"
    assert "Hello World" in response["message"]
```

## 7. Kör testerna
```bash
# Kör alla AI-tester
pytest tests/unit/ai tests/integration/ai -v
``` 