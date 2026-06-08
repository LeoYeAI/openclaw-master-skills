# OpenClaw Nodes Reference

Nodes are peripheral devices (iOS, Android, macOS, headless Linux/Windows) that connect to the Gateway via WebSocket. They expose device capabilities (camera, screen, location, exec) to the AI agent.

## Table of Contents

- [Overview](#overview)
- [Pairing + Status](#pairing--status)
- [Remote Node Host (system.run)](#remote-node-host-systemrun)
- [Canvas (Screenshots + A2UI)](#canvas-screenshots--a2ui)
- [Camera (Photos + Videos)](#camera-photos--videos)
- [Screen Recording](#screen-recording)
- [Location](#location)
- [SMS (Android)](#sms-android)
- [System Commands](#system-commands)
- [Exec Node Binding](#exec-node-binding)
- [Headless Node Host](#headless-node-host)
- [Mac Node Mode](#mac-node-mode)
- [Permissions Map](#permissions-map)
- [Troubleshooting](#troubleshooting)

## Overview

- Nodes are **peripherals**, not gateways — they don't run the gateway service
- Channel messages (WhatsApp/Telegram/etc.) land on the Gateway, not on nodes
- Nodes connect with `role: "node"` in the WebSocket handshake
- They expose capabilities: `canvas.*`, `camera.*`, `system.*`, `sms.*`, `location.*`, `screen.*`

Key distinction:
- **Gateway host**: receives messages, runs the model, routes tool calls
- **Node host**: executes `system.run`/`system.which` on the node machine
- **Approvals**: enforced on the node host via `~/.openclaw/exec-approvals.json`

## Pairing + Status

Nodes must be paired before use:

```bash
# List devices / pending approvals
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>

# Node-specific status
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
```

Notes:
- Local connections (`127.0.0.1`) are auto-approved
- Remote connections (LAN, Tailnet) require explicit approval
- Each browser profile generates a unique device ID — switching browsers requires re-pairing

## Remote Node Host (system.run)

### Start a Node Host (Foreground)

```bash
openclaw node run --host <gateway-host> --port 18789 --display-name "Build Node"
```

### Remote Gateway via SSH Tunnel (loopback bind)

```bash
# Terminal A (keep running): forward local port
ssh -N -L 18790:127.0.0.1:18789 user@gateway-host

# Terminal B: connect through the tunnel
export OPENCLAW_GATEWAY_TOKEN="<gateway-token>"
openclaw node run --host 127.0.0.1 --port 18790 --display-name "Build Node"
```

- The token is `gateway.auth.token` from the gateway config
- `openclaw node run` reads `OPENCLAW_GATEWAY_TOKEN` for auth

### Start a Node Host (Service)

```bash
openclaw node install --host <gateway-host> --port 18789 --display-name "Build Node"
openclaw node restart
```

### Pair + Name

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes list
```

- `--display-name` on `openclaw node run` / `openclaw node install` (persists in `~/.openclaw/node.json`)
- `openclaw nodes rename --node <id|name|ip> --name "Build Node"` (gateway override)

### Allowlist Commands

```bash
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/uname"
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/sw_vers"
```

Stored at: `~/.openclaw/exec-approvals.json`

### Point Exec at the Node

```bash
openclaw config set tools.exec.host node
openclaw config set tools.exec.security allowlist
openclaw config set tools.exec.node "<id-or-name>"
```

## Canvas (Screenshots + A2UI)

### Screenshots (canvas snapshots)

```bash
openclaw nodes canvas snapshot --node <idOrNameOrIp> --format png
openclaw nodes canvas snapshot --node <idOrNameOrIp> --format jpg --max-width 1200 --quality 0.9
```

### Canvas Controls

```bash
openclaw nodes canvas present --node <idOrNameOrIp> --target https://example.com
openclaw nodes canvas hide --node <idOrNameOrIp>
openclaw nodes canvas navigate https://example.com --node <idOrNameOrIp>
openclaw nodes canvas eval --node <idOrNameOrIp> --js "document.title"
```

- `canvas present` accepts URLs or local file paths (`--target`), plus optional `--x/--y/--width/--height`
- `canvas eval` accepts inline JS (`--js`)

### A2UI (Canvas)

```bash
openclaw nodes canvas a2ui push --node <idOrNameOrIp> --text "Hello"
openclaw nodes canvas a2ui push --node <idOrNameOrIp> --jsonl ./payload.jsonl
openclaw nodes canvas a2ui reset --node <idOrNameOrIp>
```

- Only A2UI v0.8 JSONL supported (v0.9/`createSurface` is rejected)

## Camera (Photos + Videos)

```bash
# List cameras
openclaw nodes camera list --node <idOrNameOrIp>

# Take photo (default: both facings)
openclaw nodes camera snap --node <idOrNameOrIp>
openclaw nodes camera snap --node <idOrNameOrIp> --facing front

# Record video clip (mp4)
openclaw nodes camera clip --node <idOrNameOrIp> --duration 10s
openclaw nodes camera clip --node <idOrNameOrIp> --duration 3000 --no-audio
```

- Node must be **foregrounded** for `canvas.*` and `camera.*` (background → `NODE_BACKGROUND_UNAVAILABLE`)
- Clip duration clamped to ≤ 60s
- Android prompts for `CAMERA`/`RECORD_AUDIO` permissions; denied → `*_PERMISSION_REQUIRED`

## Screen Recording

```bash
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10 --no-audio
```

- Requires node app to be foregrounded
- Android shows system screen-capture prompt before recording
- Clamped to ≤ 60s
- `--no-audio` disables microphone capture
- `--screen <index>` to select display when multiple screens available

## Location

```bash
openclaw nodes location get --node <idOrNameOrIp>
openclaw nodes location get --node <idOrNameOrIp> --accuracy precise --max-age 15000 --location-timeout 10000
```

- Location is **off by default**
- "Always" requires system permission; background fetch is best-effort
- Response includes: lat/lon, accuracy (meters), timestamp

## SMS (Android)

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command sms.send \
  --params '{"to":"+15555550123","message":"Hello from OpenClaw"}'
```

- Permission prompt must be accepted on the Android device
- Wi-Fi-only devices without telephony will not advertise `sms.send`

## System Commands

```bash
# Run commands on node
openclaw nodes run --node <idOrNameOrIp> -- echo "Hello from node"

# Send notifications
openclaw nodes notify --node <idOrNameOrIp> --title "Ping" --body "Gateway ready"
```

### system.run Details

- Returns stdout/stderr/exit code in the payload
- Supports `--cwd`, `--env KEY=VAL`, `--command-timeout`, `--needs-screen-recording`
- `system.notify` supports `--priority <passive|active|timeSensitive>` and `--delivery <system|overlay|auto>`

### Security

- Node hosts ignore PATH overrides and strip dangerous env keys: `DYLD_*`, `LD_*`, `NODE_OPTIONS`, `PYTHON*`, `PERL*`, `RUBYOPT`, `SHELLOPTS`, `PS4`
- On macOS node mode: gated by exec approvals (Settings → Exec approvals)
- On headless node host: gated by `~/.openclaw/exec-approvals.json`
- Denied prompts return `SYSTEM_RUN_DENIED`

## Exec Node Binding

Route `exec` tool calls to a specific node:

```bash
# Set per-agent
openclaw config set tools.exec.node "node-id-or-name"

# Or per-agent in list
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"

# Unset
openclaw config unset tools.exec.node
```

## Headless Node Host

Cross-platform (macOS / Linux / Windows):

```bash
openclaw node run --host <gateway-host> --port 18789
```

- Pairing required (Gateway shows node approval prompt)
- Node state stored at `~/.openclaw/node.json`
- Exec approvals enforced via `~/.openclaw/exec-approvals.json`
- On macOS: set `OPENCLAW_NODE_EXEC_HOST=app` to route through companion app; `OPENCLAW_NODE_EXEC_FALLBACK=0` to require it
- TLS: add `--tls` / `--tls-fingerprint` when Gateway WS uses TLS

## Mac Node Mode

- macOS menubar app connects to Gateway WS as a node
- In remote mode, the app opens an SSH tunnel for the Gateway port
- `openclaw nodes …` commands work against this Mac

## Permissions Map

| Capability | Requires |
|---|---|
| `canvas.*` | Node foregrounded |
| `camera.*` | Node foregrounded + camera permission |
| `screen.record` | Node foregrounded + screen recording permission |
| `location.get` | Location permission |
| `sms.send` | SMS permission (Android only) |
| `system.run` | Exec approval (allowlist/ask/full) |
| `system.notify` | Notification permission |

## Troubleshooting

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw devices list
openclaw doctor
```

| Symptom | Cause | Fix |
|---|---|---|
| Node not appearing | Not paired | `openclaw devices list`, approve pending |
| `NODE_BACKGROUND_UNAVAILABLE` | App not foregrounded | Bring node app to foreground |
| `*_PERMISSION_REQUIRED` | Missing device permission | Grant permission on device |
| `SYSTEM_RUN_DENIED` | Exec approval denied | Check `~/.openclaw/exec-approvals.json` |
| SSH tunnel not connecting | Wrong token/port | Check `OPENCLAW_GATEWAY_TOKEN`, port mapping |
