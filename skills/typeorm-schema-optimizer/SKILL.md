---
name: typeorm-schema-optimizer
description: Optimize TypeORM entities for performance, query efficiency, migration safety, and relationship design — analyze decorators, indexes, eager loading, and connection pooling.
metadata:
  tags: ["typeorm", "orm", "database", "typescript", "optimization"]
---

# TypeORM Schema Optimizer

Analyze TypeORM entities for performance issues, query inefficiencies, missing indexes, relationship design problems, and migration risks. Use when reviewing TypeORM schemas, optimizing slow queries, or preparing for production scale.

## Usage

```
"Optimize my TypeORM entities"
"Check for N+1 queries in my TypeORM code"
"Audit TypeORM indexes and relations"
"Review migration safety for TypeORM changes"
```

## How It Works

### 1. Entity Discovery

```bash
# Find all TypeORM entities
grep -rn "@Entity\|@ViewEntity\|@ChildEntity" src/ | head -20
# Find repositories
grep -rn "extends Repository\|@InjectRepository\|getRepository" src/ | head -20
# Check TypeORM config
cat ormconfig.json 2>/dev/null || cat data-source.ts 2>/dev/null
```

### 2. Schema Analysis

**Column optimization:**
- Column types match actual data requirements
- Unnecessary `nullable: true` on required fields
- Missing `length` on string columns (default is VARCHAR(255) — wasteful or too short?)
- Enum columns using string instead of native enum type
- JSON columns where structured columns would be more queryable
- Missing default values for common patterns

**Index analysis:**
- Columns used in WHERE clauses without indexes
- Composite indexes for multi-column queries
- Covering indexes for SELECT-heavy queries
- Unique constraints for business rules
- Partial indexes for filtered queries
- Index on foreign key columns (TypeORM doesn't auto-create)

**Relationship design:**
- `eager: true` on relationships (loads every time, often unnecessary)
- Missing `cascade` options where needed
- Circular eager loading (infinite loops)
- `@ManyToMany` without join table customization
- Missing `onDelete` behavior (default is no action)
- Polymorphic relationships using discriminators correctly

### 3. Query Performance

- N+1 detection in repository methods
- Missing `leftJoinAndSelect` where data is accessed post-query
- `find` with deep relations instead of query builder
- Missing pagination on list queries
- Raw queries bypassing TypeORM benefits
- Transaction usage for multi-step writes

### 4. Connection & Pool

- Connection pool size appropriate for workload
- Idle connection timeout configured
- Read replicas configured for read-heavy workloads
- Connection error handling and retry logic
- Logging level appropriate for environment

### 5. Migration Safety

- Entity changes that generate destructive migrations
- Column type changes that lose data
- Index changes that lock tables
- Relationship changes that break foreign keys

## Output

```
## TypeORM Schema Analysis

**Entities:** 18 | **Relations:** 24 | **Indexes:** 12

### 🔴 Critical (3)
1. **Eager loading loop** — User → Posts (eager) → Author (eager) → Posts...
   → Remove `eager: true` from at least one side

2. **Missing index on FK** — Order.userId has no index
   With 500K orders, joins on userId cause full table scans
   → Add `@Index()` on `userId` column

3. **N+1 in getOrders()** — orders.service.ts:34
   Loads orders then iterates to access `order.items` individually
   → Use `relations: ['items']` or query builder with join

### 🟡 Improvements (4)
4. 6 entities with `eager: true` — performance risk at scale
5. VARCHAR(255) on `status` fields — use enum type (4 possible values)
6. Missing `onDelete: 'CASCADE'` on child entities
7. No read replica configured (DB CPU at 80%)

### ✅ Good Practices
- Proper use of table inheritance for payment types
- Transaction wrapping for order creation flow
- Soft delete with `@DeleteDateColumn`
```
