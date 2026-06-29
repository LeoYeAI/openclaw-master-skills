#!/usr/bin/env python3
"""detect-contract-conflicts.py — Cross-skill ontology conflict detection.

Scans all skills in the skills directory for ontologyContract declarations,
then detects incompatible postconditions across skills.

Conflict types:
- Equality vs inequality: Skill A says "X.p == v" and Skill B says "X.p != v"
- Contradictory equality: Skill A says "X.p == v1" and Skill B says "X.p == v2" (v1 != v2)

Called by detect-contract-conflicts.sh via environment variables:
  _SKILLS_DIR    Path to skills directory
  _JSON_OUTPUT   'true' for JSON output
"""

import json
import os
import re
import sys
from collections import defaultdict


def load_all_contracts(skills_dir):
    """Load ontologyContract from all skill.json files in skills_dir."""
    contracts = {}

    if not os.path.isdir(skills_dir):
        return contracts

    for entry in sorted(os.listdir(skills_dir)):
        skill_json = os.path.join(skills_dir, entry, "skill.json")
        if not os.path.isfile(skill_json):
            continue

        try:
            with open(skill_json) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        contract = data.get("ontologyContract")
        if contract and contract.get("ontology"):
            contracts[entry] = contract

    return contracts


def parse_postcondition(postcond):
    """Parse a postcondition into structured form.

    Returns dict with: entity_type, property, operator, value
    or None if unparseable.
    """
    parts = postcond.split(".", 1)
    if len(parts) != 2:
        return None

    etype = parts[0]
    rest = parts[1]

    if " == " in rest:
        prop, value = rest.split(" == ", 1)
        return {
            "entity_type": etype,
            "property": prop.strip(),
            "operator": "==",
            "value": value.strip().strip("'\""),
        }
    elif " != " in rest:
        prop, value = rest.split(" != ", 1)
        return {
            "entity_type": etype,
            "property": prop.strip(),
            "operator": "!=",
            "value": value.strip().strip("'\""),
        }
    elif " is valid enum" in rest:
        prop = rest.replace(" is valid enum", "").strip()
        return {
            "entity_type": etype,
            "property": prop,
            "operator": "is_valid_enum",
            "value": None,
        }
    elif " exists" in rest:
        prop = rest.replace(" exists", "").strip()
        return {
            "entity_type": etype,
            "property": prop,
            "operator": "exists",
            "value": None,
        }

    return None


def detect_conflicts(contracts):
    """Detect conflicting postconditions across skills.

    Returns list of conflict dicts.
    """
    # Group postconditions by (entity_type, property)
    postconds_by_field = defaultdict(list)

    for skill_name, contract in contracts.items():
        ontology = contract.get("ontology", {})
        for postcond in ontology.get("postconditions", []):
            parsed = parse_postcondition(postcond)
            if parsed:
                key = (parsed["entity_type"], parsed["property"])
                postconds_by_field[key].append({
                    "skill": skill_name,
                    "raw": postcond,
                    "parsed": parsed,
                })

    conflicts = []

    for field_key, entries in postconds_by_field.items():
        if len(entries) < 2:
            continue

        # Check all pairs for conflicts
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                a = entries[i]
                b = entries[j]
                pa = a["parsed"]
                pb = b["parsed"]

                conflict = None

                # Case 1: A says == v, B says != v (same value)
                if pa["operator"] == "==" and pb["operator"] == "!=" and pa["value"] == pb["value"]:
                    conflict = {
                        "type": "equality_vs_inequality",
                        "description": (
                            f"{a['skill']} requires {pa['entity_type']}.{pa['property']} == '{pa['value']}' "
                            f"but {b['skill']} forbids it (!= '{pb['value']}')"
                        ),
                    }
                elif pa["operator"] == "!=" and pb["operator"] == "==" and pa["value"] == pb["value"]:
                    conflict = {
                        "type": "equality_vs_inequality",
                        "description": (
                            f"{b['skill']} requires {pb['entity_type']}.{pb['property']} == '{pb['value']}' "
                            f"but {a['skill']} forbids it (!= '{pa['value']}')"
                        ),
                    }

                # Case 2: A says == v1, B says == v2 (different values)
                elif pa["operator"] == "==" and pb["operator"] == "==" and pa["value"] != pb["value"]:
                    conflict = {
                        "type": "contradictory_equality",
                        "description": (
                            f"{a['skill']} requires {pa['entity_type']}.{pa['property']} == '{pa['value']}' "
                            f"but {b['skill']} requires == '{pb['value']}'"
                        ),
                    }

                if conflict:
                    conflict["skill_a"] = a["skill"]
                    conflict["skill_b"] = b["skill"]
                    conflict["postcondition_a"] = a["raw"]
                    conflict["postcondition_b"] = b["raw"]
                    conflict["field"] = f"{pa['entity_type']}.{pa['property']}"
                    conflicts.append(conflict)

    return conflicts


def main():
    skills_dir = os.path.expanduser(os.environ.get("_SKILLS_DIR", "~/.openclaw/skills"))
    json_output = os.environ.get("_JSON_OUTPUT", "false") == "true"

    contracts = load_all_contracts(skills_dir)

    if not contracts:
        result = {"conflicts": [], "skills_checked": 0, "message": "no skills with ontology contracts found"}
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print("No skills with ontology contracts found")
        sys.exit(0)

    conflicts = detect_conflicts(contracts)

    # Check reads/writes compatibility (informational, not a conflict)
    compatible_pairs = []
    for name_a, contract_a in contracts.items():
        for name_b, contract_b in contracts.items():
            if name_a >= name_b:
                continue
            writes_a = set(contract_a.get("ontology", {}).get("writes", []))
            reads_b = set(contract_b.get("ontology", {}).get("reads", []))
            writes_b = set(contract_b.get("ontology", {}).get("writes", []))
            reads_a = set(contract_a.get("ontology", {}).get("reads", []))

            shared = (writes_a & reads_b) | (writes_b & reads_a)
            if shared:
                compatible_pairs.append({
                    "skill_a": name_a,
                    "skill_b": name_b,
                    "shared_types": sorted(shared),
                })

    result = {
        "conflicts": conflicts,
        "conflicts_found": len(conflicts),
        "skills_checked": len(contracts),
        "skills": sorted(contracts.keys()),
        "compatible_pairs": compatible_pairs,
    }

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"Checked {len(contracts)} skill(s): {', '.join(sorted(contracts.keys()))}")
        print()

        if conflicts:
            print(f"CONFLICTS FOUND: {len(conflicts)}")
            for c in conflicts:
                print(f"  * [{c['type']}] {c['description']}")
                print(f"    {c['skill_a']}: {c['postcondition_a']}")
                print(f"    {c['skill_b']}: {c['postcondition_b']}")
                print()
        else:
            print("No conflicts detected")

        if compatible_pairs:
            print()
            print("Compatible read/write pairs:")
            for pair in compatible_pairs:
                print(f"  {pair['skill_a']} <-> {pair['skill_b']}: {', '.join(pair['shared_types'])}")

    sys.exit(1 if conflicts else 0)


if __name__ == "__main__":
    main()
