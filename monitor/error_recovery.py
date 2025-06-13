#!/usr/bin/env python3
"""
Error Recovery Module for Geometra AI

This module provides automatic error recovery for:
- API failures
- Memory system issues
- OpenAI connectivity problems
- System resource exhaustion

Usage:
    python error_recovery.py --watch  # Continuous monitoring
    python error_recovery.py --recover # Attempt recovery
    python error_recovery.py --status  # Show recovery status
"""

import os
import sys
import time
import json
import logging
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import requests
import redis
import chromadb
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/recovery.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('error_recovery')

class ErrorRecovery:
    def __init__(self):
        """Initialize error recovery with configuration from environment."""
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
        
        # Recovery thresholds
        self.thresholds = {
            'max_retries': 3,
            'retry_delay': 5,  # seconds
            'recovery_timeout': 300  # 5 minutes
        }
        
        # Recovery state
        self.recovery_state = {
            'last_recovery': None,
            'recovery_count': 0,
            'current_issues': []
        }

    def check_api_health(self) -> Dict:
        """Check API health and attempt recovery if needed."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                return {'status': 'healthy'}
            
            # API is unhealthy, attempt recovery
            return self._recover_api()
        except Exception as e:
            logger.error(f"API health check failed: {str(e)}")
            return self._recover_api()

    def _recover_api(self) -> Dict:
        """Attempt to recover API service."""
        try:
            # Check if API is running
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=api'],
                capture_output=True,
                text=True
            )
            
            if 'api' not in result.stdout:
                # API container is down, restart it
                subprocess.run(['docker-compose', 'restart', 'api'])
                time.sleep(self.thresholds['retry_delay'])
                
                # Verify recovery
                response = requests.get(f"{self.api_url}/health", timeout=5)
                if response.status_code == 200:
                    return {'status': 'recovered', 'action': 'restarted_api'}
            
            return {'status': 'unhealthy', 'error': 'API recovery failed'}
        except Exception as e:
            logger.error(f"API recovery failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def check_memory_health(self) -> Dict:
        """Check memory systems and attempt recovery if needed."""
        try:
            # Check Redis
            redis_healthy = self.redis_client.ping()
            if not redis_healthy:
                return self._recover_redis()
            
            # Check ChromaDB
            chroma_healthy = self.chroma_client.heartbeat()
            if not chroma_healthy:
                return self._recover_chroma()
            
            return {'status': 'healthy'}
        except Exception as e:
            logger.error(f"Memory health check failed: {str(e)}")
            return self._recover_memory()

    def _recover_redis(self) -> Dict:
        """Attempt to recover Redis."""
        try:
            # Restart Redis container
            subprocess.run(['docker-compose', 'restart', 'redis'])
            time.sleep(self.thresholds['retry_delay'])
            
            # Verify recovery
            if self.redis_client.ping():
                return {'status': 'recovered', 'action': 'restarted_redis'}
            
            return {'status': 'unhealthy', 'error': 'Redis recovery failed'}
        except Exception as e:
            logger.error(f"Redis recovery failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def _recover_chroma(self) -> Dict:
        """Attempt to recover ChromaDB."""
        try:
            # Restart ChromaDB container
            subprocess.run(['docker-compose', 'restart', 'chroma'])
            time.sleep(self.thresholds['retry_delay'])
            
            # Verify recovery
            if self.chroma_client.heartbeat():
                return {'status': 'recovered', 'action': 'restarted_chroma'}
            
            return {'status': 'unhealthy', 'error': 'ChromaDB recovery failed'}
        except Exception as e:
            logger.error(f"ChromaDB recovery failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def _recover_memory(self) -> Dict:
        """Attempt to recover both memory systems."""
        redis_result = self._recover_redis()
        chroma_result = self._recover_chroma()
        
        if redis_result['status'] == 'recovered' and chroma_result['status'] == 'recovered':
            return {'status': 'recovered', 'action': 'restarted_memory_systems'}
        
        return {
            'status': 'unhealthy',
            'redis': redis_result,
            'chroma': chroma_result
        }

    def check_openai_health(self) -> Dict:
        """Check OpenAI connectivity and attempt recovery if needed."""
        try:
            self.openai_client.models.list()
            return {'status': 'healthy'}
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return self._recover_openai()

    def _recover_openai(self) -> Dict:
        """Attempt to recover OpenAI connectivity."""
        try:
            # Check API key
            if not self.openai_api_key:
                return {'status': 'error', 'error': 'Missing OpenAI API key'}
            
            # Test with a simple request
            self.openai_client.models.list()
            return {'status': 'recovered', 'action': 'verified_api_key'}
        except Exception as e:
            logger.error(f"OpenAI recovery failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def run_recovery(self) -> Dict:
        """Run full system recovery."""
        start_time = time.time()
        issues = []
        
        # Check and recover API
        api_status = self.check_api_health()
        if api_status['status'] != 'healthy':
            issues.append(('api', api_status))
        
        # Check and recover memory
        memory_status = self.check_memory_health()
        if memory_status['status'] != 'healthy':
            issues.append(('memory', memory_status))
        
        # Check and recover OpenAI
        openai_status = self.check_openai_health()
        if openai_status['status'] != 'healthy':
            issues.append(('openai', openai_status))
        
        # Update recovery state
        self.recovery_state['last_recovery'] = datetime.now().isoformat()
        self.recovery_state['recovery_count'] += 1
        self.recovery_state['current_issues'] = issues
        
        return {
            'status': 'recovered' if not issues else 'unhealthy',
            'duration': time.time() - start_time,
            'issues': issues
        }

    def get_recovery_status(self) -> Dict:
        """Get current recovery status."""
        return {
            'last_recovery': self.recovery_state['last_recovery'],
            'recovery_count': self.recovery_state['recovery_count'],
            'current_issues': self.recovery_state['current_issues']
        }

    def generate_report(self) -> str:
        """Generate a human-readable recovery report."""
        status = self.get_recovery_status()
        
        report = [
            "=== Error Recovery Report ===",
            f"Time: {datetime.now().isoformat()}",
            f"\nLast Recovery: {status['last_recovery'] or 'Never'}",
            f"Recovery Count: {status['recovery_count']}",
            "\nCurrent Issues:"
        ]
        
        if status['current_issues']:
            for component, issue in status['current_issues']:
                report.append(f"  {component}: {issue['status']}")
                if 'error' in issue:
                    report.append(f"    Error: {issue['error']}")
        else:
            report.append("  No current issues")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='Geometra AI Error Recovery')
    parser.add_argument('--watch', action='store_true', help='Continuous monitoring')
    parser.add_argument('--recover', action='store_true', help='Attempt recovery')
    parser.add_argument('--status', action='store_true', help='Show recovery status')
    args = parser.parse_args()

    recovery = ErrorRecovery()

    if args.watch:
        logger.info("Starting continuous monitoring...")
        while True:
            report = recovery.generate_report()
            print("\033[2J\033[H")  # Clear screen
            print(report)
            time.sleep(60)  # Check every minute
    elif args.recover:
        result = recovery.run_recovery()
        print(json.dumps(result, indent=2))
    elif args.status:
        status = recovery.get_recovery_status()
        print(json.dumps(status, indent=2))
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 