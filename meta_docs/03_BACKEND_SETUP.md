# Backend Setup

## API-struktur

```
src/api/
├── main.py              # Huvudapplikation
├── config.py            # Konfigurationshantering
├── middleware/          # Middleware-komponenter
├── routes/             # API-endpoints
├── models/             # Datamodeller
├── services/           # Affärslogik
└── utils/              # Hjälpfunktioner
```

## Konfiguration

1. Skapa en `.env`-fil baserad på `.env.example`
2. Konfigurera databasanslutningar
3. Sätt säkerhetsnycklar
4. Ange loggnivåer

## Databaskoppling

1. Installera databasdrivrutiner:
```bash
pip install redis psycopg2-binary
```

2. Verifiera anslutningar:
```bash
python scripts/verify_db.py
```

## API-dokumentation

1. Starta servern:
```bash
python src/api/main.py
```

2. Öppna Swagger UI:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Testning

1. Kör enhetstester:
```bash
pytest tests/unit/api/
```

2. Kör integrationstester:
```bash
pytest tests/integration/api/
```

## Deployment

1. Bygg Docker-image:
```bash
docker build -t meta-api .
```

2. Kör containern:
```bash
docker run -p 8000:8000 meta-api
```

## Monitoring

1. Aktivera loggning:
```bash
python src/monitoring/setup_logging.py
```

2. Konfigurera metriker:
```bash
python src/monitoring/setup_metrics.py
```
