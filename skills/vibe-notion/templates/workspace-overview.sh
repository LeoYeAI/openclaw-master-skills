#!/bin/bash
# Get an overview of the workspace

if [ -z "$1" ]; then
  echo "Usage: $0 <workspace_id>"
  echo "Run 'vibe-notion workspace list' to find your workspace ID."
  exit 1
fi

WORKSPACE_ID=$1

echo "--- Current User Info ---"
vibe-notion auth status --pretty

echo -e "\n--- Accessible Databases ---"
vibe-notion database list --workspace-id "$WORKSPACE_ID" --pretty

echo -e "\n--- Recent Pages (Search) ---"
vibe-notion search "" --workspace-id "$WORKSPACE_ID" --sort lastEdited --limit 5 --pretty
