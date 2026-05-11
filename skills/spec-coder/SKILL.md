---
name: spec-coder
description: >-
  Structured spec-first development workflow with multi-role expert review gates:
  clarify requirements, author spec documents (requirements/design/tasks),
  generate code from spec, verify with real tests, and iterate while keeping
  spec and code in sync. Use when user wants to build a feature or system with
  a spec-first approach, mentions "spec coding", "spec-driven development",
  or asks to write specs before coding.
---

# Spec Coding Workflow

Write specs first, then generate code. 5 phases, each producing artifacts that feed the next. Expert review gates between phases catch issues early.

## Session Start

On every new session:

1. **Read `specs/status.md`** to identify current phase, active changes, and deferred items.
2. **Read phase-relevant spec files** — see Quick Reference table below for which artifacts each phase produces/consumes.
3. **Confirm with the user** which phase/gate to continue from. If mid-phase, summarize progress so far.
4. **No `specs/status.md`?** This is a new project — start from Phase 0 (existing codebase) or Phase 1 (greenfield).

## Workflow Overview

```
Phase 0 ──→ Phase 1 ──→ ║Gate 1║ ──→ Phase 2a ──→ Phase 2b ──→ ║Gate 2║
(scan)      (clarify)    (req.)       (design)      (preview)     (design)
                                                                     │
    ┌────────────────────────────────────────────────────────────────┘
    ▼
Phase 2c ──→ Phase 2d ──→ ║Gate 3║ ──→ Phase 3 ──→ ║Gate 4║ ──→ Phase 4 ──→ Phase 5
(tasks)      (specs)       (plan)       (code)       (code)       (verify)    (iterate)
                                                                                  │
                                                                    ┌─────────────┘
                                                                    ▼
                                                              Re-trigger Gate
                                                              2 / 3 / 4 based
                                                              on change scope
```

Gates auto-approve when no Critical/Major issues. See [Expert Review Protocol](references/expert-review-protocol.md) for details.

### Quick Reference

| Phase | Input | Output | Gate | Next |
|-------|-------|--------|------|------|
| 0. Codebase Scan | codebase files | `status.md` § Codebase Context | — | Phase 1 |
| 1. Clarify & Scope | user requirements + Phase 0 context | `requirements.md` | Gate 1 (req.) | Phase 2a |
| 2a. Technical Design | `requirements.md` | `design.md` | — | Phase 2b |
| 2b. Design Preview | `design.md` | `design-preview/` | Gate 2 (design) | Phase 2c |
| 2c. Task Breakdown | `design.md` + `requirements.md` | `tasks.md` | — | Phase 2d |
| 2d. Feature Specs | `tasks.md` + `design.md` | `spec_xxx.md` | Gate 3 (plan) | Phase 3 |
| 3. Generate | `tasks.md` + `spec_xxx.md` | code + tests | Gate 4 (code) | Phase 4 |
| 4. Verify | code + tests + `spec_xxx.md` | test results, Implementation Map | — | Phase 5 or done |
| 5. Evolve | trunk specs + user request | `changes/` | scoped gate | → Phase 1–4 |

## When to Use

**Trigger conditions:**
- User mentions "spec coding", "spec-first", "spec-driven development"
- User asks to write specs / requirements / design docs before implementation
- User mentions phase keywords: "clarify requirements", "write a spec", "generate from spec"

**When NOT to use:** Pure bug fixes, one-line config changes, dependency updates, or tasks completable in < 15 minutes without design decisions.

**Complexity triage — choose the right track:**

| Track | When | Phases | Artifacts | Review Depth |
|-------|------|--------|-----------|-------------|
| **Small** | Single endpoint, field addition, < 1 hr | Spec (lite) → Generate → Verify | `spec_xxx.md` only | Lite (1–2 roles, skip if trivial) |
| **Medium** | Single feature, 1–4 hrs, 1–3 modules | Clarify (brief) → Spec → Generate → Verify | `spec_xxx.md` + `tasks.md` | Standard (2–3 roles) |
| **Large** | Multi-module, > 4 hrs, or new system | Full 5-phase workflow | All spec files | Full (all roles) |

Ask the user which track fits, or infer from the scope of their request.

**Small track shortcut:**
Skip Phase 1. Write a single `spec_xxx.md` (Interface + Business Rules + Test Points only), then go straight to Generate → Verify.

**Medium track shortcut:**
Phase 1 is a brief bullet-point confirmation (no full `requirements.md`). Phase 2 produces `tasks.md` + `spec_xxx.md` only (skip `design.md` and `design-preview/` unless architecture decisions are needed).

**Mid-project entry:**
If the user already has spec files or an existing codebase, read them first. Validate existing artifacts against the expected format, then confirm which phase to start from.

## File Organization

Two-layer structure: **trunk** (current system truth) + **changes** (incremental work).

```
specs/
├── index.md                    ← navigation hub: all features & recent changes
├── requirements.md             ← project-level requirements (grows incrementally)
├── design.md                   ← system-level architecture (grows incrementally)
├── design-preview/
├── tasks.md                    ← active tasks only
├── status.md
├── spec_<feature_name>.md      ← feature specs (current truth, one per feature)
└── changes/                    ← all incremental work
    ├── FEAT-NNN-name/          ← new feature (full spec lifecycle)
    │   ├── spec.md
    │   ├── design.md
    │   ├── tasks.md
    │   └── delta.md            ← merge instructions for trunk
    ├── CHG-NNN-name/           ← change/enhancement (delta only)
    │   ├── spec.md             ← ADDED / MODIFIED / REMOVED sections
    │   ├── tasks.md
    │   └── delta.md
    └── archive/                ← completed & merged changes
```

**First-time projects:** Start with trunk only (no `changes/` needed). The changes layer is introduced when the first post-v1 feature or modification begins.

For full lifecycle management details, see [Spec Lifecycle Management](references/spec-lifecycle.md).

## Phase 0 (Optional): Codebase Scan

For existing codebases, run before Phase 1: read dependency files to detect tech stack, list directory tree, identify existing interfaces/models/conventions, and summarize findings.

**Output:** Write results to `specs/status.md` under `## Codebase Context` (tech stack, key conventions, existing interfaces, directory structure summary). This persists the scan across sessions. Phase 1 references this for requirements scoping; Phase 2a references it for architecture decisions.

## Phase 1: Clarify & Scope

**Goal:** Turn informal requirements into a confirmed, structured `requirements.md`.

**Constraints:** Do NOT write any code. Only ask questions and produce documents.

1. **Interactive Clarification** — Ask user for raw requirements. Summarize goals (3–5 bullets), list ambiguities with options, suggest unconsidered constraints. Iterate until confirmed.
2. **Structured Requirements** — Produce `specs/requirements.md` (see [template](references/templates.md#requirementsmd-template)): Background & Objectives, User Roles & Use Cases, Functional Requirements (FR-001...), Non-Functional Requirements, Out of Scope. If Phase 0 ran, populate the "Existing Architecture" section with requirement-relevant context from `status.md` § Codebase Context.

### → Gate 1: Requirements Review

Per [Expert Review Protocol — Gate 1](references/expert-review-protocol.md#gate-1-requirements-review-after-phase-1). **Exit:** User approves (or auto-approved).

## Phase 2: Spec

**Goal:** Produce spec documents that directly drive code generation.

### 2a: Technical Design → `specs/design.md`

Based on `requirements.md`, produce `specs/design.md` (see [template](references/templates.md#designmd-template)):
1. Architecture overview (tech stack, layers, services)
2. Core module breakdown with responsibilities and dependency directions
3. Key data models, interfaces & interaction flows
4. Cross-cutting concerns (error handling, auth, observability, deployment) — skip on Small track
5. NFR fulfillment matrix + key architecture decisions (ADR format) — skip on Small/Medium track

For existing codebases: populate "Existing Architecture" section with architecture-relevant context from `status.md` § Codebase Context (what's new vs. modified).

### 2b: Design Preview → `specs/design-preview/`

Self-contained HTML prototype visualizing architecture, module layout, UI screens or API flows, and data models.

**Constraints:**
- Single HTML file per page/screen (inline CSS + JS, no external dependencies) — must open in any browser without a build step.
- Target: validate information architecture and user flow, not pixel-perfect design. Lo-fi is acceptable.
- Limit to ≤ 5 key screens/pages. Prioritize primary user workflow.
- For non-UI projects: Architecture Diagram Preview only (module relationships + data flow as a single HTML page).

**UI projects:** All generated UI must follow the [UI Design Guidelines](references/ui-design-guidelines.md) to avoid AI-template aesthetics.

### → Gate 2: Design Review (2a + 2b combined)

Per [Expert Review Protocol — Gate 2](references/expert-review-protocol.md#gate-2-design-review-after-phase-2a--2b-combined). **Exit:** User approves (or auto-approved).

### 2c: Task Breakdown → `specs/tasks.md`

Task table (see [template](references/templates.md#tasksmd-template)). Target granularity: 30–90 min per task.

### 2d: Feature Spec → `specs/spec_<feature>.md`

Per feature (see [template](references/templates.md#spec_xxxmd-template)): Feature Description & Use Cases, Interface Definition, Data Model, Business Rules & Edge Cases, Test Points (≥ 5 per feature, complex: 10–20; categories: Normal / Error / Boundary / Combination).

### → Gate 3: Implementation Plan Review (2c + 2d combined)

Per [Expert Review Protocol — Gate 3](references/expert-review-protocol.md#gate-3-implementation-plan-review-after-phase-2c--2d-combined). **Exit:** User approves (or auto-approved).

### Spec Quality Checklist

Before leaving Phase 2: every interface has explicit I/O types; every business rule has ≥ 1 test point; specs describe **what** not **how**; each spec is self-contained for code generation; edge cases are explicit, not implied.

## Phase 3: Generate

**Goal:** Produce implementation code + tests strictly based on the spec.

**Spec adherence — tiered rules:**

| Tier | Scope | Rule |
|------|-------|------|
| **Strict** | Interfaces, data models, business rules | Follow spec exactly. Do not change signatures, field names, or behavior. |
| **Flexible** | Internal implementation (function names, code organization, logging, error messages) | AI decides, but must note deviations in Human-review points. |
| **SPEC-GAP** | Scenarios the spec doesn't cover (discovered during coding) | Implement a reasonable solution, tag it `[SPEC-GAP]`, and continue. Collect all gaps for batch review in Phase 4. |

Never silently deviate from Strict-tier items. If a Strict item is wrong or incomplete, flag it and ask the user — but do not block on every minor gap.

### Execution Strategy

1. **Order:** Sort tasks by dependency graph (topological order). Infrastructure/setup tasks first.
2. **Parallelism:** Tasks with no mutual dependencies may be executed in parallel (e.g., via subagents). Tasks sharing the same module should be sequential to avoid merge conflicts.
3. **Commit cadence:** One commit per task, tagged with task ID: `feat(TASK-001): ...`
4. **Failure handling:** If a task fails to generate or test correctly after 2 attempts, mark it `Blocked` in `tasks.md`, log the reason, and continue with non-dependent tasks. Return to blocked tasks after unblocked tasks complete.
5. **Progress tracking:** Update `tasks.md` Status column (`Pending` → `In Progress` → `Done` / `Blocked`) as each task progresses.

### Steps

1. Scan project structure and tech stack (or use Phase 0 results).
2. For each task in `tasks.md` (per execution strategy above), take its linked `spec_xxx.md` as input.
3. Output per task:
   - File list (create vs. modify, with paths)
   - Implementation code
   - Tests derived from spec Test Points (TP-001 → test function)
   - Human-review points — Flexible-tier deviations + all `[SPEC-GAP]` items
4. Add spec traceability comments at module/class level: `// SPEC: spec_auth.md | TASK-002` — enables reverse lookup from code to spec.

For existing codebases: clearly distinguish "new file" vs. "modify existing file" and show diffs for modifications.

### → Gate 4: Code Review

Per [Expert Review Protocol — Gate 4](references/expert-review-protocol.md#gate-4-code-review-after-phase-3). **Exit:** User approves (or auto-approved). Proceed to Phase 4.

## Phase 4: Verify

**Goal:** Confirm generated code satisfies the spec through execution (static compliance is already covered by Gate 4).

### 4a: Dynamic Verification

Run the following checks in order. Stop and fix if any step fails.

1. **Build** — Project compiles / bundles without errors.
2. **Lint & Type Check** — Run linter and type checker (if available). Zero errors required; warnings acceptable.
3. **Unit Tests** — Execute test suite (`pytest`, `npm test`, `go test`, etc.). Map each TP-ID to pass/fail.
4. **Integration Tests** — Run integration / E2E tests if defined in `tasks.md`.
5. **Coverage Check** — Report test coverage. Flag spec Test Points that have no corresponding test execution.
6. **NFR Verification** — If `requirements.md` defines measurable NFRs (response time, throughput), run benchmarks and compare. Log results even if not blocking.
7. **Manual Test Checklist** — For tasks marked `AI-Auto: No` in `tasks.md`, generate a manual test checklist with steps and expected results for the user to execute.

### 4b: SPEC-GAP Resolution

For each `[SPEC-GAP]` from Phase 3: **Accept** (update spec) / **Reject** (fix code) / **Defer** (add to backlog).

### 4c: Implementation Map Update

After all tests pass, update the `## Implementation Map` section in each `spec_xxx.md` with the actual code file paths and function/class names. This enables reverse lookup from spec to code.

### Output & Transitions

- **Passed** — items satisfying the spec; **Failed** — items deviating (recommend: fix spec or fix code)
- All passed → Phase 5 or next task. Failed → fix in Phase 2 or 3 → re-verify.

**Exit condition:** All items pass, or user acknowledges remaining gaps.

**Workflow completion (initial build):** If this is the initial build and no further changes are planned, update `status.md`: mark all phases complete, remove the Initial Build Progress table, and present a summary to the user (features built, test pass rate, deferred items count).

## Phase 5: Evolve — New Features & Changes

**Goal:** Add new capabilities or modify existing ones while keeping all specs in sync.

**Key rule:** Always update the spec BEFORE updating the code. Every change goes through `specs/changes/`.

### Step 1: Classify the Work

| Type | Criteria | Action |
|------|----------|--------|
| **New Feature** | Independent business value, new interfaces/models | Create `specs/changes/FEAT-NNN-name/`, run full Phase 1–4 within it |
| **Change / Enhancement** | Modifies existing feature behavior | Create `specs/changes/CHG-NNN-name/`, write delta spec, run Phase 2d–4 |
| **Trivial Fix** | Single spec file, single section, no interface/model change | Update trunk spec directly with changelog entry, skip change dir |

### Step 2: Overlap Check

Before creating the change directory, run [Overlap Check](references/spec-lifecycle.md#overlap-check) against all In-Progress changes listed in `specs/index.md`. If overlapping Target Specs are found, warn the user and agree on a resolution strategy before proceeding.

### Step 3: Work Within the Change Directory

For Features: run the full workflow (Phase 1–4) inside `specs/changes/FEAT-NNN/`.
For Changes: write a delta-format `spec.md` (ADDED / MODIFIED / REMOVED), then run Phase 2d–4.
For Changes that add/remove screens, modify navigation structure, or alter primary interaction patterns (e.g., forms → tables): also run Phase 2b to update `design-preview/`.

**Path rule:** All Phase 1–4 outputs go into the change directory, not the trunk. For example, Phase 2a produces `specs/changes/FEAT-NNN/design.md`, not `specs/design.md`. The trunk is only updated during Step 4 (Merge to Trunk).

**Nesting rule:** Changes are always flat — never create a change inside another change directory. If FEAT-NNN's implementation reveals the need for an additional feature, create a sibling `FEAT-NNN+1` at the top level (`specs/changes/FEAT-NNN+1-name/`) and add a dependency note in both `tasks.md` files.

Apply the same review gates as the main workflow, scoped to the change:
- Interface/architecture change → Gate 2 | Business rule change → Gate 3 | Implementation-only → Gate 4

### Step 4: Cross-Feature Impact Analysis

Before generating code, analyze impact across ALL trunk specs:
- **Direct:** Specs explicitly modified by this change.
- **Indirect:** Specs that depend on modified interfaces or data models.
- **Test:** Test points in other specs that may need updating.

Present impact analysis to the user for confirmation.

### Step 5: Merge to Trunk

After code is verified (Phase 4 passed):
1. **(Features only)** Copy `changes/FEAT-NNN/spec.md` to `specs/spec_<feature>.md`.
2. Generate `delta.md` — merge instructions listing every trunk file/section to update.
3. Apply delta to trunk specs (`specs/*.md`): insert ADDED content, replace MODIFIED sections, remove REMOVED items.
4. Add changelog entries to every modified trunk file.
5. Update `specs/index.md` with the change reference.
6. Commit all trunk updates atomically: `spec: merge FEAT/CHG-NNN to trunk`.
7. Move change directory to `specs/changes/archive/`.

For full lifecycle details, merge rules, and scaling guidance, see [Spec Lifecycle Management](references/spec-lifecycle.md).

## Cross-Phase Guidelines

- **No phase skipping:** Do not generate code without a confirmed spec. Ask user for confirmation before advancing phases.
- **Spec-code traceability:** Every code change traces to a spec item (TASK-ID + TP-ID); every spec item has corresponding code and tests.
- **Status tracking:** Maintain `specs/status.md` (see [template](references/templates-lifecycle.md#statusmd-template)). Update at each phase end with current phase, gate results, and deferred item counts. On session start, read `specs/status.md` first to restore context.
- **Context management:** Keep each spec file under ~300 lines. In Phase 3, feed only the relevant `spec_xxx.md` + related `design.md` sections — not all spec files at once.
- **Expert review:** All review gates follow the [Expert Review Protocol](references/expert-review-protocol.md). Key points: auto-approve when no Critical/Major issues; max 3 rounds per gate; track prior issues across rounds; deferred items logged in spec files. Users can set review preferences in `specs/status.md`.
- **UI de-AI aesthetic:** All user-facing UI must follow the [UI Design Guidelines](references/ui-design-guidelines.md) to avoid AI-template aesthetics. Gate 2 and Gate 4 reviewers check UI against the de-AI checklist.

## Error Recovery

| Scenario | Recovery Action |
|----------|----------------|
| **Phase 3: Task fails after 2 attempts** | Mark task `Blocked` in `tasks.md`, log root cause, continue with non-dependent tasks. After all other tasks complete, revisit blocked tasks — may require spec revision (back to Phase 2d). |
| **Phase 4: Tests fail** | Categorize: spec bug (fix spec then re-generate) vs. code bug (fix code, re-run tests). Do not loop more than 3 fix-verify cycles per task — escalate to user. |
| **Phase 4: Test environment unavailable** | Generate manual test checklist, document expected setup, and mark verification as `Pending-Env` in `status.md`. Proceed with remaining phases that don't require the environment. |
| **SPEC-GAP: Cannot decide autonomously** | Tag as `[SPEC-GAP-BLOCKED]`, implement a safe no-op or error response as placeholder, and batch all blocked gaps for user decision before Phase 4 verification. |
| **Phase 5: Delta merge conflict** | Follow conflict handling in [spec-lifecycle.md](references/spec-lifecycle.md#conflict-handling). Never force-overwrite trunk — always present both versions to the user. |
| **Cross-session context loss** | Read `specs/status.md` + last completed artifacts (see Session Start). If status.md is missing or stale, scan `specs/` directory structure and `tasks.md` status to reconstruct state. |
| **Phase 1: Requirements deadlock** | If the user cannot decide after 3 clarification rounds, present a default recommendation with rationale. Ask for explicit approval or override. Do not loop indefinitely. |
| **Phase 2: Design deadlock** | If two design options are equally viable, document both in ADR format (pros/cons/consequences), provide a recommended option, and ask the user to decide. Limit to 2 discussion rounds, then adopt the recommendation if no response. |

## Templates

For spec file templates, see [templates.md](references/templates.md) (core) and [templates-lifecycle.md](references/templates-lifecycle.md) (lifecycle & review).
