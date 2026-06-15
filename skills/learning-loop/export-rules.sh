#!/bin/bash
# Learning Loop - Rule Exporter for Cross-Agent Sharing (v1.4.0)
# Exports rules as portable JSON with metadata for sharing between agents
# Includes agent handle, export timestamp, rule hashes for integrity verification
# Usage: bash export-rules.sh [workspace-dir] [--output <file>] [--category <cat>]
# Returns: 0 on success, 1 on configuration error
# Schedule: Manual (when sharing rules)
# Dependencies: rules.json
# Side Effects: Creates export file (read-only operation on learning data)

set -o pipefail

SCRIPT_NAME="export-rules.sh"
VERSION="1.4.0"

WORKSPACE=""
OUTPUT_FILE=""
CATEGORY_FILTER=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --category)
            CATEGORY_FILTER="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: bash export-rules.sh [workspace-dir] [options]"
            echo ""
            echo "Options:"
            echo "  --output <file>     Output file path (default: stdout)"
            echo "  --category <cat>    Filter by category (e.g., shell, auth, memory)"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  bash export-rules.sh /path/to/workspace --output rules-export.json"
            echo "  bash export-rules.sh --category shell > shell-rules.json"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            if [ -z "$WORKSPACE" ]; then
                WORKSPACE="$1"
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

# Check workspace exists
if [[ ! -d "$WORKSPACE" ]]; then
    echo "ERROR: Workspace does not exist: $WORKSPACE"
    exit 1
fi

# Prevent system directories
if [[ "$WORKSPACE" =~ ^/(etc|bin|sbin|usr|System|Library|Applications) ]]; then
    echo "ERROR: Cannot use system directory as workspace: $WORKSPACE"
    exit 1
fi

if [ ! -f "$RULES_FILE" ]; then
    echo "ERROR: rules.json not found at $RULES_FILE"
    echo "Run init.sh first."
    exit 1
fi

# Get agent handle from environment or default
AGENT_HANDLE="${AGENT_HANDLE:-$(whoami)}"
EXPORT_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

python3 - "$RULES_FILE" "$AGENT_HANDLE" "$EXPORT_TIMESTAMP" "$CATEGORY_FILTER" "$SCRIPT_NAME" << 'PYTHON'
import json, sys, hashlib, fcntl
from datetime import datetime

rules_path = sys.argv[1]
agent_handle = sys.argv[2]
export_timestamp = sys.argv[3]
category_filter = sys.argv[4] if len(sys.argv) > 4 else ""
script_name = sys.argv[5] if len(sys.argv) > 5 else ""

def calculate_rule_hash(rule):
    """Calculate SHA256 hash of rule content for integrity verification."""
    # Normalize rule content for consistent hashing
    content = json.dumps(rule, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def sanitize_rule(rule):
    """Remove agent-specific fields that shouldn't be shared."""
    # Fields to keep in export
    keep_fields = {
        "id", "type", "category", "rule", "reason", 
        "created", "source_lesson", "confidence_score",
        "last_validated", "validation_count"
    }
    
    sanitized = {k: v for k, v in rule.items() if k in keep_fields}
    return sanitized

# Load rules
try:
    with open(rules_path, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        rules_data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"ERROR: Could not load rules.json: {e}", file=sys.stderr)
    sys.exit(1)

all_rules = rules_data.get("rules", [])

# Filter by category if specified
if category_filter:
    rules = [r for r in all_rules if r.get("category") == category_filter]
    filter_applied = True
else:
    rules = all_rules
    filter_applied = False

# Calculate statistics by category
categories = {}
rule_types = {}
for r in all_rules:
    cat = r.get("category", "unknown")
    rtype = r.get("type", "UNKNOWN")
    categories[cat] = categories.get(cat, 0) + 1
    rule_types[rtype] = rule_types.get(rtype, 0) + 1

# Build export structure
export = {
    "metadata": {
        "export_version": "1.4.0",
        "export_format": "learning-loop-rules",
        "agent_handle": agent_handle,
        "exported_at": export_timestamp,
        "source_workspace": rules_path.replace("/memory/learning/rules.json", ""),
        "filter_applied": filter_applied,
        "filter_category": category_filter if category_filter else None,
        "total_rules_in_source": len(all_rules),
        "exported_rules_count": len(rules)
    },
    "statistics": {
        "categories": categories,
        "rule_types": rule_types,
        "avg_confidence": round(
            sum(r.get("confidence_score", 0.9) for r in rules) / len(rules), 2
        ) if rules else 0
    },
    "rules": []
}

# Process each rule
for rule in rules:
    rule_export = sanitize_rule(rule)
    rule_export["_hash"] = calculate_rule_hash(rule_export)
    rule_export["_original_id"] = rule.get("id")
    export["rules"].append(rule_export)

# Calculate manifest hash for the entire export
manifest_content = json.dumps(export["metadata"], sort_keys=True) + json.dumps(export["rules"], sort_keys=True)
export["metadata"]["manifest_hash"] = hashlib.sha256(manifest_content.encode('utf-8')).hexdigest()[:16]

# Output
print(json.dumps(export, indent=2))

# Summary to stderr
print(f"\nExport complete:", file=sys.stderr)
print(f"  Rules exported: {len(rules)} / {len(all_rules)} total", file=sys.stderr)
print(f"  Categories: {', '.join(sorted(categories.keys()))}", file=sys.stderr)
print(f"  Agent: {agent_handle}", file=sys.stderr)
print(f"  Timestamp: {export_timestamp}", file=sys.stderr)
if filter_applied:
    print(f"  Filter: category = '{category_filter}'", file=sys.stderr)
print(f"  Manifest hash: {export['metadata']['manifest_hash']}", file=sys.stderr)

PYTHON

exit_code=$?

exit $exit_code
