#!/usr/bin/env bash
# lib/migrate.sh — Migration: scan arbitrary directories into Claw Drive

# Scan a source directory and output migration-plan.json
migrate_scan() {
  local source_dir="$1"
  local output="${2:-migration-plan.json}"

  if [[ ! -d "$source_dir" ]]; then
    echo "❌ Directory not found: $source_dir"
    return 1
  fi

  # Resolve absolute path
  source_dir="$(cd "$source_dir" && pwd)"

  echo "🔍 Scanning $source_dir ..."

  local files=()
  local count=0

  # Start JSON
  printf '{\n  "source": "%s",\n  "scanned_at": "%s",\n  "files": [\n' \
    "$source_dir" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$output"

  local first=true

  while IFS= read -r -d '' filepath; do
    # Skip hidden files and directories
    [[ "$(basename "$filepath")" == .* ]] && continue

    local relative="${filepath#$source_dir/}"
    local size
    size=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null || echo 0)
    local modified
    modified=$(stat -f%Sm -t%Y-%m-%d "$filepath" 2>/dev/null || stat -c%y "$filepath" 2>/dev/null | cut -d' ' -f1 || echo "unknown")
    local ext="${filepath##*.}"
    [[ "$ext" == "$filepath" ]] && ext=""
    local mime
    mime=$(file --brief --mime-type "$filepath" 2>/dev/null || echo "unknown")

    [[ "$first" == "true" ]] || printf ',\n' >> "$output"

    # Escape strings for JSON
    local escaped_path
    escaped_path=$(printf '%s' "$relative" | sed 's/\\/\\\\/g; s/"/\\"/g')
    local escaped_mime
    escaped_mime=$(printf '%s' "$mime" | sed 's/\\/\\\\/g; s/"/\\"/g')

    cat >> "$output" <<EOF
    {
      "source_path": "$escaped_path",
      "size": $size,
      "modified": "$modified",
      "extension": "$ext",
      "mime": "$escaped_mime",
      "category": null,
      "name": null,
      "tags": null,
      "description": null,
      "confidence": null,
      "status": "pending"
    }
EOF
    first=false
    ((count++)) || true

    # Progress every 50 files
    if (( count % 50 == 0 )); then
      echo "   ... $count files scanned"
    fi

  done < <(find "$source_dir" -type f -print0 | sort -z)

  # Close JSON
  printf '\n  ]\n}\n' >> "$output"

  echo "✅ Scanned $count files → $output"
}

# Apply a migration plan
migrate_apply() {
  local plan_file="$1"
  local dry_run="${2:-false}"

  if [[ ! -f "$plan_file" ]]; then
    echo "❌ Plan file not found: $plan_file"
    return 1
  fi

  claw_drive_init || return 1

  echo "📦 Applying migration plan: $plan_file"
  [[ "$dry_run" == "true" ]] && echo "   (dry run — no files will be moved)"
  echo ""

  local source_dir
  source_dir=$(python3 - "$plan_file" <<'PY'
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    print(json.load(f)['source'])
PY
)

  local total=0 stored=0 skipped=0 dupes=0 errors=0

  # Process each file in the plan
  # Note: use process substitution (< <(...)) instead of a pipe so the
  # while-loop runs in the current shell and counter variables persist.
  while IFS=$'\t' read -r src_path category new_name tags description confidence; do
    ((total++)) || true

    if [[ -z "$category" || -z "$new_name" ]]; then
      echo "  ⚠️  Skipping (no category/name): $src_path"
      ((skipped++)) || true
      continue
    fi

    # Validate path components from plan file
    if ! validate_path_component "category" "$category" 2>&1 || \
       ! validate_filename "name" "$new_name" 2>&1; then
      echo "  ❌ Unsafe path in plan: $category/$new_name"
      ((errors++)) || true
      continue
    fi

    # Validate source path from plan: must stay within source_dir
    if ! validate_path_component "source_path" "$src_path" 2>&1; then
      echo "  ❌ Unsafe source path in plan: $src_path"
      ((errors++)) || true
      continue
    fi

    local full_source="$source_dir/$src_path"
    local resolved_source source_root
    resolved_source=$(cd "$(dirname "$full_source")" 2>/dev/null && pwd -P)/$(basename "$full_source")
    source_root=$(cd "$source_dir" 2>/dev/null && pwd -P)
    if [[ "$resolved_source" != "$source_root"/* ]]; then
      echo "  ❌ Source path escapes migration source root: $src_path"
      ((errors++)) || true
      continue
    fi

    if [[ ! -f "$resolved_source" ]]; then
      echo "  ❌ Source missing: $src_path"
      ((errors++)) || true
      continue
    fi

    # Dedup check
    local existing
    if existing=$(dedup_check "$resolved_source"); then
      echo "  🔁 Duplicate (exists at $existing): $src_path"
      ((dupes++)) || true
      continue
    fi

    local dest="$CLAW_DRIVE_DIR/$category/$new_name"

    if [[ "$dry_run" == "true" ]]; then
      echo "  📄 $src_path → $category/$new_name [$tags]"
    else
      mkdir -p "$CLAW_DRIVE_DIR/$category"
      if ! validate_in_drive_dir "$dest"; then
        ((errors++)) || true
        continue
      fi
      cp "$resolved_source" "$dest"
      dedup_register "$dest" "$category/$new_name"

      # Update index
      local date_str
      date_str=$(date +%Y-%m-%d)
      index_add "$date_str" "$category/$new_name" "$description" "$tags" "migration"

      echo "  ✅ $src_path → $category/$new_name"
    fi
    ((stored++)) || true
  done < <(python3 - "$plan_file" <<'PY'
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as fh:
    plan = json.load(fh)
for f in plan['files']:
    if f.get('status') == 'skip':
        continue
    cat = f.get('category') or ''
    name = f.get('name') or ''
    tags = f.get('tags') or ''
    desc = f.get('description') or ''
    src = f.get('source_path') or ''
    conf = f.get('confidence') or ''
    print(f'{src}\t{cat}\t{name}\t{tags}\t{desc}\t{conf}')
PY
)

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Migration complete."
  echo "  Stored: $stored"
  echo "  Duplicates: $dupes"
  echo "  Skipped: $skipped"
  echo "  Errors: $errors"
}

# Show plan summary
migrate_summary() {
  local plan_file="$1"

  if [[ ! -f "$plan_file" ]]; then
    echo "❌ Plan file not found: $plan_file"
    return 1
  fi

  python3 - "$plan_file" <<'PY'
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as fh:
    plan = json.load(fh)
files = plan['files']
total = len(files)
ready = sum(1 for f in files if f.get('category') and f.get('name'))
pending = sum(1 for f in files if not f.get('category') or not f.get('name'))
skip = sum(1 for f in files if f.get('status') == 'skip')

print(f'📋 Migration Plan: {plan["source"]}')
print(f'   Scanned: {plan.get("scanned_at", "unknown")}')
print(f'   Total files: {total}')
print(f'   Ready: {ready}')
print(f'   Pending classification: {pending}')
print(f'   Marked skip: {skip}')
print()

# Category breakdown
cats = {}
for f in files:
    c = f.get('category') or 'unclassified'
    cats[c] = cats.get(c, 0) + 1
print('   Categories:')
for c in sorted(cats, key=cats.get, reverse=True):
    print(f'     {c}: {cats[c]}')
PY
}
