---
name: omniwire
version: 3.5.0
description: "Infrastructure layer for AI agent swarms — 88 MCP tools for mesh control, A2A protocol, OmniMesh VPN, CyberSync, web scraping, firewall management, browser automation, and more. ~80ms execution."
tags: [infrastructure, mesh, ssh, devops, servers, docker, remote, mcp, vpn, wireguard, a2a, cybersync, firewall, scraping, browser, security, arm, monitoring, latest]
author: VoidChecksum
homepage: https://github.com/VoidChecksum/omniwire
license: GPL-3.0-only
metadata:
  openclaw:
    emoji: "🌐"
    primaryEnv: ""
    skillKey: omniwire
    requires:
      bins: ["node", "ssh"]
      env: []
    install:
      - kind: node
        package: omniwire@latest
        bins: ["omniwire", "ow"]
    stateDirs: ["~/.omniwire"]
    persistence: "OmniWire uses SSH2 to control mesh nodes. Config in ~/.omniwire/mesh.json. Encrypted secrets in ~/.omniwire/secret.key. CyberSync stores knowledge in PostgreSQL. No data leaves your network."
---

# OmniWire v3.5.0 — Mesh Control for AI Agent Swarms

> **88 MCP tools. 12 categories. Every machine, one agent, zero friction.**

OmniWire is the infrastructure layer for AI agent swarms. It connects your entire mesh (VPS, laptops, Raspberry Pis, Docker hosts) into a single controllable surface with 88 tools spanning execution, A2A protocol, OmniMesh VPN, CyberSync, web scraping, firewall management, CDP browser automation, and more.

```
You: check disk and container status on all servers

Agent: [omniwire_broadcast + omniwire_docker — parallel across all nodes]

  contabo  | 10.0.0.1 | ONLINE | 78ms  | disk=16% | containers: 12 running
  kali     | 10.0.0.2 | ONLINE | 91ms  | disk=34% | containers: 4 running
  rpi      | 10.0.0.3 | ONLINE | 112ms | disk=20% | containers: 2 running
```

---

## What It Does

| Category | Tools | What your agent can do |
|----------|-------|----------------------|
| **Execution** | 6 | Run commands, scripts, pipelines, background jobs on any node |
| **Agentic / A2A** | 13 | Agent tasks, messaging, blackboard, workflows, semaphores, registries |
| **Files** | 6 | Read, write, list, find, transfer, deploy files across nodes |
| **Monitoring** | 4 | Mesh health, live metrics, benchmarks, node info |
| **System / DevOps** | 14 | Processes, disks, packages, services, Docker, kernel, cron, git, logs |
| **Network / VPN** | 7 | VPN switching, port forwarding, browser, shell, streams, proxy, scraping |
| **Security** | 6 | Firewall, certs, audit, 2FA/TOTP, cookies, user management |
| **CyberSync** | 9 | Bi-directional config sync for 6 AI tools + knowledge/memory |
| **Knowledge** | 2 | Store and search unified knowledge base (pgvector) |
| **OmniMesh** | 3 | WireGuard mesh manager, expose services, gateway routing |
| **Events** | 1 | Webhook + WebSocket + SSE event bus |
| **CDP Browser** | 1 | 18 browser actions via persistent Docker Chrome |
| **Utilities** | 10+ | Alerts, aliases, backups, snippets, DNS, diagnostics, scheduling |

---

## Setup — 3 Steps

### Step 1: Install OmniWire

> **AGENT: Run this via exec. User just clicks Approve.**

```bash
npm install -g omniwire@latest
```

Works on: Linux (x64, ARM64, ARMv7), macOS (Intel + Apple Silicon), Windows (x64).

### Step 2: Configure Your Mesh

Create the mesh config. Ask the user for their server details:

> **AGENT: Ask the user:**
> "What servers do you want to control? For each one I need:
> - A name (e.g., `contabo`, `kali`, `rpi`)
> - IP address or hostname
> - SSH user (usually `root`)
> - SSH key filename in ~/.ssh/ (e.g., `id_ed25519`)
> - Role: `storage`, `compute`, `gpu+browser`, or leave blank"

Then create the config:

```bash
mkdir -p ~/.omniwire
cat > ~/.omniwire/mesh.json << 'EOF'
{
  "nodes": [
    {
      "id": "contabo",
      "host": "10.0.0.1",
      "user": "root",
      "identityFile": "id_ed25519",
      "role": "storage",
      "tags": ["vps", "docker"]
    },
    {
      "id": "kali",
      "host": "10.0.0.2",
      "user": "root",
      "identityFile": "id_ed25519",
      "role": "compute",
      "tags": ["kali", "pentest"]
    }
  ],
  "cyberbase": {
    "host": "10.10.0.1",
    "port": 5432,
    "database": "cyberbase",
    "user": "cyberbase"
  }
}
EOF
```

### Step 3: Verify

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}' \
  | omniwire --stdio --no-sync 2>/dev/null | head -1
```

Should respond with `omniwire v3.5.0`. Done.

**Transport options:**

| Transport | Command | Port |
|-----------|---------|------|
| stdio (MCP default) | `omniwire --stdio` | — |
| SSE (HTTP streaming) | `omniwire --sse` | 3200 |
| REST (HTTP JSON) | `omniwire --rest` | 3201 |
| Events (WebSocket) | `omniwire --events` | 3202 |

---

## Usage Examples

### Execute commands anywhere

```
You: restart nginx on contabo

Agent: [omniwire_exec node=contabo command="systemctl restart nginx"]
  OK — nginx restarted (0ms)

You: run uptime on every server

Agent: [omniwire_broadcast command="uptime"]
  contabo  | up 42 days, 3:21
  kali     | up 7 days, 11:04
  rpi      | up 2 days, 0:15
```

### Transfer files between nodes

```
You: copy the pentest report from kali to contabo

Agent: [omniwire_transfer_file src_node=kali dest_node=contabo src=/root/report.pdf dest=/var/reports/]
  Transferred 2.4MB — LZ4 compressed — 83ms
```

Transfer modes (auto-selected):
- **SFTP** for files under 10MB
- **netcat + LZ4** for 10MB–1GB
- **aria2c** for files over 1GB (16 parallel connections)

### Docker management

```
You: what containers are running on contabo?

Agent: [omniwire_docker node=contabo action=ps]
  12 running — neo4j, postgres, omnibus-hub, kali-htb, omniwire-events...

You: pull and start the latest omniwire-events image

Agent: [omniwire_container node=contabo action=pull image=omniwire-events:latest]
  Pulled. Starting...
  ✓ omniwire-events running (healthy)
```

### Monitor mesh health

```
You: how are all my servers doing?

Agent: [omniwire_mesh_status]

  contabo  | 10.0.0.1 | ONLINE | 78ms  | load=1.2 | mem=31% | disk=16%
  kali     | 10.0.0.2 | ONLINE | 91ms  | load=0.4 | mem=19% | disk=34%
  rpi      | 10.0.0.3 | ONLINE | 112ms | load=0.7 | mem=22% | disk=20%
```

### VPN switching

```
You: switch to Mullvad on the kali node

Agent: [omniwire_vpn node=kali action=connect provider=mullvad country=nl]
  Connected — Netherlands exit — mesh routes preserved
  New IP: 185.65.134.x
```

Supported providers: Mullvad, OpenVPN, WireGuard, Tailscale. OmniMesh routes are protected during VPN switches.

### Web scraping with Cloudflare bypass

```
You: scrape the pricing table from example.com

Agent: [omniwire_scrape node=contabo url=https://example.com/pricing selector=".pricing-table"]
  Scraped 4.2KB — Scrapling engine — Cloudflare bypassed
  [returns structured data]
```

### A2A agent messaging

```
You: send a task to the pentest agent on kali

Agent: [omniwire_agent_task node=kali agent_id=pentest-agent task={type:"scan", target:"192.168.1.0/24"}]
  Task queued — ID: task_abc123

Agent: [omniwire_blackboard action=watch key=task_abc123/result]
  Result ready: {hosts: 12, open_ports: [...]}
```

### COC — Unified CyberBase + Obsidian + Canvas sync

```
You: COC save — OmniWire v3.5.0 deployed with 88 tools

Agent: [omniwire_coc action=save note="OmniWire v3.5.0 deployed with 88 tools"]
  Saved to CyberBase (knowledge table)
  Mirrored to Obsidian vault: CyberBase/omniwire-v350.md
  Canvas node updated: CyberBase MindMap.canvas
  ✓ All 3 sync targets confirmed
```

---

## Full Tool Reference

<details>
<summary><strong>Execution (6 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_exec` | Execute a command on a specific node. Args: `node`, `command`, `timeout`, `background` |
| `omniwire_run` | Run a named script or predefined task. Args: `node`, `script`, `args` |
| `omniwire_batch` | Execute multiple commands across multiple nodes in one call. Args: `commands[]` |
| `omniwire_broadcast` | Execute command on ALL nodes simultaneously. Args: `command`, `tags` (filter by tag) |
| `omniwire_pipeline` | Chain commands where output of one feeds into next. Args: `node`, `steps[]` |
| `omniwire_bg` | Background task manager — dispatch, poll, get result. Args: `action`, `task_id` |

</details>

<details>
<summary><strong>Agentic / A2A Protocol (13 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_store` | Key-value store for agents. Actions: get, set, delete, list. Args: `key`, `value`, `ttl` |
| `omniwire_watch` | Watch a key for changes (long-poll). Args: `key`, `timeout` |
| `omniwire_healthcheck` | Check agent health status across nodes. Args: `agent_id`, `node` |
| `omniwire_agent_task` | Dispatch a structured task to a named agent. Args: `node`, `agent_id`, `task` |
| `omniwire_a2a_message` | Send an A2A protocol message between agents. Args: `to`, `from`, `message`, `reply_to` |
| `omniwire_semaphore` | Distributed semaphore for agent coordination. Actions: acquire, release. Args: `name`, `count` |
| `omniwire_event` | Emit a named event into the event bus. Args: `event`, `data`, `targets[]` |
| `omniwire_workflow` | Execute a multi-step workflow definition. Args: `workflow_id`, `input` |
| `omniwire_agent_registry` | Register/discover agents by capability. Actions: register, lookup, list |
| `omniwire_blackboard` | Shared blackboard for agent state. Actions: read, write, watch, clear |
| `omniwire_task_queue` | Distributed task queue. Actions: push, pop, peek, size |
| `omniwire_capability` | Declare/query agent capabilities. Args: `agent_id`, `capabilities[]` |
| `omniwire_coc` | COC — unified CyberBase + Obsidian + Canvas sync. Actions: save, read, search, update |

</details>

<details>
<summary><strong>Files (6 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_read_file` | Read file from any node. Args: `node`, `path`, `encoding`, `lines` |
| `omniwire_write_file` | Write file to any node. Args: `node`, `path`, `content`, `mode` |
| `omniwire_list_files` | List directory on any node. Args: `node`, `path`, `recursive`, `filter` |
| `omniwire_find_files` | Search files across nodes by name/content/pattern. Args: `node`, `query`, `path` |
| `omniwire_transfer_file` | Copy files between nodes (auto-selects SFTP/LZ4/aria2c). Args: `src_node`, `dest_node`, `src`, `dest` |
| `omniwire_deploy` | Push files or directories to multiple nodes simultaneously. Args: `src`, `nodes[]`, `dest` |

</details>

<details>
<summary><strong>Monitoring (4 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_mesh_status` | Health check all nodes — latency, load, memory, disk. Cached 5s. |
| `omniwire_node_info` | Detailed info for one node — OS, CPU, uptime, IPs. Args: `node` |
| `omniwire_live_monitor` | Live system metrics snapshot. Args: `node`, `interval`, `metrics[]` |
| `omniwire_benchmark` | Benchmark node performance — CPU, disk, network. Args: `node`, `type` |

</details>

<details>
<summary><strong>System / DevOps (14 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_process_list` | List and filter processes. Args: `node`, `filter`, `sort` |
| `omniwire_disk_usage` | Disk usage — all mounts or specific path. Args: `node`, `path` |
| `omniwire_install_package` | Install packages via apt/npm/pip/brew. Args: `node`, `package`, `manager` |
| `omniwire_service_control` | systemd start/stop/restart/status/enable. Args: `node`, `service`, `action` |
| `omniwire_docker` | Docker commands (ps, logs, exec, stats, images). Args: `node`, `action`, `container` |
| `omniwire_container` | Container lifecycle — pull, run, stop, rm, inspect. Args: `node`, `action`, `image` |
| `omniwire_kernel` | dmesg, sysctl, modprobe, strace, perf. Args: `node`, `action`, `args` |
| `omniwire_cron` | Manage cron jobs — list, add, remove. Args: `node`, `action`, `schedule`, `command` |
| `omniwire_env` | Read/write environment variables. Args: `node`, `action`, `key`, `value` |
| `omniwire_network` | Network info — interfaces, routes, connections, iptables. Args: `node`, `action` |
| `omniwire_git` | Git operations on remote nodes. Args: `node`, `repo`, `action`, `args` |
| `omniwire_syslog` | Read system logs. Args: `node`, `service`, `lines`, `since` |
| `omniwire_log_aggregate` | Aggregate logs from multiple nodes. Args: `nodes[]`, `service`, `query` |
| `omniwire_metrics` | Push/pull metrics (Prometheus-compatible). Args: `node`, `action`, `metrics` |

</details>

<details>
<summary><strong>Network / VPN (7 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_vpn` | VPN management — Mullvad, OpenVPN, WireGuard, Tailscale. Args: `node`, `action`, `provider`, `country` |
| `omniwire_port_forward` | SSH tunnel / port forwarding. Args: `node`, `local_port`, `remote_host`, `remote_port` |
| `omniwire_open_browser` | Open URL on GPU/display node. Args: `node`, `url` |
| `omniwire_shell` | Persistent shell session (state preserved). Args: `node`, `session_id`, `command` |
| `omniwire_stream` | Real-time streaming output from long-running commands. Args: `node`, `command` |
| `omniwire_proxy` | HTTP/SOCKS proxy management. Args: `node`, `action`, `port`, `type` |
| `omniwire_scrape` | Scrapling-powered web scraping with Cloudflare bypass. Args: `node`, `url`, `selector`, `format` |

</details>

<details>
<summary><strong>Security (6 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_firewall` | iptables / ufw / nftables management. Args: `node`, `action`, `rule` |
| `omniwire_cert` | TLS certificate management (Let's Encrypt, self-signed). Args: `node`, `domain`, `action` |
| `omniwire_audit` | Security audit — open ports, SUID files, cron jobs, users. Args: `node`, `checks[]` |
| `omniwire_2fa` | TOTP manager — generate, add, delete codes. CyberBase + 1Password persistence. Args: `action`, `service` |
| `omniwire_cookies` | Browser cookie export/import (JSON, Header String, Netscape). Args: `node`, `action`, `browser` |
| `omniwire_user` | User account management — create, delete, sudo, SSH keys. Args: `node`, `action`, `username` |

</details>

<details>
<summary><strong>CyberSync (9 tools)</strong></summary>

CyberSync provides bi-directional config sync for 6 AI tools: **Claude Code, OpenCode, OpenClaw, Codex, Gemini, PaperClip**. All sensitive files encrypted with XChaCha20-Poly1305 at rest.

| Tool | Description |
|------|-------------|
| `omniwire_sync` | Sync a specific file or directory across nodes. Args: `path`, `nodes[]`, `direction` |
| `omniwire_sync_rules` | Manage sync rules (include/exclude patterns). Args: `action`, `rule` |
| `omniwire_sync_hooks` | Pre/post sync hooks. Args: `action`, `hook_script` |
| `omniwire_sync_memory` | Sync Claude/agent memory to CyberBase. Args: `action`, `node` |
| `omniwire_sync_agents` | Sync agent definitions across nodes. Args: `action`, `nodes[]` |
| `cybersync_status` | Sync status — item counts, heartbeats, last sync time per tool |
| `cybersync_sync_now` | Force immediate reconciliation across all nodes |
| `cybersync_diff` | Show what's out of sync before committing |
| `cybersync_history` | Sync event log — what changed, when, which node |

</details>

<details>
<summary><strong>Knowledge (2 tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_knowledge` | Store knowledge entries in CyberBase with vector embedding. Args: `action`, `key`, `content`, `tags` |
| `omniwire_search_knowledge` | Semantic search over knowledge base (pgvector). Args: `query`, `limit`, `tags` |

</details>

<details>
<summary><strong>OmniMesh (3 tools)</strong></summary>

OmniMesh is OmniWire's built-in WireGuard mesh manager. It provisions, rotates keys, and manages peer routing automatically.

| Tool | Description |
|------|-------------|
| `omniwire_omnimesh` | Mesh lifecycle — init, add-node, remove-node, rotate-keys, status. Args: `action`, `node` |
| `omniwire_mesh_expose` | Expose a local service to the mesh via WireGuard. Args: `node`, `service`, `port`, `mesh_port` |
| `omniwire_mesh_gateway` | Configure a node as a mesh gateway (egress/ingress). Args: `node`, `action`, `routes[]` |

</details>

<details>
<summary><strong>Events (1 tool)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_events` | Event bus — subscribe, publish, list. Supports Webhook callbacks, WebSocket push (port 3202), and SSE streaming. Args: `action`, `event`, `handler_url` |

</details>

<details>
<summary><strong>CDP Browser (1 tool)</strong></summary>

`omniwire_cdp` provides 18 browser actions via a persistent Docker Chrome instance on any node. Sessions persist between calls. Cookies auto-exported in JSON + Header String + Netscape format.

| Action | Description |
|--------|-------------|
| `navigate` | Navigate to URL |
| `screenshot` | Capture page screenshot |
| `click` | Click element by selector |
| `type` | Type text into input |
| `scroll` | Scroll page |
| `evaluate` | Execute JavaScript |
| `get_html` | Get page HTML |
| `get_text` | Get visible text |
| `wait_for` | Wait for selector/navigation |
| `fill_form` | Fill multiple form fields |
| `select` | Select dropdown option |
| `hover` | Hover element |
| `upload` | Upload file to input |
| `download` | Download file |
| `cookies_get` | Export cookies |
| `cookies_set` | Import cookies |
| `session_save` | Persist session state |
| `session_load` | Restore session state |

</details>

<details>
<summary><strong>Utilities (10+ tools)</strong></summary>

| Tool | Description |
|------|-------------|
| `omniwire_alert` | Send alert via Telegram/webhook/email. Args: `message`, `channel`, `priority` |
| `omniwire_alias` | Manage command aliases for nodes. Args: `action`, `name`, `command` |
| `omniwire_backup` | Backup files/DBs to remote storage. Args: `node`, `path`, `dest`, `compress` |
| `omniwire_clipboard` | Read/write clipboard on GUI node. Args: `node`, `action`, `content` |
| `omniwire_snippet` | Store and retrieve command snippets. Args: `action`, `name`, `content` |
| `omniwire_tail_log` | Tail last N lines of a log file. Args: `node`, `path`, `lines` |
| `omniwire_trace` | Distributed trace for debugging command chains. Args: `trace_id`, `action` |
| `omniwire_update` | Check for OmniWire updates + self-update. Args: `action` |
| `omniwire_schedule` | Schedule tasks (cron-style). Args: `action`, `schedule`, `task` |
| `omniwire_dns` | DNS lookup and management. Args: `node`, `query`, `type` |
| `omniwire_doctor` | Diagnose OmniWire setup issues. Args: `checks[]` |

</details>

---

## Performance

| Operation | Speed |
|-----------|-------|
| Command execution | ~80ms per node |
| File read (< 1MB) | ~60ms (SFTP) |
| File transfer (10MB) | ~150ms (LZ4 netcat) |
| Mesh status check | ~100ms (cached 5s) |
| COC sync (all 3 targets) | ~200ms (parallel) |
| Web scrape (no JS) | ~300ms |
| Web scrape (Cloudflare) | ~800ms |
| CDP browser action | ~120ms |

Encryption: **AES-128-GCM** for transport, **XChaCha20-Poly1305** for at-rest sync items. Compression: **LZ4** for transfers.

---

## Architecture & Platform Support

| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux | x64 | Supported |
| Linux | arm64 (RPi 4/5, AWS Graviton) | Supported |
| Linux | armv7l (RPi 3, older ARM) | Supported |
| macOS | Intel (x64) | Supported |
| macOS | Apple Silicon (arm64) | Supported |
| Windows | x64 | Supported |

No native compilation. Pure JavaScript + SSH2. `npm install -g omniwire` works everywhere Node.js 18+ runs.

**Transports:** stdio (MCP standard), SSE port 3200, REST port 3201, Events/WebSocket port 3202.

---

## Security

| Layer | Implementation |
|-------|---------------|
| Transport | SSH2 with zlib compression |
| At-rest (sync items) | XChaCha20-Poly1305 |
| Transfer compression | LZ4 |
| Secrets backend | 1Password, file-based, or env vars |
| Network | All traffic over your own infrastructure (WireGuard, Tailscale, direct SSH) |
| Key management | Master key in `~/.omniwire/secret.key` — generated locally, never transmitted |
| Mesh auth | Per-node WireGuard keypairs, auto-rotated by OmniMesh |

---

## Agent Instructions

### When to use OmniWire tools

Use OmniWire when the user:
- Mentions servers, VPS, nodes, mesh, or "my machines"
- Wants commands run remotely or on all servers
- Needs files read, written, or transferred between nodes
- Asks about Docker, services, processes, or system health on remote nodes
- Wants to switch VPN, manage firewall rules, or handle certs
- Mentions "scrape", "browser", "CDP", or web automation on a remote node
- Wants to sync configs, save memory, or COC/save something
- Uses agent-to-agent workflows (A2A, blackboard, task queues)
- Needs TOTP codes, cookies, or security audit
- Mentions "COC", "Save to CyberBase", "Obsidian", or canvas sync

### How to pick the right tool

| Intent | Tool |
|--------|------|
| Single node command | `omniwire_exec` |
| All nodes at once | `omniwire_broadcast` |
| Read remote file | `omniwire_read_file` |
| Copy between nodes | `omniwire_transfer_file` |
| Docker anything | `omniwire_docker` |
| Container lifecycle | `omniwire_container` |
| Mesh health check | `omniwire_mesh_status` |
| VPN switch | `omniwire_vpn` |
| Firewall rule | `omniwire_firewall` |
| Web scrape | `omniwire_scrape` |
| Browser automation | `omniwire_cdp` |
| Send agent task | `omniwire_agent_task` |
| Shared state | `omniwire_blackboard` |
| Event bus | `omniwire_event` or `omniwire_events` |
| COC save/sync | `omniwire_coc` |
| Semantic search | `omniwire_search_knowledge` |
| Background job | `omniwire_bg` |
| Sync AI configs | `cybersync_sync_now` |

### Node selection defaults

If the user doesn't specify a node:
- File storage, databases, Docker → node with `role: "storage"`
- Security/pentest tools → node with tag `"kali"` or `"pentest"`
- GPU / display / browser → node with `role: "gpu+browser"`
- Heavy compute → node with `role: "compute"`
- Background task dispatch → `omniwire_bg` with any available node
- If ambiguous, ask: "Which server should I run this on?"

### Background mode

All 88 tools support `background: true`. Use it for:
- Any operation expected to take > 5 seconds
- Builds, installs, deploys, large transfers
- Scraping and CDP sessions
- Long-running pipelines

```
omniwire_exec(node="contabo", command="apt upgrade -y", background=true)
→ returns task_id immediately
→ poll with omniwire_bg(action="poll", task_id="...")
→ get result with omniwire_bg(action="result", task_id="...")
```

### Error handling

- If a node is offline, report it and offer alternatives
- If exec fails, show stderr and suggest fixes
- If transfer fails, retry with a different mode (SFTP → LZ4 → aria2c)
- If VPN connects but mesh breaks, restore mesh routes automatically (built-in)
- For persistent shell failures, use `omniwire_shell` with a new `session_id`

---

## OpenClaw + PaperClip Integration

OmniWire is the primary infrastructure backend for OpenClaw agents and PaperClip workflows.

### OpenClaw

OpenClaw agents use OmniWire for all remote operations. The skill is auto-loaded when OpenClaw detects `omniwire` in the installed MCP servers. Agents can:
- Execute tasks across the mesh without user intervention
- Use the A2A protocol to coordinate multi-agent workflows
- Persist state via the blackboard and knowledge base
- Dispatch background jobs and collect results asynchronously

### PaperClip

PaperClip workflows integrate with OmniWire via CyberSync. Any workflow that produces knowledge, memory, or config changes can route through `omniwire_coc` for unified persistence across CyberBase, Obsidian vault, and Canvas.

**COC workflow from PaperClip:**

```
1. Workflow completes → calls omniwire_coc(action="save", ...)
2. Saved to CyberBase knowledge table with pgvector embedding
3. Mirrored to Obsidian vault as .md file
4. Canvas node created/updated in CyberBase MindMap.canvas
5. All nodes confirmed in one response
```

### Sync coverage — CyberSync 6 AI tools

| Tool | Synced Config |
|------|-------------|
| Claude Code | `~/.claude/settings.json`, CLAUDE.md, memory, agents/ |
| OpenCode | `~/.opencode/config.json`, rules/ |
| OpenClaw | `~/.openclaw/config.json`, skills/, agents/ |
| Codex | `~/.codex/config.json` |
| Gemini | `~/.gemini/settings.json` |
| PaperClip | `~/.paperclip/config.json`, workflows/ |

---

## Links

- **GitHub**: https://github.com/VoidChecksum/omniwire
- **NPM**: https://www.npmjs.com/package/omniwire
- **Issues**: https://github.com/VoidChecksum/omniwire/issues
- **License**: GPL-3.0-only

---

*OmniWire v3.5.0 — 88 tools. Every machine. One agent.*
