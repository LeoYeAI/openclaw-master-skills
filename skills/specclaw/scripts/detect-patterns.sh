#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(cd "$SCRIPT_DIR/../templates" && pwd)"

usage() {
  cat <<'EOF'
Usage:
  detect-patterns.sh <specclaw_dir> scan <change_name>
  detect-patterns.sh <specclaw_dir> list [--min-recurrence N]
  detect-patterns.sh <specclaw_dir> promote <pat-id>

Modes:
  scan     Scan a change's errors/learnings and update the pattern registry
  list     List all recorded patterns (optionally filtered by recurrence)
  promote  Promote a pattern from active to promoted

Options:
  -h, --help   Show this help message
EOF
}

# Stop words to strip from summaries
STOP_WORDS="the a an in to and or is was for of with that this it on at by from be are were has have had not but also"

strip_stop_words() {
  local text="$1"
  text=$(echo "$text" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 ]/ /g' | tr -s ' ')
  local result=""
  for word in $text; do
    local is_stop=0
    for sw in $STOP_WORDS; do
      if [[ "$word" == "$sw" ]]; then
        is_stop=1
        break
      fi
    done
    if [[ $is_stop -eq 0 && ${#word} -gt 1 ]]; then
      result="$result $word"
    fi
  done
  echo "$result" | sed 's/^ //'
}

count_overlapping() {
  local kw1="$1"
  local kw2="$2"
  local count=0
  for w in $kw1; do
    for k in $kw2; do
      if [[ "$w" == "$k" ]]; then
        count=$((count + 1))
        break
      fi
    done
  done
  echo "$count"
}

get_next_pat_id() {
  local patterns_file="$1"
  local max_id=0
  while IFS= read -r line; do
    if [[ "$line" =~ ^##\ \[PAT-([0-9]+)\] ]]; then
      local num="${BASH_REMATCH[1]}"
      num=$((10#$num))
      if [[ $num -gt $max_id ]]; then
        max_id=$num
      fi
    fi
  done < "$patterns_file"
  printf "PAT-%03d" $((max_id + 1))
}

ensure_patterns_file() {
  local specclaw_dir="$1"
  local patterns_file="$specclaw_dir/.specclaw/patterns.md"
  if [[ ! -f "$patterns_file" ]]; then
    mkdir -p "$(dirname "$patterns_file")"
    cp "$TEMPLATE_DIR/patterns.md" "$patterns_file"
  fi
  echo "$patterns_file"
}

# Parse entries from errors.md — each entry starts with "## Error:" or "## "
# Returns lines: category|summary_keywords|summary_snippet
parse_errors() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  local in_entry=0
  local summary=""
  while IFS= read -r line; do
    if [[ "$line" =~ ^##\  ]]; then
      # Emit previous if any
      if [[ $in_entry -eq 1 && -n "$summary" ]]; then
        local kw
        kw=$(strip_stop_words "$summary")
        echo "error|$kw|$summary"
      fi
      in_entry=1
      summary=""
    elif [[ "$line" =~ ^[*]{2}Summary:[*]{2}\ *(.*) || "$line" =~ ^Summary:\ *(.*) ]]; then
      summary="${BASH_REMATCH[1]}"
    fi
  done < "$file"
  # Emit last
  if [[ $in_entry -eq 1 && -n "$summary" ]]; then
    local kw
    kw=$(strip_stop_words "$summary")
    echo "error|$kw|$summary"
  fi
}

# Parse entries from learnings.md
# Returns lines: category|summary_keywords|summary_snippet
parse_learnings() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  local in_entry=0
  local summary=""
  local category=""
  while IFS= read -r line; do
    if [[ "$line" =~ ^##\  ]]; then
      # Emit previous if any
      if [[ $in_entry -eq 1 && -n "$summary" ]]; then
        local cat="${category:-uncategorized}"
        local kw
        kw=$(strip_stop_words "$summary")
        echo "$cat|$kw|$summary"
      fi
      in_entry=1
      summary=""
      category=""
    elif [[ "$line" =~ ^[*]{2}Summary:[*]{2}\ *(.*) || "$line" =~ ^Summary:\ *(.*) ]]; then
      summary="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[*]{2}Category:[*]{2}\ *(.*) || "$line" =~ ^Category:\ *(.*) ]]; then
      category="${BASH_REMATCH[1]}"
      category=$(echo "$category" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | sed 's/[^a-z0-9_]//g')
    fi
  done < "$file"
  # Emit last
  if [[ $in_entry -eq 1 && -n "$summary" ]]; then
    local cat="${category:-uncategorized}"
    local kw
    kw=$(strip_stop_words "$summary")
    echo "$cat|$kw|$summary"
  fi
}

# Extract keywords from a pattern block
get_pattern_keywords() {
  local patterns_file="$1"
  local pat_id="$2"
  local in_pat=0
  local in_kw=0
  while IFS= read -r line; do
    if [[ "$line" =~ ^##\ \[$pat_id\] ]]; then
      in_pat=1
      continue
    fi
    if [[ $in_pat -eq 1 ]]; then
      if [[ "$line" =~ ^##\  && ! "$line" =~ ^###\  ]]; then
        break
      fi
      if [[ "$line" == "### Keywords" ]]; then
        in_kw=1
        continue
      fi
      if [[ $in_kw -eq 1 ]]; then
        if [[ "$line" =~ ^### || "$line" =~ ^## ]]; then
          break
        fi
        if [[ -n "$line" ]]; then
          echo "$line" | tr ',' ' ' | tr -s ' ' | sed 's/^ //'
          break
        fi
      fi
    fi
  done < "$patterns_file"
}

# Extract category from a pattern block header
get_pattern_category() {
  local patterns_file="$1"
  local pat_id="$2"
  while IFS= read -r line; do
    if [[ "$line" =~ ^##\ \[$pat_id\]\ ([a-z_]+)\ —\  ]]; then
      echo "${BASH_REMATCH[1]}"
      return
    fi
  done < "$patterns_file"
}

# Get recurrence count for a pattern
get_pattern_recurrence() {
  local patterns_file="$1"
  local pat_id="$2"
  local in_pat=0
  while IFS= read -r line; do
    if [[ "$line" =~ ^##\ \[$pat_id\] ]]; then
      in_pat=1
      continue
    fi
    if [[ $in_pat -eq 1 ]]; then
      if [[ "$line" =~ ^##\ \[PAT- ]]; then
        break
      fi
      if [[ "$line" =~ ^\*\*Recurrence:\*\*\ *([0-9]+) ]]; then
        echo "${BASH_REMATCH[1]}"
        return
      fi
    fi
  done < "$patterns_file"
  echo "0"
}

# Get all pattern IDs
get_all_pat_ids() {
  local patterns_file="$1"
  grep -oP '(?<=^## \[)PAT-[0-9]+(?=\])' "$patterns_file" 2>/dev/null || true
}

# Update an existing pattern: increment recurrence, add occurrence, update last seen
update_pattern() {
  local patterns_file="$1"
  local pat_id="$2"
  local change_name="$3"
  local snippet="$4"
  local today="$5"

  # Get current recurrence
  local cur_rec
  cur_rec=$(get_pattern_recurrence "$patterns_file" "$pat_id")
  local new_rec=$((cur_rec + 1))

  # Update recurrence
  sed -i "/$pat_id/,/^---$/{s/\*\*Recurrence:\*\* *[0-9]*/\*\*Recurrence:\*\* $new_rec/}" "$patterns_file"

  # Update Last Seen
  sed -i "/$pat_id/,/^---$/{s/\*\*Last Seen:\*\*.*/\*\*Last Seen:\*\* $today ($change_name)/}" "$patterns_file"

  # Add occurrence before "### Prevention Rule"
  # Find the line number of Prevention Rule within this pattern block
  local start_line end_line
  start_line=$(grep -n "^## \[$pat_id\]" "$patterns_file" | head -1 | cut -d: -f1)
  end_line=$(awk "NR>$start_line && /^---$/{print NR; exit}" "$patterns_file")
  if [[ -z "$end_line" ]]; then
    end_line=$(wc -l < "$patterns_file")
  fi

  # Find Prevention Rule line within range
  local prev_line
  prev_line=$(awk "NR>=$start_line && NR<=$end_line && /^### Prevention Rule/{print NR; exit}" "$patterns_file")

  if [[ -n "$prev_line" ]]; then
    # Insert occurrence before Prevention Rule (with blank line)
    sed -i "${prev_line}i\\- ${change_name} — ${snippet}" "$patterns_file"
  else
    # Find Occurrences section and append
    local occ_line
    occ_line=$(awk "NR>=$start_line && NR<=$end_line && /^### Occurrences/{print NR; exit}" "$patterns_file")
    if [[ -n "$occ_line" ]]; then
      # Find last occurrence line (starts with "- ") after occ_line
      local insert_line=$occ_line
      local n=$((occ_line + 1))
      while IFS= read -r line; do
        if [[ "$line" =~ ^-\  ]]; then
          insert_line=$n
        elif [[ -n "$line" && ! "$line" =~ ^[[:space:]]*$ ]]; then
          break
        fi
        n=$((n + 1))
      done < <(tail -n "+$((occ_line + 1))" "$patterns_file")
      sed -i "${insert_line}a\\- ${change_name} — ${snippet}" "$patterns_file"
    fi
  fi

  echo "$new_rec"
}

# Create a new pattern entry
create_pattern() {
  local patterns_file="$1"
  local pat_id="$2"
  local category="$3"
  local keywords="$4"
  local snippet="$5"
  local change_name="$6"
  local today="$7"

  # Format keywords as comma-separated
  local kw_formatted
  kw_formatted=$(echo "$keywords" | tr ' ' '\n' | sort -u | tr '\n' ', ' | sed 's/,$//' | sed 's/,/, /g')

  # Truncate snippet for the header (first ~60 chars)
  local header_snippet
  header_snippet=$(echo "$snippet" | cut -c1-80)

  cat >> "$patterns_file" <<EOF

## [$pat_id] $category — $header_snippet

**First Seen:** $today ($change_name)
**Last Seen:** $today ($change_name)
**Recurrence:** 1
**Status:** active

### Keywords
$kw_formatted

### Occurrences
- $change_name — $snippet

### Prevention Rule
> (To be defined when pattern is promoted)

---
EOF
}

# ---- SCAN MODE ----
do_scan() {
  local specclaw_dir="$1"
  local change_name="$2"
  local changes_dir="$specclaw_dir/.specclaw/changes/$change_name"
  local patterns_file
  patterns_file=$(ensure_patterns_file "$specclaw_dir")
  local today
  today=$(date +%Y-%m-%d)

  if [[ ! -d "$changes_dir" ]]; then
    echo "Error: Change directory not found: $changes_dir" >&2
    exit 1
  fi

  local errors_file="$changes_dir/errors.md"
  local learnings_file="$changes_dir/learnings.md"

  # Collect entries: category|keywords|snippet
  local entries=()
  while IFS= read -r line; do
    [[ -n "$line" ]] && entries+=("$line")
  done < <(parse_errors "$errors_file")
  while IFS= read -r line; do
    [[ -n "$line" ]] && entries+=("$line")
  done < <(parse_learnings "$learnings_file")

  if [[ ${#entries[@]} -eq 0 ]]; then
    echo "No entries found in errors.md or learnings.md for change '$change_name'."
    return
  fi

  local new_count=0
  local updated_count=0
  local promotable=()

  for entry in "${entries[@]}"; do
    local category keywords snippet
    category=$(echo "$entry" | cut -d'|' -f1)
    keywords=$(echo "$entry" | cut -d'|' -f2)
    snippet=$(echo "$entry" | cut -d'|' -f3-)

    if [[ -z "$keywords" ]]; then
      continue
    fi

    # Check existing patterns for match
    local matched=0
    local matched_id=""
    while IFS= read -r pat_id; do
      [[ -z "$pat_id" ]] && continue
      local pat_cat
      pat_cat=$(get_pattern_category "$patterns_file" "$pat_id")
      if [[ "$pat_cat" != "$category" ]]; then
        continue
      fi
      local pat_kw
      pat_kw=$(get_pattern_keywords "$patterns_file" "$pat_id")
      local overlap
      overlap=$(count_overlapping "$keywords" "$pat_kw")
      if [[ $overlap -ge 2 ]]; then
        matched=1
        matched_id="$pat_id"
        break
      fi
    done < <(get_all_pat_ids "$patterns_file")

    if [[ $matched -eq 1 ]]; then
      local new_rec
      new_rec=$(update_pattern "$patterns_file" "$matched_id" "$change_name" "$snippet" "$today")
      updated_count=$((updated_count + 1))
      echo "📊 Updated $matched_id ($category) — recurrence: $new_rec"
      if [[ $new_rec -ge 3 ]]; then
        promotable+=("$matched_id:$new_rec")
      fi
    else
      local new_id
      new_id=$(get_next_pat_id "$patterns_file")
      create_pattern "$patterns_file" "$new_id" "$category" "$keywords" "$snippet" "$change_name" "$today"
      new_count=$((new_count + 1))
      echo "🆕 Created $new_id ($category) — $snippet"
    fi
  done

  echo ""
  echo "Summary: $new_count new pattern(s), $updated_count updated."

  for p in "${promotable[@]}"; do
    local pid pcount
    pid=$(echo "$p" | cut -d: -f1)
    pcount=$(echo "$p" | cut -d: -f2)
    echo "⚠️ $pid has $pcount occurrences — eligible for promotion"
  done
}

# ---- LIST MODE ----
do_list() {
  local specclaw_dir="$1"
  shift
  local min_rec=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --min-recurrence)
        min_rec="$2"
        shift 2
        ;;
      *)
        echo "Unknown option: $1" >&2
        exit 1
        ;;
    esac
  done

  local patterns_file="$specclaw_dir/.specclaw/patterns.md"
  if [[ ! -f "$patterns_file" ]]; then
    echo "No patterns recorded."
    return
  fi

  local found=0
  while IFS= read -r line; do
    if [[ "$line" =~ ^##\ \[(PAT-[0-9]+)\]\ ([a-z_]+)\ —\ (.*) ]]; then
      local pat_id="${BASH_REMATCH[1]}"
      local category="${BASH_REMATCH[2]}"
      local description="${BASH_REMATCH[3]}"
      local rec status
      rec=$(get_pattern_recurrence "$patterns_file" "$pat_id")

      # Get status
      local in_pat=0
      status="active"
      while IFS= read -r sline; do
        if [[ "$sline" =~ ^##\ \[$pat_id\] ]]; then
          in_pat=1
          continue
        fi
        if [[ $in_pat -eq 1 ]]; then
          if [[ "$sline" =~ ^##\ \[PAT- ]]; then
            break
          fi
          if [[ "$sline" =~ ^\*\*Status:\*\*\ *(.*) ]]; then
            status="${BASH_REMATCH[1]}"
            status=$(echo "$status" | sed 's/ *|.*//' | tr -d ' ')
            break
          fi
        fi
      done < "$patterns_file"

      if [[ $rec -ge $min_rec ]]; then
        local flag=""
        if [[ "$status" == "promoted" ]]; then
          flag="⚠️ promoted"
        elif [[ $rec -ge 3 ]]; then
          flag="⚠️ eligible"
        else
          flag="   active"
        fi
        printf "%-8s  %-14s  %d  %-14s  %s\n" "$pat_id" "$category" "$rec" "$flag" "$description"
        found=1
      fi
    fi
  done < "$patterns_file"

  if [[ $found -eq 0 ]]; then
    echo "No patterns recorded."
  fi
}

# ---- PROMOTE MODE ----
do_promote() {
  local specclaw_dir="$1"
  local pat_id="$2"
  local patterns_file="$specclaw_dir/.specclaw/patterns.md"

  pat_id=$(echo "$pat_id" | tr '[:lower:]' '[:upper:]')

  if [[ ! -f "$patterns_file" ]]; then
    echo "Error: No patterns file found." >&2
    exit 1
  fi

  if ! grep -q "^## \[$pat_id\]" "$patterns_file"; then
    echo "Error: Pattern $pat_id not found." >&2
    exit 1
  fi

  # Check if already promoted
  local start_line end_line
  start_line=$(grep -n "^## \[$pat_id\]" "$patterns_file" | head -1 | cut -d: -f1)
  end_line=$(awk "NR>$start_line && /^---$/{print NR; exit}" "$patterns_file")
  if [[ -z "$end_line" ]]; then
    end_line=$(wc -l < "$patterns_file")
  fi

  if sed -n "${start_line},${end_line}p" "$patterns_file" | grep -q '^\*\*Status:\*\* *promoted'; then
    echo "Pattern $pat_id is already promoted."
  else
    sed -i "${start_line},${end_line}s/\*\*Status:\*\* *active/\*\*Status:\*\* promoted/" "$patterns_file"
    echo "✅ Pattern $pat_id promoted."
  fi

  # Output the Prevention Rule
  echo ""
  echo "Prevention Rule for $pat_id:"
  local in_rule=0
  while IFS= read -r line; do
    if [[ "$line" == "### Prevention Rule" ]]; then
      in_rule=1
      continue
    fi
    if [[ $in_rule -eq 1 ]]; then
      if [[ "$line" =~ ^### || "$line" == "---" || "$line" =~ ^##\  ]]; then
        break
      fi
      [[ -n "$line" ]] && echo "$line"
    fi
  done < <(sed -n "${start_line},${end_line}p" "$patterns_file")
}

# ---- MAIN ----
if [[ $# -lt 1 || "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 0
fi

SPECCLAW_DIR="$1"
shift

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

MODE="$1"
shift

case "$MODE" in
  scan)
    if [[ $# -lt 1 ]]; then
      echo "Error: scan mode requires <change_name>" >&2
      usage
      exit 1
    fi
    do_scan "$SPECCLAW_DIR" "$1"
    ;;
  list)
    do_list "$SPECCLAW_DIR" "$@"
    ;;
  promote)
    if [[ $# -lt 1 ]]; then
      echo "Error: promote mode requires <pat-id>" >&2
      usage
      exit 1
    fi
    do_promote "$SPECCLAW_DIR" "$1"
    ;;
  -h|--help)
    usage
    ;;
  *)
    echo "Error: Unknown mode '$MODE'" >&2
    usage
    exit 1
    ;;
esac
