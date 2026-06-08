---
name: coolify
description: Manage Coolify deployments, applications, databases, and services via the Coolify API. Use when the user wants to deploy, start, stop, restart, or manage applications hosted on Coolify.
homepage: https://coolify.io
user-invocable: true
metadata: {"openclaw":{"emoji":"🚀","requires":{"bins":["node"],"env":["COOLIFY_TOKEN"]},"primaryEnv":"COOLIFY_TOKEN"}}
---

# Coolify API Skill

Comprehensive management of Coolify deployments, applications, databases, services, and infrastructure via the Coolify API.

## When to Use This Skill

Use this skill when the user needs to:
- Deploy applications to Coolify
- Manage application lifecycle (start, stop, restart)
- View application logs
- Create and manage databases (PostgreSQL, MySQL, MongoDB, Redis, etc.)
- Deploy Docker Compose services
- Manage servers and infrastructure
- Configure environment variables
- Trigger and monitor deployments
- Manage GitHub App integrations
- Configure SSH private keys

## Prerequisites

1. **Coolify API Token** — Generate from Coolify dashboard:
   - Navigate to **Keys & Tokens** → **API tokens**
   - Create token with appropriate permissions (`read`, `write`, `deploy`)
   - Set `COOLIFY_TOKEN` environment variable

2. **bash, curl, jq** — Required for running bash scripts

3. **API Access** — Coolify Cloud (`app.coolify.io`) or self-hosted instance

## Quick Start

### Basic Commands

```bash
# List all applications
{baseDir}/scripts/coolify applications list

# Get application details
{baseDir}/scripts/coolify applications get --uuid abc-123

# Deploy an application
{baseDir}/scripts/coolify deploy --uuid abc-123 --force

# View application logs
{baseDir}/scripts/coolify applications logs --uuid abc-123

# Restart an application
{baseDir}/scripts/coolify applications restart --uuid abc-123
```

---

## Applications

### List Applications

```bash
{baseDir}/scripts/coolify applications list
```

**Output:**
```json
{
  "success": true,
  "data": [
    {
      "uuid": "abc-123",
      "name": "my-app",
      "status": "running",
      "fqdn": "https://app.example.com"
    }
  ],
  "count": 1
}
```

### Get Application Details

```bash
{baseDir}/scripts/coolify applications get --uuid abc-123
```

### Application Lifecycle

```bash
# Start
{baseDir}/scripts/coolify applications start --uuid abc-123

# Stop
{baseDir}/scripts/coolify applications stop --uuid abc-123

# Restart
{baseDir}/scripts/coolify applications restart --uuid abc-123
```

### View Logs

```bash
{baseDir}/scripts/coolify applications logs --uuid abc-123
```

### Environment Variables

```bash
# List environment variables
{baseDir}/scripts/coolify applications envs list --uuid abc-123

# Create environment variable
{baseDir}/scripts/coolify applications envs create \
  --uuid abc-123 \
  --key DATABASE_URL \
  --value "postgres://user:pass@host:5432/db" \
  --is-runtime true \
  --is-buildtime false

# Update environment variable
{baseDir}/scripts/coolify applications envs update \
  --uuid abc-123 \
  --env-uuid env-456 \
  --value "new-value"

# Bulk update environment variables
{baseDir}/scripts/coolify applications envs bulk-update \
  --uuid abc-123 \
  --json '{"DATABASE_URL":"postgres://...","API_KEY":"..."}'

# Delete environment variable
{baseDir}/scripts/coolify applications envs delete \
  --uuid abc-123 \
  --env-uuid env-456
```

### Create Applications

```bash
# Public Git repository
{baseDir}/scripts/coolify applications create-public \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --git-repository "https://github.com/user/repo" \
  --git-branch main \
  --name "My App"

# Private GitHub App
{baseDir}/scripts/coolify applications create-private-github-app \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --github-app-uuid gh-789 \
  --git-repository "user/repo" \
  --git-branch main

# Dockerfile
{baseDir}/scripts/coolify applications create-dockerfile \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --dockerfile-location "./Dockerfile" \
  --name "My Docker App"

# Docker Image
{baseDir}/scripts/coolify applications create-dockerimage \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --docker-image "nginx:latest" \
  --name "Nginx"

# Docker Compose
{baseDir}/scripts/coolify applications create-dockercompose \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --docker-compose-location "./docker-compose.yml"
```

---

## Databases

### List Databases

```bash
{baseDir}/scripts/coolify databases list
```

### Get Database Details

```bash
{baseDir}/scripts/coolify databases get --uuid db-123
```

### Database Lifecycle

```bash
# Start
{baseDir}/scripts/coolify databases start --uuid db-123

# Stop
{baseDir}/scripts/coolify databases stop --uuid db-123

# Restart
{baseDir}/scripts/coolify databases restart --uuid db-123

# Delete
{baseDir}/scripts/coolify databases delete --uuid db-123
```

### Create Databases

```bash
# PostgreSQL
{baseDir}/scripts/coolify databases create-postgresql \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --name "my-postgres" \
  --postgres-user admin \
  --postgres-password secret \
  --postgres-db myapp

# MySQL
{baseDir}/scripts/coolify databases create-mysql \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --name "my-mysql"

# MariaDB
{baseDir}/scripts/coolify databases create-mariadb \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --name "my-mariadb"

# MongoDB
{baseDir}/scripts/coolify databases create-mongodb \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --name "my-mongo"

# Redis
{baseDir}/scripts/coolify databases create-redis \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --name "my-redis"

# KeyDB
{baseDir}/scripts/coolify databases create-keydb \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --name "my-keydb"

# ClickHouse
{baseDir}/scripts/coolify databases create-clickhouse \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --name "my-clickhouse"

# Dragonfly
{baseDir}/scripts/coolify databases create-dragonfly \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --name "my-dragonfly"
```

### Backups

```bash
# List backup configurations
{baseDir}/scripts/coolify databases backups list --uuid db-123

# Create backup configuration
{baseDir}/scripts/coolify databases backups create \
  --uuid db-123 \
  --frequency "0 2 * * *" \
  --enabled true

# Get backup details
{baseDir}/scripts/coolify databases backups get \
  --uuid db-123 \
  --backup-uuid backup-456

# Update backup
{baseDir}/scripts/coolify databases backups update \
  --uuid db-123 \
  --backup-uuid backup-456 \
  --frequency "0 3 * * *"

# Trigger manual backup
{baseDir}/scripts/coolify databases backups trigger \
  --uuid db-123 \
  --backup-uuid backup-456

# List backup executions
{baseDir}/scripts/coolify databases backups executions \
  --uuid db-123 \
  --backup-uuid backup-456

# Delete backup configuration
{baseDir}/scripts/coolify databases backups delete \
  --uuid db-123 \
  --backup-uuid backup-456
```

---

## Services (Docker Compose)

### List Services

```bash
{baseDir}/scripts/coolify services list
```

### Get Service Details

```bash
{baseDir}/scripts/coolify services get --uuid service-123
```

### Service Lifecycle

```bash
# Start
{baseDir}/scripts/coolify services start --uuid service-123

# Stop
{baseDir}/scripts/coolify services stop --uuid service-123

# Restart
{baseDir}/scripts/coolify services restart --uuid service-123

# Delete
{baseDir}/scripts/coolify services delete --uuid service-123
```

### Create Service

```bash
{baseDir}/scripts/coolify services create \
  --project-uuid proj-123 \
  --server-uuid server-456 \
  --name "My Service" \
  --docker-compose '{"version":"3.8","services":{"web":{"image":"nginx"}}}'
```

### Environment Variables

```bash
# List
{baseDir}/scripts/coolify services envs list --uuid service-123

# Create
{baseDir}/scripts/coolify services envs create \
  --uuid service-123 \
  --key API_KEY \
  --value "secret"

# Update
{baseDir}/scripts/coolify services envs update \
  --uuid service-123 \
  --env-uuid env-456 \
  --value "new-secret"

# Bulk update
{baseDir}/scripts/coolify services envs bulk-update \
  --uuid service-123 \
  --json '{"API_KEY":"secret","DB_HOST":"localhost"}'

# Delete
{baseDir}/scripts/coolify services envs delete \
  --uuid service-123 \
  --env-uuid env-456
```

---

## Deployments

### Deploy Application

```bash
# Deploy by UUID
{baseDir}/scripts/coolify deploy --uuid abc-123

# Force rebuild
{baseDir}/scripts/coolify deploy --uuid abc-123 --force

# Deploy by tag
{baseDir}/scripts/coolify deploy --tag production

# Instant deploy (skip queue)
{baseDir}/scripts/coolify deploy --uuid abc-123 --instant-deploy
```

### List Deployments

```bash
# List all running deployments
{baseDir}/scripts/coolify deployments list

# List deployments for specific application
{baseDir}/scripts/coolify deployments list-for-app --uuid abc-123
```

### Get Deployment Details

```bash
{baseDir}/scripts/coolify deployments get --uuid deploy-456
```

### Cancel Deployment

```bash
{baseDir}/scripts/coolify deployments cancel --uuid deploy-456
```

---

## Servers

### List Servers

```bash
{baseDir}/scripts/coolify servers list
```

### Get Server Details

```bash
{baseDir}/scripts/coolify servers get --uuid server-123
```

### Create Server

```bash
{baseDir}/scripts/coolify servers create \
  --name "Production Server" \
  --ip "192.168.1.100" \
  --port 22 \
  --user root \
  --private-key-uuid key-456
```

### Update Server

```bash
{baseDir}/scripts/coolify servers update \
  --uuid server-123 \
  --name "Updated Name" \
  --description "Production environment"
```

### Validate Server

```bash
{baseDir}/scripts/coolify servers validate --uuid server-123
```

### Get Server Resources

```bash
# List all resources on server
{baseDir}/scripts/coolify servers resources --uuid server-123

# Get domains configured on server
{baseDir}/scripts/coolify servers domains --uuid server-123
```

### Delete Server

```bash
{baseDir}/scripts/coolify servers delete --uuid server-123
```

---

## Projects

### List Projects

```bash
{baseDir}/scripts/coolify projects list
```

### Get Project Details

```bash
{baseDir}/scripts/coolify projects get --uuid proj-123
```

### Create Project

```bash
{baseDir}/scripts/coolify projects create \
  --name "My Project" \
  --description "Production project"
```

### Update Project

```bash
{baseDir}/scripts/coolify projects update \
  --uuid proj-123 \
  --name "Updated Name"
```

### Delete Project

```bash
{baseDir}/scripts/coolify projects delete --uuid proj-123
```

### Environments

```bash
# List environments
{baseDir}/scripts/coolify projects environments list --uuid proj-123

# Create environment
{baseDir}/scripts/coolify projects environments create \
  --uuid proj-123 \
  --name "staging"

# Get environment details
{baseDir}/scripts/coolify projects environments get \
  --uuid proj-123 \
  --environment staging

# Delete environment
{baseDir}/scripts/coolify projects environments delete \
  --uuid proj-123 \
  --environment staging
```

---

## Teams

### List Teams

```bash
{baseDir}/scripts/coolify teams list
```

### Get Current Team

```bash
{baseDir}/scripts/coolify teams current
```

### Get Team Members

```bash
{baseDir}/scripts/coolify teams members
```

### Get Team by ID

```bash
{baseDir}/scripts/coolify teams get --id 1
```

---

## Security (Private Keys)

### List Private Keys

```bash
{baseDir}/scripts/coolify security keys list
```

### Get Private Key

```bash
{baseDir}/scripts/coolify security keys get --uuid key-123
```

### Create Private Key

```bash
{baseDir}/scripts/coolify security keys create \
  --name "Production Key" \
  --description "SSH key for production servers" \
  --private-key "$(cat ~/.ssh/id_rsa)"
```

### Update Private Key

```bash
{baseDir}/scripts/coolify security keys update \
  --uuid key-123 \
  --name "Updated Key Name"
```

### Delete Private Key

```bash
{baseDir}/scripts/coolify security keys delete --uuid key-123
```

---

## GitHub Apps

### List GitHub Apps

```bash
{baseDir}/scripts/coolify github-apps list
```

### Get GitHub App

```bash
{baseDir}/scripts/coolify github-apps get --uuid gh-123
```

### Create GitHub App

```bash
{baseDir}/scripts/coolify github-apps create \
  --name "My GitHub App" \
  --app-id 123456 \
  --installation-id 789012 \
  --private-key "$(cat github-app-key.pem)"
```

### Update GitHub App

```bash
{baseDir}/scripts/coolify github-apps update \
  --uuid gh-123 \
  --name "Updated App Name"
```

### Delete GitHub App

```bash
{baseDir}/scripts/coolify github-apps delete --uuid gh-123
```

### List Repositories

```bash
{baseDir}/scripts/coolify github-apps repos --uuid gh-123
```

### List Branches

```bash
{baseDir}/scripts/coolify github-apps branches \
  --uuid gh-123 \
  --owner myorg \
  --repo myrepo
```

---

## Common Use Cases

### Deploy a New Application

1. **List available servers:**
   ```bash
   {baseDir}/scripts/coolify servers list
   ```

2. **Create application:**
   ```bash
   {baseDir}/scripts/coolify applications create-public \
     --project-uuid proj-123 \
     --server-uuid server-456 \
     --git-repository "https://github.com/user/repo" \
     --git-branch main \
     --name "My App"
   ```

3. **Configure environment variables:**
   ```bash
   {baseDir}/scripts/coolify applications envs create \
     --uuid <new-app-uuid> \
     --key DATABASE_URL \
     --value "postgres://..." \
     --is-runtime true
   ```

4. **Deploy:**
   ```bash
   {baseDir}/scripts/coolify deploy --uuid <new-app-uuid>
   ```

### Set Up Database with Backups

1. **Create database:**
   ```bash
   {baseDir}/scripts/coolify databases create-postgresql \
     --project-uuid proj-123 \
     --server-uuid server-456 \
     --name "production-db"
   ```

2. **Configure daily backups:**
   ```bash
   {baseDir}/scripts/coolify databases backups create \
     --uuid <db-uuid> \
     --frequency "0 2 * * *" \
     --enabled true
   ```

3. **Trigger manual backup:**
   ```bash
   {baseDir}/scripts/coolify databases backups trigger \
     --uuid <db-uuid> \
     --backup-uuid <backup-uuid>
   ```

### Monitor Application Health

1. **Check application status:**
   ```bash
   {baseDir}/scripts/coolify applications get --uuid abc-123
   ```

2. **View recent logs:**
   ```bash
   {baseDir}/scripts/coolify applications logs --uuid abc-123
   ```

3. **List recent deployments:**
   ```bash
   {baseDir}/scripts/coolify deployments list-for-app --uuid abc-123
   ```

---

## Troubleshooting

### "API token not configured"

**Cause:** `COOLIFY_TOKEN` environment variable not set.

**Solution:**
```bash
export COOLIFY_TOKEN="your-token-here"
```

Or configure in OpenClaw config at `~/.openclaw/openclaw.json`:
```json
{
  "skills": {
    "entries": {
      "coolify": {
        "apiKey": "your-token-here"
      }
    }
  }
}
```

### "Rate limit exceeded"

**Cause:** Too many API requests in a short time.

**Solution:** The client automatically retries with exponential backoff. Wait for the retry or reduce request frequency.

### "Application not found"

**Cause:** Invalid or non-existent UUID.

**Solution:**
```bash
# List all applications to find correct UUID
{baseDir}/scripts/coolify applications list
```

### "connect ECONNREFUSED"

**Cause:** Cannot connect to Coolify API.

**Solution for self-hosted:**
```bash
# Set custom API URL
export COOLIFY_API_URL="https://your-coolify.example.com/api/v1"
```

**Solution for cloud:** Verify internet connection and that `app.coolify.io` is accessible.

### "Deployment failed"

**Cause:** Build or deployment error.

**Solution:**
1. Check deployment logs:
   ```bash
   {baseDir}/scripts/coolify deployments get --uuid deploy-456
   ```

2. Check application logs:
   ```bash
   {baseDir}/scripts/coolify applications logs --uuid abc-123
   ```

3. Verify environment variables are correct:
   ```bash
   {baseDir}/scripts/coolify applications envs list --uuid abc-123
   ```

### Node.js Not Found

**Cause:** Node.js not installed or not in PATH.

**Solution:**
```bash
# macOS (via Homebrew)
brew install node

# Verify installation
node --version
```

---

## Output Format

All commands return structured JSON:

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "count": 42
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "type": "APIError",
    "message": "Application not found",
    "hint": "Use 'applications list' to find valid UUIDs"
  }
}
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COOLIFY_TOKEN` | Yes | — | API token from Coolify dashboard |
| `COOLIFY_API_URL` | No | `https://app.coolify.io/api/v1` | API base URL (for self-hosted) |

### Self-Hosted Coolify

For self-hosted instances, set the API URL:

```bash
export COOLIFY_API_URL="https://coolify.example.com/api/v1"
export COOLIFY_TOKEN="your-token-here"
```

---

## Additional Resources

- **Coolify Documentation:** https://coolify.io/docs/
- **API Reference:** See `{baseDir}/references/API.md`
- **GitHub:** https://github.com/coollabsio/coolify
- **Discord:** https://coollabs.io/discord

---

## Edge Cases and Best Practices

### UUID vs Name

Most commands require UUIDs, not names. Always use `list` commands first to find UUIDs:

```bash
# Bad: Using name (will fail)
{baseDir}/scripts/coolify applications get --uuid "my-app"

# Good: Using UUID
{baseDir}/scripts/coolify applications list  # Find UUID first
{baseDir}/scripts/coolify applications get --uuid abc-123
```

### Force Deployments

Use `--force` flag carefully as it rebuilds from scratch:

```bash
# Normal deployment (uses cache)
{baseDir}/scripts/coolify deploy --uuid abc-123

# Force rebuild (slower, but ensures clean build)
{baseDir}/scripts/coolify deploy --uuid abc-123 --force
```

### Environment Variable Updates

After updating environment variables, restart the application:

```bash
# Update env var
{baseDir}/scripts/coolify applications envs update \
  --uuid abc-123 \
  --env-uuid env-456 \
  --value "new-value"

# Restart to apply changes
{baseDir}/scripts/coolify applications restart --uuid abc-123
```

### Backup Frequency

Use cron expressions for backup schedules:

| Expression | Description |
|------------|-------------|
| `0 2 * * *` | Daily at 2 AM |
| `0 */6 * * *` | Every 6 hours |
| `0 0 * * 0` | Weekly on Sunday at midnight |
| `0 0 1 * *` | Monthly on 1st at midnight |

---

## Summary

This skill provides complete access to Coolify's API across:
- **Applications** — Deployment, lifecycle, logs, environment variables
- **Databases** — 8 database types, backups, lifecycle management
- **Services** — Docker Compose orchestration
- **Deployments** — Trigger, monitor, cancel
- **Servers** — Infrastructure management and validation
- **Projects** — Organization and environment management
- **Teams** — Access control and collaboration
- **Security** — SSH key management
- **GitHub Apps** — Repository integration

All operations return structured JSON for easy agent consumption.
