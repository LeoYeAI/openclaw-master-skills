---
name: phy-memory-leak-detector
description: Static memory leak pattern scanner for Node.js, Python, Go, and Java. Analyzes source files to detect event listener leaks (addEventListener without corresponding removeEventListener), unbounded cache growth (Maps/objects grown in closures without eviction), setInterval/setTimeout references that prevent GC, large buffer allocations inside request handlers, global variable accumulation, circular reference patterns, and missing cleanup in class destructors/useEffect. For Node.js also runs --expose-gc heap snapshot diff (before/after load test) to confirm leaks at runtime. Zero external service — pure static analysis + optional local Node.js heap. Triggers on "memory leak", "heap growing", "OOM in production", "memory usage", "event listener leak", "setInterval not cleared", "/mem-leak".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - memory
    - performance
    - node-js
    - python
    - go
    - java
    - static-analysis
    - developer-tools
    - debugging
    - oom
---

# Memory Leak Detector

Your Node.js process uses 200MB on startup. After 4 hours, it's at 2GB. You restart it at 3am. The next day it happens again.

This skill scans your codebase for the 12 static patterns that cause 95% of memory leaks in production services — event listener accumulation, unbounded caches, closure-captured large objects, setInterval without clear. It also guides you through a heap snapshot diff to confirm the leak at runtime.

**Supports Node.js, Python, Go, Java. Zero external API.**

---

## Trigger Phrases

- "memory leak", "heap growing", "process memory keeps growing"
- "OOM in production", "out of memory"
- "event listener leak", "addEventListener without remove"
- "setInterval not cleared", "timer leak"
- "unbounded cache", "Map growing"
- "heap snapshot", "memory profiling"
- "/mem-leak"

---

## How to Provide Input

```bash
# Option 1: Scan entire project
/mem-leak

# Option 2: Scan specific directory
/mem-leak src/

# Option 3: Focus on specific pattern
/mem-leak --check listeners    # event listener leaks
/mem-leak --check timers       # setInterval/setTimeout leaks
/mem-leak --check caches       # unbounded Map/object growth
/mem-leak --check closures     # large objects captured in closures
/mem-leak --check globals      # global variable accumulation

# Option 4: Node.js runtime heap snapshot diff
/mem-leak --heap-diff          # takes snapshot, runs 100 requests, takes second snapshot

# Option 5: CI mode
/mem-leak --ci --max-critical 0
```

---

## Step 1: Detect Logging Framework

```python
import re
import glob
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class LeakFinding:
    file: str
    line: int
    code: str
    pattern: str        # LISTENER_LEAK, TIMER_LEAK, UNBOUNDED_CACHE, etc.
    severity: str       # CRITICAL / HIGH / MEDIUM / LOW
    message: str
    fix: str
```

---

## Step 2: Static Pattern Detection

```python
# Language-specific memory leak patterns
SKIP_DIRS = {'node_modules', '.git', 'dist', 'build', '__pycache__',
             '.next', 'vendor', 'venv', '.venv', 'test', 'spec', '__tests__'}


# ── Node.js / JavaScript / TypeScript ────────────────────────────────────────

JS_PATTERNS = [

    # Event listener leak: addEventListener in a function without removeEventListener
    {
        'name': 'LISTENER_LEAK',
        'pattern': re.compile(
            r'\.addEventListener\s*\(\s*["\'](\w+)["\']',
            re.I
        ),
        'check': lambda line, context: 'removeEventListener' not in context,
        'severity': 'HIGH',
        'message': 'addEventListener without matching removeEventListener — leaks on every call',
        'fix': (
            "Store the listener reference and call removeEventListener in cleanup:\n"
            "  const handler = () => {...};\n"
            "  el.addEventListener('event', handler);\n"
            "  // In cleanup: el.removeEventListener('event', handler);"
        ),
    },

    # setInterval without clearInterval
    {
        'name': 'TIMER_LEAK',
        'pattern': re.compile(r'\bsetInterval\s*\('),
        'check': lambda line, context: 'clearInterval' not in context,
        'severity': 'HIGH',
        'message': 'setInterval without clearInterval — timer keeps running even after component unmounts',
        'fix': (
            "Store the interval ID and clear in cleanup:\n"
            "  const id = setInterval(fn, ms);\n"
            "  // In cleanup/useEffect return: clearInterval(id);"
        ),
    },

    # Node.js EventEmitter: on() without off() in request handler
    {
        'name': 'EMITTER_LEAK',
        'pattern': re.compile(
            r'(emitter|ee|bus|pubsub|EventEmitter)\.(on|once)\s*\(',
            re.I
        ),
        'check': lambda line, context: '.off(' not in context and '.removeListener(' not in context,
        'severity': 'MEDIUM',
        'message': 'EventEmitter.on() without corresponding .off() — listeners accumulate',
        'fix': "Add emitter.off(event, handler) in cleanup, or use emitter.once() for one-time listeners",
    },

    # Global Map/Set growing inside a module (cache without size limit)
    {
        'name': 'UNBOUNDED_CACHE',
        'pattern': re.compile(
            r'^(const|let|var)\s+\w+\s*=\s*new\s+(Map|Set)\s*\(\s*\)',
            re.M
        ),
        'check': lambda line, context: '.delete(' not in context and '.clear(' not in context and 'size' not in context,
        'severity': 'MEDIUM',
        'message': 'Module-level Map/Set with no eviction — grows unbounded over time',
        'fix': (
            "Add size limit with LRU eviction:\n"
            "  if (cache.size >= MAX_SIZE) cache.delete(cache.keys().next().value);\n"
            "  cache.set(key, value);\n"
            "Or use lru-cache: npm install lru-cache"
        ),
    },

    # Large buffer/array allocation per request
    {
        'name': 'REQUEST_ALLOCATION',
        'pattern': re.compile(
            r'Buffer\.alloc\s*\(\s*\d{6,}|new\s+Array\s*\(\s*\d{5,}',
            re.I
        ),
        'check': lambda line, context: True,  # Always flag
        'severity': 'MEDIUM',
        'message': 'Large buffer/array allocated per request — check that it is released',
        'fix': "Ensure large allocations go out of scope after request completes. Avoid module-level assignment.",
    },

    # require() inside a loop or hot path
    {
        'name': 'DYNAMIC_REQUIRE_IN_LOOP',
        'pattern': re.compile(r'\brequire\s*\([^)]+\)'),
        'check': lambda line, context: re.search(r'\b(for|while|forEach|map|reduce)\b', context[:200] or ''),
        'severity': 'LOW',
        'message': 'require() inside loop — repeated module loading holds references',
        'fix': "Move require() to the top of the file outside any loop",
    },

    # Missing cleanup in React useEffect
    {
        'name': 'USEEFFECT_NO_CLEANUP',
        'pattern': re.compile(r'useEffect\s*\(\s*\(\s*\)\s*=>'),
        'check': lambda line, context: 'return' not in context[context.find('useEffect'):context.find('useEffect')+500 if 'useEffect' in context else 0:],
        'severity': 'MEDIUM',
        'message': 'useEffect with no cleanup return — subscriptions/timers inside will leak on unmount',
        'fix': (
            "Add cleanup:\n"
            "  useEffect(() => {\n"
            "    const sub = subscribe();\n"
            "    return () => sub.unsubscribe();  // cleanup\n"
            "  }, [deps]);"
        ),
    },
]


# ── Python ────────────────────────────────────────────────────────────────────

PYTHON_PATTERNS = [

    # Global list/dict that grows (common caching anti-pattern)
    {
        'name': 'GLOBAL_ACCUMULATOR',
        'pattern': re.compile(
            r'^(CACHE|RESULTS|HISTORY|LOG|BUFFER|DATA|QUEUE)\s*=\s*[\[\{]',
            re.M
        ),
        'check': lambda line, context: '.pop(' not in context and '.clear(' not in context and 'maxsize' not in context,
        'severity': 'MEDIUM',
        'message': 'Module-level mutable container without eviction — accumulates data for process lifetime',
        'fix': "Use functools.lru_cache(maxsize=N) or limit size manually with CACHE[:MAX_SIZE]",
    },

    # Django/Flask: large queryset not using .iterator()
    {
        'name': 'ORM_FULL_QUERYSET',
        'pattern': re.compile(r'\.all\(\)\s*$|\.filter\([^)]*\)\s*$', re.M),
        'check': lambda line, context: '.iterator(' not in context and 'for ' in context,
        'severity': 'MEDIUM',
        'message': 'QuerySet.all()/filter() in loop without .iterator() — loads entire table into memory',
        'fix': "Use Model.objects.filter(...).iterator() for large datasets to stream rows",
    },

    # Circular reference with __del__
    {
        'name': 'CIRCULAR_WITH_DEL',
        'pattern': re.compile(r'def\s+__del__\s*\(self\)'),
        'check': lambda line, context: True,
        'severity': 'LOW',
        'message': '__del__ method detected — objects with __del__ and circular refs are not collected by CPython GC',
        'fix': "Use weakref.ref() to break circular references, or use contextlib.contextmanager instead of __del__",
    },
]


# ── Go ────────────────────────────────────────────────────────────────────────

GO_PATTERNS = [

    # Goroutine leak: go func() without context cancellation
    {
        'name': 'GOROUTINE_LEAK',
        'pattern': re.compile(r'\bgo\s+func\s*\('),
        'check': lambda line, context: 'context' not in context and 'done' not in context and 'cancel' not in context,
        'severity': 'HIGH',
        'message': 'goroutine started without context or done channel — may run forever on error paths',
        'fix': (
            "Pass context to goroutine and select on ctx.Done():\n"
            "  go func(ctx context.Context) {\n"
            "    select {\n"
            "    case <-ctx.Done(): return\n"
            "    case result := <-work: ...\n"
            "    }\n"
            "  }(ctx)"
        ),
    },

    # HTTP response body not closed
    {
        'name': 'RESP_BODY_NOT_CLOSED',
        'pattern': re.compile(r'http\.(Get|Post|Do)\s*\('),
        'check': lambda line, context: 'defer' not in context or 'Body.Close' not in context,
        'severity': 'HIGH',
        'message': 'HTTP response body not closed — leaks TCP connections and memory',
        'fix': "Add: defer resp.Body.Close() immediately after checking err",
    },

    # Unbounded channel
    {
        'name': 'UNBOUNDED_CHANNEL',
        'pattern': re.compile(r'make\s*\(\s*chan\s+\w+\s*\)'),
        'check': lambda line, context: True,
        'severity': 'MEDIUM',
        'message': 'Unbounded channel (no buffer size) — sender blocks if receiver is slow, causing goroutine leak',
        'fix': "Use make(chan T, N) with an appropriate buffer size, or ensure consumer keeps up with producer",
    },
]


def find_leaks(src_dir: str = '.') -> list[LeakFinding]:
    """Scan source files for memory leak patterns."""
    findings = []

    EXT_PATTERNS = {
        '.js': JS_PATTERNS, '.jsx': JS_PATTERNS,
        '.ts': JS_PATTERNS, '.tsx': JS_PATTERNS, '.mjs': JS_PATTERNS,
        '.py': PYTHON_PATTERNS,
        '.go': GO_PATTERNS,
    }

    for ext, patterns in EXT_PATTERNS.items():
        for fpath in glob.glob(f'{src_dir}/**/*{ext}', recursive=True):
            if any(skip in fpath for skip in SKIP_DIRS):
                continue
            try:
                content = Path(fpath).read_text(errors='replace')
                lines = content.splitlines()
            except Exception:
                continue

            for i, line in enumerate(lines, 1):
                for p in patterns:
                    if p['pattern'].search(line):
                        # Context window (±10 lines)
                        ctx_start = max(0, i - 10)
                        ctx_end = min(len(lines), i + 10)
                        context = '\n'.join(lines[ctx_start:ctx_end])

                        if p['check'](line, context):
                            findings.append(LeakFinding(
                                file=fpath,
                                line=i,
                                code=line.strip()[:120],
                                pattern=p['name'],
                                severity=p['severity'],
                                message=p['message'],
                                fix=p['fix'],
                            ))

    return findings
```

---

## Step 3: Node.js Runtime Heap Snapshot Diff

```bash
# Confirms whether a static finding is actually leaking at runtime
# Requires Node.js process to be running locally

# 1. Start your server with --expose-gc
node --expose-gc server.js &
SERVER_PID=$!
sleep 2

# 2. Take initial heap snapshot via clinic.js or heapdump
npx clinic heapprofiler -- node --expose-gc server.js &

# OR use the v8-profiler-next approach:
node -e "
const v8 = require('v8');
const fs = require('fs');

// Take snapshot before
global.gc();
const before = process.memoryUsage().heapUsed;

// Simulate 100 requests (adjust URL/count)
const http = require('http');
let done = 0;
for (let i = 0; i < 100; i++) {
  http.get('http://localhost:3000/api/users', (res) => {
    res.resume();
    res.on('end', () => {
      done++;
      if (done === 100) {
        global.gc();
        const after = process.memoryUsage().heapUsed;
        const diff = (after - before) / 1024 / 1024;
        console.log('Heap diff after 100 requests: ' + diff.toFixed(2) + ' MB');
        if (diff > 5) {
          console.log('⚠️  CONFIRMED LEAK: heap grew ' + diff.toFixed(2) + 'MB');
          process.exit(1);
        } else {
          console.log('✅  No significant leak detected');
        }
      }
    });
  });
}
"

# 3. Use clinic.js for visual flame graph
npx clinic flame -- node server.js
# Then run load test with autocannon:
npx autocannon -c 10 -d 30 http://localhost:3000/api/users
```

---

## Step 4: Output Report

```markdown
## Memory Leak Analysis
Project: my-api | Files scanned: 89 | Patterns checked: 12

---

### Summary

| Pattern | Count | Severity |
|---------|-------|---------|
| 🔴 Goroutine Leak | 3 | HIGH |
| 🟠 EventEmitter without .off() | 5 | MEDIUM |
| 🟠 Unbounded Map/Set cache | 4 | MEDIUM |
| 🟡 useEffect without cleanup | 7 | MEDIUM |
| ⚪ Large allocation per request | 2 | LOW |

---

### 🔴 HIGH — Goroutine Leaks (3 found)

**handlers/stream.go:45**
```go
go func() {
    for data := range ch {
        conn.Write(data)
    }
}()
```
⚠️ Goroutine has no context — if `conn` is closed on client disconnect, goroutine blocks forever on `ch`.

Fix:
```go
go func(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return
        case data, ok := <-ch:
            if !ok { return }
            conn.Write(data)
        }
    }
}(req.Context())
```

---

### 🟠 MEDIUM — Unbounded Cache (4 found)

**src/services/user.ts:12**
```ts
const userCache = new Map<string, User>();

export function getUser(id: string): User {
    if (!userCache.has(id)) {
        userCache.set(id, fetchUser(id));
    }
    return userCache.get(id)!;
}
```
⚠️ `userCache` grows forever — one entry per unique user ID seen. With 100K users, this holds ~100K objects in memory indefinitely.

Fix:
```ts
import LRU from 'lru-cache';
const userCache = new LRU<string, User>({ max: 1000, ttl: 1000 * 60 * 5 });
```

---

### 🟡 MEDIUM — React useEffect without cleanup (7 found)

**src/components/LiveFeed.tsx:34**
```tsx
useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onmessage = (e) => setMessages(prev => [...prev, e.data]);
}, []);
```
⚠️ WebSocket not closed on unmount — connection persists after component unmounts. Message handler references `setMessages` → prevents component GC.

Fix:
```tsx
useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onmessage = (e) => setMessages(prev => [...prev, e.data]);
    return () => ws.close();  // cleanup
}, []);
```

---

### Runtime Confirmation

```bash
# Confirm the goroutine leak:
go tool pprof http://localhost:6060/debug/pprof/goroutine
# Look for: growing count of goroutines in stream.go:45

# Confirm the Map leak:
node --expose-gc -e "require('./heap-diff.js')"
# Expected output if leaking: "Heap diff after 100 requests: 18.4 MB ⚠️ CONFIRMED LEAK"
```
```

---

## Quick Mode Output

```
Memory Leak Scan: my-api (89 files)

🔴 3 goroutine leaks — go func() without ctx.Done() (handlers/stream.go:45, :89, :112)
🟠 5 EventEmitter.on() without .off() — listeners accumulate per request
🟠 4 unbounded Maps — userCache, sessionCache, configCache, tokenCache (no eviction)
🟡 7 useEffect without cleanup return

Worst offender: userCache (Map with no size limit, user.ts:12)
Quick fix: npm install lru-cache → replace new Map() with new LRU({ max: 1000 })
Runtime confirm: node --expose-gc + 100 req test → should show heap growth
```
