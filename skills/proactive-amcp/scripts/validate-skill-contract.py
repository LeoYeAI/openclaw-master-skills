#!/usr/bin/env python3
"""validate-skill-contract.py — Validate skill ontology contracts against graph.jsonl.

Reads contract from skill.json (ontologyContract field) or direct contract file.
Checks preconditions against current graph entities.

Called by validate-skill-contract.sh via environment variables:
  _CONTRACT_SOURCE  Path to skill.json or direct contract JSON
  _GRAPH_PATH       Path to graph.jsonl
  _JSON_OUTPUT      'true' for JSON output
  _SKILL_NAME       Skill name for display
  _IS_DIRECT_CONTRACT  'true' if contract source is a direct contract file
"""

import json
import os
import sys


def load_contract(source_path, is_direct):
    """Load ontologyContract from skill.json or direct file."""
    with open(source_path) as f:
        data = json.load(f)

    if is_direct:
        return data

    # Extract from skill.json
    return data.get("ontologyContract", {})


def load_graph(graph_path):
    """Load entities from graph.jsonl grouped by type."""
    entities_by_type = {}

    if not os.path.isfile(graph_path):
        return entities_by_type

    with open(graph_path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict):
                continue

            rtype = record.get("type")
            if rtype and rtype != "relation":
                if rtype not in entities_by_type:
                    entities_by_type[rtype] = []
                entities_by_type[rtype].append(record)

    return entities_by_type


def check_precondition(precond, entities_by_type):
    """Check a single precondition. Returns list of error strings."""
    errors = []
    parts = precond.split(".", 1)
    if len(parts) != 2:
        return [f"precondition '{precond}': invalid format (expected EntityType.property ...)"]

    etype = parts[0]
    rest = parts[1]
    entities = entities_by_type.get(etype, [])

    # No entities of this type = precondition trivially holds
    if not entities:
        return []

    if " exists" in rest:
        prop = rest.replace(" exists", "").strip()
        for entity in entities:
            props = entity.get("properties", {})
            if prop not in props:
                eid = entity.get("id", "unknown")
                errors.append(
                    f"precondition '{precond}': entity '{eid}' of type "
                    f"'{etype}' missing property '{prop}'"
                )

    elif " == " in rest:
        prop, expected = rest.split(" == ", 1)
        prop = prop.strip()
        expected = expected.strip().strip("'\"")
        for entity in entities:
            props = entity.get("properties", {})
            actual = props.get(prop)
            if actual is not None and str(actual) != expected:
                eid = entity.get("id", "unknown")
                errors.append(
                    f"precondition '{precond}': entity '{eid}' has "
                    f"{etype}.{prop}='{actual}', expected '{expected}'"
                )

    elif " != " in rest:
        prop, forbidden = rest.split(" != ", 1)
        prop = prop.strip()
        forbidden = forbidden.strip().strip("'\"")
        for entity in entities:
            props = entity.get("properties", {})
            actual = props.get(prop)
            if actual is not None and str(actual) == forbidden:
                eid = entity.get("id", "unknown")
                errors.append(
                    f"precondition '{precond}': entity '{eid}' has "
                    f"forbidden {etype}.{prop}='{actual}'"
                )

    elif " is valid enum" in rest:
        prop = rest.replace(" is valid enum", "").strip()
        for entity in entities:
            props = entity.get("properties", {})
            val = props.get(prop)
            if val is not None and not isinstance(val, str):
                eid = entity.get("id", "unknown")
                errors.append(
                    f"precondition '{precond}': entity '{eid}' has "
                    f"non-string {etype}.{prop}='{val}'"
                )
    else:
        errors.append(f"precondition '{precond}': unrecognized condition format")

    return errors


def main():
    source_path = os.environ.get("_CONTRACT_SOURCE", "")
    graph_path = os.path.expanduser(os.environ.get("_GRAPH_PATH", ""))
    json_output = os.environ.get("_JSON_OUTPUT", "false") == "true"
    skill_name = os.environ.get("_SKILL_NAME", "")
    is_direct = os.environ.get("_IS_DIRECT_CONTRACT", "") == "true"

    if not source_path or not os.path.isfile(source_path):
        result = {"valid": True, "skipped": True, "reason": "contract source not found"}
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"SKIP: {skill_name or 'skill'} — contract source not found")
        sys.exit(0)

    try:
        contract = load_contract(source_path, is_direct)
    except (json.JSONDecodeError, KeyError) as e:
        result = {"valid": False, "errors": [f"Failed to load contract: {e}"]}
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"FAIL: Could not load contract: {e}")
        sys.exit(1)

    # Empty contract = backward compatible skip
    if not contract or not contract.get("ontology"):
        result = {"valid": True, "skipped": True, "reason": "no ontology contract declared"}
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"SKIP: {skill_name or 'skill'} has no ontology contract")
        sys.exit(0)

    ontology = contract["ontology"]
    reads = ontology.get("reads", [])
    writes = ontology.get("writes", [])
    preconditions = ontology.get("preconditions", [])

    entities_by_type = load_graph(graph_path)

    errors = []

    # Check reads: required entity types must exist
    for etype in reads:
        if etype not in entities_by_type:
            errors.append(f"reads '{etype}': no entities of type '{etype}' found in graph")

    # Check preconditions
    for precond in preconditions:
        errors.extend(check_precondition(precond, entities_by_type))

    result = {
        "valid": len(errors) == 0,
        "skill": skill_name or contract.get("skill_name", "unknown"),
        "reads": reads,
        "writes": writes,
        "preconditions_checked": len(preconditions),
        "entity_types_found": list(entities_by_type.keys()),
    }
    if errors:
        result["errors"] = errors

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        sname = result["skill"]
        if result["valid"]:
            print(f"PASS: {sname} — all {len(preconditions)} preconditions satisfied")
            print(f"  Reads: {', '.join(reads) or '(none)'}")
            print(f"  Writes: {', '.join(writes) or '(none)'}")
        else:
            print(f"FAIL: {sname} — {len(errors)} precondition violation(s)")
            for err in errors:
                print(f"  * {err}")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
