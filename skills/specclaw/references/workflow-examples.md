# Workflow Examples

Real-world examples of using SpecClaw commands.

---

## Example 1: Adding Authentication to a Node.js API

### User says:
> specclaw propose "add JWT authentication with refresh tokens"

### Agent does:

```
1. Analyze codebase:
   - find . -maxdepth 3 | head -80
   - cat package.json
   - head -30 src/app.ts src/routes/*.ts

2. Create .specclaw/changes/add-jwt-auth/proposal.md

3. Present to user for review
```

### After approval, user says:
> specclaw plan add-jwt-auth

### Agent generates:

**spec.md** (excerpt):
```markdown
## Acceptance Criteria
- [ ] AC-1: GIVEN a valid username/password WHEN POST /auth/login THEN return JWT access token (15min) + refresh token (7d)
- [ ] AC-2: GIVEN an expired access token WHEN POST /auth/refresh with valid refresh token THEN return new access + refresh tokens
- [ ] AC-3: GIVEN an invalid token WHEN accessing protected route THEN return 401 with error message
```

**tasks.md** (excerpt):
```markdown
### Wave 1 — Core auth infrastructure
- [ ] `T1` — Create auth middleware
  - Files: src/middleware/auth.ts, src/types/auth.ts
  - Estimate: small
- [ ] `T2` — Add JWT utility functions
  - Files: src/utils/jwt.ts, src/config/auth.ts
  - Estimate: small

### Wave 2 — Routes and handlers
- [ ] `T3` — Create auth routes (login, refresh, logout)
  - Files: src/routes/auth.ts, src/controllers/auth.ts
  - Depends: T1, T2
  - Estimate: medium

### Wave 3 — Integration
- [ ] `T4` — Protect existing routes with auth middleware
  - Files: src/routes/users.ts, src/routes/posts.ts
  - Depends: T1
  - Estimate: small
- [ ] `T5` — Auth integration tests
  - Files: tests/auth.test.ts
  - Depends: T3
  - Estimate: medium
```

### User says:
> specclaw build add-jwt-auth

### Agent orchestrates:

```
Wave 1: Spawn 2 agents (T1 + T2 in parallel)
  → T1 agent: creates auth.ts middleware + types
  → T2 agent: creates jwt.ts utils + config
  → Both complete ✅

Wave 2: Spawn 1 agent (T3)
  → T3 agent: gets spec + design + existing middleware/utils as context
  → Creates auth routes + controllers
  → Complete ✅

Wave 3: Spawn 2 agents (T4 + T5 in parallel)
  → T4 agent: adds auth middleware to existing routes
  → T5 agent: writes integration tests
  → Both complete ✅

Post-build: npm test → all passing
```

---

## Example 2: Autonomous Mode (Cron)

### Setup:
```yaml
# .specclaw/config.yaml
automation:
  auto_mode: true
  cron: "0 2 * * *"  # 2 AM daily
  max_tasks_per_run: 5
```

### What happens at 2 AM:

```
1. Agent wakes up
2. Reads .specclaw/STATUS.md
3. Finds: "add-dark-mode" has approved plan, not yet built
4. Runs: specclaw build add-dark-mode
5. Spawns agents for wave 1...
6. Completes 5 tasks (hits max_tasks_per_run)
7. Updates status, sends Discord notification:
   "🦞 Nightly build: 5/8 tasks complete for add-dark-mode. Continuing tomorrow."
8. Next night: picks up remaining 3 tasks
9. Runs verification
10. Sends: "🦞 add-dark-mode complete and verified! Ready for review."
```

---

## Example 3: Multi-Model Routing

```yaml
models:
  planning: "anthropic/claude-opus-4-6"      # Best reasoning for specs
  coding: "openai/gpt-5.1-codex"             # Fast + cheap for implementation
  review: "anthropic/claude-sonnet-4-5"       # Good balance for verification
```

### How it flows:

```
specclaw propose → Opus drafts the proposal
specclaw plan    → Opus generates spec + design + tasks
specclaw build   → Codex implements each task (parallel, cheap)
specclaw verify  → Sonnet validates against spec
```

Cost optimization: Opus for thinking, Codex for typing, Sonnet for checking.

---

## Example 4: Discord Approval Flow

### Config:
```yaml
notifications:
  channel: "discord"
  target: "channel:1486698924512116736"  # #irp channel
  on_approval_needed: true
```

### Flow:
```
1. User: "specclaw propose add-search"
2. Agent creates proposal, sends to Discord:
   "🦞 New proposal: **add-search**
    [View Proposal] [Approve] [Reject]"
3. User clicks Approve in Discord
4. Agent auto-advances to planning
5. Sends plan summary to Discord for review
6. User approves → build starts
7. Progress updates stream to Discord channel
```
