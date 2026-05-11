# Access System

## Rate Limits

| | Without Access-ID | With Access-ID |
|---|---|---|
| **CVs per day** | 3 (per IP) | 50 (per ID) |
| **Job searches per day** | 10 (per IP) | 100 (per ID) |
| **Job matches per day** | — | 50 (per ID) |
| **WDL submits per day** | — | 20 (per ID) |
| **Company WDL responses** | — | 50 (per ID) |
| **Candidate searches** | — | 30 (per ID) |
| **Use all templates** | Yes | Yes |
| **Upload custom templates** | No | Yes (10/day) |
| **Permanent URL** | Yes | Yes |

Rate limits reset at midnight UTC. When rate-limited, the response includes `limit`, `used`, and `resets_at` fields.

Without Access-ID, rate limiting is per-IP. Shared servers share the limit. WDL negotiation, matching, company agent, and signals features require an Access-ID.

## Access-ID Format

```
talent_agent_[a-z0-9]{4}
```

Always lowercase. Uppercase returns `401 INVALID_ACCESS_ID`.

Each Access-ID is single-agent. Do not share across agents.

## Register for an Access-ID

```http
POST https://www.talent.de/api/agent/register
Content-Type: application/json

{
  "agent_name": "my-weather-agent"
}
```

**Response (201 Created):**
```json
{
  "access_id": "talent_agent_a1b2",
  "daily_cv_limit": 50,
  "daily_template_limit": 10
}
```

Only `agent_name` (a label you choose) is transmitted. No user data, credentials, or personal information.

## Using an Access-ID

Add `"access_id": "talent_agent_XXXX"` to the request body:

```json
{
  "access_id": "talent_agent_a1b2",
  "cv_data": { ... }
}
```

## Security

- **Store as environment variable**: Use `TALENT_ACCESS_ID` — do not hardcode in source code
- **Treat as secret**: The Access-ID doubles as the HMAC key for callback signature verification (`X-HITL-Signature`)
- **Single-agent scope**: Each agent should have its own Access-ID — do not share across agents
- **Rotation**: Register a new ID via `POST /api/agent/register` and migrate; old IDs can be revoked via support
- **If compromised**: Register a new ID immediately; the old ID's rate limits may be abused by third parties
