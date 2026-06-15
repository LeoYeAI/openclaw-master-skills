#!/bin/bash
# Learning Loop - Rule Importer for Cross-Agent Sharing (v1.4.0)
# Imports rules from another agent with conflict detection and trust scoring
# Usage: bash import-rules.sh [workspace-dir] <import-file> [--dry-run] [--trust <score>]
# Returns: 0 on success, 1 on configuration error, 2 on import failure
# Schedule: Manual (when importing shared rules)
# Dependencies: rules.json, import file from export-rules.sh
# Side Effects: Updates rules.json (with file locking)

set -o pipefail

SCRIPT_NAME="import-rules.sh"
VERSION="1.4.0"

WORKSPACE=""
IMPORT_FILE=""
DRY_RUN=""
TRUST_THRESHOLD="0.5"

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --trust)
            TRUST_THRESHOLD="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: bash import-rules.sh [workspace-dir] <import-file> [options]"
            echo ""
            echo "Options:"
            echo "  --dry-run           Preview changes without writing"
            echo "  --trust <score>     Minimum trust score for auto-import (0.0-1.0, default: 0.5)"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  bash import-rules.sh /path/to/workspace ./exported-rules.json"
            echo "  bash import-rules.sh ./exported-rules.json --dry-run"
            echo "  bash import-rules.sh ./exported-rules.json --trust 0.8"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            if [ -z "$WORKSPACE" ] && [ ! -f "$1" ]; then
                WORKSPACE="$1"
            elif [ -z "$IMPORT_FILE" ] && [ -f "$1" ]; then
                IMPORT_FILE="$1"
            fi
            shift
            ;;
    esac
done

WORKSPACE="${WORKSPACE:-$(pwd)}"
LEARNING_DIR="$WORKSPACE/memory/learning"
RULES_FILE="$LEARNING_DIR/rules.json"

# ============================================================================
# INPUT VALIDATION
# ============================================================================

# Check workspace exists and is writable
if [[ ! -d "$WORKSPACE" ]]; then
    echo "ERROR: Workspace does not exist: $WORKSPACE"
    exit 1
fi

if [[ ! -w "$WORKSPACE" ]]; then
    echo "ERROR: Workspace is not writable: $WORKSPACE"
    exit 1
fi

# Prevent system directories
if [[ "$WORKSPACE" =~ ^/(etc|bin|sbin|usr|System|Library|Applications) ]]; then
    echo "ERROR: Cannot use system directory as workspace: $WORKSPACE"
    exit 1
fi

if [ -z "$IMPORT_FILE" ]; then
    echo "ERROR: No import file specified"
    echo "Usage: bash import-rules.sh [workspace-dir] <import-file>"
    exit 1
fi

if [ ! -f "$IMPORT_FILE" ]; then
    echo "ERROR: Import file not found: $IMPORT_FILE"
    exit 1
fi

if [ ! -f "$RULES_FILE" ]; then
    echo "ERROR: rules.json not found at $RULES_FILE"
    echo "Run init.sh first."
    exit 1
fi

# Get agent handle from environment or default
AGENT_HANDLE="${AGENT_HANDLE:-$(whoami)}"
IMPORT_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Learning Loop - Rule Importer v$VERSION"
echo "======================================"
echo ""
echo "Import file: $IMPORT_FILE"
echo "Target workspace: $WORKSPACE"
if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "Mode: DRY RUN (no changes will be made)"
fi
echo ""

# ============================================================================
# FILE LOCKING SETUP
# ============================================================================

LOCK_FILE="$LEARNING_DIR/.lockfile"
exec 200>"$LOCK_FILE"
if ! flock -w 10 200; then
    echo "ERROR: Could not acquire lock on $LOCK_FILE"
    exit 3
fi

python3 - "$RULES_FILE" "$IMPORT_FILE" "$DRY_RUN" "$TRUST_THRESHOLD" "$AGENT_HANDLE" "$IMPORT_TIMESTAMP" "$SCRIPT_NAME" << 'PYTHON'
import json, sys, hashlib, fcntl
from datetime import datetime, date

rules_path = sys.argv[1]
import_path = sys.argv[2]
dry_run = sys.argv[3] == "--dry-run" if len(sys.argv) > 3 else False
trust_threshold = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
importing_agent = sys.argv[5] if len(sys.argv) > 5 else "unknown"
import_timestamp = sys.argv[6] if len(sys.argv) > 6 else ""
script_name = sys.argv[7] if len(sys.argv) > 7 else ""

def calculate_rule_hash(rule):
    """Calculate SHA256 hash of rule content."""
    content = json.dumps(rule, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def calculate_similarity(rule1, rule2):
    """Calculate simple text similarity between two rules."""
    text1 = rule1.get("rule", "").lower()
    text2 = rule2.get("rule", "").lower()
    
    # Simple word overlap similarity
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union)

def detect_conflict(imported_rule, existing_rules):
    """Detect conflicts between imported rule and existing rules."""
    conflicts = []
    for existing in existing_rules:
        similarity = calculate_similarity(imported_rule, existing)
        if similarity > 0.7:  # High similarity threshold
            conflicts.append({
                "existing_rule": existing.get("id"),
                "similarity": round(similarity, 2),
                "existing_text": existing.get("rule", "")[:80]
            })
    return conflicts

def calculate_trust_score(import_metadata, imported_rules):
    """Calculate trust score for the import based on various factors."""
    score = 0.5  # Base score
    
    # Factor 1: Number of rules (more rules = more established)
    rule_count = len(imported_rules)
    if rule_count >= 20:
        score += 0.1
    elif rule_count >= 10:
        score += 0.05
    
    # Factor 2: Average confidence of imported rules
    avg_confidence = sum(r.get("confidence_score", 0.9) for r in imported_rules) / len(imported_rules) if imported_rules else 0
    score += avg_confidence * 0.2
    
    # Factor 3: Category diversity
    categories = set(r.get("category") for r in imported_rules)
    if len(categories) >= 5:
        score += 0.1
    elif len(categories) >= 3:
        score += 0.05
    
    # Factor 4: Has manifest hash (integrity verification)
    if import_metadata.get("manifest_hash"):
        score += 0.05
    
    return min(1.0, score)

# Load import file
try:
    with open(import_path, "r") as f:
        import_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"ERROR: Could not load import file: {e}")
    sys.exit(1)

# Validate import format - support multiple formats
if isinstance(import_data, list):
    # Format 1: Plain array of rules
    metadata = {"agent_handle": "unknown", "exported_at": "unknown"}
    imported_rules = import_data
elif "pack" in import_data and "rules" in import_data:
    # Format 2: Rule pack format (pack + rules)
    pack_info = import_data.get("pack", {})
    metadata = {
        "agent_handle": pack_info.get("name", "unknown"),
        "exported_at": pack_info.get("version", "unknown"),
        "version": pack_info.get("version", "1.0.0"),
        "description": pack_info.get("description", "")
    }
    imported_rules = import_data.get("rules", [])
elif "metadata" in import_data and "rules" in import_data:
    # Format 3: Agent export format (metadata + rules)
    metadata = import_data.get("metadata", {})
    imported_rules = import_data.get("rules", [])
else:
    print("ERROR: Invalid import file format. Expected one of:")
    print("  1. A JSON array of rule objects")
    print("  2. {\"pack\": {...}, \"rules\": [...]}")
    print("  3. {\"metadata\": {...}, \"rules\": [...]}")
    sys.exit(1)

print(f"Source agent: {metadata.get('agent_handle', 'unknown')}")
print(f"Exported at: {metadata.get('exported_at', 'unknown')}")
print(f"Rules in import: {len(imported_rules)}")
print(f"Categories: {', '.join(set(r.get('category', 'unknown') for r in imported_rules))}")
print("")

# Calculate trust score
trust_score = calculate_trust_score(metadata, imported_rules)
print(f"Trust score: {trust_score:.2f} (threshold: {trust_threshold})")

if trust_score < trust_threshold:
    print(f"\n⚠️  WARNING: Trust score {trust_score:.2f} is below threshold {trust_threshold}")
    print("Import will proceed in review mode (all rules need manual approval)")
    review_mode = True
else:
    review_mode = False

# Load existing rules
try:
    with open(rules_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        rules_data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"ERROR: Could not load rules.json: {e}")
    sys.exit(1)

existing_rules = rules_data.get("rules", [])
existing_ids = {r["id"] for r in existing_rules}

# Find next rule ID
existing_id_nums = []
for r in existing_rules:
    rid = r.get("id", "")
    if rid.startswith("R-"):
        try:
            existing_id_nums.append(int(rid.split("-")[1]))
        except (ValueError, IndexError):
            pass
next_id_num = max(existing_id_nums) + 1 if existing_id_nums else 1

# Process imports
imports = {
    "auto_imported": [],
    "needs_review": [],
    "conflicts": [],
    "skipped": []
}

print("\n" + "=" * 60)
print("PROCESSING IMPORTS")
print("=" * 60)

for imported_rule in imported_rules:
    original_id = imported_rule.pop("_original_id", None)
    rule_hash = imported_rule.pop("_hash", None)
    
    # Check for conflicts
    conflicts = detect_conflict(imported_rule, existing_rules)
    
    if conflicts:
        imports["conflicts"].append({
            "imported_rule": imported_rule.get("rule", "")[:60],
            "conflicts_with": conflicts
        })
        continue
    
    # Generate new ID
    new_id = f"R-{next_id_num:03d}"
    next_id_num += 1
    
    # Prepare rule for import
    new_rule = {
        "id": new_id,
        "type": imported_rule.get("type", "PREFER"),
        "category": imported_rule.get("category", "general"),
        "rule": imported_rule.get("rule", ""),
        "reason": imported_rule.get("reason", f"Imported from {metadata.get('agent_handle', 'unknown')}"),
        "created": str(date.today()),
        "source_lesson": f"IMPORTED:{original_id}",
        "violations": 0,
        "last_checked": str(date.today()),
        "last_validated": str(date.today()),
        "validation_count": 0,
        "confidence_score": imported_rule.get("confidence_score", 0.5),
        "imported_from": metadata.get("agent_handle", "unknown"),
        "imported_at": import_timestamp,
        "import_hash": rule_hash
    }
    
    # Decide import action
    if review_mode:
        imports["needs_review"].append({
            "id": new_id,
            "rule": new_rule,
            "reason": f"Low trust score ({trust_score:.2f} < {trust_threshold})"
        })
    else:
        imports["auto_imported"].append({
            "id": new_id,
            "rule": new_rule
        })

# Report results
print(f"\nAuto-import: {len(imports['auto_imported'])} rules")
print(f"Needs review: {len(imports['needs_review'])} rules")
print(f"Conflicts: {len(imports['conflicts'])} rules")
print(f"Skipped: {len(imports['skipped'])} rules")

if imports["conflicts"]:
    print("\n" + "=" * 60)
    print("CONFLICTS DETECTED")
    print("=" * 60)
    for c in imports["conflicts"]:
        print(f"\nRule: {c['imported_rule']}")
        print("Conflicts with:")
        for conflict in c["conflicts_with"]:
            print(f"  - {conflict['existing_rule']} (similarity: {conflict['similarity']})")
            print(f"    {conflict['existing_text']}")

if imports["needs_review"]:
    print("\n" + "=" * 60)
    print("RULES NEEDING REVIEW")
    print("=" * 60)
    for r in imports["needs_review"]:
        print(f"\n  Proposed ID: {r['id']}")
        print(f"  Rule: {r['rule']['rule']}")
        print(f"  Reason: {r['reason']}")

# Apply imports
if not dry_run and imports["auto_imported"]:
    print("\n" + "=" * 60)
    print("APPLYING IMPORTS")
    print("=" * 60)
    
    for item in imports["auto_imported"]:
        existing_rules.append(item["rule"])
        print(f"  + {item['id']}: {item['rule']['rule'][:60]}")
    
    # Save rules
    rules_data["rules"] = existing_rules
    rules_data["updated"] = str(date.today())
    
    try:
        with open(rules_path, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(rules_data, f, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        print(f"\n✓ Saved {len(existing_rules)} total rules")
    except Exception as e:
        print(f"ERROR: Failed to write rules.json: {e}")
        sys.exit(2)

# Summary
print("\n" + "=" * 60)
print("IMPORT SUMMARY")
print("=" * 60)
print(f"Total rules in target: {len(existing_rules)}")
print(f"Auto-imported: {len(imports['auto_imported'])}")
print(f"Needs manual review: {len(imports['needs_review'])}")
print(f"Conflicts: {len(imports['conflicts'])}")

if dry_run:
    print("\n[DRY RUN] No changes were made.")
else:
    print(f"\nImport complete. Review {len(imports['needs_review'])} rule(s) needing manual approval.")

PYTHON

exit_code=$?

# Release lock
exec 200>&-

exit $exit_code
