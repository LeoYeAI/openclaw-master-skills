# ADR-008: First-Class Projects

## Status

Accepted

## Context

As Palaia usage grows, entries accumulate across diverse topics — product work, research, personal notes. Users need a way to group related entries without breaking the existing flat model. Scopes (ADR-002) handle *access control* (private/team/public), but there's no mechanism for *organizational grouping*.

## Decision

### Projects as Optional Containers

Projects are first-class but entirely optional. They provide:

- **Grouping:** Entries tagged with a `project` field in frontmatter
- **Default scope per project:** Each project can define its own default scope
- **Dedicated CLI:** `palaia project create/list/show/write/query/delete/set-scope`
- **Integration:** `--project` flag on existing `write`, `query`, `list`, `export` commands

### Orthogonal to Scopes

Projects and scopes serve different purposes:

| Concern      | Mechanism | Example |
|--------------|-----------|---------|
| Organisation | Project   | "clawsy", "palaia", "research" |
| Access       | Scope     | private, team, public |

A project can contain entries with mixed scopes. A scope applies regardless of project membership.

### Default Scope Cascade

When writing an entry, scope is resolved in priority order:

1. **Explicit `--scope` argument** → always wins
2. **Project `default_scope`** → if entry belongs to a project
3. **Global `default_scope`** (from `config.json`) → for entries without project
4. **Hardcoded fallback** → `team`

### Data Model

Projects are stored in `.palaia/projects.json`:

```json
{
  "clawsy": {
    "name": "clawsy",
    "description": "Mac Companion App",
    "default_scope": "team",
    "created_at": "2026-03-11T12:00:00+00:00",
    "members": []
  }
}
```

Entries reference projects via an optional `project` field in YAML frontmatter:

```yaml
---
scope: team
project: clawsy
---
```

### Backward Compatibility

- Entries without a `project` field work identically to before
- All existing commands function unchanged
- Projects are a pure opt-in layer
- Deleting a project preserves entries (only removes the project tag)

## Consequences

- **Positive:** Clean organizational grouping without affecting access control
- **Positive:** Default scope per project reduces repetitive `--scope` flags
- **Positive:** Zero migration needed — existing stores are fully compatible
- **Risk:** `projects.json` is a single shared file (no locking yet); acceptable for current scale

## Future Work

- **Sub-teams / Members:** The `members` field is reserved for future per-project team membership
- **Project-level permissions:** Combining projects with `shared:` scopes
- **Project archival:** Moving all project entries to cold tier at once
