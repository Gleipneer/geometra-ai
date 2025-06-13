# 🚀 02: Initiera Projekt

## 📁 Projektstruktur

```
geometra-ai/
├── api/                 # Backend API
├── frontend/           # Next.js frontend
├── memory/            # Minneshantering
├── tests/             # Tester
├── docker/            # Docker-filer
├── .github/           # GitHub Actions
├── cursor_instrukt/   # Patches & felsökning
└── meta/              # Dokumentation
```

## 🛠️ Installation

1. **Skapa projektstruktur**
```bash
mkdir -p geometra-ai/{api,frontend,memory,tests,docker,.github,cursor_instrukt,meta}
cd geometra-ai
```

2. **Initiera Git**
```bash
git init
git add .
git commit -m "Initial commit"
```

3. **Skapa .gitignore**
```bash
cat > .gitignore << EOL
# Dependencies
node_modules/
.pnpm-store/
__pycache__/
*.pyc

# Environment
.env
.env.*
!.env.example

# Build
dist/
build/
.next/

# Logs
*.log
npm-debug.log*

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOL
```

4. **Skapa requirements.txt**
```bash
cat > requirements.txt << EOL
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2
chromadb==0.4.15
redis==5.0.1
openai==1.3.0
python-dotenv==1.0.0
pytest==7.4.3
httpx==0.25.1
EOL
```

5. **Skapa package.json**
```bash
cat > package.json << EOL
{
  "name": "geometra-ai",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "test": "jest",
    "lint": "eslint ."
  }
}
EOL
```

## 🔧 Konfiguration

1. **Skapa .env.example**
```bash
cat > .env.example << EOL
# API Keys
OPENAI_API_KEY=your_openai_key
RAILWAY_API_KEY=your_railway_key

# Backend
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Memory
CHROMA_HOST=localhost
CHROMA_PORT=8000
REDIS_URL=redis://localhost:6379

# Environment
NODE_ENV=development
PYTHON_ENV=development
EOL
```

2. **Skapa docker-compose.yml**
```bash
cat > docker-compose.yml << EOL
version: '3.8'

services:
  backend:
    build: ./api
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - chromadb
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file: .env

  chromadb:
    image: chromadb/chroma
    ports:
      - "8001:8000"

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
EOL
```

## ✅ Validering

Kör följande för att verifiera installationen:

```bash
# Verifiera Git
git status

# Verifiera Python-miljö
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verifiera Node-miljö
pnpm install

# Verifiera Docker
docker-compose config
```

## 🔍 Felsökning

### Vanliga problem

1. **Git-initiering misslyckas**
   ```bash
   # Rensa och försök igen
   rm -rf .git
   git init
   ```

2. **Docker Compose-problem**
   ```bash
   # Verifiera syntax
   docker-compose config
   
   # Rensa och bygg om
   docker-compose down
   docker-compose up --build
   ```

3. **pnpm-installation**
   ```bash
   # Rensa cache
   pnpm store prune
   
   # Installera om
   pnpm install
   ```

## 📝 Loggning

```bash
echo "$(date) - 02_INITIERA_PROJEKT: Projektstruktur skapad" >> bootstrap_status.log
```

bash
Kopiera kod
