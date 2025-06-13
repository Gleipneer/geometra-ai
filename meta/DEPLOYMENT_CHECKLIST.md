# 🚀 Deployment Checklist

## 📋 Preflight Checks

### Miljövariabler
- [ ] `.env` fil existerar och är komplett
- [ ] `OPENAI_API_KEY` är giltig och har tillräcklig kredit
- [ ] `CHROMA_API_KEY` är konfigurerad
- [ ] `REDIS_URL` är korrekt formaterad
- [ ] `PORT` är tillgänglig (8000)
- [ ] `RAILWAY_TOKEN` är giltig

### Dependencies
- [ ] Alla Python-paket är installerade
- [ ] Docker images är byggda
- [ ] Redis är tillgänglig
- [ ] ChromaDB är konfigurerad
- [ ] Collection namn är korrekt

### Kod
- [ ] Alla filer är committade
- [ ] Inga känsliga data i koden
- [ ] Kommentarer är uppdaterade
- [ ] Dokumentation är komplett

## 🧪 Testning

### Unit Tests
- [ ] `pytest tests/unit` passerar
- [ ] Test coverage > 90%
- [ ] Inga varningar
- [ ] Alla mocks fungerar

### Integration Tests
- [ ] `pytest tests/integration` passerar
- [ ] API endpoints fungerar
- [ ] Minne fungerar
- [ ] Fallback fungerar

### System Tests
- [ ] `./scripts/system_check.sh` ger grönt
- [ ] Alla services är tillgängliga
- [ ] Loggning fungerar
- [ ] Monitoring är aktiv

## 🚢 Deployment

### Railway
- [ ] CLI är installerad
- [ ] Projekt är konfigurerat
- [ ] Domäner är uppsatta
- [ ] SSL är konfigurerat
- [ ] Hooks är aktiva

### CI/CD
- [ ] GitHub Actions är gröna
- [ ] Docker builds lyckas
- [ ] Tester passerar
- [ ] Deployment loggar är OK

## ✅ Verifiering

### API
```bash
# Health check
curl https://api.geometra.ai/health

# Status
curl https://api.geometra.ai/status

# Chat
curl -X POST https://api.geometra.ai/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Test"}'
```

### Minne
```bash
# ChromaDB
curl https://api.geometra.ai/memory/chroma/status

# Redis
curl https://api.geometra.ai/memory/redis/status
```

### Monitoring
```bash
# Kontrollera loggar
railway logs

# Verifiera metrics
curl https://api.geometra.ai/metrics
```

## 🔄 Rollback

### Förberedelse
- [ ] Senaste version är taggad
- [ ] Backup är tagen
- [ ] Rollback script är testat
- [ ] Team är notifierat

### Procedur
```bash
# Återställ till senaste version
railway rollback

# Verifiera återställning
curl https://api.geometra.ai/health
```

## 📝 Dokumentation

### Uppdateringar
- [ ] API docs är uppdaterade
- [ ] README är uppdaterad
- [ ] Changelog är uppdaterad
- [ ] Deployment guide är uppdaterad

### Notifiering
- [ ] Team är informerat
- [ ] Support är informerad
- [ ] Kunder är notifierade
- [ ] Status är uppdaterad

## 🚨 Viktigt

- Kör ALLA tester innan deployment
- Verifiera ALLA miljövariabler
- Kontrollera ALLA loggar
- Ha rollback-plan redo
- Notifiera team och support

## 📊 Status

```bash
# Kör deployment check
./scripts/deployment_check.sh

# Verifiera status
cat bootstrap_status.log
``` 