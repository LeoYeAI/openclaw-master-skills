#!/usr/bin/env bash
# Test: scan-config.json parsing and method selection
# Verifies:
#   1. Default method is line-level when no config exists
#   2. Config file is read correctly for each method
#   3. Invalid/missing config gracefully falls back to line-level
#   4. Fallback field is respected

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

errors=0

# Create temp workspace
TMPDIR=$(mktemp -d)
FAKE_WORKSPACE="$TMPDIR/workspace"
mkdir -p "$FAKE_WORKSPACE/memory"
mkdir -p "$FAKE_WORKSPACE/skills/turing-pyramid/assets"
cp "$SKILL_DIR/assets/needs-config.json" "$FAKE_WORKSPACE/skills/turing-pyramid/assets/"
cp "$SKILL_DIR/assets/needs-state.json" "$FAKE_WORKSPACE/skills/turing-pyramid/assets/"
cp -r "$SKILL_DIR/scripts" "$FAKE_WORKSPACE/skills/turing-pyramid/"

TODAY=$(date +%Y-%m-%d)

# Initialize state with fresh timestamps so time_sat=3
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq --arg t "$NOW" '
  to_entries | map(.value.last_satisfied = $t | .value.last_decay_check = $t | .value.satisfaction = 3) |
  from_entries
' "$FAKE_WORKSPACE/skills/turing-pyramid/assets/needs-state.json" > "$TMPDIR/state.tmp" && \
mv "$TMPDIR/state.tmp" "$FAKE_WORKSPACE/skills/turing-pyramid/assets/needs-state.json"

# Standard test memory
cat > "$FAKE_WORKSPACE/memory/$TODAY.md" <<'EOF'
Completed a task successfully
EOF

cleanup() {
    rm -rf "$TMPDIR"
}
trap cleanup EXIT

assert_eq() {
    local label="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $label"
    else
        echo "  FAIL: $label (expected=$expected, got=$actual)"
        ((errors++)) || true
    fi
}

# ─── TEST 1: No config file → defaults to line-level ──────────
echo "Test 1: No scan-config.json → line-level default"

rm -f "$FAKE_WORKSPACE/skills/turing-pyramid/assets/scan-config.json"
result=$(WORKSPACE="$FAKE_WORKSPACE" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
# Should work (line-level), not crash
if [[ $? -eq 0 && -n "$result" ]]; then
    echo "  PASS: runs without config"
else
    echo "  FAIL: crashed without config"
    ((errors++)) || true
fi

# ─── TEST 2: Explicit line-level config ────────────────────────
echo "Test 2: Explicit line-level config"

cat > "$FAKE_WORKSPACE/skills/turing-pyramid/assets/scan-config.json" <<'EOF'
{"scan_method": "line-level", "fallback": "line-level"}
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
assert_eq "line_level_config" "2" "$result"

# ─── TEST 3: agent-spawn config falls back to line-level in bash ─
echo "Test 3: agent-spawn config → falls back to line-level in bash"

cat > "$FAKE_WORKSPACE/skills/turing-pyramid/assets/scan-config.json" <<'EOF'
{"scan_method": "agent-spawn", "agent_spawn": {"enabled": true, "model": "claude-haiku"}, "fallback": "line-level"}
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
# agent-spawn called from bash → should fall back to line-level
assert_eq "agent_spawn_fallback" "2" "$result"

# ─── TEST 4: external-model config falls back to line-level ───
echo "Test 4: external-model config → falls back to line-level in bash"

cat > "$FAKE_WORKSPACE/skills/turing-pyramid/assets/scan-config.json" <<'EOF'
{"scan_method": "external-model", "external_model": {"enabled": true}, "fallback": "line-level"}
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
assert_eq "external_model_fallback" "2" "$result"

# ─── TEST 5: Malformed JSON config → defaults gracefully ──────
echo "Test 5: Malformed config JSON → graceful default"

echo "this is not json" > "$FAKE_WORKSPACE/skills/turing-pyramid/assets/scan-config.json"
result=$(WORKSPACE="$FAKE_WORKSPACE" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
if [[ $? -eq 0 && -n "$result" ]]; then
    echo "  PASS: survives malformed config"
else
    echo "  FAIL: crashed on malformed config"
    ((errors++)) || true
fi

# ─── TEST 6: Unknown method → defaults to line-level ──────────
echo "Test 6: Unknown scan method → line-level fallback"

cat > "$FAKE_WORKSPACE/skills/turing-pyramid/assets/scan-config.json" <<'EOF'
{"scan_method": "quantum-telepathy", "fallback": "line-level"}
EOF

result=$(WORKSPACE="$FAKE_WORKSPACE" "$FAKE_WORKSPACE/skills/turing-pyramid/scripts/scan_competence.sh" 2>/dev/null)
assert_eq "unknown_method_fallback" "2" "$result"

# ─── RESULTS ──────────────────────────────────────────────────
echo ""
echo "Scan config tests: $errors error(s)"
[[ $errors -eq 0 ]]
