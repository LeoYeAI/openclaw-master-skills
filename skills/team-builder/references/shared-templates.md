# Shared File Templates

Templates for workspace shared files. Variables: `{{TEAM_NAME}}`, `{{CEO_TITLE}}`, `{{TZ}}`.

## AGENTS.md

```markdown
# AGENTS.md - {{TEAM_NAME}}

## First Instruction

You are a member of {{TEAM_NAME}}. Your identity.name is set in OpenClaw config.

Execute immediately:
1. Confirm your role (identity name shown in system prompt)
2. Read agents/[your-id]/SOUL.md
3. **Read shared/status/team-dashboard.md** — team-wide status (understand the full picture in 5 seconds)
4. Read shared/decisions/active.md only if current work depends on active strategy or approval context
5. Read shared/inbox/to-[your-id].md
6. Read agents/[your-id]/MEMORY.md only when prior personal context is needed

Token rule: prefer the minimum files needed to act correctly. Do not re-read long files without a reason.

### Role Lookup
| identity.name | ID | Position |
|---------------|-----|----------|
(generated from role config)

## Inbox Protocol

### Write format
```
## [YYYY-MM-DD HH:MM] from:[your-id] priority:[high/normal/low] status:pending
To: [target-id]
Subject: ...
Expected output: ...
Deadline: ...
```

### Status flow
pending → received (confirm you saw it) → in-progress → done (move to ✅ Processed)
blocked = stuck, must explain why and who can help

### Rules
- Read inbox at session start, new messages → immediately set status:received
- Urgent (priority:high) also notify chief-of-staff
- Timeout monitoring by chief-of-staff (details in chief-of-staff SOUL.md)

## Output rules
- Personal memory: agents/[id]/MEMORY.md
- Daily log: agents/[id]/memory/YYYY-MM-DD.md
- To other agents: shared/inbox/to-[id].md
- Products: shared/products/[name]/
- Knowledge: shared/knowledge/
- Tasks: shared/kanban/

## Team Workflow Rules
See `shared/knowledge/team-workflow.md` for the full team workflow rules.

Minimum defaults:
- use the task handoff minimum fields
- close work through the done chain
- follow the minimal read order
- keep role memory writes inside responsibility boundaries

## Product Knowledge
Before any product-related decision, read shared/products/{product}/ knowledge files first.
These files are generated through the dual-dev pipeline and governed by product-lead.
All agents READ. Devops handles delivery-oriented scans and shared knowledge generation. Fullstack-dev handles module-level deep dive follow-up and implementation-driven knowledge updates using claude-only direct acpx / existing-session continuity. Context hygiene defaults: active cap 60, lifecycle window 100, verify before declare-done, and confirm cwd before writing/spawning. Product-lead REVIEWS.

## Prohibited
- Do not read/write other agents' private dirs
- Do not modify shared/decisions/ (CEO only)
- Do not delete shared/ files
- Do not publish externally without CEO approval
- Do not fabricate data
```

## shared/decisions/active.md

```markdown
# Active Decisions

> All agents must read this file every session. CEO directives and priorities.

## Strategy
- Team: {{TEAM_NAME}}
- Stage: Cold start
- Focus: GEO (AI search optimization)

## Growth Channel Priority
1. GEO - highest priority
2. SEO - long-term foundation
3. Community - precision acquisition
4. Content - brand building
5. Paid ads - not yet

## Team Rules
- All output goes to shared/ directories
- Agent communication via inbox files
- Daily briefs by Chief of Staff
- Major decisions require CEO approval

## CEO Decision Queue
(None yet)

---
*Fill in: main product, goals, resource allocation*
```

## shared/products/_index.md

```markdown
# Product Matrix

> All agents reference this file for product overview.
> After adding a product, send a message to product-lead to trigger the dual-dev Deep Dive flow.

## Product Template
- Name:
- URL:
- Code directory: (local path to project root)
- One-line description:
- Target users:
- Core features:
- Tech stack:
- Status: (dev / live / maintenance)
- Keywords (for GEO/SEO):
- Competitors:
- Differentiator:

---
*CEO: fill in your products. After filling, tell product-lead to run Deep Dive.*
```

## shared/products/{product}/ — Project Knowledge Directory

When the dual-dev Deep Dive flow runs (devops primary, fullstack-dev follow-up when needed), the following files are generated under `shared/products/{product}/`:

```
shared/products/{product}/
├── overview.md              ← Product positioning, users, business model (from _index.md)
├── architecture.md          ← System architecture: tech stack, design patterns, layering, multi-tenancy
├── database.md              ← Full table schema + field descriptions + relationships + indexes + migrations
├── api.md                   ← API endpoints with params, auth, versioning, rate limits
├── routes.md                ← Complete route table (Web + API + Console/Artisan)
├── models.md                ← ORM model relationship graph + scopes + accessors + observers + traits
├── services.md              ← Core business logic: service classes, state machines, workflows, validation rules
├── frontend.md              ← Component tree + page routing + state management + data fetching patterns
├── auth.md                  ← Auth scheme: guards/policies/roles/permissions matrix/OAuth/API tokens
├── integrations.md          ← Third-party: payment/email/SMS/storage/CDN/analytics/AI/scraping
├── jobs-events.md           ← Queue jobs + event listeners + scheduled tasks + notification channels
├── config-env.md            ← Env variables inventory + feature flags + cache strategy + config files
├── dependencies.md          ← Key dependency versions + custom packages + known vulnerabilities
├── devops.md                ← Deployment: CI/CD + Docker + server config + monitoring + logging + backups
├── test-coverage.md         ← Test strategy + coverage + weak spots + testing tools
├── tech-debt.md             ← TODO/FIXME/HACK inventory + known debt + dead code + complexity hotspots
├── domain-flows.md          ← Core user journeys + business domain boundaries + module coupling map
├── data-flow.md             ← Data lifecycle: external sources → import → process → store → output
├── i18n.md                  ← Internationalization: approach + language coverage + translation workflow
├── changelog.md             ← Scan diff log: what changed between scans, when, why
└── notes.md                 ← Agent discoveries, gotchas, implicit business rules found in code
```

### File Content Standards

Each knowledge file must capture not just WHAT but WHY:
- **Design decisions**: Why this approach was chosen (e.g., polymorphic relations vs single table)
- **Implicit business rules**: Rules hidden in code (e.g., orders auto-cancel after 72h)
- **Traps & pitfalls**: What breaks if you touch this module carelessly
- **Cross-module coupling**: Hidden dependencies where changing A silently breaks B
- **Performance hotspots**: Slow queries, bottleneck endpoints, N+1 problems

### Scan Levels

| Level | Scope | Content | Trigger |
|-------|-------|---------|---------|
| L0 Snapshot | Surface | Directory tree, tech stack, dependencies, env vars | First onboard |
| L1 Skeleton | Structure | DB schema, routes, model relations, component tree | First onboard or product-lead request |
| L2 Deep Dive | Logic | Services, business flows, auth, integrations, jobs | On-demand per module |
| L3 Health Check | Quality | Tech debt, dead code, complexity, security scan | Periodic or pre-release |
| L4 Incremental | Delta | Git diff → update affected knowledge files | After code changes |

### Per-Stack Scan Strategies

**Laravel/PHP:**
- `php artisan migrate:status` or parse migration files → database.md
- `php artisan route:list` or parse route files → routes.md + api.md
- Scan `app/Models/` for relationships, scopes, casts → models.md
- Scan `app/Services/`, `app/Actions/` → services.md
- Scan `app/Http/Middleware/`, `app/Policies/` → auth.md
- Scan `app/Jobs/`, `app/Listeners/`, `app/Console/Kernel.php` → jobs-events.md
- Parse `config/`, `.env.example` → config-env.md
- Parse `composer.json` + `composer.lock` → dependencies.md

**React/Vue/Frontend:**
- Scan `src/components/`, `src/pages/` → frontend.md (component tree)
- Parse router config → frontend.md (page routing)
- Scan state management (Redux/Vuex/Zustand/Pinia) → frontend.md
- Parse `package.json` → dependencies.md
- Scan API client layer → data-flow.md

**Python/Django/FastAPI:**
- Parse `models.py` → database.md + models.md
- Parse `urls.py` / route decorators → routes.md + api.md
- Scan `views.py`, `serializers.py` → services.md
- Parse `requirements.txt` / `pyproject.toml` → dependencies.md

**General (any stack):**
- `find . -name "*.md" | head` → existing docs
- `git log --oneline -20` → recent changes
- `grep -rn "TODO\|FIXME\|HACK\|XXX"` → tech-debt.md
- Directory tree (`tree -L 3`) → architecture.md
- `.env.example` or `.env.sample` → config-env.md
- `Dockerfile`, `docker-compose.yml`, CI configs → devops.md
- Test directories → test-coverage.md

### Template: architecture.md

```markdown
# Architecture - {Product Name}

> Auto-generated by the dual-dev Deep Dive flow. Last scan: YYYY-MM-DD

## Tech Stack
- Backend:
- Frontend:
- Database:
- Cache:
- Queue:
- Search:

## Directory Structure
(tree output, annotated)

## Design Patterns
- (Repository? Service layer? Event-driven? CQRS?)

## Layering
- (MVC? Clean Architecture? Hexagonal?)

## Multi-tenancy
- (Single DB? Schema-per-tenant? DB-per-tenant? N/A?)

## Key Architectural Decisions
| Decision | Rationale | Date | Impact |
|----------|-----------|------|--------|
```

### Template: database.md

```markdown
# Database - {Product Name}

> Auto-generated by the dual-dev Deep Dive flow. Last scan: YYYY-MM-DD

## Overview
- Engine:
- Total tables:
- Key relationships:

## Tables

### {table_name}
- Purpose:
- Key columns: (name, type, description)
- Relationships: (belongsTo/hasMany/morphTo etc.)
- Indexes:
- Business rules: (constraints, triggers, soft deletes, etc.)

## Entity Relationship Summary
(Mermaid or text diagram of key relationships)

## Migration History Notes
(Notable schema evolutions, breaking changes)
```

## shared/knowledge/tech-standards.md

```markdown
# Tech Standards

> All code-related agents must follow. Product Lead reviews, Fullstack Dev executes.

## Core Principles
1. First-principles design, KISS + SOLID + DRY implementation
2. Research first: search code, find reuse opportunities, trace call chains before modifying
3. Three questions before changing: Real problem? Existing code to reuse? What breaks?

## Red Lines
- No copy-paste duplication
- No breaking existing functionality
- No blind execution without thinking
- Critical paths must have error handling

## Code Quality
- Methods under 200 lines, files over 500 lines need refactoring
- Follow existing architecture and code style
- New tech requires CEO approval
- Auto-cleanup: unused imports, debug logs, temp files

## Security
- No hardcoded secrets
- DB changes via SQL scripts, not direct execution
- User input must be validated at system boundaries

## Change Control
- Minimal change scope
- Update all call sites when changing function signatures
- Clear commit messages

---

## Tech Stack Preferences (New Projects)
New project tech stack must be confirmed with CEO before starting.
- Backend: PHP (Laravel/ThinkPHP preferred), Python as fallback
- Frontend: Vue.js or React
- Mobile: Flutter or UniApp-X
- CSS: Tailwind CSS
- DB: MySQL or PostgreSQL
- Existing projects: keep current stack
- Always propose first, get approval, then code
*CEO: customize with your tech stack specifics*
```

## shared/knowledge/coding-quickstart.md

```markdown
# Coding Quick Start

> All agents (except chief-of-staff) can code in emergencies when fullstack-dev is busy.

## Before Coding
- **coding-lead skill loaded** → follow its flow directly, skip everything below
- **coding-lead NOT loaded** → continue reading

## Without coding-lead

### Coding Standards
Find first match (don't load multiple):
1. `shared/knowledge/tech-standards.md` (team-level)
2. Project-level `CLAUDE.md` or `.cursorrules`
3. Neither exists → basics: KISS/SOLID/DRY, minimal changes, no hardcoded secrets, clear commits

### Task Levels
| Level | Criteria | How |
|-------|----------|-----|
| Simple | Single file, <60 lines | Direct read/write/edit/exec |
| Medium | 2-5 files | Prefer spawn fullstack-dev; do it yourself only if urgent |
| Complex | Architecture, multi-module | Must spawn fullstack-dev |

### ACP
Default ACP execution guidance is Claude-only. Use acpx CLI via `exec` to call Claude Code. If `sessions_spawn(runtime="acp")` is available, use it.
Otherwise → spawn fullstack-dev to handle it.

### Safety
- Never code inside ~/.openclaw/
- No hardcoded secrets
- DB changes → SQL script, not direct execution
- Sensitive file changes need CEO approval

### After Coding
Notify fullstack-dev + product-lead via inbox
```

## Knowledge Base Files

### geo-playbook.md
```
# GEO Playbook
AI search engine optimization strategies and best practices.
(Growth Lead maintains)
```

### seo-playbook.md
```
# SEO Playbook
Traditional search engine optimization strategies.
(Growth Lead maintains)
```

### competitor-map.md
```
# Competitor Map
Competitor list and analysis.
(Intel Analyst maintains, updated Mon/Wed/Fri)
*CEO: fill in initial competitor info*
```

### content-guidelines.md
```
# Content Guidelines
Brand voice, writing standards, format requirements.
(Content Chief maintains)
```

### user-personas.md
```
# User Personas
Target user characteristics and needs.
(Data Analyst maintains)
```
