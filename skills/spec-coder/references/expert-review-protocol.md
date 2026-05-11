# Expert Review Protocol

Multi-role expert review gates embedded in the spec-coding workflow. AI simulates domain experts to catch issues before the user commits to the next phase.

## Core Mechanism

### When to Run

Each phase gate triggers a review. The depth depends on the track:

| Track | Review Depth | Behavior |
|-------|-------------|----------|
| **Small** | Lite | 1–2 roles, brief bullet format. Skip entirely for trivial changes. |
| **Medium** | Standard | 2–3 roles per gate. |
| **Large** | Full | All listed roles per gate. |

### Auto-Approve Rule

If the review finds **zero Critical and zero Major** issues, present a summary and auto-approve:

> "Expert review complete — no Critical or Major issues found. [N Minor suggestions listed below.] Proceeding to next phase. Reply 'hold' to pause and address Minor items first."

This prevents review fatigue on clean artifacts. The user can still intervene.

### Review Output Format

Each expert role produces:

```markdown
### [Role Name] Review

**Strengths:** (1–3 bullets)

**Issues:**
| # | Severity | Description | Recommendation |
|---|----------|-------------|----------------|
| 1 | Critical | ... | ... |

**Suggestions:** (optional, 1–3 bullets)
```

### Severity Definitions

| Severity | Meaning | Blocks Progress? |
|----------|---------|-----------------|
| **Critical** | Fundamental flaw — missing core requirement, security hole, architectural dead-end | Yes — must resolve |
| **Major** | Significant gap — incomplete edge cases, performance risk, unclear interface | Yes — unless user explicitly defers |
| **Minor** | Polish item — naming, docs, style | No — can defer freely |

### User Response Options

After receiving the consolidated review, the user responds:

| Response | Action |
|----------|--------|
| **"Approve"** | Proceed to next phase as-is |
| **"Fix [items]"** | Address specified items, then re-review |
| **"Fix all"** | Address all issues, then re-review |
| **"Defer [items]"** | Log to Deferred Items, proceed |

### Re-Review Tracking (max 3 rounds)

When re-reviewing after fixes, include a **Prior Issues Tracker**:

```markdown
#### Prior Issues Tracker (Round 2 of 3)
| Prior # | Original Description | Status |
|---------|---------------------|--------|
| 1 | Missing auth on /admin endpoint | ✅ Resolved |
| 2 | No retry logic for payment API | ⏳ Still Open |
| — | (new) Cache invalidation race condition | 🆕 New |
```

Rules:
- **Max 3 review rounds per gate.** After round 3, force a user decision: approve with known issues, or escalate.
- Each round must explicitly track prior issues — never review from scratch.
- New issues found in later rounds are marked `🆕 New`.

### Suggested Fix Order

When a review produces multiple issues, present a **Suggested fix order** in the consolidated summary. Ordering criteria:

1. **Dependency** — if fixing issue A is required before issue B makes sense, A goes first.
2. **Severity** — Critical before Major before Minor.
3. **Blast radius** — issues affecting more modules/files go first (fixing them may resolve downstream issues).

Format: `**Suggested fix order:** #1 (Critical, blocks #3) → #3 (Major) → #2 (Minor, optional)`

### User Review Preferences

At the start of the workflow (or any time), the user can set review preferences stored in `specs/status.md` under `## Review Preferences`. Examples:

- `"Skip UX reviews"` — UX/UI Designer role is omitted from Gate 2.
- `"Focus on security"` — Security Expert role is always included, even on Small track.
- `"Auto-approve all gates"` — all gates auto-approve regardless of severity (user takes full responsibility).
- `"Only flag Critical"` — Major and Minor issues are listed but don't require user response.

If no preferences are set, use the default behavior (track-based depth, standard severity rules).

### Deferred Items Log

All deferred items are appended to the relevant spec file:

```markdown
## Deferred Review Items
| Phase | Role | Severity | Description | Status |
|-------|------|----------|-------------|--------|
| 2a | Architect | Major | Consider event-driven arch | Open |
```

---

## Phase Review Gates

Reviews are grouped into **4 gates** (not 7) to reduce fatigue. Adjacent phases with overlapping concerns are merged.

### Gate 1: Requirements Review (after Phase 1)

**Artifact:** `requirements.md`

| Role | Unique Review Questions |
|------|------------------------|
| **End User** | 1. Are there workflows I do daily that aren't captured as use cases? 2. Do the described flows match how I actually work (not how someone imagines I work)? 3. Are there error situations I encounter regularly that aren't listed? |
| **Product Expert** | 1. Is each objective measurable (has a success metric)? 2. Are FR priorities (Must/Should/Could) correctly assigned? 3. Is the out-of-scope list specific enough to prevent scope creep? |
| **Domain Expert** | 1. Are there industry regulations or compliance rules missing? 2. Are business rule edge cases (concurrent access, data conflicts) identified? 3. Are integration points with existing systems fully listed? |

---

### Gate 2: Design Review (after Phase 2a + 2b combined)

**Artifacts:** `design.md` + `design-preview/`

Review both the technical design document and its visual preview together in a single gate.

| Role | Unique Review Questions |
|------|------------------------|
| **Software Architect** | 1. Can each module be deployed/tested independently? 2. Are there circular dependencies? 3. Will this architecture support 10x the current load without redesign? 4. Are ADR trade-offs honestly stated? |
| **UX/UI Designer** | 1. Does the preview's information architecture match the module structure? 2. Are all state transitions (loading, error, empty, success) represented? 3. Is the navigation depth ≤ 3 clicks for primary workflows? 4. Does the UI pass the [de-AI checklist](ui-design-guidelines.md#quick-checklist)? |
| **Security Expert** | 1. Is there an auth check on every data-mutating endpoint? 2. Are sensitive fields (PII, tokens) identified and redaction-planned? 3. Is input validation defined at the boundary (not just internally)? |

For non-UI projects (APIs, CLIs, data pipelines): skip UX/UI Designer role; replace design-preview review with "Architecture Diagram Review" (module relationships + data flow only).

---

### Gate 3: Implementation Plan Review (after Phase 2c + 2d combined)

**Artifacts:** `tasks.md` + all `spec_xxx.md` files

Review the task breakdown and feature specs together — they are tightly coupled.

| Role | Unique Review Questions |
|------|------------------------|
| **Tech Lead** | 1. Are there tasks that should be split further (> 90 min estimate)? 2. Is the dependency graph a DAG (no cycles)? 3. Are infrastructure/setup tasks front-loaded? 4. Which tasks can be parallelized? |
| **QA Expert** | 1. Does every business rule in spec_xxx.md have ≥ 1 test point? 2. Are test points unambiguous (exact expected output, not "should work")? 3. Are integration/E2E test tasks included, not just unit tests? 4. Is there a "Combination" category for multi-condition scenarios? |
| **Senior Developer** | 1. Are interfaces in spec_xxx.md implementable with the chosen tech stack? 2. Are data model fields consistent between design.md and spec_xxx.md? 3. Are error codes and messages specific enough to debug from? |

---

### Gate 4: Code Review (after Phase 3)

**Artifacts:** Generated code + tests

| Role | Unique Review Questions |
|------|------------------------|
| **Code Reviewer** | 1. Are there functions > 50 lines that should be decomposed? 2. Is error handling consistent (no swallowed exceptions)? 3. Are naming conventions consistent with the existing codebase? 4. (UI projects) Does the generated UI follow the [UI Design Guidelines](ui-design-guidelines.md) — color palette, layout variety, icon consistency, copy tone? |
| **Security Expert** | 1. Is user input validated/sanitized before use? 2. Are SQL queries parameterized (no string concatenation)? 3. Are secrets hardcoded anywhere? 4. Are auth checks present on all protected routes? |
| **Spec Compliance Auditor** | 1. Does every Strict-tier item (interface, data model, business rule) match the spec exactly? 2. Are all `[SPEC-GAP]` items tagged and listed? 3. Is there a test function for every TP-ID in the spec? |

Note: Performance review is deferred to Phase 4 (Verify) where it can be measured with actual benchmarks, not guessed from code reading.
