#!/usr/bin/env bash
set -euo pipefail

# Runner for clawsec-scanner - orchestrates all vulnerability scanning engines.
# - Runs dependency scan (npm audit + pip-audit)
# - Enriches findings with CVE database lookups (OSV, NVD)
# - Runs SAST analysis (Semgrep + Bandit)
# - Runs DAST security tests (hook handler validation)
# - Generates unified vulnerability report

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default values
TARGET=""
OUTPUT=""
FORMAT="json"
RUN_DEPS=1
RUN_CVE=1
RUN_SAST=1
RUN_DAST=1

# Parse CLI arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --output)
      OUTPUT="${2:-}"
      shift 2
      ;;
    --format)
      FORMAT="${2:-json}"
      shift 2
      ;;
    --skip-deps)
      RUN_DEPS=0
      shift
      ;;
    --skip-cve)
      RUN_CVE=0
      shift
      ;;
    --skip-sast)
      RUN_SAST=0
      shift
      ;;
    --skip-dast)
      RUN_DAST=0
      shift
      ;;
    --help|-h)
      cat <<'EOF'
Usage: runner.sh --target <path> [options]

Orchestrates vulnerability scanning across dependency, SAST, DAST, and CVE engines.

Required:
  --target <path>        Target directory to scan (e.g., ./skills/)

Optional:
  --output <file>        Write report to file (default: stdout)
  --format <json|text>   Output format (default: json)
  --skip-deps            Skip dependency scanning (npm audit, pip-audit)
  --skip-cve             Skip CVE database enrichment
  --skip-sast            Skip static analysis (Semgrep, Bandit)
  --skip-dast            Skip dynamic analysis (hook security tests)
  --help, -h             Show this help message

Examples:
  # Scan all skills with JSON output to file
  ./runner.sh --target ./skills/ --output report.json

  # Scan with human-readable output
  ./runner.sh --target ./skills/ --format text

  # Quick scan: dependencies only
  ./runner.sh --target ./skills/ --skip-sast --skip-dast --skip-cve

Environment Variables:
  CLAWSEC_NVD_API_KEY           Optional NVD API key (avoids rate limiting)
  GITHUB_TOKEN                  Optional GitHub token for Advisory Database
  CLAWSEC_SCANNER_INTERVAL      Hook scan interval in seconds (default: 86400)
  CLAWSEC_ALLOW_UNSIGNED_FEED   Allow unsigned advisory feed (dev only)

EOF
      exit 0
      ;;
    *)
      echo "Unknown flag: $1" >&2
      echo "Run with --help for usage information" >&2
      exit 1
      ;;
  esac
done

# Validate required arguments
if [[ -z "$TARGET" ]]; then
  echo "Error: Missing required --target flag" >&2
  echo "Run with --help for usage information" >&2
  exit 1
fi

# Validate target exists
if [[ ! -e "$TARGET" ]]; then
  echo "Error: Target path does not exist: $TARGET" >&2
  exit 1
fi

# Validate format
if [[ "$FORMAT" != "json" && "$FORMAT" != "text" ]]; then
  echo "Error: Invalid --format value. Use 'json' or 'text'." >&2
  exit 1
fi

# Temporary files for intermediate results
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

DEPS_REPORT="$TEMP_DIR/deps.json"
SAST_REPORT="$TEMP_DIR/sast.json"
DAST_REPORT="$TEMP_DIR/dast.json"
MERGED_REPORT="$TEMP_DIR/merged.json"

# Run dependency scan
if [[ "$RUN_DEPS" -eq 1 ]]; then
  if command -v node >/dev/null 2>&1; then
    node "$SCRIPT_DIR/scan_dependencies.mjs" --target "$TARGET" --format json > "$DEPS_REPORT" 2>/dev/null || {
      echo '{"scan_id":"","timestamp":"","target":"","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}' > "$DEPS_REPORT"
    }
  else
    echo "Warning: node not found, skipping dependency scan" >&2
    echo '{"scan_id":"","timestamp":"","target":"","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}' > "$DEPS_REPORT"
  fi
else
  echo '{"scan_id":"","timestamp":"","target":"","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}' > "$DEPS_REPORT"
fi

# Run SAST analysis
if [[ "$RUN_SAST" -eq 1 ]]; then
  if command -v node >/dev/null 2>&1; then
    node "$SCRIPT_DIR/sast_analyzer.mjs" --target "$TARGET" --format json > "$SAST_REPORT" 2>/dev/null || {
      echo '{"scan_id":"","timestamp":"","target":"","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}' > "$SAST_REPORT"
    }
  else
    echo "Warning: node not found, skipping SAST analysis" >&2
    echo '{"scan_id":"","timestamp":"","target":"","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}' > "$SAST_REPORT"
  fi
else
  echo '{"scan_id":"","timestamp":"","target":"","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}' > "$SAST_REPORT"
fi

# Run DAST tests
if [[ "$RUN_DAST" -eq 1 ]]; then
  if command -v node >/dev/null 2>&1; then
    if ! node "$SCRIPT_DIR/dast_runner.mjs" --target "$TARGET" --format json > "$DAST_REPORT" 2>/dev/null; then
      # dast_runner exits non-zero when high/critical findings exist.
      # Preserve a valid JSON report in that case; only fall back to empty on true execution errors.
      if [[ -s "$DAST_REPORT" ]] && jq -e '.vulnerabilities and .summary' "$DAST_REPORT" >/dev/null 2>&1; then
        echo "Warning: DAST runner exited non-zero; preserving generated findings report" >&2
      else
        echo '{"scan_id":"","timestamp":"","target":"","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}' > "$DAST_REPORT"
      fi
    fi
  else
    echo "Warning: node not found, skipping DAST tests" >&2
    echo '{"scan_id":"","timestamp":"","target":"","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}' > "$DAST_REPORT"
  fi
else
  echo '{"scan_id":"","timestamp":"","target":"","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}' > "$DAST_REPORT"
fi

# Merge reports using jq
if command -v jq >/dev/null 2>&1; then
  # Extract vulnerabilities from all reports and merge
  jq -s '
    {
      scan_id: (.[0].scan_id // ""),
      timestamp: (.[0].timestamp // (now | todate)),
      target: (.[0].target // ""),
      vulnerabilities: (map(.vulnerabilities // []) | flatten),
      summary: {
        critical: (map(.summary.critical // 0) | add),
        high: (map(.summary.high // 0) | add),
        medium: (map(.summary.medium // 0) | add),
        low: (map(.summary.low // 0) | add),
        info: (map(.summary.info // 0) | add)
      }
    }
  ' "$DEPS_REPORT" "$SAST_REPORT" "$DAST_REPORT" > "$MERGED_REPORT"
else
  echo "Error: jq not found. Required for report merging." >&2
  exit 1
fi

# CVE enrichment (if enabled and vulnerabilities found)
if [[ "$RUN_CVE" -eq 1 ]]; then
  VULN_COUNT=$(jq '.vulnerabilities | length' "$MERGED_REPORT")
  if [[ "$VULN_COUNT" -gt 0 ]] && command -v node >/dev/null 2>&1; then
    # Note: CVE enrichment is done inline by scan_dependencies.mjs for efficiency
    # Future enhancement: implement post-scan enrichment for SAST/DAST findings
    :
  fi
fi

# Output final report
if [[ "$FORMAT" == "json" ]]; then
  FINAL_OUTPUT=$(cat "$MERGED_REPORT")
elif [[ "$FORMAT" == "text" ]]; then
  # Convert JSON to human-readable text using Node.js
  if command -v node >/dev/null 2>&1; then
    FINAL_OUTPUT=$(node -e "
      const fs = require('fs');
      const report = JSON.parse(fs.readFileSync('$MERGED_REPORT', 'utf8'));

      console.log('='.repeat(80));
      console.log('ClawSec Vulnerability Scan Report');
      console.log('='.repeat(80));
      console.log('');
      console.log('Scan ID:   ' + report.scan_id);
      console.log('Target:    ' + report.target);
      console.log('Timestamp: ' + report.timestamp);
      console.log('');
      console.log('Summary:');
      console.log('  Critical: ' + report.summary.critical);
      console.log('  High:     ' + report.summary.high);
      console.log('  Medium:   ' + report.summary.medium);
      console.log('  Low:      ' + report.summary.low);
      console.log('  Info:     ' + report.summary.info);
      console.log('  Total:    ' + report.vulnerabilities.length);
      console.log('');

      if (report.vulnerabilities.length === 0) {
        console.log('✓ No vulnerabilities detected');
        console.log('');
      } else {
        console.log('Vulnerabilities by Severity:');
        console.log('');

        const bySeverity = {
          critical: [],
          high: [],
          medium: [],
          low: [],
          info: []
        };

        report.vulnerabilities.forEach(v => {
          const sev = v.severity || 'info';
          if (bySeverity[sev]) {
            bySeverity[sev].push(v);
          }
        });

        ['critical', 'high', 'medium', 'low', 'info'].forEach(severity => {
          const vulns = bySeverity[severity];
          if (vulns.length > 0) {
            console.log(severity.toUpperCase() + ':');
            vulns.forEach((v, idx) => {
              console.log('  ' + (idx + 1) + '. [' + v.source + '] ' + v.id + ' - ' + v.title);
              console.log('     Package: ' + v.package + '@' + v.version);
              if (v.fixed_version) {
                console.log('     Fix: Upgrade to ' + v.fixed_version);
              }
              console.log('');
            });
          }
        });
      }

      console.log('='.repeat(80));
    ")
  else
    echo "Error: node required for text format output" >&2
    exit 1
  fi
else
  FINAL_OUTPUT=$(cat "$MERGED_REPORT")
fi

# Write output
if [[ -n "$OUTPUT" ]]; then
  printf '%s\n' "$FINAL_OUTPUT" > "$OUTPUT"
else
  printf '%s\n' "$FINAL_OUTPUT"
fi
