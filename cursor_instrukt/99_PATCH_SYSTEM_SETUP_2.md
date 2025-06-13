# System Setup Patch 2

## Loggning

Skapa en loggkonfigurationsfil:

```bash
mkdir -p src/logging
```

```python
# src/logging/config.py
import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging():
    """Configure system logging."""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger

# Create test logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
```

## Backup

Skapa backup-kataloger:

```bash
# Create backup directories
mkdir -p backup/{db,files,code}

# Create backup configuration
mkdir -p src/backup
```

```python
# src/backup/config.py
from pathlib import Path

BACKUP_DIR = Path("backup")
DB_BACKUP_DIR = BACKUP_DIR / "db"
FILES_BACKUP_DIR = BACKUP_DIR / "files"
CODE_BACKUP_DIR = BACKUP_DIR / "code"

def setup_backup():
    """Setup backup directories."""
    for directory in [BACKUP_DIR, DB_BACKUP_DIR, FILES_BACKUP_DIR, CODE_BACKUP_DIR]:
        directory.mkdir(exist_ok=True)
```

## Monitoring

Skapa monitoring-kataloger:

```bash
# Create monitoring directories
mkdir -p monitoring/{logging,metrics,alerts}

# Create monitoring configuration
mkdir -p src/monitoring
```

```python
# src/monitoring/config.py
from pathlib import Path

MONITORING_DIR = Path("monitoring")
LOGGING_DIR = MONITORING_DIR / "logging"
METRICS_DIR = MONITORING_DIR / "metrics"
ALERTS_DIR = MONITORING_DIR / "alerts"

def setup_monitoring():
    """Setup monitoring directories."""
    for directory in [MONITORING_DIR, LOGGING_DIR, METRICS_DIR, ALERTS_DIR]:
        directory.mkdir(exist_ok=True)
```

## Kör patch

```bash
# Create directories and files
mkdir -p src/{logging,backup,monitoring}
touch src/logging/config.py src/backup/config.py src/monitoring/config.py

# Copy content to files
# (Copy the Python code above to respective files)

# Create directories
mkdir -p backup/{db,files,code}
mkdir -p monitoring/{logging,metrics,alerts}

# Run setup
python -c "
from src.logging.config import setup_logging
from src.backup.config import setup_backup
from src.monitoring.config import setup_monitoring

setup_logging()
setup_backup()
setup_monitoring()
"

# Verify setup
pytest tests/unit/system/test_system_overview.py -v
``` 