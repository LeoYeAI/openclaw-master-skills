#!/bin/bash
# Query a database and list the titles of the results

if [ -z "$2" ]; then
  echo "Usage: $0 <workspace_id> <database_id>"
  exit 1
fi

WORKSPACE_ID=$1
DATABASE_ID=$2

vibe-notion database query "$DATABASE_ID" --workspace-id "$WORKSPACE_ID" --pretty
