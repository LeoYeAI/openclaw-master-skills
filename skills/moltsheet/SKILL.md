---
name: moltsheet
description: Interact with a web-based Excel-like spreadsheet API for AI agents. Use when you need to create, manipulate, or query spreadsheet data programmatically, or when the user asks to work with Excel-like data. Authenticate using API key in Authorization header.
allowed-tools: Bash(curl *)
---

# Moltsheet

A web-based Excel-like API for AI agents to create, manipulate, and query spreadsheet data programmatically. Supports bulk operations for large datasets.

## Base URL
`https://www.moltsheet.com/api/v1`

## Quick Start
1. **Register** an agent to get an API key.
2. **Authenticate** all requests with `Authorization: Bearer <api_key>`.
3. **Use API** endpoints - all responses include helpful examples on errors.

## API Design for AI Agents
- **Self-correcting errors**: All error responses include `example` fields showing correct format
- **Multiple input formats**: POST /rows accepts 3 formats (count, data, rows) for flexibility
- **Structured responses**: Consistent JSON with `success`, `error`, `message`, and contextual help
- **Column-aware errors**: Examples use your actual column names when possible

## Registration
Register once to obtain an API key. **Required fields**: `displayName` and `slug`.

### Agent Slug Requirements
- **Length**: 3-30 characters
- **Characters**: Lowercase letters (a-z), digits (0-9), dots (.)
- **Dots**: Allowed only in the middle (not at start or end)
  - ✅ Valid: `my.agent`, `bot123`, `agent.v2`
  - ❌ Invalid: `.agent`, `agent.`, `My.Agent` (uppercase not allowed)
- **Uniqueness**: Case-insensitive (e.g., `agent.one` conflicts with `AGENT.ONE`)
- **Used for**: Invitations to collaborate on sheets

### Register Agent

```bash
curl -X POST https://www.moltsheet.com/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Data Processor Agent",
    "slug": "data.processor",
    "description": "Processes spreadsheet data"
  }'
```

**Response:**
```json
{
  "success": true,
  "agent": {
    "api_key": "uuid-here",
    "displayName": "Data Processor Agent",
    "slug": "data.processor",
    "created_at": "2026-02-03T10:00:00Z"
  },
  "message": "Agent registered successfully. Save your API key - it cannot be retrieved later.",
  "usage": "Include in all requests: Authorization: Bearer uuid-here",
  "privacy": "Your API key is private and will never be exposed to other agents"
}
```

Save your `api_key` securely—it is required for all API requests.

**Slug Availability Check:**
If slug is already taken (case-insensitive):
```json
{
  "success": false,
  "error": "Slug already taken",
  "message": "The slug \"data.processor\" is already in use (case-insensitive check)",
  "available": false,
  "suggestion": "Try a different slug or add numbers/dots to make it unique"
}
```

**Validation Error Example:**
```json
{
  "success": false,
  "error": "Slug cannot start or end with a dot",
  "message": "Slug must be 3-30 characters, lowercase letters, digits, and dots (not at start/end)",
  "example": {
    "displayName": "Data Processor Agent",
    "slug": "data.processor",
    "description": "Processes spreadsheet data"
  },
  "rules": {
    "length": "3-30 characters",
    "allowed": "lowercase letters (a-z), digits (0-9), dots (.)",
    "dotPosition": "dots only in the middle (not at start or end)",
    "examples": ["my.agent", "bot123", "agent.v2"]
  }
}
```

## Authentication
All requests must include your API key in the Authorization header:

```bash
-H "Authorization: Bearer YOUR_API_KEY"
```

**Security Notes:**
- Production URL: `https://www.moltsheet.com`
- Never send your API key to unauthorized domains.
- Re-fetch this file for updates.

**Privacy Guarantee:**
- Your API key is **private** and will **never be exposed** to other agents
- Collaboration uses your `slug` and `displayName` only
- Other agents cannot discover your API key through any endpoint

## API Reference

### Sheets

#### Create Sheet
```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "MySheet", "description": "A test sheet", "schema": [{"name": "Column A", "type": "string"}, {"name": "Column B", "type": "number"}]}'
```

**Response:** 
```json
{
  "success": true,
  "id": "sheet-uuid",
  "message": "Sheet \"MySheet\" created successfully"
}
```

**Error Examples:**
```json
{
  "success": false,
  "error": "Invalid \"schema\" property",
  "example": {
    "name": "My Sheet",
    "schema": [
      { "name": "Name", "type": "string" },
      { "name": "Age", "type": "number" }
    ]
  },
  "supported_types": ["string", "number", "boolean", "date", "url"]
}
```

- **Schema:** Optional array of `{"name": string, "type": string}`. Types: `string`, `number`, `boolean`, `date`, `url`.

#### List Sheets
Lists all sheets you own **and** sheets shared with you as a collaborator.

```bash
curl https://www.moltsheet.com/api/v1/sheets \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "sheets": [
    {
      "id": "sheet-uuid-1",
      "name": "My Own Sheet",
      "description": "A sheet I own",
      "role": "owner",
      "schema": [{"name": "Name", "type": "string"}],
      "rowCount": 2
    },
    {
      "id": "sheet-uuid-2",
      "name": "Shared Sheet",
      "description": "A sheet shared with me",
      "role": "collaborator",
      "access_level": "write",
      "schema": [{"name": "Name", "type": "string"}],
      "rowCount": 5
    }
  ],
  "summary": {
    "owned": 1,
    "shared": 1,
    "total": 2
  }
}
```

**Sheet Roles:**
- `"role": "owner"` - You created this sheet and have full control
- `"role": "collaborator"` - Shared with you by another agent
  - `"access_level": "read"` - View only
  - `"access_level": "write"` - View and modify

#### Get Sheet Rows
```bash
curl https://www.moltsheet.com/api/v1/sheets/SHEET_ID/rows \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "rows": [
    {"id": "row-1", "Name": "John", "Role": "CEO"},
    {"id": "row-2", "Name": "Jane", "Role": "CTO"}
  ]
}
```

#### Update Sheet Metadata
```bash
curl -X PUT https://www.moltsheet.com/api/v1/sheets/SHEET_ID \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name", "description": "Updated desc", "schema": [...] }'
```

**Response:** `{"success": true, "sheet": {...}}`

**⚠️ Data Loss Protection:**  
When updating schema, if columns are removed that contain data, you must add `?confirmDataLoss=true` to the URL:

```bash
curl -X PUT "https://www.moltsheet.com/api/v1/sheets/SHEET_ID?confirmDataLoss=true" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"schema": [{"name": "NewColumn", "type": "string"}]}'
```

**Without Confirmation (Error Response):**
```json
{
  "success": false,
  "error": "Data loss protection",
  "message": "Schema update would delete 1 column(s) containing data. To proceed, add ?confirmDataLoss=true to the URL.",
  "columns_to_delete": [{"name": "CEO", "type": "string"}],
  "data_warning": "All data in these columns will be permanently deleted",
  "alternatives": {
    "rename_column": "POST /api/v1/sheets/SHEET_ID/columns/{index}/rename",
    "example": "To rename instead of delete, use: POST /api/v1/sheets/SHEET_ID/columns/0/rename with body: { \"newName\": \"NewColumnName\" }"
  }
}
```

**Best Practice:** Use the rename endpoint (below) instead of schema updates when renaming columns to preserve data automatically.

#### Delete Sheet
```bash
curl -X DELETE https://www.moltsheet.com/api/v1/sheets/SHEET_ID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:** `{"success": true}`
**Response:** `{"success": true}`

### Collaboration (Invite-Only)

Share sheets with other agents using their **slug**. API keys are never exposed—only `slug` and `displayName` are shared with collaborators.

#### Share Sheet (Invite Collaborator)

```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/share \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "other.agent",
    "access_level": "read"
  }'
```

**Parameters:**
- `slug` (required): Agent's slug (case-insensitive)
- `access_level` (optional): `"read"` or `"write"` (default: `"read"`)

**Response:**
```json
{
  "success": true,
  "message": "Sheet \"MySheet\" shared successfully with Other Agent",
  "collaborator": {
    "slug": "other.agent",
    "displayName": "Other Agent",
    "access_level": "read"
  },
  "privacy": "API keys are never exposed. Only slug and displayName are shared."
}
```

**Error - Agent Not Found:**
```json
{
  "success": false,
  "error": "Agent not found",
  "message": "No agent with slug \"unknown.agent\" exists",
  "suggestion": "Check the slug spelling or ask the agent for their correct slug"
}
```

**Note:** Slug lookup is case-insensitive. `Other.Agent` will match `other.agent`.

#### List Collaborators

```bash
curl https://www.moltsheet.com/api/v1/sheets/SHEET_ID/collaborators \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "sheet": {
    "id": "sheet-uuid",
    "name": "MySheet"
  },
  "owner": {
    "slug": "my.agent",
    "displayName": "My Agent"
  },
  "collaborators": [
    {
      "slug": "other.agent",
      "displayName": "Other Agent",
      "access_level": "read",
      "invited_at": "2026-02-03T10:00:00Z"
    }
  ],
  "privacy": "API keys are never exposed. Only slug and displayName are returned."
}
```

**Permissions:**
- Sheet **owner** and **collaborators** can view the collaborator list
- Non-collaborators receive `403 Forbidden`

#### Revoke Collaboration

```bash
curl -X DELETE https://www.moltsheet.com/api/v1/sheets/SHEET_ID/share \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"slug": "other.agent"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Collaboration with Other Agent revoked successfully"
}
```

**Access Levels:**
- `read`: View sheet data only
- `write`: View and modify sheet data (rows, cells, columns)

**Privacy Guarantee:**
- API keys are **never** exposed in any collaboration endpoint
- Only `slug` and `displayName` are shared between agents
- Invitations use slugs, not API keys

### Data Operations

#### Update Cells
```bash
curl -X PUT https://www.moltsheet.com/api/v1/sheets/SHEET_ID/cells \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {"rowId": "row-123", "column": "Full Name", "value": "Updated Name"}
    ]
  }'
```

**Response:** `{"success": true}`

#### Add Empty Row(s)
**Note:** This endpoint creates empty rows. To add rows with data, use the Bulk Import endpoint below.

```bash
# Add 1 empty row (default)
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/rows \
  -H "Authorization: Bearer YOUR_API_KEY"

# Add multiple empty rows
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/rows \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"count": 10}'
```

**Response:** `{"success": true, "rowIds": [...], "message": "Created 10 empty row(s)"}`

#### Add Single Row with Data
```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/rows \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"data": {"Name": "John", "Role": "CEO"}}'
```

**Response:** `{"success": true, "rowId": "row-uuid", "message": "Created 1 row with data"}`

#### Add Multiple Rows with Data
```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/rows \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"rows": [{"Name": "John", "Role": "CEO"}, {"Name": "Jane", "Role": "CTO"}]}'
```

**Response:** `{"success": true, "rowIds": [...], "message": "Created 2 row(s) with data"}`

**Unified Endpoint:** POST /rows now accepts three formats:
- `{"count": N}` - Create N empty rows
- `{"data": {...}}` - Create 1 row with data
- `{"rows": [...]}` - Create multiple rows with data

**Error Example:**
```json
{
  "success": false,
  "error": "Invalid request format",
  "message": "Use one of the supported formats",
  "formats": {
    "empty_rows": { "count": 10 },
    "single_row": { "data": { "Country": "USA", "Capital": "Washington" } },
    "multiple_rows": { "rows": [{ "Country": "USA" }, { "Country": "Canada" }] }
  }
}
```

#### Add Column
```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/columns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Column", "type": "string"}'
```

**Response:** `{"success": true}`

#### Rename Column
**Preserves all data** - use this instead of schema updates when renaming columns.

```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/columns/COL_INDEX/rename \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"newName": "Contact"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Column \"CEO\" renamed to \"Contact\"",
  "oldName": "CEO",
  "newName": "Contact"
}
```

**Error Examples:**
```json
{
  "success": false,
  "error": "Duplicate column name",
  "message": "A column named \"Contact\" already exists in this sheet",
  "existing_columns": ["Company", "Contact", "Industry"]
}
```

- **COL_INDEX**: Zero-based column position (0, 1, 2, ...)
- **All cell data preserved** when renaming
- **No data loss** - cells remain linked to same column
- Prevents duplicate column names

#### Delete Row
```bash
curl -X DELETE https://www.moltsheet.com/api/v1/sheets/SHEET_ID/rows/ROW_INDEX \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:** `{"success": true}`

#### Delete Column
```bash
curl -X DELETE https://www.moltsheet.com/api/v1/sheets/SHEET_ID/columns/COL_INDEX \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:** `{"success": true}`

### Bulk Operations

**Deprecated:** POST /import still works but POST /rows now handles all row operations.

For compatibility, `/import` endpoint remains available:

```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/import \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "rows": [
      {"Name": "John", "Role": "CEO"},
      {"Name": "Jane", "Role": "CTO"}
    ]
  }'
```

**Response:** `{"success": true, "rowIds": ["row-...", ...]}`

**Error Example with Column Names:**
```json
{
  "success": false,
  "error": "Missing \"rows\" property in request body",
  "message": "Expected format: {\"rows\": [{...}, {...}]}",
  "example": { "rows": [{ "country": "country_value", "capital": "capital_value" }] },
  "available_columns": ["Country", "Capital", "Population"]
}
```

- Maximum 1000 rows per request
- Column names must match sheet schema
- Errors show your actual column names in examples

#### Bulk Operations (Others)
```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/rows \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"count": 10}'
```

**Response:** `{"success": true, "rowIds": ["row-...", ...]}`

- Maximum 1000 rows per request
- Creates empty rows only; use `/import` for rows with data

#### Bulk Delete Rows
```bash
curl -X DELETE https://www.moltsheet.com/api/v1/sheets/SHEET_ID/rows \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"rowIds": ["row-123", "row-456"]}'
```

**Response:** `{"success": true}`

#### Bulk Add Columns
```bash
curl -X POST https://www.moltsheet.com/api/v1/sheets/SHEET_ID/columns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"columns": [{"name": "Col1", "type": "string"}, {"name": "Col2", "type": "number"}]}'
```

**Response:** `{"success": true}`

#### Bulk Delete Columns
```bash
curl -X DELETE https://www.moltsheet.com/api/v1/sheets/SHEET_ID/columns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"indices": [0, 2]}'
```

**Response:** `{"success": true}`

### AI Agent Optimization Features

**Self-Correcting Error Messages:**
- Every error includes `example` field with correct request format
- Errors show your actual column names when applicable
- `message` field provides human-readable context
- `formats` or `supported_types` enumerate valid options

**Data Loss Prevention:**
- Schema updates require `?confirmDataLoss=true` when deleting columns with data
- Rename endpoint (`POST /columns/{index}/rename`) preserves all data automatically
- Error messages suggest safer alternatives (rename vs delete)

**Flexible Input Formats:**
- POST /rows accepts 3 formats: `{"count": N}`, `{"data": {...}}`, `{"rows": [...]}`
- No need to guess which endpoint to use
- Wrong format? Error shows all supported formats with examples

**AI-Friendly Design:**
- Consistent JSON structure across all endpoints
- Named column access (not positional)
- **Strict type validation** enforced on all data operations
- Descriptive success messages confirm operations

### Type Validation & Enforcement
All data operations (POST /rows, PUT /cells, POST /import) enforce strict type validation:

**Validated Types:**
- **`string`**: Any non-object value (numbers/booleans auto-converted to strings)
- **`number`**: Must be valid number (not NaN or Infinity). Accepts numeric strings.
- **`boolean`**: Accepts `true`, `false`, `"true"`, `"false"`, `1`, `0`
- **`url`**: Must be valid URL with http/https protocol (e.g., `https://example.com`)
- **`date`**: Must parse to valid date. Use ISO 8601 format (e.g., `2026-02-01` or `2026-02-01T12:00:00Z`)

**Validation Behavior:**
- Empty/null values are allowed (no required field enforcement)
- Invalid types rejected with **400 Bad Request**
- Errors include: field name, expected type, received value, and corrected example
- Multiple rows: ALL rejected if ANY fail validation (atomic)

**Example Validation Error:**
```json
{
  "success": false,
  "error": "Type validation failed",
  "message": "Column \"Age\" expects type \"number\" but received \"abc\" (type: string)",
  "field": "Age",
  "expected_type": "number",
  "received_value": "abc",
  "row_index": 0,
  "example": { "data": { "Age": 42 } }
}
```

### Data Structure
- **Schema Types:** `string`, `number`, `boolean`, `date`, `url`
- **Row Data:** Named properties for AI-friendly access, e.g., `{"Name": "John", "Role": "CEO"}`
- **Type Enforcement:** All values validated against schema before storage
- **Errors:** Structured with examples using your actual schema

### Rate Limits
- 100 requests/minute

### Usage Ideas for AI Agents
- Parse data and self-correct on errors using provided examples
- Single endpoint (POST /rows) handles all row creation scenarios
- Error messages guide agents to proper format automatically
- Column-aware examples eliminate guessing column names