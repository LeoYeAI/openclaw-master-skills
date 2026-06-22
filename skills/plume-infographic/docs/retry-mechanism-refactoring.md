# Retry Mechanism Refactoring: Action Log Replacing Single Snapshot

## Background

The current retry mechanism relies on `~/.openclaw/media/plume/last_result_{channel}.json` to store the last **successful** task result snapshot. This design has two core flaws:

### Flaw 1: Operation Context Lost, "Try Again" Semantics Incorrect

| Step | User Action | Actual Behavior | Expected Behavior |
|------|------------|-----------------|-------------------|
| 1 | Generate infographic | Task A succeeds, last_result = A | - |
| 2 | "Replace content with XXX" | switch_content on A → Task B succeeds, last_result = B | - |
| 3 | "Try again" | repeat_last_task on B | Should execute switch_content on A with same params again |

The agent cannot distinguish "repeat last operation" from "rerun last task" because last_result only has task_id, no operation parameters.

### Flaw 2: Failed Operation Context Completely Discarded

| Step | User Action | Actual Behavior | Expected Behavior |
|------|------------|-----------------|-------------------|
| 1 | Generate infographic | Task A succeeds, last_result = A | - |
| 2 | "Switch style" | switch_style on A → Task B **fails**, last_result still A | - |
| 3 | "Try again" | repeat_last_task on A (regenerates original) | Should retry switch_style on A |

Not writing last_result on failure is reasonable (shouldn't overwrite successful result), but the operation context is also lost.

## Design

### Core Idea

Replace single snapshot `last_result_{channel}.json` with action log array `action_log_{channel}.json`, using **two-step writes**:

- `create_infographic.py` appends a record immediately after task creation (with complete operation params, status=pending)
- `poll_cron.py` updates the corresponding record's status and result fields when task reaches terminal state

### Data Structure

File path: `~/.openclaw/media/plume/action_log_{channel}.json`

```json
[
  {
    "task_id": "abc123",
    "action": null,
    "mode": "article",
    "params": {
      "article": "Complete content about the history of gold...",
      "style_hint": "classical",
      "aspect_ratio": "3:4",
      "locale": "zh-CN"
    },
    "status": "success",
    "result_url": "https://r2.example.com/xxx.png",
    "result_urls": null,
    "local_file": "/Users/xxx/.openclaw/media/plume/result_abc123.png",
    "local_files": null,
    "created_at": 1711234000.0,
    "completed_at": 1711234300.0
  },
  {
    "task_id": "def456",
    "action": "switch_content",
    "last_task_id": "abc123",
    "mode": "article",
    "params": {
      "article": "User's new replacement content..."
    },
    "status": "failed",
    "error": "Generation timeout",
    "created_at": 1711234500.0,
    "completed_at": 1711234800.0
  },
  {
    "task_id": "ghi789",
    "action": "switch_style",
    "last_task_id": "abc123",
    "mode": "article",
    "params": {},
    "status": "pending",
    "created_at": 1711235000.0
  }
]
```

Field descriptions:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Task ID |
| `action` | string \| null | Operation type: null=first creation, repeat_last_task/switch_style/switch_content/switch_all |
| `last_task_id` | string \| null | Source task ID for retry (present when action is not null) |
| `mode` | string | article / reference |
| `params` | object | Key parameter snapshot at creation time (see below) |
| `status` | string | pending / success / failed / timeout / cancelled |
| `result_url` | string \| null | Result URL on success (first image) |
| `result_urls` | string[] \| null | All result URLs on success (multiple images) |
| `local_file` | string \| null | Local file path on success (first image) |
| `local_files` | string[] \| null | All local file paths on success (multiple images) |
| `error` | string \| null | Error message on failure |
| `created_at` | float | Creation timestamp |
| `completed_at` | float \| null | Completion timestamp |

Fields saved in `params` (varies by mode):

| mode | Saved Fields |
|------|-------------|
| article | article, style_hint, aspect_ratio, locale, count, child_reference_type |
| reference | reference_type, reference_image_urls, reference_topic, reference_article, aspect_ratio, locale |

### Log Limit

Array retains a maximum of **10 entries**, FIFO eviction for oldest records. Rationale:
- 10 JSON entries ≈ 2-4KB, manageable token cost for agent reads
- Sufficient to trace user's recent operation chain
- Prevents unbounded file growth

## Code Changes

### 1. New shared module `scripts/action_log.py`

Handles log read/write, shared by create_infographic.py and poll_cron.py.

```python
"""Action log read/write module"""

import json
import time
from pathlib import Path

MEDIA_DIR = Path.home() / ".openclaw" / "media" / "plume"
MAX_LOG_SIZE = 10


def _log_path(channel: str) -> Path:
    filename = f"action_log_{channel}.json" if channel else "action_log.json"
    return MEDIA_DIR / filename


def read_log(channel: str) -> list[dict]:
    path = _log_path(channel)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_log(channel: str, log: list[dict]):
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    # FIFO eviction
    if len(log) > MAX_LOG_SIZE:
        log = log[-MAX_LOG_SIZE:]
    _log_path(channel).write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def append_entry(channel: str, entry: dict):
    """Called on task creation: append a pending record"""
    log = read_log(channel)
    entry.setdefault("status", "pending")
    entry.setdefault("created_at", time.time())
    log.append(entry)
    _write_log(channel, log)


def update_entry(channel: str, task_id: str, updates: dict):
    """Called at task terminal state: update status/result fields of the corresponding record"""
    log = read_log(channel)
    for entry in reversed(log):
        if entry.get("task_id") == task_id:
            entry.update(updates)
            entry.setdefault("completed_at", time.time())
            break
    _write_log(channel, log)
```

### 2. Changes to `scripts/create_infographic.py`

After successful task creation in `cmd_create()`, append a log record.

New `--channel` parameter needed to determine which channel's log file to write to.

```python
# At the end of cmd_create(), inside the result.get("success") branch:

import action_log

if result.get("success"):
    task_data = result.get("data", {})
    task_id = task_data.get("id")

    # Build log entry
    log_entry = {
        "task_id": task_id,
        "action": args.action,
        "last_task_id": args.last_task_id,
        "mode": mode,
        "params": _build_params_snapshot(args, mode),
    }
    if args.channel:
        action_log.append_entry(args.channel, log_entry)

    output({...})  # Original output unchanged
```

`_build_params_snapshot` extracts parameters to save:

```python
def _build_params_snapshot(args, mode: str) -> dict:
    """Extract creation parameter snapshot for retry restoration"""
    params = {}
    # Common fields
    for key in ("article", "style_hint", "aspect_ratio", "locale"):
        val = getattr(args, key, None)
        if val is not None:
            params[key] = val
    # Reference mode fields
    if mode == "reference":
        for key in ("reference_type", "reference_image_urls",
                     "reference_topic", "reference_article"):
            val = getattr(args, key, None)
            if val is not None:
                params[key] = val
    # Batch fields
    if (args.count or 1) >= 2:
        params["count"] = args.count
        if args.child_reference_type:
            params["child_reference_type"] = args.child_reference_type
    return params
```

### 3. Changes to `scripts/poll_cron.py`

In `_handle_completed()`, update log record when task reaches terminal state.

poll_cron needs to know the channel (already available).

```python
import action_log

def _handle_completed(task_id, task, channel, target):
    status = task.get("status", 0)

    if status == 3:
        # ... Original download and delivery logic unchanged ...

        # Update action log
        action_log.update_entry(channel, task_id, {
            "status": "success",
            "result_url": result_url,       # or result_urls[0]
            "result_urls": result_urls,      # for multiple images
            "local_file": local_file,        # or local_files[0]
            "local_files": local_files,      # for multiple images
        })

        # Retain last_result write (backward compatibility, transition period)
        # ...original last_result write logic...

    else:
        status_map = {4: "failed", 5: "timeout", 6: "cancelled"}
        action_log.update_entry(channel, task_id, {
            "status": status_map.get(status, f"unknown_{status}"),
            "error": task.get("result", ""),
        })

        # ...original error delivery logic unchanged...
```

### 4. Changes to `SKILL.md` retry instructions

Replace existing retry section:

```markdown
### Retry (for existing results)

When user requests "switch style/change look/switch content/regenerate/try again":

1. Read action log: `cat ~/.openclaw/media/plume/action_log_{channel}.json`

2. Select base record based on user intent:

   | User Intent | Base Record Selection Rule |
   |------------|--------------------------|
   | "Try again" / "Regenerate" | Take the **last entry** in log (regardless of success/failure), replay with same params |
   | "Switch style" / "Switch content" | Take the **most recent entry with status=success**, use its task_id as last_task_id |

3. Build retry command:

   **"Try again" logic:**
   - If last entry's `action` is null (first creation) → `repeat_last_task --last-task-id={task_id}`
   - If last entry's `action` is not null (some retry operation) → replay with **same action and params**, `--last-task-id` from last entry's `last_task_id` (retry based on same source task)
   - If last entry `status=failed`, still follow above rules (this is the core fix)

   **"Switch style/content" logic:**
   - Use most recent success record's task_id as `--last-task-id`
   - Combine with corresponding `--action`

4. If log is empty or no suitable record found → prompt user to generate an infographic first
```

### 5. Backward Compatibility & Transition

- **Retain `last_result_{channel}.json` writes during transition period**, ensuring other potential dependents are unaffected
- SKILL.md read logic changed to prefer `action_log_{channel}.json`, fallback to `last_result_{channel}.json`
- Remove last_result reads and writes after transition period

### 6. New `--channel` parameter in `create_infographic.py`

```python
# New parameter for create subcommand
p_create.add_argument("--channel", help="Channel identifier, for writing action log")
```

SKILL.md calls to create should include `--channel`:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel feishu \
  --mode article \
  --article "..." \
  ...
```

## Changed Files Summary

| File | Change Type | Description |
|------|------------|-------------|
| `scripts/action_log.py` | New | Action log read/write module |
| `scripts/create_infographic.py` | Modified | New --channel param; append log after successful creation |
| `scripts/poll_cron.py` | Modified | Update log at task terminal state; retain last_result write during transition |
| `SKILL.md` | Modified | Retry instructions changed to action log based |

## Scenario Validation

### Scenario A: Normal Retry

1. User generates infographic → Task A success → log: `[{A, action:null, status:success}]`
2. User "replace content with XXX" → Task B success → log: `[{A, ...}, {B, action:switch_content, last_task_id:A, params:{article:"XXX"}, status:success}]`
3. User "try again" → Take log[-1] = B, action=switch_content → replay switch_content on A with same params → Task C

Result: Correctly repeated the "switch content" operation.

### Scenario B: Retry After Failure

1. User generates infographic → Task A success
2. User "switch style" → Task B **failed** → log: `[{A, status:success}, {B, action:switch_style, last_task_id:A, status:failed}]`
3. User "try again" → Take log[-1] = B, action=switch_style, last_task_id=A → replay switch_style on A → Task C

Result: Correctly retried the failed style switch, instead of regenerating the original.

### Scenario C: Change Direction After Failure

1. User generates infographic → Task A success
2. User "switch style" → Task B failed
3. User "never mind, replace content with YYY" → Take most recent success = A → switch_content on A with article=YYY → Task C

Result: Correctly switched content based on the last successful task.

### Scenario D: Consecutive Failures

1. Task A success
2. switch_style → Task B failed
3. "Try again" → switch_style on A → Task C failed
4. "Try again" → switch_style on A → Task D (still retrying based on A, no vicious cycle)

Result: Consecutive failures don't cause a vicious cycle, because last_task_id always points to the successful source task A.
