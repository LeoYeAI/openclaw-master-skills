# n8n API Reference

## Authentication

The n8n API uses API key authentication via the `X-N8N-API-KEY` header.

API keys are managed in the n8n UI:
- Settings → API
- User profile → API

## Base URL

`N8N_BASE_URL`

Default: `${N8N_BASE_URL}$/api/v1`

## Endpoints

### Workflows

#### List Workflows
```
GET /workflows
Query params: ?active=true|false
```

Response:
```json
{
  "data": [
    {
      "id": "123",
      "name": "My Workflow",
      "active": true,
      "createdAt": "2026-01-14T10:00:00.000Z",
      "updatedAt": "2026-01-14T12:00:00.000Z"
    }
  ]
}
```

#### Get Workflow
```
GET /workflows/{id}
```

#### Create Workflow
```
POST /workflows
Body: workflow JSON
```

#### Update Workflow
```
PATCH /workflows/{id}
Body: partial workflow JSON
```

#### Activate/Deactivate
```
PATCH /workflows/{id}
Body: {"active": true|false}
```

#### Delete Workflow
```
DELETE /workflows/{id}
```

### Executions

#### List Executions
```
GET /executions?limit=20&workflowId={id}
```

Response:
```json
{
  "data": [
    {
      "id": "456",
      "finished": true,
      "mode": "trigger",
      "startedAt": "2026-01-14T12:00:00.000Z",
      "stoppedAt": "2026-01-14T12:00:05.000Z",
      "workflowId": "123",
      "status": "success"
    }
  ]
}
```

#### Get Execution
```
GET /executions/{id}
```

#### Delete Execution
```
DELETE /executions/{id}
```

#### Manual Execution
```
POST /workflows/{id}/execute
Body: {"data": {...}}
```

## Common Patterns

### List Active Workflows
```bash
python3 scripts/n8n_api.py list-workflows --active true --pretty
```

### Get Workflow Details
```bash
python3 scripts/n8n_api.py get-workflow --id <workflow-id> --pretty
```

### Activate/Deactivate Workflow
```bash
python3 scripts/n8n_api.py activate --id <workflow-id>
python3 scripts/n8n_api.py deactivate --id <workflow-id>
```

### List Recent Executions
```bash
python3 scripts/n8n_api.py list-executions --limit 10 --pretty
```

### Manually Execute Workflow
```bash
python3 scripts/n8n_api.py execute --id <workflow-id>
```

With data:
```bash
python3 scripts/n8n_api.py execute --id <workflow-id> --data '{"key": "value"}'
```

## Error Handling

HTTP status codes:
- `200` - Success
- `400` - Bad request
- `401` - Unauthorized (invalid API key)
- `404` - Not found
- `500` - Server error

## Environment Variables

Required:
- `N8N_API_KEY` - n8n API key
- `N8N_BASE_URL` - Base URL 