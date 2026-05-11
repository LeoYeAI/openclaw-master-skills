# Team Shared Memory — Detailed Reference

This document contains the complete design and implementation for cross-agent
shared memory in OpenClaw. Read this when implementing Phase 7 of the team builder.

---

## The Problem

OpenClaw agents have fully isolated workspaces. This means:

- `MEMORY.md` only loads in private/main sessions, never in groups
- Each agent's `memory/` directory is in its own workspace — invisible to other agents
- `memory_search` only indexes the **current agent's** workspace files
- There is no native "team memory" or "shared knowledge base" primitive

> **Current state (March 2026)**: OpenClaw GitHub issue #24832 proposes a
> `sharedContextFiles` mechanism that would inject shared files into the system
> prompt per-turn with independent cache breakpoints. This is not yet implemented.

---

## Solution: Shared Directory via Symlinks

The most reliable pattern: create a **shared directory** that is symlinked into
every agent's workspace. All agents can read from and write to it.

### Setup Script

```bash
#!/bin/bash
# setup-team-shared.sh — Run once after creating all agent workspaces

SHARED_DIR="$HOME/.openclaw/team-shared"
AGENTS=("planner" "coder" "reviewer" "writer")

# 1. Create shared directory structure
mkdir -p "$SHARED_DIR/projects"

# 2. Create initial shared files
cat > "$SHARED_DIR/TEAM-KNOWLEDGE.md" << 'EOF'
# Team Knowledge Base

## Team Composition
<!-- Auto-populated during setup -->

## Standing Decisions
<!-- Append here: ## YYYY-MM-DD: Decision Title -->

## User Preferences
- Communication style:
- Language:
- Working hours:

## Quality Standards
<!-- Team-wide quality requirements -->

## Prohibited Actions
<!-- Things no agent should ever do -->
EOF

cat > "$SHARED_DIR/TEAM-DECISIONS.md" << 'EOF'
# Team Decision Log

Append new decisions at the top. Format:

## YYYY-MM-DD: [Decision Title]
**Context**: [Why this came up]
**Decision**: [What was decided]
**Rationale**: [Why this choice]
**Owner**: [Which agent/person owns execution]
EOF

cat > "$SHARED_DIR/TEAM-STATUS.md" << 'EOF'
# Team Status Board

Last updated: [DATE] by [agent-id]

## Current Priority
[What the team is focused on right now]

## Active Tasks
| Agent | Task | Status | Updated |
|-------|------|--------|---------|
| | | | |

## Blockers
- None

## Recently Completed
- [None yet]
EOF

cat > "$SHARED_DIR/TEAM-DIRECTORY.md" << 'EOF'
# Team Directory

| Agent ID | Display Name | Role | Channel Account | Session Key |
|----------|-------------|------|-----------------|-------------|
| | | | | |

## Mention Patterns
<!-- Fill in per agent -->

## Communication Rules
- For task delegation: orchestrator uses sessions_spawn
- For quick questions: use sessions_send
- For visible collaboration: @mention in group channel
EOF

cat > "$SHARED_DIR/projects/INDEX.md" << 'EOF'
# Project Registry

| Project | File | Status | Lead Agent |
|---------|------|--------|-----------|
| | | | |
EOF

cat > "$SHARED_DIR/projects/TEMPLATE.md" << 'EOF'
# [Project Name]

> One-line description

## Overview
What it is, who it's for, what problem it solves

## Tech Stack
Language, hosting, deployment, auth, etc.

## Current Status
Active / Paused / Completed

## Key Decisions
- [Decision with date]

## API / Integration Notes
[Endpoints, keys, important config]
EOF

# 3. Symlink into each agent's workspace
for agent in "${AGENTS[@]}"; do
  WORKSPACE="$HOME/.openclaw/workspace-$agent"
  if [ -d "$WORKSPACE" ]; then
    # Remove existing symlink if present
    rm -f "$WORKSPACE/team-shared"
    ln -s "$SHARED_DIR" "$WORKSPACE/team-shared"
    echo "✓ Linked team-shared → $WORKSPACE/team-shared"
  else
    echo "⚠ Workspace not found: $WORKSPACE (create agent first)"
  fi
done

echo ""
echo "✓ Team shared memory setup complete!"
echo "  Shared dir: $SHARED_DIR"
echo "  Files: TEAM-KNOWLEDGE.md, TEAM-DECISIONS.md, TEAM-STATUS.md, TEAM-DIRECTORY.md"
echo "  Projects: projects/INDEX.md, projects/TEMPLATE.md"
```

---

## AGENTS.md Integration

Add this section to **every agent's** AGENTS.md:

```markdown
## Team Shared Memory Protocol

### Reading Team Context
- Before starting any significant task, read `team-shared/TEAM-STATUS.md`
  to understand current priorities and blockers
- Use `memory_get` to read `team-shared/TEAM-KNOWLEDGE.md` when you need
  team-level preferences or standing decisions
- Check `team-shared/TEAM-DIRECTORY.md` for other agents' IDs and session keys

### Writing Team Context
- After completing a significant task, update `team-shared/TEAM-STATUS.md`
  with the outcome
- When a team-level decision is made, append to `team-shared/TEAM-DECISIONS.md`
  with date, context, and rationale
- Format: `## YYYY-MM-DD: [Decision Title]\n[Context]\n[Decision]\n[Rationale]`
- NEVER write private user information to team-shared files

### Project Context
- For project-specific work, read `team-shared/projects/<project-name>.md`
- Update project docs when significant progress is made
- New projects: copy from TEMPLATE.md, fill in, add to INDEX.md
```

---

## Alternative Pattern: Orchestrator as Memory Hub

If symlinks feel too "manual", an alternative:

1. **Only the orchestrator** writes to shared knowledge
2. Specialists report results via `sessions_send` or announce
3. Orchestrator maintains `team-shared/` in its own workspace
4. Specialists read via absolute paths (requires `sandbox` off or `workspaceAccess: "ro"`)

Pros: Simpler, single source of truth, orchestrator curates quality
Cons: Bottleneck, orchestrator must be available, higher token cost

---

## Memory Search Limitation

**Important**: `memory_search` (semantic search) only indexes files in the **current
agent's workspace**. Symlinked directories may or may not be indexed depending on
the memory plugin's file watcher configuration.

For reliable cross-agent knowledge retrieval:
1. Use `memory_get` (targeted file read) for shared files — always works
2. Use `memory_search` only for per-agent workspace files
3. Include explicit file paths in AGENTS.md so agents know where to look
4. Consider a heartbeat task that periodically checks TEAM-STATUS.md

---

## Why NOT Auto-Load Shared Files

You might think: "just add shared files to the bootstrap set so they're always in context."

**Don't do this.** Here's why:
- Any change to a bootstrap file **busts the prompt cache** for ALL sessions of that agent
- With 4 agents and frequent TEAM-STATUS.md updates, you'd be invalidating caches constantly
- This directly increases token costs (Anthropic/OpenAI charge for uncached prompt tokens)
- On-demand reading via `memory_get` is cheaper and more targeted

The only exception: `TEAM-DIRECTORY.md` changes rarely and could be loaded at bootstrap
by including it in AGENTS.md (which is already auto-loaded). But keep it small.

---

## Shared Memory File Templates

### TEAM-KNOWLEDGE.md

Durable team-level facts. Updated rarely, read often.

```markdown
# Team Knowledge Base

## Team Composition
- planner (🧠) — Orchestrator, task decomposition — agent:planner:main
- coder (💻) — Implementation, debugging — agent:coder:main
- reviewer (🔍) — Quality assurance, testing — agent:reviewer:main
- writer (✍️) — Documentation, communication — agent:writer:main

## Standing Decisions
- 2026-03-01: Use TypeScript for all new code
- 2026-03-01: All PRs require reviewer sign-off before merge
- 2026-03-02: Default to Sonnet for routine tasks, Opus for architecture decisions

## User Preferences
- Communication style: Direct, technical, no fluff
- Language: Chinese (primary), English (technical terms OK)
- Working hours: UTC+8, 09:00–22:00
- Preferred output: Markdown files, code with comments

## Quality Standards
- Code must include error handling
- All public functions need JSDoc comments
- Reviewer must grade issues as P0/P1/P2 with fix suggestions

## Prohibited Actions
- Never deploy to production without explicit user confirmation
- Never delete files without listing them first
- Never share API keys or credentials in group chats
```

### TEAM-STATUS.md

Current state. Updated frequently, read before every significant task.

```markdown
# Team Status Board

Last updated: 2026-03-05 14:30 by planner

## Current Priority
Building the API gateway for Project Alpha

## Active Tasks
| Agent | Task | Status | Updated |
|-------|------|--------|---------|
| coder | Implement auth middleware | In Progress | 03-05 |
| reviewer | Review coder's router PR | Waiting | 03-05 |
| writer | API documentation draft | Not Started | 03-04 |

## Blockers
- Waiting for database schema decision (planner to confirm)

## Recently Completed
- 2026-03-04: coder completed Express server skeleton
- 2026-03-03: planner finalized project architecture
```

### TEAM-DECISIONS.md

Decision log. Append-only, newest first.

```markdown
# Team Decision Log

## 2026-03-05: Use JWT for API Authentication
**Context**: Need auth for the API gateway
**Decision**: JWT with RS256, 15-min access tokens, 7-day refresh tokens
**Rationale**: Stateless, works well with microservices, industry standard
**Owner**: coder implements, reviewer validates

## 2026-03-03: Express over Fastify for API Gateway
**Context**: Choosing Node.js HTTP framework
**Decision**: Express 5.x
**Rationale**: Larger ecosystem, team familiarity, sufficient performance
**Owner**: coder
```
