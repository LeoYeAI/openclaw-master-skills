#!/usr/bin/env python3
"""compute-entity-similarity.py - Semantic similarity for entity linking.

Computes similarity between entities using Levenshtein distance + keyword
overlap. Used by memory-evolution.sh to infer relations in the ontology graph.

Usage:
  compute-entity-similarity.py --graph FILE --entity-id ID [--threshold 0.75] [--max-relations 3]

Outputs JSON array of related entities with similarity scores.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter


def load_graph(filepath):
    """Load entities from graph.jsonl."""
    entities = {}
    if not os.path.isfile(filepath):
        return entities
    with open(filepath) as f:
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
            eid = record.get("id", "")
            if eid:
                entities[eid] = record
    return entities


def tokenize(text):
    """Extract meaningful tokens from text."""
    if not isinstance(text, str):
        return []
    # Lowercase, split on non-alphanumeric, filter short tokens
    tokens = re.findall(r'[a-z0-9]+', text.lower())
    return [t for t in tokens if len(t) > 2]


def extract_text(entity):
    """Extract all searchable text from an entity."""
    parts = []
    props = entity.get("properties", {})
    if isinstance(props, dict):
        for key, val in props.items():
            parts.append(str(key))
            if isinstance(val, str):
                parts.append(val)
            elif isinstance(val, list):
                parts.extend(str(v) for v in val)
    # Also include entity type and name
    if entity.get("entity_type"):
        parts.append(str(entity["entity_type"]))
    if props.get("name"):
        parts.append(str(props["name"]))
    if props.get("description"):
        parts.append(str(props["description"]))
    if props.get("title"):
        parts.append(str(props["title"]))
    return " ".join(parts)


def levenshtein_ratio(s1, s2):
    """Compute Levenshtein similarity ratio (0.0 to 1.0)."""
    if not s1 or not s2:
        return 0.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 and len2 == 0:
        return 1.0

    # Use iterative matrix (memory efficient for shorter strings)
    if len1 > 500 or len2 > 500:
        # For very long strings, fall back to token overlap only
        return 0.0

    prev = list(range(len2 + 1))
    for i in range(1, len1 + 1):
        curr = [i] + [0] * len2
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = curr

    distance = prev[len2]
    max_len = max(len1, len2)
    return 1.0 - (distance / max_len)


def keyword_overlap(tokens1, tokens2):
    """Compute Jaccard-like keyword overlap score (0.0 to 1.0)."""
    if not tokens1 or not tokens2:
        return 0.0
    set1 = set(tokens1)
    set2 = set(tokens2)
    intersection = set1 & set2
    union = set1 | set2
    if not union:
        return 0.0
    return len(intersection) / len(union)


def compute_similarity(entity_a, entity_b):
    """Compute combined similarity score between two entities."""
    text_a = extract_text(entity_a)
    text_b = extract_text(entity_b)

    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)

    # Keyword overlap (weighted 0.6)
    kw_score = keyword_overlap(tokens_a, tokens_b)

    # Levenshtein on extracted text (weighted 0.4, capped at 200 chars)
    lev_score = levenshtein_ratio(text_a[:200].lower(), text_b[:200].lower())

    combined = 0.6 * kw_score + 0.4 * lev_score

    # Build reasoning
    common = set(tokens_a) & set(tokens_b)
    reasoning = f"keyword_overlap={kw_score:.3f}, levenshtein={lev_score:.3f}"
    if common:
        reasoning += f", shared_keywords=[{','.join(sorted(common)[:5])}]"

    return combined, reasoning


def find_similar(graph, target_id, threshold=0.75, max_relations=3):
    """Find entities similar to target."""
    if target_id not in graph:
        print(f"ERROR: Entity {target_id} not found in graph", file=sys.stderr)
        sys.exit(1)

    target = graph[target_id]
    scores = []

    for eid, entity in graph.items():
        if eid == target_id:
            continue
        score, reasoning = compute_similarity(target, entity)
        if score >= threshold:
            scores.append({
                "entity_id": eid,
                "entity_type": entity.get("entity_type", "unknown"),
                "similarity_score": round(score, 4),
                "reasoning": reasoning
            })

    # Sort by score descending, take top N
    scores.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scores[:max_relations]


def main():
    parser = argparse.ArgumentParser(
        description="Compute entity similarity for relation inference"
    )
    parser.add_argument("--graph", required=True, help="Path to graph.jsonl")
    parser.add_argument("--entity-id", required=True, help="Target entity ID")
    parser.add_argument("--threshold", type=float, default=0.75, help="Similarity threshold (default: 0.75)")
    parser.add_argument("--max-relations", type=int, default=3, help="Max relations to infer (default: 3)")
    args = parser.parse_args()

    graph = load_graph(args.graph)
    if not graph:
        print("[]")
        sys.exit(0)

    results = find_similar(graph, args.entity_id, args.threshold, args.max_relations)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
