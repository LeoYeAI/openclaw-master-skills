---
name: ariadne-thread
description: Create AI-friendly project structures using progressive disclosure indexing (AGENTS.md, module INDEX.md files, file intent headers). ALWAYS use this skill when the user wants to: create or update AGENTS.md or llms.txt, add INDEX.md files to modules, set up project navigation for AI agents, retrofit an existing codebase with AI-friendly indexes, design module boundaries with explicit dependency and modification-risk documentation, or mentions "AI-friendly project", "progressive disclosure", "project index", "codebase navigation", or "ariadne". Also use when the user asks how to structure a new project so AI tools can navigate it efficiently, even if they don't use these exact terms.
---

# Ariadne Thread

Create codebases that AI agents can navigate efficiently through progressive disclosure — revealing only what's needed, when it's needed.

## When to Use

Apply this skill when the user:
- Starts a new project and wants AI-friendly structure
- Restructures or indexes an existing codebase
- Adds project navigation (AGENTS.md, INDEX.md, llms.txt)
- Designs module boundaries and dependencies
- Mentions: "AI-friendly project", "progressive disclosure", "project index", "codebase navigation", or "ariadne"

**Language-agnostic**: applies to any language. See [language-adaptation.md](references/language-adaptation.md) for per-language mappings.

**When NOT to apply**: Minimal single-file projects, quick prototypes, or codebases where indexing overhead outweighs benefit. Skip full L1/L2 when the project has fewer than ~5 source files; a lightweight AGENTS.md may suffice.

## Core Philosophy

Like Ariadne's thread through the labyrinth, a well-indexed codebase gives AI agents a clear path from project overview to implementation detail. **An agent should understand your project structure, locate any function, and assess the impact of any modification — without reading the entire codebase.**

Two optimization targets:
1. **Navigation efficiency** — minimize tokens consumed to find the right code
2. **Modification safety** — maximize probability of correct changes via explicit contracts and dependency visibility

## The 4-Level Index Architecture

```
L0  PROJECT ROOT     ← AGENTS.md (80–150 lines, prefer brevity)
│                       Project map, navigation table, build commands, cross-cutting patterns
│
L1  MODULE INDEX     ← Each directory gets an INDEX.md (~50 lines)
│                       Purpose, public API, bidirectional dependencies, contracts,
│                       task routing, modification risk, test mapping
│
L2  FILE INTENT      ← File headers (~5-10 lines per file)
│                       What this file does, public interface, contracts, side effects
│
L3  INLINE DETAIL    ← Comments on non-obvious logic only
                        Why, not what; tricky edge cases; business rules
```

AI agents start at L0 and drill down only as needed.

### L0: Project Root Index

Create an `AGENTS.md` at the project root with:

1. **One-line project description**
2. **Directory map** — ASCII tree with purpose annotations
3. **Quick navigation table** — key entry points by area
4. **Build & test commands**
5. **Code conventions summary**
6. **Architectural constraints** — illegal dependency directions, global invariants
7. **Cross-cutting behavior patterns** — error handling, logging, concurrency model
8. **Agent Workflow** — at the **end** of the file (Checklist-at-END format): mandatory steps before editing — locate module via Quick Navigation, open `INDEX.md` and check Dependents before modifying public API, confirm Modification Risk for breaking changes, run Tests before finishing
9. **Index exclusions** — Optional `.cursorignore` (same syntax as `.gitignore`) to exclude build artifacts, dependencies, generated code; common examples: `node_modules/`, `dist/`, `vendor/`, `__pycache__/`, `target/`, `*.generated.*` — adapt to your ecosystem

The cross-cutting patterns section is critical: it prevents the AI from reading 3-4 existing files just to infer "how do we handle errors here?". One 30-line declaration replaces ~1500 tokens of pattern inference.

**All 9 sections are required** — they are the difference between an AGENTS.md that actually guides AI behavior and one that merely documents the project for humans. The sections that get skipped most often (Architectural Constraints, Cross-Cutting Patterns, Agent Workflow checklist) are also the ones with the highest AI value.

**Navigation priority**: Prefer navigating via `INDEX.md` Dependents and Dependencies over semantic/keyword search. Structural dependency paths surface architecturally critical files that retrieval often misses. When modifying a module's public API, always consult its Dependents list first to assess blast radius.

**Information placement (Lost in the Middle)**: LLMs attend more to context start and end. Place high-priority content (Build, Quick Navigation, Agent Workflow) at the beginning or end of AGENTS.md; keep secondary sections toward the middle.

```markdown
## Architectural Constraints

<!-- Typical Web app layers; adapt to project: app/, packages/, layers/, etc. -->
- Dependency direction: presentation → domain → infrastructure (never reverse)
  Example: ui/ → core/ → infra/ — or app/features/, packages/core/, etc.
- All external calls (HTTP, DB, cache) go through infrastructure layer — e.g. `src/infra/` or `[project-path]/infra/`
- No direct file I/O outside designated storage module

## Cross-Cutting Patterns

### Error Handling
- Throw typed errors (e.g. [ErrorType], [ValidationError]), never raw strings
- Log errors before re-throwing across module boundaries
- Public functions document all throwable error types in file header

### Logging
- Use structured logger from [project logger location]
- Include [trace_id or request_id] in all log entries
- Levels: ERROR (failures), WARN (degradation), INFO (operations)

### Concurrency (if applicable)
- Document thread-safety per module (single-threaded vs thread-safe)
- Define lock ordering strategy (e.g. by resource name, by hierarchy) and record in AGENTS.md
- Apply consistently to avoid deadlocks
```

For the full AGENTS.md template, see [index-templates.md](references/index-templates.md).

### L1: Module Index

Every module directory gets an `INDEX.md` — any directory that has a public API, a barrel/`__init__`, or 3+ source files. This is the **most information-dense layer** — it must answer not just "what does this module do?" but also "who depends on it?", "what will break if I change it?", and "which file should I edit for task X?".

*Example below uses domain `auth`; replace with your domain — billing, reporting, catalog, etc.*

```markdown
# Module: auth

Handle user authentication and session management.

Status: stable | Fan-in: 5 | Fan-out: 2

## Public API

| Export | File | Description |
|--------|------|-------------|
| `authenticate()` | `authenticate.*` | Verify credentials, return session |
| `authorize()` | `authorize.*` | Check permissions for resource |
| `SessionStore` | `session_store.*` | Session lifecycle management |

## Dependencies (Fan-out: 2)

<!-- Use repo-root-relative paths. Optional edge type: [imports] | [inherits] | [instantiates] -->

- `src/infra/db` — user record lookups
- `src/shared/crypto` — password hashing

## Dependents (Fan-in: 5)

<!-- Prefer structural navigation via this list over semantic search. Use repo-root-relative paths. -->

- `src/api/routes/user` → authenticate()
- `src/api/middleware/auth-guard` → authorize()
- `src/core/billing` → get_session()
- `src/core/notification` → get_user_from_session()
- `src/api/routes/admin` → authorize()

## Interface Contract

- authenticate(): returns Session (token non-empty, expires_at > now) or throws AuthError
- All failed auth attempts → audit log written before exception propagates
- Thread-safe: all public functions can be called concurrently
- Side effect: authenticate() writes to audit_log on failure

## Modification Risk

- Add field to Session → compatible, no consumer changes needed
- Change authenticate() signature → BREAKING, update 5 dependents
- Change error types → BREAKING for all specific catch blocks

## Task Routing

- Add login method → modify authenticate.*, possibly add new file
- Change session TTL → modify session_store.*, update config
- Add permission type → modify authorize.*, update Permission enum
- Fix token validation bug → modify token_validator.*

## Tests

- Unit: `tests/unit/auth/`
- Integration: `tests/integration/auth_flow_test.*`
- Critical: auth_flow_test (must pass before merge)
- Untested: token_refresh() — extra caution when modifying
```

**Voice Coding**: L1 `Task Routing` supports "say task → get file path" — map natural-language tasks to specific files for hands-free navigation.

**Common mistake — avoid narrative prose in INDEX.md**: The structured sections (Dependents, Modification Risk, Task Routing) are what make an INDEX.md useful for AI navigation. A long prose description of each file ("This file is responsible for X, it does Y, here are some notes...") might look thorough but it fails to answer the core AI questions: who depends on this? what breaks if I change it? which file do I edit? Prefer the structured template even if it feels terse — density and scanability beat completeness.

**Why each section matters for AI:**

| Section | AI Question It Answers | What it replaces |
|---------|----------------------|-----------------|
| **Dependents** | "Who calls me? What breaks if I change?" | Full-project grep to discover callers |
| **Interface Contract** | "What invariants must I preserve?" | Re-reading caller files to infer constraints |
| **Modification Risk** | "Is this change safe? How many files to update?" | Underestimating blast radius and missing dependents |
| **Task Routing** | "Which file should I edit for task X?" | Reading wrong files before finding the right one |
| **Tests** | "What should I run to verify?" | Searching for test files across the project |

The actual token savings depend heavily on project size and how the AI handles uncertainty — they scale with the number of modules and files. The value is real but varies; don't treat any specific number as a guarantee.

For the full INDEX.md template, see [index-templates.md](references/index-templates.md).

### L2: File-Level Intent + Contract

Every source file starts with an intent header. For **public API files** (called by other modules), extend the header with contract annotations:

**C++ (public header with contract)**:
```cpp
/**
 * @brief Verify user credentials against stored records.
 *
 * @pre password is non-empty, username has passed format validation
 * @post On success: returned Session.token is non-empty and unique
 * @post On failure: audit log entry written before exception
 * @throws AuthError if credentials are invalid
 * @throws RateLimitError if attempts exceed MAX_ATTEMPTS
 * @sideeffect Writes to audit_log table on failure
 * @threadsafe
 *
 * @module auth
 * @public authenticate
 */
```

**TypeScript (public API with contract)**:
```typescript
/**
 * Verify user credentials against stored records.
 *
 * @pre password is non-empty, username passed format validation
 * @post Success: Session.token is non-empty and unique
 * @post Failure: audit log entry written before throwing
 * @throws {AuthError} credentials invalid
 * @throws {RateLimitError} attempts exceed MAX_ATTEMPTS
 * @sideeffect Writes audit_log on failure
 *
 * @module auth
 * @public authenticate
 */
```

**Internal files** (not called across module boundaries) keep the simple 3-5 line header. Only public API files need full contracts.

Contract annotation reference:

| Annotation | Purpose | When to Use |
|-----------|---------|-------------|
| `@pre` | What must be true before calling | Input validation assumptions |
| `@post` | What is guaranteed after return | Return value constraints |
| `@throws` | What errors can be thrown | All error conditions |
| `@sideeffect` | What state changes beyond return value | DB writes, events, cache invalidation |
| `@threadsafe` | Concurrency guarantee | Multi-threaded systems |
| `@performance` | Latency/throughput constraints | Hot-path functions |
| `@lines` / `@range` | Key line ranges for large files | When file exceeds ~300 LOC; e.g. `@lines 45-89 main logic` |

**Path convention**: In L1, use repo-root-relative paths (e.g. `src/auth/authenticate.ts`) — avoid `./`, `../` for clarity and Voice Coding compatibility.

See [index-templates.md](references/index-templates.md) for all language templates.

### L3: Inline Annotations

Comment ONLY non-obvious logic:

```cpp
// Rate limit: 5 attempts per IP per minute (compliance FR-201)
if (attempts > MAX_ATTEMPTS) throw RateLimitError();

// Must resolve parent before children — circular refs in legacy schema
auto resolved = resolve_parent_first(node);
```

**Never comment obvious code.** AI reads code natively — comments that restate the code are pure noise.

## Module Design Principles

### Single Responsibility

- One module = one clear purpose (stated in INDEX.md)
- One file = one concept, under 300 lines (or ~500 for verbose languages)
- If you cannot name it clearly, split it

```
✅ src/billing/calculate_invoice.*    — does one thing
✅ src/billing/apply_discount.*       — does one thing
❌ src/billing/utils.*                — does many things
❌ src/helpers.*                      — grab bag
```

### Clear Dependency Direction

Typical layering (example; adapt names to your project — e.g. `app/`, `packages/`, `layers/`):

```
presentation/ → domain/ → infrastructure/
         ↘ shared/ (cross-cutting) ↙
```

- Depend inward (presentation → domain → infrastructure), never outward
- Document the actual direction in AGENTS.md Architectural Constraints

### Small, Focused Files

| Metric | Target | Reason |
|--------|--------|--------|
| Lines per file | < 300 (< 500 for verbose languages) | AI reads full files; smaller = less wasted context |
| Public symbols per file | 1-5 | Clear public surface |
| Dependencies per file | < 5-8 imports/includes | Limits blast radius |

### Library vs Application Projects

The index structure works for both, but libraries differ in several key areas:

| Aspect | Application | Library |
|--------|-------------|---------|
| **Build & Test** | Has build + run commands | May have no build step (header-only); tests often in separate projects |
| **Public API** | Internal modules calling each other | Consumers are external; public API = exported headers / package interface |
| **Dependents (Fan-in)** | Other modules in the same project | Primarily external consumers (note "External: N/A — library" in Dependents) |
| **Dependency direction** | presentation → domain → infra (example) | Libraries: typically flat or layered by abstraction (e.g., core ← filtering ← testing) |
| **File size targets** | Strict (you control the code) | Guideline only for upstream/third-party code you do not own |

**Header-only libraries** (C++): no `include/` + `src/` split — all code is in headers. The entry header (e.g., `library.hpp`) acts as the barrel/`__init__`. There is no independent build step; document how consumers include and link.

**Upstream / third-party code**: When indexing a library you do not maintain (e.g., a vendored dependency), create indexes (L0 + L1) for navigation but do NOT modify source files (no L2 header changes, no refactoring oversized files). Flag issues in indexes with `⚠ UPSTREAM` instead of `⚠ needs split`.

## Intent-Oriented Code

Write code that expresses **what** it accomplishes, not **how**.

### Naming Principles (Universal)

| Layer | Principle | C++ Example | TypeScript Example | Python Example |
|-------|-----------|-------------|-------------------|----------------|
| Files | descriptive, one concept | `invoice_calculator.cpp` | `calculate-invoice.ts` | `invoice_calculator.py` |
| Dirs | group by domain | `billing/`, `auth/` | `billing/`, `auth/` | `billing/`, `auth/` |
| Functions | verb-first, outcome | `calculate_total()` | `calculateTotal()` | `calculate_total()` |
| Classes | PascalCase noun | `InvoiceCalculator` | `InvoiceCalculator` | `InvoiceCalculator` |
| Constants | SCREAMING_SNAKE | `MAX_RETRY_COUNT` | `MAX_RETRY_COUNT` | `MAX_RETRY_COUNT` |
| Booleans | is/has/should | `is_authenticated` | `isAuthenticated` | `is_authenticated` |

### Function Signatures — Express Intent

```cpp
// ✅ Intent-oriented: tells you WHAT
MonetaryAmount calculate_invoice_total(
    const std::vector<LineItem>& line_items,
    const std::vector<Discount>& discounts);

// ❌ Implementation-oriented: tells you HOW
int process_items(void* items, int count, int flags);
```

### API Design

Applies to **any external interface** (REST, gRPC, library headers, CLI):

- Name by **resource/concept**, not implementation
- Consistent input/output contracts
- Version your API (URL path, header, or namespace)
- Document error conditions explicitly

For detailed conventions, see [naming-api-conventions.md](references/naming-api-conventions.md).

## Documentation Tiers

Not all documentation serves the same audience or requires the same update frequency. This skill distinguishes two tiers:

| Tier | Files | Audience | Update Timing | Staleness Impact |
|------|-------|----------|---------------|-----------------|
| **A — AI Runtime Index** | `AGENTS.md`, `INDEX.md`, file headers (L2), inline comments (L3) | AI agents | **Real-time** — atomic with code changes | Critical: stale → wrong navigation, missed dependencies, broken contracts |
| **B — Human Communication** | `README.md`, `architecture.md`, ADRs, API docs, guides, changelogs | Human developers | **Batch** — at iteration end | Moderate: stale → human confusion, but AI unaffected |

**Key insight**: Tier A indexes are the AI's "working memory" — they must be updated in the same operation as the code change. Tier B documents are "reports" derived from Tier A — they can be regenerated at iteration boundaries.

**During active development**: AI agents only maintain Tier A files. Tier B documents are transparent to the AI — they are neither read nor written until the iteration-end sync.

**Token economics**: This separation reduces per-change AI overhead by ~60%, while actually improving Tier B document quality (batch updates are more coherent than incremental patches).

## Project Documentation (Tier B)

Human-facing documentation follows the same progressive disclosure structure, but is maintained at iteration boundaries rather than in real-time. Common structure (adapt to project; ADR is optional — omit `adr/` if you don't use ADRs):

```
docs/
├── README.md              # What is this, how to start (< 1 page)
├── architecture.md        # System overview, component diagram
├── adr/                   # Architecture Decision Records (optional)
│   ├── INDEX.md           # ADR list with one-line summaries
│   └── 001-database.md
└── api/                   # API reference (or equivalent)
    ├── INDEX.md           # Endpoint / header summary table
    └── users.md           # Detailed docs
```

Rules:
1. **One doc = one purpose**
2. **INDEX.md in every doc directory**
3. **Link, don't inline** — reference Tier A indexes (`INDEX.md`) as source of truth
4. **Max 500 lines per doc**
5. **Updated at iteration end** — not on every code change

For doc templates and ADR format, see [doc-standards.md](references/doc-standards.md).

## Language Adaptation

The 4-level index and design principles are universal. Per-language conventions (C++, TypeScript, Python, Go, Rust, Java/Kotlin) — directory layout, file naming, L2 contract annotations, build commands — are in [language-adaptation.md](references/language-adaptation.md). Load that file when indexing a project in a specific language.

## Workflow: New Project

1. **Identify language ecosystem** — see [language-adaptation.md](references/language-adaptation.md)
2. **Design the directory map** before writing code
3. **Create AGENTS.md** — project table of contents + cross-cutting patterns + AI Agent Instructions
4. **Create module INDEX.md** as you create each directory (include all sections)
5. **Add file intent headers** — simple for internal files, full contract for public API
6. **Follow naming conventions** from day one
7. **Defer Tier B docs** — create `docs/` directory structure but fill content only at first iteration end

## Workflow: Retrofit Existing Project

**Principle: Document first, refactor later.** Create indexes for the codebase AS-IS. Flag issues (oversized files, violations) in the indexes but do not block on fixing them.

**Monorepo / sub-project**: If the target is a sub-directory within a larger repo, place `AGENTS.md` at the sub-project root (e.g., `lib/AGENTS.md`). Build commands should cover this sub-project only (or note the parent command). See the [monorepo variant](references/index-templates.md#monorepo--sub-project-variant) in templates.

**Priority**: Start with the highest Fan-in module (most depended-on) — it yields the most navigation savings.

**Partial migration**: If migrating a single module (not the whole project), start at L1 — create `INDEX.md` for the target module directly. Skip L0; assume the parent `AGENTS.md` will be created later or already exists.

**Library projects**: If the target is a library (not an application), see [Library vs Application Projects](#library-vs-application-projects) for differences in Build & Test, Public API, and Dependents. For header-only C++ libraries, the entry header acts as the barrel — document it in `AGENTS.md` and treat the main header directory as a single module.

**Upstream / third-party code**: If you do not own the source code (vendored dependency, upstream library), create L0 + L1 indexes for navigation but skip L2 (do not modify source file headers) and L3 (do not modify inline comments). Flag oversized files with `⚠ UPSTREAM` instead of suggesting splits.

1. **Create L0**: Write `AGENTS.md` with directory map, navigation table, cross-cutting patterns, and AI Agent Instructions. Mark any discovered architectural violations as `⚠ KNOWN VIOLATION` in Architectural Constraints
2. **Add L1**: Create `INDEX.md` in each major module — start with Public API + Dependencies + Dependents. Use `grep -rn "from [module]" .` or IDE search to discover Dependents. For flat directories with many files, use section headers within INDEX.md to organize logical groups (see [L1 Retrofit Tips](references/index-templates.md#l1-retrofit-tips))
3. **Enrich L1**: Add Interface Contract, Task Routing, Modification Risk, Tests. In Files table, flag oversized files (e.g., `⚠ 1066 lines, needs split` or `⚠ UPSTREAM` for code you do not own). Also flag files with forbidden names — `utils.*`, `helpers.*`, `types.*`, `common.*` — with `⚠ needs split/rename` and add a rename task to Task Routing. These names indicate unclear responsibility and should be resolved over time
4. **Verify L2**: Ensure public API files have contract headers; internal files have intent headers (skip for upstream code)
5. **Audit L3**: Remove obvious comments, add explanations for tricky logic (skip for upstream code)
6. **Validate per module**: After each module's INDEX.md, test: ask an AI to locate a function and assess change impact. If it reads > 5 files or misses a dependent, improve that index before moving on
7. **Sync Tier B**: Once all Tier A indexes are complete, run an iteration-end sync to generate/update all human-facing docs from Tier A content

## Index Maintenance

**Directive**: Every code change MUST include atomic updates to relevant Tier A indexes. See [index-maintenance.md](references/index-maintenance.md) for the full trigger→action table, anti-patterns, and Tier B sync workflow. When the user says "documentation sync" or "iteration end", execute the Tier B batch process.

## Detailed References

- **Index templates (L0/L1/L2)**: [index-templates.md](references/index-templates.md)
- **Naming + API conventions**: [naming-api-conventions.md](references/naming-api-conventions.md)
- **Documentation standards + ADR format**: [doc-standards.md](references/doc-standards.md)
- **Language adaptation (C++, TS, Python, Go, Rust, Java)**: [language-adaptation.md](references/language-adaptation.md)
- **Index maintenance (Tier A/B triggers)**: [index-maintenance.md](references/index-maintenance.md)
