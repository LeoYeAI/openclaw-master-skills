#!/bin/bash
# Create a page and append a heading and paragraph

if [ -z "$3" ]; then
  echo "Usage: $0 <workspace_id> <parent_id> <title>"
  exit 1
fi

WORKSPACE_ID=$1
PARENT_ID=$2
TITLE=$3

echo "Creating page: $TITLE"
# Create page and extract ID
# Note: Requires 'jq' to be installed for ID extraction
RESPONSE=$(vibe-notion page create --workspace-id "$WORKSPACE_ID" --parent "$PARENT_ID" --title "$TITLE")
PAGE_ID=$(echo $RESPONSE | jq -r '.id')

if [ "$PAGE_ID" == "null" ] || [ -z "$PAGE_ID" ]; then
  echo "Failed to create page"
  echo $RESPONSE
  exit 1
fi

echo "Page created with ID: $PAGE_ID"

# Append content
echo "Appending content blocks..."
vibe-notion block append "$PAGE_ID" --workspace-id "$WORKSPACE_ID" --content '[
  {"type": "sub_header", "properties": {"title": [["Welcome to your new page"]]}},
  {"type": "text", "properties": {"title": [["This page was created automatically using the Vibe Notion CLI."]]}}
]' --pretty
