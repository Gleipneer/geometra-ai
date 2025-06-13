# 📚 99: Referenser

## 📋 Checklistor

### 1. Installation
- [ ] Backend dependencies installerade
- [ ] Frontend dependencies installerade
- [ ] Docker images byggda
- [ ] Miljövariabler konfigurerade
- [ ] API-nycklar verifierade

### 2. Konfiguration
- [ ] API endpoints konfigurerade
- [ ] Minne (ChromaDB + Redis) konfigurerat
- [ ] Fallback-logik implementerad
- [ ] Loggning aktiverad
- [ ] Monitoring påslaget

### 3. Deployment
- [ ] Railway CLI installerad
- [ ] GitHub Actions konfigurerade
- [ ] Domäner uppsatta
- [ ] SSL-certifikat verifierat
- [ ] Health checks implementerade

## 💻 Kodexempel

### 1. API Anrop
```python
import requests

def chat_with_ai(message: str, user_id: str) -> dict:
    response = requests.post(
        "https://api.geometra.ai/chat",
        json={
            "message": message,
            "user_id": user_id
        }
    )
    return response.json()
```

### 2. Minne
```python
from geometra.memory import MemoryManager

memory = MemoryManager()

# Spara minne
memory.store(
    user_id="user123",
    content="Viktig information",
    metadata={"type": "note"}
)

# Hämta minne
memories = memory.query(
    user_id="user123",
    query="Viktig information"
)
```

### 3. Fallback
```python
from geometra.fallback import ModelManager

manager = ModelManager()

# Anropa med fallback
response = manager.chat(
    message="Hej!",
    user_id="user123",
    fallback=True
)
```

### 4. System Check
```bash
# Kör system check
./scripts/system_check.sh

# Kontrollera health
curl https://api.geometra.ai/health

# Verifiera minne
curl https://api.geometra.ai/memory/status
```

## 🔧 Felsökning

### 1. API Problem
```bash
# Kontrollera API status
curl -v https://api.geometra.ai/health

# Kontrollera loggar
railway logs
```

### 2. Minne Problem
```bash
# Kontrollera ChromaDB
curl https://api.geometra.ai/memory/chroma/status

# Kontrollera Redis
curl https://api.geometra.ai/memory/redis/status
```

### 3. Deployment Problem
```bash
# Verifiera deployment
railway status

# Kontrollera miljövariabler
railway variables list
```

## 📝 Loggning

### 1. Bootstrap Status
```bash
# Kontrollera bootstrap status
cat bootstrap_status.log

# Lägg till logg
echo "$(date) - ACTION: Beskrivning" >> bootstrap_status.log
```

### 2. System Logs
```bash
# Kontrollera system logs
railway logs

# Filtrera loggar
railway logs | grep "ERROR"
```

## 🔄 Återställning

### 1. Återställ Minne
```bash
# Rensa ChromaDB
curl -X POST https://api.geometra.ai/memory/chroma/clear

# Rensa Redis
curl -X POST https://api.geometra.ai/memory/redis/clear
```

### 2. Återställ Deployment
```bash
# Återställ till senaste version
railway rollback

# Återställ miljövariabler
railway variables reset
```

## 📚 Dokumentation

### 1. API Dokumentation
- [API Endpoints](docs/api.md)
- [Minne API](docs/memory.md)
- [Fallback API](docs/fallback.md)

### 2. Deployment Dokumentation
- [Railway Setup](docs/railway.md)
- [CI/CD Pipeline](docs/cicd.md)
- [Monitoring](docs/monitoring.md)

### 3. Utvecklardokumentation
- [Utvecklingsguide](docs/development.md)
- [Testning](docs/testing.md)
- [Felsökning](docs/troubleshooting.md)