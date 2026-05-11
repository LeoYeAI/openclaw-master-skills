#!/usr/bin/env bash
# Test: Layer C — Context-Driven Spontaneity
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

errors=0
pass=0

assert_eq() {
    local desc=$1 expected=$2 actual=$3
    if [[ "$expected" == "$actual" ]]; then
        echo "  ✅ $desc"
        ((pass++))
    else
        echo "  ❌ $desc: expected '$expected', got '$actual'"
        ((errors++))
    fi
}

TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

export WORKSPACE="$TMP_DIR/workspace"
mkdir -p "$WORKSPACE/research" "$WORKSPACE/memory"

# Create a minimal skill structure in tmp
MOCK_SKILL="$TMP_DIR/skill"
mkdir -p "$MOCK_SKILL/assets" "$MOCK_SKILL/scripts"
cp "$SKILL_DIR/scripts/context-scan.sh" "$MOCK_SKILL/scripts/"
chmod +x "$MOCK_SKILL/scripts/context-scan.sh"

# Patch the script to use our mock skill dir
sed -i "s|SKILL_DIR=.*|SKILL_DIR=\"$MOCK_SKILL\"|" "$MOCK_SKILL/scripts/context-scan.sh"

echo "═══ Test Suite: Layer C — Context Scan ═══"
echo ""

# ── Test 1: First run with empty snapshot ──
echo "── Test 1: First run creates snapshot ──"

# Create test files
touch "$WORKSPACE/research/file1.md" "$WORKSPACE/research/file2.md"
echo "test" > "$WORKSPACE/INTENTIONS.md"
touch "$WORKSPACE/memory/day1.md"

cat > "$MOCK_SKILL/assets/context-triggers.json" << 'CONF'
{
  "snapshot_file": "last-scan-snapshot.json",
  "default_cooldown_hours": 0,
  "triggers": [
    {
      "id": "test-files",
      "detector": {"type": "file_count_delta", "path": "research/"},
      "threshold": 1,
      "boost": {"needs": ["understanding"], "amount": 0.05, "label": "[CONTEXT:test]"},
      "cooldown_hours": 0
    }
  ]
}
CONF

output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "first run fires trigger (delta from 0)" "1" "$trigger_count"

# Check snapshot was created
if [[ -f "$MOCK_SKILL/assets/last-scan-snapshot.json" ]]; then
    assert_eq "snapshot file created" "true" "true"
else
    assert_eq "snapshot file created" "true" "false"
fi

snapshot_count=$(jq -r '.file_counts."research/"' "$MOCK_SKILL/assets/last-scan-snapshot.json")
assert_eq "snapshot records file count" "2" "$snapshot_count"

# ── Test 2: No delta = no trigger ──
echo "── Test 2: No change = no trigger ──"
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "no delta no trigger" "0" "$trigger_count"

# ── Test 3: New file triggers ──
echo "── Test 3: New file detected ──"
touch "$WORKSPACE/research/file3.md"
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "new file triggers" "1" "$trigger_count"

# ── Test 4: file_modified detector ──
echo "── Test 4: File modified detection ──"
cat > "$MOCK_SKILL/assets/context-triggers.json" << 'CONF'
{
  "snapshot_file": "last-scan-snapshot.json",
  "triggers": [
    {
      "id": "test-modified",
      "detector": {"type": "file_modified", "path": "INTENTIONS.md"},
      "threshold": 1,
      "boost": {"needs": ["closure"], "amount": 0.04, "label": "[CONTEXT:mod]"},
      "cooldown_hours": 0
    }
  ]
}
CONF

# First run to set baseline
"$MOCK_SKILL/scripts/context-scan.sh" > /dev/null 2>&1

# Modify file
sleep 1
echo "changed" >> "$WORKSPACE/INTENTIONS.md"

output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "modified file triggers" "1" "$trigger_count"

# No change
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "unmodified file no trigger" "0" "$trigger_count"

# ── Test 5: Cooldown works ──
echo "── Test 5: Cooldown prevents re-fire ──"
cat > "$MOCK_SKILL/assets/context-triggers.json" << 'CONF'
{
  "snapshot_file": "last-scan-snapshot.json",
  "triggers": [
    {
      "id": "test-cooldown",
      "detector": {"type": "file_count_delta", "path": "research/"},
      "threshold": 1,
      "boost": {"needs": ["understanding"], "amount": 0.05, "label": "[CONTEXT:cd]"},
      "cooldown_hours": 24
    }
  ]
}
CONF

# First fire
touch "$WORKSPACE/research/file4.md"
"$MOCK_SKILL/scripts/context-scan.sh" > /dev/null 2>&1

# Try again with new file
touch "$WORKSPACE/research/file5.md"
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "cooldown blocks re-fire" "0" "$trigger_count"

# ── Test 6: Threshold > 1 ──
echo "── Test 6: Threshold filtering ──"
cat > "$MOCK_SKILL/assets/context-triggers.json" << 'CONF'
{
  "snapshot_file": "last-scan-snapshot.json",
  "triggers": [
    {
      "id": "test-threshold",
      "detector": {"type": "file_count_delta", "path": "research/"},
      "threshold": 3,
      "boost": {"needs": ["understanding"], "amount": 0.05, "label": "[CONTEXT:th]"},
      "cooldown_hours": 0
    }
  ]
}
CONF

# Reset snapshot
rm -f "$MOCK_SKILL/assets/last-scan-snapshot.json"
# Baseline
"$MOCK_SKILL/scripts/context-scan.sh" > /dev/null 2>&1

# Add 2 files (below threshold of 3)
touch "$WORKSPACE/research/file6.md" "$WORKSPACE/research/file7.md"
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "below threshold no trigger" "0" "$trigger_count"

# Add 1 more (now delta=1 from last snapshot which had +2)
touch "$WORKSPACE/research/file8.md" "$WORKSPACE/research/file9.md" "$WORKSPACE/research/file10.md"
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "above threshold triggers" "1" "$trigger_count"

# ── Test 7: file_keyword_delta detector ──
echo "── Test 7: Keyword delta detection ──"
cat > "$MOCK_SKILL/assets/context-triggers.json" << 'CONF'
{
  "snapshot_file": "last-scan-snapshot.json",
  "triggers": [
    {
      "id": "test-keywords",
      "detector": {
        "type": "file_keyword_delta",
        "path": "research/",
        "keywords": ["consciousness", "qualia"]
      },
      "threshold": 1,
      "boost": {"needs": ["understanding"], "amount": 0.06, "label": "[CONTEXT:kw]"},
      "cooldown_hours": 0
    }
  ]
}
CONF

# Reset snapshot and workspace
rm -f "$MOCK_SKILL/assets/last-scan-snapshot.json"
rm -f "$WORKSPACE/research/"*.md
# Create files WITHOUT keywords
echo "hello world" > "$WORKSPACE/research/plain.md"
# Baseline
"$MOCK_SKILL/scripts/context-scan.sh" > /dev/null 2>&1

# No new keywords — no trigger
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "no new keywords no trigger" "0" "$trigger_count"

# Add file WITH keyword
echo "exploring consciousness and awareness" > "$WORKSPACE/research/mind.md"
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "new keyword file triggers" "1" "$trigger_count"

# Verify boost need and label in output
boost_label=$(echo "$output" | grep -o '\[CONTEXT:kw\]' || true)
assert_eq "keyword trigger has correct label" "[CONTEXT:kw]" "$boost_label"

# No change — no trigger
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "same keywords no trigger" "0" "$trigger_count"

# Add second keyword in new file
echo "the hard problem of qualia" > "$WORKSPACE/research/qualia.md"
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "second keyword triggers" "1" "$trigger_count"

# Multiple keywords in same file — counts files not occurrences
echo "consciousness and qualia together" > "$WORKSPACE/research/both.md"
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "multi-keyword file triggers" "1" "$trigger_count"

# ── Test 8: Path traversal blocked ──
echo "── Test 8: Security — path traversal blocked ──"
cat > "$MOCK_SKILL/assets/context-triggers.json" << 'CONF'
{
  "snapshot_file": "last-scan-snapshot.json",
  "triggers": [
    {
      "id": "test-traversal",
      "detector": {"type": "file_count_delta", "path": "../../etc/"},
      "threshold": 1,
      "boost": {"needs": ["security"], "amount": 0.05, "label": "[CONTEXT:evil]"},
      "cooldown_hours": 0
    }
  ]
}
CONF

rm -f "$MOCK_SKILL/assets/last-scan-snapshot.json"
output=$("$MOCK_SKILL/scripts/context-scan.sh" 2>/dev/null)
trigger_count=$(echo "$output" | grep -c '"id"' || true)
assert_eq "path traversal blocked" "0" "$trigger_count"

# Verify BLOCKED message in stderr
stderr_out=$("$MOCK_SKILL/scripts/context-scan.sh" 2>&1 1>/dev/null)
blocked=$(echo "$stderr_out" | grep -c "BLOCKED" || true)
assert_eq "BLOCKED message in logs" "1" "$blocked"

# ── Test 9: Boost accumulation in spontaneity.sh ──
echo "── Test 9: Context boost accumulation ──"
source "$SKILL_DIR/scripts/spontaneity.sh"
CONTEXT_BOOSTS=()
CONTEXT_LABELS=()
CONTEXT_BOOSTS[understanding]="0.05"
CONTEXT_BOOSTS[expression]="0.03"
CONTEXT_LABELS[understanding]="[CONTEXT:test1]"

boost=$(get_context_boost "understanding")
assert_eq "get_context_boost returns value" "0.05" "$boost"

boost=$(get_context_boost "security")
assert_eq "get_context_boost missing need returns 0" "0" "$boost"

label=$(get_context_label "understanding")
assert_eq "get_context_label returns label" "[CONTEXT:test1]" "$label"

echo ""
echo "═══════════════════════════════════"
echo "Results: $pass passed, $errors failed"
echo "═══════════════════════════════════"

exit $errors
