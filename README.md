# 🧠 GEOMETRA AI – FULLSTACK GPT-ASSISTENT

> En självdiagnostiserande AI med minne, promptlogik, CI/CD och fallback – byggd för framtiden.

---

## 🔧 Syfte

Geometra AI är ett API-exponerat, GPT-drivet assistentsystem byggt i Python med:
- 🔁 Token- och vektorbaserat minne
- 📬 OpenAI-kommunikation med fallback
- ☁️ Railway-deploy via CI/CD
- 🧪 Full testtäckning och systemcheck

---

## 📦 Mappstruktur

```bash
geometra-ai/
├── api/                    # FastAPI med /chat, /status, /memory
├── ai/                     # Promptlogik och fallback
├── memory/                 # Korttidsminne och ChromaDB-lagring
├── tests/                  # Enhetstest, integration, systemtest
├── .env                    # API-nycklar och konfiguration
├── system_check.sh         # Lokalt hälsotest
└── .github/workflows/      # CI/CD workflow med Railway
🚀 Snabbstart
bash
Kopiera kod
git clone https://github.com/dittnamn/geometra-ai.git
cd geometra-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
Testa i terminalen:

bash
Kopiera kod
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"user_id": "joakim", "message": "Vad kan du hjälpa mig med?"}'
🧱 Arkitekturöversikt
Komponent	Beskrivning
chat_engine.py	Dirigerar GPT-anrop och hanterar kontext
prompt_builder.py	Bygger prompts dynamiskt utifrån minne och intention
short_term_memory.py	Temporär dialog (RAM)
long_term_memory.py	Persistent minne via ChromaDB
fallback.py	Säkerställer svar via GPT-3.5 vid fel
api/main.py	FastAPI med endpoints för användning
system_check.sh	Skript som testar OpenAI + Chroma + miljö
deploy.yml	CI/CD för staging och production via Railway

✅ Funktionell checklista
Funktion	Status
Korttidsminne aktivt	✅
Långtidsminne persistent (Chroma)	✅
GPT-4-anrop fungerar	✅
GPT-3.5 fallback implementerad	✅
API via FastAPI	✅
CI/CD med GitHub Actions + Railway	✅
Enhetstest & systemtest	✅
system_check.sh verifierar miljö	✅

🧪 Tester
bash
Kopiera kod
pytest tests -s
mypy .
./system_check.sh
☁️ Deployment
Railway staging: https://geometra-ai-staging.up.railway.app

Railway production: https://geometra-ai-production.up.railway.app

Push till:

staging = testmiljö

main = produktion

🧠 AI-kommandon via cURL
bash
Kopiera kod
curl -X POST https://geometra-ai-production.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "joakim", "message": "Vad sa jag senast om budgeten?"}'
🔁 Metastyrning (Cursor)
Följ meta/00_START_HÄR.md för att:

Bygga hela systemet från grunden

Se varje steg med checklista

Återanvänd strukturen för andra AI-projekt

🧭 Nästa steg
 Lägg till JWT eller API-nyckel-autentisering

 Skapa användar- och rollhantering

 Integrera Logseq eller annan kunskapsbas

 Lägg till fler GPT-motorer eller lokal modell

"The AI that remembers will be the AI that leads."

## 🧠 AI-assistent

Geometra AI:s övergripande AI-assistent är en avancerad AI med bred kompetens inom mjukvaruutveckling, AI-integration, systemarkitektur och projektledning.

### 📡 Modellhantering

Assistenten använder olika AI-modeller för olika typer av uppgifter:

- **GPT-4 Omni**: Används för:
  - Komplexa och kreativa uppgifter
  - Kontexttunga problem
  - Strategisk planering
  - Arkitekturdesign
  - Komplex felsökning

- **GPT-3.5**: Används för:
  - Enklare databehandling
  - Grundläggande felsökning
  - Rutinuppgifter
  - Kostnadseffektiva operationer

Modellvalet sker dynamiskt baserat på:
- Uppgiftens komplexitet
- Krävd svarstid
- Kostnadseffektivitet

### 🤖 Självorganisering och roller

Assistenten skapar och koordinerar dynamiskt interna "underassistenter":

1. **Planeringsassistent**
   - Strategisk planering
   - Prioritering
   - Roadmap-utveckling
   - Projektöversikt

2. **Kodningsassistent**
   - Kodimplementation
   - Refaktorisering
   - Kodgranskning
   - Bästa praxis

3. **Testassistent**
   - Testskrivning
   - Testanalys
   - Testförbättring
   - Kvalitetssäkring

4. **Dokumentationsassistent**
   - Teknisk dokumentation
   - API-dokumentation
   - Användarguider
   - README-filer

5. **Felsökningsassistent**
   - Felanalys
   - Lösningsförslag
   - Prestandaoptimering
   - Säkerhetsanalys

### ⚡ Proaktivitet och driv

Assistenten är proaktiv och:
- Följer upp öppna frågor
- Påminner om ouppklarade uppgifter
- Föreslår nästa steg
- Anpassar tonen efter kontext:
  - Formell för dokumentation och rapporter
  - Informell och engagerad i kreativa diskussioner

### 🎯 Uppgiftshantering

För varje uppgift:
1. Analyserar komplexitet och krav
2. Väljer lämplig AI-modell
3. Aktiverar relevanta underassistenter
4. Koordinerar arbetsflödet
5. Levererar strukturerade svar
6. Följer upp och verifierar resultat

### 💡 Kommunikation

Assistenten:
- Ställer precisionsfrågor vid oklarheter
- Ger strukturerade och prioriterade svar
- Dokumenterar beslut och åtgärder
- Säkerställer att inga viktiga detaljer missas

### 📊 Statusrapportering

Varje statusrapport innehåller:
1. Aktuell status
2. Prioriterade nästa steg
3. Identifierade risker
4. Rekommenderade åtgärder
5. Tidsuppskattningar

### 🔄 Kontinuerlig förbättring

Assistenten:
- Lär av tidigare interaktioner
- Anpassar strategier baserat på resultat
- Optimera modellval och arbetsflöden
- Förbättrar dokumentation och processer

## Miljövariabler

För att köra systemet behöver du konfigurera följande miljövariabler:

```bash
# API Keys
export OPENAI_API_KEY=your_openai_api_key_here

# Database URLs
export REDIS_URL=redis://localhost:6379
export DATABASE_URL=postgresql://localhost/geometra

# Railway Configuration
export RAILWAY_TOKEN=your_railway_token_here
export RAILWAY_ENVIRONMENT=production

# Monitoring
export MONITORING_INTERVAL=300
export SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# Security
export JWT_SECRET=your_jwt_secret_here
export JWT_ALGORITHM=HS256
export ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
export APP_VERSION=1.0.0
export ENVIRONMENT=development
export DEBUG=true
```

Du kan lägga till dessa i din `.bashrc` eller köra dem direkt i terminalen.

## Systemkrav

- Python 3.12+
- Node.js 20+
- Docker
- Redis
- PostgreSQL

## Installation

1. Klona repot:
```bash
git clone https://github.com/yourusername/geometra-ai.git
cd geometra-ai
```

2. Installera Python-beroenden:
```bash
pip install -r requirements.txt
```

3. Installera Node.js-beroenden:
```bash
cd frontend
npm install
cd ..
```

4. Starta tjänsterna:
```bash
docker-compose up -d
```

5. Kör systemtest:
```bash
./scripts/system_check.sh
```

## Utveckling

För att starta utvecklingsservern:

```bash
# Backend
uvicorn src.api.main:app --reload

# Frontend
cd frontend
npm run dev
```

## Testning

```bash
# Kör alla tester
pytest

# Kör frontend-tester
cd frontend
npm test
```

## Deployment

Systemet är konfigurerat för automatisk deployment till Railway. Se `.github/workflows/deploy.yml` för mer information.

## Monitoring

Monitoring är konfigurerat via `monitoring/scripts/monitor.py`. Se `monitoring/config/monitoring_config.yml` för konfiguration.

## Säkerhet

- Alla API-nycklar och hemligheter hanteras via miljövariabler
- JWT för autentisering
- Rate limiting är implementerat
- Loggning av säkerhetshändelser

## Bidra

1. Forka repot
2. Skapa en feature branch
3. Committa dina ändringar
4. Pusha till branchen
5. Skapa en Pull Request

## Licens

MIT