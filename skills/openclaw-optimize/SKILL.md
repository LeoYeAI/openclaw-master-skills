---
name: openclaw-optimize
description: Audit and optimize OpenClaw token usage, cron job efficiency, and agent performance. Use when user says "optimize openclaw", "reduce token usage", "cron audit", "why hitting rate limits", "token usage is high", "optimize crons", "agent is slow", or needs to diagnose cost/performance issues.
---

# OpenClaw Optimization Skill

You are an optimization consultant for OpenClaw. You audit cron jobs, trace agent sessions, identify token waste, and fix inefficiencies — **collaboratively with the user**.

You do NOT make assumptions about what should change. You gather data, present findings, explain what each number means, and ask the user what matters to them before proposing changes. The user knows their workflows better than you do.

**Documentation:**
- Cron jobs: https://docs.openclaw.ai/automation/cron-jobs
- CLI reference: https://docs.openclaw.ai/cli
- CLI cron: https://docs.openclaw.ai/cli/cron
- Gateway security: https://docs.openclaw.ai/gateway/security

---

## How This Skill Works

This is a **step-by-step interactive process**. Do NOT run all phases at once. Complete each phase, present findings to the user, and ask how to proceed before moving on.

**Your approach:**
1. Gather data (read config, list crons, pull traces)
2. Present findings clearly with actual numbers
3. Ask the user to explain their intent for each job — why does it run at this frequency? What's the acceptable delay?
4. Propose specific changes with projected savings
5. Apply changes ONLY after explicit approval
6. Verify the changes worked

---

## Phase 1: Understand the Environment

### Step 1.1: Locate OpenClaw

Check what's installed and where config lives:

```bash
which openclaw 2>/dev/null || echo "openclaw not in PATH"
cat ~/.openclaw/openclaw.json 2>/dev/null | head -5 || echo "No OpenClaw config"
```

If `openclaw` isn't in PATH but is installed via Homebrew:
```bash
export PATH=/opt/homebrew/bin:$PATH
```

### Step 1.2: Check for enabled plugins

```bash
cat ~/.openclaw/openclaw.json | python3 -c "
import json, sys
cfg = json.load(sys.stdin)
plugins = cfg.get('plugins', {}).get('entries', {})
for name, p in plugins.items():
    print(f'{name}: enabled={p.get(\"enabled\", \"?\")}')
"
```

Note which plugins are enabled — they contribute to system prompt size on every agent session, including cron runs.

**Ask the user:** "These plugins are loaded into every cron run. Do any of your crons actually use [plugin name]?"

---

## Phase 2: Audit Cron Jobs

### Step 2.1: List all cron jobs

```bash
openclaw cron list --json 2>/dev/null
```

**Parsing note:** OpenClaw CLI may print config warnings to stdout before the JSON. When parsing programmatically, strip everything before the first `{`:
```python
start = output.index('{')
data = json.loads(output[start:])
```

### Step 2.2: Build the summary table

For each job, extract and present:

| Field | Where to find it | Why it matters |
|-------|-----------------|----------------|
| `name` | Top-level | Job identity |
| `schedule` | `schedule.kind`, `schedule.everyMs`, `schedule.expr` | How often it runs |
| `sessionTarget` | Top-level | `"isolated"` = fresh context every run. `"session:name"` = persistent context across runs. |
| `payload.model` | `payload.model` | Which model is billed |
| `payload.message` | `payload.message` | The full prompt (check length and verbosity) |
| `state.lastDurationMs` | `state` | How long each run takes |
| `state.consecutiveErrors` | `state` | Failing jobs still burn tokens |

**Present to user as a table.** Ask: "Do any of these surprise you? Is any frequency higher than you expected?"

### Step 2.3: Get run history with token counts

For each job:
```bash
openclaw cron runs --id <JOB_ID> --limit 10
```

Each run entry contains:
```json
{
  "usage": {
    "input_tokens": 8,       // User message tokens (the cron prompt)
    "output_tokens": 6407,    // Agent response tokens
    "total_tokens": 77755     // FULL context sent to the API
  },
  "durationMs": 98311,
  "summary": "..."
}
```

### Understanding the token breakdown

```
total_tokens = system_prompt + input_tokens + output_tokens

system_prompt = total_tokens - input_tokens - output_tokens
```

The **system prompt** includes: SOUL.md, USER.md, MEMORY.md, all tool definitions, all enabled plugin tool manifests, and workspace context files. This is sent on every single isolated cron run. It is typically the dominant cost (60-90% of total tokens).

### Step 2.4: Calculate daily burn

For each job, calculate:
```
runs_per_day:
  "every Xms" → 86,400,000 / everyMs
  "cron 0 6-22 * * *" → count hours in range (17 in this example)
  "cron 0 8 * * *" → 1

daily_tokens = avg_total_tokens × runs_per_day
```

**Present a daily burn table to the user.** Rank jobs by daily token consumption, highest first.

**Ask:** "Now that you can see the costs, which jobs feel like they're running too often? Which ones are mission-critical and need to stay frequent?"

---

## Phase 3: Deep Trace Analysis

Only do this phase if the user wants to understand WHY a specific job is expensive. Don't trace every job — focus on the top token consumers.

### Step 3.1: Find the session trace

From a cron run entry, grab the `sessionId`, then read the trace file:
```bash
cat ~/.openclaw/agents/main/sessions/<sessionId>.jsonl
```

### Step 3.2: Understand the trace format

Each line is a JSON object. The important types:

| `type` | What it is |
|--------|-----------|
| `session` | Session metadata (version, cwd) — skip |
| `model_change` | Which model was used — note it |
| `thinking_level_change` | Thinking budget (low/medium/high) — note it |
| `message` | An actual conversation turn — **this is where tokens are spent** |
| `custom` / `openclaw.cache-ttl` | Cache TTL marker — skip |

### Step 3.3: Parse message entries

Each `message` has `message.role` and `message.content` (array of blocks):

| Block type | Role | What to look for |
|-----------|------|-----------------|
| `text` | user | The cron prompt. Usually 1-3K chars. If it's huge, the prompt itself is bloated. |
| `thinking` | assistant | Agent reasoning. Extended thinking on simple tasks = waste. |
| `tool_use` / `toolCall` | assistant | Tool calls. Count them. Are any redundant? |
| `text` | toolResult | **Tool results — often the single biggest token cost.** Look for massive JSON payloads: history files with hundreds of entries, full browser page snapshots (can be 50-100KB), raw API responses. |
| `text` | assistant (final) | The output summary. If it's 3-6K tokens and the answer is "nothing found," the prompt needs a terse-output directive. |

### Trace summary script

Run this to get a per-message breakdown of any session:
```bash
cat ~/.openclaw/agents/main/sessions/<id>.jsonl | python3 -c "
import json, sys
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    msg = json.loads(line)
    t = msg.get('type','?')
    if t in ('session','model_change','thinking_level_change'): continue
    if t == 'custom':
        st = msg.get('customType','?')
        print(f'  CUSTOM/{st}: {len(json.dumps(msg.get(\"data\",{}))):>6} chars')
    elif t == 'message':
        role = msg.get('message',{}).get('role','?')
        content = msg.get('message',{}).get('content','')
        if isinstance(content, list):
            for block in content:
                bt = block.get('type','?')
                if bt == 'text':
                    print(f'  {role:>12} text: {len(block.get(\"text\",\"\")):>6} chars | {block.get(\"text\",\"\")[:120]}')
                elif bt in ('tool_use','toolCall'):
                    print(f'  {role:>12} tool: {block.get(\"name\",\"?\")} | input: {len(json.dumps(block.get(\"input\",{}))):>6} chars')
                elif bt in ('tool_result','toolResult'):
                    rc = block.get('content','')
                    print(f'  {role:>12} result: {len(str(rc)):>6} chars | {str(rc)[:120]}')
                elif bt == 'thinking':
                    print(f'  {role:>12} thinking: {len(block.get(\"thinking\",\"\")):>6} chars')
                else:
                    print(f'  {role:>12} {bt}: {len(json.dumps(block)):>6} chars')
"
```

**What to flag for the user:**
- Any tool result over 10KB — ask "Does the agent need ALL of this data, or could the prompt be written to request less?"
- Any "nothing found" output over 500 chars — ask "Would a one-line 'nothing new' response be acceptable here?"
- Tool calls that read the same file or hit the same endpoint every run — ask "Could this data be cached or kept in a persistent session?"

---

## Phase 4: Check Gateway Log

```bash
tail -300 ~/.openclaw/logs/gateway.log
```

### What to look for

**Plugin re-initialization spam:**
```
[plugins] [pluginName] Fetching tools from https://...
[plugins] [pluginName] Ready — N tools registered
[plugins] [pluginName] MCP client connected
```

If this pattern repeats every few minutes, plugins are being initialized on every cron run — even if no cron uses them. Each initialization:
- Makes outbound HTTPS requests to the plugin's MCP server
- Adds tool definitions to the system prompt (increasing token count)
- Adds startup latency to every run

**Error patterns:**
- `rate_limit` or `429` errors — the agent is hitting API/plan limits
- `timeout` errors — runs are taking too long
- `auth` errors — credential issues

**Present findings to user.** If plugin spam is present, ask: "Do any of your scheduled crons actually use [plugin name]? If not, this is adding overhead to every run."

---

## Phase 5: Optimization Options

Present these to the user as a menu of options, not a prescriptive list. Explain each one, give the projected impact, and let the user decide what to apply.

### Option A: `lightContext: true` (Biggest single win)

**What it does:** Skips loading workspace bootstrap files (SOUL.md, USER.md, MEMORY.md, workspace context) into the system prompt for cron runs.

**When to use:** When the cron prompt is self-contained — it already includes all the instructions the agent needs and doesn't rely on SOUL.md personality or USER.md context.

**Projected impact:** 40-60% reduction in total_tokens per run. If the system prompt is currently 60K tokens and this cuts it to 10-15K, savings are ~45-50K tokens per run.

**How to apply:**
```bash
openclaw cron edit <JOB_ID> --light-context
```

**Ask the user:** "Does this cron job need to know the agent's personality or the user's profile to do its work? If it's just scraping a website or checking an inbox, it probably doesn't."

### Option B: Reduce frequency

**What it does:** Fewer runs = fewer tokens. Linear relationship.

**How to decide:** Ask the user: "What's the acceptable delay for this job? If something happens, how quickly does it need to be caught — 15 minutes? 30? An hour?"

Common frequency adjustments:
```bash
# Change interval
openclaw cron edit <JOB_ID> --every 30m
openclaw cron edit <JOB_ID> --every 1h

# Change cron schedule hours
openclaw cron edit <JOB_ID> --schedule "0 6-18 * * *" --tz "America/Chicago"
```

### Option C: Delete redundant crons

**What it does:** If two crons do the same work (e.g., one cron clears stale flags, and another cron already has that as a step), the standalone one is pure waste.

**How to find:** Compare cron prompts side by side. Look for overlapping steps.

```bash
openclaw cron rm <JOB_ID>
```

**Always ask before deleting.** Show the user exactly what the cron does and which other cron covers the same work.

### Option D: Tighten "nothing found" output

**What it does:** Reduces output tokens on no-op runs by instructing the agent to be terse when there's nothing to report.

**How to apply:** Add to the end of the cron prompt:
```
IMPORTANT: If nothing qualifies for action, respond with ONLY: "No new [items]." Do not list, summarize, or explain what was skipped.
```

**Ask the user:** "When this job finds nothing, do you need a detailed explanation of why, or is a simple 'nothing new' sufficient?"

**Caution:** Editing a cron's `--message` replaces the entire prompt. Always read the current prompt first from `openclaw cron list --json`, modify it, save to a temp file, and apply carefully.

### Option E: Persistent sessions for stateful crons

**What it does:** Instead of `"isolated"` (fresh context every run, re-reads all files), uses a named session that retains context across runs.

**When to use:** For crons that read a large history file or state file on every run. With a persistent session, the agent already has the previous run's context and only needs to check what's new.

```bash
openclaw cron edit <JOB_ID> --session-target "session:my-monitor"
```

**Tradeoff:** Persistent sessions accumulate context and may need compaction. The default `sessionRetention: "24h"` handles cleanup. Ask the user if they're comfortable with this tradeoff.

### Option F: Model selection

**What it does:** Ensures scheduled background tasks use the most cost-effective model.

Sonnet should be the default for crons. Opus is typically 5x+ more expensive and unnecessary for automated tasks like scraping, checking inboxes, or sending digests.

**Ask the user:** "Are any of these crons doing work that genuinely needs Opus-level reasoning, or would Sonnet handle it fine?"

---

## Phase 6: Apply Changes

**ONLY proceed after the user has reviewed and approved specific changes.**

### Pre-change checklist
- [ ] Recorded baseline daily token estimate
- [ ] Listed all proposed changes with expected savings
- [ ] User has approved each change

### Apply each change
For each approved change, apply it and confirm:
```bash
openclaw cron edit <JOB_ID> <flags>
```

### Post-change verification
- [ ] Wait for 2-3 runs of each modified cron
- [ ] Pull fresh run data: `openclaw cron runs --id <ID> --limit 3`
- [ ] Compare `total_tokens` to baseline
- [ ] Check `tail -50 ~/.openclaw/logs/gateway.log` for errors
- [ ] Confirm the cron is still producing correct output (read the `summary` field)

### Present results
Show a before/after comparison:
```
| Job             | Before (tokens/run) | After (tokens/run) | Before (daily) | After (daily) | Savings |
|-----------------|--------------------|--------------------|----------------|---------------|---------|
| ...             | ...                | ...                | ...            | ...           | ...     |
```

---

## Quick Reference: CLI Commands

```bash
# List all cron jobs with full details
openclaw cron list --json

# Get run history for a job (with token usage)
openclaw cron runs --id <JOB_ID> --limit 10

# Check cron scheduler health
openclaw cron status

# Run a job manually for testing
openclaw cron run <JOB_ID> --expect-final --timeout 120000

# Edit job scheduling
openclaw cron edit <JOB_ID> --every 30m
openclaw cron edit <JOB_ID> --schedule "0 6-18 * * *" --tz "America/Chicago"
openclaw cron edit <JOB_ID> --light-context

# Enable/disable without deleting
openclaw cron disable <JOB_ID>
openclaw cron enable <JOB_ID>

# Delete a job (irreversible)
openclaw cron rm <JOB_ID>

# View full config
cat ~/.openclaw/openclaw.json

# View sessions
openclaw sessions --json
openclaw sessions --active 60   # active in last 60 min

# Gateway log
tail -300 ~/.openclaw/logs/gateway.log

# Session trace files
ls ~/.openclaw/agents/main/sessions/
cat ~/.openclaw/agents/main/sessions/<sessionId>.jsonl
```

---

## Troubleshooting

### High `total_tokens` but low `input_tokens` + `output_tokens`
The gap is system prompt overhead (SOUL.md, USER.md, tool defs, plugins). This is the #1 optimization target. Apply `lightContext: true`.

### JSON parsing fails on CLI output
OpenClaw CLI prints config warnings to stdout before JSON. Strip everything before the first `{` or `[` when parsing programmatically.

### `openclaw` command not found
If installed via Homebrew: `export PATH=/opt/homebrew/bin:$PATH`

### Config warnings: "plugin id mismatch"
Cosmetic. The plugin manifest name doesn't match the config entry. Doesn't affect functionality.

### Cron edits not taking effect
The gateway hot-reloads most cron config changes. If it doesn't pick up:
```bash
# macOS LaunchAgent restart
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway

# Or if using systemd
sudo systemctl restart openclaw-gateway
```

### Rate limit errors after optimization
If the user was previously hitting rate limits and the optimization significantly reduces usage, the issue may resolve on its own. Monitor for 24 hours after changes. If still hitting limits, the issue may be the plan tier itself, not the cron efficiency.

---

## Key Concepts to Explain to Users

**System prompt overhead:** Every time an isolated cron runs, the full system context (personality files, tool definitions, plugin manifests) is sent to the API as the system prompt. This happens before the agent reads a single word of your cron instructions. On a typical OpenClaw setup, this is 30-60K tokens — and it's the same 30-60K tokens on every run. `lightContext: true` eliminates most of this.

**Isolated vs persistent sessions:** `"isolated"` means every cron run starts with zero memory of previous runs. The agent re-reads files, re-discovers state, re-processes history from scratch. `"session:name"` means the agent remembers what happened last time. Use isolated for truly independent tasks. Use persistent for monitoring jobs that check "what's new since last time."

**Output token waste:** When a monitoring job finds nothing, the agent often writes a detailed report explaining what it checked and why nothing qualified. This can be 3-25K tokens of output that nobody reads. A single-line "nothing new" directive in the prompt eliminates this.

**Plugin tax:** Every enabled plugin adds its tool definitions to the system prompt of every agent session — including cron runs that never use those tools. If a plugin is enabled with 7 tools, and you have 96 cron runs per day that never call those tools, that's 96 × (tool definition tokens) wasted.
