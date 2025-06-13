# Säkerhet

Detta dokument beskriver hur man konfigurerar och hanterar säkerhet för Geometra AI-systemet.

## Översikt

Säkerhetssystemet innehåller:

1. **Autentisering**
   - JWT
   - API Keys
   - OAuth2

2. **Auktorisering**
   - RBAC
   - ACL
   - Policies

3. **Datasäkerhet**
   - Kryptering
   - Sanitization
   - Validation

## Installation

1. Installera säkerhetsverktyg:
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

2. Skapa säkerhetsstruktur:
```bash
mkdir -p security/{auth,authorization,data}
```

## Konfiguration

### Autentisering

1. Skapa `security/auth/jwt.py`:
```python
"""JWT authentication."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Konfiguration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
```

2. Skapa `security/auth/api_keys.py`:
```python
"""API key authentication."""

from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from typing import Optional

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """Validate API key."""
    if api_key_header == "test-api-key":
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key"
    )
```

### Auktorisering

1. Skapa `security/authorization/rbac.py`:
```python
"""Role-based access control."""

from enum import Enum
from typing import List
from fastapi import HTTPException, status

class Role(str, Enum):
    """User roles."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Permission(str, Enum):
    """User permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"

# Role permissions
ROLE_PERMISSIONS = {
    Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE],
    Role.USER: [Permission.READ, Permission.WRITE],
    Role.GUEST: [Permission.READ],
}

def check_permission(user_role: Role, required_permission: Permission) -> bool:
    """Check if user has permission."""
    if user_role not in ROLE_PERMISSIONS:
        return False
    return required_permission in ROLE_PERMISSIONS[user_role]

def require_permission(required_permission: Permission):
    """Permission decorator."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_role = kwargs.get("user_role")
            if not check_permission(user_role, required_permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

2. Skapa `security/authorization/policies.py`:
```python
"""Access control policies."""

from typing import Dict, List
from .rbac import Role, Permission

class Policy:
    """Access control policy."""
    
    def __init__(self, name: str, roles: List[Role], permissions: List[Permission]):
        """Initialize policy."""
        self.name = name
        self.roles = roles
        self.permissions = permissions

# System policies
POLICIES = {
    "read_only": Policy(
        name="read_only",
        roles=[Role.GUEST],
        permissions=[Permission.READ]
    ),
    "standard": Policy(
        name="standard",
        roles=[Role.USER],
        permissions=[Permission.READ, Permission.WRITE]
    ),
    "admin": Policy(
        name="admin",
        roles=[Role.ADMIN],
        permissions=[Permission.READ, Permission.WRITE, Permission.DELETE]
    ),
}

def get_policy(policy_name: str) -> Policy:
    """Get policy by name."""
    if policy_name not in POLICIES:
        raise ValueError(f"Policy {policy_name} not found")
    return POLICIES[policy_name]
```

### Datasäkerhet

1. Skapa `security/data/encryption.py`:
```python
"""Data encryption."""

from cryptography.fernet import Fernet
from typing import Any, Dict
import json

# Generate key
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_data(data: Dict[str, Any]) -> bytes:
    """Encrypt data."""
    json_data = json.dumps(data)
    return cipher_suite.encrypt(json_data.encode())

def decrypt_data(encrypted_data: bytes) -> Dict[str, Any]:
    """Decrypt data."""
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode())
```

2. Skapa `security/data/sanitization.py`:
```python
"""Data sanitization."""

import re
from typing import Any, Dict
from html import escape

def sanitize_input(data: Any) -> Any:
    """Sanitize input data."""
    if isinstance(data, str):
        # Remove HTML tags
        data = re.sub(r'<[^>]+>', '', data)
        # Escape HTML characters
        data = escape(data)
        # Remove special characters
        data = re.sub(r'[^\w\s-]', '', data)
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data
```

3. Skapa `security/data/validation.py`:
```python
"""Data validation."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re

class UserInput(BaseModel):
    """User input validation."""
    
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[Dict] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    
    @validator('message')
    def validate_message(cls, v):
        """Validate message."""
        if not re.match(r'^[\w\s.,!?-]+$', v):
            raise ValueError('Message contains invalid characters')
        return v
    
    @validator('context')
    def validate_context(cls, v):
        """Validate context."""
        if v is not None:
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, (str, int, float, bool)):
                    raise ValueError('Invalid context format')
        return v
```

## Validering

1. Testa autentisering:
```bash
curl -X POST http://localhost:8000/token -d "username=test&password=test"
```

2. Testa API-nyckel:
```bash
curl -H "X-API-Key: test-api-key" http://localhost:8000/api/test
```

3. Testa RBAC:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/admin
```

## Felsökning

### Säkerhetsproblem

1. **Autentiseringsproblem**
   - Kontrollera tokens
   - Verifiera API-nycklar
   - Validera credentials

2. **Auktoriseringsproblem**
   - Kontrollera roller
   - Verifiera permissions
   - Validera policies

3. **Datasäkerhetsproblem**
   - Kontrollera kryptering
   - Verifiera sanitization
   - Validera input

## Loggning

1. Konfigurera loggning i `security/utils/logging.py`:
```python
"""Security logging configuration."""

import logging
import os
from datetime import datetime

def setup_security_logging():
    """Configure logging for security."""
    log_dir = "logs/security"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"security_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
```

## Nästa steg

1. Skapa [Dokumentation](34_DOKUMENTATION.md)
2. Implementera [Backup](35_BACKUP.md)
3. Konfigurera [DR](36_DR.md) 