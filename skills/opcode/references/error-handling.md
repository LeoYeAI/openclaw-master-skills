# Error Handling Reference

## Retry Policy

```json
{
  "max": 3,
  "backoff": "exponential",
  "delay": "1s",
  "max_delay": "30s"
}
```

### Backoff Strategies

| Strategy      | Formula            | Description                |
| ------------- | ------------------ | -------------------------- |
| `none`        | 0                  | Immediate retry (no delay) |
| `linear`      | delay \* attempt   | Linear increase            |
| `exponential` | delay \* 2^attempt | Exponential increase       |
| `constant`    | delay              | Fixed delay each attempt   |

Each retry attempt gets a fresh `context.WithTimeout`. The `max_delay` caps the computed backoff.

### Non-Retryable Errors

These error codes are never retried regardless of policy:

`VALIDATION_ERROR`, `NOT_FOUND`, `CONFLICT`, `INVALID_TRANSITION`, `CYCLE_DETECTED`, `NON_RETRYABLE`, `PERMISSION_DENIED`, `CIRCUIT_OPEN`, `ASSERTION_FAILED`, `PATH_DENIED`

Retryable errors: `EXECUTION_ERROR`, `TIMEOUT_ERROR`, `STORE_ERROR`, `INTERPOLATION_ERROR`, `ISOLATION_ERROR`, `VAULT_ERROR`

## Error Strategies

Per-step `on_error` configuration:

| Strategy        | Behavior                                                                |
| --------------- | ----------------------------------------------------------------------- |
| `ignore`        | Step marked as skipped, emit `step_ignored` event, workflow continues   |
| `fail_workflow` | Entire workflow fails immediately                                       |
| `fallback_step` | Execute step named in `fallback_step` field, emit `step_fallback` event |
| `retry`         | Defer to retry policy (default if retry configured)                     |

## Timeout Behavior

### Workflow Timeout

Set via `timeout` field at workflow level (e.g., "5m", "1h").

`on_timeout` controls behavior:

| Value            | Behavior                                           |
| ---------------- | -------------------------------------------------- |
| `fail` (default) | Workflow fails with `TIMEOUT_ERROR`                |
| `suspend`        | Workflow suspended (can be resumed)                |
| `cancel`         | Workflow cancelled, all non-terminal steps skipped |

When workflow timeout fires, step-level errors are cleared -- workflow timeout takes precedence.

### Step Timeout

Set via `timeout` field per step. Step fails with `TIMEOUT_ERROR` on expiry. Workflow continues unless error strategy says otherwise.

### Reasoning Timeout

Set via `timeout` in ReasoningConfig. If decision is not resolved before deadline:

- If `fallback` is set: auto-selects fallback option, workflow continues
- If no `fallback`: step fails with `TIMEOUT_ERROR`, workflow fails

## Error Codes

| Code                  | Description                                    | Retryable |
| --------------------- | ---------------------------------------------- | --------- |
| `VALIDATION_ERROR`    | Invalid input, schema violation                | No        |
| `EXECUTION_ERROR`     | Action execution failure                       | Yes       |
| `TIMEOUT_ERROR`       | Step or workflow deadline exceeded             | Yes       |
| `NOT_FOUND`           | Resource not found                             | No        |
| `CONFLICT`            | Duplicate or conflicting state                 | No        |
| `INVALID_TRANSITION`  | Invalid FSM state transition                   | No        |
| `CYCLE_DETECTED`      | DAG contains cycles                            | No        |
| `STEP_FAILED`         | Step execution failed                          | Yes       |
| `CANCELLED`           | Workflow was cancelled                         | Yes       |
| `SIGNAL_FAILED`       | Signal processing failed                       | Yes       |
| `RETRY_EXHAUSTED`     | All retry attempts failed                      | Yes       |
| `STORE_ERROR`         | Database operation failed                      | Yes       |
| `INTERPOLATION_ERROR` | Variable interpolation failed                  | Yes       |
| `CIRCUIT_OPEN`        | Circuit breaker is open                        | No        |
| `NON_RETRYABLE`       | Explicitly non-retryable (e.g., workflow.fail) | No        |
| `PERMISSION_DENIED`   | Access denied                                  | No        |
| `ACTION_UNAVAILABLE`  | Action not registered                          | Yes       |
| `ASSERTION_FAILED`    | Assert action failed                           | No        |
| `ISOLATION_ERROR`     | Process isolation failure                      | Yes       |
| `PATH_DENIED`         | Filesystem path access denied                  | No        |
| `VAULT_ERROR`         | Secret vault operation failed                  | Yes       |

## Circuit Breaker

Per-action failure tracking with configurable thresholds.

### States

| State       | Behavior                              |
| ----------- | ------------------------------------- |
| `closed`    | Normal operation, failures tracked    |
| `open`      | Requests rejected with `CIRCUIT_OPEN` |
| `half-open` | Single probe request allowed through  |

### Events

- `circuit_breaker_open` -- Failure threshold exceeded
- `circuit_breaker_half_open` -- Probe interval elapsed, testing recovery
- `circuit_breaker_closed` -- Probe succeeded, circuit reset

### Error Structure

All errors follow the `OpcodeError` format:

```json
{
  "code": "EXECUTION_ERROR",
  "message": "http.request: request failed: connection refused",
  "details": { "status_code": 500 },
  "step_id": "fetch-data"
}
```
