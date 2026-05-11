#!/bin/bash
# query.sh - Quick SQL query execution
# Usage: ./query.sh [options] [query or --file]

# Configuration - update these for your database
DB_TYPE="${DB_TYPE:-sqlite}"  # sqlite, postgres, mysql
DB_CONNECTION="${DB_CONNECTION:-}"

show_help() {
    echo "SQL Query Tool"
    echo "=============="
    echo ""
    echo "Usage:"
    echo "  $0 \"SELECT * FROM table\"           - Run inline query"
    echo "  $0 --file queries/report.sql       - Run query from file"
    echo "  $0 --file query.sql --output out.csv - Save results to CSV"
    echo ""
    echo "Options:"
    echo "  --file, -f    SQL file to execute"
    echo "  --output, -o  Output file (CSV)"
    echo "  --db          Database connection string"
    echo "  --type        Database type (sqlite, postgres, mysql)"
    echo ""
    echo "Environment Variables:"
    echo "  DB_TYPE       Database type (default: sqlite)"
    echo "  DB_CONNECTION Database connection string"
    echo ""
    echo "Examples:"
    echo "  DB_CONNECTION='host=localhost dbname=mydb' $0 'SELECT COUNT(*) FROM users'"
    echo "  $0 --file queries/daily-report.sql --output reports/daily.csv"
}

run_query() {
    local query="$1"
    local output="$2"
    
    case "$DB_TYPE" in
        sqlite)
            if [ -n "$output" ]; then
                sqlite3 -header -csv "$DB_CONNECTION" "$query" > "$output"
            else
                sqlite3 -header -column "$DB_CONNECTION" "$query"
            fi
            ;;
        postgres|postgresql)
            if [ -n "$output" ]; then
                psql "$DB_CONNECTION" -c "COPY ($query) TO STDOUT WITH CSV HEADER" > "$output"
            else
                psql "$DB_CONNECTION" -c "$query"
            fi
            ;;
        mysql)
            if [ -n "$output" ]; then
                mysql $DB_CONNECTION -e "$query" | sed 's/\t/,/g' > "$output"
            else
                mysql $DB_CONNECTION -e "$query"
            fi
            ;;
        *)
            echo "Unsupported database type: $DB_TYPE"
            echo "Supported: sqlite, postgres, mysql"
            exit 1
            ;;
    esac
}

# Parse arguments
QUERY=""
FILE=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --file|-f)
            FILE="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT="$2"
            shift 2
            ;;
        --db)
            DB_CONNECTION="$2"
            shift 2
            ;;
        --type)
            DB_TYPE="$2"
            shift 2
            ;;
        *)
            QUERY="$1"
            shift
            ;;
    esac
done

# Get query from file or argument
if [ -n "$FILE" ]; then
    if [ ! -f "$FILE" ]; then
        echo "❌ File not found: $FILE"
        exit 1
    fi
    QUERY=$(cat "$FILE")
fi

if [ -z "$QUERY" ]; then
    show_help
    exit 1
fi

if [ -z "$DB_CONNECTION" ]; then
    echo "❌ No database connection configured"
    echo ""
    echo "Set DB_CONNECTION environment variable or use --db flag"
    echo "Example: DB_CONNECTION='mydb.sqlite' $0 'SELECT * FROM users'"
    exit 1
fi

echo "🔍 Running query..."
run_query "$QUERY" "$OUTPUT"

if [ -n "$OUTPUT" ]; then
    echo "✅ Results saved to: $OUTPUT"
fi
