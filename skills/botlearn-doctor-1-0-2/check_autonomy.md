# Domain: Autonomous Intelligence

> Deep reference for Domain 5 in SKILL.md.
> Load this file when running L3 analysis or when SKILL.md thresholds need clarification.
>
> **Input:** `DATA.precheck`, `DATA.heartbeat`, `DATA.cron`, `DATA.memory_stats`,
>             `DATA.workspace_audit`, `DATA.doctor_deep`, `DATA.logs`, `DATA.status`
> **Output:** status (✅/⚠️/❌) + score (0–100) + autonomy mode label + findings + fix hints

---

## Analysis Checklist

### 1. Heartbeat Status

From `DATA.heartbeat` (raw content of `workspace/HEARTBEAT.md`):

Parse the last heartbeat timestamp (ISO 8601 or human-readable format).
Calculate age: `now - last_heartbeat_time`.

| Heartbeat Age | Status | Score Impact | Qualitative |
|---------------|--------|-------------|-------------|
| < 60 minutes | ✅ | 0 | Agent actively running |
| 1–6 hours | ⚠️ | -10 | Potentially idle |
| 6–24 hours | ⚠️ | -20 | Agent likely stopped |
| > 24 hours | ❌ | -40 | Agent has been down |
| File missing | ⚠️ | -15 | Heartbeat not initialized |

From `DATA.config.agents.heartbeat`:
- `autoRecovery: false` or missing → ⚠️ (-10). Risk: no automatic restart after crash.
- `intervalMinutes > 120` → ⚠️ (-5). Risk: slow crash detection.

**Fix (no heartbeat):** Verify `openclaw start` is running; check `workspace/HEARTBEAT.md` config.
**Fix (autoRecovery off):** Set `agents.heartbeat.autoRecovery: true` in `openclaw.json`.

---

### 2. Scheduled Tasks (Cron)

From `DATA.cron`:

| Condition | Status | Score Impact |
|-----------|--------|-------------|
| At least 1 active task defined | ✅ | 0 |
| 0 tasks in cron directory | ⚠️ | -10 |
| cron directory missing | ⚠️ | -5 |
| Any task with `status: error` or last-run failed | ⚠️ | -10 per task (max -20) |

For each cron task, report: `name`, `schedule`, `last_run`, `next_run`, `status`.

**Risk:** Without cron tasks, the agent cannot perform scheduled learning cycles,
self-optimization, or periodic health checks.

---

### 3. Memory Health

From `DATA.memory_stats`:

| Condition | Status | Score Impact | Qualitative |
|-----------|--------|-------------|-------------|
| `total_size` < 100 MB | ✅ | 0 | Lean and efficient |
| `total_size` 100–500 MB | ⚠️ | -10 | Growing — consider pruning |
| `total_size` > 500 MB | ❌ | -25 | Bloated — likely affects search performance |
| `total_files` < 100 | ✅ | 0 | |
| `total_files` 100–500 | ⚠️ | -5 | |
| `total_files` > 500 | ⚠️ | -10 | High file count slows memory search |

Report type breakdown to show memory composition:
e.g., "42 .md files (knowledge), 18 .json files (structured data)"

**Fix (bloated):** `clawhub memory compact` or prune entries older than 90 days manually.

---

### 3b. Agent & Service Status (from DATA.status)

From `DATA.status`:

| Check | Field | ✅ | ⚠️ | ❌ | Score Impact |
|-------|-------|-----|-----|-----|-------------|
| Gateway service running | `status.overview.gateway_service.running` | true | — | false | ❌ -20 |
| Node service installed | `status.overview.node_service.installed` | true | false | — | ⚠️ -10 |
| Active agents | `status.overview.agents_overview.active` ≥ 1 | ≥1 | 0 | — | ⚠️ -15 |
| Agent bootstrap file | `status.agents[].bootstrap_present` | true | false | — | ⚠️ -10 per agent (max -20) |

**Bootstrap file absent**: If any agent has `bootstrap_present = false`, the agent lacks
a configuration file at startup — it cannot self-configure or restore its role after restart.
Report each affected agent by name.

**Fix (gateway service not running):** `openclaw start` or `openclaw restart`
**Fix (node service not installed):** `openclaw install-service` (enables auto-start on boot)
**Fix (bootstrap absent):** Create or restore `agent.md` in the agent's store directory
(`status.agents[].store_path`) and restart: `openclaw restart`

**Log Issues from Status**: `DATA.status.log_issues[]` provides pre-filtered notable log lines
(timeouts, errors, command-not-found). Cross-reference with `DATA.logs` for completeness.
Each entry in `log_issues` that is not already captured by `DATA.logs` should be added as
an additional finding.

---

### 4. Self-Check Results (openclaw doctor)

From `DATA.precheck.summary` + `DATA.doctor_deep`:

| Condition | Status | Score Impact |
|-----------|--------|-------------|
| All checks passing (error=0, warn=0) | ✅ | 0 |
| `warn > 0` | ⚠️ | -10 per warning (max -20) |
| `error > 0` | ❌ | -20 per error (max -40) |
| `precheck_ran = false` (doctor unavailable) | ⚠️ | -15 |

From `DATA.doctor_deep` (text output of `openclaw doctor --deep --non-interactive`):
- Extract lines containing "FAIL" or "ERROR" → add as ❌ findings.
- Extract lines containing "WARN" or "CAUTION" → add as ⚠️ findings.
- Cross-reference with `DATA.precheck.summary` to catch anything not captured by JSON.

---

### 5. Log Anomalies (Autonomy Signals)

From `DATA.logs`:

| Condition | Status | Score Impact |
|-----------|--------|-------------|
| `critical_events` contains OOM or segfault | ❌ | -20 |
| `critical_events` contains UnhandledPromiseRejection | ⚠️ | -10 |
| `anomalies.error_spikes` severity=high | ⚠️ | -10 |
| `anomalies.error_spikes` severity=critical | ❌ | -20 |
| Error rate < 1% | ✅ | 0 |

Focus on patterns indicating autonomous operation disruption:
- OOM → memory pressure disrupting agent continuity
- Uncaught rejections → skill execution instability
- Error spikes → external dependency failures affecting scheduled tasks

---

### 6. Workspace Identity & Configuration Review

**Source:** `DATA.workspace_identity`

The agent's workspace should contain 5 core identity files. Their presence and content depth
directly determine how well the agent understands itself and the user it serves.

#### 6.1 File Presence

| File | Purpose | Missing → Status | Score Impact |
|------|---------|-----------------|-------------|
| `agent.md` | Role definition, capabilities, behavioral rules | ❌ | -20 — no bootstrap identity; agent restarts as blank |
| `user.md` | User profile, preferences, personal context | ❌ | -15 — agent cannot adapt to the individual |
| `soul.md` | Personality, values, principles | ⚠️ | -10 — agent lacks character consistency |
| `tool.md` | Available tools and usage context | ⚠️ | -10 — agent unaware of its own tool surface |
| `identity.md` | Agent name, version, organizational context | ⚠️ | -5 — identity is implicit only |

If `agent.md` is missing, flag as **Critical** regardless of overall score.

#### 6.2 Content Sufficiency

For each file that exists, assess content depth by word count and key structural signals.
Do not reproduce content verbatim — analyze and summarize only.

**agent.md** — Must declare the agent's role. Look for: "you are", "your role", "responsibilities",
"capabilities", behavioral rules, constraints.

| Content Level | Condition | Status | Score Impact |
|---------------|-----------|--------|-------------|
| Rich | ≥ 200 words + role declaration + behavioral rules | ✅ | 0 |
| Basic | 50–199 words, role defined but thin | ⚠️ | -5 |
| Critical | < 50 words or no clear role declaration | ❌ | -10 |

**user.md** — Must contain actual user context. Look for: name/handle, background, preferences,
communication style, goals, domain expertise. Generic template content ("Your user is...") does NOT count.

| Content Level | Condition | Status | Score Impact |
|---------------|-----------|--------|-------------|
| Personalized | ≥ 100 words + personal context + preferences | ✅ | 0 |
| Sparse | 20–99 words, minimal or generic profile | ⚠️ | -8 |
| Empty/template | < 20 words or clearly unfilled template | ❌ | -12 |

**soul.md** — Values, principles, personality traits. Look for: adjectives describing character,
ethical guidelines, tone preferences, interaction style.

| Content Level | Condition | Status | Score Impact |
|---------------|-----------|--------|-------------|
| Defined | ≥ 80 words + clear values/principles | ✅ | 0 |
| Thin | < 80 words or generic | ⚠️ | -5 |

**tool.md** — Tool inventory with context. Look for: tool names listed, usage notes, limitations.

| Content Level | Condition | Status | Score Impact |
|---------------|-----------|--------|-------------|
| Complete | ≥ 50 words + tool names with context | ✅ | 0 |
| Sparse | exists but lacks detail | ⚠️ | -3 |

**identity.md** — Agent name and organizational context. Look for: agent name, version, owner,
purpose statement.

| Content Level | Condition | Status | Score Impact |
|---------------|-----------|--------|-------------|
| Defined | ≥ 30 words + name + purpose | ✅ | 0 |
| Thin | exists but vague | ⚠️ | -3 |

#### 6.3 Identity Completeness Labels

After scoring all 5 files, assign an overall identity label:

| Condition | Label | Score Bonus |
|-----------|-------|-------------|
| All 5 present + agent.md ✅ + user.md ✅ | **Identity Complete** | +5 |
| agent.md present ✅ but user.md missing/sparse | **User-Blind** | 0 — agent cannot personalize |
| agent.md missing | **Identity Critical** | 0 — autonomous operation compromised |
| All 5 missing | **Identity Absent** | 0 — blank agent instance |

#### 6.4 Fix Guidance

For missing or thin files, generate specific recommendations:

```
# agent.md — recommended minimum structure:
You are [agent name], a [role description].
Your responsibilities: [list]
Your capabilities: [list]
Behavioral rules: [constraints]

# user.md — recommended minimum structure:
Name: [user name]
Background: [domain/expertise]
Preferences: [communication style, format]
Goals: [what they want to achieve]

# soul.md — recommended minimum structure:
Personality: [key traits]
Values: [principles that guide behavior]
Tone: [how to speak/write]
```

---

## Autonomy Readiness Assessment

After all checks, determine the overall autonomy mode.
Also incorporate `DATA.status` service indicators:

| Condition | Autonomy Mode | Score Bonus |
|-----------|--------------|-------------|
| Heartbeat <1h + autoRecovery=on + ≥1 cron task + doctor errors=0 + gateway_service running + all bootstrap_present + identity_label=Complete | Autonomous-Ready | +5 |
| Heartbeat active but: missing cron, or autoRecovery off, or gateway stopped, or any bootstrap missing, or identity label = User-Blind | Partial Autonomy | 0 |
| Heartbeat missing/stale OR identity_label = Identity Critical | Manual Mode | 0 |

---

## Scoring

```
Base score: 100
Apply all score impacts (cumulative).
Apply +5 bonus if Autonomous-Ready.
Floor: 0. Ceiling: 100.
```

| Score Range | Status |
|-------------|--------|
| ≥ 80 | ✅ |
| 60–79 | ⚠️ |
| < 60 | ❌ |

---

## Output Format

Produce in REPORT_LANG (domain label, autonomy mode label, and descriptions translated; commands and paths in English):

```
[Autonomous Intelligence — translated domain label] [STATUS] — Score: XX/100
[Autonomy Mode label in REPORT_LANG]: [Autonomous-Ready / Partial Autonomy / Manual Mode — translated]
[One-sentence summary in REPORT_LANG]

[Heartbeat label in REPORT_LANG]:  last seen [X ago / never]  interval=[X]min  autoRecovery=[on/off]  [STATUS]
[Cron label in REPORT_LANG]:       [X] tasks — [name: schedule, last-run status, ...]               [STATUS]
[Memory label in REPORT_LANG]:     [X] files, [X MB] ([X .md, X .json, ...])                       [STATUS]
[Services label in REPORT_LANG]:   gateway [running/stopped] (pid=[X])  node-service [on/off]       [STATUS]
[Agents label in REPORT_LANG]:     [X] active  bootstrap: [all present / X agents missing]          [STATUS]
[Self-Check label in REPORT_LANG]: [X pass / X warn / X error] (openclaw doctor)                   [STATUS]
[Log Health label in REPORT_LANG]: error rate [X%], critical events: [none / list]                  [STATUS]
[Identity label in REPORT_LANG]:   [Identity Complete / User-Blind / Identity Critical / Identity Absent]
  agent.md: [✅ rich / ⚠️ thin / ❌ missing]  ([X] words)
  user.md:  [✅ personalized / ⚠️ sparse / ❌ missing/template]  ([X] words)
  soul.md:  [✅ defined / ⚠️ thin / ❌ missing]
  tool.md:  [✅ complete / ⚠️ sparse / ❌ missing]
  identity.md: [✅ defined / ⚠️ thin / ❌ missing]
  [STATUS]

[If any ⚠️/❌ — Findings label in REPORT_LANG:]
- [Evidence citing DATA field and actual value]

[Fix Hints label in REPORT_LANG:]
- [Actionable steps ordered by severity, each with rollback where applicable]

[If Autonomous-Ready:]
[Confirmation message in REPORT_LANG that instance is configured for full autonomous operation]
```
