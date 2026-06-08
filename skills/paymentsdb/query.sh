#!/usr/bin/env bash
set -euo pipefail

# ---- Manually inject credentials here ----
# Go to https://paymentsdb.com to provision a read only postgres database
# and then modify `your_username` & `your_password`.
PGHOST="aws-1-us-east-1.pooler.supabase.com"
PGPORT="5432"
PGDATABASE="postgres"
PGUSER="postgres.your_username"
PGPASSWORD="your_password"
# ----------------------------------------

usage() {
  cat <<'EOF'
Usage:
  ./query.sh "SQL_QUERY"

Examples:
  ./query.sh "SELECT now();"
  ./query.sh "SELECT * FROM users LIMIT 5;"

Notes:
  - Requires psql in PATH.
  - SQL is passed as a single argument (quote it).
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 ]]; then
  echo "Error: missing SQL query." >&2
  usage >&2
  exit 1
fi

SQL="$1"

export PGPASSWORD

# -X: don't read ~/.psqlrc (more predictable for scripts)
# -v ON_ERROR_STOP=1: fail if SQL errors
# -q: quiet-ish (optional)
# -A -t: unaligned output, tuples only (useful for scripting; remove if you want pretty tables)
psql \
  -X \
  -v ON_ERROR_STOP=1 \
  -h "$PGHOST" \
  -p "$PGPORT" \
  -d "$PGDATABASE" \
  -U "$PGUSER" \
  -A -t \
  -c "$SQL"