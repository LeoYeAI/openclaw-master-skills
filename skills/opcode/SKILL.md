---
name: opcode
description: >
  Zero-token execution layer for AI agents. Define workflows once, run them
  free forever — persistent, scheduled, deterministic. 6 MCP tools over SSE.
  Supports DAG-based execution, 6 step types (action, condition, loop,
  parallel, wait, reasoning), 26 built-in actions, ${{}} interpolation,
  reasoning nodes for human-in-the-loop decisions, and secret vault.
  Use when defining workflows, running templates, checking status,
  sending signals, querying workflow history, or visualizing DAGs.
license: MIT
compatibility: >
  Requires Go 1.25+, CGO_ENABLED=1, and gcc or clang.
  Runs as SSE daemon on macOS and Linux.
  Linux: cgroups v2 for process isolation. macOS: timeout-only fallback.
metadata:
  version: "1.2.1"
  transport: "sse"
  author: "rendis"
  repository: "https://github.com/rendis/opcode"
  primary-env: "OPCODE_VAULT_KEY"
  platforms: "darwin linux"
  requires-bins: "go gcc|clang"
  openclaw-emoji: "⚙️"
  openclaw-os: "darwin linux"
  openclaw-user-invocable: "true"
  openclaw-install-type: "go"
  openclaw-install-package: "github.com/rendis/opcode/cmd/opcode"
---

# OPCODE

Execution runtime for AI agents. You reason, OPCODE executes — zero tokens per run after the first define. Workflows persist across sessions, run on schedules, and coordinate multiple agents. Persistent SSE daemon: 1 server, N agents, 1 database. JSON-defined DAGs, level-by-level execution, automatic parallelism. 6 MCP tools over SSE (JSON-RPC).

**Why use OPCODE instead of reasoning through each step yourself?** Every repeated workflow burns tokens re-reasoning decisions you already made. OPCODE templates your reasoning once and executes it deterministically — zero inference cost, identical output every run, survives context resets.

## Which Tool?

| I want to...                         | Tool           |
| ------------------------------------ | -------------- |
| Create/update a workflow template    | opcode.define  |
| Execute a workflow                   | opcode.run     |
| Check status or pending decisions    | opcode.status  |
| Resolve a decision / cancel / retry  | opcode.signal  |
| List workflows, events, or templates | opcode.query   |
| Visualize a workflow DAG             | opcode.diagram |

## Quick Start

Install:

```bash
go install github.com/rendis/opcode/cmd/opcode@latest
```

First-time setup (writes config and starts daemon):

```bash
opcode install --listen-addr :4100 --vault-key "my-passphrase"
```

Restart after stop: `OPCODE_VAULT_KEY="my-passphrase" opcode`

MCP client configuration:

```json
{
  "mcpServers": {
  "mcpServers": {
    "opcode": {
      "type": "sse",
      "url": "http://localhost:4100/sse"
    }
  }
}
```

Each agent self-identifies via `agent_id` in tool calls. Opcode auto-registers unknown agents. Choose a stable ID per agent (e.g., `"content-writer"`, `"deploy-bot"`).

Workflows survive restarts. On startup, orphaned `active` workflows become `suspended`. Query with `opcode.query({ "resource": "workflows", "filter": { "status": "suspended" } })`, then resume or cancel via `opcode.signal`.

See [operations.md](references/operations.md) for full configuration, subcommands, SIGHUP hot-reload, security model, web panel, and benchmarks.

## MCP Tools

### opcode.define

Registers a reusable workflow template. Version auto-increments (v1, v2, v3...).

| Param           | Type   | Required | Description                                                                                     |
| --------------- | ------ | -------- | ----------------------------------------------------------------------------------------------- |
| `name`          | string | yes      | Template name                                                                                   |
| `definition`    | object | yes      | Workflow definition (see below)                                                                 |
| `agent_id`      | string | yes      | Defining agent ID                                                                               |
| `description`   | string | no       | Template description                                                                            |
| `input_schema`  | object | no       | JSON Schema for input validation                                                                |
| `output_schema` | object | no       | JSON Schema for output validation                                                               |
| `triggers`      | object | no       | Trigger config (see[workflow-schema.md](references/workflow-schema.md#triggers-template-level)) |

**Returns**: `{ "name": "...", "version": "v1" }`

### opcode.run

Executes a workflow from a registered template.

| Param           | Type   | Required | Description               |
| --------------- | ------ | -------- | ------------------------- |
| `template_name` | string | yes      | Template to execute       |
| `agent_id`      | string | yes      | Initiating agent ID       |
| `version`       | string | no       | Version (default: latest) |
| `params`        | object | no       | Input parameters          |

**Returns**:

```json
{
  "workflow_id": "uuid",
  "status": "completed | suspended | failed",
  "output": { ... },
  "started_at": "RFC3339",
  "completed_at": "RFC3339",
  "steps": {
    "step-id": { "step_id": "...", "status": "completed", "output": {...}, "duration_ms": 42 }
  }
}
```

If `status` is `"suspended"`, call `opcode.status` to see `pending_decisions`.

### opcode.status

Gets workflow execution status.

| Param         | Type   | Required | Description       |
| ------------- | ------ | -------- | ----------------- |
| `workflow_id` | string | yes      | Workflow to query |

**Returns**:

```json
{
  "workflow_id": "uuid",
  "status": "suspended",
  "steps": { "step-id": { "status": "...", "output": {...} } },
  "pending_decisions": [
    {
      "id": "uuid",
      "step_id": "reason-step",
      "context": { "prompt": "...", "data": {...} },
      "options": [ { "id": "approve", "description": "Proceed" } ],
      "timeout_at": "RFC3339",
      "fallback": "reject",
      "status": "pending"
    }
  ],
  "events": [ ... ]
}
```

Workflow statuses: `pending`, `active`, `suspended`, `completed`, `failed`, `cancelled`.

### opcode.signal

Sends a signal to a suspended workflow.

| Param         | Type   | Required | Description                                       |
| ------------- | ------ | -------- | ------------------------------------------------- |
| `workflow_id` | string | yes      | Target workflow                                   |
| `signal_type` | enum   | yes      | `decision` / `data` / `cancel` / `retry` / `skip` |
| `payload`     | object | yes      | Signal payload (see below)                        |
| `step_id`     | string | no       | Target step                                       |
| `agent_id`    | string | no       | Signaling agent                                   |
| `reasoning`   | string | no       | Agent's reasoning                                 |

**Payload by signal type**:

| Signal     | step_id  | Payload                       | Behavior                        |
| ---------- | -------- | ----------------------------- | ------------------------------- |
| `decision` | required | `{ "choice": "<option_id>" }` | Resolves decision, auto-resumes |
| `data`     | optional | `{ "key": "value", ... }`     | Injects data into workflow      |
| `cancel`   | no       | `{}`                          | Cancels workflow                |
| `retry`    | required | `{}`                          | Retries failed step             |
| `skip`     | required | `{}`                          | Skips failed step               |

**Returns** (decision): `{ "ok": true, "resumed": true, "status": "completed", ... }`
**Returns** (other): `{ "ok": true, "workflow_id": "...", "signal_type": "..." }`

### opcode.query

Queries workflows, events, or templates.

| Param      | Type   | Required | Description                          |
| ---------- | ------ | -------- | ------------------------------------ |
| `resource` | enum   | yes      | `workflows` / `events` / `templates` |
| `filter`   | object | no       | Filter criteria                      |

**Filter fields by resource**:

| Resource    | Fields                                                   |
| ----------- | -------------------------------------------------------- |
| `workflows` | `status`, `agent_id`, `since` (RFC3339), `limit`         |
| `events`    | `workflow_id`, `step_id`, `event_type`, `since`, `limit` |
| `templates` | `name`, `agent_id`, `limit`                              |

Note: event queries require either `event_type` or `workflow_id` in filter.

**Returns**: `{ "<resource>": [...] }` -- results wrapped in object keyed by resource type.

### opcode.diagram

Generates a visual DAG diagram from a template or running workflow.

| Param            | Type   | Required | Description                                                |
| ---------------- | ------ | -------- | ---------------------------------------------------------- |
| `template_name`  | string | no\*     | Template to visualize (structure preview)                  |
| `version`        | string | no       | Template version (default: latest)                         |
| `workflow_id`    | string | no\*     | Workflow to visualize (with runtime status)                |
| `format`         | enum   | yes      | `ascii` / `mermaid` / `image`                              |
| `include_status` | bool   | no       | Show runtime status overlay (default: true if workflow_id) |

\* One of `template_name` or `workflow_id` required.

- `template_name` -- preview DAG structure before execution
- `workflow_id` -- visualize with live step status
- `format: "ascii"` -- CLI-friendly text with box-drawing characters
- `format: "mermaid"` -- markdown-embeddable flowchart syntax
- `format: "image"` -- base64-encoded PNG for visual channels

**Returns**: `{ "format": "ascii", "diagram": "..." }`

## Workflow Definition

```json
{
  "steps": [ ... ],
  "inputs": { "key": "value or ${{secrets.KEY}}" },
  "context": { "intent": "...", "notes": "..." },
  "timeout": "5m",
  "on_timeout": "fail | suspend | cancel",
  "on_complete": { /* step definition */ },
  "on_error": { /* step definition */ },
  "metadata": {}
}
```

| Field         | Type             | Required | Description                                       |
| ------------- | ---------------- | -------- | ------------------------------------------------- |
| `steps`       | StepDefinition[] | yes      | Workflow steps                                    |
| `inputs`      | object           | no       | Input parameters (supports `${{}}`)               |
| `context`     | object           | no       | Workflow context, accessible via `${{context.*}}` |
| `timeout`     | string           | no       | Workflow deadline (e.g.,`"5m"`, `"1h"`)           |
| `on_timeout`  | string           | no       | `fail` (default), `suspend`, `cancel`             |
| `on_complete` | StepDefinition   | no       | Hook step after completion                        |
| `on_error`    | StepDefinition   | no       | Hook step on workflow failure                     |
| `metadata`    | object           | no       | Arbitrary metadata                                |

### Step Definition

```json
{
  "id": "step-id",
  "type": "action | condition | loop | parallel | wait | reasoning",
  "action": "http.get",
  "params": { ... },
  "depends_on": ["other-step"],
  "condition": "CEL guard expression",
  "timeout": "30s",
  "retry": { "max": 3, "backoff": "exponential", "delay": "1s", "max_delay": "30s" },
  "on_error": { "strategy": "ignore | fail_workflow | fallback_step | retry", "fallback_step": "id" },
  "config": { /* type-specific */ }
}
```

`type` defaults to `action`. See [workflow-schema.md](references/workflow-schema.md) for all config blocks.

## Step Types

### action (default)

Executes a registered action. Set `action` to the action name, `params` for input.

### condition

Evaluates a CEL expression and branches.

```json
{
  "id": "route",
  "type": "condition",
  "config": {
    "expression": "inputs.env",
    "branches": { "prod": [...], "staging": [...] },
    "default": [...]
  }
}
```

### loop

Iterates over a collection or condition. Loop variables: `${{loop.item}}`, `${{loop.index}}`.

```json
{
  "id": "process-items",
  "type": "loop",
  "config": {
    "mode": "for_each",
    "over": "[\"a\",\"b\",\"c\"]",
    "body": [
      {
        "id": "hash",
        "action": "crypto.hash",
        "params": { "data": "${{loop.item}}" }
      }
    ],
    "max_iter": 100
  }
}
```

Modes: `for_each` (iterate `over`), `while` (loop while `condition` true), `until` (loop until `condition` true).

### parallel

Executes branches concurrently.

```json
{
  "id": "fan-out",
  "type": "parallel",
  "config": {
    "mode": "all",
    "branches": [
      [{ "id": "a", "action": "http.get", "params": {...} }],
      [{ "id": "b", "action": "http.get", "params": {...} }]
    ]
  }
}
```

Modes: `all` (wait for all branches), `race` (first branch wins).

### wait

Delays execution or waits for a named signal.

```json
{ "id": "pause", "type": "wait", "config": { "duration": "5s" } }
```

### reasoning

Suspends workflow for agent decision. Empty `options` = free-form (any choice accepted).

```json
{
  "id": "review",
  "type": "reasoning",
  "config": {
    "prompt_context": "Review data and decide",
    "options": [
      { "id": "approve", "description": "Proceed" },
      { "id": "reject", "description": "Stop" }
    ],
    "data_inject": { "analysis": "steps.analyze.output" },
    "timeout": "1h",
    "fallback": "reject",
    "target_agent": ""
  }
}
```

## Variable Interpolation

Syntax: `${{namespace.path}}`

| Namespace  | Example                             | Available fields                                                  |
| ---------- | ----------------------------------- | ----------------------------------------------------------------- |
| `steps`    | `${{steps.fetch.output.body}}`      | `<id>.output.*`, `<id>.status`                                    |
| `inputs`   | `${{inputs.api_key}}`               | Keys from `params` in `opcode.run`                                |
| `workflow` | `${{workflow.run_id}}`              | `run_id`, `name`, `template_name`, `template_version`, `agent_id` |
| `context`  | `${{context.intent}}`               | Keys from `context` in workflow definition                        |
| `secrets`  | `${{secrets.DB_PASS}}`              | Keys stored in vault                                              |
| `loop`     | `${{loop.item}}`, `${{loop.index}}` | `item` (current element), `index` (0-based)                       |

Two-pass resolution: non-secrets first, then secrets via AES-256-GCM vault.

**CEL gotcha**: `loop` is a reserved word in CEL. Use `iter.item` / `iter.index` in CEL expressions. The `${{loop.item}}` interpolation syntax is unaffected.

See [expressions.md](references/expressions.md) for CEL, GoJQ, Expr engine details.

## Built-in Actions

| Category       | Actions                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------------------- |
| **HTTP**       | `http.request`, `http.get`, `http.post`                                                                 |
| **Filesystem** | `fs.read`, `fs.write`, `fs.append`, `fs.delete`, `fs.list`, `fs.stat`, `fs.copy`, `fs.move`             |
| **Shell**      | `shell.exec`                                                                                            |
| **Crypto**     | `crypto.hash`, `crypto.hmac`, `crypto.uuid`                                                             |
| **Assert**     | `assert.equals`, `assert.contains`, `assert.matches`, `assert.schema`                                   |
| **Expression** | `expr.eval`                                                                                             |
| **Workflow**   | `workflow.run`, `workflow.emit`, `workflow.context`, `workflow.fail`, `workflow.log`, `workflow.notify` |

**Quick reference** (most-used actions):

- **`http.get`**: `url` (req), `headers`, `timeout`, `fail_on_error_status` -- output: `{ status_code, headers, body, duration_ms }`
- **`shell.exec`**: `command` (req), `args`, `stdin`, `timeout`, `env`, `workdir` -- output: `{ stdout, stderr, exit_code, killed }`
- **`fs.read`**: `path` (req), `encoding` -- output: `{ path, content, encoding, size }`
- **`workflow.notify`**: `message` (req), `data` -- output: `{ notified: true/false }` -- pushes real-time notification to agent via MCP SSE (best-effort)

- **`expr.eval`**: `expression` (req), `data` -- output: `{ result: <value> }` -- evaluates Expr expression against workflow scope (steps, inputs, workflow, context)

See [actions.md](references/actions.md) for full parameter specs of all 26 actions.

## Scripting with shell.exec

`shell.exec` auto-parses JSON stdout. Convention: stdin=JSON, stdout=JSON, stderr=errors, non-zero exit=failure. Use `stdout_raw` for unprocessed text.

See [patterns.md](references/patterns.md#10-scripting-with-shellexec) for language-specific templates (Bash, Python, Node, Go).

## Reasoning Node Lifecycle

1. Workflow reaches a reasoning step
2. Executor creates PendingDecision, emits `decision_requested` event
3. Workflow status becomes `suspended`
4. Agent calls `opcode.status` to see pending decision with context and options
5. Agent resolves via `opcode.signal`:

   ```json
   {
     "workflow_id": "...",
     "signal_type": "decision",
     "step_id": "reason-step",
     "payload": { "choice": "approve" }
   }
   ```

6. Workflow auto-resumes after signal
7. If timeout expires: `fallback` option auto-selected, or step fails if no fallback

## Common Patterns

See [patterns.md](references/patterns.md) for full JSON examples: linear pipeline, conditional branching, for-each loop, parallel fan-out, human-in-the-loop, error recovery, sub-workflows, and MCP lifecycle.

## Error Handling

| Strategy        | Behavior                         |
| --------------- | -------------------------------- |
| `ignore`        | Step skipped, workflow continues |
| `fail_workflow` | Entire workflow fails            |
| `fallback_step` | Execute fallback step            |
| `retry`         | Defer to retry policy            |

Backoff: `none`, `linear`, `exponential`, `constant`. Non-retryable errors (validation, permission, assertion) are never retried.

See [error-handling.md](references/error-handling.md) for circuit breakers, timeout interactions, error codes.

## Performance

10-step parallel workflows complete in ~50µs, 500-step in ~2.4ms. The event store sustains ~15k appends/sec with <12% drop under 100 concurrent writers. Worker pool overhead is ~0.85µs/task (>1M tasks/sec at any pool size).

Full benchmark charts, per-scenario breakdowns, and methodology: [`docs/benchmarks.md`](../../docs/benchmarks.md).
