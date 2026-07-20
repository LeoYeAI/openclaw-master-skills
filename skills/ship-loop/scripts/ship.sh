#!/usr/bin/env bash
# ship.sh — Stage explicit files, safety check, commit, push, tag, verify
# Usage: bash scripts/ship.sh <segment-name> [shiploop.yml path]
# Exit 0 = shipped and verified, non-zero = failure
#
# SECURITY: Never uses `git add -A`. Only stages files from `git diff`.
# Scans staged files against a blocklist before committing.

set -euo pipefail

SEGMENT_NAME="${1:?Usage: ship.sh <segment-name> [shiploop.yml]}"
SHIPLOOP_FILE="${2:-SHIPLOOP.yml}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

# --------------------------------------------------------------------------
# Built-in blocklist: files that must NEVER be committed
# --------------------------------------------------------------------------
BUILTIN_BLOCKED=(
    '.env'
    '.env.*'
    '*.key'
    '*.pem'
    '*.p12'
    '*.pfx'
    '*.secret'
    'id_rsa'
    'id_ed25519'
    '*.keystore'
    'credentials.json'
    'service-account*.json'
    'token.json'
    '.npmrc'
    'node_modules/*'
    '__pycache__/*'
    '.pytest_cache/*'
    '*.sqlite'
    '*.sqlite3'
    '.DS_Store'
    'learnings.yml'
)

# Read additional blocked patterns from SHIPLOOP.yml
EXTRA_BLOCKED=()
if [[ -f "$SHIPLOOP_FILE" ]]; then
    while IFS= read -r line; do
        pattern=$(echo "$line" | sed 's/^  *- *//;s/"//g;s/'\''//g' | xargs)
        if [[ -n "$pattern" ]]; then
            EXTRA_BLOCKED+=("$pattern")
        fi
    done < <(sed -n '/^blocked_patterns:/,/^[^ ]/{ /^  *-/p }' "$SHIPLOOP_FILE" 2>/dev/null || true)
fi

ALL_BLOCKED=("${BUILTIN_BLOCKED[@]}" "${EXTRA_BLOCKED[@]}")

# --------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------

matches_pattern() {
    local file="$1"
    local pattern="$2"
    local basename
    basename=$(basename "$file")

    # Check against full path and basename
    # shellcheck disable=SC2254
    case "$file" in
        $pattern) return 0 ;;
    esac
    case "$basename" in
        $pattern) return 0 ;;
    esac
    # Check if file is inside a blocked directory
    if [[ "$pattern" == *'/*' ]]; then
        local dir="${pattern%/*}"
        case "$file" in
            ${dir}/*) return 0 ;;
        esac
    fi
    return 1
}

check_blocked() {
    local file="$1"
    for pattern in "${ALL_BLOCKED[@]}"; do
        if matches_pattern "$file" "$pattern"; then
            echo "$file (matched: $pattern)"
            return 0
        fi
    done
    return 1
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 SHIP: $SEGMENT_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --------------------------------------------------------------------------
# Step 1: Identify changed files (tracked modified + untracked new files)
# --------------------------------------------------------------------------
echo ""
echo "📋 Identifying changed files..."

CHANGED_FILES=()

# Modified/deleted tracked files
while IFS= read -r file; do
    [[ -n "$file" ]] && CHANGED_FILES+=("$file")
done < <(git diff --name-only HEAD 2>/dev/null || git diff --name-only)

# New untracked files (not in .gitignore)
while IFS= read -r file; do
    [[ -n "$file" ]] && CHANGED_FILES+=("$file")
done < <(git ls-files --others --exclude-standard)

if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
    echo "⚠️  No changed files detected. Nothing to commit."
    exit 1
fi

echo "   Found ${#CHANGED_FILES[@]} changed file(s)"

# --------------------------------------------------------------------------
# Step 2: Security scan — check for blocked files
# --------------------------------------------------------------------------
echo ""
echo "🔒 Security scan..."

BLOCKED_FOUND=()
SAFE_FILES=()

for file in "${CHANGED_FILES[@]}"; do
    blocked_match=""
    if blocked_match=$(check_blocked "$file"); then
        BLOCKED_FOUND+=("$blocked_match")
    else
        SAFE_FILES+=("$file")
    fi
done

if [[ ${#BLOCKED_FOUND[@]} -gt 0 ]]; then
    echo "🚨 BLOCKED FILES DETECTED — commit aborted!"
    echo ""
    for bf in "${BLOCKED_FOUND[@]}"; do
        echo "   🚫 $bf"
    done
    echo ""
    echo "   These files match the security blocklist."
    echo "   Add them to .gitignore or remove them before retrying."
    exit 1
fi

echo "   ✅ All ${#SAFE_FILES[@]} files passed security scan"

# --------------------------------------------------------------------------
# Step 3: Stage only safe, changed files
# --------------------------------------------------------------------------
echo ""
echo "📂 Staging files..."

for file in "${SAFE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        git add "$file"
        echo "   + $file"
    else
        # File was deleted
        git rm --cached "$file" 2>/dev/null || true
        echo "   - $file (deleted)"
    fi
done

# --------------------------------------------------------------------------
# Step 4: Commit
# --------------------------------------------------------------------------
echo ""
echo "💾 Committing..."

COMMIT_MSG="feat(shiploop): ${SEGMENT_NAME}"
git commit -m "$COMMIT_MSG" || {
    echo "❌ Commit failed (maybe nothing to commit after staging)"
    exit 1
}

COMMIT_SHA=$(git rev-parse HEAD)
SHORT_SHA=$(git rev-parse --short HEAD)
echo "   Commit: $SHORT_SHA — $COMMIT_MSG"

# --------------------------------------------------------------------------
# Step 5: Tag for rollback
# --------------------------------------------------------------------------
TAG_NAME="shiploop/${SEGMENT_NAME}/$(date +%Y%m%d-%H%M%S)"
git tag "$TAG_NAME" HEAD
echo "   Tag: $TAG_NAME"

# --------------------------------------------------------------------------
# Step 6: Push
# --------------------------------------------------------------------------
echo ""
echo "🚀 Pushing..."

BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin "$BRANCH" --tags || {
    echo "❌ Push failed"
    exit 1
}
echo "   Pushed to origin/$BRANCH"

# --------------------------------------------------------------------------
# Step 7: Verify deployment
# --------------------------------------------------------------------------
echo ""
if [[ -x "$SCRIPT_DIR/verify-deploy.sh" ]]; then
    echo "🔍 Running deployment verification..."
    if bash "$SCRIPT_DIR/verify-deploy.sh" "$SHIPLOOP_FILE"; then
        echo ""
        echo "✅ Deploy verified!"
    else
        echo ""
        echo "❌ Deploy verification failed!"
        echo "   Commit $SHORT_SHA was pushed but deploy may not be live."
        echo "   Rollback tag: $TAG_NAME"
        exit 1
    fi
else
    echo "⚠️  No verify-deploy.sh found — skipping verification"
fi

# --------------------------------------------------------------------------
# Step 8: Output results (machine-readable last line)
# --------------------------------------------------------------------------
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SHIPPED: $SEGMENT_NAME"
echo "   Commit: $COMMIT_SHA"
echo "   Tag: $TAG_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Machine-readable output (last line, parseable by run-segment.sh)
echo "SHIP_RESULT|commit=$COMMIT_SHA|tag=$TAG_NAME|segment=$SEGMENT_NAME"
