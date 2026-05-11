---
name: "zilliz-cloud"
version: "0.3.0"
description: "Manage Zilliz Cloud clusters and Milvus vector databases — cluster ops, collections, vector search, RBAC, backups, imports, and more via zilliz-cli."
tags: ["zilliz", "milvus", "vector-database", "semantic-search", "rag", "cloud", "database"]
metadata:
  openclaw:
    emoji: "\U0001F50D"
    homepage: "https://github.com/zilliztech/zilliz-plugin"
    primaryEnv: "ZILLIZ_API_KEY"
    requires:
      env:
        - ZILLIZ_API_KEY
      bins:
        - python3
        - zilliz
      os:
        - darwin
        - linux
    install:
      - kind: uv
        package: zilliz-cli
        bins:
          - zilliz
---

# Zilliz Cloud CLI Skill

Your Zilliz Cloud console in the terminal. This skill enables you to operate the `zilliz-cli`, bringing the full power of [Zilliz Cloud](https://zilliz.com/) — cluster management, collection operations, vector search, RBAC, backups, and more — through natural language.

## When to Use

Use this skill when the user wants to:
- Manage Zilliz Cloud clusters (create, delete, suspend, resume, modify)
- Work with Milvus collections (create, describe, load, release, drop)
- Perform vector operations (search, query, insert, upsert, delete)
- Manage indexes, databases, partitions
- Set up users, roles, and access control (RBAC)
- Create and manage backups or backup policies
- Import bulk data from cloud storage
- Check billing, usage, or invoices
- Monitor cluster and collection status

## Capabilities Overview

| Area | What You Can Do |
|------|----------------|
| **Clusters** | Create, delete, suspend, resume, modify |
| **Collections** | Create with custom schema, load, release, rename, drop |
| **Vectors** | Search, query, insert, upsert, delete |
| **Indexes** | Create, list, describe, drop |
| **Databases** | Create, list, describe, drop |
| **Users & Roles** | RBAC setup, privilege management |
| **Backups** | Create, restore, export, policy management |
| **Import** | Bulk data import from cloud storage |
| **Partitions** | Create, load, release, manage |
| **Monitoring** | Cluster status, collection stats |
| **Billing** | Usage, invoices, payment methods |
| **Projects** | Project and region management |

## Requirements

- Python 3.10+
- A [Zilliz Cloud](https://cloud.zilliz.com/) account (or local Milvus instance)

---

# Setup & Authentication

## Prerequisites

Before running any zilliz-cli command, verify the following in order:

1. **CLI installed and up to date?** Run `python3 -m pip install --upgrade zilliz-cli` to ensure the latest version is installed.
2. **Logged in?** Run `zilliz auth status`. If not logged in, guide through login (see below).
3. **Context set?** (Only for data-plane operations) Run `zilliz context current`. If no context, guide through context setup.

## Install / Upgrade CLI

```bash
python3 -m pip install --upgrade zilliz-cli
```

Verify installation:

```bash
zilliz --version
```

## Authentication

**IMPORTANT:** Login commands (`zilliz login`, `zilliz configure`) require an interactive terminal and CANNOT run inside the AI agent. Always instruct the user to run these in their own terminal.

Check if already logged in:

```bash
zilliz auth status
```

If not logged in, tell the user to open their own terminal and run one of the following:

**Option 1: Browser-based login (OAuth) — full feature access**

```
zilliz login
```

- Opens a browser for authentication
- Retrieves user info, organization data, and API keys
- Use `--no-browser` in headless environments (displays a URL to visit manually)

**Option 2a: API Key via login command**

```
zilliz login --api-key
```

**Option 2b: API Key via configure (legacy)**

```
zilliz configure
```

- Prompts for an API key (found in Zilliz Cloud console under API Keys)
- Limitations compared to OAuth login:
  - Organization switching not available
  - On Serverless clusters: database management, user/role management may be restricted
  - Some control-plane operations may require OAuth login

**Option 3: Environment variable**

User can add to their shell profile (`.zshrc` / `.bashrc`):

```
export ZILLIZ_API_KEY=<your-api-key>
```

After the user completes authentication, verify by running:

```bash
zilliz auth status
```

## Configure Subcommands

```bash
zilliz configure              # Interactive API key setup
zilliz configure list          # Show all config values
zilliz configure set <key> <value>  # Set a config value
zilliz configure get <key>     # Get a config value
zilliz configure clear         # Clear all credentials
```

## Switch Organization

These commands require an interactive terminal. Instruct the user to run in their own terminal:

```
# Interactive selection
zilliz auth switch

# Direct switch by org ID
zilliz auth switch <org-id>
```

## Logout

```bash
zilliz logout
```

## Set Cluster Context

Data-plane commands (collection, vector, index, etc.) require an active cluster context.

```bash
# Set by cluster ID (endpoint auto-resolved)
zilliz context set --cluster-id <cluster-id>

# Set with explicit endpoint
zilliz context set --cluster-id <cluster-id> --endpoint <url>

# Change database (default: "default")
zilliz context set --database <db-name>
```

## View Current Context

```bash
zilliz context current
```

## Output Format

All zilliz-cli commands support `--output json` for structured, machine-readable output:

```bash
zilliz cluster list --output json
zilliz collection describe --name <name> --output json
```

Available formats: `json`, `table`, `text`. Default is `text`.

## Cluster Type Differences

| Feature | Free | Serverless | Dedicated |
|---|---|---|---|
| Collection CRUD | Yes | Yes | Yes |
| Vector search/query | Yes | Yes | Yes |
| Database create/drop | No | No | Yes |
| User/role management | No | Limited | Yes |
| Backup management | No | Yes | Yes |
| Cluster modify | No | No | Yes |

---

# Quickstart Command

Guide the user through the complete Zilliz Cloud CLI setup:

1. **Check Python** — `python3 --version` (need 3.10+)
2. **Install CLI** — `python3 -m pip install --upgrade zilliz-cli` then `zilliz --version`
3. **Authenticate** — `zilliz auth status`; if not logged in, instruct user to run `zilliz login` in their own terminal
4. **List clusters** — `zilliz cluster list`; if none, offer to create one
5. **Set context** — `zilliz context set --cluster-id <id>`
6. **Verify** — `zilliz context current` and `zilliz collection list`

---

# Cluster Management

## List Clusters

```bash
zilliz cluster list
zilliz cluster list --page-size 10 --page 1
zilliz cluster list --all
```

## Describe a Cluster

```bash
zilliz cluster describe --cluster-id <cluster-id>
```

## Create a Cluster

```bash
# Serverless (default)
zilliz cluster create --type serverless --name <name> --project-id <project-id> --region <region-id>

# Free tier
zilliz cluster create --type free --name <name> --project-id <project-id> --region <region-id>

# Dedicated
zilliz cluster create --type dedicated \
  --name <name> \
  --project-id <project-id> \
  --region <region-id> \
  --cu-type <cu-type> \
  --cu-size <cu-size>
```

To find available project IDs, cloud providers, and regions:

```bash
zilliz project list
zilliz cluster providers
zilliz cluster regions
zilliz cluster regions --cloud-id <cloud-id>
```

## Delete / Suspend / Resume a Cluster

```bash
zilliz cluster delete --cluster-id <cluster-id>
zilliz cluster suspend --cluster-id <cluster-id>
zilliz cluster resume --cluster-id <cluster-id>
```

## Modify a Cluster

```bash
zilliz cluster modify --cluster-id <cluster-id> --cu-size <new-size>
zilliz cluster modify --cluster-id <cluster-id> --replica <count>
zilliz cluster modify --cluster-id <cluster-id> --body '{"cuSize": 2, "replica": 2}'
```

### Cluster Guidance

- Before creating a cluster, help the user choose a region by running `zilliz cluster providers` and `zilliz cluster regions`.
- Cluster creation is **asynchronous**. After `cluster create`, poll with `zilliz cluster describe` until status becomes `RUNNING`.
- Before deleting a cluster, always confirm with the user — this is irreversible.
- After creating a cluster, suggest setting context with `zilliz context set --cluster-id <id>`.

---

# Collection Management

All collection commands accept an optional `--database <db-name>` flag.

## List / Describe Collections

```bash
zilliz collection list
zilliz collection list --database <db-name>
zilliz collection describe --name <collection-name>
```

## Create a Collection

Quick create with auto schema:

```bash
zilliz collection create --name <name> --dimension <dim>
# Optional: --metric-type COSINE|L2|IP --id-type Int64|VarChar --auto-id true|false
```

Advanced create with custom schema:

```bash
zilliz collection create --name <name> --body '{
  "schema": {
    "fields": [
      {"fieldName": "id", "dataType": "Int64", "isPrimary": true},
      {"fieldName": "vector", "dataType": "FloatVector", "elementTypeParams": {"dim": "768"}},
      {"fieldName": "text", "dataType": "VarChar", "elementTypeParams": {"max_length": "1024"}}
    ]
  }
}'
```

## Drop / Rename / Check Existence

```bash
zilliz collection drop --name <collection-name>
zilliz collection rename --name <old-name> --new-name <new-name>
zilliz collection rename --name <old-name> --new-name <new-name> --new-database <db-name>
zilliz collection has --name <collection-name>
```

## Load / Release / Stats

```bash
zilliz collection load --name <collection-name>
zilliz collection release --name <collection-name>
zilliz collection get-stats --name <collection-name>
zilliz collection get-load-state --name <collection-name>
zilliz collection flush --name <collection-name>
zilliz collection compact --name <collection-name>
```

## Collection Aliases

```bash
zilliz alias create --collection <collection-name> --alias <alias-name>
zilliz alias list --database <db-name>
zilliz alias list --database <db-name> --collection <collection-name>
zilliz alias describe --alias <alias-name>
zilliz alias alter --collection <new-collection-name> --alias <alias-name>
zilliz alias drop --alias <alias-name>
```

### Collection Guidance

- Ask about use case to recommend dimension, metric type, and schema.
- Before dropping a collection, confirm with the user — this deletes all data.
- A collection must be loaded before search or query.
- Use `describe` to inspect schema before vector operations.

---

# Vector Operations

All vector commands accept an optional `--database <db-name>` flag. Target collection must exist and be loaded.

## Vector Search

```bash
zilliz vector search \
  --collection <collection-name> \
  --data '[[0.1, 0.2, 0.3, ...]]' \
  --limit 10
# Optional:
#   --filter 'age > 20 and status == "active"'
#   --output-fields '["field1", "field2"]'
#   --anns-field <vector-field-name>
```

## Hybrid Search

```bash
zilliz vector hybrid-search \
  --collection <collection-name> \
  --search '[
    {"data": [[0.1, 0.2, ...]], "annsField": "dense_vector", "limit": 10},
    {"data": [["search text"]], "annsField": "sparse_vector", "limit": 10}
  ]' \
  --rerank '{"strategy": "rrf", "params": {"k": 60}}' \
  --limit 10
# Optional: --output-fields '["field1", "field2"]'
```

## Query (Filter-Based Retrieval)

```bash
zilliz vector query \
  --collection <collection-name> \
  --filter 'id in [1, 2, 3]' \
  --limit 10
# Optional: --output-fields '["field1", "field2"]'
```

## Get by ID

```bash
zilliz vector get \
  --collection <collection-name> \
  --id '[1, 2, 3]'
# Optional: --output-fields '["field1", "field2"]'
```

## Insert / Upsert Vectors

```bash
zilliz vector insert \
  --collection <collection-name> \
  --data '[
    {"id": 1, "vector": [0.1, 0.2, ...], "text": "hello"},
    {"id": 2, "vector": [0.3, 0.4, ...], "text": "world"}
  ]'

zilliz vector upsert \
  --collection <collection-name> \
  --data '[{"id": 1, "vector": [0.1, ...], "text": "updated"}]'
# Optional: --partition <partition-name>
```

For large datasets, read from file:

```bash
zilliz vector insert --collection <name> --data "$(cat data.json)"
```

## Delete Vectors

```bash
zilliz vector delete \
  --collection <collection-name> \
  --filter 'id in [1, 2, 3]'
# Optional: --partition <partition-name>
```

## Filter Expression Syntax

| Expression | Example |
|---|---|
| Comparison | `age > 20` |
| Equality | `status == "active"` |
| IN list | `id in [1, 2, 3]` |
| AND/OR | `age > 20 and status == "active"` |
| String match | `text like "hello%"` |
| Array contains | `tags array_contains "ml"` |

### Vector Guidance

- Before searching, inspect schema with `zilliz collection describe` for field names and dimensions.
- The `--data` value must match the collection's vector dimension exactly.
- For text-to-vector search, the user needs an embedding model to convert text to vectors first.
- For large insert operations, suggest writing data to a JSON file first.

---

# Index Management

All index commands accept an optional `--database <db-name>` flag.

## Create an Index

```bash
zilliz index create --collection <collection-name> --body '{
  "indexParams": [
    {
      "fieldName": "vector",
      "indexName": "vector_index",
      "metricType": "COSINE",
      "indexType": "AUTOINDEX"
    }
  ]
}'
```

Common index types: `AUTOINDEX` (recommended), `IVF_FLAT`, `IVF_SQ8`, `HNSW`.
Common metric types: `COSINE`, `L2`, `IP`.

## List / Describe / Drop Indexes

```bash
zilliz index list --collection <collection-name>
zilliz index describe --collection <collection-name> --index-name <index-name>
zilliz index drop --collection <collection-name> --index-name <index-name>
```

### Index Guidance

- On Zilliz Cloud, `AUTOINDEX` is recommended for most use cases.
- An index is required before loading a collection for search.
- After creating an index, remind the user to load the collection.

---

# Database Management

## Commands

```bash
zilliz database list
zilliz database create --name <db-name>
zilliz database create --name <db-name> --body '{"properties": {}}'
zilliz database describe --name <db-name>
zilliz database drop --name <db-name>
```

### Database Guidance

- Database create, describe, and drop are only available on **Dedicated** clusters. `database list` works on all cluster types.
- Every cluster has a "default" database.
- Before dropping a database, confirm with the user — all collections in it will be deleted.
- After creating a database, suggest switching context: `zilliz context set --database <db-name>`.

---

# Partition Management

## Commands

```bash
zilliz partition list --collection <collection-name>
zilliz partition create --collection <collection-name> --partition <partition-name>
zilliz partition has --collection <collection-name> --partition <partition-name>
zilliz partition get-stats --collection <collection-name> --partition <partition-name>
zilliz partition load --collection <collection-name> --names '["partition1", "partition2"]'
zilliz partition release --collection <collection-name> --names '["partition1", "partition2"]'
zilliz partition drop --collection <collection-name> --partition <partition-name>
```

### Partition Guidance

- Every collection has a default `_default` partition.
- A partition must be loaded before it can be searched.
- Before dropping a partition, confirm with the user.

---

# User & Role Management (RBAC)

Only available on **Dedicated** clusters.

## Users

```bash
zilliz user list
zilliz user create --user <username> --password <password>
zilliz user describe --user <username>
zilliz user update-password --user <username> --password <old-password> --new-password <new-password>
zilliz user grant-role --user <username> --role <role-name>
zilliz user revoke-role --user <username> --role <role-name>
zilliz user drop --user <username>
```

## Roles

```bash
zilliz role list
zilliz role create --role <role-name>
zilliz role describe --role <role-name>
zilliz role grant-privilege \
  --role <role-name> \
  --object-type <Collection|Global|Database> \
  --object-name <name-or-*> \
  --privilege <privilege-name>
zilliz role revoke-privilege \
  --role <role-name> \
  --object-type <Collection|Global|Database> \
  --object-name <name-or-*> \
  --privilege <privilege-name>
zilliz role drop --role <role-name>
```

Common privileges:
- Collection: `Search`, `Query`, `Insert`, `Delete`, `CreateIndex`, `DropCollection`
- Global: `CreateCollection`, `All`
- Database: `ListCollections`

### RBAC Guidance

- Built-in roles: `admin` (full access), `public` (no privileges by default).
- Suggested workflow: create role → grant privileges → create user → assign role.
- Use `*` as object-name to grant privilege on all objects of that type.

---

# Backup Management

No cluster context required — backup operations use `--cluster-id` directly.

## Create a Backup

```bash
# Full cluster backup
zilliz backup create --cluster-id in01-xxxxxxxxxxxx

# Collection-level backup
zilliz backup create --cluster-id in01-xxxxxxxxxxxx --database default --collection my_col
```

## List / Describe / Delete Backups

```bash
zilliz backup list
zilliz backup list --cluster-id <cluster-id>
zilliz backup list --creation-method manual   # or: auto
zilliz backup list --backup-type CLUSTER      # or: COLLECTION
zilliz backup describe --cluster-id <cluster-id> --backup-id <backup-id>
zilliz backup delete --cluster-id <cluster-id> --backup-id <backup-id>
```

## Export a Backup

```bash
zilliz backup export \
  --cluster-id <cluster-id> \
  --backup-id <backup-id> \
  --integration-id <integration-id> \
  --directory <path>
```

## Restore to a New Cluster

```bash
zilliz backup restore-cluster \
  --cluster-id <source-cluster-id> \
  --backup-id <backup-id> \
  --project-id <project-id> \
  --name <new-cluster-name> \
  --cu-size <size> \
  --collection-status LOADED
```

## Restore Specific Collections

```bash
zilliz backup restore-collection \
  --cluster-id <source-cluster-id> \
  --backup-id <backup-id> \
  --dest-cluster-id <destination-cluster-id> \
  --body '{"collections": [{"source": "col1", "target": "col1_restored"}]}'
```

## Backup Policy

```bash
zilliz backup describe-policy --cluster-id <cluster-id>

# Enable daily backup
zilliz backup update-policy --cluster-id in01-xxxx --auto-backup true --frequency daily --start-time 02:00 --retention-days 7

# Enable backup on Mon/Wed/Fri
zilliz backup update-policy --cluster-id in01-xxxx --auto-backup true --frequency 1,3,5 --start-time 03:00-05:00 --retention-days 14

# Disable auto-backup
zilliz backup update-policy --cluster-id in01-xxxx --auto-backup false
```

### Backup Guidance

- Before deleting a backup, confirm with the user — this is irreversible.
- Explain difference: cluster restore = new cluster, collection restore = into existing cluster.
- Suggest backup policies for production clusters.

---

# Data Import

Target collection must exist on the target cluster.

## Commands

```bash
# Start import job
zilliz import start \
  --cluster-id <cluster-id> \
  --collection <collection-name> \
  --body '{
    "files": [["s3://bucket/path/to/file.parquet"]],
    "options": {}
  }'

# List import jobs
zilliz import list --cluster-id <cluster-id>
zilliz import list --cluster-id <cluster-id> --database <db-name>

# Check import status
zilliz import status --cluster-id <cluster-id> --job-id <job-id>
```

Supported file formats: Parquet, JSON, CSV.

### Import Guidance

- Import jobs run asynchronously — use `import status` to track progress.
- Data files must be accessible from Zilliz Cloud (e.g., S3, GCS with integration configured).
- Collection schema must match the data file structure.

---

# Billing

Requires OAuth login (not API Key mode).

## Commands

```bash
# Usage
zilliz billing usage --last 7d
zilliz billing usage --month this
zilliz billing usage --month last
zilliz billing usage --month 2026-01
zilliz billing usage --start 2026-01-01 --end 2026-01-31

# Invoices
zilliz billing invoices
zilliz billing invoices --all
zilliz billing invoices --invoice-id inv-xxxxxxxxxxxx

# Bind credit card (instruct user to run in their own terminal)
zilliz billing bind-card --card-number <number> --exp-month <1-12> --exp-year <year> --cvc <code>
```

### Billing Guidance

- The `bind-card` command handles sensitive card data — always instruct the user to run it in their own terminal.

---

# Project & Region Management

## Projects

```bash
zilliz project list
zilliz project describe --project-id <project-id>
zilliz project create --name <project-name> --plan <Free|Serverless|Standard|Enterprise>
zilliz project upgrade --project-id <project-id> --plan <Serverless|Standard|Enterprise>
```

## Volumes

```bash
zilliz volume create --project-id <project-id> --region <region-id> --name <volume-name>
zilliz volume list --project-id <project-id>
zilliz volume delete --name <volume-name>
```

---

# Monitoring & Status

## Status Overview Workflow

When the user asks for status, gather and present:

1. `zilliz context current --output json`
2. `zilliz cluster describe --cluster-id <id> --output json`
3. `zilliz database list --output json`
4. `zilliz collection list --output json`
5. For each collection: `zilliz collection get-stats --name <name> --output json` and `zilliz collection get-load-state --name <name> --output json`

Present as:

**Cluster:** \<name\> (\<cluster-id\>)
**Status:** RUNNING | **Region:** \<region\> | **Plan:** \<plan\>
**Database:** \<current-db\>

**Collections:**

| Collection | Rows | Load State |
|---|---|---|
| my_collection | 10,000 | Loaded |

---

# General Guidance

- Always check prerequisites (CLI installed, logged in, context set) before executing commands.
- NEVER run `zilliz login`, `zilliz configure`, or `zilliz auth switch` inside the AI agent — they require interactive input.
- NEVER ask the user to paste API keys into the chat — guide them to configure credentials in their own terminal.
- Before any destructive operation (delete cluster, drop collection, drop database, delete backup), always confirm with the user.
- Use `--output json` when parsing results programmatically, then format into readable summaries.
- When a command fails with permissions error, check the cluster type first.
- When a command fails unexpectedly, consider whether the cluster type or auth mode may be the cause.
