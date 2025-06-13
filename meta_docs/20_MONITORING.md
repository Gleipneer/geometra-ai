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
    # Create log directory
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(
                os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
            ),
            logging.StreamHandler()
        ]
    )
    
    # Configure Loki handler
    loki_handler = LokiHandler(
        url="http://loki:3100/loki/api/v1/push",
        tags={"application": "geometra-ai"},
        version="1"
    )
    
    # Add Loki handler to root logger
    logging.getLogger().addHandler(loki_handler)
    
    # Configure application loggers
    loggers = {
        "api": logging.getLogger("api"),
        "ai": logging.getLogger("ai"),
        "db": logging.getLogger("db"),
        "security": logging.getLogger("security")
    }
    
    for logger in loggers.values():
        logger.setLevel(logging.INFO)
        logger.addHandler(loki_handler)
```

2. Skapa `monitoring/logging/handlers.py`:
```python
"""Log handlers."""

import logging
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """JSON log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

class StructuredLogger:
    """Structured logger."""
    
    def __init__(self, name: str):
        """Initialize logger."""
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs: Any):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs: Any):
        """Log error message."""
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs: Any):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs: Any):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
```

### Mätvärden

1. Skapa `monitoring/metrics/prometheus.py`:
```python
"""Prometheus metrics."""

from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, Any

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"]
)

# System metrics
system_cpu_usage = Gauge(
    "system_cpu_usage",
    "CPU usage percentage"
)

system_memory_usage = Gauge(
    "system_memory_usage",
    "Memory usage percentage"
)

system_disk_usage = Gauge(
    "system_disk_usage",
    "Disk usage percentage"
)

# AI metrics
ai_requests_total = Counter(
    "ai_requests_total",
    "Total AI requests",
    ["model", "status"]
)

ai_request_duration_seconds = Histogram(
    "ai_request_duration_seconds",
    "AI request duration",
    ["model"]
)

ai_tokens_total = Counter(
    "ai_tokens_total",
    "Total AI tokens",
    ["model", "type"]
)

# Database metrics
db_connections = Gauge(
    "db_connections",
    "Database connections",
    ["database"]
)

db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["database", "type"]
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["database", "type"]
)

class MetricsCollector:
    """Metrics collector."""
    
    def __init__(self):
        """Initialize collector."""
        self.metrics = {
            "http": {
                "requests": http_requests_total,
                "duration": http_request_duration_seconds
            },
            "system": {
                "cpu": system_cpu_usage,
                "memory": system_memory_usage,
                "disk": system_disk_usage
            },
            "ai": {
                "requests": ai_requests_total,
                "duration": ai_request_duration_seconds,
                "tokens": ai_tokens_total
            },
            "db": {
                "connections": db_connections,
                "queries": db_queries_total,
                "duration": db_query_duration_seconds
            }
        }
    
    def record_metric(self, category: str, metric: str, value: Any, **labels: Dict[str, str]):
        """Record metric."""
        if category in self.metrics and metric in self.metrics[category]:
            self.metrics[category][metric].labels(**labels).observe(value)
```

2. Skapa `monitoring/metrics/collectors.py`:
```python
"""Metric collectors."""

import psutil
import time
from typing import Dict, Any
from .prometheus import MetricsCollector

class SystemCollector:
    """System metrics collector."""
    
    def __init__(self, metrics: MetricsCollector):
        """Initialize collector."""
        self.metrics = metrics
    
    def collect(self):
        """Collect system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics.record_metric(
            "system",
            "cpu",
            cpu_percent
        )
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.metrics.record_metric(
            "system",
            "memory",
            memory.percent
        )
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.metrics.record_metric(
            "system",
            "disk",
            disk.percent
        )

class AICollector:
    """AI metrics collector."""
    
    def __init__(self, metrics: MetricsCollector):
        """Initialize collector."""
        self.metrics = metrics
    
    def collect(self, model: str, duration: float, tokens: int, status: str):
        """Collect AI metrics."""
        # Request metrics
        self.metrics.record_metric(
            "ai",
            "requests",
            1,
            model=model,
            status=status
        )
        
        # Duration metrics
        self.metrics.record_metric(
            "ai",
            "duration",
            duration,
            model=model
        )
        
        # Token metrics
        self.metrics.record_metric(
            "ai",
            "tokens",
            tokens,
            model=model,
            type="total"
        )

class DatabaseCollector:
    """Database metrics collector."""
    
    def __init__(self, metrics: MetricsCollector):
        """Initialize collector."""
        self.metrics = metrics
    
    def collect(self, database: str, query_type: str, duration: float):
        """Collect database metrics."""
        # Query metrics
        self.metrics.record_metric(
            "db",
            "queries",
            1,
            database=database,
            type=query_type
        )
        
        # Duration metrics
        self.metrics.record_metric(
            "db",
            "duration",
            duration,
            database=database,
            type=query_type
        )
```

### Varningar

1. Skapa `monitoring/alerts/rules.py`:
```python
"""Alert rules."""

from typing import Dict, Any, List
import json
import os

class AlertRule:
    """Alert rule."""
    
    def __init__(self, name: str, condition: str, threshold: float, duration: str):
        """Initialize rule."""
        self.name = name
        self.condition = condition
        self.threshold = threshold
        self.duration = duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "condition": self.condition,
            "threshold": self.threshold,
            "duration": self.duration
        }

class AlertManager:
    """Alert manager."""
    
    def __init__(self, rules_file: str):
        """Initialize manager."""
        self.rules_file = rules_file
        self.rules: List[AlertRule] = []
        self.load_rules()
    
    def load_rules(self):
        """Load alert rules."""
        if os.path.exists(self.rules_file):
            with open(self.rules_file, 'r') as f:
                rules_data = json.load(f)
                for rule_data in rules_data:
                    self.rules.append(AlertRule(
                        name=rule_data["name"],
                        condition=rule_data["condition"],
                        threshold=rule_data["threshold"],
                        duration=rule_data["duration"]
                    ))
    
    def save_rules(self):
        """Save alert rules."""
        rules_data = [rule.to_dict() for rule in self.rules]
        with open(self.rules_file, 'w') as f:
            json.dump(rules_data, f, indent=2)
    
    def add_rule(self, rule: AlertRule):
        """Add alert rule."""
        self.rules.append(rule)
        self.save_rules()
    
    def remove_rule(self, name: str):
        """Remove alert rule."""
        self.rules = [rule for rule in self.rules if rule.name != name]
        self.save_rules()
    
    def get_rules(self) -> List[AlertRule]:
        """Get alert rules."""
        return self.rules
```

2. Skapa `monitoring/alerts/notifications.py`:
```python
"""Alert notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import json
import os

class Notification:
    """Alert notification."""
    
    def __init__(self, alert: Dict[str, Any], recipients: List[str]):
        """Initialize notification."""
        self.alert = alert
        self.recipients = recipients
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert": self.alert,
            "recipients": self.recipients
        }

class NotificationManager:
    """Notification manager."""
    
    def __init__(self, config_file: str):
        """Initialize manager."""
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load notification config."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save notification config."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def send_email(self, notification: Notification):
        """Send email notification."""
        msg = MIMEMultipart()
        msg["From"] = self.config["smtp"]["username"]
        msg["To"] = ", ".join(notification.recipients)
        msg["Subject"] = f"Alert: {notification.alert['name']}"
        
        body = f"""
        Alert: {notification.alert['name']}
        Condition: {notification.alert['condition']}
        Threshold: {notification.alert['threshold']}
        Duration: {notification.alert['duration']}
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(self.config["smtp"]["host"], self.config["smtp"]["port"]) as server:
            server.starttls()
            server.login(
                self.config["smtp"]["username"],
                self.config["smtp"]["password"]
            )
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

### Monitoringproblem

1. **Loggningsproblem**
   - Kontrollera loggfiler
   - Verifiera format
   - Validera innehåll

2. **Mätvärdesproblem**
   - Kontrollera samling
   - Verifiera export
   - Validera data

3. **Varningsproblem**
   - Kontrollera regler
   - Verifiera notifieringar
   - Validera konfiguration

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

1. Konfigurera [Säkerhet](21_SÄKERHET.md)
2. Skapa [Dokumentation](22_DOKUMENTATION.md)
3. Implementera [Backup](23_BACKUP.md) 