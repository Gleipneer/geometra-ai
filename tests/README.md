# Geometra AI Test Suite

Detta är testsuiten för Geometra AI-systemet. Den innehåller enhetstester, integrationstester och end-to-end-tester för alla komponenter i systemet.

## Struktur

```
tests/
├── unit/                 # Enhetstester
│   ├── system/          # Systemtester
│   ├── installation/    # Installationstester
│   ├── backend/         # Backendtester
│   ├── frontend/        # Frontendtester
│   ├── ai/             # AI-tester
│   ├── db/             # Databastester
│   ├── api/            # API-tester
│   ├── auth/           # Autentiseringstester
│   └── logging/        # Loggningstester
├── integration/         # Integrationstester
├── e2e/                # End-to-end-tester
├── fixtures/           # Testdata
├── mocks/             # Mock-objekt
├── utils/             # Testverktyg
└── docs/              # Testdokumentation
```

## Körning

För att köra alla tester:

```bash
python -m pytest tests/test_all.py -v
```

För att köra specifika tester:

```bash
# Enhetstester
python -m pytest tests/unit -v

# Integrationstester
python -m pytest tests/integration -v

# End-to-end-tester
python -m pytest tests/e2e -v
```

## Testsekvens

Testerna körs i följande sekvens:

1. System Setup
2. Installation
3. Backend Setup
4. Frontend Setup
5. AI Setup
6. Database Setup
7. API Setup
8. Authentication Setup
9. Logging Setup
10. Integration
11. End-to-End

## Testrapporter

Testrapporter genereras i `logs/`:

- `test_run_YYYYMMDD_HHMMSS.log` - Detaljerad testlogg
- `test_results.json` - Testresultat per test
- `test_report.json` - Sammanfattande testrapport

## Testdata

Testdata finns i `tests/fixtures/`:

- `test_data.json` - Generell testdata
- `test_config.yaml` - Testkonfiguration
- `test_users.json` - Testanvändare
- `test_documents.json` - Testdokument

## Mock-objekt

Mock-objekt finns i `tests/mocks/`:

- `mock_redis.py` - Redis-mock
- `mock_chroma.py` - ChromaDB-mock
- `mock_openai.py` - OpenAI-mock
- `mock_requests.py` - HTTP-requests-mock

## Testverktyg

Testverktyg finns i `tests/utils/`:

- `test_helpers.py` - Hjälpfunktioner
- `test_assertions.py` - Anpassade assertions
- `test_generators.py` - Testdatageneratorer

## Dokumentation

Testdokumentation finns i `tests/docs/`:

- `test_guide.md` - Testguide
- `test_examples.md` - Testexempel
- `test_best_practices.md` - Bästa praxis

## Beroenden

För att köra testerna behövs:

```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

## Konfiguration

Testkonfiguration finns i:

- `pytest.ini` - Pytest-konfiguration
- `.coveragerc` - Coverage-konfiguration

## Felsökning

Om testerna misslyckas:

1. Kontrollera testloggen i `logs/`
2. Verifiera att alla beroenden är installerade
3. Kontrollera att testdata är korrekt
4. Verifiera att mock-objekt fungerar som förväntat

## Bidra

För att bidra till testsuiten:

1. Följ teststrukturen
2. Använd befintliga fixtures och mocks
3. Dokumentera nya tester
4. Uppdatera testrapporter
5. Följ bästa praxis i dokumentationen 