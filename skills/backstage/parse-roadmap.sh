#!/bin/bash
# parse-roadmap.sh - Extract epic metadata from ROADMAP.md
# Output: version|status_emoji|name (one per line)

ROADMAP="${1:-backstage/ROADMAP.md}"

if [ ! -f "$ROADMAP" ]; then
  echo "Error: ROADMAP not found at $ROADMAP" >&2
  exit 1
fi

# Process ROADMAP line by line
# New format: ## vX.Y.Z (separate line) + ### Epic Title (next line)
awk '
/^## v[0-9]+\.[0-9]+\.[0-9]+$/ {
  # Extract version
  match($0, /v[0-9]+\.[0-9]+\.[0-9]+/)
  version = substr($0, RSTART, RLENGTH)
  in_epic = 1
  next
}

in_epic && /^### / {
  # Extract epic title (everything after "### ")
  name = substr($0, 5)
  # Default status (backlog)
  status = "📋"
  print version "|" status "|" name
  in_epic = 0
  next
}
' "$ROADMAP"
