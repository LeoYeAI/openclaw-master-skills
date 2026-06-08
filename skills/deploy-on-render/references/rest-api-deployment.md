# Direct API Deployment

When `RENDER_API_KEY` is set, you can create and manage services via the REST API without using a Blueprint or deeplink. Confirm exact request bodies against the [Render API reference](https://api-docs.render.com).

## Step 1: Get owner ID (workspace)

```bash
curl -s "https://api.render.com/v1/owners" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

Returns an array of workspaces. Use the `id` of the target workspace (e.g. `tea-xxxxx`) as `ownerId` when creating services.

## Step 2: Create a web service

**Endpoint:** `POST https://api.render.com/v1/services`

**Headers:** `Authorization: Bearer $RENDER_API_KEY`, `Content-Type: application/json`

Example body (field names and structure may vary; check [Create Service](https://api-docs.render.com/reference/create-service)):

```json
{
  "type": "web_service",
  "name": "my-app",
  "ownerId": "tea-xxxxx",
  "repo": "https://github.com/user/repo",
  "branch": "main",
  "autoDeploy": "yes",
  "serviceDetails": {
    "runtime": "node",
    "plan": "free",
    "envSpecificDetails": {
      "buildCommand": "npm ci",
      "startCommand": "npm start"
    },
    "envVars": [
      { "key": "NODE_ENV", "value": "production" }
    ]
  }
}
```

```bash
curl -X POST "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"web_service","name":"my-app","ownerId":"tea-xxxxx","repo":"https://github.com/user/repo","branch":"main","autoDeploy":"yes","serviceDetails":{"runtime":"node","plan":"free","envSpecificDetails":{"buildCommand":"npm ci","startCommand":"npm start"},"envVars":[{"key":"NODE_ENV","value":"production"}]}}'
```

## Step 3: Create other resources (Postgres, Key Value, etc.)

- **Postgres:** Use the create-database or equivalent endpoint; see API docs for request body.
- **Key Value:** Use the `/v1/key-value` or equivalent endpoint; see API docs.

## Blueprint vs API type mapping

| Blueprint `type` | API `type` (typical) |
|------------------|------------------------|
| `web`            | `web_service`          |
| `pserv`          | `private_service`      |
| `worker`         | `background_worker`    |
| `cron`           | `cron_job`             |
| `keyvalue`       | Use Key Value–specific endpoint |

Always confirm current field names and values in the [Render API reference](https://api-docs.render.com).
