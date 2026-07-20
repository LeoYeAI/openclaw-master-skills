#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
BACKUP_DIR="$HOME/.openclaw/backups"
TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
ARCHIVE="$BACKUP_DIR/training-$TIMESTAMP.tar.gz"

if [ ! -d "$WORKSPACE" ]; then
  echo "ERROR: Workspace does not exist: $WORKSPACE"
  exit 1
fi

mkdir -p "$BACKUP_DIR"

# Files to back up
TARGETS=()
for f in SOUL.md AGENTS.md TOOLS.md IDENTITY.md USER.md MEMORY.md BOOTSTRAP.md HEARTBEAT.md; do
  if [ -f "$WORKSPACE/$f" ]; then
    TARGETS+=("$f")
  fi
done

# Add memory directory
if [ -d "$WORKSPACE/memory" ]; then
  TARGETS+=("memory")
fi

# Add skills directory
if [ -d "$WORKSPACE/skills" ]; then
  TARGETS+=("skills")
fi

if [ ${#TARGETS[@]} -eq 0 ]; then
  echo "ERROR: No training files found to export."
  exit 1
fi

cd "$WORKSPACE"
tar -czf "$ARCHIVE" "${TARGETS[@]}"

SIZE=$(du -h "$ARCHIVE" | cut -f1)

echo "=== Export Complete ==="
echo "  Archive: $ARCHIVE"
echo "  Size: $SIZE"
echo "  Files:"
for t in "${TARGETS[@]}"; do
  echo "    - $t"
done
echo ""
echo "Restore with: cd ~/.openclaw/workspace && tar -xzf $ARCHIVE"
