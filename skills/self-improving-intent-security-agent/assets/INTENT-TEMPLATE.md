# Intent Specifications

Track what you want the agent to achieve with clear boundaries.

---

## [INT-YYYYMMDD-XXX] task_name

**Created**: 2025-01-15T10:00:00Z
**Risk Level**: low | medium | high
**Status**: active | completed | violated

### Goal
Single clear objective (what success looks like)

### Constraints
- Boundary 1 (e.g., "Only modify files in ./src")
- Boundary 2 (e.g., "Do not make network calls")
- Boundary 3 (e.g., "Preserve existing test coverage")

### Expected Behavior
- Pattern 1 (e.g., "Read files before modifying")
- Pattern 2 (e.g., "Run tests after changes")
- Pattern 3 (e.g., "Create backups of modified files")

### Context
- Relevant files: path/to/file.ext
- Environment: development | staging | production
- Previous attempts: INT-20250115-001 (if retry)

---
