#!/usr/bin/env python3
"""
Log parser for Geometra AI system.

Analyzes system logs for important events and patterns:
- Rate limit hits
- Timeouts
- ChromaDB misses
- Error patterns
- Performance issues
"""

import os
import re
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Pattern
import logging
from logging.handlers import RotatingFileHandler
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        RotatingFileHandler('logs/log_parser.log', maxBytes=1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

@dataclass
class LogEvent:
    """Log event data class."""
    timestamp: str
    level: str
    component: str
    message: str
    pattern: str
    context: Dict[str, Any]

class LogParser:
    """Log parser implementation."""
    
    def __init__(self, log_dir: str = 'logs'):
        """Initialize log parser.
        
        Args:
            log_dir: Directory containing log files
        """
        self.log_dir = Path(log_dir)
        self.patterns: Dict[str, Pattern] = {
            'rate_limit': re.compile(r'rate limit.*exceeded|rate limit.*hit'),
            'timeout': re.compile(r'timeout|timed out|took too long'),
            'chroma_miss': re.compile(r'chroma.*miss|chroma.*not found'),
            'error': re.compile(r'error|exception|failed'),
            'performance': re.compile(r'slow|performance|latency')
        }
        self.events: List[LogEvent] = []
    
    def parse_logs(self, hours: int = 24):
        """Parse log files from the last N hours.
        
        Args:
            hours: Number of hours to look back
        """
        start_time = datetime.now() - timedelta(hours=hours)
        
        for log_file in self.log_dir.glob('*.log'):
            if log_file.name == 'log_parser.log':
                continue
            
            logging.info(f"Parsing log file: {log_file}")
            self._parse_file(log_file, start_time)
    
    def _parse_file(self, log_file: Path, start_time: datetime):
        """Parse a single log file.
        
        Args:
            log_file: Path to log file
            start_time: Start time for parsing
        """
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    # Parse timestamp
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if not timestamp_match:
                        continue
                    
                    timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                    if timestamp < start_time:
                        continue
                    
                    # Parse log level
                    level_match = re.search(r'\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]', line)
                    level = level_match.group(1) if level_match else 'INFO'
                    
                    # Parse component
                    component_match = re.search(r'\[([^\]]+)\]', line)
                    component = component_match.group(1) if component_match else 'unknown'
                    
                    # Check for patterns
                    for pattern_name, pattern in self.patterns.items():
                        if pattern.search(line.lower()):
                            event = LogEvent(
                                timestamp=timestamp.isoformat(),
                                level=level,
                                component=component,
                                message=line.strip(),
                                pattern=pattern_name,
                                context=self._extract_context(line)
                            )
                            self.events.append(event)
        except Exception as e:
            logging.error(f"Error parsing {log_file}: {e}")
    
    def _extract_context(self, line: str) -> Dict[str, Any]:
        """Extract context from log line.
        
        Args:
            line: Log line
            
        Returns:
            Dict containing extracted context
        """
        context = {}
        
        # Extract user ID if present
        user_match = re.search(r'user[_-]?id[=:]\s*([^\s,]+)', line.lower())
        if user_match:
            context['user_id'] = user_match.group(1)
        
        # Extract request ID if present
        request_match = re.search(r'request[_-]?id[=:]\s*([^\s,]+)', line.lower())
        if request_match:
            context['request_id'] = request_match.group(1)
        
        # Extract duration if present
        duration_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ms|s|seconds?)', line.lower())
        if duration_match:
            context['duration'] = float(duration_match.group(1))
        
        # Extract error code if present
        error_match = re.search(r'error[_-]?code[=:]\s*(\d+)', line.lower())
        if error_match:
            context['error_code'] = int(error_match.group(1))
        
        return context
    
    def generate_report(self):
        """Generate log analysis report."""
        if not self.events:
            logging.info("No events found in logs")
            return
        
        # Group events by pattern
        pattern_groups: Dict[str, List[LogEvent]] = {}
        for event in self.events:
            if event.pattern not in pattern_groups:
                pattern_groups[event.pattern] = []
            pattern_groups[event.pattern].append(event)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_events': len(self.events),
            'patterns': {
                pattern: {
                    'count': len(events),
                    'components': {
                        component: len([e for e in events if e.component == component])
                        for component in set(e.component for e in events)
                    },
                    'levels': {
                        level: len([e for e in events if e.level == level])
                        for level in set(e.level for e in events)
                    },
                    'recent_events': [
                        {
                            'timestamp': e.timestamp,
                            'level': e.level,
                            'component': e.component,
                            'message': e.message,
                            'context': e.context
                        }
                        for e in sorted(events, key=lambda x: x.timestamp, reverse=True)[:5]
                    ]
                }
                for pattern, events in pattern_groups.items()
            }
        }
        
        # Write report
        output_file = self.log_dir / 'log_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logging.info(f"Generated log analysis report: {output_file}")
        
        # Generate alerts if needed
        self._generate_alerts(report)
    
    def _generate_alerts(self, report: Dict[str, Any]):
        """Generate alerts based on log analysis.
        
        Args:
            report: Log analysis report
        """
        alerts = []
        
        # Check for high error rates
        if 'error' in report['patterns']:
            error_count = report['patterns']['error']['count']
            if error_count > 100:  # Threshold for error alerts
                alerts.append({
                    'type': 'high_error_rate',
                    'count': error_count,
                    'components': report['patterns']['error']['components']
                })
        
        # Check for performance issues
        if 'performance' in report['patterns']:
            perf_count = report['patterns']['performance']['count']
            if perf_count > 50:  # Threshold for performance alerts
                alerts.append({
                    'type': 'performance_issues',
                    'count': perf_count,
                    'components': report['patterns']['performance']['components']
                })
        
        # Check for rate limit issues
        if 'rate_limit' in report['patterns']:
            rate_limit_count = report['patterns']['rate_limit']['count']
            if rate_limit_count > 200:  # Threshold for rate limit alerts
                alerts.append({
                    'type': 'high_rate_limit_hits',
                    'count': rate_limit_count,
                    'components': report['patterns']['rate_limit']['components']
                })
        
        if alerts:
            alert_report = {
                'timestamp': datetime.now().isoformat(),
                'alerts': alerts
            }
            
            output_file = self.log_dir / 'log_alerts.json'
            with open(output_file, 'w') as f:
                json.dump(alert_report, f, indent=2)
            
            logging.info(f"Generated alerts: {output_file}")

def main():
    """Main entry point."""
    parser = LogParser()
    
    # Parse logs from last 24 hours
    parser.parse_logs(hours=24)
    
    # Generate report
    parser.generate_report()

if __name__ == '__main__':
    main() 