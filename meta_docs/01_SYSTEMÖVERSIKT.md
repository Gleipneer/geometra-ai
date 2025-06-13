# Systemöversikt

Detta dokument beskriver systemarkitekturen och komponenterna i Geometra AI-systemet.

## Systemarkitektur

Geometra AI är byggt med en mikrotjänstarkitektur som består av följande huvudkomponenter:

1. **Frontend**
   - React-baserad webbapplikation
   - TypeScript för typsäkerhet
   - Material-UI för komponenter
   - Redux för tillståndshantering

2. **Backend API**
   - FastAPI för REST API
   - Python 3.12
   - Async/await för prestanda
   - OpenAPI/Swagger för dokumentation

3. **Minneskomponenter**
   - ChromaDB för långtidsminne (LTM)
   - Redis för korttidsminne (STM)
   - Vektorembeddingar för semantisk sökning

4. **AI-komponenter**
   - OpenAI GPT-4 som primär modell
   - GPT-3.5 Turbo som fallback
   - Prompt-mallar för konsistent respons
   - Kontext-hantering för minnesintegration

## Dataflöde

1. **Användarinteraktion**
   ```
   Användare -> Frontend -> Backend API -> AI-komponenter
   ```

2. **Minneshantering**
   ```
   AI-komponenter -> STM (Redis) -> LTM (ChromaDB)
   ```

3. **Fallback-flöde**
   ```
   Primär modell -> Fel -> Fallback-modell -> Användare
   ```

## Komponenter

### Frontend
- `frontend/` - React-applikation
- `frontend/src/components/` - UI-komponenter
- `frontend/src/store/` - Redux-tillstånd
- `frontend/src/api/` - API-integration

### Backend
- `api/` - FastAPI-applikation
- `api/routes/` - API-endpoints
- `api/models/` - Datamodeller
- `api/services/` - Affärslogik

### Minneskomponenter
- `memory/` - Minneshantering
- `memory/chroma/` - ChromaDB-integration
- `memory/redis/` - Redis-integration
- `memory/utils/` - Hjälpfunktioner

### AI-komponenter
- `ai/` - AI-integration
- `ai/prompts/` - Prompt-mallar
- `ai/fallback/` - Fallback-logik
- `ai/utils/` - AI-hjälpfunktioner

## Validering

För att verifiera att alla komponenter fungerar korrekt:

1. **Systemkontroll**
   ```bash
   ./system_check.sh
   ```

2. **Enhetstester**
   ```bash
   python -m pytest tests/unit/
   ```

3. **Integrationstester**
   ```bash
   python -m pytest tests/integration/
   ```

4. **E2E-tester**
   ```bash
   python -m pytest tests/e2e/
   ```

## Nästa steg

1. Följ [Projektinitiering](02_INITIERA_PROJEKT.md) för att sätta upp utvecklingsmiljön
2. Konfigurera [Minneskomponenter](03_KONFIGURERA_MINNE.md)
3. Bygg [API:et](04_BYGG_API.md) 