# Synchronous Execution Mode Plan

## Background

The original plume-infographic task execution was fire-and-forget mode:

```
agent calls create → register starts background polling subprocess → agent ends current turn immediately
```

The background subprocess `poll_cron.py` can only execute hardcoded logic (download image + `openclaw message send`), unable to perform subsequent operations. This means multi-step orchestrations like "generate infographic → zip → send to me" cannot be achieved.

Compared to ComfyUI Skill's synchronous blocking mode: agent calls script → script polls internally → returns result path → agent continues with subsequent operations. OpenClaw's exec tool has a `yieldMs` mechanism (default 10s), long-running commands automatically go to background, agent retrieves results via `process` tool poll, logically still "get complete result then continue".

## Goal

Change `create_infographic.py`'s `create` subcommand to synchronous mode: create task + poll wait + download result, all in one step. Agent gets complete result (local image path) and can continue with any subsequent operations (deliver, package, format conversion, etc.).

No longer retain async mode, `poll_cron.py` is no longer used.

## Scope of Changes

| File | Change |
|------|--------|
| `scripts/create_infographic.py` | `create` changed to sync mode, new polling/download functions |
| `SKILL.md` | Updated to pure sync workflow |
| `scripts/plume_api.py` | No changes |
| `scripts/action_log.py` | No changes |

## Detailed Design

### 1. `create` Subcommand (Synchronous)

New parameters on top of existing ones:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--poll-interval` | 10 | Polling interval (seconds) |
| `--timeout` | 1800 | Max wait time (seconds, default 30 minutes), returns error on timeout |

Execution flow:

```
create
  │
  ├─ 1. _do_create(args): parameter validation + task creation
  │     Calls plume_api.create_task() to get task_id
  │
  ├─ 2. _poll_until_done(task_id, interval, timeout)
  │     while elapsed < timeout:
  │       plume_api.get_task(task_id)
  │       if status >= 3: break
  │       Output progress to stderr (doesn't affect stdout JSON)
  │       sleep(poll_interval)
  │
  ├─ 3a. Success (status=3)
  │     _download_results() downloads all result images to MEDIA_DIR
  │     Update action_log
  │     stdout output:
  │     {
  │       "success": true,
  │       "task_id": "xxx",
  │       "status": 3,
  │       "images": ["/abs/path/result_xxx_1.png", ...],
  │       "result_urls": ["https://..."],
  │       "count": 1,
  │       "credits_cost": 10
  │     }
  │
  ├─ 3b. Failure (status=4/5/6)
  │     Update action_log
  │     stdout output:
  │     {
  │       "success": false,
  │       "task_id": "xxx",
  │       "status": 4,
  │       "status_text": "Failed",
  │       "error": "..."
  │     }
  │
  └─ 3c. Timeout (elapsed >= timeout)
        stdout output:
        {
          "success": false,
          "task_id": "xxx",
          "status": "timeout",
          "error": "Wait timeout (1800s), task is still processing"
        }
```

### 2. Code Structure

Extract original `cmd_create`'s parameter validation and task creation logic into `_do_create(args)` returning a dict, `cmd_create` calls it then continues with polling and downloading.

New functions:
- `_poll_until_done(task_id, interval, timeout)` — synchronous polling
- `_download_file(url, output_path)` — download single file
- `_extract_result_urls(task_result)` — extract URL list from task result
- `_download_results(task_id, task)` — download all result images

### 3. Integration with OpenClaw exec

OpenClaw's exec tool automatically moves commands to background after exceeding `yieldMs` (default 10s). Agent retrieves output via `process poll`. This means:

- `create` can safely block for several minutes without freezing the agent
- Agent gets stdout JSON and can continue with any operation (zip, format conversion, send, etc.)
- We don't need to handle timeout-to-background logic ourselves, OpenClaw framework handles it

## Usage Examples

### Example 1: Generate Infographic + Deliver

User: "Make an infographic about the origin of gold"

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel feishu --mode article \
  --article "The origin and history of gold: from ancient Egypt to modern finance..."

# Returns: {"success": true, "images": ["/Users/xxx/.openclaw/media/plume/result_123.png"]}

openclaw message send --channel feishu --target ou_xxx \
  --media /Users/xxx/.openclaw/media/plume/result_123.png --message "Infographic generation complete"
```

### Example 2: Generate Infographic + Zip

User: "Generate an infographic about the origin of gold, then zip it and send to me"

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel feishu --mode article \
  --article "The origin and history of gold: from ancient Egypt to modern finance..."

# Returns: {"success": true, "images": ["/Users/xxx/.openclaw/media/plume/result_123.png"]}

zip -j /tmp/gold_infographic.zip /Users/xxx/.openclaw/media/plume/result_123.png

openclaw message send --channel feishu --target ou_xxx \
  --media /tmp/gold_infographic.zip --message "Gold origin infographic packaged and ready"
```

### Example 3: Batch Generate + Zip

User: "Make 5 infographics about solar system planets as a series, package and send to me"

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --channel feishu --mode article \
  --article "Solar system eight planets series..." \
  --count 5 --timeout 2400

# Returns: {"success": true, "images": ["/.../result_456_1.png", "/.../result_456_2.png", ...]}

zip -j /tmp/solar_system.zip /.../result_456_1.png /.../result_456_2.png ...

openclaw message send --channel feishu --target ou_xxx \
  --media /tmp/solar_system.zip --message "Solar system planet series infographics (5 images) packaged"
```

## Deprecated Parts

- `poll_cron.py` — No longer used (async polling + delivery)
- All `poll_cron.py register` related instructions in SKILL.md have been removed
