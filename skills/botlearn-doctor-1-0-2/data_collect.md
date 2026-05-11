# Data Collection Protocol

> Execute ALL steps below before starting any domain analysis.
> Step 1 (scripts) and Step 2 (file reads) can run in parallel with each other.
> Store every result in working context as `DATA.<key>`.
> On failure: set `DATA.<key> = null` and note the error — never abort the entire collection.

---

## Step 1 — Run Collection Scripts (parallel)

Execute each script via bash, capture JSON from stdout, store in context:

| Context Key | Script | Timeout | What It Collects |
|-------------|--------|---------|-----------------|
| `DATA.status` | `scripts/collect-status.sh` | 25s | **Full instance status**: version, OS, gateway, services, agents, channels, diagnosis, log issues |
| `DATA.env` | `scripts/collect-env.sh` | 15s | OS metrics, memory, disk, CPU, version strings |
| `DATA.config` | `scripts/collect-config.sh` | 15s | Config validation (`openclaw config validate`), sections, agent/gateway/tools settings |
| `DATA.logs` | `scripts/collect-logs.sh` | 20s | Error rate, anomaly spikes, critical events |
| `DATA.skills` | `scripts/collect-skills.sh` | 30s | Installed skills, agent tools, botlearn ecosystem, install capability |
| `DATA.health` | `scripts/collect-health.sh` | 10s | Gateway endpoint reachability, latency |
| `DATA.precheck` | `scripts/collect-precheck.sh` | 30s | `openclaw doctor` built-in self-check results |
| `DATA.channels` | `scripts/collect-channels.sh` | 10s | Channel registration, configuration status |
| `DATA.tools` | `scripts/collect-tools.sh` | 15s | MCP + CLI tool availability |
| `DATA.security` | `scripts/collect-security.sh` | 20s | Credential exposure, permissions, network exposure |
| `DATA.workspace_audit` | `scripts/collect-workspace-audit.sh` | 15s | Storage, config cross-validation, env vars |

**Run openclaw deep diagnostic (parallel with scripts):**
```bash
openclaw doctor --deep --non-interactive 2>&1
```
Store full text output as `DATA.doctor_deep`.

### DATA.status — Key Fields Reference

`collect-status.sh` runs `openclaw status --all --deep` and parses its structured output.
Key fields used across domains:

| Field Path | Example Value | Used In |
|-----------|--------------|---------|
| `status.version` | `"2026.3.2"` | Config, Hardware |
| `status.commit` | `"85377a2"` | Config |
| `status.overview.os` | `"macos 15.7.1 (arm64)"` | Hardware |
| `status.overview.node` | `"24.13.0"` | Hardware |
| `status.overview.tailscale_on` | `false` | Config, Security |
| `status.overview.up_to_date` | `true` | Config |
| `status.overview.update_channel` | `"stable (default)"` | Config |
| `status.overview.gateway.latency_ms` | `17` | Config |
| `status.overview.gateway.auth_type` | `"token"` | Config, Security |
| `status.overview.gateway.bind` | `"loopback"` | Config, Security |
| `status.overview.gateway_service.running` | `true` | Config, Autonomy |
| `status.overview.gateway_service.pid` | `10714` | Autonomy |
| `status.overview.node_service.installed` | `false` | Autonomy |
| `status.overview.agents_overview.total` | `1` | Autonomy |
| `status.overview.agents_overview.active` | `1` | Autonomy |
| `status.agents[].name` | `"main"` | Autonomy |
| `status.agents[].bootstrap_present` | `false` | Autonomy |
| `status.agents[].active_since` | `"1m ago"` | Autonomy |
| `status.channels[]` | `[{name, enabled, state}]` | Config |
| `status.diagnosis.config_valid` | `true` | Config |
| `status.diagnosis.skills_eligible` | `9` | Skills |
| `status.diagnosis.skills_missing` | `0` | Skills |
| `status.diagnosis.port_conflicts` | `[]` | Config |
| `status.log_issues[]` | `["LLM request timed out", ...]` | Autonomy |

---

## Step 2 — Direct File Reads (parallel)

Read these files directly and store content in context. Each read is independent.

### 2.1 Main Config File

```bash
cat "${OPENCLAW_HOME:-$HOME/.openclaw}/openclaw.json" 2>/dev/null
# Fallback: also try $HOME/.openclaw/config/openclaw.json
```
Store raw JSON content as `DATA.openclaw_json`.
Purpose: cross-validate against `DATA.config` script output; catch any unusual overrides.

---

### 2.2 Scheduled Tasks (Cron)

```bash
CRON_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/cron"
ls "$CRON_DIR" 2>/dev/null                    # list task files
cat "$CRON_DIR"/*.json 2>/dev/null            # read all task definitions
```
Store as `DATA.cron`: `{ files: [...], tasks: [...parsed JSON content...] }`.
If directory missing: `DATA.cron = { files: [], tasks: [], missing: true }`.

---

### 2.3 Authenticated Devices (Identity)

```bash
IDENTITY_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/identity"
ls -la "$IDENTITY_DIR" 2>/dev/null
```
Store **directory listing only** (filenames, sizes, permissions) as `DATA.identity`.
**Do NOT read file contents** — device credentials must never enter context.

---

### 2.4 Gateway Error Log (last 200 lines)

```bash
tail -200 "${OPENCLAW_HOME:-$HOME/.openclaw}/logs/gateway.err.log" 2>/dev/null
```
Store as `DATA.gateway_err_log`.
**Before storing:** redact any line matching patterns: `api[_-]?key`, `token`, `secret`, `password`, `private[_-]?key`.
Replace matched values with `[REDACTED]`.

---

### 2.5 Memory Directory Stats

```bash
MEMORY_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/memory"

# File count
find "$MEMORY_DIR" -type f 2>/dev/null | wc -l

# Total size
du -sh "$MEMORY_DIR" 2>/dev/null | awk '{print $1}'

# File type breakdown (by extension)
find "$MEMORY_DIR" -type f 2>/dev/null \
  | sed 's/.*\.//' | sort | uniq -c | sort -rn
```
Store as `DATA.memory_stats`:
```json
{
  "total_files": <number>,
  "total_size": "<human-readable>",
  "type_breakdown": [
    { "ext": "md", "count": 42 },
    { "ext": "json", "count": 18 }
  ],
  "missing": false
}
```

---

### 2.6 Workspace Heartbeat

```bash
cat "${OPENCLAW_HOME:-$HOME/.openclaw}/workspace/HEARTBEAT.md" 2>/dev/null
```
Store full content as `DATA.heartbeat`.
If file missing: `DATA.heartbeat = null`.

---

### 2.7 Workspace Identity Files

Read the agent's core identity and configuration files from the workspace directory.
These define who the agent is, who the user is, and what tools the agent has access to.

```bash
WORKSPACE_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/workspace"

for file in agent.md soul.md user.md identity.md tool.md; do
  echo "=== $file ==="
  cat "$WORKSPACE_DIR/$file" 2>/dev/null || echo "[MISSING]"
  echo "=== END ==="
done
```

Store as `DATA.workspace_identity`:
```json
{
  "agent_md":    { "exists": true,  "word_count": 350, "content": "..." },
  "soul_md":     { "exists": true,  "word_count": 120, "content": "..." },
  "user_md":     { "exists": false, "word_count": 0,   "content": null },
  "identity_md": { "exists": true,  "word_count": 85,  "content": "..." },
  "tool_md":     { "exists": false, "word_count": 0,   "content": null }
}
```

**Privacy rule:** Treat content as potentially personal. When analyzing, extract structural signals
(word count, section headings present/absent, key term presence) — do NOT echo raw content verbatim
in the final report. Summarize findings only.

---

## Step 3 — Merge Confirmation

After all steps complete, internally confirm:

1. List which `DATA.*` keys are populated vs. null
2. For each null key, note the failure reason (file not found / script error / timeout)
3. Proceed to domain analysis — null data means that aspect cannot be scored, not that collection failed

**Do not report Step 3 details to the user unless asked.** Proceed silently to Phase 2.
