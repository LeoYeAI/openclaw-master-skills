---
name: telegram-file-browser
description: Build or improve Telegram inline-button file browsers and menu-style navigators. Use when creating Telegram chat UIs for browsing directories, paging lists, previewing files, returning to parent views, closing menus, or exposing copyable file paths. Especially useful when the interaction should stay inside one message via button state updates instead of spamming new messages.
---

> ⚠️ **🚨 CRITICAL BUTTON STRUCTURE WARNING 🚨**
>
> The `buttons` array from the script is a **2D array** where each inner array = one row.
> **ALWAYS pass it directly to the message tool without modification.**
>
> - In **OpenClaw context**: use `response['buttons']` directly
> - In **Python scripts**: use `payload['buttons']` from `build_message_payload()`
>
> ❌ **NEVER** flatten, restructure, re-group, or stringify rows.

## Zero-Footgun Protocol

When sending any browser menu, follow the correct workflow for your context:

**If in OpenClaw (using exec + message tools):**
1. Run `browser_dispatcher.py` via exec tool
2. Use `response['messageToolCall']` as the complete payload for the `message` tool
3. **Don't touch the buttons** — use them exactly as returned inside that payload
4. If send succeeds and the response includes `postSend`, then update `liveMessageId` and optionally delete the previous menu

**If in standalone Python script:**
1. Generate plan via `run_browser_action.py` or import functions
2. Run `build_message_payload(plan)` and require `ok: true`
3. Use `payload['message']` and `payload['buttons']` from the validated result

**Common mistakes to avoid:**
- ❌ Don't rewrite buttons manually
- ❌ Don't flatten buttons into one row
- ❌ Don't pass buttons as a JSON string

# Telegram File Browser

Build Telegram file-browsing flows around a single live menu plus optional side messages for previews, paths, and downloads.

## Invocation

When the user explicitly invokes `telegram-file-browser` or asks to use this skill:

1. Open an interactive browser immediately in the same turn.
2. Default the root to `~/.openclaw/workspace` unless the user gave a path.
3. Do **not** reply with a conversational clarification like “你想让我做什么？” when the user already asked to browse.
4. Ask a follow-up only when the target path or safety boundary is genuinely ambiguous.
5. If the input is `config`, open the configuration flow instead of the browser tree.

Do not stop at describing the skill when you already have enough information to launch the UI.

## Runtime Contexts

This skill can be used in two different contexts. Choose the one that matches your environment.

### Context 1: OpenClaw Tool Calls (Most Common)

When you're running inside OpenClaw and using `exec` + `message` tools (like right now), use `browser_dispatcher.py` via `exec`, then call the `message` tool with the exact JSON from the script.

> ⚠️ **The script already validates and returns the correct payload — use it directly, don't rewrite anything.**

**Step 1: Run the script via exec tool**

```python
# Run the dispatcher to get the final message-tool payload
result = exec(command="python3 ~/.openclaw/workspace/skills/telegram-file-browser/scripts/browser_dispatcher.py open-root")
response = json.loads(result)  # response contains messageToolCall, postSend, and compatibility fields
```

**Step 2: Call message tool with the script's output**

```python
# ✅ CORRECT: pass the dispatcher payload through directly
message(**response['messageToolCall'])

# ❌ WRONG: don't rewrite buttons yourself
message(
    action='send',
    message=response['message'],
    buttons=[[{...}, {...}]]
)

# ❌ WRONG: don't stringify the payload either
message(action='send', message=response['message'], buttons=json.dumps(response['buttons']))
```

**Complete example:**

```python
# 1. Get the complete message-tool payload
result = exec(command="python3 ~/.openclaw/workspace/skills/telegram-file-browser/scripts/browser_dispatcher.py open-root")
response = json.loads(result.stdout)

if response['ok'] and response.get('messageToolCall'):
    # 2. Send exactly what the dispatcher returned
    msg_result = message(**response['messageToolCall'])

    # 3. Update liveMessageId if requested
    post_send = response.get('postSend') or {}
    if msg_result.get('messageId') and post_send.get('updateLiveMessageId'):
        exec(command="python3 ~/.openclaw/workspace/skills/telegram-file-browser/scripts/browser_dispatcher.py update-message-id " + str(msg_result['messageId']))

    # 4. Delete the previous live menu only after the new one succeeds
    previous_id = post_send.get('previousMessageId')
    if previous_id and post_send.get('cleanupPreviousMessage'):
        message(action='delete', messageId=previous_id)
```

**Callback handling:**

```python
# 1. Handle callback
result = exec(command="python3 ~/.openclaw/workspace/skills/telegram-file-browser/scripts/browser_dispatcher.py handle-callback " + callback_data)
response = json.loads(result.stdout)

# 2. Execute the exact tool payload returned by the script
if response.get('messageToolCall'):
    msg_result = message(**response['messageToolCall'])

    post_send = response.get('postSend') or {}
    if msg_result.get('messageId') and post_send.get('updateLiveMessageId'):
        exec(command="python3 ~/.openclaw/workspace/skills/telegram-file-browser/scripts/browser_dispatcher.py update-message-id " + str(msg_result['messageId']))

    previous_id = post_send.get('previousMessageId')
    if previous_id and post_send.get('cleanupPreviousMessage'):
        message(action='delete', messageId=previous_id)
```

**Important for current Telegram/OpenClaw routing:**

If a button click arrives as a plain inbound text message like `tfb_root_v12_w8` instead of a native callback event, **treat that text as the callback_data** and run the exact same callback flow above. Do not ignore it just because it came in as a message.

Recommended detection rule:

- if inbound text matches `^tfb_(root|dir|preview|path|download|back|close)_`
- treat it as a telegram-file-browser callback
- run `browser_dispatcher.py handle-callback <that_text>` immediately
- do not ask the user what they mean

---

### Context 2: Standalone Python Script

When you're writing a standalone Python script (not inside OpenClaw), use the import-based approach with `build_message_payload`.

```python
import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/telegram-file-browser/scripts')
from run_browser_action import open_root, handle_callback
from send_plan import build_message_payload

STATE = '~/.openclaw/workspace/.openclaw/telegram-file-browser/state.json'
ROOT = '~/.openclaw/workspace'


def send_browser_plan(plan):
    """Send message using OpenClaw's message tool or Telegram API."""
    if plan['toolAction'] == 'noop':
        return None
    if plan['toolAction'] == 'delete':
        return {"action": "delete", "messageId": plan['messageId']}
    if plan['toolAction'] == 'send-file':
        return {"action": "send", "path": plan['path'], "caption": plan.get('caption')}

    # MUST validate through build_message_payload
    wrapped = build_message_payload(plan)
    if not wrapped['ok']:
        raise RuntimeError(wrapped['error'])
    
    payload = wrapped['payload']
    return {
        "action": payload['action'],
        "message": payload['message'],
        "buttons": payload['buttons'],
        "replyTo": payload.get('replyTo')
    }


# First open
send_browser_plan(open_root(STATE, ROOT))

# Handle callback
send_browser_plan(handle_callback(STATE, callback_data))
```

**Why `build_message_payload` is required in Python scripts:**
- Validates button structure (2D array, one row per item)
- Returns the exact payload to send
- Prevents common mistakes like flattening buttons

**Why it's NOT needed in OpenClaw context:**
- `browser_dispatcher.py` already returns a validated payload
- Just use the JSON values directly

> ⚠️ **For OpenClaw tool calls: Just use `browser_dispatcher.py` — see Context 1 above.**
> 
> The examples below are for standalone Python scripts only.

## Tool Plan Contract

In **OpenClaw context** (most common): Use `browser_dispatcher.py` — it already validates and returns the correct payload. Just use the JSON values directly.

In **standalone Python scripts**: Use `run_browser_action.py` + `build_message_payload(plan)` as the guardrail.

Supported `toolAction` values:

Plans that send buttons should also include `viewType` (for example `directory` or `file-actions`) so the validator can enforce row-shape rules.

- `send`
- `delete`
- `send-file`
- `noop`

Map them to OpenClaw message actions like this:

- `send`
  - **In OpenClaw context**: Use `browser_dispatcher.py` — the response already contains validated `message` and `buttons`. Just pass them to the message tool:
    ```python
    message(action='send', message=response['message'], buttons=response['buttons'])
    ```
  - **In Python scripts**: Run `build_message_payload(plan)` first, then use:
    ```python
    payload = wrapped["payload"]
    message(action=payload["action"], message=payload["message"], buttons=payload["buttons"])
    ```
  - Pass `buttons` as a real 2D array (each inner array = one row)
  - Do **not** stringify or flatten buttons

⚠️ **Common mistakes to avoid:**
```python
# ❌ WRONG — flatten all buttons into one row
buttons = [[{...item1...}, {...item2...}, {...item3...}]]

# ❌ WRONG — stringify buttons  
buttons = json.dumps(response['buttons'])

# ✅ CORRECT — use script output directly
buttons = response['buttons']
```

- `delete`
  - use `message action=delete`
  - pass `messageId`

- `send-file`
  - use `message action=send`
  - pass `path` or `filePath`
  - pass `caption`
  - if `replyTo` is present, pass it as `replyTo`

- `noop`
  - do not send any user-visible message unless debugging is explicitly needed

Important runtime note:

- With the current OpenClaw message tool, Telegram inline buttons are reliably attached on `send`, not on `edit`.
- Therefore navigation should be implemented as **send a fresh menu**, then optionally delete the previous one.
- Treat `edit-message` mode as **replace the prior menu with minimal chat noise**, not as a literal button-preserving in-place edit.

## Display Modes

Persist display mode in `config.json`.

### `edit-message`

- keep one logical live browser menu
- because current OpenClaw tooling does not reliably preserve Telegram buttons on `edit`, implement this as:
  1. send a fresh menu
  2. update `liveMessageId`
  3. delete the previous menu after send succeeds
- best for low-noise chat history

### `new-message`

- navigation sends a fresh browser menu
- old menus remain in history unless you intentionally delete them
- update `liveMessageId` to the newly sent menu after success
- previews, path replies, and downloads still reply to the current live menu

## Core Interaction Rules

### Keep callback payloads short

Never place full file paths in `callback_data`.

Use opaque ids and store the real mapping in state.

### Split navigation from content

Use the menu for navigation only.

Use separate messages for:

- file previews
- copyable path output
- file downloads
- error notices that should not replace the current menu

### File click behavior

When a user clicks a file from a directory listing:

1. Open a file action menu.
2. Do not immediately dump file contents.
3. Offer at least `👁 预览`, `📋 路径`, `⬇️ 下载`, `⬅️ 返回`, `❌ 关闭`.
4. Prefer one button per row here as well unless a later UX change explicitly says otherwise.

### Pagination

Keep pagination inside the same state machine.

Required behavior:

- page buttons stay versioned like other callbacks
- page changes rebuild the current directory view
- pagination preserves root boundary and current path
- item ids remain resolvable after changing pages

## State Requirements

Persist at least:

- `root`
- `current`
- `stack`
- `liveMessageId`
- `menuVersion`
- `views`
- the current view's page metadata

Recommended shape:

```json
{
  "root": "/abs/root",
  "current": "/abs/root/subdir",
  "stack": ["/abs/root"],
  "liveMessageId": "2317",
  "menuVersion": 4,
  "views": {
    "/abs/root/subdir": {
      "path": "/abs/root/subdir",
      "page": 2,
      "pageSize": 12,
      "items": [
        { "id": "d12313", "name": "demo.py", "path": "/abs/root/subdir/demo.py", "type": "file" }
      ]
    }
  }
}
```

## Callback Safety

Protect against replayed and stale callbacks.

Required behavior:

- include menu version in interactive callbacks
- reject callbacks whose version does not match current state
- debounce duplicate callbacks received in a short window
- prefer silent `noop` over noisy execution for stale callbacks

## Failure Handling

### Missing or stale target

If the resolved file or directory no longer exists:

- keep the browser alive
- send a short failure message or rebuild the nearest valid view
- preserve a way back

### Callback execution loop

When Telegram delivers a button click as a callback message such as `callback_data: tfb_root_v2_w13`, do this immediately:

1. run `scripts/run_browser_action.py handle-callback <state_path> <callback>`
2. inspect the returned tool plan
3. if `toolAction == "send"`, run it through `send_plan.py` / `build_message_payload(plan)` first
4. execute the validated payload with the OpenClaw `message` tool
5. if a fresh menu was sent successfully, write the returned `messageId` back into state as `liveMessageId`
6. if the plan requests previous-menu cleanup, delete the previous menu only after the new menu send succeeds

Do not answer a callback message with a normal conversational reply when the callback belongs to the file browser.
Do not ask a follow-up unless the callback cannot be resolved safely.
Prefer silent `noop` over chatty recovery for stale callbacks.

### Message edit failure

If an edit fails because the menu no longer exists or cannot be edited:

- send a fresh menu
- update `liveMessageId`
- preserve current path and stack when possible

### Oversized or invalid callbacks

If Telegram rejects callback payloads:

- shorten callback ids
- move real state into local storage
- do not encode raw paths in buttons

## Bundled Scripts

- `scripts/build_view.py` — list a directory, sort entries, paginate, and emit view JSON
- `scripts/file_browser_state.py` — initialize/load/save state and manage current path, back stack, menu version, and live message id
- `scripts/preview_file.py` — generate safe file previews
- `scripts/render_buttons.py` — build Telegram button matrices for directory and file-action views
- `scripts/resolve_callback.py` — resolve callback payloads into browser actions
- `scripts/browser_controller.py` — orchestrate open-root, open-dir, file actions, back, paging, and live-message state updates
- `scripts/browser_config.py` — load and persist display config
- `scripts/run_browser_action.py` — convert browser actions into concrete tool plans for messaging and file delivery
- `scripts/send_plan.py` — validate send plans and build the only approved `message(action="send", ...)` payload
- `scripts/validate_buttons.py` — CLI validator for plan JSON before sending
- `scripts/test_buttons_integrity.py` — regression test for root/page/dir/file-action flows and flattened-button rejection
- **`scripts/browser_dispatcher.py`** — ⭐ **RECOMMENDED** one-click wrapper: generates plan, validates, returns exact payload. Use this instead of hand-rolling the flow.

## Runtime artifacts

Treat `state/` as runtime-only scratch data. Do not commit it. Keep it ignored in git.

## Pre-send Checklist

Before sending or replacing a browser menu, verify all of the following:

**In OpenClaw context (using exec + message tools):**
- ✅ You used `browser_dispatcher.py` to get the plan
- ✅ You passed `response['buttons']` directly to the message tool — **no manual rewriting**
- ✅ `buttons` is a real 2D array (each inner array = one row)

**In standalone Python scripts:**
- ✅ You used `build_message_payload(plan)` to validate
- ✅ You used `payload['buttons']` from the validated result

**General rules (always):**
- ⚠️ **Never rewrite buttons yourself** — use the script's output directly
- ⚠️ **Never flatten buttons into one row** — keep 2D structure
- ✅ Each directory/file item stays on its own row
- ✅ Callback payloads are short opaque ids, not raw paths
- ✅ `replyTo` is forwarded when the tool plan includes it
- ✅ After a successful send, `liveMessageId` is updated
- ✅ When replacing a live menu, send first and delete old menu only after send succeeds

## Hard rule

Treat any manual rewrite of `plan["buttons"]` as a bug, not an optimization.

## Notes

Read `references/interaction-patterns.md` when you need concrete UX guidance for:

- single-message navigation
- file action menus
- pagination behavior
- copyable path behavior
- menu recovery after edit failures
