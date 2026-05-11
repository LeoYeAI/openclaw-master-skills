---
name: afrexai-claude-code-production
version: "1.0.0"
description: "Complete Claude Code productivity system — project setup, prompting patterns, sub-agent orchestration, context management, debugging, refactoring, TDD, and shipping 10X faster. Zero scripts needed."
author: "AfrexAI"
license: "MIT"
metadata: {"openclaw":{"emoji":"⚡"}}
---

# Claude Code Production Engineering

The complete methodology for shipping production code with Claude Code at 10X speed. Not installation scripts — actual patterns, workflows, and techniques that compound your output.

---

## Quick Health Check (run mentally before every session)

| Signal | Healthy | Fix |
|--------|---------|-----|
| CLAUDE.md exists at project root | ✅ | Create one (see §1) |
| .claueignore configured | ✅ | Add noise directories |
| Session context under 60% | ✅ | `/compact` or start fresh |
| Clear task scope before prompting | ✅ | Write task brief first |
| Tests exist for target code | ✅ | Write tests first (§7) |
| Git clean before big changes | ✅ | Commit or stash |
| Sub-agents for parallel work | ✅ | Use `/new` or Task tool |
| Verifying output, not trusting blindly | ✅ | Always review diffs |

Score: /8. Below 6 = slow, buggy sessions. Fix before coding.

---

## 1. Project Setup — CLAUDE.md Architecture

CLAUDE.md is your project's brain. Claude reads it at session start. A good one saves thousands of tokens per session.

### Template

```markdown
# Project: [name]

## Tech Stack
- Language: TypeScript (strict mode)
- Framework: Next.js 15 App Router
- Database: PostgreSQL via Drizzle ORM
- Testing: Vitest + Playwright
- Styling: Tailwind CSS v4

## Architecture Rules
- Max 50 lines per function, 300 lines per file
- One responsibility per file
- All exports typed — no `any`
- Errors as values (Result type), not thrown exceptions
- Database: migrations via `drizzle-kit generate` then `drizzle-kit push`

## File Structure
src/
  app/         → Next.js routes (thin — call services)
  lib/         → Business logic (pure functions)
  db/          → Schema, migrations, queries
  components/  → UI (server components default, 'use client' only when needed)
  types/       → Shared type definitions

## Commands
- `pnpm dev` — start dev server
- `pnpm test` — run vitest
- `pnpm test:e2e` — run playwright
- `pnpm lint` — eslint + tsc --noEmit
- `pnpm db:generate` — generate migration
- `pnpm db:push` — apply migration

## Conventions
- Imports: absolute from `@/` (mapped to `src/`)
- Naming: camelCase functions, PascalCase components/types, SCREAMING_SNAKE constants
- Commits: conventional commits (feat:, fix:, refactor:, test:, docs:)
- PRs: always create branch, never commit to main directly
```

### CLAUDE.md Rules

1. **Be specific** — "TypeScript strict" not "use types." Stack versions, not just names.
2. **Include commands** — Claude needs to know how to run things. Exact commands, not descriptions.
3. **Architecture decisions** — document WHY, not just what. "Errors as values because we use Result type" tells Claude the pattern.
4. **Keep it under 200 lines** — CLAUDE.md is read every session. Bloat wastes tokens.
5. **Update when patterns change** — stale CLAUDE.md causes Claude to fight your codebase.
6. **Nested CLAUDE.md** — subdirectories can have their own. Claude merges them. Use for monorepo packages.

### .claueignore

```
node_modules/
.next/
dist/
coverage/
*.lock
.git/
*.min.js
*.map
public/assets/
```

Rule: if Claude doesn't need to read it, ignore it. Large lock files and build artifacts waste context.

---

## 2. Prompting Patterns — The 5 That Matter

### Pattern 1: Task Brief (use for any non-trivial work)

```
Task: Add user authentication with magic links
Context: Using Resend for email, no password system exists yet
Constraints:
- Server actions only (no API routes)
- Session via httpOnly cookies
- Token expires in 15 minutes
Acceptance: User enters email → receives link → clicks → logged in → cookie set
Start with: the database schema for sessions and tokens
```

Why it works: scope + constraints + acceptance criteria + starting point. Claude doesn't wander.

### Pattern 2: Show, Don't Tell

Bad: "Make the API more robust"
Good: "Add input validation to POST /api/users — validate email format, name 1-100 chars, reject extra fields. Return 422 with field-level errors matching this shape: `{ errors: { field: string, message: string }[] }`"

Rule: if you can't describe the exact output shape, you don't know what you want yet. Think first.

### Pattern 3: Incremental Refinement

```
Step 1: "Create the database schema for a todo app with projects and tasks"
[review output]
Step 2: "Now add the CRUD service layer for tasks — pure functions, no framework imports"
[review output]
Step 3: "Now the API routes that call those services — input validation with zod"
```

Why: Claude produces better code in focused steps than in one massive prompt. Each step builds verified context.

### Pattern 4: Fix With Evidence

Bad: "It's broken"
Good: "Running `pnpm test` gives this error:
```
TypeError: Cannot read properties of undefined (reading 'id')
  at getUserById (src/lib/users.ts:23:15)
```
The function expects a User object but receives undefined when the database query returns no rows. Add a null check and return a Result type."

Rule: paste the actual error. Claude is excellent at fixing bugs when it can see the stack trace.

### Pattern 5: Architecture Discussion

```
I'm deciding between these approaches for real-time updates:
A) Server-Sent Events from Next.js API routes
B) WebSocket via separate service
C) Polling every 5 seconds

Context: 500 concurrent users, updates every 30 seconds on average, deployed on Vercel.

What are the tradeoffs? Recommend one with reasoning.
```

Use this for decisions, not implementation. Get the answer, THEN switch to Task Brief for building.

---

## 3. Context Management — The #1 Productivity Lever

### Context Is Milk — It Spoils

| Context % | Action |
|-----------|--------|
| 0-30% | Fresh. Do complex work here. |
| 30-60% | Good. Continue current task. |
| 60-80% | Getting stale. Finish current unit, then compact. |
| 80%+ | Dangerous. `/compact` immediately or start new session. |

### When to Start Fresh (`/new`)

- Switching to unrelated task
- Context above 70%
- Claude starts repeating itself or making mistakes it didn't make earlier
- After shipping a feature (clean slate for next one)

### When to Compact (`/compact`)

- Mid-task but context bloating from exploration
- After a debugging session (lots of error output consumed context)
- Before a complex implementation step

### Context-Efficient Habits

1. **Don't paste entire files** — reference by path. Claude can read them.
2. **Don't re-explain** — if it's in CLAUDE.md, don't repeat it in prompts.
3. **Use specific file paths** — "Look at `src/lib/auth.ts` line 45" not "look at the auth code."
4. **Close tangents** — if Claude goes down a rabbit hole, redirect immediately. Don't let bad output consume context.
5. **One concern per message** — "Fix the auth bug AND refactor the database layer AND add tests" = context explosion. Sequential > parallel in a single session.

---

## 4. Sub-Agent Orchestration — Parallel Productivity

### When to Use Sub-Agents

| Scenario | Pattern |
|----------|---------|
| Independent features | Spawn sub-agent per feature |
| Tests + implementation | One agent writes tests, main writes code |
| Research + build | Sub-agent researches API docs, main builds |
| Refactor + maintain | Sub-agent refactors module A, main works on B |
| Code review | Sub-agent reviews your PR with fresh eyes |

### Task Tool Pattern (Claude Code native)

```
Use the Task tool to:
1. Research the Stripe API for subscription billing
2. Return: webhook event types we need, API calls for create/update/cancel, error codes to handle
```

Task tool spawns a sub-agent with its own context. Results come back summarized. Perfect for research that would bloat your main context.

### Handoff Documents

When a sub-agent finishes complex work, have it write a HANDOFF.md:

```markdown
## What Was Done
- Implemented Stripe webhook handler at src/app/api/webhooks/stripe/route.ts
- Added 4 event handlers: checkout.session.completed, invoice.paid, invoice.payment_failed, customer.subscription.deleted

## Key Decisions
- Used Stripe SDK v14 (not raw HTTP) for type safety
- Webhook signature verification via stripe.webhooks.constructEvent()
- Idempotency: check processed_events table before handling

## What's Next
- Wire up subscription status updates to user table
- Add retry logic for failed database writes
- E2E test with Stripe CLI: `stripe trigger checkout.session.completed`

## Gotchas
- Must use raw body (not parsed JSON) for signature verification
- Next.js App Router: export const runtime = 'nodejs' (not edge)
```

---

## 5. Debugging Workflow — Systematic, Not Random

### The DEBUG Protocol

**D**escribe the symptom (what you see vs. what you expect)
**E**rror output (paste full stack trace, not summary)
**B**isect (when did it last work? what changed?)
**U**nit isolate (can you reproduce in a test?)
**G**enerate hypothesis (ask Claude for 3 possible causes, ranked)

### Effective Bug Prompts

```
Bug: Users see stale data after updating their profile.

Expected: After PUT /api/profile, the profile page shows updated data.
Actual: Old data persists until hard refresh (Cmd+Shift+R).

Stack:
- Next.js 15 App Router
- Server component fetches user data
- Client component with form calls server action
- Server action calls db.update()

Hypothesis: Next.js is caching the server component fetch. Need to revalidate.

Can you confirm and show me the fix?
```

### When Claude Gets Stuck

1. **Add constraints** — "The fix must not change the API contract" narrows the search space.
2. **Share what you've tried** — "I already tried revalidatePath('/profile') and it didn't work because..."
3. **Ask for alternatives** — "Give me 3 different approaches to solve this, with tradeoffs."
4. **Fresh session** — sometimes the context is poisoned. Start clean with just the bug description.

---

## 6. Refactoring Patterns — Safe Large-Scale Changes

### The Refactoring Safety Net

Before any refactoring session:

```
Before we start refactoring:
1. Run the test suite and confirm it passes: `pnpm test`
2. Commit current state: `git add -A && git commit -m "chore: pre-refactor checkpoint"`
3. Create a branch: `git checkout -b refactor/[description]`
```

### Safe Refactoring Prompts

**Extract function:**
```
Extract the email validation logic from src/lib/users.ts (lines 34-67) into a separate
function `validateEmail` in src/lib/validation.ts. Update all imports. Run tests after.
```

**Rename across codebase:**
```
Rename the `getUserData` function to `fetchUserProfile` across the entire codebase.
This includes: function definition, all call sites, all imports, all test references.
Run `pnpm test` and `pnpm lint` after to verify nothing broke.
```

**Split large file:**
```
src/lib/api.ts is 800 lines. Split it into:
- src/lib/api/users.ts (user-related functions)
- src/lib/api/projects.ts (project-related functions)
- src/lib/api/shared.ts (shared types and helpers)
- src/lib/api/index.ts (re-exports for backward compatibility)

Preserve all existing exports from the index file so no external imports break.
Run tests after each file move.
```

### Multi-File Refactoring Rules

1. **One type of change at a time** — don't rename AND restructure AND optimize simultaneously.
2. **Run tests after each step** — catch breaks early, not after 20 files changed.
3. **Preserve exports** — use index.ts re-exports so consumers don't break.
4. **Commit incrementally** — one commit per logical change, not one giant commit.

---

## 7. Test-Driven Development With Claude Code

### The TDD Loop

```
Step 1: "Write a failing test for: creating a user with valid email stores them in the database"
Step 2: [verify test fails for the right reason]
Step 3: "Now write the minimum code to make this test pass"
Step 4: [verify test passes]
Step 5: "Refactor the implementation — the test must still pass"
```

### Why TDD Works Especially Well With Claude

- **Tests are acceptance criteria** — Claude knows exactly what "done" means.
- **Immediate verification** — no ambiguity about whether the code works.
- **Prevents gold-plating** — "minimum code to pass" stops Claude from over-engineering.
- **Regression safety** — future changes can't silently break working features.

### Test-First Prompts

```
Write tests for a `calculateShipping` function that:
- Free shipping for orders over $100
- $5.99 flat rate for orders $50-$100
- $9.99 flat rate for orders under $50
- International orders: add $15 surcharge
- Express: 2x the base rate
- Edge cases: $0 order, negative amount (throw), exactly $50, exactly $100

Use vitest. Don't implement the function yet — just the tests.
```

Then: "Now implement `calculateShipping` to pass all tests."

---

## 8. Git Workflow With Claude Code

### Pre-Work Checklist

```bash
git status          # Clean working tree?
git pull            # Up to date?
git checkout -b feat/[description]   # New branch
```

### Commit Strategy

| Scope | Commit Pattern |
|-------|---------------|
| Single function added | `feat: add calculateShipping function` |
| Bug fixed | `fix: handle null user in profile fetch` |
| Tests added | `test: add shipping calculation edge cases` |
| Refactor (no behavior change) | `refactor: extract validation into shared module` |
| Multiple related changes | Commit each logical unit separately |
| Large feature | Multiple commits on feature branch, squash on merge |

### Claude Code Git Prompts

```
# After completing work:
"Commit the changes with an appropriate conventional commit message. 
Group related files into logical commits if there are multiple concerns."

# For PR creation:
"Create a PR description for these changes. Include:
- What changed and why
- How to test it
- Any migration steps needed
- Screenshots if UI changed"
```

---

## 9. Code Review Mode — Claude as Reviewer

### Review Prompt Template

```
Review this code for:
1. Correctness — does it do what it claims?
2. Security — any injection, auth bypass, data leak risks?
3. Performance — N+1 queries, unnecessary re-renders, missing indexes?
4. Maintainability — clear naming, reasonable complexity, documented edge cases?
5. Testing — are the tests sufficient? Any missing cases?

Be specific. For each issue, cite the file:line and suggest a fix.
Skip style nits unless they affect readability.
```

### Self-Review Before PR

```
I'm about to open a PR. Review all changed files (`git diff main`) for:
- Any hardcoded secrets or credentials
- TODO/FIXME/HACK comments that should be resolved
- Console.logs that should be removed
- Missing error handling
- Type assertions (as any) that should be proper types
- Missing tests for new public functions
```

---

## 10. Production Shipping Checklist

Before deploying any Claude-generated code:

### P0 — Must Do

- [ ] All tests pass (`pnpm test && pnpm test:e2e`)
- [ ] Linting clean (`pnpm lint`)
- [ ] Type checking clean (`tsc --noEmit`)
- [ ] No hardcoded secrets in code (grep for API keys, tokens, passwords)
- [ ] Error handling exists for all external calls (DB, API, file I/O)
- [ ] Input validation on all user-facing endpoints
- [ ] Database migrations reviewed (no data loss, backward compatible)

### P1 — Should Do

- [ ] Performance: no N+1 queries, no unbounded lists, pagination exists
- [ ] Logging: structured logs at appropriate levels (not console.log)
- [ ] Auth: all new endpoints have proper authorization checks
- [ ] Rate limiting on public endpoints
- [ ] Rollback plan documented (how to revert if broken)

### P2 — Nice to Have

- [ ] Load test with expected traffic
- [ ] Monitoring alerts for new endpoints
- [ ] Documentation updated (API docs, README, CHANGELOG)
- [ ] Accessibility checked (if UI changes)

---

## 11. Anti-Patterns — What Kills Productivity

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| "Build me a full app" in one prompt | Context explosion, mediocre everything | Break into 5-10 focused tasks |
| Accepting code without reading it | Bugs compound, technical debt grows | Review every diff. Question anything unclear. |
| Re-prompting the same thing hoping for different results | Wastes tokens and context | Change your prompt. Add constraints. Try a different approach. |
| Ignoring test failures | "It mostly works" → production incidents | Fix tests immediately. Green before moving on. |
| Never using `/compact` | Context degrades, Claude gets confused | Compact every 30-45 minutes of active work |
| Pasting entire codebases | Context full of noise | Reference files by path. Let Claude read what it needs. |
| Using Claude for tasks you should think through | Outsourcing architecture decisions to AI | Discuss with Claude, but YOU decide. |
| Not committing between tasks | Can't revert, can't bisect | Commit after every working state |
| Prompting in vague language | "Make it better" → random changes | Specific inputs, specific outputs, specific constraints |
| Fighting Claude's suggestions | If Claude keeps suggesting something different, maybe it's right | Consider the suggestion. Explain why your way is better if you disagree. |

---

## 12. Speed Multipliers — Advanced Techniques

### Slash Commands Reference

| Command | When to Use |
|---------|------------|
| `/new` | New task, fresh context |
| `/compact` | Context getting heavy, mid-task |
| `/clear` | Nuclear option — wipe everything |
| `/cost` | Check token spend this session |
| `/model` | Switch models (Sonnet for speed, Opus for complexity) |
| `/vim` | Enter vim mode for file editing |

### Model Selection Strategy

| Task Type | Best Model | Why |
|-----------|-----------|-----|
| Simple bug fix | Sonnet | Fast, cheap, sufficient |
| New feature implementation | Sonnet | Good balance of speed + quality |
| Complex architecture | Opus | Deeper reasoning, better tradeoff analysis |
| Code review | Opus | Catches subtle issues |
| Refactoring | Sonnet | Mechanical changes, speed matters |
| Debugging race conditions | Opus | Needs to reason about state |

### Keyboard Shortcuts

- `Esc` → interrupt Claude (stop generation if going wrong direction)
- `Up arrow` → edit last prompt (fix typo without re-typing)
- `Tab` → accept file edit suggestion

### Session Stacking

For maximum throughput on a large feature:
1. Terminal 1: main implementation (Claude Code)
2. Terminal 2: tests for what Terminal 1 builds (Claude Code with `/new`)
3. Terminal 3: manual testing / running the app

---

## 13. Workflow Templates

### New Feature Workflow

```
1. "Create branch feat/[name]"
2. "Write failing tests for [feature spec]"
3. "Implement minimum code to pass tests"
4. "Refactor — tests must stay green"
5. "Run full test suite + lint + typecheck"
6. "Commit with conventional commit message"
7. "Self-review: check diff for security, performance, missing edge cases"
8. "Create PR with description"
```

### Bug Fix Workflow

```
1. "Create branch fix/[description]"
2. "Write a test that reproduces this bug: [paste error]"
3. "Fix the bug — test must pass"
4. "Run full test suite to check for regressions"
5. "Commit: fix: [description of what was wrong]"
```

### Refactoring Workflow

```
1. "Create branch refactor/[description]"
2. "Run tests — confirm all green"
3. "Commit pre-refactor state"
4. "[Specific refactoring instruction]"
5. "Run tests — must still be green"
6. "Commit this step"
7. [Repeat 4-6 for each refactoring step]
```

### Spike / Research Workflow

```
1. "Use Task tool to research [topic]. Return: key findings, API surface, gotchas, recommended approach."
2. [Read Task output]
3. "Based on the research, build a minimal proof of concept in /tmp/spike-[name]/"
4. [Evaluate POC]
5. "Spike looks good. Now implement properly in the main codebase."
```

---

## 14. Measuring Your Productivity

Track these weekly:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Features shipped | 3-5/week | Git commits tagged feat: |
| Bugs introduced | <1/week | Post-deploy incidents |
| Test coverage trend | ↑ or stable | Coverage reports |
| Token cost / feature | Decreasing | `/cost` per session |
| Time to first working code | <30 min | Stopwatch from task start |
| Context compacts per session | 1-2 | Count your `/compact` usage |

---

## Natural Language Commands

| Say This | Does This |
|----------|----------|
| "Set up my project for Claude Code" | Creates CLAUDE.md + .claueignore from your stack |
| "Review this code" | Runs 5-dimension review on changed files |
| "Help me debug [error]" | Walks through DEBUG protocol |
| "Refactor [file/module]" | Safe refactoring with test verification |
| "Write tests for [function]" | TDD-style test generation |
| "Ship this feature" | Runs production checklist |
| "Start a new task" | Clean context + branch setup |
| "How's my productivity?" | Reviews git log and suggests improvements |
| "Optimize my CLAUDE.md" | Reviews and improves your project config |
| "What model should I use for [task]?" | Model selection recommendation |
| "Help me with my PR" | PR description + self-review |
| "Estimate this task" | Breaks down into steps with time estimates |

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI-native business tools that ship.*
