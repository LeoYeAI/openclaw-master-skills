#!/bin/bash
# checks.sh - Unified policies/ + checks/ enforcement
# Executes checks FIRST, then reads policies

set -e

PROJECT_ROOT="${1:-.}"
MODE="${2:-start}" # start or end

cd "$PROJECT_ROOT"

echo "🔍 Running backstage enforcement (mode: $MODE)..."
echo ""

# ============================================================================
# STEP 1: Execute ALL checks (deterministic - bash domain)
# ============================================================================

echo "🔍 Executing checks/ (deterministic)..."
echo ""

GLOBAL_CHECKS_DIR="$HOME/Documents/backstage/backstage/checks/global"
LOCAL_CHECKS_DIR="backstage/checks/local"

CHECKS_PASS=true
CHECKS_RUN=0
ROADMAP_STATUS="" # Capture roadmap-tasks output

# Collect local check basenames (for override detection)
LOCAL_CHECKS=""
if [ -d "$LOCAL_CHECKS_DIR" ]; then
    for check in "$LOCAL_CHECKS_DIR"/*.sh; do
        if [ -f "$check" ]; then
            basename_check=$(basename "$check")
            LOCAL_CHECKS="$LOCAL_CHECKS $basename_check "
        fi
    done
fi

# Run global checks (skip if local has same name)
if [ -d "$GLOBAL_CHECKS_DIR" ]; then
    echo "  📋 Global checks:"
    for check in "$GLOBAL_CHECKS_DIR"/*.sh; do
        if [ -f "$check" ]; then
            basename_check=$(basename "$check")
            
            # Skip if local overrides (check if basename is in LOCAL_CHECKS string)
            if echo "$LOCAL_CHECKS" | grep -q " $basename_check "; then
                echo "    ⏭️  $basename_check (local override)"
                continue
            fi
            
            # Run check
            CHECK_OUTPUT=$(bash "$check" 2>&1)
            if [ $? -eq 0 ]; then
                echo "    ✅ $basename_check"
                # Capture roadmap-tasks output if all tasks done
                if [ "$basename_check" = "roadmap-tasks.sh" ] && echo "$CHECK_OUTPUT" | grep -q "🚦 Ready for merge-to-main"; then
                    ROADMAP_STATUS="$CHECK_OUTPUT"
                fi
            else
                echo "    ❌ $basename_check (failed)"
                CHECKS_PASS=false
            fi
            CHECKS_RUN=$((CHECKS_RUN + 1))
        fi
    done
else
    echo "  ⚠️  No global checks found ($GLOBAL_CHECKS_DIR)"
fi

echo ""

# Run local checks (always run, overrides global if same name)
if [ -d "$LOCAL_CHECKS_DIR" ]; then
    echo "  📋 Local checks:"
    for check in "$LOCAL_CHECKS_DIR"/*.sh; do
        if [ -f "$check" ]; then
            basename_check=$(basename "$check")
            
            # Run check
            if bash "$check" >/dev/null 2>&1; then
                echo "    ✅ $basename_check"
            else
                echo "    ❌ $basename_check (failed)"
                CHECKS_PASS=false
            fi
            CHECKS_RUN=$((CHECKS_RUN + 1))
        fi
    done
else
    echo "  ℹ️  No local checks found ($LOCAL_CHECKS_DIR)"
fi

echo ""
echo "  📊 Checks executed: $CHECKS_RUN"

# ============================================================================
# STEP 2: Read interpretive checks (.md files in checks/)
# ============================================================================

echo ""
echo "📋 Reading interpretive checks/ (.md files - AI enforces)..."
echo ""

INTERPRETIVE_READ=0

# Collect local interpretive basenames (for override detection)
LOCAL_INTERPRETIVE=""
if [ -d "$LOCAL_CHECKS_DIR" ]; then
    for check in "$LOCAL_CHECKS_DIR"/*.md; do
        if [ -f "$check" ]; then
            basename_check=$(basename "$check")
            LOCAL_INTERPRETIVE="$LOCAL_INTERPRETIVE $basename_check "
        fi
    done
fi

# Read global interpretive checks (skip if local has same name)
if [ -d "$GLOBAL_CHECKS_DIR" ]; then
    echo "  📋 Global interpretive:"
    for check in "$GLOBAL_CHECKS_DIR"/*.md; do
        if [ -f "$check" ]; then
            basename_check=$(basename "$check")
            
            # Skip README.md
            if [ "$basename_check" = "README.md" ]; then
                continue
            fi
            
            # Skip if local overrides
            if echo "$LOCAL_INTERPRETIVE" | grep -q " $basename_check "; then
                echo "    ⏭️  $basename_check (local override)"
                continue
            fi
            
            echo "    ✅ $basename_check (read)"
            INTERPRETIVE_READ=$((INTERPRETIVE_READ + 1))
        fi
    done
fi

echo ""

# Read local interpretive checks (always read, overrides global if same name)
if [ -d "$LOCAL_CHECKS_DIR" ]; then
    echo "  📋 Local interpretive:"
    HAS_LOCAL_INTERPRETIVE=false
    for check in "$LOCAL_CHECKS_DIR"/*.md; do
        if [ -f "$check" ] && [ "$(basename "$check")" != "README.md" ]; then
            basename_check=$(basename "$check")
            echo "    ✅ $basename_check (read)"
            INTERPRETIVE_READ=$((INTERPRETIVE_READ + 1))
            HAS_LOCAL_INTERPRETIVE=true
        fi
    done
    if [ "$HAS_LOCAL_INTERPRETIVE" = false ]; then
        echo "  ℹ️  No local interpretive checks found"
    fi
else
    echo "  ℹ️  No local interpretive checks found"
fi

echo ""
echo "  📊 Interpretive checks read: $INTERPRETIVE_READ"

# ============================================================================
# STEP 3: Integrated report
# ============================================================================

echo ""
echo "📊 Integrated Enforcement Report:"
echo ""

# Show current branch + epic info
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

if [[ "$CURRENT_BRANCH" == "main" ]]; then
    echo "🌿 Branch: main (read-only)"
elif [[ "$CURRENT_BRANCH" =~ ^v([0-9]+\.[0-9]+\.[0-9]+) ]]; then
    VERSION="${BASH_REMATCH[1]}"
    # Extract epic title from ROADMAP
    if [[ -f backstage/ROADMAP.md ]]; then
        EPIC_TITLE=$(awk "/^## v$VERSION\$/,/^###/" backstage/ROADMAP.md | grep "^###" | head -1 | sed 's/^### //')
        if [[ -n "$EPIC_TITLE" ]]; then
            echo "🌿 Epic: v$VERSION - $EPIC_TITLE"
        else
            echo "🌿 Branch: $CURRENT_BRANCH"
        fi
    else
        echo "🌿 Branch: $CURRENT_BRANCH"
    fi
else
    echo "🌿 Branch: $CURRENT_BRANCH"
fi

echo ""

echo "🔍 Checks (deterministic):"
if [ "$CHECKS_PASS" = true ]; then
    echo "  ✅ All checks passed ($CHECKS_RUN executed)"
else
    echo "  ❌ Some checks failed (see above)"
fi

echo ""
echo "📋 Interpretive checks:"
echo "  ✅ All interpretive checks read ($INTERPRETIVE_READ total)"
echo "  🤖 AI will enforce contextual rules"

# Show roadmap status if epic complete
if [ -n "$ROADMAP_STATUS" ]; then
    echo ""
    echo "$ROADMAP_STATUS"
fi

echo ""

# ============================================================================
# STEP 4: Exit code (mode-aware)
# ============================================================================

if [ "$CHECKS_PASS" = true ]; then
    echo "✅ Enforcement complete (all deterministic checks passed)"
    exit 0
else
    if [ "$MODE" = "start" ]; then
        echo "🛑 Enforcement failed (blocking commit - fix issues above)"
        exit 1
    else
        echo "⚠️  Enforcement soft fail (add issues to ROADMAP)"
        exit 0
    fi
fi
