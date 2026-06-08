# Coolify API Reference

Complete reference for the Coolify API v1. This document provides detailed endpoint specifications, request/response formats, and examples for all API operations.

## Base Information

**Base URL:**
- Cloud: `https://app.coolify.io/api/v1`
- Self-hosted: `https://<your-instance>/api/v1`

**Authentication:** Bearer token in Authorization header
```http
Authorization: Bearer <your-api-token>
```

**Content-Type:** `application/json`

**API Version:** v1

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Invalid token or bad request |
| 401 | Unauthenticated |
| 403 | Forbidden (no permission) |
| 404 | Resource not found |
| 409 | Conflict (e.g., domain conflicts) |
| 422 | Validation error |
| 429 | Rate limit exceeded |

**Error Response Format:**
```json
{
  "message": "Error description",
  "errors": {
    "field_name": ["Validation error message"]
  }
}
```

---

## Applications

### List All Applications

**GET** `/v1/applications`

**Response:**
```json
[
  {
    "uuid": "abc-123",
    "name": "my-app",
    "status": "running",
    "fqdn": "https://app.example.com",
    "git_repository": "https://github.com/user/repo",
    "git_branch": "main"
  }
]
```

### Get Application

**GET** `/v1/applications/{uuid}`

**Response:** Single application object

### Create Public Git Application

**POST** `/v1/applications/public`

**Body:**
```json
{
  "project_uuid": "proj-123",
  "server_uuid": "server-456",
  "git_repository": "https://github.com/user/repo",
  "git_branch": "main",
  "name": "My App",
  "ports_exposes": "3000",
  "build_pack": "nixpacks"
}
```

### Create Private GitHub App Application

**POST** `/v1/applications/private-github-app`

**Body:**
```json
{
  "project_uuid": "proj-123",
  "server_uuid": "server-456",
  "github_app_uuid": "gh-789",
  "git_repository": "user/repo",
  "git_branch": "main",
  "name": "My App"
}
```

### Create Dockerfile Application

**POST** `/v1/applications/dockerfile`

**Body:**
```json
{
  "project_uuid": "proj-123",
  "server_uuid": "server-456",
  "dockerfile_location": "./Dockerfile",
  "name": "My Docker App"
}
```

### Create Docker Image Application

**POST** `/v1/applications/dockerimage`

**Body:**
```json
{
  "project_uuid": "proj-123",
  "server_uuid": "server-456",
  "docker_image": "nginx:latest",
  "name": "Nginx"
}
```

### Create Docker Compose Application

**POST** `/v1/applications/dockercompose`

**Body:**
```json
{
  "project_uuid": "proj-123",
  "server_uuid": "server-456",
  "docker_compose_location": "./docker-compose.yml"
}
```

### Update Application

**PATCH** `/v1/applications/{uuid}`

**Body:** Partial application object with fields to update

### Delete Application

**DELETE** `/v1/applications/{uuid}`

### Start Application

**POST** `/v1/applications/{uuid}/start`

### Stop Application

**POST** `/v1/applications/{uuid}/stop`

### Restart Application

**POST** `/v1/applications/{uuid}/restart`

### Get Application Logs

**GET** `/v1/applications/{uuid}/logs`

**Response:** Plain text logs

---

## Application Environment Variables

### List Environment Variables

**GET** `/v1/applications/{uuid}/envs`

**Response:**
```json
[
  {
    "uuid": "env-123",
    "key": "DATABASE_URL",
    "value": "postgres://...",
    "is_runtime": true,
    "is_buildtime": false,
    "is_preview": false
  }
]
```

### Create Environment Variable

**POST** `/v1/applications/{uuid}/envs`

**Body:**
```json
{
  "key": "API_KEY",
  "value": "secret-value",
  "is_runtime": true,
  "is_buildtime": false,
  "is_preview": false,
  "is_literal": false,
  "is_multiline": false
}
```

### Update Environment Variable

**PATCH** `/v1/applications/{uuid}/envs`

**Body:**
```json
{
  "uuid": "env-123",
  "value": "new-value"
}
```

### Bulk Update Environment Variables

**PATCH** `/v1/applications/{uuid}/envs/bulk`

**Body:**
```json
{
  "DATABASE_URL": "postgres://new-url",
  "API_KEY": "new-key"
}
```

### Delete Environment Variable

**DELETE** `/v1/applications/{uuid}/envs/{env_uuid}`

---

## Databases

### List All Databases

**GET** `/v1/databases`

**Response:**
```json
[
  {
    "uuid": "db-123",
    "name": "production-db",
    "type": "postgresql",
    "status": "running"
  }
]
```

### Get Database

**GET** `/v1/databases/{uuid}`

### Create PostgreSQL Database

**POST** `/v1/databases/postgresql`

**Body:**
```json
{
  "project_uuid": "proj-123",
  "server_uuid": "server-456",
  "name": "my-postgres",
  "postgres_user": "admin",
  "postgres_password": "secret",
  "postgres_db": "myapp",
  "postgres_initdb_args": "--encoding=UTF8",
  "postgres_host_auth_method": "scram-sha-256"
}
```

### Create MySQL Database

**POST** `/v1/databases/mysql`

**Body:**
```json
{
  "project_uuid": "proj-123",
  "server_uuid": "server-456",
  "name": "my-mysql",
  "mysql_root_password": "secret",
  "mysql_user": "admin",
  "mysql_password": "secret",
  "mysql_database": "myapp"
}
```

### Create MariaDB Database

**POST** `/v1/databases/mariadb`

### Create MongoDB Database

**POST** `/v1/databases/mongodb`

### Create Redis Database

**POST** `/v1/databases/redis`

### Create KeyDB Database

**POST** `/v1/databases/keydb`

### Create ClickHouse Database

**POST** `/v1/databases/clickhouse`

### Create Dragonfly Database

**POST** `/v1/databases/dragonfly`

### Update Database

**PATCH** `/v1/databases/{uuid}`

### Delete Database

**DELETE** `/v1/databases/{uuid}`

### Start Database

**POST** `/v1/databases/{uuid}/start`

### Stop Database

**POST** `/v1/databases/{uuid}/stop`

### Restart Database

**POST** `/v1/databases/{uuid}/restart`

---

## Database Backups

### List Backup Configurations

**GET** `/v1/databases/{uuid}/backups`

**Response:**
```json
[
  {
    "uuid": "backup-123",
    "frequency": "0 2 * * *",
    "enabled": true,
    "save_s3": false
  }
]
```

### Create Backup Configuration

**POST** `/v1/databases/{uuid}/backups`

**Body:**
```json
{
  "frequency": "0 2 * * *",
  "enabled": true,
  "save_s3": false,
  "s3_storage_uuid": null
}
```

### Get Backup

**GET** `/v1/databases/{uuid}/backups/{backup_uuid}`

### Update Backup

**PATCH** `/v1/databases/{uuid}/backups/{backup_uuid}`

**Body:** Partial backup object

### Delete Backup

**DELETE** `/v1/databases/{uuid}/backups/{backup_uuid}`

### Trigger Manual Backup

**POST** `/v1/databases/{uuid}/backups/{backup_uuid}/trigger`

### List Backup Executions

**GET** `/v1/databases/{uuid}/backups/{backup_uuid}/executions`

**Response:**
```json
[
  {
    "id": 1,
    "status": "success",
    "size": 1024000,
    "created_at": "2024-01-01T02:00:00Z"
  }
]
```

---

## Services (Docker Compose)

### List All Services

**GET** `/v1/services`

### Get Service

**GET** `/v1/services/{uuid}`

### Create Service

**POST** `/v1/services`

**Body:**
```json
{
  "project_uuid": "proj-123",
  "server_uuid": "server-456",
  "name": "My Service",
  "docker_compose": {
    "version": "3.8",
    "services": {
      "web": {
        "image": "nginx:latest",
        "ports": ["80:80"]
      }
    }
  }
}
```

### Update Service

**PATCH** `/v1/services/{uuid}`

### Delete Service

**DELETE** `/v1/services/{uuid}`

### Start Service

**POST** `/v1/services/{uuid}/start`

### Stop Service

**POST** `/v1/services/{uuid}/stop`

### Restart Service

**POST** `/v1/services/{uuid}/restart`

---

## Service Environment Variables

### List Environment Variables

**GET** `/v1/services/{uuid}/envs`

### Create Environment Variable

**POST** `/v1/services/{uuid}/envs`

**Body:** Same as application env vars

### Update Environment Variable

**PATCH** `/v1/services/{uuid}/envs`

### Bulk Update Environment Variables

**PATCH** `/v1/services/{uuid}/envs/bulk`

### Delete Environment Variable

**DELETE** `/v1/services/{uuid}/envs/{env_uuid}`

---

## Deployments

### Deploy Application

**POST** `/v1/deploy`

**Query Parameters:**
- `uuid` — Application UUID (comma-separated for multiple)
- `tag` — Tag name (comma-separated for multiple)
- `force` — Force rebuild (boolean)
- `instant_deploy` — Deploy immediately (boolean)

**Example:**
```
POST /v1/deploy?uuid=abc-123&force=true
```

**Response:**
```json
{
  "deployment_uuid": "deploy-456",
  "message": "Deployment queued"
}
```

### List Running Deployments

**GET** `/v1/deployments`

**Response:**
```json
[
  {
    "deployment_uuid": "deploy-456",
    "application_id": 1,
    "status": "in_progress",
    "commit": "abc123"
  }
]
```

### Get Deployment

**GET** `/v1/deployments/{uuid}`

### Cancel Deployment

**POST** `/v1/deployments/{uuid}/cancel`

### List Deployments for Application

**GET** `/v1/deployments/applications/{uuid}`

---

## Servers

### List All Servers

**GET** `/v1/servers`

**Response:**
```json
[
  {
    "uuid": "server-123",
    "name": "Production Server",
    "ip": "192.168.1.100",
    "port": 22,
    "user": "root",
    "proxy_type": "traefik"
  }
]
```

### Get Server

**GET** `/v1/servers/{uuid}`

### Create Server

**POST** `/v1/servers`

**Body:**
```json
{
  "name": "My Server",
  "description": "Production server",
  "ip": "192.168.1.100",
  "port": 22,
  "user": "root",
  "private_key_uuid": "key-456",
  "is_build_server": false,
  "instant_validate": true
}
```

### Update Server

**PATCH** `/v1/servers/{uuid}`

### Delete Server

**DELETE** `/v1/servers/{uuid}`

### Get Server Domains

**GET** `/v1/servers/{uuid}/domains`

### Get Server Resources

**GET** `/v1/servers/{uuid}/resources`

### Validate Server Connection

**GET** `/v1/servers/{uuid}/validate`

---

## Projects

### List All Projects

**GET** `/v1/projects`

### Get Project

**GET** `/v1/projects/{uuid}`

### Create Project

**POST** `/v1/projects`

**Body:**
```json
{
  "name": "My Project",
  "description": "Production project"
}
```

### Update Project

**PATCH** `/v1/projects/{uuid}`

### Delete Project

**DELETE** `/v1/projects/{uuid}`

### List Environments

**GET** `/v1/projects/{uuid}/environments`

### Create Environment

**POST** `/v1/projects/{uuid}/environments`

**Body:**
```json
{
  "name": "staging"
}
```

### Get Environment

**GET** `/v1/projects/{uuid}/{environment_name_or_uuid}`

### Delete Environment

**DELETE** `/v1/projects/{uuid}/{environment_name_or_uuid}`

---

## Teams

### List All Teams

**GET** `/v1/teams`

### Get Current Team

**GET** `/v1/teams/current`

### Get Current Team Members

**GET** `/v1/teams/current/members`

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin"
  }
]
```

### Get Team by ID

**GET** `/v1/teams/{id}`

---

## Security (Private Keys)

### List Private Keys

**GET** `/v1/security/keys`

**Response:**
```json
[
  {
    "uuid": "key-123",
    "name": "Production Key",
    "description": "SSH key for prod servers",
    "fingerprint": "SHA256:..."
  }
]
```

### Get Private Key

**GET** `/v1/security/keys/{uuid}`

### Create Private Key

**POST** `/v1/security/keys`

**Body:**
```json
{
  "name": "My Key",
  "description": "SSH key description",
  "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\n..."
}
```

### Update Private Key

**PATCH** `/v1/security/keys/{uuid}`

### Delete Private Key

**DELETE** `/v1/security/keys/{uuid}`

---

## GitHub Apps

### List GitHub Apps

**GET** `/v1/github-apps`

### Get GitHub App

**GET** `/v1/github-apps/{uuid}`

### Create GitHub App

**POST** `/v1/github-apps`

**Body:**
```json
{
  "name": "My GitHub App",
  "app_id": 123456,
  "installation_id": 789012,
  "client_id": "Iv1...",
  "client_secret": "secret...",
  "webhook_secret": "webhook...",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\n..."
}
```

### Update GitHub App

**PATCH** `/v1/github-apps/{uuid}`

### Delete GitHub App

**DELETE** `/v1/github-apps/{uuid}`

### List Repositories

**GET** `/v1/github-apps/{uuid}/repos`

**Response:**
```json
[
  {
    "id": 123,
    "name": "my-repo",
    "full_name": "user/my-repo",
    "private": true
  }
]
```

### List Branches

**GET** `/v1/github-apps/{uuid}/{owner}/{repo}/branches`

**Response:**
```json
[
  {
    "name": "main",
    "protected": true
  },
  {
    "name": "develop",
    "protected": false
  }
]
```

---

## Rate Limiting

The API implements rate limiting. When exceeded:

**Response:** 429 Too Many Requests

**Headers:**
```
Retry-After: 60
```

**Body:**
```json
{
  "message": "Rate limit exceeded. Please try again later."
}
```

**Client behavior:** Implement exponential backoff and respect the `Retry-After` header.

---

## Common Patterns

### Pagination

Some list endpoints support pagination:

**Query Parameters:**
- `skip` — Number of records to skip (default: 0)
- `take` — Number of records to return (default: 10)

**Example:**
```
GET /v1/applications?skip=10&take=20
```

### Filtering

List endpoints may support filtering via query parameters (endpoint-specific).

### UUID Format

UUIDs are hyphenated strings: `abc-123`, `server-456`

---

## Example Requests

### Deploy with Force Rebuild

```bash
curl -X POST "https://app.coolify.io/api/v1/deploy?uuid=abc-123&force=true" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json"
```

### Create Environment Variable

```bash
curl -X POST "https://app.coolify.io/api/v1/applications/abc-123/envs" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "DATABASE_URL",
    "value": "postgres://user:pass@host:5432/db",
    "is_runtime": true,
    "is_buildtime": false
  }'
```

### List All Applications

```bash
curl -X GET "https://app.coolify.io/api/v1/applications" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Resources

- **Coolify Documentation:** https://coolify.io/docs/
- **GitHub Repository:** https://github.com/coollabsio/coolify
- **Discord Community:** https://coollabs.io/discord
