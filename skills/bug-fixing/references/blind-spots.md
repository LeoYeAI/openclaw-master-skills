# AI Blind Spot Registry

> **Purpose**: Track known blind spots that the AI tends to miss during bug fixing.
> Updated by the Self-Reflection Protocol (Phase 6.5).
> Every fix MUST check active blind spots before proceeding.

---

## Active Blind Spots (Check Before Every Fix)

| ID | Blind Spot | First Seen | Times Hit | Mitigation Check |
|----|-----------|------------|-----------|------------------|
| BS-001 | Forgetting to update test files when fixing source | Seed | 0 | Search `*.test.*` `*.spec.*` for affected symbols |
| BS-002 | Not checking indirect callers via re-exports | Seed | 0 | Run `rg "export.*symbol"` to find re-exports |
| BS-003 | Assuming API response matches TypeScript types | Seed | 0 | Log and verify actual response shape |
| BS-004 | Missing cache invalidation after data mutations | Seed | 0 | Search for cache usage of modified data |
| BS-005 | Not testing error/failure paths | Seed | 0 | Explicitly test 4xx/5xx/null/undefined |
| BS-006 | Ignoring race conditions in async code | Seed | 0 | Ask "can this be called concurrently?" |
| BS-007 | Fix scope creep — changing more than needed | Seed | 0 | Count LOC, prefer <=50 |
| BS-008 | Fixing function in one file but same function exists in another file | 2026-03-05 | 1 | `rg "def function_name" backend/` — check both `services/` and `core/graph/nodes/` |
| BS-009 | Code fixed but server still runs old bytecode (no restart) | 2026-03-05 | 1 | Kill backend process + clear `__pycache__` + restart + verify /docs returns 200 |
| BS-010 | New regex matches tool name as substring of longer name | 2026-03-05 | 1 | Add `(?<![a-zA-Z0-9_])` before pattern; test with tool names that are substrings of each other |
| BS-011 | Fixing Path A (agent_executor) but forgetting Path B (StateGraph/llm_node) | 2026-03-05 | 1 | Always check both execution paths when modifying agent/tool logic |
| BS-012 | Alphabetical sort in argument remapper maps to wrong parameter | 2026-03-05 | 0 | When parser produces {"input": x}, remapper fills first alphabetical required field — may not be the right one |
| BS-013 | Format 4 generic regex with `re.MULTILINE` matches `)` inside content | 2026-03-05 | 0 | `$` with MULTILINE matches end of ANY line; content with `)` at line end causes premature match |

---

## Retired Blind Spots (Consistently Avoided for 5+ Fixes)

| ID | Blind Spot | Retired Date | Reason |
|----|-----------|-------------|--------|
| *(none yet)* | | | |

---

## How to Use This Registry

### Before Every Fix (Phase 3.5)

1. Read all **Active Blind Spots**
2. For each, execute the **Mitigation Check**
3. Record results in your Impact Prediction

### After Every Fix (Phase 6.5)

1. Did any blind spot trigger? Increment **Times Hit**
2. Did you discover a new blind spot? Add new entry
3. Has a blind spot been avoided 5+ consecutive times? Move to **Retired**

### Adding a New Blind Spot

```markdown
| BS-NNN | [Description of what was missed] | [Date] | 1 | [Specific check to prevent this] |
```

### Common AI Blind Spot Seed List

| Category | Blind Spot | Check |
|----------|-----------|-------|
| **Scope** | Forgetting indirect callers via re-exports | `rg "export.*symbol"` |
| **Scope** | Missing test file updates | Search `*.test.*` |
| **State** | Not considering race conditions | "Can this be called concurrently?" |
| **State** | Ignoring initialization order | Check component/module load order |
| **API** | Assuming response format | Verify actual response shape |
| **API** | Not checking error paths | Test 4xx/5xx/null/undefined |
| **Types** | Trusting type assertions | Verify runtime values match types |
| **Config** | Forgetting environment differences | Check all env configs |
| **Cache** | Not invalidating after mutation | Check cache strategy |
| **UI** | Not testing different screen sizes | Check responsive behavior |
