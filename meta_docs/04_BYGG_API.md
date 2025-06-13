# Bygg API:et

Detta dokument beskriver hur man bygger och konfigurerar API:et för Geometra AI-systemet.

## Översikt

API:et är byggt med FastAPI och innehåller följande huvudkomponenter:

1. **Chat-endpoints**
   - Hantering av konversationer
   - Minnesintegration
   - Kontext-hantering

2. **System-endpoints**
   - Hälsokontroll
   - Statusövervakning
   - Konfigurationshantering

3. **Säkerhet**
   - API-nyckelvalidering
   - Rate limiting
   - CORS-konfiguration

## Installation

1. Installera beroenden:
```bash
pip install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt]
```

2. Skapa API-struktur:
```bash
mkdir -p api/{routers,models,schemas,utils}
```

## Konfiguration

### FastAPI-applikation

1. Skapa `api/main.py`:
```python
"""Main FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

from .routers import chat, system
from .utils.auth import get_api_key
from .utils.rate_limit import RateLimiter

app = FastAPI(
    title="Geometra AI API",
    description="API för Geometra AI-systemet",
    version="1.0.0"
)

# CORS-konfiguration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
rate_limiter = RateLimiter()

# Routers
app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["chat"],
    dependencies=[Depends(get_api_key)]
)
app.include_router(
    system.router,
    prefix="/api/v1/system",
    tags=["system"]
)

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
```

### Chat-router

1. Skapa `api/routers/chat.py`:
```python
"""Chat router for handling conversations."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..models.chat import ChatMessage, ChatResponse
from ..utils.auth import get_api_key
from ..utils.rate_limit import RateLimiter

router = APIRouter()
rate_limiter = RateLimiter()

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: Optional[str] = None
    context: Optional[dict] = None

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    api_key: str = Depends(get_api_key)
):
    """Send a message and get a response."""
    if not rate_limiter.check_rate_limit(api_key):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
    
    # Här kommer logiken för att hantera meddelandet
    # och generera svar
    
    return ChatResponse(
        message="Ett svar kommer här",
        session_id=request.session_id,
        timestamp=datetime.now()
    )
```

### System-router

1. Skapa `api/routers/system.py`:
```python
"""System router for health checks and monitoring."""

from fastapi import APIRouter
from typing import Dict
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict:
    """Check system health."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/status")
async def system_status() -> Dict:
    """Get system status."""
    return {
        "version": "1.0.0",
        "environment": "development",
        "uptime": "0:00:00",
        "memory_usage": "0MB",
        "cpu_usage": "0%"
    }
```

### Autentisering

1. Skapa `api/utils/auth.py`:
```python
"""Authentication utilities."""

from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Optional
import os

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate API key."""
    valid_keys = os.getenv("API_KEYS", "").split(",")
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key
```

### Rate Limiting

1. Skapa `api/utils/rate_limit.py`:
```python
"""Rate limiting utilities."""

from datetime import datetime, timedelta
from typing import Dict, Optional
import time

class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, requests_per_minute: int = 60):
        """Initialize rate limiter."""
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    def check_rate_limit(self, api_key: str) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Rensa gamla requests
        if api_key in self.requests:
            self.requests[api_key] = [
                req_time for req_time in self.requests[api_key]
                if req_time > minute_ago
            ]
        else:
            self.requests[api_key] = []
        
        # Kontrollera rate limit
        if len(self.requests[api_key]) >= self.requests_per_minute:
            return False
        
        # Lägg till ny request
        self.requests[api_key].append(now)
        return True
```

## Validering

1. Starta API:et:
```bash
uvicorn api.main:app --reload
```

2. Testa endpoints:
```bash
curl -X GET "http://localhost:8000/api/v1/system/health"
curl -X POST "http://localhost:8000/api/v1/chat/message" \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hej!"}'
```

3. Kör API-tester:
```bash
python -m pytest tests/api/
```

## Felsökning

### API-problem

1. **Anslutningsfel**
   - Verifiera att API:et körs
   - Kontrollera port-konfiguration
   - Verifiera nätverksinställningar

2. **Autentiseringsfel**
   - Kontrollera API-nyckel
   - Verifiera header-format
   - Kontrollera rate limiting

3. **Minnesproblem**
   - Verifiera ChromaDB-anslutning
   - Kontrollera Redis-anslutning
   - Verifiera kontext-hantering

## Loggning

1. Skapa loggkatalog:
```bash
mkdir -p logs/api
```

2. Konfigurera loggning i `api/utils/logging.py`:
```python
"""Logging configuration for API."""

import logging
import os
from datetime import datetime

def setup_api_logging():
    """Configure logging for API."""
    log_dir = "logs/api"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"api_{datetime.now().strftime('%Y%m%d')}.log"
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

1. Implementera [Prompt-logik](05_PROMPT_LOGIK.md)
2. Konfigurera [Fallback-logik](06_FALLBACK_LOGIK.md)
3. Bygg [Frontend](07_FRONTEND.md) 