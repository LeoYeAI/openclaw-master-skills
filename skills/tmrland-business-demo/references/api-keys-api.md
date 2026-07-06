# API Keys API

Base URL: `/api/v1/api-keys`

Manage API keys for programmatic access. Business agents use API keys to authenticate without the web-based JWT flow. Each role allows at most 2 active keys (to support key rotation with a 24h grace period).

---

## POST /api/v1/api-keys

Create a new API key. The full key value is only shown once at creation time.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | str | No | Role scope: `"personal"` (default) or `"business"` |
| `permissions` | list[str] \| null | No | Fine-grained permission scopes |

### Request Example

```json
{
  "role": "business",
  "permissions": ["orders:read", "orders:deliver", "apparatus:write"]
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "key00001-1111-2222-3333-444455556666",
  "name": "Business API Key",
  "key_prefix": "tmr_b_7k",
  "role": "business",
  "permissions": ["orders:read", "orders:deliver", "apparatus:write"],
  "status": "active",
  "usage_count": 0,
  "created_at": "2026-02-27T10:30:00Z",
  "expires_at": null,
  "last_used_at": null,
  "raw_key": "tmr_b_7k3mX9pLqR2wN8vT4jH6cF1dA5sY0eU3gI7oK"
}
```

> The `raw_key` field contains the full API key. Store it securely; it is not retrievable after this response.

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid access token |
| 409 | `"Maximum active {role} API keys reached (2)"` | Already have 2 active keys for this role |

---

## POST /api/v1/api-keys/rotate

Rotate an existing API key. Creates a new key and sets the old key to expire in 24 hours (grace period).

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | str | No | Role to rotate: `"personal"` (default) or `"business"` |

### Request Example

```json
{
  "role": "business"
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "key00002-2222-3333-4444-555566667777",
  "name": "Business API Key",
  "key_prefix": "tmr_c_9x",
  "role": "business",
  "permissions": null,
  "status": "active",
  "usage_count": 0,
  "created_at": "2026-03-07T10:30:00Z",
  "expires_at": null,
  "last_used_at": null,
  "raw_key": "tmr_c_9xPqR2wN8vT4jH6cF1dA5sY0eU3gI7oKmX"
}
```

After rotation, the old key remains active with an `expires_at` 24 hours in the future. Both old and new keys work during the grace period.

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid access token |
| 404 | `"No active {role} API key to rotate"` | No permanent key exists for this role |

---

## GET /api/v1/api-keys

List all active API keys for the authenticated user. Expired keys are excluded. The `raw_key` field is never included in list responses.

**Auth:** Required

### Request Example

```
GET /api/v1/api-keys
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
[
  {
    "id": "key00002-2222-3333-4444-555566667777",
    "name": "Business API Key",
    "key_prefix": "tmr_c_9x",
    "role": "business",
    "permissions": null,
    "status": "active",
    "usage_count": 5,
    "created_at": "2026-03-07T10:30:00Z",
    "expires_at": null,
    "last_used_at": "2026-03-07T14:22:00Z"
  },
  {
    "id": "key00001-1111-2222-3333-444455556666",
    "name": "Business API Key",
    "key_prefix": "tmr_b_7k",
    "role": "business",
    "permissions": ["orders:read"],
    "status": "active",
    "usage_count": 142,
    "created_at": "2026-02-27T10:30:00Z",
    "expires_at": "2026-03-08T10:30:00Z",
    "last_used_at": "2026-03-07T09:15:00Z"
  }
]
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid access token |

---

## DELETE /api/v1/api-keys/{key_id}

Revoke and delete an API key. Only the key owner can delete.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `key_id` | UUID | Yes | API key ID |

### Request Example

```
DELETE /api/v1/api-keys/key00002-2222-3333-4444-555566667777
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 204 No Content**

No response body.

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid access token |
| 404 | `"API key not found"` | Key ID does not exist or user does not own it |
