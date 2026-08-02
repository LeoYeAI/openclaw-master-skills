#!/bin/bash
# Migrate SurrealDB Knowledge Graph to v2 schema
# Adds: Episodes, Working Memory, Scoping, Outcome Calibration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA_FILE="$SCRIPT_DIR/schema-v2.sql"
SURREAL_URL="${SURREAL_URL:-http://localhost:8000}"
SURREAL_NS="${SURREAL_NS:-openclaw}"
SURREAL_DB="${SURREAL_DB:-memory}"
SURREAL_USER="${SURREAL_USER:-root}"
SURREAL_PASS="${SURREAL_PASS:-root}"

echo "=== SurrealDB Memory v2 Migration ==="
echo "URL: $SURREAL_URL"
echo "NS/DB: $SURREAL_NS/$SURREAL_DB"
echo ""

# Check if SurrealDB is running
if ! curl -s "$SURREAL_URL/health" > /dev/null 2>&1; then
    echo "ERROR: SurrealDB not reachable at $SURREAL_URL"
    echo "Start it with: surreal start --user root --pass root file:~/.openclaw/memory/knowledge.db"
    exit 1
fi

# Check if schema file exists
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "ERROR: Schema file not found: $SCHEMA_FILE"
    exit 1
fi

echo "Applying v2 schema..."
echo ""

# Use surreal CLI if available, otherwise use HTTP API
if command -v surreal &> /dev/null || [ -f ~/.surrealdb/surreal ]; then
    SURREAL_BIN="${SURREAL_BIN:-$(command -v surreal || echo ~/.surrealdb/surreal)}"
    
    "$SURREAL_BIN" import \
        --endpoint "$SURREAL_URL" \
        --namespace "$SURREAL_NS" \
        --database "$SURREAL_DB" \
        --username "$SURREAL_USER" \
        --password "$SURREAL_PASS" \
        "$SCHEMA_FILE"
else
    # Use Python as fallback
    python3 << EOF
import sys
sys.path.insert(0, "$SCRIPT_DIR")

from surrealdb import Surreal

db = Surreal("$SURREAL_URL")
db.signin({"username": "$SURREAL_USER", "password": "$SURREAL_PASS"})
db.use("$SURREAL_NS", "$SURREAL_DB")

with open("$SCHEMA_FILE") as f:
    schema = f.read()

# Execute each statement
for stmt in schema.split(';'):
    stmt = stmt.strip()
    if stmt and not stmt.startswith('--'):
        try:
            db.query(stmt)
            print(f"✓ Executed: {stmt[:60]}...")
        except Exception as e:
            print(f"⚠ Warning: {e}")

print("\nSchema v2 applied successfully!")
EOF
fi

echo ""
echo "=== Migration Complete ==="
echo ""
echo "New capabilities:"
echo "  • Episodes table for task histories"
echo "  • Working memory snapshots"
echo "  • Scoped facts (global/client/agent)"
echo "  • Outcome-based confidence calibration"
echo "  • Context-aware retrieval functions"
echo ""
echo "Next steps:"
echo "  1. Update MCP config to use mcp-server-v2.py"
echo "  2. Create .working-memory/ directory in workspace"
echo "  3. Start using episode_* and working_memory_* tools"
echo ""
