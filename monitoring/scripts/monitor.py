"""System monitoring script for Geometra AI."""

import requests
import time
import psutil
import logging
import os
import yaml
from datetime import datetime
from typing import Dict, List, Any
import json
from pathlib import Path

class SystemMonitor:
    """Handles system monitoring and health checks."""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.logger = logging.getLogger('SystemMonitor')
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Load monitoring configuration."""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../config/monitoring_config.yml'
            )
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default monitoring configuration."""
        return {
            'endpoints': [
                {'name': 'api', 'url': 'http://localhost:8000/api/v1/health'},
                {'name': 'memory', 'url': 'http://localhost:8000/api/v1/memory/status'}
            ],
            'chroma_url': 'http://localhost:8000/api/v1/memory/chroma',
            'redis_url': 'http://localhost:8000/api/v1/memory/redis',
            'monitoring_interval': 300,  # 5 minutes
            'log_file': 'monitoring/logs/monitor.log',
            'alert_rules': {
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
        }
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_file = self.config.get('log_file', 'monitoring/logs/monitor.log')
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def check_endpoints(self) -> Dict[str, Any]:
        """Check health of configured endpoints."""
        results = {}
        for endpoint in self.config['endpoints']:
            try:
                start_time = time.time()
                response = requests.get(endpoint['url'], timeout=5)
                response_time = time.time() - start_time
                
                results[endpoint['name']] = {
                    'status': response.status_code == 200,
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Check for alerts
                self._check_alerts(endpoint['name'], results[endpoint['name']])
                
            except Exception as e:
                results[endpoint['name']] = {
                    'status': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.logger.error(f"Error checking endpoint {endpoint['name']}: {e}")
        
        return results
    
    def check_memory(self) -> Dict[str, Any]:
        """Check memory usage of various components."""
        return {
            'chroma': self._check_chroma_memory(),
            'redis': self._check_redis_memory(),
            'system': self._check_system_memory()
        }
    
    def _check_chroma_memory(self) -> Dict[str, Any]:
        """Check ChromaDB memory usage."""
        try:
            response = requests.get(
                f"{self.config['chroma_url']}/memory",
                timeout=5
            )
            return response.json()
        except Exception as e:
            self.logger.error(f"Error checking ChromaDB memory: {e}")
            return {'error': str(e)}
    
    def _check_redis_memory(self) -> Dict[str, Any]:
        """Check Redis memory usage."""
        try:
            response = requests.get(
                f"{self.config['redis_url']}/memory",
                timeout=5
            )
            return response.json()
        except Exception as e:
            self.logger.error(f"Error checking Redis memory: {e}")
            return {'error': str(e)}
    
    def _check_system_memory(self) -> Dict[str, Any]:
        """Check system memory usage."""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent
        }
    
    def _check_alerts(self, component: str, data: Dict[str, Any]):
        """Check if any alert conditions are met."""
        for rule_name, rule in self.config['alert_rules'].items():
            try:
                if rule['condition'](data):
                    message = rule['message'].format(**data)
                    self.logger.warning(
                        f"Alert: {rule_name} - {message} "
                        f"(Severity: {rule['severity']})"
                    )
            except Exception as e:
                self.logger.error(f"Error checking alert rule {rule_name}: {e}")
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to a JSON file."""
        metrics_file = os.path.join(
            os.path.dirname(__file__),
            '../logs/metrics.json'
        )
        
        try:
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")

def main():
    """Main monitoring loop."""
    monitor = SystemMonitor()
    
    while True:
        try:
            # Collect metrics
            endpoint_status = monitor.check_endpoints()
            memory_status = monitor.check_memory()
            
            # Combine metrics
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'endpoints': endpoint_status,
                'memory': memory_status
            }
            
            # Save metrics
            monitor.save_metrics(metrics)
            
            # Log status
            monitor.logger.info(f"Metrics collected: {json.dumps(metrics, indent=2)}")
            
            # Wait for next interval
            time.sleep(monitor.config['monitoring_interval'])
            
        except KeyboardInterrupt:
            monitor.logger.info("Monitoring stopped by user")
            break
        except Exception as e:
            monitor.logger.error(f"Error in monitoring loop: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main() 