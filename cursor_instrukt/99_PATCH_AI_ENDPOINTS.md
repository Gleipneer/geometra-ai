# AI Endpoints och Minneshantering Implementation

## 1. Skapa AI-modeller

### src/api/models/ai.py
```python
"""AI models."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class AIMessage(BaseModel):
    """AI message model."""
    content: str = Field(..., min_length=1)
    role: str = Field(..., regex="^(user|assistant|system)$")
    metadata: Optional[Dict[str, Any]] = None

class AIRequest(BaseModel):
    """AI request model."""
    messages: List[AIMessage]
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = None
    stream: bool = Field(default=False)

class AIResponse(BaseModel):
    """AI response model."""
    content: str
    model: str
    usage: Dict[str, int]
    created_at: datetime

class MemoryQuery(BaseModel):
    """Memory query model."""
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    filter_metadata: Optional[Dict[str, Any]] = None

class MemoryEntry(BaseModel):
    """Memory entry model."""
    id: UUID
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    embedding: Optional[List[float]] = None
```

## 2. Implementera AI Routes

### src/api/routes/ai.py
```python
"""AI routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.ai import AIRequest, AIResponse, MemoryQuery, MemoryEntry
from ..models.user import UserInDB
from ..services.ai_service import AIService
from ..utils.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/chat", response_model=AIResponse)
async def chat(
    request: AIRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Chat with AI."""
    return await AIService.process_chat(request, current_user.id)

@router.post("/memory/query", response_model=List[MemoryEntry])
async def query_memory(
    query: MemoryQuery,
    current_user: UserInDB = Depends(get_current_user)
):
    """Query memory."""
    return await AIService.query_memory(query, current_user.id)

@router.post("/memory/store")
async def store_memory(
    content: str,
    metadata: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """Store memory."""
    return await AIService.store_memory(content, metadata, current_user.id)

@router.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete memory."""
    await AIService.delete_memory(memory_id, current_user.id)
    return {"message": "Memory deleted successfully"}
```

## 3. Implementera AI Service

### src/api/services/ai_service.py
```python
"""AI service."""
from typing import List, Optional
from ..models.ai import AIRequest, AIResponse, MemoryQuery, MemoryEntry
from ..utils.memory import MemoryManager
from ..utils.openai_client import OpenAIClient
import uuid
from datetime import datetime

class AIService:
    """AI service class."""
    
    def __init__(self):
        """Initialize AI service."""
        self.memory_manager = MemoryManager()
        self.openai_client = OpenAIClient()
    
    async def process_chat(
        self,
        request: AIRequest,
        user_id: str
    ) -> AIResponse:
        """Process chat request."""
        # Hämta relevanta minnen
        memories = await self.memory_manager.query(
            request.messages[-1].content,
            user_id,
            limit=5
        )
        
        # Lägg till minnen i systemmeddelande
        system_message = {
            "role": "system",
            "content": "Relevant context from memory:\n" + "\n".join(
                [m.content for m in memories]
            )
        }
        
        # Förbered meddelanden
        messages = [system_message] + [
            {"role": m.role, "content": m.content}
            for m in request.messages
        ]
        
        # Anropa OpenAI
        response = await self.openai_client.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        # Spara relevanta delar i minnet
        if not request.stream:
            await self.memory_manager.store(
                content=response.content,
                metadata={
                    "type": "chat_response",
                    "user_id": user_id,
                    "model": request.model
                },
                user_id=user_id
            )
        
        return response
    
    async def query_memory(
        self,
        query: MemoryQuery,
        user_id: str
    ) -> List[MemoryEntry]:
        """Query memory."""
        return await self.memory_manager.query(
            query.query,
            user_id,
            limit=query.limit,
            filter_metadata=query.filter_metadata
        )
    
    async def store_memory(
        self,
        content: str,
        metadata: dict,
        user_id: str
    ) -> MemoryEntry:
        """Store memory."""
        return await self.memory_manager.store(
            content=content,
            metadata=metadata,
            user_id=user_id
        )
    
    async def delete_memory(
        self,
        memory_id: str,
        user_id: str
    ) -> None:
        """Delete memory."""
        await self.memory_manager.delete(memory_id, user_id)
```

## 4. Implementera Minneshantering

### src/api/utils/memory.py
```python
"""Memory management utilities."""
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings
import redis
import json
from datetime import datetime
import uuid
import os

class MemoryManager:
    """Memory manager class."""
    
    def __init__(self):
        """Initialize memory manager."""
        # Initiera Redis för korttidsminne
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        
        # Initiera ChromaDB för långtidsminne
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=os.getenv(
                "CHROMA_PERSIST_DIRECTORY",
                "./data/chroma"
            )
        ))
        
        # Skapa eller hämta collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="geometra_memories"
        )
    
    async def store(
        self,
        content: str,
        metadata: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Store memory."""
        # Generera ID
        memory_id = str(uuid.uuid4())
        
        # Spara i Redis (korttidsminne)
        redis_key = f"memory:{user_id}:{memory_id}"
        self.redis_client.setex(
            redis_key,
            int(os.getenv("MEMORY_TTL", 3600)),  # 1 timme default
            json.dumps({
                "content": content,
                "metadata": metadata,
                "created_at": datetime.utcnow().isoformat()
            })
        )
        
        # Spara i ChromaDB (långtidsminne)
        self.collection.add(
            documents=[content],
            metadatas=[{
                **metadata,
                "user_id": user_id,
                "memory_id": memory_id,
                "created_at": datetime.utcnow().isoformat()
            }],
            ids=[memory_id]
        )
        
        return {
            "id": memory_id,
            "content": content,
            "metadata": metadata,
            "created_at": datetime.utcnow()
        }
    
    async def query(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query memory."""
        # Sök i ChromaDB
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={
                "user_id": user_id,
                **(filter_metadata or {})
            }
        )
        
        # Formatera resultat
        memories = []
        for i, memory_id in enumerate(results["ids"][0]):
            # Kontrollera Redis först
            redis_key = f"memory:{user_id}:{memory_id}"
            redis_data = self.redis_client.get(redis_key)
            
            if redis_data:
                # Använd Redis-data om tillgänglig
                memory_data = json.loads(redis_data)
                memories.append({
                    "id": memory_id,
                    "content": memory_data["content"],
                    "metadata": memory_data["metadata"],
                    "created_at": datetime.fromisoformat(
                        memory_data["created_at"]
                    )
                })
            else:
                # Använd ChromaDB-data som fallback
                memories.append({
                    "id": memory_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "created_at": datetime.fromisoformat(
                        results["metadatas"][0][i]["created_at"]
                    )
                })
        
        return memories
    
    async def delete(
        self,
        memory_id: str,
        user_id: str
    ) -> None:
        """Delete memory."""
        # Ta bort från Redis
        redis_key = f"memory:{user_id}:{memory_id}"
        self.redis_client.delete(redis_key)
        
        # Ta bort från ChromaDB
        self.collection.delete(
            ids=[memory_id],
            where={"user_id": user_id}
        )
```

## 5. Implementera OpenAI-klient

### src/api/utils/openai_client.py
```python
"""OpenAI client utilities."""
from openai import AsyncOpenAI
import os
from typing import List, Dict, Any, Optional
from ..models.ai import AIResponse
from datetime import datetime

class OpenAIClient:
    """OpenAI client class."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> AIResponse:
        """Get chat completion."""
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        if stream:
            return response
        
        return AIResponse(
            content=response.choices[0].message.content,
            model=model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            created_at=datetime.fromtimestamp(response.created)
        )
```

## 6. Uppdatera main.py

```python
"""Main FastAPI application for Geometra AI system."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import users, projects, ai

app = FastAPI(
    title="Geometra AI API",
    description="API for Geometra AI system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(ai.router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/version")
async def get_version():
    """Get API version."""
    return {"version": "1.0.0"}
```

## 7. Installera Nödvändiga Paket

```bash
pip install chromadb redis openai
```

## 8. Verifiera Implementation

```bash
# Starta servern
uvicorn src.api.main:app --reload

# Testa AI-endpoints med curl eller Postman
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hej, hur mår du?"}
    ]
  }'
```

## 9. Nästa steg

Efter att ha implementerat AI-endpoints och minneshantering, kör:

```bash
# Kör API-tester
pytest tests/unit/api/test_ai_endpoints.py

# Generera API-dokumentation
python scripts/generate_api_docs.py
```

Detta implementerar:
- AI-chatfunktionalitet med minneshantering
- Integration med OpenAI
- Korttidsminne med Redis
- Långtidsminne med ChromaDB
- Minnessökning och -hantering

Nästa steg är att implementera frontend-integration och komplettera testningen. 