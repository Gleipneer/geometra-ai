# Projektinitiering

Detta dokument beskriver hur man initierar och sätter upp Geometra AI-projektet.

## Projektstruktur

Skapa följande katalogstruktur:

```
geometra-ai/
├── api/                    # Backend API
├── frontend/              # React frontend
├── memory/               # Minneskomponenter
├── ai/                  # AI-integration
├── tests/              # Testfiler
├── docker/            # Docker-konfiguration
├── docs/             # Dokumentation
└── scripts/         # Hjälpskript
```

## Git-initiering

1. Initiera Git-repository:
```bash
git init
```

2. Skapa `.gitignore`:
```bash
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# Node
node_modules/
dist/
build/
.pnpm-store/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Test
.coverage
htmlcov/
.pytest_cache/
```

3. Första commit:
```bash
git add .
git commit -m "Initial commit: Project structure"
```

## Konfigurationsfiler

### Python-konfiguration

1. Skapa `requirements.txt`:
```txt
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.4.2
pydantic-settings>=2.0.3
python-dotenv>=1.0.0
redis>=5.0.1
chromadb>=0.4.15
openai>=1.3.0
pytest>=7.4.3
pytest-asyncio>=0.21.1
pytest-cov>=4.1.0
```

2. Skapa `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
env =
    PYTHONPATH=.
    ENV=test
timeout = 30
```

### Node.js-konfiguration

1. Skapa `package.json`:
```json
{
  "name": "geometra-ai",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest",
    "lint": "eslint src --ext ts,tsx",
    "format": "prettier --write \"src/**/*.{ts,tsx}\""
  },
  "dependencies": {
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "@mui/material": "^5.14.18",
    "@reduxjs/toolkit": "^1.9.7",
    "axios": "^1.6.2",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-redux": "^8.1.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@typescript-eslint/eslint-plugin": "^6.10.0",
    "@typescript-eslint/parser": "^6.10.0",
    "@vitejs/plugin-react": "^4.2.0",
    "eslint": "^8.53.0",
    "prettier": "^3.1.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.0",
    "vitest": "^0.34.6"
  }
}
```

### Docker-konfiguration

1. Skapa `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: 
      context: .
      dockerfile: docker/api.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    volumes:
      - .:/app
    depends_on:
      - redis
      - chromadb

  frontend:
    build:
      context: .
      dockerfile: docker/frontend.Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - .:/app
    depends_on:
      - api

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  redis_data:
  chroma_data:
```

2. Skapa `.env.example`:
```env
# API Settings
API_HOST=localhost
API_PORT=8000
ENV=development

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# ChromaDB Settings
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# OpenAI Settings
OPENAI_API_KEY=your-api-key
FALLBACK_OPENAI_API_KEY=your-fallback-key

# Frontend Settings
VITE_API_URL=http://localhost:8000
```

## Validering

1. Verifiera projektstruktur:
```bash
./scripts/validate_structure.sh
```

2. Kör enhetstester:
```bash
python -m pytest tests/unit/
```

3. Verifiera Docker-konfiguration:
```bash
docker-compose config
```

## Nästa steg

1. Konfigurera [Minneskomponenter](03_KONFIGURERA_MINNE.md)
2. Bygg [API:et](04_BYGG_API.md)
3. Implementera [Prompt-logik](05_PROMPT_LOGIK.md) 