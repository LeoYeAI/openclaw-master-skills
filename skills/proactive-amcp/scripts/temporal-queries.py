#!/usr/bin/env python3
"""temporal-queries.py - Cross-checkpoint entity history queries.

3-level temporal storage:
  Level 1: Current graph.jsonl (live entities)
  Level 2: Checkpoint snapshots in ~/.amcp/checkpoints/
  Level 3: Temporal index at ~/.amcp/memory/temporal-index.jsonl

Usage:
  temporal-queries.py history <entity_id>
  temporal-queries.py query <entity_id> --start YYYY-MM-DD --end YYYY-MM-DD
  temporal-queries.py build-index --graph <path> --cid <checkpoint_cid>

Environment:
  TEMPORAL_INDEX_PATH   Override temporal index location
  CONTENT_DIR           Override workspace path
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone

def _get_workspace():
    try:
        with open(os.path.expanduser("~/.openclaw/openclaw.json")) as f:
            return os.path.expanduser(json.load(f).get("agents",{}).get("defaults",{}).get("workspace","~/.openclaw/workspace"))
    except (IOError, json.JSONDecodeError):
        return os.path.expanduser("~/.openclaw/workspace")

CONTENT_DIR = os.environ.get("CONTENT_DIR", _get_workspace())
TEMPORAL_INDEX_PATH = os.environ.get("TEMPORAL_INDEX_PATH", os.path.expanduser("~/.amcp/memory/temporal-index.jsonl"))
GRAPH_PATH = os.path.join(CONTENT_DIR, "memory", "ontology", "graph.jsonl")

# ============================================================
# Level 1: Read current graph.jsonl
# ============================================================

def read_graph_entities(graph_path):
    """Read all non-relation entities from graph.jsonl."""
    entities = {}
    if not os.path.isfile(graph_path):
        return entities
    with open(graph_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("type") == "relation":
                continue
            eid = record.get("id")
            if eid:
                entities[eid] = record
    return entities

# ============================================================
# Level 3: Temporal index operations
# ============================================================

def compute_version_hash(entity):
    """Deterministic hash of entity properties for change detection."""
    serialized = json.dumps(entity, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]

def build_index(graph_path, checkpoint_cid, timestamp=None):
    """Extract entities from graph.jsonl and append to temporal index."""
    if not os.path.isfile(graph_path):
        print(f"No graph at {graph_path}")
        return 0

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()

    entities = read_graph_entities(graph_path)
    if not entities:
        print("No entities in graph")
        return 0

    # Load existing index to check for unchanged entities
    existing = {}
    if os.path.isfile(TEMPORAL_INDEX_PATH):
        with open(TEMPORAL_INDEX_PATH) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    eid = r.get("entity_id", "")
                    if eid:
                        existing[eid] = r.get("version_hash", "")
                except json.JSONDecodeError:
                    continue

    os.makedirs(os.path.dirname(TEMPORAL_INDEX_PATH), exist_ok=True)
    added = 0
    with open(TEMPORAL_INDEX_PATH, "a") as f:
        for eid, entity in entities.items():
            vh = compute_version_hash(entity)
            # Skip if entity unchanged since last index entry
            if existing.get(eid) == vh:
                continue
            # Build compact snapshot
            snapshot = {}
            for k in ("name", "type", "description", "status", "labels"):
                if k in entity:
                    snapshot[k] = entity[k]
            props = entity.get("properties", {})
            if props:
                snapshot["properties"] = props

            entry = {
                "entity_id": eid,
                "checkpoint_cid": checkpoint_cid,
                "timestamp": timestamp,
                "version_hash": vh,
                "properties_snapshot": snapshot,
            }
            f.write(json.dumps(entry) + "\n")
            added += 1

    print(f"Indexed {added} entities (skipped {len(entities) - added} unchanged)")
    return added

# ============================================================
# Query functions
# ============================================================

def load_temporal_index(entity_id=None):
    """Load temporal index entries, optionally filtered by entity_id."""
    entries = []
    if not os.path.isfile(TEMPORAL_INDEX_PATH):
        return entries
    with open(TEMPORAL_INDEX_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entity_id and r.get("entity_id") != entity_id:
                continue
            entries.append(r)
    return entries

def get_memory_history(entity_id):
    """Full evolution timeline for an entity across all checkpoints."""
    # Level 3: temporal index
    indexed = load_temporal_index(entity_id)

    # Level 1: current graph (if entity exists and differs from last indexed)
    current = read_graph_entities(GRAPH_PATH).get(entity_id)
    if current:
        current_vh = compute_version_hash(current)
        last_vh = indexed[-1]["version_hash"] if indexed else ""
        if current_vh != last_vh:
            indexed.append({
                "entity_id": entity_id,
                "checkpoint_cid": "current",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version_hash": current_vh,
                "properties_snapshot": current,
            })

    # Sort by timestamp
    indexed.sort(key=lambda x: x.get("timestamp", ""))
    return indexed

def query_by_time_range(entity_id, start_date, end_date):
    """Query entity versions within a time range."""
    history = get_memory_history(entity_id)
    results = []
    for entry in history:
        ts = entry.get("timestamp", "")
        # Compare date portion
        entry_date = ts[:10] if len(ts) >= 10 else ""
        if start_date and entry_date < start_date:
            continue
        if end_date and entry_date > end_date:
            continue
        results.append(entry)
    return results

# ============================================================
# CLI
# ============================================================

def cmd_history(args):
    history = get_memory_history(args.entity_id)
    if not history:
        print(f"No history found for entity: {args.entity_id}")
        return
    print(json.dumps(history, indent=2))

def cmd_query(args):
    results = query_by_time_range(args.entity_id, args.start, args.end)
    if not results:
        print(f"No results for {args.entity_id} in range [{args.start or '*'}, {args.end or '*'}]")
        return
    print(json.dumps(results, indent=2))

def cmd_build_index(args):
    ts = args.timestamp or datetime.now(timezone.utc).isoformat()
    build_index(args.graph, args.cid, ts)

def main():
    parser = argparse.ArgumentParser(description="Temporal query interface for entity history")
    sub = parser.add_subparsers(dest="command")

    p_hist = sub.add_parser("history", help="Full evolution timeline for an entity")
    p_hist.add_argument("entity_id", help="Entity ID to query")

    p_query = sub.add_parser("query", help="Query entity versions by time range")
    p_query.add_argument("entity_id", help="Entity ID to query")
    p_query.add_argument("--start", default="", help="Start date YYYY-MM-DD")
    p_query.add_argument("--end", default="", help="End date YYYY-MM-DD")

    p_build = sub.add_parser("build-index", help="Build temporal index from graph.jsonl")
    p_build.add_argument("--graph", required=True, help="Path to graph.jsonl")
    p_build.add_argument("--cid", required=True, help="Checkpoint CID")
    p_build.add_argument("--timestamp", default="", help="Checkpoint timestamp (ISO)")

    args = parser.parse_args()
    if args.command == "history":
        cmd_history(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "build-index":
        cmd_build_index(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
