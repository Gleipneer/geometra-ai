# API Endpoints Implementation

## 1. Skapa API-struktur

```bash
mkdir -p src/api/{routes,models,services,utils}
```

## 2. Implementera Basmodeller

### src/api/models/base.py
```python
"""Base models for API."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")

class ErrorResponse(BaseResponse):
    """Error response model."""
    error_code: str = Field(..., description="Error code")
    error_details: Optional[dict] = Field(None, description="Error details")
```

### src/api/models/user.py
```python
"""User models."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """User update model."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)

class UserInDB(UserBase):
    """User database model."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
```

### src/api/models/project.py
```python
"""Project models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ProjectBase(BaseModel):
    """Base project model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ProjectCreate(ProjectBase):
    """Project creation model."""
    pass

class ProjectUpdate(BaseModel):
    """Project update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ProjectInDB(ProjectBase):
    """Project database model."""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
```

## 3. Implementera Routes

### src/api/routes/users.py
```python
"""User routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.user import UserCreate, UserUpdate, UserInDB
from ..services.user_service import UserService
from ..utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserInDB)
async def create_user(user: UserCreate):
    """Create new user."""
    return await UserService.create_user(user)

@router.get("/me", response_model=UserInDB)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """Get current user info."""
    return current_user

@router.put("/me", response_model=UserInDB)
async def update_user(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update current user."""
    return await UserService.update_user(current_user.id, user_update)

@router.delete("/me")
async def delete_user(current_user: UserInDB = Depends(get_current_user)):
    """Delete current user."""
    await UserService.delete_user(current_user.id)
    return {"message": "User deleted successfully"}
```

### src/api/routes/projects.py
```python
"""Project routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.project import ProjectCreate, ProjectUpdate, ProjectInDB
from ..models.user import UserInDB
from ..services.project_service import ProjectService
from ..utils.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectInDB)
async def create_project(
    project: ProjectCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create new project."""
    return await ProjectService.create_project(project, current_user.id)

@router.get("/", response_model=List[ProjectInDB])
async def list_projects(current_user: UserInDB = Depends(get_current_user)):
    """List user's projects."""
    return await ProjectService.list_user_projects(current_user.id)

@router.get("/{project_id}", response_model=ProjectInDB)
async def get_project(
    project_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get project by ID."""
    return await ProjectService.get_project(project_id, current_user.id)

@router.put("/{project_id}", response_model=ProjectInDB)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update project."""
    return await ProjectService.update_project(
        project_id,
        project_update,
        current_user.id
    )

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete project."""
    await ProjectService.delete_project(project_id, current_user.id)
    return {"message": "Project deleted successfully"}
```

## 4. Implementera Services

### src/api/services/user_service.py
```python
"""User service."""
from typing import Optional
from ..models.user import UserCreate, UserUpdate, UserInDB
from ..utils.db import get_db
from ..utils.security import get_password_hash

class UserService:
    """User service class."""
    
    @staticmethod
    async def create_user(user: UserCreate) -> UserInDB:
        """Create new user."""
        db = await get_db()
        hashed_password = get_password_hash(user.password)
        user_dict = user.dict()
        user_dict["password"] = hashed_password
        user_id = await db.users.insert_one(user_dict)
        return await UserService.get_user_by_id(str(user_id.inserted_id))
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        db = await get_db()
        user = await db.users.find_one({"_id": user_id})
        return UserInDB(**user) if user else None
    
    @staticmethod
    async def update_user(user_id: str, user_update: UserUpdate) -> UserInDB:
        """Update user."""
        db = await get_db()
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])
        await db.users.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        return await UserService.get_user_by_id(user_id)
    
    @staticmethod
    async def delete_user(user_id: str) -> None:
        """Delete user."""
        db = await get_db()
        await db.users.delete_one({"_id": user_id})
```

### src/api/services/project_service.py
```python
"""Project service."""
from typing import List, Optional
from ..models.project import ProjectCreate, ProjectUpdate, ProjectInDB
from ..utils.db import get_db

class ProjectService:
    """Project service class."""
    
    @staticmethod
    async def create_project(project: ProjectCreate, owner_id: str) -> ProjectInDB:
        """Create new project."""
        db = await get_db()
        project_dict = project.dict()
        project_dict["owner_id"] = owner_id
        project_id = await db.projects.insert_one(project_dict)
        return await ProjectService.get_project(str(project_id.inserted_id), owner_id)
    
    @staticmethod
    async def get_project(project_id: str, owner_id: str) -> Optional[ProjectInDB]:
        """Get project by ID."""
        db = await get_db()
        project = await db.projects.find_one({
            "_id": project_id,
            "owner_id": owner_id
        })
        return ProjectInDB(**project) if project else None
    
    @staticmethod
    async def list_user_projects(owner_id: str) -> List[ProjectInDB]:
        """List user's projects."""
        db = await get_db()
        projects = await db.projects.find({"owner_id": owner_id}).to_list(None)
        return [ProjectInDB(**project) for project in projects]
    
    @staticmethod
    async def update_project(
        project_id: str,
        project_update: ProjectUpdate,
        owner_id: str
    ) -> ProjectInDB:
        """Update project."""
        db = await get_db()
        update_data = project_update.dict(exclude_unset=True)
        await db.projects.update_one(
            {"_id": project_id, "owner_id": owner_id},
            {"$set": update_data}
        )
        return await ProjectService.get_project(project_id, owner_id)
    
    @staticmethod
    async def delete_project(project_id: str, owner_id: str) -> None:
        """Delete project."""
        db = await get_db()
        await db.projects.delete_one({
            "_id": project_id,
            "owner_id": owner_id
        })
```

## 5. Uppdatera main.py

```python
"""Main FastAPI application for Geometra AI system."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import users, projects

app = FastAPI(
    title="Geometra AI API",
    description="API for Geometra AI system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(projects.router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/version")
async def get_version():
    """Get API version."""
    return {"version": "1.0.0"}
```

## 6. Skapa Utils

### src/api/utils/auth.py
```python
"""Authentication utilities."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from ..models.user import UserInDB
from ..services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        "your-secret-key",  # In production, use environment variable
        algorithm="HS256"
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Get current user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            "your-secret-key",  # In production, use environment variable
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await UserService.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
```

### src/api/utils/db.py
```python
"""Database utilities."""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

_client: Optional[AsyncIOMotorClient] = None

async def get_db():
    """Get database connection."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    return _client.geometra_db
```

### src/api/utils/security.py
```python
"""Security utilities."""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Get password hash."""
    return pwd_context.hash(password)
```

## 7. Installera Nödvändiga Paket

```bash
pip install motor pydantic[email] python-jose[cryptography] passlib[bcrypt]
```

## 8. Verifiera Implementation

```bash
# Starta servern
uvicorn src.api.main:app --reload

# Testa endpoints med curl eller Postman
curl http://localhost:8000/health
curl http://localhost:8000/version
```

## 9. Nästa steg

Efter att ha implementerat dessa endpoints, kör:

```bash
# Kör API-tester
pytest tests/unit/api/

# Generera API-dokumentation
python scripts/generate_api_docs.py
```

Detta implementerar grundläggande API-endpoints för användar- och projekthantering, med stöd för:
- Användarregistrering och autentisering
- Projekt-CRUD-operationer
- Säkerhetsfunktioner
- Databasintegration
- API-dokumentation

Nästa steg är att implementera AI-relaterade endpoints och integration med minneshanteringen. 