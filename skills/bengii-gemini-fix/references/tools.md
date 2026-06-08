# OpenClaw Tools Inventory Reference

Detailed per-tool documentation for all built-in OpenClaw agent tools. Manage with `tools.allow`, `tools.deny`, and `tools.profile` in config.

## Table of Contents

- [Tool Profiles](#tool-profiles)
- [Tool Groups](#tool-groups)
- [File System Tools](#file-system-tools)
- [Exec + Process](#exec--process)
- [Loop Detection](#loop-detection)
- [Web Tools](#web-tools)
- [Browser Tool](#browser-tool)
- [Canvas Tool](#canvas-tool)
- [Nodes Tool](#nodes-tool)
- [Image Tool](#image-tool)
- [Message Tool](#message-tool)
- [Cron Tool](#cron-tool)
- [Gateway Tool](#gateway-tool)
- [Session Tools](#session-tools)
- [Memory Tools](#memory-tools)
- [Plugins + Skills](#plugins--skills)
- [Common Parameters](#common-parameters)
- [Recommended Agent Flows](#recommended-agent-flows)
- [Safety](#safety)

## Tool Profiles

| Profile | Allowed |
|---|---|
| `minimal` | `session_status` only |
| `coding` | `group:fs`, `group:runtime`, `group:sessions`, `group:memory`, `image` |
| `messaging` | `group:messaging`, sessions tools |
| `full` | No restrictions (default) |

## Tool Groups

Use `group:*` shorthands in `tools.allow` / `tools.deny`:

| Group | Tools Included |
|---|---|
| `group:runtime` | exec, bash, process |
| `group:fs` | read, write, edit, apply_patch |
| `group:sessions` | sessions_list, sessions_history, sessions_send, sessions_spawn, session_status |
| `group:memory` | memory_search, memory_get |
| `group:web` | web_search, web_fetch |
| `group:ui` | browser, canvas |
| `group:automation` | cron, gateway |
| `group:messaging` | message |
| `group:nodes` | nodes |
| `group:openclaw` | All built-in OpenClaw tools (excludes provider plugins) |

Example:

```json5
{ tools: { allow: ["group:fs", "browser"] } }
```

### Provider-Specific Tool Policy

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```

## File System Tools

See also: [Exec Tool (detailed)](exec.md), [Exec Approvals](exec_approvals.md).

### read / write / edit

- `read`: Read file contents
- `write`: Write/create files
- `edit`: Edit existing files (find + replace)

Config:

```json5
{
  tools: {
    fs: {
      workspaceOnly: true,    // Restrict to workspace directory
    },
  },
}
```

### apply_patch

Unified diff-based file patching.

Config:

```json5
{
  tools: {
    exec: {
      applyPatch: {
        enabled: true,            // Default: true
        workspaceOnly: false,     // Default: false
      },
    },
  },
}
```

## Exec + Process

### exec

Execute shell commands.

Parameters:
- `command` (required)
- `yieldMs` — auto-background after timeout (default 10000)
- `background` — immediate background
- `timeout` — seconds; kills process if exceeded (default 1800)
- `elevated` — run on host if elevated mode is enabled (only matters when sandboxed)
- `host` — `sandbox | gateway | node`
- `security` — `deny | allowlist | full`
- `ask` — `off | on-miss | always`
- `node` — node id/name for `host=node`
- `pty: true` — for commands needing a real TTY

Return behavior:
- Returns `status: "running"` + `sessionId` when backgrounded
- Use `process` to poll/log/write/kill/clear background sessions
- If `process` is disallowed, exec runs synchronously

**elevated mode**: alias for `host=gateway + security=full`. Gated by both `tools.elevated` AND any `agents.list[].tools.elevated` override. Only differs when agent is sandboxed.

**host=node**: targets macOS companion app or headless node host.

### process

Manage background exec sessions.

Actions: `list`, `poll`, `log`, `write`, `kill`, `clear`, `remove`

- `poll` returns new output and exit status when complete
- `log` supports line-based `offset`/`limit` (omit `offset` for last N lines)
- Scoped per agent; sessions from other agents not visible

## Loop Detection

Prevents tool-call loops. Enabled by default.

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      historySize: 30,
      detectors: {
        genericRepeat: true,          // Same tool + same params
        knownPollNoProgress: true,    // Repeated poll with identical outputs
        pingPong: true,               // Alternating A/B/A/B patterns
      },
    },
  },
}
```

Per-agent override: `agents.list[].tools.loopDetection`

## Web Tools

See also: [Web Tools (detailed)](web_tools.md) for provider setup (Brave, Perplexity, Gemini).

### web_search

Web search via Brave Search API.

Config:

```json5
{
  tools: {
    web: {
      search: {
        apiKey: "${BRAVE_API_KEY}",
      },
    },
  },
}
```

### web_fetch

Fetch web page content.

## Browser Tool

See also: [Browser (detailed)](browser.md) for profiles, remote CDP, extension relay, SSRF policy, and Control API.

Full browser automation via CDP (Chrome DevTools Protocol).

Recommended flow:
1. `browser` → `status` / `start`
2. `snapshot` (AI or ARIA modes)
3. `act` (click/type/press)
4. `screenshot` for visual confirmation

Parameters:
- `profile` — optional; defaults to `browser.defaultProfile`
- `target` — `sandbox | host | node`
- `node` — optional; pin a specific node id/name

Config:

```json5
{
  browser: {
    executablePath: "/usr/bin/google-chrome",
    // CDP config...
  },
}
```

CLI:

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
```

## Canvas Tool

Control canvas surfaces on nodes.

Actions: `present`, `hide`, `navigate`, `eval`, `snapshot`, `a2ui_push`, `a2ui_reset`

Recommended flow:
1. `canvas` → `present`
2. `a2ui_push` (optional)
3. `snapshot`

- Uses `node.invoke` under the hood
- If no node specified, picks default (single connected node or local mac node)
- A2UI is v0.8 only (no `createSurface`)

## Nodes Tool

Control connected peripheral devices.

Actions:
- **Status**: `status`, `describe`
- **Pairing**: `pending`, `approve`, `reject`
- **System**: `notify` (macOS `system.notify`), `run` (macOS `system.run`)
- **Camera**: `camera_list`, `camera_snap`, `camera_clip`, `screen_record`
- **Location**: `location_get`
- **Device**: `device_status`, `device_info`, `device_permissions`, `device_health`
- **Notifications**: `notifications_list`, `notifications_action`

Recommended flow:
1. `nodes` → `status`
2. `describe` on the chosen node
3. `notify` / `run` / `camera_snap` / `screen_record`

See [references/nodes.md](nodes.md) for detailed node documentation.

## Image Tool

Generate images using configured image model.

Parameters:
- `image` (required path or URL)
- `prompt` (optional; defaults to "Describe the image.")
- `model` (optional override)
- `maxBytesMb` (optional size cap)

Requires `agents.defaults.imageModel` to be configured.

## PDF Tool

Analyze PDF documents using configured model.

Parameters:
- `pdf` (single path or URL)
- `pdfs` (multiple paths or URLs, up to 10)
- `prompt` (optional; defaults to "Analyze this PDF document.")
- `pages` (optional page range like `1-5` or `1,3,7-9`)
- `model` (optional override)
- `maxBytesMb` (optional size cap)

Notes:
- Native PDF mode supported for Anthropic and Google models
- Non-native models use extraction fallback (text → rasterized page images)
- `pages` filtering only works in extraction fallback mode
- Defaults: `agents.defaults.pdfModel`, `agents.defaults.pdfMaxBytesMb`, `agents.defaults.pdfMaxPages`

## Message Tool

Send messages and perform channel-specific actions.

Actions:
- **Core**: `send` (text + optional media), `edit`, `delete`, `read`
- **Reactions**: `react`, `reactions`
- **Polls**: `poll` (WhatsApp/Discord/MS Teams)
- **Pins**: `pin`, `unpin`, `list-pins`
- **Threads**: `thread-create`, `thread-list`, `thread-reply`
- **Search**: `search`
- **Stickers**: `sticker`, `sticker-upload`
- **Emoji**: `emoji-list`, `emoji-upload`
- **Roles**: `role-add`, `role-remove`, `role-info`
- **Channels**: `channel-info`, `channel-list`
- **Members**: `member-info`
- **Moderation**: `timeout`, `kick`, `ban`
- **Events**: `event-list`, `event-create`
- **Voice**: `voice-status`
- **Cards**: `card` (MS Teams Adaptive Cards)
- **Permissions**: `permissions`

Notes:
- `send` routes WhatsApp via Gateway; other channels go direct
- `poll` uses Gateway for WhatsApp/MS Teams; Discord goes direct
- When bound to an active chat session, sends are constrained to that session's target (prevents cross-context leaks)

## Cron Tool

Manage scheduled jobs.

Actions: `status`, `list`, `add`, `update`, `remove`, `run`, `runs`, `wake`

- `add` expects a full cron job object (same schema as `cron.add` RPC)
- `update` uses `{ jobId, patch }`
- `wake` enqueues system event + optional immediate heartbeat

Config:

```json5
{
  cron: {
    jobs: [
      {
        schedule: "0 9 * * *",
        message: "Good morning!",
        channel: "whatsapp",
      },
    ],
    webhookToken: "your-webhook-token",  // For webhook delivery
  },
}
```

Delivery modes:
- **announce**: Summary to channel/target
- **webhook**: `delivery.mode = "webhook"` with `delivery.to` as HTTP(S) URL
- **none**: Internal-only runs

Advanced options: delete-after-run, agent model/thinking overrides, cron stagger, best-effort delivery toggles.

## Gateway Tool

Remote gateway management from agent.

Actions:
- `restart` — in-process restart via `SIGUSR1`
- `config.get` / `config.schema`
- `config.apply` — validate + write config + restart + wake
- `config.patch` — merge partial update + restart + wake
- `update.run` — run package update + restart + wake

Notes:
- Use `delayMs` (default 2000) to avoid interrupting in-flight replies
- Disable restart with `commands.restart: false`

## Session Tools

### sessions_list / sessions_history / sessions_send / sessions_spawn / session_status

- **sessions_list**: `kinds?`, `limit?`, `activeMinutes?`, `messageLimit?` (0 = none)
- **sessions_history**: `sessionKey` (or `sessionId`), `limit?`, `includeTools?`
- **sessions_send**: `sessionKey` (or `sessionId`), `message`, `timeoutSeconds?` (0 = fire-and-forget)
- **sessions_spawn**: Create sub-agent or ACP session
  - `task`, `label?`, `runtime?` (`"subagent"` | `"acp"`), `agentId?`, `model?`, `thinking?`
  - `cwd?`, `runTimeoutSeconds?`, `thread?`, `mode?` (`"run"` | `"session"`), `cleanup?`, `sandbox?`
  - `attachments?` (inline files, subagent only), `attachAs?`
  - Supports one-shot mode (`mode: "run"`) and persistent thread-bound mode (`mode: "session"` with `thread: true`)
  - Non-blocking: returns `status: "accepted"` immediately
  - Attachments: materialized at `.openclaw/attachments/<uuid>/` with `.manifest.json`
  - Configure limits: `tools.sessions_spawn.attachments` (enabled, maxTotalBytes, maxFiles, maxFileBytes)
- **session_status**: `sessionKey?` (default current), `model?`

Notes:
- `main` is the canonical direct-chat key; `global`/`unknown` are hidden
- `messageLimit > 0` fetches last N messages per session
- Session visibility: `tools.sessions.visibility` (default `tree`: current + spawned sessions)
- For shared agents: set `tools.sessions.visibility: "self"` to prevent cross-session browsing
- `sessions_send` supports ping-pong (reply `REPLY_SKIP` to stop; max via `session.agentToAgent.maxPingPongTurns`)
- Sandbox clamp: when sandboxed, `sessionToolsVisibility` clamps to `tree`

### agents_list

List configured agents for `sessions_spawn`.

- Result restricted to per-agent allowlists (`agents.list[].subagents.allowAgents`)
- When `["*"]` configured, includes all agents with `allowAny: true`

## Memory Tools

- **memory_search**: Search agent memory store
- **memory_get**: Retrieve specific memory entry

## Plugins + Skills

See also: [Plugins (detailed)](plugins.md), [Skills (detailed)](skills.md).

- **Plugins**: Extended tools from plugin packages
  - Install: `openclaw plugins install <name>`
  - CLI: `openclaw plugins list|info|enable|disable|doctor`
  - Official plugins: Memory, Voice Call, Zalo, Matrix, Nostr, MS Teams, Google Auth, Gemini CLI, Qwen, Copilot Proxy

- **Skills**: Per-agent skills in `agentDir/skills/` or shared from `~/.openclaw/skills`
  - CLI: managed via Control UI (Skills panel)
  - Marketplace: [ClawHub](https://clawhub.com)

- **Lobster**: Typed workflow runtime with resumable approvals (requires Lobster CLI). See [Lobster (detailed)](lobster.md).
- **LLM Task**: JSON-only LLM step for structured workflow output. See [LLM Task (detailed)](llm_task.md).
- **OpenProse**: Multi-agent program runtime with parallelism and approvals. See [OpenProse (detailed)](openprose.md).
- **Diffs**: Read-only diff viewer and PNG renderer. See [Diffs & Firecrawl (detailed)](diffs_firecrawl.md).

## Common Parameters

For `canvas`, `nodes`, `cron` tools:
- `gatewayUrl` — default `ws://127.0.0.1:18789`
- `gatewayToken` — if auth enabled
- `timeoutMs`

## Recommended Agent Flows

### Browser Automation
1. `browser` → `status` / `start`
2. `snapshot` (AI or ARIA)
3. `act` (click/type/press)
4. `screenshot` for visual confirmation

### Canvas Interaction
1. `canvas` → `present`
2. `a2ui_push` (optional)
3. `snapshot`

### Node Operations
1. `nodes` → `status`
2. `describe` on chosen node
3. `notify` / `run` / `camera_snap` / `screen_record`

## Safety

- Avoid direct `system.run`; use `nodes` → `run` only with explicit user consent
- Respect user consent for camera/screen capture
- Use `status`/`describe` to ensure permissions before invoking media commands
- Tool schemas are presented to the model both as system prompt text and structured function definitions
