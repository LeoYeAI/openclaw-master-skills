---
name: clawsec-scanner-hook
description: Periodic vulnerability scanning for installed skills and dependencies with configurable scan intervals.
metadata: { "openclaw": { "events": ["agent:bootstrap", "command:new"] } }
---

# ClawSec Scanner Hook

This hook performs comprehensive vulnerability scanning on installed skills and their dependencies on:

- `agent:bootstrap`
- `command:new`

When triggered, it runs all configured scanning engines (dependency scan, SAST, DAST, CVE database lookup) and posts findings as conversation messages. Scans are rate-limited by configurable interval to avoid performance impact.

## Scanning Capabilities

The hook orchestrates four independent scanning engines:

1. **Dependency Scanning**: Executes `npm audit` and `pip-audit` to detect known vulnerabilities in JavaScript and Python dependencies
2. **SAST (Static Analysis)**: Runs Semgrep (JS/TS) and Bandit (Python) to detect security issues like hardcoded secrets, command injection, and path traversal
3. **CVE Database Lookup**: Queries OSV API (primary), NVD 2.0 (optional), and GitHub Advisory Database (optional) for vulnerability enrichment
4. **DAST (Dynamic Analysis)**: Executes real OpenClaw hook handlers in an isolated harness and tests malicious-input resilience, timeout behavior, output bounds, and event mutation safety

## Safety Contract

- The hook does not modify or delete skills.
- It only reports findings and provides remediation guidance.
- Scanning is non-blocking and runs on a configurable interval (default 24 hours).
- Failed scans (network errors, missing tools) produce warnings but do not block execution.
- Findings are deduplicated to avoid alert fatigue.

## Optional Environment Variables

### Core Configuration

- `CLAWSEC_SCANNER_INTERVAL`: Minimum interval between hook scans in seconds (default `86400` / 24 hours).
- `CLAWSEC_SCANNER_TARGET`: Override default scan target path (default: installed skills root).
- `CLAWSEC_SCANNER_STATE_FILE`: Override state file path for deduplication (default `~/.openclaw/clawsec-scanner-state.json`).
- `CLAWSEC_INSTALL_ROOT`: Override installed skills root directory.

### CVE Database Integration

- `CLAWSEC_NVD_API_KEY`: NVD API key for rate-limit-free access (without this, 6-second delays apply).
- `GITHUB_TOKEN`: GitHub OAuth token for GitHub Advisory Database queries (optional enhancement).

### Selective Scanning

- `CLAWSEC_SKIP_DEPENDENCY_SCAN`: Set to `1` to disable dependency scanning (npm audit, pip-audit).
- `CLAWSEC_SKIP_SAST`: Set to `1` to disable static analysis (Semgrep, Bandit).
- `CLAWSEC_SKIP_DAST`: Set to `1` to disable dynamic analysis (hook security tests).
- `CLAWSEC_SKIP_CVE_LOOKUP`: Set to `1` to disable CVE database enrichment.

### Advanced Options

- `CLAWSEC_SCANNER_TIMEOUT`: Maximum scan duration in seconds before timeout (default `300` / 5 minutes).
- `CLAWSEC_SCANNER_FORMAT`: Output format for findings (`json` or `text`, default `text`).
- `CLAWSEC_SCANNER_MIN_SEVERITY`: Minimum severity to report (`critical`, `high`, `medium`, `low`, `info`, default `medium`).
- `CLAWSEC_SCANNER_OUTPUT_FILE`: Optional path to write full scan report JSON (default: conversation only).

## Required Binaries

The hook requires the following binaries to be available on `PATH`:

- `node` (20+) - JavaScript runtime
- `npm` - For npm audit execution
- `python3` (3.10+) - Python runtime
- `pip-audit` - Python dependency scanner
- `semgrep` - JavaScript/TypeScript static analysis
- `bandit` - Python static analysis
- `jq` - JSON parsing and merging
- `curl` - API requests (fallback)

Missing binaries will be logged as warnings; available tools will still run.
