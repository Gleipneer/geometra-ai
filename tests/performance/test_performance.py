"""Performance tests for Geometra AI system."""

import pytest
import asyncio
import time
from typing import Dict, List
import aiohttp
import statistics
from datetime import datetime

# Test configuration
CONCURRENT_USERS = 10
REQUESTS_PER_USER = 100
TARGET_ENDPOINTS = [
    "/api/v1/health",
    "/api/v1/version"
]

class PerformanceTest:
    """Handles performance testing of the API endpoints."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: Dict[str, List[float]] = {endpoint: [] for endpoint in TARGET_ENDPOINTS}
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str) -> float:
        """Make a single request and measure response time."""
        start_time = time.time()
        async with session.get(f"{self.base_url}{endpoint}") as response:
            await response.text()
            return time.time() - start_time
    
    async def user_session(self, user_id: int) -> None:
        """Simulate a user session making multiple requests."""
        async with aiohttp.ClientSession() as session:
            for _ in range(REQUESTS_PER_USER):
                for endpoint in TARGET_ENDPOINTS:
                    response_time = await self.make_request(session, endpoint)
                    self.results[endpoint].append(response_time)
                await asyncio.sleep(0.1)  # Small delay between requests
    
    async def run_test(self) -> Dict[str, Dict[str, float]]:
        """Run the performance test with multiple concurrent users."""
        tasks = [self.user_session(i) for i in range(CONCURRENT_USERS)]
        await asyncio.gather(*tasks)
        
        # Calculate statistics
        stats = {}
        for endpoint, times in self.results.items():
            stats[endpoint] = {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "p95": statistics.quantiles(times, n=20)[18],  # 95th percentile
                "total_requests": len(times)
            }
        
        return stats

@pytest.mark.asyncio
async def test_api_performance():
    """Run performance tests against the API."""
    base_url = "http://localhost:8000"  # Update with your API URL
    test = PerformanceTest(base_url)
    
    # Run the test
    start_time = time.time()
    results = await test.run_test()
    total_time = time.time() - start_time
    
    # Print results
    print(f"\nPerformance Test Results ({datetime.now().isoformat()})")
    print(f"Total test duration: {total_time:.2f} seconds")
    print(f"Concurrent users: {CONCURRENT_USERS}")
    print(f"Requests per user: {REQUESTS_PER_USER}")
    print("\nEndpoint Statistics:")
    
    for endpoint, stats in results.items():
        print(f"\n{endpoint}:")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Min response time: {stats['min']*1000:.2f}ms")
        print(f"  Max response time: {stats['max']*1000:.2f}ms")
        print(f"  Mean response time: {stats['mean']*1000:.2f}ms")
        print(f"  Median response time: {stats['median']*1000:.2f}ms")
        print(f"  95th percentile: {stats['p95']*1000:.2f}ms")
    
    # Assertions
    for endpoint, stats in results.items():
        assert stats["mean"] < 0.5, f"Mean response time for {endpoint} exceeds 500ms"
        assert stats["p95"] < 1.0, f"95th percentile for {endpoint} exceeds 1000ms"
        assert stats["total_requests"] == CONCURRENT_USERS * REQUESTS_PER_USER, \
            f"Unexpected number of requests for {endpoint}" 