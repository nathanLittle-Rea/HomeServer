# Private Git Server & Bitwarden Server Integration Plan

## Overview

Adding self-hosted Git and password management to the HomeServer project.

**Date:** 2025-11-07
**Status:** Planning Phase

---

## Table of Contents
1. [Service Recommendations](#service-recommendations)
2. [Architecture Integration](#architecture-integration)
3. [Git Server Implementation](#git-server-implementation)
4. [Bitwarden Server Implementation](#bitwarden-server-implementation)
5. [Authentication Integration](#authentication-integration)
6. [Docker Compose Configuration](#docker-compose-configuration)
7. [Reverse Proxy Setup](#reverse-proxy-setup)
8. [Security Considerations](#security-considerations)
9. [Backup Strategy](#backup-strategy)
10. [Implementation Roadmap](#implementation-roadmap)

---

## Service Recommendations

### Git Server: Gitea

**Why Gitea?**
- Lightweight (written in Go, ~30MB Docker image)
- GitHub-like interface (familiar UX)
- Built-in features: Issues, Pull Requests, Wiki, Projects
- SQLite/PostgreSQL/MySQL support (we can use our existing PostgreSQL)
- REST API for integration
- Low resource usage (~100-200MB RAM)
- Active development and community

**Alternatives Considered:**
- GitLab CE: Too heavy for home server (requires 4GB+ RAM)
- Gogs: Older, less active development than Gitea
- cgit: Too minimal, lacks modern features

### Password Manager: Vaultwarden

**Why Vaultwarden?**
- Unofficial Bitwarden-compatible server (written in Rust)
- Extremely lightweight (~10MB Docker image, ~10MB RAM)
- 100% compatible with official Bitwarden clients
- All premium features free (TOTP, attachments, etc.)
- SQLite/PostgreSQL/MySQL support
- WebSocket support for live sync
- Admin panel for user management

**Alternatives Considered:**
- Official Bitwarden: Too heavy, complex deployment
- KeePass/KeePassXC: File-based, no sync server
- Pass: CLI-only, less user-friendly

---

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                         Nginx Reverse Proxy                      │
│                         (Port 80/443)                            │
└─────┬───────────────┬─────────────────┬────────────┬───────────┘
      │               │                 │            │
      │               │                 │            │
┌─────▼──────┐  ┌────▼─────┐  ┌────────▼──────┐  ┌─▼─────────┐
│ HomeServer │  │  Gitea   │  │  Vaultwarden  │  │  Existing │
│  FastAPI   │  │   Git    │  │   Password    │  │  Services │
│  :8000     │  │  :3000   │  │    Manager    │  │           │
└─────┬──────┘  └────┬─────┘  │    :8080      │  └───────────┘
      │               │        └────────┬──────┘
      │               │                 │
      └───────────────┴─────────────────┴──────────────────┐
                                                            │
                                              ┌─────────────▼────────────┐
                                              │   PostgreSQL Database    │
                                              │                          │
                                              │  - homeserver DB         │
                                              │  - gitea DB              │
                                              │  - vaultwarden DB        │
                                              └──────────────────────────┘
```

### URL Structure
- `homeserver.local` or `home.yourdomain.com` - Main HomeServer API/UI
- `git.homeserver.local` or `git.yourdomain.com` - Gitea
- `vault.homeserver.local` or `vault.yourdomain.com` - Vaultwarden

---

## Git Server Implementation

### 1. Gitea Docker Configuration

```yaml
# Add to docker-compose.yml
gitea:
  image: gitea/gitea:latest
  container_name: homeserver-gitea
  environment:
    - USER_UID=1000
    - USER_GID=1000
    - GITEA__database__DB_TYPE=postgres
    - GITEA__database__HOST=postgres:5432
    - GITEA__database__NAME=gitea
    - GITEA__database__USER=gitea
    - GITEA__database__PASSWD=gitea_password
    - GITEA__server__DOMAIN=git.homeserver.local
    - GITEA__server__SSH_DOMAIN=git.homeserver.local
    - GITEA__server__ROOT_URL=http://git.homeserver.local/
    - GITEA__server__HTTP_PORT=3000
    - GITEA__server__SSH_PORT=2222
    - GITEA__security__INSTALL_LOCK=true
    - GITEA__service__DISABLE_REGISTRATION=false
    - GITEA__service__REQUIRE_SIGNIN_VIEW=true
  restart: always
  networks:
    - homeserver-network
  volumes:
    - gitea-data:/data
    - /etc/timezone:/etc/timezone:ro
    - /etc/localtime:/etc/localtime:ro
  ports:
    - "3000:3000"  # HTTP
    - "2222:2222"  # SSH
  depends_on:
    - postgres
```

### 2. Database Setup

```sql
-- Create Gitea database and user
CREATE DATABASE gitea;
CREATE USER gitea WITH PASSWORD 'gitea_password';
GRANT ALL PRIVILEGES ON DATABASE gitea TO gitea;
```

### 3. Gitea Features

**Repository Management:**
- Create unlimited private/public repos
- Branch protection rules
- Web-based file editor
- Commit history and diffs
- Release management with attachments

**Collaboration:**
- Issues with labels, milestones, assignees
- Pull Requests with code review
- Wiki for documentation
- Project boards (Kanban)
- Organizations and teams

**Integration:**
- Webhooks for CI/CD
- API access tokens
- Git LFS support
- Markdown rendering
- SSH and HTTPS clone

### 4. API Integration with HomeServer

```python
# src/services/git/gitea_client.py
import httpx
from typing import List, Optional

class GiteaClient:
    """Client for interacting with Gitea API."""

    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "Authorization": f"token {api_token}",
            "Content-Type": "application/json",
        }

    async def create_repo(
        self,
        name: str,
        description: str = "",
        private: bool = True,
        auto_init: bool = True,
    ) -> dict:
        """Create a new repository."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/user/repos",
                headers=self.headers,
                json={
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": auto_init,
                },
            )
            response.raise_for_status()
            return response.json()

    async def list_repos(self, username: Optional[str] = None) -> List[dict]:
        """List repositories."""
        endpoint = f"/api/v1/user/repos" if not username else f"/api/v1/users/{username}/repos"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def delete_repo(self, owner: str, repo: str) -> bool:
        """Delete a repository."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/v1/repos/{owner}/{repo}",
                headers=self.headers,
            )
            return response.status_code == 204
```

---

## Bitwarden Server Implementation

### 1. Vaultwarden Docker Configuration

```yaml
# Add to docker-compose.yml
vaultwarden:
  image: vaultwarden/server:latest
  container_name: homeserver-vaultwarden
  environment:
    - DATABASE_URL=postgresql://vaultwarden:vaultwarden_password@postgres:5432/vaultwarden
    - ADMIN_TOKEN=${VAULTWARDEN_ADMIN_TOKEN}  # Generate with: openssl rand -base64 48
    - DOMAIN=https://vault.homeserver.local
    - SIGNUPS_ALLOWED=true
    - INVITATIONS_ALLOWED=true
    - WEBSOCKET_ENABLED=true
    - SMTP_HOST=${SMTP_HOST}
    - SMTP_FROM=${SMTP_FROM}
    - SMTP_PORT=${SMTP_PORT}
    - SMTP_USERNAME=${SMTP_USERNAME}
    - SMTP_PASSWORD=${SMTP_PASSWORD}
  restart: always
  networks:
    - homeserver-network
  volumes:
    - vaultwarden-data:/data
  ports:
    - "8080:80"
    - "3012:3012"  # WebSocket port
  depends_on:
    - postgres
```

### 2. Database Setup

```sql
-- Create Vaultwarden database and user
CREATE DATABASE vaultwarden;
CREATE USER vaultwarden WITH PASSWORD 'vaultwarden_password';
GRANT ALL PRIVILEGES ON DATABASE vaultwarden TO vaultwarden;
```

### 3. Vaultwarden Features

**Password Management:**
- Unlimited passwords, notes, identities, cards
- Secure notes with rich text
- TOTP 2FA token generator (premium feature, free in Vaultwarden)
- File attachments (premium feature, free in Vaultwarden)
- Password generator with configurable rules
- Password strength auditing

**Organization Features:**
- Shared vaults for families/teams
- Collections for organizing items
- Granular permissions
- Activity logs

**Security:**
- End-to-end encryption (client-side)
- Master password never sent to server
- Optional 2FA for login (TOTP, U2F, Duo, email)
- Emergency access
- Vault timeout options

**Client Support:**
- Web vault (included)
- Browser extensions (Chrome, Firefox, Safari, Edge)
- Mobile apps (iOS, Android)
- Desktop apps (Windows, macOS, Linux)
- CLI for scripting

### 4. API Integration (Optional)

Vaultwarden is primarily used through Bitwarden clients, but you can integrate:

```python
# src/services/vault/vaultwarden_client.py
import httpx
from typing import List, Optional

class VaultwardenClient:
    """Client for Vaultwarden admin API."""

    def __init__(self, base_url: str, admin_token: str):
        self.base_url = base_url.rstrip('/')
        self.admin_token = admin_token

    async def list_users(self) -> List[dict]:
        """List all users (admin only)."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/admin/users",
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )
            response.raise_for_status()
            return response.json()

    async def invite_user(self, email: str) -> dict:
        """Invite a new user (admin only)."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/admin/invite",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                json={"email": email},
            )
            response.raise_for_status()
            return response.json()
```

---

## Authentication Integration

### Option 1: Separate Authentication (Recommended for Start)

Each service maintains its own user database:
- **HomeServer**: JWT authentication (already implemented)
- **Gitea**: Built-in user management
- **Vaultwarden**: Built-in user management

**Pros:**
- Simple to set up
- Services work independently
- No complex SSO configuration

**Cons:**
- Multiple sets of credentials
- Manual user management across services

### Option 2: SSO with OAuth2/OIDC (Future Enhancement)

Implement HomeServer as OAuth2 provider:
- **HomeServer**: Acts as identity provider
- **Gitea**: OAuth2 client (Gitea supports OAuth2)
- **Vaultwarden**: Currently doesn't support SSO (community feature request)

**Implementation Steps:**
1. Add OAuth2 server to HomeServer (using Authlib)
2. Configure Gitea to use HomeServer OAuth2
3. Single sign-on for HomeServer + Gitea

### Option 3: LDAP Integration (Advanced)

Set up OpenLDAP container:
- All services authenticate against LDAP
- Centralized user management
- More complex to maintain

---

## Docker Compose Configuration

### Complete docker-compose.yml

```yaml
version: '3.8'

services:
  # Existing services...
  homeserver:
    # ... existing config

  postgres:
    # ... existing config
    # Add initialization for new databases
    environment:
      - POSTGRES_MULTIPLE_DATABASES=homeserver,gitea,vaultwarden

  # New Git Server
  gitea:
    image: gitea/gitea:1.21
    container_name: homeserver-gitea
    environment:
      - USER_UID=1000
      - USER_GID=1000
      - GITEA__database__DB_TYPE=postgres
      - GITEA__database__HOST=postgres:5432
      - GITEA__database__NAME=gitea
      - GITEA__database__USER=gitea
      - GITEA__database__PASSWD=${GITEA_DB_PASSWORD}
      - GITEA__server__DOMAIN=${GITEA_DOMAIN:-git.homeserver.local}
      - GITEA__server__ROOT_URL=https://${GITEA_DOMAIN:-git.homeserver.local}/
      - GITEA__server__HTTP_PORT=3000
      - GITEA__server__SSH_PORT=2222
      - GITEA__security__INSTALL_LOCK=true
      - GITEA__service__DISABLE_REGISTRATION=${GITEA_DISABLE_REGISTRATION:-false}
    restart: always
    networks:
      - homeserver-network
    volumes:
      - gitea-data:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "3000:3000"
      - "2222:2222"
    depends_on:
      - postgres

  # New Password Manager
  vaultwarden:
    image: vaultwarden/server:1.30.1-alpine
    container_name: homeserver-vaultwarden
    environment:
      - DATABASE_URL=postgresql://vaultwarden:${VAULTWARDEN_DB_PASSWORD}@postgres:5432/vaultwarden
      - ADMIN_TOKEN=${VAULTWARDEN_ADMIN_TOKEN}
      - DOMAIN=https://${VAULTWARDEN_DOMAIN:-vault.homeserver.local}
      - SIGNUPS_ALLOWED=${VAULTWARDEN_SIGNUPS_ALLOWED:-true}
      - WEBSOCKET_ENABLED=true
      - SMTP_HOST=${SMTP_HOST:-}
      - SMTP_FROM=${SMTP_FROM:-}
      - SMTP_PORT=${SMTP_PORT:-587}
      - SMTP_SECURITY=${SMTP_SECURITY:-starttls}
      - SMTP_USERNAME=${SMTP_USERNAME:-}
      - SMTP_PASSWORD=${SMTP_PASSWORD:-}
    restart: always
    networks:
      - homeserver-network
    volumes:
      - vaultwarden-data:/data
    ports:
      - "8080:80"
      - "3012:3012"
    depends_on:
      - postgres

  # Optional: Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: homeserver-nginx
    restart: always
    networks:
      - homeserver-network
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - homeserver
      - gitea
      - vaultwarden

networks:
  homeserver-network:
    driver: bridge

volumes:
  postgres-data:
  homeserver-data:
  gitea-data:
  vaultwarden-data:
```

---

## Reverse Proxy Setup

### Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    # Upstream servers
    upstream homeserver {
        server homeserver:8000;
    }

    upstream gitea {
        server gitea:3000;
    }

    upstream vaultwarden {
        server vaultwarden:80;
    }

    # HomeServer - Main application
    server {
        listen 80;
        server_name homeserver.local home.yourdomain.com;

        client_max_body_size 100M;

        location / {
            proxy_pass http://homeserver;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://homeserver;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }

    # Gitea - Git server
    server {
        listen 80;
        server_name git.homeserver.local git.yourdomain.com;

        client_max_body_size 500M;

        location / {
            proxy_pass http://gitea;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # Vaultwarden - Password manager
    server {
        listen 80;
        server_name vault.homeserver.local vault.yourdomain.com;

        client_max_body_size 50M;

        location / {
            proxy_pass http://vaultwarden;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Vaultwarden WebSocket
        location /notifications/hub {
            proxy_pass http://vaultwarden:3012;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### SSL/TLS Configuration (Production)

For production, add SSL certificates:

```bash
# Generate self-signed certificates (for local testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/homeserver.key \
  -out nginx/ssl/homeserver.crt

# Or use Let's Encrypt with certbot
certbot certonly --standalone -d git.yourdomain.com
certbot certonly --standalone -d vault.yourdomain.com
```

---

## Security Considerations

### 1. Network Security

**Firewall Rules:**
```bash
# Only expose necessary ports
# 80/443: HTTP/HTTPS (Nginx)
# 2222: SSH for Git (Gitea)

# Block direct access to service ports
# 3000 (Gitea), 8000 (HomeServer), 8080 (Vaultwarden)
```

**Docker Network Isolation:**
- All services on private `homeserver-network`
- Only Nginx exposed to host network
- Services communicate via internal DNS

### 2. Vaultwarden Security

**Critical Settings:**
```bash
# Generate strong admin token
openssl rand -base64 48

# Disable signups after initial setup
SIGNUPS_ALLOWED=false

# Enable email invitations only
INVITATIONS_ALLOWED=true

# Require email verification
SIGNUPS_VERIFY=true
```

**2FA Enforcement:**
- Enable 2FA for all admin accounts
- Encourage users to enable TOTP
- Consider U2F/WebAuthn for hardware keys

### 3. Gitea Security

**SSH Key Management:**
- Disable password authentication for Git operations
- Require SSH keys or personal access tokens
- Regular key rotation policy

**Repository Access:**
```ini
# In Gitea app.ini
[security]
INSTALL_LOCK = true
SECRET_KEY = <generate-with-gitea-command>

[service]
DISABLE_REGISTRATION = true  # After initial setup
REQUIRE_SIGNIN_VIEW = true   # Private by default
```

### 4. Backup Security

**Encrypted Backups:**
```bash
# Backup with encryption
tar czf - /path/to/data | \
  gpg --symmetric --cipher-algo AES256 > backup.tar.gz.gpg

# Restore
gpg --decrypt backup.tar.gz.gpg | tar xzf -
```

---

## Backup Strategy

### 1. PostgreSQL Backups

```bash
#!/bin/bash
# backup.sh - Daily database backup

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup all databases
docker-compose exec -T postgres pg_dumpall -U homeserver | \
  gzip > "${BACKUP_DIR}/all_databases_${DATE}.sql.gz"

# Backup individual databases
for DB in homeserver gitea vaultwarden; do
  docker-compose exec -T postgres pg_dump -U homeserver ${DB} | \
    gzip > "${BACKUP_DIR}/${DB}_${DATE}.sql.gz"
done

# Keep only last 30 days
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete
```

### 2. Volume Backups

```bash
#!/bin/bash
# backup_volumes.sh - Backup Docker volumes

BACKUP_DIR="/backups/volumes"
DATE=$(date +%Y%m%d_%H%M%S)

# Gitea data
docker run --rm \
  -v homeserver_gitea-data:/data \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/gitea_${DATE}.tar.gz /data

# Vaultwarden data
docker run --rm \
  -v homeserver_vaultwarden-data:/data \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/vaultwarden_${DATE}.tar.gz /data

# Keep only last 30 days
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +30 -delete
```

### 3. Automated Backups with Cron

```cron
# /etc/cron.d/homeserver-backup

# Database backup - Daily at 2 AM
0 2 * * * root /opt/homeserver/scripts/backup.sh

# Volume backup - Daily at 3 AM
0 3 * * * root /opt/homeserver/scripts/backup_volumes.sh

# Upload to remote storage - Daily at 4 AM
0 4 * * * root rclone sync /backups remote:homeserver-backups
```

---

## Implementation Roadmap

### Phase 1: Gitea Setup (Week 1)
- [ ] Add Gitea service to docker-compose.yml
- [ ] Create Gitea database and user
- [ ] Configure Gitea environment variables
- [ ] Start Gitea container and complete web setup
- [ ] Create admin account
- [ ] Test repository creation
- [ ] Configure SSH access
- [ ] Document Git workflow for team

### Phase 2: Vaultwarden Setup (Week 1)
- [ ] Add Vaultwarden service to docker-compose.yml
- [ ] Create Vaultwarden database and user
- [ ] Generate admin token
- [ ] Configure SMTP for email notifications
- [ ] Start Vaultwarden container
- [ ] Access admin panel and verify setup
- [ ] Create test user account
- [ ] Test Bitwarden browser extension connection
- [ ] Import existing passwords (if any)
- [ ] Document password management workflow

### Phase 3: Nginx Reverse Proxy (Week 2)
- [ ] Create nginx.conf with all service routes
- [ ] Add Nginx service to docker-compose.yml
- [ ] Configure DNS or /etc/hosts for subdomains
- [ ] Test HTTP access to all services
- [ ] Generate SSL certificates
- [ ] Configure HTTPS with proper certificates
- [ ] Set up automatic HTTP to HTTPS redirect
- [ ] Test all services through Nginx

### Phase 4: Integration (Week 2)
- [ ] Create HomeServer API endpoints for Gitea
- [ ] Add Gitea client to HomeServer
- [ ] Create dashboard showing Git repos
- [ ] Add quick links to Vaultwarden
- [ ] Update API documentation
- [ ] Create integration tests

### Phase 5: Security Hardening (Week 3)
- [ ] Disable public signups after initial setup
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Test backup restoration
- [ ] Enable 2FA for all admin accounts
- [ ] Configure fail2ban for brute force protection
- [ ] Security audit and penetration testing
- [ ] Document security procedures

### Phase 6: Advanced Features (Week 4+)
- [ ] Set up CI/CD with Gitea webhooks
- [ ] Implement OAuth2 SSO (HomeServer → Gitea)
- [ ] Add repository mirroring
- [ ] Configure email notifications
- [ ] Set up monitoring and alerts
- [ ] Create backup verification system
- [ ] Add usage analytics dashboard

---

## Resource Requirements

### Estimated Resource Usage

**Idle State:**
- Gitea: ~150-200MB RAM, minimal CPU
- Vaultwarden: ~10-20MB RAM, minimal CPU
- Nginx: ~5-10MB RAM, minimal CPU
- PostgreSQL: +50MB RAM for new databases
- **Total Additional:** ~215-280MB RAM

**Active Use (5-10 users):**
- Gitea: ~300-500MB RAM
- Vaultwarden: ~20-50MB RAM
- **Total Additional:** ~320-550MB RAM

**Storage:**
- Gitea: Depends on repository size (plan for 10-50GB)
- Vaultwarden: ~100-500MB (minimal, mostly encrypted vault data)
- Database: ~500MB-2GB for both services combined

---

## Cost Analysis (vs SaaS)

### Current SaaS Pricing

**GitHub:**
- Free: Public repos only
- Pro: $4/user/month
- Team: $4/user/month
- Enterprise: $21/user/month

**Bitwarden:**
- Free: Basic features, 1 user
- Premium: $10/year
- Families: $40/year (6 users)
- Teams: $3/user/month
- Enterprise: $5/user/month

**Example: 5 Users**
- GitHub Team: $20/month = $240/year
- Bitwarden Families: $40/year
- **Total:** $280/year

**Self-Hosted (HomeServer):**
- Server cost: Amortized (already have hardware)
- Electricity: ~$2-5/month
- Domain (optional): $12/year
- **Total:** ~$36-72/year

**Savings:** $208-244/year (~75% reduction)

---

## Next Steps

### Immediate Actions

1. **Review this plan** and decide on implementation priority
2. **Update .env file** with new service credentials
3. **Choose deployment approach:**
   - All services at once
   - Incremental (Gitea first, then Vaultwarden)
4. **Determine domain strategy:**
   - Local only (.local domains)
   - Public with Let's Encrypt SSL
   - Hybrid (local + VPN access)

### Questions to Answer

1. **Domain Names:**
   - Will you use custom domain names?
   - Local network only or externally accessible?

2. **User Management:**
   - How many users will access these services?
   - Do you want SSO integration?

3. **Backup Location:**
   - Local backups only?
   - Cloud backup (S3, Backblaze, etc.)?
   - NAS or external drive?

4. **Email Configuration:**
   - Do you have SMTP server for notifications?
   - Gmail, SendGrid, Mailgun, or self-hosted?

---

## Conclusion

Adding Gitea and Vaultwarden transforms your HomeServer into a complete self-hosted productivity suite:

✅ **File Storage** - Already implemented
✅ **Authentication** - Already implemented
🔄 **Git Hosting** - Planned (Gitea)
🔄 **Password Management** - Planned (Vaultwarden)
📋 **Future:** Media server, home automation, etc.

This creates a powerful, private, and cost-effective alternative to multiple SaaS subscriptions.

---

*Plan created: 2025-11-07*
*Ready for implementation upon approval*
