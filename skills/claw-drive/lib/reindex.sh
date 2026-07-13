#!/usr/bin/env bash
# lib/reindex.sh — Reindex support for Claw Drive
#
# Scan drive for orphan files and existing entries,
# output a plan for the agent to enrich, then apply updates.

reindex_scan() {
  local output="reindex-plan.json"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --output|-o) output="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  claw_drive_init || return 1

  echo "🔍 Scanning $CLAW_DRIVE_DIR for reindex..."

  # Collect indexed paths
  local indexed_paths_file
  indexed_paths_file=$(safe_mktemp) || return 1
  jq -r '.path' "$CLAW_DRIVE_INDEX" > "$indexed_paths_file" 2>/dev/null || true

  # Build orphans array
  local orphans_file
  orphans_file=$(safe_mktemp) || return 1
  echo "[]" > "$orphans_file"

  while IFS= read -r -d '' filepath; do
    local basename
    basename=$(basename "$filepath")
    [[ "$basename" == .* || "$basename" == "INDEX.jsonl" || "$basename" == "INDEX.md" ]] && continue

    local rel="${filepath#$CLAW_DRIVE_DIR/}"

    # Check if indexed (direct match or inside indexed directory)
    local found=false
    while IFS= read -r idx_path; do
      [[ -z "$idx_path" ]] && continue
      if [[ "$rel" == "$idx_path" ]]; then
        found=true; break
      fi
      if [[ -d "$CLAW_DRIVE_DIR/$idx_path" && "$rel" == "$idx_path"* ]]; then
        found=true; break
      fi
    done < "$indexed_paths_file"

    if [[ "$found" == "false" ]]; then
      local size_bytes modified
      size_bytes=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null || echo 0)
      modified=$(stat -f%Sm -t "%Y-%m-%d" "$filepath" 2>/dev/null || stat -c%y "$filepath" 2>/dev/null | cut -d' ' -f1 || echo "unknown")

      local tmp_orphans
      tmp_orphans=$(safe_mktemp) || return 1
      jq -c --arg path "$rel" --argjson size "$size_bytes" --arg modified "$modified" \
        '. + [{path: $path, size_bytes: $size, modified: $modified, desc: "", tags: [], source: "", skip: false}]' \
        "$orphans_file" > "$tmp_orphans"
      mv "$tmp_orphans" "$orphans_file"
    fi
  done < <(find "$CLAW_DRIVE_DIR" -type f -not -path '*/.git/*' -not -name '.*' -not -name 'INDEX.jsonl' -not -name 'INDEX.md' -print0 | sort -z)

  # Build existing array with file_exists and size
  local existing_file
  existing_file=$(safe_mktemp) || return 1
  echo "[]" > "$existing_file"

  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    local path
    path=$(printf '%s' "$line" | jq -r '.path')
    local full="$CLAW_DRIVE_DIR/$path"
    local file_exists=false size_bytes=0

    if [[ -e "$full" ]]; then
      file_exists=true
      if [[ -f "$full" ]]; then
        size_bytes=$(stat -f%z "$full" 2>/dev/null || stat -c%s "$full" 2>/dev/null || echo 0)
      fi
    fi

    local tmp_existing
    tmp_existing=$(safe_mktemp) || return 1
    printf '%s' "$line" | jq -c --argjson exists "$file_exists" --argjson size "$size_bytes" \
      '. + {file_exists: $exists, size_bytes: $size}' | \
      jq -c --slurpfile arr "$existing_file" '$arr[0] + [.]' > "$tmp_existing"
    mv "$tmp_existing" "$existing_file"
  done < "$CLAW_DRIVE_INDEX"

  # Combine into plan
  jq -cn --slurpfile orphans "$orphans_file" --slurpfile existing "$existing_file" \
    '{orphans: $orphans[0], existing: $existing[0]}' > "$output"

  local orphan_count existing_count
  orphan_count=$(jq '.orphans | length' "$output")
  existing_count=$(jq '.existing | length' "$output")

  rm -f "$indexed_paths_file" "$orphans_file" "$existing_file"

  echo ""
  echo "📋 Plan written to: $output"
  echo "   Orphan files: $orphan_count"
  echo "   Existing entries: $existing_count"
  echo ""
  if [[ "$orphan_count" -gt 0 ]]; then
    echo "Orphans found:"
    jq -r '.orphans[] | "  📄 \(.path) (\(.size_bytes) bytes, \(.modified))"' "$output"
    echo ""
  fi
  echo "💡 Next: agent enriches the plan, then run 'claw-drive reindex apply $output'"
}

reindex_apply() {
  local plan="${1:-reindex-plan.json}"
  local dry_run=false
  shift || true

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) dry_run=true; shift ;;
      *) shift ;;
    esac
  done

  if [[ ! -f "$plan" ]]; then
    echo "❌ Plan file not found: $plan"
    return 1
  fi

  claw_drive_init || return 1

  echo "📥 Applying reindex plan: $plan"
  [[ "$dry_run" == "true" ]] && echo "   (dry run — no changes will be made)"
  echo ""

  local added=0 updated=0 skipped=0

  # Process orphans
  local orphan_count
  orphan_count=$(jq '.orphans | length' "$plan")

  local i=0
  while [[ $i -lt $orphan_count ]]; do
    local skip desc tags source path
    skip=$(jq -r ".orphans[$i].skip // false" "$plan")
    path=$(jq -r ".orphans[$i].path" "$plan")

    if [[ "$skip" == "true" ]]; then
      echo "  ⏭️  Skip: $path"
      ((skipped++)) || true
      ((i++)) || true
      continue
    fi

    desc=$(jq -r ".orphans[$i].desc // \"\"" "$plan")
    tags=$(jq -r ".orphans[$i].tags // [] | join(\",\")" "$plan")
    source=$(jq -r ".orphans[$i].source // \"reindex\"" "$plan")
    local metadata_json correspondent_val
    metadata_json=$(jq -c ".orphans[$i].metadata // null" "$plan")
    correspondent_val=$(jq -r ".orphans[$i].correspondent // \"\"" "$plan")

    if [[ -z "$desc" ]]; then
      echo "  ⚠️  No description for orphan: $path (skipping)"
      ((skipped++)) || true
      ((i++)) || true
      continue
    fi

    local date_str
    date_str=$(jq -r ".orphans[$i].modified // \"$(date +%Y-%m-%d)\"" "$plan")

    local meta_arg=""
    [[ "$metadata_json" != "null" ]] && meta_arg="$metadata_json"

    if [[ "$dry_run" == "true" ]]; then
      echo "  ➕ Would add: $path"
      echo "     desc: $desc"
      echo "     tags: $tags"
      [[ -n "$meta_arg" ]] && echo "     metadata: $meta_arg"
      [[ -n "$correspondent_val" ]] && echo "     correspondent: $correspondent_val"
    else
      # Add to index
      index_add "$date_str" "$path" "$desc" "$tags" "$source" "$meta_arg" "" "$correspondent_val"

      # Register hash
      local full="$CLAW_DRIVE_DIR/$path"
      if [[ -f "$full" ]]; then
        dedup_register "$full" "$path"
      fi

      echo "  ✅ Added: $path"
    fi
    ((added++)) || true
    ((i++)) || true
  done

  # Process existing entries with updates
  local existing_count
  existing_count=$(jq '.existing | length' "$plan")

  i=0
  while [[ $i -lt $existing_count ]]; do
    local new_desc new_tags new_metadata new_correspondent path
    path=$(jq -r ".existing[$i].path" "$plan")
    new_desc=$(jq -r ".existing[$i].new_desc // \"\"" "$plan")
    new_tags=$(jq -r ".existing[$i].new_tags // null" "$plan")
    new_metadata=$(jq -c ".existing[$i].new_metadata // null" "$plan")
    new_correspondent=$(jq -r ".existing[$i].new_correspondent // \"\"" "$plan")
    local new_source
    new_source=$(jq -r ".existing[$i].new_source // \"\"" "$plan")

    if [[ -n "$new_desc" || "$new_tags" != "null" || "$new_metadata" != "null" || -n "$new_correspondent" || -n "$new_source" ]]; then
      if [[ "$dry_run" == "true" ]]; then
        echo "  📝 Would update: $path"
        [[ -n "$new_desc" ]] && echo "     new desc: $new_desc"
        [[ "$new_tags" != "null" ]] && echo "     new tags: $(jq -r ".existing[$i].new_tags | join(\",\")" "$plan")"
        [[ "$new_metadata" != "null" ]] && echo "     new metadata: $new_metadata"
        [[ -n "$new_correspondent" ]] && echo "     new correspondent: $new_correspondent"
        [[ -n "$new_source" ]] && echo "     new source: $new_source"
      else
        local update_args=()
        [[ -n "$new_desc" ]] && update_args+=(--desc "$new_desc")
        if [[ "$new_tags" != "null" ]]; then
          local tags_csv
          tags_csv=$(jq -r ".existing[$i].new_tags | join(\",\")" "$plan")
          update_args+=(--tags "$tags_csv")
        fi
        [[ "$new_metadata" != "null" ]] && update_args+=(--metadata "$new_metadata")
        [[ -n "$new_correspondent" ]] && update_args+=(--correspondent "$new_correspondent")
        [[ -n "$new_source" ]] && update_args+=(--source "$new_source")

        index_update "$path" "${update_args[@]}"
        echo "  ✅ Updated: $path"
      fi
      ((updated++)) || true
    fi
    ((i++)) || true
  done

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  if [[ "$dry_run" == "true" ]]; then
    echo "Dry run complete: $added would be added, $updated would be updated, $skipped skipped"
  else
    echo "✅ Reindex complete: $added added, $updated updated, $skipped skipped"
  fi
}
