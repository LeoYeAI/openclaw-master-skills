# Docker Deployment

Run Mission Control in Docker containers instead of installing Node.js dependencies directly.

---

## Prerequisites

- Docker installed and running ([docker.com](https://docker.com))
- Docker Compose v2+ (included with Docker Desktop)

---

## Quick Start

```bash
# Install with Docker mode
./setup.sh --docker

# Or if already installed, just start the containers
cd ~/.openclaw/mission-control
docker compose up -d
```

The setup script with `--docker` skips npm install and configures everything for container use.

---

## Manual Docker Setup

If you prefer to set things up manually:

```bash
# Navigate to the dashboard directory
cd ~/.openclaw/mission-control

# Create your .env file
cp backend/.env.example backend/.env
# Edit backend/.env with your gateway URL, token, and hook secret

# Build and start
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

---

## Accessing the Dashboard

- **Frontend**: http://localhost:4173
- **Backend API**: http://localhost:8000
- **Health check**: http://localhost:8000/api/health

---

## Managing Containers

```bash
# Stop
docker compose down

# Restart
docker compose restart

# Rebuild after code changes
docker compose up -d --build

# View logs
docker compose logs -f
docker compose logs -f backend    # backend only
docker compose logs -f frontend   # frontend only
```

---

## Data Persistence

The SQLite database is stored in a Docker volume, so your data persists across container restarts. To see where:

```bash
docker volume ls | grep mission-control
```

To back up the database:

```bash
docker compose exec backend cat /app/data/mission-control.db > backup.db
```

---

## Updating

When you get a new version of Mission Control:

```bash
cd ~/.openclaw/mission-control
docker compose down
# Replace files with new version
docker compose up -d --build
```

---

## Networking Notes

The hook needs to reach the backend container from the host. If OpenClaw runs on the host (not in Docker), the default `http://localhost:8000` in `MISSION_CONTROL_URL` works because Docker maps port 8000 to the host.

If OpenClaw also runs in Docker, use the Docker network name instead:

```
MISSION_CONTROL_URL=http://mission-control-backend:8000
```

And ensure both containers are on the same Docker network.
