# Index Templates

Copy-paste ready templates for each level of the progressive disclosure index. All templates are language-agnostic — replace `[ext]` placeholders with your language's file extension.

**Information placement (Lost in the Middle)**: Place high-priority content (Build, Quick Navigation, Agent Workflow) at the start or end of files. LLMs attend less to the middle of long context — keep critical routing/checklist sections near the top or bottom.

## L0: AGENTS.md Template

```markdown
# [Project Name]

[One-sentence description: what this project does and for whom.]

## Architecture Overview

[2-3 sentences describing the system architecture and key design decisions.]

## Directory Map

<!-- Typical Web app layout; adapt to project: app/, packages/, layers/, monorepo sub-packages, etc. -->

\```
src/              # (or include/ + src/ for C/C++; or app/, packages/, etc.)
├── api/          # [Purpose: external interface layer]
├── core/         # [Purpose: business logic and domain models]
├── infra/        # [Purpose: database, cache, external services]
├── shared/       # [Purpose: cross-cutting utilities]
└── ui/           # [Purpose: frontend components, if applicable]
tests/
├── unit/         # Unit tests (mirrors src/ structure)
├── integration/  # Integration tests
└── e2e/          # End-to-end tests
docs/
├── adr/          # Architecture Decision Records (optional — omit if not using ADRs)
└── api/          # API reference (or equivalent)
\```

## Quick Navigation

| Area | Entry Point | Purpose |
|------|-------------|---------|
| [Area 1] | `src/[path]/INDEX.md` | [What this area handles] |
| [Area 2] | `src/[path]/INDEX.md` | [What this area handles] |
| [Area 3] | `src/[path]/INDEX.md` | [What this area handles] |
| Config | `src/config/INDEX.md` | Application configuration |

## Build & Test

| Command | Purpose |
|---------|---------|
| `[install command]` | Install dependencies |
| `[build command]` | Build the project |
| `[test command]` | Run test suite |
| `[run command]` | Start / run the application |
| `[lint command]` | Lint and format check |

## Conventions

- **Files**: [naming-convention], under 300 lines, one concept per file
- **Tests**: co-located or mirrored in `tests/`
- **Naming**: see `docs/conventions.md`
- **Dependencies**: inward direction only (presentation → domain → infra; example: ui → core → infra)

## Architectural Constraints

- Dependency direction: presentation → domain → infra (never reverse). Example: ui/ → core/ → infra/ — adapt to your layout.
- All external calls (HTTP, DB, cache) go through infrastructure layer — e.g. `src/infra/` or `[your-infra-path]/`
- [Add project-specific constraints]

## Cross-Cutting Patterns

### Error Handling
- [Error type strategy: typed errors, error codes, or Result types]
- [Propagation rule: log before re-throw, wrap with context, etc.]
- [Public functions document throwable errors in file header]

### Logging
- [Logger location and usage pattern]
- [Structured logging fields: request_id, user_id, etc.]
- [Log levels and when to use each]

### Concurrency (if applicable)
- [Thread safety model per module]
- [Lock ordering convention]
- [Async/await patterns or thread pool usage]

## Key Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `[VAR_NAME]` | [What it configures] | [Yes/No] |

## AI Agent Instructions

This project uses a two-tier documentation model:

- **Tier A (this file + all `INDEX.md` + file headers)**: Maintain in real-time, atomic with every code change. A code change is NOT complete until Tier A indexes reflect it.
- **Tier B (`docs/*.md`, `README.md`, ADRs, API docs, guides)**: Do NOT read or update during active development. Updated only at iteration-end sync.

When modifying code:
1. Update the parent `INDEX.md` if files are added/removed/renamed
2. Update this `AGENTS.md` if modules or navigation entries change
3. Update `INDEX.md` Dependents/Dependencies if call relationships change
4. Do NOT touch any file under `docs/` — defer to iteration-end sync

## Agent Workflow (Read Before Edit)

**Checklist-at-END — complete before any code modification:**

- [ ] Locate target module via Quick Navigation table
- [ ] Open module `INDEX.md` and check Dependents before modifying public API
- [ ] Confirm Modification Risk before signature/error-type changes
- [ ] Run Tests section commands before finishing
```

## Index Exclusions (Optional)

Create `.cursorignore` at project root (same syntax as `.gitignore`) to exclude from AI indexing. Recommended for large repos and monorepos.

Common exclusions (adapt to your ecosystem):

```
# Dependencies
node_modules/
vendor/
.pnp/

# Build output
dist/
build/
.next/
out/
target/

# Generated / cache
*.generated.ts
*.generated.js
__pycache__/
prisma/generated/
graphql/generated/
coverage/
```

Excluding these can reduce indexing time significantly. Add project-specific paths (e.g. `packages/*/dist/` for monorepos). Consider opening specific packages as multi-root workspaces rather than indexing the entire repo.

## L0: llms.txt Template

Use `llms.txt` for **web-accessible projects** (published libraries, SaaS APIs, open-source projects with docs sites) where external AI agents discover your project via URL.

**Division of labor**:
- **llms.txt**: Discovery entry — placed at site/project root (`/llms.txt`); helps agents find key resources when browsing. Optional `llms-full.txt` for detailed docs.
- **AGENTS.md**: Local repo execution context — build commands, navigation, conventions. Always create for local development. Agents read the nearest `AGENTS.md` when editing.

```markdown
# [Project Name]

> [One-sentence description]

## Documentation

- [Getting Started](/docs/getting-started.md): Setup and first steps
- [Architecture](/docs/architecture.md): System design overview
- [API Reference](/docs/api/INDEX.md): API endpoints / public headers

## Source Code

- [API Layer](/src/api/INDEX.md): External interface handlers
- [Core Logic](/src/core/INDEX.md): Business domain models
- [Infrastructure](/src/infra/INDEX.md): Database, cache, external services
```

## L1: Module INDEX.md Template (Tier A — Real-time)

**Path convention**: Use repo-root-relative paths (e.g. `src/auth/authenticate.ts`) in all Dependencies and Dependents. Avoid `./`, `../` for clarity and Voice Coding compatibility.

**Section order**: Place Dependents, Modification Risk, Task Routing near the top or bottom — high-value for AI navigation; avoid burying in the middle (Lost in the Middle).

```markdown
# Module: [module-name]

[One-sentence: what this module is responsible for.]

Status: [stable | active | deprecated | experimental] | Fan-in: [N] | Fan-out: [N]

## Dependents (Fan-in: [N])

<!-- Prefer structural navigation via this list over semantic search. Use repo-root-relative paths. -->
<!-- Optional edge type: [imports] | [inherits] | [instantiates] per line -->
<!-- Discovery: grep -rn "from [this_module]" . or grep -rn "import [this_module]" . -->
<!-- If Fan-in > 10, group by parent module instead of listing individual files -->

- `[src/module-x]` → [which function/class it calls]
- `[src/module-y]` → [which function/class it calls]
- `[src/module-z]` → [which function/class it calls]

## Modification Risk

- [Change type A] → [compatible | BREAKING], [impact description]
- [Change type B] → [compatible | BREAKING], [impact description]
- [Change type C] → [compatible | BREAKING], [impact description]

## Task Routing

<!-- Maps natural-language tasks to files; supports Voice Coding "say task → get path" -->

- [Common task 1] → modify `[repo-relative/path/file]`, [brief note]
- [Common task 2] → modify `[repo-relative/path/file]`, [brief note]
- [Common task 3] → modify `[repo-relative/path/file]`, [brief note]
- [Common task 4] → modify `[repo-relative/path/file]`, [brief note]

## Public API

| Export | File | Description |
|--------|------|-------------|
| `[function_or_class]` | `[filename]` | [What it does] |
| `[function_or_class]` | `[filename]` | [What it does] |
| `[function_or_class]` | `[filename]` | [What it does] |

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `[file-1]` | ~[N] | [Brief purpose] |
| `[file-2]` | ~[N] | [Brief purpose] |
| `[file-3]` | ~[N] | [Brief purpose] |
<!-- Flag oversized files: | `big_file.py` | ⚠ ~1066 | [Purpose] — needs split | -->
<!-- For files >300 LOC, add @lines or @range in L2 header to guide partial reads -->

## Dependencies (Fan-out: [N])

<!-- Use repo-root-relative paths. Optional: [imports] | [inherits] | [instantiates] per line -->

- `[src/module-a]` — [why this module depends on it]
- `[src/module-b]` — [why this module depends on it]

## Interface Contract

- [function_a()]: [return guarantee] or [error condition]
- [function_b()]: [return guarantee] or [error condition]
- Side effects: [list any state changes beyond return values]
- Thread safety: [safe | unsafe | specific details]

## Tests

- Unit: `[test directory or file pattern]`
- Integration: `[test file]`
- Critical: [test name] (must pass before merge)
- Untested: [area] — extra caution when modifying

## Key Decisions

- [Decision 1] (see `docs/adr/[NNN]-[topic].md`)
- [Decision 2] — [brief rationale if no ADR]
```

### L1 Retrofit Tips

**Discovering Dependents (Fan-in)**:
Run a project-wide search from the project root (or use IDE "Find Usages"). Collect all importing files, then group by the function/class they call.

- **Python**: `grep -rn "from [module_path]" .`
- **TS/JS/Java**: `grep -rn "import.*[module_name]" .`
- **C/C++**: `grep -rn '#include.*[header_name]' .`
- **Go**: `grep -rn '"[module_path]"' .`
- **Rust**: `grep -rn "use [crate]::[module]" .`

**High Fan-in modules** (Fan-in > 10, e.g., loggers, shared utilities):
Group dependents by parent module instead of listing every file:

```markdown
## Dependents (Fan-in: 22)

- `web/skills/` (8 files) → logger
- `web/node/` (6 files) → logger
- `web/services/` (4 files) → logger, log_exception
- `web/database/` (2 files) → logger
- `web/core/` (2 files) → logger, log_startup
```

**Oversized files** (> 300 LOC, or > 500 for verbose languages):
Mark with ⚠ in the Files table. Add a split task in Task Routing. Do NOT block index creation on refactoring.

**Known architectural violations**:
If a file violates the declared Architectural Constraints (e.g., `lib/` imports `web/`), mark it in AGENTS.md:

```markdown
## Architectural Constraints

- lib/ must not depend on web/ (⚠ KNOWN VIOLATION: lib/llm/factory.py imports web.database.models)
```

**Flat directories with many files** (10+ files in one directory, no sub-directories):
When a single directory contains many files that belong to distinct logical groups (e.g., a header-only C++ library with core, parsing, and utility headers all in one folder), use section headers within the INDEX.md to organize them:

```markdown
## Files

### Core (trace lifecycle)

| File | Lines | Purpose |
|------|-------|---------|
| `trace.hpp` | ~424 | trace<T> — session orchestration and callback dispatch |
| `provider.hpp` | ⚠ ~666 | Provider registration and event callbacks |
| `etw.hpp` | ~394 | ETW API start/stop interface |

### Schema & Parsing

| File | Lines | Purpose |
|------|-------|---------|
| `schema.hpp` | ~375 | Event metadata from EVENT_RECORD |
| `parser.hpp` | ~431 | Extract typed properties from events |
| `property.hpp` | ~201 | Single property representation |
```

This keeps a single INDEX.md while preserving logical grouping. The ~50 line target is a guideline — flat directories with 10+ files will naturally exceed it. Prefer one well-organized INDEX.md over splitting by virtual groupings that do not exist as directories.

**Upstream / third-party libraries**:
When indexing code you do not own or maintain, flag oversized files with `⚠ UPSTREAM` instead of `⚠ needs split`. Do NOT add split tasks to Task Routing for upstream code.

### Module Status Values

| Status | Meaning | AI Behavior |
|--------|---------|-------------|
| `stable` | API frozen, rarely changes | Safe to depend on; do not change its interface |
| `active` | Under development, API may change | Review carefully before depending on it |
| `deprecated` | Being phased out | Do NOT add new code here; look for replacement |
| `experimental` | May be removed entirely | Do not depend on this from stable modules |

## L2: File Intent Header Templates (Tier A — Real-time)

### Basic Header (Internal Files)

For files not called across module boundaries — keep it simple:

**C++**:
```cpp
/**
 * @file [filename].h
 * @brief [One sentence: what this file does.]
 *
 * @module [module-name]
 * @public [ClassName], [function_name]
 */
```

**TypeScript**:
```typescript
/**
 * [One sentence: what this file does.]
 *
 * @module [module-name]
 * @public [exported-name-1], [exported-name-2]
 */
```

**Python**:
```python
"""[One sentence: what this module does.]

Public API: [function_or_class_1], [function_or_class_2]
"""
```

**TypeScript — React component / hook variant**:
```typescript
/**
 * [One sentence: what this component/hook does.]
 *
 * @pre [Context/Provider requirement, e.g., "QueryClientProvider in tree"]
 * @sideeffect [HTTP fetch, WebSocket subscription, etc. — if any]
 *
 * @module [feature-name]
 * @public [ComponentName or useHookName]
 */
```

Use this variant for React components and hooks. `@pre` captures required Context/Providers (the React equivalent of input preconditions). `@sideeffect` captures data fetching, subscriptions, or state mutations. Omit `@post`/`@throws` for pure UI components.

### Contract Header (Public API Files)

For files whose functions are called by OTHER modules — include contracts:

**C++**:
```cpp
/**
 * @file [filename].h
 * @brief [One sentence: what this file does.]
 *
 * @pre [precondition: what must be true before calling]
 * @post [postcondition: what is guaranteed after return]
 * @throws [ErrorType] [when this error occurs]
 * @sideeffect [state changes beyond return value]
 * @threadsafe | @not_threadsafe
 * @performance [constraint, e.g., "< 50ms p99"]
 *
 * @module [module-name]
 * @public [ClassName], [function_name]
 */
```

**TypeScript**:
```typescript
/**
 * [One sentence: what this file does.]
 *
 * @pre [precondition]
 * @post [postcondition]
 * @throws {ErrorType} [when]
 * @sideeffect [state changes]
 *
 * @module [module-name]
 * @public [exported-name]
 */
```

**Python** (functions/services with contracts):
```python
"""[One sentence: what this module does.]

Pre: [precondition]
Post: [postcondition]
Raises: [ErrorType] — [when]
Side Effects: [state changes]

Public API: [function_or_class]
"""
```

**Python** (type definitions, enums, exceptions, data classes):
```python
"""[One sentence: what types this module defines.]

Public API:
  - [ClassName]: [purpose]
  - [EnumName]: [purpose, e.g., "error type classification with should_retry property"]
  - [ExceptionName]: [purpose, e.g., "wraps non-retryable errors"]

Usage: [which module(s) consume these types]
"""
```

Use the type definition variant when the file primarily defines classes/enums/dataclasses and has no meaningful pre/post conditions at the module level.

**Go**:
```go
// Package [name] [one sentence: what this package does].
//
// Precondition: [what must be true]
// Returns: [what is guaranteed]
// Errors: [error conditions]
// Side effects: [state changes]
//
// Public API:
//   - [FunctionOrType]: [description]
package name
```

**Rust**:
```rust
//! [One sentence: what this module does.]
//!
//! # Panics
//! [when this module panics]
//!
//! # Errors
//! [error conditions]
//!
//! # Safety
//! [unsafe usage notes, if applicable]
//!
//! # Public API
//! - [`function_or_type`]: [description]
```

**Java**:
```java
/**
 * [One sentence: what this class does.]
 *
 * <p>Pre: [precondition]
 * <p>Post: [postcondition]
 *
 * @throws [ErrorType] [when]
 * @apiNote [side effects or important behavior notes]
 * @see [RelatedClass]
 */
```

## Contract Annotation Quick Reference

| Annotation | When to Use | Example |
|-----------|-------------|---------|
| `@pre` | Input assumptions | `@pre password is non-empty` |
| `@post` | Output guarantees | `@post returned token is unique` |
| `@throws` | Error conditions | `@throws AuthError if credentials invalid` |
| `@sideeffect` | Non-return state changes | `@sideeffect writes audit_log` |
| `@threadsafe` | Concurrency guarantee | `@threadsafe` |
| `@performance` | Latency/throughput | `@performance < 50ms p99` |
| `@lines` / `@range` | Key line ranges for large files (>300 LOC) | `@lines 45-89 main logic`, `@range 120-180 parsing` |

**Rule of thumb**: If a function is only called within its own module, skip contract annotations. If it's called from other modules, add them — the AI needs these to assess modification safety. For oversized files, `@lines` guides agents to partial reads instead of loading the whole file.

## Docs Directory INDEX.md Template (Tier B — Iteration-End)

```markdown
# [Section Name] Documentation

## Contents

| Document | Purpose | Last Updated |
|----------|---------|--------------|
| `[doc-1.md]` | [What it covers] | [YYYY-MM] |
| `[doc-2.md]` | [What it covers] | [YYYY-MM] |
| `[doc-3.md]` | [What it covers] | [YYYY-MM] |

## How to Use

- Start with `[recommended-first-doc.md]` for an overview
- Refer to `[specific-doc.md]` for [specific topic]
- ADRs are numbered chronologically; read INDEX for summaries
```

## ADR INDEX.md Template (Tier B — Iteration-End)

*ADR is optional. Use when your project tracks architecture decisions formally; omit `adr/` if not.*

```markdown
# Architecture Decision Records

| # | Title | Status | Date |
|---|-------|--------|------|
| 001 | [Decision title] | Accepted | YYYY-MM-DD |
| 002 | [Decision title] | Accepted | YYYY-MM-DD |
| 003 | [Decision title] | Proposed | YYYY-MM-DD |
| 004 | [Decision title] | Superseded by 007 | YYYY-MM-DD |

## How to Add an ADR

1. Copy the template from `docs/adr/TEMPLATE.md`
2. Number sequentially (next: [NNN])
3. Update this INDEX.md
4. Set status to `Proposed`, move to `Accepted` after review
```

## Monorepo / Sub-project Variant

When indexing a sub-directory within a larger monorepo (e.g., `lib/` inside a full-stack project):

**AGENTS.md placement**: At the sub-project root (e.g., `lib/AGENTS.md`), not the repo root.

**Build & Test**: List commands relevant to this sub-project only. If tests run from the repo root, note that:

```markdown
## Build & Test

| Command | Purpose |
|---------|---------|
| `pytest tests/unit/lib/` | Run lib unit tests (from repo root) |
| `pytest lib/` | Run tests co-located in lib |
| `pip install -r requirements.txt` | Install dependencies (shared with parent) |

Note: This is a sub-module of the chimera monorepo. Build and dependency
management is handled at the repo root level.
```

**Architectural Constraints**: Include the boundary contract with sibling modules:

```markdown
## Architectural Constraints

- lib/ is a pure dependency — it MUST NOT import from web/, agent/, or other siblings
- Sibling modules depend on lib/ via its `__init__.py` public API only
- ⚠ KNOWN VIOLATION: lib/llm/factory.py imports web.database.models (to be refactored)
```

**Quick Navigation**: Reference only sub-project modules, not the whole repo.

## C++ Project: Full AGENTS.md Example

### Compiled library (CMake, include/ + src/ layout)

```markdown
# ImageProcessor

High-performance image processing library with GPU acceleration support.

## Directory Map

\```
include/
├── imgproc/          # Public API headers
│   ├── core/         # Core image types and operations
│   ├── filters/      # Image filter algorithms
│   ├── io/           # Image file I/O (PNG, JPEG, WebP)
│   └── gpu/          # GPU-accelerated operations (optional)
src/
├── core/             # Core implementation
├── filters/          # Filter implementations
├── io/               # I/O implementations
└── gpu/              # GPU backend (CUDA/OpenCL)
tests/
├── unit/             # Unit tests (Google Test)
└── benchmark/        # Performance benchmarks (Google Benchmark)
third_party/          # Vendored or FetchContent deps
docs/
├── adr/              # Architecture Decision Records
└── api/              # API reference (Doxygen output)
\```

## Quick Navigation

| Area | Entry Point | Purpose |
|------|-------------|---------|
| Core | `include/imgproc/core/INDEX.md` | Image types, pixel ops |
| Filters | `include/imgproc/filters/INDEX.md` | Blur, sharpen, edge detect |
| I/O | `include/imgproc/io/INDEX.md` | File format read/write |
| GPU | `include/imgproc/gpu/INDEX.md` | CUDA/OpenCL acceleration |

## Build & Test

| Command | Purpose |
|---------|---------|
| `cmake -B build -DCMAKE_BUILD_TYPE=Release` | Configure |
| `cmake --build build -j$(nproc)` | Build |
| `ctest --test-dir build --output-on-failure` | Run tests |
| `cmake --build build --target benchmark` | Run benchmarks |

## Conventions

- **Headers**: `snake_case.h` in `include/imgproc/[module]/`
- **Sources**: `snake_case.cpp` in `src/[module]/`
- **Naming**: `snake_case` functions, `PascalCase` classes
- **Include guards**: `#pragma once`
- **Tests**: mirrored in `tests/unit/[module]/`
- **Max file size**: 300 lines (headers), 500 lines (implementation)

## Architectural Constraints

- Public API headers in `include/` MUST NOT include internal headers from `src/`
- GPU module is optional; core/filters/io must work without it
- No exceptions in public API (use Result<T, Error> pattern)
- All I/O operations go through `imgproc::io` namespace

## Cross-Cutting Patterns

### Error Handling
- Public API: return `Result<T, Error>` (no exceptions across ABI boundary)
- Internal: exceptions allowed within a module, caught at module boundary
- Error types defined in `include/imgproc/core/error.h`

### Memory Management
- Public API: accept `const&` for input, return by value (move semantics)
- Internal: use `std::unique_ptr` for owned heap objects
- No raw `new`/`delete` in application code

### Thread Safety
- `core/` and `filters/`: stateless functions, inherently thread-safe
- `io/`: NOT thread-safe (file handles); callers must synchronize
- `gpu/`: thread-safe per GPU context; do not share contexts across threads

## AI Agent Instructions

- **Tier A** (this file + all `INDEX.md` + file headers): update atomically with code changes.
- **Tier B** (`docs/`, `README.md`): do NOT update during active development; sync at iteration end.
- When adding/removing files: update the parent module's `INDEX.md`.
- When changing public API: update `INDEX.md` Public API table + Interface Contract.
- When adding a caller: update the callee module's `INDEX.md` Dependents list.
```

### Header-only library (MSBuild / VS, flat layout)

A concrete example for a header-only C++ library with flat directory structure:

```markdown
# Krabs

Header-only C++11 library wrapping Windows ETW for simplified event tracing.

## Directory Map

\```
krabs.hpp              # Entry header — includes all library headers, links libs
krabs/                 # Library headers (flat with logical groups)
├── [core]             # Trace lifecycle, provider registration, ETW API
│   ├── trace.hpp, provider.hpp, etw.hpp, client.hpp, trace_context.hpp
├── [schema+parsing]   # Event metadata and property extraction
│   ├── schema.hpp, schema_locator.hpp, parser.hpp, property.hpp
│   ├── parse_types.hpp, size_provider.hpp, tdh_helpers.hpp
├── [support]          # GUID, errors, kernel definitions, utilities
│   ├── guid.hpp, errors.hpp, kernel_guids.hpp, kernel_providers.hpp
│   ├── collection_view.hpp, perfinfo_groupmask.hpp, version_helpers.hpp
│   ├── wstring_convert.hpp, compiler_check.hpp, ut.hpp, kt.hpp
├── filtering/         # Predicate-based event filtering
└── testing/           # Test helpers: synthetic records, mock proxies
\```

## Quick Navigation

| Area | Entry Point | Purpose |
|------|-------------|---------|
| Core | `krabs/INDEX.md` (Core section) | Trace session and provider management |
| Parsing | `krabs/INDEX.md` (Parsing section) | Event schema and property extraction |
| Filtering | `krabs/filtering/INDEX.md` | Predicate-based event filtering |
| Testing | `krabs/testing/INDEX.md` | Synthetic records and mock traces |

## Build & Test

| Command | Purpose |
|---------|---------|
| N/A (header-only) | No build step — `#include "krabs.hpp"` and link `advapi32.lib ole32.lib` |
| `msbuild krabs.sln /p:Configuration=Release /p:Platform=x64` | Build tests + examples |

Note: Header-only library. Consumer includes `krabs.hpp`; test projects live in sibling directories (`../tests/`).

## Conventions

- **Headers**: `snake_case.hpp`
- **Naming**: `snake_case` functions, `PascalCase` classes, `krabs::` namespace
- **Include guards**: `#pragma once`
- **Preprocessor**: `UNICODE` required, `NDEBUG` for release
- **Comment style**: XML-doc `<summary>` (existing project convention)

## Architectural Constraints

- Header-only: no .cpp files — all code in .hpp headers
- MSVC 2015+ required (`_MSC_VER >= 1900`)
- `filtering/` and `testing/` depend on root `krabs/` headers (never reverse)
- Windows-only: depends on ETW APIs (evntrace.h, evntcons.h, tdh.h)

## Cross-Cutting Patterns

### Error Handling
- Custom exception hierarchy in `errors.hpp`
- `error_check_common_conditions()` for ETW API error translation

### Memory Management
- RAII for ETW trace handles
- `std::deque` for provider/callback storage; no raw new/delete

### Thread Safety
- trace<T>: NOT thread-safe (one session per thread)
- Schema cache: per-trace context, no cross-thread sharing

## AI Agent Instructions

- **Tier A** (this file + all `INDEX.md`): update atomically with code changes.
- **Tier B** (`README.md`): do NOT update during active development.
- This is a header-only library — no L2 header modifications unless you own the code.
- When adding/removing headers: update `krabs/INDEX.md` and `krabs.hpp` include list.
- Use section headers in `INDEX.md` to organize the flat directory by logical group.
```
