#!/usr/bin/env bash
# verify-deploy.sh — Poll production until new deployment is verified
# Usage: bash scripts/verify-deploy.sh [shiploop.yml path]
# Exit 0 = verified, non-zero = verification failed
#
# Platform-aware: vercel, netlify, static, custom
# Checks: HTTP 200, response markers, deployment headers, health endpoints

set -euo pipefail

SHIPLOOP_FILE="${1:-SHIPLOOP.yml}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

# --------------------------------------------------------------------------
# Parse config from SHIPLOOP.yml
# --------------------------------------------------------------------------
get_value() {
    local key="$1"
    local default="${2:-}"
    local val
    val=$(grep -E "^${key}:|^  ${key}:" "$SHIPLOOP_FILE" 2>/dev/null \
        | head -1 \
        | sed "s/^[[:space:]]*${key}:[[:space:]]*//" \
        | sed 's/^"//;s/"$//' \
        | sed "s/^'//;s/'$//" \
        | xargs)
    if [[ -n "$val" && "$val" != "null" ]]; then
        echo "$val"
    else
        echo "$default"
    fi
}

get_list() {
    local key="$1"
    sed -n "/^  ${key}:/,/^  [^ ]/{ /^    *-/p }" "$SHIPLOOP_FILE" 2>/dev/null \
        | sed 's/^  *- *//;s/"//g' \
        | xargs -I{} echo "{}" || true
}

SITE=$(get_value "site" "")
PLATFORM=$(get_value "platform" "static")
VERIFY_TIMEOUT=$(get_value "verify" "180")
# Try to get verify timeout specifically
VERIFY_TIMEOUT_SPECIFIC=$(grep -A5 "^timeouts:" "$SHIPLOOP_FILE" 2>/dev/null | grep "verify:" | sed 's/.*verify:[[:space:]]*//' | xargs 2>/dev/null || true)
[[ -n "$VERIFY_TIMEOUT_SPECIFIC" ]] && VERIFY_TIMEOUT="$VERIFY_TIMEOUT_SPECIFIC"

MARKER=$(get_value "marker" "")
HEALTH_ENDPOINT=$(get_value "health_endpoint" "")
DEPLOY_HEADER=$(get_value "deploy_header" "")

# Read routes
ROUTES=()
while IFS= read -r route; do
    [[ -n "$route" ]] && ROUTES+=("$route")
done < <(get_list "routes")

# Default to / if no routes specified
[[ ${#ROUTES[@]} -eq 0 ]] && ROUTES=("/")

if [[ -z "$SITE" ]]; then
    echo "❌ No 'site' configured in $SHIPLOOP_FILE"
    exit 1
fi

# Remove trailing slash from site
SITE="${SITE%/}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 VERIFY DEPLOYMENT"
echo "   Site: $SITE"
echo "   Platform: $PLATFORM"
echo "   Timeout: ${VERIFY_TIMEOUT}s"
echo "   Routes: ${ROUTES[*]}"
[[ -n "$MARKER" ]] && echo "   Marker: $MARKER"
[[ -n "$HEALTH_ENDPOINT" ]] && echo "   Health: $HEALTH_ENDPOINT"
[[ -n "$DEPLOY_HEADER" ]] && echo "   Deploy header: $DEPLOY_HEADER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --------------------------------------------------------------------------
# Verification functions
# --------------------------------------------------------------------------

check_http() {
    local url="$1"
    local status
    status=$(curl -sL -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")
    echo "$status"
}

check_marker() {
    local url="$1"
    local marker="$2"
    local body
    body=$(curl -s --max-time 10 "$url" 2>/dev/null || true)
    if echo "$body" | grep -qi "$marker" 2>/dev/null; then
        return 0
    fi
    return 1
}

check_deploy_header() {
    local url="$1"
    local header="$2"
    local value
    value=$(curl -s -I --max-time 10 "$url" 2>/dev/null | grep -i "^${header}:" | sed "s/^${header}:[[:space:]]*//" | tr -d '\r' || true)
    if [[ -n "$value" ]]; then
        echo "$value"
        return 0
    fi
    return 1
}

check_health() {
    local url="$1"
    local status
    local body
    status=$(curl -s -o /tmp/health-check.json -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")
    if [[ "$status" == "200" ]]; then
        body=$(cat /tmp/health-check.json 2>/dev/null || true)
        # Check for common health response patterns
        if echo "$body" | grep -qiE '"(status|health)"[[:space:]]*:[[:space:]]*"(ok|healthy|up|pass)"' 2>/dev/null; then
            return 0
        fi
        # If 200 but no recognizable health body, still count it
        return 0
    fi
    return 1
}

# --------------------------------------------------------------------------
# Platform-specific pre-check
# --------------------------------------------------------------------------

vercel_precheck() {
    # Capture initial deployment ID to detect change
    local initial_deploy
    initial_deploy=$(check_deploy_header "$SITE" "x-vercel-deployment-url" 2>/dev/null || true)
    echo "$initial_deploy"
}

# --------------------------------------------------------------------------
# Main verification loop
# --------------------------------------------------------------------------

START_TIME=$(date +%s)
POLL_INTERVAL=5
ATTEMPT=0
INITIAL_DEPLOY_ID=""

# For Vercel: capture initial deployment to detect change
if [[ "$PLATFORM" == "vercel" && -n "$DEPLOY_HEADER" ]]; then
    INITIAL_DEPLOY_ID=$(check_deploy_header "$SITE" "$DEPLOY_HEADER" 2>/dev/null || true)
    [[ -n "$INITIAL_DEPLOY_ID" ]] && echo "   Initial deploy ID: $INITIAL_DEPLOY_ID"
fi

echo ""
echo "⏳ Waiting for deployment..."

while true; do
    ELAPSED=$(( $(date +%s) - START_TIME ))
    ((ATTEMPT++))

    if [[ $ELAPSED -ge $VERIFY_TIMEOUT ]]; then
        echo ""
        echo "❌ Verification timed out after ${VERIFY_TIMEOUT}s"
        exit 1
    fi

    ALL_PASSED=true

    # Step 1: Health endpoint (if configured)
    if [[ -n "$HEALTH_ENDPOINT" ]]; then
        if check_health "${SITE}${HEALTH_ENDPOINT}"; then
            echo "   ✅ Health endpoint OK (attempt $ATTEMPT, ${ELAPSED}s)"
        else
            ALL_PASSED=false
            echo "   ⏳ Health endpoint not ready (attempt $ATTEMPT, ${ELAPSED}s)"
            sleep "$POLL_INTERVAL"
            continue
        fi
    fi

    # Step 2: Deployment header change (Vercel/Netlify)
    if [[ -n "$DEPLOY_HEADER" && -n "$INITIAL_DEPLOY_ID" ]]; then
        CURRENT_DEPLOY=$(check_deploy_header "$SITE" "$DEPLOY_HEADER" 2>/dev/null || true)
        if [[ -n "$CURRENT_DEPLOY" && "$CURRENT_DEPLOY" != "$INITIAL_DEPLOY_ID" ]]; then
            echo "   ✅ New deployment detected: $CURRENT_DEPLOY"
        elif [[ -n "$CURRENT_DEPLOY" ]]; then
            ALL_PASSED=false
            echo "   ⏳ Same deployment ($CURRENT_DEPLOY), waiting for new... (attempt $ATTEMPT, ${ELAPSED}s)"
            sleep "$POLL_INTERVAL"
            continue
        fi
    fi

    # Step 3: Check all routes
    for route in "${ROUTES[@]}"; do
        URL="${SITE}${route}"
        STATUS=$(check_http "$URL")
        if [[ "$STATUS" == "200" ]]; then
            # Check marker if configured
            if [[ -n "$MARKER" ]]; then
                if check_marker "$URL" "$MARKER"; then
                    echo "   ✅ $route — HTTP $STATUS, marker found"
                else
                    ALL_PASSED=false
                    echo "   ⏳ $route — HTTP $STATUS but marker '$MARKER' not found (attempt $ATTEMPT)"
                fi
            else
                echo "   ✅ $route — HTTP $STATUS"
            fi
        else
            ALL_PASSED=false
            echo "   ⏳ $route — HTTP $STATUS (attempt $ATTEMPT, ${ELAPSED}s)"
        fi
    done

    if $ALL_PASSED; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ DEPLOYMENT VERIFIED (${ELAPSED}s, $ATTEMPT attempts)"
        DEPLOY_URL="$SITE"
        [[ -n "${CURRENT_DEPLOY:-}" ]] && DEPLOY_URL="$CURRENT_DEPLOY"
        echo "VERIFY_RESULT|deploy_url=$DEPLOY_URL|elapsed=${ELAPSED}s"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 0
    fi

    sleep "$POLL_INTERVAL"
done
