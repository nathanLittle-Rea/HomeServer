# HomeServer - Network Architecture Diagram

**Generated**: November 8, 2025
**System**: miniMe.local (macOS 26.0.1)

---

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Host: miniMe.local                                  │
│                              macOS 26.0.1 (Darwin 25.0.0)                       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
        ┌───────────────────┐ ┌─────────────────┐ ┌──────────────────┐
        │  External Users   │ │  Local Browser  │ │   API Clients    │
        │   (Future: WAN)   │ │  (localhost)    │ │   (Scripts/CLI)  │
        └───────────────────┘ └─────────────────┘ └──────────────────┘
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
    ┌───────────────▼───────────────────▼───────────────────▼───────────────┐
    │                        Network Layer (Host)                            │
    │                                                                         │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
    │  │ Port 8000    │  │ Port 5432    │  │ Port 11434   │                │
    │  │ HTTP/WS      │  │ PostgreSQL   │  │ Ollama LLM   │                │
    │  │ (Published)  │  │ (Published)  │  │ (Localhost)  │                │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                │
    │         │                  │                  │                        │
    │         │                  │                  │                        │
    │  ┌──────▼──────────────────▼──────────────────▼──────────────────┐   │
    │  │               Docker Desktop (com.docker.backend)              │   │
    │  │              CPUs: 10 | Memory: 8GB | Network: Bridge          │   │
    │  │                                                                 │   │
    │  │  ┌──────────────────────────────────────────────────────────┐ │   │
    │  │  │        Docker Network: homeserver-network (Bridge)       │ │   │
    │  │  │                                                          │ │   │
    │  │  │  ┌─────────────────────────┐  ┌───────────────────────┐ │ │   │
    │  │  │  │  Container: homeserver  │  │ Container: postgres   │ │ │   │
    │  │  │  │  ─────────────────────  │  │ ───────────────────── │ │ │   │
    │  │  │  │                         │  │                       │ │ │   │
    │  │  │  │  Image:                 │  │  Image:               │ │ │   │
    │  │  │  │  homeserver-homeserver  │  │  postgres:16-alpine   │ │ │   │
    │  │  │  │                         │  │                       │ │ │   │
    │  │  │  │  Internal IP:           │  │  Internal IP:         │ │ │   │
    │  │  │  │  172.x.x.x              │  │  172.x.x.x            │ │ │   │
    │  │  │  │                         │  │                       │ │ │   │
    │  │  │  │  Exposed Ports:         │  │  Exposed Ports:       │ │ │   │
    │  │  │  │  8000 → 8000 (host)     │  │  5432 → 5432 (host)   │ │ │   │
    │  │  │  │                         │  │                       │ │ │   │
    │  │  │  │  Services:              │  │  Services:            │ │ │   │
    │  │  │  │  ├─ FastAPI/Uvicorn    │  │  └─ PostgreSQL 16     │ │ │   │
    │  │  │  │  ├─ Auth API (JWT)     │  │                       │ │ │   │
    │  │  │  │  ├─ File Storage API   │  │  Database:            │ │ │   │
    │  │  │  │  ├─ File Browser API   │  │  └─ homeserver        │ │ │   │
    │  │  │  │  ├─ Monitoring API     │  │     ├─ users          │ │ │   │
    │  │  │  │  └─ WebSocket Server   │  │     ├─ files          │ │ │   │
    │  │  │  │                         │  │     └─ alembic_ver.   │ │ │   │
    │  │  │  │  Health:                │  │                       │ │ │   │
    │  │  │  │  ✅ Healthy             │  │  Health:              │ │ │   │
    │  │  │  │  (HTTP check /health)   │  │  ✅ Healthy           │ │ │   │
    │  │  │  │                         │  │  (pg_isready)         │ │ │   │
    │  │  │  └────────┬────────────────┘  └───────────┬───────────┘ │ │   │
    │  │  │           │                               │             │ │   │
    │  │  │           │  Database Connection          │             │ │   │
    │  │  │           │  (asyncpg + psycopg2)         │             │ │   │
    │  │  │           └───────────────────────────────┘             │ │   │
    │  │  │                                                          │ │   │
    │  │  └──────────────────────────────────────────────────────────┘ │   │
    │  └─────────────────────────────────────────────────────────────────┘   │
    │                                                                         │
    │  Other System Services:                                                │
    │  ├─ Ollama (127.0.0.1:11434) - Local LLM inference                    │
    │  ├─ Control Center (ports 5000, 7000) - macOS AirPlay                 │
    │  ├─ Rapportd (port 64761) - macOS remote management                   │
    │  └─ VS Code + Extensions                                              │
    └─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
    ┌──────────────────────┐ ┌──────────────────┐ ┌─────────────────┐
    │ External Drive       │ │ Local Filesystem │ │  Source Code    │
    │ /Volumes/allDaStuffs │ │ /Users/...       │ │  (Hot Reload)   │
    │                      │ │                  │ │                 │
    │ ├─ postgres/         │ │ ├─ Docker data   │ │ ./src/          │
    │ │  └─ data/          │ │ └─ App data      │ │ ├─ api/         │
    │ └─ storage/          │ │                  │ │ ├─ models/      │
    │    └─ [files]        │ │                  │ │ ├─ services/    │
    │                      │ │                  │ │ └─ static/      │
    │ 931 GB total         │ │                  │ │                 │
    │ 524 GB used (57%)    │ │                  │ │ Mounted to:     │
    │ 407 GB free          │ │                  │ │ /app/src        │
    └──────────────────────┘ └──────────────────┘ └─────────────────┘
```

---

## Network Traffic Flow

### 1. HTTP API Request Flow

```
┌──────────────┐
│   Browser    │  User visits http://localhost:8000
│  (Client)    │
└──────┬───────┘
       │
       │ HTTP Request
       │ GET /dashboard.html
       │
       ▼
┌──────────────────────────────────────┐
│    Host Network Layer (Port 8000)    │
└──────┬───────────────────────────────┘
       │
       │ Port mapping 8000:8000
       │
       ▼
┌──────────────────────────────────────┐
│   Docker Bridge Network              │
│   homeserver-network                 │
└──────┬───────────────────────────────┘
       │
       │ Forward to container
       │
       ▼
┌──────────────────────────────────────┐
│   Container: homeserver:8000         │
│                                      │
│   Uvicorn ASGI Server                │
│   ├─ Receive HTTP request            │
│   ├─ Route to FastAPI app            │
│   ├─ Execute endpoint handler        │
│   └─ Return HTTP response            │
└──────┬───────────────────────────────┘
       │
       │ Response
       │ 200 OK + HTML
       │
       ▼
┌──────────────┐
│   Browser    │  Renders page
└──────────────┘
```

### 2. Authenticated API Request Flow

```
┌──────────────┐
│   Browser    │  Has JWT token in localStorage
└──────┬───────┘
       │
       │ HTTP Request
       │ GET /api/v1/files/list
       │ Authorization: Bearer eyJhbGci...
       │
       ▼
┌───────────────────────────────────────┐
│   Container: homeserver               │
│                                       │
│   ┌────────────────────────────────┐ │
│   │  FastAPI Dependency Injection  │ │
│   │  ─────────────────────────────  │ │
│   │  1. Extract Bearer token       │ │
│   │  2. Decode JWT                 │ │
│   │  3. Verify signature           │ │
│   │  4. Check expiration           │ │
│   └────────┬───────────────────────┘ │
│            │                          │
│            │ Valid token?             │
│            ├─ NO → 401 Unauthorized   │
│            │                          │
│            ▼ YES                      │
│   ┌────────────────────────────────┐ │
│   │  Database Query                │ │
│   └────────┬───────────────────────┘ │
└────────────┼───────────────────────────┘
             │
             │ PostgreSQL query
             │ SELECT * FROM users WHERE id = ?
             │
             ▼
┌─────────────────────────────────────┐
│   Container: postgres               │
│                                     │
│   PostgreSQL 16                     │
│   └─ Query users table              │
│      Return user object             │
└─────────────┬───────────────────────┘
              │
              │ User found and active?
              ├─ NO → 403 Forbidden
              │
              ▼ YES
┌─────────────────────────────────────┐
│   Container: homeserver             │
│                                     │
│   Execute endpoint logic            │
│   └─ Query files table              │
│      Return file list               │
└─────────────┬───────────────────────┘
              │
              │ Response
              │ 200 OK + JSON
              │
              ▼
┌──────────────┐
│   Browser    │  Process file list
└──────────────┘
```

### 3. WebSocket Connection Flow

```
┌──────────────┐
│   Browser    │  Dashboard page loads
└──────┬───────┘
       │
       │ Get token from localStorage
       │
       │ WebSocket handshake
       │ ws://localhost:8000/api/v1/monitoring/ws?token=eyJhbGci...
       │
       ▼
┌────────────────────────────────────────┐
│   Container: homeserver                │
│                                        │
│   WebSocket endpoint                   │
│   ┌─────────────────────────────────┐ │
│   │ 1. Extract token from query     │ │
│   │ 2. Decode and validate JWT      │ │
│   │ 3. Verify user exists & active  │ │
│   └─────────────┬───────────────────┘ │
│                 │                      │
│                 │ Valid?               │
│                 ├─ NO → Close (4001)  │
│                 │                      │
│                 ▼ YES                  │
│   ┌─────────────────────────────────┐ │
│   │ Accept WebSocket connection     │ │
│   │                                 │ │
│   │ Loop every 2 seconds:           │ │
│   │ ├─ Get system metrics           │ │
│   │ ├─ Get storage stats (DB query)│ │
│   │ ├─ Calculate uptime             │ │
│   │ └─ Send JSON to client          │ │
│   └─────────────────────────────────┘ │
└────────────────────────────────────────┘
       │
       │ JSON messages every 2s
       │ { system: {...}, storage: {...}, uptime_seconds: ... }
       │
       ▼
┌──────────────┐
│   Browser    │  Updates dashboard UI in real-time
│              │  CPU graphs, memory bars, etc.
└──────────────┘
```

### 4. Database Connection Flow

```
┌─────────────────────────────────────┐
│   Container: homeserver             │
│                                     │
│   Application startup:              │
│   └─ Create AsyncEngine             │
│      Connection pool (asyncpg)      │
└─────────────┬───────────────────────┘
              │
              │ PostgreSQL connection string:
              │ postgresql+asyncpg://homeserver:password@postgres:5432/homeserver
              │
              │ DNS resolution: "postgres" → 172.x.x.x (container IP)
              │
              ▼
┌─────────────────────────────────────┐
│   Docker Bridge Network             │
│   homeserver-network                │
│                                     │
│   Routes traffic between containers │
└─────────────┬───────────────────────┘
              │
              │ TCP connection to postgres:5432
              │
              ▼
┌─────────────────────────────────────┐
│   Container: postgres:5432          │
│                                     │
│   PostgreSQL Server                 │
│   ├─ Accept connection              │
│   ├─ Authenticate user              │
│   ├─ Select database "homeserver"   │
│   └─ Ready for queries              │
└─────────────────────────────────────┘

On-demand queries:
┌─────────────────┐
│   homeserver    │  SELECT * FROM users WHERE username = 'user'
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   postgres      │  Execute query, return results
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   homeserver    │  Process results
└─────────────────┘
```

### 5. File Storage Flow

```
┌──────────────┐
│   Browser    │  Upload file
│              │  POST /api/v1/files/upload
│              │  Content-Type: multipart/form-data
└──────┬───────┘
       │
       │ File: document.pdf (5 MB)
       │ Tags: "work,important"
       │ Authorization: Bearer token
       │
       ▼
┌────────────────────────────────────────┐
│   Container: homeserver                │
│                                        │
│   1. Authenticate user ✓               │
│   2. Read file content into memory     │
│   3. Generate UUID for file            │
│   4. Parse tags                        │
│   5. Save to disk                      │
│      └─ /app/storage/[uuid]            │
└────────────┬───────────────────────────┘
             │
             │ Write file
             │ (Docker volume mount)
             │
             ▼
┌────────────────────────────────────────┐
│   External Drive                       │
│   /Volumes/allDaStuffs/homeserver/     │
│   storage/                             │
│                                        │
│   File saved:                          │
│   └─ d9e1a6cb-2ec4-49bf-bd78-...       │
│      (5 MB)                            │
└────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│   Container: homeserver                │
│                                        │
│   6. Create metadata record            │
│      └─ INSERT INTO files (...)        │
└────────────┬───────────────────────────┘
             │
             │ Database insert
             │
             ▼
┌────────────────────────────────────────┐
│   Container: postgres                  │
│                                        │
│   Insert into files table:             │
│   ├─ id: d9e1a6cb-...                  │
│   ├─ filename: document.pdf            │
│   ├─ content_type: application/pdf     │
│   ├─ size: 5242880                     │
│   ├─ file_path: /app/storage/d9e1...   │
│   ├─ upload_date: 2025-11-08...        │
│   └─ tags: ["work", "important"]       │
└────────────┬───────────────────────────┘
             │
             │ Metadata stored
             │
             ▼
┌─────────────────────────────────────────┐
│   External Drive (PostgreSQL data)      │
│   /Volumes/allDaStuffs/homeserver/      │
│   postgres/data/                        │
│                                         │
│   Database updated with file metadata   │
└─────────────────────────────────────────┘
             │
             │ Response
             │
             ▼
┌──────────────┐
│   Browser    │  200 OK { id, filename, size }
└──────────────┘
```

---

## Port Mapping Detail

```
┌────────────────────────────────────────────────────────────────┐
│                    Host: miniMe.local                          │
└────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌────────────────┐    ┌────────────────┐
│ Port 8000     │    │ Port 5432      │    │ Port 11434     │
│ (Published)   │    │ (Published)    │    │ (Localhost)    │
│               │    │                │    │                │
│ 0.0.0.0:8000  │    │ 0.0.0.0:5432   │    │ 127.0.0.1:11434│
│ [::]:8000     │    │ [::]:5432      │    │                │
│               │    │                │    │                │
│ Accessible:   │    │ Accessible:    │    │ Accessible:    │
│ - localhost   │    │ - localhost    │    │ - localhost    │
│ - 127.0.0.1   │    │ - 127.0.0.1    │    │                │
│ - LAN IP      │    │ - LAN IP       │    │ NOT accessible │
│ - WAN (if FW) │    │ - WAN (if FW)  │    │ from network   │
│               │    │                │    │                │
│ Forwards to:  │    │ Forwards to:   │    │ Direct bind    │
│ ├─ Container  │    │ ├─ Container   │    │ (no Docker)    │
│ │  homeserver │    │ │  postgres    │    │                │
│ └─ Port 8000  │    │ └─ Port 5432   │    │                │
└───────────────┘    └────────────────┘    └────────────────┘
```

---

## Volume Mount Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        Host Filesystem                           │
└──────────────────────────────────────────────────────────────────┘
                                │
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ ./src/         │    │ /Volumes/        │    │ /Volumes/       │
│                │    │ allDaStuffs/     │    │ allDaStuffs/    │
│ Source code    │    │ homeserver/      │    │                 │
│ directory      │    │ storage/         │    │ Full drive      │
│                │    │                  │    │ (read-only)     │
│ Hot reload     │    │ File uploads     │    │                 │
└────────┬───────┘    └────────┬─────────┘    └────────┬────────┘
         │                     │                       │
         │ Bind mount          │ Bind mount            │ Bind mount
         │ (Read/Write)        │ (Read/Write)          │ (Read-Only)
         │                     │                       │
         ▼                     ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              Docker Container: homeserver                        │
│                                                                  │
│  /app/src/              /app/storage/         /Volumes/allDa... │
│  ├─ api/                ├─ [UUID files]       (browse external  │
│  ├─ models/             └─ ...                 drive content)    │
│  ├─ services/                                                    │
│  ├─ static/                                                      │
│  └─ main.py                                                      │
│                                                                  │
│  Changes to host ./src/ immediately reflected in container      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        Host Filesystem                           │
│                                                                  │
│  /Volumes/allDaStuffs/homeserver/postgres/                      │
│  └─ PostgreSQL database files                                   │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          │ Bind mount
                          │ (Read/Write)
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│              Docker Container: postgres                          │
│                                                                  │
│  /var/lib/postgresql/data/                                      │
│  ├─ base/ (database files)                                      │
│  ├─ global/ (shared objects)                                    │
│  ├─ pg_wal/ (write-ahead log)                                   │
│  └─ ... (other PostgreSQL files)                                │
│                                                                  │
│  Data persists on external drive, survives container restarts   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Security Zones

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SECURITY ZONES                               │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  Zone 1: Public Internet (Future)                                    │
│  ────────────────────────────────────────────────────────────────    │
│  Risk Level: HIGH                                                    │
│  Access: Untrusted, unauthenticated traffic                         │
│  Security: Firewall, WAF, DDoS protection needed                    │
│  Status: Not yet exposed (localhost only)                           │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           │ (Future: Nginx reverse proxy with SSL)
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Zone 2: Application Layer (DMZ)                                     │
│  ────────────────────────────────────────────────────────────────    │
│  Risk Level: MEDIUM                                                  │
│  Services: HomeServer FastAPI application                            │
│  Port: 8000 (HTTP)                                                   │
│  Security:                                                           │
│    ✅ JWT authentication required for all protected endpoints       │
│    ✅ Input validation (Pydantic)                                   │
│    ✅ Rate limiting (recommended to add)                            │
│    ⚠️  No HTTPS (add Nginx with SSL)                                │
│  Access Control:                                                     │
│    - Public: /health, /api/v1/info, /login, /register              │
│    - Authenticated: All other endpoints                             │
│    - Superuser: /api/v1/auth/users/{id}                            │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           │ Internal Docker network (encrypted connection)
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Zone 3: Database Layer (Internal)                                   │
│  ────────────────────────────────────────────────────────────────    │
│  Risk Level: LOW (if port 5432 firewalled)                          │
│  Services: PostgreSQL 16                                             │
│  Port: 5432 (PostgreSQL)                                             │
│  Security:                                                           │
│    ✅ Password authentication                                       │
│    ✅ Network isolation (Docker bridge)                             │
│    ⚠️  Port exposed to host (should be internal only)               │
│    ✅ Passwords hashed with bcrypt                                  │
│    ✅ Data at rest on encrypted volume (external drive)             │
│  Access Control:                                                     │
│    - Only homeserver container should access                        │
│    - Consider: Remove port mapping for production                   │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           │ Volume mount to external drive
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Zone 4: Storage Layer (Physical)                                    │
│  ────────────────────────────────────────────────────────────────    │
│  Risk Level: LOW (physical access required)                         │
│  Location: /Volumes/allDaStuffs                                     │
│  Security:                                                           │
│    ✅ macOS filesystem permissions                                  │
│    ✅ External drive (can be disconnected)                          │
│    ✅ Read-only mount for browsing                                  │
│    ⚠️  No encryption at rest (consider FileVault)                   │
│  Access Control:                                                     │
│    - Host user: Full access                                         │
│    - homeserver container: RW to storage/, RO to root               │
│    - postgres container: RW to postgres/ only                       │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  Zone 5: Localhost Services                                          │
│  ────────────────────────────────────────────────────────────────    │
│  Risk Level: VERY LOW                                                │
│  Services: Ollama (port 11434), VS Code, etc.                       │
│  Security:                                                           │
│    ✅ Bound to 127.0.0.1 only                                       │
│    ✅ Not accessible from network                                   │
│    ✅ No authentication needed (localhost trust)                    │
│  Access Control:                                                     │
│    - Only local processes can access                                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: End-to-End Example

**Scenario**: User logs in and uploads a file

```
┌─────────────────────────────────────────────────────────────────────┐
│ Step 1: User Authentication                                         │
└─────────────────────────────────────────────────────────────────────┘

Browser (http://localhost:8000/login.html)
    │
    │ 1. Load login page
    │
    ▼
homeserver:8000 (/login.html)
    │
    │ 2. Return HTML form
    │
    ▼
Browser
    │
    │ 3. User enters credentials
    │    username: "john"
    │    password: "secret123"
    │
    │ POST /api/v1/auth/login
    │ { username: "john", password: "secret123" }
    │
    ▼
homeserver:8000 (/api/v1/auth/login)
    │
    │ 4. Query database for user
    │    SELECT * FROM users WHERE username = 'john'
    │
    ▼
postgres:5432 (users table)
    │
    │ 5. Return user record
    │    { id: 1, username: "john", hashed_password: "$2b$12..." }
    │
    ▼
homeserver (AuthService)
    │
    │ 6. Verify password: bcrypt.verify("secret123", "$2b$12...")
    │    ✅ Match!
    │
    │ 7. Generate JWT token
    │    Payload: { sub: "john", user_id: 1, exp: 1731187200 }
    │    Sign with secret key (HS256)
    │    Token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    │
    ▼
Browser
    │
    │ 8. Receive token
    │    { access_token: "eyJhbGci...", token_type: "bearer" }
    │
    │ 9. Store in localStorage
    │    localStorage.setItem('access_token', 'eyJhbGci...')
    │
    │ 10. Redirect to dashboard
    │
    ▼
Browser (http://localhost:8000/dashboard.html)

┌─────────────────────────────────────────────────────────────────────┐
│ Step 2: Accessing Protected Resource (File Upload)                  │
└─────────────────────────────────────────────────────────────────────┘

Browser (on /files.html page)
    │
    │ 1. User selects file: report.pdf (2 MB)
    │    User enters tags: "work, quarterly"
    │
    │ 2. Prepare multipart/form-data
    │    file: [binary data]
    │    tags: "work,quarterly"
    │
    │ 3. Get token from localStorage
    │    token = localStorage.getItem('access_token')
    │
    │ POST /api/v1/files/upload
    │ Authorization: Bearer eyJhbGci...
    │ Content-Type: multipart/form-data
    │
    ▼
homeserver:8000 (FastAPI middleware)
    │
    │ 4. Extract Bearer token from header
    │    "eyJhbGci..."
    │
    │ 5. Decode JWT token
    │    jose.jwt.decode(token, secret_key, algorithms=["HS256"])
    │
    │ 6. Verify signature ✅
    │    Check expiration ✅ (not expired)
    │    Extract user_id: 1
    │
    │ 7. Query database for user
    │    SELECT * FROM users WHERE id = 1
    │
    ▼
postgres:5432 (users table)
    │
    │ 8. Return user
    │    { id: 1, username: "john", is_active: true }
    │
    ▼
homeserver:8000 (upload_file endpoint)
    │
    │ 9. User authenticated and active ✅
    │
    │ 10. Read file content into memory
    │     content = await file.read()  # 2 MB
    │
    │ 11. Generate UUID for file
    │     file_id = "a7b3c9d1-4e5f-6g7h-8i9j-0k1l2m3n4o5p"
    │
    │ 12. Parse tags
    │     ["work", "quarterly"]
    │
    │ 13. Write file to disk
    │     path = /app/storage/a7b3c9d1-4e5f-6g7h-8i9j-0k1l2m3n4o5p
    │
    ▼
External Drive (/Volumes/allDaStuffs/homeserver/storage/)
    │
    │ 14. File written successfully
    │     a7b3c9d1-4e5f-6g7h-8i9j-0k1l2m3n4o5p (2 MB)
    │
    ▼
homeserver:8000 (FileStorageService)
    │
    │ 15. Insert metadata into database
    │     INSERT INTO files (id, filename, content_type, size, file_path, tags)
    │     VALUES ('a7b3c9d1...', 'report.pdf', 'application/pdf',
    │             2097152, '/app/storage/a7b3c9d1...',
    │             ARRAY['work', 'quarterly'])
    │
    ▼
postgres:5432 (files table)
    │
    │ 16. Record inserted successfully
    │
    ▼
homeserver:8000
    │
    │ 17. Return response
    │     200 OK
    │     {
    │       "id": "a7b3c9d1-4e5f-6g7h-8i9j-0k1l2m3n4o5p",
    │       "filename": "report.pdf",
    │       "size": 2097152
    │     }
    │
    ▼
Browser
    │
    │ 18. Display success message
    │     "File uploaded successfully!"
    │
    └─ File now appears in file list
```

---

## Future Architecture (Planned)

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Internet / WAN (Port 443)                         │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             │ HTTPS
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  Nginx Reverse Proxy (Container)                     │
│                                                                      │
│  Features:                                                           │
│  ├─ SSL/TLS termination (Let's Encrypt)                             │
│  ├─ Rate limiting                                                   │
│  ├─ Load balancing                                                  │
│  ├─ Static file caching                                             │
│  └─ WebSocket proxying                                              │
│                                                                      │
│  Routes:                                                             │
│  ├─ homeserver.local → homeserver:8000                              │
│  ├─ git.homeserver.local → gitea:3000                               │
│  └─ vault.homeserver.local → vaultwarden:80                         │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             │ Internal HTTP
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌──────────────┐    ┌────────────────┐
│  homeserver   │    │    Gitea     │    │  Vaultwarden   │
│  Container    │    │  Container   │    │   Container    │
│               │    │              │    │                │
│  Port: 8000   │    │  Port: 3000  │    │  Port: 80      │
│  (internal)   │    │  Port: 22    │    │                │
└───────┬───────┘    └──────┬───────┘    └────────┬───────┘
        │                   │                     │
        │                   │                     │
        └───────────────────┼─────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   postgres    │
                    │   Container   │
                    │               │
                    │  Port: 5432   │
                    │  (internal)   │
                    └───────────────┘
```

---

## Performance & Scaling Considerations

### Current Architecture (Single Host)

```
┌──────────────────────────────────────┐
│        Docker Host (miniMe.local)    │
│                                      │
│  Resources:                          │
│  ├─ CPUs: 10 cores                   │
│  ├─ Memory: 8 GB                     │
│  ├─ Disk: 228 GB (system)            │
│  └─ External: 931 GB                 │
│                                      │
│  Containers:                         │
│  ├─ homeserver (~100 MB)             │
│  └─ postgres (~100 MB)               │
│                                      │
│  Capacity:                           │
│  ├─ Concurrent users: ~50-100        │
│  ├─ File storage: Limited by disk    │
│  └─ Database: Single instance        │
└──────────────────────────────────────┘
```

### Future Scaling Options

```
Option 1: Vertical Scaling (Increase Resources)
├─ More CPUs (Docker VM allocation)
├─ More Memory (Docker VM allocation)
└─ Larger external drive

Option 2: Horizontal Scaling (Multiple Instances)
┌────────────────────────────────────────────┐
│         Load Balancer (Nginx)              │
└────────┬─────────────────────┬─────────────┘
         │                     │
         ▼                     ▼
┌─────────────────┐    ┌─────────────────┐
│  homeserver-1   │    │  homeserver-2   │
│  (read/write)   │    │  (read/write)   │
└────────┬────────┘    └────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────┐
         │  PostgreSQL      │
         │  (single primary)│
         └──────────────────┘

Option 3: Database Replication
┌─────────────────────────────────────┐
│      PostgreSQL Primary             │
│      (Write operations)             │
└────────┬────────────────────────────┘
         │
         │ Streaming replication
         │
         ├────────────────┬────────────┐
         ▼                ▼            ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │ PostgreSQL  │  │ PostgreSQL  │
│ Replica 1   │  │ Replica 2   │  │ Replica 3   │
│ (Read-only) │  │ (Read-only) │  │ (Read-only) │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

**Document Version**: 1.0
**Last Updated**: November 8, 2025
**Next Update**: When new services (Gitea, Vaultwarden, Nginx) are added
