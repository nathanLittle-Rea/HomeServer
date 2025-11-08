# HomeServer Project Context

## Overview
<!-- Describe what this project does and its main purpose -->
This is a home server application for [describe your use case].

## Details

### First Commit
  🎉 https://github.com/nathanLittle-Rea/HomeServer

  What was pushed:
  - ✓ 30 files
  - ✓ 4,734 lines of code
  - ✓ Complete documentation (DOCUMENTATION.md + SUMMARY.md)
  - ✓ All source code (Python backend + HTML frontend)
  - ✓ Docker configuration
  - ✓ Requirements and dependencies
  - ✓ README with project overview

  Repository details:
  - Visibility: Public
  - Description: "Multi-purpose home server with file storage and real-time monitoring. Built with FastAPI, PostgreSQL, and Docker."
  - Branch: main
  - Remote: origin (set up and tracking)

  You can now:
  1. View your repo at: https://github.com/nathanLittle-Rea/HomeServer
  2. Clone it elsewhere: git clone https://github.com/nathanLittle-Rea/HomeServer.git
  3. Make changes and push: git add . && git commit -m "message" && git push
  4. Share it with others
  5. Add topics/tags to make it discoverable
  
### Second Commit

  What we built:
  - Complete file browser for exploring your external drive and file system
  - Browse directories, view metadata, and download files
  - Read-only access to /Volumes/allDaStuffs
  - Beautiful dark-themed UI with breadcrumb navigation

  Features:
  - 📁 Directory Navigation - Click folders to browse, breadcrumb path to go back
  - 📊 File Metadata - View size, modified date, and permissions
  - ⬇️ Download - Download any file with one click
  - 🔒 Permission Control - Only browse allowed paths
  - 🎨 Consistent UI - Matches dashboard and file manager design
  - 🔗 Navigation Links - Easy switching between all three pages

  API Endpoints:
  - GET /api/v1/browser/roots - List allowed root paths
  - GET /api/v1/browser/list?path=... - List directory contents
  - GET /api/v1/browser/info?path=... - Get file metadata
  - GET /api/v1/browser/download?path=... - Download file

  Access:
  - Local: http://localhost:8000/static/browser.html
  - Network: http://192.168.0.40:8000/static/browser.html

  GitHub:
  - Branch: refinement
  - Commit: Added file browser with 891 insertions across 9 files
  - Push URL: https://github.com/nathanLittle-Rea/HomeServer/pull/new/refinement

  Now you have 3 interfaces:
  1. Dashboard - Real-time monitoring (CPU, memory, disk, files)
  2. File Manager - Upload and manage files via API
  3. File Browser - Browse and download existing files on external drive  

## Tech Stack
<!-- Update with your actual stack -->
- **Language**:

- **Framework**:
- **Database**:
- **Other tools**:

## Project Structure
```
HomeServer/
├── .claude/           # Claude Code configuration
└── ...                # Add your directory structure here
```

## Architecture
<!-- Describe your architecture patterns -->
-

## Development Guidelines

### Coding Standards
-
-

### Testing Approach
-
-

### Key Conventions
-
-

## Important Context
<!-- Add any domain-specific knowledge or important context -->

### Security Considerations
-

### Performance Notes
-

## Common Tasks
<!-- Document frequent development tasks -->

### Setup
```bash
# Add setup commands
```

### Running Locally
```bash
# Add run commands
```

### Deployment
<!-- Describe deployment process -->

## External Dependencies
<!-- List important external services, APIs, etc. -->

## Known Issues / Tech Debt
<!-- Track ongoing concerns -->
-

## Additional Notes
<!-- Any other relevant context -->
