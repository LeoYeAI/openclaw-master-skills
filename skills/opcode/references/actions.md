# Built-in Actions Reference

## HTTP Actions

### http.request

Full HTTP request with control over method, headers, body, auth, and redirects.

**Params**:

| Param                  | Type              | Required | Default | Description                   |
| ---------------------- | ----------------- | -------- | ------- | ----------------------------- |
| `url`                  | string            | yes      | -       | Request URL                   |
| `method`               | string            | no       | `GET`   | HTTP method                   |
| `headers`              | map[string]string | no       | -       | Request headers               |
| `body`                 | any               | no       | -       | Request body                  |
| `body_encoding`        | string            | no       | `json`  | `json`, `form`, `text`, `raw` |
| `auth`                 | object            | no       | -       | Auth config (see below)       |
| `timeout`              | string            | no       | `30s`   | Request timeout               |
| `follow_redirects`     | bool              | no       | `true`  | Follow redirects              |
| `max_redirects`        | int               | no       | `10`    | Max redirect hops             |
| `tls_skip_verify`      | bool              | no       | `false` | Skip TLS verification         |
| `fail_on_error_status` | bool              | no       | `false` | Fail on HTTP 4xx/5xx          |

**Auth object**: `{ "type": "bearer|basic|api_key", "token": "...", "username": "...", "password": "...", "header_name": "...", "header_value": "..." }`

**Output**: `{ "status_code": 200, "status": "200 OK", "headers": {...}, "body": ..., "content_type": "...", "duration_ms": 42 }`

### http.get

Convenience GET. Same params as http.request minus `method` (fixed to GET) and `body`/`body_encoding`.

### http.post

Convenience POST. Same params as http.request minus `method` (fixed to POST).

## Filesystem Actions

All FS actions respect isolator path validation (deny_paths, read_only_paths, writable_paths).

### fs.read

| Param      | Type   | Required | Default | Description              |
| ---------- | ------ | -------- | ------- | ------------------------ |
| `path`     | string | yes      | -       | File path                |
| `encoding` | string | no       | `auto`  | `text`, `base64`, `auto` |

**Output**: `{ "path": "...", "content": "...", "encoding": "text", "size": 1024 }`

### fs.write

| Param         | Type   | Required | Default | Description               |
| ------------- | ------ | -------- | ------- | ------------------------- |
| `path`        | string | yes      | -       | File path                 |
| `content`     | string | yes      | -       | Content to write          |
| `create_dirs` | bool   | no       | `false` | Create parent directories |
| `mode`        | int    | no       | `0644`  | File permissions          |

**Output**: `{ "path": "...", "size": 1024 }`

### fs.append

| Param     | Type   | Required | Description       |
| --------- | ------ | -------- | ----------------- |
| `path`    | string | yes      | File path         |
| `content` | string | yes      | Content to append |

**Output**: `{ "path": "...", "size": 2048 }`

### fs.delete

| Param       | Type   | Required | Default | Description                    |
| ----------- | ------ | -------- | ------- | ------------------------------ |
| `path`      | string | yes      | -       | Path to delete                 |
| `recursive` | bool   | no       | `false` | Delete directories recursively |

**Output**: `{ "path": "...", "deleted": true }`

### fs.list

| Param       | Type   | Required | Default | Description                 |
| ----------- | ------ | -------- | ------- | --------------------------- |
| `path`      | string | yes      | -       | Directory path              |
| `pattern`   | string | no       | -       | Glob filter pattern         |
| `recursive` | bool   | no       | `false` | Recurse into subdirectories |

**Output**: `{ "path": "...", "entries": [{ "name": "...", "path": "...", "size": 0, "modified_at": "...", "is_dir": false }] }`

### fs.stat

| Param  | Type   | Required | Description         |
| ------ | ------ | -------- | ------------------- |
| `path` | string | yes      | File/directory path |

**Output**: `{ "path": "...", "size": 1024, "modified_at": "2025-01-01T00:00:00Z", "is_dir": false, "permissions": "0644" }`

### fs.copy

| Param         | Type   | Required | Default | Description               |
| ------------- | ------ | -------- | ------- | ------------------------- |
| `src`         | string | yes      | -       | Source path               |
| `dst`         | string | yes      | -       | Destination path          |
| `create_dirs` | bool   | no       | `false` | Create parent directories |

**Output**: `{ "src": "...", "dst": "...", "size": 1024, "is_dir": false }`

### fs.move

| Param         | Type   | Required | Default | Description               |
| ------------- | ------ | -------- | ------- | ------------------------- |
| `src`         | string | yes      | -       | Source path               |
| `dst`         | string | yes      | -       | Destination path          |
| `create_dirs` | bool   | no       | `false` | Create parent directories |

**Output**: `{ "src": "...", "dst": "...", "size": 1024, "is_dir": false }`

## Shell Actions

### shell.exec

Execute a system command with process isolation.

| Param     | Type              | Required | Default | Description                                    |
| --------- | ----------------- | -------- | ------- | ---------------------------------------------- |
| `command` | string            | yes      | -       | Command to execute                             |
| `args`    | string[]          | no       | -       | Command arguments                              |
| `env`     | map[string]string | no       | -       | Environment variables (added to inherited env) |
| `cwd`     | string            | no       | -       | Working directory                              |
| `stdin`   | string            | no       | -       | Standard input                                 |
| `timeout` | string            | no       | `30s`   | Execution timeout                              |
| `shell`   | bool              | no       | `false` | Run via `/bin/sh -c`                           |

**Output**: `{ "stdout": ..., "stdout_raw": "...", "stderr": "...", "exit_code": 0, "duration_ms": 150, "killed": false }`

- `stdout`: **auto-parsed** if valid JSON (becomes map/array/number), raw string otherwise. Enables `${{steps.cmd.output.stdout.field}}` for JSON-producing scripts.
- `stdout_raw`: always the raw string (use when you need unprocessed text, e.g. `${{steps.cmd.output.stdout_raw}}`).
- `killed`: `true` when process was terminated by timeout.

## Crypto Actions

### crypto.hash

| Param       | Type   | Required | Default  | Description                                 |
| ----------- | ------ | -------- | -------- | ------------------------------------------- |
| `data`      | string | yes      | -        | Data to hash                                |
| `algorithm` | string | no       | `sha256` | `sha256`, `sha512`, `sha384`, `md5`, `sha1` |

**Output**: `{ "hash": "a1b2c3...", "algorithm": "sha256" }`

### crypto.hmac

| Param       | Type   | Required | Default  | Description     |
| ----------- | ------ | -------- | -------- | --------------- |
| `data`      | string | yes      | -        | Data to sign    |
| `key`       | string | yes      | -        | HMAC secret key |
| `algorithm` | string | no       | `sha256` | Hash algorithm  |

**Output**: `{ "hmac": "d4e5f6...", "algorithm": "sha256" }`

### crypto.uuid

No params required.

**Output**: `{ "uuid": "550e8400-e29b-41d4-a716-446655440000" }`

## Assert Actions

All assert actions return `{ "pass": true }` on success or fail with `ASSERTION_FAILED` error.

### assert.equals

| Param      | Type   | Required | Description            |
| ---------- | ------ | -------- | ---------------------- |
| `expected` | any    | yes      | Expected value         |
| `actual`   | any    | yes      | Actual value           |
| `message`  | string | no       | Custom failure message |

Deep equality comparison with JSON number normalization.

### assert.contains

| Param      | Type            | Required | Description            |
| ---------- | --------------- | -------- | ---------------------- |
| `haystack` | string or array | yes      | Value to search in     |
| `needle`   | any             | yes      | Value to find          |
| `message`  | string          | no       | Custom failure message |

String: substring check. Array: element membership.

### assert.matches

| Param     | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `value`   | string | yes      | String to test         |
| `pattern` | string | yes      | Regular expression     |
| `message` | string | no       | Custom failure message |

**Output on success**: `{ "pass": true, "matches": "matched-text" }`

### assert.schema

| Param     | Type   | Required | Description                 |
| --------- | ------ | -------- | --------------------------- |
| `data`    | object | yes      | Data to validate            |
| `schema`  | object | yes      | JSON Schema (Draft 2020-12) |
| `message` | string | no       | Custom failure message      |

## Expression Actions

### expr.eval

Evaluate an [Expr](https://expr-lang.org/) expression against the current workflow scope or explicit data. Uses a compiled program cache for repeated evaluations.

| Param        | Type   | Required | Default | Description                          |
| ------------ | ------ | -------- | ------- | ------------------------------------ |
| `expression` | string | yes      | -       | Expr expression to evaluate          |
| `data`       | any    | no       | -       | Explicit data available as `data` var |

**Scope**: The action context includes `steps`, `inputs`, `workflow`, and `context` — same namespaces as `${{}}` interpolation but accessed directly (e.g., `steps['fetch-data'].body.count`, not `steps.fetch-data.output.body.count`).

**Output**: `{ "result": <evaluated_value> }`

**Available functions**: `filter`, `map`, `count`, `len`, `sum`, `min`, `max`, `any`, `all`, and all standard Expr builtins.

**Examples**:

```json
{ "expression": "filter(steps['fetch-data'].body.items, {.score >= inputs.threshold})" }
{ "expression": "len(filter(data, {.level == 'ERROR'}))", "data": [{"level": "ERROR"}, {"level": "INFO"}] }
{ "expression": "sum(items, {#})", "data": [1, 2, 3] }
```

## Workflow Actions

### workflow.run

| Param           | Type   | Required | Description                  |
| --------------- | ------ | -------- | ---------------------------- |
| `template_name` | string | yes      | Child workflow template name |
| `version`       | string | no       | Template version             |
| `params`        | object | no       | Input parameters for child   |

**Output**: Child workflow's output.

### workflow.emit

| Param        | Type   | Required | Description            |
| ------------ | ------ | -------- | ---------------------- |
| `event_type` | string | yes      | Custom event type name |
| `payload`    | any    | no       | Event payload          |

**Output**: `{ "emitted": true }`

### workflow.context

| Param         | Type   | Required | Description                |
| ------------- | ------ | -------- | -------------------------- |
| `action`      | string | yes      | `read` or `update`         |
| `workflow_id` | string | yes      | Target workflow            |
| `data`        | any    | no       | Data to store (for update) |
| `agent_notes` | string | no       | Agent notes (for update)   |

**Output (read)**: Workflow context object. **Output (update)**: `{ "updated": true }`

### workflow.fail

| Param    | Type   | Required | Description    |
| -------- | ------ | -------- | -------------- |
| `reason` | string | yes      | Failure reason |

Always fails with `NON_RETRYABLE` error. Used to force-fail a workflow from within a step.

### workflow.log

| Param     | Type   | Required | Default | Description                      |
| --------- | ------ | -------- | ------- | -------------------------------- |
| `message` | string | yes      | -       | Log message                      |
| `level`   | string | no       | `info`  | `debug`, `info`, `warn`, `error` |
| `data`    | any    | no       | -       | Structured data to log           |

**Output**: `{ "logged": true }`

### workflow.notify

| Param     | Type   | Required | Default | Description                                |
| --------- | ------ | -------- | ------- | ------------------------------------------ |
| `message` | string | yes      | -       | Notification message                       |
| `data`    | any    | no       | -       | Additional data payload                    |

Pushes a real-time notification to the workflow's agent via MCP SSE. Best-effort: if the agent is not connected, the step completes without error.

**Output**: `{ "notified": true }` or `{ "notified": false, "reason": "..." }`
