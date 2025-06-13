# Installation

## Förutsättningar

- Python 3.9 eller senare
- Node.js 16 eller senare
- Redis 6 eller senare
- PostgreSQL 13 eller senare
- Docker (valfritt)

## Steg-för-steg Installation

1. Klona repot:
```bash
git clone https://github.com/your-org/meta.git
cd meta
```

2. Skapa och aktivera en virtuell miljö:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# eller
.\venv\Scripts\activate  # Windows
```

3. Installera Python-beroenden:
```bash
pip install -r requirements.txt
```

4. Installera Node.js-beroenden:
```bash
cd frontend
npm install
```

5. Konfigurera miljövariabler:
```bash
cp .env.example .env
# Redigera .env med dina inställningar
```

6. Starta Redis och PostgreSQL:
```bash
# Med Docker
docker-compose up -d redis postgres

# Eller installera och starta lokalt
```

7. Kör databasmigrationer:
```bash
python scripts/migrate.py
```

8. Starta utvecklingsservern:
```bash
# Backend
python src/api/main.py

# Frontend (i en annan terminal)
cd frontend
npm start
```

## Verifiering

1. Öppna http://localhost:3000 i din webbläsare
2. API-dokumentation finns på http://localhost:8000/docs
3. Kontrollera loggarna i `logs/app.log`

## Felsökning

- Se till att alla portar är tillgängliga
- Kontrollera att miljövariablerna är korrekt konfigurerade
- Verifiera att Redis och PostgreSQL är igång
- Kontrollera loggarna för eventuella felmeddelanden
