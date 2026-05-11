#!/usr/bin/env bash
# opsec-scan.sh <skill-dir>
# OPSEC scan for a skill release directory.
# Primary: delegates to validate-job-output.py (refactory scanner).
# Fallback: grep-based scan for common sensitive patterns.
# Exits 0 if CLEAN, exits 1 if violations found.

set -euo pipefail

SKILL_DIR="${1:-}"
if [[ -z "$SKILL_DIR" ]]; then
  echo "Usage: $0 <skill-dir>" >&2
  exit 1
fi

if [[ ! -d "$SKILL_DIR" ]]; then
  echo "ERROR: Directory not found: $SKILL_DIR" >&2
  exit 1
fi

PYTHON_SCANNER="/tmp/openclaw-knowledge/refactory/scripts/validate-job-output.py"
VIOLATIONS=()
ALL_CLEAN=true

echo ""
echo "OPSEC scan: $SKILL_DIR"
echo "──────────────────────────────────────────"

# ── Primary: Python refactory scanner ─────────────────────────────────────────
# The refactory scanner expects a specific job-output directory format.
# We try it, but fall back to grep scan if it reports an unsupported type.
if [[ -f "$PYTHON_SCANNER" ]]; then
  echo "  Trying: refactory/scripts/validate-job-output.py"
  SCANNER_OUTPUT=$(python3 "$PYTHON_SCANNER" "$SKILL_DIR" 2>&1 || true)
  SCANNER_EXIT=$?

  # Fall back if the scanner doesn't recognize the directory type
  if echo "$SCANNER_OUTPUT" | grep -q "Unknown job type\|Valid types:"; then
    echo "  (refactory scanner does not support raw skill dirs — using fallback)"
    echo ""
  elif [[ "$SCANNER_EXIT" -eq 0 ]]; then
    echo "$SCANNER_OUTPUT"
    echo ""
    echo "✅ CLEAN — refactory scanner found no violations"
    exit 0
  else
    echo "$SCANNER_OUTPUT"
    echo ""
    echo "❌ BLOCKED — refactory scanner found violations (see above)"
    exit 1
  fi
fi

# ── Fallback: grep-based scan ─────────────────────────────────────────────────
echo "  Refactory scanner not available — using fallback grep scan"
echo ""

# Collect all text files to scan
SCAN_FILES=$(find "$SKILL_DIR" -type f \
  -not -path "*/.git/*" \
  \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" \
     -o -name "*.py" -o -name "*.json" -o -name "*.txt" -o -name "*.js" \) \
  2>/dev/null)

if [[ -z "$SCAN_FILES" ]]; then
  echo "  No text files found to scan."
fi

record_violations() {
  local label="$1"
  local matches="$2"
  if [[ -n "$matches" ]]; then
    ALL_CLEAN=false
    VIOLATIONS+=("$label")
    while IFS= read -r line; do
      VIOLATIONS+=("  $line")
    done <<< "$matches"
  fi
}

# ── Pattern 1: Personal email addresses (non-example domains) ─────────────────
# Exclude: @example.com, @example.org, @example.net, @localhost
EMAILS=$(echo "$SCAN_FILES" | xargs grep -hEn \
  '[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}' 2>/dev/null \
  | grep -Ev '@(example\.(com|org|net)|localhost|127\.|openclaw\.ai|clawhub\.ai)' \
  | grep -Ev '^\s*#' \
  | head -20 || true)
record_violations "❌ Personal email addresses found:" "$EMAILS"

# ── Pattern 2: IP addresses (excluding safe/example ranges) ───────────────────
# Exclude: 127.x.x.x, 192.0.2.x (TEST-NET), 0.0.0.0, example patterns
IPS=$(echo "$SCAN_FILES" | xargs grep -hEn \
  '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' 2>/dev/null \
  | grep -Ev '\b(127\.|192\.0\.2\.|0\.0\.0\.0|10\.0\.0\.|172\.(1[6-9]|2[0-9]|3[01])\.)' \
  | grep -Ev '(example|placeholder|your-ip|x\.x\.x\.x)' \
  | grep -Ev '^\s*#' \
  | head -20 || true)
record_violations "❌ IP addresses (non-example) found:" "$IPS"

# ── Pattern 3: Hardcoded absolute paths /Users/ or /home/ ─────────────────────
# Exclude: lines that look like examples/placeholders
PATHS=$(echo "$SCAN_FILES" | xargs grep -hEn \
  '/(Users|home)/[a-zA-Z0-9_\-]+/' 2>/dev/null \
  | grep -Ev '(example|your-username|<user>|YOUR_|placeholder|e\.g\.|e\.g,)' \
  | grep -Ev '^\s*#.*example' \
  | head -20 || true)
record_violations "❌ Hardcoded absolute paths (/Users/, /home/) found:" "$PATHS"

# ── Pattern 4: Known identifier patterns ──────────────────────────────────────
# AWS keys, GitHub tokens, API keys
IDENTIFIERS=$(echo "$SCAN_FILES" | xargs grep -hEn \
  '(AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{32,}|AIza[0-9A-Za-z\-_]{35})' \
  2>/dev/null | head -20 || true)
record_violations "❌ Known credential/token patterns found:" "$IDENTIFIERS"

# ── Report ─────────────────────────────────────────────────────────────────────
if [[ "$ALL_CLEAN" == "true" ]]; then
  echo "  ✅ No personal emails"
  echo "  ✅ No suspicious IP addresses"
  echo "  ✅ No hardcoded absolute paths"
  echo "  ✅ No credential/token patterns"
  echo ""
  echo "✅ CLEAN — fallback scan found no violations"
  exit 0
else
  for v in "${VIOLATIONS[@]}"; do echo "  $v"; done
  echo ""
  echo "❌ BLOCKED — OPSEC violations found (see above)"
  echo "   Fix violations in the release copy before proceeding."
  echo "   Do NOT modify the source in openclaw-knowledge."
  exit 1
fi
