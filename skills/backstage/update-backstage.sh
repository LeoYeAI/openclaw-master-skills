#!/bin/bash
# update-backstage.sh - Sync local checks/global with upstream repo
#
# Usage: update-backstage.sh [project-path]
# Triggers: "update backstage" (from AI)

set -e

# Config
UPSTREAM="https://github.com/nonlinear/backstage"
PROJECT_PATH="${1:-.}"

# Find backstage folder
BACKSTAGE_DIR=$(find "$PROJECT_PATH" -type d -name "backstage" -path "*/backstage" | head -1)

if [ -z "$BACKSTAGE_DIR" ]; then
  echo "❌ No backstage/ folder found in $PROJECT_PATH"
  echo "   Are you in a project using backstage protocol?"
  exit 1
fi

echo "📂 Backstage folder: $BACKSTAGE_DIR"
echo ""

# Check if symlinked (admin mode)
if [ -L "$BACKSTAGE_DIR/checks/global" ]; then
  echo "✅ checks/global/ is symlinked to upstream"
  echo "   Auto-updates enabled (no action needed)"
  exit 0
fi

# Confirm upstream
echo "Upstream: $UPSTREAM"
read -p "Is this correct? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

# Fetch latest from upstream
echo ""
echo "🔄 Fetching latest from upstream..."
TMP_DIR=$(mktemp -d)
git clone --quiet --depth 1 "$UPSTREAM" "$TMP_DIR/backstage" 2>/dev/null || {
  echo "❌ Failed to clone upstream (offline or repo moved?)"
  rm -rf "$TMP_DIR"
  exit 1
}

# Compare local vs upstream
echo "📊 Comparing local vs upstream..."
echo ""

NEW_FILES=()
CHANGED_FILES=()
REMOVED_FILES=()

# Find new/changed files
for file in "$TMP_DIR/backstage/backstage/checks/global"/*; do
  filename=$(basename "$file")
  local_file="$BACKSTAGE_DIR/checks/global/$filename"
  
  if [ ! -f "$local_file" ]; then
    NEW_FILES+=("$filename")
  elif ! diff -q "$local_file" "$file" >/dev/null 2>&1; then
    CHANGED_FILES+=("$filename")
  fi
done

# Find removed files (upstream deleted)
for file in "$BACKSTAGE_DIR/checks/global"/*; do
  filename=$(basename "$file")
  upstream_file="$TMP_DIR/backstage/backstage/checks/global/$filename"
  
  if [ ! -f "$upstream_file" ]; then
    REMOVED_FILES+=("$filename")
  fi
done

# Check if up to date
if [ ${#NEW_FILES[@]} -eq 0 ] && [ ${#CHANGED_FILES[@]} -eq 0 ] && [ ${#REMOVED_FILES[@]} -eq 0 ]; then
  echo "✅ Already up to date (no changes)"
  rm -rf "$TMP_DIR"
  exit 0
fi

# Generate mini changelog
echo "📦 Backstage Updates Available:"
echo ""

if [ ${#NEW_FILES[@]} -gt 0 ]; then
  echo "NEW files (${#NEW_FILES[@]}):"
  for file in "${NEW_FILES[@]}"; do
    # Extract DESCRIPTION from file (if exists)
    desc=$(grep -m1 "^# DESCRIPTION:" "$TMP_DIR/backstage/backstage/checks/global/$file" 2>/dev/null | cut -d':' -f2- | xargs || echo "")
    if [ -n "$desc" ]; then
      echo "  - $file ($desc)"
    else
      echo "  - $file"
    fi
  done
  echo ""
fi

if [ ${#CHANGED_FILES[@]} -gt 0 ]; then
  echo "CHANGED files (${#CHANGED_FILES[@]}):"
  for file in "${CHANGED_FILES[@]}"; do
    echo "  - $file"
  done
  echo ""
fi

if [ ${#REMOVED_FILES[@]} -gt 0 ]; then
  echo "REMOVED from upstream (${#REMOVED_FILES[@]}):"
  for file in "${REMOVED_FILES[@]}"; do
    echo "  - $file (will be kept locally unless you delete)"
  done
  echo ""
fi

# Summarize what you gain
echo "WHAT YOU GAIN:"
echo "  Latest checks, bug fixes, new workflows from backstage protocol."
echo ""

# Prompt user
read -p "Apply these updates? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  rm -rf "$TMP_DIR"
  exit 0
fi

# Update
echo ""
echo "🔄 Updating checks/global/..."
rsync -av --delete "$TMP_DIR/backstage/backstage/checks/global/" "$BACKSTAGE_DIR/checks/global/" >/dev/null

# Cleanup
rm -rf "$TMP_DIR"

# Report
echo ""
echo "🎉 Backstage updated!"
echo ""
echo "Files changed: $((${#NEW_FILES[@]} + ${#CHANGED_FILES[@]}))"
if [ ${#NEW_FILES[@]} -gt 0 ]; then
  echo "  - Added: ${NEW_FILES[*]}"
fi
if [ ${#CHANGED_FILES[@]} -gt 0 ]; then
  echo "  - Modified: ${CHANGED_FILES[*]}"
fi
echo ""
echo "Next: Run 'backstage start' to test new checks."
