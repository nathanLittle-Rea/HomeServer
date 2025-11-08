# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

HomeServer is a multi-purpose home server application providing file storage, file browsing, system monitoring, and user authentication. Built with FastAPI and PostgreSQL, running in Docker containers with persistent storage on an external drive (`/Volumes/allDaStuffs`).

**Current Status**: Authentication system complete. File storage, file browser, and real-time monitoring active. Planning to add Gitea (Git server), Vaultwarden (password manager), and Nginx reverse proxy.

---

## Essential Commands

### Complete Startup Procedure

**Step 1: Pre-Flight Checks**

```bash
# 1. Verify external drive is mounted (CRITICAL - containers won't start without it)
ls /Volumes/allDaStuffs
# Should show: homeserver/ and other drive contents

# If not mounted:
# - Check if drive is connected physically
# - Mount via Finder or Disk Utility
# - On macOS: ls /Volumes/ to see all mounted drives

# 2. Navigate to project directory
cd /Users/nathanlittle-rea/projects/HomeServer

# 3. Verify docker-compose.yml exists
ls docker-compose.yml

# 4. Check Docker Desktop is running
docker ps
# Should not error. If it does, start Docker Desktop app.
```

**Step 2: Start All Services**

```bash
# Option A: Start in foreground (see logs in terminal)
docker-compose up

# Option B: Start in background (detached mode) - RECOMMENDED
docker-compose up -d

# Option C: Rebuild images and start (after dependency changes)
docker-compose up --build -d
```

**Step 3: Verify Services Started**

```bash
# Check container status (should show "Up" and "healthy")
docker-compose ps
# Expected output:
# NAME                  STATUS
# homeserver            Up X minutes (healthy)
# homeserver-postgres   Up X minutes (healthy)

# Check logs for errors
docker-compose logs --tail=50 homeserver
docker-compose logs --tail=50 postgres

# Verify health endpoints
curl http://localhost:8000/health
# Should return: {"status":"healthy","app":"HomeServer","version":"0.1.0"}

# Check API info
curl http://localhost:8000/api/v1/info
# Should return service status

# Test database connection (from inside homeserver container)
docker-compose exec homeserver python -c "from src.database import engine; import asyncio; asyncio.run(engine.connect())"
# Should complete without errors
```

**Step 4: Access Services**

```bash
# Web interfaces (open in browser):
# - Main dashboard: http://localhost:8000/
# - Login page: http://localhost:8000/login.html
# - Register: http://localhost:8000/register.html
# - Dashboard: http://localhost:8000/dashboard.html
# - File Manager: http://localhost:8000/files.html
# - File Browser: http://localhost:8000/browser.html
# - API Docs (Swagger): http://localhost:8000/docs
# - API Docs (ReDoc): http://localhost:8000/redoc

# Database access:
docker-compose exec postgres psql -U homeserver -d homeserver
```

---

### Complete Shutdown Procedure

**Step 1: Graceful Shutdown (Recommended)**

```bash
# Stop all containers gracefully (allows DB to flush writes)
docker-compose down

# This will:
# 1. Stop homeserver container (FastAPI shuts down gracefully)
# 2. Stop postgres container (PostgreSQL checkpoints and closes)
# 3. Remove containers (but preserve volumes/data)
# 4. Remove the homeserver-network

# Data is PRESERVED in:
# - /Volumes/allDaStuffs/homeserver/postgres/ (database files)
# - /Volumes/allDaStuffs/homeserver/storage/ (uploaded files)
```

**Step 2: Verify Shutdown**

```bash
# Check no containers are running
docker-compose ps
# Should show empty or "Exit" status

# Verify with Docker
docker ps -a --filter "name=homeserver"
# Should show containers in "Exited" state or not listed

# Check logs for clean shutdown
docker-compose logs --tail=20 homeserver
# Should see: "Application shutdown complete"
```

**Step 3: Complete Cleanup (Optional - USE WITH CAUTION)**

```bash
# Remove stopped containers (safe - volumes preserved)
docker-compose down

# Remove containers AND images (forces rebuild on next start)
docker-compose down --rmi all

# DANGER: Remove volumes (DELETES ALL DATA)
# Only use if you want to completely reset the database
docker-compose down -v
# ⚠️ WARNING: This deletes the Docker-managed volumes
# ⚠️ External drive data (/Volumes/allDaStuffs) is NOT deleted
# ⚠️ But any volume-only data would be lost

# DANGER: Nuclear option (remove everything)
docker-compose down -v --rmi all
```

---

### Restart Procedures

**Quick Restart (After Code Changes)**

```bash
# Source code is hot-reloaded automatically (./src mounted as volume)
# But sometimes you need to restart:

# Restart just the homeserver container
docker-compose restart homeserver

# Check logs to confirm restart
docker-compose logs -f homeserver
# Should see: "Application startup complete"
```

**Full Restart (After Configuration Changes)**

```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost:8000/health
```

**Rebuild and Restart (After Dependency Changes)**

```bash
# If you modified:
# - requirements.txt
# - Dockerfile
# - alembic.ini (copied into container)

# Stop, rebuild, start
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or in one command:
docker-compose up --build -d
```

---

### Docker Operations (Day-to-Day)

```bash
# View live logs
docker-compose logs -f homeserver
docker-compose logs -f postgres

# View last N lines of logs
docker-compose logs --tail=100 homeserver

# Follow logs from both containers
docker-compose logs -f

# Access container shell
docker-compose exec homeserver sh

# Access PostgreSQL CLI
docker-compose exec postgres psql -U homeserver -d homeserver

# Run a command in container
docker-compose exec homeserver python -c "print('Hello from container')"

# Copy files from container to host
docker-compose cp homeserver:/app/some-file.txt ./local-copy.txt

# Copy files from host to container
docker-compose cp ./local-file.txt homeserver:/app/destination.txt
```

### Database Migrations (Alembic)

```bash
# Create new migration (auto-generate from model changes)
docker-compose exec homeserver alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec homeserver alembic upgrade head

# Rollback one migration
docker-compose exec homeserver alembic downgrade -1

# View migration history
docker-compose exec homeserver alembic history

# Database backup
docker-compose exec -T postgres pg_dump -U homeserver homeserver > backup.sql

# Database restore
docker-compose exec -T postgres psql -U homeserver -d homeserver < backup.sql
```

### Code Quality (when developing outside Docker)

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy src/

# Run all checks
black . && ruff check . && mypy src/

# Run tests (when test suite is implemented)
pytest
pytest --cov=src tests/
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Use authenticated endpoint
curl http://localhost:8000/api/v1/files/list \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Architecture

### High-Level Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    External Users                           │
│                (Browser/API Clients)                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              HomeServer Container (Port 8000)               │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │         FastAPI Application (Uvicorn)              │   │
│  │  ┌──────────────────────────────────────────────┐ │   │
│  │  │  API Layer (src/api/)                        │ │   │
│  │  │  - auth.py: JWT authentication (6 endpoints) │ │   │
│  │  │  - files.py: File storage (5 endpoints)      │ │   │
│  │  │  - browser.py: File browsing (4 endpoints)   │ │   │
│  │  │  - monitoring.py: System metrics (4 + WS)    │ │   │
│  │  └──────────────┬───────────────────────────────┘ │   │
│  │                 │                                  │   │
│  │  ┌──────────────▼───────────────────────────────┐ │   │
│  │  │  Service Layer (src/services/)               │ │   │
│  │  │  - AuthService: User management + JWT        │ │   │
│  │  │  - FileStorageService: File CRUD             │ │   │
│  │  │  - FileBrowserService: FS navigation         │ │   │
│  │  │  - MonitoringService: System metrics         │ │   │
│  │  └──────────────┬───────────────────────────────┘ │   │
│  │                 │                                  │   │
│  │  ┌──────────────▼───────────────────────────────┐ │   │
│  │  │  Data Layer                                  │ │   │
│  │  │  - models/db_models.py: SQLAlchemy ORM       │ │   │
│  │  │  - models/*.py: Pydantic schemas             │ │   │
│  │  │  - database.py: Async session factory        │ │   │
│  │  └──────────────┬───────────────────────────────┘ │   │
│  └─────────────────┼──────────────────────────────────┘   │
└────────────────────┼──────────────────────────────────────┘
                     │ asyncpg (async PostgreSQL driver)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         PostgreSQL Container (Port 5432)                    │
│  Database: homeserver                                       │
│  Tables: users, files, alembic_version                     │
└────────────────────┬────────────────────────────────────────┘
                     │ Volume mount
                     ▼
┌─────────────────────────────────────────────────────────────┐
│    External Drive: /Volumes/allDaStuffs/homeserver/        │
│    ├─ postgres/ (database files)                           │
│    └─ storage/ (uploaded files)                            │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

**1. Async-First Architecture**
- All I/O operations use `async/await`
- AsyncSession for database operations
- ASGI server (Uvicorn) for concurrent request handling
- Async file I/O where applicable

**2. Dependency Injection (FastAPI)**
```python
# Authentication is injected via dependencies
@router.get("/files/list")
async def list_files(
    current_user: User = Depends(get_current_active_user),  # Auto-validates JWT
    db: AsyncSession = Depends(get_db),                      # Auto-manages session
) -> FileListResponse:
    # current_user is guaranteed to be authenticated and active
    # db session is automatically created and cleaned up
```

**3. Service Layer Pattern**
- API routes (thin): Handle HTTP concerns only
- Services (business logic): Implement core functionality
- Models (data): Define schemas and validation
```
API Route → Service → Database/Filesystem
```

**4. JWT Authentication Flow**
```
1. User registers/logs in → Receive JWT token (24h expiration)
2. Client stores token in localStorage
3. All protected endpoints require: Authorization: Bearer <token>
4. FastAPI dependency extracts token → decodes → validates → loads user
5. If invalid/expired: 401 Unauthorized
6. If user inactive: 403 Forbidden
```

**5. WebSocket Authentication**
- WebSockets cannot send custom headers
- Token passed as query parameter: `ws://host/ws?token=...`
- Server validates token before accepting connection
- Used for real-time monitoring dashboard updates (every 2s)

---

## Critical Implementation Details

### Database Models vs Pydantic Models

**Two separate model systems** (do not confuse):

```python
# src/models/db_models.py - SQLAlchemy ORM (database)
class UserDB(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    # ... database-level fields

# src/models/auth.py - Pydantic (API validation/serialization)
class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    # ... API-level fields (no hashed_password!)
    model_config = ConfigDict(from_attributes=True)  # Allows ORM conversion
```

**Conversion**: `User.model_validate(user_db)` converts ORM → Pydantic

### File Storage Architecture

**Files are stored in TWO places**:
1. **Physical files**: `/Volumes/allDaStuffs/homeserver/storage/{UUID}`
   - Actual file content
   - Named by UUID (no filename collisions)
   - Mapped into container at `/app/storage/`

2. **Metadata**: PostgreSQL `files` table
   - `id` (UUID), `filename`, `content_type`, `size`, `tags[]`, `upload_date`
   - Links to physical file via `file_path`

**Critical**: When deleting files, delete BOTH database record AND physical file.

### External Drive Dependency

**The external drive MUST be mounted** at `/Volumes/allDaStuffs` before starting containers.

```bash
# Verify before starting
ls /Volumes/allDaStuffs  # Should list drive contents

# If not mounted, containers will fail with volume mount errors
```

**Volume Mappings**:
- `./src` → `/app/src` (hot reload)
- `/Volumes/allDaStuffs/homeserver/storage` → `/app/storage` (file storage)
- `/Volumes/allDaStuffs/homeserver/postgres` → `/var/lib/postgresql/data` (database)
- `/Volumes/allDaStuffs` → `/Volumes/allDaStuffs:ro` (read-only browsing)

### Authentication Middleware

**All protected endpoints use this pattern**:
```python
from src.dependencies import get_current_active_user
from src.models.auth import User

@router.get("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # current_user is already authenticated
    # No need to check token manually
```

**Dependency chain**:
```
get_current_active_user
  → get_current_user
    → security (HTTPBearer) extracts token
    → decode_access_token validates JWT
    → AuthService.get_user_by_id loads from DB
  → checks user.is_active
```

### Password Security

```python
# NEVER store plaintext passwords
# ALWAYS use passlib + bcrypt

from src.utils.security import get_password_hash, verify_password

# Hashing (on registration)
hashed = get_password_hash("user_password")  # Returns bcrypt hash

# Verification (on login)
is_valid = verify_password("user_password", hashed)  # Constant-time comparison
```

**Critical versions** (compatibility issue):
- `bcrypt==4.1.3` (NOT 5.0.0 - incompatible with passlib 1.7.4)
- `passlib==1.7.4` (without [bcrypt] extra to avoid version conflicts)

---

## File Organization

```
src/
├── api/                    # FastAPI route handlers (thin controllers)
│   ├── auth.py            # 6 auth endpoints (register, login, profile)
│   ├── files.py           # 5 file endpoints (upload, list, download, delete)
│   ├── browser.py         # 4 browser endpoints (list dirs, download)
│   └── monitoring.py      # 4 monitoring + WebSocket
│
├── models/                 # Data models
│   ├── db_models.py       # SQLAlchemy ORM models (UserDB, FileDB)
│   ├── auth.py            # Pydantic schemas (User, Token, LoginRequest)
│   ├── files.py           # Pydantic schemas (FileMetadata, FileUploadResponse)
│   ├── browser.py         # Pydantic schemas (DirectoryListing, FileSystemItem)
│   └── monitoring.py      # Pydantic schemas (SystemMetrics, DashboardMetrics)
│
├── services/              # Business logic (where the work happens)
│   ├── auth/
│   │   └── service.py     # AuthService (user CRUD, authentication)
│   ├── files.py           # FileStorageService (file operations + DB)
│   ├── browser.py         # FileBrowserService (filesystem navigation)
│   └── monitoring.py      # MonitoringService (psutil metrics)
│
├── utils/                 # Shared utilities
│   └── security.py        # Password hashing, JWT encode/decode
│
├── static/                # Frontend HTML/CSS/JS
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # Real-time monitoring (WebSocket)
│   ├── files.html         # File upload/download manager
│   └── browser.html       # File browser UI
│
├── config.py              # Settings (Pydantic BaseSettings)
├── database.py            # Database session factory (async)
├── dependencies.py        # FastAPI dependencies (auth, DB)
└── main.py                # FastAPI app entry point

alembic/
└── versions/              # Database migration files
    └── 27699c07a691_add_users_table.py
```

### Understanding the Flow

**Example: File Upload**
1. `POST /api/v1/files/upload` → `src/api/files.py:upload_file()`
2. Dependency injection validates JWT → loads `current_user`
3. Route calls `FileStorageService.save_file()`
4. Service layer:
   - Generates UUID for file
   - Writes file to `/app/storage/{uuid}` (external drive)
   - Inserts metadata into `files` table (database)
5. Returns `FileUploadResponse` (Pydantic model)
6. FastAPI serializes to JSON → client receives response

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### Files Table
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    size BIGINT NOT NULL,
    file_path TEXT NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    tags VARCHAR[] DEFAULT ARRAY[]::VARCHAR[]
);
```

---

## Environment Configuration

**Required variables** (`.env` file):

```bash
# Database (container name "postgres" resolves via Docker network)
DATABASE_URL=postgresql+asyncpg://homeserver:homeserver_dev_password@postgres:5432/homeserver

# Security (CHANGE IN PRODUCTION - use: openssl rand -hex 32)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# Application
APP_NAME=HomeServer
APP_VERSION=0.1.0
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Storage (container path)
STORAGE_PATH=/app/storage
```

**Production security**:
```bash
# Generate secure secret key
export SECRET_KEY=$(openssl rand -hex 32)

# Use strong database password
# Enable HTTPS (add Nginx reverse proxy)
# Firewall PostgreSQL port (internal only)
# Add rate limiting
```

---

## Testing Strategy

### Manual Testing (Current)

**API endpoints tested via curl/browser**:
- Health check: `http://localhost:8000/health`
- Interactive docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:8000/login.html`

### Automated Testing (Planned)

```bash
# Run tests
pytest

# With coverage
pytest --cov=src tests/

# Test structure (when implemented)
tests/
├── test_api/           # API endpoint tests
│   ├── test_auth.py
│   ├── test_files.py
│   └── test_monitoring.py
├── test_services/      # Service layer tests
└── conftest.py         # Shared fixtures
```

**Key test fixtures needed**:
- `async_client`: TestClient for API calls
- `test_db`: Temporary database for each test
- `test_user`: Authenticated user fixture
- `test_token`: Valid JWT token

---

## Startup Troubleshooting

### Common Startup Issues

**Issue 1: Containers Won't Start - Volume Mount Error**

```bash
# Symptom:
Error response from daemon: invalid mount config for type "bind": bind source path does not exist: /Volumes/allDaStuffs

# Cause: External drive not mounted

# Solution:
# 1. Check if drive is connected
ls /Volumes/
# Should show: allDaStuffs

# 2. If not listed, check Finder or reconnect drive
# 3. Verify the exact path
ls /Volumes/allDaStuffs/homeserver

# 4. Try starting again
docker-compose up -d
```

**Issue 2: PostgreSQL Container Unhealthy**

```bash
# Symptom:
docker-compose ps shows: homeserver-postgres (unhealthy)

# Check logs:
docker-compose logs postgres

# Common causes:
# A) Permission issues on external drive
ls -la /Volumes/allDaStuffs/homeserver/postgres/
# Should be readable/writable

# B) Corrupt database files
# Nuclear option: Remove postgres data and recreate
docker-compose down
mv /Volumes/allDaStuffs/homeserver/postgres /Volumes/allDaStuffs/homeserver/postgres.backup
docker-compose up -d
# WARNING: This loses all database data

# C) Port already in use
lsof -i :5432
# If another postgres is running, stop it or change port in docker-compose.yml
```

**Issue 3: HomeServer Container Exits Immediately**

```bash
# Check logs for errors
docker-compose logs homeserver

# Common causes:

# A) Database connection failed
# Look for: "could not connect to server: Connection refused"
# Solution: Ensure postgres container is healthy first
docker-compose ps  # postgres should be "healthy"

# B) Missing dependencies
# Look for: "ModuleNotFoundError: No module named 'X'"
# Solution: Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# C) Alembic migration failed
# Look for: "alembic.util.exc.CommandError"
# Solution: Check database migrations
docker-compose exec homeserver alembic current
docker-compose exec homeserver alembic upgrade head
```

**Issue 4: Port 8000 Already in Use**

```bash
# Symptom:
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use

# Find what's using the port:
lsof -i :8000

# Solution A: Stop the other process
kill -9 <PID>

# Solution B: Change HomeServer port
# Edit docker-compose.yml:
ports:
  - "8001:8000"  # Changed from 8000:8000
# Then access at http://localhost:8001
```

**Issue 5: Docker Desktop Not Running**

```bash
# Symptom:
Cannot connect to the Docker daemon. Is the docker daemon running?

# Solution:
# 1. Open Docker Desktop app (macOS)
# 2. Wait for it to start (whale icon in menu bar should be steady)
# 3. Verify:
docker ps
# Should not error

# 4. Try again:
docker-compose up -d
```

**Issue 6: Database Connection Timeout**

```bash
# Symptom in logs:
asyncpg.exceptions.ConnectionDoesNotExistError

# Solution:
# 1. Ensure postgres is fully healthy before starting homeserver
docker-compose up -d postgres
sleep 10  # Wait for postgres to be ready
docker-compose up -d homeserver

# 2. Check database URL in .env
cat .env | grep DATABASE_URL
# Should be: postgresql+asyncpg://homeserver:homeserver_dev_password@postgres:5432/homeserver
#                                                           ^^^^^^^
# Use "postgres" (container name), NOT "localhost"
```

**Issue 7: WebSocket Connection Fails in Browser**

```bash
# Symptom: Dashboard shows "Disconnected", browser console shows WebSocket error

# Check:
# 1. Is container running?
docker-compose ps

# 2. Can you access HTTP endpoints?
curl http://localhost:8000/health

# 3. Check browser console (F12) for WebSocket URL
# Should be: ws://localhost:8000/api/v1/monitoring/ws?token=...

# 4. Verify token is present
# Open browser DevTools → Application → Local Storage → access_token

# 5. Test WebSocket endpoint
# Try logging in again to get fresh token
```

**Issue 8: Hot Reload Not Working**

```bash
# Symptom: Code changes not reflected in running container

# Verify volume mount:
docker-compose exec homeserver ls -la /app/src
# Should show your source files with recent timestamps

# Check docker-compose.yml has:
volumes:
  - ./src:/app/src

# Force restart:
docker-compose restart homeserver

# Check logs for reload:
docker-compose logs -f homeserver
# Should see: "Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)"
```

---

## Common Gotchas

### 1. Bcrypt Version Conflicts
**Problem**: `bcrypt==5.0.0` breaks passlib
**Solution**: Pin `bcrypt==4.1.3` in requirements.txt

### 2. Database Connection String
**Inside container**: Use `postgres` as hostname (Docker network DNS)
**From host**: Use `localhost` or `127.0.0.1`

### 3. Alembic Must Be in Container
**Wrong**: Running `alembic` on host (won't find PostgreSQL)
**Right**: `docker-compose exec homeserver alembic upgrade head`

### 4. External Drive Not Mounted
**Symptom**: Container fails to start with volume mount error
**Check**: `ls /Volumes/allDaStuffs` before `docker-compose up`

### 5. WebSocket Authentication
**Wrong**: Setting `Authorization` header (not supported in browsers)
**Right**: Query parameter: `ws://host/ws?token=...`

### 6. File Deletion
**Must delete both**:
1. Database record: `DELETE FROM files WHERE id = ?`
2. Physical file: `os.remove(file_path)`

### 7. Hot Reload Not Working
**Cause**: Code changes in `src/` should auto-reload
**Check**: Volume mount exists in docker-compose.yml: `./src:/app/src`
**Restart**: `docker-compose restart homeserver`

---

## API Endpoint Summary

**Total: 20 endpoints + 1 WebSocket**

### Public (No Auth)
- `GET /health` - Health check
- `GET /api/v1/info` - Service status
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Get JWT token

### Protected (Bearer Token Required)
- `GET /api/v1/auth/me` - Current user info
- `PATCH /api/v1/auth/me` - Update profile
- `DELETE /api/v1/auth/me` - Delete account
- `POST /api/v1/files/upload` - Upload file
- `GET /api/v1/files/list` - List files (optional tag filter)
- `GET /api/v1/files/{id}/metadata` - File metadata
- `GET /api/v1/files/{id}/download` - Download file
- `DELETE /api/v1/files/{id}` - Delete file
- `GET /api/v1/browser/roots` - Allowed root paths
- `GET /api/v1/browser/list` - Directory listing
- `GET /api/v1/browser/info` - File/dir metadata
- `GET /api/v1/browser/download` - Download from filesystem
- `GET /api/v1/monitoring/system` - System metrics
- `GET /api/v1/monitoring/storage` - Storage stats
- `GET /api/v1/monitoring/dashboard` - Combined metrics
- `WS /api/v1/monitoring/ws?token=...` - Real-time updates

### Superuser Only
- `GET /api/v1/auth/users/{id}` - Get any user by ID

---

## Documentation Files

- `API_ENDPOINTS.md` - Complete API reference with examples
- `AUTHENTICATION_COMPLETE.md` - Auth implementation details
- `AUTHENTICATION_IMPLEMENTATION.md` - Technical auth guide
- `SERVER_INVENTORY.md` - Complete service inventory
- `NETWORK_DIAGRAM.md` - Network architecture diagrams
- `GIT_AND_BITWARDEN_PLAN.md` - Planned services (Gitea, Vaultwarden)

---

## Next Planned Features

From todo list and planning docs:

1. **Gitea** - Self-hosted Git server (port 3000, 22)
2. **Vaultwarden** - Password manager (port 80/443)
3. **Nginx Reverse Proxy** - SSL termination, domain routing
4. **Integration Testing** - End-to-end test suite
5. **Media Server** - Streaming with transcoding
6. **AI Integration** - Connect to Ollama (localhost:11434)

---

## Docker Network Details

**Network**: `homeserver-network` (bridge)
**Containers**: homeserver, postgres

**DNS resolution** (automatic):
- `postgres` → PostgreSQL container IP
- `homeserver` → HomeServer container IP

**Port mappings**:
- `8000:8000` (homeserver) - HTTP/WebSocket
- `5432:5432` (postgres) - PostgreSQL (should be internal-only in production)

**Health checks**:
- homeserver: `GET /health` every 30s
- postgres: `pg_isready -U homeserver` every 10s

---

## Code Style Configuration

### Black (Formatting)
- Line length: 88
- Target: Python 3.11+
- Configured in: `pyproject.toml`

### Ruff (Linting)
- Enabled: pycodestyle, pyflakes, isort, flake8-bugbear, comprehensions, pyupgrade
- Ignores: E501 (line length - handled by black)

### MyPy (Type Checking)
- Strict mode enabled
- Requires type hints on all functions
- Exception: `tests/` directory

### Running Formatters
```bash
# Format, lint, and type check
black . && ruff check . && mypy src/
```
