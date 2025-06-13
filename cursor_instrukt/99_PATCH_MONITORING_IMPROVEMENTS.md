# Loggning och monitoring

## 1. Förbättra loggning
```python
# src/logging/advanced.py
import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
            
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
            
        return json.dumps(log_data)

def setup_advanced_logging():
    """Setup advanced logging configuration."""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler with JSON formatting
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.json",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.json",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)
```

## 2. Implementera avancerade mätvärden
```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

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

# AI metrics
AI_REQUESTS = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['type', 'model']
)

AI_LATENCY = Histogram(
    'ai_request_duration_seconds',
    'AI request latency',
    ['type', 'model']
)

# System metrics
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

# Custom metrics
ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

ERROR_RATE = Counter(
    'error_rate_total',
    'Total number of errors',
    ['type']
)
```

## 3. Implementera varningssystem
```python
# src/monitoring/alerts.py
import smtplib
from email.mime.text import MIMEText
from src.logging.advanced import setup_advanced_logging

logger = setup_advanced_logging()

class AlertManager:
    def __init__(self):
        self.thresholds = {
            'error_rate': 0.1,  # 10% error rate
            'latency': 1.0,     # 1 second
            'memory': 0.9,      # 90% memory usage
            'cpu': 0.8         # 80% CPU usage
        }
    
    def check_metrics(self, metrics):
        """Check metrics against thresholds."""
        alerts = []
        
        if metrics['error_rate'] > self.thresholds['error_rate']:
            alerts.append({
                'type': 'error_rate',
                'value': metrics['error_rate'],
                'threshold': self.thresholds['error_rate']
            })
            
        if metrics['latency'] > self.thresholds['latency']:
            alerts.append({
                'type': 'latency',
                'value': metrics['latency'],
                'threshold': self.thresholds['latency']
            })
            
        if metrics['memory'] > self.thresholds['memory']:
            alerts.append({
                'type': 'memory',
                'value': metrics['memory'],
                'threshold': self.thresholds['memory']
            })
            
        if metrics['cpu'] > self.thresholds['cpu']:
            alerts.append({
                'type': 'cpu',
                'value': metrics['cpu'],
                'threshold': self.thresholds['cpu']
            })
            
        return alerts
    
    def send_alert(self, alert):
        """Send alert notification."""
        try:
            # Log alert
            logger.error(f"Alert triggered: {alert}")
            
            # Send email
            msg = MIMEText(f"Alert: {alert['type']} exceeded threshold")
            msg['Subject'] = f"Alert: {alert['type']}"
            msg['From'] = "alerts@geometra.ai"
            msg['To'] = "admin@geometra.ai"
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login("alerts@geometra.ai", "password")
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
```

## 4. Implementera health checks
```python
# src/monitoring/health.py
from fastapi import APIRouter
from src.monitoring.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    MEMORY_USAGE,
    CPU_USAGE
)
import psutil

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    # Get system metrics
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent()
    
    # Update metrics
    MEMORY_USAGE.set(memory.used)
    CPU_USAGE.set(cpu)
    
    # Check health
    health = {
        "status": "healthy",
        "memory_usage": memory.percent,
        "cpu_usage": cpu,
        "request_count": REQUEST_COUNT._value.get(),
        "request_latency": REQUEST_LATENCY._sum.get()
    }
    
    # Check thresholds
    if memory.percent > 90 or cpu > 80:
        health["status"] = "degraded"
        
    return health
```

## 5. Kör testerna
```bash
# Kör alla monitoring-tester
pytest tests/unit/monitoring tests/integration/monitoring -v
``` 