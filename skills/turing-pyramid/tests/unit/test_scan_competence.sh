#!/usr/bin/env bash
# Test: competence scanner — line-level method
# Verifies that line-level scanning correctly handles:
#   1. Pure positive lines → positive signal
#   2. Pure negative lines → negative signal
#   3. Mixed lines (e.g. "fixed a bug") → positive wins
#   4. Neutral lines → no signal
#   5. Empty/header lines → skipped
#   6. Overall satisfaction output is correct

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
SCANNER="$SKILL_DIR/scripts/scan_competence.sh"

errors=0

# Create temp workspace for isolated testing
TMPDIR=$(mktemp -d)
FAKE_WORKSPACE="$TMPDIR/workspace"
mkdir -p "$FAKE_WORKSPACE/memory"
mkdir -p "$FAKE_WORKSPACE/skills/turing-pyramid/assets"

# Copy required assets
cp "$SKILL_DIR/assets/needs-config.json" "$FAKE_WORKSPACE/skills/turing-pyramid/assets/"
cp "$SKILL_DIR/assets/needs-state.json" "$FAKE_WORKSPACE/skills/turing-pyramid/assets/"
cp "$SKILL_DIR/assets/scan-config.json" "$FAKE_WORKSPACE/skills/turing-pyramid/assets/" 2>/dev/null || true
cp -r "$SKILL_DIR/scripts" "$FAKE_WORKSPACE/skills/turing-pyramid/"

# Ensure scan-config.json exists with line-level default
cat > "$FAKE_WORKSPACE/skills/turing-pyramid/assets/scan-config.json" <<'EOF'
{"scan_method": "line-level", "fallback": "line-level"}
EOF

# Initialize state with fresh timestamps so time_sat=3
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq --arg t "$NOW" '
  to_entries | map(.value.last_satisfied = $t | .value.last_decay_check = $t | .value.satisfaction = 3) |
  from_entries
' "$FAKE_WORKSPACE/skills/turing-pyramid/assets/needs-state.json" > "$TMPDIR/state.tmp" && \
mv "$TMPDIR/state.tmp" "$FAKE_WORKSPACE/skills/turing-pyramid/assets/needs-state.json"

# Set today's date for memory file
TODAY=$(date +%Y-%m-%d)

cleanup() {
    rm -rf "$TMPDIR"
}
trap cleanup EXIT

assert_eq() {
    local label="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $label (expected=$expected, got=$actual)"
    else
        echo "  FAIL: $label (expected=$expected, got=$actual)"
        ((errors++)) || true
    fi
}

# ─── TEST 1: Pure positive lines ───────────────────────────────
echo "Test 1: Pure positive lines → high satisfaction"

cat > "$FAKE_WORKSPACE/memory/$TODAY.md" <<'EOF'
## Work Log
Completed the paper draft
Achieved major milestone today
Published new version to ClawHub
Built a new feature successfully
Implemented the scanner fix
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" SKIP_SCANS="" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
assert_eq "pure_positive" "3" "$result"

# ─── TEST 2: Pure negative lines ──────────────────────────────
echo "Test 2: Pure negative lines → low satisfaction"

cat > "$FAKE_WORKSPACE/memory/$TODAY.md" <<'EOF'
## Problems
Everything is broken
Can't figure out the error
The system crashed again
Still stuck on this bug
Failed to deploy
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" SKIP_SCANS="" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
assert_eq "pure_negative" "0" "$result"

# ─── TEST 3: Mixed context — positive should win ──────────────
echo "Test 3: Mixed context lines → positive wins"

cat > "$FAKE_WORKSPACE/memory/$TODAY.md" <<'EOF'
## Work Log
Fixed the critical bug in scanner
Resolved the error in configuration
Worked around the crash issue
Solved the broken pipeline
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" SKIP_SCANS="" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
assert_eq "mixed_positive_wins" "3" "$result"

# ─── TEST 4: The exact bug case — old scanner failed here ─────
echo "Test 4: Regression — 'fixed a bug' should NOT count as failure"

cat > "$FAKE_WORKSPACE/memory/$TODAY.md" <<'EOF'
## Heartbeat
Bugs fixed: Rounding formula was producing wrong values
Error reviewed: Recognition scanner vocabulary mismatch
Fixed competence scanner vocabulary mismatch
Completed paper draft
Drafted methodology section
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" SKIP_SCANS="" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
# All 5 lines have positive words. Lines 1-3 also have negative, but positive wins.
# Net should be positive → sat=3
assert_eq "regression_mixed_context" "3" "$result"

# ─── TEST 5: Neutral content — should default to time-based ───
echo "Test 5: Neutral content → time-based satisfaction"

cat > "$FAKE_WORKSPACE/memory/$TODAY.md" <<'EOF'
## Notes
Discussed architecture with Max
Read through the documentation
Reviewed the project timeline
Thought about next steps
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" SKIP_SCANS="" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
# No positive or negative → defaults to time_sat (which is time-based)
# Should NOT be 0 (that would mean "failing")
if [[ "$result" -eq 0 ]]; then
    echo "  FAIL: neutral_not_failing (got 0, neutral should not mean failing)"
    ((errors++)) || true
else
    echo "  PASS: neutral_not_failing (got $result, correctly not 0)"
fi

# ─── TEST 6: Empty file ──────────────────────────────────────
echo "Test 6: Empty memory file → time-based, not failure"

cat > "$FAKE_WORKSPACE/memory/$TODAY.md" <<'EOF'
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" SKIP_SCANS="" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
if [[ "$result" -eq 0 ]]; then
    echo "  FAIL: empty_not_failing (got 0, empty should not mean failing)"
    ((errors++)) || true
else
    echo "  PASS: empty_not_failing (got $result, correctly not 0)"
fi

# ─── TEST 7: Headers should be skipped ────────────────────────
echo "Test 7: Headers with keywords should be ignored"

cat > "$FAKE_WORKSPACE/memory/$TODAY.md" <<'EOF'
# Error Handling Module
## Bug Tracking
### Failed Experiments Section
This is neutral content
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" SKIP_SCANS="" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
# Headers skipped → only "This is neutral content" → neutral → time-based
if [[ "$result" -eq 0 ]]; then
    echo "  FAIL: headers_skipped (got 0, headers should be ignored)"
    ((errors++)) || true
else
    echo "  PASS: headers_skipped (got $result, headers correctly ignored)"
fi

# ─── TEST 8: Yesterday's file is also scanned ─────────────────
echo "Test 8: Yesterday's file contributes to scanning"

YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Today: neutral
cat > "$FAKE_WORKSPACE/memory/$TODAY.md" <<'EOF'
Just a regular day
EOF

# Yesterday: lots of successes
cat > "$FAKE_WORKSPACE/memory/$YESTERDAY.md" <<'EOF'
Completed the entire project
Shipped the release
Achieved all goals
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" SKIP_SCANS="" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
assert_eq "yesterday_scanned" "3" "$result"

# ─── RESULTS ──────────────────────────────────────────────────
echo ""
echo "Scan competence tests: $errors error(s)"
[[ $errors -eq 0 ]]
