# 🏗️ 01: Systemöversikt

## 📐 Arkitektur

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │     │     Backend     │     │     Memory      │
│  (Next.js/TS)   │◄───►│   (FastAPI)     │◄───►│  (ChromaDB)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       ▲                       ▲
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Railway      │     │    OpenAI       │     │    Monitoring   │
│  (Deployment)   │     │   (GPT-4/3.5)   │     │    (Prometheus) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 🧩 Komponenter

### Frontend
- Next.js med TypeScript
- Tailwind CSS för styling
- React Query för state management
- SWR för data fetching

### Backend
- FastAPI för API-endpoints
- Pydantic för validering
- ChromaDB för vektordatabas
- Redis för caching

### Memory
- ChromaDB för LTM (Long Term Memory)
- Redis för STM (Short Term Memory)
- Vector embeddings med OpenAI

### DevOps
- GitHub Actions för CI/CD
- Railway för deployment
- Docker för containerization
- Prometheus för monitoring

## 🔄 Dataflöde

1. **Chat-initiering**
   - Frontend → Backend API
   - Validering av input
   - Kontext-hämtning från minne

2. **AI-bearbetning**
   - Backend → OpenAI API
   - Fallback till GPT-3.5 vid fel
   - Kontext-injektion i prompt

3. **Minneshantering**
   - Sparar konversation i ChromaDB
   - Cachelagrar aktiv kontext i Redis
   - Vektorisering av ny information

## ✅ Validering

Kör systemcheck:
```bash
./system_check.sh
```

Verifiera komponenter:
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000/api/health

# Memory
curl http://localhost:8000/memory/status
```

## 🔍 Felsökning

### Vanliga problem

1. **Backend startar inte**
   ```bash
   # Kontrollera loggar
   docker-compose logs backend
   
   # Verifiera miljövariabler
   cat .env | grep -v "^#"
   ```

2. **Memory-anslutning misslyckas**
   ```bash
   # Kontrollera ChromaDB
   docker-compose ps chromadb
   
   # Verifiera Redis
   redis-cli ping
   ```

3. **Frontend bygger inte**
   ```bash
   # Rensa cache
   pnpm clean
   
   # Bygg om
   pnpm build
   ```

## 📝 Loggning

```bash
echo "$(date) - 01_SYSTEMÖVERSIKT: Systemkomponenter verifierade" >> bootstrap_status.log
```
