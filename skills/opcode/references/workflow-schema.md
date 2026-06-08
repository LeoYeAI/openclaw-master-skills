# Workflow Schema Reference

## WorkflowDefinition

```json
{
  "steps": [],
  "inputs": {},
  "timeout": "5m",
  "on_timeout": "fail",
  "on_complete": null,
  "on_error": null,
  "metadata": {}
}
```

| Field         | Type             | Required | Description                                     |
| ------------- | ---------------- | -------- | ----------------------------------------------- |
| `steps`       | StepDefinition[] | yes      | Workflow steps                                  |
| `inputs`      | map[string]any   | no       | Input parameters (supports ${{}} interpolation) |
| `timeout`     | string           | no       | Workflow deadline (e.g., "5m", "1h")            |
| `on_timeout`  | string           | no       | `fail` (default), `suspend`, `cancel`           |
| `on_complete` | StepDefinition   | no       | Hook step after completion                      |
| `on_error`    | StepDefinition   | no       | Hook step on workflow failure                   |
| `metadata`    | map[string]any   | no       | Arbitrary metadata                              |

## StepDefinition

```json
{
  "id": "step-id",
  "type": "action",
  "action": "http.get",
  "params": {},
  "depends_on": [],
  "condition": "",
  "timeout": "30s",
  "retry": null,
  "on_error": null,
  "config": null
}
```

| Field        | Type         | Required | Description                                      |
| ------------ | ------------ | -------- | ------------------------------------------------ |
| `id`         | string       | yes      | Unique step ID within workflow                   |
| `type`       | StepType     | no       | Default:`action`                                 |
| `action`     | string       | no       | Action name (required for action type)           |
| `params`     | object       | no       | Action parameters (supports ${{}} interpolation) |
| `depends_on` | string[]     | no       | Step IDs that must complete first                |
| `condition`  | string       | no       | CEL guard expression; step skipped if false      |
| `timeout`    | string       | no       | Step-level timeout                               |
| `retry`      | RetryPolicy  | no       | Retry configuration                              |
| `on_error`   | ErrorHandler | no       | Error handling strategy                          |
| `config`     | object       | no       | Type-specific config (see below)                 |

## Type-Specific Configs

### ConditionConfig

```json
{
  "expression": "inputs.env == 'prod'",
  "branches": {
    "true": [ { "id": "deploy", "action": "shell.exec", "params": {...} } ],
    "false": [ { "id": "test", "action": "shell.exec", "params": {...} } ]
  },
  "default": []
}
```

| Field        | Type                        | Required | Description                |
| ------------ | --------------------------- | -------- | -------------------------- |
| `expression` | string                      | yes      | CEL expression to evaluate |
| `branches`   | map[string]StepDefinition[] | yes      | Value -> steps mapping     |
| `default`    | StepDefinition[]            | no       | Steps if no branch matches |

Sub-step IDs are namespaced: `parentID.branchName.subStepID`.

### LoopConfig

```json
{
  "mode": "for_each",
  "over": "[\"a\",\"b\",\"c\"]",
  "condition": "",
  "body": [
    {
      "id": "process",
      "action": "crypto.hash",
      "params": { "data": "${{loop.item}}" }
    }
  ],
  "max_iter": 100
}
```

| Field       | Type             | Required    | Description                                          |
| ----------- | ---------------- | ----------- | ---------------------------------------------------- |
| `mode`      | string           | yes         | `for_each`, `while`, `until`                         |
| `over`      | string           | for_each    | Expression producing iterable (GoJQ or JSON literal) |
| `condition` | string           | while/until | CEL condition for while/until loops                  |
| `body`      | StepDefinition[] | yes         | Steps to execute per iteration                       |
| `max_iter`  | int              | no          | Maximum iterations (safety limit)                    |

Loop variables: `${{loop.item}}`, `${{loop.index}}`. In CEL: `iter.item`, `iter.index`.

### ParallelConfig

```json
{
  "mode": "all",
  "branches": [
    [ { "id": "branch-a", "action": "http.get", "params": {...} } ],
    [ { "id": "branch-b", "action": "http.get", "params": {...} } ]
  ]
}
```

| Field      | Type               | Required | Description                                              |
| ---------- | ------------------ | -------- | -------------------------------------------------------- |
| `branches` | StepDefinition[][] | yes      | Array of step arrays (one per branch)                    |
| `mode`     | string             | no       | `all` (default): wait for all; `race`: first branch wins |

### WaitConfig

```json
{ "duration": "5s" }
```

| Field      | Type   | Required | Description                     |
| ---------- | ------ | -------- | ------------------------------- |
| `duration` | string | no       | Time to wait (e.g., "5s", "1m") |
| `signal`   | string | no       | Wait for named signal           |

One of `duration` or `signal` is required.

### ReasoningConfig

```json
{
  "prompt_context": "Review analysis and decide next action",
  "data_inject": { "analysis": "steps.analyze.output" },
  "options": [
    { "id": "approve", "description": "Proceed with deployment" },
    { "id": "reject", "description": "Cancel deployment" }
  ],
  "timeout": "1h",
  "fallback": "reject",
  "target_agent": ""
}
```

| Field            | Type              | Required | Description                                       |
| ---------------- | ----------------- | -------- | ------------------------------------------------- |
| `prompt_context` | string            | yes      | Context for the decision maker                    |
| `data_inject`    | map[string]string | no       | Step output paths to inject into decision context |
| `options`        | ReasoningOption[] | no       | Available choices. Empty = free-form              |
| `timeout`        | string            | no       | Decision deadline                                 |
| `fallback`       | string            | no       | Option ID auto-selected on timeout                |
| `target_agent`   | string            | no       | Specific agent to resolve                         |

## RetryPolicy

```json
{ "max": 3, "backoff": "exponential", "delay": "1s", "max_delay": "30s" }
```

| Field       | Type   | Default | Description                                 |
| ----------- | ------ | ------- | ------------------------------------------- |
| `max`       | int    | 0       | Maximum retry attempts                      |
| `backoff`   | string | `none`  | `none`, `linear`, `exponential`, `constant` |
| `delay`     | string | -       | Initial delay (e.g., "500ms", "1s")         |
| `max_delay` | string | -       | Cap on backoff delay                        |

## ErrorHandler

```json
{ "strategy": "fallback_step", "fallback_step": "backup-step" }
```

| Field           | Type   | Required | Description                                         |
| --------------- | ------ | -------- | --------------------------------------------------- |
| `strategy`      | string | yes      | `ignore`, `fail_workflow`, `fallback_step`, `retry` |
| `fallback_step` | string | no       | Step ID for fallback_step strategy                  |

## Workflow Statuses

`pending` -> `active` -> `completed` / `failed` / `cancelled` / `suspended`

`suspended` -> `active` (resume) / `cancelled` / `failed`

## Step Statuses

`pending` -> `scheduled` -> `running` -> `completed` / `failed` / `skipped` / `suspended` / `retrying`

`suspended` -> `running` (resume) / `failed` / `skipped`

`retrying` -> `running` (retry) / `failed`

## Signal Types

| Type       | Description                           |
| ---------- | ------------------------------------- |
| `decision` | Resolve a pending reasoning decision  |
| `data`     | Inject data into a suspended workflow |
| `cancel`   | Cancel the workflow                   |
| `retry`    | Retry a failed step                   |
| `skip`     | Skip a suspended step                 |

## Event Types

For use with `opcode.query` resource `events` filter `event_type`:

**Workflow lifecycle**: `workflow_started`, `workflow_completed`, `workflow_failed`, `workflow_cancelled`, `workflow_suspended`, `workflow_resumed`, `workflow_timed_out`

**Step lifecycle**: `step_started`, `step_completed`, `step_failed`, `step_skipped`, `step_retrying`, `step_suspended`

**Decision**: `decision_requested`, `decision_resolved`

**Signal**: `signal_received`, `variable_set`, `dag_mutated`

**Error handling**: `step_retry_attempt`, `error_handler_invoked`, `step_fallback`, `step_ignored`

**Circuit breaker**: `circuit_breaker_open`, `circuit_breaker_half_open`, `circuit_breaker_closed`

**Flow control**: `condition_evaluated`, `loop_iter_started`, `loop_iter_completed`, `loop_completed`, `parallel_started`, `parallel_completed`, `wait_started`, `wait_completed`

## Triggers (Template-level)

The `triggers` field in `opcode.define` stores trigger metadata on the template. Currently used as a storage placeholder for cron/webhook configuration. Scheduled jobs are created separately via the Store API / web panel.

```json
{
  "triggers": {
    "cron": [
      {
        "name": "daily-cleanup",
        "expression": "0 2 * * *",
        "enabled": true,
        "params": { "retention_days": 30 }
      }
    ]
  }
}
```

### ScheduledJob

Cron jobs are the primary trigger implementation. Managed via web panel (Scheduler page) or Store API.

```json
{
  "id": "uuid",
  "template_name": "my-template",
  "template_version": "v1",
  "cron_expression": "0 * * * *",
  "params": { "key": "value" },
  "agent_id": "bot-1",
  "enabled": true,
  "last_run_at": "RFC3339",
  "next_run_at": "RFC3339",
  "last_run_status": "completed"
}
```

| Field              | Type   | Required | Description                   |
| ------------------ | ------ | -------- | ----------------------------- |
| `id`               | string | auto     | UUID, auto-generated          |
| `template_name`    | string | yes      | Template to execute           |
| `template_version` | string | no       | Version (default: latest)     |
| `cron_expression`  | string | yes      | Standard 5-field Unix cron    |
| `params`           | object | no       | Input parameters for each run |
| `agent_id`         | string | yes      | Agent identity for executions |
| `enabled`          | bool   | yes      | Whether job is active         |
| `last_run_at`      | string | auto     | Last execution timestamp      |
| `next_run_at`      | string | auto     | Next scheduled execution      |
| `last_run_status`  | string | auto     | Status of last run            |

### Cron Expression Format

Standard 5-field Unix cron (via `robfig/cron` v3):

```plaintext
┌───────── minute (0-59)
│ ┌─────── hour (0-23)
│ │ ┌───── day of month (1-31)
│ │ │ ┌─── month (1-12)
│ │ │ │ ┌─ day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

Examples: `*/15 * * * *` (every 15 min), `0 2 * * *` (daily 2am), `0 * * * *` (hourly).

The scheduler ticks every 60 seconds, executes due jobs, and recovers missed jobs on startup via `RecoverMissed()`. Concurrent executions of the same job are deduplicated.

## Real-time Notifications

Use `workflow.notify` to push notifications to the agent at any point in the workflow. The agent is identified by the workflow's `agent_id`. If the agent is not connected via SSE, the step completes without error (best-effort).

```json
{
  "steps": [
    {
      "id": "fetch",
      "action": "http.get",
      "params": { "url": "https://api.example.com/data" }
    },
    {
      "id": "notify-done",
      "action": "workflow.notify",
      "params": {
        "message": "Data fetch complete",
        "data": "${{steps.fetch.output}}"
      },
      "depends_on": ["fetch"]
    }
  ]
}
```

Scheduled workflow example -- notify the agent on failure:

```json
{
  "steps": [
    {
      "id": "check",
      "action": "http.get",
      "params": { "url": "https://api.example.com/health" }
    },
    {
      "id": "alert",
      "action": "workflow.notify",
      "params": {
        "message": "Health check failed: ${{steps.check.output.status_code}}"
      },
      "depends_on": ["check"],
      "condition": "${{steps.check.output.status_code != 200}}"
    }
  ]
}
```
