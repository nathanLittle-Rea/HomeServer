# Authentication Implementation Summary

## Overview
This document summarizes the JWT-based authentication system implementation for the HomeServer project.

**Implementation Date:** 2025-11-07
**Status:** Backend Complete - Ready for Migration & Testing
**Authentication Type:** JWT (JSON Web Tokens) with Bearer Authentication

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Dependencies Added](#dependencies-added)
3. [Database Models](#database-models)
4. [Pydantic Models](#pydantic-models)
5. [Security Utilities](#security-utilities)
6. [Authentication Service](#authentication-service)
7. [API Endpoints](#api-endpoints)
8. [Dependency Injection](#dependency-injection)
9. [Configuration](#configuration)
10. [Database Migration Setup](#database-migration-setup)
11. [Next Steps](#next-steps)

---

## Architecture Overview

The authentication system follows a clean architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  src/api/auth.py - Authentication endpoints                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Dependency Injection                       │
│  src/dependencies.py - Auth middleware & user validation     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Service Layer                             │
│  src/services/auth/service.py - Business logic               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Utilities Layer                            │
│  src/utils/security.py - Password hashing & JWT              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Database Layer                             │
│  src/models/db_models.py - SQLAlchemy models                 │
│  PostgreSQL - User data storage                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Dependencies Added

### File: `requirements.txt`

```python
# Authentication
python-jose[cryptography]==3.3.0  # JWT token creation and validation
passlib[bcrypt]==1.7.4            # Password hashing with bcrypt
python-multipart==0.0.20          # Form data parsing (already present)
```

### Key Libraries:
- **python-jose**: JWT encoding/decoding with cryptographic support
- **passlib**: Secure password hashing using bcrypt algorithm
- **bcrypt**: Industry-standard password hashing (via passlib)

---

## Database Models

### File: `src/models/db_models.py`

#### UserDB Model

```python
class UserDB(Base):
    """Database model for users."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
```

#### Fields:
- **id**: Auto-incrementing primary key
- **username**: Unique username (3-50 chars), indexed for fast lookup
- **email**: Unique email address, indexed for fast lookup
- **hashed_password**: Bcrypt-hashed password (never stored in plaintext)
- **is_active**: Account active status (for soft account disabling)
- **is_superuser**: Admin privileges flag
- **created_at**: Account creation timestamp (UTC)
- **updated_at**: Last modification timestamp (UTC, auto-updated)

---

## Pydantic Models

### File: `src/models/auth.py`

#### UserBase
Base model with common user fields:
```python
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
```

#### UserCreate
Used for user registration:
```python
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
```

#### User
Public user representation (without password):
```python
class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

#### UserUpdate
Optional fields for updating user profile:
```python
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
```

#### Token
JWT token response:
```python
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

#### LoginRequest
Login credentials:
```python
class LoginRequest(BaseModel):
    username: str
    password: str
```

#### RegisterResponse
Combined registration response (user + token):
```python
class RegisterResponse(BaseModel):
    user: User
    access_token: str
    token_type: str = "bearer"
```

---

## Security Utilities

### File: `src/utils/security.py`

#### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)
```

**Security Features:**
- Bcrypt algorithm (adaptive hashing, resistant to rainbow tables)
- Automatic salt generation
- Configurable work factor for future-proofing

#### JWT Token Management

```python
from jose import jwt, JWTError
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
```

**JWT Features:**
- HS256 algorithm (HMAC with SHA-256)
- Configurable expiration (default: 24 hours)
- Automatic expiration validation
- Payload contains: `{"sub": user_id, "exp": expiration_timestamp}`

---

## Authentication Service

### File: `src/services/auth/service.py`

```python
class AuthService:
    """Service for user authentication and management."""

    async def create_user(self, db: AsyncSession, user_create: UserCreate) -> User:
        """Create a new user account."""
        # Check if username already exists
        result = await db.execute(select(UserDB).where(UserDB.username == user_create.username))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already registered")

        # Check if email already exists
        result = await db.execute(select(UserDB).where(UserDB.email == user_create.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password and create user
        hashed_password = get_password_hash(user_create.password)
        db_user = UserDB(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return User.model_validate(db_user)

    async def authenticate_user(
        self, db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        """Authenticate a user by username and password."""
        result = await db.execute(select(UserDB).where(UserDB.username == username))
        user = result.scalar_one_or_none()

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None

        return User.model_validate(user)

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        result = await db.execute(select(UserDB).where(UserDB.id == user_id))
        user = result.scalar_one_or_none()
        return User.model_validate(user) if user else None

    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await db.execute(select(UserDB).where(UserDB.username == username))
        user = result.scalar_one_or_none()
        return User.model_validate(user) if user else None

    async def update_user(
        self, db: AsyncSession, user_id: int, user_update: UserUpdate
    ) -> Optional[User]:
        """Update a user's information."""
        result = await db.execute(select(UserDB).where(UserDB.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Update fields if provided
        if user_update.username is not None:
            # Check uniqueness
            result = await db.execute(
                select(UserDB).where(
                    UserDB.username == user_update.username,
                    UserDB.id != user_id
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = user_update.username

        if user_update.email is not None:
            # Check uniqueness
            result = await db.execute(
                select(UserDB).where(
                    UserDB.email == user_update.email,
                    UserDB.id != user_id
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already taken")
            user.email = user_update.email

        if user_update.password is not None:
            user.hashed_password = get_password_hash(user_update.password)

        await db.commit()
        await db.refresh(user)

        return User.model_validate(user)

    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        """Delete a user account."""
        result = await db.execute(select(UserDB).where(UserDB.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return False

        await db.delete(user)
        await db.commit()
        return True
```

---

## API Endpoints

### File: `src/api/auth.py`

All endpoints are mounted at `/api/v1/auth/` prefix.

#### POST /register
Create a new user account and receive a JWT token.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-11-07T12:00:00Z",
    "updated_at": "2025-11-07T12:00:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /login
Authenticate with username and password to receive a JWT token.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET /me
Get current authenticated user's information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-07T12:00:00Z",
  "updated_at": "2025-11-07T12:00:00Z"
}
```

#### PATCH /me
Update current authenticated user's information.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body (all fields optional):**
```json
{
  "username": "newusername",
  "email": "newemail@example.com",
  "password": "newpassword123"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "newusername",
  "email": "newemail@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-07T12:00:00Z",
  "updated_at": "2025-11-07T12:05:00Z"
}
```

#### DELETE /me
Delete current authenticated user's account.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204 No Content)**

#### GET /users/{user_id}
Get any user's information (superuser only).

**Headers:**
```
Authorization: Bearer <superuser_token>
```

**Response (200 OK):**
```json
{
  "id": 2,
  "username": "otheruser",
  "email": "other@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-07T11:00:00Z",
  "updated_at": "2025-11-07T11:00:00Z"
}
```

---

## Dependency Injection

### File: `src/dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get the current authenticated user."""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure the current user is a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

### Usage in Protected Endpoints:
```python
@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello {current_user.username}"}

@router.get("/admin-only")
async def admin_route(
    current_user: User = Depends(get_current_superuser)
):
    return {"message": "Admin access granted"}
```

---

## Configuration

### File: `src/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    # Security
    api_key: str = "dev-key-change-in-production"
    secret_key: str = "change-this-to-random-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Environment Variables:
Create a `.env` file with:
```env
SECRET_KEY=<generate-a-secure-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Security Note:** Generate a secure secret key using:
```bash
openssl rand -hex 32
```

---

## Database Migration Setup

### Alembic Configuration

#### File: `alembic.ini`
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://homeserver:homeserver_dev_password@postgres:5432/homeserver

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### File: `alembic/env.py`
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Add the project directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import your models
from src.database import Base
from src.models.db_models import FileMetadataDB, UserDB

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## Next Steps

### 1. Create and Apply Database Migration

```bash
# Create migration for users table
docker-compose exec homeserver alembic revision --autogenerate -m "Add users table"

# Apply migration
docker-compose exec homeserver alembic upgrade head

# Verify migration
docker-compose exec postgres psql -U homeserver -d homeserver -c "\d users"
```

### 2. Test Authentication Flow

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123"
  }'

# Get current user (use token from login response)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <token>"
```

### 3. Create Login UI

Create simple HTML pages for:
- User registration form
- Login form
- User profile page
- Password change form

### 4. Protect Existing Endpoints

Add authentication to existing endpoints:
```python
@router.get("/api/v1/files")
async def list_files(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Only authenticated users can list files
    pass
```

### 5. Update API Documentation

Add authentication examples to `API_GUIDE.md`:
- How to register
- How to login
- How to use bearer tokens
- Token expiration and refresh

### 6. Security Enhancements

Future improvements:
- [ ] Add refresh token mechanism
- [ ] Implement email verification
- [ ] Add password reset flow
- [ ] Rate limiting on auth endpoints
- [ ] Add audit logging for auth events
- [ ] Implement 2FA (Two-Factor Authentication)
- [ ] Add OAuth2 providers (Google, GitHub)
- [ ] Session management and token revocation

---

## Testing Checklist

- [ ] User registration with valid data
- [ ] User registration with duplicate username
- [ ] User registration with duplicate email
- [ ] User registration with weak password
- [ ] Login with correct credentials
- [ ] Login with incorrect password
- [ ] Login with non-existent user
- [ ] Access protected endpoint without token
- [ ] Access protected endpoint with invalid token
- [ ] Access protected endpoint with expired token
- [ ] Access protected endpoint with valid token
- [ ] Update user profile
- [ ] Update to duplicate username/email (should fail)
- [ ] Delete user account
- [ ] Superuser-only endpoint access by regular user (should fail)
- [ ] Superuser-only endpoint access by superuser (should succeed)

---

## Security Best Practices Implemented

1. **Password Security:**
   - Bcrypt hashing (adaptive algorithm)
   - Minimum password length (8 characters)
   - Never store plaintext passwords
   - Salt automatically generated per password

2. **Token Security:**
   - JWT with HMAC-SHA256 signature
   - Token expiration (24 hours default)
   - Secret key stored in environment variables
   - Token validation on every protected request

3. **Database Security:**
   - Indexed username and email for performance
   - Unique constraints on username and email
   - SQL injection protection (SQLAlchemy ORM)
   - Parameterized queries

4. **API Security:**
   - HTTP Bearer authentication
   - Proper HTTP status codes (401, 403, etc.)
   - Input validation with Pydantic
   - Email format validation

5. **Account Management:**
   - Soft delete capability (is_active flag)
   - Role-based access control (is_superuser)
   - Unique constraint enforcement
   - Timestamp tracking (created_at, updated_at)

---

## File Structure

```
HomeServer/
├── requirements.txt                      # Added auth dependencies
├── alembic.ini                          # Alembic configuration
├── alembic/
│   ├── env.py                           # Migration environment setup
│   └── versions/                        # Migration files (to be created)
├── src/
│   ├── config.py                        # Added JWT settings
│   ├── main.py                          # Added auth router
│   ├── dependencies.py                  # NEW: Auth dependencies
│   ├── api/
│   │   └── auth.py                      # NEW: Auth endpoints
│   ├── models/
│   │   ├── db_models.py                 # Added UserDB model
│   │   └── auth.py                      # NEW: Auth Pydantic models
│   ├── services/
│   │   └── auth/
│   │       └── service.py               # NEW: Auth service
│   └── utils/
│       └── security.py                  # NEW: Password & JWT utilities
└── AUTHENTICATION_IMPLEMENTATION.md     # This file
```

---

## Implementation Summary

**Files Created:** 5
- `src/api/auth.py`
- `src/models/auth.py`
- `src/services/auth/service.py`
- `src/dependencies.py`
- `src/utils/security.py`

**Files Modified:** 4
- `requirements.txt`
- `src/config.py`
- `src/main.py`
- `src/models/db_models.py`

**Lines of Code:** ~650 lines total

**Time Investment:** Backend implementation complete

**Status:** Ready for database migration and testing

---

## Contact & Support

For questions or issues with the authentication system:
1. Review this documentation
2. Check the API_GUIDE.md for endpoint usage
3. Verify environment configuration in `.env`
4. Ensure database migrations are applied

---

*Document generated on 2025-11-07*
*Last updated: 2025-11-07*
