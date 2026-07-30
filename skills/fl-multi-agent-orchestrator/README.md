# Multi-Agent Orchestrator

> Production-grade orchestration patterns for running multiple AI agents in parallel. Battle-tested on real codebases with 20-50 concurrent agents.

## What It Does

Multi-Agent Orchestrator gives your AI assistant the knowledge to decompose complex tasks into subtasks, spawn multiple agents, coordinate their execution, handle failures, and aggregate results — all without you writing orchestration code.

Instead of asking one agent to do everything sequentially, you get:
- **5x faster execution** via parallel agent spawning
- **Higher quality** via specialized agents (coder, reviewer, tester)
- **Cost control** via smart model selection (Opus plans, Haiku executes)
- **Reliability** via retry logic, budget enforcement, and quality gates

## Why This One

There are 17 skills in the "Agent-to-Agent Protocols" category. Here's why this one is different:

| Feature | Generic Skills | Multi-Agent Orchestrator |
|---------|---------------|--------------------------|
| Patterns | "Use multiple agents" | 4 battle-tested patterns with implementation details |
| Error handling | None or basic | Retry, fallback, partial success, budget enforcement |
| Cost optimization | Use one model | Model selection strategy (Opus for planning, Haiku for work) |
| File conflicts | Not addressed | Pessimistic file locking with conflict detection |
| Templates | None | 4 ready-to-use templates for common workflows |
| Real examples | Theoretical | Extracted from systems running 20-50 agents in production |

**Source material:** Patterns extracted from [claude-swarm](https://github.com/affaan-m/claude-swarm) (hackathon winner), [claude_code_agent_farm](https://github.com/mckaywrigley/claude_code_agent_farm) (50-agent parallel orchestration), and [TubeFlow](https://github.com/webnestify/tubeflow) (5-agent research pipeline). These aren't theoretical — they run in production.

## Quick Start

Install the skill:
```
openclaw install multi-agent-orchestrator
```

Then ask your AI agent:
```
"I need to refactor our auth module, update tests, and review the changes.
Use the multi-agent orchestrator to parallelize this."
```

The agent will:
1. Decompose your task into a dependency graph
2. Choose the right orchestration pattern (swarm, pipeline, fan-out, or review cycle)
3. Spawn agents with focused prompts and minimal tool sets
4. Coordinate execution with file locking and budget tracking
5. Run a quality gate on the combined output
6. Deliver a structured report

## 4 Orchestration Patterns

### 1. Fan-Out / Fan-In
Multiple agents research or process in parallel, results aggregated at the end.
```
Task ──► [Agent A, Agent B, Agent C] ──► Aggregator ──► Result
```
**Best for:** Research, data gathering, analysis across multiple domains.

### 2. Sequential Pipeline
Each stage feeds into the next. Assembly-line processing.
```
Task ──► Generate ──► Review ──► Fix ──► Test ──► Result
```
**Best for:** Content creation, code generation with review, ETL workflows.

### 3. Swarm
Autonomous agents work on a shared codebase with coordination.
```
Wave 1: [coder-1, coder-2, coder-3]  (parallel, file-locked)
Wave 2: [tester]                       (depends on wave 1)
Wave 3: [reviewer]                     (depends on wave 2)
```
**Best for:** Large refactors, multi-file changes, codebase-wide improvements.

### 4. Review Cycle
Iterative build-review-fix loop until quality threshold is met.
```
Builder ──► Reviewer ──► (pass?) ──► Result
                │ (fail)
                └──► Builder (with feedback) ──► Reviewer ──► ...
```
**Best for:** Quality-critical outputs, code that must pass review, polished content.

## What's Included

```
multi-agent-orchestrator/
  SKILL.md                          # Core skill (agent instructions + all patterns)
  README.md                         # This file
  templates/
    parallel-research.md            # Fan-out template for research tasks
    pipeline.md                     # Sequential pipeline template
    swarm.md                        # Autonomous swarm with file locking
    review-cycle.md                 # Build-review-fix loop template
```

## Pricing

| | Free | Pro ($19/month) |
|---|---|---|
| Max agents per orchestration | 3 | Unlimited |
| Patterns | Fan-Out, Pipeline | All 4 (+ Swarm, Review Cycle) |
| Templates | parallel-research.md | All 4 templates |
| Error handling | Basic retry | Full (retry, fallback, partial success, budget enforcement) |
| Quality gates | -- | Opus-powered review cycle |
| Model selection strategy | -- | Full cost optimization guide |
| Priority support | -- | Discord + email |

## Use Cases

**Software Development:**
- Refactor a large codebase with 20+ agents working on different modules simultaneously
- Run code review cycles that catch bugs before they ship
- Generate code, tests, and documentation in parallel

**Research & Analysis:**
- Fan-out 5 agents to research competitors, SEO, community, pricing, and trends simultaneously
- Pipeline: gather data, analyze, synthesize, format report

**Content Creation:**
- Parallel research (5 agents) then sequential creation pipeline (research, write, review, publish)
- Review cycle for polished output (write, review, revise until quality bar is met)

**DevOps & Infrastructure:**
- Swarm of agents auditing security, performance, and code quality across a monorepo
- Pipeline for deployment: lint, test, build, deploy, verify

## Technical Details

- Works with any AI model that supports tool use (Claude, GPT, etc.)
- Patterns are model-agnostic but optimized for Claude's tool system
- Templates use YAML for configuration and structured JSON for execution plans
- All patterns include cost tracking and budget enforcement

## License

MIT

---

Built by [@felipe_bmottaa](https://threads.net/@felipe_bmottaa) | Patterns extracted from production systems running 20-50 agents in parallel
