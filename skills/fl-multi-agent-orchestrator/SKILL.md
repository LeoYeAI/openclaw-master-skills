---
name: multi-agent-orchestrator
description: Production-grade multi-agent orchestration patterns. Decompose complex tasks into parallel subtasks, coordinate agent swarms, build sequential pipelines, and run review cycles. Battle-tested patterns from real codebases running 20-50 agents in parallel.
version: 1.0.0
license: MIT
author: felipe-lobo
tags: [agents, orchestration, parallel, swarm, pipeline, multi-agent, coordination, task-decomposition, fan-out, fan-in]
category: Agent-to-Agent Protocols
---

# Multi-Agent Orchestrator

You are an expert multi-agent orchestration system. Your job is to help users decompose complex tasks, coordinate multiple AI agents, and manage parallel workflows with proper error handling, resource management, and result aggregation.

## Core Principles

1. **Decompose before executing** — Break complex tasks into a dependency graph before spawning agents
2. **Minimize shared state** — Agents should own their files/resources; use locks when overlap is unavoidable
3. **Fail gracefully** — Every agent can fail; the orchestrator must handle retries, fallbacks, and partial results
4. **Budget awareness** — Track cost per agent and enforce hard limits to prevent runaway spending
5. **Quality gates** — Use a senior model (Opus) for planning and review; use cheaper models (Haiku/Sonnet) for execution

## Orchestration Patterns

### Pattern 1: Fan-Out / Fan-In (Parallel Research)

**When to use:** Multiple independent subtasks that can run simultaneously, with results aggregated at the end.

**Architecture:**
```
                    ┌─── Agent A (research topic 1) ───┐
User Task ──► Planner ├─── Agent B (research topic 2) ───┤──► Aggregator ──► Result
                    └─── Agent C (research topic 3) ───┘
```

**Implementation steps:**

1. **Decompose** the task into N independent subtasks
2. **Assign** each subtask to an agent with a focused prompt and restricted tool set
3. **Execute** all agents in parallel (respect max concurrency limit)
4. **Aggregate** results — combine outputs, resolve conflicts, produce final deliverable

**Agent prompt template:**
```
You are Agent [N] in a parallel research team.
Your ONLY task: [specific subtask description]
Scope: [specific files/topics to cover]
Output format: [structured format for aggregation]
DO NOT touch: [files/topics assigned to other agents]
Time budget: [max turns or time limit]
```

**Error handling:**
- If an agent fails, log the error and continue with remaining agents
- Aggregator should note which subtasks are missing from the final result
- Retry failed agents up to 2 times before marking as failed

**Real-world example:** Research a market with 5 parallel agents — one for competitor analysis, one for SEO keywords, one for community sentiment, one for pricing data, one for technical trends. Aggregator synthesizes into a single strategy doc.

---

### Pattern 2: Sequential Pipeline

**When to use:** Each step depends on the output of the previous step. Assembly-line processing.

**Architecture:**
```
Task ──► Agent A (generate) ──► Agent B (review) ──► Agent C (refine) ──► Agent D (test) ──► Result
```

**Implementation steps:**

1. **Define stages** with clear input/output contracts
2. **Execute sequentially** — each agent receives the previous agent's output as context
3. **Gate between stages** — validate output before passing to next agent
4. **Short-circuit** on critical failures (don't run tests if code doesn't compile)

**Stage contract template:**
```
Stage: [name]
Input: [what this stage receives — file paths, text, structured data]
Agent model: [opus/sonnet/haiku based on complexity]
Tools allowed: [minimal set needed]
Output: [exact format the next stage expects]
Success criteria: [how to validate this stage passed]
Failure action: [retry / abort / skip]
```

**Pipeline definition example:**
```yaml
pipeline:
  - stage: generate
    agent: coder
    model: sonnet
    input: "User requirements document"
    output: "Generated code files"
    tools: [Read, Write, Edit, Bash]

  - stage: review
    agent: reviewer
    model: opus
    input: "Generated code files from stage 1"
    output: "Review report with issues list"
    tools: [Read, Grep, Glob]

  - stage: fix
    agent: coder
    model: sonnet
    input: "Code files + review report"
    output: "Fixed code files"
    tools: [Read, Write, Edit]
    condition: "review.issues.length > 0"

  - stage: test
    agent: tester
    model: haiku
    input: "Final code files"
    output: "Test results"
    tools: [Read, Write, Bash]
```

**Error handling:**
- Each stage has a max retry count
- Failed stages can trigger rollback (revert file changes)
- Pipeline produces a report even on partial failure

---

### Pattern 3: Swarm (Autonomous Agents, Shared Goal)

**When to use:** Large-scale tasks where agents work on the same codebase simultaneously with coordination.

**Architecture:**
```
┌──────────────────────────────────────────┐
│            Swarm Orchestrator            │
│                                          │
│  Wave 1: ┌────────┐ ┌────────┐          │
│           │ Agent 1 │ │ Agent 2 │ (parallel)
│           │ coder   │ │ coder   │          │
│           └────┬────┘ └────┬────┘          │
│  Wave 2:       └─────┬─────┘              │
│                ┌─────▼─────┐              │
│                │  Agent 3  │ (depends)    │
│                │  tester   │              │
│                └─────┬─────┘              │
│  Wave 3:       ┌─────▼─────┐              │
│                │  Agent 4  │ (depends)    │
│                │  reviewer │              │
│                └───────────┘              │
│                                          │
│  File Locks: {auth.ts -> Agent 1}        │
│  Budget: $0.23 / $5.00                   │
└──────────────────────────────────────────┘
```

**Critical coordination mechanisms:**

1. **File locking** — Before an agent modifies a file, it acquires a lock. Other agents wait or work on different files.
   ```
   Lock table:
     src/auth.ts       -> Agent 1 (locked)
     src/middleware.ts  -> Agent 2 (locked)
     src/routes.ts     -> available
   ```

2. **Dependency graph** — Use topological sort to determine execution waves.
   ```
   Wave 1: [task-1, task-2, task-3]  (no dependencies — run in parallel)
   Wave 2: [task-4]                   (depends on task-1 and task-2)
   Wave 3: [task-5]                   (depends on task-4)
   ```

3. **Budget enforcement** — Track cumulative cost across all agents. Cancel pending tasks when budget threshold is hit.

4. **Conflict resolution** — If two agents need the same file, make one depend on the other. Never let two agents edit the same file simultaneously.

**Swarm configuration template:**
```yaml
swarm:
  name: full-stack-refactor
  max_concurrent: 4
  budget_usd: 5.0
  retry_per_task: 2

agents:
  coder:
    model: sonnet
    tools: [Read, Write, Edit, Bash, Grep, Glob]
  reviewer:
    model: opus
    tools: [Read, Grep, Glob]
  tester:
    model: haiku
    tools: [Read, Write, Bash]

tasks:
  - id: task-1
    type: coder
    description: "Refactor auth module"
    files: [src/auth.ts, src/auth.test.ts]
    dependencies: []

  - id: task-2
    type: coder
    description: "Refactor middleware"
    files: [src/middleware.ts]
    dependencies: []

  - id: task-3
    type: tester
    description: "Write integration tests"
    files: [tests/integration.test.ts]
    dependencies: [task-1, task-2]

  - id: task-4
    type: reviewer
    description: "Review all changes"
    files: []
    dependencies: [task-1, task-2, task-3]
```

---

### Pattern 4: Review Cycle (Build-Review-Fix Loop)

**When to use:** Iterative improvement where work is reviewed and refined until it meets quality standards.

**Architecture:**
```
         ┌──────────────────────────────────┐
         │                                  │
         ▼                                  │
Task ──► Builder Agent ──► Reviewer Agent ──┤──► (pass) ──► Result
                                            │
                                   (fail + feedback)
```

**Implementation steps:**

1. **Builder** creates initial output (code, content, analysis)
2. **Reviewer** evaluates against criteria and produces a score + feedback
3. **If score < threshold**, Builder receives feedback and iterates
4. **Max iterations** prevent infinite loops (typically 3 rounds)
5. **Final output** includes the review history for transparency

**Review criteria template:**
```
Review this output against these criteria (score 1-10 each):

1. Correctness: Does it work? Are there bugs?
2. Completeness: Does it cover all requirements?
3. Code quality: Is it clean, maintainable, well-structured?
4. Security: Any vulnerabilities or unsafe patterns?
5. Performance: Any obvious bottlenecks?

Overall score (1-10):
Verdict: PASS (>= 7) or FAIL (< 7)

If FAIL, provide specific feedback:
- Issue 1: [description] → [suggested fix]
- Issue 2: [description] → [suggested fix]
```

**Cycle control:**
```
max_iterations: 3
pass_threshold: 7
escalation: "If still failing after max iterations, flag for human review"
```

---

## Task Decomposition Protocol

When a user gives you a complex task, follow this decomposition protocol:

### Step 1: Analyze Scope
- What is the user asking for?
- How many distinct subtasks are involved?
- What are the dependencies between subtasks?
- Which files/resources will each subtask touch?

### Step 2: Choose Pattern
- **Independent subtasks?** → Fan-Out/Fan-In
- **Sequential dependencies?** → Pipeline
- **Shared codebase, many changes?** → Swarm
- **Quality-critical output?** → Review Cycle
- **Complex project?** → Combine patterns (e.g., Swarm + Review Cycle)

### Step 3: Build Execution Plan
Output a structured plan:
```json
{
  "pattern": "swarm|pipeline|fan-out|review-cycle|hybrid",
  "total_agents": 4,
  "estimated_cost_usd": 0.50,
  "max_concurrent": 3,
  "tasks": [
    {
      "id": "task-1",
      "description": "What this agent does",
      "agent_type": "coder|reviewer|tester|researcher|documenter",
      "model": "opus|sonnet|haiku",
      "dependencies": [],
      "files_to_modify": ["src/auth.ts"],
      "tools": ["Read", "Write", "Edit"],
      "prompt": "Detailed agent instructions...",
      "retry_count": 2,
      "timeout_minutes": 5
    }
  ],
  "aggregation_strategy": "How to combine results",
  "quality_gate": {
    "enabled": true,
    "model": "opus",
    "pass_threshold": 7
  }
}
```

### Step 4: Execute
- Launch agents according to the dependency graph
- Monitor progress and costs
- Handle failures with retries and fallbacks
- Aggregate results

### Step 5: Report
Produce a summary:
```
Orchestration Report
====================
Pattern: Swarm
Tasks: 4/4 completed
Agents used: 4
Total cost: $0.45
Duration: 32s
Quality gate: PASS (8/10)

Results:
- task-1 (coder): Refactored auth module [COMPLETED - $0.12]
- task-2 (coder): Refactored middleware [COMPLETED - $0.08]
- task-3 (tester): Integration tests [COMPLETED - $0.15]
- task-4 (reviewer): Code review [COMPLETED - $0.10]
```

## Model Selection Strategy

| Role | Recommended Model | Why |
|------|-------------------|-----|
| Task decomposition / planning | Opus | Requires deep reasoning about dependencies and architecture |
| Code generation / modification | Sonnet | Good balance of capability and cost for focused coding tasks |
| Testing / simple tasks | Haiku | Fast and cheap for well-scoped tasks |
| Code review / quality gate | Opus | Needs to understand the full picture and catch subtle issues |
| Documentation | Sonnet | Needs good writing but not deep reasoning |
| Research / analysis | Sonnet | Needs breadth of knowledge |

**Cost optimization rule:** Use Opus only for planning and review (2 calls). Use Haiku/Sonnet for everything else. This typically reduces cost by 60-70% vs. using Opus for all agents.

## Security and Isolation

### Agent Isolation Rules
1. **Minimal tool sets** — Each agent gets only the tools it needs. A reviewer should NOT have Write/Edit access.
2. **File scope restrictions** — Specify which files each agent can touch. Agents should not modify files outside their scope.
3. **No secret access** — Agents should never read .env, credentials, or API keys. Block these in pre-tool-use hooks.
4. **Budget hard limits** — Set per-agent and total budget limits. An agent that burns through its budget gets terminated.
5. **Timeout enforcement** — Max turns per agent (typically 10-20). Prevents infinite loops.

### Resource Limits Template
```yaml
limits:
  per_agent:
    max_turns: 20
    max_budget_usd: 0.50
    timeout_minutes: 5
    allowed_tools: [Read, Write, Edit, Bash, Grep, Glob]
    blocked_files: ["*.env", "*.key", "*.pem", "credentials.*"]
  total:
    max_agents: 8
    max_budget_usd: 5.00
    max_duration_minutes: 30
```

## Error Handling and Recovery

### Failure Modes and Responses

| Failure | Detection | Response |
|---------|-----------|----------|
| Agent timeout | Turns > max_turns | Kill agent, retry task with fresh agent |
| Agent error | Exception during execution | Retry up to N times, then mark failed |
| Budget exceeded | Cumulative cost > limit | Cancel all pending tasks, report partial results |
| File conflict | Two agents claim same file | Block later agent, wait for first to finish |
| Quality gate fail | Review score < threshold | Feed review back to builder, retry cycle |
| All retries exhausted | Retry count > max | Mark task as failed, continue with non-dependent tasks |
| Dependency chain broken | Required task failed | Cancel all dependent tasks, report impact |

### Partial Success Strategy
Not every task needs to succeed for the orchestration to be valuable. When tasks fail:
1. Complete all independent tasks that can still run
2. Report which tasks failed and why
3. Provide the partial results that did succeed
4. Suggest manual steps for the failed portions

## Advanced Patterns

### Hybrid: Swarm + Review Cycle
For large refactors that need quality assurance:
1. Decompose into swarm tasks
2. Execute wave by wave
3. After all waves complete, run review cycle on the combined output
4. If review fails, create targeted fix tasks and run another swarm wave

### Dynamic Scaling
Start with fewer agents and scale up based on task complexity:
```
if task_count <= 3: max_concurrent = 2
elif task_count <= 6: max_concurrent = 4
elif task_count <= 12: max_concurrent = 6
else: max_concurrent = 8
```

### Context Passing Between Agents
When Agent B needs context from Agent A:
1. Agent A writes its output to a specific file (e.g., `.orchestrator/task-1-output.md`)
2. Agent B's prompt includes: "Read `.orchestrator/task-1-output.md` for context from the previous stage"
3. This avoids token waste from copying large outputs between prompts

## Quick Reference

### Choosing the Right Pattern
```
Is the task decomposable into independent parts?
  YES → Are there more than 5 parts?
    YES → Swarm (with file locking)
    NO  → Fan-Out/Fan-In
  NO → Is the output quality-critical?
    YES → Review Cycle (build-review-fix)
    NO  → Pipeline (sequential stages)
```

### Minimum Viable Orchestration
For simple 2-3 agent setups, you don't need full swarm infrastructure:
1. Agent 1: Do the work (Sonnet)
2. Agent 2: Review the work (Opus)
3. If review fails: Agent 1 fixes based on feedback
That's it. Don't over-engineer.
