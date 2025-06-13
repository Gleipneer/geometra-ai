#!/usr/bin/env python3
"""
Audit Logger Module for Geometra AI

Provides structured logging of security-relevant events:
- API key usage and rotation
- Rate limit violations
- Authentication attempts
- System access patterns

Usage:
    from security.audit_logger import AuditLogger
    
    # Initialize logger
    logger = AuditLogger()
    
    # Log security event
    logger.log_event(
        event_type='api_key_used',
        user_id='user_123',
        details={'service': 'openai'}
    )
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Optional, Any, List
import redis
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('audit_logger')

class AuditEvent(BaseModel):
    """Audit event model."""
    event_id: str
    event_type: str
    timestamp: datetime
    user_id: Optional[str]
    ip_address: Optional[str]
    details: Dict[str, Any]
    severity: str = 'info'

class AuditLogger:
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize audit logger.
        
        Args:
            redis_url: Optional Redis URL for distributed logging
        """
        # Initialize Redis client if URL provided
        self.redis_client = None
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
        
        # Event type definitions
        self.event_types = {
            'api_key_used': {
                'severity': 'info',
                'retention_days': 90
            },
            'api_key_rotated': {
                'severity': 'warning',
                'retention_days': 365
            },
            'rate_limit_exceeded': {
                'severity': 'warning',
                'retention_days': 30
            },
            'authentication_failed': {
                'severity': 'warning',
                'retention_days': 30
            },
            'authentication_success': {
                'severity': 'info',
                'retention_days': 90
            },
            'system_access': {
                'severity': 'info',
                'retention_days': 90
            },
            'security_violation': {
                'severity': 'error',
                'retention_days': 365
            }
        }
        
        logger.info("Initialized audit logger")

    def _generate_event_id(self, event_type: str, user_id: Optional[str]) -> str:
        """Generate unique event ID."""
        timestamp = datetime.now().isoformat()
        base = f"{event_type}:{user_id or 'anonymous'}:{timestamp}"
        return hashlib.sha256(base.encode()).hexdigest()

    def _get_event_key(self, event_id: str) -> str:
        """Get Redis key for event storage."""
        return f"audit:event:{event_id}"

    def _get_user_events_key(self, user_id: str) -> str:
        """Get Redis key for user events list."""
        return f"audit:user:{user_id}"

    def _get_event_type_key(self, event_type: str) -> str:
        """Get Redis key for event type list."""
        return f"audit:type:{event_type}"

    def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log security event.
        
        Args:
            event_type: Type of event (must be in event_types)
            user_id: Optional user identifier
            ip_address: Optional IP address
            details: Optional event details
            
        Returns:
            str: Event ID
        """
        try:
            # Validate event type
            if event_type not in self.event_types:
                logger.error(f"Unknown event type: {event_type}")
                return None
            
            # Create event
            event = AuditEvent(
                event_id=self._generate_event_id(event_type, user_id),
                event_type=event_type,
                timestamp=datetime.now(),
                user_id=user_id,
                ip_address=ip_address,
                details=details or {},
                severity=self.event_types[event_type]['severity']
            )
            
            # Log to file
            logger.info(
                f"Event: {event.event_type} | "
                f"User: {event.user_id or 'anonymous'} | "
                f"Severity: {event.severity}"
            )
            
            # Store in Redis if available
            if self.redis_client:
                # Store event
                event_key = self._get_event_key(event.event_id)
                self.redis_client.set(
                    event_key,
                    event.json(),
                    ex=self.event_types[event_type]['retention_days'] * 86400
                )
                
                # Add to user events
                if user_id:
                    user_key = self._get_user_events_key(user_id)
                    self.redis_client.lpush(user_key, event.event_id)
                    self.redis_client.expire(
                        user_key,
                        self.event_types[event_type]['retention_days'] * 86400
                    )
                
                # Add to event type list
                type_key = self._get_event_type_key(event_type)
                self.redis_client.lpush(type_key, event.event_id)
                self.redis_client.expire(
                    type_key,
                    self.event_types[event_type]['retention_days'] * 86400
                )
            
            return event.event_id
        except Exception as e:
            logger.error(f"Failed to log event: {str(e)}")
            return None

    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Get event by ID."""
        try:
            if not self.redis_client:
                return None
            
            event_data = self.redis_client.get(self._get_event_key(event_id))
            if event_data:
                return AuditEvent.parse_raw(event_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get event: {str(e)}")
            return None

    def get_user_events(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Get recent events for user."""
        try:
            if not self.redis_client:
                return []
            
            user_key = self._get_user_events_key(user_id)
            event_ids = self.redis_client.lrange(user_key, 0, limit - 1)
            
            events = []
            for event_id in event_ids:
                event = self.get_event(event_id.decode())
                if event:
                    events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Failed to get user events: {str(e)}")
            return []

    def get_events_by_type(
        self,
        event_type: str,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Get recent events of type."""
        try:
            if not self.redis_client:
                return []
            
            type_key = self._get_event_type_key(event_type)
            event_ids = self.redis_client.lrange(type_key, 0, limit - 1)
            
            events = []
            for event_id in event_ids:
                event = self.get_event(event_id.decode())
                if event:
                    events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Failed to get events by type: {str(e)}")
            return []

    def search_events(
        self,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Search events with filters."""
        try:
            if not self.redis_client:
                return []
            
            # Get candidate events
            if event_type:
                events = self.get_events_by_type(event_type, limit)
            elif user_id:
                events = self.get_user_events(user_id, limit)
            else:
                # Get all events (not recommended for production)
                events = []
                for event_type in self.event_types:
                    events.extend(self.get_events_by_type(event_type, limit))
            
            # Apply filters
            filtered_events = []
            for event in events:
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue
                if severity and event.severity != severity:
                    continue
                if user_id and event.user_id != user_id:
                    continue
                filtered_events.append(event)
            
            return filtered_events[:limit]
        except Exception as e:
            logger.error(f"Failed to search events: {str(e)}")
            return []

    def generate_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """Generate audit report."""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'period': {
                    'start': start_time.isoformat() if start_time else None,
                    'end': end_time.isoformat() if end_time else None
                },
                'events_by_type': {},
                'events_by_severity': {
                    'info': 0,
                    'warning': 0,
                    'error': 0
                },
                'top_users': {}
            }
            
            # Get all events in period
            events = self.search_events(
                start_time=start_time,
                end_time=end_time,
                limit=1000
            )
            
            # Process events
            for event in events:
                # Count by type
                if event.event_type not in report['events_by_type']:
                    report['events_by_type'][event.event_type] = 0
                report['events_by_type'][event.event_type] += 1
                
                # Count by severity
                report['events_by_severity'][event.severity] += 1
                
                # Count by user
                if event.user_id:
                    if event.user_id not in report['top_users']:
                        report['top_users'][event.user_id] = 0
                    report['top_users'][event.user_id] += 1
            
            # Sort top users
            report['top_users'] = dict(
                sorted(
                    report['top_users'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            )
            
            return report
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Example usage
if __name__ == '__main__':
    # Create logger
    audit_logger = AuditLogger(redis_url=os.getenv('REDIS_URL'))
    
    # Log some events
    audit_logger.log_event(
        event_type='api_key_used',
        user_id='user_123',
        details={'service': 'openai'}
    )
    
    audit_logger.log_event(
        event_type='rate_limit_exceeded',
        user_id='user_456',
        ip_address='192.168.1.1',
        details={'limit': 100, 'count': 150}
    )
    
    # Generate report
    report = audit_logger.generate_report()
    print(json.dumps(report, indent=2)) 