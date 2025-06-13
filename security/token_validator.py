#!/usr/bin/env python3
"""
Token Validator Module for Geometra AI

Handles API key validation, rotation, and management.
Supports multiple API keys for different services (OpenAI, ChromaDB, etc.).

Usage:
    from security.token_validator import TokenValidator
    
    # Initialize validator
    validator = TokenValidator()
    
    # Validate API key
    if validator.validate_key('openai', 'sk-...'):
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
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import redis
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/token_validator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('token_validator')

class TokenInfo(BaseModel):
    """Token information model."""
    key: str
    service: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int = 0
    is_active: bool = True

class TokenValidator:
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize token validator.
        
        Args:
            redis_url: Optional Redis URL for distributed token storage
        """
        # Initialize Redis client if URL provided
        self.redis_client = None
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
        
        # Load API keys from environment
        self.api_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'chroma': os.getenv('CHROMA_API_KEY'),
            'redis': os.getenv('REDIS_URL')
        }
        
        # Token rotation settings
        self.rotation_settings = {
            'openai': {
                'max_age_days': 30,
                'max_usage': 1000000,
                'rotation_notice_days': 7
            },
            'chroma': {
                'max_age_days': 90,
                'max_usage': 5000000,
                'rotation_notice_days': 14
            }
        }
        
        logger.info("Initialized token validator")

    def _get_token_key(self, service: str, key: str) -> str:
        """Get Redis key for token storage."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return f"token:{service}:{key_hash}"

    def _load_token_info(self, service: str, key: str) -> Optional[TokenInfo]:
        """Load token information from Redis or create new."""
        if not self.redis_client:
            return None
        
        token_key = self._get_token_key(service, key)
        token_data = self.redis_client.get(token_key)
        
        if token_data:
            return TokenInfo.parse_raw(token_data)
        
        # Create new token info
        token_info = TokenInfo(
            key=key,
            service=service,
            created_at=datetime.now(),
            expires_at=None,
            last_used=None
        )
        
        # Save to Redis
        self.redis_client.set(
            token_key,
            token_info.json(),
            ex=3600 * 24 * 30  # 30 days TTL
        )
        
        return token_info

    def _update_token_info(self, token_info: TokenInfo) -> None:
        """Update token information in Redis."""
        if not self.redis_client:
            return
        
        token_info.last_used = datetime.now()
        token_info.usage_count += 1
        
        token_key = self._get_token_key(token_info.service, token_info.key)
        self.redis_client.set(
            token_key,
            token_info.json(),
            ex=3600 * 24 * 30  # 30 days TTL
        )

    def validate_key(self, service: str, key: str) -> bool:
        """Validate API key for service.
        
        Args:
            service: Service name (e.g., 'openai', 'chroma')
            key: API key to validate
            
        Returns:
            bool: True if key is valid, False otherwise
        """
        try:
            # Check if key exists in environment
            if service not in self.api_keys:
                logger.error(f"Unknown service: {service}")
                return False
            
            if not self.api_keys[service]:
                logger.error(f"No API key configured for {service}")
                return False
            
            # Validate key format
            if not self._validate_key_format(service, key):
                logger.error(f"Invalid key format for {service}")
                return False
            
            # Load token info
            token_info = self._load_token_info(service, key)
            if token_info:
                # Check if token is expired
                if token_info.expires_at and token_info.expires_at < datetime.now():
                    logger.warning(f"Token expired for {service}")
                    return False
                
                # Check usage limits
                settings = self.rotation_settings.get(service, {})
                if settings.get('max_usage') and token_info.usage_count >= settings['max_usage']:
                    logger.warning(f"Token usage limit exceeded for {service}")
                    return False
                
                # Update token info
                self._update_token_info(token_info)
            
            return True
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return False

    def _validate_key_format(self, service: str, key: str) -> bool:
        """Validate API key format."""
        if service == 'openai':
            return key.startswith('sk-') and len(key) > 20
        elif service == 'chroma':
            return len(key) > 10
        elif service == 'redis':
            return key.startswith('redis://')
        return True

    def rotate_key(self, service: str) -> Optional[str]:
        """Rotate API key for service.
        
        Args:
            service: Service name to rotate key for
            
        Returns:
            Optional[str]: New API key if rotation successful
        """
        try:
            # Check if rotation is needed
            if not self._needs_rotation(service):
                return None
            
            # Generate new key (implementation depends on service)
            new_key = self._generate_new_key(service)
            if not new_key:
                return None
            
            # Update environment
            self.api_keys[service] = new_key
            
            # Create new token info
            token_info = TokenInfo(
                key=new_key,
                service=service,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(
                    days=self.rotation_settings[service]['max_age_days']
                )
            )
            
            # Save to Redis
            if self.redis_client:
                token_key = self._get_token_key(service, new_key)
                self.redis_client.set(
                    token_key,
                    token_info.json(),
                    ex=3600 * 24 * 30  # 30 days TTL
                )
            
            logger.info(f"Rotated key for {service}")
            return new_key
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            return None

    def _needs_rotation(self, service: str) -> bool:
        """Check if key needs rotation."""
        if service not in self.rotation_settings:
            return False
        
        settings = self.rotation_settings[service]
        token_info = self._load_token_info(service, self.api_keys[service])
        
        if not token_info:
            return False
        
        # Check age
        if token_info.created_at + timedelta(days=settings['max_age_days']) <= datetime.now():
            return True
        
        # Check usage
        if settings.get('max_usage') and token_info.usage_count >= settings['max_usage']:
            return True
        
        return False

    def _generate_new_key(self, service: str) -> Optional[str]:
        """Generate new API key for service."""
        # This is a placeholder - actual implementation depends on service
        if service == 'openai':
            # OpenAI key rotation requires manual intervention
            return None
        elif service == 'chroma':
            # Generate new ChromaDB key
            return f"chroma-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:20]}"
        elif service == 'redis':
            # Redis URL rotation requires manual intervention
            return None
        return None

    def get_key_status(self, service: str) -> Dict:
        """Get status of API key for service."""
        try:
            token_info = self._load_token_info(service, self.api_keys[service])
            if not token_info:
                return {
                    'status': 'unknown',
                    'service': service
                }
            
            settings = self.rotation_settings.get(service, {})
            needs_rotation = self._needs_rotation(service)
            
            return {
                'status': 'active' if token_info.is_active else 'inactive',
                'service': service,
                'created_at': token_info.created_at.isoformat(),
                'expires_at': token_info.expires_at.isoformat() if token_info.expires_at else None,
                'last_used': token_info.last_used.isoformat() if token_info.last_used else None,
                'usage_count': token_info.usage_count,
                'max_usage': settings.get('max_usage'),
                'needs_rotation': needs_rotation
            }
        except Exception as e:
            logger.error(f"Failed to get key status: {str(e)}")
            return {
                'status': 'error',
                'service': service,
                'error': str(e)
            }

# FastAPI middleware
class TokenValidationMiddleware:
    def __init__(self, validator: TokenValidator):
        """Initialize token validation middleware."""
        self.validator = validator

    async def __call__(self, request: Request, call_next):
        """Validate API key before processing request."""
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={'error': 'Missing API Key'}
            )
        
        # Get service from path
        service = request.url.path.split('/')[1]  # e.g., /openai/... -> openai
        
        # Validate key
        if not self.validator.validate_key(service, api_key):
            return JSONResponse(
                status_code=401,
                content={'error': 'Invalid API Key'}
            )
        
        return await call_next(request)

# Example usage
if __name__ == '__main__':
    # Create validator
    validator = TokenValidator(redis_url=os.getenv('REDIS_URL'))
    
    # Test key validation
    for service in ['openai', 'chroma', 'redis']:
        key = os.getenv(f'{service.upper()}_API_KEY')
        if key:
            is_valid = validator.validate_key(service, key)
            status = validator.get_key_status(service)
            print(f"{service}: {'Valid' if is_valid else 'Invalid'}")
            print(json.dumps(status, indent=2)) 