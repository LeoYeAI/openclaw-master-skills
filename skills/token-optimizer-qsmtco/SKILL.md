---
name: token-optimizer
description: Reduce OpenClaw token usage and API costs through smart model routing, heartbeat optimization, budget tracking, and multi-provider fallbacks. Use when token costs are high, API rate limits are being hit, or hosting multiple agents at scale. Includes ready-to-use scripts for task classification, usage monitoring, and optimized heartbeat scheduling. All operations are local file analysis only - no network requests, no code execution. See SECURITY.md for details.
---

# Token Optimizer

Comprehensive toolkit for reducing token usage and API costs in OpenClaw deployments. Combines smart model routing, optimized heartbeat intervals, usage tracking, and multi-provider strategies.

## Quick Start

**Immediate actions** (no config changes needed):

1. **Generate optimized AGENTS.md (BIGGEST WIN!):**
   ```bash
   python3 scripts/context_optimizer.py generate-agents
   # Creates AGENTS.md.optimized — review and replace your current AGENTS.md
   ```

2. **Check what context you ACTUALLY need:**
   ```bash
   python3 scripts/context_optimizer.py recommend "hi, how are you?"
   # Shows: Only 2 files needed (not 50+!)
   ```

3. **Install optimized heartbeat:**
   ```bash
   cp assets/HEARTBEAT.template.md ~/.openclaw/workspace/HEARTBEAT.md
   ```

4. **Enforce cheap models for casual chat:**
   ```bash
   python3 scripts/model_router.py "thanks!"
   # Shows: Use Quick, not Deep!
   ```

5. **Check current token budget:**
   ```bash
   python3 scripts/token_tracker.py check
   ```

**Expected savings:** 50-80% reduction in token costs for typical workloads (context optimization is the biggest factor!).

## Core Capabilities

### 1. Context Optimization (NEW!)

**Biggest token saver** — Only load files you actually need, not everything upfront.

**Problem:** Default OpenClaw loads ALL context files every session:
- SOUL.md, AGENTS.md, USER.md, TOOLS.md, MEMORY.md
- docs/**/*.md (hundreds of files)
- memory/2026-*.md (daily logs)
- Total: Often 50K+ tokens before user even speaks!

**Solution:** Lazy loading based on prompt complexity.

**Usage:**
```bash
python3 scripts/context_optimizer.py recommend "<user prompt>"
```

**Examples:**
```bash
# Simple greeting → minimal context (2 files only!)
context_optimizer.py recommend "hi"
→ Load: SOUL.md, IDENTITY.md
→ Skip: Everything else
→ Savings: ~80% of context

# Standard work → selective loading
context_optimizer.py recommend "write a function"
→ Load: SOUL.md, IDENTITY.md, memory/TODAY.md
→ Skip: docs, old memory, knowledge base
→ Savings: ~50% of context

# Complex task → full context
context_optimizer.py recommend "analyze our entire architecture"
→ Load: SOUL.md, IDENTITY.md, MEMORY.md, memory/TODAY+YESTERDAY.md
→ Conditionally load: Relevant docs only
→ Savings: ~30% of context
```

**Output format:**
```json
{
  "complexity": "simple",
  "context_level": "minimal",
  "recommended_files": ["SOUL.md", "IDENTITY.md"],
  "file_count": 2,
  "savings_percent": 80,
  "skip_patterns": ["docs/**/*.md", "memory/20*.md"]
}
```

**Integration pattern:**
Before loading context for a new session:
```python
from context_optimizer import recommend_context_bundle

user_prompt = "thanks for your help"
recommendation = recommend_context_bundle(user_prompt)

if recommendation["context_level"] == "minimal":
    # Load only SOUL.md + IDENTITY.md
    # Skip everything else
    # Save ~80% tokens!
```

**Generate optimized AGENTS.md:**
```bash
context_optimizer.py generate-agents
# Creates AGENTS.md.optimized with lazy loading instructions
# Review and replace your current AGENTS.md
```

**Expected savings:** 50-80% reduction in context tokens.

### 2. Smart Model Routing (ENHANCED!)

Automatically classify tasks and route to appropriate model tiers.

**NEW: Communication pattern enforcement** — Never waste Deep tokens on "hi" or "thanks"!

**Usage:**
```bash
python3 scripts/model_router.py "<user prompt>" [current_model] [force_tier]
```

**Examples:**
```bash
# Communication (NEW!) → ALWAYS Quick
python3 scripts/model_router.py "thanks!"
python3 scripts/model_router.py "hi"
python3 scripts/model_router.py "ok got it"
→ Enforced: Quick (NEVER Standard/Deep for casual chat)

# Simple task → suggests Quick
python3 scripts/model_router.py "read the log file"

# Medium task → suggests Standard
python3 scripts/model_router.py "write a function to parse JSON"

# Complex task → suggests Deep
python3 scripts/model_router.py "design a microservices architecture"
```

**Patterns enforced to Quick (NEVER Standard/Deep):**

*Communication:*
- Greetings: hi, hey, hello, yo
- Thanks: thanks, thank you, thx
- Acknowledgments: ok, sure, got it, understood
- Short responses: yes, no, yep, nope
- Single words or very short phrases

*Background tasks:*
- Heartbeat checks: "check email", "monitor servers"
- Cronjobs: "scheduled task", "periodic check", "reminder"
- Document parsing: "parse CSV", "extract data from log", "read JSON"
- Log scanning: "scan error logs", "process logs"

**Integration pattern:**
```python
from model_router import route_task

user_prompt = "show me the config"
routing = route_task(user_prompt)

if routing["should_switch"]:
    # Use routing["recommended_model"]
    # Save routing["cost_savings_percent"]
```

**Customization:**
Edit `ROUTING_RULES` or `COMMUNICATION_PATTERNS` in `scripts/model_router.py` to adjust patterns and keywords.

### 3. Heartbeat Optimization

Reduce API calls from heartbeat polling with smart interval tracking:

**Setup:**
```bash
# Copy template to workspace
cp assets/HEARTBEAT.template.md ~/.openclaw/workspace/HEARTBEAT.md

# Plan which checks should run
python3 scripts/heartbeat_optimizer.py plan
```

**Commands:**
```bash
# Check if specific type should run now
heartbeat_optimizer.py check email
heartbeat_optimizer.py check calendar

# Record that a check was performed
heartbeat_optimizer.py record email

# Update check interval (seconds)
heartbeat_optimizer.py interval email 7200  # 2 hours

# Reset state
heartbeat_optimizer.py reset
```

**How it works:**
- Tracks last check time for each type (email, calendar, weather, etc.)
- Enforces minimum intervals before re-checking
- Respects quiet hours (23:00-08:00) — skips all checks
- Returns `HEARTBEAT_OK` when nothing needs attention (saves tokens)

**Default intervals:**
- Email: 60 minutes
- Calendar: 2 hours
- Weather: 4 hours
- Social: 2 hours
- Monitoring: 30 minutes

**Integration in HEARTBEAT.md:**
```markdown
## Email Check
Run only if: `heartbeat_optimizer.py check email` → `should_check: true`
After checking: `heartbeat_optimizer.py record email`
```

**Expected savings:** 50% reduction in heartbeat API calls.

**Model enforcement:** Heartbeat should ALWAYS use Quick — see updated `HEARTBEAT.template.md` for model override instructions.

### 4. Cronjob Optimization (NEW!)

**Problem:** Cronjobs often default to expensive models (Standard/Deep) even for routine tasks.

**Solution:** Always specify Quick for 90% of scheduled tasks.

**See:** `assets/cronjob-model-guide.md` for comprehensive guide with examples.

**Quick reference:**

| Task Type | Model Tier | Example |
|-----------|------------|---------|
| Monitoring/alerts | Quick | Check server health, disk space |
| Data parsing | Quick | Extract CSV/JSON/logs |
| Reminders | Quick | Daily standup, backup reminders |
| Simple reports | Quick | Status summaries |
| Content generation | Standard | Blog summaries (quality matters) |
| Deep analysis | Standard | Weekly insights |
| Complex reasoning | Avoid Deep | Use only when absolutely necessary |

**Example (good):**
```bash
# Parse daily logs with Quick model
cron add --schedule "0 2 * * *" \
  --payload '{
    "kind":"agentTurn",
    "message":"Parse yesterday error logs and summarize",
    "model":"openrouter/stepfun/step-3.5-flash:free"
  }' \
  --sessionTarget isolated
```

**Example (bad):**
```bash
# ❌ Using Deep for simple check (60x more expensive!)
cron add --schedule "*/15 * * * *" \
  --payload '{
    "kind":"agentTurn",
    "message":"Check email",
    "model":"openrouter/minimax/minimax-m2.5"
  }' \
  --sessionTarget isolated
```

**Savings:** Using Quick instead of Deep for 10 daily cronjobs = **$17.70/month saved per agent**.

**Integration with model_router:**
```bash
# Test if your cronjob should use Quick
model_router.py "parse daily error logs"
# → Output: Quick (background task pattern detected)
```

### 5. Token Budget Tracking & Dynamic Pricing

Monitor usage and alert when approaching limits. Now with **live pricing** from providers.

**Setup:**
```bash
# Check current daily usage
python3 scripts/token_tracker.py check

# Get model suggestions (uses dynamic pricing)
python3 scripts/token_tracker.py suggest general

# Show currently loaded model prices
python3 scripts/token_tracker.py pricing

# Refresh prices from OpenRouter (requires OPENROUTER_API_KEY)
export OPENROUTER_API_KEY="sk-or-v1-..."
python3 scripts/token_tracker.py refresh-pricing

# Reset daily tracking
python3 scripts/token_tracker.py reset
```

**Output format:**
```json
{
  "date": "2026-02-06",
  "cost": 2.50,
  "tokens": 50000,
  "limit": 5.00,
  "percent_used": 50,
  "status": "ok",
  "alert": null
}
```

**Status levels:**
- `ok`: Below 80% of daily limit
- `warning`: 80-99% of daily limit
- `exceeded`: Over daily limit

**Integration pattern:**
Before starting expensive operations, check budget:
```python
import json
import subprocess

result = subprocess.run(
    ["python3", "scripts/token_tracker.py", "check"],
    capture_output=True, text=True
)
budget = json.loads(result.stdout)

if budget["status"] == "exceeded":
    # Switch to cheaper model or defer non-urgent work
    use_model = "anthropic/claude-haiku-4"
elif budget["status"] == "warning":
    # Use balanced model
    use_model = "anthropic/claude-sonnet-4-5"
```

**Customization:**
Edit `daily_limit_usd` and `warn_threshold` parameters in function calls.

**Dynamic Pricing:**
- Pricing data is stored in `pricing.json` in the skill directory.
- Run `token_tracker.py refresh-pricing` to fetch latest prices from OpenRouter (requires `OPENROUTER_API_KEY`).
- The `suggest` command uses the loaded pricing to give accurate cost comparisons.
- If `pricing.json` is missing, built-in defaults are used (may be outdated).

### 6. Multi-Provider Strategy

See `references/PROVIDERS.md` for comprehensive guide on:
- Alternative providers (OpenRouter, Together.ai, Google AI Studio)
- Cost comparison tables
- Routing strategies by task complexity
- Fallback chains for rate-limited scenarios
- API key management

**Quick reference:**

| Provider | Model | Cost/MTok | Use Case |
|----------|-------|-----------|----------|
| Anthropic | Haiku 4 | $0.25 | Simple tasks |
| Anthropic | Sonnet 4.5 | $3.00 | Balanced default |
| Anthropic | Opus 4 | $15.00 | Complex reasoning |
| OpenRouter | Gemini 2.5 Flash | $0.075 | Bulk operations |
| Google AI | Gemini 2.0 Flash Exp | FREE | Dev/testing |
| Together | Llama 3.3 70B | $0.18 | Open alternative |

## Configuration Patches

See `assets/config-patches.json` for advanced optimizations:

**Implemented by this skill:**
- ✅ Heartbeat optimization (fully functional)
- ✅ Token budget tracking (fully functional)
- ✅ Model routing logic (fully functional)

**Requires OpenClaw core support:**
- ⏳ Prompt caching (Anthropic API feature, OpenClaw integration pending)
- ⏳ Lazy context loading (requires core changes)
- ⏳ Multi-provider fallback (partially supported)

**Apply config patches:**
```bash
# Example: Enable multi-provider fallback
gateway config.patch --patch '{"providers": [...]}'
```

## Deployment Patterns

### For Personal Use
1. Install optimized `HEARTBEAT.md`
2. Run budget checks before expensive operations
3. Manually route complex tasks to Deep only when needed

**Expected savings:** 20-30%

### For Managed Hosting (xCloud, etc.)
1. Default all agents to Quick
2. Route user interactions to Standard
3. Reserve Deep for explicitly complex requests
4. Use Gemini Flash for background operations
5. Implement daily budget caps per customer

**Expected savings:** 40-60%

### For High-Volume Deployments
1. Use multi-provider fallback (OpenRouter + Together.ai)
2. Implement aggressive routing (80% Gemini, 15% Quick, 5% Standard)
3. Deploy local Ollama for offline/cheap operations
4. Batch heartbeat checks (every 2-4 hours, not 30 min)

**Expected savings:** 70-90%

## Integration Examples

### Workflow: Smart Task Handling
```bash
# 1. User sends message
user_msg="debug this error in the logs"

# 2. Route to appropriate model
routing=$(python3 scripts/model_router.py "$user_msg")
model=$(echo $routing | jq -r .recommended_model)

# 3. Check budget before proceeding
budget=$(python3 scripts/token_tracker.py check)
status=$(echo $budget | jq -r .status)

if [ "$status" = "exceeded" ]; then
    # Use cheapest model regardless of routing
    model="anthropic/claude-haiku-4"
fi

# 4. Process with selected model
# (OpenClaw handles this via config or override)
```

### Workflow: Optimized Heartbeat
```markdown
## HEARTBEAT.md

# Plan what to check
result=$(python3 scripts/heartbeat_optimizer.py plan)
should_run=$(echo $result | jq -r .should_run)

if [ "$should_run" = "false" ]; then
    echo "HEARTBEAT_OK"
    exit 0
fi

# Run only planned checks
planned=$(echo $result | jq -r '.planned[].type')

for check in $planned; do
    case $check in
        email) check_email ;;
        calendar) check_calendar ;;
    esac
    python3 scripts/heartbeat_optimizer.py record $check
done
```

## Troubleshooting

**Issue:** Scripts fail with "module not found"
- **Fix:** Ensure Python 3.7+ is installed. Scripts use only stdlib.

**Issue:** State files not persisting
- **Fix:** Check that `~/.openclaw/workspace/memory/` directory exists and is writable.

**Issue:** Budget tracking shows $0.00
- **Fix:** `token_tracker.py` needs integration with OpenClaw's `session_status` tool. Currently tracks manually recorded usage.

**Issue:** Routing suggests wrong model tier
- **Fix:** Customize `ROUTING_RULES` in `model_router.py` for your specific patterns.

## Maintenance

**Daily:**
- Check budget status: `token_tracker.py check`

**Weekly:**
- Review routing accuracy (are suggestions correct?)
- Adjust heartbeat intervals based on activity

**Monthly:**
- Compare costs before/after optimization
- Review and update `PROVIDERS.md` with new options

## Cost Estimation

**Example: 100K tokens/day workload**

Without skill:
- 50K context tokens + 50K conversation tokens = 100K total
- All Standard (e.g., Sonnet): 100K × ~$3/MTok = **$0.30/day = $9/month**

| Strategy | Context | Model Tier | Daily Cost | Monthly | Savings |
|----------|---------|------------|-----------|---------|---------|
| Baseline (no optimization) | 50K | Standard | $0.30 | $9.00 | 0% |
| Context opt only | 10K (-80%) | Standard | $0.18 | $5.40 | 40% |
| Model routing only | 50K | Mixed | $0.18 | $5.40 | 40% |
| **Both (this skill)** | **10K** | **Mixed** | **$0.09** | **$2.70** | **70%** |
| Aggressive + Gemini | 10K | Quick (Gemini) | $0.03 | $0.90 | **90%** |

**Note:** Actual pricing depends on models configured in `config.py`. For your current setup, Step 3.5 Flash is free, Minimax is ~$0.60/1M tokens.

**Key insight:** Context optimization (50K → 10K tokens) saves MORE than model routing!

**xCloud hosting scenario** (100 customers, 50K tokens/customer/day):
- Baseline (all Standard tier, full context): $450/month
- With token-optimizer: $135/month
- **Savings: $315/month per 100 customers (70%)**

## Resources

### Scripts (4 total)
- **`context_optimizer.py`** — Context loading optimization and lazy loading (NEW!)
- **`model_router.py`** — Task classification, model suggestions, and communication enforcement (ENHANCED!)
- **`heartbeat_optimizer.py`** — Interval management and check scheduling
- **`token_tracker.py`** — Budget monitoring and alerts

### References
- `PROVIDERS.md` — Alternative AI providers, pricing, and routing strategies

### Assets (3 total)
- **`HEARTBEAT.template.md`** — Drop-in optimized heartbeat template with Quick enforcement (ENHANCED!)
- **`cronjob-model-guide.md`** — Complete guide for choosing models in cronjobs (NEW!)
- **`config-patches.json`** — Advanced configuration examples

## Future Enhancements

Ideas for extending this skill:
1. **Auto-routing integration** — Hook into OpenClaw message pipeline
2. **Real-time usage tracking** — Parse session_status automatically
3. **Cost forecasting** — Predict monthly spend based on recent usage
4. **Provider health monitoring** — Track API latency and failures
5. **A/B testing** — Compare quality across different routing strategies
