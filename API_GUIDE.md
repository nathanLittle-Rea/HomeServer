# HomeServer API Complete Guide

**Version**: 0.1.0
**Base URL**: `http://localhost:8000` (local) or `http://192.168.0.40:8000` (network)
**Documentation**: http://localhost:8000/docs (Interactive Swagger UI)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Endpoints](#core-endpoints)
3. [File Storage API](#file-storage-api)
4. [File Browser API](#file-browser-api)
5. [Monitoring API](#monitoring-api)
6. [Frontend Pages](#frontend-pages)
7. [Planned Features](#planned-features)
8. [Common Workflows](#common-workflows)
9. [Error Handling](#error-handling)
10. [Rate Limits & Performance](#rate-limits--performance)

---

## Quick Start

### Prerequisites
```bash
# Ensure Docker containers are running
docker-compose ps

# Should show:
# - homeserver (running)
# - homeserver-postgres (running)
```

### Test Connection
```bash
# Check if server is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","app":"HomeServer","version":"0.1.0"}
```

### Access Interactive Documentation
Open in browser: http://localhost:8000/docs

---

## Core Endpoints

### 1. Root Endpoint

**`GET /`**

Get basic server information.

**Step-by-step:**
```bash
# 1. Make the request
curl http://localhost:8000/

# 2. Response
{
  "message": "Welcome to HomeServer",
  "version": "0.1.0",
  "status": "running"
}
```

**Use cases:**
- Verify server is accessible
- Check server version
- Health monitoring

---

### 2. Health Check

**`GET /health`**

Health endpoint for monitoring systems.

**Step-by-step:**
```bash
# 1. Make the request
curl http://localhost:8000/health

# 2. Response (200 OK)
{
  "status": "healthy",
  "app": "HomeServer",
  "version": "0.1.0"
}
```

**Use cases:**
- Docker health checks
- Load balancer health probes
- Uptime monitoring
- CI/CD pipeline checks

**Integration example (Docker Compose):**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

### 3. API Information

**`GET /api/v1/info`**

Get API version and service status.

**Step-by-step:**
```bash
# 1. Make the request
curl http://localhost:8000/api/v1/info

# 2. Response
{
  "api_version": "v1",
  "services": {
    "media": "planned",
    "files": "active",
    "browser": "active",
    "automation": "planned",
    "ai": "planned",
    "monitoring": "active",
    "web": "planned"
  }
}
```

**Use cases:**
- Check which services are available
- API version discovery
- Feature detection

---

## File Storage API

The File Storage API manages uploaded files with metadata stored in PostgreSQL.

### 1. Upload File

**`POST /api/v1/files/upload`**

Upload a file with optional tags.

**Step-by-step:**

**Using curl:**
```bash
# 1. Upload a simple file
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@/path/to/document.pdf"

# 2. Upload with tags
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@/path/to/photo.jpg" \
  -F "tags=vacation,2024,beach"

# 3. Response
{
  "id": "abc123-def456-...",
  "filename": "photo.jpg",
  "size": 2048576,
  "message": "File uploaded successfully"
}
```

**Using Python:**
```python
import requests

# Upload file
url = "http://localhost:8000/api/v1/files/upload"
files = {"file": open("document.pdf", "rb")}
data = {"tags": "important,work"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**Using JavaScript:**
```javascript
// Upload from browser
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('tags', 'important,work');

const response = await fetch('http://localhost:8000/api/v1/files/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log('Uploaded:', data);
```

**Parameters:**
- `file` (required): File to upload
- `tags` (optional): Comma-separated tags

**Response fields:**
- `id`: UUID for the file (use this for all future operations)
- `filename`: Original filename
- `size`: File size in bytes
- `message`: Success message

**Use cases:**
- Backup important documents
- Share files between devices
- Store application data
- Archive photos/videos

---

### 2. List Files

**`GET /api/v1/files/list`**

List all uploaded files with optional tag filtering.

**Step-by-step:**

```bash
# 1. List all files
curl http://localhost:8000/api/v1/files/list

# 2. Response
{
  "files": [
    {
      "id": "abc123...",
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "size": 1024000,
      "upload_date": "2025-11-07T01:25:15.053271Z",
      "tags": ["important", "work"]
    },
    {
      "id": "def456...",
      "filename": "photo.jpg",
      "content_type": "image/jpeg",
      "size": 2048576,
      "upload_date": "2025-11-07T02:30:20.123456Z",
      "tags": ["vacation", "2024"]
    }
  ],
  "total": 2
}

# 3. Filter by tag
curl http://localhost:8000/api/v1/files/list?tag=work

# 4. Response (only files with "work" tag)
{
  "files": [
    {
      "id": "abc123...",
      "filename": "document.pdf",
      ...
      "tags": ["important", "work"]
    }
  ],
  "total": 1
}
```

**Using Python:**
```python
import requests

# List all files
response = requests.get("http://localhost:8000/api/v1/files/list")
files = response.json()

for file in files['files']:
    print(f"{file['filename']} ({file['size']} bytes)")

# Filter by tag
response = requests.get(
    "http://localhost:8000/api/v1/files/list",
    params={"tag": "work"}
)
work_files = response.json()
```

**Query parameters:**
- `tag` (optional): Filter files by tag

**Use cases:**
- Display file list in UI
- Find files by tag
- Check storage usage
- Generate reports

---

### 3. Get File Metadata

**`GET /api/v1/files/{file_id}/metadata`**

Get detailed metadata for a specific file.

**Step-by-step:**

```bash
# 1. Get metadata
curl http://localhost:8000/api/v1/files/abc123-def456.../metadata

# 2. Response
{
  "id": "abc123-def456-...",
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "size": 1024000,
  "upload_date": "2025-11-07T01:25:15.053271Z",
  "tags": ["important", "work"]
}
```

**Using Python:**
```python
import requests

file_id = "abc123-def456-..."
url = f"http://localhost:8000/api/v1/files/{file_id}/metadata"

response = requests.get(url)
metadata = response.json()

print(f"Filename: {metadata['filename']}")
print(f"Size: {metadata['size']} bytes")
print(f"Uploaded: {metadata['upload_date']}")
print(f"Tags: {', '.join(metadata['tags'])}")
```

**Use cases:**
- Display file details in UI
- Check file existence
- Verify upload integrity
- Build file index

---

### 4. Download File

**`GET /api/v1/files/{file_id}/download`**

Download a file by its ID.

**Step-by-step:**

```bash
# 1. Download file (saves with original filename)
curl -O -J http://localhost:8000/api/v1/files/abc123-def456.../download

# 2. Download and rename
curl -o myfile.pdf http://localhost:8000/api/v1/files/abc123-def456.../download

# 3. Download and pipe to another command
curl http://localhost:8000/api/v1/files/abc123-def456.../download | wc -l
```

**Using Python:**
```python
import requests

file_id = "abc123-def456-..."
url = f"http://localhost:8000/api/v1/files/{file_id}/download"

# Stream download (efficient for large files)
response = requests.get(url, stream=True)

# Get original filename from headers
filename = response.headers.get('Content-Disposition').split('filename=')[1].strip('"')

# Save to disk
with open(filename, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"Downloaded: {filename}")
```

**Using JavaScript (browser):**
```javascript
// Trigger browser download
async function downloadFile(fileId) {
  const url = `http://localhost:8000/api/v1/files/${fileId}/download`;
  window.location.href = url;
}

// Or fetch and process
async function fetchFile(fileId) {
  const response = await fetch(url);
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  // Create download link
  const a = document.createElement('a');
  a.href = url;
  a.download = 'filename.pdf';
  a.click();
}
```

**Response headers:**
- `Content-Disposition`: `attachment; filename="original.pdf"`
- `Content-Type`: Original MIME type

**Use cases:**
- Retrieve uploaded files
- Backup files to local machine
- Share files between devices
- Programmatic file access

---

### 5. Delete File

**`DELETE /api/v1/files/{file_id}`**

Delete a file from both disk and database.

**Step-by-step:**

```bash
# 1. Delete file
curl -X DELETE http://localhost:8000/api/v1/files/abc123-def456...

# 2. Response
{
  "id": "abc123-def456-...",
  "message": "File deleted successfully"
}

# 3. Verify deletion (should return 404)
curl http://localhost:8000/api/v1/files/abc123-def456.../metadata
# Response: {"detail": "File not found"}
```

**Using Python:**
```python
import requests

file_id = "abc123-def456-..."
url = f"http://localhost:8000/api/v1/files/{file_id}"

# Delete with confirmation
confirm = input(f"Delete file {file_id}? (y/n): ")
if confirm.lower() == 'y':
    response = requests.delete(url)
    if response.status_code == 200:
        print("File deleted successfully")
    else:
        print(f"Error: {response.json()}")
```

**Using JavaScript:**
```javascript
// Delete with confirmation
async function deleteFile(fileId, filename) {
  if (!confirm(`Delete ${filename}?`)) return;

  const response = await fetch(
    `http://localhost:8000/api/v1/files/${fileId}`,
    { method: 'DELETE' }
  );

  if (response.ok) {
    const data = await response.json();
    console.log(data.message);
  } else {
    console.error('Delete failed');
  }
}
```

**Important:**
- Deletion is permanent and irreversible
- Both file data and database entry are removed
- Returns 404 if file doesn't exist

**Use cases:**
- Clean up old files
- Remove sensitive data
- Free up storage space
- File lifecycle management

---

## File Browser API

The File Browser API allows browsing existing files on the external drive and file system.

### 1. Get Root Paths

**`GET /api/v1/browser/roots`**

Get list of allowed root directories for browsing.

**Step-by-step:**

```bash
# 1. Get allowed paths
curl http://localhost:8000/api/v1/browser/roots

# 2. Response
[
  "/Volumes/allDaStuffs",
  "/app/storage"
]
```

**Use cases:**
- Display available locations in UI
- Validate paths before browsing
- Build navigation menu

---

### 2. List Directory

**`GET /api/v1/browser/list`**

List contents of a directory.

**Step-by-step:**

```bash
# 1. List root directory
curl "http://localhost:8000/api/v1/browser/list?path=/Volumes/allDaStuffs"

# 2. Response
{
  "path": "/Volumes/allDaStuffs",
  "parent": "/Volumes",
  "items": [
    {
      "name": "homeserver",
      "path": "/Volumes/allDaStuffs/homeserver",
      "is_directory": true,
      "size": null,
      "modified": "2025-11-07T00:26:21.090000",
      "permissions": "rwx------",
      "is_readable": true
    },
    {
      "name": "document.pdf",
      "path": "/Volumes/allDaStuffs/document.pdf",
      "is_directory": false,
      "size": 1024000,
      "modified": "2025-11-06T15:30:00",
      "permissions": "rw-------",
      "is_readable": true
    }
  ],
  "total_items": 2
}

# 3. Browse subdirectory
curl "http://localhost:8000/api/v1/browser/list?path=/Volumes/allDaStuffs/homeserver"
```

**Using Python:**
```python
import requests

def browse_directory(path):
    url = "http://localhost:8000/api/v1/browser/list"
    response = requests.get(url, params={"path": path})

    if response.status_code == 200:
        data = response.json()
        print(f"Contents of {data['path']}:")

        # List directories first
        for item in data['items']:
            if item['is_directory']:
                print(f"  [DIR]  {item['name']}")

        # Then files
        for item in data['items']:
            if not item['is_directory']:
                size_mb = item['size'] / (1024**2)
                print(f"  [FILE] {item['name']} ({size_mb:.2f} MB)")
    else:
        print(f"Error: {response.json()['detail']}")

# Browse root
browse_directory("/Volumes/allDaStuffs")
```

**Query parameters:**
- `path` (required): Directory path to list

**Response fields:**
- `path`: Current directory absolute path
- `parent`: Parent directory path (null if root)
- `items`: Array of files and directories
  - `name`: File/directory name
  - `path`: Full absolute path
  - `is_directory`: Boolean
  - `size`: File size in bytes (null for directories)
  - `modified`: Last modified timestamp
  - `permissions`: Unix permissions (e.g., "rwxr-xr-x")
  - `is_readable`: Whether you can read this item

**Error responses:**
- `403`: Access denied (path not in allowed list)
- `404`: Directory not found
- `400`: Path is not a directory

**Use cases:**
- Build file browser UI
- Navigate directory tree
- Find files on external drive
- Explore server file system

---

### 3. Get File Info

**`GET /api/v1/browser/info`**

Get metadata for a specific file or directory.

**Step-by-step:**

```bash
# 1. Get file info
curl "http://localhost:8000/api/v1/browser/info?path=/Volumes/allDaStuffs/document.pdf"

# 2. Response
{
  "name": "document.pdf",
  "path": "/Volumes/allDaStuffs/document.pdf",
  "is_directory": false,
  "size": 1024000,
  "modified": "2025-11-06T15:30:00",
  "permissions": "rw-------",
  "is_readable": true
}
```

**Using Python:**
```python
import requests
from datetime import datetime

def get_file_info(path):
    url = "http://localhost:8000/api/v1/browser/info"
    response = requests.get(url, params={"path": path})

    if response.status_code == 200:
        info = response.json()

        print(f"Name: {info['name']}")
        print(f"Type: {'Directory' if info['is_directory'] else 'File'}")

        if not info['is_directory']:
            size_mb = info['size'] / (1024**2)
            print(f"Size: {size_mb:.2f} MB")

        modified = datetime.fromisoformat(info['modified'].replace('Z', '+00:00'))
        print(f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Permissions: {info['permissions']}")
        print(f"Readable: {info['is_readable']}")
    else:
        print(f"Error: {response.json()['detail']}")

get_file_info("/Volumes/allDaStuffs/document.pdf")
```

**Query parameters:**
- `path` (required): File or directory path

**Use cases:**
- Check if file exists
- Get file size before downloading
- Verify permissions
- Display file details in UI

---

### 4. Download File from Browser

**`GET /api/v1/browser/download`**

Download a file from the file system.

**Step-by-step:**

```bash
# 1. Download file from external drive
curl -O -J "http://localhost:8000/api/v1/browser/download?path=/Volumes/allDaStuffs/document.pdf"

# 2. Check file was downloaded
ls -lh document.pdf

# 3. Download file from specific location
curl "http://localhost:8000/api/v1/browser/download?path=/Volumes/allDaStuffs/homeserver/storage/abc123..." \
  -o downloaded.pdf
```

**Using Python:**
```python
import requests
import os

def download_file(path, save_as=None):
    url = "http://localhost:8000/api/v1/browser/download"
    response = requests.get(url, params={"path": path}, stream=True)

    if response.status_code == 200:
        # Extract filename from Content-Disposition header
        if save_as is None:
            content_disp = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disp:
                save_as = content_disp.split('filename=')[1].strip('"')
            else:
                save_as = os.path.basename(path)

        # Download file
        with open(save_as, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded to: {save_as}")
        return save_as
    else:
        print(f"Error: {response.json()['detail']}")
        return None

# Download file
download_file("/Volumes/allDaStuffs/document.pdf")

# Download with custom name
download_file("/Volumes/allDaStuffs/photo.jpg", "vacation_2024.jpg")
```

**Query parameters:**
- `path` (required): File path to download

**Error responses:**
- `403`: Access denied (path not in allowed list)
- `404`: File not found
- `400`: Path is a directory (cannot download)

**Use cases:**
- Access files on external drive
- Retrieve backup files
- Download media files
- Copy files from server

---

## Monitoring API

The Monitoring API provides real-time system and storage metrics.

### 1. System Metrics

**`GET /api/v1/monitoring/system`**

Get current system resource usage.

**Step-by-step:**

```bash
# 1. Get system metrics
curl http://localhost:8000/api/v1/monitoring/system

# 2. Response
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

**Using Python:**
```python
import requests

def get_system_metrics():
    url = "http://localhost:8000/api/v1/monitoring/system"
    response = requests.get(url)
    metrics = response.json()

    print("System Metrics:")
    print(f"CPU Usage: {metrics['cpu_percent']}%")
    print(f"Memory: {metrics['memory_used_gb']:.2f} GB / {metrics['memory_total_gb']:.2f} GB ({metrics['memory_percent']}%)")
    print(f"Disk: {metrics['disk_used_gb']:.2f} GB / {metrics['disk_total_gb']:.2f} GB ({metrics['disk_percent']}%)")
    print(f"Free Space: {metrics['disk_free_gb']:.2f} GB")

    # Alert if usage is high
    if metrics['cpu_percent'] > 80:
        print("⚠️  High CPU usage!")
    if metrics['memory_percent'] > 80:
        print("⚠️  High memory usage!")
    if metrics['disk_percent'] > 80:
        print("⚠️  Low disk space!")

get_system_metrics()
```

**Monitoring with polling:**
```python
import requests
import time

def monitor_system(interval=5):
    """Monitor system every N seconds"""
    while True:
        response = requests.get("http://localhost:8000/api/v1/monitoring/system")
        metrics = response.json()

        print(f"[{time.strftime('%H:%M:%S')}] CPU: {metrics['cpu_percent']}% | "
              f"Memory: {metrics['memory_percent']}% | "
              f"Disk: {metrics['disk_percent']}%")

        time.sleep(interval)

monitor_system(5)  # Poll every 5 seconds
```

**Response fields:**
- `cpu_percent`: CPU usage percentage (0-100)
- `memory_percent`: Memory usage percentage (0-100)
- `memory_used_gb`: Memory used in GB
- `memory_total_gb`: Total system memory in GB
- `disk_percent`: Disk usage percentage (0-100)
- `disk_used_gb`: Disk space used in GB
- `disk_total_gb`: Total disk space in GB
- `disk_free_gb`: Free disk space in GB

**Use cases:**
- System monitoring dashboards
- Resource alerts
- Capacity planning
- Performance monitoring

---

### 2. Storage Statistics

**`GET /api/v1/monitoring/storage`**

Get file storage statistics from database.

**Step-by-step:**

```bash
# 1. Get storage stats
curl http://localhost:8000/api/v1/monitoring/storage

# 2. Response
{
  "total_files": 15,
  "total_size_gb": 2.45,
  "storage_path": "/app/storage"
}
```

**Using Python:**
```python
import requests

def get_storage_stats():
    url = "http://localhost:8000/api/v1/monitoring/storage"
    response = requests.get(url)
    stats = response.json()

    print("Storage Statistics:")
    print(f"Total Files: {stats['total_files']:,}")
    print(f"Total Size: {stats['total_size_gb']:.2f} GB")
    print(f"Storage Path: {stats['storage_path']}")

    # Calculate average file size
    if stats['total_files'] > 0:
        avg_size_mb = (stats['total_size_gb'] * 1024) / stats['total_files']
        print(f"Average File Size: {avg_size_mb:.2f} MB")

get_storage_stats()
```

**Response fields:**
- `total_files`: Number of files in database
- `total_size_gb`: Total storage used in GB
- `storage_path`: Directory where files are stored

**Use cases:**
- Track storage growth
- Monitor file uploads
- Storage capacity planning
- Usage reports

---

### 3. Dashboard Metrics

**`GET /api/v1/monitoring/dashboard`**

Get all dashboard metrics (system + storage + uptime).

**Step-by-step:**

```bash
# 1. Get dashboard metrics
curl http://localhost:8000/api/v1/monitoring/dashboard

# 2. Response
{
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "memory_used_gb": 3.45,
    "memory_total_gb": 7.65,
    "disk_percent": 62.4,
    "disk_used_gb": 142.35,
    "disk_total_gb": 228.27,
    "disk_free_gb": 85.92
  },
  "storage": {
    "total_files": 15,
    "total_size_gb": 2.45,
    "storage_path": "/app/storage"
  },
  "uptime_seconds": 3600.5
}
```

**Using Python:**
```python
import requests
from datetime import timedelta

def get_dashboard():
    url = "http://localhost:8000/api/v1/monitoring/dashboard"
    response = requests.get(url)
    data = response.json()

    # System metrics
    print("=== System Resources ===")
    print(f"CPU: {data['system']['cpu_percent']}%")
    print(f"Memory: {data['system']['memory_percent']}%")
    print(f"Disk: {data['system']['disk_percent']}%")

    # Storage metrics
    print("\n=== File Storage ===")
    print(f"Files: {data['storage']['total_files']:,}")
    print(f"Size: {data['storage']['total_size_gb']:.2f} GB")

    # Uptime
    uptime = timedelta(seconds=int(data['uptime_seconds']))
    print(f"\n=== Server Info ===")
    print(f"Uptime: {uptime}")

get_dashboard()
```

**Response structure:**
- `system`: System metrics object
- `storage`: Storage statistics object
- `uptime_seconds`: Server uptime in seconds

**Use cases:**
- Display comprehensive dashboard
- Single endpoint for all metrics
- Monitoring overview
- Status page

---

### 4. WebSocket Real-time Metrics

**`WS /api/v1/monitoring/ws`**

WebSocket connection for real-time metrics updates.

**Step-by-step (JavaScript):**

```javascript
// 1. Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/monitoring/ws');

// 2. Handle connection open
ws.onopen = () => {
  console.log('Connected to monitoring WebSocket');
};

// 3. Handle incoming messages (every 2 seconds)
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  // Update UI with new metrics
  document.getElementById('cpu').textContent = data.system.cpu_percent + '%';
  document.getElementById('memory').textContent = data.system.memory_percent + '%';
  document.getElementById('disk').textContent = data.system.disk_percent + '%';
  document.getElementById('files').textContent = data.storage.total_files;

  console.log('Metrics updated:', data);
};

// 4. Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// 5. Handle close
ws.onclose = () => {
  console.log('WebSocket closed, reconnecting...');
  // Reconnect after 3 seconds
  setTimeout(() => {
    // Reconnect logic here
  }, 3000);
};

// 6. Close connection when done
// ws.close();
```

**Using Python (websockets library):**

```python
import asyncio
import websockets
import json

async def monitor_realtime():
    uri = "ws://localhost:8000/api/v1/monitoring/ws"

    async with websockets.connect(uri) as websocket:
        print("Connected to monitoring WebSocket")

        while True:
            try:
                # Receive message
                message = await websocket.recv()
                data = json.loads(message)

                # Display metrics
                print(f"CPU: {data['system']['cpu_percent']}% | "
                      f"Memory: {data['system']['memory_percent']}% | "
                      f"Disk: {data['system']['disk_percent']}% | "
                      f"Files: {data['storage']['total_files']}")

            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

# Run
asyncio.run(monitor_realtime())
```

**Message format:**
Same as `/api/v1/monitoring/dashboard` endpoint, sent every 2 seconds.

**Connection behavior:**
- Server sends metrics every 2 seconds automatically
- Connection stays open until client disconnects
- Auto-reconnect recommended on disconnect

**Use cases:**
- Real-time dashboards
- Live monitoring displays
- Alerts and notifications
- Streaming metrics to other systems

---

## Frontend Pages

### 1. Dashboard

**URL**: `http://localhost:8000/static/dashboard.html`

**Features:**
- Real-time system metrics (CPU, memory, disk)
- File storage statistics
- Server uptime display
- WebSocket auto-updates every 2 seconds
- Auto-reconnect on disconnect
- Warning colors for high usage (>80%)

**How to use:**
1. Open URL in browser
2. Metrics update automatically
3. Connection status shown in top-right
4. View system health at a glance

---

### 2. File Manager

**URL**: `http://localhost:8000/static/files.html`

**Features:**
- Upload files with drag-and-drop
- Add tags for organization
- View all uploaded files
- Download files with one click
- Delete files with confirmation
- Filter files by tags

**How to use:**

**Upload a file:**
1. Click "Choose File" or drag file to upload area
2. (Optional) Add comma-separated tags
3. Click "Upload"
4. File appears in list below

**Download a file:**
1. Find file in list
2. Click "Download" button
3. File downloads to your device

**Delete a file:**
1. Find file in list
2. Click "Delete" button
3. Confirm deletion in popup
4. File is removed permanently

**Filter by tag:**
1. Files are displayed with colored tags
2. Click on a tag to filter (future feature)

---

### 3. File Browser

**URL**: `http://localhost:8000/static/browser.html`

**Features:**
- Browse external drive and file system
- Navigate directories with breadcrumb path
- View file metadata (size, date, permissions)
- Download files from anywhere
- Click folders to browse
- Click breadcrumb path to go back

**How to use:**

**Start browsing:**
1. Click one of the root location buttons (e.g., "/Volumes/allDaStuffs")
2. Directory contents load below

**Navigate directories:**
1. Click any folder to browse inside
2. Breadcrumb path shows current location
3. Click any part of breadcrumb to go back

**Download a file:**
1. Navigate to file location
2. Click "Download" button next to file
3. File downloads to your device

**View file details:**
- Name, size, modified date, and permissions shown for each file
- Folders shown with folder icon
- Files shown with file icon

---

## Common Workflows

### Workflow 1: Backup Important Documents

```bash
# 1. Upload multiple files with tags
for file in ~/Documents/*.pdf; do
  curl -X POST http://localhost:8000/api/v1/files/upload \
    -F "file=@$file" \
    -F "tags=backup,documents,$(date +%Y-%m)"
done

# 2. Verify uploads
curl http://localhost:8000/api/v1/files/list?tag=backup

# 3. Check storage usage
curl http://localhost:8000/api/v1/monitoring/storage
```

### Workflow 2: Find and Download Files

```bash
# 1. List all files
curl http://localhost:8000/api/v1/files/list > files.json

# 2. Extract file ID (using jq)
FILE_ID=$(jq -r '.files[0].id' files.json)

# 3. Get metadata
curl http://localhost:8000/api/v1/files/$FILE_ID/metadata

# 4. Download file
curl -O -J http://localhost:8000/api/v1/files/$FILE_ID/download
```

### Workflow 3: Monitor Server Health

```bash
# 1. Check if server is healthy
curl http://localhost:8000/health

# 2. Get system metrics
curl http://localhost:8000/api/v1/monitoring/system

# 3. Check storage usage
curl http://localhost:8000/api/v1/monitoring/storage

# 4. Get complete dashboard
curl http://localhost:8000/api/v1/monitoring/dashboard | jq
```

### Workflow 4: Browse External Drive

```bash
# 1. Get allowed root paths
curl http://localhost:8000/api/v1/browser/roots

# 2. List root directory
curl "http://localhost:8000/api/v1/browser/list?path=/Volumes/allDaStuffs"

# 3. Browse subdirectory
curl "http://localhost:8000/api/v1/browser/list?path=/Volumes/allDaStuffs/Photos"

# 4. Download a file
curl -O -J "http://localhost:8000/api/v1/browser/download?path=/Volumes/allDaStuffs/Photos/vacation.jpg"
```

### Workflow 5: Automated Cleanup

```python
import requests
from datetime import datetime, timedelta

# Delete files older than 30 days with specific tag
url = "http://localhost:8000/api/v1/files/list?tag=temporary"
response = requests.get(url)
files = response.json()['files']

cutoff = datetime.now() - timedelta(days=30)

for file in files:
    upload_date = datetime.fromisoformat(file['upload_date'].replace('Z', '+00:00'))

    if upload_date < cutoff:
        print(f"Deleting old file: {file['filename']}")
        delete_url = f"http://localhost:8000/api/v1/files/{file['id']}"
        requests.delete(delete_url)
```

---

## Error Handling

### Common Error Responses

**404 Not Found:**
```json
{
  "detail": "File not found"
}
```

**403 Forbidden:**
```json
{
  "detail": "Access to /path/to/file is not allowed"
}
```

**400 Bad Request:**
```json
{
  "detail": "/path is not a directory"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error downloading file: ..."
}
```

### Error Handling Best Practices

**Python example:**
```python
import requests

def safe_api_call(url, method='GET', **kwargs):
    try:
        if method == 'GET':
            response = requests.get(url, **kwargs)
        elif method == 'POST':
            response = requests.post(url, **kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, **kwargs)

        response.raise_for_status()  # Raise exception for 4xx/5xx
        return response.json()

    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server")
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Detail: {e.response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None

# Usage
data = safe_api_call("http://localhost:8000/api/v1/files/list")
if data:
    print(f"Found {data['total']} files")
```

---

## Rate Limits & Performance

### Current Limits
- **No rate limits** currently implemented
- All endpoints are public (no authentication)
- WebSocket updates every 2 seconds
- File upload size: Limited by server memory (recommend <100MB per file)

### Performance Tips

**For large file uploads:**
- Use streaming uploads when possible
- Consider chunking files >100MB
- Monitor disk space before uploading

**For listing many files:**
- Pagination not yet implemented (returns all files)
- Consider adding limit/offset parameters (future)
- Use tag filtering to reduce result size

**For monitoring:**
- Use WebSocket for real-time updates (more efficient than polling)
- Poll REST endpoints no more than once per second
- Cache results when possible

---

## Planned Features

See full list in API_ENDPOINTS.md, including:

- **Authentication** (OAuth2/JWT)
- **Search** (full-text, semantic)
- **Media Server** (streaming, transcoding)
- **Home Automation** (IoT devices, scenes, rules)
- **Advanced Monitoring** (network stats, processes, logs)
- **AI Integration** (chatbot, file analysis)
- **Backup Management** (automated backups, restore)

---

## Additional Resources

- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **GitHub Repository**: https://github.com/nathanLittle-Rea/HomeServer
- **Complete Endpoint List**: See API_ENDPOINTS.md

---

## Support

For issues or questions:
1. Check server logs: `docker-compose logs homeserver`
2. View API documentation: http://localhost:8000/docs
3. Open GitHub issue: https://github.com/nathanLittle-Rea/HomeServer/issues

---

**Last Updated**: 2025-11-06
**Version**: 0.1.0
**Branch**: refinement
