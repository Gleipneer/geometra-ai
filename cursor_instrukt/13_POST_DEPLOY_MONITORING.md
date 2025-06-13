# 📊 13: Post-Deployment Monitoring

## 🎯 Syfte
Övervaka och optimera systemet i produktion med fokus på:
- Endpoint tillgänglighet
- Minnesanvändning
- Loggning och rotation
- Externa övervakningstjänster

## 📦 Komponenter

### 1. Endpoint Monitoring
- Ping-kontroller
- Response time tracking
- Error rate monitoring
- Uptime tracking

### 2. Minnesövervakning
- ChromaDB användning
- Redis memory usage
- Cache hit/miss rates
- Memory leaks detection

### 3. Loggning
- Log rotation
- Error aggregation
- Performance metrics
- Security events

### 4. Externa Tjänster
- Railway status
- OpenAI API status
- External health checks
- SSL certificate monitoring

## 🛠️ Installation

1. **Skapa Monitoring-struktur**
```bash
mkdir -p monitoring/{scripts,config,logs}
```

2. **Implementera Monitoring Script**
```python
# monitoring/scripts/monitor.py
import requests
import time
import psutil
import logging
from datetime import datetime
from typing import Dict, List

class SystemMonitor:
    def __init__(self, config: Dict):
        self.config = config
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            filename='monitoring/logs/monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def check_endpoints(self) -> Dict:
        results = {}
        for endpoint in self.config['endpoints']:
            try:
                start_time = time.time()
                response = requests.get(endpoint['url'])
                response_time = time.time() - start_time
                
                results[endpoint['name']] = {
                    'status': response.status_code == 200,
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                results[endpoint['name']] = {
                    'status': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        return results
    
    def check_memory(self) -> Dict:
        return {
            'chroma': self._check_chroma_memory(),
            'redis': self._check_redis_memory(),
            'system': self._check_system_memory()
        }
    
    def _check_chroma_memory(self) -> Dict:
        try:
            response = requests.get(f"{self.config['chroma_url']}/memory")
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def _check_redis_memory(self) -> Dict:
        try:
            response = requests.get(f"{self.config['redis_url']}/memory")
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def _check_system_memory(self) -> Dict:
        return {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        }

def main():
    config = {
        'endpoints': [
            {'name': 'api', 'url': 'https://api.geometra.ai/health'},
            {'name': 'memory', 'url': 'https://api.geometra.ai/memory/status'}
        ],
        'chroma_url': 'https://api.geometra.ai/memory/chroma',
        'redis_url': 'https://api.geometra.ai/memory/redis'
    }
    
    monitor = SystemMonitor(config)
    
    # Kör kontroller
    endpoint_status = monitor.check_endpoints()
    memory_status = monitor.check_memory()
    
    # Logga resultat
    logging.info(f"Endpoint Status: {endpoint_status}")
    logging.info(f"Memory Status: {memory_status}")

if __name__ == "__main__":
    main()
```

3. **Skapa Log Rotation Config**
```bash
# monitoring/config/logrotate.conf
/var/log/geometra/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        /usr/bin/systemctl reload geometra
    endscript
}
```

4. **Skapa External Monitoring**
```yaml
# monitoring/config/external_monitors.yml
monitors:
  - name: api_health
    type: http
    url: https://api.geometra.ai/health
    interval: 60
    timeout: 5
    expected_status: 200
    
  - name: memory_status
    type: http
    url: https://api.geometra.ai/memory/status
    interval: 300
    timeout: 10
    expected_status: 200
    
  - name: ssl_cert
    type: ssl
    host: api.geometra.ai
    port: 443
    interval: 3600
    warning_days: 30
```

## 🔧 Konfiguration

1. **Skapa Monitoring Miljövariabler**
```bash
# .env
MONITORING_INTERVAL=300
ALERT_EMAIL=alerts@geometra.ai
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

2. **Konfigurera Alerts**
```python
# monitoring/config/alerts.py
ALERT_RULES = {
    'endpoint_down': {
        'condition': lambda x: not x['status'],
        'message': 'Endpoint {name} is down',
        'severity': 'high'
    },
    'high_memory': {
        'condition': lambda x: x['percent'] > 90,
        'message': 'Memory usage is {percent}%',
        'severity': 'medium'
    },
    'slow_response': {
        'condition': lambda x: x['response_time'] > 2,
        'message': 'Response time is {response_time}s',
        'severity': 'low'
    }
}
```

## ✅ Validering

Kör följande för att verifiera monitoring:

```bash
# Starta monitoring
python monitoring/scripts/monitor.py

# Kontrollera loggar
tail -f monitoring/logs/monitor.log

# Verifiera log rotation
logrotate -d monitoring/config/logrotate.conf
```

## 🔍 Felsökning

### Vanliga problem

1. **Monitoring misslyckas**
```bash
# Kontrollera loggar
cat monitoring/logs/monitor.log

# Verifiera konfiguration
python monitoring/scripts/monitor.py --validate
```

2. **Log rotation fungerar inte**
```bash
# Testa log rotation
logrotate -f monitoring/config/logrotate.conf

# Kontrollera behörigheter
ls -l /var/log/geometra/
```

3. **Alerts fungerar inte**
```bash
# Testa alert
python monitoring/scripts/test_alert.py

# Kontrollera webhook
curl -X POST $SLACK_WEBHOOK_URL -d '{"text":"Test alert"}'
```

## 📝 Loggning

```bash
echo "$(date) - 13_POST_DEPLOY_MONITORING: Monitoring konfigurerad" >> bootstrap_status.log
``` 