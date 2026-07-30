#!/bin/bash
# Search emails using provider abstraction
# Usage: email_search.sh --query <query> [--max <n>] [--include-body] [--provider <provider>]
#
# Returns JSON with list of matching emails

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

QUERY=""
MAX="20"
INCLUDE_BODY=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --query)
            QUERY="$2"
            shift 2
            ;;
        --max)
            MAX="$2"
            shift 2
            ;;
        --include-body)
            INCLUDE_BODY="true"
            shift
            ;;
        --provider)
            PROVIDER="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$QUERY" ]; then
    echo "Usage: email_search.sh --query <query> [--max <n>] [--include-body] [--provider <provider>]" >&2
    exit 1
fi

# Build args array (avoids eval quoting issues)
ARGS=(search --query "$QUERY" --max "$MAX")
if [ "$INCLUDE_BODY" = "true" ]; then
    ARGS+=(--include-body true)
fi
if [ -n "$PROVIDER" ]; then
    ARGS+=(--provider "$PROVIDER")
fi

python3 "$UTILS_DIR/email_ops.py" "${ARGS[@]}"
