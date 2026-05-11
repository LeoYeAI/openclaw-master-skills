# System-Level Root Cause Analysis

> **When to use**: Browser automation, streaming/SSE/WebSocket, async tasks, microservices,
> IPC, or any bug spanning multiple processes or layers.

---

## Why System-Level Bugs Are Hard

Symptoms tell you where the problem surfaces, not where it originates:

| Symptom | Possible Root Causes |
|---------|---------------------|
| `Element not found` | Wrong session, DOM not ready, iframe, selector typo, redirect |
| `Timeout` | Slow network, hung handler, wrong endpoint, resource exhaustion |
| `Data mismatch` | Stale cache, race condition, wrong routing, schema drift |
| `Connection lost` | Server crash, network issue, client disconnect, idle timeout |

---

## Core Method: End-to-End Chain Analysis

### Step 1: Draw the Chain

Map every participant from trigger to result:

```
[Trigger] -> [Producer] -> [Transport] -> [Consumer] -> [Result]
```

### Step 2: Define Evidence Points

For each edge, define what proves the handshake is correct:

```markdown
| Edge | From -> To | Evidence of Correct Handshake |
|------|-----------|-------------------------------|
| E1 | LLM -> Backend | Received request with correct params |
| E2 | Backend -> SSE | Emitted event with correct payload |
| E3 | SSE -> Frontend | Frontend received event, logged |
| E4 | Frontend -> Runner | Action enqueued with correct sessionId |
| ...  | ... | ... |
```

### Step 3: Insert Probes

BEFORE modifying any behavior, insert probes to collect evidence:

| Probe Type | Location | What to Log |
|-----------|----------|-------------|
| Log | Each edge | `[EdgeN] from=X to=Y payload={...}` |
| Return field | Tool result | `{ ..., debug: { sessionId, url } }` |
| Metric | Critical path | Latency, success rate |
| Assertion | Invariant points | `assert(sessionId != null)` |

### Step 4: Narrow the Search Space

Run reproduction with probes:

1. Find the **last correct edge** (evidence shows handshake OK)
2. Find the **first broken edge** (evidence shows failure)
3. Root cause is between those two edges

```
E1 OK -> E2 OK -> E3 OK -> E4 FAIL -> E5 ? -> E6 ?
                            ^
                       Root cause here
```

---

## System-Level Bug Categories

### Routing Bugs

- **Symptom**: Action hits wrong target (wrong session/instance/handler)
- **Evidence needed**: Routing key at each hop, actual vs expected target
- **Common causes**: Stale key, missing key, key collision

### Timing Bugs

- **Symptom**: Action intermittently fails, succeeds on retry
- **Evidence needed**: Timestamps at each edge, state at each edge
- **Common causes**: Race condition, timeout too short, no retry/backoff

### State Bugs

- **Symptom**: Wrong data, stale data, missing data
- **Evidence needed**: State snapshot at each edge, cache state, DB state
- **Common causes**: Cache not invalidated, stale closure, missing sync

### Transport Bugs

- **Symptom**: Messages lost, corrupted, duplicated
- **Evidence needed**: Message at send/receive, sequence numbers, acks
- **Common causes**: No acknowledgment/retry, buffer overflow, encoding mismatch

---

## Common Patterns

| Pattern | Description | Fix |
|---------|-------------|-----|
| **Session Mismatch** | Frontend has sessionA, backend routes to sessionB | Add session validation at each hop |
| **DOM Not Ready** | Navigation complete but JS still rendering | Wait for specific element, not just network idle |
| **Stale Closure** | Handler captures sessionId at creation, session changes later | Read session from context at execution time |
| **Cache Pollution** | Side-effect operation cached, replayed from cache | Mark side-effect operations non-cacheable |
| **Race Condition** | Action A starts, B completes and changes state, A uses stale state | Serialize actions or use optimistic locking |

---

## System-Level RCA Template

```markdown
## System-Level RCA [BUG-XXX]

### 1. End-to-End Chain
[Step 1] -> [Step 2] -> [Step 3] -> ... -> [Result]

### 2. Evidence Points
| Edge | From -> To | Expected | Actual | Status |
|------|-----------|----------|--------|--------|

### 3. Probes Inserted
| Probe | Location | What It Logs |
|-------|----------|-------------|

### 4. Search Space Narrowing
- Last correct edge: E[N]
- First broken edge: E[N+1]
- Root cause location: [component/function]

### 5. Root Cause
[One sentence explaining the mechanism]

### 6. Fix
[Minimal change targeting root cause]
```

---

## Checklist

Before declaring root cause confirmed:

- [ ] Drew end-to-end chain (all participants)
- [ ] Defined evidence for each edge
- [ ] Inserted probes before modifying behavior
- [ ] Collected evidence from reproduction
- [ ] Narrowed to specific edge/component
- [ ] Explained the mechanism (not just "it's wrong")
- [ ] Fix targets root cause, not symptom
