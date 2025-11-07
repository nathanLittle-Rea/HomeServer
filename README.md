# HomeServer

Multi-purpose home server running on Mac Mini, providing integrated services for media streaming, file storage, home automation, AI assistant, monitoring, and web hosting.

## Features (Planned)

- **Media Streaming**: Video/audio streaming with transcoding
- **File Storage**: Network file sharing with version control
- **Home Automation**: Smart device control and ML-based automation
- **AI Assistant**: Natural language interface for home control
- **Monitoring Dashboard**: System health and metrics
- **Web Server**: Host personal web applications

## Tech Stack

- **Runtime**: Python 3.11+
- **Framework**: FastAPI (async)
- **Database**: AWS DynamoDB
- **Deployment**: Docker + Docker Compose
- **External Access**: Twingate (zero-trust VPN)

## Quick Start

### Local Development

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Ensure external drive is mounted
ls /Volumes/allDaStuffs  # Should show your drive

# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

**Note**: Files are stored on the external drive at `/Volumes/allDaStuffs/homeserver/storage`. Make sure this drive is mounted before starting the container.

The server will be available at `http://localhost:8000`

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Development

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy src/

# Run all checks
black . && ruff check . && mypy src/
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src tests/
```

## Project Status

Currently in Phase 2: File Storage Service (Active)

**Completed:**
- [x] Basic project structure
- [x] FastAPI application with health checks
- [x] Docker configuration
- [x] Development tooling (Black, Ruff, mypy)
- [x] File storage service with external drive support
  - Upload, download, list, delete files
  - Tag-based organization
  - Files stored on `/Volumes/allDaStuffs` external drive

**In Progress:**
- [ ] DynamoDB integration for metadata persistence
- [ ] Twingate setup for external access

**Planned:**
- [ ] Media streaming
- [ ] Home automation
- [ ] AI assistant

## Architecture

Modular microservices pattern with:
- Async-first design for I/O operations
- RESTful APIs for all services
- Hybrid deployment (local + AWS DynamoDB)
- Secure external access via Twingate

See `.claude/project.context.md` for detailed context and guidelines.
