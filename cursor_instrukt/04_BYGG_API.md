# 🚀 04: Bygg API

## 📦 API-komponenter

### FastAPI
- REST API med OpenAPI-dokumentation
- Pydantic för validering
- Async/await för prestanda

### Endpoints
- `/chat` - AI-konversation
- `/memory` - Minneshantering
- `/status` - Systemstatus

## 🛠️ Installation

1. **Skapa API-struktur**
```bash
mkdir -p api/{routes,models,services}
touch api/__init__.py
```

2. **Skapa main.py**
```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import chat, memory, status

app = FastAPI(title="Geometra AI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(memory.router, prefix="/memory", tags=["memory"])
app.include_router(status.router, prefix="/status", tags=["status"])
```

3. **Skapa routes**
```python
# api/routes/chat.py
from fastapi import APIRouter, HTTPException
from ..models.chat import ChatRequest, ChatResponse
from ..services.chat import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await chat_service.process_message(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

4. **Skapa models**
```python
# api/models/chat.py
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    context: Optional[dict] = None
```

5. **Skapa services**
```python
# api/services/chat.py
from typing import Optional
from ..models.chat import ChatRequest
from memory.memory_manager import MemoryManager

class ChatService:
    def __init__(self):
        self.memory = MemoryManager(
            chroma_host="localhost",
            chroma_port=8001,
            redis_url="redis://localhost:6379"
        )
    
    async def process_message(self, message: str) -> str:
        # Hämta kontext från minne
        context = self.memory.query_memory(message)
        
        # Bearbeta med GPT
        response = await self._get_gpt_response(message, context)
        
        # Spara i minne
        self.memory.store_memory(
            text=message,
            metadata={"type": "user_message"}
        )
        
        return response
```

## 🔧 Konfiguration

1. **Skapa api_config.py**
```python
# api/config.py
from pydantic import BaseSettings

class APISettings(BaseSettings):
    OPENAI_API_KEY: str
    MODEL_NAME: str = "gpt-4"
    MAX_TOKENS: int = 2000
    
    class Config:
        env_file = ".env"
```

2. **Skapa Dockerfile**
```dockerfile
# api/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## ✅ Validering

Kör följande för att verifiera API:en:

```bash
# Starta API:en
docker-compose up -d backend

# Testa endpoints
curl http://localhost:8000/status
curl http://localhost:8000/docs

# Verifiera OpenAPI
curl http://localhost:8000/openapi.json
```

## 🔍 Felsökning

### Vanliga problem

1. **API startar inte**
   ```bash
   # Kontrollera loggar
   docker-compose logs backend
   
   # Verifiera port
   netstat -tulpn | grep 8000
   ```

2. **OpenAI-anslutning misslyckas**
   ```bash
   # Verifiera API-nyckel
   cat .env | grep OPENAI_API_KEY
   
   # Testa anslutning
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

3. **Minnesanslutning misslyckas**
   ```bash
   # Verifiera ChromaDB
   curl http://localhost:8001/api/v1/heartbeat
   
   # Verifiera Redis
   redis-cli ping
   ```

## 📝 Loggning

```bash
echo "$(date) - 04_BYGG_API: API konfigurerad och verifierad" >> bootstrap_status.log
```