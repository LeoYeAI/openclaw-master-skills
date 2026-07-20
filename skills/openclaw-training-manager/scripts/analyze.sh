#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
MAX_CHARS=20000
STALE_DAYS=90
DEEP=false

# Parse flags
for arg in "$@"; do
  case "$arg" in
    --deep) DEEP=true ;;
  esac
done

# --- Findings accumulator ---
HIGH_COUNT=0
MED_COUNT=0
LOW_COUNT=0
FINDINGS=""

add_finding() {
  local level="$1"
  local message="$2"
  case "$level" in
    HIGH) HIGH_COUNT=$((HIGH_COUNT + 1)); FINDINGS="${FINDINGS}  [HIGH] ${message}\n" ;;
    MED)  MED_COUNT=$((MED_COUNT + 1));   FINDINGS="${FINDINGS}  [MED]  ${message}\n" ;;
    LOW)  LOW_COUNT=$((LOW_COUNT + 1));    FINDINGS="${FINDINGS}  [LOW]  ${message}\n" ;;
  esac
}

# =============================================================================
# CHECK 1: Training Update accumulation
# =============================================================================
check_training_updates() {
  for f in SOUL.md AGENTS.md USER.md; do
    local path="$WORKSPACE/$f"
    if [ -f "$path" ]; then
      local count
      count=$(grep -c '^## Training Update' "$path" 2>/dev/null || true)
      if [ "$count" -ge 10 ]; then
        add_finding "HIGH" "$f: $count Training Update sections — run consolidate"
      elif [ "$count" -ge 5 ]; then
        add_finding "MED" "$f: $count Training Update sections — consider consolidating"
      fi
    fi
  done
}

# =============================================================================
# CHECK 2: File size trending toward char limit
# =============================================================================
check_file_sizes() {
  local BOOTSTRAP_FILES=("SOUL.md" "AGENTS.md" "TOOLS.md" "IDENTITY.md" "USER.md" "MEMORY.md")
  for f in "${BOOTSTRAP_FILES[@]}"; do
    local path="$WORKSPACE/$f"
    if [ -f "$path" ]; then
      local chars
      chars=$(wc -c < "$path" | tr -d ' ')
      local pct=$((chars * 100 / MAX_CHARS))
      if [ "$pct" -ge 90 ]; then
        add_finding "HIGH" "$f: $chars chars (${pct}% of ${MAX_CHARS}) — near limit, content may be truncated"
      elif [ "$pct" -ge 75 ]; then
        add_finding "MED" "$f: $chars chars (${pct}% of ${MAX_CHARS}) — approaching limit"
      fi
    fi
  done
}

# =============================================================================
# CHECK 3: Memory sprawl
# =============================================================================
check_memory_sprawl() {
  if [ ! -d "$WORKSPACE/memory" ]; then
    return
  fi

  local log_count
  log_count=$(find "$WORKSPACE/memory" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')

  # Check if MEMORY.md is large but unstructured
  if [ -f "$WORKSPACE/MEMORY.md" ]; then
    local mem_chars
    mem_chars=$(wc -c < "$WORKSPACE/MEMORY.md" | tr -d ' ')
    local heading_count
    heading_count=$(grep -c '^##' "$WORKSPACE/MEMORY.md" 2>/dev/null || true)

    if [ "$mem_chars" -gt 10000 ] && [ "$heading_count" -lt 3 ]; then
      add_finding "MED" "MEMORY.md: ${mem_chars} chars with only ${heading_count} section heading(s) — add structure"
    fi
  fi

  # Check for many daily logs without recent MEMORY.md update
  if [ "$log_count" -ge 30 ] && [ -f "$WORKSPACE/MEMORY.md" ]; then
    local mem_mtime
    mem_mtime=$(stat -c '%Y' "$WORKSPACE/MEMORY.md" 2>/dev/null || stat -f '%m' "$WORKSPACE/MEMORY.md" 2>/dev/null)
    local now
    now=$(date +%s)
    local mem_age_days=$(( (now - mem_mtime) / 86400 ))

    if [ "$mem_age_days" -ge 14 ]; then
      add_finding "LOW" "$log_count daily logs, MEMORY.md last modified ${mem_age_days} days ago — review and merge key facts"
    fi
  elif [ "$log_count" -ge 30 ] && [ ! -f "$WORKSPACE/MEMORY.md" ]; then
    add_finding "MED" "$log_count daily logs but no MEMORY.md — create one to consolidate key facts"
  fi
}

# =============================================================================
# CHECK 4: Stale workspace files
# =============================================================================
check_stale_files() {
  local BOOTSTRAP_FILES=("SOUL.md" "AGENTS.md" "TOOLS.md" "IDENTITY.md" "USER.md")
  local now
  now=$(date +%s)

  for f in "${BOOTSTRAP_FILES[@]}"; do
    local path="$WORKSPACE/$f"
    if [ -f "$path" ]; then
      local mtime
      mtime=$(stat -c '%Y' "$path" 2>/dev/null || stat -f '%m' "$path" 2>/dev/null)
      local age_days=$(( (now - mtime) / 86400 ))

      if [ "$age_days" -ge "$STALE_DAYS" ]; then
        add_finding "LOW" "$f: not modified in ${age_days} days — still accurate?"
      fi
    fi
  done
}

# =============================================================================
# CHECK 5: Placeholder content
# =============================================================================
check_placeholders() {
  local BOOTSTRAP_FILES=("SOUL.md" "AGENTS.md" "TOOLS.md" "IDENTITY.md" "USER.md" "MEMORY.md")

  for f in "${BOOTSTRAP_FILES[@]}"; do
    local path="$WORKSPACE/$f"
    if [ -f "$path" ]; then
      # Match parenthesized placeholder prompts like "(set your name here)"
      local placeholder_count
      placeholder_count=$(grep -ciE '\(.*\b(set|list|add|your)\b.*here\)' "$path" 2>/dev/null || true)

      if [ "$placeholder_count" -gt 0 ]; then
        add_finding "MED" "$f: $placeholder_count placeholder(s) still present — customize it"
      fi
    fi
  done
}

# =============================================================================
# CHECK 6: Skill health
# =============================================================================
check_skill_health() {
  if [ ! -d "$WORKSPACE/skills" ]; then
    return
  fi

  local no_metadata=0
  local large_skills=0
  local total_skills=0

  for skill_dir in "$WORKSPACE/skills"/*/; do
    [ -d "$skill_dir" ] || continue
    local skill_file="$skill_dir/SKILL.md"
    [ -f "$skill_file" ] || continue

    total_skills=$((total_skills + 1))

    # Check for metadata field in frontmatter
    local has_metadata
    has_metadata=$(sed -n '/^---$/,/^---$/p' "$skill_file" | grep -c '^metadata:' || true)
    if [ "$has_metadata" -eq 0 ]; then
      no_metadata=$((no_metadata + 1))
    fi

    # Check skill size
    local chars
    chars=$(wc -c < "$skill_file" | tr -d ' ')
    local pct=$((chars * 100 / MAX_CHARS))
    if [ "$pct" -ge 90 ]; then
      local skill_name
      skill_name=$(basename "$skill_dir")
      add_finding "MED" "Skill '$skill_name': $chars chars (${pct}% of limit) — consider splitting"
    fi
  done

  if [ "$no_metadata" -gt 0 ] && [ "$total_skills" -gt 0 ]; then
    add_finding "LOW" "$no_metadata of $total_skills skill(s) have no metadata gating — consider adding requirements"
  fi
}

# =============================================================================
# CHECK 7: Cross-file overlap (opt-in: --deep)
# =============================================================================
check_cross_file_overlap() {
  if [ "$DEEP" != "true" ]; then
    return
  fi

  if [ ! -f "$WORKSPACE/AGENTS.md" ] || [ ! -f "$WORKSPACE/SOUL.md" ]; then
    return
  fi

  # Extract bullet lines (- ...) from both files, normalize whitespace, find exact duplicates
  local agents_bullets soul_bullets
  agents_bullets=$(grep '^- ' "$WORKSPACE/AGENTS.md" 2>/dev/null | sed 's/^- //' | sort -u || true)
  soul_bullets=$(grep '^- ' "$WORKSPACE/SOUL.md" 2>/dev/null | sed 's/^- //' | sort -u || true)

  if [ -z "$agents_bullets" ] || [ -z "$soul_bullets" ]; then
    return
  fi

  local dupes
  dupes=$(comm -12 <(printf '%s\n' "$agents_bullets") <(printf '%s\n' "$soul_bullets") | wc -l | tr -d ' ')

  if [ "$dupes" -gt 0 ]; then
    add_finding "LOW" "AGENTS.md and SOUL.md share $dupes identical rule line(s) — consider deduplicating"
  fi
}

# =============================================================================
# Run all checks
# =============================================================================

echo "=== Workspace Analysis ==="
printf 'Workspace: %s\n' "$WORKSPACE"
if [ "$DEEP" = "true" ]; then
  echo "Mode: deep analysis"
fi
echo ""

if [ ! -d "$WORKSPACE" ]; then
  echo "ERROR: Workspace directory does not exist."
  exit 0
fi

check_training_updates
check_file_sizes
check_memory_sprawl
check_stale_files
check_placeholders
check_skill_health
check_cross_file_overlap

# Output findings
TOTAL=$((HIGH_COUNT + MED_COUNT + LOW_COUNT))

if [ "$TOTAL" -eq 0 ]; then
  echo "--- Recommendations ---"
  echo "  No issues found. Workspace looks well-maintained."
else
  echo "--- Recommendations ---"
  printf '%b' "$FINDINGS"
fi

echo ""
echo "=== Summary ==="
printf '  High priority: %d\n' "$HIGH_COUNT"
printf '  Medium priority: %d\n' "$MED_COUNT"
printf '  Low priority: %d\n' "$LOW_COUNT"

# Actionable next-step suggestion
if [ "$HIGH_COUNT" -gt 0 ] || [ "$MED_COUNT" -gt 0 ]; then
  echo ""
  # Suggest the most impactful action
  if printf '%b' "$FINDINGS" | grep -q 'Training Update sections'; then
    echo "  Suggested: run '/training-manager consolidate' to clean up Training Update buildup."
  elif printf '%b' "$FINDINGS" | grep -q 'placeholder'; then
    echo "  Suggested: customize placeholder content in workspace files."
  elif printf '%b' "$FINDINGS" | grep -q 'limit'; then
    echo "  Suggested: trim or split large files approaching the injection limit."
  fi
fi

exit 0
