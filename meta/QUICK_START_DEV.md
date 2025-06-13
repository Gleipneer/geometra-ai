# 🚀 Quick Start Guide för Geometra AI

## 📋 Snabböversikt

Geometra AI är ett självläkande AI-system med:
- GPT-4/3.5 integration
- Minnesarkitektur (ChromaDB + Redis)
- Automatisk deployment via Railway
- CI/CD pipeline med GitHub Actions

## 🛠️ Installation

1. **Klona repot**
```bash
git clone https://github.com/your-org/geometra-ai.git
cd geometra-ai
```

2. **Skapa miljövariabler**
```bash
# Kopiera .env.example
cp .env.example .env

# Uppdatera med dina nycklar
OPENAI_API_KEY=sk-...
CHROMA_API_KEY=...
REDIS_URL=redis://localhost:6379
```

3. **Starta dependencies**
```bash
# Starta Redis
docker run -d -p 6379:6379 redis

# Starta ChromaDB
docker run -d -p 8000:8000 chromadb/chroma
```

4. **Installera Python-paket**
```bash
pip install -r requirements.txt
```

## 🚀 Snabbstart

1. **Starta API:et**
```bash
uvicorn api.main:app --reload
```

2. **Testa API:et**
```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Hej!"}'

# Minne
curl -X POST http://localhost:8000/memory \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "content": "Testminne"}'
```

## 📚 Dokumentation

Följande dokumentation finns tillgänglig:

1. [Systemöversikt](01_SYSTEMÖVERSIKT.md)
2. [Projektinitiering](02_INITIERA_PROJEKT.md)
3. [Minneskonfiguration](03_KONFIGURERA_MINNE.md)
4. [API-byggande](04_BYGG_API.md)
5. [Prompt-logik](05_PROMPT_LOGIK.md)
6. [Fallback-logik](06_FALLBACK_LOGIK.md)
7. [Systemcheck](07_SYSTEMCHECK.md)
8. [Testning](08_TESTNING.md)
9. [CI/CD Pipeline](09_CICD_PIPELINE.md)
10. [Railway Deployment](10_DEPLOY_RAILWAY.md)
11. [Referenser](99_REFERENSER.md)

## 🔧 Felsökning

### Vanliga problem

1. **API startar inte**
```bash
# Kontrollera portar
lsof -i :8000
# Kontrollera loggar
cat logs/api.log
```

2. **Minnesproblem**
```bash
# Kontrollera Redis
redis-cli ping
# Kontrollera ChromaDB
curl http://localhost:8000/memory/status
```

3. **OpenAI-problem**
```bash
# Testa API-nyckel
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Nyttiga kommandon

```bash
# Systemcheck
./scripts/system_check.sh

# Tester
pytest tests/

# Docker status
docker ps

# Loggar
tail -f logs/*.log
```

## 🎯 Utvecklingsflöde

1. **Skapa feature branch**
```bash
git checkout -b feature/ny-funktion
```

2. **Kör tester**
```bash
pytest tests/
```

3. **Pusha och skapa PR**
```bash
git push origin feature/ny-funktion
```

## 📝 Loggning

Alla viktiga händelser loggas i:
- `logs/api.log` - API-loggning
- `logs/memory.log` - Minnesloggning
- `logs/fallback.log` - Fallback-loggning
- `bootstrap_status.log` - Systemstatus

## 🔄 Återställning

Om något går fel:

1. **Återställ minne**
```bash
curl -X POST http://localhost:8000/memory/reset
```

2. **Återställ deployment**
```bash
railway rollback
```

3. **Återställ miljövariabler**
```bash
cp .env.example .env
```

## 🚨 Viktigt

- Kör alltid `system_check.sh` efter ändringar
- Verifiera alla miljövariabler innan deployment
- Testa fallback-logiken regelbundet
- Håll koll på minnesanvändningen 