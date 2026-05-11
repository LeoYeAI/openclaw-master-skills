# Setup & Prerequisites

> Read this on first activation or when the OpenClaw environment is unverified.
> Execute checks sequentially. Abort and report to the user if any REQUIRED check fails.
> This is a lightweight guard — re-run on every invocation (no persistent marker written).

---

## Step 1 — Required Binaries

Run each command and capture output:

| Binary | Check Command | Requirement |
|--------|--------------|-------------|
| `node` | `node --version` | ✅ Required — must be ≥ 18.0.0 |
| `bash` | `bash --version` | ✅ Required |
| `curl` | `curl --version` | ✅ Required |
| `openclaw` | `openclaw --version` | ✅ At least one of these two |
| `clawhub` | `clawhub --version` | ✅ At least one of these two |
| `jq` | `jq --version` | ⚠️ Optional — enhances JSON parsing speed |

**Failure conditions — halt immediately and report:**
- `node` missing or version < 18.0.0
- Neither `openclaw` nor `clawhub` found in PATH

**Report format on failure:**
```
❌ Setup Failed: [binary] is missing or incompatible.
  Required: [requirement]
  Found: [actual value or "not found"]
  Fix: [install command for darwin/linux]
```

---

## Step 2 — OpenClaw Home Detection

Resolve `OPENCLAW_HOME` in order:

```bash
# Priority order:
1. $OPENCLAW_HOME environment variable (if set)
2. $HOME/.openclaw (default)
```

Verify the directory exists:
```bash
[ -d "$OPENCLAW_HOME" ] || WARN "OPENCLAW_HOME not found at $OPENCLAW_HOME"
```

If not found: proceed with warning — some data sources will return null.

---

## Step 3 — Expected Directory Structure

Check presence of each subdirectory under `$OPENCLAW_HOME`:

| Directory | Purpose | Required |
|-----------|---------|---------|
| `config/` | openclaw.json and channel configs | ✅ Required |
| `logs/` | gateway.err.log and other logs | ✅ Required |
| `skills/` | Installed skill packages | ✅ Required |
| `memory/` | Agent memory files | ⚠️ Expected |
| `workspace/` | HEARTBEAT.md and active task files | ⚠️ Expected |
| `cron/` | Scheduled task definitions (*.json) | ⚠️ Expected |
| `identity/` | Authenticated device credentials | ⚠️ Expected |

Missing ⚠️ directories: note as findings in Domain 5 (Autonomous Intelligence) — do not abort.
Missing ✅ directories: include as ❌ finding in Domain 2 (Configuration Health).

---

## Step 4 — Environment Variables Audit

Check these variables and note their effective values:

| Variable | Default | Notes |
|----------|---------|-------|
| `OPENCLAW_HOME` | `$HOME/.openclaw` | Override of base directory |
| `OPENCLAW_CONFIG_PATH` | `$OPENCLAW_HOME/openclaw.json` | If set, must point to valid file |
| `OPENCLAW_STATE_DIR` | `$OPENCLAW_HOME` | Alternate state directory |
| `OPENCLAW_LOG_DIR` | `$OPENCLAW_HOME/logs` | Log output path |
| `OPENCLAW_SKILLS_DIR` | `$OPENCLAW_HOME/skills` | Installed skills path |

**Conflict check:** If `OPENCLAW_CONFIG_PATH` is set but points outside `OPENCLAW_HOME`, flag as ⚠️.

---

## Step 5 — Readiness Confirmation

After all checks complete, output a readiness confirmation to the user in REPORT_LANG.
The message must convey: environment verified, OpenClaw home path, Node.js version,
CLI version (openclaw or clawhub), count of directories found, and that data collection is starting.

Example structure (translate all labels to REPORT_LANG):
```
✅ [Environment verified — in REPORT_LANG]
  OpenClaw home: /path/to/.openclaw
  Runtime: node vXX.XX.XX
  CLI: openclaw vX.X.X (or clawhub vX.X.X)
  Directories: X/7 present
[Proceeding to data collection — in REPORT_LANG]
```

---

## Safety Notice

- This skill is **read-only** during the collection phase.
- Fix operations always require explicit user confirmation before execution.
- Credential values are **never** printed — type and file path only.
- No outbound network requests are made outside the local OpenClaw gateway.
- All destructive operations (e.g., `rm`, `chmod`) include rollback commands.
