---
name: sql-toolkit
description: Query, design, migrate, and optimize SQL databases. Use when working with SQLite, PostgreSQL, or MySQL — schema design, writing queries, creating migrations, indexing, backup/restore, and debugging slow queries. No ORMs required.
metadata: {"clawdbot":{"emoji":"🗄️","requires":{"anyBins":["sqlite3","psql","mysql"]},"os":["linux","darwin","win32"]}}
---

# SQL Toolkit

Work with relational databases directly from the command line. Covers SQLite, PostgreSQL, and MySQL with patterns for schema design, querying, migrations, indexing, and operations.

## When to Use

- Creating or modifying database schemas
- Writing complex queries (joins, aggregations, window functions, CTEs)
- Building migration scripts
- Optimizing slow queries with indexes and EXPLAIN
- Backing up and restoring databases
- Quick data exploration with SQLite (zero setup)

## SQLite (Zero Setup)

SQLite is included with Python and available on every system. Use it for local data, prototyping, and single-file databases.

### Quick Start

```bash
# Create/open a database
sqlite3 mydb.sqlite

# Import CSV directly
sqlite3 mydb.sqlite ".mode csv" ".import data.csv mytable" "SELECT COUNT(*) FROM mytable;"

# One-liner queries
sqlite3 mydb.sqlite "SELECT * FROM users WHERE created_at > '2026-01-01' LIMIT 10;"

# Export to CSV
sqlite3 -header -csv mydb.sqlite "SELECT * FROM orders;" > orders.csv

# Interactive mode with headers and columns
sqlite3 -header -column mydb.sqlite
```

### Schema Operations

```sql
-- Create table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Create with foreign key
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total REAL NOT NULL CHECK(total >= 0),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','paid','shipped','cancelled')),
    created_at TEXT DEFAULT (datetime('now'))
);

-- Add column
ALTER TABLE users ADD COLUMN phone TEXT;

-- Create index
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- View schema
.schema users
.tables
```

## PostgreSQL

### Connection

```bash
# Connect
psql -h localhost -U myuser -d mydb

# Connection string
psql "postgresql://user:pass@localhost:5432/mydb?sslmode=require"

# Run single query
psql -h localhost -U myuser -d mydb -c "SELECT NOW();"

# Run SQL file
psql -h localhost -U myuser -d mydb -f migration.sql

# List databases
psql -l
```

### Schema Design Patterns

```sql
-- Use UUIDs for distributed-friendly primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin','moderator')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT users_email_unique UNIQUE(email)
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Enum type (PostgreSQL-specific)
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status order_status NOT NULL DEFAULT 'pending',
    total NUMERIC(10,2) NOT NULL CHECK(total >= 0),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partial index (only index active orders — smaller, faster)
CREATE INDEX idx_orders_active ON orders(user_id, created_at)
    WHERE status NOT IN ('delivered', 'cancelled');

-- GIN index for JSONB queries
CREATE INDEX idx_orders_metadata ON orders USING GIN(metadata);
```

### JSONB Queries (PostgreSQL)

```sql
-- Store JSON
INSERT INTO orders (user_id, total, metadata)
VALUES ('...', 99.99, '{"source": "web", "coupon": "SAVE10", "items": [{"sku": "A1", "qty": 2}]}');

-- Query JSON fields
SELECT * FROM orders WHERE metadata->>'source' = 'web';
SELECT * FROM orders WHERE metadata->'items' @> '[{"sku": "A1"}]';
SELECT metadata->>'coupon' AS coupon, COUNT(*) FROM orders GROUP BY 1;

-- Update JSON field
UPDATE orders SET metadata = jsonb_set(metadata, '{source}', '"mobile"') WHERE id = '...';
```

## MySQL

### Connection

```bash
mysql -h localhost -u root -p mydb
mysql -h localhost -u root -p -e "SELECT NOW();" mydb
```

### Key Differences from PostgreSQL

```sql
-- Auto-increment (not SERIAL)
CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- JSON type (MySQL 5.7+)
CREATE TABLE orders (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    metadata JSON,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Query JSON
SELECT * FROM orders WHERE JSON_EXTRACT(metadata, '$.source') = 'web';
-- Or shorthand:
SELECT * FROM orders WHERE metadata->>'$.source' = 'web';
```

## Query Patterns

### Joins

```sql
-- Inner join (only matching rows)
SELECT u.name, o.total, o.status
FROM users u
INNER JOIN orders o ON o.user_id = u.id
WHERE o.created_at > '2026-01-01';

-- Left join (all users, even without orders)
SELECT u.name, COUNT(o.id) AS order_count, COALESCE(SUM(o.total), 0) AS total_spent
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;

-- Self-join (find users with same email domain)
SELECT a.name, b.name, SPLIT_PART(a.email, '@', 2) AS domain
FROM users a
JOIN users b ON SPLIT_PART(a.email, '@', 2) = SPLIT_PART(b.email, '@', 2)
WHERE a.id < b.id;
```

### Aggregations

```sql
-- Group by with having
SELECT status, COUNT(*) AS cnt, SUM(total) AS revenue
FROM orders
GROUP BY status
HAVING COUNT(*) > 10
ORDER BY revenue DESC;

-- Running total (window function)
SELECT date, revenue,
    SUM(revenue) OVER (ORDER BY date) AS cumulative_revenue
FROM daily_sales;

-- Rank within groups
SELECT user_id, total,
    RANK() OVER (PARTITION BY user_id ORDER BY total DESC) AS rank
FROM orders;

-- Moving average (last 7 entries)
SELECT date, revenue,
    AVG(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7
FROM daily_sales;
```

### Common Table Expressions (CTEs)

```sql
-- Readable multi-step queries
WITH monthly_revenue AS (
    SELECT DATE_TRUNC('month', created_at) AS month,
           SUM(total) AS revenue
    FROM orders
    WHERE status = 'paid'
    GROUP BY 1
),
growth AS (
    SELECT month, revenue,
           LAG(revenue) OVER (ORDER BY month) AS prev_revenue,
           ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) /
                 NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100, 1) AS growth_pct
    FROM monthly_revenue
)
SELECT * FROM growth ORDER BY month;

-- Recursive CTE (org chart / tree traversal)
WITH RECURSIVE org_tree AS (
    SELECT id, name, manager_id, 0 AS depth
    FROM employees
    WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, t.depth + 1
    FROM employees e
    JOIN org_tree t ON e.manager_id = t.id
)
SELECT REPEAT('  ', depth) || name AS org_chart FROM org_tree ORDER BY depth, name;
```

## Migrations

### Manual Migration Script Pattern

```bash
#!/bin/bash
# migrate.sh - Run numbered SQL migration files
DB_URL="${1:?Usage: migrate.sh <db-url>}"
MIGRATIONS_DIR="./migrations"

# Create tracking table
psql "$DB_URL" -c "CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW()
);"

# Run pending migrations in order
for file in $(ls "$MIGRATIONS_DIR"/*.sql | sort); do
    version=$(basename "$file" .sql)
    already=$(psql "$DB_URL" -tAc "SELECT 1 FROM schema_migrations WHERE version='$version';")
    if [ "$already" = "1" ]; then
        echo "SKIP: $version (already applied)"
        continue
    fi
    echo "APPLY: $version"
    psql "$DB_URL" -f "$file" && \
    psql "$DB_URL" -c "INSERT INTO schema_migrations (version) VALUES ('$version');" || {
        echo "FAILED: $version"
        exit 1
    }
done
echo "All migrations applied."
```

### Migration File Convention

```
migrations/
  001_create_users.sql
  002_create_orders.sql
  003_add_users_phone.sql
  004_add_orders_metadata_index.sql
```

Each file:
```sql
-- 003_add_users_phone.sql
-- Up
ALTER TABLE users ADD COLUMN phone TEXT;

-- To reverse: ALTER TABLE users DROP COLUMN phone;
```

## Query Optimization

### EXPLAIN (PostgreSQL)

```sql
-- Show query plan
EXPLAIN SELECT * FROM orders WHERE user_id = '...' AND status = 'paid';

-- Show actual execution times
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = '...' AND status = 'paid';
```

**What to look for:**
- `Seq Scan` on large tables → needs an index
- `Nested Loop` with large row counts → consider `Hash Join` (may need more `work_mem`)
- `Rows Removed by Filter` being high → index doesn't cover the filter
- Actual rows far from estimated → run `ANALYZE tablename;` to update statistics

### Index Strategy

```sql
-- Single column (most common)
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Composite (for queries filtering on both columns)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
-- Column ORDER matters: put equality filters first, range filters last

-- Covering index (includes data columns to avoid table lookup)
CREATE INDEX idx_orders_covering ON orders(user_id, status) INCLUDE (total, created_at);

-- Partial index (smaller, faster — only index what you query)
CREATE INDEX idx_orders_pending ON orders(user_id) WHERE status = 'pending';

-- Check unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexname NOT LIKE '%pkey%'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### SQLite EXPLAIN

```sql
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id = 5;
-- Look for: SCAN (bad) vs SEARCH USING INDEX (good)
```

## Backup & Restore

### PostgreSQL

```bash
# Full dump (custom format, compressed)
pg_dump -Fc -h localhost -U myuser mydb > backup.dump

# Restore
pg_restore -h localhost -U myuser -d mydb --clean --if-exists backup.dump

# SQL dump (portable, readable)
pg_dump -h localhost -U myuser mydb > backup.sql

# Dump specific tables
pg_dump -h localhost -U myuser -t users -t orders mydb > partial.sql

# Copy table to CSV
psql -c "\copy (SELECT * FROM users) TO 'users.csv' CSV HEADER"
```

### SQLite

```bash
# Backup (just copy the file, but use .backup for consistency)
sqlite3 mydb.sqlite ".backup backup.sqlite"

# Dump to SQL
sqlite3 mydb.sqlite .dump > backup.sql

# Restore from SQL
sqlite3 newdb.sqlite < backup.sql
```

### MySQL

```bash
# Dump
mysqldump -h localhost -u root -p mydb > backup.sql

# Restore
mysql -h localhost -u root -p mydb < backup.sql
```

## Tips

- Always use parameterized queries in application code — never concatenate user input into SQL
- Use `TIMESTAMPTZ` (not `TIMESTAMP`) in PostgreSQL for timezone-aware dates
- Set `PRAGMA journal_mode=WAL;` in SQLite for concurrent read performance
- Use `EXPLAIN` before deploying any query that runs on large tables
- PostgreSQL: `\d+ tablename` shows columns, indexes, and size. `\di+` lists all indexes with sizes
- For quick data exploration, import any CSV into SQLite: `sqlite3 :memory: ".mode csv" ".import file.csv t" "SELECT ..."`
