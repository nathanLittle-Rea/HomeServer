# HomeServer API Endpoints

## Current Endpoints (Implemented)

### Core

#### `GET /`
- **Description**: Root endpoint with server info
- **Response**: `{ message, version, status }`
- **Auth**: None

#### `GET /health`
- **Description**: Health check for monitoring/load balancers
- **Response**: `{ status, app, version }`
- **Auth**: None

#### `GET /api/v1/info`
- **Description**: API version and service status
- **Response**: `{ api_version, services: {...} }`
- **Auth**: None

---

### Authentication

#### `POST /api/v1/auth/register`
- **Description**: Register a new user
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "username": "string (3-50 characters)",
    "email": "string (valid email)",
    "password": "string (min 8 characters)"
  }
  ```
- **Response**:
  ```json
  {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "is_active": true,
      "is_superuser": false,
      "created_at": "2025-11-08T12:00:00Z",
      "updated_at": "2025-11-08T12:00:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
  ```
- **Auth**: None
- **Example**:
  ```bash
  curl -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
  ```

#### `POST /api/v1/auth/login`
- **Description**: Login and get JWT access token
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
  ```
- **Auth**: None
- **Token expires in**: 24 hours
- **Example**:
  ```bash
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"testuser","password":"password123"}'
  ```

#### `GET /api/v1/auth/me`
- **Description**: Get current authenticated user information
- **Response**:
  ```json
  {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-11-08T12:00:00Z",
    "updated_at": "2025-11-08T12:00:00Z"
  }
  ```
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl http://localhost:8000/api/v1/auth/me \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `PATCH /api/v1/auth/me`
- **Description**: Update current user's profile
- **Content-Type**: `application/json`
- **Body** (all fields optional):
  ```json
  {
    "username": "string (3-50 characters)",
    "email": "string (valid email)"
  }
  ```
- **Response**: Updated user object
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl -X PATCH http://localhost:8000/api/v1/auth/me \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
    -H "Content-Type: application/json" \
    -d '{"email":"newemail@example.com"}'
  ```

#### `DELETE /api/v1/auth/me`
- **Description**: Delete current user's account
- **Response**: 204 No Content
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl -X DELETE http://localhost:8000/api/v1/auth/me \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `GET /api/v1/auth/users/{user_id}`
- **Description**: Get user information by ID (admin only)
- **Path Params**:
  - `user_id`: User ID (integer)
- **Response**: User object
- **Auth**: Bearer token required (superuser only)
- **Example**:
  ```bash
  curl http://localhost:8000/api/v1/auth/users/1 \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

---

### File Storage (Upload/Manage)

#### `POST /api/v1/files/upload`
- **Description**: Upload a file with optional tags
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file`: File to upload (required)
  - `tags`: Comma-separated tags (optional)
- **Response**: `{ id, filename, size, message }`
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl -X POST http://localhost:8000/api/v1/files/upload \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
    -F "file=@document.pdf" \
    -F "tags=important,work"
  ```

#### `GET /api/v1/files/list`
- **Description**: List all uploaded files
- **Query Params**:
  - `tag`: Filter by tag (optional)
- **Response**: `{ files: [...], total }`
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl http://localhost:8000/api/v1/files/list?tag=work \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `GET /api/v1/files/{file_id}/metadata`
- **Description**: Get file metadata
- **Path Params**:
  - `file_id`: File UUID
- **Response**: `{ id, filename, content_type, size, upload_date, tags }`
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl http://localhost:8000/api/v1/files/abc123.../metadata \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `GET /api/v1/files/{file_id}/download`
- **Description**: Download a file
- **Path Params**:
  - `file_id`: File UUID
- **Response**: File content (streaming)
- **Headers**: `Content-Disposition: attachment; filename="..."`
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl -O -J http://localhost:8000/api/v1/files/abc123.../download \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `DELETE /api/v1/files/{file_id}`
- **Description**: Delete a file (from disk and database)
- **Path Params**:
  - `file_id`: File UUID
- **Response**: `{ id, message }`
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl -X DELETE http://localhost:8000/api/v1/files/abc123... \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

---

### File Browser (Browse Existing Files)

#### `GET /api/v1/browser/roots`
- **Description**: Get list of allowed root paths for browsing
- **Response**: `["/Volumes/allDaStuffs", "/app/storage"]`
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl http://localhost:8000/api/v1/browser/roots \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `GET /api/v1/browser/list`
- **Description**: List directory contents
- **Query Params**:
  - `path`: Directory path (required)
- **Response**: `{ path, parent, items: [...], total_items }`
- **Item fields**: `name, path, is_directory, size, modified, permissions, is_readable`
- **Auth**: Bearer token required
- **Errors**:
  - 403: Access denied (path not allowed or not authenticated)
  - 404: Directory not found
  - 400: Not a directory
- **Example**:
  ```bash
  curl "http://localhost:8000/api/v1/browser/list?path=/Volumes/allDaStuffs" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `GET /api/v1/browser/info`
- **Description**: Get file or directory metadata
- **Query Params**:
  - `path`: File/directory path (required)
- **Response**: `{ name, path, is_directory, size, modified, permissions, is_readable }`
- **Auth**: Bearer token required
- **Errors**:
  - 403: Access denied or not authenticated
  - 404: Not found
- **Example**:
  ```bash
  curl "http://localhost:8000/api/v1/browser/info?path=/Volumes/allDaStuffs/file.txt" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `GET /api/v1/browser/download`
- **Description**: Download a file from file system
- **Query Params**:
  - `path`: File path (required)
- **Response**: File content (streaming)
- **Headers**: `Content-Disposition: attachment; filename="..."`
- **Auth**: Bearer token required
- **Errors**:
  - 403: Access denied or not authenticated
  - 404: File not found
  - 400: Path is a directory
- **Example**:
  ```bash
  curl -O -J "http://localhost:8000/api/v1/browser/download?path=/Volumes/allDaStuffs/file.txt" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

---

### Monitoring

#### `GET /api/v1/monitoring/system`
- **Description**: Get current system metrics (CPU, memory, disk)
- **Response**:
  ```json
  {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "memory_used_gb": 3.45,
    "memory_total_gb": 7.65,
    "disk_percent": 62.4,
    "disk_used_gb": 142.35,
    "disk_total_gb": 228.27,
    "disk_free_gb": 85.92
  }
  ```
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl http://localhost:8000/api/v1/monitoring/system \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `GET /api/v1/monitoring/storage`
- **Description**: Get file storage statistics from database
- **Response**:
  ```json
  {
    "total_files": 15,
    "total_size_gb": 2.45,
    "storage_path": "/app/storage"
  }
  ```
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl http://localhost:8000/api/v1/monitoring/storage \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `GET /api/v1/monitoring/dashboard`
- **Description**: Get all dashboard metrics (combines system + storage + uptime)
- **Response**:
  ```json
  {
    "system": { cpu_percent, memory_percent, ... },
    "storage": { total_files, total_size_gb, ... },
    "uptime_seconds": 3600.5
  }
  ```
- **Auth**: Bearer token required
- **Example**:
  ```bash
  curl http://localhost:8000/api/v1/monitoring/dashboard \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
  ```

#### `WS /api/v1/monitoring/ws`
- **Description**: WebSocket for real-time metrics updates
- **Protocol**: Sends dashboard metrics JSON every 2 seconds
- **Auth**: JWT token required (sent as query parameter)
- **Example**:
  ```javascript
  const token = localStorage.getItem('access_token');
  const ws = new WebSocket(`ws://localhost:8000/api/v1/monitoring/ws?token=${token}`);
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Metrics:', data);
  };
  ```

---

## Frontend Pages

#### `GET /login.html`
- **Description**: User login page
- **Features**: Username/password authentication, token storage, error handling, auto-redirect if already logged in

#### `GET /register.html`
- **Description**: User registration page
- **Features**: Username/email/password validation, real-time field validation, automatic login after registration

#### `GET /dashboard.html`
- **Description**: Real-time monitoring dashboard
- **Features**: CPU/memory/disk graphs, WebSocket updates with authentication, auto-reconnect, user profile display, logout
- **Auth**: Requires valid token in localStorage

#### `GET /files.html`
- **Description**: File manager (upload/download/delete)
- **Features**: Drag-drop upload, tags, download, delete with confirmation, authentication
- **Auth**: Requires valid token in localStorage

#### `GET /browser.html`
- **Description**: File browser for external drives
- **Features**: Directory navigation, breadcrumbs, file metadata, download, authentication
- **Auth**: Requires valid token in localStorage

---

## Planned Endpoints (Not Yet Implemented)

### File Operations (Advanced)

#### `PATCH /api/v1/files/{file_id}`
- **Description**: Update file metadata (tags, filename)
- **Body**: `{ filename?, tags? }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/files/search`
- **Description**: Search files by name, tags, content
- **Body**: `{ query, tags?, content_type?, date_range? }`
- **Response**: `{ files: [...], total, page }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/files/{file_id}/share`
- **Description**: Create shareable link
- **Body**: `{ expires_in?, password? }`
- **Response**: `{ share_url, expires_at }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/files/{file_id}/preview`
- **Description**: Get file preview (thumbnail for images, first page for PDFs)
- **Query Params**: `size=small|medium|large`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/files/bulk-delete`
- **Description**: Delete multiple files
- **Body**: `{ file_ids: [...] }`
- **Auth**: Bearer token
- **Status**: Planned

---

### Browser Operations (Advanced)

#### `POST /api/v1/browser/create-folder`
- **Description**: Create a new directory
- **Body**: `{ path, name }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/browser/move`
- **Description**: Move/rename file or directory
- **Body**: `{ source_path, destination_path }`
- **Auth**: Bearer token
- **Status**: Planned

#### `DELETE /api/v1/browser/delete`
- **Description**: Delete file or directory from file system
- **Query Params**: `path`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/browser/copy`
- **Description**: Copy file or directory
- **Body**: `{ source_path, destination_path }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/browser/search`
- **Description**: Search files by name pattern
- **Query Params**: `path, pattern, recursive=true|false`
- **Auth**: Bearer token
- **Status**: Planned

---

### Media Server

#### `GET /api/v1/media/libraries`
- **Description**: List media libraries (Movies, TV, Music)
- **Response**: `{ libraries: [...] }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/media/libraries/{library_id}/items`
- **Description**: List items in library
- **Query Params**: `page, limit, sort, filter`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/media/items/{item_id}`
- **Description**: Get media item details
- **Response**: `{ title, year, duration, metadata, ... }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/media/items/{item_id}/stream`
- **Description**: Stream media file (with transcoding)
- **Query Params**: `quality, format`
- **Response**: Media stream
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/media/scan`
- **Description**: Scan library for new media
- **Body**: `{ library_id }`
- **Auth**: Bearer token
- **Status**: Planned

---

### Home Automation

#### `GET /api/v1/automation/devices`
- **Description**: List all IoT devices
- **Response**: `{ devices: [...] }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/automation/devices/{device_id}`
- **Description**: Get device details and state
- **Response**: `{ id, name, type, state, capabilities }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/automation/devices/{device_id}/control`
- **Description**: Control device (turn on/off, set value)
- **Body**: `{ action, value? }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/automation/scenes`
- **Description**: List automation scenes
- **Response**: `{ scenes: [...] }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/automation/scenes/{scene_id}/trigger`
- **Description**: Trigger a scene
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/automation/rules`
- **Description**: List automation rules
- **Response**: `{ rules: [...] }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/automation/rules`
- **Description**: Create automation rule
- **Body**: `{ name, trigger, conditions, actions }`
- **Auth**: Bearer token
- **Status**: Planned

---

### Monitoring (Advanced)

#### `GET /api/v1/monitoring/network`
- **Description**: Network statistics (bandwidth, connections)
- **Response**: `{ upload_mbps, download_mbps, connections, ... }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/monitoring/processes`
- **Description**: Running processes
- **Query Params**: `sort=cpu|memory|name, limit`
- **Response**: `{ processes: [...] }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/monitoring/logs`
- **Description**: Server logs
- **Query Params**: `level, service, since, limit`
- **Response**: `{ logs: [...], total }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/monitoring/history`
- **Description**: Historical metrics
- **Query Params**: `metric, from, to, interval`
- **Response**: `{ data_points: [...] }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/monitoring/alerts`
- **Description**: Create alert rule
- **Body**: `{ metric, threshold, action }`
- **Auth**: Bearer token
- **Status**: Planned

---

### AI/LLM Integration

#### `POST /api/v1/ai/chat`
- **Description**: Chat with AI assistant
- **Body**: `{ message, conversation_id? }`
- **Response**: `{ reply, conversation_id }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/ai/analyze-file`
- **Description**: Analyze file content with AI
- **Body**: `{ file_id, prompt }`
- **Response**: `{ analysis }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/ai/search`
- **Description**: Semantic search across files
- **Body**: `{ query }`
- **Response**: `{ results: [...] }`
- **Auth**: Bearer token
- **Status**: Planned

---

### Backup & Maintenance

#### `POST /api/v1/backup/create`
- **Description**: Create backup of database/files
- **Body**: `{ include: ["database", "files"], compression? }`
- **Auth**: Bearer token
- **Status**: Planned

#### `GET /api/v1/backup/list`
- **Description**: List available backups
- **Response**: `{ backups: [...] }`
- **Auth**: Bearer token
- **Status**: Planned

#### `POST /api/v1/backup/{backup_id}/restore`
- **Description**: Restore from backup
- **Auth**: Bearer token
- **Status**: Planned

---

### Settings & Configuration

#### `GET /api/v1/settings`
- **Description**: Get server settings
- **Auth**: Bearer token (admin)
- **Status**: Planned

#### `PATCH /api/v1/settings`
- **Description**: Update server settings
- **Body**: `{ key: value, ... }`
- **Auth**: Bearer token (admin)
- **Status**: Planned

---

## Summary

### Current Status
- **Implemented**: 20 endpoints + 1 WebSocket + 5 frontend pages
- **Categories**: Core (3), Auth (6), Files (5), Browser (4), Monitoring (4)
- **Authentication**: JWT-based authentication implemented
  - All file, browser, and monitoring endpoints require authentication
  - User registration, login, profile management working
  - Bearer token authentication with 24-hour expiration

### Next Priorities
1. **Search** - File search functionality
2. **Media Server** - Basic streaming
3. **Network Monitoring** - Bandwidth/connection stats
4. **Settings Page** - Configuration UI
5. **Git Server (Gitea)** - Self-hosted Git repository
6. **Password Manager (Vaultwarden)** - Self-hosted Bitwarden

### Total Planned
- **100+ endpoints** across all categories
- **10+ frontend pages**
- **Multiple WebSocket channels** for real-time data
