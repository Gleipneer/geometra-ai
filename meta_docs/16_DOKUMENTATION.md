# Dokumentation

Detta dokument beskriver hur man skapar och underhåller dokumentation för Geometra AI-systemet.

## Översikt

Dokumentationssystemet innehåller:

1. **Teknisk dokumentation**
   - API-dokumentation
   - Kodkommentarer
   - Arkitekturdokumentation

2. **Användardokumentation**
   - Installationsguider
   - Användarguider
   - Felsökningsguider

3. **Utvecklardokumentation**
   - Utvecklingsmiljö
   - Kodstandarder
   - Teststrategier

## Installation

1. Installera dokumentationsverktyg:
```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
pip install graphviz plantuml
```

2. Skapa dokumentationsstruktur:
```bash
mkdir -p docs/{api,user,developer}
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
    'sphinx.ext.graphviz',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
```

2. Skapa `docs/index.rst`:
```rst
Geometra AI Documentation
========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/index
   user/index
   developer/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

### API-dokumentation

1. Skapa `docs/api/index.rst`:
```rst
API Documentation
================

.. toctree::
   :maxdepth: 2

   backend
   frontend
```

2. Skapa `docs/api/backend.rst`:
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

3. Skapa `docs/api/frontend.rst`:
```rst
Frontend API
===========

.. automodule:: frontend.src.api
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
* pnpm 7+

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

3. Skapa `docs/user/usage.rst`:
```rst
Usage Guide
==========

Getting Started
-------------

1. Start backend:

   .. code-block:: bash

      python -m api.main

2. Start frontend:

   .. code-block:: bash

      cd frontend
      pnpm dev

3. Open browser:

   .. code-block:: text

      http://localhost:3000
```

### Utvecklardokumentation

1. Skapa `docs/developer/index.rst`:
```rst
Developer Guide
=============

.. toctree::
   :maxdepth: 2

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
   - Install recommended extensions
   - Configure settings
```

3. Skapa `docs/developer/standards.rst`:
```rst
Coding Standards
==============

Python
------

* Follow PEP 8
* Use type hints
* Write docstrings
* Use black for formatting
* Use isort for imports

TypeScript
---------

* Follow TSLint rules
* Use strict mode
* Write JSDoc comments
* Use Prettier for formatting
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
   - Validera autodoc

2. **Länkproblem**
   - Kontrollera relativa länkar
   - Verifiera externa länkar
   - Validera referenser

3. **Kodkommentarsproblem**
   - Kontrollera docstrings
   - Verifiera type hints
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

1. Implementera [Backup](17_BACKUP.md)
2. Konfigurera [DR](18_DR.md)
3. Skapa [Arkitekturdiagram](19_ARKITEKTURDIAGRAM.md) 