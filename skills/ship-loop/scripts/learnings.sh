#!/usr/bin/env bash
# learnings.sh — Persistent learnings engine for ship-loop
# Usage:
#   bash scripts/learnings.sh record <segment> <failure> <root-cause> <fix> [learnings.yml]
#   bash scripts/learnings.sh load <prompt-keywords> [learnings.yml]
#
# record: Append a new learning entry to learnings.yml
# load: Output relevant learnings matching prompt keywords (for agent context injection)

set -euo pipefail

ACTION="${1:?Usage: learnings.sh <record|load> ...}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

# Stop words to filter out of keyword matching
STOP_WORDS="a an the is are was were to from in on of for with by at and or but not this that it"

case "$ACTION" in
    record)
        SEGMENT="${2:?Usage: learnings.sh record <segment> <failure> <root-cause> <fix> [learnings.yml]}"
        FAILURE="${3:?Missing failure description}"
        ROOT_CAUSE="${4:?Missing root cause}"
        FIX="${5:?Missing fix description}"
        LEARNINGS_FILE="${6:-learnings.yml}"

        # Generate next ID
        if [[ -f "$LEARNINGS_FILE" ]]; then
            LAST_ID=$(grep -oP 'id: L\K[0-9]+' "$LEARNINGS_FILE" 2>/dev/null | sort -n | tail -1 || echo "0")
        else
            LAST_ID=0
        fi
        NEXT_ID=$(printf "L%03d" $((LAST_ID + 1)))
        TODAY=$(date +%Y-%m-%d)

        # Escape values for safe YAML (wrap in single quotes, escape internal single quotes)
        escape_yaml() {
            local val="$1"
            # Replace single quotes with '' (YAML single-quote escaping)
            val="${val//\'/\'\'}"
            echo "'${val}'"
        }

        SAFE_SEGMENT=$(escape_yaml "$SEGMENT")
        SAFE_FAILURE=$(escape_yaml "$FAILURE")
        SAFE_ROOT_CAUSE=$(escape_yaml "$ROOT_CAUSE")
        SAFE_FIX=$(escape_yaml "$FIX")

        # Append entry
        cat >> "$LEARNINGS_FILE" << ENTRY_EOF

- id: $NEXT_ID
  date: "$TODAY"
  segment: $SAFE_SEGMENT
  failure: $SAFE_FAILURE
  root_cause: $SAFE_ROOT_CAUSE
  fix: $SAFE_FIX
  applies_to: [prompt, code]
ENTRY_EOF

        echo "📝 Learning $NEXT_ID recorded: $FAILURE"
        ;;

    load)
        KEYWORDS="${2:-}"
        LEARNINGS_FILE="${3:-learnings.yml}"

        if [[ ! -f "$LEARNINGS_FILE" ]]; then
            # No learnings yet, silently exit
            exit 0
        fi

        if [[ -z "$KEYWORDS" ]]; then
            # Output all learnings
            echo "## Learnings from Previous Runs"
            echo ""
            echo "Apply these lessons to avoid repeating past failures:"
            echo ""
            cat "$LEARNINGS_FILE"
            exit 0
        fi

        # Filter out stop words from keywords
        FILTERED_KEYWORDS=""
        for keyword in $KEYWORDS; do
            kw_lower=$(echo "$keyword" | tr '[:upper:]' '[:lower:]')
            IS_STOP=false
            for sw in $STOP_WORDS; do
                if [[ "$kw_lower" == "$sw" ]]; then
                    IS_STOP=true
                    break
                fi
            done
            if ! $IS_STOP && [[ ${#kw_lower} -ge 3 ]]; then
                FILTERED_KEYWORDS="$FILTERED_KEYWORDS $kw_lower"
            fi
        done
        FILTERED_KEYWORDS=$(echo "$FILTERED_KEYWORDS" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

        if [[ -z "$FILTERED_KEYWORDS" ]]; then
            echo "(No meaningful keywords after filtering)"
            exit 0
        fi

        # Search for relevant learnings by keyword matching
        echo "## Relevant Learnings"
        echo ""
        echo "These past failures are relevant to your current task. Avoid repeating them:"
        echo ""

        # Collect matching blocks, limit to 5 most recent
        MATCHED_BLOCKS=()
        CURRENT_BLOCK=""
        IN_BLOCK=false

        while IFS= read -r line; do
            if [[ "$line" =~ ^-\ id: ]]; then
                # Start of a new block — check previous block for matches
                if $IN_BLOCK && [[ -n "$CURRENT_BLOCK" ]]; then
                    BLOCK_LOWER=$(echo "$CURRENT_BLOCK" | tr '[:upper:]' '[:lower:]')
                    for keyword in $FILTERED_KEYWORDS; do
                        # Use grep -w for word boundary, -- to prevent option injection
                        if echo "$BLOCK_LOWER" | grep -qw -- "$keyword" 2>/dev/null; then
                            MATCHED_BLOCKS+=("$CURRENT_BLOCK")
                            break
                        fi
                    done
                fi
                CURRENT_BLOCK="$line"
                IN_BLOCK=true
            elif $IN_BLOCK; then
                CURRENT_BLOCK="${CURRENT_BLOCK}
${line}"
            fi
        done < "$LEARNINGS_FILE"

        # Check the last block
        if $IN_BLOCK && [[ -n "$CURRENT_BLOCK" ]]; then
            BLOCK_LOWER=$(echo "$CURRENT_BLOCK" | tr '[:upper:]' '[:lower:]')
            for keyword in $FILTERED_KEYWORDS; do
                if echo "$BLOCK_LOWER" | grep -qw -- "$keyword" 2>/dev/null; then
                    MATCHED_BLOCKS+=("$CURRENT_BLOCK")
                    break
                fi
            done
        fi

        if [[ ${#MATCHED_BLOCKS[@]} -eq 0 ]]; then
            echo "(No relevant learnings found for: $FILTERED_KEYWORDS)"
        else
            # Output only the 5 most recent matches
            TOTAL=${#MATCHED_BLOCKS[@]}
            START=$(( TOTAL > 5 ? TOTAL - 5 : 0 ))
            for (( i=START; i<TOTAL; i++ )); do
                echo "${MATCHED_BLOCKS[$i]}"
                echo ""
            done
        fi
        ;;

    *)
        echo "❌ Unknown action: $ACTION"
        echo "Usage: learnings.sh <record|load> ..."
        exit 1
        ;;
esac
