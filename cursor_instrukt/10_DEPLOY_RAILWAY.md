# 🚀 10: Deploy Railway

## 📦 Deployment-komponenter

### Railway Setup
- Projektkonfiguration
- Miljövariabler
- Domänhantering

### Monitoring
- Loggning
- Metrics
- Alerts

## 🛠️ Installation

1. **Skapa Railway-struktur**
```bash
mkdir -p railway/{config,scripts}
```

2. **Skapa Railway Config**
```json
# railway/config/project.json
{
  "name": "geometra-ai",
  "services": [
    {
      "name": "api",
      "source": ".",
      "domains": ["api.geometra.ai"],
      "env": {
        "NODE_ENV": "production",
        "PYTHON_ENV": "production"
      }
    },
    {
      "name": "chroma",
      "source": "chromadb",
      "env": {
        "CHROMA_SERVER_HOST": "0.0.0.0",
        "CHROMA_SERVER_PORT": "8000"
      }
    },
    {
      "name": "redis",
      "source": "redis",
      "env": {
        "REDIS_URL": "redis://localhost:6379"
      }
    }
  ]
}
```

3. **Skapa Deployment Script**
```bash
# railway/scripts/deploy.sh
#!/bin/bash

# Loggning
LOG_FILE="bootstrap_status.log"

log() {
    echo "$(date) - $1" >> "$LOG_FILE"
    echo "✓ $1"
}

error() {
    echo "$(date) - ERROR: $1" >> "$LOG_FILE"
    echo "✗ $1"
    exit 1
}

# Verifiera Railway CLI
if ! command -v railway &> /dev/null; then
    error "Railway CLI saknas"
fi

# Verifiera miljövariabler
if [ -z "$RAILWAY_TOKEN" ]; then
    error "RAILWAY_TOKEN saknas"
fi

# Deploy
log "Startar deployment..."
railway up

# Verifiera deployment
log "Verifierar deployment..."
railway status

# Kontrollera loggar
log "Kontrollerar loggar..."
railway logs
```

4. **Skapa Health Check**
```python
# railway/scripts/health_check.py
import requests
import time
from typing import Dict, List
import os

class HealthCheck:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def check_health(self) -> Dict[str, bool]:
        try:
            response = requests.get(f"{self.base_url}/health")
            return {
                "status": response.status_code == 200,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e)
            }
    
    def check_memory(self) -> Dict[str, bool]:
        try:
            response = requests.get(f"{self.base_url}/memory/status")
            return {
                "status": response.status_code == 200,
                "chroma": response.json().get("chroma", False),
                "redis": response.json().get("redis", False)
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e)
            }

def main():
    base_url = os.getenv("RAILWAY_URL", "https://api.geometra.ai")
    checker = HealthCheck(base_url)
    
    # Kör health check
    health = checker.check_health()
    print(f"Health: {health}")
    
    # Kör memory check
    memory = checker.check_memory()
    print(f"Memory: {memory}")

if __name__ == "__main__":
    main()
```

## 🔧 Konfiguration

1. **Skapa Railway Secrets**
```bash
# Lägg till i Railway dashboard:
RAILWAY_TOKEN=your_railway_token
OPENAI_API_KEY=your_openai_key
CHROMA_API_KEY=your_chroma_key
```

2. **Skapa Railway Domains**
```bash
# Konfigurera domäner i Railway dashboard:
api.geometra.ai -> API service
```

## ✅ Validering

Kör följande för att verifiera deployment:

```bash
# Verifiera Railway CLI
railway login
railway status

# Kör health check
python railway/scripts/health_check.py

# Kontrollera loggar
railway logs
```

## 🔍 Felsökning

### Vanliga problem

1. **Deployment misslyckas**
   ```bash
   # Kontrollera loggar
   railway logs
   
   # Verifiera miljövariabler
   railway variables list
   ```

2. **Health Check failar**
   ```bash
   # Kontrollera API
   curl https://api.geometra.ai/health
   
   # Kontrollera minne
   curl https://api.geometra.ai/memory/status
   ```

3. **Domänproblem**
   ```bash
   # Verifiera DNS
   dig api.geometra.ai
   
   # Kontrollera SSL
   curl -v https://api.geometra.ai
   ```

## 📝 Loggning

```bash
echo "$(date) - 10_DEPLOY_RAILWAY: Deployment konfigurerad" >> bootstrap_status.log
```