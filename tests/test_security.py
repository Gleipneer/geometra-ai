#!/usr/bin/env python3
"""
Security Component Tests

Tests for:
- Rate limiter
- Token validator
- Audit logger
"""

import os
import time
import pytest
from datetime import datetime, timedelta
from security.rate_limiter import RateLimiter
from security.token_validator import TokenValidator
from security.audit_logger import AuditLogger

# Test configuration
TEST_REDIS_URL = os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/0')
TEST_API_KEY = 'test_api_key_123'
TEST_USER_ID = 'test_user_123'

@pytest.fixture
def rate_limiter():
    """Create rate limiter instance."""
    return RateLimiter(
        requests_per_minute=10,
        burst_size=5,
        redis_url=TEST_REDIS_URL
    )

@pytest.fixture
def token_validator():
    """Create token validator instance."""
    return TokenValidator(redis_url=TEST_REDIS_URL)

@pytest.fixture
def audit_logger():
    """Create audit logger instance."""
    return AuditLogger(redis_url=TEST_REDIS_URL)

class TestRateLimiter:
    """Test rate limiter functionality."""
    
    def test_initial_state(self, rate_limiter):
        """Test initial state of rate limiter."""
        assert rate_limiter.requests_per_minute == 10
        assert rate_limiter.burst_size == 5
    
    def test_single_request(self, rate_limiter):
        """Test single request is allowed."""
        assert rate_limiter.is_allowed(TEST_USER_ID)
    
    def test_burst_requests(self, rate_limiter):
        """Test burst of requests."""
        # Should allow burst_size requests
        for _ in range(rate_limiter.burst_size):
            assert rate_limiter.is_allowed(TEST_USER_ID)
        
        # Next request should be blocked
        assert not rate_limiter.is_allowed(TEST_USER_ID)
    
    def test_rate_limit_recovery(self, rate_limiter):
        """Test rate limit recovery after waiting."""
        # Use up all tokens
        for _ in range(rate_limiter.burst_size):
            rate_limiter.is_allowed(TEST_USER_ID)
        
        # Wait for token refill
        time.sleep(6)  # Wait for 1/10 of a minute
        
        # Should allow some requests
        assert rate_limiter.is_allowed(TEST_USER_ID)
    
    def test_different_users(self, rate_limiter):
        """Test rate limits for different users."""
        user1 = 'user1'
        user2 = 'user2'
        
        # Use up user1's tokens
        for _ in range(rate_limiter.burst_size):
            rate_limiter.is_allowed(user1)
        
        # user2 should still have tokens
        assert rate_limiter.is_allowed(user2)

class TestTokenValidator:
    """Test token validator functionality."""
    
    def test_token_validation(self, token_validator):
        """Test token validation."""
        # Add test token
        token_validator.update_token_info(
            TEST_API_KEY,
            'test_service',
            is_active=True
        )
        
        # Validate token
        assert token_validator.validate_key(TEST_API_KEY, 'test_service')
    
    def test_invalid_token(self, token_validator):
        """Test invalid token rejection."""
        assert not token_validator.validate_key('invalid_key', 'test_service')
    
    def test_token_rotation(self, token_validator):
        """Test token rotation."""
        old_key = TEST_API_KEY
        new_key = 'new_test_key_456'
        
        # Add old token
        token_validator.update_token_info(
            old_key,
            'test_service',
            is_active=True
        )
        
        # Rotate to new token
        token_validator.rotate_key('test_service', new_key)
        
        # Old token should be invalid
        assert not token_validator.validate_key(old_key, 'test_service')
        
        # New token should be valid
        assert token_validator.validate_key(new_key, 'test_service')
    
    def test_token_expiration(self, token_validator):
        """Test token expiration."""
        # Add token with short expiration
        token_validator.update_token_info(
            TEST_API_KEY,
            'test_service',
            is_active=True,
            expires_at=datetime.now() + timedelta(seconds=1)
        )
        
        # Token should be valid initially
        assert token_validator.validate_key(TEST_API_KEY, 'test_service')
        
        # Wait for expiration
        time.sleep(2)
        
        # Token should be invalid
        assert not token_validator.validate_key(TEST_API_KEY, 'test_service')

class TestAuditLogger:
    """Test audit logger functionality."""
    
    def test_event_logging(self, audit_logger):
        """Test basic event logging."""
        event_id = audit_logger.log_event(
            event_type='api_key_used',
            user_id=TEST_USER_ID,
            details={'service': 'test_service'}
        )
        
        assert event_id is not None
        
        # Verify event was logged
        event = audit_logger.get_event(event_id)
        assert event is not None
        assert event.event_type == 'api_key_used'
        assert event.user_id == TEST_USER_ID
    
    def test_event_retrieval(self, audit_logger):
        """Test event retrieval methods."""
        # Log multiple events
        for i in range(3):
            audit_logger.log_event(
                event_type='api_key_used',
                user_id=TEST_USER_ID,
                details={'count': i}
            )
        
        # Get user events
        user_events = audit_logger.get_user_events(TEST_USER_ID)
        assert len(user_events) > 0
        
        # Get events by type
        type_events = audit_logger.get_events_by_type('api_key_used')
        assert len(type_events) > 0
    
    def test_event_search(self, audit_logger):
        """Test event search functionality."""
        # Log events with different types
        audit_logger.log_event(
            event_type='api_key_used',
            user_id=TEST_USER_ID,
            details={'service': 'test_service'}
        )
        
        audit_logger.log_event(
            event_type='rate_limit_exceeded',
            user_id=TEST_USER_ID,
            details={'limit': 100}
        )
        
        # Search by type
        events = audit_logger.search_events(event_type='api_key_used')
        assert len(events) > 0
        assert all(e.event_type == 'api_key_used' for e in events)
        
        # Search by time range
        now = datetime.now()
        events = audit_logger.search_events(
            start_time=now - timedelta(minutes=5),
            end_time=now + timedelta(minutes=5)
        )
        assert len(events) > 0
    
    def test_report_generation(self, audit_logger):
        """Test report generation."""
        # Log some events
        for i in range(5):
            audit_logger.log_event(
                event_type='api_key_used',
                user_id=f'user_{i}',
                details={'count': i}
            )
        
        # Generate report
        report = audit_logger.generate_report()
        
        assert 'timestamp' in report
        assert 'events_by_type' in report
        assert 'events_by_severity' in report
        assert 'top_users' in report
        
        # Verify event counts
        assert report['events_by_type']['api_key_used'] == 5
        assert len(report['top_users']) > 0

def test_security_integration(rate_limiter, token_validator, audit_logger):
    """Test integration between security components."""
    # Simulate API request
    user_id = TEST_USER_ID
    api_key = TEST_API_KEY
    
    # 1. Check rate limit
    assert rate_limiter.is_allowed(user_id)
    
    # 2. Validate token
    token_validator.update_token_info(
        api_key,
        'test_service',
        is_active=True
    )
    assert token_validator.validate_key(api_key, 'test_service')
    
    # 3. Log the event
    event_id = audit_logger.log_event(
        event_type='api_key_used',
        user_id=user_id,
        details={
            'service': 'test_service',
            'rate_limited': True,
            'token_validated': True
        }
    )
    
    # Verify event was logged
    event = audit_logger.get_event(event_id)
    assert event is not None
    assert event.event_type == 'api_key_used'
    assert event.user_id == user_id
    assert event.details['service'] == 'test_service'
    assert event.details['rate_limited']
    assert event.details['token_validated'] 