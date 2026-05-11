#!/usr/bin/env bash
# validate-structure.sh <skill-dir>
# Validates that a skill directory has all required structural components.
# Scores 1 point per check (8 total). Exits 0 if 8/8, exits 1 otherwise.

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

SCORE=0
TOTAL=8
RESULTS=()

pass() { SCORE=$((SCORE + 1)); RESULTS+=("  ✅ $1"); }
fail() {                        RESULTS+=("  ❌ $1"); }

# ── Check 1: SKILL.md exists ──────────────────────────────────────────────────
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
  pass "SKILL.md exists"
else
  fail "SKILL.md missing"
fi

# ── Check 2: skill.yml exists ─────────────────────────────────────────────────
if [[ -f "$SKILL_DIR/skill.yml" ]]; then
  pass "skill.yml exists"
else
  fail "skill.yml missing"
fi

# ── Check 3: README.md exists ─────────────────────────────────────────────────
if [[ -f "$SKILL_DIR/README.md" ]]; then
  pass "README.md exists"
else
  fail "README.md missing"
fi

# ── Check 4: skill.yml has required fields (name, description, version, triggers)
if [[ -f "$SKILL_DIR/skill.yml" ]]; then
  MISSING_FIELDS=()
  grep -q '^name:' "$SKILL_DIR/skill.yml"        || MISSING_FIELDS+=("name")
  grep -q '^description:' "$SKILL_DIR/skill.yml" || MISSING_FIELDS+=("description")
  grep -q '^version:' "$SKILL_DIR/skill.yml"     || MISSING_FIELDS+=("version")
  grep -q '^triggers:' "$SKILL_DIR/skill.yml"    || MISSING_FIELDS+=("triggers")
  if [[ ${#MISSING_FIELDS[@]} -eq 0 ]]; then
    pass "skill.yml has required fields (name, description, version, triggers)"
  else
    fail "skill.yml missing fields: ${MISSING_FIELDS[*]}"
  fi
else
  fail "skill.yml missing fields (file absent)"
fi

# ── Check 5: SKILL.md has ## Configuration section ───────────────────────────
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
  if grep -q '^## Configuration' "$SKILL_DIR/SKILL.md"; then
    pass "SKILL.md has ## Configuration section"
  else
    fail "SKILL.md missing ## Configuration section"
  fi
else
  fail "SKILL.md missing ## Configuration section (file absent)"
fi

# ── Check 6: SKILL.md has trigger words ──────────────────────────────────────
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
  # Check for trigger words either in frontmatter or in a triggers section
  if grep -q 'trigger' "$SKILL_DIR/SKILL.md"; then
    pass "SKILL.md references trigger words"
  else
    fail "SKILL.md has no trigger words"
  fi
else
  fail "SKILL.md has no trigger words (file absent)"
fi

# ── Check 7: tests/ directory exists with at least 1 file ────────────────────
if [[ -d "$SKILL_DIR/tests" ]]; then
  FILE_COUNT=$(find "$SKILL_DIR/tests" -maxdepth 2 -type f | wc -l | tr -d ' ')
  if [[ "$FILE_COUNT" -ge 1 ]]; then
    pass "tests/ directory exists with $FILE_COUNT file(s)"
  else
    fail "tests/ directory exists but is empty"
  fi
else
  fail "tests/ directory missing"
fi

# ── Check 8: CHANGELOG.md exists ─────────────────────────────────────────────
if [[ -f "$SKILL_DIR/CHANGELOG.md" ]]; then
  pass "CHANGELOG.md exists"
else
  fail "CHANGELOG.md missing"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "Structure validation: $SKILL_DIR"
echo "──────────────────────────────────────────"
for r in "${RESULTS[@]}"; do echo "$r"; done
echo "──────────────────────────────────────────"
echo "Score: $SCORE/$TOTAL"
echo ""

if [[ "$SCORE" -eq "$TOTAL" ]]; then
  echo "✅ PASS — structure complete"
  exit 0
else
  echo "❌ FAIL — $((TOTAL - SCORE)) check(s) failed"
  exit 1
fi
