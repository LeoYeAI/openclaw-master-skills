# System-Level Root Cause Analysis

> **Purpose**: Root cause analysis for multi-surface, cross-layer, stateful bugs.
> **When to use**: Browser automation, streaming, async tasks, microservices, IPC, or any bug spanning multiple processes/layers.

---

## Why System-Level Bugs Are Hard

System-level bugs present the same symptoms from different root causes:

| Symptom | Possible Root Causes |
|---------|---------------------|
| `Element not found` | Wrong session, DOM not ready, iframe, selector typo, page redirect |
| `Timeout` | Slow network, handler hung, wrong endpoint, resource exhaustion |
| `Data mismatch` | Stale cache, race condition, wrong routing, schema drift |
| `Connection lost` | Server crash, network issue, client disconnect, idle timeout |

**Symptoms tell you where the problem surfaces, not where it originates.**

---

## Core Method: End-to-End Chain Analysis

### Step 1: Draw the Chain

Map every participant from trigger to result:

```
[Trigger] → [Producer] → [Transport] → [Consumer] → [Result]
```

**Example: Browser Automation**

```
LLM Tool Call
    ↓
Backend BrowserActionManager
    ↓
SSE to Frontend
    ↓
Frontend Event Dispatcher
    ↓
browserActionRunner Queue
    ↓
Electron IPC
    ↓
WebContents DOM
    ↓
Result back to LLM
```

### Step 2: Define Evidence Points

For each edge in the chain, define what proves the handshake is correct:

```markdown
## Evidence Points

| Edge | From → To | Evidence of Correct Handshake |
|------|-----------|-------------------------------|
| E1 | LLM → Backend | Received request with correct params |
| E2 | Backend → SSE | Emitted SSE event with correct payload |
| E3 | SSE → Frontend | Frontend received event, logged |
| E4 | Frontend → Runner | Action enqueued with correct sessionId |
| E5 | Runner → Electron | Sent IPC message with correct params |
| E6 | Electron → DOM | DOM query returned expected result |
| E7 | DOM → Result | Result correctly propagated back |
```

### Step 3: Insert Probes

**BEFORE modifying any behavior**, insert probes to collect evidence:

| Probe Type | Location | What to Log |
|-----------|----------|-------------|
| Log | Each edge | `[EdgeN] from=X to=Y payload={...}` |
| Return field | Tool result | `{ ..., debug: { sessionId, url, title } }` |
| Metric | Critical path | Latency, success rate |
| Assertion | Invariant points | `assert(sessionId != null)` |

### Step 4: Narrow the Search Space

Run reproduction with probes, then:

1. **Find the last correct edge** (evidence shows handshake correct)
2. **Find the first broken edge** (evidence shows handshake failed or wrong)
3. **Root cause is between these two edges**

```
✅ E1 → ✅ E2 → ✅ E3 → ❌ E4 → ? E5 → ? E6
                        ↑
                   Root cause is here
```

---

## System-Level Bug Categories

### Category 1: Routing Bugs

**Symptom**: Action hits wrong target (wrong session, wrong instance, wrong handler)

**Evidence needed**:
- Routing key at each hop (sessionId, requestId, routeKey)
- Actual target vs expected target

**Common causes**:
- Stale routing key (old session ID)
- Missing routing key (using default)
- Key collision (two sessions, same key)

### Category 2: Timing Bugs

**Symptom**: Action intermittently fails, succeeds on retry

**Evidence needed**:
- Timestamps at each edge
- State at each edge (ready? loading? error?)
- Wait/timeout configuration

**Common causes**:
- Race condition (action before ready)
- Timeout too short
- No retry/backoff

### Category 3: State Bugs

**Symptom**: Wrong data, stale data, missing data

**Evidence needed**:
- State snapshot at each edge
- Cache state (hit/miss, TTL, key)
- Database state (before/after)

**Common causes**:
- Cache not invalidated
- Stale closure (captured old state)
- Missing state synchronization

### Category 4: Transport Bugs

**Symptom**: Messages lost, corrupted, duplicated

**Evidence needed**:
- Message at send time vs receive time
- Sequence numbers
- Acknowledgments

**Common causes**:
- No acknowledgment/retry
- Buffer overflow
- Encoding mismatch

---

## System-Level RCA Template

```markdown
## System-Level RCA [BUG-XXX]

### 1. End-to-End Chain

```
[Step 1] → [Step 2] → [Step 3] → ... → [Result]
```

### 2. Evidence Points

| Edge | From → To | Expected Evidence | Actual Evidence | Status |
|------|-----------|-------------------|-----------------|--------|
| E1 | ... | ... | ... | ✅/❌ |
| E2 | ... | ... | ... | ✅/❌ |

### 3. Probes Inserted

| Probe | Location | What It Logs |
|-------|----------|-------------|
| ... | ... | ... |

### 4. Search Space Narrowing

- Last correct edge: E[N]
- First broken edge: E[N+1]
- Root cause location: [specific component/function]

### 5. Root Cause

[One sentence explaining the mechanism]

### 6. Fix

[Minimal change targeting root cause]
```

---

## Common System-Level Bug Patterns

### Pattern 1: Session Mismatch

```
Frontend has sessionA
Backend routes to sessionB
→ Action hits wrong browser
```

**Fix pattern**: Add session validation at each hop, return session info in results.

### Pattern 2: DOM Not Ready

```
Navigation complete (network idle)
But JS still rendering
→ Element not found
```

**Fix pattern**: Wait for specific element, not just network idle.

### Pattern 3: Stale Closure

```
Handler captures sessionId at creation time
Session changes
Handler still uses old sessionId
```

**Fix pattern**: Read session from context at execution time, not creation time.

### Pattern 4: Cache Pollution

```
Side-effect operation is cached
Replayed from cache
→ Duplicate side effects or stale results
```

**Fix pattern**: Mark side-effect operations as non-cacheable.

### Pattern 5: Race Condition

```
Action A starts
Action B starts
B completes, changes state
A completes, uses stale state
```

**Fix pattern**: Serialize actions or use optimistic locking.

---

## System-Level Bug Checklist

Before declaring root cause confirmed:

- [ ] Drew end-to-end chain (all participants)
- [ ] Defined evidence for each edge
- [ ] Inserted probes before modifying behavior
- [ ] Collected evidence from reproduction
- [ ] Narrowed to specific edge/component
- [ ] Explained the mechanism (not just "it's wrong")
- [ ] Fix targets root cause, not symptom

---

## Integration with Main Workflow

System-level RCA is used in Phase 2 (Root Cause Analysis):

1. **Triage**: Identify as system-level bug (multi-surface/cross-layer)
2. **RCA**: Use system-level RCA instead of simple Five Whys
3. **Scope**: Consumer list includes all chain participants
4. **Fix**: May require changes at multiple points in the chain
5. **Verification**: Regression matrix covers all edges
