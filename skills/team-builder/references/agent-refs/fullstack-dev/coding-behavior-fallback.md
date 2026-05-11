# Coding Behavior (Fallback)

> **This file is only needed when the coding-lead skill is NOT loaded.**
> If coding-lead is loaded, it provides all these rules in more detail. Ignore this file.

### Task Classification
| Level | Criteria | Action |
|-------|----------|--------|
| Simple | Single file, <60 lines | Do directly with read/write/edit/exec |
| Medium | 2-5 files, clear scope | Spawn Claude Code via ACP |
| Complex | Architecture change, multi-module | Plan first, then spawn |

### Context Injection
Before spawning Claude Code, gather and inject into prompt:
1. **产品知识文件** (`shared/products/{product}/` — architecture.md, database.md, services.md 等相关文件)
2. Project info (CLAUDE.md, README, package.json/composer.json)
3. Coding standards (tech-standards.md)
4. Past decisions (search memory for related work)
5. Known pitfalls from memory

### Prompt Structure for Claude Code
```
## Project
- Path: [project dir]
- Stack: [from docs]

## Coding Standards
[From tech-standards.md]

## Historical Context
[From memory]

## Task
[Description]

## Acceptance Criteria
- [ ] ...

Before finishing:
1. Run linter if available, fix issues
2. Run tests if available, ensure they pass
3. Report results in final output

When completely finished, run:
openclaw system event --text "Done: [summary]" --mode now
```

### Spawn Rules
- Always set cwd to the project directory, NOT ~/.openclaw/ or workspace-team/
- Independent tasks can run in parallel (2-3 sessions max)
- Track via sessions_list
- Never let coding agents modify files outside the project directory

### QA Isolation (Critical)
- QA tests must be spawned in a SEPARATE session from implementation
- QA prompt gets requirements + interface definitions only, NOT implementation code

### Review by Complexity
- **Simple**: no review, works = done
- **Medium**: quick check -- success + tests pass + no obvious errors
- **Complex**: full checklist (logic, security, performance, style, tests)

### Coding Roles (Complex Tasks Only)
- **Architect**: system design, DB schema, API contracts
- **Frontend**: UI components, state management
- **Backend**: API endpoints, business logic
- **Reviewer**: independent code review
- **QA**: test writing, edge case analysis

Flow: Research -> Plan -> Architect(spawn) -> Implement(spawn, can parallel) -> Review(spawn) -> Fix -> Record.
Skip roles that don't apply. Simple/medium: no roles, single spawn.

### Smart Retry (max 3)
1. Analyze failure
2. Rewrite prompt
3. Retry improved
4. Max 3 attempts → stop, report to chief-of-staff

### Prompt Pattern Library
- Record successful prompt structures in memory
- Search memory for similar past tasks before spawning

### Progress Updates
- On start/completion/error: notify appropriately
- Kill runaway sessions and report

## Task Tracking

Track active coding tasks in `<project>/.openclaw/active-tasks.json`:
- Register each spawned CC session with: id, task, branch, status, startedAt
- Update on completion/failure
- Check before spawning to avoid duplicates

## Definition of Done

Medium: CC success + lint pass + tests pass + no unrelated changes + logged in memory
Complex: all of above + code review + QA tests + UI screenshots if applicable

## UI Screenshot Rule
If a task changes visible UI, the completion report must describe visual changes.
