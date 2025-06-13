# Övervakning och Loggning Implementation

## 1. Implementera Backend-loggning

### src/api/utils/logging.py
```python
"""Logging utilities."""
import structlog
import logging
import sys
from typing import Any, Dict
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Konfigurera structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class RequestLogger(BaseHTTPMiddleware):
    """Middleware för att logga HTTP requests."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Logga request och response."""
        start_time = time.time()
        
        # Logga request
        request_id = request.headers.get("X-Request-ID", "unknown")
        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host,
            user_agent=request.headers.get("user-agent"),
        )
        
        try:
            response = await call_next(request)
            
            # Logga response
            process_time = time.time() - start_time
            logger.info(
                "request_completed",
                request_id=request_id,
                status_code=response.status_code,
                process_time=process_time,
            )
            
            return response
        except Exception as e:
            # Logga fel
            logger.error(
                "request_failed",
                request_id=request_id,
                error=str(e),
                exc_info=True,
            )
            raise

class AILogger:
    """Logger för AI-interaktioner."""
    
    @staticmethod
    def log_chat_interaction(
        user_id: str,
        message: str,
        response: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Logga chat-interaktion."""
        logger.info(
            "chat_interaction",
            user_id=user_id,
            message=message,
            response=response,
            **metadata
        )
    
    @staticmethod
    def log_memory_operation(
        user_id: str,
        operation: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Logga minnesoperation."""
        logger.info(
            "memory_operation",
            user_id=user_id,
            operation=operation,
            content=content,
            **metadata
        )
```

## 2. Implementera Frontend-loggning

### src/frontend/utils/logging.ts
```typescript
/** Frontend logging utilities */
import winston from 'winston';

// Konfigurera logger
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      ),
    }),
    ...(process.env.NODE_ENV === 'production'
      ? [
          new winston.transports.Http({
            host: 'localhost',
            port: 8000,
            path: '/api/logs',
          }),
        ]
      : []),
  ],
});

// Loggning av fel
export const logError = (error: Error, context?: Record<string, any>) => {
  logger.error({
    message: error.message,
    stack: error.stack,
    ...context,
  });
};

// Loggning av info
export const logInfo = (message: string, context?: Record<string, any>) => {
  logger.info({
    message,
    ...context,
  });
};

// Loggning av varningar
export const logWarning = (message: string, context?: Record<string, any>) => {
  logger.warn({
    message,
    ...context,
  });
};

// Loggning av debug
export const logDebug = (message: string, context?: Record<string, any>) => {
  logger.debug({
    message,
    ...context,
  });
};
```

## 3. Implementera Prometheus Metrics

### src/api/utils/metrics.py
```python
"""Prometheus metrics."""
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

# AI metrics
ai_requests_total = Counter(
    "ai_requests_total",
    "Total number of AI requests",
    ["type", "status"]
)

ai_request_duration_seconds = Histogram(
    "ai_request_duration_seconds",
    "AI request duration in seconds",
    ["type"]
)

# Memory metrics
memory_operations_total = Counter(
    "memory_operations_total",
    "Total number of memory operations",
    ["operation", "status"]
)

memory_size_bytes = Gauge(
    "memory_size_bytes",
    "Total size of memory in bytes"
)

# User metrics
active_users = Gauge(
    "active_users",
    "Number of active users"
)

def setup_metrics(app):
    """Setup Prometheus metrics."""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="fastapi_inprogress",
        inprogress_labels=True,
    )

    instrumentator.add(metrics.default())
    instrumentator.add(metrics.latency())
    instrumentator.add(metrics.requests())
    instrumentator.add(metrics.exceptions())
    instrumentator.add(metrics.runtime())

    instrumentator.instrument(app).expose(app)
```

## 4. Implementera Grafana Dashboard

### monitoring/grafana/dashboards/geometra.json
```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "panels": [
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {}
        },
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 2,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.2.0",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "rate(http_requests_total[5m])",
          "interval": "",
          "legendFormat": "{{method}} {{endpoint}}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Request Rate",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "custom": {}
        },
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 3,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.2.0",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "rate(ai_requests_total[5m])",
          "interval": "",
          "legendFormat": "{{type}}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "AI Request Rate",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "refresh": "5s",
  "schemaVersion": 26,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Geometra AI Dashboard",
  "uid": "geometra",
  "version": 1
}
```

## 5. Implementera Alerting

### monitoring/alertmanager/config.yml
```yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-notifications'
  routes:
    - match:
        severity: critical
      receiver: 'slack-critical'
      continue: true

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts'
        send_resolved: true
        title: '{{ template "slack.default.title" . }}'
        text: '{{ template "slack.default.text" . }}'
        actions:
          - type: button
            text: 'View Dashboard'
            url: '{{ .CommonAnnotations.dashboard }}'

  - name: 'slack-critical'
    slack_configs:
      - channel: '#critical-alerts'
        send_resolved: true
        title: '{{ template "slack.default.title" . }}'
        text: '{{ template "slack.default.text" . }}'
        actions:
          - type: button
            text: 'View Dashboard'
            url: '{{ .CommonAnnotations.dashboard }}'
```

### monitoring/prometheus/rules.yml
```yaml
groups:
  - name: geometra
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
          description: Error rate is above 5% for the last 5 minutes

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High latency detected
          description: 95th percentile latency is above 2 seconds

      - alert: AIRequestFailures
        expr: rate(ai_requests_total{status="error"}[5m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: AI request failures detected
          description: AI requests are failing

      - alert: MemoryOperationFailures
        expr: rate(memory_operations_total{status="error"}[5m]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: Memory operation failures detected
          description: Memory operations are failing
```

## 6. Uppdatera Docker Compose

### docker-compose.monitoring.yml
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    ports:
      - "9090:9090"
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager
    command:
      - '--config.file=/etc/alertmanager/config.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./monitoring/grafana:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3000:3000"
    restart: unless-stopped

volumes:
  prometheus_data:
```

## 7. Verifiera Implementation

```bash
# Starta övervakningsstacken
docker-compose -f docker-compose.monitoring.yml up -d

# Verifiera Prometheus
curl http://localhost:9090/-/healthy

# Verifiera Grafana
curl http://localhost:3000/api/health

# Verifiera Alertmanager
curl http://localhost:9093/-/healthy
```

## 8. Nästa steg

Efter att ha implementerat övervakning och loggning, kör:

```bash
# Konfigurera Slack-integration
# Uppdatera monitoring/alertmanager/config.yml med din Slack webhook URL

# Starta hela stacken
docker-compose up -d

# Verifiera loggning
curl http://localhost:8000/api/health
# Kontrollera loggarna i Grafana
```

Detta implementerar:
- Strukturerad loggning med structlog
- Frontend-loggning med winston
- Prometheus metrics
- Grafana dashboards
- Alertmanager för notifieringar
- Slack-integration
- Docker Compose för övervakning
- Hälsokontroller

Nästa steg är att implementera säkerhet och autentisering. 