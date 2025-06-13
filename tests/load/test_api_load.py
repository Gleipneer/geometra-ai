#!/usr/bin/env python3
"""
Load tests for API endpoints.

Tests:
- Concurrent request handling
- Rate limiting under load
- Memory usage under load
- Response times under load
- Error handling under load
"""

import os
import time
import json
import random
import asyncio
import aiohttp
import pytest
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from memory.memory_manager import MemoryManager

# Test configuration
API_URL = os.getenv('TEST_API_URL', 'http://localhost:8000')
TEST_USER_IDS = [f'load_test_user_{i}' for i in range(100)]
TEST_MESSAGES = [
    'What is artificial intelligence?',
    'Explain machine learning',
    'How do neural networks work?',
    'What are transformers?',
    'Tell me about deep learning',
    'What is natural language processing?',
    'Explain computer vision',
    'How does reinforcement learning work?',
    'What are GANs?',
    'Tell me about transfer learning'
]

class LoadTest:
    """Load test implementation."""
    
    def __init__(
        self,
        num_requests: int = 1000,
        concurrent_users: int = 50,
        request_timeout: int = 30,
        memory_manager: MemoryManager = None
    ):
        """Initialize load test.
        
        Args:
            num_requests: Total number of requests to send
            concurrent_users: Number of concurrent users
            request_timeout: Request timeout in seconds
            memory_manager: Optional memory manager for verification
        """
        self.num_requests = num_requests
        self.concurrent_users = concurrent_users
        self.request_timeout = request_timeout
        self.memory_manager = memory_manager
        self.results: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
    
    async def make_request(
        self,
        session: aiohttp.ClientSession,
        user_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Make a single API request.
        
        Args:
            session: aiohttp session
            user_id: User ID
            message: Message to send
            
        Returns:
            Dict containing request results
        """
        start_time = time.time()
        try:
            async with session.post(
                f'{API_URL}/chat',
                json={
                    'user_id': user_id,
                    'message': message
                },
                timeout=self.request_timeout
            ) as response:
                response_time = time.time() - start_time
                result = {
                    'user_id': user_id,
                    'message': message,
                    'status': response.status,
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat()
                }
                
                if response.status == 200:
                    data = await response.json()
                    result['response'] = data
                else:
                    result['error'] = await response.text()
                    self.errors.append(result)
                
                return result
        except Exception as e:
            response_time = time.time() - start_time
            result = {
                'user_id': user_id,
                'message': message,
                'status': 0,
                'response_time': response_time,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.errors.append(result)
            return result
    
    async def run_user(
        self,
        session: aiohttp.ClientSession,
        user_id: str,
        num_requests: int
    ):
        """Run requests for a single user.
        
        Args:
            session: aiohttp session
            user_id: User ID
            num_requests: Number of requests to make
        """
        for _ in range(num_requests):
            message = random.choice(TEST_MESSAGES)
            result = await self.make_request(session, user_id, message)
            self.results.append(result)
            await asyncio.sleep(random.uniform(0.1, 0.5))  # Random delay
    
    async def run_load_test(self):
        """Run the load test."""
        async with aiohttp.ClientSession() as session:
            tasks = []
            requests_per_user = self.num_requests // self.concurrent_users
            
            for i in range(self.concurrent_users):
                user_id = TEST_USER_IDS[i % len(TEST_USER_IDS)]
                task = asyncio.create_task(
                    self.run_user(session, user_id, requests_per_user)
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results.
        
        Returns:
            Dict containing analysis results
        """
        if not self.results:
            return {'error': 'No results to analyze'}
        
        # Calculate statistics
        response_times = [r['response_time'] for r in self.results]
        status_codes = [r['status'] for r in self.results]
        
        analysis = {
            'total_requests': len(self.results),
            'successful_requests': len([r for r in self.results if r['status'] == 200]),
            'failed_requests': len(self.errors),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'avg_response_time': sum(response_times) / len(response_times),
            'status_code_distribution': {
                code: status_codes.count(code)
                for code in set(status_codes)
            },
            'error_types': {
                error['error']: len([e for e in self.errors if e['error'] == error['error']])
                for error in self.errors
            }
        }
        
        # Add memory analysis if memory manager is available
        if self.memory_manager:
            analysis['memory_stats'] = {
                'stm_size': len(self.memory_manager.get_recent_memories(limit=1000)),
                'ltm_size': len(self.memory_manager.search_memories('', limit=1000))
            }
        
        return analysis

@pytest.mark.asyncio
async def test_api_load():
    """Run API load test."""
    # Initialize memory manager
    memory_manager = MemoryManager(
        redis_url=os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/0'),
        chroma_url=os.getenv('TEST_CHROMA_URL', 'http://localhost:8000')
    )
    
    # Create and run load test
    load_test = LoadTest(
        num_requests=1000,
        concurrent_users=50,
        request_timeout=30,
        memory_manager=memory_manager
    )
    
    # Run test
    start_time = time.time()
    await load_test.run_load_test()
    total_time = time.time() - start_time
    
    # Analyze results
    analysis = load_test.analyze_results()
    
    # Print results
    print('\nLoad Test Results:')
    print(f'Total time: {total_time:.2f} seconds')
    print(f'Total requests: {analysis["total_requests"]}')
    print(f'Successful requests: {analysis["successful_requests"]}')
    print(f'Failed requests: {analysis["failed_requests"]}')
    print(f'Average response time: {analysis["avg_response_time"]:.2f} seconds')
    print(f'Min response time: {analysis["min_response_time"]:.2f} seconds')
    print(f'Max response time: {analysis["max_response_time"]:.2f} seconds')
    print('\nStatus code distribution:')
    for code, count in analysis['status_code_distribution'].items():
        print(f'  {code}: {count}')
    print('\nError types:')
    for error, count in analysis['error_types'].items():
        print(f'  {error}: {count}')
    
    # Verify results
    assert analysis['successful_requests'] > 0
    assert analysis['avg_response_time'] < 5  # Should be under 5 seconds
    assert analysis['failed_requests'] < analysis['total_requests'] * 0.1  # Less than 10% failures

@pytest.mark.asyncio
async def test_rate_limit_handling():
    """Test rate limit handling under load."""
    # Initialize load test with high concurrency
    load_test = LoadTest(
        num_requests=100,
        concurrent_users=20,
        request_timeout=10
    )
    
    # Run test
    await load_test.run_load_test()
    
    # Analyze results
    analysis = load_test.analyze_results()
    
    # Verify rate limiting
    rate_limit_errors = len([
        e for e in load_test.errors
        if 'rate limit' in str(e.get('error', '')).lower()
    ])
    
    assert rate_limit_errors > 0  # Should have some rate limit errors
    assert analysis['avg_response_time'] < 2  # Should be fast

@pytest.mark.asyncio
async def test_memory_usage():
    """Test memory usage under load."""
    # Initialize memory manager
    memory_manager = MemoryManager(
        redis_url=os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/0'),
        chroma_url=os.getenv('TEST_CHROMA_URL', 'http://localhost:8000')
    )
    
    # Initialize load test
    load_test = LoadTest(
        num_requests=500,
        concurrent_users=25,
        request_timeout=20,
        memory_manager=memory_manager
    )
    
    # Run test
    await load_test.run_load_test()
    
    # Analyze results
    analysis = load_test.analyze_results()
    
    # Verify memory usage
    assert 'memory_stats' in analysis
    assert analysis['memory_stats']['stm_size'] > 0
    assert analysis['memory_stats']['ltm_size'] > 0
    
    # Verify memory growth
    initial_stm_size = analysis['memory_stats']['stm_size']
    initial_ltm_size = analysis['memory_stats']['ltm_size']
    
    # Run another batch
    await load_test.run_load_test()
    
    # Check memory growth
    new_analysis = load_test.analyze_results()
    assert new_analysis['memory_stats']['stm_size'] >= initial_stm_size
    assert new_analysis['memory_stats']['ltm_size'] >= initial_ltm_size

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling under load."""
    # Initialize load test with invalid requests
    load_test = LoadTest(
        num_requests=100,
        concurrent_users=10,
        request_timeout=5
    )
    
    # Run test with invalid requests
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):
            # Randomly generate invalid requests
            if random.random() < 0.3:  # 30% invalid requests
                user_id = None
                message = None
            else:
                user_id = TEST_USER_IDS[i % len(TEST_USER_IDS)]
                message = random.choice(TEST_MESSAGES)
            
            task = asyncio.create_task(
                load_test.make_request(session, user_id, message)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    # Analyze results
    analysis = load_test.analyze_results()
    
    # Verify error handling
    assert analysis['failed_requests'] > 0
    assert all(
        error['status'] in [400, 422, 500]
        for error in load_test.errors
    )

if __name__ == '__main__':
    # Run load test
    asyncio.run(test_api_load()) 