---
name: cloud-functions
description: Complete guide for CloudBase cloud functions development - supports both Event Functions (Node.js) and HTTP Functions (multi-language Web services). Covers runtime selection, deployment, logging, invocation, scf_bootstrap, SSE, WebSocket, and HTTP access configuration.
alwaysApply: false
---

# Cloud Functions Development

Use this skill when developing, deploying, and managing CloudBase cloud functions. CloudBase supports two types of cloud functions:

- **Event Functions (普通云函数)**: Traditional serverless functions triggered by events (SDK calls, timers)
- **HTTP Functions (HTTP 云函数)**: Web service functions triggered by HTTP requests, supporting multiple languages

## When to use this skill

Use this skill for **cloud function operations** when you need to:

- Create and deploy Event Functions (Node.js)
- Create and deploy HTTP Functions (Node.js/Python/Go/Java)
- Understand runtime limitations and selection
- Query function logs and monitor execution
- Invoke cloud functions from applications
- Configure HTTP access for cloud functions
- Implement SSE (Server-Sent Events) or WebSocket

**Do NOT use for:**
- CloudRun backend services (use `cloudrun-development` skill)
- Complex container-based services (use `cloudrun-development` skill)
- Database operations (use database skills)

## How to use this skill (for a coding agent)

1. **Choose the right function type**
   - **Event Function**: For SDK calls, scheduled tasks, event-driven scenarios
   - **HTTP Function**: For Web APIs, REST services, SSE/WebSocket, multi-language support

2. **Understand runtime limitations**
   - Runtime **CANNOT be changed** after function creation
   - Must select correct runtime during initial creation
   - If runtime needs to change, must delete and recreate function

3. **Deploy functions correctly**
   - **MCP Tool**: Use `createFunction` with `type: "Event"` or `type: "HTTP"`
   - **CLI**: Use `tcb fn deploy` (Event) or `tcb fn deploy --httpFn` (HTTP)
   - HTTP Functions require `scf_bootstrap` file in the function directory
   - Provide correct `functionRootPath` (parent directory of function folder)

4. **Query logs properly**
   - Use `getFunctionLogs` for log list (basic info)
   - Use `getFunctionLogDetail` with RequestId for detailed logs
   - Note time range limitations (max 1 day interval)

---

## Function Types Comparison

| Feature | Event Function (普通云函数) | HTTP Function (HTTP 云函数) |
|---------|---------------------------|----------------------------|
| Trigger | Event-driven (SDK, timer) | HTTP request |
| Entry Point | `exports.main = async (event, context) => {}` | Web Server (Express/Flask/Gin etc.) |
| Port | No port required | **Must listen on port 9000** |
| Bootstrap | Not required | Requires `scf_bootstrap` |
| Connection | Short connection | Supports long connection |
| Languages | Node.js only | Node.js, Python, Go, Java |
| Protocols | N/A | HTTP, SSE, WebSocket |
| Use Cases | Event processing, scheduled tasks | Web APIs, REST services, real-time streaming |

---

## Core Knowledge - Event Functions

### Runtime Environment

**⚠️ CRITICAL: Runtime cannot be modified after function creation**

Once a cloud function is created with a specific runtime, the runtime **cannot be changed**. If you need a different runtime:

1. Delete the existing function
2. Create a new function with the desired runtime

**Supported Node.js Runtimes:**

- `Nodejs18.15` (Default, Recommended)
- `Nodejs16.13`
- `Nodejs14.18`
- `Nodejs12.16`
- `Nodejs10.15`
- `Nodejs8.9`

**Runtime Selection Guidelines:**

- **Use `Nodejs18.15`** for new projects (default, most modern)
- Choose older versions only if dependencies require specific Node.js versions
- Consider security updates and support lifecycle
- Test thoroughly with selected runtime before deployment

### Event Function Structure

Event functions require:

1. **Function Directory**: Contains function code
   - Must have `index.js` (or specified entry file)
   - Must export handler: `exports.main = async (event, context) => {}`
   - Include `package.json` with dependencies

2. **Function Root Path**: Parent directory containing function directories
   - Example: If function is at `/project/cloudfunctions/myFunction/`
   - `functionRootPath` should be `/project/cloudfunctions/`
   - **Important**: Do NOT include function name in root path

3. **Entry Point**: Default is `index.js` with `exports.main`
   - Can be customized via `handler` parameter

### Event Function Deployment

**Creating New Functions:**

Use `createFunction` tool (see MCP tool documentation for full parameter list):
- **Important**: Always specify `func.runtime` explicitly (defaults to `Nodejs18.15`)
- Provide `functionRootPath` as parent directory of function folders (absolute path)
- Use `force=true` to overwrite existing function

**Updating Function Code:**

Use `updateFunctionCode` tool:
- **⚠️ Note**: Only updates code, **cannot change runtime**
- If runtime needs to change, delete and recreate function

**Deployment Best Practices:**

1. **Always specify runtime** explicitly when creating functions
2. **Use absolute paths** for `functionRootPath`
3. **Don't upload node_modules** - dependencies installed automatically
4. **Test locally** before deployment when possible
5. **Use environment variables** for configuration, not hardcoded values

---

## Core Knowledge - HTTP Functions

### HTTP Function Overview

HTTP Functions are optimized for Web service scenarios, supporting standard HTTP request/response patterns.

**Key Characteristics:**
- **Must listen on port 9000** (platform requirement)
- Requires `scf_bootstrap` startup script
- Supports multiple languages: Node.js, Python, Go, Java
- Supports HTTP, SSE, WebSocket protocols

### scf_bootstrap Startup Script

**⚠️ CRITICAL: HTTP Functions require `scf_bootstrap` file**

| Requirement | Description |
|-------------|-------------|
| File name | Must be exactly `scf_bootstrap` (no extension) |
| Permission | Must have execute permission (`chmod +x scf_bootstrap`) |
| Port | Must start server on port **9000** |
| Line endings | Must use LF (Unix), not CRLF (Windows) |

**Examples:**
```bash
# Node.js
#!/bin/bash
node index.js

# Python
#!/bin/bash
export PYTHONPATH="./third_party:$PYTHONPATH"
/var/lang/python310/bin/python3.10 app.py

# Go
#!/bin/bash
./main

# Java
#!/bin/bash
java -jar *.jar
```

### HTTP Function Structure & Example

```
my-http-function/
├── scf_bootstrap      # Required: startup script
├── package.json       # Dependencies
└── index.js           # Application code
```

**Node.js Example (Express):**
```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => res.json({ message: 'Hello!' }));
app.listen(9000);  // Must be port 9000
```

### HTTP Function Deployment

**MCP Tool:**
```javascript
createFunction({
  func: {
    name: "myHttpFunction",
    type: "HTTP",           // Required for HTTP Function
    protocolType: "HTTP",   // "HTTP" (default) or "WS" (WebSocket)
    timeout: 60
  },
  functionRootPath: "/path/to/functions",
  force: false
})
```

**CLI:**
```bash
tcb fn deploy <name> --httpFn        # HTTP Function
tcb fn deploy <name> --httpFn --ws   # With WebSocket
```

**⚠️ Notes:**
- Function type **cannot be changed** after creation
- HTTP Functions do NOT auto-install dependencies; include `node_modules` or use layers

### Invoking HTTP Functions

**Method 1: HTTP API (with Access Token)**
```bash
curl -L 'https://{envId}.api.tcloudbasegateway.com/v1/functions/{name}?webfn=true' \
  -H 'Authorization: Bearer <TOKEN>'
```
**⚠️ Must include `webfn=true` parameter**

**Method 2: HTTP Access Service (Custom Domain)**

Use `createFunctionHTTPAccess` MCP tool to configure HTTP access:

```javascript
createFunctionHTTPAccess({
  name: "myHttpFunction",
  type: "HTTP",           // "HTTP" for HTTP Function
  path: "/api/hello",     // Trigger path
  // domain: "your-domain.com"  // Optional custom domain
})
```

```bash
# Access via default domain
curl https://{envId}.{region}.app.tcloudbase.com/{path}

# Access via custom domain
curl https://your-domain.com/{path}
```

| Method | Auth Required | Use Case |
|--------|--------------|----------|
| HTTP API (`?webfn=true`) | Yes (Bearer Token) | Server-to-server |
| HTTP Access Service | Optional | Browser, public APIs |

### SSE & WebSocket Support

**SSE (Server-Sent Events):** Enabled by default, for server-to-client streaming (AI chat, progress updates).

```javascript
// Server
res.setHeader('Content-Type', 'text/event-stream');
res.write(`data: ${JSON.stringify({ content: 'Hello' })}\n\n`);

// Client
const es = new EventSource('https://your-domain/stream');
es.onmessage = (e) => console.log(JSON.parse(e.data));
```

**WebSocket:** Enable via `protocolType: "WS"` in `createFunction`. For bidirectional real-time communication.

| Limit | Value |
|-------|-------|
| Idle timeout | 10 - 7200 seconds |
| Max message size | 256KB |

```javascript
const wss = new WebSocket.Server({ port: 9000 });
wss.on('connection', (ws) => {
  ws.on('message', (msg) => ws.send(`Echo: ${msg}`));
});
```

---

### Function Logs

**Querying Logs:**

**Primary Method:** Use `getFunctionLogs` and `getFunctionLogDetail` tools (see MCP tool documentation).

**Alternative Method (Plan B):** If tools unavailable, use `callCloudApi`:

1. **Get Log List** - Use `GetFunctionLogs` action:
```
callCloudApi({
  service: "tcb",
  action: "GetFunctionLogs",
  params: {
    EnvId: "{envId}",
    FunctionName: "functionName",
    Offset: 0,
    Limit: 10,
    StartTime: "2024-01-01 00:00:00",
    EndTime: "2024-01-01 23:59:59",
    LogRequestId: "optional-request-id",
    Qualifier: "$LATEST"
  }
})
```

2. **Get Log Details** - Use `GetFunctionLogDetail` action (requires LogRequestId from step 1):
```
callCloudApi({
  service: "tcb",
  action: "GetFunctionLogDetail",
  params: {
    StartTime: "2024-01-01 00:00:00",
    EndTime: "2024-01-01 23:59:59",
    LogRequestId: "request-id-from-log-list"
  }
})
```

**Log Query Limitations:**

- `Offset + Limit` cannot exceed 10000
- `StartTime` and `EndTime` interval cannot exceed 1 day
- Use pagination for large time ranges

**Log Query Best Practices:**

1. Query logs within 1-day windows
2. Use RequestId for specific invocation debugging
3. Combine list and detail queries for comprehensive debugging
4. Check logs after deployment to verify function behavior

### Invoking Event Functions

**From Web Applications:**

```javascript
import cloudbaseSDK from "@cloudbase/js-sdk";

const cloudbase = cloudbaseSDK.init({
  env: 'your-env-id',
  region: 'ap-shanghai',
  accessKey: 'your-access-key'
});

// Call event function
const result = await cloudbase.callFunction({
  name: "functionName",
  data: { /* function parameters */ }
});
```

**From Mini Programs:**

```javascript
wx.cloud.callFunction({
  name: "functionName",
  data: { /* function parameters */ }
}).then(res => {
  console.log(res.result);
});
```

**From Node.js Backend:**

```javascript
const cloudbase = require("@cloudbase/node-sdk");

const app = cloudbase.init({
  env: "your-env-id"
});

const result = await app.callFunction({
  name: "functionName",
  data: { /* function parameters */ }
});
```

**From HTTP API:**

Use CloudBase HTTP API to invoke event functions:
- Endpoint: `https://{envId}.api.tcloudbasegateway.com/v1/functions/{functionName}`
- Requires authentication token (Bearer Token)
- See `http-api` skill for details

### HTTP Access Configuration (for Event Functions)

**HTTP Access vs HTTP API:**

- **HTTP API**: Uses CloudBase API endpoint with authentication token
- **HTTP Access**: Creates direct HTTP/HTTPS endpoint for standard REST API access without SDK

**Creating HTTP Access:**

**Primary Method:** Use `createFunctionHTTPAccess` tool (see MCP tool documentation).

**Alternative Method (Plan B):** If tool unavailable, use `callCloudApi` with `CreateCloudBaseGWAPI`:

```
callCloudApi({
  service: "tcb",
  action: "CreateCloudBaseGWAPI",
  params: {
    EnableUnion: true,
    Path: "/api/users",
    ServiceId: "{envId}",
    Type: 6,
    Name: "functionName",
    AuthSwitch: 2,
    PathTransmission: 2,
    EnableRegion: true,
    Domain: "*"  // Use "*" for default domain, or custom domain name
  }
})
```

**Key Parameters:**
- `Type: 6` - Cloud Function type (required)
- `AuthSwitch: 2` - No auth (1 = with auth)
- `Domain: "*"` - Default domain, or specify custom domain

**Access URL:** `https://{envId}.{region}.app.tcloudbase.com/{path}` or `https://{domain}/{path}`

### Function Configuration

**Environment Variables:**

Set via `func.envVariables` when creating/updating:
```javascript
{
  envVariables: {
    "DATABASE_URL": "mysql://...",
    "API_KEY": "secret-key"
  }
}
```

**⚠️ CRITICAL: Environment Variable Update Constraint**

When updating environment variables for existing functions:

1. **MUST first query current environment variables** using `getFunctionList` with `action=detail` to get the function's current configuration
2. **MUST merge** new environment variables with existing ones
3. **DO NOT directly overwrite** - this will delete existing environment variables not included in the update

**Correct Update Pattern:**

```javascript
// 1. First, get current function details
const currentFunction = await getFunctionList({
  action: "detail",
  name: "functionName"
});

// 2. Merge existing envVariables with new ones
const mergedEnvVariables = {
  ...currentFunction.EnvVariables,  // Existing variables
  ...newEnvVariables                 // New/updated variables
};

// 3. Update with merged variables
await updateFunctionConfig({
  funcParam: {
    name: "functionName",
    envVariables: mergedEnvVariables
  }
});
```

**Why This Matters:**

- Direct overwrite will **delete** all environment variables not included in the update
- This can break function functionality if critical variables are removed
- Always preserve existing configuration when making partial updates

**Timeout Configuration:**

Set via `func.timeout` (in seconds):
- Default timeout varies by runtime
- Maximum timeout depends on runtime version
- Consider function execution time when setting

**Timer Triggers:**

Configure via `func.triggers`:
- Type: `timer` (only supported type)
- Config: Cron expression (7 fields: second minute hour day month week year)
- Examples:
  - `"0 0 2 1 * * *"` - 2:00 AM on 1st of every month
  - `"0 30 9 * * * *"` - 9:30 AM every day

**VPC Configuration:**

For accessing VPC resources:
```javascript
{
  vpc: {
    vpcId: "vpc-xxxxx",
    subnetId: "subnet-xxxxx"
  }
}
```

## MCP Tools Reference

**Function Management:**
- `getFunctionList` - List functions or get function details
- `createFunction` - Create cloud function (supports both Event and HTTP types via `type` parameter)
  - `type: "Event"` - Event Function (default)
  - `type: "HTTP"` - HTTP Function
  - `protocolType: "WS"` - Enable WebSocket for HTTP Function
- `updateFunctionCode` - Update function code (runtime cannot change)
- `updateFunctionConfig` - Update function configuration (⚠️ when updating envVariables, must first query and merge with existing values to avoid overwriting)

**Logging:**
- `getFunctionLogs` - Get function log list (basic info)
- `getFunctionLogDetail` - Get detailed log content by RequestId
- `callCloudApi` (Plan B) - Use `GetFunctionLogs` and `GetFunctionLogDetail` actions if direct tools unavailable

**HTTP Access:**
- `createFunctionHTTPAccess` - Create HTTP access for function (supports both Event and HTTP types via `type` parameter)
- `callCloudApi` (Plan B) - Use `CreateCloudBaseGWAPI` action if direct tool unavailable

**Triggers:**
- `manageFunctionTriggers` - Create or delete function triggers

**CLI Commands:**
- `tcb fn deploy <name>` - Deploy Event Function
- `tcb fn deploy <name> --httpFn` - Deploy HTTP Function
- `tcb fn deploy <name> --httpFn --ws` - Deploy HTTP Function with WebSocket
- `tcb fn deploy --all` - Deploy all functions in config

## Common Patterns

### Error Handling

```javascript
exports.main = async (event, context) => {
  try {
    // Function logic
    return {
      code: 0,
      message: "Success",
      data: result
    };
  } catch (error) {
    return {
      code: -1,
      message: error.message,
      data: null
    };
  }
};
```

### Environment Variable Usage

```javascript
exports.main = async (event, context) => {
  const apiKey = process.env.API_KEY;
  const dbUrl = process.env.DATABASE_URL;
  
  // Use environment variables
};
```

### Database Operations

```javascript
const cloudbase = require("@cloudbase/node-sdk");

const app = cloudbase.init({
  env: process.env.ENV_ID
});

exports.main = async (event, context) => {
  const db = app.database();
  const result = await db.collection("users").get();
  return result;
};
```

## Best Practices

### General Best Practices
1. **Runtime Selection**: Always specify runtime explicitly, use `Nodejs18.15` for new projects
2. **Code Organization**: Keep functions focused and single-purpose
3. **Error Handling**: Always implement proper error handling
4. **Environment Variables**: Use env vars for configuration, never hardcode secrets
5. **Logging**: Add meaningful logs for debugging
6. **Testing**: Test functions locally when possible before deployment
7. **Security**: Implement authentication/authorization for HTTP access
8. **Performance**: Optimize cold start time, use connection pooling for databases
9. **Monitoring**: Regularly check logs and monitor function performance
10. **Documentation**: Document function parameters and return values

### HTTP Function Specific Best Practices
1. **Port Configuration**: Always listen on port 9000
2. **scf_bootstrap**: Ensure correct file permissions and LF line endings
3. **Health Check**: Add `/health` endpoint for monitoring
4. **CORS**: Configure CORS headers for browser access
5. **Graceful Shutdown**: Handle process signals properly
6. **Dependencies**: Include `node_modules` in package or use layers (no auto-install for HTTP Functions)
7. **Timeout**: Set appropriate timeout for long-running SSE/WebSocket connections
8. **Error Responses**: Return proper HTTP status codes and error messages

### Choosing Between Event and HTTP Functions

| Scenario | Recommended Type |
|----------|-----------------|
| SDK/Mini Program calls | Event Function |
| Scheduled tasks (cron) | Event Function |
| REST API / Web services | HTTP Function |
| SSE streaming (AI chat) | HTTP Function |
| WebSocket real-time | HTTP Function |
| File upload/download | HTTP Function |
| Multi-language support | HTTP Function |

## Related Skills

- `cloudrun-development` - For container-based backend services
- `http-api` - For HTTP API invocation patterns
- `cloudbase-platform` - For general CloudBase platform knowledge

