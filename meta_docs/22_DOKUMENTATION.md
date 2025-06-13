# Dokumentation

Detta dokument beskriver hur man skapar och underhåller dokumentation för Geometra AI-systemet.

## Översikt

Dokumentationssystemet innehåller:

1. **Teknisk dokumentation**
   - API-dokumentation
   - Kodkommentarer
   - Arkitekturdiagram

2. **Användardokumentation**
   - Installationsguide
   - Användarguide
   - Felsökningsguide

3. **Utvecklardokumentation**
   - Utvecklingsmiljö
   - Kodstandarder
   - Testning

## Installation

1. Installera dokumentationsverktyg:
```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints graphviz plantuml
```

2. Skapa dokumentationsstruktur:
```bash
mkdir -p docs/{api,user,developer}
```

## Konfiguration

### Teknisk dokumentation

1. Skapa `docs/conf.py`:
```python
"""Sphinx configuration."""

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Geometra AI'
copyright = '2024, Geometra'
author = 'Geometra'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
```

2. Skapa `docs/api/index.rst`:
```rst
API Documentation
===============

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   backend
   frontend
```

3. Skapa `docs/api/backend.rst`:
```rst
Backend API
==========

.. automodule:: backend.api
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.models
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.services
   :members:
   :undoc-members:
   :show-inheritance:
```

### Användardokumentation

1. Skapa `docs/user/index.rst`:
```rst
User Guide
=========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   troubleshooting
```

2. Skapa `docs/user/installation.rst`:
```rst
Installation Guide
================

System Requirements
-----------------

* Python 3.8+
* Node.js 16+
* Redis
* ChromaDB

Installation Steps
----------------

1. Clone repository:
   .. code-block:: bash

      git clone https://github.com/geometra/ai.git
      cd ai

2. Install backend:
   .. code-block:: bash

      pip install -r requirements.txt

3. Install frontend:
   .. code-block:: bash

      cd frontend
      pnpm install
```

### Utvecklardokumentation

1. Skapa `docs/developer/index.rst`:
```rst
Developer Guide
=============

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   environment
   standards
   testing
```

2. Skapa `docs/developer/environment.rst`:
```rst
Development Environment
=====================

Setup
-----

1. Install development tools:
   .. code-block:: bash

      pip install -r requirements-dev.txt

2. Configure pre-commit hooks:
   .. code-block:: bash

      pre-commit install

3. Setup IDE:
   - Install VS Code
   - Install Python extension
   - Install ESLint extension
```

## Validering

1. Bygg dokumentation:
```bash
cd docs
make html
```

2. Kontrollera länkar:
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
   - Validera Python-kod

2. **Länkproblem**
   - Kontrollera länkar
   - Verifiera referenser
   - Validera bilder

3. **Kodkommentarsproblem**
   - Kontrollera docstrings
   - Verifiera typer
   - Validera exempel

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

1. Implementera [Backup](23_BACKUP.md)
2. Konfigurera [DR](24_DR.md)
3. Skapa [Arkitekturdiagram](25_ARKITEKTURDIAGRAM.md) 