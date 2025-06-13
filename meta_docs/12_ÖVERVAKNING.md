# Övervakning

Detta dokument beskriver hur man konfigurerar och hanterar övervakning av Geometra AI-systemet.

## Översikt

Övervakningssystemet innehåller:

1. **Loggning**
   - Applikationsloggar
   - Systemloggar
   - Säkerhetsloggar

2. **Metrics**
   - Prestandametrics
   - Resursmetrics
   - Användarmetrics

3. **Alerting**
   - Varningar
   - Notifieringar
   - Eskalering

## Installation

1. Installera övervakningsverktyg:
```bash
pip install prometheus-client grafana-api python-logging-loki
```

2. Installera frontend-verktyg:
```bash
cd frontend
pnpm add @sentry/react @sentry/tracing
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
    log_dir = "logs/app"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"app_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    # Konfigurera filhanterare
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Konfigurera Loki-hanterare
    loki_handler = LokiHandler(
        url="http://loki:3100/loki/api/v1/push",
        tags={"application": "geometra"},
        version="1",
    )
    loki_handler.setLevel(logging.INFO)
    
    # Konfigurera formatering
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    loki_handler.setFormatter(formatter)
    
    # Konfigurera root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(loki_handler)
```

2. Skapa `monitoring/logging/middleware.py`:
```python
"""Logging middleware."""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for FastAPI."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response."""
        start_time = time.time()
        
        # Logga request
        logging.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host,
            }
        )
        
        # Hantera request
        response = await call_next(request)
        
        # Beräkna svarstid
        process_time = time.time() - start_time
        
        # Logga response
        logging.info(
            f"Response: {response.status_code}",
            extra={
                "status_code": response.status_code,
                "process_time": process_time,
            }
        )
        
        return response
```

### Metrics

1. Skapa `monitoring/metrics/prometheus.py`:
```python
"""Prometheus metrics configuration."""

from prometheus_client import Counter, Histogram, Gauge
from prometheus_client.openmetrics.exposition import generate_latest

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# System metrics
CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

# AI metrics
AI_REQUESTS = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['model', 'status']
)

AI_LATENCY = Histogram(
    'ai_request_duration_seconds',
    'AI request latency',
    ['model']
)
```

2. Skapa `monitoring/metrics/middleware.py`:
```python
"""Metrics middleware."""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .prometheus import REQUEST_COUNT, REQUEST_LATENCY

class MetricsMiddleware(BaseHTTPMiddleware):
    """Metrics middleware for FastAPI."""
    
    async def dispatch(self, request: Request, call_next):
        """Record metrics for request and response."""
        start_time = time.time()
        
        # Hantera request
        response = await call_next(request)
        
        # Beräkna svarstid
        process_time = time.time() - start_time
        
        # Uppdatera metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(process_time)
        
        return response
```

### Alerting

1. Skapa `monitoring/alerting/rules.py`:
```python
"""Alerting rules configuration."""

from prometheus_client import Gauge
from .prometheus import CPU_USAGE, MEMORY_USAGE, AI_LATENCY

# System alerts
CPU_ALERT = Gauge(
    'cpu_alert',
    'CPU usage alert',
    ['severity']
)

MEMORY_ALERT = Gauge(
    'memory_alert',
    'Memory usage alert',
    ['severity']
)

# AI alerts
AI_LATENCY_ALERT = Gauge(
    'ai_latency_alert',
    'AI latency alert',
    ['model', 'severity']
)

def check_alerts():
    """Check and update alerts."""
    # CPU alerts
    cpu_usage = CPU_USAGE.get()
    if cpu_usage > 90:
        CPU_ALERT.labels(severity='critical').set(1)
    elif cpu_usage > 70:
        CPU_ALERT.labels(severity='warning').set(1)
    else:
        CPU_ALERT.labels(severity='critical').set(0)
        CPU_ALERT.labels(severity='warning').set(0)
    
    # Memory alerts
    memory_usage = MEMORY_USAGE.get()
    if memory_usage > 90:
        MEMORY_ALERT.labels(severity='critical').set(1)
    elif memory_usage > 70:
        MEMORY_ALERT.labels(severity='warning').set(1)
    else:
        MEMORY_ALERT.labels(severity='critical').set(0)
        MEMORY_ALERT.labels(severity='warning').set(0)
    
    # AI latency alerts
    for model in ['gpt-4', 'gpt-3.5']:
        latency = AI_LATENCY.labels(model=model).get()
        if latency > 5:
            AI_LATENCY_ALERT.labels(
                model=model,
                severity='critical'
            ).set(1)
        elif latency > 2:
            AI_LATENCY_ALERT.labels(
                model=model,
                severity='warning'
            ).set(1)
        else:
            AI_LATENCY_ALERT.labels(
                model=model,
                severity='critical'
            ).set(0)
            AI_LATENCY_ALERT.labels(
                model=model,
                severity='warning'
            ).set(0)
```

2. Skapa `monitoring/alerting/notifications.py`:
```python
"""Alert notifications configuration."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_alert_email(alert_type, severity, message):
    """Send alert email."""
    # Skapa email
    msg = MIMEMultipart()
    msg['From'] = 'alerts@geometra.ai'
    msg['To'] = 'admin@geometra.ai'
    msg['Subject'] = f'Alert: {alert_type} - {severity}'
    
    # Lägg till meddelande
    msg.attach(MIMEText(message, 'plain'))
    
    # Skicka email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('alerts@geometra.ai', 'password')
        server.send_message(msg)
```

## Validering

1. Starta övervakning:
```bash
docker-compose up -d prometheus grafana loki
```

2. Verifiera metrics:
```bash
curl http://localhost:9090/metrics
```

3. Verifiera loggar:
```bash
curl http://localhost:3100/loki/api/v1/query
```

## Felsökning

### Övervakningsproblem

1. **Loggningsproblem**
   - Kontrollera loggfiler
   - Verifiera Loki
   - Validera formatering

2. **Metrics-problem**
   - Kontrollera Prometheus
   - Verifiera exporters
   - Validera queries

3. **Alerting-problem**
   - Kontrollera regler
   - Verifiera notifieringar
   - Validera eskaleringskedja

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

1. Skapa [Arkitekturdiagram](13_ARKITEKTUR.md)
2. Implementera [CI/CD](14_CI_CD.md)
3. Konfigurera [Säkerhet](15_SÄKERHET.md) 