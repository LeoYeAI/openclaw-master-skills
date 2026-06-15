#!/bin/bash
# Team Dispatch uninstall (safe by default)
# Usage:
#   bash <SKILL_DIR>/scripts/uninstall.sh            # safe uninstall
#   bash <SKILL_DIR>/scripts/uninstall.sh --purge   # also delete managed agentDirs/config
#   bash <SKILL_DIR>/scripts/uninstall.sh --dry-run

set -euo pipefail

DRY_RUN=0
PURGE=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --purge) PURGE=1 ;;
    *) echo "Unknown arg: $arg"; exit 2 ;;
  esac
done

run() {
  if [ "$DRY_RUN" = "1" ]; then
    printf '[dry-run]'; printf ' %q' "$@"; printf '\n'
  else
    "$@"
  fi
}

safe_rm_dir() {
  local p="$1"
  if [ ! -e "$p" ]; then return 0; fi
  if [ "$DRY_RUN" = "1" ]; then
    printf '[dry-run]'; printf ' %q' "trash" "$p"; printf ' (fallback: rm -rf)\n'
    return 0
  fi
  if command -v trash >/dev/null 2>&1; then
    trash "$p"
  else
    rm -rf "$p"
  fi
}

say() { echo "$@"; }

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OPENCLAW_JSON="$HOME/.openclaw/openclaw.json"
BACKUP_ROOT="$HOME/.openclaw/backups/team-dispatch"
LATEST_FILE="$BACKUP_ROOT/latest"

say "🧹 Team Dispatch uninstall"

# Remove skill symlink (only if it points to this skill dir)
LINK="$HOME/.openclaw/skills/team-dispatch"
if [ -L "$LINK" ]; then
  TARGET="$(readlink "$LINK")"
  if [ "$TARGET" = "$SKILL_DIR" ]; then
    run rm "$LINK"
    say "✅ removed symlink: $LINK"
  else
    say "⏭️  symlink exists but points elsewhere: $LINK -> $TARGET (skip)"
  fi
else
  say "⏭️  no symlink: $LINK"
fi

# Safe mode does NOT edit openclaw.json (because we can't know user's other changes).
# We only provide restore via restore.sh from backups.

if [ "$PURGE" != "1" ]; then
  say ""
  say "✅ safe uninstall done (no purge)."
  say "If you want to rollback config, run: bash $SKILL_DIR/scripts/restore.sh --latest"
  exit 0
fi

say ""
say "⚠️  purge mode: will delete ONLY directories marked as managed-by=team-dispatch"

AGENTS=(coder product tester research trader writer)
for a in "${AGENTS[@]}"; do
  AD="$HOME/.openclaw/agents/$a"
  if [ -d "$AD" ] && [ -f "$AD/.team-dispatch-managed" ]; then
    safe_rm_dir "$AD"
    say "🗑️  purged agentDir: $AD"
  else
    say "⏭️  skip agentDir: $AD (missing or not managed)"
  fi
done

CFG="$HOME/.openclaw/configs/team-dispatch.json"
if [ -f "$CFG" ] && [ -f "$HOME/.openclaw/configs/.team-dispatch-managed" ]; then
  run rm -f "$CFG"
  say "🗑️  removed config: $CFG"
else
  say "⏭️  skip config: $CFG (missing or not managed)"
fi

say ""
say "✅ purge uninstall done."
say "Backups (if any): $BACKUP_ROOT"
