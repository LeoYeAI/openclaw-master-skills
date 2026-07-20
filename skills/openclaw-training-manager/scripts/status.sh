#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"

echo "=== Training Status ==="
echo "Workspace: $WORKSPACE"
echo ""

if [ ! -d "$WORKSPACE" ]; then
  echo "Workspace does not exist. Run scaffold first."
  exit 1
fi

# Bootstrap files
echo "--- Bootstrap Files ---"
BOOTSTRAP_FILES=("SOUL.md" "AGENTS.md" "TOOLS.md" "IDENTITY.md" "USER.md" "MEMORY.md")

printf "  %-15s %-8s %-20s\n" "FILE" "SIZE" "LAST MODIFIED"
printf "  %-15s %-8s %-20s\n" "----" "----" "-------------"

for file in "${BOOTSTRAP_FILES[@]}"; do
  path="$WORKSPACE/$file"
  if [ -f "$path" ]; then
    size=$(wc -c < "$path" | tr -d ' ')
    modified=$(stat -c '%Y' "$path" 2>/dev/null || stat -f '%m' "$path" 2>/dev/null)
    modified_human=$(date -d "@$modified" '+%Y-%m-%d %H:%M' 2>/dev/null || date -r "$modified" '+%Y-%m-%d %H:%M' 2>/dev/null)
    printf "  %-15s %-8s %-20s\n" "$file" "${size}b" "$modified_human"
  else
    printf "  %-15s %-8s %-20s\n" "$file" "--" "(missing)"
  fi
done

# Skills
echo ""
echo "--- Skills ---"
if [ -d "$WORKSPACE/skills" ]; then
  skill_count=$(find "$WORKSPACE/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  echo "  Total skills: $skill_count"

  if [ "$skill_count" -gt 0 ]; then
    echo ""
    for skill_dir in "$WORKSPACE/skills"/*/; do
      [ -d "$skill_dir" ] || continue
      name=$(basename "$skill_dir")
      skill_file="$skill_dir/SKILL.md"
      if [ -f "$skill_file" ]; then
        desc=$(sed -n '/^---$/,/^---$/{ /^description:/p }' "$skill_file" | head -1 | sed 's/^description: *//')
        echo "  - $name: $desc"
      else
        echo "  - $name: (no SKILL.md)"
      fi
    done
  fi
else
  echo "  No skills/ directory"
fi

# Memory
echo ""
echo "--- Memory ---"
if [ -f "$WORKSPACE/MEMORY.md" ]; then
  mem_size=$(wc -c < "$WORKSPACE/MEMORY.md" | tr -d ' ')
  mem_lines=$(wc -l < "$WORKSPACE/MEMORY.md" | tr -d ' ')
  echo "  MEMORY.md: ${mem_size}b, $mem_lines lines"
else
  echo "  MEMORY.md: (missing)"
fi

if [ -d "$WORKSPACE/memory" ]; then
  log_count=$(find "$WORKSPACE/memory" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "  Daily logs: $log_count"

  if [ "$log_count" -gt 0 ]; then
    latest=$(find "$WORKSPACE/memory" -name "*.md" -type f 2>/dev/null | sort -r | head -1)
    echo "  Latest: $(basename "$latest")"
  fi
else
  echo "  Daily logs: (no memory/ directory)"
fi

# Disk usage
echo ""
echo "--- Disk Usage ---"
total=$(du -sh "$WORKSPACE" 2>/dev/null | cut -f1)
echo "  Total workspace: $total"
