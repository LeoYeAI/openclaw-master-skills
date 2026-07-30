---
name: perf-profiler
description: Profile and optimize application performance. Use when diagnosing slow code, measuring CPU/memory usage, generating flame graphs, benchmarking functions, load testing APIs, finding memory leaks, or optimizing database queries.
metadata: {"clawdbot":{"emoji":"⚡","requires":{"anyBins":["node","python3","go","curl","ab"]},"os":["linux","darwin","win32"]}}
---

# Performance Profiler

Measure, profile, and optimize application performance. Covers CPU profiling, memory analysis, flame graphs, benchmarking, load testing, and language-specific optimization patterns.

## When to Use

- Diagnosing why an application or function is slow
- Measuring CPU and memory usage
- Generating flame graphs to visualize hot paths
- Benchmarking functions or endpoints
- Load testing APIs before deployment
- Finding and fixing memory leaks
- Optimizing database query performance
- Comparing performance before and after changes

## Quick Timing

### Command-line timing

```bash
# Time any command
time my-command --flag

# More precise: multiple runs with stats
for i in $(seq 1 10); do
  /usr/bin/time -f "%e" my-command 2>&1
done | awk '{sum+=$1; sumsq+=$1*$1; count++} END {
  avg=sum/count;
  stddev=sqrt(sumsq/count - avg*avg);
  printf "runs=%d avg=%.3fs stddev=%.3fs\n", count, avg, stddev
}'

# Hyperfine (better benchmarking tool)
# Install: https://github.com/sharkdp/hyperfine
hyperfine 'command-a' 'command-b'
hyperfine --warmup 3 --runs 20 'my-command'
hyperfine --export-json results.json 'old-version' 'new-version'
```

### Inline timing (any language)

```javascript
// Node.js
console.time('operation');
await doExpensiveThing();
console.timeEnd('operation'); // "operation: 142.3ms"

// High-resolution
const start = performance.now();
await doExpensiveThing();
const elapsed = performance.now() - start;
console.log(`Elapsed: ${elapsed.toFixed(2)}ms`);
```

```python
# Python
import time

start = time.perf_counter()
do_expensive_thing()
elapsed = time.perf_counter() - start
print(f"Elapsed: {elapsed:.4f}s")

# Context manager
from contextlib import contextmanager

@contextmanager
def timer(label=""):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed:.4f}s")

with timer("data processing"):
    process_data()
```

```go
// Go
start := time.Now()
doExpensiveThing()
fmt.Printf("Elapsed: %v\n", time.Since(start))
```

## Node.js Profiling

### CPU profiling with V8 inspector

```bash
# Generate CPU profile (writes .cpuprofile file)
node --cpu-prof app.js
# Open the .cpuprofile in Chrome DevTools > Performance tab

# Profile for a specific duration
node --cpu-prof --cpu-prof-interval=100 app.js

# Inspect running process
node --inspect app.js
# Open chrome://inspect in Chrome, click "inspect"
# Go to Performance tab, click Record
```

### Heap snapshots (memory)

```bash
# Generate heap snapshot
node --heap-prof app.js

# Take snapshots programmatically
node -e "
const v8 = require('v8');
const fs = require('fs');

// Take snapshot
const snapshotStream = v8.writeHeapSnapshot();
console.log('Heap snapshot written to:', snapshotStream);
"

# Compare heap snapshots to find leaks:
# 1. Take snapshot A (baseline)
# 2. Run operations that might leak
# 3. Take snapshot B
# 4. In Chrome DevTools > Memory, load both and use "Comparison" view
```

### Memory usage monitoring

```javascript
// Print memory usage periodically
setInterval(() => {
  const usage = process.memoryUsage();
  console.log({
    rss: `${(usage.rss / 1024 / 1024).toFixed(1)}MB`,
    heapUsed: `${(usage.heapUsed / 1024 / 1024).toFixed(1)}MB`,
    heapTotal: `${(usage.heapTotal / 1024 / 1024).toFixed(1)}MB`,
    external: `${(usage.external / 1024 / 1024).toFixed(1)}MB`,
  });
}, 5000);

// Detect memory growth
let lastHeap = 0;
setInterval(() => {
  const heap = process.memoryUsage().heapUsed;
  const delta = heap - lastHeap;
  if (delta > 1024 * 1024) { // > 1MB growth
    console.warn(`Heap grew by ${(delta / 1024 / 1024).toFixed(1)}MB`);
  }
  lastHeap = heap;
}, 10000);
```

### Node.js benchmarking

```javascript
// Simple benchmark function
function benchmark(name, fn, iterations = 10000) {
  // Warmup
  for (let i = 0; i < 100; i++) fn();

  const start = performance.now();
  for (let i = 0; i < iterations; i++) fn();
  const elapsed = performance.now() - start;

  console.log(`${name}: ${(elapsed / iterations).toFixed(4)}ms/op (${iterations} iterations in ${elapsed.toFixed(1)}ms)`);
}

benchmark('JSON.parse', () => JSON.parse('{"key":"value","num":42}'));
benchmark('regex match', () => /^\d{4}-\d{2}-\d{2}$/.test('2026-02-03'));
```

## Python Profiling

### cProfile (built-in CPU profiler)

```bash
# Profile a script
python3 -m cProfile -s cumulative my_script.py

# Save to file for analysis
python3 -m cProfile -o profile.prof my_script.py

# Analyze saved profile
python3 -c "
import pstats
stats = pstats.Stats('profile.prof')
stats.sort_stats('cumulative')
stats.print_stats(20)
"

# Profile a specific function
python3 -c "
import cProfile
from my_module import expensive_function

cProfile.run('expensive_function()', sort='cumulative')
"
```

### line_profiler (line-by-line)

```bash
# Install
pip install line_profiler

# Add @profile decorator to functions of interest, then:
kernprof -l -v my_script.py
```

```python
# Programmatic usage
from line_profiler import LineProfiler

def process_data(data):
    result = []
    for item in data:           # Is this loop the bottleneck?
        transformed = transform(item)
        if validate(transformed):
            result.append(transformed)
    return result

profiler = LineProfiler()
profiler.add_function(process_data)
profiler.enable()
process_data(large_dataset)
profiler.disable()
profiler.print_stats()
```

### Memory profiling (Python)

```bash
# memory_profiler
pip install memory_profiler

# Profile memory line-by-line
python3 -m memory_profiler my_script.py
```

```python
from memory_profiler import profile

@profile
def load_data():
    data = []
    for i in range(1000000):
        data.append({'id': i, 'value': f'item_{i}'})
    return data

# Track memory over time
import tracemalloc

tracemalloc.start()

# ... run code ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

### Python benchmarking

```python
import timeit

# Time a statement
result = timeit.timeit('sorted(range(1000))', number=10000)
print(f"sorted: {result:.4f}s for 10000 iterations")

# Compare two approaches
setup = "data = list(range(10000))"
t1 = timeit.timeit('list(filter(lambda x: x % 2 == 0, data))', setup=setup, number=1000)
t2 = timeit.timeit('[x for x in data if x % 2 == 0]', setup=setup, number=1000)
print(f"filter: {t1:.4f}s  |  listcomp: {t2:.4f}s  |  speedup: {t1/t2:.2f}x")

# pytest-benchmark
# pip install pytest-benchmark
# def test_sort(benchmark):
#     benchmark(sorted, list(range(1000)))
```

## Go Profiling

### Built-in pprof

```go
// Add to main.go for HTTP-accessible profiling
import (
    "net/http"
    _ "net/http/pprof"
)

func main() {
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()
    // ... rest of app
}
```

```bash
# CPU profile (30 seconds)
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Memory profile
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine profile
go tool pprof http://localhost:6060/debug/pprof/goroutine

# Inside pprof interactive mode:
# top 20          - top functions by CPU/memory
# list funcName   - source code with annotations
# web             - open flame graph in browser
# png > out.png   - save call graph as image
```

### Go benchmarks

```go
// math_test.go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(42, 58)
    }
}

func BenchmarkSort1000(b *testing.B) {
    data := make([]int, 1000)
    for i := range data {
        data[i] = rand.Intn(1000)
    }
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        sort.Ints(append([]int{}, data...))
    }
}
```

```bash
# Run benchmarks
go test -bench=. -benchmem ./...

# Compare before/after
go test -bench=. -count=5 ./... > old.txt
# ... make changes ...
go test -bench=. -count=5 ./... > new.txt
go install golang.org/x/perf/cmd/benchstat@latest
benchstat old.txt new.txt
```

## Flame Graphs

### Generate flame graphs

```bash
# Node.js: 0x (easiest)
npx 0x app.js
# Opens interactive flame graph in browser

# Node.js: clinic.js (comprehensive)
npx clinic flame -- node app.js
npx clinic doctor -- node app.js
npx clinic bubbleprof -- node app.js

# Python: py-spy (sampling profiler, no code changes needed)
pip install py-spy
py-spy record -o flame.svg -- python3 my_script.py

# Profile running Python process
py-spy record -o flame.svg --pid 12345

# Go: built-in
go tool pprof -http=:8080 http://localhost:6060/debug/pprof/profile?seconds=30
# Navigate to "Flame Graph" view

# Linux (any process): perf + flamegraph
perf record -g -p PID -- sleep 30
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg
```

### Reading flame graphs

```
Key concepts:
- X-axis: NOT time. It's alphabetical sort of stack frames. Width = % of samples.
- Y-axis: Stack depth. Top = leaf function (where CPU time is spent).
- Wide bars at the top = hot functions (optimize these first).
- Narrow tall stacks = deep call chains (may indicate excessive abstraction).

What to look for:
1. Wide plateaus at the top → function that dominates CPU time
2. Multiple paths converging to one function → shared bottleneck
3. GC/runtime frames taking significant width → memory pressure
4. Unexpected functions appearing wide → performance bug
```

## Load Testing

### curl-based quick test

```bash
# Single request timing
curl -o /dev/null -s -w "HTTP %{http_code} | Total: %{time_total}s | TTFB: %{time_starttransfer}s | Connect: %{time_connect}s\n" https://api.example.com/endpoint

# Multiple requests in sequence
for i in $(seq 1 20); do
  curl -o /dev/null -s -w "%{time_total}\n" https://api.example.com/endpoint
done | awk '{sum+=$1; count++; if($1>max)max=$1} END {printf "avg=%.3fs max=%.3fs n=%d\n", sum/count, max, count}'
```

### Apache Bench (ab)

```bash
# 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:3000/api/endpoint

# With POST data
ab -n 100 -c 10 -p data.json -T application/json http://localhost:3000/api/endpoint

# Key metrics to watch:
# - Requests per second (throughput)
# - Time per request (latency)
# - Percentage of requests served within a certain time (p50, p90, p99)
```

### wrk (modern load testing)

```bash
# Install: https://github.com/wg/wrk
# 10 seconds, 4 threads, 100 connections
wrk -t4 -c100 -d10s http://localhost:3000/api/endpoint

# With Lua script for custom requests
wrk -t4 -c100 -d10s -s post.lua http://localhost:3000/api/endpoint
```

```lua
-- post.lua
wrk.method = "POST"
wrk.body   = '{"key": "value"}'
wrk.headers["Content-Type"] = "application/json"

-- Custom request generation
request = function()
  local id = math.random(1, 10000)
  local path = "/api/users/" .. id
  return wrk.format("GET", path)
end
```

### Autocannon (Node.js load testing)

```bash
npx autocannon -c 100 -d 10 http://localhost:3000/api/endpoint
npx autocannon -c 100 -d 10 -m POST -b '{"key":"value"}' -H 'Content-Type=application/json' http://localhost:3000/api/endpoint
```

## Database Query Performance

### EXPLAIN analysis

```bash
# PostgreSQL
psql -c "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT * FROM orders WHERE user_id = 123;"

# MySQL
mysql -e "EXPLAIN SELECT * FROM orders WHERE user_id = 123;" mydb

# SQLite
sqlite3 mydb.sqlite "EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id = 123;"
```

### Slow query detection

```bash
# PostgreSQL: enable slow query logging
# In postgresql.conf:
# log_min_duration_statement = 100  (ms)

# MySQL: slow query log
# In my.cnf:
# slow_query_log = 1
# long_query_time = 0.1

# Find queries missing indexes (PostgreSQL)
psql -c "
SELECT schemaname, relname, seq_scan, seq_tup_read,
       idx_scan, idx_tup_fetch,
       seq_tup_read / GREATEST(seq_scan, 1) AS avg_rows_per_scan
FROM pg_stat_user_tables
WHERE seq_scan > 100 AND seq_tup_read / GREATEST(seq_scan, 1) > 1000
ORDER BY seq_tup_read DESC
LIMIT 10;
"
```

## Memory Leak Detection Patterns

### Node.js

```javascript
// Track object counts over time
const v8 = require('v8');

function checkMemory() {
  const heap = v8.getHeapStatistics();
  const usage = process.memoryUsage();
  return {
    heapUsedMB: (usage.heapUsed / 1024 / 1024).toFixed(1),
    heapTotalMB: (usage.heapTotal / 1024 / 1024).toFixed(1),
    rssMB: (usage.rss / 1024 / 1024).toFixed(1),
    externalMB: (usage.external / 1024 / 1024).toFixed(1),
    arrayBuffersMB: (usage.arrayBuffers / 1024 / 1024).toFixed(1),
  };
}

// Sample every 10s, alert on growth
let baseline = process.memoryUsage().heapUsed;
setInterval(() => {
  const current = process.memoryUsage().heapUsed;
  const growthMB = (current - baseline) / 1024 / 1024;
  if (growthMB > 50) {
    console.warn(`Memory grew ${growthMB.toFixed(1)}MB since start`);
    console.warn(checkMemory());
  }
}, 10000);
```

### Common leak patterns

```
Node.js:
- Event listeners not removed (emitter.on without emitter.off)
- Closures capturing large objects in long-lived scopes
- Global caches without eviction (Map/Set that only grows)
- Unresolved promises accumulating

Python:
- Circular references (use weakref for caches)
- Global lists/dicts that grow unbounded
- File handles not closed (use context managers)
- C extension objects not properly freed

Go:
- Goroutine leaks (goroutine started, never returns)
- Forgotten channel listeners
- Unclosed HTTP response bodies
- Global maps that grow forever
```

## Performance Comparison Script

```bash
#!/bin/bash
# perf-compare.sh - Compare performance before/after a change
# Usage: perf-compare.sh <command> [runs]
CMD="${1:?Usage: perf-compare.sh <command> [runs]}"
RUNS="${2:-10}"

echo "Benchmarking: $CMD"
echo "Runs: $RUNS"
echo ""

times=()
for i in $(seq 1 "$RUNS"); do
  start=$(date +%s%N)
  eval "$CMD" > /dev/null 2>&1
  end=$(date +%s%N)
  elapsed=$(echo "scale=3; ($end - $start) / 1000000" | bc)
  times+=("$elapsed")
  printf "  Run %2d: %sms\n" "$i" "$elapsed"
done

echo ""
printf '%s\n' "${times[@]}" | awk '{
  sum += $1
  sumsq += $1 * $1
  if (NR == 1 || $1 < min) min = $1
  if (NR == 1 || $1 > max) max = $1
  count++
} END {
  avg = sum / count
  stddev = sqrt(sumsq/count - avg*avg)
  printf "Results: avg=%.1fms min=%.1fms max=%.1fms stddev=%.1fms (n=%d)\n", avg, min, max, stddev, count
}'
```

## Tips

- **Profile before optimizing.** Guessing where bottlenecks are is wrong more often than right. Measure first.
- **Optimize the hot path.** Flame graphs show you exactly which functions consume the most time. A 10% improvement in a function that takes 80% of CPU time is worth more than a 50% improvement in one that takes 2%.
- **Memory and CPU are different problems.** A memory leak can exist in fast code. A CPU bottleneck can exist in code with stable memory. Profile both independently.
- **Benchmark under realistic conditions.** Microbenchmarks (empty loops, single-function timing) can be misleading due to JIT optimization, caching, and branch prediction. Use realistic data and workloads.
- **p99 matters more than average.** An API with 50ms average but 2s p99 has a tail latency problem. Always look at percentiles, not just averages.
- **Load test before shipping.** `ab`, `wrk`, or `autocannon` for 60 seconds at expected peak traffic reveals problems that unit tests never will.
- **GC pauses are real.** In Node.js, Python, Go, and Java, garbage collection can cause latency spikes. If flame graphs show significant GC time, reduce allocation pressure (reuse objects, use object pools, avoid unnecessary copies).
- **Database queries are usually the bottleneck.** Before optimizing application code, run `EXPLAIN` on your slowest queries. An index can turn a 2-second query into 2ms.
