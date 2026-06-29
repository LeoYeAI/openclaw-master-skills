#!/usr/bin/env python3
"""prune-ontology.py - Typed pruning policy framework for ontology graph.

Reads per-entity-type retention rules from ~/.amcp/config.json and prunes
memory/ontology/graph.jsonl. Supports TTL (30d, 90d, 1y), conditional
expressions (status == 'done'), and relation stub preservation.

Usage:
  prune-ontology.py [--dry-run] [--config FILE] [--graph FILE]

Environment:
  CONFIG_FILE   Override config path (default: ~/.amcp/config.json)
  CONTENT_DIR   Override workspace (default: from openclaw.json)
"""

import argparse, json, os, re, sys
from datetime import datetime, timezone, timedelta


def get_config_path():
    return os.path.expanduser(os.environ.get("CONFIG_FILE", "~/.amcp/config.json"))


def get_graph_path():
    content_dir = os.environ.get("CONTENT_DIR")
    if not content_dir:
        oc = os.path.expanduser("~/.openclaw/openclaw.json")
        try:
            with open(oc) as f:
                content_dir = json.load(f).get("agents", {}).get("defaults", {}).get(
                    "workspace", "~/.openclaw/workspace")
        except (IOError, json.JSONDecodeError):
            content_dir = "~/.openclaw/workspace"
    return os.path.join(os.path.expanduser(content_dir), "memory", "ontology", "graph.jsonl")


def load_policies(config_path):
    """Load pruning.policies from config.json."""
    try:
        with open(config_path) as f:
            cfg = json.load(f)
        return cfg.get("pruning", {}).get("policies", {})
    except (IOError, json.JSONDecodeError):
        return {}


def parse_ttl(ttl_str):
    """Parse TTL string (30d, 90d, 1y, 2w, 4h) into timedelta."""
    if not ttl_str or ttl_str == "null":
        return None
    m = re.match(r'^(\d+)([hdwmy])$', str(ttl_str).strip())
    if not m:
        return None
    val, unit = int(m.group(1)), m.group(2)
    if unit == 'h':
        return timedelta(hours=val)
    if unit == 'd':
        return timedelta(days=val)
    if unit == 'w':
        return timedelta(weeks=val)
    if unit == 'm':
        return timedelta(days=val * 30)
    if unit == 'y':
        return timedelta(days=val * 365)
    return None


def parse_timestamp(ts_str):
    """Parse ISO timestamp string to datetime."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def evaluate_condition(condition_str, entity, now):
    """Evaluate a simple condition expression against entity properties.

    Supports: field == 'value', field != 'value', updated < 90d
    Conjunctions with AND (all must match).
    """
    if not condition_str:
        return False

    clauses = re.split(r'\s+AND\s+', condition_str, flags=re.IGNORECASE)
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue

        # Temporal comparison: field < TTL (e.g., "updated < 90d")
        m = re.match(r'^(\w+)\s*<\s*(\d+[hdwmy])$', clause)
        if m:
            field, ttl_str = m.group(1), m.group(2)
            ttl = parse_ttl(ttl_str)
            if ttl is None:
                return False
            val = entity.get(field) or entity.get("properties", {}).get(field)
            ts = parse_timestamp(str(val)) if val else None
            if ts is None:
                return False
            if now - ts < ttl:
                return False
            continue

        # Equality: field == 'value'
        m = re.match(r"^(\w+)\s*==\s*'([^']*)'$", clause)
        if m:
            field, expected = m.group(1), m.group(2)
            actual = entity.get(field) or entity.get("properties", {}).get(field, "")
            if str(actual) != expected:
                return False
            continue

        # Inequality: field != 'value'
        m = re.match(r"^(\w+)\s*!=\s*'([^']*)'$", clause)
        if m:
            field, expected = m.group(1), m.group(2)
            actual = entity.get(field) or entity.get("properties", {}).get(field, "")
            if str(actual) == expected:
                return False
            continue

        # Unknown clause — fail safe (don't prune)
        return False

    return True


def should_prune(entity, policy, now):
    """Check if entity should be pruned based on its type's policy."""
    # Conditional expression takes priority (even with ttl: null)
    prune_if = policy.get("prune_if")
    if prune_if:
        return evaluate_condition(prune_if, entity, now)

    # ttl: null means never prune by age
    ttl_val = policy.get("ttl")
    if ttl_val is None:
        return False

    ttl = parse_ttl(ttl_val)
    if ttl is not None:
        created = parse_timestamp(entity.get("created") or entity.get("updated", ""))
        if created and (now - created) > ttl:
            return True

    return False


def prune_graph(graph_path, policies, dry_run=False):
    """Apply pruning policies to graph.jsonl. Returns summary dict."""
    if not os.path.isfile(graph_path):
        print("ERROR: Graph file not found: " + graph_path, file=sys.stderr)
        return {"pruned": 0, "kept": 0, "error": "file_not_found"}

    now = datetime.now(timezone.utc)
    entities, relations, pruned_ids = [], [], set()
    lines = []

    with open(graph_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                lines.append(line)
                continue

            if rec.get("type") == "entity":
                etype = rec.get("entity_type", "")
                policy = policies.get(etype, {})
                if policy and should_prune(rec, policy, now):
                    pruned_ids.add(rec.get("id"))
                else:
                    entities.append(rec)
                    lines.append(json.dumps(rec))
            elif rec.get("type") == "relation":
                relations.append(rec)
            else:
                lines.append(json.dumps(rec))

    # Process relations: preserve stubs or remove
    relation_stubs = []
    kept_relations = []
    for rel in relations:
        from_pruned = rel.get("from_id") in pruned_ids
        to_pruned = rel.get("to_id") in pruned_ids
        if from_pruned or to_pruned:
            # Check if relation's entity type policy has preserve_relations
            # Look up the pruned entity's type
            preserve = False
            for eid in [rel.get("from_id"), rel.get("to_id")]:
                if eid in pruned_ids:
                    # We need the entity_type, but it's already pruned
                    # Check all policies for preserve_relations
                    for etype, pol in policies.items():
                        if pol.get("preserve_relations"):
                            preserve = True
                            break
            if preserve:
                stub = rel.copy()
                stub["deleted_at"] = now.isoformat()
                relation_stubs.append(stub)
                lines.append(json.dumps(stub))
            # else: relation removed entirely
        else:
            kept_relations.append(rel)
            lines.append(json.dumps(rel))

    summary = {
        "pruned_entities": len(pruned_ids),
        "pruned_ids": sorted(pruned_ids),
        "kept_entities": len(entities),
        "kept_relations": len(kept_relations),
        "relation_stubs": len(relation_stubs),
    }

    if dry_run:
        summary["dry_run"] = True
        print(json.dumps(summary, indent=2))
        return summary

    # Write .pruned then atomic rename
    pruned_path = graph_path + ".pruned"
    with open(pruned_path, "w") as f:
        for line in lines:
            f.write(line + "\n")
    os.rename(pruned_path, graph_path)

    summary["dry_run"] = False
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description="Prune ontology graph by typed policies")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be pruned")
    parser.add_argument("--config", help="Override config.json path")
    parser.add_argument("--graph", help="Override graph.jsonl path")
    args = parser.parse_args()

    config_path = args.config or get_config_path()
    graph_path = args.graph or get_graph_path()

    policies = load_policies(config_path)
    if not policies:
        print("No pruning policies configured in " + config_path, file=sys.stderr)
        print(json.dumps({"pruned_entities": 0, "kept_entities": 0, "message": "no_policies"}))
        sys.exit(0)

    prune_graph(graph_path, policies, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
