---
name: sveltekit-webapp
version: 1.1.1
description: |
  Scaffold and configure a production-ready SvelteKit PWA with opinionated defaults.
  Use when: creating a new web application, setting up a SvelteKit project, building a PWA,
  or when a user asks to "build me an app/site/webapp". Handles full setup including TypeScript,
  Tailwind, Skeleton + Bits UI components, testing, linting, and Vercel deployment.
  Generates a PRD with user stories for review, then upon user approval, builds through
  development, staging, and production with user approval at each stage.
requires_tools: [exec, Write, Edit, browser]
safety_notes: |
  This skill executes shell commands to scaffold and deploy web applications.
  All commands require user approval via the agent's safety framework.
  No commands are executed without user confirmation of the PRD.
---

# SvelteKit Webapp Skill

Scaffold production-ready SvelteKit PWAs with opinionated defaults and guided execution.

## Quick Start

1. **Describe your app** — Tell me what you want to build
2. **Review the PRD** — I'll generate a plan with user stories
3. **Approve** — I build, test, and deploy with your oversight
4. **Done** — Get a live URL + admin documentation

> "Build me a task tracker with due dates and priority labels"

That's all I need to start. I'll ask follow-up questions if needed.

## Prerequisites

These CLIs must be available (the skill will verify during preflight):

| CLI | Purpose | Install |
|-----|---------|---------|
| `sv` | SvelteKit scaffolding | `npm i -g sv` (or use via `pnpx`) |
| `pnpm` | Package manager | `npm i -g pnpm` |
| `gh` | GitHub repo creation | [cli.github.com](https://cli.github.com) |
| `vercel` | Deployment | `npm i -g vercel` |

Optional (if features require):
- `turso` — Turso database CLI

## Opinionated Defaults

This skill ships with sensible defaults that work well together. **All defaults can be overridden** via `SKILL-CONFIG.json`:

- **Component library:** Skeleton (Svelte 5 native) + Bits UI fallback
- **Package manager:** pnpm
- **Deployment:** Vercel
- **Add-ons:** ESLint, Prettier, Vitest, Playwright, mdsvex, MCP
- **State:** Svelte 5 runes ($state, $derived, $effect)

See [User Configuration](#user-configuration) for override details.

---

## User Configuration

Check `~/.openclaw/workspace/SKILL-CONFIG.json` for user-specific defaults before using skill defaults. User config overrides skill defaults for:
- Deployment provider (e.g., vercel, cloudflare, netlify)
- Package manager (pnpm, npm, yarn)
- Add-ons to always include
- MCP IDE configuration
- Component library preferences

## Workflow Overview

1. **Gather**: Freeform description + design references + targeted follow-ups
2. **Plan**: Generate complete PRD (scaffold, configure, features, tests as stories)
3. **Iterate**: Refine PRD with user until confirmed
4. **Preflight**: Verify all required auths and credentials
5. **Execute**: Guided build-deploy-verify cycle with user checkpoints (development → staging → production)

---

## Phase 1: Gather Project Description

A conversational, iterative approach to understanding what the user wants.

### 1a. Freeform Opening

Start with an open question:
- "What do you want to build?"
- "Describe the webapp you have in mind"

Let the user lead with what matters to them.

### 1b. Design References

Ask for inspiration:
```
Share 1-3 sites you'd like this to feel like 
(design, functionality, or both).

Examples:
- "Like Notion but simpler"
- "Fieldwire's mobile-first approach"
- "Linear's clean aesthetic"
```

"Show me what you like" communicates more than paragraphs of description.

### 1c. Visual Identity (Optional)

If design references suggest custom branding, ask:
```
Any specific colors, fonts, or logos you want to use?
(I can pre-configure the Tailwind theme)
```

### 1d. Targeted Follow-ups

Based on gaps in the description, ask specifically:

| Gap | Question |
|-----|----------|
| Users unclear | "Who's the primary user? (role, context)" |
| Core action unclear | "What's the ONE thing they must be able to do?" |
| Content unknown | "Any existing content/assets to incorporate?" |
| Scale unknown | "How many users do you expect? (ballpark)" |
| Timeline | "Any deadline driving this?" |

Only ask what's missing—don't interrogate.

### 1e. Structured Summary

Before proceeding, confirm understanding:

```
📝 PROJECT SUMMARY: [Name]

Purpose: [one sentence]
Primary user: [who]
Core action: [what they do]
Design inspiration: [references]
Visual identity: [colors/fonts if specified]
Key features:
  • [feature 1]
  • [feature 2]
  • [feature 3]

Technical signals detected:
  • Database: [yes/no] — [reason]
  • Authentication: [yes/no] — [reason]
  • Internationalization: [yes/no] — [reason]

Does this capture it? [Yes / Adjust]
```

Iterate until the user confirms.

---

## Phase 2: Plan (Generate PRD)

Generate a complete PRD with technical stack, user stories, and mock data strategy.

### Technical Stack

**Always Included:**
```
CLI:              pnpx sv (fallback: npx sv)
Template:         minimal
TypeScript:       yes
Package manager:  pnpm (fallback: npm)

Core add-ons (via sv add):
  ✓ eslint
  ✓ prettier
  ✓ mcp (claude-code)
  ✓ mdsvex
  ✓ tailwindcss (+ typography, forms plugins)
  ✓ vitest
  ✓ playwright

Post-scaffold:
  ✓ Skeleton (primary component library — Svelte 5 native, accessible)
  ✓ Bits UI (headless primitives — fallback for gaps/complex custom UI)
  ✓ vite-plugin-pwa (PWA support)
  ✓ Svelte 5 runes mode
  ✓ adapter-auto (auto-detects deployment target)
```

**Why Skeleton + Bits UI?**
- Skeleton: Full-featured component library built for Svelte 5, accessible by default
- Bits UI: Headless primitives when you need more control or custom styling
- Both play well together — Skeleton for speed, Bits for flexibility

**Inferred from Description:**
```
drizzle     → if needs database (ask: postgres/sqlite/turso)
lucia       → if needs auth
paraglide   → if needs i18n (ask: which languages)
```

### State Management

Follow Svelte 5 best practices (see https://svelte.dev/docs/kit/state-management):

- Use `$state()` runes for reactive state
- Use `$derived()` for computed values
- Use Svelte's context API (`setContext`/`getContext`) for cross-component state
- Server state flows through `load` functions → `data` prop
- **Never** store user-specific state in module-level variables (shared across requests)

### Code Style Preferences

Check `SKILL-CONFIG.json` for user preferences. Common patterns:

- **Prefer `bind:` over callbacks** — For child→parent data flow, use `bind:value` instead of `onchange` callback props. More declarative, less boilerplate.
- **Avoid `onMount`** — Use `$effect()` for side effects. It's reactive and works with SSR.
- **Runes everywhere** — `$state()`, `$derived()`, `$effect()` over legacy stores and lifecycle hooks.
- **Small components** — Default soft limit of ~200 lines per component (configurable in SKILL-CONFIG.json). If growing larger, extract sub-components. Small is beautiful. 🤩

### Directory Structure

`sv create` generates:
```
src/
├── routes/          # SvelteKit routes
├── app.html         # HTML template
├── app.d.ts         # Type declarations
└── app.css          # Global styles
static/              # Static assets
```

We add:
```
src/
├── lib/
│   ├── components/  # Reusable components (Skeleton + Bits UI)
│   ├── server/      # Server-only code (db client, auth)
│   ├── stores/      # Svelte stores (.svelte.ts for runes)
│   ├── utils/       # Helper functions
│   └── types/       # TypeScript types
static/
└── icons/           # PWA icons
```

### User Stories (prd.json)

**Story structure:**
```json
{
  "project": "ProjectName",
  "branchName": "dev",
  "description": "Brief description",
  "userStories": [
    {
      "id": "US-001",
      "title": "Scaffold project",
      "description": "Set up the base SvelteKit project.",
      "acceptanceCriteria": [...],
      "priority": 1,
      "passes": false,
      "blocked": false,
      "notes": ""
    }
  ]
}
```

**Story sizing rule:** Each story must fit in one context window. If it feels big, split it.

**Standard story sequence:**

1. **Scaffold** — `pnpx sv create`, add core add-ons
2. **Configure** — Skeleton + Bits UI, PWA, directory structure, VSCode workspace, Tailwind theme
3. **Mock Data** — Set up mock database/fixtures for development
4. **Foundation** — Root layout, design tokens, home page (INDEX PAGE CHECKPOINT)
5. **Features** — Core features from gathered requirements
6. **Infrastructure** — Database schema, migrations, auth (if needed)
7. **Polish** — PWA manifest, icons
8. **Tests** — E2E tests for critical flows

**Index Page Checkpoint:** After the index/home page is built (but before other pages), PAUSE execution and request user review. The index page establishes the visual direction—getting early feedback here avoids wasted work on subsequent pages.

See [references/scaffold-stories.md](references/scaffold-stories.md) for story templates.

### Mock Data Strategy

Development uses mock data; production uses real database.

```
Mock data approach:
- Generate mock data per-story as needed
- Store in src/lib/server/mocks/ or use MSW for API mocking
- E2E tests run against mock data locally
- Stage 2+ switches to real database
```

When `drizzle` is selected, include stories for:
- Initial schema creation
- Drizzle Kit configuration  
- First migration

### External Dependencies

Identify required credentials:

| Feature | Dependency | Required |
|---------|------------|----------|
| Any project | GitHub CLI | Yes |
| Deployment | Vercel CLI or adapter-auto | Yes |
| Database (postgres) | DATABASE_URL | For staging |
| Database (turso) | Turso CLI | For staging |
| OAuth providers | Client ID/Secret | For staging |
| Payments | Stripe API keys | For staging |

**Dev uses mocks; staging/production need real credentials.**

---

## Phase 3: Iterate Until Confirmed

Present the PRD and refine until the user approves.

### Present the PRD

```
📋 PRD: [Project Name]

TECHNICAL STACK:
✅ Always: TypeScript, Tailwind, Skeleton + Bits UI, ESLint, 
   Prettier, Vitest, Playwright, PWA
🔍 Inferred:
   [✓/✗] Database (drizzle) - [reason]
   [✓/✗] Authentication (lucia) - [reason]  
   [✓/✗] Internationalization (paraglide) - [reason]

USER STORIES: [N] stories
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
US-001: Scaffold project (Setup)
US-002: Configure Skeleton + Bits UI (Setup)
US-003: Set up mock data (Setup)
US-004: Create root layout (Foundation)
[... feature stories ...]
US-XXX: Configure PWA manifest (Polish)
US-XXX: Add E2E tests (Tests)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 External dependencies:
   • GitHub CLI (required now)
   • Vercel CLI (required now)
   • DATABASE_URL (required for staging)
   • [others for staging]

[Approve / See full stories / Edit stories / Change stack]
```

### Iteration Loop

Expect refinement. Common adjustments:
- Add/remove/modify user stories
- Change technical stack choices
- Adjust story priorities
- Split stories that are too large
- Add acceptance criteria

**Continue iterating until user explicitly approves.**

### Confirmation

When user approves:
```
✅ PRD CONFIRMED

[N] user stories ready for execution.
Proceeding to preflight checks...
```

---

## Phase 4: Preflight

Verify all dependencies. Development can start with mocks; staging needs real credentials.

### Run Checks

Verify authentication for required CLIs (GitHub, pnpm, Vercel, and optionally Turso). See [references/cli-commands.md](references/cli-commands.md#preflight-checks) for specific commands.

### Present Status

```
┌─────────────────────────────────────────────┐
│ 🔐 PREFLIGHT CHECK                          │
├─────────────────────────────────────────────┤
│ For development (Stage 1):                  │
│ ✓ GitHub CLI         authenticated          │
│ ✓ pnpm               installed              │
│ ✓ Write access       verified               │
│                                             │
│ For staging (Stage 2):                      │
│ ✓ Vercel CLI         authenticated          │
│ ✗ DATABASE_URL       not set                │
│                                             │
│ ─────────────────────────────────────────── │
│ Development can start now.                  │
│ DATABASE_URL needed before Stage 2.         │
│                                             │
│ [Start development / Resolve all first]     │
└─────────────────────────────────────────────┘
```

### Resolution

- Development can proceed with mock data
- Staging credentials can be resolved during Stage 1
- Production credentials verified before Stage 3

---

## Phase 5: Execute

Guided build-deploy-verify cycle with user checkpoints and live progress updates.

```
EXECUTE
├── Stage 1: Development (local, dev branch, mock data)
│   └── Build all features, tests pass locally
│
├── Stage 2: Staging (main branch, preview URL, real data)
│   └── Deploy, fix environment issues, tests pass on preview
│
└── Stage 3: Production (permanent URL)
    └── Connect domain, final verification, handoff
```

**Live progress updates:** Report each completed story:
```
✅ US-001: Scaffold project
✅ US-002: Configure Skeleton + Bits UI
✅ US-003: Set up mock data
⏳ US-004: Create root layout (in progress)
```

---

### Stage 1: Development

Build everything locally with mock data.

#### Setup

Initialize a git repository on a `dev` branch and create a `progress.txt` tracking file. See [references/cli-commands.md](references/cli-commands.md#initialize-repository) for commands.

#### Execute Stories via Sub-Agents

Use `sessions_spawn` to execute stories in parallel where dependencies allow.

**Wave structure:**
- **Wave 1:** Scaffold (must complete first)
- **Wave 2:** Configure (shadcn, PWA, directories) — parallel
- **Wave 3:** Mock data setup
- **Wave 4+:** Feature stories — parallel where independent
- **Final wave:** E2E test stories

**Sub-agent task template:**
```
Implement user story [US-XXX] for SvelteKit project at [project_path].

Story: [title]
Description: [description]

Acceptance Criteria:
- [criterion 1]
- [criterion 2]
- Typecheck passes

Instructions:
1. Read progress.txt for codebase patterns
2. Implement with minimal, focused changes
3. Use Svelte 5 runes for state ($state, $derived, $effect)
4. Use context API for cross-component state
5. Follow Conventional Commits: "feat: [US-XXX] - [title]"
6. Run `pnpm check` to verify
7. Update prd.json: passes: true
8. Append learnings to progress.txt
```

#### Handling Blocked Stories

If a story cannot be completed:
1. Mark as `blocked: true` in prd.json
2. Add explanation to `notes` field
3. Continue with other parallelizable stories
4. Report blocked stories in final summary

#### Stage 1 Exit Criteria

All checks must pass before proceeding: TypeScript verification, unit tests, and E2E tests against the local dev server with mocks. See [references/cli-commands.md](references/cli-commands.md#verify-build) for commands.

---

### Stage 2: Staging

Push to main, deploy to preview, switch from mocks to real data.

#### Verify Staging Credentials

Before proceeding, ensure all staging credentials are set:
- DATABASE_URL (if using database)
- OAuth client ID/secret (if using auth)
- Other API keys

If missing, pause and request from user.

#### Deploy via GitHub-Vercel Integration

**One-time setup (recommended over CLI deploys):**

Create a private GitHub repository, link to a Vercel project, and connect GitHub in the Vercel dashboard (Settings → Git → Connect Git Repository). Set the production branch to `main`. See [references/cli-commands.md](references/cli-commands.md#create-github-repo-and-push) for commands.

**Benefits of GitHub integration:**
- Push to deploy (no CLI needed after setup)
- Automatic preview URLs for all branches
- Persistent branch URLs: `[project]-git-dev-[team].vercel.app`
- Better CI/CD visibility in both dashboards

**Deploy to staging:**

Merge the `dev` branch into `main` and push. The push triggers Vercel to build and deploy automatically. See [references/cli-commands.md](references/cli-commands.md#merge-and-deploy-to-staging) for commands.

**Dev branch preview URL:**
After connecting GitHub, the `dev` branch gets a persistent preview URL:
`https://[project]-git-dev-[team].vercel.app`

This URL stays the same across commits—great for sharing with stakeholders.

#### Fix Environment Issues

Common issues in deployed environments:
- OAuth callback URLs (must match deployed domain)
- CORS configuration
- Environment variables not set in Vercel
- Database connection strings
- API endpoints using localhost

**Smart retry logic:**
1. **Diagnose** error type from stdout/stderr
2. **Attempt fix** based on error:
   - Dependency error → `pnpm install`
   - Type error → analyze `pnpm check` output
   - Test failure → re-run with verbose logging
   - Network/timeout → wait 30s, retry
3. **Escalate** after 3 failed attempts

#### Stage 2 Exit Criteria

E2E tests must pass against the Vercel preview URL. See [references/cli-commands.md](references/cli-commands.md#run-e2e-against-preview) for commands.

---

### Stage 3: Production

Deploy to production URL and hand off to user.

#### Deploy Production

With GitHub-Vercel integration, production deploys automatically when you push to `main`. Custom domains can be configured via the Vercel dashboard (Settings → Domains) or CLI. See [references/cli-commands.md](references/cli-commands.md#deploy-to-production) for commands.

#### Final Verification

Run E2E tests against the production URL to confirm everything works. See [references/cli-commands.md](references/cli-commands.md#final-verification) for commands.

#### Completion Report

```
🚀 DEPLOYED

Repository: github.com/[user]/[project-name]
Live URL: https://[production-url]

Build Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stories completed: [N]/[N]
Blocked stories: [list if any]
Tests passing: [X] unit, [Y] E2E
Deployment: Vercel production
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The app is live and ready for users.
```

---

## Phase 6: Handoff

Provide lifecycle management documentation.

### Generate Admin Manual

Create `ADMIN.md` in project root:

```markdown
# [Project Name] — Administration Guide

## Running Locally

\`\`\`bash
pnpm install
pnpm dev          # Start dev server at localhost:5173
\`\`\`

## Environment Variables

Copy `.env.example` to `.env` and configure:
- DATABASE_URL: [description]
- [other vars]

Set these in Vercel dashboard for production.

## Project Structure

\`\`\`
src/
├── routes/           # Pages and API routes
├── lib/components/   # UI components (Skeleton + Bits UI)
├── lib/server/       # Server-only code
└── lib/stores/       # State management
\`\`\`

## Adding New Pages

1. Create `src/routes/[page-name]/+page.svelte`
2. Add server data loading in `+page.server.ts`
3. Run `pnpm check` to verify types

## Database Migrations

\`\`\`bash
pnpm drizzle-kit generate  # Generate migration
pnpm drizzle-kit push      # Apply to database
\`\`\`

## Deployment

Push to `main` branch → auto-deploys to Vercel.

## Troubleshooting

- **Type errors**: Run `pnpm check`
- **Test failures**: Run `pnpm test:e2e --debug`
- **Build issues**: Check Vercel deployment logs
```

### Report Handoff

```
📖 HANDOFF COMPLETE

Admin manual: ADMIN.md
- How to run locally
- Environment variable setup
- Project structure overview
- Adding new pages
- Database migrations
- Deployment workflow
- Troubleshooting guide

The project is ready for ongoing development.
```

---

## Error Handling

If any stage fails and cannot be automatically resolved:

1. **Diagnose**: Analyze error output
2. **Categorize**: 
   - Dependency → `pnpm install`
   - Type error → show specific errors
   - Test failure → show failing tests
   - Network → retry with backoff
3. **Retry**: Up to 3 attempts with appropriate fix
4. **Escalate**: Report to user with:
   - What failed
   - What was tried
   - Specific error messages
   - Suggested manual resolution

**Never leave the project broken.** If Stage 2/3 fails, dev branch still works.

---

## Quick Reference

For all CLI commands and auth checks, see [references/cli-commands.md](references/cli-commands.md#quick-reference).

### Default Adapter

Use `adapter-auto` — automatically detects:
- Vercel → adapter-vercel
- Cloudflare → adapter-cloudflare
- Netlify → adapter-netlify
- Otherwise → adapter-node

### Database Options (drizzle)
- `postgresql` + `postgres.js` or `neon`
- `sqlite` + `better-sqlite3` or `libsql`
- `turso` + `@libsql/client`
