# 🧠 03: Konfigurera Minne

## 📦 Minneskomponenter

### ChromaDB (LTM)
- Vektordatabas för långtidsminne
- Sparar konversationer och kontext
- Stöd för semantisk sökning

### Redis (STM)
- Korttidsminne för aktiva sessioner
- Caching av kontext
- Snabb åtkomst till aktiv data

## 🛠️ Installation

1. **Skapa memory-modulen**
```bash
mkdir -p memory/{chroma,redis,utils}
touch memory/__init__.py
```

2. **Skapa ChromaDB-hanterare**
```python
# memory/chroma/manager.py
from chromadb import Client, Settings
from chromadb.config import Settings as ChromaSettings

class ChromaManager:
    def __init__(self, host: str, port: int):
        self.client = Client(Settings(
            chroma_api_impl="rest",
            chroma_server_host=host,
            chroma_server_http_port=port
        ))
        self.collection = self.client.get_or_create_collection("geometra_memory")
```

3. **Skapa Redis-hanterare**
```python
# memory/redis/manager.py
import redis
from typing import Optional

class RedisManager:
    def __init__(self, url: str):
        self.client = redis.from_url(url)
    
    def set_context(self, session_id: str, context: str):
        self.client.set(f"context:{session_id}", context)
    
    def get_context(self, session_id: str) -> Optional[str]:
        return self.client.get(f"context:{session_id}")
```

4. **Skapa Minneshanterare**
```python
# memory/memory_manager.py
from typing import Optional
from .chroma.manager import ChromaManager
from .redis.manager import RedisManager

class MemoryManager:
    def __init__(self, chroma_host: str, chroma_port: int, redis_url: str):
        self.ltm = ChromaManager(chroma_host, chroma_port)
        self.stm = RedisManager(redis_url)
    
    def store_memory(self, text: str, metadata: dict):
        self.ltm.collection.add(
            documents=[text],
            metadatas=[metadata]
        )
    
    def query_memory(self, query: str, n_results: int = 5):
        return self.ltm.collection.query(
            query_texts=[query],
            n_results=n_results
        )
```

## 🔧 Konfiguration

1. **Skapa memory_config.py**
```python
# memory/config.py
from pydantic import BaseSettings

class MemorySettings(BaseSettings):
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
```

2. **Skapa memory_utils.py**
```python
# memory/utils/embeddings.py
from openai import OpenAI
from typing import List

def get_embeddings(texts: List[str], api_key: str) -> List[List[float]]:
    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-ada-002"
    )
    return [data.embedding for data in response.data]
```

## ✅ Validering

Kör följande för att verifiera minneskonfigurationen:

```bash
# Starta tjänster
docker-compose up -d chromadb redis

# Verifiera ChromaDB
curl http://localhost:8001/api/v1/heartbeat

# Verifiera Redis
redis-cli ping
```

## 🔍 Felsökning

### Vanliga problem

1. **ChromaDB startar inte**
   ```bash
   # Kontrollera loggar
   docker-compose logs chromadb
   
   # Verifiera port
   netstat -tulpn | grep 8001
   ```

2. **Redis-anslutning misslyckas**
   ```bash
   # Testa anslutning
   redis-cli -h localhost ping
   
   # Kontrollera loggar
   docker-compose logs redis
   ```

3. **Minneshantering ger fel**
   ```bash
   # Verifiera miljövariabler
   cat .env | grep -E "CHROMA|REDIS"
   
   # Testa Python-import
   python -c "from memory.memory_manager import MemoryManager"
   ```

## 📝 Loggning

```bash
echo "$(date) - 03_KONFIGURERA_MINNE: Minneskomponenter konfigurerade" >> bootstrap_status.log
```