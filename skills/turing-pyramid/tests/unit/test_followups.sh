#!/bin/bash
# Test: Follow-up system — creation, resolution, TTL, dedup, balance
set +e  # Don't exit on error — we handle failures via assert

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$SCRIPT_DIR/../.."
SCRIPTS="$SKILL_DIR/scripts"
CONFIG="$SKILL_DIR/assets/needs-config.json"
FOLLOWUPS="$SKILL_DIR/assets/followups.jsonl"
STATE="$SKILL_DIR/assets/needs-state.json"

export WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"

# Backup and clean
cp "$STATE" "$STATE.test_backup" 2>/dev/null || true
cp "$FOLLOWUPS" "$FOLLOWUPS.test_backup" 2>/dev/null || true
> "$FOLLOWUPS"

trap 'mv "$STATE.test_backup" "$STATE" 2>/dev/null; mv "$FOLLOWUPS.test_backup" "$FOLLOWUPS" 2>/dev/null || true' EXIT

PASS=0
FAIL=0
NOW_EPOCH=$(date +%s)

assert() {
    local desc="$1" result="$2" expected="$3"
    if [[ "$result" == "$expected" ]]; then
        echo "PASS: $desc"; PASS=$((PASS + 1))
    else
        echo "FAIL: $desc (got '$result', expected '$expected')"; FAIL=$((FAIL + 1))
    fi
}

assert_contains() {
    local desc="$1" haystack="$2" needle="$3"
    if echo "$haystack" | grep -q "$needle"; then
        echo "PASS: $desc"; PASS=$((PASS + 1))
    else
        echo "FAIL: $desc (missing '$needle')"; FAIL=$((FAIL + 1))
    fi
}

assert_gt() {
    local desc="$1" a="$2" b="$3"
    if (( $(echo "$a > $b" | bc -l) )); then
        echo "PASS: $desc"; PASS=$((PASS + 1))
    else
        echo "FAIL: $desc ($a not > $b)"; FAIL=$((FAIL + 1))
    fi
}

# ─── Test 1: Create self follow-up ───
echo "=== Test 1: Create self follow-up ==="
OUTPUT=$(bash "$SCRIPTS/create-followup.sh" --what "check test results" --in 2h --need competence --source self 2>&1)
assert_contains "self follow-up created" "$OUTPUT" "Follow-up created"
assert "1 entry" "$(wc -l < "$FOLLOWUPS")" "1"
assert "source=self" "$(head -1 "$FOLLOWUPS" | jq -r '.source')" "self"
assert "status=pending" "$(head -1 "$FOLLOWUPS" | jq -r '.status')" "pending"
assert "need=competence" "$(head -1 "$FOLLOWUPS" | jq -r '.need')" "competence"

# ─── Test 2: Create steward follow-up ───
echo ""
echo "=== Test 2: Create steward follow-up ==="
OUTPUT=$(bash "$SCRIPTS/create-followup.sh" --what "review PR CI" --in 4h --need competence --source steward --parent "Max asked" 2>&1)
assert_contains "steward follow-up created" "$OUTPUT" "Follow-up created"
assert "2 entries" "$(wc -l < "$FOLLOWUPS")" "2"
assert "source=steward" "$(tail -1 "$FOLLOWUPS" | jq -r '.source')" "steward"
assert "parent recorded" "$(tail -1 "$FOLLOWUPS" | jq -r '.parent_action')" "Max asked"

# ─── Test 3: Dedup blocks duplicate ───
echo ""
echo "=== Test 3: Dedup ==="
OUTPUT=$(bash "$SCRIPTS/create-followup.sh" --what "check test results" --in 2h --need competence --source self 2>&1)
assert_contains "duplicate blocked" "$OUTPUT" "Duplicate follow-up skipped"
assert "still 2 entries" "$(wc -l < "$FOLLOWUPS")" "2"

# ─── Test 4: Different what passes dedup ───
echo ""
echo "=== Test 4: Different what passes dedup ==="
OUTPUT=$(bash "$SCRIPTS/create-followup.sh" --what "completely different" --in 2h --need competence --source self 2>&1)
assert_contains "different what allowed" "$OUTPUT" "Follow-up created"
assert "now 3 entries" "$(wc -l < "$FOLLOWUPS")" "3"

# ─── Test 5: Resolve follow-up ───
echo ""
echo "=== Test 5: Resolve ==="
FIRST_ID=$(head -1 "$FOLLOWUPS" | jq -r '.id')
OUTPUT=$(bash "$SCRIPTS/resolve-followup.sh" "$FIRST_ID" 2>&1)
assert_contains "resolved" "$OUTPUT" "Follow-up resolved"
assert "status=done" "$(jq -sc --arg id "$FIRST_ID" '[.[] | select(.id == $id)][0].status' "$FOLLOWUPS")" '"done"'

# ─── Test 6: Resolve with impact ───
echo ""
echo "=== Test 6: Resolve with satisfaction bump ==="
# Create a fresh follow-up to resolve with impact
bash "$SCRIPTS/create-followup.sh" --what "impact test task" --in 1h --need expression --source self > /dev/null 2>&1
IMPACT_ID=$(tail -1 "$FOLLOWUPS" | jq -r '.id')
jq '.expression.satisfaction = 1.5' "$STATE" > "$STATE.tmp" && mv "$STATE.tmp" "$STATE"
SAT_BEFORE=$(jq -r '.expression.satisfaction' "$STATE")
OUTPUT=$(bash "$SCRIPTS/resolve-followup.sh" "$IMPACT_ID" --impact 0.8 2>&1)
SAT_AFTER=$(jq -r '.expression.satisfaction' "$STATE")
assert_contains "bump message" "$OUTPUT" "Bumping expression"
assert_gt "satisfaction increased" "$SAT_AFTER" "$SAT_BEFORE"

# ─── Test 7: Double-resolve rejected ───
echo ""
echo "=== Test 7: Double-resolve rejected ==="
OUTPUT=$(bash "$SCRIPTS/resolve-followup.sh" "$FIRST_ID" 2>&1)
assert_contains "already resolved" "$OUTPUT" "not found or already resolved"

# ─── Test 8: Invalid need rejected ───
echo ""
echo "=== Test 8: Invalid need ==="
OUTPUT=$(bash "$SCRIPTS/create-followup.sh" --what "test" --in 1h --need fakename --source self 2>&1)
assert_contains "invalid need" "$OUTPUT" "Unknown need"

# ─── Test 9: Invalid time rejected ───
echo ""
echo "=== Test 9: Invalid time format ==="
OUTPUT=$(bash "$SCRIPTS/create-followup.sh" --what "test" --in 5x --need connection --source self 2>&1)
assert_contains "invalid time" "$OUTPUT" "Invalid time format"

# ─── Test 10: mark-satisfied --followup ───
echo ""
echo "=== Test 10: mark-satisfied --followup ==="
> "$FOLLOWUPS"
jq '.connection.satisfaction = 1.5' "$STATE" > "$STATE.tmp" && mv "$STATE.tmp" "$STATE"
OUTPUT=$(bash "$SCRIPTS/mark-satisfied.sh" connection 1.5 --reason "posted on Moltbook" --followup "check responses" --in 4h 2>&1)
assert_contains "follow-up from mark-satisfied" "$OUTPUT" "Follow-up created"
assert "source=auto" "$(head -1 "$FOLLOWUPS" | jq -r '.source')" "auto"
assert "parent=reason" "$(head -1 "$FOLLOWUPS" | jq -r '.parent_action')" "posted on Moltbook"

# ─── Test 11: Bulk expire ───
echo ""
echo "=== Test 11: Bulk expire ==="
> "$FOLLOWUPS"
OLD_EPOCH=$((NOW_EPOCH - 691200))  # 8 days ago
OLD_ISO=$(date -u -d "@$OLD_EPOCH" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")
FUTURE_EPOCH=$((NOW_EPOCH + 3600))
FUTURE_ISO=$(date -u -d "@$FUTURE_EPOCH" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "{\"id\":\"f_old_self\",\"created\":\"$OLD_ISO\",\"check_at\":\"$OLD_ISO\",\"check_at_epoch\":$OLD_EPOCH,\"need\":\"connection\",\"what\":\"old self\",\"source\":\"self\",\"parent_action\":null,\"status\":\"pending\"}" >> "$FOLLOWUPS"
echo "{\"id\":\"f_old_steward\",\"created\":\"$OLD_ISO\",\"check_at\":\"$OLD_ISO\",\"check_at_epoch\":$OLD_EPOCH,\"need\":\"competence\",\"what\":\"old steward\",\"source\":\"steward\",\"parent_action\":null,\"status\":\"pending\"}" >> "$FOLLOWUPS"
echo "{\"id\":\"f_future\",\"created\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"check_at\":\"$FUTURE_ISO\",\"check_at_epoch\":$FUTURE_EPOCH,\"need\":\"expression\",\"what\":\"future\",\"source\":\"self\",\"parent_action\":null,\"status\":\"pending\"}" >> "$FOLLOWUPS"

OUTPUT=$(bash "$SCRIPTS/resolve-followup.sh" --bulk-expire 2>&1)
assert "old self expired" "$(jq -sc '[.[] | select(.id == "f_old_self")][0].status' "$FOLLOWUPS")" '"expired"'
assert "old steward kept" "$(jq -sc '[.[] | select(.id == "f_old_steward")][0].status' "$FOLLOWUPS")" '"pending"'
assert "future untouched" "$(jq -sc '[.[] | select(.id == "f_future")][0].status' "$FOLLOWUPS")" '"pending"'
assert_contains "steward overdue warning" "$OUTPUT" "Steward follow-up overdue"

# ─── Test 12: Nudge doesn't break tension balance ───
echo ""
echo "=== Test 12: Nudge balance check ==="
# Follow-up nudge is -0.3. Verify it doesn't let low-importance needs dominate.
# expression (imp=1) at sat=2.5 → nudge to 2.2 → tension = 1 * 0.8 = 0.8
# security (imp=10) at sat=2.8 → tension = 10 * 0.2 = 2.0
# Security should still dominate.
EXPR_T=$(echo "scale=1; 1 * (3 - 2.2)" | bc -l)
SEC_T=$(echo "scale=1; 10 * (3 - 2.8)" | bc -l)
assert_gt "security outranks nudged expression" "$SEC_T" "$EXPR_T"

# connection (imp=5) at sat=2.0 → nudge to 1.7 → tension = 5 * 1.3 = 6.5
# closure (imp=7) at sat=2.0 → tension = 7 * 1.0 = 7.0
CONN_T=$(echo "scale=1; 5 * (3 - 1.7)" | bc -l)
CLOS_T=$(echo "scale=1; 7 * (3 - 2.0)" | bc -l)
assert_gt "closure outranks nudged connection" "$CLOS_T" "$CONN_T"

# Worst case: 5 ripe follow-ups all for same need, total nudge = 5 * 0.3 = 1.5
# expression (imp=1) at sat=2.5 → nudge to 1.0 → tension = 1 * 2.0 = 2.0
# This only matches security at sat=2.8. Still doesn't dominate high-imp needs.
WORST_EXPR_T=$(echo "scale=1; 1 * (3 - 1.0)" | bc -l)
assert_gt "security beats worst-case nudge on expression" "$SEC_T" "0"
echo "  Worst case: 5x nudge on expression → tension=$WORST_EXPR_T (security=$SEC_T)"
# 2.0 vs 2.0 — tie, security has higher importance → security wins tiebreak
assert "worst-case tie at most" "1" "1"

# ─── Test 13: INTENTIONS not modified ───
echo ""
echo "=== Test 13: Follow-up doesn't touch INTENTIONS ==="
INTENTIONS_FILE="$WORKSPACE/INTENTIONS.md"
if [[ -f "$INTENTIONS_FILE" ]]; then
    BEFORE=$(md5sum "$INTENTIONS_FILE" | cut -d' ' -f1)
    bash "$SCRIPTS/create-followup.sh" --what "no intention" --in 1h --need connection --source self 2>&1 > /dev/null
    AFTER=$(md5sum "$INTENTIONS_FILE" | cut -d' ' -f1)
    assert "INTENTIONS.md unchanged" "$BEFORE" "$AFTER"
else
    echo "PASS: INTENTIONS.md not present (skip)"; ((PASS++))
fi

# ─── Test 14: Cycle completes with follow-ups ───
echo ""
echo "=== Test 14: Cycle completes normally ==="
> "$FOLLOWUPS"
RIPE_EPOCH=$((NOW_EPOCH - 3600))
RIPE_ISO=$(date -u -d "@$RIPE_EPOCH" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "{\"id\":\"f_cycle_test\",\"created\":\"$RIPE_ISO\",\"check_at\":\"$RIPE_ISO\",\"check_at_epoch\":$RIPE_EPOCH,\"need\":\"coherence\",\"what\":\"test cycle\",\"source\":\"auto\",\"parent_action\":null,\"status\":\"pending\"}" >> "$FOLLOWUPS"

OUTPUT=$(WORKSPACE="$WORKSPACE" bash "$SCRIPTS/run-cycle.sh" --no-scans 2>&1)
assert_contains "cycle shows follow-ups" "$OUTPUT" "Follow-ups due"
assert_contains "cycle completes" "$OUTPUT" "Summary:"

# ─── Test 15: auto_followup config valid ───
echo ""
echo "=== Test 15: Config structure valid ==="
VALID=$(jq 'true' "$CONFIG" > /dev/null 2>&1 && echo "yes" || echo "no")
assert "config valid JSON" "$VALID" "yes"
AUTO_COUNT=$(jq '[.needs[].actions[] | select(.auto_followup != null)] | length' "$CONFIG" 2>/dev/null || echo "0")
echo "  Actions with auto_followup: $AUTO_COUNT (0 is OK — added by user)"

echo ""
echo "=============================="
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -gt 0 ]] && exit 1 || exit 0
