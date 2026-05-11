# Spec Lifecycle Management

How to manage specs as a project evolves — new features, changes to existing features, and long-term maintenance.

## Core Principle: Trunk + Changes

```
specs/                          ← "trunk": always reflects CURRENT system truth
├── index.md                    ← navigation hub
├── requirements.md, design.md  ← project-level docs (grow incrementally)
├── spec_xxx.md                 ← feature specs (current truth)
└── changes/                    ← all incremental work
    ├── FEAT-NNN-name/          ← new feature (full spec lifecycle)
    ├── CHG-NNN-name/           ← change/enhancement (delta only)
    └── archive/                ← completed & merged changes
```

**`specs/`** = "what the system IS right now." Read only trunk to understand the full current state.

**`specs/changes/<id>/`** = "what we're building or built." Each change has its own spec lifecycle. After completion, content is folded into trunk.

## Change ID Assignment

| Source | Format | Example |
|--------|--------|---------|
| External tracker (preferred) | Use tracker ID directly | `FEAT-JIRA-1234-rate-limit`, `CHG-GH-567-fix-retry` |
| No tracker | Sequential from `index.md` — take max ID + 1 | `FEAT-004-rate-limit`, `CHG-005-fix-retry` |

When creating a change, check `specs/index.md` (In-Progress + Recent Completions) to avoid ID collisions.

## Change Units: Feature vs Change

| Type | ID Prefix | When | Required Docs | Trunk Impact |
|------|-----------|------|---------------|-------------|
| **Feature** | `FEAT-` | New capability with independent business value | `spec.md` + `design.md` + `tasks.md` | New `spec_xxx.md` + updates to `requirements.md` and `design.md` |
| **Change** | `CHG-` | Modification, enhancement, or bugfix to existing feature | `spec.md` (delta-only) + `tasks.md` | Updates to existing trunk specs |
| **Trivial Fix** | (none) | Single spec file, single section, no interface/model change | (none) | Direct trunk edit with changelog entry |

## Change Directory Structure

### Feature (`FEAT-NNN/`)

```
specs/changes/FEAT-NNN-name/
├── spec.md              ← requirements for THIS feature (same format as spec_xxx.md)
├── design.md            ← technical design for THIS feature
├── design-preview/      ← optional: HTML mockup (if UI-related)
├── tasks.md             ← task breakdown
└── delta.md             ← merge instructions (generated after Phase 4)
```

Full Phase 1–4 workflow applies within this directory. All outputs go here, NOT into trunk.

### Change/Enhancement (`CHG-NNN/`)

```
specs/changes/CHG-NNN-name/
├── spec.md              ← delta-only: ADDED / MODIFIED / REMOVED
├── tasks.md             ← task breakdown (often 1–3 tasks)
└── delta.md             ← merge instructions (generated after Phase 4)
```

### Change spec.md — Delta Format

See [Change Spec Template](templates-lifecycle.md#change-spec-template-for-chg-nnn--delta-format) for the full template. Key sections: Status, Target Specs, Track, Background, Delta (MODIFIED / ADDED / REMOVED), and Impact Analysis.

## delta.md — Generation Rules

delta.md is the "patch" that maps change spec content to exact trunk locations.

### When to Generate

AI generates delta.md **after Phase 4 passes** (code verified). Never before — the change may still evolve during implementation.

### How to Generate

1. **Read** the change's `spec.md` (and `design.md` for Features).
2. **Read** the current trunk specs that are listed in `Target Specs`.
3. **Diff** — for each ADDED/MODIFIED/REMOVED item in the change spec, produce a merge instruction: target file, target section, operation (ADD/REPLACE/REMOVE), and exact content.
4. **Conflict check** — scan trunk spec changelogs for entries added since this change was created. If another change modified the same section, flag it as a conflict for manual resolution.

### delta.md Format

See [delta.md template](templates-lifecycle.md#deltamd-template) for the full format. Key fields per instruction:

| Field | Description |
|-------|-------------|
| File | Trunk spec file path |
| Section | Target section (use `→` for nested: `Business Rules → Rule 3`) |
| Operation | `CREATE` / `ADD (after X)` / `REPLACE` / `REMOVE` |
| Content | Exact text to insert or replace with |

### Conflict Handling

If the conflict check finds overlapping changes:
1. List all conflicts with both versions (trunk current vs. change proposed).
2. Present to user for manual resolution.
3. User picks one version or writes a merged version.
4. Update delta.md with the resolved content before proceeding.

## Overlap Check

Before creating a new change directory, check all In-Progress changes (listed in `specs/index.md`):

1. Compare the new change's Target Specs against every In-Progress change's Target Specs.
2. If any overlap (same spec file + same section), **warn the user**: list conflicting changes and affected sections.
3. User decides: serialize (finish one first), coordinate (split non-overlapping sections), or accept risk (proceed in parallel, resolve conflicts at merge).

This catches conflicts early — far cheaper than discovering them at delta merge time.

## Nesting Constraint

Changes are always **flat** — all change directories live directly under `specs/changes/`. Never nest a change inside another change directory. If FEAT-NNN's implementation reveals the need for a sub-feature, create `FEAT-NNN+1` as a sibling with a dependency note.

## Lifecycle Flows

### New Feature

```
Create FEAT-NNN/ → Phase 1–4 (in change dir) → Verify → Generate delta.md → Merge to trunk → Archive
```

### Change/Enhancement

```
Create CHG-NNN/ → Write delta spec.md → Phase 2d–4 → Verify → Generate delta.md → Merge to trunk → Archive
```

### Merge-to-Trunk Rules

1. **Timing:** Only after Phase 4 passes. Never merge spec before code is verified.
2. **Conflict check:** Always run before applying delta (see above).
3. **File creation (Features only):** Copy `changes/FEAT-NNN/spec.md` to `specs/spec_<feature>.md`. This is the only time a new trunk-level spec file is created.
4. **Changelog:** Every modified trunk file gets: `| YYYY-MM-DD | [description] | FEAT/CHG-NNN |`
5. **Atomic:** All trunk updates from one change in a single commit: `spec: merge FEAT/CHG-NNN to trunk`.
6. **Index update:** Move change from "In-Progress" to "Recent Completions" in `specs/index.md`.
7. **Archive:** Move change directory to `specs/changes/archive/`.

## Feature Status Lifecycle

| Status | Where | Meaning |
|--------|-------|---------|
| **Draft** | change dir | Being written, not yet reviewed |
| **In Review** | change dir | Going through review gates |
| **In Progress** | change dir | Being implemented |
| **Complete** | change dir | Code verified, ready to merge |
| **Archived** | archive/ | Merged to trunk, kept for history |
| **Active** | trunk | Reflects current system behavior |
| **Deprecated** | trunk | Feature being phased out |

## Cross-Feature Impact Analysis

When a change affects multiple features, delta.md must list ALL affected trunk specs:

1. **Direct:** Specs explicitly modified by this change.
2. **Indirect:** Specs depending on modified interfaces/data models (check `design.md` dependency graph).
3. **Test:** Test points in other specs that may need updating.

Present impact analysis to user before generating delta.md.

## Scaling

As the project accumulates features:

### When to Split Trunk Specs

| File | Split Trigger | How to Split |
|------|--------------|-------------|
| `design.md` | > 300 lines OR > 5 modules | Split into `design_<domain>.md` per domain. Keep `design.md` as overview (tech stack + module index + cross-cutting concerns only). |
| `requirements.md` | > 200 lines OR > 3 modules | Split into `requirements_<module>.md`. Keep `requirements.md` as overview (objectives + NFRs + out-of-scope only). |
| `spec_xxx.md` | > 300 lines | Split by sub-feature: `spec_auth_login.md`, `spec_auth_rbac.md`. Update `tasks.md` references. |
| `index.md` | > 50 Recent Completions | Archive old completions to `index_archive.md`, keep only last 20 in main index. |

### Maintenance

- **Archive aggressively:** Move completed changes to `archive/` immediately after merge.
- **Periodic audit:** Every 5–10 changes, review trunk specs: clean up `[DEPRECATED]` items, verify changelog accuracy, confirm `index.md` is current.
- **Stale detection:** If a trunk spec hasn't been updated in 6+ months but the code has changed, flag it for review.

### Deprecation Flow

When a feature is retired or replaced:

1. **Mark deprecated:** Add `[DEPRECATED: YYYY-MM-DD, reason]` tag to the feature's `spec_xxx.md` header and all related sections in `requirements.md` / `design.md`.
2. **Update index.md:** Move the feature from "Active Features" to a "Deprecated Features" section (or add an inline `⚠️ Deprecated` marker).
3. **Grace period (default 3 months):** Keep deprecated items in trunk for reference. Code may still reference them during migration.
4. **Cleanup:** After the grace period, remove deprecated sections from trunk specs. Archive the `spec_xxx.md` to `specs/archive/` (not `changes/archive/`). Remove corresponding entries from `requirements.md`, `design.md`, and `index.md`. Log the removal in each file's changelog.

### Spec Versioning

Rely on **git commits** as the versioning mechanism for specs:

- **Merge-to-Trunk commits:** Always use the format `spec: merge FEAT/CHG-NNN to trunk` so commits are searchable.
- **Git tags (optional):** For milestone releases, tag the commit: `git tag spec-v1.0` or `git tag spec-after-FEAT-004`.
- **Reconstructing past state:** To see what the spec looked like when a specific change was built, find the merge commit for that change ID in git log, then checkout that commit.
- **Archive as snapshot:** The `specs/changes/archive/` directory preserves the change's own spec files at the time of completion, providing a partial snapshot without needing git history.
