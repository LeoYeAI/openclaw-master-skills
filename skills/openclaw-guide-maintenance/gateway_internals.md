# Gateway Internals Reference

> Sources: network-model, gateway-lock, health, doctor, logging, background-process

## Network Model

> Source: https://docs.openclaw.ai/gateway/network-model

### Core Rules

- **One Gateway per host** recommended. For rescue bots or strict isolation, use multiple gateways with isolated profiles and unique ports.
- **Loopback first**: Gateway WS defaults to `ws://127.0.0.1:18789`. Wizard generates a token even for loopback. For tailnet access: `openclaw gateway --bind tailnet --token ...` (tokens required for non-loopback).
- **Nodes** connect via LAN, tailnet, or SSH. Legacy TCP bridge is deprecated.
- **Canvas/UI routes** served on same port as Gateway HTTP:
  - `/__openclaw__/canvas/`
  - `/__openclaw__/a2ui/`
  - Protected by `gateway.auth` when binding beyond loopback.
  - Node clients use node-scoped capability URLs tied to their active WS session.
- **Remote use**: typically SSH tunnel or Tailscale VPN.

## Gateway Lock

> Source: https://docs.openclaw.ai/gateway/gateway-lock

### Why
- Ensure only one gateway instance per base port per host.
- Survive crashes/SIGKILL without stale lock files.
- Fail fast when the control port is occupied.

### Mechanism
- Gateway binds WebSocket listener (default `ws://127.0.0.1:18789`) immediately on startup using exclusive TCP.
- If bind fails with `EADDRINUSE`: `GatewayLockError("another gateway instance is already listening on ws://127.0.0.1:<port>")`.
- OS releases the listener automatically on any process exit (including crashes, SIGKILL) — no lock file needed.
- On shutdown, Gateway closes WS server and HTTP server to free the port promptly.

### Error Surface
| Error | Cause |
|---|---|
| `GatewayLockError("another gateway instance is already listening...")` | Another process holds the port |
| `GatewayLockError("failed to bind gateway socket...")` | Other bind failure |

### Fix
- Free the port or choose another: `openclaw gateway --port <port>`
- macOS app maintains its own PID guard before spawning; runtime lock enforced by WS bind.

## Health Checks

> Source: https://docs.openclaw.ai/gateway/health

### Quick Checks
| Command | Purpose |
|---|---|
| `openclaw status` | Local summary: reachability, mode, update hint, channel auth age, sessions |
| `openclaw status --all` | Full local diagnosis (read-only, safe to paste for debugging) |
| `openclaw status --deep` | Also probes running Gateway (per-channel probes) |
| `openclaw health --json` | Asks running Gateway for full health snapshot (WS-only) |
| `/status` (in WhatsApp/WebChat) | Status reply without invoking agent |

### Deep Diagnostics
- **Creds on disk**: `ls -l ~/.openclaw/credentials/whatsapp/<accountId>/creds.json` (mtime should be recent)
- **Session store**: `ls -l ~/.openclaw/agents/<agentId>/sessions/sessions.json`
- **Relink flow**: `openclaw channels logout && openclaw channels login --verbose` when status codes 409–515 or `loggedOut` appear
- **Logs**: `tail /tmp/openclaw/openclaw-*.log` and filter for `web-heartbeat`, `web-reconnect`, `web-auto-reply`, `web-inbound`

### When Something Fails
| Symptom | Fix |
|---|---|
| `logged out` or status 409–515 | Relink: `openclaw channels logout` then `openclaw channels login` |
| Gateway unreachable | Start it: `openclaw gateway --port 18789` (`--force` if busy) |
| No inbound messages | Check `channels.whatsapp.allowFrom`, group `mentionPatterns` |

## Doctor

> Source: https://docs.openclaw.ai/gateway/doctor

### Quick Start
```bash
openclaw doctor       # Interactive diagnosis + healing
openclaw doctor --fix # Auto-fix safe issues (non-interactive)
```

### What It Does (19 Steps)
1. Optional pre-flight update (git installs, interactive only)
2. UI protocol freshness check (rebuilds Control UI when schema is newer)
3. Config normalization for legacy values
4. OpenCode Zen provider override warnings (`models.providers.opencode`)
5. Legacy on-disk state migration (sessions/agent dir/WhatsApp auth)
6. State integrity + permissions checks (sessions, transcripts, state dir, chmod 600)
7. Model auth health: OAuth expiry, token refresh, profile cooldown/disabled states
8. Extra workspace dir detection (`~/openclaw`)
9. Sandbox image repair (when sandboxing enabled)
10. Legacy service migration + extra gateway detection
11. Skills status summary (eligible/missing/blocked)
12. Gateway auth checks (local token mode, offers token generation)
13. SecretRef-aware read-only repairs
14. Gateway health check + restart prompt
15. Channel status warnings (probed from running gateway)
16. Supervisor config audit + repair (launchd/systemd/schtasks)
17. Gateway runtime + port diagnostics (default 18789)
18. Gateway runtime best-practice checks (Node vs Bun, version-manager paths)
19. Config write + wizard metadata

### Headless / Automation
```bash
openclaw doctor --fix   # Non-interactive mode
openclaw doctor --json  # Machine-readable output
```

## Logging

> Source: https://docs.openclaw.ai/gateway/logging

### File-Based Logger
- Default rolling log file: `/tmp/openclaw/openclaw-YYYY-MM-DD.log` (one per day, local timezone)
- Configure via `logging.file` and `logging.level` in `openclaw.json`
- Tail logs: `openclaw logs --follow`
- `--verbose` only affects console verbosity, **not** file log level
- For verbose details in file logs: set `logging.level` to `debug` or `trace`

### Console Capture
- `logging.consoleLevel` (default: `info`)
- `logging.consoleStyle`: `pretty` | `compact` | `json`

### Tool Summary Redaction
- `logging.redactSensitive`: `off` | `tools` (default: `tools`)
- `logging.redactPatterns`: array of regex strings (overrides defaults)
- Masks: keeps first 6 + last 4 chars (length ≥ 18), otherwise `***`
- Defaults cover: key assignments, CLI flags, JSON fields, bearer headers, PEM blocks, token prefixes

### Gateway WebSocket Logs
- **Normal mode**: only "interesting" results — errors (`ok=false`), slow calls (≥ 50ms), parse errors
- **Verbose mode** (`--verbose`): prints all WS request/response traffic

## Background Exec + Process Tool

> Source: https://docs.openclaw.ai/gateway/background-process

### exec Tool Parameters
| Parameter | Default | Description |
|---|---|---|
| `command` | (required) | Command to run |
| `yieldMs` | 10000 | Auto-background after this delay |
| `background` | false | Background immediately |
| `timeout` | 1800 sec | Kill process after timeout |
| `elevated` | false | Run on host if elevated mode allowed |
| `pty` | false | Set `true` for real TTY |
| `workdir` | workspace | Working directory |
| `env` | — | Environment variables |

- Foreground runs return output directly
- When backgrounded: returns `status: "running"` + `sessionId` and short tail
- Spawned exec commands receive `OPENCLAW_SHELL=exec`

### Config Tuning
| Key | Default | Description |
|---|---|---|
| `tools.exec.backgroundMs` | 10000 | Auto-background threshold |
| `tools.exec.timeoutSec` | 1800 | Process timeout |
| `tools.exec.cleanupMs` | 1800000 | Cleanup TTL |
| `tools.exec.notifyOnExit` | true | Enqueue event on background exit |
| `tools.exec.notifyOnExitEmptySuccess` | false | Also notify on empty success |

### process Tool Actions
| Action | Description |
|---|---|
| `list` | Running + finished sessions |
| `poll` | Drain new output (reports exit status) |
| `log` | Read aggregated output (offset + limit) |
| `write` | Send stdin (data, optional eof) |
| `kill` | Terminate background session |
| `clear` | Remove finished session |
| `remove` | Kill if running, clear if finished |

- Sessions are **not** persisted to disk — lost on restart
- Process scoped per agent; only sees sessions from that agent

## See Also

- [architecture.md](architecture.md) — Gateway architecture overview
- [remote_access.md](remote_access.md) — SSH, Tailscale, web dashboard
- [presence_discovery.md](presence_discovery.md) — Presence and discovery
