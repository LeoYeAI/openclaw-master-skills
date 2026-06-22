---
name: odoo-manager
description: Manage Odoo (contacts, any business objects, and metadata) via the official External XML-RPC API. Supports generic CRUD operations on any model using execute_kw, with ready-made flows for res.partner and model introspection. Features dynamic instance and database switching with context-aware URL, database, and credential resolution.
homepage: https://www.odoo.com/documentation/
metadata: {"openclaw":{"emoji":"🏢","requires":{"env":["ODOO_URL","ODOO_DB","ODOO_USERNAME","ODOO_PASSWORD"]},"primaryEnv":"ODOO_PASSWORD"}}
---

# Odoo Manager Skill

## 🔐 URL, Database & Credential Resolution

### URL Resolution

Odoo server URL precedence (highest to lowest):

1. `temporary_url` — one-time URL for a specific operation
2. `user_url` — user-defined URL for the current session
3. `ODOO_URL` — environment default URL

This allows you to:

- Switch between multiple Odoo instances (production, staging, client-specific)
- Test against demo databases
- Work with different client environments without changing global config

**Examples (conceptual):**

```text
// Default: uses ODOO_URL from environment
{{resolved_url}}/xmlrpc/2/common

// Override for one operation:
temporary_url = "https://staging.mycompany.odoo.com"
{{resolved_url}}/xmlrpc/2/common

// Override for session:
user_url = "https://client-xyz.odoo.com"
{{resolved_url}}/xmlrpc/2/common
```

### Database Resolution

Database name (`db`) precedence:

1. `temporary_db`
2. `user_db`
3. `ODOO_DB`

Use this to:

- Work with multiple databases on the same Odoo server
- Switch between test and production databases

### Username & Secret Resolution

Username precedence:

1. `temporary_username`
2. `user_username`
3. `ODOO_USERNAME`

Secret (password or API key) precedence:

1. `temporary_api_key` or `temporary_password`
2. `user_api_key` or `user_password`
3. `ODOO_API_KEY` (if set) or `ODOO_PASSWORD`

**Important:**

- Odoo API keys are used **in place of** the password, with the usual login.
- Store passwords / API keys like real passwords; never log or expose them.

Environment variables are handled via standard OpenClaw metadata: `requires.env` declares **required** variables (`ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`). `ODOO_API_KEY` is an **optional** environment variable used instead of the password when present; it is not listed in metadata and should simply be set in the environment when needed.

### Resolved Values

At runtime the skill always works with:

- `{{resolved_url}}` — final URL
- `{{resolved_db}}` — final database name
- `{{resolved_username}}` — final login
- `{{resolved_secret}}` — password **or** API key actually used to authenticate

These are computed using the precedence rules above.

---

## 🔄 Context Management

> The `temporary_*` and `user_*` names are **runtime context variables used by the skill logic**, not OpenClaw metadata fields. OpenClaw does **not** have an `optional.context` metadata key; context is resolved dynamically at runtime as described below.

### Temporary Context (One-Time Use)

**User examples:**

- "Pour cette requête, utilise l’instance staging Odoo"
- "Utilise la base `odoo_demo` juste pour cette opération"
- "Connecte-toi avec cet utilisateur uniquement pour cette action"

**Behavior:**

- Set `temporary_*` (url, db, username, api_key/password)
- Use them for **a single logical operation**
- Automatically clear after use

This is ideal for:

- Comparing data between two environments
- Running a single check on a different database

### Session Context (Current Session)

**User examples:**

- "Travaille sur l’instance Odoo du client XYZ"
- "Utilise la base `clientx_prod` pour cette session"
- "Connecte-toi avec mon compte administrateur pour les prochaines opérations"

**Behavior:**

- Set `user_*` (url, db, username, api_key/password)
- Persist for the whole current session
- Overridden only by `temporary_*` or by clearing `user_*`

### Resetting Context

**User examples:**

- "Reviens à la configuration Odoo par défaut"
- "Efface mon contexte utilisateur Odoo"

**Action:**

- Clear `user_url`, `user_db`, `user_username`, `user_password`, `user_api_key`
- Skill falls back to environment variables (`ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD` / `ODOO_API_KEY`)

### Viewing Current Context

**User examples:**

- "Sur quelle instance Odoo es-tu connecté ?"
- "Montre la configuration Odoo actuelle"

**Response should show (never full secrets):**

```text
Current Odoo Context:
- URL: https://client-xyz.odoo.com (user_url)
- DB: clientxyz_prod (user_db)
- Username: api_integration (user_username)
- Secret: using API key (user_api_key)
- Fallback URL: https://default.odoo.com (ODOO_URL)
- Fallback DB: default_db (ODOO_DB)
```

---

## ⚙️ Odoo XML-RPC Basics

Odoo exposes part of its server framework over **XML-RPC** (not REST).
The External API is documented here: https://www.odoo.com/documentation/18.0/fr/developer/reference/external_api.html

Two main endpoints:

- `{{resolved_url}}/xmlrpc/2/common` — authentication and meta calls
- `{{resolved_url}}/xmlrpc/2/object` — model methods via `execute_kw`

### 1. Checking Server Version

Call `version()` on the `common` endpoint to verify URL and connectivity:

```python
common = xmlrpc.client.ServerProxy(f"{resolved_url}/xmlrpc/2/common")
version_info = common.version()
```

Example result:

```json
{
  "server_version": "18.0",
  "server_version_info": [18, 0, 0, "final", 0],
  "server_serie": "18.0",
  "protocol_version": 1
}
```

### 2. Authenticating

Use `authenticate(db, username, password_or_api_key, {})` on the `common` endpoint:

```python
uid = common.authenticate(resolved_db, resolved_username, resolved_secret, {})
```

`uid` is an integer user ID and will be used in all subsequent calls.

If authentication fails, `uid` is `False` / `0` — the skill should:

- Inform the user that credentials or database are invalid
- Suggest checking `ODOO_URL`, `ODOO_DB`, username, and secret

### 3. Calling Model Methods with execute_kw

Build an XML-RPC client for the `object` endpoint:

```python
models = xmlrpc.client.ServerProxy(f"{resolved_url}/xmlrpc/2/object")
```

Then use `execute_kw` with the following signature:

```python
models.execute_kw(
    resolved_db,
    uid,
    resolved_secret,
    "model.name",     # e.g. "res.partner"
    "method_name",    # e.g. "search_read"
    [positional_args],
    {keyword_args}
)
```

All ORM operations in this skill are expressed in terms of `execute_kw`.

---

## 🔍 Domains & Data Types (Odoo ORM)

### Domain Filters

Domains are lists of conditions:

```python
domain = [["field_name", "operator", value], ...]
```

Examples:

- All companies: `[['is_company', '=', True]]`
- Partners in France: `[['country_id', '=', france_id]]`
- Leads with probability > 50%: `[['probability', '>', 50]]`

Common operators:

- `"="`, `"!="`, `">"`, `">="`, `"<"`, `"<="`
- `"like"`, `"ilike"` (case-insensitive)
- `"in"`, `"not in"`
- `"child_of"` (hierarchical relations)

### Field Value Conventions

- **Integer / Float / Char / Text**: use native types.
- **Date / Datetime**: strings in `YYYY-MM-DD` or ISO 8601 format.
- **Many2one**: usually send the **record ID** (`int`) when writing; reads often return `[id, display_name]`.
- **One2many / Many2many**: use the Odoo **command list** protocol for writes (not fully detailed here; see Odoo docs if needed).

---

## 🧩 Generic ORM Operations (execute_kw)

Each subsection below shows typical user queries and the corresponding
`execute_kw` usage. They are applicable to **any** model (not only `res.partner`).

### List / Search Records (search)

**User queries:**

- "Liste tous les partenaires société"
- "Cherche les commandes de vente confirmées"

**Action (generic):**

```python
ids = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "model.name", "search",
    [domain],
    {"offset": 0, "limit": 80}
)
```

Notes:

- `domain` is a list (can be empty `[]` to match all records).
- Use `offset` and `limit` for pagination.

### Count Records (search_count)

**User queries:**

- "Combien de partenaires sont des sociétés ?"
- "Compte les tâches en cours"

**Action:**

```python
count = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "model.name", "search_count",
    [domain]
)
```

### Read Records by ID (read)

**User queries:**

- "Affiche les détails du partenaire 7"
- "Donne-moi les champs name et country_id pour ces IDs"

**Action:**

```python
records = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "model.name", "read",
    [ids],
    {"fields": ["name", "country_id", "comment"]}
)
```

If `fields` is omitted, Odoo returns all readable fields (often a lot).

### Search and Read in One Step (search_read)

Shortcut for `search()` + `read()` in a single call.

**User queries:**

- "Liste les sociétés (nom, pays, commentaire)"
- "Montre les 5 premiers partenaires avec leurs pays"

**Action:**

```python
records = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "model.name", "search_read",
    [domain],
    {
        "fields": ["name", "country_id", "comment"],
        "limit": 5,
        "offset": 0,
        # Optional: "order": "name asc"
    }
)
```

### Create Records (create)

**User queries:**

- "Crée un nouveau partenaire 'New Partner'"
- "Crée une nouvelle tâche dans le projet X"

**Action:**

```python
new_id = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "model.name", "create",
    [{
        "name": "New Partner"
        # other fields...
    }]
)
```

Returns the newly created record ID.

### Update Records (write)

**User queries:**

- "Met à jour le partenaire 7, change son nom"
- "Baisse la probabilité de ces leads"

**Action:**

```python
success = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "model.name", "write",
    [ids, {"field": "new value", "other_field": 123}]
)
```

Notes:

- `ids` is a list of record IDs.
- All records in `ids` receive the **same** values.

### Delete Records (unlink)

**User queries:**

- "Supprime ce partenaire de test"
- "Efface ces tâches temporaires"

**Action:**

```python
success = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "model.name", "unlink",
    [ids]
)
```

### Name-Based Search (name_search)

Useful for quick lookup on models with a display name (e.g. partners, products).

**User queries:**

- "Trouve le partenaire dont le nom contient 'Agrolait'"

**Action:**

```python
results = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "res.partner", "name_search",
    ["Agrolait"],
    {"limit": 10}
)
```

Result is a list of `[id, display_name]`.

---

## 👥 Contacts / Partners (res.partner)

`res.partner` is the core model for contacts, companies, and many business relations in Odoo.

### List Company Partners

**User queries:**

- "Liste toutes les sociétés"
- "Montre les sociétés avec leur pays"

**Action:**

```python
companies = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "res.partner", "search_read",
    [[["is_company", "=", True]]],
    {"fields": ["name", "country_id", "comment"], "limit": 80}
)
```

### Get a Single Partner

**User queries:**

- "Affiche le partenaire 7"
- "Donne-moi le pays et le commentaire du partenaire 7"

**Action:**

```python
[partner] = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "res.partner", "read",
    [[7]],
    {"fields": ["name", "country_id", "comment"]}
)
```

### Create a New Partner

**User queries:**

- "Crée un partenaire 'Agrolait 2' en tant que société"
- "Crée un contact personne rattaché à la société X"

**Minimal body:**

```python
partner_id = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "res.partner", "create",
    [{
        "name": "New Partner",
        "is_company": True
    }]
)
```

**Additional fields examples:**

- `street`, `zip`, `city`, `country_id`
- `email`, `phone`, `mobile`
- `company_type` (`"person"` or `"company"`)

### Update a Partner

**User queries:**

- "Change l’adresse du partenaire 7"
- "Met à jour le pays et le téléphone"

**Action:**

```python
models.execute_kw(
    resolved_db, uid, resolved_secret,
    "res.partner", "write",
    [[7], {
        "street": "New street 1",
        "phone": "+33 1 23 45 67 89"
    }]
)
```

### Delete a Partner

**User queries:**

- "Supprime le partenaire 999 de test"

**Action:**

```python
models.execute_kw(
    resolved_db, uid, resolved_secret,
    "res.partner", "unlink",
    [[999]]
)
```

---

## 🧱 Model Introspection (ir.model, ir.model.fields, fields_get)

### Discover Fields of a Model (fields_get)

**User queries:**

- "Quels sont les champs de res.partner ?"
- "Montre les types et labels des champs pour ce modèle"

**Action:**

```python
fields = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "res.partner", "fields_get",
    [],
    {"attributes": ["string", "help", "type"]}
)
```

The result is a mapping from field name to metadata:

```json
{
  "name": {"type": "char", "string": "Name", "help": ""},
  "country_id": {"type": "many2one", "string": "Country", "help": ""},
  "is_company": {"type": "boolean", "string": "Is a Company", "help": ""}
}
```

### List All Models (ir.model)

**User queries:**

- "Quels modèles sont disponibles dans ma base Odoo ?"

**Action:**

```python
models_list = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "ir.model", "search_read",
    [[]],
    {"fields": ["model", "name", "state"], "limit": 200}
)
```

`state` indicates whether a model is defined in code (`"base"`) or created dynamically (`"manual"`).

### List Fields of a Specific Model (ir.model.fields)

**User queries:**

- "Donne-moi la liste des champs du modèle res.partner via ir.model.fields"

**Action (simplified):**

```python
partner_model_ids = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "ir.model", "search",
    [[["model", "=", "res.partner"]]]
)
fields_meta = models.execute_kw(
    resolved_db, uid, resolved_secret,
    "ir.model.fields", "search_read",
    [[["model_id", "in", partner_model_ids]]],
    {"fields": ["name", "field_description", "ttype", "required", "readonly"], "limit": 500}
)
```

---

## ⚠️ Error Handling & Best Practices

### Typical Errors

- **Authentication failure**: wrong URL, DB, username, or secret → `authenticate` returns `False` or later calls fail.
- **Access rights / ACLs**: user does not have permission on a model or record.
- **Validation errors**: required fields missing, constraints violated.
- **Connectivity issues**: network errors reaching `xmlrpc/2/common` or `xmlrpc/2/object`.

The skill should:

- Clearly indicate if the issue is with **connection**, **credentials**, or **business validation**.
- Propose next steps (check env vars, context overrides, user rights).

### Pagination

- Use `limit` / `offset` on `search` and `search_read` to handle large datasets.
- For interactive use, default `limit` to a reasonable value (e.g. 80).

### Field Selection

- Always send an explicit `fields` list for `read` / `search_read` when possible.
- This reduces payload and speeds up responses.

### Domains & Performance

- Prefer indexed fields and simple operators (`=`, `in`) for large datasets.
- Avoid unbounded searches without domain on very big tables when possible.

---

## 🚀 Quick End-to-End Examples

### Example 1: Check Connection & List Company Partners

1. Resolve context: `{{resolved_url}}`, `{{resolved_db}}`, `{{resolved_username}}`, `{{resolved_secret}}`
2. Call `version()` on `{{resolved_url}}/xmlrpc/2/common`
3. Authenticate to get `uid`
4. Call `execute_kw` on `res.partner` with `search_read` and domain `[['is_company', '=', True]]`

### Example 2: Create a Partner, Then Read It Back

1. Authenticate via `common.authenticate`
2. `create` a new `res.partner` with `{"name": "New Partner", "is_company": True}`
3. `read` that ID with fields `["name", "is_company", "country_id"]`

### Example 3: Work on Another Database for One Operation

1. Set `temporary_url` and/or `temporary_db` to point to another Odoo environment.
2. Authenticate and perform the requested operation using resolved context.
3. Temporary context is cleared automatically.

---

## 📚 References & Capabilities Summary

- Official Odoo External API documentation (XML-RPC): https://www.odoo.com/documentation/18.0/fr/developer/reference/external_api.html
- Requires an Odoo plan with External API access (Custom plans; not available on One App Free / Standard).

**This skill can:**

- Connect to Odoo via XML-RPC using password **or** API key.
- Switch dynamically between multiple instances and databases using context.
- Perform generic CRUD (`search`, `search_count`, `read`, `search_read`, `create`, `write`, `unlink`) on **any** Odoo model via `execute_kw`.
- Provide ready-made flows for `res.partner` (contacts / companies).
- Inspect model structures using `fields_get`, `ir.model`, and `ir.model.fields`.
- Apply best practices regarding pagination, field selection, and error handling.

