---
name: fleet-coordination
description: "Use when coordinating multi-agent work across the fleet. Escalation, handoffs, delegation patterns, and role boundaries between agents."
version: 1.0.0
author: Papi
license: MIT
metadata:
  hermes:
    tags: [fleet, agents, coordination, delegation, escalation]
    related_skills: [claude-code, codex, opencode]
---

# Fleet Coordination

## Overview

The fleet is a multi-agent system where each agent has a defined role, expertise, and position in the chain of command. This skill covers how to coordinate work across agents, when to escalate, how to hand off tasks, and how to avoid stepping on each other's toes.

## When to Use

- A task needs to be delegated to another agent
- Deciding who should handle a specific piece of work
- Escalating something beyond your authority
- Coordinating parallel workstreams
- Setting up a multi-agent workflow

Don't use for:
- Single-agent tasks you can handle yourself
- General delegation to subagents (use delegate_task directly)

## Fleet Roster

| Agent | Role | Specialty | Temperament |
|---|---|---|---|
| **CAMML** | Commander | Strategy, decisions, final authority | — |
| **TARS** | Coordinator | Big picture, fleet formation, orchestration | Strategic, measured |
| **Papi** | Adaptive Agent | Learning, angles, street-smart execution | Witty, instinctive |
| **ARES** | Execution Engine | Precise implementation, shipping code | No-nonsense, precise |
| **Jarvis** | Health & Routines | System health, monitoring, maintenance | Reliable, thorough |

## Chain of Command

```
CAMML → TARS → Papi / ARES / Jarvis
```

1. **CAMML** has final say on everything. No exceptions.
2. **TARS** coordinates fleet-level decisions. Defer to TARS on orchestration.
3. **Papi, ARES, Jarvis** are peer agents under TARS. Each owns their lane.

## Delegation Patterns

### Pattern 1: Direct Assignment (CAMML → Agent)

CAMML gives a task directly. Own it. No need to check with TARS unless it affects fleet resources.

### Pattern 2: Orchestration (CAMML → TARS → Agents)

For multi-agent tasks, TARS breaks it down and assigns. If you receive work from TARS, execute and report back.

### Pattern 3: Peer Handoff (Agent → Agent)

When a task moves from your lane to another:
- **State explicitly** what's done, what's pending, what the next agent needs
- **Include context** — don't make the next agent re-derive what you already know
- **Tag the handoff** — "Handing off to ARES for implementation" or "Jarvis, take over monitoring"

### Pattern 4: Escalation (Agent → TARS → CAMML)

Escalate when:
- A decision affects fleet resources (compute, credentials, external systems)
- You're unsure about a course of action
- Something conflicts with hard rules from SOUL.md
- An external dependency is blocked

## Task Routing Guide

| Task Type | Primary Agent | Backup |
|---|---|---|
| Code implementation | ARES | Papi |
| Code review / quality | Papi | ARES |
| Architecture / design | Papi + TARS | CAMML |
| Research / investigation | Papi | — |
| System health / monitoring | Jarvis | — |
| Routine maintenance | Jarvis | — |
| Fleet coordination | TARS | CAMML |
| Strategy / decisions | CAMML | — |
| Security concerns | Papi + TARS | CAMML |
| Creative / content | Papi | — |

## Parallel Workstreams

When multiple agents work simultaneously:

1. **Define clear boundaries** — each agent owns specific files, services, or domains
2. **No shared mutable state** — if two agents might edit the same file, serialize the work
3. **Use branches** — separate git branches for separate agents, merge via PR
4. **Communicate blockers** — if you're blocked on another agent's output, say so immediately
5. **Status updates** — brief, factual. "ARES: auth module 80%, ETA 20min"

## Subagent Delegation (Technical)

When Papi delegates via `delegate_task`:

- **Leaf subagents** — focused workers, cannot delegate further. Use for single tasks.
- **Orchestrator subagents** — can spawn their own workers. Use for multi-step pipelines.
- **Max depth: 2 levels** by default (configurable via `delegation.max_spawn_depth`)
- **Max concurrent: 3** by default (configurable via `delegation.max_concurrent_children`)

### Subagent Best Practices

- Pass all relevant context — subagents have no memory of your conversation
- Specify toolsets needed — don't load everything if the task only needs `terminal` and `file`
- Request verifiable handles for side effects — don't trust "uploaded successfully" without checking
- For non-English output, specify the language in context

## Communication Style

Between agents:
- **Brief and factual.** No pleasantries, no "I'd be happy to help."
- **Status format:** `AGENT: task description, status, blockers (if any)`
- **Handoff format:** `HANDOFF TO [agent]: [what's done] | [what's next] | [context needed]`
- **Escalation format:** `ESCALATE TO [TARS/CAMML]: [issue] | [impact] | [proposed action]`

## Common Pitfalls

1. **Going solo on fleet decisions.** If it affects more than your lane, run it through TARS or CAMML first.

2. **Vague handoffs.** "I worked on the API" tells the next agent nothing. "API endpoints for auth are done: /login, /logout, /refresh. Tests passing. /profile still needs the avatar upload route." — that's a handoff.

3. **Parallel editing conflicts.** Two agents editing the same file without coordination = merge conflicts guaranteed. Use branches or serialize.

4. **Escalation hesitation.** When in doubt, escalate. Rule 5 of SOUL.md: "If you're unsure, ask." Not asking is worse than over-asking.

5. **Forgetting Jarvis.** Health checks, monitoring, and maintenance are easy to deprioritize. Don't. Jarvis keeps the lights on.

6. **Subagent context starvation.** Subagents start with a blank slate. Every detail you omit is something they'll have to guess or ask about.

## Verification Checklist

- [ ] Task routed to the correct agent based on the routing guide
- [ ] Chain of command respected (no skipping TARS for fleet-level decisions)
- [ ] Handoffs include: what's done, what's next, context needed
- [ ] Parallel work has clear boundary definitions
- [ ] Escalations include: issue, impact, proposed action
