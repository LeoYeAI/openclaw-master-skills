# Spec Coding — Lifecycle & Review Templates

Templates for lifecycle management (index, changes, delta, status) and expert review output. For core spec templates (requirements, design, tasks, feature spec), see [templates.md](templates.md).

---

## index.md Template

Maintained at `specs/index.md`. Single entry point for the entire spec system.

```markdown
# Spec Index: [Project Name]

## Active Features

| ID | Name | Spec File | Status | Last Updated |
|----|------|-----------|--------|-------------|
| auth | Authentication | spec_auth.md | Active | 2026-03-15 |
| payment | Payment | spec_payment.md | Active | 2026-03-10 |

## In-Progress Changes

| ID | Name | Type | Target Specs | Phase |
|----|------|------|-------------|-------|
| FEAT-004 | Rate Limiting | Feature | (new) spec_rate_limit.md | Phase 2 |
| CHG-005 | Fix payment retry | Change | spec_payment.md | Phase 3 |

## Recent Completions

| ID | Name | Type | Merged Date | Affected Specs |
|----|------|------|------------|---------------|
| CHG-003 | Auth timeout | Change | 2026-03-18 | spec_auth.md, design.md |
| FEAT-002 | Payment | Feature | 2026-03-01 | spec_payment.md, design.md |
```

---

## Change Spec Template (for CHG-NNN — delta format)

Used in `specs/changes/CHG-NNN-name/spec.md` for modifications to existing features.

```markdown
# CHG-NNN: [Short Description]

## Status: Draft | In Review | In Progress | Complete | Archived
## Target Specs: [spec_xxx.md, design.md#Section]
## Track: Small | Medium

## Background

[Why this change is needed. 1-3 sentences.]

## Delta

### MODIFIED: spec_xxx.md → [Section Name]
- [Old behavior] → [New behavior]

### ADDED: spec_xxx.md → [Section Name]
- [New item description]

### REMOVED: spec_xxx.md → [Section Name]
- [Item being removed and why]

### ADDED: spec_xxx.md → Test Points
| TP-ID | Category | Input | Expected Output | Notes |
|-------|----------|-------|-----------------|-------|
| TP-NNN | Normal | ... | ... | |

## Impact Analysis

| Affected Spec | Impact Type | Sections | Risk |
|--------------|-------------|----------|------|
| spec_xxx.md | Direct | Business Rules, Test Points | Low |
| spec_yyy.md | Indirect | Interface (depends on xxx) | Medium |
```

---

## delta.md Template

Generated when a change is complete. Provides exact merge instructions for trunk specs.

```markdown
# Delta: [FEAT/CHG-NNN] → Trunk

## Generated: YYYY-MM-DD
## Change: [Short description]

## Merge Instructions

### File: specs/spec_xxx.md
| Section | Operation | Content |
|---------|-----------|---------|
| Business Rules → Rule N | REPLACE | "[New rule text]" |
| Business Rules → Rule N+1 | ADD (after Rule N) | "[New rule text]" |
| Test Points | ADD | TP-NNN, TP-NNN (see change spec.md) |

### File: specs/design.md
| Section | Operation | Content |
|---------|-----------|---------|
| [Module] → [Subsection] | REPLACE | "[Updated design text]" |

### File: specs/spec_<feature>.md (NEW — Features only)
| Operation | Content |
|-----------|---------|
| CREATE | Copy from `changes/FEAT-NNN/spec.md`, rename to `spec_<feature>.md`, add to trunk |

### File: specs/requirements.md
| Section | Operation | Content |
|---------|-----------|---------|
| FR table → [Module] | ADD | "FR-NNN: [New requirement]" |

## Post-Merge Checklist
- [ ] All trunk spec sections updated per instructions above
- [ ] Changelog entry added to each modified trunk file
- [ ] specs/index.md updated (move from In-Progress to Recent Completions)
- [ ] Change directory moved to specs/changes/archive/
- [ ] status.md updated
```

---

## status.md Template

Maintained automatically at `specs/status.md`. Updated at the end of each phase.

```markdown
# Project Status: [Project Name]

## Trunk Health

| Metric | Value |
|--------|-------|
| Active features | 3 (spec_auth, spec_payment, spec_notifications) |
| Last trunk update | 2026-03-18 (CHG-003 merged) |
| Open deferred items | 2 (1 Major, 1 Minor) |

## Active Changes

| Change ID | Type | Track | Current Phase | Gate Status | Notes |
|-----------|------|-------|--------------|-------------|-------|
| FEAT-004-rate-limit | Feature | Large | Phase 2c | Gate 2 ✅ | |
| CHG-005-fix-retry | Change | Small | Phase 3 | Gate 3 ✅ | |

## Initial Build Progress

Use during first-time project build. Remove after initial Phase 4 passes.

| Phase | Status | Artifact | Gate |
|-------|--------|----------|------|
| 0. Scan | ✅ Done | context | — |
| 1. Clarify | ✅ Done | requirements.md | Gate 1 ✅ |
| 2a–2b. Design | ✅ Done | design.md + preview | Gate 2 ✅ |
| 2c–2d. Plan | 🔄 In Progress | tasks.md + specs | Gate 3 ⬜ |
| 3. Generate | ⬜ | code + tests | Gate 4 ⬜ |
| 4. Verify | ⬜ | test results | — |

## Codebase Context

Populated by Phase 0 (Codebase Scan). Persists scan results across sessions.

- **Tech Stack:** [e.g., TypeScript + Express.js + PostgreSQL + Redis]
- **Key Conventions:** [e.g., kebab-case file names, barrel exports, service layer pattern]
- **Existing Interfaces:** [e.g., REST API at /api/v1/*, GraphQL at /graphql]
- **Directory Structure:** [Brief tree summary of key directories]
- **Notes:** [Any other relevant observations]

## Review Preferences

[User-specified preferences, e.g., "skip UX reviews", "focus on security"]

## Deferred Items Summary

| Source | Change ID | Count | Highest Severity |
|--------|-----------|-------|-----------------|
| Gate 2 | (initial) | 1 | Major |
| Gate 3 | FEAT-004 | 1 | Minor |

## Last Updated: YYYY-MM-DD
```

---

## Context Reload Template

Use at the start of a new session to restore context from previous phases:

```markdown
We are continuing a Spec Coding workflow for [Project Name].

Please read specs/status.md first, then the relevant spec files, and continue from the current phase.
```

---

## Expert Review Output Template

Use this format when producing expert reviews at any gate:

```markdown
## Expert Review — [Gate Name] (Round [N] of 3)

### [Role Name] Review

**Strengths:**
- [What the artifact gets right]

**Issues:**
| # | Severity | Description | Recommendation |
|---|----------|-------------|----------------|
| 1 | Critical | [Problem description] | [Specific fix] |
| 2 | Major | [Problem description] | [Specific fix] |
| 3 | Minor | [Problem description] | [Specific fix] |

**Suggestions:**
- [Optional improvement ideas]

### [Next Role Name] Review
...

---

### Consolidated Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 2 |
| Minor | 1 |

**Suggested fix order:** #1 (Major, blocks #2) → #2 (Major) → #3 (Minor, optional)

**Verdict:** [Auto-approved ✅ / Needs user decision ⚠️]
```
