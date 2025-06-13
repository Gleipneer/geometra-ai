# Dokumentation

Detta dokument beskriver hur man skapar och underhåller dokumentation för Geometra AI-systemet.

## Översikt

Dokumentationssystemet innehåller:

1. **Teknisk dokumentation**
   - API-dokumentation
   - Kodkommentarer
   - Arkitekturdiagram

2. **Användardokumentation**
   - Installationsguider
   - Användarguider
   - Felsökningsguider

3. **Utvecklardokumentation**
   - Utvecklingsmiljö
   - Kodstandarder
   - Teststrategi

## Installation

1. Installera dokumentationsverktyg:
```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

2. Installera diagramverktyg:
```bash
pip install graphviz plantuml
```

## Konfiguration

### Sphinx

1. Skapa `docs/conf.py`:
```python
"""Sphinx configuration."""

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Geometra AI'
copyright = '2024, Geometra AI Team'
author = 'Geometra AI Team'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
    'pydantic': ('https://docs.pydantic.dev/', None),
}
```

2. Skapa `docs/index.rst`:
```rst
"""Main documentation page."""

Welcome to Geometra AI's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   development
   troubleshooting

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

### API-dokumentation

1. Skapa `docs/api.rst`:
```rst
"""API documentation."""

API Reference
============

Backend API
----------

.. automodule:: api.main
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api.routers.chat
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api.routers.system
   :members:
   :undoc-members:
   :show-inheritance:

Frontend API
-----------

.. automodule:: frontend.src.api
   :members:
   :undoc-members:
   :show-inheritance:
```

### Användarguide

1. Skapa `docs/usage.rst`:
```rst
"""User guide."""

User Guide
=========

Installation
-----------

1. Installera beroenden:

.. code-block:: bash

   pip install -r requirements.txt
   cd frontend
   pnpm install

2. Starta tjänster:

.. code-block:: bash

   docker-compose up -d

3. Öppna webbläsaren:

   http://localhost:80

Användning
---------

1. Skicka meddelanden:

   - Skriv meddelande i chatten
   - Klicka på "Skicka"
   - Vänta på svar

2. Visualiseringar:

   - Klicka på "Visualisera"
   - Välj typ av visualisering
   - Anpassa parametrar

3. Exportera:

   - Klicka på "Exportera"
   - Välj format
   - Spara fil
```

### Utvecklarguide

1. Skapa `docs/development.rst`:
```rst
"""Developer guide."""

Developer Guide
==============

Utvecklingsmiljö
--------------

1. Installera verktyg:

.. code-block:: bash

   pip install -r requirements-dev.txt
   pre-commit install

2. Konfigurera IDE:

   - Använd VS Code
   - Installera Python-extension
   - Installera ESLint
   - Installera Prettier

Kodstandarder
-----------

1. Python:

   - Följ PEP 8
   - Använd type hints
   - Skriv docstrings
   - Använd black för formatering

2. TypeScript:

   - Följ Airbnb style guide
   - Använd ESLint
   - Använd Prettier
   - Skriv JSDoc

Teststrategi
----------

1. Enhetstester:

   - Använd pytest
   - Använd Jest
   - Skriv testfall
   - Kör tester

2. Integrationstester:

   - Använd pytest
   - Använd Cypress
   - Skriv testfall
   - Kör tester

3. Prestandatester:

   - Använd locust
   - Skriv testfall
   - Kör tester
```

## Validering

1. Bygg dokumentation:
```bash
cd docs
make html
```

2. Verifiera länkar:
```bash
make linkcheck
```

3. Verifiera kodkommentarer:
```bash
pydocstyle .
```

## Felsökning

### Dokumentationsproblem

1. **Byggproblem**
   - Kontrollera Sphinx-konfiguration
   - Verifiera RST-syntax
   - Validera länkar

2. **Länkproblem**
   - Kontrollera URL:er
   - Verifiera referenser
   - Validera ankare

3. **Formateringsproblem**
   - Kontrollera RST-syntax
   - Verifiera indentation
   - Validera listor

## Loggning

1. Konfigurera loggning i `docs/utils/logging.py`:
```python
"""Documentation logging configuration."""

import logging
import os
from datetime import datetime

def setup_docs_logging():
    """Configure logging for documentation."""
    log_dir = "logs/docs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"docs_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
```

## Nästa steg

1. Implementera [Tester](11_TESTER.md)
2. Konfigurera [Övervakning](12_ÖVERVAKNING.md)
3. Skapa [Arkitekturdiagram](13_ARKITEKTUR.md) 