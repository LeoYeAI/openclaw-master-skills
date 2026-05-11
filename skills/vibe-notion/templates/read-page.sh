#!/bin/bash
# Read a page and its direct children

if [ -z "$2" ]; then
  echo "Usage: $0 <workspace_id> <page_id>"
  exit 1
fi

WORKSPACE_ID=$1
PAGE_ID=$2

echo "--- Page Metadata ---"
vibe-notion page get "$PAGE_ID" --workspace-id "$WORKSPACE_ID" --pretty

echo -e "\n--- Page Content (Direct Children) ---"
vibe-notion block children "$PAGE_ID" --workspace-id "$WORKSPACE_ID" --pretty
