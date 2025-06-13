#!/usr/bin/env python3
"""
Memory Monitor Module for Geometra AI

This module provides comprehensive monitoring for:
- ChromaDB collections and embeddings
- Redis memory usage and operations
- Memory system performance metrics

Usage:
    python memory_monitor.py --watch  # Continuous monitoring
    python memory_monitor.py --stats  # Show current stats
    python memory_monitor.py --clean  # Clean up old data
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import redis
import chromadb
from chromadb.config import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/memory.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('memory_monitor')

class MemoryMonitor:
    def __init__(self):
        """Initialize memory monitoring with configuration from environment."""
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.chroma_host = os.getenv('CHROMA_HOST', 'localhost')
        self.chroma_port = int(os.getenv('CHROMA_PORT', '8001'))
        self.collection_name = os.getenv('CHROMA_COLLECTION', 'geometra_memory')
        
        # Initialize clients
        self.redis_client = redis.from_url(self.redis_url)
        self.chroma_client = chromadb.HttpClient(
            host=self.chroma_host,
            port=self.chroma_port
        )
        
        # Get collection
        self.collection = self.chroma_client.get_collection(self.collection_name)
        
        # Monitoring thresholds
        self.thresholds = {
            'redis_memory': 0.8,  # 80% of max memory
            'chroma_size': 1000000,  # 1M embeddings
            'query_latency': 1.0,  # 1 second
            'cleanup_age': 30  # 30 days
        }

    def get_redis_stats(self) -> Dict:
        """Get Redis memory and operation statistics."""
        try:
            info = self.redis_client.info()
            return {
                'used_memory': info['used_memory'],
                'used_memory_peak': info['used_memory_peak'],
                'connected_clients': info['connected_clients'],
                'total_commands_processed': info['total_commands_processed'],
                'keyspace_hits': info['keyspace_hits'],
                'keyspace_misses': info['keyspace_misses']
            }
        except Exception as e:
            logger.error(f"Redis stats failed: {str(e)}")
            return {'error': str(e)}

    def get_chroma_stats(self) -> Dict:
        """Get ChromaDB collection statistics."""
        try:
            count = self.collection.count()
            return {
                'total_embeddings': count,
                'collection_name': self.collection_name,
                'dimensions': self.collection.metadata.get('dimension', 'unknown')
            }
        except Exception as e:
            logger.error(f"ChromaDB stats failed: {str(e)}")
            return {'error': str(e)}

    def measure_query_performance(self) -> Dict:
        """Measure memory query performance."""
        try:
            start_time = time.time()
            # Perform a test query
            self.collection.query(
                query_embeddings=[[0.0] * 1536],  # Dummy embedding
                n_results=1
            )
            latency = time.time() - start_time
            
            return {
                'query_latency': latency,
                'status': 'healthy' if latency < self.thresholds['query_latency'] else 'slow'
            }
        except Exception as e:
            logger.error(f"Query performance test failed: {str(e)}")
            return {'error': str(e)}

    def check_memory_health(self) -> Dict:
        """Check overall memory system health."""
        redis_stats = self.get_redis_stats()
        chroma_stats = self.get_chroma_stats()
        perf_stats = self.measure_query_performance()
        
        # Calculate health status
        redis_healthy = 'used_memory' in redis_stats and \
                       redis_stats['used_memory'] < self.thresholds['redis_memory']
        chroma_healthy = 'total_embeddings' in chroma_stats and \
                        chroma_stats['total_embeddings'] < self.thresholds['chroma_size']
        perf_healthy = 'query_latency' in perf_stats and \
                      perf_stats['query_latency'] < self.thresholds['query_latency']
        
        return {
            'status': 'healthy' if all([redis_healthy, chroma_healthy, perf_healthy]) else 'unhealthy',
            'components': {
                'redis': redis_stats,
                'chroma': chroma_stats,
                'performance': perf_stats
            }
        }

    def cleanup_old_data(self, days: int = None) -> Dict:
        """Clean up old memory data."""
        if days is None:
            days = self.thresholds['cleanup_age']
            
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        try:
            # Clean Redis
            keys = self.redis_client.keys('memory:*')
            deleted_keys = 0
            for key in keys:
                if self.redis_client.ttl(key) > 0:  # Only delete keys with TTL
                    self.redis_client.delete(key)
                    deleted_keys += 1
            
            # Clean ChromaDB
            # Note: ChromaDB cleanup requires custom implementation based on your metadata structure
            # This is a placeholder for the actual implementation
            
            return {
                'status': 'success',
                'deleted_keys': deleted_keys,
                'cutoff_date': cutoff_date.isoformat()
            }
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            return {'error': str(e)}

    def generate_report(self) -> str:
        """Generate a human-readable memory report."""
        health = self.check_memory_health()
        
        report = [
            "=== Memory System Report ===",
            f"Time: {datetime.now().isoformat()}",
            f"\nOverall Status: {health['status']}",
            "\nRedis Status:",
            f"  Memory Usage: {health['components']['redis'].get('used_memory', 'N/A')} bytes",
            f"  Peak Memory: {health['components']['redis'].get('used_memory_peak', 'N/A')} bytes",
            f"  Connected Clients: {health['components']['redis'].get('connected_clients', 'N/A')}",
            "\nChromaDB Status:",
            f"  Total Embeddings: {health['components']['chroma'].get('total_embeddings', 'N/A')}",
            f"  Collection: {health['components']['chroma'].get('collection_name', 'N/A')}",
            f"  Dimensions: {health['components']['chroma'].get('dimensions', 'N/A')}",
            "\nPerformance:",
            f"  Query Latency: {health['components']['performance'].get('query_latency', 'N/A'):.2f}s"
        ]
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='Geometra AI Memory Monitor')
    parser.add_argument('--watch', action='store_true', help='Continuous monitoring')
    parser.add_argument('--stats', action='store_true', help='Show current stats')
    parser.add_argument('--clean', action='store_true', help='Clean up old data')
    parser.add_argument('--days', type=int, help='Days of data to keep when cleaning')
    args = parser.parse_args()

    monitor = MemoryMonitor()

    if args.watch:
        logger.info("Starting continuous monitoring...")
        while True:
            report = monitor.generate_report()
            print("\033[2J\033[H")  # Clear screen
            print(report)
            time.sleep(60)  # Check every minute
    elif args.stats:
        health = monitor.check_memory_health()
        print(json.dumps(health, indent=2))
    elif args.clean:
        result = monitor.cleanup_old_data(args.days)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 