#!/bin/bash
set -e

# ============================================================
# ⚠️  SECURITY NOTICE — READ BEFORE RUNNING
# ============================================================
# This script patches OpenClaw source files using sed and
# copies files into the OpenClaw codebase. These are HIGH-IMPACT
# operations that modify your installation.
#
# You MUST pass either --dry-run (preview) or --apply (real changes).
# Running with no arguments will EXIT with a usage error.
#
# ALWAYS start with --dry-run:
#   ./integrate-openclaw.sh --dry-run
#
# Only after reviewing the output, apply for real:
#   ./integrate-openclaw.sh --apply
#
# Strongly recommended before applying:
#   1. Review every sed command in this script manually
#   2. Have a git commit or backup of your OpenClaw source
#   3. Test on a dev copy first
#
# Automatic backups are created for each patched file (*.backup.TIMESTAMP)
# ============================================================

# ── Hard gate: require an explicit flag ──────────────────────────────────────
if [ $# -eq 0 ]; then
  echo ""
  echo "ERROR: No flag provided. This script requires an explicit intent flag."
  echo ""
  echo "  --dry-run   Preview all changes without touching any files (safe)"
  echo "  --apply     Apply changes for real (destructive — back up first!)"
  echo ""
  echo "Example (always start with dry-run):"
  echo "  ./integrate-openclaw.sh --dry-run"
  echo "  ./integrate-openclaw.sh --apply"
  echo ""
  exit 1
fi

DRY_RUN=true
EXPLICIT_FLAG=false
for arg in "$@"; do
  case $arg in
    --apply)    DRY_RUN=false; EXPLICIT_FLAG=true ;;
    --dry-run)  DRY_RUN=true;  EXPLICIT_FLAG=true ;;
  esac
done

if [ "$EXPLICIT_FLAG" = false ]; then
  echo "ERROR: Unrecognized flag(s). Use --dry-run or --apply."
  exit 1
fi

# Helper: run or simulate a command
run_cmd() {
  if [ "$DRY_RUN" = true ]; then
    echo "  [DRY-RUN] $*"
  else
    eval "$@"
  fi
}

# SurrealDB Memory Skill - OpenClaw Integration Installer
# This script patches OpenClaw to add the Memory UI tab and gateway handlers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
INTEGRATION_DIR="${SKILL_DIR}/openclaw-integration"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ "$DRY_RUN" = true ]; then
  echo ""
  echo -e "${YELLOW}════════════════════════════════════════════════════${NC}"
  echo -e "${YELLOW}  DRY-RUN MODE — no files will be changed${NC}"
  echo -e "${YELLOW}  Pass --apply to make changes for real${NC}"
  echo -e "${YELLOW}════════════════════════════════════════════════════${NC}"
  echo ""
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       SurrealDB Memory - OpenClaw Integration Installer      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Find OpenClaw installation
if [ -n "$OPENCLAW_DIR" ]; then
    CLAWDBOT_ROOT="$OPENCLAW_DIR"
elif [ -d "$HOME/openclaw" ]; then
    CLAWDBOT_ROOT="$HOME/openclaw"
elif [ -d "/opt/openclaw" ]; then
    CLAWDBOT_ROOT="/opt/openclaw"
else
    echo -e "${RED}ERROR: Could not find OpenClaw installation.${NC}"
    echo "Set OPENCLAW_DIR environment variable or install OpenClaw first."
    exit 1
fi

echo "Found OpenClaw at: $CLAWDBOT_ROOT"
echo ""

# Check if already integrated
if [ -f "${CLAWDBOT_ROOT}/src/gateway/server-methods/memory.ts" ]; then
    echo -e "${YELLOW}Memory handlers already present.${NC}"
    read -p "Overwrite? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping handler installation."
        SKIP_HANDLERS=true
    fi
fi

# Backup function (no-op in dry-run)
backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        run_cmd "cp '$file' '${file}.backup.$(date +%Y%m%d%H%M%S)'"
    fi
}

echo "=== Step 1: Installing Gateway Handlers ==="
if [ -z "$SKIP_HANDLERS" ]; then
    # Copy memory.ts handler
    echo "  Copying memory.ts handler..."
    run_cmd "cp '${INTEGRATION_DIR}/gateway/memory.ts' '${CLAWDBOT_ROOT}/src/gateway/server-methods/memory.ts'"
    
    # Patch server-methods.ts to register handlers
    METHODS_FILE="${CLAWDBOT_ROOT}/src/gateway/server-methods.ts"
    if [ "$DRY_RUN" = true ] || ! grep -q 'memoryHandlers' "$METHODS_FILE"; then
        echo "  Patching server-methods.ts..."
        backup_file "$METHODS_FILE"
        
        run_cmd "sed -i '/import { skillsHandlers } from \".\/server-methods\/skills\.js\";/a import { memoryHandlers } from \"./server-methods/memory.js\";' '$METHODS_FILE'"
        run_cmd "sed -i '/\.\.\.skillsHandlers,/a \\  ...memoryHandlers,' '$METHODS_FILE'"
        run_cmd "sed -i '/\"chat\.history\",/a \\  \"memory.health\",\\n  \"memory.stats\",' '$METHODS_FILE'"
        
        echo -e "  ${GREEN}✓ Gateway handlers${NC}"
    else
        echo -e "  ${YELLOW}Handlers already registered${NC}"
    fi
else
    echo -e "  ${YELLOW}Skipped${NC}"
fi

echo ""
echo "=== Step 2: Installing UI Components ==="

# Check UI source exists
UI_SRC="${CLAWDBOT_ROOT}/ui/src/ui"
if [ ! -d "$UI_SRC" ]; then
    echo -e "${YELLOW}UI source not found. Skipping UI integration.${NC}"
    echo "UI will need to be installed manually or use the standalone web-ui.py"
else
    # Copy view and controller
    echo "  Copying memory view and controller..."
    run_cmd "cp '${INTEGRATION_DIR}/ui/memory-view.ts' '${UI_SRC}/views/memory.ts'"
    run_cmd "cp '${INTEGRATION_DIR}/ui/memory-controller.ts' '${UI_SRC}/controllers/memory.ts'"
    
    # Patch navigation.ts
    NAV_FILE="${UI_SRC}/navigation.ts"
    if [ "$DRY_RUN" = true ] || ! grep -q '"memory"' "$NAV_FILE"; then
        echo "  Patching navigation.ts..."
        backup_file "$NAV_FILE"
        
        run_cmd "sed -i 's/\"apikeys\"\\]}/\"apikeys\", \"memory\"\\]}/' '$NAV_FILE'"
        run_cmd "sed -i '/| \"apikeys\"/a \\  | \"memory\"' '$NAV_FILE'"
        run_cmd "sed -i '/apikeys: \"\/apikeys\",/a \\  memory: \"\/memory\",' '$NAV_FILE'"
        run_cmd "sed -i '/case \"apikeys\":/a \\    case \"memory\":\\n      return \"database\";' '$NAV_FILE'"
        run_cmd "sed -i '/case \"apikeys\":/,/return \"API Keys\";/a \\    case \"memory\":\\n      return \"Memory\";' '$NAV_FILE'"
        run_cmd "sed -i '/case \"apikeys\":/,/\"Manage API keys/a \\    case \"memory\":\\n      return \"Knowledge graph memory with confidence scoring and maintenance.\";' '$NAV_FILE'"
        
        echo -e "  ${GREEN}✓ Navigation${NC}"
    else
        echo -e "  ${YELLOW}Navigation already has memory tab${NC}"
    fi
    
    # Add database icon if missing
    ICONS_FILE="${UI_SRC}/icons.ts"
    if [ "$DRY_RUN" = true ] || ! grep -q 'database:' "$ICONS_FILE"; then
        echo "  Adding database icon..."
        backup_file "$ICONS_FILE"
        run_cmd "sed -i '/key: html\`/a \\  database: html\`<svg viewBox=\"0 0 24 24\"><ellipse cx=\"12\" cy=\"5\" rx=\"9\" ry=\"3\"/><path d=\"M3 5V19A9 3 0 0 0 21 19V5\"/><path d=\"M3 12A9 3 0 0 0 21 12\"/></svg>\`,' '$ICONS_FILE'"
        echo -e "  ${GREEN}✓ Database icon${NC}"
    fi
    
    # Patch app.ts for state
    APP_FILE="${UI_SRC}/app.ts"
    if [ "$DRY_RUN" = true ] || ! grep -q 'memoryLoading' "$APP_FILE"; then
        echo "  Patching app.ts for memory state..."
        backup_file "$APP_FILE"
        run_cmd "sed -i '/@state() skillMessages/a \\  \\/\\/ Memory (SurrealDB knowledge graph)\\n  @state() memoryLoading = false;\\n  @state() memoryHealth: unknown = null;\\n  @state() memoryStats: unknown = null;\\n  @state() memoryError: string | null = null;\\n  @state() memoryMaintenanceLog: string | null = null;\\n  @state() memoryInstallLog: string | null = null;\\n  @state() memoryBusyAction: string | null = null;' '$APP_FILE'"
        echo -e "  ${GREEN}✓ App state${NC}"
    fi
    
    # Patch app-render.ts
    RENDER_FILE="${UI_SRC}/app-render.ts"
    if [ "$DRY_RUN" = true ] || ! grep -q 'renderMemory' "$RENDER_FILE"; then
        echo "  Patching app-render.ts..."
        backup_file "$RENDER_FILE"
        echo -e "  ${YELLOW}Note: You may need to manually add imports to app-render.ts${NC}"
        echo "  Add: import { renderMemory } from './views/memory';"
    fi
    
    echo ""
    echo -e "${GREEN}✓ UI components${NC}"
fi

echo ""
echo "=== Step 3: Rebuilding OpenClaw ==="
echo "Run these commands to complete installation:"
echo ""
echo "  cd $CLAWDBOT_ROOT"
echo "  npm run build"
echo "  npm run ui:build"
echo "  openclaw gateway restart"
echo ""

echo "=== Step 4: Start SurrealDB ==="
echo "Run these commands to start the database:"
echo ""
echo "  cd ${SKILL_DIR}/scripts"
echo "  ./install.sh      # Install SurrealDB if needed"
echo "  ./init-db.sh      # Initialize schema"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Installation Complete!                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  After rebuilding, you'll see a 'Memory' tab in the UI.     ║"
echo "║  Use the Auto-Repair button for one-click database setup.    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
