# Scope Accuracy Protocol

> **Purpose**: Ensure impact scope is accurate and complete before fixing, preventing "fix A, break B" regressions.
> **When to use**: Every time you modify shared code (API, component, utility, config, cache).

---

## Core Principles

You cannot mathematically prove scope is 100% complete, but you can achieve **high confidence** through:

1. **Enumerate all consumers** (who is using the modified artifact)
2. **List all contracts** (what behavior/interfaces are promised)
3. **Define invariants** (what must remain true)
4. **Build regression matrix** (what to verify for each consumer)

---

## Step 1: Consumer List (MANDATORY)

### Template

```markdown
## Consumer List

| Consumer | Layer | Entry Point | Contract Used | Risk | Verification |
|----------|-------|-------------|---------------|------|-------------|
| [who] | [frontend/backend/CLI/test] | [file:line] | [signature/field] | [H/M/L] | [how to verify] |
```

### Consumer Types

| Type | Description | How to Find |
|------|------------|-------------|
| **Direct callers** | Directly import and call the symbol | `rg "import.*symbol"` |
| **Indirect dependents** | Use via re-export or wrapper | `rg "export.*symbol"` |
| **Config consumers** | Read the config/env var being modified | `rg "process.env.VAR"` |
| **Cache consumers** | Depend on cache key/TTL/invalidation logic | Search cache usage |
| **Event subscribers** | Listen for events you emit | Search event handlers |
| **Test consumers** | Use the code in tests | `rg "symbol" --glob "*.test.*"` |

### Risk Assessment

| Risk Level | Criteria |
|-----------|----------|
| **High** | Production critical path, no tests, complex logic |
| **Medium** | Secondary path, some tests, moderate complexity |
| **Low** | Dev-only, well-tested, simple logic |

---

## Step 2: Contract & Invariant List

### Contract Template

```markdown
## Contract List

| Contract Type | Before | After | Breaking? |
|---------------|--------|-------|-----------|
| Function signature | `fn(a: string): number` | `fn(a: string, b?: number): number` | ✅ No |
| Return type | `{ id: number }` | `{ id: number, name: string }` | ✅ No (additive) |
| Error codes | `404 = not found` | `404 = not found` | ✅ No |
| Side effects | Writes to DB | Writes to DB + cache | ⚠️ Maybe |
```

### Invariant Template

```markdown
## Invariant List

| ID | Invariant | Why It Matters | Verification |
|----|-----------|---------------|-------------|
| INV-1 | Response structure never removes fields | Clients may depend on them | Schema diff |
| INV-2 | Error codes maintain same semantics | Error handling depends on them | Code review |
| INV-3 | Session routing consistent | Wrong session = wrong data | Log correlation |
| INV-4 | Side-effect operations not cached | Cached = duplicate side effects | Cache config review |
```

### Common Invariant Categories

| Category | Examples |
|----------|---------|
| **API invariants** | Response structure, error codes, status codes |
| **State invariants** | State transitions (loading→success), no orphan states |
| **Routing invariants** | Request → correct handler, session → correct instance |
| **Cache invariants** | Idempotent operations cacheable, side-effect operations not |
| **Security invariants** | Auth checked before actions, no privilege escalation |

---

## Step 3: Call Site Enumeration

### Discovery Commands

```bash
# Direct calls
rg -n "symbolName" . --glob "*.{ts,tsx,py,go,java}"

# Re-exports
rg -n "export.*symbolName" . --glob "*.{ts,tsx,py}"

# Dynamic calls (harder to find, e.g. obj["methodName"])
rg -n "\[.*symbolName.*\]" . --glob "*.{ts,tsx,py}"
```

### Call Site Classification

```markdown
## Call Site List

| File:Line | Call Type | Classification | Needs Update | Update Content |
|-----------|----------|----------------|--------------|----------------|
| api.ts:23 | Direct | Runtime critical | ☐ | - |
| utils.ts:45 | Re-export | Runtime critical | ☐ | - |
| test.ts:100 | Direct | Test only | ☐ | Update mock |
| script.ts:50 | Direct | Dev only | ☐ | - |
```

### Classification Rules

| Classification | Definition | Priority |
|----------------|-----------|----------|
| **Runtime critical** | Production code path | Must verify |
| **Test only** | Test files | Update tests |
| **Dev only** | Dev scripts, tools | Low priority |
| **Dead code** | Unreachable | Consider removal |

---

## Step 4: Minimal Regression Matrix

### Template

```markdown
## Regression Matrix

| Consumer | Normal Flow | Critical Boundary | Verification Status |
|----------|------------|-------------------|---------------------|
| [consumer 1] | [normal flow test] | [boundary test] | ☐ |
| [consumer 2] | [normal flow test] | [boundary test] | ☐ |
```

### Matrix Rules

1. **Each consumer needs at least 1 normal flow + 1 boundary case**
2. **Prioritize runtime critical consumers**
3. **At least 1 automated guard at root cause location**

### Guard Types

| Type | Description | Example |
|------|------------|---------|
| **Unit test** | Directly test the fixed function | `expect(fn()).toBe(correct)` |
| **Integration test** | Test consumer flow | API test with real DB |
| **Assertion** | Runtime check in code | `assert sessionId != null` |
| **Log alert** | Log + alert on violation | `if (unexpected) log.error(...)` |

---

## Scope Discovery Checklist

Verify before fixing:

- [ ] Consumer list complete (all types checked)
- [ ] Contracts listed (signatures, return values, errors, side effects)
- [ ] Invariants defined (what cannot change)
- [ ] Call sites enumerated and classified
- [ ] Regression matrix covers all runtime critical consumers

---

## Common Scope Gaps (Anti-Patterns)

| Gap | Problem | Fix |
|-----|---------|-----|
| Missing indirect consumers | Breaking code via re-exports | Search re-exports |
| Missing config consumers | Breaking code that reads same config | Search config key usage |
| Missing cache consumers | Stale cache causes bug | Review cache invalidation |
| Missing event subscribers | Events not handled | Search event handlers |
| No regression matrix | Can't verify fix doesn't break | Build matrix before fix |

---

## Integration with Fix Phase

After scope discovery, the fix should:

1. **Respect all invariants** (no breaking changes unless necessary)
2. **Update all affected call sites** (from enumeration)
3. **Pass all regression matrix items** (before declaring done)
4. **Add a guard at root cause** (prevent recurrence)
