---
name: oc-doctor
description: >
  Runs a comprehensive 11-section health check on local OpenClaw installations.
  Diagnoses configuration errors, session bloat, model drift, cron issues, security
  misconfigurations, gateway problems, and system instruction token budget.
  Generates a structured report with CRITICAL/WARNING/INFO findings and offers
  interactive one-click fixes. Use when: "openclaw doctor", "claw doctor",
  "claw health check", "openclaw diagnose", or troubleshooting OpenClaw.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - openclaw
        - jq
    emoji: "stethoscope"
    homepage: https://github.com/bryant24hao/oc-doctor
    os:
      - macos
      - linux
---

# OpenClaw Doctor

Comprehensive health check for OpenClaw installations. Outputs a structured diagnostic report with severity levels and actionable fixes.

## Language

Respond in the same language the user used to invoke this skill. If invoked via slash command with no additional text, infer the preferred language from context: check recent conversation history, workspace file content (e.g., CJK content in AGENTS.md or cron job payloads), and system locale. Fall back to English only if no language signal is found.

## Prerequisites

```bash
command -v openclaw >/dev/null || echo "CRITICAL: openclaw not found in PATH"
command -v jq >/dev/null || echo "CRITICAL: jq not found — install with: brew install jq (macOS) or apt install jq (Linux)"
```

## Paths

Auto-detect all paths at runtime. Do NOT hardcode platform-specific locations.

```bash
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OPENCLAW_CONFIG="$OPENCLAW_HOME/openclaw.json"
OPENCLAW_DIST=""
if command -v openclaw &>/dev/null; then
  OPENCLAW_DIST="$(dirname "$(readlink -f "$(command -v openclaw)")")/../lib/node_modules/openclaw/dist"
  [ -d "$OPENCLAW_DIST" ] || OPENCLAW_DIST=""
fi
SESSIONS_DIR="$OPENCLAW_HOME/agents/main/sessions"
SESSIONS_INDEX="$SESSIONS_DIR/sessions.json"
MODELS_JSON="$OPENCLAW_HOME/agents/main/agent/models.json"
WORKSPACE_GLOB="$OPENCLAW_HOME/workspace-*"
LOGS_DIR="$OPENCLAW_HOME/logs"
BROWSER_CACHE="$OPENCLAW_HOME/browser"
CRON_DIR="$OPENCLAW_HOME/cron"
```

If any path doesn't exist, note it and skip that check section.

## Diagnostic Sections

Run ALL sections below sequentially. For each finding, assign a severity:
- `CRITICAL` — broken functionality, data loss risk
- `WARNING` — suboptimal config, potential issues
- `INFO` — informational, optimization opportunity

### 1. Installation & Version

Use the built-in status command as the primary data source:

```bash
openclaw status --all 2>&1
openclaw --version 2>/dev/null
```

Report: version, gateway running status, LaunchAgent status, channel health.

### 2. Config Consistency

Read `$OPENCLAW_CONFIG` and check:

1. **Default model validity**: Is `agents.defaults.model.primary` a known model? Cross-check with `agents.defaults.models` entries.
2. **Fallback models**: Are all models in `agents.defaults.model.fallbacks` defined in the models list?
3. **Legacy config files**: Check if `clawdbot.json` or other legacy files exist in `$OPENCLAW_HOME/`.
4. **Backup file accumulation**: Count `*.bak*` files in `$OPENCLAW_HOME/`. More than 2 is WARNING.
5. **Channel config**:
   - Telegram: Check `requireMention` setting per group. `false` = WARNING (bot responds to all messages).
   - Feishu: Check `groupPolicy`. `"open"` = WARNING (any group can interact).

### 3. Session Maintenance Config

Check `openclaw.json` for `session.maintenance` settings:

1. **Maintenance mode**: Missing or `"warn"` = WARNING (stale sessions accumulate without cleanup). Should be `"enforce"`.
2. **pruneAfter**: Missing or > 30d = INFO. Recommended: `"7d"` to `"14d"`.
3. **maxEntries**: Missing or > 200 = INFO. Default is 500, reasonable personal value is 50-100.
4. **maxDiskBytes**: Missing = INFO. Recommended: set a cap like `"100mb"`.

### 4. Compaction Config

Check `agents.defaults.compaction` in `openclaw.json`:

1. **mode**: Should be `"safeguard"` (default, safe). Note if missing.
2. **reserveTokensFloor**: Missing = WARNING. Without this buffer, context can overflow before compaction triggers. Recommended: `20000`.
3. **keepRecentTokens**: Missing = INFO. Controls how much recent conversation is preserved verbatim during compaction. Recommended: `8000`.

### 5. Model Alignment

Use the built-in sessions list, then cross-reference with config:

```bash
openclaw sessions 2>&1
```

Also read `sessions.json` programmatically to check:

1. **Session model drift**: List any sessions whose `model` field differs from the configured default. Particularly check channel sessions (telegram:*, feishu:*).
2. **contextTokens vs model contextWindow**: Compare each session's `contextTokens` against its model's actual `contextWindow` (from `models.json` or built-in registry). Mismatch = WARNING (e.g., 272k contextTokens on a 200k model can cause overflow).
3. **Forward-compat patches**: Check if dist files have been locally patched by searching for non-standard constants (e.g. model IDs not in the official `XHIGH_MODEL_REFS` or custom `resolveForwardCompatModel` additions) in `$OPENCLAW_DIST/*.js`.
4. **Thinking config**: Read the thinking config file (find via `grep -rl "XHIGH_MODEL_REFS" $OPENCLAW_DIST/`) and verify the current default model is included in `XHIGH_MODEL_REFS` if it should support xhigh thinking.
5. **models.json override**: Read `$MODELS_JSON` and check if inline model definitions are consistent with `openclaw.json`.

### 6. Session Health

Use the built-in cleanup dry-run as primary data source:

```bash
openclaw sessions cleanup --dry-run --fix-missing 2>&1
```

Then supplement with filesystem checks:

1. **Orphan JSONL files**: Files in directory but not referenced in `sessions.json`. Calculate total size.
2. **Zombie session entries**: Entries in `sessions.json` pointing to non-existent JSONL files.
3. **Empty JSONL files**: Referenced files that are 0 bytes.
4. **Deleted file accumulation**: `*.deleted.*` files that can be cleaned up. Calculate total size.
5. **Cron session accumulation**: Count sessions with `:cron:` in their key. Separate parent jobs from `:run:` sub-sessions. Large numbers (>20) indicate cleanup isn't working.

### 7. Cron Health

Read `$CRON_DIR/jobs.json` and check:

1. **Duplicate enabled jobs**: Jobs with identical `name` + `schedule` + `enabled: true`. Flag as WARNING with dedup suggestion.
2. **Disabled job accumulation**: Count `enabled: false` jobs. More than 10 = INFO (suggest cleanup if user confirms they're not needed).
3. **Tmp file accumulation**: Count `jobs.json.*.tmp` files in `$CRON_DIR`. These are abandoned atomic-write artifacts. Any count > 0 with no process holding them open (`lsof`) = safe to delete.
4. **Cron runs directory**: Check `$CRON_DIR/runs/` for accumulated run logs. Count and total size.
5. **Stale enabled jobs**: Enabled jobs whose `state.lastRunAtMs` is older than expected based on their schedule (e.g., a daily job that hasn't run in 3+ days).

### 8. Security Audit

Check `openclaw.json` for:

1. **Feishu groupPolicy**: `"open"` means any Feishu group can interact = CRITICAL.
2. **Feishu/Telegram allowFrom**: `["*"]` means no restriction = WARNING.
3. **Telegram requireMention**: `false` on groups = WARNING (bot responds to every message).
4. **Gateway auth mode**: Read `gateway.auth.mode` from config. `"token"` is good, `"none"` = CRITICAL.
5. **Exposed secrets in non-gitignored files**: Check if `$OPENCLAW_HOME/` contains any files that might be accidentally synced (e.g., check for `.git` directory in `$OPENCLAW_HOME/`).
6. **API keys in models.json**: Note if API keys are stored in plaintext in `models.json` (this is expected but worth noting).

### 9. Resource Usage

```bash
du -sh $OPENCLAW_HOME/browser/ 2>/dev/null    # Browser cache
du -sh $OPENCLAW_HOME/logs/ 2>/dev/null       # Logs
du -sh $SESSIONS_DIR/ 2>/dev/null             # Sessions
du -sh $OPENCLAW_HOME/media/ 2>/dev/null      # Media files
du -sh $OPENCLAW_HOME/memory/ 2>/dev/null     # Memory files
du -sh $CRON_DIR/ 2>/dev/null                 # Cron data
du -sh $OPENCLAW_HOME/ 2>/dev/null            # Total

# Log file sizes
ls -lhS $LOGS_DIR/ 2>/dev/null

# Large JSONL sessions (top 5)
ls -lhS $SESSIONS_DIR/*.jsonl 2>/dev/null | head -5
```

Flag:
- Browser cache > 200MB = WARNING
- Logs > 50MB = WARNING
- Any single JSONL > 10MB = INFO
- Total `$OPENCLAW_HOME/` > 1GB = WARNING

### 10. Gateway & Process Health

Read `gateway.port` from `openclaw.json` to determine the correct port (do NOT hardcode).

```bash
# Check for stuck/zombie openclaw processes
ps aux | grep -E "openclaw-gateway|openclaw " | grep -v grep

# Check gateway port binding (use port from config)
lsof -i :<port> 2>/dev/null | head -5

# Check gateway error log for recent errors
tail -20 $LOGS_DIR/gateway.err.log 2>/dev/null
```

Flag:
- Multiple gateway processes = CRITICAL
- Gateway not listening on configured port = CRITICAL
- Recent errors in gateway.err.log = WARNING (show last 5 errors)

### 11. System Instruction Health

Measures static system instruction token footprint. Complements Section 5 (runtime session pressure) — together they form the **Context Budget** picture.

#### Step A: Data Collection (deterministic script)

Locate and run the bundled collector script from the skill directory:

```bash
# Find the skill directory (works whether installed via skills.sh, clawhub, or manually)
SKILL_DIR="$(find ~/.claude/skills ~/.agents/skills -maxdepth 3 -name 'sysinstruction-check.sh' -path '*/oc-doctor/*' 2>/dev/null | head -1 | xargs dirname)"
bash "$SKILL_DIR/sysinstruction-check.sh"
```

The script auto-detects workspace directories and outputs structured JSON. See [scripts/sysinstruction-check.sh](scripts/sysinstruction-check.sh) for details.

Output schema:
```json
{
  "workspace_files": [
    {"file": "workspace-name/FILE.md", "chars": 0, "lines": 0, "est_tokens": 0, "is_empty_template": false}
  ],
  "total_est_tokens": 0,
  "largest_file": "AGENTS.md",
  "empty_template_files": [],
  "tool_bloat_files": [],
  "tool_bloat_est_tokens": 0,
  "bootstrap_still_present": false,
  "context_window": 200000,
  "context_window_source": "models.json | default_fallback",
  "pct_of_context": "0.0"
}
```

#### Step B: LLM Analysis

Analyze the JSON output along these dimensions:

1. **Context budget ratio** (complements Section 5's runtime check):
   - `pct_of_context < 2%` = `INFO` healthy
   - `2-5%` = `INFO` acceptable but worth reviewing
   - `5-10%` = `WARNING` consider trimming
   - `10-15%` = `WARNING` (strong) actively optimize
   - `> 15%` = `CRITICAL` only if paired with runtime truncation evidence
   - If `context_window_source` is `"default_fallback"`, note that thresholds may be inaccurate

2. **Tool description bloat**:
   - `tool_bloat_files` non-empty = `WARNING`, list files and estimated token cost
   - These are auto-injected by OpenClaw (e.g., Feishu bitable tools) — check if all are necessary

3. **Reclaimable space** (read `empty_template_files` and `bootstrap_still_present`):
   - `bootstrap_still_present = true` = `INFO`, can be deleted after initial setup
   - `empty_template_files` non-empty = `INFO`, list files and estimated token savings

4. **Per-file analysis**:
   - Single file > 40% of total tokens = `WARNING`, consider splitting
   - Single file > 2% of context window = `WARNING`, review individually
   - AGENTS.md is typically the largest (memory/group-chat/heartbeat rules), but > 5000 tokens warrants review

5. **Benchmarks** (dynamic, based on actual context window):
   ```
   Healthy:        < 2% of context_window
   Needs review:   2-5% of context_window
   Needs optimization: > 5% of context_window
   ```

6. **Cross-reference integrity**:
   - Scan the largest workspace file (typically AGENTS.md) for references to other `.md` filenames (e.g., `HEARTBEAT.md`, `BOOTSTRAP.md`, `MEMORY.md`).
   - For each referenced file: check if it exists in any `workspace-*/ directory` and whether it is an empty template.
   - Referenced but missing = `WARNING` — the agent has instructions that depend on a file that doesn't exist. Offer to generate a practical version based on the user's actual config (cron jobs, channels, heartbeat rules in AGENTS.md).
   - Referenced but empty template = `WARNING` — the file exists but has no real content, so the agent's instructions referencing it are ineffective. Offer to populate it with useful content or remove the dead reference.

#### Output (integrated into main report)

Add a System Instruction section to Findings:

```
### [SEVERITY] System Instruction Token Usage

| File | Lines | Chars | ~Tokens | % of Context |
|------|-------|-------|---------|--------------|
| AGENTS.md | N | N | N | N% |
| SOUL.md | N | N | N | N% |
| ... | ... | ... | ... | ... |
| **Total** | **N** | **N** | **N** | **N%** |

- Status: Healthy / Elevated / Needs Optimization
- Suggestions: (specific optimization actions, if any)
```

## Output Format

Present results as a structured diagnostic report:

```
# OpenClaw Doctor Report

## Summary
- Version: x.x.x
- Gateway: running/stopped
- Overall Health: HEALTHY / NEEDS ATTENTION / CRITICAL

## Findings

### [SEVERITY] Finding Title
- Description: ...
- Impact: ...
- Fix: (specific command or config change)

(repeat for each finding)

## Quick Stats
| Metric | Value |
|---|---|
| Active sessions | N |
| Cron jobs (enabled/disabled) | N / N |
| Orphan files | N (size) |
| Browser cache | size |
| Total disk usage | size |

## Recommended Actions
1. (prioritized list of suggested fixes)
```

## Interactive Mode

After presenting the report, ask the user (in their language):
> "Would you like me to fix these issues? I can address them one by one, or batch-fix all WARNING-level and below. CRITICAL issues will be confirmed individually."

For fixes:
- **Orphan/deleted files**: Offer to delete with size summary.
- **Model drift / contextTokens mismatch**: Offer to align all sessions to default model and correct contextWindow.
- **Config issues**: Show the specific config change needed, confirm before applying.
- **Cron dedup / tmp cleanup**: Show what will be removed, confirm before applying.
- **Maintenance config**: Suggest optimal values, confirm before applying.
- **Resource cleanup**: Offer to clear browser cache, rotate logs.
- **Security issues**: Show the config change and explain the tradeoff before applying.
- **System instruction bloat**: Offer to archive BOOTSTRAP.md (rename to `.bak`), clean empty template files, flag tool description injection.
- **Referenced but missing/empty workspace files**: Generate a practical version based on the user's actual config. For HEARTBEAT.md specifically, analyze cron jobs, channels, and heartbeat rules in AGENTS.md to produce a useful checklist (not an empty template).

## Secret Redaction (MANDATORY)

When displaying config excerpts in the report, **always redact sensitive values**:
- API keys / tokens: show only first 8 chars + `...` (e.g., `8263689670:A...`)
- Passwords / secrets: show `***REDACTED***`
- Never include full botToken, appSecret, auth token, or API key values in the report output.

## Security & Privacy

This skill operates locally and makes no network requests. However, diagnostic output becomes part of the LLM conversation context.

**Files read** (read-only unless user approves a fix):
- `$OPENCLAW_HOME/openclaw.json` — main config
- `$OPENCLAW_HOME/agents/main/agent/models.json` — model definitions
- `$OPENCLAW_HOME/agents/main/sessions/sessions.json` — session index
- `$OPENCLAW_HOME/workspace-*/*.md` — system instruction files
- `$OPENCLAW_HOME/cron/jobs.json` — cron job definitions
- `$OPENCLAW_HOME/logs/gateway.err.log` — recent gateway errors
- `$OPENCLAW_DIST/*.js` — installed dist files (for patch detection)

**Files modified** (only with explicit user confirmation):
- Session JSONL files (orphan cleanup)
- Config JSON files (optimization)
- Workspace `.md` files (BOOTSTRAP.md archival)
- Cron tmp files (cleanup)

**Environment variables read**: `OPENCLAW_HOME` (optional override).

**No secrets are transmitted or logged.** The skill may display config excerpts in the diagnostic report shown to the user.
