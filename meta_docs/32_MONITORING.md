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

1. Installera monitoringsverktyg:
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
    
    # Configure loggers
    loggers = {
        'api': logging.getLogger('api'),
        'ai': logging.getLogger('ai'),
        'db': logging.getLogger('db'),
        'security': logging.getLogger('security')
    }
    
    # Configure handlers
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    )
    loki_handler = LokiHandler(
        url="http://loki:3100/loki/api/v1/push",
        tags={"application": "geometra-ai"},
        version="1"
    )
    
    # Configure formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    loki_handler.setFormatter(formatter)
    
    # Configure loggers
    for logger in loggers.values():
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(loki_handler)
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
        """Initialize logger."""
        self.logger = logging.getLogger(name)
    
    def _log(self, level: int, msg: str, **kwargs: Any) -> None:
        """Log message with extra data."""
        extra = {
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        self.logger.log(level, msg, extra=extra)
    
    def info(self, msg: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, msg, **kwargs)
    
    def error(self, msg: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log(logging.ERROR, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, msg, **kwargs)
```

### Mätvärden

1. Skapa `monitoring/metrics/prometheus.py`:
```python
"""Prometheus metrics."""

from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List

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
    'System CPU usage',
    ['host']
)

system_memory_usage = Gauge(
    'system_memory_usage',
    'System memory usage',
    ['host']
)

system_disk_usage = Gauge(
    'system_disk_usage',
    'System disk usage',
    ['host', 'mount']
)

# AI metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['model', 'type']
)

ai_request_duration_seconds = Histogram(
    'ai_request_duration_seconds',
    'AI request duration',
    ['model', 'type']
)

ai_tokens_total = Counter(
    'ai_tokens_total',
    'Total AI tokens',
    ['model', 'type']
)

# Database metrics
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['database', 'operation']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['database', 'operation']
)
```

2. Skapa `monitoring/metrics/collectors.py`:
```python
"""Metric collectors."""

import psutil
from prometheus_client import start_http_server
from typing import Dict, List
import time

class SystemCollector:
    """System metric collector."""
    
    def collect(self) -> None:
        """Collect system metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage.labels(host=psutil.gethostname()).set(cpu_percent)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        system_memory_usage.labels(host=psutil.gethostname()).set(
            memory.percent
        )
        
        # Disk metrics
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            system_disk_usage.labels(
                host=psutil.gethostname(),
                mount=partition.mountpoint
            ).set(usage.percent)

class AICollector:
    """AI metric collector."""
    
    def collect(self) -> None:
        """Collect AI metrics."""
        # Model metrics
        for model in ['gpt-4', 'gpt-3.5-turbo']:
            for type in ['completion', 'chat']:
                ai_requests_total.labels(
                    model=model,
                    type=type
                ).inc()
                
                ai_request_duration_seconds.labels(
                    model=model,
                    type=type
                ).observe(0.5)
                
                ai_tokens_total.labels(
                    model=model,
                    type=type
                ).inc(100)

def start_metrics_server(port: int = 8000) -> None:
    """Start metrics server."""
    start_http_server(port)
    
    # Start collectors
    system_collector = SystemCollector()
    ai_collector = AICollector()
    
    while True:
        system_collector.collect()
        ai_collector.collect()
        time.sleep(15)
```

### Varningar

1. Skapa `monitoring/alerts/rules.py`:
```python
"""Alert rules."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class AlertRule:
    """Alert rule."""
    
    name: str
    condition: str
    threshold: float
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
    
    def evaluate_rules(self, metrics: Dict[str, float]) -> List[AlertRule]:
        """Evaluate alert rules."""
        triggered = []
        
        for rule in self.rules:
            if self._evaluate_condition(rule, metrics):
                triggered.append(rule)
        
        return triggered
    
    def _evaluate_condition(
        self,
        rule: AlertRule,
        metrics: Dict[str, float]
    ) -> bool:
        """Evaluate alert condition."""
        # Parse condition
        metric, operator, value = rule.condition.split()
        
        # Get metric value
        metric_value = metrics.get(metric, 0.0)
        
        # Evaluate condition
        if operator == '>':
            return metric_value > rule.threshold
        elif operator == '<':
            return metric_value < rule.threshold
        elif operator == '>=':
            return metric_value >= rule.threshold
        elif operator == '<=':
            return metric_value <= rule.threshold
        elif operator == '==':
            return metric_value == rule.threshold
        else:
            return False
```

2. Skapa `monitoring/alerts/notifications.py`:
```python
"""Alert notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from datetime import datetime

class Notification:
    """Alert notification."""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str
    ):
        """Initialize notification."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
    
    def send_alert(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> None:
        """Send alert email."""
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

class NotificationManager:
    """Notification manager."""
    
    def __init__(self, notification: Notification):
        """Initialize notification manager."""
        self.notification = notification
    
    def send_notifications(
        self,
        alerts: List[AlertRule],
        to_email: str
    ) -> None:
        """Send alert notifications."""
        if not alerts:
            return
        
        subject = f"Alert: {len(alerts)} alerts triggered"
        body = self._format_alert_body(alerts)
        
        self.notification.send_alert(to_email, subject, body)
    
    def _format_alert_body(self, alerts: List[AlertRule]) -> str:
        """Format alert body."""
        body = []
        
        for alert in alerts:
            body.append(f"Alert: {alert.name}")
            body.append(f"Severity: {alert.severity}")
            body.append(f"Description: {alert.description}")
            body.append(f"Condition: {alert.condition}")
            body.append(f"Threshold: {alert.threshold}")
            body.append(f"Duration: {alert.duration}")
            body.append("Labels:")
            for key, value in alert.labels.items():
                body.append(f"  {key}: {value}")
            body.append("")
        
        return "\n".join(body)
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

### Monitoringsproblem

1. **Loggningsproblem**
   - Kontrollera filrättigheter
   - Verifiera format
   - Validera rotation

2. **Mätvärdesproblem**
   - Kontrollera collectors
   - Verifiera metrics
   - Validera labels

3. **Varningsproblem**
   - Kontrollera regler
   - Verifiera notifieringar
   - Validera thresholds

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

1. Konfigurera [Säkerhet](33_SÄKERHET.md)
2. Skapa [Dokumentation](34_DOKUMENTATION.md)
3. Implementera [Backup](35_BACKUP.md) 