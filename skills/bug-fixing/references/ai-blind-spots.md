# AI Blind Spot Registry (AI 盲点注册表)

> **Purpose**: Track known blind spots that the AI tends to miss during bug fixing.
> This file is updated by the Self-Reflection Protocol (Phase 6.5).
> Every fix MUST check active blind spots before proceeding.

---

## Active Blind Spots (Must Check Every Fix)

| ID | Blind Spot | First Seen | Times Repeated | Mitigation Check |
|----|-----------|------------|----------------|------------------|
| BS-001 | Forgetting to update test files when fixing source code | Seed | 0 | Search `*.test.*` `*.spec.*` for affected symbols |
| BS-002 | Not checking indirect callers via re-exports | Seed | 0 | Run `rg "export.*symbol"` to find re-exports |
| BS-003 | Assuming API response matches TypeScript types | Seed | 0 | Log and verify actual response shape |
| BS-004 | Missing cache invalidation after data mutations | Seed | 0 | Search for cache usage of modified data |
| BS-005 | Not testing error/failure paths | Seed | 0 | Explicitly test 4xx/5xx/null/undefined |
| BS-006 | Ignoring race conditions in async code | Seed | 0 | Ask "can this be called concurrently?" |
| BS-007 | Fix scope creep — changing more than needed | Seed | 0 | Count LOC, enforce ≤50 line limit |

---

## Retired Blind Spots (Consistently Avoided for 5+ Fixes)

| ID | Blind Spot | Retired Date | Reason |
|----|-----------|-------------|--------|
| _(none yet)_ | | | |

---

## How to Use This Registry

### Before Every Fix (Phase 3.5)
1. Read all **Active Blind Spots**
2. For each, execute the **Mitigation Check**
3. Record results in your Impact Prediction

### After Every Fix (Phase 6.5)
1. Did any blind spot trigger? → Increment **Times Repeated**
2. Did you discover a new blind spot? → Add new entry
3. Has a blind spot been avoided 5+ times? → Move to **Retired**

### Adding a New Blind Spot
```markdown
| BS-NNN | [Description of what was missed] | [Today's date] | 1 | [Specific check to prevent this] |
```
