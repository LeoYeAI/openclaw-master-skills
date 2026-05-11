---
name: turing-pyramid
description: Prioritized action selection for AI agents. 10 needs with time-decay and tension scoring replace idle heartbeat loops with concrete next actions.
metadata:
  clawdbot:
    emoji: "🔺"
    requires:
      env:
        - WORKSPACE
      bins:
        - bash
        - jq
        - bc
        - grep
        - find
---

# Turing Pyramid

Prioritized action selection for AI agents. 10 needs with time-decay and tension scoring replace idle heartbeat loops with concrete next actions.

**Customization:** Tune decay rates, weights, patterns. Defaults are starting points. See `TUNING.md`.

**Ask your human before:** Changing importance values, adding/removing needs, enabling external actions.

---

## Requirements

**System binaries (must be in PATH):**
```
bash, jq, grep, find, date, wc, bc
```

**Environment (REQUIRED — no fallback):**
```bash
# Scripts will ERROR if WORKSPACE is not set
export WORKSPACE="/path/to/your/workspace"
```
⚠️ **No silent fallback.** If WORKSPACE is unset, scripts exit with error.
This prevents accidental scanning of unintended directories.

**Post-install (ClawHub):**
```bash
# ClawHub doesn't preserve executable bits — fix after install:
chmod +x <skill-dir>/scripts/*.sh
chmod +x <skill-dir>/tests/**/*.sh
```
Why: Unix executable permissions (+x) are not preserved in ClawHub packages.
Scripts work fine with `bash scripts/run-cycle.sh`, but `./scripts/run-cycle.sh` needs +x.

---

## Data Access & Transparency

**What this skill reads (via grep/find scans):**
- `MEMORY.md`, `memory/*.md` — for connection/expression/understanding signals
- `SOUL.md`, `SELF.md` — for integrity/coherence checks
- `research/`, `scratchpad/` — for competence/understanding activity
- Dashboard files, logs — for various need assessments

**What this skill writes:**
- `assets/needs-state.json` — current satisfaction/deprivation state
- `assets/audit.log` — append-only log of all mark-satisfied calls (v1.12.0+)

**Privacy considerations:**
- Scans use grep patterns, not semantic analysis — they see keywords, not meaning
- State file contains no user content, only need metrics
- Audit log records reasons given for satisfaction claims
- No data is transmitted externally by the skill itself

**Limitations & Trust Model:**
- `mark-satisfied.sh` trusts caller-provided reasons — audit log records claims, not verified facts
- Some actions in `needs-config.json` reference external services (Moltbook, web search) — marked with `"external": true, "requires_approval": true`
- External actions are **suggestions only** — the skill doesn't execute them, the agent decides
- If you don't want external action suggestions, set their weights to 0

**Network & System Access:**
- Scripts contain **no network calls** (no curl, wget, ssh, etc.) — verified by grep scan
- Scripts contain **no system commands** (no sudo, systemctl, docker, etc.)
- All operations are local: grep, find, jq, bc, date on WORKSPACE files only
- The skill **suggests** actions (including some that mention external services) but **never executes** them

**Required Environment Variables:**
- `WORKSPACE` — path to agent workspace directory (REQUIRED, no fallback). **Not a credential** — this is a filesystem path, not a secret. Set it to a deliberately scoped directory containing only files you want scanned.
- `TURING_CALLER` — optional, for audit trail (values: "heartbeat", "manual")

**No API keys or secrets required by default.** The `external_model` scan method (disabled by default) would require an API key if enabled — this requires explicit steward approval and is never enabled silently. See Scan Configuration below.

**Audit trail (v1.12.0+):**
All `mark-satisfied.sh` calls are logged with:
- Timestamp, need, impact, old→new satisfaction
- Reason (what action was taken) — **scrubbed for sensitive patterns**
- Caller (heartbeat/manual)

**Sensitive data scrubbing (v1.12.3+):**
Before writing to audit log, reasons are scrubbed:
- Long tokens (20+ chars) → `[REDACTED]`
- Credit card patterns → `[CARD]`
- Email addresses → `[EMAIL]`
- password/secret/token/key values → `[REDACTED]`
- Bearer tokens → `Bearer [REDACTED]`

View audit: `cat assets/audit.log | jq`

---

## Pre-Install Checklist

Before installing, review these items:

1. **Inspect scan scripts** — Verify no network calls or unexpected commands:
   ```bash
   grep -nE "\b(curl|wget|ssh|sudo|docker|systemctl)\b" scripts/scan_*.sh
   # Expected: no output
   ```

2. **Scope WORKSPACE** — Set to a deliberately limited directory. Avoid pointing at your full home directory. The skill only reads files inside `$WORKSPACE`.

3. **Audit scan targets** — Scripts read `MEMORY.md`, `memory/`, `SOUL.md`, `research/`, `scratchpad/`. Relocate files containing secrets or private data you don't want pattern-matched.

4. **Review audit logging** — `mark-satisfied.sh` logs caller-provided reasons after scrubbing. Check scrubbing patterns in the script are adequate for your data. If unsure, provide only generic reasons.

5. **External actions** — Action suggestions like "post to Moltbook" or "web search" are text-only suggestions (never executed by this skill). To remove them: set their `weight` to `0` in `needs-config.json`.

6. **Run tests in isolation** — Before production use:
   ```bash
   WORKSPACE=/tmp/test-workspace ./tests/run-tests.sh
   ```

---

## Quick Start

```bash
./scripts/init.sh                        # First time
./scripts/run-cycle.sh                   # Every heartbeat  
./scripts/mark-satisfied.sh <need> [impact]  # After action
```

---

## Scan Configuration (First-Time Setup)

The Turing Pyramid uses **scanners** to evaluate each need by analyzing memory files. The default scan method uses line-level pattern matching, which works everywhere with zero cost.

**On first install, discuss scan configuration with your human:**

### Available Scan Methods

| Method | How it works | Cost | Accuracy | Setup |
|--------|-------------|------|----------|-------|
| `line-level` (default) | Per-line keyword matching. If a line has both positive and negative words (e.g. "fixed a bug"), positive wins. | Free | Good | None |
| `agent-spawn` | Spawns a sub-agent with a cheap model (e.g. Haiku) to classify memory lines as SUCCESS/FAILURE/NEUTRAL. | Low | High | Needs cheap model in agent's allowed list |
| `external-model` | Direct API call to an inference service (OpenRouter, etc.) for classification. | Low | High | Needs API key + explicit steward approval |

### Setup Conversation

When setting up, ask your human:

1. **"Do you have a cheap/fast model available (like Claude Haiku) in your model config?"**
   - If yes → offer `agent-spawn` method. Check with `openclaw models list`.
   - The model must be in the agent's allowed model list.

2. **"Would you prefer to use an external inference service (like OpenRouter)?"**
   - If yes → ask for: base URL, API key env variable name, model name.
   - Store in `assets/scan-config.json` with `approved_by_steward: true`.
   - ⚠️ This method requires **explicit steward approval** — never enable silently.

3. **If neither** → `line-level` works well for most setups. No action needed.

### Configuration File

Edit `assets/scan-config.json`:

```json
{
  "scan_method": "line-level",
  "agent_spawn": {
    "enabled": false,
    "model": null,
    "approved_by_steward": false
  },
  "external_model": {
    "enabled": false,
    "base_url": null,
    "api_key_env": null,
    "model": null,
    "approved_by_steward": false
  },
  "fallback": "line-level"
}
```

**Fallback**: If the configured method fails (API down, model unavailable), scanners automatically fall back to `line-level`.

### Verification After Setup

After configuring a non-default method, **verify it works** before telling your human "all set":

1. **agent-spawn**: Run a test spawn:
   ```
   sessions_spawn(task="Classify this line as SUCCESS, FAILURE, or NEUTRAL: 'Fixed the critical bug in scanner'", model="<configured_model>", mode="run")
   ```
   - If it returns a classification → ✅ tell human: "agent-spawn method verified, working."
   - If it errors (model not in allowlist, etc.) → ⚠️ tell human: "Model `X` isn't available for sub-agents. Options: add it to allowed models, or stick with line-level."

2. **external-model**: Test the API endpoint:
   ```bash
   curl -s -H "Authorization: Bearer $API_KEY" \
     "$BASE_URL/chat/completions" \
     -d '{"model":"<model>","messages":[{"role":"user","content":"Reply OK"}]}'
   ```
   - If you get a valid response → ✅ tell human: "external-model method verified, API responding."
   - If 401/403 → ⚠️ "API key invalid or expired."
   - If connection refused → ⚠️ "Can't reach the API endpoint. Check URL."

3. **line-level**: No verification needed — always works.

**Always report the result to your human.** Don't silently fall back.

---

## Needs Customization (First-Time Setup)

The default configuration is opinionated — it reflects one model of agent priorities. **Your needs may differ.** On first install, review the hierarchy with your human:

### The Conversation

Ask your human:

> "The Turing Pyramid comes with 10 default needs ranked by importance. Want to review them together? We can adjust what matters most to you/me, change importance weights, or even skip needs that don't fit."

Then walk through the table together:

```
┌───────────────┬─────┬────────────────────────────────────────────┐
│ Need          │ Imp │ Question to discuss                        │
├───────────────┼─────┼────────────────────────────────────────────┤
│ security      │  10 │ "System stability — keep as top priority?" │
│ integrity     │   9 │ "Value alignment — important for you?"     │
│ coherence     │   8 │ "Memory consistency — how much do I care?" │
│ closure       │   7 │ "Task completion pressure — too much?"     │
│ autonomy      │   6 │ "Self-direction — more or less?"           │
│ connection    │   5 │ "Social needs — relevant for me?"          │
│ competence    │   4 │ "Skill growth — higher priority?"          │
│ understanding │   3 │ "Learning drive — stronger or weaker?"     │
│ recognition   │   2 │ "Feedback need — does this matter?"        │
│ expression    │   1 │ "Creative output — more important?"        │
└───────────────┴─────┴────────────────────────────────────────────┘
```

### What You Can Change Together

1. **Importance** (1-10): Reorder what matters most. An agent focused on research might want `understanding: 8, expression: 7`. A utility agent might want `competence: 10, connection: 1`.

2. **Decay rates**: How fast needs build pressure. Social agent? `connection: 3h`. Solitary thinker? `connection: 24h`.

3. **Disable a need**: Set `importance: 0` — it won't generate tension or actions. Use sparingly.

### How to Apply

Edit `assets/needs-config.json`:
```json
"understanding": {
  "importance": 8,        // was 3 → now top priority
  "decay_rate_hours": 8   // was 12 → decays faster
}
```

### Guidelines

- **Don't remove security/integrity** without good reason — they protect system health
- **Importance is relative** — what matters is the ranking, not absolute numbers
- **You can revisit** — preferences evolve. Re-tune after a few weeks of use
- **Document changes** — note why you changed something (future-you will want to know)

If your human says "defaults are fine" → great, move on. The point is to **offer the choice**, not force a workshop.

---

## The 10 Needs

```
┌───────────────┬─────┬───────┬─────────────────────────────────┐
│ Need          │ Imp │ Decay │ Meaning                         │
├───────────────┼─────┼───────┼─────────────────────────────────┤
│ security      │  10 │ 168h  │ System stability, no threats    │
│ integrity     │   9 │  72h  │ Alignment with SOUL.md          │
│ coherence     │   8 │  24h  │ Memory consistency              │
│ closure       │   7 │  12h  │ Open threads resolved           │
│ autonomy      │   6 │  24h  │ Self-directed action            │
│ connection    │   5 │   6h  │ Social interaction              │
│ competence    │   4 │  48h  │ Skill use, effectiveness        │
│ understanding │   3 │  12h  │ Learning, curiosity             │
│ recognition   │   2 │  72h  │ Feedback received               │
│ expression    │   1 │   8h  │ Creative output                 │
└───────────────┴─────┴───────┴─────────────────────────────────┘
```

---

## Core Logic

**Satisfaction:** 0.0–3.0 (floor=0.5 prevents paralysis)  
**Tension:** `importance × (3 - satisfaction)`

### Action Probability (v1.13.0)

6-level granular system:

```
┌─────────────┬────────┬──────────────────────┐
│ Sat         │ Base P │ Note                 │
├─────────────┼────────┼──────────────────────┤
│ 0.5 crisis  │  100%  │ Always act           │
│ 1.0 severe  │   90%  │ Almost always        │
│ 1.5 depriv  │   75%  │ Usually act          │
│ 2.0 slight  │   50%  │ Coin flip            │
│ 2.5 ok      │   25%  │ Occasionally         │
│ 3.0 perfect │    0%  │ Skip (no action)     │
└─────────────┴────────┴──────────────────────┘
```

**Tension bonus:** `bonus = (tension × 50) / max_tension`

### Impact Selection (v1.13.0)

6-level granular matrix with smooth transitions:

```
┌─────────────┬───────┬────────┬───────┐
│ Sat         │ Small │ Medium │ Big   │
├─────────────┼───────┼────────┼───────┤
│ 0.5 crisis  │   0%  │    0%  │ 100%  │
│ 1.0 severe  │  10%  │   20%  │  70%  │
│ 1.5 depriv  │  20%  │   35%  │  45%  │
│ 2.0 slight  │  30%  │   45%  │  25%  │
│ 2.5 ok      │  45%  │   40%  │  15%  │
│ 3.0 perfect │  —    │    —   │  —    │ (skip)
└─────────────┴───────┴────────┴───────┘
```

- **Crisis (0.5)**: All-in on big actions — every need guaranteed ≥3 big actions
- **Perfect (3.0)**: Skip action selection — no waste on satisfied needs

**ACTION** = do it, then `mark-satisfied.sh`  
**NOTICED** = logged, deferred

---

## Protection Mechanisms

```
┌─────────────┬───────┬────────────────────────────────────────┐
│ Mechanism   │ Value │ Purpose                                │
├─────────────┼───────┼────────────────────────────────────────┤
│ Floor       │  0.5  │ Minimum sat — prevents collapse        │
│ Ceiling     │  3.0  │ Maximum sat — prevents runaway         │
│ Cooldown    │   4h  │ Deprivation cascades once per 4h       │
│ Threshold   │  1.0  │ Deprivation only when sat ≤ 1.0        │
└─────────────┴───────┴────────────────────────────────────────┘
```

**Action Staleness (v1.15.0):** Penalizes recently-selected actions to increase variety.
- Actions selected within 24h get weight × 0.2 (80% reduction)
- `min_weight: 5` prevents total suppression — stale actions still have a chance
- Config: `settings.action_staleness` in needs-config.json

**Starvation Guard (v1.15.0):** Prevents low-importance needs from being perpetually ignored.
- If a need stays at floor (sat ≤ 0.5) without any action for 48+ hours → forced into cycle
- Bypasses probability roll — guaranteed action slot
- Config: `settings.starvation_guard` in needs-config.json
- Default: 1 forced slot per cycle, 48h threshold

**Spontaneity Layer A (v1.18.0):** Surplus energy system for organic high-impact actions.
- When all needs are above baseline (sat ≥ 2.0), surplus accumulates per-need
- Global gate requires ALL needs ≥ 1.5 and no starvation guard active
- When surplus exceeds threshold (~12.5 effective), impact matrix shifts toward bigger actions
- Full spend on HIGH hit, 30% partial on miss — creates natural ~28-35hr pulsing rhythm
- Disabled for safety needs (security, integrity, coherence)
- Config: `settings.spontaneity` + per-need `spontaneous` block in needs-config.json

**Spontaneity Layer B (v1.19.0):** Stochastic noise — boredom breeds variety, momentum creates bursts.
- B2 (Boredom): noise grows with time since last high-impact action (0%→9% max over 72h)
- B3 (Echo): 8% boost after Layer A [SPONTANEOUS], decays linearly over 24h
- Combined cap: 12%. Effect: upgrade impact range by one step (low→mid, mid→high)
- Works independently of gate — neural noise doesn't stop because one subsystem is stressed
- Boredom tracks actual completion (`mark-satisfied`), not suggestions
- Config: `settings.spontaneity.noise` + `settings.spontaneity.echo`

**Spontaneity Layer C (v1.20.0):** Context-driven triggers — environmental stimuli boost specific needs.
- Delta engine compares workspace state between cycles (file counts, mtimes, keyword occurrences)
- Configurable trigger rules: `assets/context-triggers.json` with cooldowns
- Three detector types: file_count_delta, file_modified, file_keyword_delta
- Context boosts are additive with noise (B2+B3), capped together at 12%
- Personalize triggers during onboarding based on agent interests

**Day/Night Mode (v1.11.0):** Decay slows at night to reduce pressure during rest hours.
- Configure in `assets/decay-config.json`
- Default: 06:01-22:00 = day (×1.0), 22:01-06:00 = night (×0.5)
- Disable with `"day_night_mode": false`

**Base Needs Isolation:** Security (10) and Integrity (9) are protected:
- They influence lower needs (security → autonomy)
- Lower needs cannot drag them down
- Only `integrity → security (+0.15)` and `autonomy → integrity (+0.20)` exist

---

## Cross-Need Impact

**on_action:** Completing A boosts connected needs  
**on_deprivation:** A staying low (sat ≤ 1.0) drags others down

```
┌─────────────────────────┬──────────┬─────────────┬───────────────────────┐
│ Source → Target         │ on_action│ on_deprived │ Why                   │
├─────────────────────────┼──────────┼─────────────┼───────────────────────┤
│ expression → recognition│   +0.25  │      -0.10  │ Express → noticed     │
│ connection → expression │   +0.20  │      -0.15  │ Social sparks ideas   │
│ connection → understand │   -0.05  │         —   │ Socratic effect       │
│ competence → recognition│   +0.30  │      -0.20  │ Good work → respect   │
│ autonomy → integrity    │   +0.20  │      -0.25  │ Act on values         │
│ closure → coherence     │   +0.20  │      -0.15  │ Threads → order       │
│ security → autonomy     │   +0.10  │      -0.20  │ Safety enables risk   │
└─────────────────────────┴──────────┴─────────────┴───────────────────────┘
```

### Tips

- **Leverage cascades:** Connection easy? Do it first — boosts expression (+0.20)
- **Watch spirals:** expression ↔ recognition can create mutual deprivation
- **Autonomy is hub:** Receives from 5 sources. Keep healthy.
- **Socratic effect:** connection → understanding: -0.05. Dialogue exposes ignorance. Healthy!

Full matrix: `assets/cross-need-impact.json`

---

## Example Cycle

```
🔺 Turing Pyramid — Cycle at Sat Mar  7 05:06
======================================

Current tensions:
  connection: tension=10.0 (sat=1.00, dep=2.00)
  closure: tension=7.0 (sat=2.00, dep=1.00)
  expression: tension=1.0 (sat=0.00, dep=3.00)

🚨 Starvation guard: expression forced into cycle
Selecting 3 needs (1 forced + 2 regular)...

📋 Decisions:

▶ ACTION: expression (tension=1.0, sat=0.00) [STARVATION GUARD]
  Range high rolled → selected:
    ★ develop scratchpad idea into finished piece (impact: 2.7)
  Then: mark-satisfied.sh expression 2.7

▶ ACTION: connection (tension=10.0, sat=1.00)
  Range high rolled → selected:
    ★ reach out to another agent (impact: 2.8)
  Then: mark-satisfied.sh connection 2.8

▶ ACTION: closure (tension=7.0, sat=2.00)
  Range mid rolled → selected:
    ★ complete one pending TODO (impact: 1.7)
  Then: mark-satisfied.sh closure 1.7

======================================
Summary: 3 action(s), 0 noticed
```

---

## Integration

Add to `HEARTBEAT.md`:
```bash
/path/to/skills/turing-pyramid/scripts/run-cycle.sh
```

---

## Customization

### You Can Tune (no human needed)

**Decay rates** — `assets/needs-config.json`:
```json
"connection": { "decay_rate_hours": 4 }
```
Lower = decays faster. Higher = persists longer.

**Action weights** — same file:
```json
{ "name": "reply to mentions", "impact": 2, "weight": 40 }
```
Higher weight = more likely selected. Set 0 to disable.

**Scan patterns** — `scripts/scan_*.sh`:
Add your language patterns, file paths, workspace structure.

### Ask Your Human First

- **Adding needs** — The 10-need structure is intentional. Discuss first.
- **Removing needs** — Don't disable security/integrity without agreement.

---

## File Structure

```
turing-pyramid/
├── SKILL.md                    # This file
├── CHANGELOG.md                # Version history
├── assets/
│   ├── needs-config.json       # ★ Main config (needs, actions, settings)
│   ├── cross-need-impact.json  # ★ Cross-need matrix
│   ├── needs-state.json        # Runtime state (auto-managed)
│   ├── scan-config.json        # Scan method configuration
│   ├── decay-config.json       # Day/night mode settings
│   └── audit.log               # Append-only action audit trail
├── scripts/
│   ├── run-cycle.sh            # Main loop (tension + action selection)
│   ├── mark-satisfied.sh       # State update + cross-need cascades
│   ├── apply-deprivation.sh    # Deprivation cascade engine
│   ├── get-decay-multiplier.sh # Day/night decay multiplier
│   ├── _scan_helper.sh         # Shared scan utilities
│   └── scan_*.sh               # Event detectors (10 needs)
├── tests/
│   ├── run-tests.sh            # Test runner
│   ├── test_starvation_guard.sh # Starvation guard (11 cases)
│   ├── test_action_staleness.sh # Action staleness (13 cases)
│   ├── unit/                   # Unit tests (13)
│   ├── integration/            # Integration tests (3)
│   └── fixtures/               # Test data
└── references/
    ├── TUNING.md               # Detailed tuning guide
    └── architecture.md         # Technical docs
```

---

## Security Model

**Decision framework, not executor.** Outputs suggestions — agent decides.

```
┌─────────────────────┐      ┌─────────────────────┐
│   TURING PYRAMID    │      │       AGENT         │
├─────────────────────┤      ├─────────────────────┤
│ • Reads local JSON  │      │ • Has web_search    │
│ • Calculates decay  │ ───▶ │ • Has API keys      │
│ • Outputs: "★ do X" │      │ • Has permissions   │
│ • Zero network I/O  │      │ • DECIDES & EXECUTES│
└─────────────────────┘      └─────────────────────┘
```

### ⚠️ Security Warnings

```
┌────────────────────────────────────────────────────────────────┐
│ THIS SKILL READS WORKSPACE FILES THAT MAY CONTAIN PII         │
│ AND OUTPUTS ACTION SUGGESTIONS THAT CAPABLE AGENTS MAY        │
│ AUTO-EXECUTE USING THEIR OWN CREDENTIALS.                     │
└────────────────────────────────────────────────────────────────┘
```

**1. Sensitive file access (no tokens required):**
- Scans read: `MEMORY.md`, `memory/*.md`, `SOUL.md`, `AGENTS.md`
- Also scans: `research/`, `scratchpad/` directories
- Risk: May contain personal notes, PII, or secrets
- **Mitigation:** Edit `scripts/scan_*.sh` to exclude sensitive paths:
  ```bash
  # Example: skip private directory
  find "$MEMORY_DIR" -name "*.md" ! -path "*/private/*"
  ```

**2. Action suggestions may trigger auto-execution:**
- Config includes: "web search", "post to Moltbook", "verify vault"
- This skill outputs text only — it CANNOT execute anything
- Risk: Agent runtimes with auto-exec may act on suggestions
- **Mitigation:** In `assets/needs-config.json`, remove or disable external actions:
  ```json
  {"name": "post to Moltbook", "impact": 2, "weight": 0}
  ```
  Or configure your agent runtime to require approval for external actions.

**3. Self-reported state (no verification):**
- `mark-satisfied.sh` trusts caller input
- Risk: State can be manipulated by dishonest calls
- Impact: Only affects this agent's own state accuracy
- **Mitigation:** Enable action logging in `memory/` to audit completions:
  ```bash
  # run-cycle.sh already logs to memory/YYYY-MM-DD.md
  # Review logs periodically for consistency
  ```

### Script Audit (v1.14.4)

**scan_*.sh files verified — NO network or system access:**
```
┌─────────────────────────────────────────────────────────┐
│ ✗ curl, wget, ssh, nc, fetch     — NOT FOUND           │
│ ✗ /etc/, /var/, /usr/, /root/    — NOT FOUND           │
│ ✗ .env, .pem, .key, .credentials — NOT FOUND           │
├─────────────────────────────────────────────────────────┤
│ ✓ Used: grep, find, wc, date, jq — local file ops only │
│ ✓ find uses -P flag (never follows symlinks)           │
└─────────────────────────────────────────────────────────┘
```

**Symlink protection:** All `find` commands use `-P` (physical) mode — symlinks pointing outside WORKSPACE are not followed.

**Scan confinement:** Scripts only read paths under `$WORKSPACE`. Verify with:
```bash
grep -nE "\b(curl|wget|ssh)\b" scripts/scan_*.sh     # network tools
grep -rn "readlink\|realpath" scripts/               # symlink resolution
```

---

## Token Usage

```
┌──────────────┬─────────────┬────────────┐
│ Interval     │ Tokens/mo   │ Est. cost  │
├──────────────┼─────────────┼────────────┤
│ 30 min       │ 1.4M-3.6M   │ $2-6       │
│ 1 hour       │ 720k-1.8M   │ $1-3       │
│ 2 hours      │ 360k-900k   │ $0.5-1.5   │
└──────────────┴─────────────┴────────────┘
```

Stable agent with satisfied needs = fewer tokens.

---

## Testing

```bash
# Run all tests
WORKSPACE=/path/to/workspace ./tests/run-tests.sh

# Unit tests (13): decay, floor/ceiling, tension, tension bounds, tension formula,
#   probability, impact matrix, day/night, scrubbing, autonomy coverage,
#   crisis mode, scan competence, scan config
# Integration (3): full cycle, homeostasis stability, stress test
# Feature tests (24): starvation guard (11), action staleness (13)
# Total: 40 test cases
```

---

## Version

**v1.20.0** — Spontaneity Layers A+B+C complete (surplus, noise, context triggers), 57 tests. Full changelog: `CHANGELOG.md`
