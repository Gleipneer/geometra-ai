# Miljövariabel- och Paketkonfiguration

## 1. Skapa .env-fil

Skapa en `.env`-fil i projektets rot med följande innehåll:

```bash
# Database Configuration
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://user:password@localhost:5432/geometra_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
ENVIRONMENT=development

# Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration
OPENAI_API_KEY=your-openai-api-key
MODEL_NAME=gpt-4
TEMPERATURE=0.7

# Memory Configuration
CHROMA_PERSIST_DIRECTORY=./data/chroma
MEMORY_TTL=3600  # 1 hour in seconds

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Monitoring
ENABLE_METRICS=True
METRICS_PORT=9090
```

## 2. Installera saknade paket

Kör följande kommandon för att installera saknade paket:

```bash
# Aktivera virtuell miljö om den inte redan är aktiverad
source venv/bin/activate

# Uppdatera pip
python -m pip install --upgrade pip

# Installera paket från requirements.txt
pip install -r requirements.txt

# Installera ytterligare testpaket
pip install pytest-xdist==3.5.0 pytest-cov==4.1.0 pytest-json-report==1.5.0
```

## 3. Verifiera installation

Kör följande kommandon för att verifiera att allt är korrekt installerat:

```bash
# Verifiera Python-paket
python -c "import pytest; import pytest_xdist; import pytest_cov; import pytest_json_report"

# Verifiera miljövariabler
python scripts/verify_env.py
```

## 4. Nästa steg

Efter att ha kört dessa kommandon, kör:

```bash
# Rensa testcache
pytest --cache-clear

# Kör testerna igen
./run_all_tests.sh
```

Detta bör lösa de omedelbara blockerarna och låta oss fortsätta med nästa steg i utvecklingen. 