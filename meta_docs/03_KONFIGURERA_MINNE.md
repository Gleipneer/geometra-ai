# Konfigurera Minneskomponenter

Detta dokument beskriver hur man konfigurerar och integrerar minneskomponenterna i Geometra AI-systemet.

## Minneskomponenter

Systemet använder två huvudsakliga minneskomponenter:

1. **ChromaDB** - Långtidsminne (LTM)
   - Vektorembeddingar för semantisk sökning
   - Persistent lagring av konversationshistorik
   - Metadata för kontext-hantering

2. **Redis** - Korttidsminne (STM)
   - Temporär lagring av aktiva konversationer
   - Snabb åtkomst till kontext
   - TTL-baserad cache

## Installation

### ChromaDB

1. Installera ChromaDB:
```bash
pip install chromadb
```

2. Starta ChromaDB-tjänsten:
```bash
docker-compose up -d chromadb
```

### Redis

1. Installera Redis-klient:
```bash
pip install redis
```

2. Starta Redis-tjänsten:
```bash
docker-compose up -d redis
```

## Konfiguration

### ChromaDB-konfiguration

1. Skapa `memory/chroma/manager.py`:
```python
"""ChromaDB manager for long-term memory."""

from chromadb import Client, Settings
from typing import List, Dict, Any

class ChromaManager:
    """Manages ChromaDB operations for long-term memory."""
    
    def __init__(self, host: str = "localhost", port: int = 8001):
        """Initialize ChromaDB client and collection."""
        self.client = Client(Settings(
            chroma_api_impl="rest",
            chroma_server_host=host,
            chroma_server_http_port=port
        ))
        self.collection = self.client.get_or_create_collection("geometra_memory")
    
    def add_memory(self, text: str, metadata: Dict[str, Any]) -> str:
        """Add a memory to the collection."""
        return self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[metadata.get("id", str(hash(text)))]
        )
    
    def get_memory(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories based on semantic similarity."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return [
            {
                "text": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
```

### Redis-konfiguration

1. Skapa `memory/redis/manager.py`:
```python
"""Redis manager for short-term memory."""

import redis
from typing import Optional, Dict, Any

class RedisManager:
    """Manages Redis operations for short-term memory."""
    
    def __init__(self, url: str = "redis://localhost:6379"):
        """Initialize Redis client."""
        self.client = redis.from_url(url)
    
    def set_context(self, session_id: str, context: Dict[str, Any], ttl: int = 600):
        """Store context for a session."""
        self.client.setex(
            f"context:{session_id}",
            ttl,
            str(context)
        )
    
    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve context for a session."""
        data = self.client.get(f"context:{session_id}")
        return eval(data) if data else None
```

### Minneskonfiguration

1. Skapa `memory/config.py`:
```python
"""Memory configuration settings."""

from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import field_validator

class MemorySettings(BaseSettings):
    """Settings for memory components."""
    
    # ChromaDB Settings
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_OPENAI_API_KEY: Optional[str] = None
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_TTL_SECONDS: int = 600
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    FALLBACK_OPENAI_API_KEY: Optional[str] = None
    
    # Model Settings
    DEFAULT_MODEL: str = "gpt-4"
    FALLBACK_MODEL: str = "gpt-3.5-turbo"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    
    # API Settings
    API_KEYS: str = ""  # Kommaseparerad sträng
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Environment Settings
    ENV: str = "development"
    RAILWAY_PROJECT_NAME: str = "geometra-ai"
    RAILWAY_ENVIRONMENT: str = "staging"
    
    # System Settings
    ENABLE_SYSTEM_CHECK: bool = True
    SYSTEM_CHECK_INTERVAL_SECONDS: int = 300
    
    # CI Settings
    CI_COMMIT_TAG: str = "latest"
    CI_DEPLOY_BRANCH: str = "main"
    
    # Memory Settings
    MEMORY_CONTEXT_WINDOW: int = 10
    DEBUG_MODE: bool = False
    
    @field_validator("API_KEYS")
    @classmethod
    def parse_api_keys(cls, v: str) -> List[str]:
        """Parse comma-separated API keys into a list."""
        if not v:
            return []
        return [key.strip() for key in v.split(",")]
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        extra = "allow"  # Tillåt extra fält i .env-filen
```

## Validering

1. Verifiera ChromaDB-anslutning:
```bash
python -c "from memory.chroma.manager import ChromaManager; ChromaManager()"
```

2. Verifiera Redis-anslutning:
```bash
python -c "from memory.redis.manager import RedisManager; RedisManager()"
```

3. Kör minnestester:
```bash
python -m pytest tests/memory/
```

## Felsökning

### ChromaDB-problem

1. **Anslutningsfel**
   - Verifiera att ChromaDB-tjänsten körs
   - Kontrollera port-konfiguration
   - Verifiera nätverksinställningar

2. **Embedding-fel**
   - Kontrollera OpenAI API-nyckel
   - Verifiera modell-tillgänglighet
   - Kontrollera token-gränser

### Redis-problem

1. **Anslutningsfel**
   - Verifiera att Redis-tjänsten körs
   - Kontrollera URL-format
   - Verifiera autentisering

2. **TTL-problem**
   - Kontrollera TTL-inställningar
   - Verifiera minnesanvändning
   - Övervaka cache-storlek

## Loggning

1. Skapa loggkatalog:
```bash
mkdir -p logs/memory
```

2. Konfigurera loggning i `memory/utils/logging.py`:
```python
"""Logging configuration for memory components."""

import logging
import os
from datetime import datetime

def setup_memory_logging():
    """Configure logging for memory components."""
    log_dir = "logs/memory"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"memory_{datetime.now().strftime('%Y%m%d')}.log"
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

1. Bygg [API:et](04_BYGG_API.md)
2. Implementera [Prompt-logik](05_PROMPT_LOGIK.md)
3. Konfigurera [Fallback-logik](06_FALLBACK_LOGIK.md) 