# Backend-förbättringar

## 1. Implementera saknade API-endpoints
```python
# src/api/routes/ai.py
from fastapi import APIRouter, HTTPException
from src.ai.service import AIService
from src.ai.prompt import PromptManager
from src.ai.chat import ChatManager
from src.ai.fallback import FallbackManager
from src.ai.memory import MemoryManager

router = APIRouter()
ai_service = AIService(
    prompt_manager=PromptManager(),
    chat_manager=ChatManager(),
    fallback_manager=FallbackManager(),
    memory_manager=MemoryManager()
)

@router.post("/prompt")
async def create_prompt(request: dict):
    """Create a new prompt."""
    try:
        response = await ai_service.process_prompt(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: dict):
    """Handle chat messages."""
    try:
        response = await ai_service.process_chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fallback")
async def fallback(request: dict):
    """Handle fallback requests."""
    try:
        response = await ai_service.process_fallback(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 2. Förbättra felhantering
```python
# src/api/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.logging.config import setup_logging

logger = setup_logging()

async def error_handler(request: Request, call_next):
    """Global error handler middleware."""
    try:
        return await call_next(request)
    except Exception as e:
        # Log error
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        
        # Return appropriate error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": str(e),
                "request_id": request.state.request_id
            }
        )
```

## 3. Implementera rate limiting
```python
# src/api/middleware/rate_limiter.py
from fastapi import Request, HTTPException
from src.redis import get_redis
import time

async def rate_limit(request: Request, call_next):
    """Rate limiting middleware."""
    redis = await get_redis()
    client_ip = request.client.host
    
    # Check rate limit
    key = f"rate_limit:{client_ip}"
    current = await redis.get(key)
    
    if current and int(current) > 100:  # 100 requests per minute
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )
    
    # Increment counter
    await redis.incr(key)
    await redis.expire(key, 60)  # 1 minute
    
    return await call_next(request)
```

## 4. Förbättra databashantering
```python
# src/db/manager.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import os

# Create async engine
engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    echo=True,
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_session():
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## 5. Implementera caching
```python
# src/cache/manager.py
from src.redis import get_redis
import json

class CacheManager:
    def __init__(self):
        self.redis = get_redis()
    
    async def get(self, key: str):
        """Get value from cache."""
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: dict, ttl: int = 3600):
        """Set value in cache."""
        await self.redis.set(
            key,
            json.dumps(value),
            ex=ttl
        )
    
    async def delete(self, key: str):
        """Delete value from cache."""
        await self.redis.delete(key)
```

## 6. Uppdatera huvudapplikationen
```python
# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.middleware.error_handler import error_handler
from src.api.middleware.rate_limiter import rate_limit
from src.api.routes import ai, memory, monitoring

app = FastAPI(title="Geometra AI API")

# Add middleware
app.middleware("http")(error_handler)
app.middleware("http")(rate_limit)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])
```

## 7. Kör testerna
```bash
# Kör alla backend-tester
pytest tests/unit/api tests/integration/api -v
``` 