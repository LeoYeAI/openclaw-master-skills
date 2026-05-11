#!/bin/bash
# collect-precheck.sh — Run `openclaw doctor` built-in precheck, parse output to JSON
# Timeout: 15s | Compatible: macOS (darwin) + Linux
set -euo pipefail

# Check if openclaw CLI is available
OPENCLAW_BIN=""
if command -v openclaw &>/dev/null; then
  OPENCLAW_BIN="openclaw"
elif command -v clawhub &>/dev/null; then
  OPENCLAW_BIN="clawhub"
fi

if [[ -z "$OPENCLAW_BIN" ]]; then
  cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "cli_available": false,
  "precheck_ran": false,
  "status": "skipped",
  "message": "Neither openclaw nor clawhub CLI found",
  "checks": [],
  "summary": { "pass": 0, "warn": 0, "error": 0, "total": 0 }
}
EOF
  exit 0
fi

# Run openclaw doctor (built-in precheck) and capture output
PRECHECK_OUTPUT=""
PRECHECK_EXIT=0
PRECHECK_OUTPUT=$($OPENCLAW_BIN doctor --json 2>/dev/null) || PRECHECK_EXIT=$?

# If --json is not supported, try plain text parsing
if [[ -z "$PRECHECK_OUTPUT" || "$PRECHECK_EXIT" -ne 0 ]]; then
  PRECHECK_OUTPUT=$($OPENCLAW_BIN doctor 2>&1) || PRECHECK_EXIT=$?
fi

# Parse the output with Node.js
node -e '
const output = process.argv[1];
const exitCode = parseInt(process.argv[2]);

const result = {
  timestamp: new Date().toISOString(),
  cli_available: true,
  cli_used: process.argv[3],
  precheck_ran: true,
  exit_code: exitCode,
  checks: [],
  summary: { pass: 0, warn: 0, error: 0, total: 0 }
};

// Try JSON parse first
try {
  const parsed = JSON.parse(output);
  if (parsed.checks) {
    result.checks = parsed.checks;
  } else if (Array.isArray(parsed)) {
    result.checks = parsed;
  }
} catch {
  // Parse plain text output line by line
  // Expected patterns: ✓ / ✔ / PASS / OK → pass, ⚠ / WARN → warn, ✗ / ✘ / FAIL / ERROR → error
  const lines = output.split("\n").filter(l => l.trim());
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || trimmed.startsWith("---")) continue;

    let status = "unknown";
    if (/[✓✔]|PASS|OK|\bpass\b/i.test(trimmed)) status = "pass";
    else if (/[⚠]|WARN|\bwarn/i.test(trimmed)) status = "warn";
    else if (/[✗✘]|FAIL|ERROR|\berror\b/i.test(trimmed)) status = "error";
    else continue; // skip non-check lines

    // Extract check name: remove status indicators and clean up
    const name = trimmed
      .replace(/[✓✔✗✘⚠]/g, "")
      .replace(/\b(PASS|OK|WARN|FAIL|ERROR)\b/gi, "")
      .replace(/^\s*[-:•]\s*/, "")
      .trim()
      .substring(0, 200);

    if (name) {
      result.checks.push({ name, status, raw: trimmed.substring(0, 200) });
    }
  }
}

// Calculate summary
for (const check of result.checks) {
  const s = (check.status || "").toLowerCase();
  if (s === "pass" || s === "ok") result.summary.pass++;
  else if (s === "warn" || s === "warning") result.summary.warn++;
  else if (s === "error" || s === "fail") result.summary.error++;
}
result.summary.total = result.checks.length;

// Overall status
if (result.summary.error > 0) result.status = "error";
else if (result.summary.warn > 0) result.status = "warn";
else if (result.summary.pass > 0) result.status = "pass";
else result.status = "unknown";

// If no checks parsed but command ran, note it
if (result.checks.length === 0 && output) {
  result.raw_output = output.substring(0, 1000);
  result.status = exitCode === 0 ? "pass" : "error";
}

console.log(JSON.stringify(result, null, 2));
' "$PRECHECK_OUTPUT" "$PRECHECK_EXIT" "$OPENCLAW_BIN"
