---
name: bug-fixing-openclaw
description: |
  Zero-regression bug fix workflow: triage → reproduce → root cause →
  impact analysis → fix → verify → knowledge deposit → self-reflect.

  Use when:
  - Feature broken, incorrect behavior, wrong output, errors/exceptions
  - Console errors/warnings even when feature appears functional
  - Regressions, timeouts, degraded performance
  - Keywords: "fix bug", "debug", "not working", "error", "broken"

  Output: Bug summary + verification report + code review + self-reflection score.
  Not for: new features (use fullstack-developer); pure review (use code-review);
  optimization (use performance-optimization).
allowed-tools: [read, write, execute, grep, glob]
metadata:
  language: en
  version: 4.0.0
  last_updated: 2026-03-06
  platform: openclaw
  enhancement:
    - v4.0 Iron Rules 20→12 (attention-dilution fix, aligned with bug-fixing v4.0)
    - v4.0 Rule 8 NEW — UI bugs require runtime evidence before fix
    - v4.0 Rule 10 NEW — Classify problem layer before fixing
    - v4.0 Phase 0 adds P0-P3 severity + auto-initializes knowledge files
    - v4.0 Severity-adaptive workflow depth (P0=full, P3=quick)
    - v4.0 Domain-Specific Checks consolidated table
    - v4.0 Kept OpenClaw project context, hot zones, Windows gotchas
---

# Bug Fix v4.0 — OpenClaw Edition (Zero-Regression + Portable)

**Core Promise**: Fix completely. Fix everywhere. Break nothing. Learn from every fix.

---

## Iron Rules (12 — NEVER Violate)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Rule 1:  Root cause MUST pass 4 gates before fixing                     │
│           (reproducible + causal + reversible + mechanistic)              │
│                                                                          │
│  Rule 2:  Scope MUST pass 5 gates before fixing                          │
│           (consumers + contracts + invariants + call sites + dup scan)    │
│                                                                          │
│  Rule 3:  MUST trace IMPACT CHAIN (code → data → time → event)          │
│           + scan ALL files for same pattern before writing fix            │
│                                                                          │
│  Rule 4:  MUST predict side effects + check blind spots before coding    │
│           (references/blind-spots.md is single source of truth)           │
│                                                                          │
│  Rule 5:  After fix, MUST run regression verification                    │
│           (functional + performance + concurrency + all impact levels)    │
│                                                                          │
│  Rule 6:  MUST verify fix is LOADED at runtime                           │
│           (clear __pycache__ + restart + exercise code path)              │
│                                                                          │
│  Rule 7:  Framework behavior → read source code first, never trust       │
│           docs/comments/assumptions alone                                │
│                                                                          │
│  Rule 8:  UI bugs MUST gather RUNTIME EVIDENCE before proposing fixes    │
│           (screenshot + DevTools DOM/console + user repro steps)          │
│           Do NOT fix UI bugs based on code reading alone.                │
│                                                                          │
│  Rule 9:  Fix is NOT done until: Bug Summary output + code-review        │
│           passes + knowledge files updated + self-reflection complete     │
│                                                                          │
│  Rule 10: Before fixing, CLASSIFY the problem layer:                     │
│           code bug? missing config? wrong architecture? AI capability?   │
│           Fix at the root layer, not at the symptom layer.               │
│                                                                          │
│  Rule 11: Pattern matching (regex, string match, name lookup) MUST       │
│           check boundary conditions (word boundaries / anchors / exact)   │
│                                                                          │
│  Rule 12: Before fix, MUST search bug pattern library + bug records      │
│           for known fixes and historical context                         │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow Overview

```
Phase 0: Triage → Severity (P0-P3) + Tier (Trivial/Standard/Complex)
  │
  ├─ Trivial → Quick Fix → test → done
  │
  ├─ Standard ─┐
  └─ Complex ──┘
      │
Phase 1: Reproduce (evidence required)
      │
Phase 2: Root Cause Analysis
    2A: Hypothesis ladder → 5 Whys → evidence
    2B: Search knowledge files (bug-patterns + bug-records)
    2C: Impact chain (code + data + time + event)
    2D: Similar issue scan across codebase
      │
Phase 3: Scope + Prediction
    3A: Consumer list → contracts → invariants → dup scan (5 gates)
    3B: Side effect prediction + blind spot check
    3C: Fix strategy comparison (when >10 LOC, Complex only)
      │
Phase 4: Fix (minimal change, prefer ≤50 LOC)
      │
Phase 5: Verify + Review
    5A: Regression verification (functional + perf + concurrency)
    5B: Runtime deployment verification
    5C: Bug Summary + code-review skill
      │
Phase 6: Knowledge Deposit + Self-Reflection
```

---

## Phase 0: Triage + Severity

> Classify severity AND tier FIRST to control workflow depth.

### Severity Classification (controls workflow depth)

| Severity | Criteria | Workflow | Time-box |
|----------|----------|----------|----------|
| **P0 Critical** | Production down / data loss / security | FULL (all phases) | 4h escalation |
| **P1 High** | Core feature broken / data corruption | FULL (all phases) | 8h escalation |
| **P2 Medium** | Non-core feature / UI issue | STANDARD (skip 3C) | 16h |
| **P3 Low** | Cosmetic / minor edge case | QUICK (skip 2C, 2D, 3A-3C) | No limit |

### Tier Classification (controls fix path)

| Tier | Criteria | Path |
|------|----------|------|
| **Trivial** | Typo, config value, 1-line obvious fix, no behavioral change | Quick Fix (below) |
| **Standard** | Logic bug, 1-3 files, clear symptom, no cross-module risk | Standard Path (skip phases marked "Complex only") |
| **Complex** | Cross-module, >3 files, shared utility, schema change, multi-process | Full Path (all phases mandatory) |

### Quick Fix Path (Trivial only)

```markdown
## Quick Fix
- Bug: [one-line description]
- Fix: [one-line change]
- File: [path:line]
- Test: [how verified — lint/test/manual]
- Risk: None (isolated, no behavioral change)
```

After quick fix: update `references/bug-records.md`, done. No RCA, no impact chain, no self-reflection needed.

**If "trivial" fix touches >1 file or changes behavior → upgrade to Standard.**

### Auto-Initialize Knowledge Files

```
Check: references/bug-patterns.md exists?
  YES → search it in Phase 2B
  NO  → skip pattern search; create after first fix

Check: references/bug-records.md exists?
  YES → search it in Phase 2B
  NO  → skip records search; create after first fix

Check: references/blind-spots.md exists?
  YES → use it in Phase 3B
  NO  → skip blind spot check; create after first fix
```

---

## Phase 1: Reproduce

> MUST have evidence before continuing. No evidence = no fix.

| Bug Type | Evidence Required |
|----------|------------------|
| Backend error | Stack trace + request/response |
| Frontend UI | Screenshot + browser console + user repro steps (Rule 8) |
| Performance | Before/after metrics + profiler output |
| Intermittent | Timing conditions + frequency estimate |

**UI Bug Protocol (Rule 8):**
1. Get user screenshot or screen recording
2. Open browser DevTools → check Console for errors/warnings
3. Inspect DOM structure (check for overflow clipping, z-index, Portal needs)
4. Reproduce the exact user steps
5. ONLY THEN form hypotheses

### Evidence Bundle Template

```markdown
### Trigger Conditions
- Input/params: [...]
- Environment: [OS/browser/runtime version]
- Timing: [action sequence or time interval]

### Observable Output
- Error message: [full error text]
- Logs: [key log lines]
- Screenshot/recording: [if available]

### Correlation IDs
- requestId/traceId: [...]
- sessionId: [...]
```

---

## Phase 2: Root Cause Analysis

### 2A: Hypothesis Ladder

| # | Hypothesis | Likelihood | Confirmation Test | Rejection Test | Status |
|---|-----------|-----------|-------------------|----------------|--------|
| 1 | [description] | High/Med/Low | [prove it IS this] | [prove it is NOT this] | [ ] |

**Rules**: Sort by likelihood → each must be falsifiable → run rejection tests first → test ONE at a time → use 5 Whys to reach root cause.

### Root Cause Confirmation Gate (Rule 1)

Root cause is confirmed only when ALL 4 conditions are met:

| Gate | Meaning |
|------|---------|
| **Reproducible** | Can trigger symptom in controlled scenario |
| **Causal** | Minimal change makes bug disappear |
| **Reversible** | Reverting the change makes bug reappear |
| **Mechanistic** | Can point to exact code path / state transition |

### Framework Assumption Audit (Rule 7)

When fix involves framework/library behavior: list assumptions → read source code to verify → document in comments with source references.

### 2B: Search Knowledge Files (Rule 12)

> Search bug-patterns.md and bug-records.md for matching patterns.
> Skip if files don't exist (see Phase 0 auto-init).

| Match Level | Action |
|-------------|--------|
| High (symptom + root cause match) | Apply known fix, can skip remaining RCA |
| Medium (similar symptom) | Reference strategy, verify |
| No match | Full investigation, must deposit after fix |

### 2C: Impact Chain (Rule 3)

| Dimension | What to Check |
|-----------|---------------|
| **Code** | Bug file → direct callers → indirect callers → deep callers |
| **Data** | Corrupted records in DB/file/cache? Repair script needed? |
| **Time** | When introduced? Duration of exposure? Users affected? |
| **Event** | Message queues, WebSocket, background workers affected? |

### 2D: Similar Issue Scan (Rule 3)

> Scan ALL files for the same bug pattern, not just the reported file.

```bash
rg -n "function_name\|similar_pattern" --glob "*.{ts,tsx,py,js}"
```

---

## Phase 3: Scope + Prediction

### Scope Accuracy Gate (Rule 2)

| # | Gate | Meaning |
|---|------|---------|
| 1 | **Consumer List** | All consumers (callers/dependents) enumerated |
| 2 | **Contract List** | Modified contracts/interfaces/behaviors listed |
| 3 | **Invariant Check** | Must-hold invariants listed |
| 4 | **Call Site Enum** | All call sites enumerated and classified |
| 5 | **Duplicate Scan** | No parallel implementation left unfixed |

### 3A: Side Effect Prediction (Rule 4)

1. **Change Blueprint** — What exactly will change
2. **Impact Ripple** — L0 (code) → L1 (module) → L2 (feature) → L3 (system) → L4 (user)
3. **Blind Spot Check** — Read `references/blind-spots.md` and execute every active check
4. **Go/No-Go Decision**

**Quick version** (for Standard-tier, ≤5 LOC, 1 file):
```markdown
## Quick Impact Check
- Change: [one-line description]
- Direct callers: [list or "none - local function"]
- Duplicates: [checked — none / found and planned]
- Could break: [prediction or "low risk - isolated"]
- Decision: GO
```

### 3B: Fix Strategy Comparison (>10 LOC, Complex only)

| Dimension | Strategy A | Strategy B |
|-----------|-----------|-----------|
| LOC change | | |
| Impact scope | | |
| Regression risk | | |
| Rollback-able | | |

---

## Phase 4: Fix

- Minimal change, prefer ≤50 LOC; justify if more
- ONE change at a time, never batch unrelated fixes
- **Layer Rule (Rule 10)**: Before writing fix code, verify you're fixing the right layer:

| Problem in… | Fix… | Do NOT fix… |
|-------------|------|-------------|
| Params/config | Config or param passing | Business logic |
| Single component | That component | Framework |
| Multiple components same issue | Framework/base class | Each component one by one |
| Docs vs code mismatch | Both sides in sync | Only one side |

- **Pattern matching safety (Rule 11)**: regex, string match, name lookup → always consider boundary conditions
- **DB schema change?** Generate Alembic migration:
  ```bash
  cd backend && alembic revision --autogenerate -m "describe change"
  ```

---

## Phase 5: Verify + Review

### 5A: Regression Verification (Rule 5)

| Category | Checks |
|----------|--------|
| **Functional** | Unit tests + integration + API + E2E + manual |
| **Performance** | No N+1 queries, no resource leaks, no response time increase |
| **Concurrency** | Thread-safe shared state, atomic operations, no race conditions |

Test the entire impact chain (L0-L3), not just the original bug.

### 5B: Runtime Deployment Verification (Rule 6)

| Step | Action | Evidence |
|------|--------|----------|
| 1 | Clear Python bytecode cache | `__pycache__` removed |
| 2 | Restart backend service | PID changed from X to Y |
| 3 | Health check passes | `/docs` returns 200 |
| 4 | Exercise the fixed code path | Request triggers fixed logic |

**If NOT deployed → restart and re-verify before proceeding.**

### 5C: Bug Summary + Code Review (Rule 9)

```markdown
## Bug Summary [BUG-XXX]
- **Symptom**: [one-sentence user-visible problem]
- **Root Cause**: [one-sentence actual cause]
- **Fix**: [one-sentence fix description]
- **Files Modified**: [file1.py, file2.ts]
- **Severity**: P0/P1/P2
```

Output Bug Summary → run `code-review` skill → if review finds issues → fix → re-verify

**Stop condition**: Code review clean + regression passed + deployment verified + original bug fixed.

### Special Checks

| Bug Type | Key Checks |
|----------|-----------|
| **API Bug** | Frontend → API → Schema → Service → DB chain; field completeness |
| **DB Migration** | Model changed → `alembic revision --autogenerate`; no migration = schema drift |
| **System-level** | Draw E2E chain; define handshake evidence per edge; insert probes first |
| **Cross-Surface** | Shared artifact → identify contract → consumer list → regression matrix |

---

## Phase 6: Knowledge Deposit + Self-Reflection

### 6.1 Update Knowledge Files (Rule 9)

| File | When to Update |
|------|---------------|
| `references/bug-records.md` | Every fix (project history) |
| `references/bug-patterns.md` | New pattern / new fix strategy (universal) |
| `references/blind-spots.md` | New blind spot discovered |

### 6.2 Self-Reflection (Rule 9)

| Dimension | Score (1-5) | Evidence |
|-----------|------------|----------|
| First-time correctness | [1-5] | Did the fix work on first attempt? |
| Scope accuracy | [1-5] | Did I find all affected areas? |
| Minimal change | [1-5] | Was the change as small as possible? |
| Side effect prediction | [1-5] | Did I predict all side effects? |
| Root cause depth | [1-5] | Did I fix root cause, not symptom? |
| **Total** | [/25] | |

| Issue | What Happened | Why I Missed It | Prevention |
|-------|--------------|-----------------|------------|

### Regression Autopsy (when fix introduced a regression)

```markdown
- **Original Bug**: [what was being fixed]
- **New Bug Introduced**: [what broke]
- **Why I didn't predict it**: [blind spot]
- **Classification**: [missed consumer / contract violation / edge case / ...]
```

---

## Domain-Specific Checks

| Bug Type | Key Checks |
|----------|-----------|
| **Backend/API** | Schema drift, timeout/retry, transactions, N+1, connection pool, ORM lazy loading |
| **Frontend/UI** | State (useEffect deps, unmount), race conditions, CORS, hydration, overflow/Portal |
| **System-level** | Cross-layer chain, async/streaming, IPC, routing |
| **Framework** | Read source code first (Rule 7), verify assumptions with tests |
| **AI/LLM** | Tool binding modes, simulated vs native, streaming, token limits |

---

## Skill Delegation

| Trigger | Delegate To |
|---------|-----------|
| Need new API endpoint | fullstack-developer |
| UI fix needed | frontend-design |
| Schema change needed | database-migrations |
| After fix (mandatory) | code-review |

---

## Anti-Patterns (FORBIDDEN)

| Forbidden | Correct |
|-----------|---------|
| Fix without RCA | Hypothesis ladder first |
| Single hypothesis then fix | List 3-5 hypotheses, verify each |
| Fix UI bug by code reading alone | Get runtime evidence first (Rule 8) |
| Skip consumer list for shared code | Fill consumer list first |
| Tests pass but server runs old code | Clear cache + restart + verify fix is live (Rule 6) |
| Fix code but ignore corrupted data | Assess data impact + repair if needed |
| Trust framework docs blindly | Read source code or run tests (Rule 7) |
| Fix one copy, miss the duplicate | Grep function name; check both Path A and Path B |
| Pattern match without boundary check | Add word boundaries / anchors / exact match (Rule 11) |
| Model changed but no migration | Run `alembic revision --autogenerate` |
| Use full workflow for a typo | Use Quick Fix path (Phase 0 Trivial tier) |
| Skip self-reflection | Must score, analyze, and learn |

---

## Final Checklist

### Core (Standard + Complex tiers)

| # | Check | Phase |
|---|-------|-------|
| 1 | Severity (P0-P3) + Tier (Trivial/Standard/Complex) classified | 0 |
| 2 | Root cause passes 4 gates | 2A |
| 3 | Bug pattern library + records searched | 2B |
| 4 | Impact chain traced (code+data+time+event) | 2C |
| 5 | Similar issue scan completed | 2D |
| 6 | Scope passes 5 gates (incl. duplicate scan) | 3A |
| 7 | Side effect prediction + blind spot check | 3A |
| 8 | Regression verification ALL passed (L0-L3) | 5A |
| 9 | Runtime deployment verified | 5B |
| 10 | Bug Summary output + code-review passed | 5C |
| 11 | Knowledge files updated | 6.1 |
| 12 | Self-reflection completed | 6.2 |
| 13 | If DB model changed: Alembic migration generated | 5 |
| 14 | User confirmed fix + no new bugs | Final |

### Trivial Tier Checklist (Quick Fix path only)

| # | Check | Status |
|---|-------|--------|
| 1 | Fix applied and tested (lint/test/manual) | [ ] |
| 2 | Bug record entry added | [ ] |
| 3 | No behavioral change introduced | [ ] |

---

## OpenClaw Project Context

### Architecture Map

```
backend/app/
├── api/v1/              # FastAPI routes (agents, auth, chat, skills, tools, profile)
├── core/
│   ├── graph/           # LangGraph StateGraph (agent_graph, nodes/llm_node, tool_node, prepare_node)
│   ├── langchain/       # LangChain tools (tools.py, shell_tool.py, e2b_tools.py)
│   ├── mcp/             # MCP server integration (pool.py)
│   ├── database.py      # SQLAlchemy async engine
│   └── security.py      # JWT auth
├── models/              # SQLAlchemy ORM models (agent, tool, user, skill)
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic (agent_executor, chat_service, tool_call_parser, ...)
├── middleware/           # Request logging, audit, error handling
└── main.py              # FastAPI app entry

frontend/src/
├── features/            # Feature modules (chat, settings, admin, knowledge, skills, agents)
│   ├── chat/            # ChatPageV2, MessageRenderer, ToolCallCard, SkillExecutionInline
│   └── ...
├── components/ui/       # shadcn/ui style components (dialog, switch, checkbox)
├── hooks/               # React hooks (useChatStream — SSE event handling)
├── store/               # Zustand state management
└── lib/                 # API client (api-client.ts), markdown utils
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.11+ |
| ORM | SQLAlchemy 2.0 (async) |
| DB | PostgreSQL (asyncpg) or MySQL (aiomysql) |
| Migrations | **Alembic** (`backend/alembic/`) |
| Cache | Redis |
| AI | LangChain 0.3.x + LangGraph 0.4.x |
| Vector DB | ChromaDB |
| Frontend | React 18 + Vite + TypeScript |
| UI | Radix UI + Tailwind CSS |
| State | Zustand + TanStack Query |
| Tests | pytest (backend), Vitest (frontend) |
| Deploy | Docker Compose, supports PyInstaller desktop build |

### High-Risk Bug Zones

#### Backend Hot Zones

| Zone | Files | Why It's High-Risk |
|------|-------|--------------------|
| **Simulated Tool Call Parsing** | `services/tool_call_parser.py`, `core/graph/nodes/llm_node.py` | Regex-based; dual implementations; multi-arg edge cases |
| **Agent Executor** | `services/agent_executor.py` | 3000+ LOC; native + simulated modes; complex streaming |
| **Tool Argument Remapping** | `core/graph/nodes/tool_node.py` | LLM wrong param names → alphabetical guess |
| **LLM Streaming (httpx)** | `services/llm_manager.py` | Reasoning model fallback; SSE; reasoning_content |
| **MCP Tool Integration** | `core/mcp/pool.py`, `services/tool_service.py` | MCP lifecycle; command vs HTTP; timeout |
| **Skill Runtime** | `services/skill_executor.py`, `services/skill_service.py` | Script exec; env var injection; enhanced vs local |
| **Chat Streaming** | `services/chat_service.py` | SSE events; client disconnect; async save |
| **Memory System** | `services/unified_memory_manager.py` | L1/L2; embedding scoring; slow queries |

#### Frontend Hot Zones

| Zone | Files | Why It's High-Risk |
|------|-------|--------------------|
| **SSE Chat Stream** | `hooks/useChatStream.ts` | Event parsing; reconnection; reasoning_content |
| **Tool Call Rendering** | `features/chat/components/ToolCallCard.tsx` | Dynamic display; error states; loading |
| **Skill Execution UI** | `features/chat/components/SkillExecutionInline.tsx` | Inline status; progress; error display |
| **Markdown Renderer** | `features/chat/components/MarkdownRenderer.tsx` | Nested code fences; special chars; XSS |
| **Agent Editor** | `features/agents/AgentEditorPage.tsx` | Complex form state; tool/skill/KB associations |
| **Zustand Store** | `store/` | State updates not re-rendering if reference unchanged |

### Two Code Paths for Agent Execution

```
Path A: Direct Executor (most common)
  chat API → chat_service → agent_executor.py → tool_call_parser.py → tool execution

Path B: StateGraph (LangGraph)
  chat API → chat_service → agent_graph.py → llm_node.py → tool_node.py → tool execution
```

**When fixing anything in Path A, always check Path B for the same issue (and vice versa).**

### Known Duplicate Implementations

| Function / Feature | Primary Location | Known Alternate Location |
|--------------------|-----------------|-------------------------|
| `parse_simulated_tool_calls` | `services/tool_call_parser.py` | `core/graph/nodes/llm_node.py` |
| Tool loading / binding | `services/agent_executor.py` | `core/graph/agent_graph.py` |
| Token counting | `services/token_counter.py` | May have inline counting in `agent_executor.py` |
| Memory management | `services/unified_memory_manager.py` | `core/graph/nodes/prepare_node.py` |

### OpenClaw Common Framework Pitfalls (Rule 7)

| Area | Assumption | Reality |
|------|-----------|---------|
| Config load order | First file has priority | Often last file wins (dict.update) |
| ORM lazy loading | Relations auto-load | Default lazy, causes N+1 |
| Async on Windows | Same as Linux | Windows uses ProactorEventLoop; `run_dev.py` forces SelectorEventLoop |
| Pydantic serialization | model_dump() includes all | exclude_unset=True changes behavior |
| LangChain tool binding | All models support tools | Reasoning models need simulated mode |
| `__pycache__` | Python uses latest source | Stale `.pyc` can persist across restarts |

### Windows Development Environment Gotchas

| Issue | Symptom | Workaround |
|-------|---------|-----------|
| Path separators | `\` vs `/` | Use `pathlib.Path` or `os.path.join` |
| asyncio event loop | ProactorEventLoop default | `run_dev.py` forces `loop="asyncio"` |
| `__pycache__` file locks | Can't delete while running | Kill process FIRST, then clean |
| Console encoding | GBK/CP936 default | `sys.stdout.reconfigure(encoding='utf-8')` |
| Playwright on Windows | Browser launch may fail | Runs in separate thread with own loop |

---

## Verification Commands (OpenClaw)

### Backend

```bash
cd backend
ruff check app/                                    # Lint
python -m pytest tests/ -v --tb=short              # Unit tests
python -m pytest tests/test_specific.py -v         # Specific test
alembic revision --autogenerate -m "check"         # DB migration check
```

### Frontend

```bash
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
```

### Backend Server Restart

```powershell
Get-WmiObject Win32_Process -Filter "Name='python.exe'" | Where { $_.CommandLine -like "*run_dev*" }
Stop-Process -Id [PID] -Force
Get-ChildItem -Path "backend" -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
Start-Process -FilePath "backend\venv\Scripts\python.exe" -ArgumentList "run_dev.py" -WorkingDirectory "backend"
Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -UseBasicParsing -TimeoutSec 5
```

---

## Reference Files

### Living Data Files (update after every fix)

| File | Purpose |
|------|---------|
| `references/bug-records.md` | Project-specific bug history |
| `references/blind-spots.md` | **Single source of truth** for AI blind spot registry |

### Pattern Libraries (domain knowledge)

| File | Purpose |
|------|---------|
| `references/bug-patterns.md` | Universal bug pattern library (11 categories) |
| `references/backend-patterns.md` | Backend issues (API, ORM, LLM integration, OpenClaw-specific) |
| `references/frontend-patterns.md` | Frontend issues (React hooks, race conditions, CORS) |

### Detailed Guides

| File | Purpose |
|------|---------|
| `references/system-rca.md` | System-level RCA (cross-layer, multi-process bugs) |
| `references/regression-matrix.md` | Complete zero-regression verification matrix |

---

## Skill Evolution

Update this skill when:
- Code review finds a bug that the workflow should have prevented
- A recurring bug class repeats across fixes

Prefer updating specific sections over adding new rules.
After updates, validate that the workflow is still coherent and not overly bureaucratic.
