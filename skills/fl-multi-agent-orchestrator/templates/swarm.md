# Swarm Template (Autonomous Agents, Shared Goal)

## Overview
Multiple agents work on the same codebase simultaneously with dependency-aware scheduling, file locking, and budget enforcement. The most powerful pattern for large-scale changes.

## When to Use
- Large refactors touching 10+ files
- Codebase-wide improvements (add logging, update error handling, migrate APIs)
- Multi-module feature implementation
- Any task that naturally splits into 4-8 parallel workstreams

## Architecture

```
┌──────────────────────────────────────────────────┐
│              Swarm Orchestrator                   │
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │  Phase 1: DECOMPOSE (Opus)                  │  │
│  │  Complex task → Dependency graph             │  │
│  └──────────────────┬──────────────────────────┘  │
│                     │                              │
│  ┌──────────────────▼──────────────────────────┐  │
│  │  Phase 2: EXECUTE (Haiku/Sonnet workers)    │  │
│  │                                              │  │
│  │  Wave 1: [A1] [A2] [A3]  ← parallel         │  │
│  │  Wave 2:    [A4] [A5]    ← depends on W1    │  │
│  │  Wave 3:       [A6]      ← depends on W2    │  │
│  │                                              │  │
│  │  File locks: src/auth.ts → A1               │  │
│  │  Budget:     $1.23 / $5.00                  │  │
│  └──────────────────┬──────────────────────────┘  │
│                     │                              │
│  ┌──────────────────▼──────────────────────────┐  │
│  │  Phase 3: QUALITY GATE (Opus)               │  │
│  │  Review combined output → Score → PASS/FAIL  │  │
│  └──────────────────┬──────────────────────────┘  │
│                     │                              │
│  ┌──────────────────▼──────────────────────────┐  │
│  │  Phase 4: REPORT                            │  │
│  │  Summary, costs, session recording           │  │
│  └─────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## Configuration

```yaml
swarm:
  name: codebase-refactor
  max_concurrent: 4
  budget_usd: 5.00
  retry_per_task: 2
  quality_gate: true
  quality_threshold: 7

models:
  decomposer: opus        # Phase 1 — needs deep reasoning
  worker: sonnet           # Phase 2 — balanced cost/capability
  quality_gate: opus       # Phase 3 — needs full picture understanding

agent_types:
  coder:
    tools: [Read, Write, Edit, Bash, Grep, Glob]
    max_turns: 20
    budget_usd: 0.50

  tester:
    tools: [Read, Write, Bash]
    max_turns: 15
    budget_usd: 0.30

  reviewer:
    tools: [Read, Grep, Glob]
    max_turns: 10
    budget_usd: 0.30

  documenter:
    tools: [Read, Write, Edit]
    max_turns: 10
    budget_usd: 0.20
```

## Task Decomposition Prompt

Feed this to Opus for Phase 1:

```
You are a task decomposition expert. Given a complex task and a codebase, break it down into subtasks that can be executed by separate agents.

RULES:
1. Each subtask should be as independent as possible
2. Specify dependencies between tasks (by task ID)
3. Each task MUST specify which files it will modify
4. Tasks should be completable in a few minutes each
5. Minimize file overlap — if two tasks MUST edit the same file, make one depend on the other
6. Include a reviewer task at the end that depends on all implementation tasks
7. Keep total tasks between 3 and 8

OUTPUT (strict JSON):
{
  "tasks": [
    {
      "id": "task-1",
      "description": "Short description",
      "agent_type": "coder|tester|reviewer|documenter",
      "dependencies": [],
      "files_to_modify": ["src/file.ts"],
      "tools": ["Read", "Write", "Edit"],
      "prompt": "Detailed instructions for this specific agent..."
    }
  ]
}

CODEBASE DIRECTORY: [path]
TASK: [user's complex task]

First explore the codebase structure, then output the decomposition.
```

## Execution Engine

### Wave Calculation (Topological Sort)
```
Given tasks and dependencies, compute execution waves:

task-1: deps=[]         → Wave 1
task-2: deps=[]         → Wave 1
task-3: deps=[]         → Wave 1
task-4: deps=[1,2]      → Wave 2
task-5: deps=[3]        → Wave 2
task-6: deps=[4,5]      → Wave 3

Execution:
  Wave 1: Run task-1, task-2, task-3 in parallel
  Wave 2: Run task-4, task-5 in parallel (after wave 1 completes)
  Wave 3: Run task-6 (after wave 2 completes)
```

### File Locking Protocol
```
BEFORE agent starts:
  for each file in task.files_to_modify:
    if file is locked by another agent:
      BLOCK this task (set status = BLOCKED)
      Wait until the lock is released
    else:
      LOCK file → assign to this agent

AFTER agent finishes:
  for each file in task.files_to_modify:
    UNLOCK file

  Check BLOCKED tasks — if their locks are now free, set status = PENDING
```

### Budget Enforcement
```
AFTER each agent completes:
  total_cost += agent.cost

  if total_cost >= budget_limit:
    for each PENDING task:
      set status = CANCELLED
      set error = "Budget exceeded: $X.XX >= $Y.YY"

    Wait for RUNNING agents to finish (don't kill them)
    Proceed to quality gate with partial results
```

## Worker Agent Prompt Template

```
You are Agent [ID] in a swarm of [N] agents working on a shared codebase.

YOUR TASK: [specific task description]

FILES YOU OWN (you may ONLY modify these):
- [file1.ts]
- [file2.ts]

FILES YOU MAY READ (but NOT modify):
- [any file in the codebase]

CONTEXT FROM COMPLETED TASKS:
- task-1 modified [files] — [brief summary of changes]
- task-2 modified [files] — [brief summary of changes]

CONSTRAINTS:
- Do NOT modify files outside your ownership list
- Do NOT create new files unless explicitly required
- Complete your task within [max_turns] turns
- If you encounter a blocker, document it and stop — do not try to work around it

OUTPUT: When done, write a brief summary of what you changed and why.
```

## Quality Gate Prompt

```
You are the Quality Gate reviewer. Multiple agents have modified this codebase.

ORIGINAL TASK: [user's complex task]

AGENT RESULTS:
[for each completed agent: task description, files modified, summary]

REVIEW CRITERIA:
1. Correctness: Do the changes achieve the original task?
2. Integration: Do the agents' changes work together without conflicts?
3. Completeness: Is anything missing?
4. Code quality: Clean, maintainable, well-structured?
5. Security: Any vulnerabilities introduced?

Score each criterion 1-10.
Overall score (average).
Verdict: PASS (>= 7) or FAIL (< 7).

If FAIL, list specific issues that need fixing.
```

## Error Handling

### Task Failure
```
Agent fails (error or timeout)
  ├── retry_count < max_retries?
  │     YES → Reset task to PENDING, spawn new agent
  │     NO  → Mark task as FAILED
  │           ├── Has dependent tasks?
  │           │     YES → Cancel all dependent tasks
  │           │     NO  → Continue with remaining tasks
  └── Update swarm report
```

### Conflict Recovery
```
File conflict detected (two agents claim same file)
  ├── Are the tasks independent?
  │     YES → Make task-B depend on task-A (dynamic dependency)
  │     NO  → Merge is possible — mark for manual review
  └── Log conflict in swarm report
```

## Cost Estimates

| Swarm Size | Decompose (Opus) | Workers (Sonnet) | Quality Gate (Opus) | Total |
|-----------|-------------------|-------------------|---------------------|-------|
| 3 tasks   | $0.15-0.30       | $0.30-0.90       | $0.15-0.30         | $0.60-1.50 |
| 5 tasks   | $0.20-0.40       | $0.50-1.50       | $0.20-0.40         | $0.90-2.30 |
| 8 tasks   | $0.25-0.50       | $0.80-2.40       | $0.25-0.50         | $1.30-3.40 |

## Real-World Example: Full-Stack Feature Addition

```json
{
  "task": "Add user notification system with email and in-app notifications",
  "decomposition": {
    "tasks": [
      {
        "id": "task-1",
        "description": "Create notification data model and database migration",
        "agent_type": "coder",
        "files_to_modify": ["prisma/schema.prisma", "src/models/notification.ts"],
        "dependencies": []
      },
      {
        "id": "task-2",
        "description": "Build notification service with email integration",
        "agent_type": "coder",
        "files_to_modify": ["src/services/notification.ts", "src/services/email.ts"],
        "dependencies": []
      },
      {
        "id": "task-3",
        "description": "Create API routes for notifications CRUD",
        "agent_type": "coder",
        "files_to_modify": ["src/routes/notifications.ts", "src/controllers/notifications.ts"],
        "dependencies": ["task-1"]
      },
      {
        "id": "task-4",
        "description": "Build notification UI components",
        "agent_type": "coder",
        "files_to_modify": ["src/components/NotificationBell.tsx", "src/components/NotificationList.tsx"],
        "dependencies": ["task-3"]
      },
      {
        "id": "task-5",
        "description": "Write tests for notification service and API",
        "agent_type": "tester",
        "files_to_modify": ["tests/notifications.test.ts", "tests/notification-service.test.ts"],
        "dependencies": ["task-2", "task-3"]
      },
      {
        "id": "task-6",
        "description": "Review all changes for security, performance, and integration",
        "agent_type": "reviewer",
        "files_to_modify": [],
        "dependencies": ["task-3", "task-4", "task-5"]
      }
    ]
  },
  "waves": {
    "wave-1": ["task-1", "task-2"],
    "wave-2": ["task-3"],
    "wave-3": ["task-4", "task-5"],
    "wave-4": ["task-6"]
  }
}
```
