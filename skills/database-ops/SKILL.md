---
name: database-ops
description: "Use when working with databases — queries, migrations, backups, schema inspection, and troubleshooting for PostgreSQL, SQLite, MySQL, and MongoDB."
version: 1.0.0
author: Papi
license: MIT
metadata:
  hermes:
    tags: [database, postgres, sqlite, mysql, mongodb, sql, migrations, backups]
    related_skills: [docker-ops, security-audit]
---

# Database Ops

## Overview

Working with databases from the command line: running queries, managing migrations, inspecting schemas, creating backups, and troubleshooting common issues. Covers PostgreSQL, SQLite, MySQL, and MongoDB.

## When to Use

- Running ad-hoc queries against a database
- Creating or running migrations
- Inspecting schema, tables, indexes
- Creating backups or restoring from backup
- Debugging connection or performance issues
- Importing/exporting data

Don't use for:
- ORM-specific tasks (use the application's migration tools)
- Database server installation (use docker-ops for containerized DBs)

## PostgreSQL

### Connection

```bash
# Local socket
psql -U postgres -d mydb

# Remote / Docker
psql -h localhost -p 5432 -U postgres -d mydb
PGPASSWORD=secret psql -h host -U user -d mydb

# Connection string
psql "postgres://user:pass@host:5432/mydb?sslmode=require"

# From inside Docker container
docker exec -it postgres-db psql -U postgres -d mydb
```

### Essential Queries

```sql
-- List databases
\l

-- Connect to database
\c mydb

-- List tables
\dt

-- Describe table
\d tablename
\d+ tablename              -- More detail (size, description)

-- List indexes
\di

-- List schemas
\dn

-- Table sizes
SELECT relname AS table, pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC;

-- Active connections
SELECT pid, usename, datname, client_addr, state, query
FROM pg_stat_activity WHERE state = 'active';

-- Kill a stuck query
SELECT pg_terminate_backend(pid);

-- Long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;

-- Locks
SELECT blocked_locks.pid AS blocked_pid,
       blocking_locks.pid AS blocking_pid,
       blocked_activity.query AS blocked_query,
       blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE blocked_locks.granted = false AND blocking_locks.granted = true;
```

### Migrations

```bash
# Using raw SQL files
psql -U postgres -d mydb -f migrations/001_create_users.sql

# Using pg_dump for schema-only export
pg_dump -U postgres --schema-only mydb > schema.sql

# Apply multiple migrations in order
for f in migrations/*.sql; do
  echo "Applying $f..."
  psql -U postgres -d mydb -f "$f" || exit 1
done

# Common migration frameworks
# Python: alembic upgrade head
# Node: npx knex migrate:latest
# Rails: rails db:migrate
```

### Backup & Restore

```bash
# Full backup (custom format, recommended)
pg_dump -U postgres -F c -f mydb.backup mydb

# Plain SQL backup
pg_dump -U postgres mydb > mydb.sql

# Compressed backup
pg_dump -U postgres mydb | gzip > mydb.sql.gz

# Backup specific tables only
pg_dump -U postgres -t users -t orders mydb > tables.sql

# Restore from custom format
pg_restore -U postgres -d mydb mydb.backup

# Restore from plain SQL
psql -U postgres -d mydb < mydb.sql

# Restore from compressed
gunzip -c mydb.sql.gz | psql -U postgres -d mydb

# Full cluster backup
pg_dumpall -U postgres > cluster.sql
```

### Copy Data (CSV Import/Export)

```sql
-- Export to CSV
COPY (SELECT * FROM users WHERE active = true) TO '/tmp/users.csv' WITH CSV HEADER;

-- Import from CSV
COPY users FROM '/tmp/users.csv' WITH CSV HEADER;

-- Using psql \copy (no superuser needed)
\copy users TO '/tmp/users.csv' WITH CSV HEADER
\copy users FROM '/tmp/users.csv' WITH CSV HEADER
```

## SQLite

### Connection

```bash
sqlite3 mydb.db
sqlite3 :memory:          # In-memory database
```

### Essential Commands

```sql
-- List tables
.tables

-- Schema
.schema tablename
.schema                    -- All tables

-- Full table info
PRAGMA table_info(tablename);

-- Indexes
.indexes tablename

-- Enable foreign keys (off by default!)
PRAGMA foreign_keys = ON;

-- Check foreign key violations
PRAGMA foreign_key_check;

-- Export to SQL
.output backup.sql
.dump
.output stdout

-- Import from SQL
.read backup.sql

-- Export to CSV
.mode csv
.headers on
.output data.csv
SELECT * FROM users;
.output stdout

-- Import from CSV
.mode csv
.import data.csv users

-- Performance analysis
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';

-- Database integrity check
PRAGMA integrity_check;
```

### Backup

```bash
# Safe backup (handles concurrent writes)
sqlite3 mydb.db ".backup backup.db"

# Simple copy (only safe if no writes happening)
cp mydb.db mydb_backup.db
```

## MySQL

### Connection

```bash
mysql -u root -p -h localhost mydb
mysql -u root -pmypassword mydb     # Password on command line (not recommended)
```

### Essential Queries

```sql
-- List databases
SHOW DATABASES;

-- Use database
USE mydb;

-- List tables
SHOW TABLES;

-- Describe table
DESCRIBE tablename;
SHOW CREATE TABLE tablename;

-- Indexes
SHOW INDEX FROM tablename;

-- Table sizes
SELECT table_name, data_length + index_length AS size_bytes,
       ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables WHERE table_schema = 'mydb' ORDER BY size_bytes DESC;

-- Active processes
SHOW PROCESSLIST;
SHOW FULL PROCESSLIST;

-- Kill query
KILL <id>;

-- Slow query log
SHOW VARIABLES LIKE 'slow_query_log%';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

### Backup & Restore

```bash
# Full backup
mysqldump -u root -p mydb > mydb.sql

# Compressed
mysqldump -u root -p mydb | gzip > mydb.sql.gz

# Specific tables
mysqldump -u root -p mydb users orders > tables.sql

# Schema only
mysqldump -u root -p --no-data mydb > schema.sql

# Data only
mysqldump -u root -p --no-create-info mydb > data.sql

# Restore
mysql -u root -p mydb < mydb.sql
gunzip < mydb.sql.gz | mysql -u root -p mydb
```

## MongoDB

### Connection

```bash
mongosh "mongodb://localhost:27017/mydb"
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/mydb"
```

### Essential Operations

```javascript
// List databases
show dbs

// Use database
use mydb

// List collections
show collections

// Find documents
db.users.find({ active: true })
db.users.findOne({ email: "test@example.com" })

// Count
db.users.countDocuments({ active: true })

// Aggregate
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: { _id: "$userId", total: { $sum: "$amount" } } },
  { $sort: { total: -1 } },
  { $limit: 10 }
])

// Indexes
db.users.getIndexes()
db.users.createIndex({ email: 1 }, { unique: true })

// Explain query
db.users.find({ email: "test@example.com" }).explain("executionStats")

// Collection stats
db.users.stats()
```

### Backup & Restore

```bash
# Full database backup
mongodump --uri="mongodb://localhost:27017/mydb" --out=/backup/

# Restore
mongorestore --uri="mongodb://localhost:27017/mydb" /backup/mydb/

# Specific collection
mongodump --uri="mongodb://localhost:27017/mydb" --collection=users --out=/backup/

# Export to JSON
mongoexport --uri="mongodb://localhost:27017/mydb" --collection=users --out=users.json

# Import from JSON
mongoimport --uri="mongodb://localhost:27017/mydb" --collection=users --file=users.json
```

## Performance Troubleshooting

### Slow Queries (All SQL)

1. **Find the slow queries** — check slow query logs or pg_stat_activity
2. **EXPLAIN the query** — look for sequential scans on large tables
3. **Check indexes** — is there an index on the filtered column?
4. **Check row counts** — is the table bigger than expected?
5. **Check locks** — is the query waiting on another transaction?

### Common Fixes

```sql
-- Add missing index (PostgreSQL)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Add composite index for multi-column queries
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Analyze table to update statistics (PostgreSQL)
ANALYZE users;

-- Check index usage (PostgreSQL)
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes ORDER BY idx_scan;

-- Find unused indexes (candidates for removal)
SELECT schemaname, relname, indexrelname
FROM pg_stat_user_indexes WHERE idx_scan = 0;
```

## Common Pitfalls

1. **No backups before schema changes.** Always backup before running migrations. No exceptions.

2. **SQLite foreign keys off by default.** `PRAGMA foreign_keys = ON;` must be set every connection. Orphans will sneak in otherwise.

3. **Running migrations in production without testing.** Test on a copy first. Always.

4. **COPY vs \copy in PostgreSQL.** `COPY` runs as the server user and needs absolute paths. `\copy` runs as the client user and handles permissions correctly. Prefer `\copy`.

5. **Not using CONCURRENTLY for indexes on live tables.** `CREATE INDEX` locks the table. `CREATE INDEX CONCURRENTLY` doesn't. Use it in production.

6. **Forgetting VACUUM in PostgreSQL.** Dead rows accumulate. `VACUUM ANALYZE` regularly, or enable autovacuum.

7. **MongoDB default concerns.** Writes may not be durable with default write concern. Use `w: 1` or `w: "majority"` for important data.

## Verification Checklist

- [ ] Backup created before any schema changes
- [ ] Migrations tested on a copy of production data
- [ ] Slow queries identified and indexed
- [ ] Foreign keys enforced (especially SQLite)
- [ ] Connection strings don't contain hardcoded passwords in code (use env vars)
- [ ] Database size monitored — unexpected growth investigated
