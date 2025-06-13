# 🔍 07: Systemcheck

## 📦 Systemcheck-komponenter

### Health Checks
- API-status
- Minnesstatus
- OpenAI-anslutning

### Monitoring
- Prestandamätning
- Resursanvändning
- Felloggning

## 🛠️ Installation

1. **Skapa systemcheck-struktur**
```bash
mkdir -p scripts/checks
touch scripts/system_check.sh
```

2. **Skapa system_check.sh**
```bash
#!/bin/bash

# scripts/system_check.sh
set -e

# Färger
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Loggning
LOG_FILE="bootstrap_status.log"

log() {
    echo "$(date) - $1" >> "$LOG_FILE"
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo "$(date) - ERROR: $1" >> "$LOG_FILE"
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# API Check
check_api() {
    log "Kontrollerar API..."
    if curl -s http://localhost:8000/health > /dev/null; then
        log "API är online"
    else
        error "API är offline"
    fi
}

# Memory Check
check_memory() {
    log "Kontrollerar minne..."
    
    # ChromaDB
    if curl -s http://localhost:8001/api/v1/heartbeat > /dev/null; then
        log "ChromaDB är online"
    else
        error "ChromaDB är offline"
    fi
    
    # Redis
    if redis-cli ping > /dev/null; then
        log "Redis är online"
    else
        error "Redis är offline"
    fi
}

# OpenAI Check
check_openai() {
    log "Kontrollerar OpenAI..."
    if python3 -c "
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client.models.list()
" > /dev/null; then
        log "OpenAI är online"
    else
        error "OpenAI är offline"
    fi
}

# Docker Check
check_docker() {
    log "Kontrollerar Docker..."
    if docker ps > /dev/null; then
        log "Docker är online"
    else
        error "Docker är offline"
    fi
}

# Main
main() {
    log "Startar systemcheck..."
    
    check_docker
    check_api
    check_memory
    check_openai
    
    log "Systemcheck klar!"
}

main
```

3. **Skapa Python Health Check**
```python
# scripts/checks/health.py
from typing import Dict, List
import requests
import redis
from openai import OpenAI
import os

class HealthCheck:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.chroma_url = "http://localhost:8001"
        self.redis_client = redis.from_url("redis://localhost:6379")
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def check_all(self) -> Dict[str, bool]:
        return {
            "api": self.check_api(),
            "chroma": self.check_chroma(),
            "redis": self.check_redis(),
            "openai": self.check_openai()
        }
    
    def check_api(self) -> bool:
        try:
            response = requests.get(f"{self.api_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def check_chroma(self) -> bool:
        try:
            response = requests.get(f"{self.chroma_url}/api/v1/heartbeat")
            return response.status_code == 200
        except:
            return False
    
    def check_redis(self) -> bool:
        try:
            return self.redis_client.ping()
        except:
            return False
    
    def check_openai(self) -> bool:
        try:
            self.openai_client.models.list()
            return True
        except:
            return False
```

## 🔧 Konfiguration

1. **Skapa check_config.py**
```python
# scripts/checks/config.py
from pydantic import BaseSettings

class CheckSettings(BaseSettings):
    API_URL: str = "http://localhost:8000"
    CHROMA_URL: str = "http://localhost:8001"
    REDIS_URL: str = "redis://localhost:6379"
    CHECK_INTERVAL: int = 60
    
    class Config:
        env_file = ".env"
```

2. **Skapa check_utils.py**
```python
# scripts/checks/utils.py
from typing import Dict, Any
import json
from datetime import datetime

def format_check_result(results: Dict[str, bool]) -> str:
    return json.dumps({
        "timestamp": datetime.now().isoformat(),
        "results": results
    }, indent=2)

def save_check_result(results: Dict[str, bool], file: str = "health_check.log"):
    with open(file, "a") as f:
        f.write(format_check_result(results) + "\n")
```

## ✅ Validering

Kör följande för att verifiera systemcheck:

```bash
# Gör scriptet körbart
chmod +x scripts/system_check.sh

# Kör systemcheck
./scripts/system_check.sh

# Verifiera Python-check
python3 scripts/checks/health.py
```

## 🔍 Felsökning

### Vanliga problem

1. **API är offline**
   ```bash
   # Kontrollera API-logg
   docker-compose logs backend
   
   # Verifiera port
   netstat -tulpn | grep 8000
   ```

2. **Minnesproblem**
   ```bash
   # Kontrollera ChromaDB
   docker-compose logs chromadb
   
   # Kontrollera Redis
   docker-compose logs redis
   ```

3. **OpenAI-problem**
   ```bash
   # Verifiera API-nyckel
   echo $OPENAI_API_KEY
   
   # Testa anslutning
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

## 📝 Loggning

```bash
echo "$(date) - 07_SYSTEMCHECK: Systemcheck konfigurerad" >> bootstrap_status.log
```