# AI Setup

## Konfiguration

1. Installera OpenAI-paketet:
```bash
pip install openai
```

2. Konfigurera API-nyckel:
```bash
export OPENAI_API_KEY=your-api-key-here
```

## Komponenter

### AI Service
```python
# src/ai/service.py
from openai import OpenAI

class AIService:
    def __init__(self):
        self.client = OpenAI()
    
    async def generate_response(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

### Prompt Hantering
```python
# src/ai/prompts.py
class PromptManager:
    def __init__(self):
        self.templates = {}
    
    def load_template(self, name: str, template: str):
        self.templates[name] = template
    
    def format_prompt(self, name: str, **kwargs) -> str:
        return self.templates[name].format(**kwargs)
```

### Kontext Hantering
```python
# src/ai/context.py
class ContextManager:
    def __init__(self):
        self.context = []
    
    def add_to_context(self, role: str, content: str):
        self.context.append({"role": role, "content": content})
    
    def get_context(self) -> list:
        return self.context
```

## Användning

1. Initiera AI-tjänsten:
```python
from src.ai.service import AIService

ai_service = AIService()
```

2. Generera svar:
```python
response = await ai_service.generate_response("Din prompt här")
```

## Caching

1. Konfigurera Redis-cache:
```python
# src/ai/cache.py
import redis

class AICache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    def get_cached_response(self, prompt: str) -> str:
        return self.redis.get(prompt)
    
    def cache_response(self, prompt: str, response: str):
        self.redis.set(prompt, response)
```

## Testning

1. Kör AI-tester:
```bash
pytest tests/unit/ai/
```

2. Verifiera integration:
```bash
pytest tests/integration/ai/
```

## Monitoring

1. Logga AI-användning:
```python
# src/ai/monitoring.py
import logging

logger = logging.getLogger('ai')

def log_ai_request(prompt: str, response: str):
    logger.info(f"AI Request: {prompt}")
    logger.info(f"AI Response: {response}")
```

## Säkerhet

1. Validera prompts:
```python
# src/ai/security.py
def validate_prompt(prompt: str) -> bool:
    # Implementera prompt-validering
    return True
```

2. Begränsa användning:
```python
# src/ai/rate_limiter.py
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=60)
def rate_limited_request():
    pass
```
