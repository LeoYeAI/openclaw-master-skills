# Reference Draft — Semantic Search Diagnostics

Status: draft-for-skill
Role: backend-aware diagnostic reference for semantic-search trust and failure analysis

## Scope

Use this reference when a workspace has:
- semantic-search results that feel inconsistent or misleading
- disagreement between host-side inspection and runtime-facing query behavior
- possible config/cache/index path mismatch
- pending indexing or embedding gaps
- different retrieval quality across different query classes

This reference is especially relevant when the workspace uses qmd or a similar semantic-search runtime with separate config, cache, index, embedding, and reranking layers.

## Non-goals

This reference does **not**:
- declare a backend globally reliable or unreliable in one jump
- replace source-of-truth layering or current-state routing
- promise backend-neutral repair automation in v1
- treat one successful query as proof of universal health

It exists to prevent fake confidence, fake pessimism, and wrong-path diagnosis.

## Purpose

Define how to diagnose semantic-search reliability problems without reducing everything to a vague statement like "search is unreliable."

This reference is backend-aware. It is especially relevant when the workspace uses qmd or a similar semantic-search runtime with separate config, cache, index, embedding, and reranking layers.

---

## Core Principle

Do not diagnose semantic search in one jump.

Separate the problem into layers:
1. baseline / observed state
2. runtime-path alignment
3. index / update / embedding state
4. query-class behavior
5. diagnostic-method limits

A useful diagnosis says **where** confidence is weak, not just that confidence is weak.

---

## Quick Start

Use this reference in six steps:
1. capture a baseline
2. verify config/cache/index path alignment
3. inspect indexing and embedding state
4. test representative query classes
5. account for diagnostic-method limits
6. write trust conclusions by query class, not as a blanket verdict

If runtime-facing evidence and host-side evidence disagree, treat path alignment as unresolved until proven otherwise.

---

## Diagnostic Layers

### 1. Baseline / observed state
Capture before-data before attempting repair.

Useful baseline data includes:
- runtime-reported index path
- inspected index path(s)
- index size
- document counts / table counts when safely available
- current runtime-reported status
- pending embedding count if available
- simple timing snapshots if safe to collect

Why:
- without baseline data, later "improvement" claims are hard to prove
- before/after comparison is often the only way to distinguish repair from coincidence

---

### 2. Runtime-path alignment
A common failure mode is split-brain diagnostics.

Typical pattern:
- config points to one runtime context
- cache/index path points somewhere else
- host-side inspection looks at a different file than runtime queries actually use

Always verify:
- config path
- cache path
- runtime-reported index path
- whether CLI checks and in-process search are actually reading the same physical index

Do not trust a semantic-runtime diagnosis until these are aligned or the mismatch is explicitly understood.

---

### 3. Index / update / embedding state
Confirm whether the problem is caused by:
- missing indexed docs
- pending embeddings / missing vectors
- partial update state
- stale runtime cache
- reranker or model-runtime fragility

Repair obvious pending gaps before drawing broad conclusions about retrieval quality.

A backend that is merely pending embeddings should not be judged as if its retrieval stack were fully healthy.

---

### 4. Query-class behavior
Do not ask only whether search "works."

Test representative query classes such as:
- system-state
- governance / rule-boundary
- weekly-review / approval-state
- user-preference / profile
- historical trace / evidence
- maintenance / upkeep

The same backend may behave well for one class and poorly for another.

A strong diagnostic pass should identify:
- which classes are strong enough for supporting recall
- which classes should remain secondary only
- which classes are still discovery/background only

---

### 5. Diagnostic-method limits
The diagnostic method itself may be incomplete.

Examples:
- host-side SQLite can inspect basic tables but not vector extensions
- broad concurrent query validation may trigger timeouts or resource kills
- CLI checks may need explicit config/cache alignment to represent the intended runtime
- provider/model layers may fail even when the base SQLite file looks healthy

A diagnosis that ignores method limits often creates fake conclusions.

---

## Trust Judgments

Avoid blanket statements like:
- "semantic search is reliable"
- "semantic search is unreliable"

Prefer scoped judgments such as:
- stronger supporting recall for system-state queries
- secondary only for profile/preference queries
- discovery-only for historical trace
- background-only for governance questions unless aligned and validated better

Trust should be stated by:
- backend
- path alignment state
- query class
- current operational limits

---

## Practical Repair Loop

Recommended loop:
1. baseline
2. path alignment
3. update/index/embedding check
4. repair obvious pending gaps
5. validate representative queries in serial or small batches
6. write backend trust as query-class policy

Do not skip from baseline straight to global trust claims.

---

## Validation Rules

A semantic-search diagnostic pass is good enough when:
- the runtime-facing and host-side evidence relationship is explicit
- path alignment is either confirmed or clearly identified as unresolved
- obvious pending embedding/index gaps are accounted for
- at least a few representative query classes were tested
- the final judgment is scoped instead of global

Use serial or small-batch validation first.
Do not over-interpret failures from broad concurrent tests that exceed the diagnostic method's safe operating range.

---

## Precedence and Conflict Handling

This reference governs how to diagnose semantic-search trust, not how to replace source-of-truth policy.

Conflict order:
1. explicit local safety and current-state routing rules
2. source-of-truth layering and bridge/current-state policy
3. this reference as backend-diagnostic guidance

Even when semantic search improves, it should not automatically outrank fresher live source-of-truth documents.

---

## Minimal Examples

### Example 1 — Split-brain path mismatch
Situation:
- host-side inspection reads an agent-local index
- runtime CLI reports a different cache index path

Decision:
- classify the issue as unresolved path alignment
- do not compare quality results as if they came from the same physical index
- fix or declare alignment before making trust judgments

### Example 2 — Pending embeddings
Situation:
- runtime status shows pending embeddings
- retrieval quality looks mixed

Decision:
- treat embedding state as an active confounder
- repair obvious pending gaps first
- avoid broad quality conclusions until the backend is no longer partially pending

### Example 3 — Query-class split
Situation:
- system-state queries improve materially after alignment
- user-preference queries still rank noisy results

Decision:
- record stronger trust for system-state supporting recall
- keep user-preference as secondary/background only
- do not compress both classes into one backend verdict

### Example 4 — Host-side observability limit
Situation:
- SQLite inspection can read relational tables but fails on vector-module introspection

Decision:
- treat host-side inspection as partial evidence
- do not use host inspection alone to prove end-to-end runtime health or corruption
- combine it with runtime-facing status and query checks

---

## v1 Boundary

This reference explains how to diagnose and scope semantic-search trust.
It does not promise full backend-neutral automation in v1.

Use it to avoid fake confidence, fake pessimism, and wrong-path diagnostics.
