#!/usr/bin/env bash
# preflight.sh — Mandatory pre-commit gate: build + lint + test
# Usage: bash scripts/preflight.sh [shiploop.yml path]
# Exit 0 = all checks passed, non-zero = failure (do NOT commit)

set -euo pipefail

SHIPLOOP_FILE="${1:-SHIPLOOP.yml}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

# --------------------------------------------------------------------------
# Parse preflight commands from SHIPLOOP.yml
# Uses grep/sed for portability (no yq dependency)
# --------------------------------------------------------------------------
get_config() {
    local key="$1"
    local default="$2"
    local value
    value=$(grep -A1 "^  ${key}:" "$SHIPLOOP_FILE" 2>/dev/null | tail -1 | sed 's/^  *//;s/"//g' || true)
    # If the value is on the same line as the key
    value2=$(grep "^  ${key}:" "$SHIPLOOP_FILE" 2>/dev/null | sed "s/^  ${key}: *//;s/\"//g" || true)
    if [[ -n "$value2" && "$value2" != "" ]]; then
        echo "$value2"
    elif [[ -n "$value" && "$value" != "" ]]; then
        echo "$value"
    else
        echo "$default"
    fi
}

# Read preflight commands
BUILD_CMD=$(get_config "build" "")
LINT_CMD=$(get_config "lint" "")
TEST_CMD=$(get_config "test" "")

PASSED=0
FAILED=0
SKIPPED=0
ERRORS=""

run_check() {
    local name="$1"
    local cmd="$2"

    if [[ -z "$cmd" || "$cmd" == "null" ]]; then
        echo "⏭  $name: skipped (not configured)"
        ((SKIPPED++))
        return 0
    fi

    echo "🔍 $name: running '$cmd'..."
    local start_time
    start_time=$(date +%s)

    if eval "$cmd" > /tmp/preflight-${name}.log 2>&1; then
        local elapsed=$(( $(date +%s) - start_time ))
        echo "✅ $name: passed (${elapsed}s)"
        ((PASSED++))
    else
        local exit_code=$?
        local elapsed=$(( $(date +%s) - start_time ))
        echo "❌ $name: FAILED (exit $exit_code, ${elapsed}s)"
        echo "   Output (last 20 lines):"
        tail -20 /tmp/preflight-${name}.log | sed 's/^/   │ /'
        ERRORS="${ERRORS}\n  - ${name}: exit $exit_code"
        ((FAILED++))
        # Don't exit yet — run all checks to report full picture
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛫 PREFLIGHT CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_check "build" "$BUILD_CMD"
run_check "lint" "$LINT_CMD"
run_check "test" "$TEST_CMD"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Results: $PASSED passed, $FAILED failed, $SKIPPED skipped"

if [[ $FAILED -gt 0 ]]; then
    echo ""
    echo "🚫 PREFLIGHT FAILED — commit blocked"
    echo -e "   Failures:$ERRORS"
    echo ""
    echo "   Fix the issues and retry. Logs in /tmp/preflight-*.log"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi

if [[ $PASSED -eq 0 && $SKIPPED -gt 0 ]]; then
    echo ""
    echo "⚠️  WARNING: All checks skipped. Configure preflight commands in SHIPLOOP.yml."
fi

echo "✅ PREFLIGHT PASSED — safe to commit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
exit 0
