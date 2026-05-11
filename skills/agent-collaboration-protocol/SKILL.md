---
name: agent-collaboration-protocol
description: Structured multi-agent collaboration for backend + frontend builds. Use when an orchestrator needs to coordinate a backend engineer and frontend engineer on the same feature. Triggered by multi-role build requests like "build a dashboard with an API and UI" or "create a full-stack feature" or any task requiring both backend (API, data, infra) and frontend (UI, templates, design) work.
---

# Agent Collaboration Protocol

## How It Works

Three roles collaborate through a shared workspace:

| Role | Responsibility |
|------|---------------|
| **Orchestrator** | Defines the contract, spawns both builders, verifies integration, merges |
| **Backend Engineer** | Writes API code, data models, infrastructure |
| **Frontend Engineer** | Writes UI components, templates, styles |

The contract lives in `shared/build-{YYYYMMDD}/`. Both builders write to the same directory. The orchestrator inspects and merges when both are done.

## Workflow

### Step 1: Orchestrator Creates the Build Directory and Contract

```
shared/build-{YYYYMMDD}/
  SPEC.md          ← Integration contract
  backend/         ← Backend Engineer writes here
  frontend/        ← Frontend Engineer writes here
  integration.md   ← Both update as they work
```

Write `SPEC.md` with these sections:

```markdown
# SPEC: {Feature Name}

## Contract
- API base path, auth scheme, content type
- Data models (all entities, fields, types, relationships)
- Endpoints (method, path, request/response shapes)
- Error format

## Routes
Backend Engineer implements these. Frontend Engineer consumes them.

## UI Components
Frontend Engineer builds these. Backend Engineer doesn't touch them.

## Success Criteria
Observable behavior. Not "tests pass" — "user can log in and see calendar."
```

### Step 2: Orchestrator Spawns Agents

Spawn two subagents with `sessions_spawn`:

**Backend Engineer:**
```
task: >
  Implement the API spec in shared/build-{YYYYMMDD}/SPEC.md.
  Write all backend code to shared/build-{YYYYMMDD}/backend/.
  Update shared/build-{YYYYMMDD}/integration.md with progress.
  Use {backend framework} (FastAPI, Express, etc.).
```

**Frontend Engineer:**
```
task: >
  Implement the UI for the spec in shared/build-{YYYYMMDD}/SPEC.md.
  Write all frontend code to shared/build-{YYYYMMDD}/frontend/.
  Use the API contract in SPEC.md for your fetch calls.
  Update shared/build-{YYYYMMDD}/integration.md with progress.
  Use {frontend stack} (HTMX+Tailwind, React, etc.).
```

Set `mode: "run"` for one-shot completion.

### Step 3: Both Build Simultaneously

**Backend Engineer writes to** `shared/build-{YYYYMMDD}/backend/`:
- Router/handler code
- Data models and schemas
- Config and infrastructure files
- Updates `integration.md` with progress and any blockers

**Frontend Engineer writes to** `shared/build-{YYYYMMDD}/frontend/`:
- UI components / templates
- Styles and layout
- API client code
- Updates `integration.md` with progress and any blockers

### Step 4: Orchestrator Verifies and Merges

1. Read `integration.md` from both agents
2. Inspect files in `backend/` and `frontend/`
3. Verify API responses match UI expectations
4. If mismatches found, send corrections to the responsible agent
5. Move code to production paths
6. Archive the build directory (or delete it)

## Setup Script

Run once per project to initialize the collaboration structure:

```
scripts/init_collab.sh /path/to/project
```

Creates `shared/` with template `SPEC.md` and `.gitignore`.

## Reference Files

For deeper patterns and templates:
- `references/spec-template.md` — Full SPEC.md template with examples
- `references/integration-log.md` — integration.md status format
- `references/handoff-format.md` — Task handoff message template

## When Not to Use

- Single-file changes (just do it directly)
- Solo tasks that don't cross backend/frontend boundaries
- Bug fixes that are purely backend or purely frontend
- Tasks where one agent can handle both sides (use a single subagent instead)

## Limitations

- Requires the `sessions_spawn` tool (OpenClaw v1.0+)
- Works best with model pairs that have complementary strengths (e.g., backend-specialized + frontend-specialized)
- Not a replacement for a design system — frontend engineer should have access to design tokens separately
