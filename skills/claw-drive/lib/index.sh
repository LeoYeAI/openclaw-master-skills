#!/usr/bin/env bash
# lib/index.sh — INDEX.jsonl management for Claw Drive
#
# INDEX.jsonl is a structured JSONL file — one JSON object per line.
# Agents read it directly for search/list/tag operations.
# This library handles atomic write operations (add, update, delete).

# Safe mktemp wrapper — exits on failure instead of proceeding with empty path
safe_mktemp() {
  local tmp
  tmp=$(mktemp) || { echo "❌ mktemp failed" >&2; return 1; }
  echo "$tmp"
}

# Append a new entry to the index
# Usage: index_add <date> <path> <desc> <tags> <source> [metadata_json] [original_name] [correspondent]
index_add() {
  local date="$1" path="$2" desc="$3" tags="$4" source="$5" metadata="${6:-}" original_name="${7:-}" correspondent="${8:-}"

  # Convert comma-separated tags to JSON array
  local tags_json
  tags_json=$(printf '%s' "$tags" | jq -R 'split(",") | map(gsub("^\\s+|\\s+$";""))')

  local jq_args=(
    --arg date "$date"
    --arg path "$path"
    --arg desc "$desc"
    --argjson tags "$tags_json"
    --arg source "$source"
  )
  local jq_expr='{date:$date, path:$path, desc:$desc, tags:$tags, source:$source}'

  if [[ -n "$metadata" ]]; then
    jq_args+=(--argjson metadata "$metadata")
    jq_expr='{date:$date, path:$path, desc:$desc, tags:$tags, source:$source, metadata:$metadata}'
  fi

  # Build optional fields dynamically
  local optional_fields=""
  if [[ -n "$original_name" ]]; then
    jq_args+=(--arg original_name "$original_name")
    optional_fields="$optional_fields, original_name:\$original_name"
  fi
  if [[ -n "$correspondent" ]]; then
    jq_args+=(--arg correspondent "$correspondent")
    optional_fields="$optional_fields, correspondent:\$correspondent"
  fi

  # Rebuild expression with optional fields
  if [[ -n "$metadata" ]]; then
    jq_expr="{date:\$date, path:\$path, desc:\$desc, tags:\$tags, source:\$source, metadata:\$metadata${optional_fields}}"
  else
    jq_expr="{date:\$date, path:\$path, desc:\$desc, tags:\$tags, source:\$source${optional_fields}}"
  fi

  jq -cn "${jq_args[@]}" "$jq_expr" >> "$CLAW_DRIVE_INDEX"
}

# Remove an entry by path (exact match)
index_remove() {
  local target_path="$1"
  local tmp
  tmp=$(safe_mktemp) || return 1

  jq -c --arg path "$target_path" 'select(.path != $path)' "$CLAW_DRIVE_INDEX" > "$tmp"
  mv "$tmp" "$CLAW_DRIVE_INDEX"
}

# Update fields on an entry by path (exact match)
# Usage: index_update <path> [--desc <desc>] [--tags <tags>]
index_update() {
  local target_path="$1"
  shift

  local new_desc="" new_tags="" new_metadata="" new_correspondent="" new_source=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --desc|-d) new_desc="$2"; shift 2 ;;
      --tags|-t) new_tags="$2"; shift 2 ;;
      --metadata|-m) new_metadata="$2"; shift 2 ;;
      --correspondent) new_correspondent="$2"; shift 2 ;;
      --source|-s) new_source="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  local tmp
  tmp=$(safe_mktemp) || return 1

  local jq_filter='if .path == $path then'
  local jq_args
  jq_args=(--arg path "$target_path")

  if [[ -n "$new_desc" ]]; then
    jq_filter="$jq_filter .desc = \$desc |"
    jq_args+=(--arg desc "$new_desc")
  fi

  if [[ -n "$new_tags" ]]; then
    local tags_json
    tags_json=$(printf '%s' "$new_tags" | jq -R 'split(",") | map(gsub("^\\s+|\\s+$";""))')
    jq_filter="$jq_filter .tags = \$tags |"
    jq_args+=(--argjson tags "$tags_json")
  fi

  if [[ -n "$new_metadata" ]]; then
    # Merge new metadata into existing (or create if absent)
    jq_filter="$jq_filter .metadata = ((.metadata // {}) * \$meta) |"
    jq_args+=(--argjson meta "$new_metadata")
  fi

  if [[ -n "$new_correspondent" ]]; then
    jq_filter="$jq_filter .correspondent = \$correspondent |"
    jq_args+=(--arg correspondent "$new_correspondent")
  fi

  if [[ -n "$new_source" ]]; then
    jq_filter="$jq_filter .source = \$new_source |"
    jq_args+=(--arg new_source "$new_source")
  fi

  # Remove trailing pipe if present
  jq_filter="${jq_filter% |}"
  jq_filter="$jq_filter else . end"

  jq -c "${jq_args[@]}" "$jq_filter" "$CLAW_DRIVE_INDEX" > "$tmp"
  mv "$tmp" "$CLAW_DRIVE_INDEX"
}

# Check if a path exists in the index
index_has() {
  local target_path="$1"
  # jq -e can return non-zero with JSONL streams in some envs despite a match;
  # use exact path membership check for robust existence probing.
  jq -r '.path // empty' "$CLAW_DRIVE_INDEX" 2>/dev/null | grep -Fxq "$target_path"
}

# Rename/move an entry path in the index (exact match)
# Usage: index_move <old_path> <new_path>
index_move() {
  local old_path="$1"
  local new_path="$2"
  local tmp
  tmp=$(safe_mktemp) || return 1

  jq -c --arg old "$old_path" --arg new "$new_path" \
    'if .path == $old then .path = $new else . end' \
    "$CLAW_DRIVE_INDEX" > "$tmp"
  mv "$tmp" "$CLAW_DRIVE_INDEX"
}

# Dedup: remove hash entry for a path (exact match, regex-safe)
dedup_unregister() {
  local target_path="$1"

  if [[ ! -f "$CLAW_DRIVE_HASHES" ]]; then
    return 0
  fi

  local tmp
  tmp=$(safe_mktemp) || return 1
  # Use shell parameter expansion to extract path from "hash  path" format,
  # avoiding unescaped grep which breaks on regex special chars (., (, ), etc.)
  while IFS= read -r line || [[ -n "$line" ]]; do
    local line_path="${line#*  }"
    [[ "$line_path" != "$target_path" ]] && printf '%s\n' "$line"
  done < "$CLAW_DRIVE_HASHES" > "$tmp"
  mv "$tmp" "$CLAW_DRIVE_HASHES"
}
