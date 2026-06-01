---
name: relational-database-mcp-cloudbase
description: This is the required documentation for agents operating on the CloudBase Relational Database. It lists the only four supported tools for running SQL and managing security rules. Read the full content to understand why you must NOT use standard Application SDKs and how to safely execute INSERT, UPDATE, or DELETE operations without corrupting production data.
alwaysApply: false
---

## When to use this skill

Use this skill when an **agent** needs to operate on **CloudBase Relational Database via MCP tools**, for example:

- Inspecting or querying data in tables
- Modifying data or schema (INSERT/UPDATE/DELETE/DDL)
- Reading or changing table security rules

Do **NOT** use this skill for:

- Building Web or Node.js applications that talk to CloudBase Relational Database (use the Web/Node Relational Database skills)
- Auth flows or user identity (use the Auth skills)

## How to use this skill (for a coding agent)

1. **Recognize MCP context**
   - If you can call tools like `executeReadOnlySQL`, `executeWriteSQL`, `readSecurityRule`, `writeSecurityRule`, you are in MCP context.
   - In this context, **never initialize SDKs for CloudBase Relational Database**; use MCP tools instead.

2. **Pick the right tool for the job**
   - Reads → `executeReadOnlySQL`
   - Writes/DDL → `executeWriteSQL`
   - Inspect rules → `readSecurityRule`
   - Change rules → `writeSecurityRule`

3. **Always be explicit about safety**
   - Before destructive operations (DELETE, DROP, etc.), summarize what you are about to run and why.
   - Prefer running read-only SELECTs first to verify assumptions.

---

## Available MCP tools (CloudBase Relational Database)

These tools are the **only** supported way to interact with CloudBase Relational Database via MCP:

### 1. `executeReadOnlySQL`

- **Purpose:** Run `SELECT` queries (read-only).
- **Use for:**
  - Listing rows, aggregations, joins.
  - Inspecting data before changing it.

**Example call (conceptual):**

```sql
SELECT id, email FROM users WHERE active = true ORDER BY created_at DESC LIMIT 50;
```

Call this through the MCP tool instead of embedding SQL in code.

### 2. `executeWriteSQL`

- **Purpose:** Run **write or DDL** statements:
  - `INSERT`, `UPDATE`, `DELETE`
  - `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`
- **Use for:**
  - Data migrations
  - Fixing or seeding data
  - Schema changes

**Important:** When creating a new table, you **must** include the `_openid` column for per-user access control:

```sql
_openid VARCHAR(64) DEFAULT '' NOT NULL
```

> 💡 **Note about `_openid`**: When a user is logged in, the `_openid` field is **automatically populated by the server** with the current user's identity. You do NOT need to manually set this field in INSERT operations - the server will fill it automatically based on the authenticated user's session.

Before calling this tool, **confirm**:

- The target tables and conditions are correct.
- You have run a corresponding `SELECT` via `executeReadOnlySQL` when appropriate.

### 3. `readSecurityRule`

- **Purpose:** Read security rules for a given table.
- **Use for:**
  - Understanding who can read/write a table.
  - Auditing permissions on sensitive tables.

Security rule types typically include:

- `READONLY` – anyone can read, no one can write
- `PRIVATE` – only authenticated users can read/write
- `ADMINWRITE` – anyone can read, only admins can write
- `ADMINONLY` – only admins can read/write
- `CUSTOM` – custom security logic

### 4. `writeSecurityRule`

- **Purpose:** Set or update security rules for a table.
- **Use for:**
  - Hardening access to sensitive data
  - Opening up read access while restricting writes
  - Applying custom rules when needed

When using this tool:

- Clearly explain the **intent** (who should read/write what).
- Prefer standard rule types (`READONLY`, `PRIVATE`, etc.) before `CUSTOM`.

---

## Scenario 1: Safely inspect data in a table

1. Use `executeReadOnlySQL` with a limited `SELECT`:
   - Include a `LIMIT` clause.
   - Filter by relevant conditions.
2. Review the result set and confirm it matches expectations.

This pattern prevents accidental full-table scans and gives you context before any write operations.

---

## Scenario 2: Apply a schema change

1. Use `executeReadOnlySQL` to inspect the current schema or data (if needed).
2. Plan the `CREATE TABLE` / `ALTER TABLE` statement.
3. Run it once via `executeWriteSQL`.
4. Optionally, validate by running `SELECT` again.

Always describe:

- What schema change you are making.
- Why it is safe in the current context.

---

## Scenario 3: Tighten security rules on a sensitive table

1. Call `readSecurityRule` for the table to see current settings.
2. Decide on the target rule (e.g., from `READONLY` → `PRIVATE`).
3. Explain the change and why it matches the user’s requirements.
4. Call `writeSecurityRule` with the new rule.
5. Optionally, re-read the rule to confirm the update.

---

## Key principle: MCP tools vs SDKs

- **MCP tools** are for **agent operations** and **database management**:
  - Run ad-hoc SQL.
  - Inspect and change security rules.
  - Do not depend on application auth state.

- **SDKs** are for **application code**:
  - Frontend Web apps → Web Relational Database skill.
  - Backend Node apps → Node Relational Database quickstart.

When working as an MCP agent, **always prefer these MCP tools** for CloudBase Relational Database, and avoid mixing them with SDK initialization in the same flow.
