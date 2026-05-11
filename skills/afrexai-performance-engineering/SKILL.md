---
name: afrexai-performance-engineering
description: Complete performance engineering system — profiling, optimization, load testing, capacity planning, and performance culture. Use when diagnosing slow applications, optimizing code/queries/infrastructure, load testing before launch, planning capacity, or building performance into CI/CD. Covers Node.js, Python, Go, Java, databases, APIs, and frontend.
metadata:
  openclaw:
    os: [linux, darwin, win32]
---

# Performance Engineering System

> From "it's slow" to "here's why and here's the fix" — a complete methodology for measuring, diagnosing, optimizing, and preventing performance problems.

## Phase 1: Performance Investigation Brief

Before touching anything, define the problem.

```yaml
# performance-brief.yaml
investigation:
  reported_by: ""
  reported_date: ""
  system: ""              # service/app name
  environment: ""         # production, staging, dev

problem_statement:
  symptom: ""             # "API response time increased 3x"
  impact: ""              # "15% of users seeing timeouts"
  since_when: ""          # "After deploy v2.14 on Feb 20"
  affected_scope: ""      # "All endpoints" | "Only /search" | "Users in EU"

baselines:
  target_p50: ""          # e.g., "200ms"
  target_p95: ""          # e.g., "500ms"
  target_p99: ""          # e.g., "1000ms"
  current_p50: ""
  current_p95: ""
  current_p99: ""
  throughput_target: ""   # e.g., "1000 rps"
  error_rate_target: ""   # e.g., "<0.1%"

constraints:
  budget: ""              # time/money for optimization
  risk_tolerance: ""      # "Can we change the schema?" "Can we add caching?"
  deadline: ""            # "Must fix before Black Friday"

hypothesis:
  primary: ""             # "N+1 queries in the new recommendation engine"
  secondary: ""           # "Connection pool exhaustion under load"
  evidence: ""            # "Slow query log shows 200+ queries per request"
```

### Performance Budget Framework

Set budgets BEFORE building, not after complaints:

| Metric | Web App | API | Mobile | Batch Job |
|--------|---------|-----|--------|-----------|
| P50 response | <200ms | <100ms | <300ms | N/A |
| P95 response | <500ms | <250ms | <800ms | N/A |
| P99 response | <1s | <500ms | <1.5s | N/A |
| Error rate | <0.1% | <0.01% | <0.5% | <0.001% |
| Time to Interactive | <3s | N/A | <2s | N/A |
| Memory per request | <50MB | <20MB | <100MB | <1GB |
| CPU per request | <100ms | <50ms | <200ms | N/A |
| Throughput | 100+ rps | 500+ rps | N/A | items/min |

## Phase 2: Measurement & Profiling

### The Golden Rule
**Never optimize without measuring first. Never measure without a hypothesis.**

### Profiling Decision Tree

```
Is it slow?
├── YES → Where is time spent?
│   ├── CPU-bound → Profile CPU (flame graph)
│   │   ├── Hot function found → Optimize algorithm/data structure
│   │   └── Spread evenly → Architecture problem (too many layers)
│   ├── I/O-bound → Profile I/O
│   │   ├── Database → Query analysis (Phase 4)
│   │   ├── Network → Connection profiling
│   │   ├── Disk → I/O scheduler + buffering
│   │   └── External API → Caching + async + circuit breaker
│   ├── Memory-bound → Profile allocations
│   │   ├── GC pressure → Reduce allocations, pool objects
│   │   ├── Memory leak → Heap snapshot comparison
│   │   └── Cache thrashing → Resize or eviction policy
│   └── Concurrency-bound → Profile locks/contention
│       ├── Lock contention → Reduce critical section, lock-free structures
│       ├── Thread starvation → Pool sizing
│       └── Deadlock → Lock ordering analysis
└── NO → Define "fast enough" (see budgets above)
```

### CPU Profiling by Language

#### Node.js
```bash
# Built-in profiler (V8)
node --prof app.js
node --prof-process isolate-*.log > profile.txt

# Inspector-based (connect Chrome DevTools)
node --inspect app.js
# Open chrome://inspect → Profiler → Start

# Clinic.js (best overall Node.js profiler)
npx clinic doctor -- node app.js
npx clinic flame -- node app.js    # Flame graph
npx clinic bubbleprof -- node app.js  # Async bottlenecks

# 0x (flame graphs)
npx 0x app.js
```

#### Python
```python
# cProfile (built-in)
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20

# Line profiler (pip install line-profiler)
# Add @profile decorator, then:
# kernprof -l -v script.py

# py-spy (sampling profiler, no code changes)
# pip install py-spy
# py-spy top --pid <PID>
# py-spy record -o profile.svg --pid <PID>  # Flame graph

# Scalene (CPU + memory + GPU)
# pip install scalene
# scalene script.py
```

#### Go
```go
// Built-in pprof
import (
    "net/http"
    _ "net/http/pprof"
    "runtime/pprof"
)

// HTTP server (add to existing server)
// Access: http://localhost:6060/debug/pprof/
go func() { http.ListenAndServe(":6060", nil) }()

// CLI analysis
// go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
// go tool pprof -http=:8080 profile.out  # Web UI
```

#### Java
```bash
# async-profiler (best for JVM)
# https://github.com/async-profiler/async-profiler
./asprof -d 30 -f profile.html <PID>

# JFR (built-in since JDK 11)
java -XX:StartFlightRecording=duration=60s,filename=rec.jfr MyApp
jfr print --events CPULoad rec.jfr

# jstack (thread dump)
jstack <PID> > threads.txt
```

### Memory Profiling

#### Leak Detection Pattern (any language)
```
1. Take heap snapshot at T0
2. Run suspected operation N times
3. Force GC
4. Take heap snapshot at T1
5. Compare: objects that grew = potential leak
6. Check: are they reachable? From where? (retention path)
```

#### Node.js Memory
```javascript
// Heap snapshot
const v8 = require('v8');
const fs = require('fs');

function takeSnapshot(label) {
  const snapshotStream = v8.writeHeapSnapshot();
  console.log(`Heap snapshot written to ${snapshotStream}`);
}

// Process memory monitoring
setInterval(() => {
  const mem = process.memoryUsage();
  console.log({
    rss_mb: (mem.rss / 1048576).toFixed(1),
    heap_used_mb: (mem.heapUsed / 1048576).toFixed(1),
    heap_total_mb: (mem.heapTotal / 1048576).toFixed(1),
    external_mb: (mem.external / 1048576).toFixed(1),
  });
}, 10000);
```

#### Python Memory
```python
# tracemalloc (built-in)
import tracemalloc

tracemalloc.start()
# ... code ...
snapshot = tracemalloc.take_snapshot()
top = snapshot.statistics('lineno')
for stat in top[:10]:
    print(stat)

# objgraph (pip install objgraph)
import objgraph
objgraph.show_most_common_types(limit=20)
objgraph.show_growth(limit=10)  # Call twice to see what's growing
```

### Flame Graph Interpretation

```
Reading a flame graph:
┌─────────────────────────────────────────────┐
│                  main()                      │  ← Entry point (bottom)
├──────────────────────┬──────────────────────┤
│     processData()    │    renderOutput()     │  ← Width = time spent
├──────────┬───────────┤                      │
│ parseCSV │ validate  │                      │  ← Tall = deep call stack
├──────────┤           │                      │
│ readline │           │                      │  ← Top = where CPU burns
└──────────┴───────────┴──────────────────────┘

WHAT TO LOOK FOR:
1. Wide plateaus at top → CPU-intensive leaf function (optimize this!)
2. Many thin towers → excessive function calls (batch or reduce)
3. Recursive patterns → potential stack overflow risk
4. Unexpected width → function taking more time than expected
5. GC/runtime frames → memory pressure

ACTION RULES:
- Plateau >20% width → must investigate
- Plateau >40% width → almost certainly the bottleneck
- If top 3 functions = 80% of time → focused optimization will work
- If evenly distributed → architectural change needed
```

## Phase 3: Common Optimization Patterns

### Algorithm & Data Structure Optimizations

| Problem | Bad O() | Fix | Good O() |
|---------|---------|-----|----------|
| Search unsorted array | O(n) | Sort + binary search, or use Set/Map | O(log n) or O(1) |
| Nested loop matching | O(n²) | Hash map lookup | O(n) |
| Repeated string concat | O(n²) | StringBuilder/join array | O(n) |
| Sorting already-sorted data | O(n log n) | Check if sorted first | O(n) |
| Finding duplicates | O(n²) | Set-based detection | O(n) |
| Frequent min/max of changing data | O(n) per query | Heap/priority queue | O(log n) |

### Caching Strategy Decision Matrix

```
Should you cache this?
├── Does the same input always produce the same output?
│   ├── YES → Cache candidate ✓
│   └── NO → Can you define a valid TTL?
│       ├── YES → Cache with TTL ✓
│       └── NO → Don't cache ✗
├── Is it called frequently?
│   ├── <10x/min → Probably not worth caching
│   └── >10x/min → Cache ✓
├── Is the source data expensive to compute/fetch?
│   ├── <10ms → Probably not worth caching
│   └── >10ms → Cache ✓
└── Does staleness cause problems?
    ├── Critical (financial, auth) → Short TTL or cache-aside with invalidation
    ├── Important (user data) → 1-5 min TTL with invalidation
    └── Tolerant (content, search) → 5-60 min TTL

CACHE LAYERS (use in order):
1. In-process (Map/LRU) → <1μs, limited by memory, per-instance
2. Shared cache (Redis/Memcached) → <1ms, shared across instances
3. CDN/edge cache → <10ms, geographic distribution
4. Browser cache → 0ms for user, stale risk

INVALIDATION STRATEGIES:
- TTL-based: simplest, best for read-heavy + staleness-tolerant
- Event-based: publish cache-invalidate on write, best for consistency
- Write-through: update cache on every write, best for write-read patterns
- Cache-aside: app manages cache explicitly, most flexible
```

### Connection Pooling

```yaml
# Sizing formula
pool_size: min(available_cores * 2 + effective_spindle_count, max_connections / num_instances)

# Rules of thumb:
# - PostgreSQL: connections = cores * 2 + 1 (per pgBouncer docs)
# - MySQL: keep total connections < 150 for most workloads
# - HTTP clients: match to concurrent request volume
# - Redis: usually 5-10 per instance is enough

# Warning signs of pool problems:
# - "connection timeout" errors under load
# - Response time spikes at regular intervals
# - Idle connections holding resources
# - Connection count hitting max_connections
```

### Async & Concurrency Patterns

```javascript
// BAD: Sequential when independent
const user = await getUser(id);
const orders = await getOrders(id);
const prefs = await getPreferences(id);
// Total: user_time + orders_time + prefs_time

// GOOD: Parallel when independent
const [user, orders, prefs] = await Promise.all([
  getUser(id),
  getOrders(id),
  getPreferences(id),
]);
// Total: max(user_time, orders_time, prefs_time)

// GOOD: Controlled concurrency for many items
// (npm: p-limit, p-map, or manual semaphore)
import pLimit from 'p-limit';
const limit = pLimit(10); // Max 10 concurrent
const results = await Promise.all(
  items.map(item => limit(() => processItem(item)))
);
```

```python
# Python: asyncio for I/O-bound
import asyncio

async def fetch_all(ids):
    # Parallel
    tasks = [fetch_one(id) for id in ids]
    return await asyncio.gather(*tasks)

# Python: ProcessPoolExecutor for CPU-bound
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(cpu_intensive_fn, items))
```

### N+1 Query Detection & Fix

```
SYMPTOM: Response time scales linearly with result count
DETECTION: Enable query logging, count queries per request

# Bad: N+1
users = db.query("SELECT * FROM users LIMIT 100")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")
# Result: 1 + 100 = 101 queries

# Fix 1: JOIN
SELECT u.*, o.* FROM users u
LEFT JOIN orders o ON o.user_id = u.id
LIMIT 100

# Fix 2: Batch load (better for large datasets)
users = db.query("SELECT * FROM users LIMIT 100")
user_ids = [u.id for u in users]
orders = db.query(f"SELECT * FROM orders WHERE user_id IN ({','.join(user_ids)})")
# Result: 2 queries regardless of count

# Fix 3: ORM eager loading
# Drizzle: .with(users.orders)
# SQLAlchemy: joinedload(User.orders)
# Prisma: include: { orders: true }
```

## Phase 4: Database Performance

### Query Optimization Checklist

```
For every slow query:
□ Run EXPLAIN ANALYZE (not just EXPLAIN)
□ Check: is it doing a sequential scan on a large table?
□ Check: is the row estimate accurate? (bad stats = bad plan)
□ Check: are there implicit type casts preventing index use?
□ Check: is it sorting more data than needed? (add LIMIT earlier)
□ Check: is it joining in the right order?
□ Check: can a covering index eliminate table lookups?
□ Check: is the query running during peak hours? (schedule if batch)
```

### EXPLAIN ANALYZE Interpretation

```sql
-- PostgreSQL EXPLAIN output reading guide:
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;

-- Key metrics to check:
-- 1. Actual time vs estimated time (large gap = stale stats → ANALYZE)
-- 2. Rows actual vs estimated (>10x off = bad stats)
-- 3. Seq Scan on large table (>10K rows) = needs index
-- 4. Sort with external merge = needs more work_mem or index
-- 5. Nested Loop with large outer = consider hash/merge join
-- 6. Buffers shared hit vs read (low hit ratio = needs more shared_buffers)
```

### Index Strategy Guide

```
WHEN TO ADD AN INDEX:
✓ WHERE clause column (equality or range)
✓ JOIN condition column
✓ ORDER BY column (if query is index-only scan candidate)
✓ Foreign key column (prevents table lock on parent delete)
✓ Column in a unique constraint

WHEN NOT TO ADD AN INDEX:
✗ Table has <1000 rows (seq scan is fine)
✗ Column has very low cardinality (boolean, status with 3 values)
✗ Write-heavy table where reads are rare
✗ You already have 8+ indexes on the table (diminishing returns, write penalty)

INDEX TYPES:
- B-tree (default): equality, range, sorting, LIKE 'prefix%'
- Hash: equality only (rarely better than B-tree)
- GIN: arrays, JSONB, full-text search
- GiST: geometry, range types, full-text
- BRIN: large tables with natural ordering (timestamps, sequential IDs)

COMPOSITE INDEX RULES:
1. Equality columns first, then range columns
2. Most selective column first (if all equality)
3. Index on (a, b) works for WHERE a=1 AND b=2 AND for WHERE a=1 alone
4. Index on (a, b) does NOT work for WHERE b=2 alone
```

## Phase 5: Load Testing

### Load Test Design

```yaml
# load-test-plan.yaml
test_name: ""
target: ""              # URL/endpoint
date: ""

scenarios:
  - name: "Baseline"
    description: "Normal traffic pattern"
    vus: 50               # Virtual users
    duration: "5m"
    ramp_up: "30s"
    think_time: "1-3s"    # Pause between requests

  - name: "Peak"
    description: "2x normal traffic (expected peak)"
    vus: 100
    duration: "10m"
    ramp_up: "1m"

  - name: "Stress"
    description: "Find the breaking point"
    vus_start: 50
    vus_end: 500
    step_duration: "2m"   # Add users every 2 min
    step_size: 50

  - name: "Soak"
    description: "Memory leaks, connection exhaustion"
    vus: 50
    duration: "2h"

pass_criteria:
  p95_response_ms: 500
  error_rate_pct: 0.1
  throughput_rps: 200
```

### k6 Load Test Template

```javascript
// load-test.js (run: k6 run load-test.js)
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up
    { duration: '3m', target: 20 },    // Steady
    { duration: '30s', target: 50 },   // Peak
    { duration: '3m', target: 50 },    // Steady peak
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% under 500ms
    errors: ['rate<0.01'],              // <1% error rate
  },
};

export default function () {
  const res = http.get('https://api.example.com/endpoint');

  check(res, {
    'status 200': (r) => r.status === 200,
    'response < 500ms': (r) => r.timings.duration < 500,
  });

  errorRate.add(res.status !== 200);
  responseTime.add(res.timings.duration);

  sleep(Math.random() * 2 + 1); // 1-3s think time
}
```

### Load Test Results Analysis

```
READING RESULTS:
┌──────────────────────────────────────────┐
│ Metric          │ Healthy │ Warning │ Bad│
├──────────────────────────────────────────┤
│ p50/p95 ratio   │ <2x     │ 2-5x    │>5x│  ← High ratio = tail latency problem
│ p95/p99 ratio   │ <2x     │ 2-3x    │>3x│  ← Outliers affecting some users
│ Error rate      │ <0.1%   │ 0.1-1%  │>1%│  ← Above 1% = user-visible
│ Throughput drop  │ <5%     │ 5-20%   │>20%│ ← System under stress
│ CPU at peak     │ <70%    │ 70-85%  │>85%│ ← No headroom
│ Memory at peak  │ <75%    │ 75-90%  │>90%│ ← Risk of OOM
│ GC pause time   │ <50ms   │ 50-200ms│>200ms│ ← GC storm
└──────────────────────────────────────────┘

BOTTLENECK IDENTIFICATION:
- Throughput plateaus but CPU is low → I/O bound (DB, network, disk)
- Throughput plateaus and CPU is high → CPU bound (optimize hot path)
- Response time climbs linearly → Queue building (capacity limit)
- Response time climbs exponentially → Resource exhaustion (connection pool, memory)
- Errors spike at specific VU count → Hard limit hit (max connections, file descriptors)
```

## Phase 6: Frontend Performance

### Core Web Vitals Optimization

```
METRIC      │ GOOD    │ NEEDS WORK │ POOR   │ HOW TO FIX
────────────┼─────────┼────────────┼────────┼────────────────────────
LCP         │ <2.5s   │ 2.5-4s     │ >4s    │ Optimize largest image/text
FID/INP     │ <100ms  │ 100-300ms  │ >300ms │ Break up long tasks, defer JS
CLS         │ <0.1    │ 0.1-0.25   │ >0.25  │ Set dimensions, font-display

LCP FIXES (in priority order):
1. Preload the LCP image: <link rel="preload" as="image" href="...">
2. Use responsive images: srcset with correct sizes
3. Serve WebP/AVIF (30-50% smaller)
4. Remove render-blocking CSS/JS from <head>
5. Use CDN for static assets
6. Server-side render the above-fold content

INP FIXES:
1. Break long tasks (>50ms) with requestIdleCallback or setTimeout(0)
2. Use web workers for CPU-intensive work
3. Debounce/throttle event handlers
4. Defer non-critical JS: <script defer> or dynamic import()
5. Avoid layout thrashing (batch DOM reads, then batch writes)

CLS FIXES:
1. Always set width/height on <img> and <video>
2. Use aspect-ratio CSS for dynamic content
3. Reserve space for ads/embeds
4. Use font-display: swap with size-adjusted fallback
5. Never insert content above existing content
```

### Bundle Optimization

```
ANALYSIS:
- Webpack: npx webpack-bundle-analyzer stats.json
- Vite: npx vite-bundle-visualizer
- Next.js: @next/bundle-analyzer

REDUCTION STRATEGIES (in order of impact):
1. Code splitting: dynamic import() for routes and heavy components
2. Tree shaking: use ESM imports, avoid barrel files (index.ts re-exports)
3. Replace heavy libraries:
   - moment.js (330KB) → date-fns (tree-shakeable) or dayjs (2KB)
   - lodash (530KB) → lodash-es (tree-shakeable) or native JS
   - chart.js → lightweight alternative for simple charts
4. Lazy load below-fold components
5. Externalize large deps to CDN (React, etc.)
6. Compress: Brotli > gzip (15-20% smaller)
```

## Phase 7: Infrastructure & Scaling

### Scaling Decision Framework

```
VERTICAL SCALING (scale up):
✓ Quick fix, no code changes
✓ Database servers (often best first move)
✓ Memory-bound workloads
✗ Diminishing returns past 8-16 cores
✗ Single point of failure
✗ Expensive at high end

HORIZONTAL SCALING (scale out):
✓ Stateless services (APIs, workers)
✓ Read-heavy workloads (read replicas)
✓ Geographic distribution
✗ Requires stateless design
✗ Adds complexity (load balancing, session management)
✗ Not all workloads parallelize

SCALING CHECKLIST:
□ Can we optimize the code first? (cheapest option)
□ Can we add caching? (often 10-100x improvement)
□ Can we add a read replica? (if read-heavy)
□ Can we queue and process async? (if latency-tolerant)
□ Can we scale vertically? (if CPU/memory bound)
□ Do we need horizontal scaling? (if all above exhausted)
```

### Auto-scaling Configuration

```yaml
# Kubernetes HPA example
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70    # Scale at 70% CPU
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60    # Wait 1m before scaling up
      policies:
        - type: Percent
          value: 50                      # Max 50% increase per step
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300   # Wait 5m before scaling down
      policies:
        - type: Percent
          value: 25                      # Max 25% decrease per step
          periodSeconds: 120
```

## Phase 8: Capacity Planning

### Capacity Model Template

```yaml
# capacity-model.yaml
service: ""
last_updated: ""

current_state:
  daily_requests: 0
  peak_rps: 0
  avg_response_ms: 0
  instances: 0
  cpu_peak_pct: 0
  memory_peak_pct: 0
  db_connections_peak: 0
  storage_used_gb: 0

growth_model:
  request_growth_monthly_pct: 0    # e.g., 15%
  storage_growth_monthly_gb: 0
  seasonal_peak_multiplier: 0      # e.g., 3x for Black Friday

projections:
  # Formula: current * (1 + growth_rate)^months * seasonal_multiplier
  3_month:
    daily_requests: 0
    peak_rps: 0
    instances_needed: 0
    storage_gb: 0
    estimated_cost: ""
  6_month:
    daily_requests: 0
    peak_rps: 0
    instances_needed: 0
    storage_gb: 0
    estimated_cost: ""
  12_month:
    daily_requests: 0
    peak_rps: 0
    instances_needed: 0
    storage_gb: 0
    estimated_cost: ""

headroom_rules:
  cpu: "Scale when sustained >70% for 5m"
  memory: "Scale when >80%"
  storage: "Alert when >75%, expand when >85%"
  db_connections: "Alert when >80% of max"
```

### Cost-Performance Tradeoff Analysis

```
For every optimization, calculate:

ROI = (time_saved_per_month × cost_per_hour) / implementation_cost

EXAMPLE:
- P95 latency: 800ms → 200ms after optimization
- Requests/month: 10M
- Time saved: 600ms × 10M = 1,667 hours of compute
- Compute cost: $0.05/hour = $83/month savings
- Implementation: 16 hours × $150/hr = $2,400
- Payback: 29 months ← NOT WORTH IT for cost alone

BUT ALSO CONSIDER:
- User experience improvement → conversion rate
- Reduced infrastructure needs → fewer instances
- Headroom for growth → delayed scaling investment
- Developer productivity → faster local dev cycles
```

## Phase 9: Performance in CI/CD

### Automated Performance Gates

```yaml
# .github/workflows/perf-gate.yml
name: Performance Gate
on: pull_request

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run benchmarks
        run: |
          # Run your benchmark suite
          npm run benchmark -- --json > bench-results.json

      - name: Compare with baseline
        run: |
          # Compare against main branch baseline
          node scripts/compare-benchmarks.js \
            --baseline benchmarks/baseline.json \
            --current bench-results.json \
            --threshold 10  # Fail if >10% regression

      - name: Load test (on staging)
        if: github.base_ref == 'main'
        run: |
          k6 run --out json=load-results.json tests/load-test.js
          # Check thresholds automatically via k6

      - name: Bundle size check
        run: |
          npm run build
          node scripts/check-bundle-size.js \
            --max-size 250KB \
            --max-increase 5%
```

### Performance Regression Detection

```
AUTOMATED CHECKS (run on every PR):
□ Unit benchmarks: critical path functions < threshold
□ Bundle size: total and per-chunk limits
□ Lighthouse CI: Core Web Vitals pass
□ Query count: no N+1 regressions (count queries per test)
□ Memory: no leak patterns in test suite

WEEKLY CHECKS (cron job):
□ Production p50/p95/p99 trends (compare to 4-week average)
□ Error rate trends
□ Database slow query log review
□ Infrastructure cost vs traffic ratio
□ Cache hit rates

MONTHLY REVIEW:
□ Capacity model update
□ Performance budget review
□ Top 10 slowest endpoints → optimization candidates
□ Cost-performance analysis
□ Load test full suite against staging
```

## Phase 10: Performance Culture

### Performance Review Checklist

Score your system (0-100):

```
MEASUREMENT (25 points):
□ (5) Performance budgets defined for all key metrics
□ (5) Real User Monitoring (RUM) in production
□ (5) Alerting on p95 degradation
□ (5) Dashboards visible to team
□ (5) Regular load testing

PREVENTION (25 points):
□ (5) Performance gates in CI/CD
□ (5) Bundle size limits enforced
□ (5) Query count checks in tests
□ (5) Code review includes perf review
□ (5) Capacity planning model maintained

OPTIMIZATION (25 points):
□ (5) Caching strategy documented
□ (5) Database indexes reviewed quarterly
□ (5) No known N+1 queries
□ (5) Connection pools properly sized
□ (5) Async patterns used for I/O

OPERATIONS (25 points):
□ (5) Auto-scaling configured and tested
□ (5) Slow query logging enabled
□ (5) Memory leak monitoring
□ (5) Performance incident runbook exists
□ (5) Monthly performance review
```

### Common Anti-Patterns

```
1. PREMATURE OPTIMIZATION
   Problem: Optimizing before measuring
   Fix: Profile first, optimize the measured bottleneck

2. MICRO-BENCHMARKING IN ISOLATION
   Problem: Function is fast alone but slow in context (cache, contention)
   Fix: Always benchmark in realistic conditions with realistic data

3. OPTIMIZING THE WRONG LAYER
   Problem: Tuning app code when the DB is the bottleneck
   Fix: Use distributed tracing to find the actual bottleneck

4. CACHING EVERYTHING
   Problem: Cache invalidation bugs, stale data, memory pressure
   Fix: Cache selectively using the decision matrix (Phase 3)

5. PREMATURE HORIZONTAL SCALING
   Problem: Adding instances when single instance is underoptimized
   Fix: Vertical optimization first, scale second

6. IGNORING TAIL LATENCY
   Problem: p50 is fine but p99 is terrible
   Fix: Investigate outliers — they're often the most important users

7. LOAD TESTING IN DEV
   Problem: Dev environment doesn't match production
   Fix: Load test against staging with production-like data

8. OPTIMIZING COLD PATHS
   Problem: Spending time on rarely-executed code
   Fix: Profile in production to find actual hot paths
```

## Quick Reference: Tool Selection

| Task | Recommended Tool | Alternative |
|------|-----------------|-------------|
| HTTP benchmarking | k6 | wrk, ab, hey |
| CPU profiling (Node) | clinic flame | 0x, --prof |
| CPU profiling (Python) | py-spy | Scalene, cProfile |
| CPU profiling (Go) | pprof | go tool trace |
| CPU profiling (Java) | async-profiler | JFR, VisualVM |
| Memory profiling | language-specific (see Phase 2) | |
| CLI benchmarking | hyperfine | time |
| Bundle analysis | webpack-bundle-analyzer | source-map-explorer |
| Web performance | Lighthouse | WebPageTest |
| DB query analysis | EXPLAIN ANALYZE | pgMustard, pganalyze |
| Distributed tracing | Jaeger, Zipkin | OpenTelemetry |
| APM | Datadog, New Relic | Grafana + Prometheus |
| Continuous profiling | Pyroscope | Parca |

## Natural Language Commands

```
"Profile this function"     → CPU profiling with flame graph
"Why is this endpoint slow" → Full investigation brief + profiling
"Load test the API"         → k6 test design and execution
"Check for memory leaks"    → Heap snapshot comparison workflow
"Optimize this query"       → EXPLAIN ANALYZE + index recommendations
"Review frontend perf"      → Core Web Vitals audit + bundle analysis
"Plan capacity for 10x"     → Capacity model with projections
"Set up perf monitoring"    → CI/CD gates + dashboards + alerts
"Find the bottleneck"       → Profiling decision tree walkthrough
"Score our performance"     → Performance review checklist (0-100)
"Compare before and after"  → Benchmark comparison methodology
"Reduce bundle size"        → Bundle analysis + reduction strategies
```
