# Operations & Configuration

## Configuration

Data directory: `~/.opcode/` (DB, settings, pidfile). Created automatically.

First-time setup:

```bash
opcode install --listen-addr :4100 --vault-key "my-passphrase"
```

`--vault-key` is memory-only (not persisted). For production, set `OPCODE_VAULT_KEY` env var.

Writes `~/.opcode/settings.json`, downloads [`mermaid-ascii`](https://github.com/AlexanderGrooff/mermaid-ascii) to `~/.opcode/bin/` for enhanced ASCII diagrams, and starts the daemon. All settings overridable via env vars (`OPCODE_LISTEN_ADDR`, `OPCODE_DB_PATH`, etc.).

| Setting       | Default                 | Env override         | Description                                 |
| ------------- | ----------------------- | -------------------- | ------------------------------------------- |
| `listen_addr` | `:4100`                 | `OPCODE_LISTEN_ADDR` | TCP listen address                          |
| `base_url`    | `http://localhost:4100` | `OPCODE_BASE_URL`    | Public base URL for SSE                     |
| `db_path`     | `~/.opcode/opcode.db`   | `OPCODE_DB_PATH`     | Path to embedded libSQL database            |
| `log_level`   | `info`                  | `OPCODE_LOG_LEVEL`   | `debug`, `info`, `warn`, `error`            |
| `pool_size`   | `10`                    | `OPCODE_POOL_SIZE`   | Worker pool size                            |
| `panel`       | `false`                 | `OPCODE_PANEL`       | Enable web panel (`true`/`1`)               |
| _(env only)_  | _(empty)_               | `OPCODE_VAULT_KEY`   | Passphrase for secret vault (never in JSON) |

> **Security**: Never put `OPCODE_VAULT_KEY` in `settings.json`. Use env vars or your platform's secrets manager. The passphrase derives the AES-256 encryption key via PBKDF2.

If the process stops, restart with:

```bash
OPCODE_VAULT_KEY="my-passphrase" opcode
```

`install` is only needed once. Subsequent restarts use `opcode` directly with the env var.

## Subcommands

| Command          | Description                                            |
| ---------------- | ------------------------------------------------------ |
| `opcode`         | Start SSE daemon (same as `opcode serve`)              |
| `opcode serve`   | Start SSE daemon explicitly                            |
| `opcode install` | Write settings.json, SIGHUP running server or start    |
| `opcode update`  | Self-update (GitHub releases -> `go install` fallback) |
| `opcode version` | Print embedded version (default `dev`)                 |

## Hot-Reload via SIGHUP

Running `opcode install` with a server already running sends SIGHUP to reload configuration without restarting. You can also send it manually: `kill -HUP $(cat ~/.opcode/opcode.pid)`.

| Setting       | Hot-Reload | Notes                   |
| ------------- | ---------- | ----------------------- |
| `panel`       | YES        | Mux swapped atomically  |
| `log_level`   | YES        | LevelVar.Set()          |
| `listen_addr` | NO         | Needs listener rebind   |
| `base_url`    | NO         | SSEServer constructed   |
| `db_path`     | NO         | Store opened at startup |
| `pool_size`   | NO         | Pool sized at startup   |

## Building with Version

```bash
make build          # embeds git tag/commit as version
./opcode version    # prints e.g. "v1.0.0" or "abc1234-dirty"
```

Without `make`, `go build` works normally (version = `dev`).

## Connecting via mcporter

[mcporter](https://github.com/steipete/mcporter) is a universal MCP CLI client (npm), used by [openclaw](https://openclaw.ai/).

Register the running opcode daemon:

```bash
mcporter config add opcode http://localhost:4100/sse --allow-http
```

Verify connection:

```bash
mcporter list                       # all servers
mcporter list opcode --schema       # 6 tools with JSON schemas
```

Call tools (function-call syntax):

```bash
mcporter call 'opcode.run(template_name: "my-wf", agent_id: "bot-1")'
```

Or flag-based syntax:

```bash
mcporter call --server opcode --tool opcode.define --args '{
  "name": "my-workflow",
  "agent_id": "bot-1",
  "definition": { "steps": [...] }
}'
```

Manual config (`~/.mcporter/mcporter.json`):

```json
{
  "mcpServers": {
    "opcode": {
      "url": "http://localhost:4100/sse"
    }
  }
}
```

> Non-HTTPS endpoints require `--allow-http` on each call, or `--insecure` as alias.

## Startup Sequence

1. Writes pidfile to `~/.opcode/opcode.pid`
2. Loads config from `~/.opcode/settings.json` (env vars override)
3. Creates data directory, opens/creates libSQL database, runs migrations
4. Suspends orphaned `active` workflows (emits `workflow_interrupted`)
5. Initializes secret vault (if `OPCODE_VAULT_KEY` set)
6. Registers 25 built-in actions
7. Starts cron scheduler (recovers missed jobs)
8. Registers SIGHUP handler for config hot-reload
9. Begins listening for MCP JSON-RPC over SSE (+ web panel if `panel` enabled) on same port
10. Shuts down gracefully on SIGTERM/SIGINT (10s timeout), removes pidfile

## Security Model

Built-in actions respect `ResourceLimits` configured at startup:

| Control        | Description                                                                                                |
| -------------- | ---------------------------------------------------------------------------------------------------------- |
| **Filesystem** | `DenyPaths` / `ReadOnlyPaths` / `WritablePaths` restrict file access. Symlink resolution prevents escapes. |
| **Shell**      | Linux: cgroups v2 (memory, CPU, PID namespace). macOS: timeout-only fallback.                              |
| **HTTP**       | `MaxResponseBody` (10 MB) and `DefaultTimeout` (30 s).                                                     |

**Defaults are permissive** (no path deny-lists, no network restrictions). For production:

- Set `DenyPaths` for sensitive directories (`/etc/shadow`, `~/.ssh`)
- Set `WritablePaths` to constrain write scope
- Run the opcode process under a restricted OS user
- Use a network proxy/firewall for HTTP egress control
- Treat `OPCODE_VAULT_KEY` as root-equivalent for stored secrets

Crypto, assert, and workflow actions perform no I/O beyond the opcode database.

## Web Panel

The daemon can serve a web management panel at the same port as MCP SSE (default `http://localhost:4100`). Enable with `--panel` flag or `OPCODE_PANEL=true` env var. Can be toggled at runtime via SIGHUP.

| Page            | Features                                                  |
| --------------- | --------------------------------------------------------- |
| Dashboard       | System counters, per-agent table, pending decisions, feed |
| Workflows       | Filter by status/agent, pagination, cancel, re-run        |
| Workflow Detail | Live DAG diagram, step states, events timeline            |
| Templates       | List, create via JSON paste (auto-versions), definition   |
| Template Detail | Version selector, Mermaid diagram preview                 |
| Decisions       | Pending queue, resolve/reject forms with context          |
| Scheduler       | Cron job CRUD, enable/disable, run history                |
| Events          | Event log filtered by workflow and/or type                |
| Agents          | Registered agents with type and last-seen                 |

Live updates via SSE -- dashboard and workflow detail pages auto-refresh on new events.

## Performance

Key benchmarks (run `make benchmarks` to regenerate):

| Metric                     | Value           |
| -------------------------- | --------------- |
| 10-step parallel workflow  | ~50us           |
| 100-step parallel workflow | ~460us          |
| Event append (libSQL)      | ~15k events/sec |
| Event replay (1000 events) | ~6.5ms          |
| Worker pool throughput     | >1M tasks/sec   |
