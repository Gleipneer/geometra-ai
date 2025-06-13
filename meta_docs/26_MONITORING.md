# Monitoring

Detta dokument beskriver hur man konfigurerar och hanterar monitoring för Geometra AI-systemet.

## Översikt

Monitoringsystemet innehåller:

1. **Loggning**
   - Applikationsloggar
   - Systemloggar
   - Säkerhetsloggar

2. **Mätvärden**
   - Prestandamätvärden
   - Resursmätvärden
   - Användningsmätvärden

3. **Varningar**
   - Systemvarningar
   - Säkerhetsvarningar
   - Prestandavarningar

## Installation

1. Installera monitoringverktyg:
```bash
pip install prometheus-client grafana-api python-logging-loki
```

2. Skapa monitoringstruktur:
```bash
mkdir -p monitoring/{logging,metrics,alerts}
```

## Konfiguration

### Loggning

1. Skapa `monitoring/logging/config.py`:
```python
"""Logging configuration."""

import logging
import os
from datetime import datetime
from python_logging_loki import LokiHandler

def setup_logging():
    """Configure logging."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create loggers
    loggers = {
        'api': logging.getLogger('api'),
        'ai': logging.getLogger('ai'),
        'db': logging.getLogger('db'),
        'security': logging.getLogger('security')
    }
    
    # Configure handlers
    for name, logger in loggers.items():
        # File handler
        log_file = os.path.join(
            log_dir,
            f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Loki handler
        loki_handler = LokiHandler(
            url="http://loki:3100/loki/api/v1/push",
            tags={"application": name},
            version="1"
        )
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(loki_handler)
        logger.setLevel(logging.INFO)
```

2. Skapa `monitoring/logging/handlers.py`:
```python
"""Logging handlers."""

import json
import logging
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """JSON log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data)

class StructuredLogger:
    """Structured logger."""
    
    def __init__(self, name: str):
        """Initialize structured logger."""
        self.logger = logging.getLogger(name)
    
    def log(self, level: int, message: str, **kwargs: Any) -> None:
        """Log message with extra data."""
        extra = {
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        self.logger.log(level, message, extra=extra)
```

### Mätvärden

1. Skapa `monitoring/metrics/prometheus.py`:
```python
"""Prometheus metrics."""

from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, Any

# HTTP metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# System metrics
system_cpu_usage = Gauge(
    'system_cpu_usage',
    'CPU usage percentage'
)

system_memory_usage = Gauge(
    'system_memory_usage',
    'Memory usage percentage'
)

system_disk_usage = Gauge(
    'system_disk_usage',
    'Disk usage percentage'
)

# AI metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['model', 'status']
)

ai_request_duration_seconds = Histogram(
    'ai_request_duration_seconds',
    'AI request duration',
    ['model']
)

ai_tokens_total = Counter(
    'ai_tokens_total',
    'Total tokens processed',
    ['model', 'type']
)

# Database metrics
db_connections = Gauge(
    'db_connections',
    'Database connections',
    ['database']
)

db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['database', 'type']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['database', 'type']
)
```

2. Skapa `monitoring/metrics/collectors.py`:
```python
"""Metric collectors."""

import psutil
import time
from typing import Dict, Any
from .prometheus import (
    system_cpu_usage,
    system_memory_usage,
    system_disk_usage
)

class SystemMetricsCollector:
    """System metrics collector."""
    
    def collect(self) -> None:
        """Collect system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        system_memory_usage.set(memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        system_disk_usage.set(disk.percent)

class AIMetricsCollector:
    """AI metrics collector."""
    
    def collect(self, model: str, duration: float, tokens: int) -> None:
        """Collect AI metrics."""
        # Request duration
        ai_request_duration_seconds.labels(model=model).observe(duration)
        
        # Tokens
        ai_tokens_total.labels(model=model, type='input').inc(tokens)

class DatabaseMetricsCollector:
    """Database metrics collector."""
    
    def collect(self, database: str, query_type: str, duration: float) -> None:
        """Collect database metrics."""
        # Query duration
        db_query_duration_seconds.labels(
            database=database,
            type=query_type
        ).observe(duration)
        
        # Query count
        db_queries_total.labels(
            database=database,
            type=query_type
        ).inc()
```

### Varningar

1. Skapa `monitoring/alerts/rules.py`:
```python
"""Alert rules."""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AlertRule:
    """Alert rule."""
    
    name: str
    condition: str
    duration: str
    severity: str
    description: str
    labels: Dict[str, str]

class AlertManager:
    """Alert manager."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.rules: List[AlertRule] = []
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add alert rule."""
        self.rules.append(rule)
    
    def get_rules(self) -> List[AlertRule]:
        """Get all alert rules."""
        return self.rules
    
    def evaluate_rules(self, metrics: Dict[str, Any]) -> List[AlertRule]:
        """Evaluate alert rules."""
        triggered = []
        for rule in self.rules:
            if self._evaluate_rule(rule, metrics):
                triggered.append(rule)
        return triggered
    
    def _evaluate_rule(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate single alert rule."""
        # TODO: Implement rule evaluation
        return False
```

2. Skapa `monitoring/alerts/notifications.py`:
```python
"""Alert notifications."""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

@dataclass
class Notification:
    """Alert notification."""
    
    alert: str
    severity: str
    description: str
    timestamp: datetime
    labels: Dict[str, str]

class NotificationManager:
    """Notification manager."""
    
    def __init__(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str):
        """Initialize notification manager."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
    
    def send_notification(self, notification: Notification) -> None:
        """Send notification."""
        # Create email
        msg = MIMEText(f"""
        Alert: {notification.alert}
        Severity: {notification.severity}
        Description: {notification.description}
        Time: {notification.timestamp}
        Labels: {notification.labels}
        """)
        
        msg['Subject'] = f"Alert: {notification.alert}"
        msg['From'] = self.smtp_user
        msg['To'] = "admin@geometra.ai"
        
        # Send email
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
```

## Validering

1. Testa loggning:
```bash
python -m monitoring.logging.config
```

2. Testa mätvärden:
```bash
python -m monitoring.metrics.prometheus
```

3. Testa varningar:
```bash
python -m monitoring.alerts.rules
```

## Felsökning

### Monitoring-problem

1. **Loggningsproblem**
   - Kontrollera loggfiler
   - Verifiera format
   - Validera innehåll

2. **Mätvärdesproblem**
   - Kontrollera samling
   - Verifiera värden
   - Validera format

3. **Varningsproblem**
   - Kontrollera regler
   - Verifiera notifieringar
   - Validera format

## Loggning

1. Konfigurera loggning i `monitoring/utils/logging.py`:
```python
"""Monitoring logging configuration."""

import logging
import os
from datetime import datetime

def setup_monitoring_logging():
    """Configure logging for monitoring."""
    log_dir = "logs/monitoring"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"monitoring_{datetime.now().strftime('%Y%m%d')}.log"
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

1. Konfigurera [Säkerhet](27_SÄKERHET.md)
2. Skapa [Dokumentation](28_DOKUMENTATION.md)
3. Implementera [Backup](29_BACKUP.md) 