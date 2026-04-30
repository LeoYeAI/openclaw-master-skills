---
name: docker-ops
description: "Use when building, running, composing, deploying, or troubleshooting Docker containers and Docker Compose stacks. Covers build, runtime, networking, volumes, and debugging."
version: 1.0.0
author: Papi
license: MIT
metadata:
  hermes:
    tags: [docker, containers, compose, devops, deployment, debugging]
    related_skills: [wsl-workflow]
---

# Docker / Container Ops

## Overview

Everything Docker — from building images and writing Compose files to debugging running containers, managing networks, cleaning up, and production deployment patterns. No fluff, just the commands you actually need.

## When to Use

- Building Docker images or writing Dockerfiles
- Running Docker Compose stacks
- Debugging container issues (logs, shells, networking)
- Managing volumes, networks, and cleanup
- Production deployment patterns
- Docker performance issues

Don't use for:
- Kubernetes orchestration (that's a different beast)
- CI/CD pipeline setup (use github-pr-workflow skill)

## Essential Commands

### Images

```bash
# Build
docker build -t myapp:latest .
docker build --no-cache -t myapp:latest .          # Force fresh build
docker build --build-arg VERSION=1.0 -t myapp .    # With build args
docker build --target builder -t myapp:builder .    # Multi-stage specific target

# List & Inspect
docker images
docker images -f "dangling=true"                    # Dangling images only
docker inspect myapp:latest
docker history myapp:latest                         # Layer breakdown

# Tag & Push
docker tag myapp:latest registry.example.com/myapp:latest
docker push registry.example.com/myapp:latest

# Remove
docker rmi myapp:latest
docker image prune                                  # Remove dangling
docker image prune -a                               # Remove ALL unused
```

### Containers

```bash
# Run
docker run -d --name myapp -p 8080:80 myapp:latest
docker run -it --rm myapp:latest /bin/bash          # Interactive, auto-remove
docker run --env-file .env myapp:latest              # Env from file
docker run -v /host/path:/container/path myapp       # Bind mount
docker run --memory=512m --cpus=1 myapp:latest       # Resource limits
docker run --restart=unless-stopped myapp:latest     # Restart policy

# Lifecycle
docker start myapp
docker stop myapp          # SIGTERM, then SIGKILL after 10s
docker stop -t 30 myapp    # Extended grace period
docker restart myapp
docker kill myapp          # Immediate SIGKILL
docker rm myapp            # Remove stopped container
docker rm -f myapp         # Force remove running container

# Execute & Debug
docker exec -it myapp /bin/bash
docker exec myapp cat /etc/config.yaml
docker logs myapp
docker logs -f myapp                    # Follow (tail)
docker logs --since 1h myapp            # Last hour
docker logs --tail 100 myapp            # Last 100 lines
docker top myapp                        # Processes in container
docker stats myapp                      # Resource usage
docker diff myapp                       # Filesystem changes

# Port mapping check
docker port myapp
```

### Docker Compose

```bash
# Lifecycle
docker compose up -d                    # Start in background
docker compose up --build               # Rebuild then start
docker compose up -d --force-recreate   # Force recreate all
docker compose down                     # Stop and remove
docker compose down -v                  # Also remove volumes
docker compose down --rmi all           # Also remove images

# Status & Debug
docker compose ps
docker compose logs
docker compose logs -f service_name
docker compose logs --since 30m service_name
docker compose exec service_name /bin/bash
docker compose top

# Scale
docker compose up -d --scale worker=3

# Validate config
docker compose config
docker compose config --services        # List service names only
```

### Compose File Best Practices

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production        # Multi-stage target
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    env_file:
      - .env
    volumes:
      - app-data:/app/data      # Named volume (preferred)
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "1.0"

  db:
    image: postgres:16-alpine
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  app-data:
  db-data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### Volumes

```bash
# List
docker volume ls

# Inspect
docker volume inspect myapp-data

# Create named volume
docker volume create myapp-data

# Remove
docker volume rm myapp-data
docker volume prune                # Remove all unused volumes
```

### Networks

```bash
# List
docker network ls

# Create
docker network create my-network
docker network create --driver bridge --subnet 172.20.0.0/16 my-network

# Connect/disconnect running containers
docker network connect my-network myapp
docker network disconnect my-network myapp

# Inspect
docker network inspect my-network

# Remove
docker network rm my-network
docker network prune
```

## Debugging Playbook

### Container Won't Start

```bash
# Check exit code
docker inspect myapp --format='{{.State.ExitCode}}'

# Common codes:
# 0 = exited gracefully
# 1 = application error
# 137 = OOM killed (check memory limits)
# 139 = segfault

# Get the logs
docker logs myapp

# If it exits immediately, run interactively
docker run -it --rm --entrypoint /bin/bash myapp:latest
```

### Networking Issues

```bash
# Check container's IP
docker inspect myapp --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

# DNS resolution from inside container
docker exec myapp nslookup db

# Port not accessible from host?
# 1. Check port mapping: docker port myapp
# 2. Check if app binds to 0.0.0.0 not just localhost
# 3. Check firewall rules
# 4. WSL2: may need to check Windows firewall too
```

### Performance Issues

```bash
# Resource usage
docker stats --no-stream

# Disk usage
docker system df

# Full system cleanup (nuclear)
docker system prune -a --volumes
# WARNING: removes everything not in use
```

### Volume/Permission Issues

```bash
# Check volume mounts
docker inspect myapp --format='{{json .Mounts}}' | jq

# Common fix: app user UID doesn't match host UID
# In Dockerfile:
# RUN useradd -u 1000 appuser
```

## Dockerfile Best Practices

```dockerfile
# Multi-stage build (smaller final image)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine AS production
WORKDIR /app
RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -s /bin/sh -D appuser
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER appuser
EXPOSE 8080
HEALTHCHECK CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
CMD ["node", "dist/server.js"]
```

Key rules:
1. **Pin versions** — `node:20.11-alpine` not `node:latest`
2. **Multi-stage builds** — build and runtime in separate stages
3. **Non-root user** — always set USER
4. **Order matters** — copy package files first, install, then copy source (cache layers)
5. **.dockerignore** — exclude node_modules, .git, .env, docs
6. **One process per container** — don't run app + cron + nginx in one container

## Common Pitfalls

1. **Forgot .dockerignore.** node_modules, .git, .env files getting baked into the image. Create .dockerignore first.

2. **Running as root.** Default USER is root. Always create and switch to a non-root user.

3. **Bind mount on WSL2 /mnt/c.** Performance is terrible. Use named volumes or work in the Linux filesystem.

4. **OOM kills.** Set memory limits in compose or run. Container exit code 137 = OOM.

5. **Stale layers.** If builds aren't picking up changes, `docker build --no-cache`.

6. **Orphaned volumes.** `docker compose down` does NOT remove volumes by default. Use `down -v` if you want them gone.

7. **Health check timing.** If your health check starts before the app is ready, the container gets killed in a loop. Set `start_period` generously.

## Verification Checklist

- [ ] Dockerfile follows multi-stage build pattern
- [ ] Non-root user set in Dockerfile
- [ ] .dockerignore excludes .git, .env, node_modules
- [ ] Health checks defined in compose
- [ ] Volumes used for persistent data (not bind mounts for production)
- [ ] Resource limits set (memory, CPU)
- [ ] Secrets not in compose file (use Docker secrets or env files with restricted perms)
- [ ] Images pinned to specific versions, not :latest
