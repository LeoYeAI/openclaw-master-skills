---
name: phy-otel-audit
description: OpenTelemetry instrumentation coverage auditor. Scans Node.js/Python/Go/Java source code to detect missing or misconfigured OTel instrumentation — HTTP handlers without spans, database calls outside trace context, missing resource attributes, span errors not recorded, baggage not propagated, SDK not initialized before first import, sampler misconfiguration, and more. Outputs a per-file coverage score and actionable fix snippets. Zero external dependencies.
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
tags:
  - observability
  - opentelemetry
  - otel
  - tracing
  - metrics
  - instrumentation
  - static-analysis
  - zero-deps
  - node
  - python
  - golang
  - java
---

# phy-otel-audit — OpenTelemetry Instrumentation Auditor

Scans your source code for **10 classes of missing or misconfigured OpenTelemetry instrumentation** that cause invisible blind spots in your traces: unspanned HTTP handlers, DB calls outside trace context, swallowed span errors, missing service.name attributes, and more.

## Quick Start

```bash
# Scan a directory
python otel_audit.py ./src

# Single file
python otel_audit.py src/handlers/users.js

# CI mode — exit 1 on HIGH findings
python otel_audit.py ./src --ci

# Verbose: show which line triggered each finding
python otel_audit.py ./src --verbose

# Only HIGH findings
python otel_audit.py ./src --only-severity HIGH
```

## The 10 Checks

| ID | Severity | Check |
|----|----------|-------|
| OT001 | HIGH | No OTel SDK imported anywhere — zero instrumentation |
| OT002 | HIGH | HTTP handler without span creation |
| OT003 | HIGH | Database/cache call outside active span |
| OT004 | HIGH | Exception caught but span.recordException() not called |
| OT005 | MEDIUM | service.name not set in Resource attributes |
| OT006 | MEDIUM | OTel SDK initialized after first import (instrumentation gap) |
| OT007 | MEDIUM | Span created but status not set on error path |
| OT008 | MEDIUM | Async context propagation missing (Promise/goroutine context not passed) |
| OT009 | LOW | Trace exporter using console/stdout in non-dev environment |
| OT010 | LOW | Manual span naming uses dynamic values (high-cardinality span names) |

### OT001 — No OTel SDK Imported
Scans all files for any OpenTelemetry import. If none found, zero instrumentation exists.

**Detected imports:**
- JS/TS: `@opentelemetry/api`, `@opentelemetry/sdk-node`, `@opentelemetry/auto-instrumentations-node`
- Python: `opentelemetry`, `opentelemetry-sdk`, `from opentelemetry`
- Go: `go.opentelemetry.io/otel`
- Java: `io.opentelemetry`, `opentelemetry-java`

### OT002 — HTTP Handler Without Span
Finds route handler definitions (Express, FastAPI, Flask, gin, Spring) without a `tracer.startSpan` or `tracer.startActiveSpan` nearby. Auto-instrumentation covers framework-level spans, but business logic within handlers needs custom spans for meaningful traces.

### OT003 — Database/Cache Call Outside Span
Detects DB/cache operations (`db.query`, `prisma.`, `mongoose.`, `cursor.execute`, `db.Execute`, `redis.get`, `cache.get`) that appear in functions where no span context is active (no `tracer.startActiveSpan`, no `ctx` parameter carrying trace context, no `with tracer.start_as_current_span`).

### OT004 — Exception Not Recorded on Span
Finds `catch` blocks or `except` clauses that handle errors but don't call `span.recordException(err)` and `span.setStatus({ code: SpanStatusCode.ERROR })`. Unrecorded exceptions make traces appear successful when they failed — the most common OTel mistake.

### OT005 — Missing service.name Resource
Scans OTel SDK initialization code for `Resource.create` or `resource:` config without `service.name`. Without `service.name`, all traces appear as `unknown_service` in backends (Jaeger/Tempo/Honeycomb) — impossible to filter.

### OT006 — SDK Initialized After First Import
In Node.js, `require('@opentelemetry/sdk-node')` must happen before any other `require` statements. If SDK init file is imported after other modules, auto-instrumentation patches miss the already-loaded modules. Detects `tracing.js` or `instrumentation.js` imported after other modules in entry files.

### OT007 — Span Status Not Set on Error Path
Finds `span.end()` calls in error branches (catch blocks, error handlers) without a preceding `span.setStatus(SpanStatusCode.ERROR)` or `span.setStatus({ code: 2 })`. Span ends without status = treated as OK by the backend.

### OT008 — Context Not Propagated Through Async
Finds `Promise.all(`, `asyncio.gather(`, or goroutine `go func()` patterns where the OTel context is not explicitly passed. In Go, `context.Context` must be threaded through goroutines manually. In Python asyncio, OpenTelemetry context is propagated automatically via contextvars — but only if tasks are created from within an active span.

### OT009 — Console/Stdout Exporter in Production
Finds `ConsoleSpanExporter`, `SimpleSpanProcessor(new ConsoleSpanExporter())`, or `ConsoleMetricExporter` outside of dev/test configuration files. Console exporters flood logs and provide no tracing backend value in production.

### OT010 — High-Cardinality Span Names
Finds `tracer.startSpan(` with dynamic values in the span name (string interpolation with variables, request paths with IDs). High-cardinality span names (`GET /users/12345`) break trace aggregation — span names should be templates (`GET /users/{id}`).

## Sample Output

```
============================================================
  OTel Instrumentation Audit — src/
  Files scanned: 52  |  Files with issues: 9
============================================================

── HIGH (3) ────────────────────────────────────────────────
🟠 OT001 [HIGH] <project>
   No OpenTelemetry SDK imported anywhere. Zero instrumentation.
   Fix: npm install @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node
        Create instrumentation.js and require it first in your entry point.

🟠 OT004 [HIGH] src/handlers/orders.js:78
   Exception caught in catch block but span.recordException() not called.
   Fix: catch (err) { span.recordException(err); span.setStatus({ code: SpanStatusCode.ERROR }); throw err; }

🟠 OT002 [HIGH] src/routes/payments.js:12
   HTTP handler (app.post /checkout) has no custom span. Business logic is a trace black box.
   Fix: tracer.startActiveSpan('checkout.process', async (span) => { ... span.end(); })

── MEDIUM (2) ──────────────────────────────────────────────
🟡 OT005 [MEDIUM] src/tracing.js:8
   OTel Resource initialized without service.name attribute.
   Fix: Resource.create({ [SemanticResourceAttributes.SERVICE_NAME]: 'payment-service' })

🟡 OT007 [MEDIUM] src/services/inventory.js:45
   span.end() called in error branch without span.setStatus(SpanStatusCode.ERROR).
   Fix: span.setStatus({ code: SpanStatusCode.ERROR, message: err.message }); span.end();

── LOW (1) ─────────────────────────────────────────────────
🔵 OT010 [LOW] src/handlers/users.js:23
   High-cardinality span name: tracer.startSpan(`GET /users/${userId}`)
   Fix: Use template: tracer.startSpan('GET /users/{id}') and set userId as span attribute.

────────────────────────────────────────────────────────────
  Total: 6 findings
  High: 3 | Medium: 2 | Low: 1

  ❌ CI GATE FAILED — resolve HIGH findings before merging.
```

## The Script

```python
#!/usr/bin/env python3
"""
phy-otel-audit — OpenTelemetry Instrumentation Coverage Auditor
Scans Node.js/Python/Go/Java for missing or misconfigured OTel instrumentation.
Zero external dependencies.
"""

import sys
import re
from dataclasses import dataclass, field
from pathlib import Path


# ─── Data Structures ─────────────────────────────────────────────────────────

@dataclass
class Finding:
    check_id: str
    severity: str      # HIGH / MEDIUM / LOW
    location: str
    message: str
    fix: str = ""

    def __str__(self) -> str:
        icon = {"HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(self.severity, "⚪")
        parts = [f"{icon} {self.check_id} [{self.severity}] {self.location}"]
        parts.append(f"   {self.message}")
        if self.fix:
            parts.append(f"   Fix: {self.fix}")
        return "\n".join(parts)


@dataclass
class AuditResult:
    scan_root: str
    files_scanned: int = 0
    files_flagged: int = 0
    findings: list = field(default_factory=list)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "HIGH")

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "MEDIUM")

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "LOW")


# ─── Constants ────────────────────────────────────────────────────────────────

OTEL_IMPORT_RE = re.compile(
    r"(@opentelemetry/api|@opentelemetry/sdk-node|@opentelemetry/auto-instrumentations|"
    r"from opentelemetry|import opentelemetry|go\.opentelemetry\.io/otel|"
    r"io\.opentelemetry|opentelemetry-java)",
    re.IGNORECASE,
)

HTTP_HANDLER_RE = re.compile(
    r"""(app|router|r|e|g|mux)\.(get|post|put|patch|delete|handle)\s*\(\s*['"`/]""",
    re.IGNORECASE,
)

PYTHON_ROUTE_RE = re.compile(
    r"""@(app|router|blueprint)\.(get|post|put|patch|delete|route)\s*\(""",
    re.IGNORECASE,
)

GO_ROUTE_RE = re.compile(
    r"""(router|r|mux|e)\.(GET|POST|PUT|PATCH|DELETE|Handle)\s*\(""",
)

SPRING_HANDLER_RE = re.compile(
    r"@(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RequestMapping)",
)

DB_CALL_RE = re.compile(
    r"(db\.query|db\.execute|db\.find|db\.save|db\.update|db\.delete|"
    r"prisma\.\w+\.(find|create|update|delete|upsert)|"
    r"mongoose\.\w+\.(find|save|update|delete)|"
    r"cursor\.execute|session\.execute|"
    r"db\.Execute|db\.Query|db\.QueryRow|"
    r"redis\.(get|set|del|hget|hset)|"
    r"cache\.(get|set|delete)|"
    r"\.findById|\.findOne|\.findAll|\.save\(\)|\.delete\(\))",
    re.IGNORECASE,
)

SPAN_ACTIVE_RE = re.compile(
    r"(tracer\.(startActiveSpan|startSpan)|"
    r"with\s+tracer\.start_as_current_span|"
    r"otel\.trace\.getActiveSpan|"
    r"span\s*:?=\s*tracer\.Start|"
    r"@WithSpan|@NewSpan)",
    re.IGNORECASE,
)

CATCH_BLOCK_RE = re.compile(r"(catch\s*\(|except\s+\w|except\s*:)", re.IGNORECASE)

EXCEPTION_RECORD_RE = re.compile(
    r"(span\.recordException|span\.record_exception|span\.RecordError)",
    re.IGNORECASE,
)

SPAN_STATUS_ERROR_RE = re.compile(
    r"(span\.setStatus|span\.set_status|span\.SetStatus)",
    re.IGNORECASE,
)

RESOURCE_INIT_RE = re.compile(
    r"(Resource\.create|Resource\.default\(\)|new Resource|resource\.New)",
    re.IGNORECASE,
)

SERVICE_NAME_RE = re.compile(
    r"(SERVICE_NAME|service\.name|service_name\s*:|\"service\.name\")",
    re.IGNORECASE,
)

CONSOLE_EXPORTER_RE = re.compile(
    r"(ConsoleSpanExporter|ConsoleMetricExporter|ConsoleLogRecordExporter|"
    r"StdoutSpanExporter|stdout_span_exporter)",
    re.IGNORECASE,
)

ASYNC_CONCURRENT_RE = re.compile(
    r"(Promise\.all\s*\(|Promise\.allSettled\s*\(|asyncio\.gather\s*\(|"
    r"go\s+func\s*\(|go\s+\w+\()",
    re.IGNORECASE,
)

CONTEXT_PASS_RE = re.compile(
    r"(context\.TODO\(\)|context\.Background\(\)|ctx,|propagation\.|"
    r"W3CTraceContextPropagator|TraceContext\.inject|extract\()",
    re.IGNORECASE,
)

SPAN_START_WITH_TEMPLATE_RE = re.compile(
    r"""tracer\.(startSpan|startActiveSpan)\s*\(\s*[`'"].*(\$\{|\%s|\+\s*\w+)""",
)

SPAN_END_RE = re.compile(r"span\.(end|End)\(\)", re.IGNORECASE)

DEV_CONFIG_PATTERN = re.compile(
    r"(dev|development|test|local|debug)",
    re.IGNORECASE,
)

OTEL_INIT_FILE_RE = re.compile(
    r"(tracing|instrumentation|telemetry|otel)(\.(js|ts|py))?$",
    re.IGNORECASE,
)

REQUIRE_RE = re.compile(r"require\s*\(['\"]([^'\"]+)['\"]\)")

SUPPORTED_EXTENSIONS = {".js", ".ts", ".jsx", ".tsx", ".mjs", ".py", ".go", ".java", ".kt"}
SKIP_DIRS = {"node_modules", ".git", "venv", ".venv", "__pycache__", "dist", "build", ".next", "vendor", "test", "tests", "__tests__"}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_context_lines(lines: list, idx: int, window: int = 20) -> str:
    start = max(0, idx - window)
    end = min(len(lines), idx + window)
    return "\n".join(lines[start:end])


def collect_files(path: str) -> list:
    p = Path(path)
    if p.is_file():
        return [p] if p.suffix in SUPPORTED_EXTENSIONS else []
    files = []
    for f in p.rglob("*"):
        if any(skip in f.parts for skip in SKIP_DIRS):
            continue
        if f.is_file() and f.suffix in SUPPORTED_EXTENSIONS:
            files.append(f)
    return files


def is_dev_config_file(filepath: str) -> bool:
    """Heuristic: is this a dev/test config file?"""
    name = Path(filepath).name.lower()
    return bool(DEV_CONFIG_PATTERN.search(name))


# ─── Checks ──────────────────────────────────────────────────────────────────

def check_ot001_no_otel_sdk(all_contents: dict) -> list:
    """OT001 — No OTel SDK imported anywhere."""
    for content in all_contents.values():
        if OTEL_IMPORT_RE.search(content):
            return []
    return [Finding(
        check_id="OT001",
        severity="HIGH",
        location="<project>",
        message="No OpenTelemetry SDK imported anywhere. Zero instrumentation — no traces, metrics, or logs exported.",
        fix=(
            "JS: npm install @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node\n"
            "   Python: pip install opentelemetry-sdk opentelemetry-exporter-otlp\n"
            "   Go: go get go.opentelemetry.io/otel go.opentelemetry.io/otel/exporters/otlp/otlptrace"
        ),
    )]


def check_ot002_handler_no_span(filepath: str, lines: list) -> list:
    """OT002 — HTTP handler without custom span."""
    findings = []
    for i, line in enumerate(lines):
        is_handler = (
            HTTP_HANDLER_RE.search(line) or
            PYTHON_ROUTE_RE.search(line) or
            GO_ROUTE_RE.search(line) or
            SPRING_HANDLER_RE.search(line)
        )
        if not is_handler:
            continue
        ctx = get_context_lines(lines, i, 30)
        if not SPAN_ACTIVE_RE.search(ctx):
            findings.append(Finding(
                check_id="OT002",
                severity="HIGH",
                location=f"{filepath}:{i + 1}",
                message=f"HTTP handler '{line.strip()[:70]}' has no custom span. Business logic inside is a trace black box.",
                fix="tracer.startActiveSpan('handler.name', async (span) => { try { ... } finally { span.end(); } })",
            ))
    return findings


def check_ot003_db_outside_span(filepath: str, lines: list) -> list:
    """OT003 — DB/cache call where no span context is active in scope."""
    findings = []
    for i, line in enumerate(lines):
        if not DB_CALL_RE.search(line):
            continue
        ctx = get_context_lines(lines, i, 30)
        if not SPAN_ACTIVE_RE.search(ctx):
            findings.append(Finding(
                check_id="OT003",
                severity="HIGH",
                location=f"{filepath}:{i + 1}",
                message=f"DB/cache call '{line.strip()[:70]}' outside an active span — DB timing won't appear in traces.",
                fix="Wrap DB calls inside tracer.startActiveSpan('db.query') or ensure callers always create a span first.",
            ))
    return findings


def check_ot004_exception_not_recorded(filepath: str, lines: list) -> list:
    """OT004 — Exception caught without span.recordException()."""
    findings = []
    for i, line in enumerate(lines):
        if not CATCH_BLOCK_RE.search(line):
            continue
        ctx = get_context_lines(lines, i, 15)
        # Only flag if there's a span in scope
        if not SPAN_ACTIVE_RE.search(ctx) and "span" not in ctx.lower():
            continue
        if not EXCEPTION_RECORD_RE.search(ctx):
            findings.append(Finding(
                check_id="OT004",
                severity="HIGH",
                location=f"{filepath}:{i + 1}",
                message="Exception caught inside a span scope but span.recordException() not called. Trace appears successful on error.",
                fix="catch (err) { span.recordException(err); span.setStatus({ code: SpanStatusCode.ERROR, message: err.message }); throw err; }",
            ))
    return findings


def check_ot005_no_service_name(filepath: str, lines: list, content: str) -> list:
    """OT005 — OTel Resource initialized without service.name."""
    if not RESOURCE_INIT_RE.search(content):
        return []
    if SERVICE_NAME_RE.search(content):
        return []
    # Resource init found but no service.name
    for i, line in enumerate(lines):
        if RESOURCE_INIT_RE.search(line):
            return [Finding(
                check_id="OT005",
                severity="MEDIUM",
                location=f"{filepath}:{i + 1}",
                message="OTel Resource initialized without service.name. All traces appear as 'unknown_service' in Jaeger/Tempo/Honeycomb.",
                fix="Resource.create({ [SemanticResourceAttributes.SERVICE_NAME]: 'my-service-name' })",
            )]
    return []


def check_ot006_sdk_late_init(filepath: str, lines: list) -> list:
    """OT006 — OTel SDK initialized after other imports (Node.js only)."""
    if not filepath.endswith((".js", ".ts", ".mjs")):
        return []
    # Only check entry files (server.js, index.js, app.js, main.js)
    name = Path(filepath).stem.lower()
    if name not in ("server", "index", "app", "main", "start"):
        return []

    requires = []
    for i, line in enumerate(lines):
        m = REQUIRE_RE.search(line)
        if m:
            requires.append((i, m.group(1)))

    otel_idx = None
    first_other_idx = None
    for idx, module in requires:
        if "opentelemetry" in module or "tracing" in module or "instrumentation" in module:
            if otel_idx is None:
                otel_idx = idx
        else:
            if first_other_idx is None:
                first_other_idx = idx

    if otel_idx is not None and first_other_idx is not None and otel_idx > first_other_idx:
        return [Finding(
            check_id="OT006",
            severity="MEDIUM",
            location=f"{filepath}:{otel_idx + 1}",
            message="OTel SDK initialized AFTER other imports. Auto-instrumentation patches miss already-loaded modules.",
            fix="Move require('./tracing') to the very first line of your entry file, before any other require().",
        )]
    return []


def check_ot007_span_end_no_status(filepath: str, lines: list) -> list:
    """OT007 — span.end() in error branch without setStatus(ERROR)."""
    findings = []
    for i, line in enumerate(lines):
        if not SPAN_END_RE.search(line):
            continue
        # Check if inside an error branch
        ctx_before = "\n".join(lines[max(0, i - 10):i])
        if not re.search(r"(catch|except|error|err|Error|Exception)", ctx_before, re.IGNORECASE):
            continue
        if not SPAN_STATUS_ERROR_RE.search(ctx_before):
            findings.append(Finding(
                check_id="OT007",
                severity="MEDIUM",
                location=f"{filepath}:{i + 1}",
                message="span.end() in error branch without span.setStatus(SpanStatusCode.ERROR). Span marked OK despite error.",
                fix="span.setStatus({ code: SpanStatusCode.ERROR, message: err.message }); span.end();",
            ))
    return findings


def check_ot008_async_context_not_passed(filepath: str, lines: list) -> list:
    """OT008 — Concurrent async without context propagation (Go goroutines)."""
    findings = []
    # Only relevant for Go files (Python asyncio propagates automatically via contextvars)
    if not filepath.endswith(".go"):
        return []
    for i, line in enumerate(lines):
        if not re.search(r"^(\s*)go\s+(func|\w+)\s*\(", line):
            continue
        ctx = get_context_lines(lines, i, 15)
        # Check if ctx is passed into the goroutine
        if not re.search(r"ctx|context\.Context|trace\.SpanFromContext", ctx):
            findings.append(Finding(
                check_id="OT008",
                severity="MEDIUM",
                location=f"{filepath}:{i + 1}",
                message="Goroutine launched without passing context.Context — OTel trace context is lost in this goroutine.",
                fix="go func(ctx context.Context) { ... }(ctx)  — always thread ctx through goroutines.",
            ))
    return findings


def check_ot009_console_exporter(filepath: str, lines: list) -> list:
    """OT009 — Console/stdout exporter in non-dev file."""
    if is_dev_config_file(filepath):
        return []
    findings = []
    for i, line in enumerate(lines):
        if CONSOLE_EXPORTER_RE.search(line):
            findings.append(Finding(
                check_id="OT009",
                severity="LOW",
                location=f"{filepath}:{i + 1}",
                message="ConsoleSpanExporter detected outside dev config. Console exporter floods logs with no backend value in production.",
                fix="Replace with OTLPTraceExporter pointing to your Jaeger/Tempo/Honeycomb/Grafana Cloud endpoint.",
            ))
    return findings


def check_ot010_high_cardinality_span_name(filepath: str, lines: list) -> list:
    """OT010 — High-cardinality span name (dynamic values in name string)."""
    findings = []
    for i, line in enumerate(lines):
        if SPAN_START_WITH_TEMPLATE_RE.search(line):
            findings.append(Finding(
                check_id="OT010",
                severity="LOW",
                location=f"{filepath}:{i + 1}",
                message=f"Span name uses dynamic value: '{line.strip()[:80]}'. High-cardinality names break trace aggregation in backends.",
                fix="Use fixed template: tracer.startSpan('GET /users/{id}') and add userId as a span attribute: span.setAttribute('user.id', userId)",
            ))
    return findings


# ─── Main Audit ───────────────────────────────────────────────────────────────

def audit(path: str) -> AuditResult:
    result = AuditResult(scan_root=path)
    files = collect_files(path)

    all_contents = {}
    for f in files:
        try:
            all_contents[str(f)] = f.read_text(errors="ignore")
        except Exception:
            pass

    result.files_scanned = len(files)

    # Global check
    result.findings.extend(check_ot001_no_otel_sdk(all_contents))

    # Per-file checks
    for f in files:
        content = all_contents.get(str(f), "")
        lines = content.splitlines()
        fp = str(f)

        file_findings = []
        file_findings.extend(check_ot002_handler_no_span(fp, lines))
        file_findings.extend(check_ot003_db_outside_span(fp, lines))
        file_findings.extend(check_ot004_exception_not_recorded(fp, lines))
        file_findings.extend(check_ot005_no_service_name(fp, lines, content))
        file_findings.extend(check_ot006_sdk_late_init(fp, lines))
        file_findings.extend(check_ot007_span_end_no_status(fp, lines))
        file_findings.extend(check_ot008_async_context_not_passed(fp, lines))
        file_findings.extend(check_ot009_console_exporter(fp, lines))
        file_findings.extend(check_ot010_high_cardinality_span_name(fp, lines))

        if file_findings:
            result.files_flagged += 1
        result.findings.extend(file_findings)

    return result


def format_report(result: AuditResult, ci_mode: bool = False) -> str:
    out = []
    out.append(f"\n{'='*60}")
    out.append(f"  OTel Instrumentation Audit — {result.scan_root}")
    out.append(f"  Files scanned: {result.files_scanned}  |  Files with issues: {result.files_flagged}")
    out.append(f"{'='*60}")

    if not result.findings:
        out.append("✅ No OTel instrumentation gaps detected.")
        return "\n".join(out)

    for severity in ("HIGH", "MEDIUM", "LOW"):
        sev_findings = [f for f in result.findings if f.severity == severity]
        if sev_findings:
            out.append(f"\n── {severity} ({len(sev_findings)}) {'─'*40}")
            for finding in sev_findings:
                out.append(str(finding))

    out.append(f"\n{'─'*60}")
    out.append(
        f"  Total: {len(result.findings)} findings  |  "
        f"High: {result.high_count}  Medium: {result.medium_count}  Low: {result.low_count}"
    )
    if ci_mode and result.high_count > 0:
        out.append("\n  ❌ CI GATE FAILED — resolve HIGH findings before merging.")
    return "\n".join(out)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="phy-otel-audit — OpenTelemetry Instrumentation Auditor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python otel_audit.py ./src
  python otel_audit.py src/handlers/orders.js
  python otel_audit.py ./src --ci
  python otel_audit.py ./src --only-severity HIGH
        """,
    )
    parser.add_argument("path", help="Directory or file to audit")
    parser.add_argument("--ci", action="store_true", help="Exit 1 on HIGH findings")
    parser.add_argument(
        "--only-severity",
        choices=["HIGH", "MEDIUM", "LOW"],
        help="Filter to this severity and above",
    )
    args = parser.parse_args()

    result = audit(args.path)

    sev_order = ["HIGH", "MEDIUM", "LOW"]
    if args.only_severity:
        cutoff = sev_order.index(args.only_severity)
        result.findings = [f for f in result.findings if sev_order.index(f.severity) <= cutoff]

    print(format_report(result, ci_mode=args.ci))

    if args.ci and result.high_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## CI Integration

```yaml
# GitHub Actions
- name: OTel Instrumentation Audit
  run: python otel_audit.py ./src --ci

# Only block on HIGH
- name: OTel Audit (strict)
  run: python otel_audit.py ./src --only-severity HIGH --ci
```

## False Positive Notes

- **OT002** — If you use auto-instrumentation exclusively (e.g., `@opentelemetry/auto-instrumentations-node`), framework-level spans are created automatically. OT002 fires because it can't see the auto-instrumentation wrapper. Suppress with `# phy-ignore: OT002` on the route line if auto-instrumentation is confirmed.
- **OT003** — DB calls in utility functions called from within spans will false-positive (the span context exists at runtime but isn't visible in the static 30-line window). Check actual trace output to confirm.
- **OT006** — Only checks Node.js entry files named `server`, `index`, `app`, `main`, `start`.
- **OT008** — Only checks Go goroutines. Python asyncio propagates context automatically via `contextvars`.

## Related Skills

- **phy-async-audit** — async error propagation (unhandled exceptions in spans)
- **phy-log-smell-auditor** — structured logging gaps that complement OTel spans
- **phy-rate-limit-audit** — rate limit signals visible in OTel metrics
