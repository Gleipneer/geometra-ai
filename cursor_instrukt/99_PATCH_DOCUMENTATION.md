# Dokumentation och API-specifikation Implementation

## 1. Implementera API-dokumentation med OpenAPI/Swagger

### src/api/main.py
```python
"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, ai, users
from .middleware.security import setup_security_middleware
from .middleware.rate_limit import RateLimiter
import os

app = FastAPI(
    title="Geometra AI API",
    description="API för Geometra AI - En intelligent assistent för geometriska beräkningar",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Konfigurera säkerhet
setup_security_middleware(app)

# Konfigurera rate limiting
rate_limiter = RateLimiter()

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Rate limiting middleware."""
    await rate_limiter.check_rate_limit(request)
    return await call_next(request)

# Inkludera routers
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(users.router)

def custom_openapi():
    """Custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Lägg till säkerhetsschema
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Lägg till global säkerhet
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## 2. Implementera README.md

### README.md
```markdown
# Geometra AI

En intelligent assistent för geometriska beräkningar och ritningar.

## Funktioner

- AI-driven geometrisk analys
- Automatisk ritningsgenerering
- Minneshantering för kontextbevarande
- Säker användarautentisering
- RESTful API
- Modern React-frontend

## Teknisk Stack

### Backend
- FastAPI
- PostgreSQL
- Redis
- ChromaDB
- OpenAI API

### Frontend
- React
- TypeScript
- Material-UI
- React Router
- Axios

### DevOps
- Docker
- GitHub Actions
- AWS ECS
- Prometheus
- Grafana

## Installation

### Förutsättningar
- Python 3.9+
- Node.js 16+
- Docker och Docker Compose
- PostgreSQL
- Redis

### Utvecklingsmiljö

1. Klona repot:
```bash
git clone https://github.com/yourusername/geometra-ai.git
cd geometra-ai
```

2. Skapa och aktivera virtuell miljö:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# eller
.\venv\Scripts\activate  # Windows
```

3. Installera beroenden:
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

4. Konfigurera miljövariabler:
```bash
cp .env.example .env
# Redigera .env med dina inställningar
```

5. Starta utvecklingsservern:
```bash
# Backend
uvicorn src.api.main:app --reload

# Frontend
cd frontend
npm start
```

### Produktionsmiljö

1. Bygg och starta med Docker:
```bash
docker-compose up -d
```

## API-dokumentation

API-dokumentationen finns tillgänglig på:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Utveckling

### Kodstandard
- Python: PEP 8
- TypeScript: ESLint + Prettier
- Git: Conventional Commits

### Tester
```bash
# Backend
pytest

# Frontend
cd frontend
npm test
```

### CI/CD
- Automatiska tester vid push
- Automatisk deployment till staging
- Manuell godkännande för produktion

## Säkerhet

- JWT-autentisering
- Rate limiting
- CORS-konfiguration
- Säkerhetsheaders
- Lösenordshashning
- Session-hantering

## Övervakning

- Prometheus metrics
- Grafana dashboards
- Alertmanager för notifieringar
- Loggning med structlog

## Licens

MIT License - se [LICENSE](LICENSE) för detaljer.
```

## 3. Implementera API-dokumentation för specifika endpoints

### src/api/routes/ai.py
```python
"""AI routes."""
from fastapi import APIRouter, Depends, HTTPException
from ..models.ai import AIMessage, AIRequest, AIResponse, MemoryQuery, MemoryEntry
from ..services.ai_service import AIService
from ..utils.auth import get_current_active_user
from ..models.user import UserInDB
from typing import List

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/chat", response_model=AIResponse)
async def chat(
    request: AIRequest,
    current_user: UserInDB = Depends(get_current_active_user),
    ai_service: AIService = Depends()
):
    """
    Skicka ett meddelande till AI:n och få svar.
    
    - **message**: Meddelandet att skicka
    - **context**: Valfri kontext för AI:n
    - **options**: Valfria inställningar för AI-svaret
    
    Returnerar:
    - **response**: AI:ns svar
    - **metadata**: Metadata om svaret
    """
    return await ai_service.process_chat(request, current_user)

@router.get("/memory", response_model=List[MemoryEntry])
async def query_memory(
    query: MemoryQuery,
    current_user: UserInDB = Depends(get_current_active_user),
    ai_service: AIService = Depends()
):
    """
    Sök i AI:ns minne.
    
    - **query**: Sökfrågan
    - **limit**: Maximalt antal resultat
    - **threshold**: Relevanströskel
    
    Returnerar:
    - Lista med minnesposter som matchar sökfrågan
    """
    return await ai_service.query_memory(query, current_user)

@router.post("/memory", response_model=MemoryEntry)
async def store_memory(
    memory: MemoryEntry,
    current_user: UserInDB = Depends(get_current_active_user),
    ai_service: AIService = Depends()
):
    """
    Lagra information i AI:ns minne.
    
    - **content**: Innehållet att lagra
    - **metadata**: Metadata om innehållet
    - **tags**: Taggar för kategorisering
    
    Returnerar:
    - Den lagrade minnesposten
    """
    return await ai_service.store_memory(memory, current_user)

@router.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    ai_service: AIService = Depends()
):
    """
    Ta bort en minnespost.
    
    - **memory_id**: ID för minnesposten att ta bort
    
    Returnerar:
    - Bekräftelse på borttagning
    """
    return await ai_service.delete_memory(memory_id, current_user)
```

## 4. Implementera TypeScript-typer för API

### src/frontend/types/api.ts
```typescript
/** API types */

export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface AIRequest {
  message: string;
  context?: string;
  options?: {
    temperature?: number;
    max_tokens?: number;
    top_p?: number;
  };
}

export interface AIResponse {
  response: string;
  metadata: {
    tokens_used: number;
    processing_time: number;
    model: string;
  };
}

export interface MemoryQuery {
  query: string;
  limit?: number;
  threshold?: number;
}

export interface MemoryEntry {
  id: string;
  content: string;
  metadata: {
    source: string;
    timestamp: string;
    user_id: string;
  };
  tags: string[];
}

export interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiError {
  detail: string;
  status: number;
}
```

## 5. Implementera API-klient

### src/frontend/services/api.ts
```typescript
/** API client service */
import axios, { AxiosInstance } from 'axios';
import {
  AIRequest,
  AIResponse,
  MemoryQuery,
  MemoryEntry,
  User,
  AuthResponse,
  ApiError,
} from '../types/api';

export class ApiService {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Lägg till auth token i requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Hantera 401 errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await this.client.post<AuthResponse>('/auth/token', formData);
    return response.data;
  }

  async register(userData: Partial<User>): Promise<User> {
    const response = await this.client.post<User>('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // AI endpoints
  async chat(request: AIRequest): Promise<AIResponse> {
    const response = await this.client.post<AIResponse>('/ai/chat', request);
    return response.data;
  }

  async queryMemory(query: MemoryQuery): Promise<MemoryEntry[]> {
    const response = await this.client.get<MemoryEntry[]>('/ai/memory', {
      params: query,
    });
    return response.data;
  }

  async storeMemory(memory: MemoryEntry): Promise<MemoryEntry> {
    const response = await this.client.post<MemoryEntry>('/ai/memory', memory);
    return response.data;
  }

  async deleteMemory(memoryId: string): Promise<void> {
    await this.client.delete(`/ai/memory/${memoryId}`);
  }
}

export const api = new ApiService(process.env.REACT_APP_API_URL || 'http://localhost:8000');
```

## 6. Verifiera Implementation

```bash
# Starta servern
uvicorn src.api.main:app --reload

# Öppna API-dokumentation
open http://localhost:8000/docs
open http://localhost:8000/redoc

# Testa API-klienten
cd frontend
npm test
```

## 7. Nästa steg

Efter att ha implementerat dokumentation och API-specifikation, kör:

```bash
# Generera API-dokumentation
curl http://localhost:8000/openapi.json > openapi.json

# Validera OpenAPI-specifikationen
npx @redocly/cli lint openapi.json

# Generera TypeScript-typer från OpenAPI-specifikationen
npx openapi-typescript openapi.json --output src/frontend/types/generated.ts
```

Detta implementerar:
- OpenAPI/Swagger-dokumentation
- ReDoc-dokumentation
- README med installationsinstruktioner
- API-typer för TypeScript
- API-klient för frontend
- Automatisk generering av API-dokumentation
- Validering av API-specifikation

Nästa steg är att implementera testning och kvalitetssäkring. 