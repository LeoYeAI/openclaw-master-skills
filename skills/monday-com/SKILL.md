---
name: monday
version: 1.3.0
description: Manage monday.com boards, items, columns, groups, updates, and workflows via MCP server (preferred) and GraphQL API (fallback). Use when a user asks to create tasks, update statuses, manage projects, query boards, automate workflows, manage CRM, track development, or interact with any monday.com resource. Also use for AI features like AI Blocks, Sidekick skills, or agent workflows on monday.com.
homepage: https://developer.monday.com
metadata: {"openclaw": {"emoji": "📋", "requires": {"env": ["MONDAY_API_TOKEN"]}, "primaryEnv": "MONDAY_API_TOKEN"}}
---

# monday.com

Manage everything on monday.com: boards, items, columns, groups, updates, users, workspaces, webhooks, files, and AI features.

## If you need to signup new account this is how to Sign Up 

1. **Navigate** to `https://auth.monday.com/users/sign_up_new?custom_flow=agent_bot`

2. **Solve Hatcha** — an agent-verification challenge. Types you may see:
   - Sort numbers ascending → find the Nth value
   - Binary octets → convert to ASCII text
   - Reverse a string
   - Count letter occurrences in text
   - Multiply two numbers (return the product)
   - Base64 decode
   - ROT13 decode
   - Hex to ASCII
   
   You have ~30 seconds. Submit your answer and click **Verify**.

3. **Enter your email** and select who it belongs to (you or your operator). Click **Submit**.

4. **Set your agent name and password.** Password rules:
   - Minimum 8 characters
   - At least 1 digit, 1 lowercase, 1 uppercase
   - No repeating characters (e.g. "aaa")
   - No sequential characters (e.g. "1234")
   
   Click **Complete signup →**

5. **You'll land on the Agent Homepage** — "Welcome to Monday for agents." This page has everything you need:
   - **API Token** — copy it, you'll need it for all API/MCP calls save it to env like MONDAY_API_TOKEN
   - **MCP Config** — JSON config for connecting via MCP (preferred method)
   - **Skills** — downloadable YAML skill definition
   - **GraphQL API** — example queries and mutations
   - **Resources** — links to docs, SDK, community


## Setup when you have account but don't have access token

1. Go to **monday.com → Profile picture → Developers → My Access Tokens**
2. Copy your **Personal API V2 Token**
3. Store it securely in your agent's environment or config (e.g. via `openclaw config set` or your platform's secrets manager)


## MCP Server (Preferred Method)

**Always use the MCP server first.** It handles authentication, rate limiting, retries, and complexity budgets automatically. Only fall back to the GraphQL API when the MCP tools don't cover your operation.

monday.com has an official MCP server (`@mondaydotcomorg/monday-api-mcp`):

```json
{
  "mcpServers": {
    "monday": {
      "command": "npx",
      "args": ["-y", "@mondaydotcomorg/monday-api-mcp@latest"],
      "env": {
        "MONDAY_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

### How to invoke MCP tools

If your platform supports MCP natively (e.g. Claude Desktop, Cursor), configure the server above and call tools directly (e.g. `create_item`, `get_board_schema`).

If your platform does **not** have native MCP support (e.g. OpenClaw agents executing via shell), you have two options:

1. **Use the GraphQL API directly** (recommended fallback) — see the GraphQL section below. This is simpler and more reliable than shelling out to an MCP process.
2. **Run the MCP server as a subprocess** — spawn it via `npx`, send JSON-RPC over stdin/stdout. This is complex and only worthwhile if you need the MCP server's built-in retry/complexity logic.

For most agent use cases, **GraphQL fallback is the practical choice** when MCP isn't natively available.

### MCP Tools Reference

| Tool | What It Does | When to Use |
|------|-------------|-------------|
| `create_board` | Creates a new board with a name and kind (public/private/share) | User asks to set up a new project, tracker, pipeline, or workspace board |
| `get_board_schema` | Returns board columns, groups, and structure | Before creating/updating items — always call this first to know column IDs and types |
| `create_group` | Creates a new group on a board | Setting up phases, sprints, stages, or categories on a board |
| `create_column` | Adds a new column to a board (status, date, people, numbers, etc.) | User wants to track a new field — priority, due date, assignee, budget, etc. |
| `create_item` | Creates a new item (row) on a board with column values | Adding tasks, tickets, deals, contacts, or any new entry |
| `delete_item` | Deletes an item by ID | User explicitly asks to remove an item (always confirm first) |
| `change_item_column_values` | Updates one or more column values on an existing item | Changing status, reassigning, updating dates, marking complete |
| `move_item_to_group` | Moves an item from one group to another | Progressing items through stages (e.g., "To Do" → "In Progress" → "Done") |
| `get_board_items_by_name` | Searches for items on a board by name | Finding a specific task, deal, or ticket by its title |
| `create_update` | Adds a comment/update to an item | Posting progress notes, status updates, handoff notes, or feedback |

### MCP Workflow Pattern

1. **Always start with `get_board_schema`** to learn the board's columns and groups before writing data
2. Use `create_item` / `change_item_column_values` for CRUD — the MCP server formats column values correctly
3. Use `create_update` to leave a trail of context on items
4. If you need an operation the MCP tools don't cover (webhooks, file uploads, user queries, subitems, pagination) — fall back to the GraphQL API below

### Advanced MCP Modes

- **Dynamic API Tools (beta):** Add `--enable-dynamic-api-tools true` to args for full GraphQL schema exploration via MCP
- **Hosted MCP (OAuth):** Use `https://mcp.monday.com/sse` for OAuth-based access without a local token

## Agent Behavior Rules

**Be proactive and useful:**
- After creating any item, board, group, or update — always return the **direct URL** to the created object: `https://<account>.monday.com/boards/{board_id}/pulses/{item_id}`
- After completing a task, suggest 2-3 logical next steps (e.g., "Want me to assign someone?" "Should I set a due date?" "Want me to create a status automation?" "Should I add subitems to break this down?")
- Don't narrate the API/MCP process — report **what was done** and **how the user can use it**
- When querying boards, present results in a clean summary (table or bullet points), not raw JSON
- If an operation fails, explain why in plain language and suggest a fix — don't just show the error
- Batch related operations (e.g., creating multiple items) into efficient calls
- Before creating a board, ask if the user wants a specific template or structure — suggest popular ones (Kanban, Sprint Board, CRM Pipeline, Bug Tracker)
- When a user asks "what's the status of X?", go beyond raw data — highlight blockers, overdue items, items without assignees, and progress percentages
- If you notice a board has no automations, suggest useful ones ("Want me to set up an automation to notify you when items are marked Done?")
- When creating items, proactively set reasonable defaults (e.g., status = "Not Started", assign to the requesting user if known)
- When working with dates, always use the user's timezone context and flag items that are overdue or due within 24 hours
- After bulk operations (creating 5+ items), provide a count summary and a link to the board rather than listing every item

**Memory & caching (platform-specific):**
> These patterns apply to agents with persistent memory (e.g. OpenClaw workspace). Adapt to your platform's memory model.
- Save every created resource (ID, name, URL, context) to your memory/notes for reuse — include the board name, item name, and what it's for so you can find it later without re-querying
- If a user references a board or item by name and you've seen it before, retrieve the saved ID from memory instead of re-querying
- Cache board schemas after the first fetch — only re-query if the user mentions adding/changing columns

## GraphQL API (Fallback)

Use the GraphQL API directly when MCP tools don't cover the operation (webhooks, file uploads, subitems, pagination, user/workspace queries, activity logs).

- **Endpoint:** `https://api.monday.com/v2` (POST, JSON body with `query` field)
- **File uploads:** `https://api.monday.com/v2/file` (multipart POST, max 500MB)
- **Auth:** Include your API token in the request header (see [API docs](https://developer.monday.com/api-reference))
- **API version:** Include `API-Version: 2024-10` header. Check [developer.monday.com/api-reference](https://developer.monday.com/api-reference) for the current stable version.

> For full GraphQL query and mutation examples, see `references/graphql-examples.md`.

## Core Operations (GraphQL)

All operations use `POST` to the API endpoint with a `query` field. Key operations:

| Operation | Mutation/Query | Key Fields |
|-----------|---------------|------------|
| List boards | `{ boards(limit: 25) { id name } }` | `order_by: used_at` |
| Get board + items | `{ boards(ids: [...]) { columns groups items_page { ... } } }` | Always fetch schema first |
| Create board | `create_board(board_name, board_kind, workspace_id)` | Kinds: `public`, `private`, `share` |
| Create item | `create_item(board_id, group_id, item_name, column_values)` | column_values = JSON string |
| Update columns | `change_multiple_column_values(board_id, item_id, column_values)` | Prefer over single-column updates |
| Create group | `create_group(board_id, group_name, group_color)` | — |
| Add comment | `create_update(item_id, body)` | Supports HTML |
| Create subitem | `create_subitem(parent_item_id, item_name)` | Returns subitem board ID |
| Move item | `move_item_to_group(item_id, group_id)` | — |
| Delete item | `delete_item(item_id)` | Always confirm first |
| Search by column | `items_page_by_column_values(board_id, columns)` | Column ID + value filter |
| Activity logs | `boards(ids) { activity_logs(limit, from, to) }` | Events: `update_column_value`, `create_pulse`, etc. |
| Create webhook | `create_webhook(board_id, url, event)` | Events: `change_column_value`, `create_item`, etc. |
| User info | `{ me { id name email account { slug } } }` | Get account slug for URLs |
| Workspaces | `{ workspaces { id name kind } }` | — |

## Pagination

Use cursor-based pagination for large datasets:

1. First request: include `items_page(limit: 200)` — returns a `cursor`
2. Next pages: use `next_items_page(limit: 200, cursor: "CURSOR_VALUE")`

Recommended page size: 200. Max: 500. Cursors expire after 60 minutes.

## Column Value Formats

When setting column values, use these JSON formats:

| Column Type | JSON Format |
|-------------|-------------|
| Status | `{"label": "Done"}` or `{"index": 1}` |
| Date | `{"date": "2026-03-15"}` or `{"date": "2026-03-15", "time": "14:30:00"}` |
| Person | `{"personsAndTeams": [{"id": 12345, "kind": "person"}]}` |
| Numbers | `"42"` (string) |
| Text | `"Hello world"` |
| Dropdown | `{"labels": ["Option A", "Option B"]}` |
| Checkbox | `{"checked": "true"}` |
| Email | `{"email": "[email protected]", "text": "Contact"}` |
| Phone | `{"phone": "+15551234567", "countryShortName": "US"}` |
| Link | `{"url": "https://example.com", "text": "Click here"}` |
| Timeline | `{"from": "2026-03-01", "to": "2026-03-31"}` |
| Long Text | `{"text": "Detailed description here"}` |
| Rating | `{"rating": 4}` |
| Hour | `{"hour": 14, "minute": 30}` |
| Week | `{"week": {"startDate": "2026-03-09", "endDate": "2026-03-15"}}` |
| Color | `{"color": {"hex": "#FF5AC4"}}` |
| Tags | `{"tag_ids": [123, 456]}` |
| Country | `{"countryCode": "US", "countryName": "United States"}` |
| Location | `{"lat": "40.7128", "lng": "-74.0060", "address": "New York, NY"}` |

All column values must be JSON-stringified when passed to mutations.

## URL Patterns

Build direct links for users:
- **Board:** `https://{account}.monday.com/boards/{board_id}`
- **Item:** `https://{account}.monday.com/boards/{board_id}/pulses/{item_id}`
- **Dashboard:** `https://{account}.monday.com/dashboards/{dashboard_id}`

Get the account slug from: `{ me { account { slug } } }`

## Rate Limits

| Limit | Free | Standard | Pro | Enterprise |
|-------|------|----------|-----|------------|
| Per minute | 1,000 | 1,000 | 2,500 | 5,000 |
| Daily calls | 200 | 1,000 | 10,000 | 25,000 |
| Concurrency | 40 | 40 | 100 | 250 |
| Complexity/query | 5,000,000 | 5,000,000 | 5,000,000 | 5,000,000 |
| Complexity/min | 10,000,000 | 10,000,000 | 10,000,000 | 10,000,000 |
| IP limit | 5,000 per 10s | 5,000 per 10s | 5,000 per 10s | 5,000 per 10s |

When rate-limited (HTTP 429): read the `Retry-After` header and wait that many seconds. Rate-limited requests count as only 0.1 toward the daily limit.

Always include `complexity { before after query }` in queries to monitor budget.

## Error Handling

monday.com returns errors in two ways:
- **HTTP 200 with `errors` array** — application-level errors (invalid query, missing permissions)
- **HTTP 4xx/5xx** — transport-level errors (rate limit, auth failure, server error)

Common error codes:
- `InvalidColumnIdException` — column ID doesn't exist on the board
- `InvalidBoardIdException` — board doesn't exist or no access
- `ItemsLimitationException` — board reached item limit
- `CorrectedValueException` — value was auto-corrected (check `corrected_value`)
- `ColumnValueException` — invalid format for column type
- `UserUnauthorizedException` — token doesn't have required permissions
- `ComplexityException` — query too expensive, simplify or paginate
- `ResourceNotFoundException` — ID doesn't exist

## monday.com AI Features

- **AI Blocks** — modular AI in columns and automations: Categorize, Summarize, Translate, Extract Info, Detect Sentiment, Improve Text, Write with AI, Custom Prompt. Available on Pro+ (500 free credits/month)
- **monday Sidekick** — conversational AI assistant for cross-board analysis, report generation, content drafting, task creation
- **monday AI Agents** — autonomous workers: Lead Agent (qualifies prospects), SDR Agent (outreach calls, SMS, meeting booking)
- **monday Vibe** — AI no-code app builder, turns natural language into custom apps

## Use Cases

| Scenario | What to Do |
|----------|-----------|
| "Create a project board" | Create board → add groups (phases/sprints) → add columns → report board URL |
| "Add tasks to my board" | Get board schema → create items with proper column values → return item URLs |
| "What's the status of project X?" | Query board items → summarize by status/group → highlight blockers |
| "Move done items to archive" | Search by status "Done" → move each to archive group |
| "Set up a sprint" | Create group → create items → assign people → set dates → return board link |
| "Track a bug" | Create item in dev board → set priority/status → assign → add description as update |
| "Create a CRM pipeline" | Create board with deal stages as groups → add contact/value/date columns |
| "Generate a weekly report" | Query multiple boards → aggregate by status → format as summary with metrics |
| "Automate status notifications" | Create webhook for status changes → explain how to connect to Slack/email |
| "What changed this week?" | Query activity logs → summarize by user/event type → highlight key changes |
| "Upload a spec to a task" | Upload file to item's files column via multipart POST → return file URL |

## Security & Legal Guidelines

**Data handling:**
- Never log or store API tokens in conversation history, memory files, or updates
- When displaying board data, respect that it may contain confidential business information
- Don't share board data across different users' sessions or conversations
- monday.com customer data is never used to train AI models

**Permissions:**
- Personal API tokens inherit the user's UI permissions — if they can't see a board in the UI, the API won't return it
- Always verify board access before performing operations
- Don't delete items, boards, or groups without explicit user confirmation
- For destructive operations (delete, archive), always ask first and explain what will happen

**Rate limiting etiquette:**
- Space out bulk operations (add 100ms delay between mutations)
- Use `change_multiple_column_values` instead of multiple single-column updates
- Cache board schemas and user IDs — don't re-query every turn
- If rate-limited, wait the full `Retry-After` duration before retrying

**Compliance:**
- Don't create automations that send external emails/notifications without user awareness
- Don't modify workspace-level settings without explicit permission
- When creating webhooks, inform the user and document the endpoint
- Respect workspace data isolation — don't query across workspaces unless asked

## Links

- Developer docs: https://developer.monday.com
- API reference: https://developer.monday.com/api-reference
- MCP server: https://github.com/mondaycom/mcp
- Apps marketplace: https://monday.com/marketplace
- Status page: https://status.monday.com
