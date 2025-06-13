#!/usr/bin/env python3
"""
Rate Limiter Module for Geometra AI

Implements a distributed rate limiter using the token bucket algorithm
with Redis as the backend for distributed rate limiting.

Usage:
    from security.rate_limiter import RateLimiter
    
    # Create a rate limiter (100 requests per minute)
    limiter = RateLimiter(
        requests_per_minute=100,
        burst_size=50
    )
    
    # Check if request is allowed
    if limiter.is_allowed("user_123"):
        # Process request
        pass
    else:
        # Reject request
        pass
"""

import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import redis
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rate_limiter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('rate_limiter')

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 100,
        burst_size: int = 50,
        redis_url: Optional[str] = None
    ):
        """Initialize rate limiter with token bucket algorithm.
        
        Args:
            requests_per_minute: Number of requests allowed per minute
            burst_size: Maximum number of tokens that can be accumulated
            redis_url: Optional Redis URL for distributed rate limiting
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.tokens_per_second = requests_per_minute / 60.0
        
        # Initialize Redis client if URL provided
        self.redis_client = None
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
        
        # Local rate limiting state (used if Redis is not available)
        self.local_buckets: Dict[str, Tuple[float, float]] = {}
        
        logger.info(
            f"Initialized rate limiter: {requests_per_minute} req/min, "
            f"burst: {burst_size}, distributed: {bool(redis_url)}"
        )

    def _get_bucket_key(self, identifier: str) -> str:
        """Get Redis key for rate limit bucket."""
        return f"rate_limit:{identifier}"

    def _get_local_bucket(self, identifier: str) -> Tuple[float, float]:
        """Get or create local rate limit bucket."""
        if identifier not in self.local_buckets:
            self.local_buckets[identifier] = (time.time(), self.burst_size)
        return self.local_buckets[identifier]

    def _update_local_bucket(
        self,
        identifier: str,
        last_update: float,
        tokens: float
    ) -> Tuple[float, float]:
        """Update local rate limit bucket."""
        now = time.time()
        time_passed = now - last_update
        new_tokens = min(
            self.burst_size,
            tokens + time_passed * self.tokens_per_second
        )
        self.local_buckets[identifier] = (now, new_tokens)
        return (now, new_tokens)

    def _update_redis_bucket(
        self,
        identifier: str,
        last_update: float,
        tokens: float
    ) -> Tuple[float, float]:
        """Update Redis rate limit bucket."""
        now = time.time()
        time_passed = now - last_update
        new_tokens = min(
            self.burst_size,
            tokens + time_passed * self.tokens_per_second
        )
        
        # Update Redis atomically
        pipe = self.redis_client.pipeline()
        pipe.hset(
            self._get_bucket_key(identifier),
            mapping={
                'last_update': now,
                'tokens': new_tokens
            }
        )
        pipe.expire(self._get_bucket_key(identifier), 3600)  # 1 hour TTL
        pipe.execute()
        
        return (now, new_tokens)

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed under rate limit.
        
        Args:
            identifier: Unique identifier for rate limiting (e.g., user ID, IP)
            
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        try:
            if self.redis_client:
                return self._is_allowed_redis(identifier)
            return self._is_allowed_local(identifier)
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            # Fail open in case of errors
            return True

    def _is_allowed_redis(self, identifier: str) -> bool:
        """Check rate limit using Redis backend."""
        bucket_key = self._get_bucket_key(identifier)
        
        # Get current bucket state
        bucket_data = self.redis_client.hgetall(bucket_key)
        if not bucket_data:
            # New bucket
            last_update = time.time()
            tokens = self.burst_size
        else:
            last_update = float(bucket_data[b'last_update'])
            tokens = float(bucket_data[b'tokens'])
        
        # Update bucket
        now, new_tokens = self._update_redis_bucket(identifier, last_update, tokens)
        
        # Check if request is allowed
        if new_tokens >= 1.0:
            # Consume one token
            self.redis_client.hincrbyfloat(bucket_key, 'tokens', -1.0)
            return True
        
        return False

    def _is_allowed_local(self, identifier: str) -> bool:
        """Check rate limit using local state."""
        last_update, tokens = self._get_local_bucket(identifier)
        now, new_tokens = self._update_local_bucket(identifier, last_update, tokens)
        
        if new_tokens >= 1.0:
            # Consume one token
            self.local_buckets[identifier] = (now, new_tokens - 1.0)
            return True
        
        return False

    def get_remaining_tokens(self, identifier: str) -> float:
        """Get number of remaining tokens for identifier."""
        try:
            if self.redis_client:
                bucket_data = self.redis_client.hgetall(self._get_bucket_key(identifier))
                if bucket_data:
                    return float(bucket_data[b'tokens'])
                return self.burst_size
            
            _, tokens = self._get_local_bucket(identifier)
            return tokens
        except Exception as e:
            logger.error(f"Failed to get remaining tokens: {str(e)}")
            return 0.0

    def reset_bucket(self, identifier: str) -> None:
        """Reset rate limit bucket for identifier."""
        try:
            if self.redis_client:
                self.redis_client.delete(self._get_bucket_key(identifier))
            elif identifier in self.local_buckets:
                del self.local_buckets[identifier]
        except Exception as e:
            logger.error(f"Failed to reset bucket: {str(e)}")

# FastAPI middleware
class RateLimitMiddleware:
    def __init__(
        self,
        requests_per_minute: int = 100,
        burst_size: int = 50,
        redis_url: Optional[str] = None
    ):
        """Initialize rate limit middleware."""
        self.limiter = RateLimiter(
            requests_per_minute=requests_per_minute,
            burst_size=burst_size,
            redis_url=redis_url
        )

    async def __call__(self, request: Request, call_next):
        """Check rate limit before processing request."""
        # Get identifier (IP or user ID)
        identifier = request.headers.get('X-User-ID') or request.client.host
        
        if not self.limiter.is_allowed(identifier):
            return JSONResponse(
                status_code=429,
                content={
                    'error': 'Too Many Requests',
                    'retry_after': 60  # 1 minute
                }
            )
        
        return await call_next(request)

# Example usage
if __name__ == '__main__':
    # Create rate limiter
    limiter = RateLimiter(
        requests_per_minute=100,
        burst_size=50,
        redis_url=os.getenv('REDIS_URL')
    )
    
    # Test rate limiting
    for i in range(120):
        allowed = limiter.is_allowed('test_user')
        remaining = limiter.get_remaining_tokens('test_user')
        print(f"Request {i}: {'Allowed' if allowed else 'Rate Limited'} "
              f"(Remaining: {remaining:.1f})")
        time.sleep(0.1) 