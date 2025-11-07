# HomeServer - Complete Documentation

## Project Overview

**HomeServer** is a multi-purpose home server built with FastAPI, PostgreSQL, and Docker. It provides file storage with a web interface and real-time system monitoring dashboard, all running on a Mac Mini with external drive storage.

**Tech Stack:**
- **Backend**: Python 3.11, FastAPI, SQLAlchemy (async)
- **Database**: PostgreSQL 16
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Docker Compose
- **Storage**: External drive at `/Volumes/allDaStuffs/homeserver/`
- **Monitoring**: psutil for system metrics, WebSocket for real-time updates

---

## Project Structure

```
HomeServer/
├── .claude/
│   └── project.context.md          # Project context and preferences
├── alembic/
│   ├── versions/                   # Database migrations
│   │   └── 001_initial_schema.py
│   ├── env.py                      # Alembic environment config
│   └── script.py.mako             # Migration template
├── src/
│   ├── api/
│   │   ├── files.py               # File storage API endpoints
│   │   └── monitoring.py          # Monitoring API endpoints + WebSocket
│   ├── models/
│   │   ├── db_models.py           # SQLAlchemy database models
│   │   ├── files.py               # Pydantic models for file operations
│   │   └── monitoring.py          # Pydantic models for monitoring
│   ├── services/
│   │   ├── files/
│   │   │   ├── __init__.py
│   │   │   └── service.py         # File storage business logic
│   │   └── monitoring/
│   │       ├── __init__.py
│   │       └── service.py         # Monitoring business logic
│   ├── static/
│   │   ├── dashboard.html         # Real-time monitoring dashboard
│   │   └── files.html             # File manager interface
│   ├── config.py                  # Application configuration
│   ├── database.py                # Database session management
│   └── main.py                    # FastAPI application entry point
├── docker-compose.yml             # Docker services configuration
├── Dockerfile                     # Container image definition
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── alembic.ini                    # Alembic configuration
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── pyproject.toml                 # Python project metadata
```

---

## System Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                       │
│  (Dashboard: WebSocket updates every 2s)                    │
│  (File Manager: REST API for CRUD operations)               │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Files Router │  │ Monitoring   │  │ Static Files │     │
│  │              │  │ Router       │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘     │
│         │                  │                                 │
│         ▼                  ▼                                 │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ File Storage │  │ Monitoring   │                        │
│  │ Service      │  │ Service      │                        │
│  └──────┬───────┘  └──────┬───────┘                        │
└─────────┼──────────────────┼──────────────────────────────┘
          │                  │
          ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│   PostgreSQL    │  │     psutil      │
│   (metadata)    │  │ (system metrics)│
└─────────────────┘  └─────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  External Drive: /Volumes/allDaStuffs   │
│  ├── postgres/ (database files)         │
│  └── storage/ (uploaded files)          │
└─────────────────────────────────────────┘
```

### Docker Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Docker Host (Mac)                   │
│                                                        │
│  ┌─────────────────────────────────────────────────┐ │
│  │         homeserver (FastAPI container)          │ │
│  │  • Python 3.11                                  │ │
│  │  • Port: 8000 → 8000                            │ │
│  │  • Volume: external drive → /app/storage        │ │
│  │  • Depends on: postgres (with health check)    │ │
│  └─────────────────────┬───────────────────────────┘ │
│                        │                              │
│  ┌─────────────────────▼───────────────────────────┐ │
│  │      postgres (PostgreSQL 16 container)         │ │
│  │  • Port: 5432 (internal only)                   │ │
│  │  • Volume: external drive → /var/lib/postgresql│ │
│  │  • Health check: pg_isready                     │ │
│  └─────────────────────────────────────────────────┘ │
│                                                        │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  /Volumes/allDaStuffs/homeserver/        │
│  ├── postgres/ (persistent DB data)      │
│  └── storage/ (uploaded files)           │
└──────────────────────────────────────────┘
```

---

## Complete Code Explanations

### 1. Configuration Files

#### `docker-compose.yml`
```yaml
version: '3.8'  # Docker Compose file format version

services:
  # PostgreSQL database service
  postgres:
    image: postgres:16-alpine  # Lightweight PostgreSQL 16 image
    container_name: homeserver-postgres
    environment:
      # Database credentials (should use .env in production)
      POSTGRES_USER: homeserver
      POSTGRES_PASSWORD: homeserver_dev_password
      POSTGRES_DB: homeserver
    ports:
      # Map container port 5432 to host port 5432
      - "5432:5432"
    volumes:
      # Persist database data to external drive
      - /Volumes/allDaStuffs/homeserver/postgres:/var/lib/postgresql/data
    healthcheck:
      # Check if PostgreSQL is ready to accept connections
      test: ["CMD-SHELL", "pg_isready -U homeserver"]
      interval: 5s        # Check every 5 seconds
      timeout: 5s         # Timeout after 5 seconds
      retries: 5          # Retry 5 times before marking unhealthy

  # FastAPI application service
  homeserver:
    build: .  # Build from Dockerfile in current directory
    container_name: homeserver
    ports:
      # Map container port 8000 to host port 8000
      - "8000:8000"
    volumes:
      # Mount source code for development (hot reload)
      - ./src:/app/src
      # Mount external drive for file storage
      - /Volumes/allDaStuffs/homeserver/storage:/app/storage
    environment:
      # Override default database URL to use postgres service
      DATABASE_URL: postgresql+asyncpg://homeserver:homeserver_dev_password@postgres:5432/homeserver
    depends_on:
      postgres:
        # Wait for postgres to be healthy before starting
        condition: service_healthy
```

**Key Points:**
- Uses Docker Compose format 3.8
- Two services: postgres (database) and homeserver (application)
- External drive mounted at `/Volumes/allDaStuffs/homeserver/`
- Health check ensures postgres is ready before starting app
- All data persists on external drive (survives container restarts)

---

#### `Dockerfile`
```dockerfile
# Use official Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for Python packages
# gcc: C compiler for building Python extensions (psutil, asyncpg)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Points:**
- Based on Python 3.11 slim (smaller image size)
- Installs gcc for compiling Python C extensions
- Uses layer caching (requirements.txt copied before source code)
- Runs uvicorn ASGI server on all interfaces (0.0.0.0)

---

#### `requirements.txt`
```txt
# Web Framework
fastapi==0.115.5            # Modern async web framework
uvicorn[standard]==0.32.1   # ASGI server with WebSocket support
pydantic>=2.8.0             # Data validation using Python type hints
pydantic-settings==2.6.1    # Settings management
python-multipart==0.0.20    # Form/file upload support

# AWS (for future use)
boto3==1.35.36              # AWS SDK
aioboto3==13.2.0            # Async AWS SDK

# File Handling
aiofiles==24.1.0            # Async file operations

# Configuration
python-dotenv==1.0.1        # Load environment variables from .env

# HTTP Client
httpx==0.28.1               # Modern async HTTP client

# Database
sqlalchemy[asyncio]==2.0.36 # Async ORM for PostgreSQL
asyncpg==0.30.0             # Async PostgreSQL driver
alembic==1.14.0             # Database migrations

# System Monitoring
psutil==6.1.1               # Cross-platform system and process utilities
```

**Key Points:**
- FastAPI for web framework with async support
- SQLAlchemy with asyncio for async database operations
- psutil for system metrics (CPU, memory, disk)
- All versions pinned for reproducibility

---

#### `requirements-dev.txt`
```txt
# Testing
pytest==8.3.3               # Testing framework
pytest-asyncio==0.24.0      # Async test support
httpx==0.28.1               # For testing HTTP endpoints

# Code Quality
black==24.10.0              # Code formatter
ruff==0.7.4                 # Fast Python linter
mypy==1.13.0                # Static type checker
```

**Key Points:**
- Development tools not needed in production
- pytest for async testing
- black, ruff, mypy for code quality

---

### 2. Application Code

#### `src/config.py`
```python
"""Configuration management for HomeServer."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    This class automatically loads values from:
    1. Environment variables
    2. .env file
    3. Default values defined here
    """

    model_config = SettingsConfigDict(
        env_file=".env",                # Load from .env file
        env_file_encoding="utf-8",      # UTF-8 encoding
        case_sensitive=False            # Environment vars are case-insensitive
    )

    # Application settings
    app_name: str = "HomeServer"        # Application name
    app_version: str = "0.1.0"          # Semantic version
    debug: bool = False                 # Debug mode (enables hot reload)

    # Server settings
    host: str = "0.0.0.0"               # Listen on all network interfaces
    port: int = 8000                    # HTTP port

    # AWS settings (for future use)
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    dynamodb_table_prefix: str = "homeserver"

    # Security settings
    api_key: str = "dev-key-change-in-production"  # Should use secrets in prod

    # Storage settings
    storage_path: str = "/app/storage"  # Path inside container (mounted from external drive)

    # Database settings
    database_url: str = "postgresql+asyncpg://homeserver:homeserver_dev_password@postgres:5432/homeserver"


# Global settings instance (singleton pattern)
settings = Settings()
```

**Key Concepts:**
- **Pydantic BaseSettings**: Automatic loading from environment variables
- **Type hints**: Each setting has a type (str, bool, int)
- **Default values**: Fallback if not provided via environment
- **Singleton pattern**: One global `settings` instance used throughout app

---

#### `src/database.py`
```python
"""Database session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

# Create async database engine
# echo=False: Don't log SQL queries (set True for debugging)
# future=True: Use SQLAlchemy 2.0 style
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

# Create session factory
# expire_on_commit=False: Keep objects usable after commit
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection for database sessions.

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # db is automatically provided and cleaned up

    Yields:
        AsyncSession: Database session
    """
    # Create new session
    async with async_session_maker() as session:
        try:
            # Yield session to route handler
            yield session
            # Commit changes if no exception occurred
            await session.commit()
        except Exception:
            # Rollback on any exception
            await session.rollback()
            raise
        # Session automatically closed when exiting context
```

**Key Concepts:**
- **Async engine**: Non-blocking database operations
- **Session factory**: Creates new sessions for each request
- **Dependency injection**: FastAPI automatically calls get_db()
- **Context manager**: Automatic commit/rollback/cleanup
- **Generator pattern**: Yields session, then cleans up

---

#### `src/models/db_models.py`
```python
"""SQLAlchemy database models."""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY  # PostgreSQL-specific array type
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class FileMetadataDB(Base):
    """File metadata stored in PostgreSQL.

    Attributes:
        id: Unique file identifier (UUID)
        filename: Original filename
        content_type: MIME type (e.g., "text/plain")
        size: File size in bytes
        storage_path: Path on disk (relative to storage root)
        upload_date: When file was uploaded (auto-set)
        tags: List of tags for categorization
    """

    __tablename__ = "file_metadata"  # Table name in database

    # Primary key: UUID string
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # File information
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Timestamp (auto-set to current time on insert)
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # PostgreSQL function
        nullable=False,
    )

    # PostgreSQL array for tags
    # Uses ARRAY from sqlalchemy.dialects.postgresql (not generic ARRAY)
    tags: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list  # Empty list by default
    )
```

**Key Concepts:**
- **Mapped**: SQLAlchemy 2.0 type hints for columns
- **mapped_column**: Defines column properties
- **ARRAY(String)**: PostgreSQL-specific array type
- **func.now()**: Server-side default (PostgreSQL CURRENT_TIMESTAMP)
- **Relationships**: None yet, but could add foreign keys later

---

#### `src/models/files.py`
```python
"""Pydantic models for file operations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """File metadata response model.

    Used for API responses. Matches database model structure.
    """
    id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes", ge=0)
    upload_date: datetime = Field(..., description="Upload timestamp")
    tags: list[str] = Field(default_factory=list, description="File tags")


class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Uploaded filename")
    size: int = Field(..., description="File size in bytes")
    message: str = Field(default="File uploaded successfully")


class FileListResponse(BaseModel):
    """Response model for listing files."""
    files: list[FileMetadata] = Field(..., description="List of files")
    total: int = Field(..., description="Total file count")


class FileDeleteResponse(BaseModel):
    """Response model for file deletion."""
    id: str = Field(..., description="Deleted file ID")
    message: str = Field(default="File deleted successfully")
```

**Key Concepts:**
- **Pydantic BaseModel**: Data validation and serialization
- **Field**: Adds metadata (description, validation rules)
- **default_factory**: Function to create default values
- **Automatic JSON serialization**: Pydantic handles datetime conversion

---

#### `src/models/monitoring.py`
```python
"""Pydantic models for monitoring service."""

from pydantic import BaseModel, Field


class SystemMetrics(BaseModel):
    """System resource metrics.

    All values are rounded for readability.
    """
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_used_gb: float = Field(..., description="Memory used in GB")
    memory_total_gb: float = Field(..., description="Total memory in GB")
    disk_percent: float = Field(..., description="Disk usage percentage")
    disk_used_gb: float = Field(..., description="Disk used in GB")
    disk_total_gb: float = Field(..., description="Total disk in GB")
    disk_free_gb: float = Field(..., description="Disk free in GB")


class FileStorageStats(BaseModel):
    """File storage statistics from database."""
    total_files: int = Field(..., description="Total number of files")
    total_size_gb: float = Field(..., description="Total storage used in GB")
    storage_path: str = Field(..., description="Storage directory path")


class DashboardMetrics(BaseModel):
    """Combined metrics for dashboard.

    Includes system metrics, storage stats, and uptime.
    """
    system: SystemMetrics = Field(..., description="System resource metrics")
    storage: FileStorageStats = Field(..., description="File storage statistics")
    uptime_seconds: float = Field(..., description="Server uptime in seconds")
```

**Key Concepts:**
- **Nested models**: DashboardMetrics contains SystemMetrics and FileStorageStats
- **Field descriptions**: Auto-generate API documentation
- **JSON serialization**: Easy conversion to/from JSON

---

#### `src/services/files/service.py`
```python
"""File storage service implementation."""

import uuid
from pathlib import Path
from typing import Optional

import aiofiles  # Async file operations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.db_models import FileMetadataDB
from src.models.files import FileMetadata


class FileStorageService:
    """Service for managing file storage.

    Handles both file system operations and database metadata.
    """

    def __init__(self, storage_path: str = "./storage") -> None:
        """Initialize the file storage service.

        Args:
            storage_path: Directory where files are stored
        """
        self.storage_path = Path(storage_path)
        # Create directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        db: AsyncSession,  # Database session
        file_content: bytes,  # File data
        filename: str,  # Original filename
        content_type: str,  # MIME type
        tags: Optional[list[str]] = None,  # Optional tags
    ) -> FileMetadata:
        """Save a file to storage and database.

        Process:
        1. Generate unique ID
        2. Write file to disk
        3. Store metadata in database
        4. Return metadata

        Args:
            db: Database session
            file_content: File bytes
            filename: Original filename
            content_type: MIME type
            tags: Optional list of tags

        Returns:
            FileMetadata: Saved file metadata
        """
        # Generate unique ID
        file_id = str(uuid.uuid4())

        # Determine storage path (store in subdirectories by first 2 chars of UUID)
        # Example: abc123... -> storage/ab/abc123...
        subdir = self.storage_path / file_id[:2]
        subdir.mkdir(exist_ok=True)
        file_path = subdir / file_id

        # Write file to disk (async, doesn't block)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)

        # Create database record
        db_file = FileMetadataDB(
            id=file_id,
            filename=filename,
            content_type=content_type,
            size=len(file_content),
            storage_path=str(file_path.relative_to(self.storage_path)),
            tags=tags or [],
        )

        # Add to database
        db.add(db_file)
        await db.flush()  # Execute INSERT but don't commit yet

        # Convert to Pydantic model and return
        return FileMetadata(
            id=db_file.id,
            filename=db_file.filename,
            content_type=db_file.content_type,
            size=db_file.size,
            upload_date=db_file.upload_date,
            tags=db_file.tags,
        )

    async def list_files(
        self, db: AsyncSession, tag: Optional[str] = None
    ) -> list[FileMetadata]:
        """List all files, optionally filtered by tag.

        Args:
            db: Database session
            tag: Optional tag filter

        Returns:
            List of FileMetadata objects
        """
        # Build query
        query = select(FileMetadataDB)

        # Add tag filter if provided
        if tag:
            # Use PostgreSQL array operator .any() to check if tag exists in array
            query = query.where(FileMetadataDB.tags.any(tag))

        # Execute query
        result = await db.execute(query)
        files = result.scalars().all()

        # Convert to Pydantic models
        return [
            FileMetadata(
                id=f.id,
                filename=f.filename,
                content_type=f.content_type,
                size=f.size,
                upload_date=f.upload_date,
                tags=f.tags,
            )
            for f in files
        ]

    async def get_file(
        self, db: AsyncSession, file_id: str
    ) -> tuple[bytes, FileMetadata]:
        """Get a file's content and metadata.

        Args:
            db: Database session
            file_id: File identifier

        Returns:
            Tuple of (file_content, metadata)

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        # Get metadata from database
        result = await db.execute(
            select(FileMetadataDB).where(FileMetadataDB.id == file_id)
        )
        db_file = result.scalar_one_or_none()

        if not db_file:
            raise FileNotFoundError(f"File {file_id} not found")

        # Read file from disk
        file_path = self.storage_path / db_file.storage_path
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()

        # Convert metadata to Pydantic model
        metadata = FileMetadata(
            id=db_file.id,
            filename=db_file.filename,
            content_type=db_file.content_type,
            size=db_file.size,
            upload_date=db_file.upload_date,
            tags=db_file.tags,
        )

        return content, metadata

    async def get_metadata(
        self, db: AsyncSession, file_id: str
    ) -> Optional[FileMetadata]:
        """Get file metadata without reading file content.

        Args:
            db: Database session
            file_id: File identifier

        Returns:
            FileMetadata or None if not found
        """
        result = await db.execute(
            select(FileMetadataDB).where(FileMetadataDB.id == file_id)
        )
        db_file = result.scalar_one_or_none()

        if not db_file:
            return None

        return FileMetadata(
            id=db_file.id,
            filename=db_file.filename,
            content_type=db_file.content_type,
            size=db_file.size,
            upload_date=db_file.upload_date,
            tags=db_file.tags,
        )

    async def delete_file(self, db: AsyncSession, file_id: str) -> None:
        """Delete a file from storage and database.

        Args:
            db: Database session
            file_id: File identifier

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        # Get metadata
        result = await db.execute(
            select(FileMetadataDB).where(FileMetadataDB.id == file_id)
        )
        db_file = result.scalar_one_or_none()

        if not db_file:
            raise FileNotFoundError(f"File {file_id} not found")

        # Delete from disk
        file_path = self.storage_path / db_file.storage_path
        file_path.unlink(missing_ok=True)  # Delete file, ignore if missing

        # Delete from database
        await db.delete(db_file)
```

**Key Concepts:**
- **Async/await**: Non-blocking file and database operations
- **aiofiles**: Async file I/O
- **SQLAlchemy queries**: Using select() for type-safe queries
- **PostgreSQL array operators**: .any() for tag filtering
- **Service pattern**: Business logic separated from API routes
- **Error handling**: Raises FileNotFoundError for missing files

---

#### `src/services/monitoring/service.py`
```python
"""Monitoring service implementation."""

import time
from pathlib import Path

import psutil  # Cross-platform system utilities
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.db_models import FileMetadataDB
from src.models.monitoring import DashboardMetrics, FileStorageStats, SystemMetrics

# Track server start time (module-level variable)
SERVER_START_TIME = time.time()


class MonitoringService:
    """Service for collecting system and application metrics."""

    def __init__(self, storage_path: str = "./storage") -> None:
        """Initialize the monitoring service.

        Args:
            storage_path: Directory where files are stored
        """
        self.storage_path = Path(storage_path)

    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system resource metrics.

        Uses psutil to query:
        - CPU usage
        - Memory usage
        - Disk usage

        Returns:
            SystemMetrics object with current stats
        """
        # CPU usage (percentage over 0.1 second interval)
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024**3)  # Convert bytes to GB
        memory_total_gb = memory.total / (1024**3)

        # Disk usage for storage path
        disk = psutil.disk_usage(str(self.storage_path))
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        disk_free_gb = disk.free / (1024**3)

        return SystemMetrics(
            cpu_percent=round(cpu_percent, 1),
            memory_percent=round(memory.percent, 1),
            memory_used_gb=round(memory_used_gb, 2),
            memory_total_gb=round(memory_total_gb, 2),
            disk_percent=round(disk.percent, 1),
            disk_used_gb=round(disk_used_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            disk_free_gb=round(disk_free_gb, 2),
        )

    async def get_file_storage_stats(self, db: AsyncSession) -> FileStorageStats:
        """Get file storage statistics from database.

        Queries PostgreSQL for:
        - Total file count
        - Total storage used

        Args:
            db: Database session

        Returns:
            FileStorageStats object with storage statistics
        """
        # Count total files
        count_result = await db.execute(select(func.count(FileMetadataDB.id)))
        total_files = count_result.scalar() or 0

        # Sum total size
        size_result = await db.execute(select(func.sum(FileMetadataDB.size)))
        total_size_bytes = size_result.scalar() or 0
        total_size_gb = total_size_bytes / (1024**3)

        return FileStorageStats(
            total_files=total_files,
            total_size_gb=round(total_size_gb, 4),
            storage_path=str(self.storage_path),
        )

    async def get_dashboard_metrics(self, db: AsyncSession) -> DashboardMetrics:
        """Get all dashboard metrics.

        Combines:
        - System metrics (CPU, memory, disk)
        - Storage stats (file count, size)
        - Uptime

        Args:
            db: Database session

        Returns:
            DashboardMetrics object with all metrics
        """
        # Get system metrics
        system_metrics = await self.get_system_metrics()

        # Get storage stats
        storage_stats = await self.get_file_storage_stats(db)

        # Calculate uptime
        uptime = time.time() - SERVER_START_TIME

        return DashboardMetrics(
            system=system_metrics,
            storage=storage_stats,
            uptime_seconds=round(uptime, 1),
        )
```

**Key Concepts:**
- **psutil**: Cross-platform library for system metrics
- **PostgreSQL aggregates**: func.count(), func.sum()
- **Time tracking**: Module-level variable for server start time
- **Composed metrics**: DashboardMetrics combines multiple metric types

---

#### `src/api/files.py`
```python
"""API routes for file storage service."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.files import (
    FileDeleteResponse,
    FileListResponse,
    FileMetadata,
    FileUploadResponse,
)
from src.services.files import FileStorageService

# Create router with prefix and tags
router = APIRouter(prefix="/api/v1/files", tags=["files"])

# Initialize file storage service (singleton)
file_service = FileStorageService(storage_path=settings.storage_path)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),  # File upload field
    tags: Optional[str] = Form(None),  # Optional form field for tags
    db: AsyncSession = Depends(get_db),  # Inject database session
) -> FileUploadResponse:
    """Upload a file to the storage service.

    Accepts multipart/form-data with:
    - file: The file to upload
    - tags: Optional comma-separated tags

    Args:
        file: Uploaded file
        tags: Optional comma-separated tags
        db: Database session (injected)

    Returns:
        FileUploadResponse with file details
    """
    # Read file content into memory
    content = await file.read()

    # Parse comma-separated tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Save file using service
    metadata = await file_service.save_file(
        db=db,
        file_content=content,
        filename=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
        tags=tag_list,
    )

    return FileUploadResponse(
        id=metadata.id,
        filename=metadata.filename,
        size=metadata.size,
    )


@router.get("/list", response_model=FileListResponse)
async def list_files(
    tag: Optional[str] = None,  # Optional query parameter
    db: AsyncSession = Depends(get_db),
) -> FileListResponse:
    """List all files, optionally filtered by tag.

    Query parameters:
    - tag: Optional tag to filter by

    Args:
        tag: Optional tag to filter by
        db: Database session (injected)

    Returns:
        FileListResponse with list of files
    """
    files = await file_service.list_files(db=db, tag=tag)

    return FileListResponse(
        files=files,
        total=len(files),
    )


@router.get("/{file_id}/metadata", response_model=FileMetadata)
async def get_file_metadata(
    file_id: str,  # Path parameter
    db: AsyncSession = Depends(get_db),
) -> FileMetadata:
    """Get metadata for a specific file.

    Args:
        file_id: The unique file identifier
        db: Database session (injected)

    Returns:
        FileMetadata object

    Raises:
        HTTPException: 404 if file not found
    """
    metadata = await file_service.get_metadata(db=db, file_id=file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")

    return metadata


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Download a file.

    Returns file with proper Content-Disposition header
    to trigger browser download.

    Args:
        file_id: The unique file identifier
        db: Database session (injected)

    Returns:
        StreamingResponse with file content

    Raises:
        HTTPException: 404 if file not found
    """
    try:
        content, metadata = await file_service.get_file(db=db, file_id=file_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    # Create streaming response
    # iter([content]) creates iterator with single item
    return StreamingResponse(
        iter([content]),
        media_type=metadata.content_type,
        headers={
            # Tell browser to download (not display inline)
            "Content-Disposition": f'attachment; filename="{metadata.filename}"'
        },
    )


@router.delete("/{file_id}", response_model=FileDeleteResponse)
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileDeleteResponse:
    """Delete a file.

    Deletes both file from disk and metadata from database.

    Args:
        file_id: The unique file identifier
        db: Database session (injected)

    Returns:
        FileDeleteResponse confirming deletion

    Raises:
        HTTPException: 404 if file not found
    """
    try:
        await file_service.delete_file(db=db, file_id=file_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    return FileDeleteResponse(id=file_id)
```

**Key Concepts:**
- **APIRouter**: Groups related endpoints with common prefix
- **Dependency injection**: Depends(get_db) automatically provides session
- **Path parameters**: {file_id} in route path
- **Query parameters**: Optional[str] = None in function signature
- **Form data**: Form() for multipart/form-data
- **File uploads**: UploadFile handles file uploads
- **StreamingResponse**: Efficient for large files
- **HTTPException**: FastAPI exception handling

---

#### `src/api/monitoring.py`
```python
"""API routes for monitoring service."""

import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.monitoring import DashboardMetrics, FileStorageStats, SystemMetrics
from src.services.monitoring import MonitoringService

# Create router
router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

# Initialize monitoring service (singleton)
monitoring_service = MonitoringService(storage_path=settings.storage_path)


@router.get("/system", response_model=SystemMetrics)
async def get_system_metrics() -> SystemMetrics:
    """Get current system metrics.

    Returns CPU, memory, and disk usage.

    Returns:
        SystemMetrics with CPU, memory, and disk usage
    """
    return await monitoring_service.get_system_metrics()


@router.get("/storage", response_model=FileStorageStats)
async def get_storage_stats(db: AsyncSession = Depends(get_db)) -> FileStorageStats:
    """Get file storage statistics.

    Queries database for file count and total size.

    Args:
        db: Database session (injected)

    Returns:
        FileStorageStats with file count and total size
    """
    return await monitoring_service.get_file_storage_stats(db)


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
) -> DashboardMetrics:
    """Get all dashboard metrics.

    Combines system metrics, storage stats, and uptime.

    Args:
        db: Database session (injected)

    Returns:
        DashboardMetrics with system and storage stats
    """
    return await monitoring_service.get_dashboard_metrics(db)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time metrics updates.

    Sends dashboard metrics every 2 seconds.

    Protocol:
    1. Client connects
    2. Server accepts connection
    3. Server sends metrics JSON every 2 seconds
    4. Loop continues until client disconnects

    Args:
        websocket: WebSocket connection
    """
    # Accept WebSocket connection
    await websocket.accept()

    try:
        # Get database session for this WebSocket connection
        # async for gets one session from the generator
        async for db in get_db():
            # Inner loop: send metrics repeatedly
            while True:
                try:
                    # Get latest metrics
                    metrics = await monitoring_service.get_dashboard_metrics(db)

                    # Send to client as JSON
                    # model_dump(mode="json") converts to JSON-serializable dict
                    await websocket.send_json(metrics.model_dump(mode="json"))

                    # Wait 2 seconds before next update
                    await asyncio.sleep(2)

                except WebSocketDisconnect:
                    # Client disconnected normally
                    break
                except Exception as e:
                    # Other error (network issue, etc.)
                    print(f"WebSocket error: {e}")
                    break

            # Break outer loop when websocket disconnects
            break

    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        # Always try to close connection gracefully
        try:
            await websocket.close()
        except:
            pass  # Ignore errors when closing
```

**Key Concepts:**
- **WebSocket**: Two-way persistent connection
- **Real-time updates**: Push data to client without polling
- **asyncio.sleep()**: Non-blocking delay
- **WebSocketDisconnect**: Exception for clean disconnect
- **Nested loops**: Outer for session, inner for metrics
- **Error handling**: Graceful handling of disconnects and errors

---

#### `src/main.py`
```python
"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.files import router as files_router
from src.api.monitoring import router as monitoring_router
from src.config import settings

# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-purpose home server with media, files, automation, and AI",
)

# Include API routers
# Files API: /api/v1/files/*
app.include_router(files_router)
# Monitoring API: /api/v1/monitoring/*
app.include_router(monitoring_router)

# Mount static files for dashboard
# Static files: /static/*
app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - basic info about the server.

    Returns:
        Dict with welcome message, version, and status
    """
    return {
        "message": "Welcome to HomeServer",
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint for monitoring.

    Used by Docker health checks and load balancers.

    Returns:
        JSONResponse with 200 status and health info
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
        },
    )


@app.get("/api/v1/info")
async def api_info() -> dict[str, str | dict[str, str]]:
    """API information endpoint.

    Lists available services and their status.

    Returns:
        Dict with API version and service status
    """
    return {
        "api_version": "v1",
        "services": {
            "media": "planned",
            "files": "active",
            "automation": "planned",
            "ai": "planned",
            "monitoring": "active",
            "web": "planned",
        },
    }


# Run with uvicorn when executed directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",  # Import path to app
        host=settings.host,  # Listen on all interfaces
        port=settings.port,  # Port 8000
        reload=settings.debug,  # Hot reload in debug mode
    )
```

**Key Concepts:**
- **FastAPI app**: Main application instance
- **Router inclusion**: Modular organization of endpoints
- **Static file mounting**: Serve HTML/CSS/JS files
- **Health check**: Standard endpoint for monitoring
- **Type hints**: Return types for better IDE support
- **Uvicorn**: ASGI server for FastAPI

---

### 3. Frontend Code

#### `src/static/dashboard.html`
This is a complete HTML file with embedded CSS and JavaScript. I'll break it down section by section.

**HTML Structure (lines 1-143):**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HomeServer Dashboard</title>
    <!-- Embedded CSS styles (lines 7-134) -->
</head>
<body>
    <!-- Connection status indicator (fixed top-right) -->
    <div class="connection-status" id="connectionStatus">
        <span class="status-indicator"></span>
        <span id="statusText">Connecting...</span>
    </div>

    <div class="container">
        <h1>HomeServer Dashboard</h1>

        <!-- Grid layout for metric cards -->
        <div class="grid">
            <!-- System Resources Card -->
            <div class="card">
                <h2>System Resources</h2>
                <!-- CPU, Memory, Disk with progress bars -->
            </div>

            <!-- File Storage Card -->
            <div class="card">
                <h2>File Storage</h2>
                <!-- Total files, size, path -->
            </div>

            <!-- Server Info Card -->
            <div class="card">
                <h2>Server Information</h2>
                <!-- Uptime, disk free, total memory -->
            </div>
        </div>
    </div>

    <!-- JavaScript (lines 217-301) -->
</body>
</html>
```

**CSS Styling (lines 7-134):**
```css
/* Dark theme colors */
body {
    background: #0a0a0a;  /* Near-black background */
    color: #e0e0e0;        /* Light gray text */
}

/* Cards with subtle borders */
.card {
    background: #1a1a1a;   /* Dark gray background */
    border: 1px solid #2a2a2a;  /* Subtle border */
    border-radius: 12px;   /* Rounded corners */
}

/* Purple gradient for headings */
h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;  /* Gradient text effect */
}

/* Progress bars */
.progress-bar {
    background: #2a2a2a;  /* Dark track */
}

.progress-fill {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);  /* Purple gradient */
}

.progress-fill.warning {
    background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);  /* Red gradient for >80% */
}

/* Pulsing status indicator */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.status-indicator {
    animation: pulse 2s infinite;  /* Pulse every 2 seconds */
}
```

**JavaScript - WebSocket Connection (lines 218-250):**
```javascript
// Determine WebSocket protocol based on page protocol
// http: → ws:, https: → wss:
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/api/v1/monitoring/ws`;
let ws;
let reconnectTimeout;

function connect() {
    // Create WebSocket connection
    ws = new WebSocket(wsUrl);

    // Connection opened
    ws.onopen = () => {
        console.log('WebSocket connected');
        // Update UI to show connected status
        document.getElementById('connectionStatus').className = 'connection-status connected';
        document.getElementById('statusText').textContent = 'Connected';
    };

    // Message received from server
    ws.onmessage = (event) => {
        // Parse JSON data
        const data = JSON.parse(event.data);
        // Update dashboard with new data
        updateDashboard(data);
    };

    // Connection closed
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        // Update UI to show disconnected status
        document.getElementById('connectionStatus').className = 'connection-status disconnected';
        document.getElementById('statusText').textContent = 'Disconnected';

        // Attempt to reconnect after 3 seconds
        reconnectTimeout = setTimeout(connect, 3000);
    };

    // Error occurred
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}
```

**JavaScript - Update Dashboard (lines 252-279):**
```javascript
function updateDashboard(data) {
    // Destructure data object
    const { system, storage, uptime_seconds } = data;

    // Update CPU display
    document.getElementById('cpuValue').textContent = `${system.cpu_percent}%`;
    document.getElementById('cpuProgress').style.width = `${system.cpu_percent}%`;
    // Change color to red if > 80%
    document.getElementById('cpuProgress').className =
        system.cpu_percent > 80 ? 'progress-fill warning' : 'progress-fill';

    // Update Memory display
    document.getElementById('memoryValue').textContent =
        `${system.memory_percent}% (${system.memory_used_gb}/${system.memory_total_gb} GB)`;
    document.getElementById('memoryProgress').style.width = `${system.memory_percent}%`;
    document.getElementById('memoryProgress').className =
        system.memory_percent > 80 ? 'progress-fill warning' : 'progress-fill';

    // Update Disk display
    document.getElementById('diskValue').textContent =
        `${system.disk_percent}% (${system.disk_used_gb}/${system.disk_total_gb} GB)`;
    document.getElementById('diskProgress').style.width = `${system.disk_percent}%`;
    document.getElementById('diskProgress').className =
        system.disk_percent > 80 ? 'progress-fill warning' : 'progress-fill';

    // Update Storage stats
    document.getElementById('totalFiles').textContent = storage.total_files.toLocaleString();
    document.getElementById('totalSize').textContent = `${storage.total_size_gb} GB`;
    document.getElementById('storagePath').textContent = storage.storage_path;

    // Update Server info
    document.getElementById('uptime').textContent = formatUptime(uptime_seconds);
    document.getElementById('diskFree').textContent = `${system.disk_free_gb} GB`;
    document.getElementById('totalMemory').textContent = `${system.memory_total_gb} GB`;
}
```

**JavaScript - Format Uptime (lines 281-291):**
```javascript
function formatUptime(seconds) {
    // Calculate days, hours, minutes, seconds
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    // Format based on magnitude
    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m ${secs}s`;
    if (minutes > 0) return `${minutes}m ${secs}s`;
    return `${secs}s`;
}
```

**JavaScript - Initialization and Cleanup (lines 293-301):**
```javascript
// Start connection when page loads
connect();

// Cleanup when page unloads (user navigates away)
window.addEventListener('beforeunload', () => {
    if (ws) ws.close();  // Close WebSocket
    if (reconnectTimeout) clearTimeout(reconnectTimeout);  // Cancel reconnect timer
});
```

**Key Concepts:**
- **Real-time updates**: WebSocket pushes data every 2 seconds
- **Auto-reconnect**: Attempts to reconnect after disconnect
- **Responsive design**: Grid layout adapts to screen size
- **Visual feedback**: Progress bars change color when usage > 80%
- **No frameworks**: Pure JavaScript, no dependencies

---

#### `src/static/files.html`
Similar structure to dashboard.html, but for file management.

**Key JavaScript Functions:**

**Load Files (lines 286-335):**
```javascript
async function loadFiles() {
    try {
        // Fetch file list from API
        const response = await fetch(`${API_BASE}/list`);
        const data = await response.json();

        const filesList = document.getElementById('filesList');
        const fileCount = document.getElementById('fileCount');

        // Update count
        fileCount.textContent = data.total;

        // Handle empty state
        if (data.total === 0) {
            filesList.innerHTML = `<div class="empty-state">...</div>`;
            return;
        }

        // Render file items
        filesList.innerHTML = data.files.map(file => `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-name">${file.filename}</div>
                    <div class="file-meta">
                        ${formatSize(file.size)} • ${formatDate(file.upload_date)}
                    </div>
                    ${file.tags && file.tags.length > 0 ? `
                        <div class="file-tags">
                            ${file.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
                <div class="file-actions">
                    <button onclick="downloadFile('${file.id}', '${file.filename}')">Download</button>
                    <button class="danger" onclick="deleteFile('${file.id}', '${file.filename}')">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load files:', error);
        showStatus('Failed to load files', 'error');
    }
}
```

**Upload File (lines 337-380):**
```javascript
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();  // Prevent form submission

    const fileInput = document.getElementById('fileInput');
    const tagsInput = document.getElementById('tagsInput');
    const uploadBtn = document.getElementById('uploadBtn');

    // Validate file selected
    if (!fileInput.files.length) {
        showStatus('Please select a file', 'error');
        return;
    }

    // Create FormData for multipart upload
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (tagsInput.value.trim()) {
        formData.append('tags', tagsInput.value.trim());
    }

    // Disable button during upload
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';

    try {
        // POST to upload endpoint
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        showStatus(`${data.filename} uploaded successfully!`, 'success');

        // Reset form
        fileInput.value = '';
        tagsInput.value = '';

        // Reload file list
        await loadFiles();
    } catch (error) {
        console.error('Upload failed:', error);
        showStatus('Upload failed', 'error');
    } finally {
        // Re-enable button
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload';
    }
});
```

**Download File (lines 382-391):**
```javascript
async function downloadFile(fileId, filename) {
    try {
        // Trigger browser download by navigating to download URL
        window.location.href = `${API_BASE}/${fileId}/download`;
        showStatus(`Downloading ${filename}...`, 'success');
    } catch (error) {
        console.error('Download failed:', error);
        showStatus('Download failed', 'error');
    }
}
```

**Delete File (lines 393-414):**
```javascript
async function deleteFile(fileId, filename) {
    // Confirm deletion
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
        return;
    }

    try {
        // DELETE request to API
        const response = await fetch(`${API_BASE}/${fileId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Delete failed');
        }

        showStatus(`${filename} deleted`, 'success');
        // Reload file list
        await loadFiles();
    } catch (error) {
        console.error('Delete failed:', error);
        showStatus('Delete failed', 'error');
    }
}
```

**Key Concepts:**
- **Fetch API**: Modern way to make HTTP requests
- **FormData**: For multipart file uploads
- **Async/await**: Clean handling of promises
- **Template literals**: Easy string interpolation and HTML generation
- **Event delegation**: onclick handlers in dynamically generated HTML
- **User feedback**: Status messages, loading states, confirmations

---

### 4. Database Migrations

#### `alembic/versions/001_initial_schema.py`
```python
"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-11-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tables."""
    # Create file_metadata table
    op.create_table(
        'file_metadata',
        # Columns
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column(
            'upload_date',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),  # PostgreSQL function
            nullable=False
        ),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False),
        # Primary key
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop tables."""
    op.drop_table('file_metadata')
```

**Key Concepts:**
- **Migration**: Version-controlled database schema changes
- **upgrade()**: Apply changes (create table)
- **downgrade()**: Revert changes (drop table)
- **Revision identifiers**: Track migration order
- **PostgreSQL-specific**: Uses ARRAY type

---

## Complete Session Timeline

### Phase 1: Project Setup and Configuration
1. **Created project context** (`.claude/project.context.md`)
2. **Set up directory structure**
3. **Created requirements files**
4. **Wrote Dockerfile and docker-compose.yml**
5. **Fixed dependency conflicts** (boto3 version)
6. **Added python-multipart** for file uploads

### Phase 2: File Storage Service
1. **Created Pydantic models** (files.py, db_models.py)
2. **Implemented file storage service** (in-memory initially)
3. **Created API endpoints** (upload, download, list, delete)
4. **Tested file operations**

### Phase 3: PostgreSQL Integration
1. **Added PostgreSQL to docker-compose.yml**
2. **Created database models** (SQLAlchemy)
3. **Set up session management** (database.py)
4. **Created Alembic migrations**
5. **Fixed ARRAY type issues** (PostgreSQL-specific)
6. **Fixed array filter issues** (.any() instead of .contains())
7. **Migrated file service to use PostgreSQL**
8. **Tested data persistence**

### Phase 4: Monitoring Dashboard
1. **Added psutil dependency**
2. **Created monitoring models** (monitoring.py)
3. **Implemented monitoring service** (system metrics + storage stats)
4. **Created monitoring API endpoints**
5. **Added WebSocket endpoint** for real-time updates
6. **Created dashboard.html** (dark theme, real-time updates)
7. **Mounted static files** in FastAPI
8. **Rebuilt containers** with new dependencies
9. **Tested dashboard** (locally and on network)

### Phase 5: File Manager UI
1. **Created files.html** (upload, browse, download, delete)
2. **Tested file manager** (upload, download, delete operations)
3. **Verified network access**

### Phase 6: Documentation
1. **Created comprehensive documentation**
2. **Line-by-line code explanations**
3. **Architecture diagrams**
4. **Complete timeline**

---

## Key Achievements

### ✓ Complete File Storage System
- Upload files via web interface or API
- Download files with proper Content-Disposition
- Delete files (disk + database)
- Tag-based organization
- PostgreSQL metadata storage
- External drive persistence

### ✓ Real-time Monitoring Dashboard
- CPU, memory, disk usage
- File storage statistics
- Server uptime
- WebSocket updates every 2 seconds
- Auto-reconnect on disconnect
- Warning colors for high usage

### ✓ Network Accessibility
- Accessible on local network (192.168.0.40:8000)
- Dark theme UI
- Responsive design
- No external dependencies (vanilla JS)

### ✓ Production-Ready Infrastructure
- Docker containerization
- PostgreSQL persistence
- External drive storage
- Health checks
- Database migrations
- Async all the way (FastAPI + SQLAlchemy + aiofiles)

---

## File Manifest

### Configuration Files
- `.claude/project.context.md` - Project context and preferences
- `docker-compose.yml` - Docker services configuration
- `Dockerfile` - Container image definition
- `requirements.txt` - Python dependencies
- `requirements-dev.txt` - Development dependencies
- `alembic.ini` - Alembic configuration
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules
- `pyproject.toml` - Python project metadata

### Application Code
- `src/main.py` - FastAPI application entry point
- `src/config.py` - Application configuration
- `src/database.py` - Database session management
- `src/models/db_models.py` - SQLAlchemy database models
- `src/models/files.py` - Pydantic models for file operations
- `src/models/monitoring.py` - Pydantic models for monitoring
- `src/api/files.py` - File storage API endpoints
- `src/api/monitoring.py` - Monitoring API endpoints + WebSocket
- `src/services/files/service.py` - File storage business logic
- `src/services/monitoring/service.py` - Monitoring business logic

### Frontend Code
- `src/static/dashboard.html` - Real-time monitoring dashboard
- `src/static/files.html` - File manager interface

### Database Migrations
- `alembic/versions/001_initial_schema.py` - Initial database schema
- `alembic/env.py` - Alembic environment configuration

### External Drive Storage
- `/Volumes/allDaStuffs/homeserver/postgres/` - PostgreSQL data
- `/Volumes/allDaStuffs/homeserver/storage/` - Uploaded files

---

## Next Steps (Planned but Not Implemented)

1. **Twingate Integration** - External access from outside network
2. **Media Streaming** - Plex/Jellyfin-style media server
3. **Home Automation** - IoT device control
4. **AI Assistant** - LLM-powered chatbot
5. **Web Hosting** - Host static sites
6. **Authentication** - User accounts and permissions
7. **File Browser** - Browse existing drives (not just uploaded files)

---

## Technical Highlights

### Async Everything
- FastAPI (async web framework)
- SQLAlchemy with asyncio (async database)
- asyncpg (async PostgreSQL driver)
- aiofiles (async file operations)
- WebSocket (async real-time updates)

### Type Safety
- Python type hints throughout
- Pydantic for data validation
- SQLAlchemy 2.0 Mapped types
- mypy for static type checking

### Best Practices
- Dependency injection
- Service layer pattern
- Database migrations (Alembic)
- Environment-based configuration
- Docker containerization
- Health checks
- Error handling
- Code formatting (Black, Ruff)

---

## Access URLs

### Local Access
- Dashboard: `http://localhost:8000/static/dashboard.html`
- File Manager: `http://localhost:8000/static/files.html`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Network Access
- Dashboard: `http://192.168.0.40:8000/static/dashboard.html`
- File Manager: `http://192.168.0.40:8000/static/files.html`
- API Docs: `http://192.168.0.40:8000/docs`

---

## Environment

- **Platform**: macOS (Darwin 25.0.0)
- **Hardware**: Mac Mini with external SSD
- **External Drive**: `/Volumes/allDaStuffs`
- **Python**: 3.11 (via Docker)
- **PostgreSQL**: 16 (Alpine Linux)
- **Docker**: Docker Desktop for Mac

---

## Summary

You now have a fully functional home server with:
- **File storage** with web interface and REST API
- **Real-time monitoring** dashboard with WebSocket updates
- **PostgreSQL** persistence on external drive
- **Docker** containerization for easy deployment
- **Network accessibility** from any device on your local network

All code is production-ready with proper error handling, type safety, and async operations throughout. The system is designed to be extended with additional services (media, automation, AI) as needed.
