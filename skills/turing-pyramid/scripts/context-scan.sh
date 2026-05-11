#!/bin/bash
# Turing Pyramid — Layer C: Context-Driven Spontaneity
# Delta engine: snapshot → compare → detect triggers → emit boosts
#
# Called by run-cycle.sh after B, before action selection.
# Outputs fired triggers as JSON lines to stdout.
# Logs to stderr.
#
# Detector types:
#   file_count_delta  — count files in path, compare to snapshot
#   file_modified     — check mtime of specific file vs snapshot
#   file_keyword_delta — count keyword occurrences in path, compare to snapshot

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRIGGERS_FILE="$SKILL_DIR/assets/context-triggers.json"
ASSETS_DIR="$SKILL_DIR/assets"

if [[ -z "${WORKSPACE:-}" ]]; then
    echo "❌ WORKSPACE not set" >&2
    exit 1
fi

if [[ ! -f "$TRIGGERS_FILE" ]]; then
    exit 0  # No triggers configured
fi

# Snapshot file path (relative to assets/)
SNAPSHOT_NAME=$(jq -r '.snapshot_file // "last-scan-snapshot.json"' "$TRIGGERS_FILE")
SNAPSHOT_FILE="$ASSETS_DIR/$SNAPSHOT_NAME"
DEFAULT_COOLDOWN=$(jq -r '.default_cooldown_hours // 6' "$TRIGGERS_FILE")

NOW_EPOCH=$(date +%s)
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# ─── Security: validate path stays within WORKSPACE ───
validate_path() {
    local rel_path=$1
    local resolved
    # Block obvious traversal
    if [[ "$rel_path" == *".."* ]]; then
        echo "  [CONTEXT] BLOCKED: path traversal in '$rel_path'" >&2
        return 1
    fi
    local abs="$WORKSPACE/$rel_path"
    # Resolve and verify it's under WORKSPACE
    resolved=$(realpath -m "$abs" 2>/dev/null || echo "$abs")
    if [[ "$resolved" != "$WORKSPACE"* ]]; then
        echo "  [CONTEXT] BLOCKED: path '$rel_path' escapes workspace" >&2
        return 1
    fi
    return 0
}

# Load or create snapshot
if [[ -f "$SNAPSHOT_FILE" ]]; then
    SNAPSHOT=$(cat "$SNAPSHOT_FILE")
else
    SNAPSHOT='{"taken_at":"1970-01-01T00:00:00Z","file_counts":{},"file_mtimes":{},"keyword_counts":{},"trigger_cooldowns":{}}'
fi

# New snapshot to build
NEW_FILE_COUNTS="{}"
NEW_FILE_MTIMES="{}"
NEW_KEYWORD_COUNTS="{}"
NEW_COOLDOWNS=$(echo "$SNAPSHOT" | jq '.trigger_cooldowns // {}')

FIRED_COUNT=0

# Process each trigger
TRIGGER_COUNT=$(jq '.triggers | length' "$TRIGGERS_FILE")

for ((i=0; i<TRIGGER_COUNT; i++)); do
    trigger=$(jq -c ".triggers[$i]" "$TRIGGERS_FILE")
    
    id=$(echo "$trigger" | jq -r '.id')
    detector_type=$(echo "$trigger" | jq -r '.detector.type')
    threshold=$(echo "$trigger" | jq -r '.threshold // 1')
    cooldown_hours=$(echo "$trigger" | jq -r ".cooldown_hours // $DEFAULT_COOLDOWN")
    
    # Check cooldown
    last_fired=$(echo "$SNAPSHOT" | jq -r ".trigger_cooldowns.\"$id\" // \"1970-01-01T00:00:00Z\"")
    last_fired_epoch=$(date -d "$last_fired" +%s 2>/dev/null || echo 0)
    cooldown_seconds=$(echo "$cooldown_hours * 3600" | bc -l | cut -d. -f1)
    
    if (( NOW_EPOCH - last_fired_epoch < cooldown_seconds )); then
        echo "  [CONTEXT] $id: cooldown ($(( (cooldown_seconds - NOW_EPOCH + last_fired_epoch) / 3600 ))h remaining)" >&2
        continue
    fi
    
    delta=0
    
    case "$detector_type" in
        file_count_delta)
            rel_path=$(echo "$trigger" | jq -r '.detector.path')
            validate_path "$rel_path" || continue
            abs_path="$WORKSPACE/$rel_path"
            
            # Current count (no symlink following)
            if [[ -d "$abs_path" ]]; then
                current_count=$(find "$abs_path" -not -type l -type f 2>/dev/null | wc -l)
            else
                current_count=0
            fi
            
            # Snapshot count
            snapshot_count=$(echo "$SNAPSHOT" | jq -r ".file_counts.\"$rel_path\" // 0")
            
            delta=$((current_count - snapshot_count))
            
            # Update new snapshot
            NEW_FILE_COUNTS=$(echo "$NEW_FILE_COUNTS" | jq --arg p "$rel_path" --argjson c "$current_count" '.[$p] = $c')
            ;;
            
        file_modified)
            rel_path=$(echo "$trigger" | jq -r '.detector.path')
            validate_path "$rel_path" || continue
            abs_path="$WORKSPACE/$rel_path"
            
            if [[ -f "$abs_path" ]]; then
                current_mtime=$(stat -c %Y "$abs_path" 2>/dev/null || echo 0)
                current_mtime_iso=$(date -u -d "@$current_mtime" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "1970-01-01T00:00:00Z")
            else
                current_mtime_iso="1970-01-01T00:00:00Z"
            fi
            
            snapshot_mtime=$(echo "$SNAPSHOT" | jq -r ".file_mtimes.\"$rel_path\" // \"1970-01-01T00:00:00Z\"")
            
            if [[ "$current_mtime_iso" != "$snapshot_mtime" ]]; then
                delta=1
            fi
            
            # Update new snapshot
            NEW_FILE_MTIMES=$(echo "$NEW_FILE_MTIMES" | jq --arg p "$rel_path" --arg m "$current_mtime_iso" '.[$p] = $m')
            ;;
            
        file_keyword_delta)
            rel_path=$(echo "$trigger" | jq -r '.detector.path')
            validate_path "$rel_path" || continue
            abs_path="$WORKSPACE/$rel_path"
            keywords=$(echo "$trigger" | jq -r '.detector.keywords[]' 2>/dev/null)
            
            total_current=0
            total_snapshot=0
            
            while IFS= read -r kw; do
                [[ -z "$kw" ]] && continue
                snapshot_key="$kw:$rel_path"
                
                if [[ -d "$abs_path" ]]; then
                    # Fixed grep: -F for literal match (no regex injection), no symlink following
                    kw_count=$(find "$abs_path" -not -type l -type f -print0 2>/dev/null | xargs -0 grep -lF "$kw" 2>/dev/null | wc -l)
                else
                    kw_count=0
                fi
                
                snap_count=$(echo "$SNAPSHOT" | jq -r ".keyword_counts.\"$snapshot_key\" // 0")
                
                total_current=$((total_current + kw_count))
                total_snapshot=$((total_snapshot + snap_count))
                
                NEW_KEYWORD_COUNTS=$(echo "$NEW_KEYWORD_COUNTS" | jq --arg k "$snapshot_key" --argjson c "$kw_count" '.[$k] = $c')
            done <<< "$keywords"
            
            delta=$((total_current - total_snapshot))
            ;;
            
        *)
            echo "  [CONTEXT] $id: unknown detector type '$detector_type'" >&2
            continue
            ;;
    esac
    
    # Check threshold
    if [[ $delta -ge $threshold ]]; then
        # FIRED
        ((FIRED_COUNT++))
        
        boost_needs=$(echo "$trigger" | jq -c '.boost.needs')
        boost_amount=$(echo "$trigger" | jq -r '.boost.amount')
        boost_label=$(echo "$trigger" | jq -r '.boost.label // "[CONTEXT]"')
        
        echo "  [CONTEXT] ✓ $id: delta=$delta (threshold=$threshold) → boost $boost_needs by $boost_amount $boost_label" >&2
        
        # Output fired trigger as JSON line (consumed by caller)
        echo "{\"id\":\"$id\",\"needs\":$boost_needs,\"amount\":$boost_amount,\"label\":\"$boost_label\"}"
        
        # Update cooldown
        NEW_COOLDOWNS=$(echo "$NEW_COOLDOWNS" | jq --arg id "$id" --arg t "$NOW_ISO" '.[$id] = $t')
    else
        echo "  [CONTEXT] $id: delta=$delta (threshold=$threshold) — no trigger" >&2
    fi
done

# Merge and save new snapshot
# Merge new counts with existing (keep entries not re-scanned)
EXISTING_FILE_COUNTS=$(echo "$SNAPSHOT" | jq '.file_counts // {}')
EXISTING_FILE_MTIMES=$(echo "$SNAPSHOT" | jq '.file_mtimes // {}')
EXISTING_KEYWORD_COUNTS=$(echo "$SNAPSHOT" | jq '.keyword_counts // {}')

jq -n \
    --arg taken_at "$NOW_ISO" \
    --argjson fc "$(echo "$EXISTING_FILE_COUNTS $NEW_FILE_COUNTS" | jq -s '.[0] * .[1]')" \
    --argjson fm "$(echo "$EXISTING_FILE_MTIMES $NEW_FILE_MTIMES" | jq -s '.[0] * .[1]')" \
    --argjson kc "$(echo "$EXISTING_KEYWORD_COUNTS $NEW_KEYWORD_COUNTS" | jq -s '.[0] * .[1]')" \
    --argjson cd "$NEW_COOLDOWNS" \
    '{taken_at: $taken_at, file_counts: $fc, file_mtimes: $fm, keyword_counts: $kc, trigger_cooldowns: $cd}' \
    > "$SNAPSHOT_FILE"

if [[ $FIRED_COUNT -gt 0 ]]; then
    echo "  [CONTEXT] $FIRED_COUNT trigger(s) fired" >&2
fi
