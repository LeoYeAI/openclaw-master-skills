#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA_FILE="${SCRIPT_DIR}/schema.sql"

# Default connection settings
DB_HOST="${SURREALDB_HOST:-http://localhost:8000}"
DB_USER="${SURREALDB_USER:-root}"
DB_PASS="${SURREALDB_PASS:-root}"
DB_NS="${SURREALDB_NS:-openclaw}"
DB_DB="${SURREALDB_DB:-memory}"

echo "=== Initializing SurrealDB Memory Schema ==="
echo "Host: $DB_HOST"
echo "Namespace: $DB_NS"
echo "Database: $DB_DB"
echo ""

# Check if surreal is available
if ! command -v surreal &> /dev/null; then
    echo "ERROR: surreal command not found. Run install.sh first."
    exit 1
fi

# Check if server is running
echo "Checking database connection..."
if ! curl -s "${DB_HOST}/health" > /dev/null 2>&1; then
    echo ""
    echo "WARNING: Database not responding at $DB_HOST"
    echo ""
    echo "Start the database first:"
    echo "  surreal start --user root --pass root file:~/.openclaw/memory/knowledge.db"
    echo ""
    read -p "Start database now? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    
    # Start database in background
    DATA_DIR="${HOME}/.openclaw/memory"
    mkdir -p "$DATA_DIR"
    surreal start --user "$DB_USER" --pass "$DB_PASS" "file:${DATA_DIR}/knowledge.db" &
    SURREAL_PID=$!
    echo "Started SurrealDB (PID: $SURREAL_PID)"
    sleep 2
fi

# Import schema
echo ""
echo "Importing schema..."
surreal import \
    --conn "$DB_HOST" \
    --user "$DB_USER" \
    --pass "$DB_PASS" \
    --ns "$DB_NS" \
    --db "$DB_DB" \
    "$SCHEMA_FILE"

echo ""
echo "=== Schema Initialized Successfully ==="
echo ""
echo "Database ready at: $DB_HOST"
echo "Namespace: $DB_NS"
echo "Database: $DB_DB"
echo ""
echo "Test with:"
echo "  surreal sql --conn $DB_HOST --user $DB_USER --pass $DB_PASS --ns $DB_NS --db $DB_DB"
