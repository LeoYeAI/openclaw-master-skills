# PatchMon Integration Guide

PatchMon is an open-source Linux patch monitoring dashboard that provides:

- Web-based UI for viewing update status across all hosts
- Per-host package tracking and history
- Security update highlighting
- Automated update scheduling
- Update history and audit logs

## Installation

### Docker Compose (Recommended)

Create `/opt/patchmon/docker-compose.yml`:

```yaml
version: '3.8'

services:
  patchmon-database:
    image: postgres:17
    container_name: patchmon-database
    restart: always
    environment:
      POSTGRES_DB: patchmon_db
      POSTGRES_USER: patchmon_user
      POSTGRES_PASSWORD: ${PATCHMON_DB_PASSWORD}
    volumes:
      - patchmon-postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U patchmon_user -d patchmon_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  patchmon-redis:
    image: redis:7
    container_name: patchmon-redis
    restart: always
    command: redis-server --requirepass ${PATCHMON_REDIS_PASSWORD}
    volumes:
      - patchmon-redis:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${PATCHMON_REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  patchmon-backend:
    image: ghcr.io/patchmon/patchmon-backend:latest
    container_name: patchmon-backend
    restart: always
    environment:
      DATABASE_URL: postgresql://patchmon_user:${PATCHMON_DB_PASSWORD}@patchmon-database:5432/patchmon_db
      REDIS_HOST: patchmon-redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${PATCHMON_REDIS_PASSWORD}
      JWT_SECRET: ${PATCHMON_JWT_SECRET}
      JWT_EXPIRES_IN: 1h
      JWT_REFRESH_EXPIRES_IN: 7d
      PORT: 3001
    volumes:
      - patchmon-agent-files:/app/agent-files
    depends_on:
      patchmon-database:
        condition: service_healthy
      patchmon-redis:
        condition: service_healthy

  patchmon-frontend:
    image: ghcr.io/patchmon/patchmon-frontend:latest
    container_name: patchmon-frontend
    restart: always
    ports:
      - "3000:3000"
    environment:
      BACKEND_HOST: patchmon-backend
      BACKEND_PORT: 3001
    depends_on:
      - patchmon-backend

volumes:
  patchmon-postgres:
  patchmon-redis:
  patchmon-agent-files:
```

Create `.env` file:

```bash
# Generate secure passwords:
# openssl rand -base64 32

PATCHMON_DB_PASSWORD=<generate-secure-password>
PATCHMON_REDIS_PASSWORD=<generate-secure-password>
PATCHMON_JWT_SECRET=<generate-secure-password>
```

Start PatchMon:

```bash
cd /opt/patchmon
docker compose up -d
```

Access at: `http://localhost:3000`

## Agent Installation

Install PatchMon agent on each monitored host:

```bash
curl -sSL https://raw.githubusercontent.com/PatchMon/PatchMon/main/agent/install.sh | sudo bash
```

Configure agent (`/etc/patchmon/config.yml`):

```yaml
server:
  url: "http://patchmon-server:3001"
  api_key: "your-api-key-from-web-ui"

reporting:
  interval: 3600  # Report every hour
  report_offset: 300  # Stagger by 5 minutes

features:
  auto_update: true  # Auto-update agent itself
  docker: true       # Enable Docker monitoring
```

Start agent:

```bash
sudo systemctl enable patchmon-agent
sudo systemctl start patchmon-agent
```

## Web Dashboard Usage

### View Update Status

1. Log into PatchMon UI
2. Navigate to **Dashboard**
3. View summary cards:
   - Total Hosts
   - Needs Updating
   - Outdated Packages
   - Security Updates

### View Host Details

1. Navigate to **Hosts**
2. Click on a hostname
3. View:
   - Outdated packages list
   - Security updates
   - Update history
   - Reboot requirements

### Schedule Updates

1. Navigate to **Jobs** → **Create Job**
2. Configure:
   - Target hosts or groups
   - Update type (packages only / full)
   - Schedule (cron expression)
   - Notification settings
3. Save and enable

## Integration with Linux Patcher Skill

PatchMon and this skill complement each other:

**PatchMon provides:**
- Visual dashboard
- Update tracking
- Scheduled automated updates
- Web UI for non-technical users

**Linux Patcher skill provides:**
- OpenClaw integration
- Ad-hoc updates via chat
- Flexible scripting
- Custom workflows

### Recommended Setup

1. **Install PatchMon** for monitoring and dashboard
2. **Use PatchMon agents** for automated scheduled updates
3. **Use Linux Patcher skill** for manual/urgent updates via OpenClaw

Example workflow:
- PatchMon runs nightly updates automatically
- User asks OpenClaw: "Update webserver immediately"
- OpenClaw uses Linux Patcher skill for instant update
- Both systems log to PatchMon dashboard

## API Access (Advanced)

Query PatchMon programmatically:

```bash
# Get authentication token
TOKEN=$(curl -X POST https://patchmon.example.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  | jq -r '.token')

# List hosts needing updates
curl https://patchmon.example.com/api/v1/dashboard/hosts \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.[] | select(.needsUpdates == true)'

# Get outdated packages for a host
curl https://patchmon.example.com/api/v1/dashboard/hosts/HOST_ID/packages \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.outdated'
```

## Resources

- **Official Documentation:** https://docs.patchmon.net
- **GitHub Repository:** https://github.com/PatchMon/PatchMon
- **Discord Community:** https://patchmon.net/discord
- **Reddit Community:** https://reddit.com/r/patchmon

## Security Considerations

- **Use HTTPS** for production deployments (configure reverse proxy)
- **Restrict API access** with firewall rules
- **Rotate JWT secrets** regularly
- **Use strong passwords** for database and Redis
- **Limit agent permissions** to necessary commands only
- **Monitor PatchMon logs** for suspicious activity
