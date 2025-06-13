# Security Implementation Patch

This patch implements comprehensive security features for the Geometra AI system, including rate limiting, token validation, and audit logging.

## Components Added

1. Rate Limiter (`security/rate_limiter.py`)
   - Token bucket algorithm
   - Redis backend for distributed rate limiting
   - Configurable limits and burst sizes

2. Token Validator (`security/token_validator.py`)
   - API key validation and rotation
   - Redis-based key storage
   - Automatic expiration handling

3. Audit Logger (`security/audit_logger.py`)
   - Structured event logging
   - Redis-based event storage
   - Report generation

4. System Check Updates (`scripts/system_check.sh`)
   - Security component verification
   - Environment variable checks
   - Service health monitoring

5. Security Tests (`tests/test_security.py`)
   - Unit tests for each component
   - Integration tests
   - Edge case handling

## Installation Steps

1. Create security directory:
```bash
mkdir -p security
```

2. Install dependencies:
```bash
pip install redis pydantic pytest
```

3. Copy security components:
```bash
cp security/rate_limiter.py security/
cp security/token_validator.py security/
cp security/audit_logger.py security/
```

4. Update system check script:
```bash
cp scripts/system_check.sh scripts/
chmod +x scripts/system_check.sh
```

5. Add security tests:
```bash
cp tests/test_security.py tests/
chmod +x tests/test_security.py
```

## Configuration

1. Update environment variables in `.env`:
```bash
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_api_key
CHROMA_API_KEY=your_api_key
```

2. Configure rate limits in `config/rate_limits.json`:
```json
{
    "default": {
        "requests_per_minute": 100,
        "burst_size": 50
    },
    "api": {
        "requests_per_minute": 1000,
        "burst_size": 200
    }
}
```

3. Configure token rotation in `config/tokens.json`:
```json
{
    "openai": {
        "rotation_days": 30,
        "max_usage": 1000000
    },
    "chroma": {
        "rotation_days": 90,
        "max_usage": 500000
    }
}
```

## Validation

1. Run system check:
```bash
./scripts/system_check.sh
```

2. Run security tests:
```bash
pytest tests/test_security.py -v
```

3. Verify Redis connection:
```bash
redis-cli ping
```

4. Check audit logs:
```bash
tail -f logs/audit.log
```

## Troubleshooting

### Rate Limiter Issues

1. Check Redis connection:
```bash
redis-cli ping
```

2. Verify rate limit configuration:
```bash
cat config/rate_limits.json
```

3. Check rate limit logs:
```bash
tail -f logs/rate_limiter.log
```

### Token Validation Issues

1. Verify API keys:
```bash
echo $OPENAI_API_KEY
echo $CHROMA_API_KEY
```

2. Check token storage:
```bash
redis-cli keys "token:*"
```

3. View token logs:
```bash
tail -f logs/token_validator.log
```

### Audit Logger Issues

1. Check log directory:
```bash
ls -l logs/
```

2. Verify Redis storage:
```bash
redis-cli keys "audit:*"
```

3. Test event logging:
```bash
python3 -c "from security.audit_logger import AuditLogger; logger = AuditLogger(); logger.log_event('test_event', 'test_user')"
```

## Rollback

If issues occur, you can rollback the security implementation:

1. Remove security components:
```bash
rm -rf security/
```

2. Restore original system check:
```bash
git checkout -- scripts/system_check.sh
```

3. Remove security tests:
```bash
rm tests/test_security.py
```

4. Clear Redis data:
```bash
redis-cli flushall
```

## Logging

The following log entries will be added to `bootstrap_status.log`:

```
[2024-03-14 10:00:00] Security components installed
[2024-03-14 10:00:01] Rate limiter configured
[2024-03-14 10:00:02] Token validator initialized
[2024-03-14 10:00:03] Audit logger started
[2024-03-14 10:00:04] Security tests passed
```

## Future Enhancements

1. JWT Authentication
   - Token generation and validation
   - Refresh token mechanism
   - Role-based access control

2. OAuth2 Integration
   - Support for major providers
   - Custom OAuth server
   - Scope-based permissions

3. Enhanced Monitoring
   - Real-time security metrics
   - Alert thresholds
   - Automated response

# Säkerhet och Autentisering Implementation

## 1. Implementera JWT Autentisering

### src/api/utils/auth.py
```python
"""Authentication utilities."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..models.user import UserInDB
from ..database import get_db
from sqlalchemy.orm import Session

# Konfiguration
SECRET_KEY = "YOUR_SECRET_KEY"  # I produktion, använd miljövariabel
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
    """Get password hash."""
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

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserInDB:
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
    
    user = db.query(UserInDB).filter(UserInDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

## 2. Implementera Säkerhetsheaders

### src/api/middleware/security.py
```python
"""Security middleware."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import os

def setup_security_middleware(app: FastAPI) -> None:
    """Setup security middleware."""
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Session
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SESSION_SECRET", "your-secret-key"),
        max_age=3600,  # 1 timme
    )

    # Trusted hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(","),
    )

    # Security headers
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.openai.com;"
        )
        return response
```

## 3. Implementera Rate Limiting

### src/api/middleware/rate_limit.py
```python
"""Rate limiting middleware."""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from typing import Dict, Tuple
import redis
import os

class RateLimiter:
    """Rate limiter class."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        self.window_size = 60  # 1 minut
        self.max_requests = 100  # Max antal requests per minut
    
    async def check_rate_limit(self, request: Request) -> None:
        """Check rate limit."""
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        # Hämta nuvarande antal requests
        current = self.redis_client.get(key)
        
        if current is None:
            # Första requesten
            self.redis_client.setex(key, self.window_size, 1)
        elif int(current) >= self.max_requests:
            # Överskriden gräns
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        else:
            # Öka räknare
            self.redis_client.incr(key)
```

## 4. Implementera Frontend Autentisering

### src/frontend/hooks/useAuth.ts
```typescript
import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from './useApi';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  token: string | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    return {
      isAuthenticated: !!token,
      user: user ? JSON.parse(user) : null,
      token,
    };
  });

  const { post } = useApi();
  const navigate = useNavigate();

  const login = useCallback(async (username: string, password: string) => {
    try {
      const response = await post('/auth/token', {
        username,
        password,
      });

      const { access_token, user } = response;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));

      setAuthState({
        isAuthenticated: true,
        user,
        token: access_token,
      });

      navigate('/');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }, [post, navigate]);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setAuthState({
      isAuthenticated: false,
      user: null,
      token: null,
    });
    navigate('/login');
  }, [navigate]);

  const register = useCallback(async (userData: any) => {
    try {
      const response = await post('/auth/register', userData);
      await login(userData.username, userData.password);
      return response;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }, [post, login]);

  return {
    ...authState,
    login,
    logout,
    register,
  };
};
```

## 5. Implementera Protected Routes

### src/frontend/components/PrivateRoute.tsx
```typescript
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface PrivateRouteProps {
  children: React.ReactNode;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};
```

## 6. Implementera Login-komponent

### src/frontend/components/Login.tsx
```typescript
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
} from '@mui/material';
import { useAuth } from '../hooks/useAuth';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await login(username, password);
      const from = (location.state as any)?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (err) {
      setError('Felaktigt användarnamn eller lösenord');
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" component="h1" gutterBottom>
            Logga in
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Användarnamn"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Lösenord"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
            />
            <Button
              type="submit"
              variant="contained"
              fullWidth
              sx={{ mt: 3 }}
            >
              Logga in
            </Button>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};
```

## 7. Uppdatera API Routes

### src/api/routes/auth.py
```python
"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import UserCreate, UserInDB
from ..utils.auth import (
    verify_password,
    create_access_token,
    get_password_hash,
    get_current_active_user,
)
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint."""
    user = db.query(UserInDB).filter(
        UserInDB.username == form_data.username
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
        }
    }

@router.post("/register", response_model=UserInDB)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register endpoint."""
    # Kontrollera om användaren redan finns
    db_user = db.query(UserInDB).filter(
        UserInDB.username == user.username
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Skapa ny användare
    hashed_password = get_password_hash(user.password)
    db_user = UserInDB(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/me", response_model=UserInDB)
async def read_users_me(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get current user."""
    return current_user
```

## 8. Verifiera Implementation

```bash
# Testa autentisering
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123", "email": "test@example.com"}'

curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test123"

# Testa skyddade endpoints
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 9. Nästa steg

Efter att ha implementerat säkerhet och autentisering, kör:

```bash
# Uppdatera miljövariabler
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "SESSION_SECRET=$(openssl rand -hex 32)" >> .env

# Starta om applikationen
docker-compose down
docker-compose up -d
```

Detta implementerar:
- JWT-baserad autentisering
- Säkerhetsheaders
- Rate limiting
- Skyddade routes
- Användarhantering
- Lösenordshashning
- Session-hantering
- CORS-konfiguration

Nästa steg är att implementera dokumentation och API-specifikation. 