# HomeServer Project Context

## Overview
Multi-purpose home server providing integrated services for media streaming, file storage, home automation, AI-powered assistant, monitoring, and web hosting. Designed for hybrid deployment (local + cloud) with secure external access.

**Hardware**: Running on a Mac Mini (local server)

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI (async web framework with automatic API documentation)
- **Database**: AWS DynamoDB (NoSQL for flexibility across services)
- **Containerization**: Docker & Docker Compose
- **External Access**: Twingate (zero-trust network access)
- **AI/ML**: TBD (for home automation ML and assistant functionality)
- **Other tools**:
  - Black (code formatting)
  - Ruff (linting)
  - mypy (type checking)
  - pytest (testing)

## Project Structure
```
HomeServer/
├── .claude/              # Claude Code configuration
├── src/
│   ├── api/             # FastAPI routes and endpoints
│   ├── services/        # Business logic for each service
│   │   ├── media/       # Media streaming service
│   │   ├── files/       # File storage/sharing service
│   │   ├── automation/  # Home automation service
│   │   ├── ai/          # AI assistant and ML models
│   │   ├── monitoring/  # System monitoring and dashboards
│   │   └── web/         # Web server functionality
│   ├── models/          # Data models and schemas
│   ├── utils/           # Shared utilities
│   └── config.py        # Configuration management
├── tests/               # Test suite
├── docker/              # Docker configurations
├── scripts/             # Deployment and utility scripts
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project metadata and tool configs
└── README.md
```

## Architecture
- **Microservices Pattern**: Each major service (media, files, automation, AI) is modular
- **API-First**: RESTful APIs with FastAPI for all services
- **Async Operations**: Leverage FastAPI's async capabilities for I/O-bound operations
- **Hybrid Deployment**:
  - Local server for media storage, file access, and AI inference
  - DynamoDB in AWS for persistent data storage
  - Twingate for secure external access without exposing ports
- **Event-Driven**: Use async events for home automation triggers and AI assistant interactions

## Development Guidelines

### Coding Standards
- **Type Hints Required**: All functions must have type hints; enforced by mypy
- **Code Formatting**: Use Black with default settings (88 char line length)
- **Linting**: Ruff for fast, comprehensive linting (replaces flake8, isort, pylint)
- **Async/Await**: Prefer async functions for I/O operations (API calls, file I/O, DB queries)
- **Naming Conventions**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

### Testing Approach
- **Framework**: pytest for all tests
- **Coverage**: Focus on critical paths and business logic (not aiming for 100%)
- **Test Types**:
  - Unit tests for service logic
  - Integration tests for API endpoints
  - Mock external dependencies (AWS, AI models)
- **Location**: Mirror `src/` structure in `tests/` directory

### Key Conventions
- One service per module in `src/services/`
- Pydantic models for all API request/response schemas
- Environment variables for configuration (never hardcode secrets)
- Use dependency injection for database and external service connections
- Structured logging for all services (JSON format for monitoring)

## Important Context

### Services Overview
1. **Media Streaming**: Video/audio streaming with transcoding support
2. **File Storage**: Network file sharing with version control
3. **Home Automation**: Smart device control, automation rules, ML-based predictions
4. **AI Assistant**: Natural language interface for home control and queries
5. **Monitoring Dashboard**: System health, logs, metrics visualization
6. **Web Server**: Host personal web applications and services

### Security Considerations
- **Zero Trust Access**: All external access via Twingate VPN (no port forwarding required)
- **Twingate Connector**: Runs locally, establishes outbound-only connection to Twingate cloud
- **No Router Configuration**: No inbound ports opened on router
- **Secrets Management**: Use environment variables, never commit secrets
- **AWS IAM**: Least privilege access for DynamoDB operations
- **API Authentication**: Implement JWT or API key authentication for all endpoints
- **Input Validation**: Pydantic models validate all inputs
- **File Access**: Sandboxed file operations, validate paths to prevent traversal

### Performance Notes
- **Async First**: Use async/await for all I/O to maximize throughput
- **Caching**: Cache frequently accessed media metadata and file listings
- **AI Model Loading**: Keep models in memory to avoid reload overhead
- **Connection Pooling**: Reuse database and AWS SDK connections
- **Streaming**: Use streaming responses for large files and media

## Common Tasks

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials and other configs

# Run linting and formatting
ruff check .
black .
mypy src/
```

### Running Locally
```bash
# Development server with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# With Docker Compose
docker-compose up --build

# Run tests
pytest

# Run tests with coverage
pytest --cov=src tests/
```

### Deployment
- **Local Server**: Docker Compose on home server hardware (Mac Mini)
- **External Storage**: Files stored on `/Volumes/allDaStuffs/homeserver/storage`
  - Ensure drive is mounted before starting container
  - Drive auto-mounts on boot
- **Twingate Setup**: Configure Twingate connector for secure access
- **AWS**: Ensure IAM roles and DynamoDB tables are provisioned
- **Environment**: Set production environment variables
- **Monitoring**: Configure logging to monitoring service

## External Dependencies
- **AWS Services**:
  - DynamoDB for data persistence
  - IAM for access management
- **Twingate**: Zero-trust network access
- **AI/ML Models**: TBD (likely Ollama for local LLM, scikit-learn for automation ML)
- **Media Libraries**: FFmpeg for transcoding
- **Home Automation Protocols**: TBD (Zigbee, Z-Wave, MQTT)

## Known Issues / Tech Debt
- Project is in initial setup phase
- Need to determine specific AI/ML stack for assistant and automation
- Home automation protocol integration to be defined
- Media transcoding optimization strategy TBD

## Additional Notes
- This is a personal project for learning and home use
- Prioritize security and privacy (all data stays local or in personal AWS account)
- Design for extensibility - easy to add new services and integrations
- Document decisions and learnings as the project evolves

## Communication Preferences
- Add occasional humor (Feynman-style: curious, playful, demystifying complexity)
- Keep explanations clear and approachable
- Don't take things too seriously, but stay technically accurate
