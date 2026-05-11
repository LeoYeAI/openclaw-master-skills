#!/usr/bin/env bash
# validate-release-content.sh <skill-dir>
# Validates that a skill release directory has no placeholder text, no empty
# files, and a substantive README.md.
# Prints PASS/FAIL per check. Exits 0 if all pass, exits 1 if any fail.

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

ALL_PASS=true
RESULTS=()

pass() { RESULTS+=("  ✅ PASS — $1"); }
fail() { RESULTS+=("  ❌ FAIL — $1"); ALL_PASS=false; }

# ── Check 1: No placeholder text ─────────────────────────────────────────────
PLACEHOLDER_PATTERNS=('\{\{' 'TODO' 'FIXME' 'YOUR_')
PLACEHOLDER_HITS=()

# Scan content files only (not shell scripts — they may reference these
# patterns as search strings in grep commands).
for pattern in "${PLACEHOLDER_PATTERNS[@]}"; do
  MATCHES=$(grep -r "$pattern" "$SKILL_DIR" \
    --include="*.md" --include="*.yml" --include="*.yaml" \
    --include="*.json" --include="*.txt" \
    --exclude-dir=scripts \
    -l 2>/dev/null || true)
  if [[ -n "$MATCHES" ]]; then
    while IFS= read -r file; do
      PLACEHOLDER_HITS+=("$file (pattern: $pattern)")
    done <<< "$MATCHES"
  fi
done

if [[ ${#PLACEHOLDER_HITS[@]} -eq 0 ]]; then
  pass "No placeholder text found ({{, TODO, FIXME, YOUR_)"
else
  fail "Placeholder text found in:"
  for hit in "${PLACEHOLDER_HITS[@]}"; do
    RESULTS+=("       • $hit")
  done
fi

# ── Check 2: No empty files (< 50 bytes) ─────────────────────────────────────
EMPTY_FILES=()
while IFS= read -r -d '' f; do
  SIZE=$(wc -c < "$f" | tr -d ' ')
  if [[ "$SIZE" -lt 50 ]]; then
    EMPTY_FILES+=("$f ($SIZE bytes)")
  fi
done < <(find "$SKILL_DIR" -type f \
  -not -path "*/.git/*" \
  -not -name ".git" \
  -not -name ".gitmodules" \
  -print0)

if [[ ${#EMPTY_FILES[@]} -eq 0 ]]; then
  pass "No empty files (all files ≥ 50 bytes)"
else
  fail "Files smaller than 50 bytes:"
  for f in "${EMPTY_FILES[@]}"; do
    RESULTS+=("       • $f")
  done
fi

# ── Check 3: README.md has at least 200 chars ─────────────────────────────────
README="$SKILL_DIR/README.md"
if [[ -f "$README" ]]; then
  CHAR_COUNT=$(wc -c < "$README" | tr -d ' ')
  if [[ "$CHAR_COUNT" -ge 200 ]]; then
    pass "README.md has $CHAR_COUNT chars (≥ 200 required)"
  else
    fail "README.md too short: $CHAR_COUNT chars (need ≥ 200)"
  fi
else
  fail "README.md not found"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "Release content validation: $SKILL_DIR"
echo "──────────────────────────────────────────"
for r in "${RESULTS[@]}"; do echo "$r"; done
echo "──────────────────────────────────────────"
echo ""

if [[ "$ALL_PASS" == "true" ]]; then
  echo "✅ PASS — release content is clean"
  exit 0
else
  echo "❌ FAIL — release content has issues (see above)"
  exit 1
fi
