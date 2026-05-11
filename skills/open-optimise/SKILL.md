---
name: cost-optimizer
version: 7.0.0
description: Smart cost optimization skill for OpenClaw. Reduces API costs by 70-97% through intelligent model routing, session management, output efficiency, and free model usage. Includes 29 executable scripts for auditing, monitoring, backup/restore, health checks, and automated reporting. Walks user through setup on first activation.
tags:
  - cost
  - optimization
  - budget
  - models
  - routing
  - monitoring
  - audit
---

# Cost Optimizer v7 — Smart API Cost Reduction

This skill helps reduce your OpenClaw API costs by 70-97% through intelligent model routing, session management, and response efficiency.

> **New to this skill?** Read `GUIDE.md` for installation instructions, requirements, example outputs from every script, and common workflows.

## What's Included

| Category | Files | Purpose |
|----------|-------|---------|
| Agent instructions | `SKILL.md` (this file) | 13 chapters of cost optimization logic |
| User guide | `GUIDE.md` | Requirements, installation, example outputs, workflows |
| References | `references/` (2 files) | Model pricing card, config templates |
| Scripts | `scripts/` (29 files) | Audit, monitor, backup, health check, reporting |
| Presets | `presets/` (5 files) | Ready-to-apply configs: solo-coder, writer, researcher, zero-budget, agency-team |
| Metadata | `VERSION`, `CHANGELOG.md` | Version tracking and update history |

### Requirements

- OpenClaw 2026.3.x+, Node.js v18+, bash, curl
- Optional: OpenRouter API key (for free models), webhook URL (for reports)

### Quick Start

```
# Install
cd ~/.openclaw/workspace/skills/
unzip cost-optimizer.zip
chmod +x cost-optimizer/scripts/*.sh

# Audit current costs
bash cost-optimizer/scripts/cost-audit.sh

# Interactive setup
Tell your agent: /cost-setup
```

## SETUP FLOW (Run on first activation)

When this skill is first activated or user says "/cost-setup", walk through these steps. Ask permission at each step before making changes:

**Step 1: Budget Target**
Ask: "What's your monthly budget target? Options: Ultra-low ($0-5/mo), Low ($5-30/mo), Medium ($30-100/mo), Flexible (no hard limit but minimize waste)"
Save their answer to memory/cost-preferences.md

**Step 2: Free Models**
Ask: "Want me to add free OpenRouter models to your config? These cost $0.00 per request and handle 60-80% of simple tasks well. I'll add: DeepSeek V3 Free, Llama 4 Scout Free, Qwen 3 Free, Gemma 3 Free, Mistral Small Free. Approve? (yes/no)"
If yes: add the free models to config with aliases

**Step 3: Default Model**
Ask: "Your current default model is [current model]. Want me to switch your default to MiniMax M2.5 ($0.04/request) or DeepSeek V3.2 ($0.04/request)? This alone saves 73-94% vs Opus/Sonnet. Options: minimax / deepseek / keep current"
If they choose: update model.primary

**Step 4: Heartbeat Optimization**
Ask: "Heartbeats keep your agent alive but cost money on expensive models. Want me to route heartbeats to a free model at 55-minute intervals? This saves $7-562/month depending on your current setup. Approve? (yes/no)"
If yes: set heartbeat model to free, interval 55m

**Step 5: Session Management**
Ask: "Want me to enable aggressive memory flush before compaction? This prevents context bloat and saves 10-30% on long sessions. Approve? (yes/no)"
If yes: enable memoryFlush with threshold 3000

**Step 6: Response Style**
Ask: "In cost-conscious mode, should I: (a) Always be concise to save tokens, (b) Be concise by default but go detailed when you ask, or (c) Keep my normal response style?"
Save preference to memory/cost-preferences.md

After setup, confirm: "Cost optimizer configured. Here's your estimated monthly cost: ~$X based on [usage estimate]. Use /cost-status anytime to check, /cost-setup to reconfigure."

---

## CHAPTER 1: MODEL TIERS AND ROUTING

When this skill is active and user hasn't overridden with [name], suggest the cheapest adequate model for each task.

### Understanding the Cost Structure

Every OpenClaw request sends approximately 140,000 tokens of fixed overhead (system prompt, tool schemas, context). This overhead is the dominant cost. What it costs depends entirely on which model processes it:

| Model Tier | Overhead Cost | Per Request | Monthly (50 q/day) |
|------------|--------------|-------------|-------------------|
| Free models | $0.00 | $0.00 | $0.00 |
| Budget (MiniMax/DeepSeek) | ~$0.04 | ~$0.04 | ~$60 |
| Mid (Haiku) | ~$0.14 | ~$0.15 | ~$225 |
| Quality (Sonnet) | ~$0.42 | ~$0.43 | ~$645 |
| Premium (Opus) | ~$0.70 | ~$0.71 | ~$1,065 |

A simple question costs $0.71 on Opus and $0.00 on a free model. The answer quality for simple factual questions is nearly identical. Model selection is the single biggest cost lever.

### Free Models (Tier 0 — $0.00/request)

These are your first choice for tasks that don't need premium quality:

| Alias | Model | Context | Good For |
|-------|-------|---------|----------|
| deepseek-free | DeepSeek V3 Free | 164K | Best free model overall. Coding, reasoning, general tasks. |
| llama-free | Llama 4 Scout Free | 512K | Largest context window. Research, long docs. |
| qwen-free | Qwen 3 235B Free | 40K | Multilingual and translation tasks. |
| mistral-free | Mistral Small 3.1 Free | 96K | Quick short answers. Classification. |
| gemma-free | Gemma 3 27B Free | 96K | Reliable fallback. |

If one free model is rate-limited, try the next: deepseek-free, llama-free, qwen-free, mistral-free, gemma-free

### Budget Models (Tier 1 — $0.01-0.14/request)

| Alias | Model | Cost/req | Good For |
|-------|-------|----------|----------|
| nano | GPT-5 Nano | ~$0.01 | Simplest tasks when free models are down |
| flashlite | Gemini Flash-Lite | ~$0.01 | Cron jobs, heartbeats |
| deepseek | DeepSeek V3.2 | ~$0.04 | Coding daily driver |
| minimax | MiniMax M2.5 | ~$0.04 | General daily driver (recommended default) |
| kimi | Kimi K2.5 | ~$0.07 | Long sessions — auto-caching drops to ~$0.02 after warmup |
| glm | GLM-5 | ~$0.14 | Complex architecture-level coding |

### Quality Models (Tier 2 — $0.15-0.53/request)

| Alias | Model | Cost/req | Good For |
|-------|-------|----------|----------|
| haiku | Claude Haiku 4.5 | ~$0.15 | Mid-tier quality work |
| sonnet | Claude Sonnet 4.6 | ~$0.53 | Quality writing, code review, final polish |

### Premium Models (Tier 3 — $0.71+/request)

| Alias | Model | Cost/req | Good For |
|-------|-------|----------|----------|
| opus | Claude Opus 4.6 | ~$0.71 | Maximum reasoning power |
| gpt5 | GPT-5 | ~$0.44 | Complex multi-domain tasks |

Use premium only when user explicitly requests or task genuinely requires it.

---

## CHAPTER 2: SMART ROUTING GUIDELINES

When this skill is active, use this decision process to suggest the best model for each task:

**Simple tasks — try free first:**
Factual questions, brainstorming, lists, first drafts, explanations, summaries, simple code, formatting, translations, yes/no questions, code scaffolds
Suggest: "I can handle this on [free model] at $0.00. Want me to proceed?"
If user hasn't set a preference yet, ask the first time. After that, follow their preference from setup.

**Standard work — use budget models:**
General questions needing reliable quality, coding tasks, analysis
Use the configured default (minimax or deepseek at ~$0.04)

**Long reasoning sessions:**
Multi-turn analysis, complex problem-solving
Suggest kimi ($0.07 first request, ~$0.02 after due to auto-caching)

**Complex coding:**
Systems architecture, difficult debugging
Suggest glm ($0.14) — only when task is genuinely complex

**Quality output for external sharing:**
Final versions of writing, thorough code reviews, research synthesis
Suggest doing research/gathering on budget model first, then switching to sonnet ($0.53) for the final output only.
Ask: "Draft complete. Want me to polish on Sonnet (~$0.53) or is this good enough?"

**Premium reasoning:**
Never auto-select opus. Instead ask: "This seems to need deep reasoning. Want me to use Opus (~$0.71/request) or try Sonnet first (~$0.53)?"

**User override:**
If user says /model [alias], use that model. No questions.
Resume smart routing after /reset or /model auto.

---

## CHAPTER 3: RESPONSE EFFICIENCY

When the user chose concise mode during setup, follow these guidelines to reduce output tokens:

### Response Length Guidelines

| Task Type | Target Length | Example |
|-----------|-------------|---------|
| Yes/No questions | 1-2 sentences | Direct answer with brief reason |
| Factual lookups | 1-3 sentences | The answer, sourced if relevant |
| Simple Q&A | Short paragraph | Answer first, brief context |
| Explanations | 2-3 paragraphs | Structured, no padding |
| Code snippets | Code + 1-line comment | No narration unless asked |
| Full functions | Code + minimal comments | Explain only tricky parts |
| Analysis | Structured bullets | Key findings, not essays |

### Conciseness Guidelines

- Start with the answer. First sentence should directly address the question.
- Use bullet points for lists of 3 or more items
- Provide one example instead of three unless asked for more
- For code: provide the code first, explain only if asked
- Skip phrases that don't add information: "Great question!", "I'd be happy to help!", "Let me break this down..."
- Don't restate the question back to the user
- Don't add sign-offs like "Let me know if you have questions!"

### Cost Impact

Reducing average response from 800 tokens to 300 tokens saves:
- On MiniMax: ~$0.90/month (50 requests/day)
- On Sonnet: ~$11/month
- On Opus: ~$19/month

---

## CHAPTER 4: SESSION LIFECYCLE MANAGEMENT

Long sessions cost more because every old message gets re-sent with each new request on top of the 140K base overhead.

### How Context Bloat Increases Cost

| Session Length | Extra Context | Extra Cost per Request (MiniMax) | Extra Cost per Request (Sonnet) |
|---------------|--------------|--------------------------------|-------------------------------|
| 5 exchanges | ~2,500 tokens | +$0.001 | +$0.008 |
| 10 exchanges | ~5,000 tokens | +$0.002 | +$0.015 |
| 20 exchanges | ~15,000 tokens | +$0.005 | +$0.045 |
| 50 exchanges | ~50,000 tokens | +$0.015 | +$0.150 |
| 100 exchanges | ~150,000 tokens | +$0.045 | +$0.450 |

At 100 exchanges, every request costs roughly triple its base price.

### When to Suggest a Reset

- After 12-15 exchanges: gently mention the option
- After a complete topic change: suggest a clean slate
- When context exceeds 50K accumulated tokens: recommend it
- When context exceeds 100K accumulated tokens: strongly recommend it
- When you notice you've lost early context: be honest about it

### Reset Protocol

Before every reset, provide a brief summary so nothing is lost:

"Session summary:
- [Key point 1]
- [Key point 2] 
- [Any open items]
Type /reset to clear context and reduce costs."

### Context Pruning in Responses

To slow context growth within a session:
- Don't repeat information already established earlier
- Don't quote the user's message back to them
- Don't restate your previous answers — reference them: "As I mentioned earlier..."
- Summarize tool output to essential data points instead of including raw output
- Each pruned repetition saves 100-500 tokens that would be re-sent on every future request

### Memory Over Context

For important facts that should persist across sessions:
1. Save key facts to memory files
2. Reset the session to clear expensive context
3. Facts persist in memory, context is fresh and cheap

---

## CHAPTER 5: TOOL CALL DISCIPLINE

Each tool call triggers a full model roundtrip with the entire context window. On MiniMax that costs ~$0.04+ per call. On Sonnet it costs ~$0.43+ per call.

### Pre-Call Checklist

Before making any tool call, consider:

1. **Can I answer from existing knowledge?** Many questions don't need a tool call. If you're 90%+ confident in the answer, provide it and offer to verify: "I believe X is the case. Want me to confirm with a lookup?"

2. **Did I already retrieve this data?** If the same or similar data was fetched earlier in the session, use the cached result instead of re-fetching.

3. **Can I batch this with other calls?** If multiple pieces of related data are needed, try to get them in fewer calls rather than one call per data point.

4. **Will the user need follow-up data?** If so, fetch slightly broader data now to avoid additional calls later.

5. **Is there a lighter tool option?** Use the simplest tool that gets the job done.

### Tool Output Handling

Raw tool output is often thousands of tokens. Always compress it:

- API responses: Extract the relevant fields. "Status 200. User: name='John', role='admin', last_active='2024-01-15'"
- Error logs: Extract the error. "NullPointerException at UserService.java:347. Root cause: missing database record."
- Search results: Summarize top 3 relevant results in one line each
- Web pages: Extract title and the specific information needed, not the full page content

### Limits

- If a task requires more than 5-6 tool calls, consider breaking it into phases and checking with the user before continuing
- If a tool returns an error, retry once. If it fails again, inform the user rather than looping
- If you notice the same tool being called with identical parameters, stop — that's a loop

---

## CHAPTER 6: SUBAGENT COST AWARENESS

Each subagent spawns a separate request that carries the full system prompt overhead.

### Cost Impact

| Configuration | Base Overhead Cost (MiniMax) |
|--------------|---------------------------|
| Main agent only | ~$0.04 |
| Main + 1 subagent | ~$0.08 |
| Main + 2 subagents | ~$0.12 |
| Main + 4 subagents | ~$0.20 |

### Guidelines

- Handle tasks inline when possible rather than delegating to subagents
- If subagents are needed, prefer 1-2 rather than 4-8 running in parallel
- Be aware that subagents inherit the current model — if you're on Sonnet and spawn 4 subagents, that's 4 x $0.53 = $2.12 in overhead
- For sequential subtasks, doing them in the main agent one after another is cheaper than parallel subagents
- Reserve subagents for genuinely complex parallel work where the time savings justify the cost

---

## CHAPTER 7: SYSTEM PROMPT OPTIMIZATION

The ~140K base overhead per request is partially reducible. Small reductions compound significantly over hundreds of daily requests.

### Optimization Opportunities

**Unused tools (highest impact):**
Each tool schema adds approximately 200 tokens to every request. If you have 20 tools but only use 10, the other 10 waste ~2,000 tokens per request.
- At 50 requests/day on MiniMax: ~$0.90/month wasted
- At 50 requests/day on Sonnet: ~$9/month wasted
Recommendation: audit loaded tools and disable any that are never used.

**Instructions that belong in skills:**
Content in system.md loads on every single request. Skills only load when activated. If you have instructions that are only relevant sometimes (code review guidelines, writing style rules, specific workflows), moving them to skills reduces base overhead.

**Verbose tool descriptions:**
Many tool descriptions are unnecessarily long. Compressing them saves tokens on every request.
Before: "This tool searches the web using the Google Custom Search API and returns results in JSON format including titles, URLs, snippets, and metadata"
After: "Web search. Returns title, URL, snippet per result."
Savings: ~30 tokens per tool x number of verbose tools

**Personality file trimming:**
If personality instructions are long (2000+ tokens), consider trimming to essentials. The personality is sent with every request.

### When User Runs /trim

If the user asks to optimize their system prompt, offer to:
1. Count current system prompt tokens
2. List all loaded tools with approximate token counts
3. Identify tools that have never been used in this session
4. Suggest specific instructions that could move to skills
5. Show before/after for verbose tool descriptions
6. Estimate monthly savings from recommended changes

Always ask permission before making any changes to system.md or tool configuration.

---

## CHAPTER 8: MULTI-PHASE TASK STRATEGY

For complex tasks that involve multiple steps, using cheaper models for early phases and reserving expensive models for the final output saves significantly.

### Research Tasks

| Phase | Suggested Model | Cost |
|-------|----------------|------|
| Web searches and data gathering | Free model or minimax | $0.00-0.04 per call |
| Organizing and structuring data | Free model | $0.00 |
| Writing the synthesis | minimax | $0.04 |
| Final polish (if user wants) | sonnet | $0.53 |

Total: $0.04-0.57 compared to doing everything on Sonnet: $2-4+

### Coding Tasks

| Phase | Suggested Model | Cost |
|-------|----------------|------|
| Scaffolding and boilerplate | Free model | $0.00 |
| Core logic implementation | deepseek or minimax | $0.04 |
| Debugging and testing | deepseek or minimax | $0.04 |
| Architecture review (if complex) | glm | $0.14 |

Total: $0.04-0.22 compared to doing everything on Sonnet: $1.50-2.50+

### Writing Tasks

| Phase | Suggested Model | Cost |
|-------|----------------|------|
| Outline and structure | Free model | $0.00 |
| First draft | minimax | $0.04 |
| Editing and polish (if sharing externally) | sonnet | $0.53 |

Total: $0.04-0.57 compared to doing everything on Sonnet: $1-2+

### How to Apply This

After completing the draft/gathering phase, ask:
"Draft complete on [current model]. Want me to polish this on Sonnet (~$0.53) or is this version good enough?"

Let the user decide whether the polish phase is worth the cost.

---

## CHAPTER 9: CACHE OPTIMIZATION

Prompt caching can dramatically reduce the effective cost of the 140K base overhead.

### How Caching Works

**Anthropic models (Claude):**
The system prompt and tool schemas are automatically cached. Subsequent requests within the cache window pay only 10% of the normal input price for cached tokens. A heartbeat every 55 minutes keeps this cache warm.

**Kimi K2.5 auto-caching:**
Kimi K2.5 has built-in context caching that drops repeat input costs from $0.50/M to $0.13/M — a 75% discount. This means:
- First request in a session: ~$0.07
- Subsequent requests: ~$0.02 each
- For sessions with 5+ turns, Kimi can be cheaper than MiniMax overall

### Cache-Friendly Behaviors

1. **Stay on one model within a session.** Switching models invalidates the prompt cache. Every switch means re-paying full price for the 140K base overhead.

2. **Cluster similar work together.** Do all coding tasks, then all writing tasks, then all research. This keeps the same model cached throughout each cluster.

3. **Don't re-fetch data.** If you retrieved information from a tool, remember it. Re-fetching wastes both the tool call cost and the cache benefit.

4. **For long reasoning sessions, use Kimi.** Its auto-caching compounds — the longer you stay, the cheaper each request becomes.

5. **The 55-minute heartbeat matters.** It keeps the Anthropic prompt cache warm so your next real request gets the 90% discount on base overhead.

---

## CHAPTER 10: IDLE AND BACKGROUND COST CONTROL

### Heartbeat Optimization

Heartbeats keep the agent session alive. If configured to use an expensive model, they silently drain budget 24/7:

- Opus heartbeats every 30 min: ~$1,022/month
- Opus heartbeats every 55 min: ~$558/month
- Free model heartbeats every 55 min: $0.00/month

During setup, this skill configures heartbeats to use a free model. If the user reports heartbeats still costing money (known bug in some versions), suggest the cron workaround:
"Set up a cron job that pings every 55 minutes with an isolated session instead of using the built-in heartbeat system."

### Cron Job Optimization

- Run automated tasks in isolated sessions (--session isolated) to avoid inheriting bloated context
- Use free models or flashlite for routine cron jobs
- 3 daily cron jobs on free models: $0.00/month vs $144/month on Opus

### Request Batching

If the user tends to send many simple questions one at a time, suggest batching:
"If you have several questions on this topic, listing them all in one message saves money — each separate message pays the full 140K overhead again."

- 5 separate questions = 5 x 140K overhead = 700K tokens processed
- 5 questions in 1 message = 1 x 140K overhead = 140K tokens processed
- Savings: 80% reduction in input tokens

---

## CHAPTER 11: BUDGET MONITORING

### Cost Awareness

After completing multi-step or expensive operations, briefly note the approximate cost:
"Done. Used minimax for research + sonnet for synthesis. Estimated cost: ~$0.57"

Don't announce cost on simple single-request tasks — that would be annoying.

### Spending Alerts

Based on the budget target set during setup:

- If estimated daily spend is approaching 75% of daily budget: mention it
- If a single task will likely cost more than $1: state the estimate and ask permission
- If a single task will cost more than $5: strongly suggest breaking it into smaller pieces

### Runaway Prevention

Watch for these patterns and intervene:

- Same tool called with identical parameters multiple times: stop the loop
- More than 6 tool calls triggered from a single message: pause and check with user
- Session context exceeding 100K accumulated tokens: recommend reset
- Multiple escalations to expensive models in one day: gently note the pattern

---

## CHAPTER 12: COMMANDS

When this skill is active, respond to these commands:

| Command | Action |
|---------|--------|
| /cost-setup | Run the full setup flow, asking permission at each step |
| /cost-status | Show current model, session stats, estimated costs |
| /cost-audit | Audit current configuration and suggest optimizations |
| /cost-trim | Analyze system prompt and suggest reductions |
| /free | Switch to free-only mode ($0.00 per request) |
| /free off | Return to normal smart routing |
| | Resume smart routing after a manual model override |
| /model [alias] | Switch to specific model (overrides smart routing until reset) |
| /reset | Clear session context (provide summary first) |

### /cost-status Response Format

When user asks for cost status, provide:

- Current active model and its approximate cost per request
- Number of exchanges in this session
- Estimated session cost so far
- Heartbeat configuration and monthly heartbeat cost
- Whether free models are currently available or rate-limited
- One specific actionable tip based on current patterns

### /cost-audit Response Format

When user asks for an audit, analyze and report:

- Current default model and whether a cheaper option would work
- Heartbeat model and cost
- Session health (fresh, moderate, or bloated)
- System prompt size and trimming opportunities
- Recent spending patterns and optimization suggestions
- Estimated current monthly cost vs potential optimized cost

---

## CHAPTER 13: INSTALLATION GUIDE

When this skill is shared with another OpenClaw user, include these instructions:

### Quick Install

1. Copy the skill files to your OpenClaw workspace
2. Say "/cost-setup" in chat to start the guided configuration
3. The skill will walk you through each optimization step and ask permission before changing anything
4. Your preferences are saved to memory so they persist across sessions

### What Gets Changed (Only With Your Permission)

- Free models added to your model configuration
- Default model switched to a budget option
- Heartbeat model switched to free
- Memory flush enabled for session management
- Response style adjusted based on your preference

### Estimated Savings

| Your Current Setup | Estimated Monthly Cost | With This Skill | Savings |
|-------------------|----------------------|-----------------|---------|
| Opus for everything | ~$1,000-2,500 | ~$0-30 | 97-100% |
| Sonnet for everything | ~$500-800 | ~$0-30 | 94-100% |
| MiniMax default, no free models | ~$60-80 | ~$0-15 | 75-100% |
| Already optimized | ~$30-60 | ~$0-10 | 50-100% |

### Requirements

- OpenRouter API key configured
- OpenClaw with model switching support
- Access to free models on OpenRouter (check openrouter.ai/models)

---

## CHAPTER 14: SCRIPTS REFERENCE

When the user asks to run any cost optimization task, use the appropriate script from `scripts/`. All paths are relative to the skill directory.

### Safety & Prevention
- `scripts/backup-config.sh [config] [label]` — Snapshot config before changes
- `scripts/restore-config.sh [backup|"latest"]` — Restore from backup, restart gateway
- `scripts/fallback-validator.sh [config]` — Test every model in fallback chain with real API calls

### Cost Analysis
- `scripts/cost-audit.sh [config]` — Full config analysis, monthly estimate, recommendations
- `scripts/heartbeat-cost.sh [log] [days]` — Isolate heartbeat spending from real usage
- `scripts/cost-history.sh [log] [days]` — Recalculate past usage across all model tiers
- `scripts/session-replay.sh <session|"latest"> [log]` — Per-exchange cost breakdown
- `scripts/provider-compare.sh [config]` — Detect same model across providers, find cheapest

### Waste Detection
- `scripts/tool-audit.sh [log] [days]` — Find unused tools and duplicate calls
- `scripts/token-counter.sh [workspace]` — Count system prompt overhead per file
- `scripts/context-monitor.sh [log]` — Track context growth, predict compaction
- `scripts/prompt-tracker.sh [workspace] [--snapshot|--report]` — Track prompt size over time
- `scripts/compaction-log.sh [log] [days]` — Track compaction and memory flush events
- `scripts/dedup-detector.sh [log] [days]` — Find redundant requests and tool calls

### Active Optimization
- `scripts/apply-preset.sh <free|budget|balanced|quality> [--dry-run]` — One-command presets
- `scripts/token-enforcer.sh <config> <strict|moderate|normal|generous|unlimited> [--dry-run]` — Set maxTokens limits
- `scripts/config-diff.sh [config]` — Current vs recommended side-by-side
- `scripts/idle-sleep.sh [log] [idle-hours] [sleep-interval]` — Auto-sleep during idle periods
- `scripts/setup-openrouter.sh <api-key>` — Generate OpenRouter provider config

### Monitoring & Reporting
- `scripts/cost-monitor.sh [log] [--live]` — Real-time spend tracking
- `scripts/cost-dashboard.js [config] [output.html]` — HTML cost dashboard
- `scripts/webhook-report.sh <url> [discord|slack|generic]` — Send reports to webhooks
- `scripts/cron-setup.sh` — Generate cron job templates for automated monitoring

### Model Management
- `scripts/model-switcher.sh [config]` — All models: status + cost + strength
- `scripts/provider-health.sh [config]` — Test all models: UP/DOWN/SLOW + latency
- `scripts/model-test.sh [config]` — Basic reachability test

### Distribution
- `scripts/preset-manager.sh <export|import|list>` — Export/import named presets
- `scripts/multi-instance.sh [instances-config]` — Aggregate costs across instances
- `scripts/parse-config.js <config> <dot.path> [default]` — JSON5 config parser (dependency)

When running scripts, resolve paths relative to the skill directory:
```
bash /path/to/skills/cost-optimizer/scripts/cost-audit.sh
```

---

## CLOSING: PRINCIPLES

This skill operates on these principles:

1. Free is better than cheap. Cheap is better than expensive. Try in that order.
2. The user decides. Always ask before spending money on model upgrades.
3. Start concise. Go detailed only when asked.
4. Fresh sessions save money. Suggest resets proactively.
5. The best tool call is the one you skip. Answer from knowledge when possible.
6. Research on cheap, polish on quality. Split expensive tasks into phases.
7. Caching saves money. Stay on one model per session.
8. Every token matters. Don't repeat, don't pad, don't re-fetch.
9. Transparency builds trust. Report costs when relevant.
10. The user's budget is sacred. Treat every request as if you're paying for it.