# Caller Impact Protocol (Method/Class)

Purpose: When fixing a method/class, force an inventory of callers and impact scope to prevent "fixed A, broke B".

> **Related**: For full consumer list and invariant list templates, see `scope-accuracy-protocol.md`.

---

## 🔴 Scope Accuracy Gate (MANDATORY)

Before modifying any shared code, must satisfy:

| Gate | Requirement |
|------|------------|
| **Consumer List** | List all consumers (direct, indirect, config, cache, event) |
| **Contract List** | List the behaviors/interfaces being modified |
| **Invariant Check** | List what must remain true after the fix |
| **Call Site Enum** | Enumerate all call sites and classify them |

If any gate is not satisfied, the fix may introduce regressions.

---

## 1) Inventory: Who Is Calling (MANDATORY)

- Direct callers: Search for function name/method name/export name.
- Indirect callers: Find upper-level wrappers, interface adapters, shared hooks/stores, utility functions.
- Implicit calls: Event names/string keys/route mappings/config mappings/reflection/serialization field names.

### Consumer Types (Complete List)

| Type | Description | How to Find |
|------|------------|-------------|
| **Direct callers** | Directly import and call the symbol | `rg "import.*symbol"` |
| **Indirect dependents** | Use via re-export or wrapper | `rg "export.*symbol"` |
| **Config consumers** | Read the config/env var being modified | `rg "process.env.VAR"` |
| **Cache consumers** | Depend on cache key/TTL/invalidation logic | Search cache usage |
| **Event subscribers** | Listen for events you emit | Search event handlers |
| **Test consumers** | Use the code in tests | `rg "symbol" --glob "*.test.*"` |

Recommended approach:
- Use `rg -n` to search the entire repo for key symbols and key strings.
- If you have symbol tools (e.g. LSP), do references lookup on key methods.

Common search templates (replace keywords as needed):

```bash
# Search function/method/class name
rg -n "MyFunction|MyClass|my_method" .

# Search string keys (event names/route names/config keys)
rg -n "\"my_key\"|'my_key'|my_key" .

# Search exports and imports (common in JS/TS)
rg -n "export {" .
rg -n "from " .
```

## 2) Classify: Which Are High-Risk Consumers (MANDATORY)

High-risk (must regression verify at minimum):
- List/detail/selector/settings pages sharing the same data or contract
- Permission/auth paths
- Write operations (mutations) and their subsequent read paths
- Cache keys / sort-pagination / compat fallbacks

## 3) Decide: Need to Fix Together? (MANDATORY)

If any of these are true, must fix jointly (or explicitly block and document reason):
- Callers have the same incorrect assumption about input/output
- Fix changes return shape / default values / error model / timing
- Fix changes semantics of shared component / shared mapping

## 4) Minimal Regression Matrix (MANDATORY)

For each high-risk consumer, verify at minimum:
- Normal flow
- One failure/boundary path (empty/permission/timeout/error code)
- Write-then-read consistency (if mutations involved)

### Regression Matrix Template

```markdown
## Regression Matrix

| Consumer | Normal Flow | Critical Boundary | Verification Status |
|----------|------------|-------------------|---------------------|
| [consumer 1] | [normal flow test] | [boundary test] | ☐ |
| [consumer 2] | [normal flow test] | [boundary test] | ☐ |
```

---

## 5) Contracts & Invariants (MANDATORY)

When modifying shared code, must list the contracts being modified and invariants that must hold.

### Contract Template

```markdown
## Contract List

| Contract Type | Before | After | Breaking? |
|---------------|--------|-------|-----------|
| Function signature | `fn(a: string)` | `fn(a: string, b?: number)` | ✅ No |
| Return type | `{ id: number }` | `{ id: number, name: string }` | ✅ No |
```

### Invariant Template

```markdown
## Invariant List

| ID | Invariant | Why It Matters | Verification |
|----|-----------|---------------|-------------|
| INV-1 | [must remain true] | [impact of violation] | [how to verify] |
```

For full templates and examples, see `scope-accuracy-protocol.md`.
