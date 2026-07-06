# Queue Schema Reference

Complete documentation for model-queue queue file format.

---

## Queue File Location

```
${MODEL_QUEUES_DIR}/{source_name}.json
```

Example:
- `~/.openclaw/model-queues/ollama-local.json`
- `~/.openclaw/model-queues/ollama-remote.json`

---

## Top-Level Queue Object

```json
{
  "version": "1.0",
  "source": "ollama-local",
  "models": ["ollama/llama3", "ollama/qwen2.5"],
  "maxConcurrent": 1,
  "maxRetries": 3,
  "lastId": "T-005",
  "tasks": [...]
}
```

### Queue Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Schema version. Current: `"1.0"` |
| `source` | string | Model source identifier |
| `models` | array | List of models in this source |
| `maxConcurrent` | integer | Max simultaneous tasks (default: 1) |
| `maxRetries` | integer | Max retry attempts per task |
| `lastId` | string | Last assigned task ID |
| `tasks` | array | Array of task objects |

---

## Task Object

```json
{
  "id": "T-003",
  "queue": "ollama-local",
  "model": "ollama/qwen2.5",
  "description": "Analyze the sales data and generate insights",
  "goal": "Generate a summary of Q1 sales performance with key metrics",
  "status": "pending",
  "priority": 0,
  
  "depends_on": null,
  "on_depends_fail": "block",
  "context_input": null,
  
  "result": null,
  "result_status": null,
  "result_summary": null,
  "error_message": null,
  
  "retries": 0,
  "maxRetries": 3,
  "subagent_session": null,
  
  "added_at": "2026-03-04T16:51:00Z",
  "started_at": null,
  "completed_at": null
}
```

---

## Field Details

### Identification Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique task ID. Format: `T-NNN` (per-queue numbering) |
| `queue` | string | Yes | Source name this task belongs to |
| `model` | string | Yes | Target model for execution |

### Task Definition Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Original user request (verbatim or lightly cleaned) |
| `goal` | string | Yes | Parsed objective in one clear sentence |
| `priority` | integer | No | Higher = first. Default: 0 |
| `status` | string | Yes | Current state (see Status Values) |

### Dependency Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `depends_on` | string\|null | No | Task ID this depends on |
| `on_depends_fail` | string | No | `block` \| `skip` \| `continue`. Default: `block` |
| `context_input` | object\|null | No | Context from dependency (auto-populated) |

### Result Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `result` | string\|null | No | Full result from execution |
| `result_status` | string\|null | No | `success` \| `partial` \| `failed` |
| `result_summary` | string\|null | No | Human-readable summary (1-2 sentences) |
| `error_message` | string\|null | No | Error details if failed |

### Execution Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `retries` | integer | Yes | Execution attempts so far. Default: 0 |
| `maxRetries` | integer | Yes | Max attempts before failing |
| `subagent_session` | string\|null | No | Session ID when running |

### Timestamp Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `added_at` | ISO 8601 | Yes | When added to queue |
| `started_at` | ISO 8601\|null | No | When execution started |
| `completed_at` | ISO 8601\|null | No | When reached terminal state |

---

## Status Values

| Status | Description | Transitions To |
|--------|-------------|----------------|
| `pending` | Ready to be dispatched | `running`, `waiting` |
| `waiting` | Waiting for dependency | `pending` (when dep done), `blocked`, `skipped` |
| `running` | Currently executing | `done`, `failed` |
| `done` | Completed successfully | Archive |
| `failed` | Failed after max retries | Archive |
| `blocked` | Dependency failed, needs action | `pending` (after user action) |
| `skipped` | Skipped intentionally | Archive |

---

## Context Input Object

When a task depends on another, `context_input` is auto-populated:

```json
{
  "context_input": {
    "source_task": "T-002",
    "result_summary": "Q1 sales: $2.3M, up 15% YoY",
    "result_status": "success",
    "included_at": "2026-03-04T17:05:00Z"
  }
}
```

---

## ID Numbering

- IDs are per-queue: each queue starts at T-001
- Format: `T-NNN` (3 digits minimum)
- When N > 999, expand: `T-1000`, `T-1001`
- IDs never reused within a queue

---

## Full Example

```json
{
  "version": "1.0",
  "source": "ollama-local",
  "models": ["ollama/llama3", "ollama/qwen2.5"],
  "maxConcurrent": 1,
  "maxRetries": 3,
  "lastId": "T-003",
  "tasks": [
    {
      "id": "T-001",
      "queue": "ollama-local",
      "model": "ollama/qwen2.5",
      "description": "Analyze Q1 sales data",
      "goal": "Generate sales performance summary",
      "status": "done",
      "priority": 0,
      "depends_on": null,
      "on_depends_fail": "block",
      "context_input": null,
      "result": "Full analysis text...",
      "result_status": "success",
      "result_summary": "Q1 sales: $2.3M, up 15% YoY. Top products: Widget A, Widget B.",
      "error_message": null,
      "retries": 0,
      "maxRetries": 3,
      "subagent_session": "agent:main:subagent:abc123",
      "added_at": "2026-03-04T16:51:00Z",
      "started_at": "2026-03-04T16:52:00Z",
      "completed_at": "2026-03-04T16:55:00Z"
    },
    {
      "id": "T-002",
      "queue": "ollama-local",
      "model": "ollama/qwen2.5",
      "description": "Create a report based on the analysis",
      "goal": "Generate formatted report from T-001 results",
      "status": "running",
      "priority": 0,
      "depends_on": "T-001",
      "on_depends_fail": "block",
      "context_input": {
        "source_task": "T-001",
        "result_summary": "Q1 sales: $2.3M, up 15% YoY. Top products: Widget A, Widget B.",
        "result_status": "success",
        "included_at": "2026-03-04T16:55:00Z"
      },
      "result": null,
      "result_status": null,
      "result_summary": null,
      "error_message": null,
      "retries": 0,
      "maxRetries": 3,
      "subagent_session": "agent:main:subagent:def456",
      "added_at": "2026-03-04T16:51:00Z",
      "started_at": "2026-03-04T16:55:00Z",
      "completed_at": null
    },
    {
      "id": "T-003",
      "queue": "ollama-local",
      "model": "ollama/llama3",
      "description": "Summarize the report for the team meeting",
      "goal": "Create a brief summary suitable for team presentation",
      "status": "waiting",
      "priority": 1,
      "depends_on": "T-002",
      "on_depends_fail": "skip",
      "context_input": null,
      "result": null,
      "result_status": null,
      "result_summary": null,
      "error_message": null,
      "retries": 0,
      "maxRetries": 3,
      "subagent_session": null,
      "added_at": "2026-03-04T16:52:00Z",
      "started_at": null,
      "completed_at": null
    }
  ]
}
```

---

## Archive Schema

Archived tasks use the same structure, stored by month:

```
${MODEL_QUEUES_DIR}/archive/{source}/{YYYY-MM}.json
```

Archive file contains:
```json
{
  "source": "ollama-local",
  "month": "2026-03",
  "tasks": [...]
}
```
