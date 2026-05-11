#!/usr/bin/env bash
# check-gh-auth.sh — Check GitHub CLI authentication status, token type, and scopes.
# Outputs JSON with compatibility assessment for Telnyx upgrade evaluation.
#
# Usage: bash check-gh-auth.sh
# Output: JSON to stdout

set -euo pipefail

REQUIRED_SCOPES=("user" "read:org")

json_output() {
    local authenticated="$1"
    local username="$2"
    local token_prefix="$3"
    local token_type="$4"
    local scopes="$5"
    local missing_scopes="$6"
    local compatible="$7"
    local degraded="$8"
    local message="$9"

    cat <<EOF
{
  "authenticated": ${authenticated},
  "username": ${username},
  "token_prefix": ${token_prefix},
  "token_type": ${token_type},
  "scopes": ${scopes},
  "missing_scopes": ${missing_scopes},
  "compatible": ${compatible},
  "degraded": ${degraded},
  "message": ${message}
}
EOF
}

# Check if gh is installed
if ! command -v gh &>/dev/null; then
    json_output "false" "null" "null" "null" "[]" "[]" "false" "false" \
        '"GitHub CLI (gh) is not installed. Install: https://cli.github.com"'
    exit 0
fi

# Check if gh is authenticated
if ! gh auth status &>/dev/null 2>&1; then
    json_output "false" "null" "null" "null" "[]" "[]" "false" "false" \
        '"GitHub CLI is not authenticated. Run: gh auth login --web"'
    exit 0
fi

# Get the token
TOKEN=$(gh auth token 2>/dev/null || true)
if [ -z "$TOKEN" ]; then
    json_output "false" "null" "null" "null" "[]" "[]" "false" "false" \
        '"Failed to retrieve GitHub token. Run: gh auth login --web"'
    exit 0
fi

# Determine token prefix and type
TOKEN_PREFIX="${TOKEN:0:4}"
TOKEN_TYPE=""
COMPATIBLE=true
DEGRADED=false

case "$TOKEN" in
    gho_*)
        TOKEN_PREFIX="gho_"
        TOKEN_TYPE="oauth"
        ;;
    ghp_*)
        TOKEN_PREFIX="ghp_"
        TOKEN_TYPE="classic_pat"
        ;;
    github_pat_*)
        TOKEN_PREFIX="github_pat_"
        TOKEN_TYPE="fine_grained_pat"
        DEGRADED=true
        ;;
    ghs_*)
        TOKEN_PREFIX="ghs_"
        TOKEN_TYPE="app_installation"
        COMPATIBLE=false
        ;;
    ghu_*)
        TOKEN_PREFIX="ghu_"
        TOKEN_TYPE="app_user"
        ;;
    *)
        TOKEN_PREFIX="${TOKEN:0:4}_"
        TOKEN_TYPE="unknown"
        ;;
esac

# Get username from gh auth status
USERNAME=$(gh auth status 2>&1 | grep -oP 'Logged in to github\.com account \K\S+' || \
           gh auth status 2>&1 | grep -oP 'account \K\S+' || \
           echo "")
# Remove trailing parenthesis or special chars
USERNAME=$(echo "$USERNAME" | sed 's/[^a-zA-Z0-9_.-]//g')

if [ -z "$USERNAME" ]; then
    USERNAME="null"
else
    USERNAME="\"${USERNAME}\""
fi

# Parse scopes from gh auth status
SCOPES_RAW=$(gh auth status 2>&1 | grep -i "token scopes" | sed "s/.*Token scopes: *'//;s/'//g" || echo "")
# Also try the format without quotes
if [ -z "$SCOPES_RAW" ]; then
    SCOPES_RAW=$(gh auth status 2>&1 | grep -i "scopes" | sed "s/.*scopes: *//;s/'//g" || echo "")
fi

# Build scopes JSON array
SCOPES_JSON="["
MISSING_JSON="["
if [ -n "$SCOPES_RAW" ]; then
    IFS=',' read -ra SCOPE_ARR <<< "$SCOPES_RAW"
    first=true
    for scope in "${SCOPE_ARR[@]}"; do
        scope=$(echo "$scope" | xargs)  # trim whitespace
        if [ -n "$scope" ]; then
            if [ "$first" = true ]; then
                SCOPES_JSON+="\"${scope}\""
                first=false
            else
                SCOPES_JSON+=", \"${scope}\""
            fi
        fi
    done
fi
SCOPES_JSON+="]"

# Check for missing required scopes
first=true
for req in "${REQUIRED_SCOPES[@]}"; do
    found=false
    if [ -n "$SCOPES_RAW" ]; then
        IFS=',' read -ra SCOPE_ARR <<< "$SCOPES_RAW"
        for scope in "${SCOPE_ARR[@]}"; do
            scope=$(echo "$scope" | xargs)
            if [ "$scope" = "$req" ]; then
                found=true
                break
            fi
        done
    fi
    if [ "$found" = false ]; then
        if [ "$first" = true ]; then
            MISSING_JSON+="\"${req}\""
            first=false
        else
            MISSING_JSON+=", \"${req}\""
        fi
    fi
done
MISSING_JSON+="]"

# Build message
if [ "$COMPATIBLE" = false ]; then
    MESSAGE="\"Incompatible token type: ${TOKEN_TYPE}. GitHub App installation tokens cannot access user profile data. Run: gh auth login --web\""
elif [ "$DEGRADED" = true ]; then
    MESSAGE="\"Fine-grained PAT detected. Some profile data (organizations, GraphQL contributions) may be unavailable. For best results, run: gh auth login --web\""
elif [ "$MISSING_JSON" != "[]" ]; then
    MESSAGE="\"Missing required scopes. Run: gh auth refresh --scopes user,read:org\""
else
    MESSAGE="\"GitHub CLI is authenticated and compatible. Ready for upgrade evaluation.\""
fi

json_output "true" "$USERNAME" "\"${TOKEN_PREFIX}\"" "\"${TOKEN_TYPE}\"" \
    "$SCOPES_JSON" "$MISSING_JSON" "$COMPATIBLE" "$DEGRADED" "$MESSAGE"
