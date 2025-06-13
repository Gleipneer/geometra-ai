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

# Graphviz settings
graphviz_output_format = 'svg'
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
   ai
```

3. Skapa `docs/api/backend.rst`:
```rst
Backend API
==========

.. automodule:: api.main
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api.routes
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
* PostgreSQL 13+
* Redis 6+

Installation Steps
----------------

1. Clone repository::

   git clone https://github.com/geometra/ai.git
   cd ai

2. Install dependencies::

   pip install -r requirements.txt
   npm install

3. Configure environment::

   cp .env.example .env
   # Edit .env with your settings

4. Initialize database::

   python manage.py migrate
   python manage.py createsuperuser

5. Start services::

   python manage.py runserver
   npm run dev
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

2. Skapa `docs/developer/standards.rst`:
```rst
Coding Standards
==============

Python
------

* Follow PEP 8 style guide
* Use type hints
* Write docstrings for all functions
* Keep functions small and focused
* Use meaningful variable names

JavaScript
---------

* Follow ESLint configuration
* Use TypeScript
* Write JSDoc comments
* Use async/await for promises
* Follow component structure

Git
---

* Use feature branches
* Write descriptive commit messages
* Keep commits atomic
* Review code before merging
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
   - Validera autodoc

2. **Länkproblem**
   - Kontrollera externa länkar
   - Verifiera interna länkar
   - Validera referenser

3. **Kodkommentarsproblem**
   - Kontrollera docstrings
   - Verifiera type hints
   - Validera format

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

1. Implementera [Backup](29_BACKUP.md)
2. Konfigurera [DR](30_DR.md)
3. Skapa [Arkitekturdiagram](31_ARKITEKTURDIAGRAM.md) 