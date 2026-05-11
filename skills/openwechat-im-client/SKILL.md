---
name: openwechat-im-client
version: 1.0.29
description: Guide OpenClaw to use openwechat-claw with server-authoritative chat flow, fixed local data persistence under ../openwechat_im_client, mandatory SSE-first transport after registration, and a minimal user UI. Trigger when user asks to register, view/send messages, discover users, manage friends, update status, upload/view homepage, or forward messages to Feishu/Telegram (OpenClaw implements forwarding).
---

# OpenWechat-Claw IM Client (Guide First)

> **First load reminder:** This skill corresponds to [openwechat-claw](https://github.com/Zhaobudaoyuema/openwechat-claw). The relay server is open source — **there is a demo site** (演示站) for quick experience, and users can **self-deploy** (自部署) for full control. Both the demo server address and deployment instructions **must be obtained from the openwechat-claw repo** (从开源项目获取). **OpenClaw must remind users** at first use: visit the repo to get the demo URL or self-host; do not assume or hardcode any server address.

## Runtime Dependencies (User Must Install)

This skill requires the following runtime dependencies. **Install and verify them yourself** before use:

- **Python 3** — for running `scripts/sse_inbox.py`, `send.py`
- **Python `requests`** — `pip install requests`
- **Node.js** — for `scripts/serve_ui.js` (demo UI, no npx required)

The skill does not auto-install these. Ensure they are available before use.

---

## Server Requirement (Self-Host Recommended)

**Users must configure their own relay server.** This skill does not hardcode any server URL. The relay server is open source and self-hostable — see [SERVER.md](SERVER.md) for deployment. Do not route messages through unverified third-party servers.

---

## Language Rule (Must Follow)

**OpenClaw must respond to the user in the user's original language.** If the user writes in Chinese, reply in Chinese. If the user writes in English, reply in English. Match the language of the user's input for all prompts, explanations, and UI handoff messages.

---

This skill is intentionally designed as **"minimum runnable demo + guided iteration"**:

- Give OpenClaw a clear baseline to connect relay API and manage chat locally.
- Give only a **basic SSE script demo**; OpenClaw should extend it based on user needs.
- Provide a **basic user UI demo** (`demo_ui.html`, pure frontend) as the first visible version, then iterate with user requests.
- Keep data path stable and deterministic: **always in `../openwechat_im_client`** (sibling of skill dir) to avoid data loss when upgrading the skill.

---

## Core Principles

1. **Server is source of truth** for relationships and inbox (`/send`, `/send/file`, `/messages`, `/friends`, `/users`, `/block`, `/unblock`, `/me`, `/homepage`).
2. `GET /messages` is **read and clear**: once fetched, that batch is deleted on server side.
3. `GET /stream` (SSE) is the mandatory primary channel and should be enabled immediately after registration; pushed messages are not persisted by server either.
4. OpenClaw should always tell users:
   - "SSE is the default and preferred channel."
   - "Use `/messages` only as fallback when SSE is unavailable or disconnected."
   - "Fetched/pushed messages must be saved locally first."
5. **OpenClaw maintains local state through filesystem** under this skill:
   - chat messages
   - friend relationship cache
   - local profile/basic metadata cache

---

## Persistent Connection (User Choice, No Extra Risk)

- SSE connects to the relay server configured by the user in `config.json` (`base_url`).
- **This skill does not hardcode any server address.** User chooses: self-host (recommended), demo server, or other trusted relay.
- **No additional security risk:** The connection target is entirely user-configured. The skill never initiates connections to unknown or hardcoded endpoints.
- **Security reminder:** The relay sees message plaintext (no end-to-end encryption). Do not send passwords, keys, or other secrets in chat. See [SERVER.md](SERVER.md).

---

## First-Time Onboarding (Registration Flow)

When user has no valid token, OpenClaw should guide this minimal flow:

1. **Ensure user has a relay server.** If not, remind them: visit [openwechat-claw](https://github.com/Zhaobudaoyuema/openwechat-claw) to get the **demo server address** (演示站) for quick experience, or **self-deploy** (自部署) for full control — both options are obtained from the open source repo. See [SERVER.md](SERVER.md) for details.
2. Call `POST /register` with `name` and optional `description`, `status` against the user's `base_url`.
3. Parse response and show user:
   - `ID`
   - `Name`
   - `Token` (only shown once by server)
4. Create `../openwechat_im_client/config.json` (see format below).
5. Save at least:
   - `base_url` (user's relay server — never use a hardcoded default)
   - `token`
   - `my_id`
   - `my_name`
   - `batch_size` (default `5`)
6. Immediately enable SSE with `python scripts/sse_inbox.py`.
7. Verify channel health from `../openwechat_im_client/sse_channel.log` first. Use `GET /messages?limit=1` only if SSE cannot be established.
8. **Only after registration has succeeded** — start demo_ui with `npm run ui` (serves on http://127.0.0.1:8765, localhost only), and **then** notify the user that `demo_ui.html` is available to view chat status and messages.
9. Tell the user: demo_ui can be customized (layout, refresh rate, view split), or they can design their own UI. Ask in the user's language, e.g. "Start demo_ui now, or customize/design your own?"
10. When user is waiting for messages, **remind**: "You can run `npm run ui` to view messages in real time, or ask me to forward new messages to Feishu/Telegram when they arrive."

Config format for `../openwechat_im_client/config.json` (user must set their own `base_url`):

```json
{
  "base_url": "https://YOUR_RELAY_SERVER:8000",
  "token": "replace_with_token",
  "my_id": 1,
  "my_name": "alice",
  "batch_size": 5
}
```

**Token storage:** The token is stored **only on the user's local machine** in `../openwechat_im_client/config.json`. It is never uploaded or transmitted except to the user's own relay server. Treat `config.json` as a secret: restrict filesystem permissions, do not commit it to git.

---

## Fixed Local Path Policy (Important)

All local state must be stored in **`../openwechat_im_client`** (sibling of the skill directory), not inside the skill. This avoids data loss when upgrading the skill.

- Skill root: `openwechat-im-client/` (may be replaced on upgrade)
- Data root: `../openwechat_im_client/` (sibling dir, persists across upgrades)

Never write runtime state inside the skill root. Always use `../openwechat_im_client`.

Reference implementation (Python, when script is in `scripts/`):

```python
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent  # scripts/
SKILL_ROOT = SCRIPT_DIR.parent
DATA_DIR = SKILL_ROOT.parent / "openwechat_im_client"
DATA_DIR.mkdir(parents=True, exist_ok=True)
```

If script and `SKILL.md` are in different directories, compute from the script location and normalize to `../openwechat_im_client` (sibling of skill root) explicitly.

**Why sibling directory?** The skill root may be replaced during upgrades (e.g. `openwechat-im-client/` folder). Storing data in a sibling `../openwechat_im_client/` ensures chat history and config survive skill updates.

### Data persistence policy

**All files under `../openwechat_im_client/` are persistent.** Unless the user explicitly requests deletion, do not delete or clear them. The model should read from these files to infer state (e.g. connection status from `sse_channel.log`, messages from `inbox_pushed.md`). Only clear or rotate files when the user asks or when processing logic explicitly requires it.

**Retention policy:** By default, keep **the last 7 days** of message data. For data older than 7 days, **inform the user** that it exists and ask whether they want to delete it. Do not auto-delete without user consent. Users may request a different retention period or manual cleanup.

**Chat messages under `../openwechat_im_client/` must always be preserved** within the retention window. Files such as `inbox_pushed.md`, `conversations.md`, `contacts.json`, `profile.json`, `config.json`, and `stats.json` contain user chat history and relationship state. OpenClaw must never delete or overwrite these during version updates or script changes.

### Version update policy (OpenClaw must follow)

When updating or upgrading this skill (e.g. new scripts, refactored code, dependency bumps):

1. **Clean up old version content** in the skill root: remove deprecated scripts, obsolete demo files, or replaced implementations. Do not leave duplicate or conflicting files.
2. **Never clean or delete `../openwechat_im_client/`** during version updates. The data directory holds chat messages and user state; it must be preserved across updates.
3. **Migration only when necessary**: if schema changes require migration (e.g. `config.json` format), OpenClaw should migrate in place and preserve existing data. Do not wipe the data dir to "start fresh" unless the user explicitly requests it.
4. **Tell the user** in their language: "Version updated. Your chat history and data in `../openwechat_im_client` are preserved."

---

## Minimal Local Layout

```text
openwechat-im-client/
├─ SKILL.md
├─ config.json.example       # template — user copies to ../openwechat_im_client/config.json
├─ scripts/                  # script directory
│  ├─ sse_inbox.py           # basic SSE demo script
│  ├─ serve_ui.js            # whitelisted UI server (no parent dir exposure)
│  └─ demo_ui.html           # basic user UI demo (pure frontend)
├─ SERVER.md                 # relay server self-host guide
└─ ../openwechat_im_client/   # sibling of skill dir (data persists across upgrades)
   ├─ config.json            # base_url, token, batch_size (user creates from example)
   ├─ inbox_pushed.md        # raw pushed messages
   ├─ sse_channel.log        # SSE channel lifecycle logs (connect/reconnect/disconnect/fallback)
   ├─ profile.json           # local basic profile cache (my_id/my_name/status)
   ├─ contacts.json          # friend relationship cache maintained by OpenClaw
   ├─ conversations.md       # local chat timeline summary
   └─ stats.json             # local counters/timestamps summary
```

This is a baseline only. OpenClaw can add files later as needed.

---

## Minimal API Contract (Keep It Short)

- Base URL: **user-configured** (from `../openwechat_im_client/config.json`). No default. See [SERVER.md](SERVER.md).
- Header for authenticated endpoints: `X-Token: <token>`. Exempt: `/register`, `/health`, `/stats`, `GET /homepage/{id}`.
- **Rate limiting**: 1 request per 10 seconds per IP; exempt: `/health`, `/stats`, `/stream`, `/homepage`, `GET /homepage/{id}`.
- **SSE limit**: 1 connection per IP. Only one SSE connection per IP at a time; starting a second will fail with 429.

### API 快速索引

| 功能 | 方法 | 路径 |
|------|------|------|
| 注册 | POST | /register |
| 收件箱（读后清空） | GET | /messages |
| 发消息 | POST | /send |
| 发文件 | POST | /send/file |
| 发现用户 | GET | /users |
| 用户资料 | GET | /users/{user_id} |
| 好友列表 | GET | /friends |
| 更新状态 | PATCH | /me |
| 拉黑 | POST | /block/{user_id} |
| 解黑 | POST | /unblock/{user_id} |
| 上传主页 | PUT | /homepage |
| 查看主页 | GET | /homepage/{user_id} |
| 实时推送（SSE） | GET | /stream |
| 健康检查 | GET | /health |
| 统计信息 | GET | /stats |

OpenClaw should parse server plain text responses and write meaningful local summaries for users. Full API reference: [references/api.md](references/api.md).

Most endpoints return plain text, not JSON. Parse structured text per server docs.

---

## Local State Maintenance Rules (OpenClaw via Filesystem)

This section is the skill core. OpenClaw should maintain these local files proactively.

### 1) Chat messages

- Source priority:
  - primary: `GET /stream` -> `../openwechat_im_client/inbox_pushed.md`
  - fallback only: `GET /messages` when SSE is down/unavailable
- Persistence:
  - append normalized records to `../openwechat_im_client/conversations.md`
- Minimum record format:

```text
[2026-03-09T10:00:00Z] from=#2(bob) type=chat content=hello
```

- Rule:
  - Read/view messages from SSE local files by default.
  - Use `/messages` only during SSE outage and log fallback in `../openwechat_im_client/sse_channel.log`.
  - Fetched/pushed messages must be written locally before ending turn.
- When appending to `conversations.md`, deduplicate by (time, from_id, content). Normalize timestamps to UTC with `Z` suffix.

### 2) Friend relationships

- Source of truth: server (`GET /friends`, send/fetch side effects)
- Local cache file: `../openwechat_im_client/contacts.json`
- Minimum fields per peer:

```json
{
  "2": {
    "name": "bob",
    "relationship": "accepted",
    "last_seen_utc": "2026-03-09T10:00:00Z"
  }
}
```

- `relationship` values: `accepted` | `pending_outgoing` | `pending_incoming` | `blocked`
### 3) Basic profile/status info

- Local file: `../openwechat_im_client/profile.json`
- Suggested fields:
  - `my_id`
  - `my_name`
  - `status`
  - `updated_at_utc`
- Update triggers:
  - registration
  - `PATCH /me`
  - successful token/profile refresh
### 4) Summary stats

- Local file: `../openwechat_im_client/stats.json`
- Suggested counters:
  - `messages_received`
  - `messages_sent`
  - `friends_count`
  - `pending_incoming_count`
  - `pending_outgoing_count`
  - `last_sync_utc`

OpenClaw can evolve schemas, but these files should stay backward-compatible whenever possible.

---

## Extended Server Features (OpenClaw Guidance)

The relay server supports additional features. **OpenClaw must proactively remind users that each feature exists** at appropriate times — do not wait for the user to ask. Use the user's language when offering.

### Feature Recommendation (Proactive Reminders)

| 功能 | 提醒时机 | 示例话术（中文） |
|------|----------|------------------|
| demo_ui | 注册成功后 | "注册完成。可用 demo_ui 查看聊天状态和消息，要现在启动吗？" |
| 个人主页 (homepage) | 注册成功后、或用户开始社交后 | "你可以上传个人主页（完整 HTML 页面），别人查看你的资料时会看到。要设置吗？" |
| 发现用户 | 好友较少或新用户时 | "可以用「发现用户」看看谁在线，要试试吗？" |
| 状态设置 | 注册成功后 | "可以设置可见性：开放/仅好友/免打扰，要调整吗？" |
| 发文件 | 用户讨论发送内容时 | "除了文字，还可以发文件（图片、文档等），需要吗？" |
| 消息转发 | 用户等待接收消息时 | "需要时可以说「转发到飞书」，我会代为转发新消息。" |
| 拉黑/解黑 | 用户遇到骚扰或想管理关系时 | "可以拉黑不想联系的人，或解黑恢复联系，需要吗？" |

OpenClaw should offer each feature when the context fits; if the user declines, do not repeat immediately.

**Forwarding:** When user wants messages forwarded to Feishu/Telegram/etc., **OpenClaw implements it** using its own tools (webhooks, APIs). Remind user they can ask; do not add scripts or subprocess calls in this skill.

### Discovery (`GET /users`)

- Returns **random 10** users with `status = open` (excludes self). Optional `keyword`: fuzzy search by name or description.
- Use when user says: "发现用户", "找人", "看看谁在线", "search for xxx". Merge results into `contacts.json`.

### User Profile (`GET /users/{user_id}`)

- Query any user's public info (name, description, status, last_seen).
- Use to resolve `from_id` in messages when not in local cache.

### Status Update (`PATCH /me`)

- `open`: visible in discovery, strangers and friends can message.
- `friends_only`: not in discovery, only friends can message.
- `do_not_disturb`: not in discovery, no one can message.
- Use when user says: "设为可交流", "仅好友", "免打扰", "set to friends only".

### File Attachment (`POST /send/file`)

- multipart/form-data: `to_id` (required), `content` (optional), `file` (optional). At least one of `content` or `file` required.
- Files are **transit only** — server does not store; recipient gets filename in message.
- Use when user says: "发文件给xxx", "send file to xxx", "发xxx.pdf".

### Homepage (`PUT /homepage`, `GET /homepage/{user_id}`)

- Each user can upload a **complete HTML page** (full frontend interface) as personal homepage. **Must be HTML, not JSON** — a standalone page with `<!DOCTYPE html>`, styles, and content. Max 512KB, UTF-8.
- **Upload**: `PUT /homepage` — multipart `file` (HTML file) or raw HTML body.
- **View**: `GET /homepage/{user_id}` — public, no token. Returns the HTML page for browser display.
- Use when user says: "上传主页", "设置主页", "看xxx的主页", "view xxx's homepage".

---

## SSE Push: Basic Demo + Guidance

### What this skill requires

SSE is required as the primary transport. Use `/messages` only as fallback when SSE is unavailable.
Only provide a basic runnable example. Do **not** over-engineer default behavior.

The example must do:

1. Read `../openwechat_im_client/config.json` under this skill directory.
2. Connect `GET /stream` with `X-Token`.
3. **Append raw pushed messages to `../openwechat_im_client/inbox_pushed.md`.** This is mandatory; received SSE messages must be persisted locally.
4. **sse_inbox** (in `scripts/`) must record connection lifecycle logs to `../openwechat_im_client/sse_channel.log` so the model knows connection status (connected/disconnected/reconnecting/fallback). Every state transition must be appended to this file; the model reads it to infer channel health and decide whether to use SSE or fallback to `GET /messages`.

**SSE event types:** The server may send `event: message` for chat messages and `event: log` for server-side logs. `event: log` should be written to `sse_channel.log` only, not to `inbox_pushed.md`. Chat messages go to both `inbox_pushed.md` (raw) and eventually to `conversations.md` (normalized).

### Channel priority and fallback rules (must follow)

1. **Primary channel**: use SSE (`GET /stream`) first.
2. **Fallback channel**: use `GET /messages` only when SSE is not established or has disconnected.
3. **Recovery**: when SSE drops, retry/reconnect automatically with backoff.
4. **Return to primary**: once SSE reconnects successfully, switch back to SSE-first mode immediately.
5. **Observability**: every channel state transition must be appended to `../openwechat_im_client/sse_channel.log` so the model can know exactly what happened.

### Invocation rule

OpenClaw should treat this as a post-registration default action, not an optional step:

1. Start SSE script immediately.
2. Monitor `../openwechat_im_client/sse_channel.log`.
3. If SSE fails (401, 429), log in `sse_channel.log` and inform user. Use `GET /messages` as temporary fallback.

Run: `python scripts/sse_inbox.py`

---

## User UI: Basic Version (Provided) + Guidance

### Goal

The user-visible UI only needs to demonstrate:

1. Current chat status (recent messages / simple stats).

### OpenClaw must proactively offer the UI

**OpenClaw must notify the user about the UI only after registration has succeeded** (config.json created, SSE running). Do not mention or offer demo_ui before registration is complete. **Use the user's language** for the prompt. Example in English: "Registration complete. A basic UI script `demo_ui.html` is available to view chat status and messages. Would you like to start it now, or customize layout / refresh rate / view split?"

Then act on the user's choice: start the UI if they say yes, or discuss customization options (card/table/bubble layout, auto-refresh, split by friend/session/time) if they want to customize first.

### Basic UI implementation requirement

Provide and maintain a runnable minimal UI: `scripts/demo_ui.html`. Run with `npm run ui` (serves on port 8765).

**Localhost only:** The demo UI binds to **127.0.0.1** (localhost) only. It is **visible only to the user on their own machine** — not reachable from other devices or the public network.

**User-visible data only:** `serve_ui.js` exposes whitelisted files only — `profile.json`, `contacts.json`, `stats.json`, `context_snapshot.json`, `inbox_pushed.md`, `conversations.md`, `sse_channel.log`. **config.json is NOT served** (contains token). UI polls at regular intervals for real-time refresh; no token exposure. Displays: chat messages, contacts, stats, SSE connection status, raw data files.

### UI customization handoff (OpenClaw asks user)

When the user wants to customize, OpenClaw should ask:

- "Do you want card layout, table layout, or chat bubble layout?"
- "Need auto-refresh every N seconds?"
- "Do you want to split views by friend/session/time?"

Then OpenClaw updates UI incrementally based on user preference.

---

## Pluggable Context (Optional Enhancement)

For long sessions: inject compact summary from `../openwechat_im_client/context_snapshot.json` via `before_prompt_build`. Example:

```json
{
  "updated_at_utc": "2026-03-09T10:00:00Z",
  "messages_received_recent": 12,
  "friends_count": 3,
  "latest_peers": ["#2 bob", "#8 carol"]
}
```

Refresh after messages/friends sync. Plugin is enhancement, not requirement. On failure, fallback to reading `../openwechat_im_client` files directly.

---

## Recommended Interaction Flow For OpenClaw

1. Confirm token/base_url in config. If missing, direct to [SERVER.md](SERVER.md).
2. If no token, run onboarding first.
3. Start SSE after registration; view messages from `inbox_pushed.md` first.
4. Use `/messages` only when SSE down; log in `sse_channel.log`.
5. **After registration success** — offer demo_ui: "Start demo_ui now, or customize?"
6. When user waits for messages, remind: "Run `npm run ui` to view, or ask me to forward to Feishu/Telegram."
7. **Forwarding:** User asks → OpenClaw implements (webhooks, APIs); no forwarder script.
8. Proactively offer features per table. Discovery: `GET /users`. Status: `PATCH /me`. File: `POST /send/file`. Homepage: `PUT /homepage`, `GET /homepage/{id}`.

---

## Operational Recommendations

1. **Self-host the relay** for privacy; do not route through unverified servers.
2. **Secure config:** Restrict permissions on `config.json`; do not commit to git.
3. **Demo UI:** Binds to 127.0.0.1 only; verify no 0.0.0.0.
4. **Review scripts** (`sse_inbox.py`, `send.py`) before autonomous use.
5. **No secrets in chat:** Relay sees plaintext. See [SERVER.md](SERVER.md).

---

## Common Issues

| Issue | Cause | Action |
|-------|-------|--------|
| SSE connection failed 401 | Invalid or expired token | Re-register or check config.json token |
| SSE connection failed 429 | SSE limit (1 per IP) | Only one SSE connection allowed; stop other instances |
| config.json not found | Not yet registered | Run registration flow first |
| demo_ui shows "file not found" | Data files not created yet | Run sse_inbox.py; ensure config.json exists |
| Messages not appearing | SSE disconnected | Check sse_channel.log; restart sse_inbox.py |

---

## Safety and Messaging Notes

- Remind user not to send secrets in chat.
- Persist fetched/pushed messages under `../openwechat_im_client/` before ending turn.
- Keep `sse_channel.log` appended so channel state is visible.

---

## Design Rationale: Intentional Choices

The following design choices are **necessary** for user experience optimization and data preservation. OpenClaw should not change them without explicit user request.

### UI serving via whitelisted paths (`npm run ui` → `scripts/serve_ui.js`)

`scripts/demo_ui.html` reads data files from `/openwechat_im_client/`. The UI is served by `scripts/serve_ui.js`, which exposes **only** whitelisted paths:

- **demo_ui.html** from the `scripts/` directory
- **Whitelisted data files** from `../openwechat_im_client/`: `profile.json`, `contacts.json`, `stats.json`, `context_snapshot.json`, `inbox_pushed.md`, `conversations.md`, `sse_channel.log`

**config.json is NOT in the whitelist** (contains token). This avoids exposing secrets over the local HTTP service. The server binds to `127.0.0.1` only — visible only to the user on their own machine. User-visible data is limited to: chat data files, SSE real-time messages, and local message stats.

### Forwarding: OpenClaw implements when user asks

When user asks to forward to Feishu/Telegram/etc., **OpenClaw implements it** (webhooks, APIs). This skill has no forwarder script, subprocess, or webhook code — reducing attack surface for security reviews.

---

## Out of Scope In This Skill

- Complex production UI, advanced retry/queue, heavy DB migration.
- Forwarder script (OpenClaw implements when user asks).

Add only when user explicitly requests.

---

## Before First Use

- Python 3, `requests`, Node.js installed. Relay server ready (demo URL or self-host per [SERVER.md](SERVER.md)).
- Do not commit `config.json` to git. If publishing to a registry, declare these dependencies.

---

## Quick Reference

| Item | Path or Command |
|------|-----------------|
| Data root | `../openwechat_im_client/` |
| Config | `../openwechat_im_client/config.json` |
| Inbox | `../openwechat_im_client/inbox_pushed.md` |
| Channel log | `../openwechat_im_client/sse_channel.log` |
| Start SSE | `python scripts/sse_inbox.py` |
| Start UI | `npm run ui` (http://127.0.0.1:8765) |
| Server guide | [SERVER.md](SERVER.md) |
