#!/usr/bin/env python3
"""
Metrics collector for Geometra AI system.

Collects and exports system metrics:
- Response times
- Request counts
- Memory usage
- Token costs
- API usage
"""

import os
import time
import json
import psutil
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from logging.handlers import RotatingFileHandler
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        RotatingFileHandler('logs/metrics_collector.log', maxBytes=1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

@dataclass
class SystemMetrics:
    """System metrics data class."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used: int
    disk_usage_percent: float
    network_io: Dict[str, int]

@dataclass
class APIMetrics:
    """API metrics data class."""
    timestamp: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    rate_limit_hits: int
    token_usage: Dict[str, int]
    cost_estimate: float

class MetricsCollector:
    """Metrics collector implementation."""
    
    def __init__(
        self,
        output_dir: str = 'metrics',
        collection_interval: int = 60,
        retention_days: int = 7
    ):
        """Initialize metrics collector.
        
        Args:
            output_dir: Directory to store metrics
            collection_interval: Collection interval in seconds
            retention_days: Number of days to retain metrics
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collection_interval = collection_interval
        self.retention_days = retention_days
        self.api_metrics: List[APIMetrics] = []
        self.system_metrics: List[SystemMetrics] = []
    
    async def collect_metrics(self):
        """Collect system and API metrics."""
        while True:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.system_metrics.append(system_metrics)
                
                # Collect API metrics
                api_metrics = await self._collect_api_metrics()
                self.api_metrics.append(api_metrics)
                
                # Export metrics
                self._export_metrics()
                
                # Clean up old metrics
                self._cleanup_old_metrics()
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logging.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics.
        
        Returns:
            SystemMetrics object
        """
        # Get CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used
        
        # Get disk metrics
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        
        # Get network metrics
        net_io = psutil.net_io_counters()
        network_io = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used=memory_used,
            disk_usage_percent=disk_usage_percent,
            network_io=network_io
        )
    
    async def _collect_api_metrics(self) -> APIMetrics:
        """Collect API metrics.
        
        Returns:
            APIMetrics object
        """
        # Get API metrics from Redis or other storage
        # This is a placeholder - implement actual collection logic
        return APIMetrics(
            timestamp=datetime.now().isoformat(),
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            avg_response_time=0.0,
            p95_response_time=0.0,
            p99_response_time=0.0,
            rate_limit_hits=0,
            token_usage={'prompt': 0, 'completion': 0},
            cost_estimate=0.0
        )
    
    def _export_metrics(self):
        """Export metrics to files."""
        # Export system metrics
        system_metrics_file = self.output_dir / 'system_metrics.json'
        with open(system_metrics_file, 'w') as f:
            json.dump([asdict(m) for m in self.system_metrics], f, indent=2)
        
        # Export API metrics
        api_metrics_file = self.output_dir / 'api_metrics.json'
        with open(api_metrics_file, 'w') as f:
            json.dump([asdict(m) for m in self.api_metrics], f, indent=2)
        
        # Export Prometheus metrics
        self._export_prometheus_metrics()
    
    def _export_prometheus_metrics(self):
        """Export metrics in Prometheus format."""
        prometheus_metrics = []
        
        # System metrics
        if self.system_metrics:
            latest_system = self.system_metrics[-1]
            prometheus_metrics.extend([
                f'# HELP system_cpu_percent CPU usage percentage',
                f'# TYPE system_cpu_percent gauge',
                f'system_cpu_percent {latest_system.cpu_percent}',
                '',
                f'# HELP system_memory_percent Memory usage percentage',
                f'# TYPE system_memory_percent gauge',
                f'system_memory_percent {latest_system.memory_percent}',
                '',
                f'# HELP system_memory_used Memory used in bytes',
                f'# TYPE system_memory_used gauge',
                f'system_memory_used {latest_system.memory_used}',
                '',
                f'# HELP system_disk_usage_percent Disk usage percentage',
                f'# TYPE system_disk_usage_percent gauge',
                f'system_disk_usage_percent {latest_system.disk_usage_percent}'
            ])
        
        # API metrics
        if self.api_metrics:
            latest_api = self.api_metrics[-1]
            prometheus_metrics.extend([
                f'# HELP api_total_requests Total number of API requests',
                f'# TYPE api_total_requests counter',
                f'api_total_requests {latest_api.total_requests}',
                '',
                f'# HELP api_successful_requests Number of successful API requests',
                f'# TYPE api_successful_requests counter',
                f'api_successful_requests {latest_api.successful_requests}',
                '',
                f'# HELP api_failed_requests Number of failed API requests',
                f'# TYPE api_failed_requests counter',
                f'api_failed_requests {latest_api.failed_requests}',
                '',
                f'# HELP api_avg_response_time Average API response time',
                f'# TYPE api_avg_response_time gauge',
                f'api_avg_response_time {latest_api.avg_response_time}',
                '',
                f'# HELP api_rate_limit_hits Number of rate limit hits',
                f'# TYPE api_rate_limit_hits counter',
                f'api_rate_limit_hits {latest_api.rate_limit_hits}'
            ])
        
        # Write Prometheus metrics
        prometheus_file = self.output_dir / 'metrics.prom'
        with open(prometheus_file, 'w') as f:
            f.write('\n'.join(prometheus_metrics))
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics files."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for metrics_file in self.output_dir.glob('*.json'):
            try:
                file_date = datetime.fromtimestamp(metrics_file.stat().st_mtime)
                if file_date < cutoff_date:
                    metrics_file.unlink()
                    logging.info(f"Deleted old metrics file: {metrics_file}")
            except Exception as e:
                logging.error(f"Error cleaning up {metrics_file}: {e}")

async def main():
    """Main entry point."""
    collector = MetricsCollector()
    await collector.collect_metrics()

if __name__ == '__main__':
    asyncio.run(main()) 