---
name: agent-orchestration
description: 'Multi-agent orchestration patterns for production deployments. Covers sub-agent QC workflow, model staggering across 5+ models, cross-validation patterns, fallback chains, task routing by model strength, ACPX configuration, and cost optimization. Use when coordinating multiple agents or models for complex workflows. Do NOT use for single-agent prompting, prompt engineering, or fine-tuning — those are separate skills.'
license: MIT
metadata:
  openclaw:
    emoji: '🎭'
---

# Agent Orchestration

Production-tested patterns for coordinating multiple AI agents and models. This skill covers the full spectrum from simple fallback chains to complex multi-model workflows with cross-validation and quality control loops.

## When to Use

- Coordinating 2+ agents or models on a single workflow
- Building QC loops where one model checks another's work
- Routing tasks to the right model based on task type
- Setting up fallback chains for reliability
- Optimizing cost across subscription and API models
- Configuring ACPX (Agent Computer Protocol eXtended) for Claude Code and Codex
- Designing spawn patterns for runtime sub-agents

## When NOT to Use

- Single-agent prompting or prompt engineering (use a prompt-engineering skill)
- Fine-tuning or training models (different domain entirely)
- Simple API calls to one model (just call the API)
- RAG or retrieval pipeline design (use a RAG-specific skill)
- Agent memory architecture (use the agent-memory-architecture skill)

---

## 1. Sub-Agent QC Workflow

The core pattern: **Produce → Review → Cross-Check → Incorporate → Deliver**.

### The Five-Step Loop

```
┌─────────────┐
│  1. PRODUCE  │  Sonnet 4.6 generates first draft
│  (Grinder)   │  Fast, cost-effective, good enough for 80% of tasks
└──────┬──────┘
       ▼
┌─────────────┐
│  2. REVIEW   │  Same model self-reviews against criteria
│  (Self-QC)   │  Catches obvious errors, formatting issues
└──────┬──────┘
       ▼
┌─────────────┐
│  3. CROSS    │  Different model (GPT-4o / Grok) validates
│  CHECK       │  Catches blind spots, model-specific biases
└──────┬──────┘
       ▼
┌─────────────┐
│  4. INCORP.  │  Opus 4.6 synthesizes feedback
│  (Orchestr.) │  Resolves conflicts, applies judgment
└──────┬──────┘
       ▼
┌─────────────┐
│  5. DELIVER  │  Final output with confidence score
│  (Output)    │  Includes provenance trail
└─────────────┘
```

### Implementation Example

```python
async def qc_workflow(task: str, context: dict) -> dict:
    """Five-step QC workflow with cross-model validation."""

    # Step 1: Produce (Sonnet — fast, cheap)
    draft = await call_model(
        model="claude-sonnet-4-6",
        prompt=f"Complete this task:\n{task}",
        context=context,
        max_tokens=4096
    )

    # Step 2: Self-review (same model, different prompt)
    self_review = await call_model(
        model="claude-sonnet-4-6",
        prompt=f"""Review this output for errors, omissions, and quality:

TASK: {task}
OUTPUT: {draft}

Score 1-10 on: accuracy, completeness, clarity.
List specific issues to fix.""",
        max_tokens=1024
    )

    # Step 3: Cross-check (different model family)
    cross_check = await call_model(
        model="gpt-4o",
        prompt=f"""Independent review. Do NOT assume the draft is correct.

TASK: {task}
DRAFT: {draft}
SELF-REVIEW: {self_review}

Identify: factual errors, logical gaps, missing context, biases.""",
        max_tokens=1024
    )

    # Step 4: Incorporate (Opus — best judgment)
    final = await call_model(
        model="claude-opus-4-6",
        prompt=f"""Synthesize and produce final output.

TASK: {task}
DRAFT: {draft}
SELF-REVIEW: {self_review}
CROSS-CHECK: {cross_check}

Resolve any conflicts. Produce the best possible final output.
Include a confidence score (0-100) and list any unresolved concerns.""",
        max_tokens=4096
    )

    # Step 5: Deliver with metadata
    return {
        "output": final,
        "provenance": {
            "producer": "claude-sonnet-4-6",
            "reviewer": "claude-sonnet-4-6",
            "cross_checker": "gpt-4o",
            "synthesizer": "claude-opus-4-6",
            "steps_completed": 5
        }
    }
```

### When to Skip Steps

| Scenario | Skip | Rationale |
|----------|------|-----------|
| Low-stakes internal task | Steps 3-4 | Self-review is sufficient |
| Time-critical (<30s budget) | Steps 2-4 | Single model, accept risk |
| High-stakes client deliverable | None | Full loop, every time |
| Coding task with tests | Step 3 | Tests serve as cross-check |
| Creative/subjective work | Step 3 | Cross-check adds noise, not signal |

---

## 2. Model Staggering

Assign models to tasks based on their demonstrated strengths.

### The Model Roster

```
Model              Strength Zone              Cost Tier    Speed
────────────────────────────────────────────────────────────────
Opus 4.6           Strategy, synthesis,       $$$$$        Slow
                   complex reasoning,
                   judgment calls

Sonnet 4.6         Production work, coding,   $$$          Fast
                   analysis, writing,
                   general-purpose grinder

GPT-4o             Coding, scoring rubrics,   $$$$         Medium
                   structured output,
                   alternative perspective

Grok               X/Twitter analysis,        $$           Fast
                   social media content,
                   real-time commentary

Gemini 2.5 Pro     Deep research, long        $$$          Medium
                   context analysis,
                   multimodal processing

Haiku 4.5          Classification, routing,   $            Very Fast
                   simple extraction,
                   high-volume tasks
```

### Task Routing Rules

```yaml
routing_rules:
  # Strategic / High-judgment tasks → Opus
  strategy:
    models: [claude-opus-4-6]
    triggers:
      - "requires judgment between competing priorities"
      - "synthesize conflicting information"
      - "make a recommendation with tradeoffs"
      - "review and improve another agent's work"

  # Production work → Sonnet
  production:
    models: [claude-sonnet-4-6]
    triggers:
      - "write code to specification"
      - "generate content from template"
      - "analyze data and report findings"
      - "standard business communication"

  # Coding with scoring → GPT
  coding_and_scoring:
    models: [gpt-4o]
    triggers:
      - "write and debug complex algorithms"
      - "score outputs against rubric"
      - "generate structured JSON/YAML"
      - "cross-validate another model's output"

  # Social / real-time → Grok
  social:
    models: [grok-3]
    triggers:
      - "analyze X/Twitter trends"
      - "generate social media content"
      - "real-time event commentary"
      - "meme-aware communication"

  # Deep research → Gemini
  research:
    models: [gemini-2.5-pro]
    triggers:
      - "analyze documents >100K tokens"
      - "cross-reference multiple long sources"
      - "multimodal analysis (images + text)"
      - "broad research synthesis"

  # High-volume classification → Haiku
  classification:
    models: [claude-haiku-4-5]
    triggers:
      - "classify items into categories"
      - "extract structured fields from text"
      - "route incoming requests"
      - "simple yes/no decisions"
```

### Staggering in Practice

```
Example: "Write a market analysis report"

1. Gemini 2.5 Pro  → Research phase (long context, web search)
2. Sonnet 4.6      → Draft the report (fast production)
3. GPT-4o          → Score against quality rubric (structured eval)
4. Opus 4.6        → Final synthesis and executive summary (judgment)
5. Haiku 4.5       → Extract key metrics into structured JSON (cheap, fast)
```

---

## 3. Fallback Chains

When a model is unavailable, rate-limited, or returns low-quality output, fall through to the next option.

### Chain Configuration

```yaml
fallback_chains:
  # Primary reasoning chain
  reasoning:
    - model: claude-opus-4-6
      timeout: 60s
      retry: 1
    - model: gpt-4o
      timeout: 45s
      retry: 1
    - model: claude-sonnet-4-6
      timeout: 30s
      retry: 2
    - model: gemini-2.5-pro
      timeout: 45s
      retry: 1

  # Fast production chain
  production:
    - model: claude-sonnet-4-6
      timeout: 30s
      retry: 2
    - model: gpt-4o
      timeout: 30s
      retry: 1
    - model: grok-3
      timeout: 20s
      retry: 1

  # Classification chain (optimize for cost)
  classification:
    - model: claude-haiku-4-5
      timeout: 10s
      retry: 3
    - model: claude-sonnet-4-6
      timeout: 15s
      retry: 1
```

### Fallback Decision Logic

```python
async def call_with_fallback(chain: str, prompt: str) -> dict:
    """Try models in order until one succeeds with acceptable quality."""

    for entry in CHAINS[chain]:
        for attempt in range(entry["retry"] + 1):
            try:
                result = await call_model(
                    model=entry["model"],
                    prompt=prompt,
                    timeout=entry["timeout"]
                )

                # Quality gate: reject low-confidence outputs
                if result.get("confidence", 100) < 30:
                    log(f"{entry['model']} returned low confidence, trying next")
                    break  # Move to next model, don't retry

                return {
                    "output": result,
                    "model_used": entry["model"],
                    "attempt": attempt + 1,
                    "fallback_depth": CHAINS[chain].index(entry)
                }

            except (TimeoutError, RateLimitError) as e:
                log(f"{entry['model']} attempt {attempt+1} failed: {e}")
                continue

    raise AllModelsFailed(f"No model in chain '{chain}' produced acceptable output")
```

---

## 4. ACPX Configuration

ACPX (Agent Computer Protocol eXtended) enables tool-using agents to coordinate. Configuration for Claude Code and Codex environments.

### Claude Code Configuration

In your project's `CLAUDE.md`:

```markdown
# Agent Orchestration

## Sub-agent Spawning
When a task requires cross-model validation:
1. Use the Agent tool to spawn a sub-agent for the secondary task
2. The sub-agent inherits the project context but gets its own conversation
3. Results flow back to the orchestrator via the Agent tool response

## Model Selection
- Use claude-opus-4-6 for: architectural decisions, code review, complex debugging
- Use claude-sonnet-4-6 for: implementation, test writing, documentation
- Use claude-haiku-4-5 for: linting, formatting, simple refactors

## Tool Permissions
Sub-agents may: read files, search code, run tests
Sub-agents may NOT: push to git, modify CI/CD, delete files without confirmation
```

### ACP Server Setup

```json
{
  "mcpServers": {
    "orchestrator": {
      "command": "node",
      "args": ["./orchestrator-server.js"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "MAX_CONCURRENT_AGENTS": "5",
        "DEFAULT_CHAIN": "production"
      }
    }
  }
}
```

### Codex Integration

```yaml
# codex.yaml
agents:
  orchestrator:
    model: claude-opus-4-6
    role: "Route tasks and synthesize results"
    tools: [spawn_agent, review_output, merge_results]

  grinder:
    model: claude-sonnet-4-6
    role: "Execute implementation tasks"
    tools: [read_file, write_file, run_tests, search_code]

  validator:
    model: gpt-4o
    role: "Cross-validate outputs"
    tools: [read_file, run_tests, score_output]
```

---

## 5. Cost Optimization

### Subscription vs API Economics

```
Subscription Models ($20-200/month flat):
  Claude Pro/Max    → Best for: daily interactive use, long sessions
  ChatGPT Plus      → Best for: GPT-4o access, plugins
  Grok Premium      → Best for: X integration, real-time
  Gemini Advanced   → Best for: Google ecosystem, long context

API Models (per-token):
  claude-opus-4-6   → $15/M input, $75/M output
  claude-sonnet-4-6 → $3/M input, $15/M output
  claude-haiku-4-5  → $0.80/M input, $4/M output
  gpt-4o            → $2.50/M input, $10/M output
```

### $0 Marginal Cost Routing

When you have active subscriptions, route interactive and exploratory work through subscriptions (zero marginal cost) and reserve API for automated/batch workflows.

```
Decision Tree:
  Is this interactive/exploratory?
    YES → Route through subscription (Claude Code, ChatGPT, etc.)
    NO  → Is this batch/automated?
      YES → Use API with cheapest adequate model
      NO  → Is this high-volume (>1000 calls/day)?
        YES → Use Haiku via API ($0.80/M input)
        NO  → Use Sonnet via API ($3/M input)
```

### Cost Tracking Template

```
Monthly AI Spend:
  Subscriptions (fixed):
    Claude Max            $200.00
    ChatGPT Plus           $20.00
    Grok Premium           $30.00
    Gemini Advanced        $20.00
  Subtotal Fixed          $270.00

  API Usage (variable):
    Opus 4.6         42K tokens    $3.78
    Sonnet 4.6      380K tokens    $6.84
    Haiku 4.5     1.2M tokens      $1.76
    GPT-4o          95K tokens     $1.19
  Subtotal Variable                $13.57

  Total                           $283.57
  Cost per task (avg)               $0.28
  Tasks completed                  1,013
```

---

## 6. Spawn Patterns

### Pattern 1: Runtime Sub-Agent (Within Claude Code)

Use the `Agent` tool to spawn sub-agents that inherit project context.

```
Orchestrator (Opus)
  ├── Agent: "Research the API surface" (Explore subagent)
  ├── Agent: "Implement the endpoint" (general-purpose subagent)
  └── Agent: "Write tests" (general-purpose subagent)
```

Best for: tasks where sub-agents need file system access and project context.

### Pattern 2: API-Spawned Agent (External)

Call model APIs directly for tasks that don't need project context.

```python
# Spawn multiple validators in parallel
import asyncio

async def parallel_validate(content: str) -> list:
    tasks = [
        call_model("claude-sonnet-4-6", f"Review for accuracy:\n{content}"),
        call_model("gpt-4o", f"Review for accuracy:\n{content}"),
        call_model("gemini-2.5-pro", f"Review for accuracy:\n{content}"),
    ]
    return await asyncio.gather(*tasks)
```

Best for: cross-validation, scoring, classification — tasks that are self-contained.

### Pattern 3: Orchestrator-Grinder Split

The orchestrator plans and delegates. Grinders execute. Never let a grinder make strategic decisions.

```
ORCHESTRATOR (Opus 4.6):
  - Reads the task requirements
  - Breaks into subtasks
  - Assigns each subtask to appropriate grinder
  - Reviews grinder outputs
  - Synthesizes final deliverable
  - Makes judgment calls on conflicts

GRINDER (Sonnet 4.6 / GPT-4o):
  - Receives specific, scoped subtask
  - Executes without strategic decisions
  - Returns output with confidence score
  - Flags uncertainty rather than guessing
```

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Grinder makes strategic calls | Inconsistent decisions, wasted work | Escalate to orchestrator |
| Orchestrator does grinder work | Slow, expensive, bottleneck | Delegate production tasks |
| No quality gate between steps | Errors compound through pipeline | Add review step after each stage |
| Same model reviews its own work | Blind spots persist | Cross-model validation |
| Spawning agents for trivial tasks | Overhead exceeds task cost | Direct call for simple tasks |
| Infinite retry loops | Cost explosion | Max 3 retries, then escalate |

---

## 7. Orchestrator vs Grinder Principle

This is the foundational principle of multi-agent systems.

### The Rule

> **The orchestrator thinks. The grinder does. Never confuse the two.**

### Role Definitions

```
ORCHESTRATOR                          GRINDER
─────────────────────────────────     ─────────────────────────────────
Decides WHAT to do                    Decides HOW to do it
Chooses which model/tool              Uses the tools it's given
Reviews and judges quality            Produces and reports confidence
Resolves conflicts between agents     Flags conflicts for resolution
Owns the final output                 Owns its subtask output
Expensive, slow, high-judgment        Cheap, fast, high-throughput
1 per workflow                        N per workflow
```

### Decision Framework

```
"Should this be an orchestrator or grinder decision?"

Ask: "If two reasonable people disagreed on this, would it matter?"
  YES → Orchestrator decision (judgment required)
  NO  → Grinder decision (execution, not judgment)

Ask: "Does this affect the overall workflow direction?"
  YES → Orchestrator decision
  NO  → Grinder decision

Ask: "Could a junior employee do this with clear instructions?"
  YES → Grinder task
  NO  → Orchestrator task
```

### Example Workflow: Client Deliverable

```
ORCHESTRATOR (Opus):
  1. Read client brief → decide deliverable structure
  2. Break into sections → assign to grinders
  3. Review all sections → identify gaps
  4. Resolve quality issues → request rewrites
  5. Synthesize → produce final deliverable
  6. Generate executive summary → deliver

GRINDER 1 (Sonnet): Write Section A per outline
GRINDER 2 (Sonnet): Write Section B per outline
GRINDER 3 (GPT-4o): Generate data tables and charts
GRINDER 4 (Gemini): Research background for Section C
GRINDER 5 (Haiku): Format citations and references
```

Total cost: 1 Opus call (synthesis) + 5 cheaper calls (production)
vs. doing everything in Opus: 6 Opus calls at 5x the cost.
