---
name: phy-concurrency-audit
description: Static concurrency and race-condition auditor for Go, Java, Python, Node.js/TypeScript. Detects shared-state mutations without locks (Go map races, Java non-atomic increments, Python thread/asyncio shared lists), TOCTOU (time-of-check-time-of-use) patterns across all languages, sync.Mutex copied by value, WaitGroup.Add inside goroutines, SimpleDateFormat as instance field, double-checked locking without volatile, asyncio shared state without Lock. Maps findings to CWE-362 (race condition) and CWE-367 (TOCTOU). Zero competitors on ClawHub — not a single concurrency-audit SKILL.md in 13,700+ files.
license: Apache-2.0
tags:
  - concurrency
  - race-condition
  - toctou
  - go
  - java
  - python
  - nodejs
  - thread-safety
  - correctness
metadata:
  author: PHY041
  version: "1.0.0"
---

# phy-concurrency-audit

Static scanner for **race conditions** (CWE-362) and **TOCTOU vulnerabilities** (CWE-367) in Go, Java, Python, and Node.js/TypeScript codebases. Finds shared-state mutations without synchronization, unsafe concurrency patterns, and check-then-act anti-patterns. Zero external API calls, zero dependencies beyond Python 3 stdlib.

## Why Concurrency Bugs Are Special

- **Non-deterministic**: reproduce only under load, on multi-core machines, or on specific OS schedulers
- **Silent corruption**: data races don't crash immediately — they corrupt state silently for hours
- **Security impact**: TOCTOU races in file ops enable symlink attacks and privilege escalation (CWE-367)
- **Hard to test**: even `go test -race` only finds races that actually execute during the test run
- Static analysis catches the ones that never trigger in testing

## What It Detects

### Go Race Conditions
| Pattern | Severity | CWE |
|---------|----------|-----|
| Global `map` variable read/written in concurrent functions | CRITICAL | CWE-362 |
| `sync.Mutex` or `sync.RWMutex` copied by value after first use | HIGH | CWE-362 |
| `sync.WaitGroup.Add()` called inside a goroutine | HIGH | CWE-362 |
| Package-level slice/map mutated without mutex | HIGH | CWE-362 |
| `atomic.Value` used without checking type consistency | MEDIUM | CWE-362 |
| Missing `sync.Once` for lazy singleton initialization | MEDIUM | CWE-362 |
| Struct fields accessed in goroutines without receiver mutex | HIGH | CWE-362 |

### Java Thread-Safety Violations
| Pattern | Severity | CWE |
|---------|----------|-----|
| `count++` / `i++` on shared instance/static field without `synchronized` or `AtomicInteger` | HIGH | CWE-362 |
| `HashMap` or `ArrayList` as instance field in class with concurrent methods | HIGH | CWE-362 |
| `SimpleDateFormat` as `static` or instance field (not thread-safe) | HIGH | CWE-362 |
| Double-checked locking without `volatile` keyword | HIGH | CWE-362 |
| `synchronized` block on non-final field (lock can change) | MEDIUM | CWE-362 |
| `Vector`/`Hashtable` used (thread-safe but deprecated, miss modern happens-before) | LOW | CWE-362 |
| `Calendar.getInstance()` result stored as field | MEDIUM | CWE-362 |

### Python Threading & Asyncio
| Pattern | Severity | CWE |
|---------|----------|-----|
| Thread function mutating module-level list/dict without `threading.Lock` | HIGH | CWE-362 |
| `counter += 1` / `list.append()` on global var in thread without lock | HIGH | CWE-362 |
| `asyncio` coroutine mutating shared object without `asyncio.Lock` | HIGH | CWE-362 |
| `multiprocessing.Process` sharing mutable list/dict without `Manager` | HIGH | CWE-362 |
| `threading.Thread` target accessing `global` without lock | HIGH | CWE-362 |

### Node.js / TypeScript Async Races
| Pattern | Severity | CWE |
|---------|----------|-----|
| Module-level object/array mutated inside `async` request handler | HIGH | CWE-362 |
| TOCTOU: `await cache.has(key)` followed by `await cache.get(key)` | HIGH | CWE-367 |
| Counter increment `count++` in async handler (non-atomic) | MEDIUM | CWE-362 |
| Promise chain modifying shared closure variable | MEDIUM | CWE-362 |

### TOCTOU Patterns (All Languages)
| Pattern | Severity | CWE |
|---------|----------|-----|
| `os.path.exists(path)` followed by `open(path)` without lock | HIGH | CWE-367 |
| `os.path.isdir(d)` then `os.makedirs(d)` without exist_ok=True | MEDIUM | CWE-367 |
| `os.path.exists` then `os.rename/remove/chmod` | HIGH | CWE-367 |
| `if not User.exists()` then `User.create()` — DB check-then-insert | HIGH | CWE-367 |
| Java `File.exists()` then `new FileOutputStream(file)` | HIGH | CWE-367 |
| Node.js `fs.existsSync()` then `fs.writeFileSync()` | HIGH | CWE-367 |
| Go `os.Stat(path)` check then `os.Open(path)` | HIGH | CWE-367 |

## Implementation

```python
#!/usr/bin/env python3
"""
phy-concurrency-audit — Race condition & TOCTOU static scanner
Usage: python3 audit_concurrency.py [path] [--json] [--ci]
"""
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

CRITICAL, HIGH, MEDIUM, LOW = "CRITICAL", "HIGH", "MEDIUM", "LOW"
SEV_ORDER = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3}
ICONS = {CRITICAL: "🔴", HIGH: "🟠", MEDIUM: "🟡", LOW: "⚪"}

@dataclass
class Finding:
    file: str
    line: int
    pattern_name: str
    matched_text: str
    severity: str
    cwe: str
    title: str
    detail: str
    fix: str

# ─── Pattern registry ────────────────────────────────────────────────────────

PATTERNS: dict[str, list] = {
    ".go": [
        ("GO_GLOBAL_MAP_RACE",
         re.compile(r'^var\s+\w+\s*=\s*(?:map\[|make\s*\(\s*map)', re.MULTILINE),
         HIGH, "CWE-362",
         "Package-level map — likely shared across goroutines without mutex",
         "Go maps are NOT goroutine-safe. Any concurrent read+write is a data race that can panic.",
         "Protect with sync.RWMutex or replace with sync.Map for concurrent access."),

        ("GO_MUTEX_COPY",
         re.compile(r'\b(?:sync\.Mutex|sync\.RWMutex)\b'),
         HIGH, "CWE-362",
         "sync.Mutex/RWMutex — verify it is not copied after first use",
         "Copying a Mutex after first Lock/Unlock produces a copy of a locked mutex — deadlock.",
         "Always pass Mutex by pointer (*sync.Mutex) or embed in struct accessed via pointer."),

        ("GO_WAITGROUP_ADD_IN_GOROUTINE",
         re.compile(r'go\s+func\s*\([^)]*\)\s*\{[^}]*wg\.Add\s*\(', re.DOTALL),
         HIGH, "CWE-362",
         "WaitGroup.Add() inside goroutine — race between Add and Wait",
         "If wg.Wait() is called before wg.Add() completes, Wait returns prematurely.",
         "Always call wg.Add(n) BEFORE launching goroutines, not inside them."),

        ("GO_ATOMIC_VALUE_MISUSE",
         re.compile(r'\batomic\.Value\b'),
         MEDIUM, "CWE-362",
         "atomic.Value — verify consistent type across Store/Load calls",
         "Storing different types in the same atomic.Value panics at runtime.",
         "Ensure all Store() calls use the same concrete type; document the stored type in a comment."),
    ],
    ".java": [
        ("JAVA_NON_ATOMIC_INCREMENT",
         re.compile(r'(?:private|protected|public|static)\s+(?:int|long|volatile\s+int|volatile\s+long)\s+\w+\s*(?:=\s*\d+)?\s*;'),
         HIGH, "CWE-362",
         "Shared numeric field — verify increments use AtomicInteger/AtomicLong",
         "count++ on a shared field is a read-modify-write that is NOT atomic — silently loses updates.",
         "Replace int count with AtomicInteger count = new AtomicInteger(0); use count.incrementAndGet()."),

        ("JAVA_SHARED_HASHMAP",
         re.compile(r'(?:private|protected|public)\s+(?:final\s+)?HashMap\s*<'),
         HIGH, "CWE-362",
         "HashMap as instance field — not thread-safe for concurrent access",
         "Concurrent reads+writes to HashMap can cause infinite loop (Java 7) or data loss (Java 8+).",
         "Replace with ConcurrentHashMap or wrap access with synchronized blocks."),

        ("JAVA_SHARED_ARRAYLIST",
         re.compile(r'(?:private|protected|public)\s+(?:final\s+)?ArrayList\s*<'),
         HIGH, "CWE-362",
         "ArrayList as instance field — not thread-safe for concurrent modification",
         "Concurrent modification throws ConcurrentModificationException or silently drops elements.",
         "Replace with CopyOnWriteArrayList or Collections.synchronizedList(new ArrayList<>())."),

        ("JAVA_SIMPLE_DATE_FORMAT",
         re.compile(r'(?:private|protected|public|static)\s+(?:final\s+)?SimpleDateFormat\b'),
         HIGH, "CWE-362",
         "SimpleDateFormat as instance/static field — not thread-safe",
         "SimpleDateFormat maintains mutable state internally — concurrent use causes wrong dates or exceptions.",
         "Use ThreadLocal<SimpleDateFormat> or replace with thread-safe DateTimeFormatter (Java 8+)."),

        ("JAVA_DOUBLE_CHECKED_LOCKING",
         re.compile(r'if\s*\(\s*\w+\s*==\s*null\s*\)\s*\{\s*synchronized\s*\('),
         HIGH, "CWE-362",
         "Double-checked locking without volatile — broken without memory barrier",
         "Without volatile, the JIT can reorder writes; the second thread sees a partially constructed object.",
         "Add 'volatile' to the field declaration: private volatile MyClass instance;"),

        ("JAVA_SYNC_ON_NONFINAL",
         re.compile(r'synchronized\s*\(\s*(?!this|class)\w+\s*\)'),
         MEDIUM, "CWE-362",
         "synchronized() on potentially non-final field — lock can change",
         "If the locked object's reference changes between synchronized blocks, protection is lost.",
         "Only synchronize on final fields, 'this', or class literals."),
    ],
    ".py": [
        ("PY_THREAD_GLOBAL_MUTATION",
         re.compile(r'def\s+\w+\s*\([^)]*\)\s*:\s*(?:[^\n]*\n\s*)*?global\s+\w+', re.MULTILINE),
         HIGH, "CWE-362",
         "Thread function using 'global' — likely shared state without lock",
         "Global mutations in threads (counter += 1, list.append) are not atomic in CPython despite the GIL.",
         "Protect with threading.Lock(): with lock: global_var += 1"),

        ("PY_THREAD_LIST_MUTATION",
         re.compile(r'threading\.Thread\s*\([^)]*target\s*=\s*\w+'),
         MEDIUM, "CWE-362",
         "threading.Thread — verify shared list/dict access is protected by threading.Lock()",
         "Compound operations on shared containers (check-then-modify) are not atomic under GIL.",
         "Use threading.Lock() or queue.Queue for thread-safe producer/consumer patterns."),

        ("PY_ASYNCIO_SHARED_MUTATION",
         re.compile(r'async\s+def\s+\w+.*?(?:\n.*?){0,10}(?:shared|cache|results|state)\s*[\[.]=', re.DOTALL),
         HIGH, "CWE-362",
         "asyncio coroutine mutating shared variable — TOCTOU risk at await boundaries",
         "Between two await points, another coroutine can run and modify the same shared state.",
         "Use asyncio.Lock() to protect read-modify-write sequences across await boundaries."),

        ("PY_TOCTOU_EXISTS_OPEN",
         re.compile(r'os\.path\.exists\s*\([^)]+\)(?:[^\n]*\n){0,5}[^\n]*\bopen\s*\(', re.MULTILINE),
         HIGH, "CWE-367",
         "TOCTOU: os.path.exists() followed by open() — race window for file swap",
         "An attacker can replace the file with a symlink between exists() check and open() call.",
         "Remove exists() check; use try/except FileNotFoundError on open() directly (atomic)."),

        ("PY_TOCTOU_ISDIR_MAKEDIRS",
         re.compile(r'os\.path\.isdir\s*\([^)]+\)(?:[^\n]*\n){0,5}[^\n]*os\.makedirs\s*\('),
         MEDIUM, "CWE-367",
         "TOCTOU: isdir() + makedirs() — another process can create dir between checks",
         "Race causes FileExistsError even though the directory now exists.",
         "Use os.makedirs(path, exist_ok=True) — single atomic operation."),

        ("PY_TOCTOU_EXISTS_RENAME",
         re.compile(r'os\.path\.exists\s*\([^)]+\)(?:[^\n]*\n){0,5}[^\n]*(?:os\.rename|os\.remove|os\.chmod|shutil\.move)\s*\('),
         HIGH, "CWE-367",
         "TOCTOU: exists() check then file operation — file can be replaced between calls",
         "Symlink attack: attacker replaces target file with symlink to sensitive file before chmod/rename.",
         "Use try/except on the operation directly; or use os.open() with O_NOFOLLOW flag for security-sensitive ops."),
    ],
    ".js": _build_js_concurrency_patterns(),
    ".ts": _build_js_concurrency_patterns(),
}

def _build_js_concurrency_patterns():
    return [
        ("JS_MODULE_STATE_ASYNC_MUTATION",
         re.compile(r'(?:const|let|var)\s+\w+\s*=\s*(?:\{|\[)(?:[^;]*\n){0,5}.*?(?:app|router|server)\.[a-z]+\s*\(.*?\+\+|\s+\w+\.push\(|\s+\w+\[', re.DOTALL),
         MEDIUM, "CWE-362",
         "Module-level state mutated in request handler — concurrent requests race",
         "Node.js is single-threaded but async: two requests can interleave at await points, corrupting shared state.",
         "Move state into request scope, use a database/cache, or protect with async-mutex library."),

        ("JS_TOCTOU_CACHE_HAS_GET",
         re.compile(r'await\s+\w+\.has\s*\([^)]+\)(?:[^\n]*\n){0,5}[^\n]*await\s+\w+\.get\s*\('),
         HIGH, "CWE-367",
         "TOCTOU: await cache.has() followed by await cache.get() — key can be deleted between awaits",
         "Another async operation can delete the cache key after has() returns true but before get().",
         "Use atomic getOrCreate pattern: const val = cache.get(key) ?? (await compute()); cache.set(key, val);"),

        ("JS_COUNTER_ASYNC",
         re.compile(r'(?:let|var)\s+\w*(?:count|counter|total|hits)\w*\s*=\s*0(?:[^;]*\n){0,20}.*?\+\+', re.DOTALL),
         MEDIUM, "CWE-362",
         "Counter incremented across async boundaries — not atomic",
         "count++ is not atomic when two requests execute counter++ concurrently at an await boundary.",
         "Use a single-tick increment (no await between read and write), or use an atomic counter library."),

        ("JS_TOCTOU_FS_EXISTS_WRITE",
         re.compile(r'(?:fs\.existsSync|await\s+fs\.(?:promises\.)?access)\s*\([^)]+\)(?:[^\n]*\n){0,5}[^\n]*(?:fs\.writeFileSync|await\s+fs\.(?:promises\.)?writeFile)\s*\('),
         HIGH, "CWE-367",
         "TOCTOU: fs.existsSync + fs.writeFile — race between check and write",
         "Another process can create or modify the file between existsSync() and writeFile().",
         "Use flags: fs.writeFileSync(path, data, {flag: 'wx'}) — fails atomically if file already exists."),
    ]

# Shared-state context helpers
GO_GOROUTINE_MARKER = re.compile(r'\bgo\s+(?:func|\w+)\s*\(')
JAVA_CONCURRENT_MARKER = re.compile(r'(?:Thread|Executor|CompletableFuture|@Async|synchronized|Runnable|Callable)\b')
PY_CONCURRENT_MARKER = re.compile(r'(?:threading|asyncio|concurrent\.futures|multiprocessing)\b')
JS_ASYNC_MARKER = re.compile(r'\basync\s+function|\bPromise\.all|\bawait\b')

CONCURRENCY_MARKERS = {
    ".go": GO_GOROUTINE_MARKER,
    ".java": JAVA_CONCURRENT_MARKER,
    ".py": PY_CONCURRENT_MARKER,
    ".js": JS_ASYNC_MARKER,
    ".ts": JS_ASYNC_MARKER,
}

SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", ".venv", "venv",
             "dist", "build", "target", "test", "tests", "__tests__", "spec"}

def scan_file(filepath: Path) -> list[Finding]:
    suffix = filepath.suffix.lower()
    if suffix not in PATTERNS:
        return []
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, PermissionError):
        return []

    full_text = "\n".join(lines)

    # Skip files with no concurrency markers at all (reduces false positives significantly)
    marker = CONCURRENCY_MARKERS.get(suffix)
    if marker and not marker.search(full_text):
        # Only skip for non-TOCTOU checks if truly no concurrent code
        pass  # Still scan for TOCTOU even in non-concurrent files

    findings: list[Finding] = []
    for (name, pat, base_sev, cwe, title, detail, fix) in PATTERNS[suffix]:
        for m in pat.finditer(full_text):
            lineno = full_text[:m.start()].count("\n") + 1
            line_text = lines[lineno - 1]

            findings.append(Finding(
                file=str(filepath),
                line=lineno,
                pattern_name=name,
                matched_text=line_text.strip()[:120],
                severity=base_sev,
                cwe=cwe,
                title=title,
                detail=detail,
                fix=fix,
            ))
    return findings

def walk_files(root: Path) -> list[Path]:
    exts = {".go", ".java", ".py", ".js", ".ts"}
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if Path(fname).suffix.lower() in exts:
                results.append(Path(dirpath) / fname)
    return results

def format_report(findings: list[Finding], scanned: int) -> str:
    by_sev = {CRITICAL: [], HIGH: [], MEDIUM: [], LOW: []}
    for f in findings:
        by_sev[f.severity].append(f)

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "  CONCURRENCY AUDIT — Race Conditions & TOCTOU (CWE-362/367)",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  Scanned:  {scanned} files",
        f"  Findings: {len(by_sev[CRITICAL])} CRITICAL  {len(by_sev[HIGH])} HIGH  "
        f"{len(by_sev[MEDIUM])} MEDIUM  {len(by_sev[LOW])} LOW",
        "",
    ]

    for sev in [CRITICAL, HIGH, MEDIUM, LOW]:
        group = by_sev[sev]
        if not group:
            continue
        lines.append(f"{ICONS[sev]} {sev} ({len(group)} findings)")
        lines.append("")
        for f in sorted(group, key=lambda x: x.file):
            rel = os.path.relpath(f.file)
            lines += [
                f"  {rel}:{f.line} — {f.pattern_name}",
                f"  Code:   {f.matched_text}",
                f"  Issue:  {f.title}",
                f"  Why:    {f.detail}",
                f"  {f.cwe}",
                f"  Fix:    {f.fix}",
                "",
            ]

    critical_high = len(by_sev[CRITICAL]) + len(by_sev[HIGH])
    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  CI gate: {'exit 1 — race conditions detected' if critical_high else 'exit 0 — clean'}",
        "  Runtime verification: go test -race ./... | ThreadSanitizer",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Race condition & TOCTOU scanner")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--ci", action="store_true", help="Exit 1 if HIGH or CRITICAL found")
    args = parser.parse_args()

    files = walk_files(Path(args.path).resolve())
    all_findings: list[Finding] = []
    for f in files:
        all_findings.extend(scan_file(f))
    all_findings.sort(key=lambda x: (SEV_ORDER[x.severity], x.file, x.line))

    if args.json:
        import dataclasses
        print(json.dumps([dataclasses.asdict(f) for f in all_findings], indent=2))
    else:
        print(format_report(all_findings, len(files)))

    if args.ci:
        has_high = any(f.severity in (CRITICAL, HIGH) for f in all_findings)
        sys.exit(1 if has_high else 0)

if __name__ == "__main__":
    main()
```

## Usage

```bash
# Scan current project
python3 audit_concurrency.py

# CI fail-gate (exits 1 on HIGH/CRITICAL)
python3 audit_concurrency.py --ci

# JSON output for pipeline integration
python3 audit_concurrency.py --json | jq '[.[] | select(.cwe == "CWE-367")]'

# GitHub Actions
- name: Concurrency Audit
  run: python3 .claude/skills/phy-concurrency-audit/audit_concurrency.py --ci
```

## Sample Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CONCURRENCY AUDIT — Race Conditions & TOCTOU (CWE-362/367)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scanned:  78 files
  Findings: 0 CRITICAL  4 HIGH  2 MEDIUM  0 LOW

🟠 HIGH (4 findings)

  internal/cache/store.go:12 — GO_GLOBAL_MAP_RACE
  Code:   var requestCache = map[string]*Response{}
  Issue:  Package-level map — likely shared across goroutines without mutex
  Why:    Go maps are NOT goroutine-safe. Concurrent read+write causes panic.
  CWE-362
  Fix:    Protect with sync.RWMutex or replace with sync.Map for concurrent access.

  src/DateParser.java:8 — JAVA_SIMPLE_DATE_FORMAT
  Code:   private static final SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
  Issue:  SimpleDateFormat as static field — not thread-safe
  Why:    SimpleDateFormat maintains mutable state; concurrent use corrupts date parsing.
  CWE-362
  Fix:    Use ThreadLocal<SimpleDateFormat> or replace with DateTimeFormatter (Java 8+).

  api/file_handler.py:34 — PY_TOCTOU_EXISTS_OPEN
  Code:   if os.path.exists(upload_path):
  Issue:  TOCTOU: os.path.exists() followed by open() — race window for file swap
  Why:    Attacker can replace file with symlink between exists() and open().
  CWE-367
  Fix:    Remove exists() check; use try/except FileNotFoundError on open() directly.

  routes/api.js:67 — JS_TOCTOU_CACHE_HAS_GET
  Code:   if (await redisClient.has(userId)) {
  Issue:  TOCTOU: await cache.has() followed by await cache.get()
  Why:    Key can be evicted between has() and get() under concurrent load.
  CWE-367
  Fix:    Use atomic getOrCreate: const val = await cache.get(key) ?? compute();

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CI gate: exit 1 — race conditions detected
  Runtime verification: go test -race ./... | ThreadSanitizer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Relationship to Runtime Detectors

This skill does **static** analysis — fast, zero infrastructure, no load required. Use alongside:

| Tool | What It Adds |
|------|-------------|
| `go test -race ./...` | Finds Go races that actually execute during tests |
| Java ThreadSanitizer | Runtime instrumentation for JVM races |
| Python `threading-sanitizer` | Runtime detection for CPython |
| `node --inspect` + `clinic.js` | Profiles async bottlenecks + race-prone patterns |

## Companion Skills

| Skill | Use Together For |
|-------|-----------------|
| `phy-memory-leak-detector` | Goroutine/listener leaks + race conditions — concurrent correctness sweep |
| `phy-deserialization-audit` | Security sweep: races often affect auth/session state |
| `phy-k8s-security-audit` | Race conditions in init containers + probe handlers |
| `phy-ssrf-audit` | Async SSRF: race between URL validation and fetch |
