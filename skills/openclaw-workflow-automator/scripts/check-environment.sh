#!/usr/bin/env bash
set -eo pipefail

# check-environment.sh — Preflight check for required tools.
# Verifies all binaries needed by workflow-automator are present
# before any workflow runs. Fails fast with clear install guidance.

REQUIRED_TOOLS="bash jq date grep sed awk mktemp curl bc"
OPTIONAL_TOOLS="timeout gtimeout wkhtmltopdf"
SHA_TOOLS="shasum sha256sum"

CACHE_DIR="$HOME/.openclaw/workflow-automator"
CACHE_FILE="$CACHE_DIR/.env-check-cache"
CACHE_TTL=3600  # Re-check every hour (seconds)

usage() {
    cat <<'EOF'
Usage: check-environment.sh [options]

Verify all required tools for workflow-automator are installed.

Options:
  --no-cache    Skip cache, always re-check
  --verbose     Show all tools, not just missing ones
  --help        Show this help message

Required tools:
  bash, jq, shasum/sha256sum, date, grep, sed, awk, mktemp, curl, bc

Optional tools (fallbacks exist):
  timeout/gtimeout — step execution timeouts (skipped if absent)
  wkhtmltopdf — PDF invoice generation (not needed for core features)

Exit codes:
  0  All required tools present
  1  One or more required tools missing
EOF
    exit 0
}

NO_CACHE="false"
VERBOSE="false"

for arg in "$@"; do
    case "$arg" in
        --help) usage ;;
        --no-cache) NO_CACHE="true" ;;
        --verbose) VERBOSE="true" ;;
    esac
done

mkdir -p "$CACHE_DIR"

# Check cache
if [ "$NO_CACHE" = "false" ] && [ -f "$CACHE_FILE" ]; then
    cache_age=0
    if stat -f %m "$CACHE_FILE" >/dev/null 2>&1; then
        cache_ts=$(stat -f %m "$CACHE_FILE")
        now_ts=$(date +%s)
        cache_age=$((now_ts - cache_ts))
    elif stat -c %Y "$CACHE_FILE" >/dev/null 2>&1; then
        cache_ts=$(stat -c %Y "$CACHE_FILE")
        now_ts=$(date +%s)
        cache_age=$((now_ts - cache_ts))
    fi

    if [ "$cache_age" -lt "$CACHE_TTL" ]; then
        cached_result=$(cat "$CACHE_FILE")
        if [ "$cached_result" = "PASS" ]; then
            [ "$VERBOSE" = "true" ] && echo "PASS (cached): All required tools present"
            exit 0
        fi
    fi
fi

# Use simple strings to track results (avoids bash array issues with set -u)
missing=""
present=""
missing_count=0

# Check required tools
for tool in $REQUIRED_TOOLS; do
    if command -v "$tool" >/dev/null 2>&1; then
        present="$present $tool"
        if [ "$VERBOSE" = "true" ]; then
            path=$(command -v "$tool")
            echo "  [OK]      $tool ($path)"
        fi
    else
        missing="$missing $tool"
        missing_count=$((missing_count + 1))
        if [ "$VERBOSE" = "true" ]; then
            echo "  [MISSING] $tool"
        fi
    fi
done

# Check SHA tool (need at least one)
sha_found="false"
for tool in $SHA_TOOLS; do
    if command -v "$tool" >/dev/null 2>&1; then
        sha_found="true"
        present="$present $tool"
        if [ "$VERBOSE" = "true" ]; then
            path=$(command -v "$tool")
            echo "  [OK]      $tool ($path)"
        fi
        break
    fi
done
if [ "$sha_found" = "false" ]; then
    missing="$missing shasum/sha256sum"
    missing_count=$((missing_count + 1))
    if [ "$VERBOSE" = "true" ]; then
        echo "  [MISSING] shasum/sha256sum"
    fi
fi

# Check optional tools
if [ "$VERBOSE" = "true" ]; then
    echo ""
    echo "Optional tools:"
    for tool in $OPTIONAL_TOOLS; do
        if command -v "$tool" >/dev/null 2>&1; then
            path=$(command -v "$tool")
            echo "  [OK]      $tool ($path)"
        else
            echo "  [SKIP]    $tool (optional, fallback available)"
        fi
    done
    echo ""
fi

# Report results
if [ "$missing_count" -gt 0 ]; then
    echo "FAIL: Missing required tools:$missing"
    echo ""
    echo "Install hints:"
    for tool in $missing; do
        case "$tool" in
            jq)
                echo "  jq:              brew install jq  (macOS)  |  apt install jq  (Linux)"
                ;;
            shasum/sha256sum)
                echo "  shasum/sha256sum: brew install perl  (macOS)  |  apt install perl  (Linux)"
                ;;
            curl)
                echo "  curl:            brew install curl  (macOS)  |  apt install curl  (Linux)"
                ;;
            bc)
                echo "  bc:              brew install bc  (macOS)  |  apt install bc  (Linux)"
                ;;
            *)
                echo "  $tool:           Usually pre-installed. Check your PATH."
                ;;
        esac
    done

    echo "FAIL" > "$CACHE_FILE"
    exit 1
else
    if [ "$VERBOSE" = "true" ]; then
        echo "Result: PASS — All required tools present"
    else
        echo "PASS: All required tools present"
    fi

    echo "PASS" > "$CACHE_FILE"
    exit 0
fi
