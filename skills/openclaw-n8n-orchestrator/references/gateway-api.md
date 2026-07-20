# OpenClaw Gateway API Reference

Complete specification for the OpenClaw Gateway HTTP and WebSocket interfaces used for n8n ingress communication.

---

## Table of Contents

1. [Gateway Overview](#gateway-overview)
2. [/v1/responses Endpoint](#v1-responses-endpoint)
3. [/tools/invoke Endpoint](#tools-invoke-endpoint)
4. [WebSocket Handshake Protocol](#websocket-handshake-protocol)
5. [Telemetry and Diagnostic Codes](#telemetry-codes)
6. [Payload Schema Reference](#payload-schemas)

---

## Gateway Overview

The OpenClaw Gateway multiplexes WebSocket and HTTP traffic on a unified port (default: `18789`). It serves as the primary control plane and node transport mechanism.

**Key Endpoints**:
- `POST /v1/responses` — OpenResponses-compatible ingress for injecting data into the agent's context
- `POST /tools/invoke` — Direct tool invocation bypassing the conversational LLM
- `WebSocket /` — Persistent streaming connection for real-time communication

**Authentication Modes**:
- `token` — Bearer token via `Authorization` header (recommended)
- `none` — No authentication (development only, never use in production)

The auth token is configured via `gateway.auth.token` in `openclaw.json` or the `OPENCLAW_GATEWAY_TOKEN` environment variable.

---

## /v1/responses Endpoint

The primary ingress point for n8n to push data into OpenClaw's active session.

### Enabling the Endpoint

**Disabled by default.** Must be explicitly enabled in `openclaw.json`:

```json
{
  "gateway": {
    "http": {
      "endpoints": {
        "responses": { "enabled": true }
      }
    }
  }
}
```

### Request Format

```http
POST /v1/responses HTTP/1.1
Host: {gateway-host}:18789
Authorization: Bearer {OPENCLAW_GATEWAY_TOKEN}
Content-Type: application/json
```

### Primary Request Schema

```json
{
  "model": "string",
  "user": "string",
  "input": [ ...input_objects ],
  "instructions": "string (optional)",
  "tools": [ ...tool_definitions (optional) ],
  "stream": false,
  "timeout_seconds": 0
}
```

#### Parameter Details

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | LLM model identifier (e.g., `claude-sonnet-4-20250514`) |
| `user` | string | Yes | Stable session routing key. Use `n8n-workflow-{id}` pattern for consistent session history |
| `input` | array | Yes | Array of input objects to inject into agent context |
| `instructions` | string | No | Merges dynamically into the system prompt for this request |
| `tools` | array | No | Client-side function schemas the agent can call back |
| `stream` | boolean | No | Enable Server-Sent Events for streaming responses (default: false) |
| `timeout_seconds` | integer | **Critical** | Set to `0` to prevent infinite echo loops |

### Input Object Types

#### Standard Message

Appended to historical context as a conversation turn.

```json
{
  "role": "user",
  "content": "The n8n workflow completed. Here are the results: ..."
}
```

#### Function Call Output

Returns the result of a previously requested function call. Use when the agent initiated the webhook via a tool call and expects structured results.

```json
{
  "type": "function_call_output",
  "call_id": "call_abc123",
  "output": "{\"status\": \"success\", \"records_processed\": 147}"
}
```

#### Image Input

Inject images from n8n processing pipelines (e.g., generated charts, screenshots).

```json
{
  "type": "input_image",
  "image_url": "https://example.com/chart.png"
}
```

Or via base64:

```json
{
  "type": "input_image",
  "image_data": {
    "media_type": "image/png",
    "data": "iVBORw0KGgo..."
  }
}
```

**Supported formats**: JPEG, PNG, GIF, WEBP
**Size limit**: 10MB default

#### Document Input

Inject processed documents from n8n pipelines.

```json
{
  "type": "input_file",
  "file_data": {
    "media_type": "application/pdf",
    "data": "JVBERi0xLjQ..."
  }
}
```

**Supported MIME types**: text/csv, text/plain, application/json, application/pdf
**PDF page cap**: 4 pages by default (to preserve token limits)

### Response Format

```json
{
  "id": "resp_abc123",
  "status": "completed",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "The workflow processed 147 records successfully."
        }
      ]
    }
  ]
}
```

### Session Routing

The `user` parameter drives session persistence. For n8n integrations, use a consistent naming pattern:

```
n8n-workflow-{workflow_id}              → One session per workflow
n8n-workflow-{workflow_id}-{user_name}  → Per-user session per workflow
n8n-global                              → Shared session for all n8n workflows
```

The Gateway hashes this string to derive a stable session key, ensuring repeated calls share conversation history.

---

## /tools/invoke Endpoint

Bypasses the conversational LLM and directly triggers an OpenClaw tool. Used for direct command execution from n8n when no reasoning step is needed.

```http
POST /tools/invoke HTTP/1.1
Host: {gateway-host}:18789
Authorization: Bearer {OPENCLAW_GATEWAY_TOKEN}
Content-Type: application/json
```

```json
{
  "tool": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Important**: The tool must be allowlisted by the Gateway's policy chain. Attempting to invoke a restricted tool returns `403 Forbidden`.

**Use case from n8n**: Red-team testing, direct file operations, or triggering specific agent capabilities without LLM overhead.

---

## WebSocket Handshake Protocol

For persistent streaming connections (used by client UIs and advanced n8n integrations).

### Connection Lifecycle

```
1. Client connects to ws://{gateway-host}:18789
2. Gateway sends: connect.challenge { nonce, timestamp }
3. Client responds: connect { minProtocol, maxProtocol, caps, signature }
4. Gateway validates signature and assigns role
5. Connection established with assigned permissions
```

### Challenge-Response Detail

**Gateway Challenge**:
```json
{
  "method": "connect.challenge",
  "params": {
    "nonce": "a1b2c3d4e5f6...",
    "timestamp": "2026-03-10T14:30:00Z"
  }
}
```

**Client Response**:
```json
{
  "method": "connect",
  "params": {
    "minProtocol": 1,
    "maxProtocol": 2,
    "caps": ["operator.read", "session.send"],
    "device_id": "n8n-integration-001",
    "signature": "hmac-sha256-of-nonce-with-token"
  }
}
```

### Connection Roles and Permissions

| Role | Permissions | Use Case |
|------|-------------|----------|
| `operator` | `operator.read`, `operator.write`, `session.send` | Control plane commands, full session access |
| `node` | `node.capabilities`, `tool.execute` | Capability host for specific tool sets |

n8n integrations typically use the `operator` role with `session.send` permission for ingress operations.

### Permission Scopes

| Scope | Description |
|-------|-------------|
| `operator.read` | Fetch tool catalogs, read session state |
| `operator.write` | Modify agent configuration |
| `session.send` | Inject messages into active sessions |
| `screen.record` | Visual capabilities (screen capture) |
| `tool.execute` | Direct tool invocation |

---

## Telemetry Codes

Diagnostic codes returned during connection failures. Use these to debug n8n ↔ Gateway integration issues.

### Authentication Errors

| Code | Meaning | Fix |
|------|---------|-----|
| `DEVICE_AUTH_NONCE_MISMATCH` | Client signed a stale or incorrect nonce | Refresh WebSocket connection; ensure nonce from latest challenge is used |
| `DEVICE_AUTH_SIGNATURE_EXPIRED` | Signed timestamp outside acceptable latency skew | Sync NTP clocks between n8n host and OpenClaw host |
| `DEVICE_AUTH_DEVICE_ID_MISMATCH` | Device identity doesn't match public key fingerprint | Verify device_id matches registered identity |
| `AUTH_TOKEN_INVALID` | Bearer token doesn't match Gateway configuration | Check `OPENCLAW_GATEWAY_TOKEN` matches on both sides |
| `AUTH_TOKEN_MISSING` | No Authorization header in request | Add `Authorization: Bearer {token}` header |

### Endpoint Errors

| Code | Meaning | Fix |
|------|---------|-----|
| `ENDPOINT_DISABLED` | `/v1/responses` not enabled | Set `gateway.http.endpoints.responses.enabled: true` in openclaw.json |
| `ENDPOINT_RATE_LIMITED` | Too many requests in time window | Implement rate limiting in n8n before calling Gateway |
| `SESSION_NOT_FOUND` | No active session for provided `user` key | Ensure agent has an active session; check `user` parameter consistency |
| `TOOL_NOT_ALLOWLISTED` | Attempted `/tools/invoke` on restricted tool | Add tool to Gateway policy allowlist |

### Connection Errors

| Code | Meaning | Fix |
|------|---------|-----|
| `PROTOCOL_VERSION_MISMATCH` | Client protocol version not supported | Update client to match Gateway's supported protocol range |
| `CAPABILITY_DENIED` | Requested capability not granted to role | Request appropriate permissions or elevate role |

---

## Payload Schemas

### Complete Egress Payload (OpenClaw → n8n Webhook)

```json
{
  "action": "string — identifies the specific operation",
  "payload": {
    "...": "structured data specific to the workflow"
  },
  "metadata": {
    "agent_session": "string — current OpenClaw session ID",
    "timestamp": "ISO 8601",
    "model": "string — LLM model used for decision"
  }
}
```

### Complete Ingress Payload (n8n → OpenClaw Gateway)

```json
{
  "model": "claude-sonnet-4-20250514",
  "user": "n8n-workflow-{workflow_id}",
  "input": [
    {
      "role": "user",
      "content": "Workflow execution complete. Results: {structured_summary}"
    }
  ],
  "instructions": "Process this workflow result. Summarize key findings for the user. Do not re-trigger the workflow.",
  "stream": false,
  "timeout_seconds": 0
}
```

### Minimal Ingress Payload (Notification Only)

```json
{
  "model": "claude-sonnet-4-20250514",
  "user": "n8n-global",
  "input": [
    {
      "role": "user",
      "content": "Alert: Workflow 'daily-backup' failed at 03:15 UTC. Error: disk full."
    }
  ],
  "timeout_seconds": 0
}
```

### Image Injection Payload

```json
{
  "model": "claude-sonnet-4-20250514",
  "user": "n8n-workflow-chart-generator",
  "input": [
    {
      "type": "input_image",
      "image_url": "https://internal-cdn.example.com/charts/q3-revenue.png"
    },
    {
      "role": "user",
      "content": "Analyze this Q3 revenue chart generated by the reporting workflow."
    }
  ],
  "timeout_seconds": 0
}
```
