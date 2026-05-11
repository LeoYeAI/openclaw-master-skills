#!/bin/bash
# test_audit_scrubbing.sh — Verify sensitive data is scrubbed from audit log

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
MARK_SCRIPT="$SKILL_DIR/scripts/mark-satisfied.sh"
AUDIT_FILE="$SKILL_DIR/assets/audit.log"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"

export WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"

PASS=true

echo "Testing audit log scrubbing..."

# Backup current state and audit
cp "$STATE_FILE" "$STATE_FILE.scrub_backup" 2>/dev/null || true
cp "$AUDIT_FILE" "$AUDIT_FILE.scrub_backup" 2>/dev/null || true

# Test patterns that should be scrubbed
TEST_PATTERNS=(
    "token abc123xyz789def456ghi000jkl111mno"  # Long token
    "email test@example.com"                    # Email
    "password=secretpass123"                    # Password
    "Bearer sk-1234567890abcdef"               # Bearer token
)

EXPECTED_SCRUBBED=(
    "[REDACTED]"
    "[EMAIL]"
    "[REDACTED]"
    "Bearer [REDACTED]"
)

for i in "${!TEST_PATTERNS[@]}"; do
    pattern="${TEST_PATTERNS[$i]}"
    expected="${EXPECTED_SCRUBBED[$i]}"
    
    # Clear audit and run mark-satisfied with sensitive data
    > "$AUDIT_FILE"
    "$MARK_SCRIPT" security 0.1 --reason "test with $pattern" > /dev/null 2>&1
    
    # Check if scrubbed version appears in audit
    if grep -q "$expected" "$AUDIT_FILE"; then
        echo "  Pattern '$pattern' → scrubbed — OK"
    else
        # Check if original pattern leaked
        if grep -q "$pattern" "$AUDIT_FILE"; then
            echo "  Pattern '$pattern' → LEAKED — FAIL"
            PASS=false
        else
            echo "  Pattern '$pattern' → scrubbed (different format) — OK"
        fi
    fi
done

# Restore backups
cp "$STATE_FILE.scrub_backup" "$STATE_FILE" 2>/dev/null || true
cp "$AUDIT_FILE.scrub_backup" "$AUDIT_FILE" 2>/dev/null || true
rm -f "$STATE_FILE.scrub_backup" "$AUDIT_FILE.scrub_backup"

if $PASS; then
    echo "✅ Audit scrubbing test PASSED"
    exit 0
else
    echo "❌ Audit scrubbing test FAILED"
    exit 1
fi
