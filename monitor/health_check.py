#!/usr/bin/env python3
"""
Health Check Module for Geometra AI

This module provides comprehensive health monitoring for:
- API endpoints
- Memory systems (ChromaDB + Redis)
- OpenAI connectivity
- System resources

Usage:
    python health_check.py --watch  # Continuous monitoring
    python health_check.py --check  # Single check
    python health_check.py --report # Generate report
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import requests
import redis
import chromadb
from openai import OpenAI
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('health_check')

class HealthCheck:
    def __init__(self):
        """Initialize health check with configuration from environment."""
        self.api_url = os.getenv('API_URL', 'http://localhost:8000')
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.chroma_host = os.getenv('CHROMA_HOST', 'localhost')
        self.chroma_port = int(os.getenv('CHROMA_PORT', '8001'))
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize clients
        self.redis_client = redis.from_url(self.redis_url)
        self.chroma_client = chromadb.HttpClient(
            host=self.chroma_host,
            port=self.chroma_port
        )
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Health thresholds
        self.thresholds = {
            'cpu_percent': 80,
            'memory_percent': 80,
            'disk_percent': 80,
            'api_timeout': 5,
            'memory_timeout': 3
        }

    def check_api(self) -> Dict:
        """Check API health."""
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=self.thresholds['api_timeout'])
            latency = time.time() - start_time
            
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'latency': latency,
                'code': response.status_code
            }
        except Exception as e:
            logger.error(f"API check failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def check_memory(self) -> Dict:
        """Check memory systems (Redis + ChromaDB)."""
        results = {
            'redis': self._check_redis(),
            'chroma': self._check_chroma()
        }
        
        return {
            'status': 'healthy' if all(r['status'] == 'healthy' for r in results.values()) else 'unhealthy',
            'components': results
        }

    def _check_redis(self) -> Dict:
        """Check Redis connection and basic operations."""
        try:
            start_time = time.time()
            self.redis_client.ping()
            latency = time.time() - start_time
            
            return {
                'status': 'healthy',
                'latency': latency
            }
        except Exception as e:
            logger.error(f"Redis check failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def _check_chroma(self) -> Dict:
        """Check ChromaDB connection and basic operations."""
        try:
            start_time = time.time()
            self.chroma_client.heartbeat()
            latency = time.time() - start_time
            
            return {
                'status': 'healthy',
                'latency': latency
            }
        except Exception as e:
            logger.error(f"ChromaDB check failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def check_openai(self) -> Dict:
        """Check OpenAI API connectivity."""
        try:
            start_time = time.time()
            self.openai_client.models.list()
            latency = time.time() - start_time
            
            return {
                'status': 'healthy',
                'latency': latency
            }
        except Exception as e:
            logger.error(f"OpenAI check failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def check_system(self) -> Dict:
        """Check system resources."""
        return {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }

    def run_check(self) -> Dict:
        """Run all health checks."""
        return {
            'timestamp': datetime.now().isoformat(),
            'api': self.check_api(),
            'memory': self.check_memory(),
            'openai': self.check_openai(),
            'system': self.check_system()
        }

    def generate_report(self) -> str:
        """Generate a human-readable health report."""
        check_results = self.run_check()
        
        report = [
            "=== Health Check Report ===",
            f"Time: {check_results['timestamp']}",
            "\nAPI Status:",
            f"  Status: {check_results['api']['status']}",
            f"  Latency: {check_results['api'].get('latency', 'N/A'):.2f}s",
            "\nMemory Status:",
            f"  Redis: {check_results['memory']['components']['redis']['status']}",
            f"  ChromaDB: {check_results['memory']['components']['chroma']['status']}",
            "\nOpenAI Status:",
            f"  Status: {check_results['openai']['status']}",
            f"  Latency: {check_results['openai'].get('latency', 'N/A'):.2f}s",
            "\nSystem Resources:",
            f"  CPU: {check_results['system']['cpu']}%",
            f"  Memory: {check_results['system']['memory']}%",
            f"  Disk: {check_results['system']['disk']}%"
        ]
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='Geometra AI Health Check')
    parser.add_argument('--watch', action='store_true', help='Continuous monitoring')
    parser.add_argument('--check', action='store_true', help='Single health check')
    parser.add_argument('--report', action='store_true', help='Generate report')
    args = parser.parse_args()

    health_check = HealthCheck()

    if args.watch:
        logger.info("Starting continuous monitoring...")
        while True:
            report = health_check.generate_report()
            print("\033[2J\033[H")  # Clear screen
            print(report)
            time.sleep(60)  # Check every minute
    elif args.check:
        results = health_check.run_check()
        print(json.dumps(results, indent=2))
    elif args.report:
        print(health_check.generate_report())
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 