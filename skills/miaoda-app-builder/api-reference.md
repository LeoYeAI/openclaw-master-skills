# Miaoda Platform API Reference

All requests must include the following authentication header:

```
Authorization: Bearer <apiKey>
```

All API responses follow a common structure:

```json
{
  "status": 0,
  "data": {...}
}
```

* `status = 0` indicates success
* `status != 0` indicates an error and includes a `msg` field

---

# 1. List Applications

Retrieve a paginated list of applications associated with the current Miaoda account.

**Endpoint**

```
POST /api/v1/app/list
```

**Request**

```json
{
  "name": "",
  "page": 1,
  "size": 12,
  "sort": {
    "direction": "desc",
    "property": "updatedAt"
  }
}
```

| Field            | Description                      |
| ---------------- | -------------------------------- |
| `name`           | Optional app name filter         |
| `page`           | Page index                       |
| `size`           | Page size                        |
| `sort.direction` | Sort direction (`asc` or `desc`) |
| `sort.property`  | Field to sort by                 |

**Response**

```json
{
  "status": 0,
  "data": {
    "items": [
      {
        "appId": "app-xxx",
        "name": "My App",
        "appDesc": "App description",
        "appType": "AGENT",
        "appCreateSource": "miaoda",
        "status": "PUBLISHED",
        "updatedAt": "2024-01-01T00:00:00Z",
        "createdAt": "2024-01-01T00:00:00Z",
        "host": "https://xxx.miaoda.com",
        "hasChange": false,
        "hasBackend": true,
        "versionId": "ver-xxx"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 12
  }
}
```

**Fields**

| Field        | Description                               |
| ------------ | ----------------------------------------- |
| `appId`      | Unique application identifier             |
| `name`       | Application name                          |
| `appDesc`    | Application description                   |
| `appType`    | Application type                          |
| `status`     | Current publish status                    |
| `updatedAt`  | Last update timestamp                     |
| `createdAt`  | Creation timestamp                        |
| `host`       | Public host URL if deployed               |
| `hasChange`  | Indicates unpublished changes             |
| `hasBackend` | Whether the app includes backend services |
| `versionId`  | Current version identifier                |

---

# 2. Get Application Detail

Retrieve full metadata and configuration for a specific application.

**Endpoint**

```
GET /api/v1/app/bootstrap/{app_id}
```

**Response**

```json
{
  "status": 0,
  "data": {
    "appId": "app-854thewfvcht",
    "appDesc": "Write a hello world website",
    "appCreateSource": "",
    "appFocus": "NOT_GENERATE",
    "hasAppHost": false,
    "hasBackend": false,
    "isKeepAlive": false,
    "updatedAt": "2025-12-11T00:28:31.433+08:00",
    "previewUrl": "https://www.miaoda.cn/projects/app-854thewfvcht",
    "miniProgram": {
      "appId": "app-854thewfvcht",
      "enable": false,
      "channelType": "WEAPP",
      "releaseMode": "SHARED",
      "domainName": "miniprogram-weapp-app-xxx.miaoda.cn",
      "urlSchema": "weixin://dl/business/?t=xxx"
    },
    "customDomains": [],
    "supabaseState": {
      "hasSupabase": false
    }
  }
}
```

**Key Fields**

| Field           | Description                            |
| --------------- | -------------------------------------- |
| `appId`         | Application identifier                 |
| `appDesc`       | Application description                |
| `hasAppHost`    | Whether a production host exists       |
| `hasBackend`    | Whether backend services exist         |
| `previewUrl`    | App preview URL (`https://www.miaoda.cn/projects/<appId>`) |
| `isKeepAlive`   | Whether the environment remains active |
| `miniProgram`   | Mini program configuration             |
| `supabaseState` | Supabase integration status            |
| `updatedAt`     | Last modification time                 |

---

# 3. Chat (Application Generation and Iteration)

Miaoda uses a **chat-driven development model**.
Users describe an application or feature, and the system generates or modifies the full-stack project.

The chat API uses **JSON-RPC 2.0**.

**Endpoint**

```
POST /api/v1/conversation/chat
```

**Method**

```
message/send
```

---

## Create a New Application

To create a new application, send the request with:

```
contextId = ""
```

The server automatically creates:

* `appId`
* `conversationId`

**Request**

```json
{
  "jsonrpc": "2.0",
  "method": "message/send",
  "id": "uuid",
  "params": {
    "message": {
      "parts": [
        { "kind": "text", "text": "Create a simple Hello World webpage" }
      ],
      "kind": "message",
      "messageId": "uuid",
      "role": "user",
      "contextId": "",
      "metadata": {},
      "taskId": "",
      "lang": "zh"
    },
    "metadata": {
      "defaultAgent": "AdaPro",
      "agentConfig": {},
      "runtime": "miaoda",
      "queryMode": "deep_mode",
      "inputFieldType": "web"
    }
  }
}
```

**Response**

```json
{
  "result": {
    "contextId": "conv-xxx",
    "status": {
      "state": "submitted",
      "message": {
        "metadata": {
          "appId": "app-xxx",
          "conversationId": "conv-xxx"
        }
      }
    }
  }
}
```

The identifiers returned in `metadata` must be stored for subsequent operations.

---

## Continue an Existing Conversation

To continue modifying an existing application:

* `contextId = conversationId`
* `metadata.appId = appId`

Example structure:

```json
{
  "params": {
    "message": {
      "contextId": "<conversationId>"
    },
    "metadata": {
      "appId": "<appId>"
    }
  }
}
```

---

## Confirm Application Generation

When the trajectory stream returns generated content, the client must confirm application creation.

Send a follow-up request with a **user confirmation flag**.

**Request**

```json
{
  "jsonrpc": "2.0",
  "method": "message/send",
  "id": "uuid",
  "params": {
    "message": {
      "parts": [{ "kind": "text", "text": "Generate application" }],
      "kind": "message",
      "contextId": "<conversationId>"
    },
    "metadata": {
      "defaultAgent": "AdaPro",
      "runtime": "miaoda",
      "queryMode": "deep_mode",
      "userConfirmation": {
        "type": "generateApp"
      }
    }
  }
}
```

**Successful Response**

```json
{
  "result": {
    "status": {
      "state": "submitted"
    }
  }
}
```

A `submitted` state indicates the application has been queued for generation.

---

# 4. Conversation Trajectory (SSE Stream)

Retrieve real-time event streams for an application conversation.

**Endpoint**

```
GET /api/v1/conversation/trajectory
```

**Query Parameters**

```
appId=<appId>
lastEventId=0
```

**Required Headers**

```
Accept: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
Authorization: Bearer <apiKey>
```

**SSE Format**

```
data: {"jsonrpc":"2.0","id":"...","result":{...}}

data: [DONE]
```

**Event Structure**

```json
{
  "status": {
    "state": "working | completed | input-required | failed",
    "message": {
      "parts": [{ "kind": "text", "text": "..." }],
      "role": "agent"
    }
  },
  "metadata": {
    "eventId": 42
  },
  "final": false
}
```

**Stream Termination Conditions**

The stream ends when:

* `status.state = completed`
* `status.state = input-required`
* `final = true`
* `[DONE]` is received

---

# 5. Publish Application

Deploy an application to the production environment.

**Endpoint**

```
POST /api/v1/app/release
```

**Request**

```json
{
  "appId": "app-xxx",
  "appEnv": "PRODUCE",
  "enableWeappMiniProgram": true,
  "isReleaseAppSquare": false,
  "appName": null,
  "enableExclusiveMiniProgram": null
}
```

**Response**

```json
{
  "status": 0,
  "data": {
    "releaseId": "app_release_record-xxx"
  }
}
```

---

## Check Publish Status

**Endpoint**

```
GET /api/v1/app/release/status/{release_id}
```

**Response**

```json
{
  "status": 0,
  "data": {
    "releaseId": "app_release_record-xxx",
    "status": "PROCESSING | SUCCESS | FAILED",
    "appHost": "https://xxx.miaoda.com",
    "errorMsg": null
  }
}
```

**Status Values**

| Status       | Meaning                |
| ------------ | ---------------------- |
| `PROCESSING` | Deployment in progress |
| `SUCCESS`    | Deployment completed   |
| `FAILED`     | Deployment failed      |

Clients should poll this endpoint until the deployment reaches a terminal state.

---

# Error Response

If a request fails, the API returns:

```json
{
  "status": 1,
  "msg": "Error description"
}
```

The `msg` field contains the failure reason.
