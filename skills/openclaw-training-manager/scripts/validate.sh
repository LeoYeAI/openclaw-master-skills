#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
MAX_CHARS=20000

errors=0
warnings=0

echo "=== Workspace Validation ==="
echo "Workspace: $WORKSPACE"
echo ""

# Check workspace exists
if [ ! -d "$WORKSPACE" ]; then
  echo "FATAL: Workspace directory does not exist: $WORKSPACE"
  exit 1
fi

# Check bootstrap files
BOOTSTRAP_FILES=("SOUL.md" "AGENTS.md" "TOOLS.md" "IDENTITY.md" "USER.md" "MEMORY.md")

echo "--- Bootstrap Files ---"
for file in "${BOOTSTRAP_FILES[@]}"; do
  path="$WORKSPACE/$file"
  if [ ! -f "$path" ]; then
    echo "  MISSING: $file"
    errors=$((errors + 1))
  elif [ ! -s "$path" ]; then
    echo "  EMPTY:   $file"
    warnings=$((warnings + 1))
  else
    chars=$(wc -c < "$path" | tr -d ' ')
    if [ "$chars" -gt "$MAX_CHARS" ]; then
      echo "  TOOLONG: $file ($chars chars, limit $MAX_CHARS)"
      warnings=$((warnings + 1))
    else
      echo "  OK:      $file ($chars chars)"
    fi
  fi
done

# Check memory directory
echo ""
echo "--- Memory ---"
if [ ! -d "$WORKSPACE/memory" ]; then
  echo "  MISSING: memory/ directory"
  warnings=$((warnings + 1))
else
  log_count=$(find "$WORKSPACE/memory" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "  Daily logs: $log_count"

  # Check for logs with bad date format
  bad_names=$(find "$WORKSPACE/memory" -name "*.md" -type f 2>/dev/null | while read -r f; do
    basename "$f" .md
  done | grep -cvE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' || true)
  if [ "$bad_names" -gt 0 ]; then
    echo "  WARNING: $bad_names files don't match YYYY-MM-DD.md format"
    warnings=$((warnings + 1))
  fi
fi

# Check skills
echo ""
echo "--- Skills ---"
if [ ! -d "$WORKSPACE/skills" ]; then
  echo "  No skills/ directory"
else
  skill_count=0
  skill_errors=0

  for skill_dir in "$WORKSPACE/skills"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    skill_file="$skill_dir/SKILL.md"
    skill_count=$((skill_count + 1))

    if [ ! -f "$skill_file" ]; then
      echo "  ERROR: $skill_name/ missing SKILL.md"
      skill_errors=$((skill_errors + 1))
      errors=$((errors + 1))
      continue
    fi

    # Check for YAML frontmatter
    first_line=$(head -1 "$skill_file")
    if [ "$first_line" != "---" ]; then
      echo "  ERROR: $skill_name/SKILL.md missing YAML frontmatter"
      skill_errors=$((skill_errors + 1))
      errors=$((errors + 1))
      continue
    fi

    # Check for required fields
    has_name=$(sed -n '/^---$/,/^---$/p' "$skill_file" | grep -c '^name:' || true)
    has_desc=$(sed -n '/^---$/,/^---$/p' "$skill_file" | grep -c '^description:' || true)

    if [ "$has_name" -eq 0 ]; then
      echo "  ERROR: $skill_name/SKILL.md missing 'name' field"
      errors=$((errors + 1))
    fi
    if [ "$has_desc" -eq 0 ]; then
      echo "  ERROR: $skill_name/SKILL.md missing 'description' field"
      errors=$((errors + 1))
    fi

    if [ "$has_name" -gt 0 ] && [ "$has_desc" -gt 0 ]; then
      chars=$(wc -c < "$skill_file" | tr -d ' ')
      echo "  OK: $skill_name ($chars chars)"
    fi
  done

  echo ""
  echo "  Total skills: $skill_count"
  if [ "$skill_errors" -gt 0 ]; then
    echo "  Skills with errors: $skill_errors"
  fi
fi

# Summary
echo ""
echo "=== Summary ==="
echo "  Errors:   $errors"
echo "  Warnings: $warnings"

if [ "$errors" -gt 0 ]; then
  echo ""
  echo "Fix errors before deploying. Run 'scaffold' to create missing files."
  exit 1
elif [ "$warnings" -gt 0 ]; then
  echo ""
  echo "Workspace is usable but has warnings to address."
  exit 0
else
  echo ""
  echo "Workspace looks good."
  exit 0
fi
