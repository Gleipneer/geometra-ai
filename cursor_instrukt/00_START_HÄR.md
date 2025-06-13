# 🚀 00: Start Här

## 📋 Förutsättningar

### Systemkrav
- Node.js 18+ 
- Python 3.9+
- pnpm 8+
- Docker
- Git

### Verktyg
- VS Code med Cursor
- Railway CLI
- GitHub CLI

### API-nycklar
- OpenAI API-nyckel
- Railway API-nyckel
- GitHub Personal Access Token

## 🎯 Uppstart

1. Klona repot
```bash
git clone https://github.com/your-org/geometra-ai.git
cd geometra-ai
```

2. Installera verktyg
```bash
# Installera pnpm om det saknas
npm install -g pnpm

# Installera Python-verktyg
pip install -r requirements.txt
```

3. Konfigurera miljövariabler
```bash
cp .env.example .env
# Fyll i dina API-nycklar i .env
```

## ✅ Validering

Kör följande för att verifiera installationen:

```bash
# Verifiera Node.js
node --version  # Ska vara 18+

# Verifiera Python
python --version  # Ska vara 3.9+

# Verifiera pnpm
pnpm --version  # Ska vara 8+

# Verifiera Docker
docker --version
```

## 🔍 Felsökning

### Vanliga problem

1. **pnpm ERR_PNPM_PUBLIC_HOIST_PATTERN_DIFF**
   ```bash
   rm -rf node_modules pnpm-lock.yaml
   pnpm install
   ```

2. **Python-beroenden saknas**
   ```bash
   pip install -r requirements.txt
   ```

3. **Docker-problem**
   ```bash
   docker system prune -a
   docker-compose up --build
   ```

## 📝 Loggning

Alla steg loggas i `bootstrap_status.log`:

```bash
echo "$(date) - 00_START_HÄR: Installation verifierad" >> bootstrap_status.log
```

# 🟢 GEOMETRA AI – CURSOR BOOT

## 🧠 Syfte
Starta upp Geometra AI-systemet från grunden via Cursor. Följ stegen i ordning tills systemet körs live via Railway.

## ✅ Översikt

| Steg | Filnamn                  | Beskrivning |
|------|--------------------------|-------------|
| 1    | 01_SYSTEMÖVERSIKT.md     | Läs hela systemarkitekturen |
| 2    | 02_INITIERA_PROJEKT.md   | Initiera nytt Python-projekt |
| 3    | 03_KONFIGURERA_MINNE.md  | Ställ in korttids- och långtidsminne |
| 4    | 04_BYGG_API.md           | Skapa FastAPI /chat och /status |
| 5    | 05_PROMPT_LOGIK.md       | Bygg prompt-bygge och injection |
| 6    | 06_FALLBACK_LOGIK.md     | Lägg till GPT-3.5 fallback |
| 7    | 07_SYSTEMCHECK.md        | Verifiera med `system_check.sh` |
| 8    | 08_TESTNING.md           | Enhets- och systemtestning |
| 9    | 09_CICD_PIPELINE.md      | GitHub Actions + Railway deploy |
| 10   | 10_DEPLOY_RAILWAY.md     | Lansera produktion |
| 🔚   | 99_REFERENSER.md         | Exempel, curl, checklistor |

## 🎯 Mål
- [ ] Systemet kan anropas via `/chat` externt
- [ ] STM + LTM fungerar sömlöst
- [ ] GPT fallback fungerar korrekt
- [ ] CI/CD körs automatiskt
- [ ] Minne är persistent via ChromaDB
- [ ] `system_check.sh` passerar alla test

---
