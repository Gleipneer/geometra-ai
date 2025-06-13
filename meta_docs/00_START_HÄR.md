# Start här

Detta dokument beskriver systemkraven och installationsprocessen för Geometra AI-systemet.

## Systemkrav

### Verktyg
- Node.js-version: 18.x eller senare
- Python-version: 3.12.x
- pnpm-version: 8.x eller senare
- Docker-version: 24.x eller senare

### Verifiera installationer
```bash
# Verifiera Node.js
node --version

# Verifiera Python
python --version

# Verifiera pnpm
pnpm --version

# Verifiera Docker
docker --version
```

## Installation

1. Klona projektet:
```bash
git clone https://github.com/your-org/geometra-ai.git
cd geometra-ai
```

2. Skapa och aktivera Python-miljö:
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
pnpm install
```

## Konfiguration

1. Kopiera `.env.example` till `.env`:
```bash
cp .env.example .env
```

2. Uppdatera miljövariabler i `.env` med dina inställningar.

## Verifiering

Kör systemkontrollen för att verifiera installationen:
```bash
./system_check.sh
```

## Felsökning

### Vanliga problem

1. **Node.js-version**
   - Om du får fel relaterade till Node.js-version, uppdatera till senaste LTS-versionen.

2. **Python-version**
   - Se till att använda Python 3.12.x
   - Om du har flera Python-versioner installerade, använd `pyenv` för att hantera dem.

3. **pnpm-problem**
   - Om du får felet `ERR_PNPM_PUBLIC_HOIST_PATTERN_DIFF`:
     ```bash
     rm -rf node_modules pnpm-lock.yaml
     pnpm install
     ```

4. **Docker-problem**
   - Se till att Docker-tjänsten körs
   - Verifiera att du har rätt behörigheter för att köra Docker

## Nästa steg

1. Läs [Systemöversikt](01_SYSTEMÖVERSIKT.md) för att förstå systemarkitekturen
2. Följ [Projektinitiering](02_INITIERA_PROJEKT.md) för att sätta upp utvecklingsmiljön
3. Konfigurera [Minneskomponenter](03_KONFIGURERA_MINNE.md) 