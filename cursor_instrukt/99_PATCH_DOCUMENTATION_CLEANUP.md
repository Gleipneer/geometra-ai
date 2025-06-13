# Dokumentationsrensning och strukturering

## 1. Ta bort dubbla dokument
```bash
# Ta bort dubbla dokument (behåll de senaste versionerna)
rm meta_docs/{29,30,31,32,33,34,35}_*.md
```

## 2. Uppdatera dokumentationsstruktur
```bash
# Skapa ny dokumentationsstruktur
mkdir -p meta_docs/{system,api,ai,frontend,security,monitoring,deployment}

# Flytta och byt namn på dokument
mv meta_docs/01_ÖVERSIKT.md meta_docs/system/01_system_overview.md
mv meta_docs/02_INSTALLATION.md meta_docs/system/02_installation.md
mv meta_docs/03_BACKEND_SETUP.md meta_docs/api/01_backend_setup.md
mv meta_docs/04_FRONTEND_SETUP.md meta_docs/frontend/01_frontend_setup.md
mv meta_docs/05_AI_SETUP.md meta_docs/ai/01_ai_setup.md
```

## 3. Uppdatera dokumentationsinnehåll

### Systemöversikt (meta_docs/system/01_system_overview.md)
```markdown
# Systemöversikt

## Komponenter
- API (FastAPI)
- AI (OpenAI GPT-4)
- Frontend (React)
- Databas (PostgreSQL + Redis)
- Säkerhet
- Monitoring
- Backup & DR

## Arkitektur
- Mikrotjänster
- Event-driven
- Asynkron kommunikation

## Teknisk Stack
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+
- Docker
- Kubernetes
```

### API-dokumentation (meta_docs/api/01_backend_setup.md)
```markdown
# Backend Setup

## Endpoints
- /api/v1/ai/prompt
- /api/v1/ai/chat
- /api/v1/ai/fallback
- /api/v1/memory
- /api/v1/monitoring

## Databaskoppling
- PostgreSQL för persistent lagring
- Redis för caching och sessions

## Säkerhet
- JWT-autentisering
- API-nyckelhantering
- Rate limiting
```

### AI-dokumentation (meta_docs/ai/01_ai_setup.md)
```markdown
# AI Setup

## Komponenter
- Prompt-hantering
- Konversationshantering
- Fallback-logik
- Minneshantering

## Konfiguration
- OpenAI API-integration
- Prompt-templates
- Kontext-hantering
- Caching-strategi
```

## 4. Skapa dokumentationsindex
```bash
# Skapa index-fil
cat > meta_docs/README.md << 'EOF'
# Geometra AI-system Dokumentation

## System
- [Systemöversikt](system/01_system_overview.md)
- [Installation](system/02_installation.md)

## API
- [Backend Setup](api/01_backend_setup.md)

## AI
- [AI Setup](ai/01_ai_setup.md)

## Frontend
- [Frontend Setup](frontend/01_frontend_setup.md)

## Säkerhet
- [Säkerhetskonfiguration](security/01_security.md)

## Monitoring
- [Monitoring Setup](monitoring/01_monitoring.md)

## Deployment
- [Deployment Guide](deployment/01_deployment.md)
EOF
```

## 5. Verifiera dokumentation
```bash
# Kör dokumentationstester
pytest tests/test_docs.py -v
``` 