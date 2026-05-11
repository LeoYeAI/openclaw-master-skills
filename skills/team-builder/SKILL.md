---
name: team-builder
description: Deploy a multi-agent SaaS growth team on OpenClaw with shared workspace, async inbox communication, cron-scheduled tasks, deep project code scanning (Deep Dive), and optional Telegram integration. Use when building or upgrading multi-agent teams for SaaS/product-matrix work. Supports dual-development tracks by default: `devops` for delivery/deploy/environment/acceptance and `fullstack-dev` for implementation/module deep-dive/claude-only coding execution using direct acpx or existing session continuity. Includes Project Deep Dive capability so shared product knowledge files (DB schema, routes, models, services, auth, integrations, tech debt, etc.) can be generated and consumed efficiently by all agents. Supports customizable team name, agent roles, models, timezone, and Telegram bots.
---

# Team Builder

Deploy a reusable multi-agent SaaS/growth team template on OpenClaw in one shot.

## System Impact & Prerequisites

> **Read before running.** This skill creates files and modifies system config.

### What it creates
- A new workspace directory with ~40 files (agent configs, shared knowledge, inboxes, kanban)
- `apply-config.js` -- script that **modifies `~/.openclaw/openclaw.json`** (adds agents, bindings, agentToAgent config). Auto-backs up before writing.
- `create-crons.ps1` / `create-crons.sh` -- scripts that **create cron jobs** via `openclaw cron add`
- After running these scripts you must **restart the gateway** (`openclaw gateway restart`)

### What it does NOT do automatically
- Does not modify openclaw.json directly -- you run `apply-config.js` yourself
- Does not create cron jobs directly -- you run the cron script yourself
- Does not restart the gateway -- you do that manually

### Optional: Telegram
- If you provide bot tokens during setup, `apply-config.js` will also add Telegram account configs and bindings
- Requires: Telegram bot tokens from @BotFather, your Telegram user ID
- Requires: network access to Telegram API (proxy configurable)

### Optional: ACP / Claude Code
- The `fullstack-dev` agent is configured as the implementation-focused Claude coding role
- Current production path is **claude only**
- Preferred execution modes: simple direct, medium Claude ACP `run` or direct acpx, complex work via existing fullstack-dev continuity + context files
- Do not assume IM-bound ACP `session` persistence is available

### Credentials involved
- **Telegram bot tokens** (optional) -- stored in openclaw.json, used for agent-to-Telegram binding
- **Model API keys** -- must already be configured in your OpenClaw model providers (not handled by this skill)

### Recommended
- Review generated `apply-config.js` before running
- Check the backup of openclaw.json after running
- Test with 2-3 agents before enabling all cron jobs

## Team Architecture

Default reference architecture for a SaaS/growth multi-agent team (customizable to 2-10 agents):

```
CEO
 |-- Chief of Staff (dispatch + strategy + efficiency)
 |-- Data Analyst (data + user research)
 |-- Growth Lead (GEO + SEO + community + social media)
 |-- Content Chief (strategy + writing + copywriting + i18n)
 |-- Intel Analyst (competitor monitoring + market trends)
 |-- Product Lead (product management + tech architecture)
 |-- DevOps (delivery / deploy / environment / acceptance)
 |-- Fullstack Dev (implementation / module deep dive / ACP coding session)
```

### Multi-Team Support

One OpenClaw instance can run multiple teams:

```bash
node <skill-dir>/scripts/deploy.js                  # default team
node <skill-dir>/scripts/deploy.js --team alpha      # named team "alpha"
node <skill-dir>/scripts/deploy.js --team beta       # named team "beta"
```

Named teams use prefixed agent IDs (`alpha-chief-of-staff`, `beta-growth-lead`) to avoid conflicts. Each team gets its own workspace subdirectory.

### Flexible Team Size

The wizard lets you select 2-10 agents from the available roles. Skip roles you don't need. The 8-agent default covers most SaaS scenarios with dual-dev routing, but you can run leaner (3-4 agents) or expand with custom roles.

### Model Auto-Detection

The wizard scans your `openclaw.json` for registered model providers and auto-suggests models by role type:

| Role Type | Best For | Auto-detect Pattern |
|-----------|----------|-------------------|
| Thinking | Strategic roles (chief, growth, content, product) | /glm-5\|opus\|o1\|deepthink/i |
| Execution | Operational roles (data, intel, fullstack) | /glm-4\|sonnet\|gpt-4/i |
| Fast | Lightweight tasks | /flash\|haiku\|mini/i |

You can always override with manual model IDs.

## Setup / Config / Scripts

### Required Inputs
- Team name
- Workspace dir
- Timezone
- Morning brief hour
- Evening brief hour
- Thinking model
- Execution model
- CEO title

### Optional Inputs
- Telegram user ID
- Telegram bot tokens
- Proxy
- ACP coding agent（给 fullstack-dev 使用）

### Core Scripts
```bash
node <skill-dir>/scripts/deploy.js
node <workspace-dir>/apply-config.js
powershell <workspace-dir>/create-crons.ps1
bash <workspace-dir>/create-crons.sh
openclaw gateway restart
```

### Execution Priority
- First: matched execution skill (for coding work, `coding-lead` if loaded)
- Second: agent-role fallback when no matching skill is loaded
- Third: templates/README explain boundaries and ownership only; they should not override matched skills

### Context File Hygiene
- Active context files live under `<project>/.openclaw/`
- Reuse one context file per active code chain when possible
- Naming pattern: `context-<task-slug>.md`
- Active context file cap per project: **60**
- Context-file lifecycle window per project: **100 total files** across active + archive
- Completed or stale files should be deleted or moved to `.openclaw/archive/`

### Current Dual-Dev Standard
- fullstack-dev：实现、模块深挖、开发文档、接口文档、Claude coding 执行；默认 coding skill 可采用 `coding-lead`，其中 simple 任务直做，medium 倾向 Claude ACP `run` 或 direct acpx，complex 通过现有会话连续协作 + 上下文文件推进，不把 ACP `session` 持久线程作为正式主路径；context 活跃上限 60、生命周期总窗口 100；并行允许但必须先定义边界，总上限 5 个工作单元
- devops：交付、部署、环境、回归、冒烟、自动QA、发布门禁
- product-lead：澄清、PRD、验收标准，不完整不得派工
- chief-of-staff：路由、裁决、控制 token 浪费

## Deployment Flow

### Step 1: Collect Configuration

Ask the user for these inputs (use defaults if not provided):

| Parameter | Default | Description |
|-----------|---------|-------------|
| Team name | Alpha Team | Used in all docs and configs |
| Workspace dir | `~/.openclaw/workspace-team` | Shared workspace root |
| Timezone | Asia/Shanghai | For cron schedules |
| Morning brief hour | 8 | Chief's morning report |
| Evening brief hour | 18 | Chief's evening report |
| Thinking model | zai/glm-5 | For strategic roles |
| Execution model | zai/glm-4.7 | For execution roles |
| CEO title | Boss | How agents address the CEO |

Optional: Telegram user ID, proxy, and 7 bot tokens.

### Step 2: Run Deploy Script

```bash
node <skill-dir>/scripts/deploy.js
```

Interactive -- asks all questions from Step 1, generates the full workspace.

### Step 2b: Non-interactive / Verify Mode

Prepare a JSON config file:

```json
{
  "teamName": "Alpha Team",
  "workspaceDir": "~/.openclaw/workspace-team",
  "timezone": "Asia/Shanghai",
  "morningHour": 8,
  "eveningHour": 18,
  "thinkingModel": "zai/glm-5",
  "executionModel": "zai/glm-4.7",
  "ceoTitle": "Boss",
  "roles": ["chief-of-staff","data-analyst","growth-lead","content-chief","intel-analyst","product-lead","devops","fullstack-dev"]
}
```

Run:

```bash
node <skill-dir>/scripts/deploy.js --config team-builder.json
node <skill-dir>/scripts/deploy.js --verify --config team-builder.json
```

`--verify` checks that generated files contain the expected dual-dev model, role ownership, and cron entries.

### Step 3: Apply Config

```bash
node <workspace-dir>/apply-config.js
```

Adds agents to openclaw.json, preserving existing config.

### Step 4: Create Cron Jobs

```bash
# Windows
powershell <workspace-dir>/create-crons.ps1

# Linux/Mac
bash <workspace-dir>/create-crons.sh
```

### Step 5: Restart Gateway

```bash
openclaw gateway restart
```

### Step 6: Fill Business Info

User must edit:
- `shared/decisions/active.md` -- strategy, priorities
- `shared/products/_index.md` -- products overview (≤5 lines per product: URL, code path, positioning, tech, status). Detailed info goes in each product's `overview.md`.
- `shared/knowledge/competitor-map.md` -- competitor analysis
- `shared/knowledge/tech-standards.md` -- coding standards

### Step 7: Trigger Deep Dive Scans

After filling in products with code directories, tell product-lead to trigger Deep Dive scans:
1. Product-lead sends delivery-oriented scan requests to devops via inbox
2. Devops enters each project directory and generates shared knowledge / deployment-oriented scan outputs
3. Fullstack-dev picks up module-level deep dive or implementation follow-up when needed
4. Product-lead reviews the generated files for completeness and acceptance impact
5. All agents now have deep project understanding for informed decisions

## Cron Schedule

| Offset | Agent | Task | Frequency |
|--------|-------|------|-----------|
| H-1 | Data Analyst | Data + user feedback | Daily |
| H-1 | Intel Analyst | Competitor scan | Mon/Wed/Fri |
| H | Chief of Staff | Morning brief (announced) | Daily |
| H+1 | Growth Lead | GEO + SEO + community | Daily |
| H+1 | Content Chief | Weekly content plan | Monday |
| H+2 | DevOps | Delivery / environment / Deep Dive / acceptance | Daily |
| H+10 | Chief of Staff | Evening brief (announced) | Daily |

(H = morning brief hour)

## Generated File Structure

```
<workspace>/
├── AGENTS.md, SOUL.md, USER.md  (auto-injected)
├── apply-config.js, create-crons.ps1/.sh, README.md
├── agents/<8 agent dirs>/       (SOUL.md + MEMORY.md + memory/)
└── shared/
    ├── briefings/, decisions/, inbox/ (v2: with status tracking)
    ├── status/team-dashboard.md     (chief-of-staff maintains, all agents read first)
    ├── data/                        (public data pool, data-analyst writes, all read)
    ├── kanban/, knowledge/
    └── products/
        ├── _index.md                (product matrix overview)
        ├── _template/               (knowledge directory template)
        └── {product}/               (per-product knowledge, up to 20 files)
            ├── overview.md, architecture.md, database.md, api.md, routes.md
            ├── models.md, services.md, frontend.md, auth.md, integrations.md
            ├── jobs-events.md, config-env.md, dependencies.md, devops.md
            ├── test-coverage.md, tech-debt.md, domain-flows.md, data-flow.md
            ├── i18n.md, changelog.md, notes.md
```



## Knowledge Governance

Each shared knowledge file has a designated owner. Only the owner agent updates it; others read only.

| File | Owner | Update Trigger |
|------|-------|---------------|
| geo-playbook.md | growth-lead | After GEO experiments/discoveries |
| seo-playbook.md | growth-lead | After SEO experiments |
| competitor-map.md | intel-analyst | After each competitor scan |
| content-guidelines.md | content-chief | After proven writing patterns |
| user-personas.md | data-analyst | After new user insights |
| tech-standards.md | product-lead | After architecture decisions |

### Update Protocol
When updating a knowledge file, the owner must:
1. Add a dated entry at the top: `## [YYYY-MM-DD] <what changed>`
2. Include the reason and data evidence
3. Never delete existing entries without CEO approval (append, don't replace)

### Chief of Staff Governance
The chief-of-staff monitors knowledge file health during weekly reviews:
- Are files being updated regularly?
- Any conflicting information between files?
- Any stale entries that should be archived?

## Self-Evolution Pattern

Agents improve their own strategies over time through a feedback loop:

```
1. Execute task (cron or inbox triggered)
2. Collect results (data, metrics, outcomes)
3. Analyze: what worked vs what didn't
4. Update knowledge files with proven strategies (with evidence)
5. Next execution reads updated knowledge → better performance
```

This is NOT the agent randomly changing rules. Updates must be:
- **Data-driven**: backed by metrics or concrete outcomes
- **Incremental**: append new findings, don't rewrite everything
- **Traceable**: dated with evidence so others can verify

### What Agents Can Self-Update
- Their own knowledge files (per ownership table above)
- Their own MEMORY.md (lessons learned, decisions)
- shared/data/ outputs (data-analyst only)

### What Requires CEO Approval
- shared/decisions/active.md (strategy changes)
- Adding/removing agents or changing team architecture
- External publishing or spending decisions

## Public Data Layer

The `shared/data/` directory serves as a read-only data pool for all agents:

- **data-analyst** writes: daily metrics, user feedback summaries, anomaly alerts
- **All agents** read: to inform their own decisions
- Format: structured markdown or JSON, dated filenames (e.g., `metrics-2026-03-01.md`)
- Retention: keep 30 days, archive older files

## Project Deep Dive — Code Scanning

Agents can deeply understand each SaaS product through automated code scanning. This is critical — without deep project knowledge, all team decisions are surface-level.

### How It Works

1. CEO adds a product to `shared/products/_index.md` (name, URL, code directory, tech stack)
2. Product Lead triggers a delivery-oriented Deep Dive scan by messaging DevOps via inbox
3. DevOps enters the project directory (read-only) and generates shared knowledge / delivery-oriented scan outputs
4. Fullstack Dev picks up module-level deep dive or implementation follow-up when needed
5. Knowledge files are generated in `shared/products/{product}/`
6. All agents consume these files **via manifest-based lazy loading** (never read all at once)

### Manifest-Based Lazy Loading (MANDATORY)

Each product directory includes a `manifest.json` (~200 tokens) that lists all files with one-line summaries and a `taskFileMap` mapping task types to relevant files.

**Agent workflow:**
1. Read `_index.md` → identify which product
2. Read `{product}/manifest.json` → see all files + summaries (~200 tokens)
3. Based on `taskFileMap` or summaries, read only 1-3 relevant files
4. Never read more than 5 product files per session

**Why:** With 15+ products × 20 files each, full loading = 40K+ tokens per product. Manifest loading = 200 tokens + only what's needed.

**DevOps MUST regenerate `manifest.json`** after every delivery-oriented scan (L0-L4). Fullstack Dev updates it when doing module-level follow-up that changes knowledge scope. Template in `_template/manifest.json`.

### Manifest Quality Standards

摘要不能为了省 token 丢掉关键信息。每条摘要须满足：
- **核心文件**（database/models/services/routes/integrations）：50-130字，列出关键实体名/数量/域名
- **中等文件**（auth/frontend/commands/config）：30-80字，点明方案和范围
- **轻量文件**（changelog/notes/metrics）：可以短（<20字）
- **taskFileMap**：必须覆盖该产品的所有核心业务场景（不少于8个映射）
- **codeStats**：必须包含文件数、行数、模型数、表数等量化指标

### Product Knowledge Directory

Each product gets a knowledge directory with up to 20 files + manifest:

```
shared/products/{product}/
├── manifest.json        ← **INDEX** (~200 tokens): file list, summaries, taskFileMap
├── overview.md          ← Product positioning (from _index.md)
├── architecture.md      ← System architecture, tech stack, design patterns, layering
├── database.md          ← Full table schema, relationships, indexes, migrations
├── api.md               ← API endpoints, params, auth, versioning
├── routes.md            ← Complete route table (Web + API + Console)
├── models.md            ← ORM relationships, scopes, accessors, observers
├── services.md          ← Business logic, state machines, workflows, validation
├── frontend.md          ← Component tree, page routing, state management
├── auth.md              ← Auth scheme, roles/permissions matrix, OAuth
├── integrations.md      ← Third-party: payment/email/SMS/storage/CDN/analytics
├── jobs-events.md       ← Queue jobs, event listeners, scheduled tasks, notifications
├── config-env.md        ← Environment variables, feature flags, cache strategy
├── dependencies.md      ← Key dependencies, custom packages, vulnerabilities
├── devops.md            ← Deployment, CI/CD, Docker, monitoring, logging
├── test-coverage.md     ← Test strategy, coverage, weak spots
├── tech-debt.md         ← TODO/FIXME/HACK inventory, dead code, complexity hotspots
├── domain-flows.md      ← Core user journeys, domain boundaries, module coupling
├── data-flow.md         ← Data lifecycle: external → import → process → store → output
├── i18n.md              ← Internationalization, language coverage
├── changelog.md         ← Scan diff log (what changed between scans)
└── notes.md             ← Agent discoveries, gotchas, implicit rules
```

### Scan Levels

| Level | Scope | When | Output |
|-------|-------|------|--------|
| L0 Snapshot | Surface: directory tree, packages, env | First onboard | architecture, dependencies, config-env |
| L1 Skeleton | Structure: DB, routes, models, components | First onboard | database, routes, api, models, frontend |
| L2 Deep Dive | Logic: services, auth, jobs, integrations | On-demand per module | services, auth, jobs-events, integrations, domain-flows, data-flow |
| L3 Health Check | Quality: tech debt, tests, security | Periodic / pre-release | tech-debt, test-coverage, devops |
| L4 Incremental | Delta: git diff → update affected files | After code changes | changelog + targeted updates |

### Content Standards

Knowledge files capture not just WHAT exists but WHY:
- **Design decisions**: Why this approach was chosen
- **Implicit business rules**: Logic buried in code (e.g., "orders auto-cancel after 72h")
- **Gotchas**: What breaks if you touch this module carelessly
- **Cross-module coupling**: Where changing A silently breaks B
- **Performance hotspots**: N+1 queries, missing indexes, bottleneck endpoints

### Role Responsibilities

| Role | Responsibility |
|------|---------------|
| Product Lead | **Clarification / PRD / acceptance**: complete clarification, PRD, user stories, acceptance criteria, and review knowledge freshness before delegating |
| DevOps | **Delivery / QA gate / Deep Dive**: enter code directory for deployment-oriented scans, maintain release checklist, smoke/regression testing, auto-QA access, and generate/update shared product knowledge files |
| Fullstack Dev | **Implementation / docs / Deep Dive follow-up**: continue module-level deep dive, code analysis, implementation, dev docs, interface docs, and ACP session work |
| Chief of Staff | **Routing / escalation**: split implementation vs delivery tasks, prevent duplicate labor, escalate blockers |
| All Agents | **Consumption**: read product knowledge before any product-related decision |

### Per-Stack Auto-Detection

Fullstack Dev auto-detects tech stack and applies stack-specific scan strategies:
- **Laravel/PHP**: migrations, route:list, Models, Services, Middleware, Policies, Jobs, Console/Kernel
- **React/Vue**: components, router, stores, API client, i18n
- **Python/Django/FastAPI**: models.py, urls.py, views.py, middleware, celery
- **General**: tree, git log, grep TODO/FIXME, .env.example, Docker, CI, tests

## Team Coordination v2

### Inbox Protocol v2 (status tracking)

Every inbox message now has a `status` field:
- `pending` → `received` → `in-progress` → `done` (or `blocked`)
- Chief-of-staff monitors timeouts: high>4h, normal>24h pending = intervention
- Blocked >8h = escalation to CEO
- Recipients MUST update status immediately upon reading

### Team Dashboard (`shared/status/team-dashboard.md`)

Chief-of-staff maintains a "live scoreboard" updated every session:
- 🔴 Urgent/Blocked items
- 📊 Per-agent status table (last active, current task, status icon)
- 📬 Unprocessed inbox summary (pending/blocked messages across all inboxes)
- 🔗 Cross-agent task chain tracking (A→B→C with per-step status)
- 📅 Today/Tomorrow focus

**All agents read this file first when waking up.** 5-second situational awareness.

### Chief-of-Staff as Router

The chief is upgraded from "briefing writer" to "active team router":
- **Blocker detection**: scans all inboxes for overdue messages
- **Active dispatch**: writes reminders directly to lagging agents' inboxes
- **Task chain tracking**: identifies multi-agent workflows and tracks each step
- **Escalation**: persistent blockers get flagged to CEO
- **Runs 4x/day** (morning brief, midday patrol, afternoon patrol, evening brief)

### Cron Schedule (10 jobs, up from 7)

| Time | Agent | Type | Purpose |
|------|-------|------|---------|
| 07:00 | data-analyst | daily | Data pull + feedback scan |
| 08:00 | chief-of-staff | **announce** | Morning: router scan + brief + quality |
| 09:00 | growth-lead | daily | GEO/SEO/community |
| 09:00 | product-lead | **daily (NEW)** | Inbox + clarification/PRD + task delegation |
| 10:00 | content-chief | **daily M-F (was weekly)** | Content creation + collaboration |
| 10:00 | devops | **daily (delivery track)** | Inbox + Deep Dive + delivery + QA gate |
| 12:00 | chief-of-staff | **patrol (NEW)** | Router scan only, no brief |
| 15:00 | chief-of-staff | **patrol (NEW)** | Router scan only, no brief |
| 18:00 | chief-of-staff | **announce** | Evening: router scan + summary + next day plan |
| 07:00 M/W/F | intel-analyst | 3x/week | Competitor scan |

### Why These Changes Matter

| Before | After | Impact |
|--------|-------|--------|
| Inbox = blind drop | Inbox with status tracking | Messages are acknowledged and trackable |
| Chief 2x/day | Chief 4x/day with router role | Blockers caught within hours, not days |
| Content-chief 1x/week | Daily M-F | Actually produces content |
| Product-lead no cron | Daily | Knowledge governance happens |
| No team dashboard | Dashboard every session | All agents know the full picture |
| No timeout detection | Automatic timeout rules | Nothing falls through cracks |

## Key Design Decisions

- **Shared workspace** so qmd indexes everything for all agents
- **Inbox Protocol v2** with status tracking and timeout rules for reliable async communication
- **Chief as Router** — not just a briefing writer but active coordinator who detects and resolves blockers
- **Team Dashboard** — single source of truth for team-wide status, maintained by chief every session
- **GEO as #1 priority** (AI search = blue ocean)
- **Fullstack Dev spawns Claude Code** via ACP for complex implementation tasks
- **DevOps owns delivery and QA gate** so implementation and release responsibilities stay separated
- **Project Deep Dive** gives all agents deep codebase understanding, not just surface-level product overviews

## Customization

Edit ROLES array in `scripts/deploy.js` to add/remove agents.
Edit `references/soul-templates.md` for SOUL.md templates.
Edit `references/shared-templates.md` for shared file templates.
