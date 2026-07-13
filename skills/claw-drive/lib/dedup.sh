#!/usr/bin/env bash
# lib/dedup.sh — Content-based deduplication for Claw Drive

# Hash a file and return SHA-256
dedup_hash() {
  local file="$1"
  shasum -a 256 "$file" | awk '{print $1}'
}

# Check if a file is a duplicate. Returns 0 if duplicate, 1 if new.
# Prints the existing path if duplicate.
dedup_check() {
  local file="$1"

  if [[ ! -f "$CLAW_DRIVE_HASHES" ]]; then
    return 1
  fi

  local hash
  hash=$(dedup_hash "$file")

  local existing
  existing=$(grep "^$hash " "$CLAW_DRIVE_HASHES" | head -1)
  # Preserve paths with spaces by splitting on the double-space delimiter.
  existing="${existing#*  }"

  if [[ -n "$existing" ]]; then
    echo "$existing"
    return 0
  fi

  return 1
}

# Register a file hash in the dedup ledger
dedup_register() {
  local file="$1"
  local relative_path="$2"

  local hash
  hash=$(dedup_hash "$file")

  echo "$hash  $relative_path" >> "$CLAW_DRIVE_HASHES"
}

# Update a registered path in hash ledger after move/rename
# Usage: dedup_move <old_path> <new_path>
dedup_move() {
  local old_path="$1"
  local new_path="$2"

  if [[ ! -f "$CLAW_DRIVE_HASHES" ]]; then
    return 0
  fi

  local tmp
  tmp=$(mktemp) || { echo "❌ mktemp failed" >&2; return 1; }

  while IFS= read -r line || [[ -n "$line" ]]; do
    local hash="${line%%  *}"
    local path="${line#*  }"
    if [[ "$path" == "$old_path" ]]; then
      printf '%s  %s\n' "$hash" "$new_path"
    else
      printf '%s\n' "$line"
    fi
  done < "$CLAW_DRIVE_HASHES" > "$tmp"

  mv "$tmp" "$CLAW_DRIVE_HASHES"
}

# Show dedup stats
dedup_status() {
  local format="${1:-table}"

  if [[ ! -f "$CLAW_DRIVE_HASHES" ]]; then
    echo "No hash ledger found."
    return 0
  fi

  local count
  count=$(wc -l < "$CLAW_DRIVE_HASHES" | xargs)

  if [[ "$format" == "json" ]]; then
    printf '{"tracked_files":%d,"ledger":"%s"}\n' "$count" "$CLAW_DRIVE_HASHES"
  else
    echo "Dedup ledger: $CLAW_DRIVE_HASHES"
    echo "Tracked files: $count"
  fi
}
