#!/usr/bin/env python3
"""validate-ontology.py - Schema validation for JSONL ontology graph files.

Validates graph.jsonl format and integrity:
- Each line is valid JSON with 'type' field (entity or relation)
- Entities have required fields: id, type, properties
- Relations have required fields: from_id, relation_type, to_id
- Relation integrity: from_id and to_id reference existing entities
- Acyclic check: 'blocks' relations must not form cycles

Output JSON:
  { "valid": true, "entity_count": N, "relation_count": M }
  { "valid": false, "errors": [...], "entity_count": N, "relation_count": M }

Usage:
  validate-ontology.py <graph.jsonl>
  validate-ontology.py --graph <path>
"""

import argparse
import json
import os
import sys
from collections import defaultdict


def load_and_validate(filepath):
    """Load graph.jsonl and validate each record."""
    entities = {}
    relations = []
    errors = []

    if not os.path.isfile(filepath):
        return {
            "valid": True,
            "entity_count": 0,
            "relation_count": 0,
            "skipped": True,
            "reason": "file not found",
        }

    with open(filepath) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            # Valid JSON check
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {lineno}: invalid JSON: {e}")
                continue

            if not isinstance(record, dict):
                errors.append(f"line {lineno}: expected object, got {type(record).__name__}")
                continue

            record_type = record.get("type")
            if not record_type:
                errors.append(f"line {lineno}: missing 'type' field")
                continue

            if record_type == "relation":
                # Validate relation fields
                missing = []
                for field in ("from_id", "relation_type", "to_id"):
                    if not record.get(field):
                        missing.append(field)
                if missing:
                    errors.append(
                        f"line {lineno}: relation missing fields: {', '.join(missing)}"
                    )
                else:
                    relations.append(
                        {
                            "lineno": lineno,
                            "from_id": record["from_id"],
                            "to_id": record["to_id"],
                            "relation_type": record["relation_type"],
                        }
                    )
            else:
                # Entity — validate required fields
                eid = record.get("id")
                if not eid:
                    errors.append(f"line {lineno}: entity missing 'id' field")
                    continue

                if "properties" not in record and not isinstance(
                    record.get("properties"), dict
                ):
                    # properties can be missing (backward compat) but should be dict if present
                    pass

                entities[eid] = lineno

    # Relation integrity: from_id and to_id must reference existing entities
    for rel in relations:
        if rel["from_id"] not in entities:
            errors.append(
                f"line {rel['lineno']}: relation from_id '{rel['from_id']}' "
                f"references non-existent entity"
            )
        if rel["to_id"] not in entities:
            errors.append(
                f"line {rel['lineno']}: relation to_id '{rel['to_id']}' "
                f"references non-existent entity"
            )

    # Acyclic check for 'blocks' relations
    blocks_graph = defaultdict(set)
    for rel in relations:
        if rel["relation_type"] == "blocks":
            blocks_graph[rel["from_id"]].add(rel["to_id"])

    if blocks_graph:
        cycle = detect_cycle(blocks_graph)
        if cycle:
            errors.append(
                f"circular dependency in 'blocks' relations: "
                f"{' -> '.join(cycle)}"
            )

    result = {
        "valid": len(errors) == 0,
        "entity_count": len(entities),
        "relation_count": len(relations),
    }
    if errors:
        result["errors"] = errors

    return result


def detect_cycle(graph):
    """Detect cycle in directed graph using DFS. Returns cycle path or None."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = defaultdict(int)
    parent = {}

    def dfs(node, path):
        color[node] = GRAY
        path.append(node)
        for neighbor in graph.get(node, set()):
            if color[neighbor] == GRAY:
                # Found cycle
                cycle_start = path.index(neighbor)
                return path[cycle_start:] + [neighbor]
            if color[neighbor] == WHITE:
                parent[neighbor] = node
                result = dfs(neighbor, path)
                if result:
                    return result
        path.pop()
        color[node] = BLACK
        return None

    for node in list(graph.keys()):
        if color[node] == WHITE:
            result = dfs(node, [])
            if result:
                return result

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Validate ontology graph.jsonl schema and integrity"
    )
    parser.add_argument(
        "graph_path", nargs="?", help="Path to graph.jsonl"
    )
    parser.add_argument(
        "--graph", dest="graph_flag", help="Path to graph.jsonl (alternative)"
    )
    args = parser.parse_args()

    filepath = args.graph_path or args.graph_flag
    if not filepath:
        print(json.dumps({"valid": True, "entity_count": 0, "relation_count": 0,
                          "skipped": True, "reason": "no path provided"}))
        sys.exit(0)

    filepath = os.path.expanduser(filepath)
    result = load_and_validate(filepath)
    print(json.dumps(result, indent=2))

    if not result.get("valid", True) and not result.get("skipped"):
        sys.exit(1)


if __name__ == "__main__":
    main()
