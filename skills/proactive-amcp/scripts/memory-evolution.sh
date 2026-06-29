#!/bin/bash
# memory-evolution.sh - Zettelkasten-style dynamic entity linking
# Usage: ./memory-evolution.sh [--entity-id ID] [--graph PATH] [--dry-run]
#
# When a new entity is added to graph.jsonl, finds semantically similar
# entities and adds bidirectional 'related_to' relations.
# Logs evolution chain to evolution.jsonl.

set -euo pipefail

command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AMCP_CLI="${AMCP_CLI:-$(command -v amcp 2>/dev/null || echo "$HOME/bin/amcp")}"
IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"

# Resolve workspace dynamically
get_workspace() {
  local ws
  ws=$(python3 -c "import json,os; d=json.load(open(os.path.expanduser('~/.openclaw/openclaw.json'))); print(d.get('agents',{}).get('defaults',{}).get('workspace','~/.openclaw/workspace'))" 2>/dev/null || echo "$HOME/.openclaw/workspace")
  echo "${ws/#\~/$HOME}"
}

CONTENT_DIR="${CONTENT_DIR:-$(get_workspace)}"
GRAPH_FILE="${GRAPH_FILE:-$CONTENT_DIR/memory/ontology/graph.jsonl}"
EVOLUTION_LOG="${EVOLUTION_LOG:-$HOME/.amcp/memory/evolution.jsonl}"
EVOLUTION_THRESHOLD="${EVOLUTION_THRESHOLD:-0.75}"
EVOLUTION_MAX_RELATIONS="${EVOLUTION_MAX_RELATIONS:-3}"

# ============================================================
# Parse arguments
# ============================================================
DRY_RUN=false
TARGET_ENTITY_ID=""
PROCESS_ALL_NEW=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --entity-id) TARGET_ENTITY_ID="$2"; shift 2 ;;
    --graph) GRAPH_FILE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --all-new) PROCESS_ALL_NEW=true; shift ;;
    --threshold) EVOLUTION_THRESHOLD="$2"; shift 2 ;;
    --max-relations) EVOLUTION_MAX_RELATIONS="$2"; shift 2 ;;
    -h|--help)
      cat <<EOF
memory-evolution.sh — Zettelkasten-style entity linking

Usage: $(basename "$0") [options]

Options:
  --entity-id ID       Process a specific entity
  --all-new            Process all entities not yet evolved
  --graph PATH         Path to graph.jsonl (default: \$CONTENT_DIR/memory/ontology/graph.jsonl)
  --threshold FLOAT    Similarity threshold (default: $EVOLUTION_THRESHOLD)
  --max-relations N    Max relations per entity (default: $EVOLUTION_MAX_RELATIONS)
  --dry-run            Show what would be linked without modifying files
  -h, --help           Show this help

Environment:
  EVOLUTION_THRESHOLD      Similarity threshold (default: 0.75)
  EVOLUTION_MAX_RELATIONS  Max relations per entity (default: 3)
EOF
      exit 0
      ;;
    *) shift ;;
  esac
done

# ============================================================
# Validate identity
# ============================================================
validate_identity() {
  if [ ! -f "$IDENTITY_PATH" ]; then
    echo "FATAL: Invalid AMCP identity — run amcp identity create" >&2
    exit 1
  fi
  if ! "$AMCP_CLI" identity validate --identity "$IDENTITY_PATH" 2>/dev/null; then
    echo "FATAL: Invalid AMCP identity" >&2
    exit 1
  fi
}

validate_identity

# ============================================================
# Check graph exists
# ============================================================
if [ ! -f "$GRAPH_FILE" ]; then
  echo "No graph.jsonl found at $GRAPH_FILE — nothing to evolve"
  exit 0
fi

# Ensure evolution log directory exists
mkdir -p "$(dirname "$EVOLUTION_LOG")"

# ============================================================
# Find entities to process
# ============================================================
get_entity_ids() {
  if [ -n "$TARGET_ENTITY_ID" ]; then
    echo "$TARGET_ENTITY_ID"
    return
  fi

  if [ "$PROCESS_ALL_NEW" = true ]; then
    # Find entities not yet in evolution log
    python3 -c "
import json, os

graph_path = '$GRAPH_FILE'
evo_path = '$EVOLUTION_LOG'

# Get all entity IDs from graph
entity_ids = set()
with open(graph_path) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            r = json.loads(line)
            if r.get('type') != 'relation' and r.get('id'):
                entity_ids.add(r['id'])
        except json.JSONDecodeError:
            continue

# Get already-evolved IDs
evolved = set()
if os.path.isfile(evo_path):
    with open(evo_path) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                r = json.loads(line)
                if r.get('trigger_entity_id'):
                    evolved.add(r['trigger_entity_id'])
            except json.JSONDecodeError:
                continue

# Output new ones
for eid in sorted(entity_ids - evolved):
    print(eid)
"
    return
  fi

  echo "ERROR: Specify --entity-id ID or --all-new" >&2
  exit 1
}

ENTITY_IDS=$(get_entity_ids)

if [ -z "$ENTITY_IDS" ]; then
  echo "No new entities to evolve"
  exit 0
fi

ENTITY_COUNT=$(echo "$ENTITY_IDS" | wc -l | tr -d ' ')
echo "=== Memory Evolution Engine ==="
echo "Graph: $GRAPH_FILE"
echo "Entities to process: $ENTITY_COUNT"
echo "Threshold: $EVOLUTION_THRESHOLD"
echo "Max relations: $EVOLUTION_MAX_RELATIONS"
echo ""

# ============================================================
# Process each entity
# ============================================================
RELATIONS_ADDED=0
ENTITIES_PROCESSED=0

while IFS= read -r entity_id; do
  [ -z "$entity_id" ] && continue
  ENTITIES_PROCESSED=$((ENTITIES_PROCESSED + 1))

  echo "[$ENTITIES_PROCESSED/$ENTITY_COUNT] Entity: $entity_id"

  # Compute similarity
  SIMILAR=$(python3 "$SCRIPT_DIR/compute-entity-similarity.py" \
    --graph "$GRAPH_FILE" \
    --entity-id "$entity_id" \
    --threshold "$EVOLUTION_THRESHOLD" \
    --max-relations "$EVOLUTION_MAX_RELATIONS" 2>/dev/null || echo '[]')

  # Check if any results
  MATCH_COUNT=$(echo "$SIMILAR" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo '0')

  if [ "$MATCH_COUNT" = "0" ]; then
    echo "  No similar entities above threshold"
    continue
  fi

  echo "  Found $MATCH_COUNT similar entit(y|ies)"

  # Process each match
  echo "$SIMILAR" | python3 -c "
import json, sys, os
from datetime import datetime, timezone

matches = json.load(sys.stdin)
graph_path = '$GRAPH_FILE'
evo_path = '$EVOLUTION_LOG'
entity_id = '$entity_id'
dry_run = '$DRY_RUN' == 'true'

for m in matches:
    related_id = m['entity_id']
    score = m['similarity_score']
    reasoning = m['reasoning']

    print(f'  -> {related_id} (score={score:.4f})')

    if dry_run:
        print('     [DRY RUN] Would add relation')
        continue

    now = datetime.now(timezone.utc).isoformat()

    # Add bidirectional relation to graph.jsonl
    rel_forward = {
        'type': 'relation',
        'from_id': entity_id,
        'relation_type': 'related_to',
        'to_id': related_id,
        'properties': {
            'similarity_score': score,
            'source': 'evolution_engine',
            'created': now
        }
    }
    rel_backward = {
        'type': 'relation',
        'from_id': related_id,
        'relation_type': 'related_to',
        'to_id': entity_id,
        'properties': {
            'similarity_score': score,
            'source': 'evolution_engine',
            'created': now
        }
    }

    with open(graph_path, 'a') as f:
        f.write(json.dumps(rel_forward) + '\n')
        f.write(json.dumps(rel_backward) + '\n')

    # Log to evolution.jsonl
    evo_entry = {
        'timestamp': now,
        'trigger_entity_id': entity_id,
        'related_entity_id': related_id,
        'similarity_score': score,
        'relation_type': 'related_to',
        'reasoning': reasoning
    }
    os.makedirs(os.path.dirname(evo_path), exist_ok=True)
    with open(evo_path, 'a') as f:
        f.write(json.dumps(evo_entry) + '\n')

print(len(matches))
" 2>/dev/null || echo '0'

  BATCH_COUNT=$(echo "$SIMILAR" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo '0')
  RELATIONS_ADDED=$((RELATIONS_ADDED + BATCH_COUNT))

done <<< "$ENTITY_IDS"

# ============================================================
# Summary
# ============================================================
echo ""
echo "=== Evolution Summary ==="
echo "  Entities processed: $ENTITIES_PROCESSED"
echo "  Relations added:    $RELATIONS_ADDED"
echo "  Evolution log:      $EVOLUTION_LOG"
if [ "$DRY_RUN" = true ]; then
  echo "  (DRY RUN — no changes made)"
fi
