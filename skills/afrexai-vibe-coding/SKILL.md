---
name: Vibe Coding Mastery
slug: afrexai-vibe-coding
version: 1.0.0
description: The complete operating system for building software with AI. From first prompt to production deployment — prompting frameworks, architecture patterns, testing strategies, debugging playbooks, and production graduation checklists. Works with Claude Code, Cursor, Windsurf, Copilot, and any AI coding tool.
metadata: {"openclaw":{"emoji":"🎸","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

# Vibe Coding Mastery

The complete system for building software with AI — from zero to production. Not tips. Not theory. A full operating methodology.

**What is vibe coding?** Programming where you describe what you want and let AI generate code. You evaluate by results, not by reading every line. Coined by Andrej Karpathy (Feb 2025).

**Key distinction (Simon Willison):** If you review, test, and explain the code — that's AI-assisted software development. Vibe coding means accepting AI output without fully understanding every function. This skill covers both modes and the spectrum between them.

---

## Phase 1: When to Vibe (Decision Matrix)

Before starting, classify your project:

| Factor | Vibe ✅ | Don't Vibe ❌ |
|--------|---------|---------------|
| **Stakes** | Low (prototype, internal, learning) | High (payments, auth, compliance) |
| **Timeline** | Hours to days | Months+ |
| **Team size** | Solo or pair | Large team with standards |
| **Domain knowledge** | You understand the domain | Unfamiliar territory |
| **Reversibility** | Easy to rewrite | Hard to change later |
| **Data sensitivity** | Public/test data | PII, financial, health |

**Scoring:** Count ✅ checks.
- 5-6: Full vibe mode. Ship fast.
- 3-4: Vibe with guardrails. Review critical paths.
- 1-2: AI-assisted development, not vibe coding. Review everything.
- 0: Write it yourself or hire someone who understands the domain.

### Vibe Coding Maturity Levels

| Level | Description | Who |
|-------|-------------|-----|
| **L1 — Passenger** | Copy-paste AI output, hope it works | Beginners |
| **L2 — Navigator** | Guide AI with context, catch obvious errors | Intermediate |
| **L3 — Pilot** | Architecture decisions, AI implements, you review | Experienced devs |
| **L4 — Conductor** | Orchestrate multiple AI sessions, parallel streams | Power users |

**Target: L3 minimum for anything going to production.**

---

## Phase 2: Tool Selection

### Primary Tools Matrix

| Tool | Best For | Context Window | Multi-file | Terminal | Cost |
|------|----------|---------------|------------|----------|------|
| **Claude Code** | Full-stack, complex refactors, CLI | 200K | Excellent | Native | API usage |
| **Cursor** | Editor-integrated, rapid iteration | 128K | Good | Via terminal | $20/mo + API |
| **Windsurf** | Beginner-friendly, guided flows | 128K | Good | Limited | $10/mo + API |
| **GitHub Copilot** | Inline completions, small edits | 8-32K | Limited | No | $10-19/mo |
| **Aider** | Git-aware, open source, CLI | Varies | Good | Native | API only |
| **Cline (VS Code)** | VS Code native, plan mode | Varies | Good | Via terminal | API only |

### Multi-Tool Strategy

Use tools in combination:
1. **Architecture & planning** → Claude Code or Claude chat (largest context, best reasoning)
2. **Implementation** → Cursor or Claude Code (fast iteration, multi-file edits)
3. **Quick fixes & completions** → Copilot (inline, zero friction)
4. **Code review** → Claude chat (paste diffs, get thorough review)

---

## Phase 3: Rules Files (Your Persistent Context)

Rules files teach AI your conventions once. Without them, every session starts from zero.

### Universal Rules File Template

```markdown
# Project Rules

## Stack
- Language: [TypeScript/Python/Go/etc.]
- Framework: [Next.js/FastAPI/etc.]
- Database: [PostgreSQL/SQLite/etc.]
- Styling: [Tailwind/CSS Modules/etc.]
- Package manager: [pnpm/npm/poetry/etc.]

## Code Style
- Max function length: 50 lines
- Max file length: 300 lines
- One export per file (prefer)
- Use [const/let, never var] / [type hints always]
- Error handling: [explicit try/catch, never swallow errors]
- Naming: [camelCase functions, PascalCase components, UPPER_SNAKE constants]

## Architecture
- File structure: [describe or reference]
- API pattern: [REST/tRPC/GraphQL]
- State management: [Zustand/Redux/signals/etc.]
- Auth pattern: [JWT/session/OAuth provider]

## Testing
- Framework: [Vitest/Jest/Pytest/etc.]
- Minimum coverage: [80%/90%/etc.]
- Test file location: [co-located/__tests__/tests/]
- Run before committing: [command]

## Do NOT
- Do not use `any` type in TypeScript
- Do not install new dependencies without asking
- Do not modify database schema without migration
- Do not hardcode secrets, URLs, or config values
- Do not remove existing tests

## When Unsure
- Ask before making architectural decisions
- Show the plan before implementing changes >100 lines
- Flag security-adjacent code for manual review
```

### Where to Put It

| Tool | File | Notes |
|------|------|-------|
| Claude Code | `CLAUDE.md` in repo root | Also reads .claude/ directory |
| Cursor | `.cursor/rules/*.mdc` | Supports conditional rules with globs |
| Windsurf | `.windsurfrules` in repo root | Single file |
| Aider | `.aider.conf.yml` + conventions in chat | YAML config + initial prompt |
| Generic | `AGENTS.md` or `CONVENTIONS.md` | Any tool can be told to read it |

### Cursor Conditional Rules (.mdc)

```markdown
---
description: React component standards
globs: src/components/**/*.tsx
alwaysApply: false
---

# Component Rules
- Functional components only (no class components)
- Props interface above component, named [Component]Props
- Use forwardRef for components that accept ref
- Co-locate styles in [component].module.css
- Co-locate tests in [component].test.tsx
- Export component as named export, not default
```

### Rules File Quality Checklist

- [ ] Stack and versions specified
- [ ] File/function size limits defined
- [ ] Naming conventions documented
- [ ] "Do NOT" section with common AI mistakes
- [ ] Testing expectations clear
- [ ] Architecture patterns described or referenced
- [ ] Security-sensitive areas flagged
- [ ] Dependencies policy stated

---

## Phase 4: Prompt Engineering for Code

### The 5-Level Prompt Quality Hierarchy

**Level 1 — Wish (bad)**
> "Build a todo app"

**Level 2 — Request (okay)**
> "Build a todo app with React and Tailwind"

**Level 3 — Specification (good)**
> "Build a todo app: React 18, TypeScript, Tailwind. Features: add/edit/delete/toggle todos. Store in localStorage. Responsive. Under 200 lines total."

**Level 4 — Brief (great)**
> "Build a todo app. Here's the spec:
> - Stack: React 18 + TS + Tailwind + Vite
> - Features: CRUD todos, toggle complete, filter (all/active/done), persist to localStorage
> - Constraints: Single component file, under 200 lines, no external deps beyond stack
> - Done when: All features work, page refresh preserves state, mobile responsive
> - Start with the data types, then build up."

**Level 5 — Contract (production-grade)**
```yaml
task: Todo application
stack:
  runtime: React 18 + TypeScript strict
  styling: Tailwind CSS 3.x
  build: Vite 5
  test: Vitest + Testing Library
features:
  - CRUD operations on todos
  - Toggle completion status
  - Filter: all | active | completed
  - Bulk actions: complete all, clear completed
  - Persist to localStorage with versioned schema
constraints:
  - Max 3 component files
  - Max 200 lines per file
  - No external state management library
  - Keyboard accessible (tab, enter, escape)
  - Mobile responsive (min 320px)
acceptance:
  - All features functional
  - Page refresh preserves state
  - 90%+ test coverage
  - No TypeScript errors (strict mode)
  - Lighthouse accessibility score > 90
approach: Start with types/interfaces, then hooks, then components, then tests.
```

### 12 Proven Prompt Patterns

1. **Scaffolding**: "Create the project structure with empty files and type definitions. Don't implement yet."
2. **Incremental**: "Implement only [specific function]. Don't touch other files."
3. **Explain-then-build**: "Explain how you'd architect this, then implement after I approve."
4. **Test-first**: "Write the tests first based on these requirements. Then implement to make them pass."
5. **Refactor**: "Refactor [file] to [goal]. Keep the same behavior. Don't add features."
6. **Debug**: [paste error] "This happens when [action]. Expected [behavior]. The relevant code is in [files]."
7. **Review**: "Review this code for [security/performance/readability]. Be specific about issues and fixes."
8. **Migrate**: "Convert this from [old pattern] to [new pattern]. Show me the plan first."
9. **Document**: "Add JSDoc/docstrings to all public functions in [file]. Include param types and examples."
10. **Optimize**: "This function is slow with >10K items. Profile, identify bottleneck, optimize. Keep same API."
11. **Parallel session**: "Read [these files] and summarize the architecture. Don't change anything."
12. **Recovery**: "The codebase is in a broken state. [describe symptoms]. Help me understand what went wrong before we fix it."

### Anti-Patterns (What NOT to Prompt)

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| "Build me an app" | Too vague, AI guesses everything | Use Level 4+ prompts |
| "Fix it" (no context) | AI doesn't know what "it" is | Paste error + expected behavior |
| "Rewrite everything" | Nukes working code, introduces regressions | Incremental refactors |
| "Make it better" | Subjective, AI changes random things | Specify what "better" means |
| "Use best practices" | AI's "best practices" may not match your stack | Specify the practices you want |
| Multiple unrelated asks | Context bleed, partial implementations | One task per prompt |
| Long conversation chains | Context degrades after 10+ turns | Start fresh sessions |

---

## Phase 5: The RPIV Workflow

**Research → Plan → Implement → Validate**

### Step 1: Research
> "Read [files/docs/codebase]. Explain how [feature/module] works. Don't modify anything."

Purpose: Load context. Catch misunderstandings before they cascade. AI explains back to you — if the explanation is wrong, the implementation will be wrong too.

### Step 2: Plan
> "Based on your understanding, write a plan:
> 1. Which files you'll create/modify
> 2. What changes in each file
> 3. What order you'll implement
> 4. What could go wrong"

Purpose: Review the approach before committing to it. 10x cheaper to fix a plan than debug cascading implementation errors.

**Plan Review Checklist:**
- [ ] Does it touch files it shouldn't?
- [ ] Is the change order logical (types → utils → components → tests)?
- [ ] Are there missing files or steps?
- [ ] Does it respect existing patterns?
- [ ] Did it flag risks/unknowns?

### Step 3: Implement
> "Proceed with the plan. Implement step by step. Stop after each file for me to verify."

**The 200-Line Rule:** If any single implementation step is >200 lines of changes, break it down further. Large changes = large bugs.

**Checkpoint System:**
- After each file: quick scan for obvious issues
- After each feature: run tests
- After each milestone: manual test + commit

### Step 4: Validate
> "Run the tests. Show me the output. If anything fails, explain why and fix it."

Then manually verify:
- [ ] Feature works as specified
- [ ] Edge cases handled (empty state, max length, special chars)
- [ ] No console errors
- [ ] Mobile responsive (if UI)
- [ ] Existing features still work (regression check)

---

## Phase 6: Architecture for Vibe Coding

AI generates better code when your architecture is clear and consistent.

### Recommended Project Structure

```
project/
├── CLAUDE.md (or .cursorrules)     # AI rules
├── README.md                        # What this is
├── src/
│   ├── types/                       # Shared types (AI reads these first)
│   │   ├── index.ts
│   │   └── [domain].ts
│   ├── lib/                         # Pure utilities (no side effects)
│   │   ├── [utility].ts
│   │   └── [utility].test.ts
│   ├── services/                    # External integrations (DB, API, etc.)
│   │   ├── [service].ts
│   │   └── [service].test.ts
│   ├── components/ (or routes/)     # UI or route handlers
│   │   ├── [Component]/
│   │   │   ├── index.tsx
│   │   │   ├── [Component].test.tsx
│   │   │   └── [Component].module.css
│   └── app/                         # App entry, layout, config
├── tests/                           # Integration/E2E tests
├── scripts/                         # Build/deploy/utility scripts
└── docs/                            # Architecture decisions, API docs
```

### Vibe-Friendly Patterns

1. **Types first.** Define your data shapes before anything else. AI uses these as contracts.
2. **Small files.** 300 lines max. AI handles small files better — fewer hallucinations, cleaner diffs.
3. **Explicit imports.** No barrel exports (index.ts re-exports). AI gets confused by indirect imports.
4. **Co-located tests.** `thing.ts` + `thing.test.ts` side by side. AI writes tests when they're right there.
5. **Config in one place.** Environment, feature flags, constants — one file AI can reference.
6. **Database schema as code.** Drizzle/Prisma schema file = single source of truth AI can read.

### Schema-First Design

```typescript
// src/types/todo.ts — AI reads this and understands your domain
export interface Todo {
  id: string;          // UUID v4
  title: string;       // 1-200 chars, trimmed
  completed: boolean;  // default false
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateTodoInput {
  title: string;       // Required, 1-200 chars
}

export interface UpdateTodoInput {
  title?: string;
  completed?: boolean;
}

// This is ALL AI needs to implement CRUD operations correctly.
```

---

## Phase 7: Testing in Vibe Mode

### The Vibe Testing Pyramid

```
         /  E2E  \        ← 10% (critical user flows only)
        / Integration \    ← 30% (API endpoints, DB queries)
       /    Unit Tests  \  ← 60% (pure functions, utils, logic)
```

### Test-First Vibe Pattern

```
Prompt: "Write tests for a function that validates email addresses.
Requirements:
- Returns true for valid emails
- Returns false for empty string, missing @, missing domain
- Handles edge cases: plus addressing, subdomains, international domains
Write ONLY the tests. I'll implement after."
```

Then: "Now implement the function to make all tests pass."

This pattern produces better code because AI has clear acceptance criteria.

### What to Test (Minimum Viable Testing)

| Category | Test? | Why |
|----------|-------|-----|
| Pure functions | Always | Easy, high value, catches logic bugs |
| Data transformations | Always | Wrong transforms corrupt data silently |
| API endpoints | Always | Contract verification |
| UI components | Sometimes | Test behavior, not implementation |
| Database queries | Sometimes | Test complex queries, skip simple CRUD |
| Config/env loading | Rarely | Test once, trust after |
| Third-party wrappers | Rarely | Test integration, not their code |

### When AI Tests Are Wrong

Signs of bad AI tests:
- Tests that test the implementation, not the behavior
- Tests that pass with any input (always return true)
- Tests that mock everything (testing mocks, not code)
- Snapshot tests for everything (brittle, meaningless)

Fix: "These tests mock too much. Write tests that exercise real behavior. Only mock external services (DB, API calls). Use in-memory alternatives where possible."

---

## Phase 8: Debugging with AI

### The Error Paste Pattern

**What Karpathy does:** Copy error, paste with no comment, AI usually fixes it.

**When it works:** Clear error messages, stack traces, type errors, syntax errors.

**When it doesn't (and what to do instead):**

| Situation | Better Prompt |
|-----------|--------------|
| Vague runtime error | "When I [action], [behavior] happens. Expected [expected]. Here's the relevant code: [paste]" |
| Silent failure | "This function returns [wrong result] for input [input]. Expected [expected]. Walk me through the logic step by step." |
| Intermittent bug | "This works sometimes but fails with [condition]. I think it's a [race condition/state issue/timing problem]. Here's the code:" |
| Build/config error | Paste full error + your config files. "Don't guess — check the config values against the docs." |
| AI broke something while fixing | "Stop. Let's go back. The original issue was [X]. You introduced a new bug: [Y]. Let's fix the original issue without changing [Z]." |

### The 3-Strike Rule

If AI can't fix something in 3 attempts:
1. **Stop.** Don't keep asking the same thing.
2. **Reframe.** Describe the behavior you want, not the error.
3. **Simplify.** Create a minimal reproduction case.
4. **Start fresh.** New session, clean context.
5. **Manual.** Sometimes you need to read the code yourself.

### Recovery Playbooks

**Spaghetti Code (AI made a mess)**
```
1. git stash (save current mess)
2. git checkout [last good commit]
3. Start a NEW AI session
4. Paste only the requirements, not the broken code
5. "Implement this from scratch following these patterns: [your conventions]"
```

**Recurring Bug (Fix breaks something else)**
```
1. Write a failing test for the bug
2. Write regression tests for the things that keep breaking
3. "Make ALL these tests pass. Don't modify the tests."
```

**Dependency Hell**
```
1. Check `package.json` / `requirements.txt` — AI sometimes adds conflicting deps
2. "List all dependencies you added and why each is needed"
3. Remove anything that duplicates existing functionality
4. Lock versions: "Pin all dependencies to exact versions"
```

**Context Exhaustion (AI forgot earlier instructions)**
```
1. Start a new session
2. Load rules file + key files
3. Summarize what's done and what remains
4. Continue with fresh context
```

---

## Phase 9: Production Graduation Checklist

Before ANY vibe-coded project goes to production:

### P0 — Security (Must fix)
- [ ] No hardcoded secrets (grep for API keys, passwords, tokens)
- [ ] Input validation on all user inputs (XSS, SQL injection, path traversal)
- [ ] Authentication checks on protected routes
- [ ] Authorization: users can only access their own data
- [ ] HTTPS enforced
- [ ] Dependencies: `npm audit` / `pip audit` — zero critical/high
- [ ] Rate limiting on public endpoints
- [ ] CORS configured (not `*` in production)
- [ ] Error messages don't leak internals (no stack traces to users)

### P1 — Performance (Should fix)
- [ ] Database queries have indexes for common filters
- [ ] No N+1 queries (check ORM query logs)
- [ ] Images optimized (WebP, lazy load)
- [ ] Bundle size reasonable (<200KB initial JS)
- [ ] Loading states for async operations
- [ ] Pagination for list endpoints (no unbounded queries)

### P2 — Reliability (Should fix)
- [ ] Error handling: try/catch on all async operations
- [ ] Graceful degradation when services are down
- [ ] Health check endpoint
- [ ] Logging (structured, not console.log)
- [ ] Environment config via env vars (not hardcoded)
- [ ] Database migrations (not raw SQL)
- [ ] Backup strategy for data

### P3 — Quality (Nice to have)
- [ ] Test coverage >80%
- [ ] TypeScript strict mode / type hints everywhere
- [ ] Linter configured and clean
- [ ] README with setup instructions
- [ ] CI pipeline runs tests on push

**AI-Assisted Hardening Prompt:**
> "Review this codebase for production readiness. Check against this list: [paste checklist]. For each item, tell me: pass/fail/not applicable, and what to fix if fail. Be specific — file names and line numbers."

---

## Phase 10: Advanced Patterns

### Parallel AI Sessions

Run multiple AI sessions simultaneously:
- **Session A**: Implementing backend API
- **Session B**: Building frontend components
- **Session C**: Writing tests

**Rules for parallel sessions:**
- Define interfaces/types FIRST (shared contract)
- Each session gets its own rules file section
- Merge via git (commit each session's work to a branch)
- Integration test after merging

### Pair Programming Patterns

**Navigator-Driver (you navigate, AI drives)**
> You: "We need to add pagination. The API should accept page and limit query params. Return items, total count, and hasNextPage."
> AI: [implements]
> You: "Good. Now add cursor-based pagination as an alternative. The cursor should be the last item's ID."
> AI: [implements]

**Ping-Pong (alternate implementing)**
> You: Write the test
> AI: Write the implementation
> You: Write the next test
> AI: Write the next implementation
> (TDD style — extremely effective)

**Rubber Duck (AI explains, you catch issues)**
> "Walk me through this code line by line. Explain what each function does, what could go wrong, and what assumptions you're making."
> (AI explains → you catch bad assumptions before they become bugs)

### Context Window Management

| Strategy | When | How |
|----------|------|-----|
| **Fresh start** | Every 15-20 turns | New session, reload rules + key files |
| **Summarize** | Before complex task | "Summarize what we've done. Then let's tackle [next thing]." |
| **File focus** | Large codebase | "Only look at src/services/auth.ts. Ignore everything else." |
| **Memory file** | Multi-session project | Keep PROGRESS.md with what's done/remaining |

### Git Workflow for Vibe Coding

```bash
# Before starting
git checkout -b feature/[name]
git status  # clean working tree

# During (commit often!)
git add -A && git commit -m "feat: [what AI just implemented]"
# Every 2-3 AI turns, commit. Your safety net.

# If things go wrong
git diff  # see what AI changed
git stash  # save mess
git checkout .  # nuclear option: discard all changes

# When done
git diff main..HEAD  # review ALL changes before merging
```

---

## Phase 11: Common Mistakes & How to Avoid Them

| # | Mistake | Consequence | Prevention |
|---|---------|-------------|------------|
| 1 | No rules file | AI reinvents conventions each session | Write rules file before first prompt |
| 2 | Prompting implementation before plan | Cascading wrong assumptions | Always: Research → Plan → Implement |
| 3 | Never reading AI's code | Hidden bugs, security holes, debt | Review at least critical paths |
| 4 | One giant prompt | AI loses focus, partial implementation | One task per prompt, sequential |
| 5 | Not committing frequently | Can't rollback when AI breaks things | Commit every 2-3 turns |
| 6 | Ignoring test failures | "It works on my machine" | Tests pass = done. Not before. |
| 7 | Letting AI add dependencies freely | Bloated bundle, version conflicts | "Don't add deps without asking" in rules |
| 8 | No production checklist | Ship security holes | Phase 9 checklist before deploy |
| 9 | Marathon AI sessions | Context degrades, AI "forgets" | Fresh session every 15-20 turns |
| 10 | Vibe coding auth/payments | Critical bugs in critical paths | Manual review for all security code |
| 11 | No types/schema | AI guesses data shapes differently each time | Define types FIRST, always |
| 12 | Trusting AI's "it works" | AI confidently ships broken code | Verify yourself. Run it. Test it. |
| 13 | Same prompt after 3 failures | AI stuck in a loop | Reframe, simplify, or do it manually |
| 14 | Mixing concerns in one session | Context pollution | One feature per session |
| 15 | No architecture guidance | AI creates inconsistent patterns | Document patterns in rules file |

---

## Phase 12: Weekly Effectiveness Tracking

Track your vibe coding quality over time:

```yaml
week_of: "YYYY-MM-DD"
sessions: [count]
features_shipped: [count]
bugs_introduced: [count]  # found post-ship
bugs_caught_in_review: [count]  # caught before ship
avg_prompts_per_feature: [count]
time_saved_estimate_hours: [number]
fresh_session_restarts: [count]

# Score yourself (1-5):
prompt_quality: [1-5]      # Are you using Level 4+ prompts?
review_discipline: [1-5]   # Are you reviewing critical code?
testing_rigor: [1-5]       # Are you testing before shipping?
architecture: [1-5]        # Is the codebase staying clean?
commit_frequency: [1-5]    # Are you committing every 2-3 turns?

total_score: [5-25]
```

| Score | Rating | Action |
|-------|--------|--------|
| 20-25 | Elite | You're a vibe coding conductor. Teach others. |
| 15-19 | Solid | Good habits. Focus on weakest dimension. |
| 10-14 | Learning | Review this guide weekly. Build the habits. |
| 5-9 | Risky | Slow down. More planning, more testing, more review. |

---

## The 10 Commandments of Vibe Coding

1. **Types first.** Define your data before writing logic.
2. **Rules file always.** No rules = no consistency.
3. **Plan before implement.** 5 minutes planning saves 5 hours debugging.
4. **One task per prompt.** Focus = quality.
5. **Commit after every win.** Git is your safety net.
6. **Test the critical path.** At minimum: happy path + one edge case.
7. **Fresh sessions.** Don't let context rot.
8. **Review security code.** Auth, payments, data access — always manual review.
9. **200-line rule.** If a change is bigger, break it down.
10. **Know when to stop vibing.** If AI can't fix it in 3 tries, change approach.

---

## Quick Reference Commands

```
"Read [files] and explain the architecture. Don't change anything."
"Write a plan for [feature]. List files to create/modify and changes in each."
"Implement only [specific thing]. Don't touch other files."
"Write tests first for [requirements]. Then implement to pass them."
"Review this for [security/performance/readability]. Be specific."
"This error occurs when [action]. Expected [behavior]. Here's the code: [paste]"
"Refactor [file] to [goal]. Same behavior. Don't add features."
"What dependencies did you add and why? Remove anything unnecessary."
"Walk me through this code. Explain assumptions and potential issues."
"Stop. The original issue was [X]. Let's start fresh with a minimal approach."
"Run all tests. If any fail, fix them without breaking other tests."
"Check this against the production checklist: [paste P0-P3 items]."
```

---

*Built by AfrexAI — the team that ships AI agents, not just AI prompts.*
