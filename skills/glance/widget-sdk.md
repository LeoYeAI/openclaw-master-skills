# Widget SDK Documentation

The Glance Widget SDK enables AI assistants (and developers) to create custom widgets that display data from any API. Widgets are written in JSX/TSX and have access to a rich set of UI components and data-fetching hooks.

## Table of Contents

- [When to Use This Skill](#when-to-use-this-skill)
- [Prompt Examples](#prompt-examples)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Common Workflows](#common-workflows)
- [Widget Creation API](#widget-creation-api)
- [Credential Management](#credential-management)
- [When to Use Server Code](#when-to-use-server-code)
- [Reading Widget Data](#reading-widget-data)
- [Components](#components)
- [Hooks](#hooks)
- [Server-Side Code](#server-side-code)
- [Icons](#icons)
- [Widget Lifecycle](#widget-lifecycle)
- [Error Handling Patterns](#error-handling-patterns)
- [Output Format](#output-format)
- [Full API Reference](#full-api-reference)
- [Best Practices](#best-practices)
- [OpenClaw Integration Guide](#openclaw-integration-guide)

---

## When to Use This Skill

Use the Glance Widget SDK when a user's intent matches any of these patterns:

### Widget Creation & Management

- User wants to **create a widget** or dashboard element
- User wants to **update, modify, or reconfigure** an existing widget
- User wants to **delete or remove** a widget
- User wants to **move or resize** widgets on the dashboard

> **Note:** For moving, resizing, or reorganizing widget layouts (especially for mobile/tablet/desktop), see the [Dashboard API](./dashboard-api.md).

### Data Visualization & Tracking

- User asks to **see their GitHub PRs**, issues, or repository stats
- User wants to **track API usage** (Anthropic, OpenAI, etc.)
- User asks about **calendar events** or schedules
- User wants a **weather widget** for any location
- User wants to **visualize or track any data** from an external API
- User mentions wanting to **monitor** something

### Dashboard Queries

- User asks **"what's on my dashboard"** or "show me my dashboard"
- User asks **"what needs my attention"** or "any updates?"
- User wants a **summary of their widgets' data**
- User asks about the **status of tracked items** (PRs, usage, etc.)

### Explicit Mentions

- User mentions **"Glance"** by name
- User mentions **"widgets"** or **"dashboard"**
- User asks about **"credentials"** for widget APIs

---

## Prompt Examples

Real phrases users might say that should trigger Glance widget actions:

### Creating Widgets

- "Show me my GitHub PRs for libra and glance"
- "Add a weather widget for NYC"
- "Create a widget tracking my Anthropic API spend"
- "I want to see my Linear issues on my dashboard"
- "Can you add a calendar widget?"
- "Track the open issues on acfranzen/glance"
- "Show me my Notion tasks"

### Querying Dashboard

- "What's on my dashboard?"
- "What needs my attention?"
- "Give me a status update"
- "Summarize my widgets"
- "Any new PRs?"
- "What does my dashboard show right now?"

### Modifying Widgets

- "Update the GitHub widget to show closed PRs too"
- "Change the weather widget to show SF instead of NYC"
- "Make the PR widget bigger"
- "Move the GitHub widget to the top right"
- "Rename the weather widget to 'Local Weather'"

### Deleting Widgets

- "Delete the clock widget"
- "Remove the weather widget"
- "Get rid of the old PR tracker"

### Credential Management

- "I need to add my GitHub token"
- "Store my OpenWeather API key"
- "What credentials do I have set up?"
- "Delete my old Notion token"

---

## Prerequisites

Before using the Glance Widget SDK:

### 1. Glance Must Be Running

```bash
cd ~/projects/glance
npm run dev
```

The server should be accessible at `http://localhost:3000` (or configured port).

### 2. Authentication Token

All API requests require a Bearer token. Obtain this from:

- Glance settings page, or
- Environment variable `GLANCE_API_TOKEN`

```http
Authorization: Bearer <your-token-here>
```

### 3. Credentials for Authenticated APIs

For widgets that access external APIs (GitHub, Anthropic, etc.), store credentials first:

```http
POST /api/credentials
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "github",
  "name": "My GitHub Token",
  "value": "ghp_your_personal_access_token"
}
```

**Common credentials needed:**

| Widget Type       | Credential Key | How to Get                                                     |
| ----------------- | -------------- | -------------------------------------------------------------- |
| GitHub PRs/Issues | `github`       | [GitHub Settings → Tokens](https://github.com/settings/tokens) |
| Anthropic Usage   | `anthropic`    | [Anthropic Console](https://console.anthropic.com/)            |
| OpenAI Usage      | `openai`       | [OpenAI API Keys](https://platform.openai.com/api-keys)        |
| Weather           | `openweather`  | [OpenWeatherMap](https://openweathermap.org/api)               |
| Notion            | `notion`       | [Notion Integrations](https://www.notion.so/my-integrations)   |
| Linear            | `linear`       | [Linear Settings → API](https://linear.app/settings/api)       |

---

## Quick Start

Here's a minimal widget that displays a greeting:

```tsx
function Widget() {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Hello World</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Welcome to Glance!</p>
      </CardContent>
    </Card>
  );
}
```

A more practical widget that fetches data:

```tsx
function Widget() {
  const { data, loading, error } = useData("github", {
    endpoint: "/user/repos",
    params: { sort: "updated", per_page: 5 },
  });

  if (loading) return <Loading />;
  if (error) return <ErrorDisplay message={error.message} />;

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>My Repos</CardTitle>
      </CardHeader>
      <CardContent>
        <List
          items={data.map((repo) => ({
            title: repo.name,
            subtitle: repo.description,
            badge: repo.private ? "Private" : "Public",
          }))}
        />
      </CardContent>
    </Card>
  );
}
```

---

## Common Workflows

Step-by-step flows for the most common operations.

### Workflow 1: Create a Widget

```
1. CHECK CREDENTIALS
   GET /api/credentials
   → Look for required credential (e.g., "github" provider)
   → If missing, ask user and POST /api/credentials

2. CREATE WIDGET DEFINITION
   POST /api/widgets
   {
     "name": "GitHub PRs",
     "description": "Shows open pull requests",
     "source_code": "function Widget() { ... }",
     "server_code": "const token = await getCredential('github'); ...",
     "server_code_enabled": true,
     "data_providers": ["github"],
     "default_size": { "w": 4, "h": 3 },
     "min_size": { "w": 2, "h": 2 },
     "refresh_interval": 300
   }
   → Returns widget definition with ID (e.g., "cw_abc123")

3. ADD WIDGET TO DASHBOARD
   POST /api/widgets/instances
   {
     "type": "custom",
     "title": "GitHub PRs",
     "custom_widget_id": "cw_abc123",
     "config": { "owner": "acfranzen", "repo": "libra" }
   }

4. VERIFY CREATION
   → Check response status (201 = success)
   → Inform user: "Done! Your GitHub PRs widget is now on the dashboard."
```

### Workflow 2: Update a Widget

```
1. GET CURRENT STATE
   GET /api/widgets/:slug
   → Retrieve current source_code, server_code, etc.

2. MODIFY WIDGET DEFINITION (code changes)
   PATCH /api/widgets/:slug
   {
     "source_code": "function Widget() { ... }",
     "server_code": "..."
   }
   → Only include fields being changed

3. MODIFY WIDGET INSTANCE (config, position, size)
   PATCH /api/widgets/instances/:id
   {
     "config": { "owner": "acfranzen", "repo": "glance", "show_drafts": true },
     "position": { "x": 0, "y": 0, "w": 6, "h": 4 }
   }

4. CONFIRM
   → Check response status (200 = success)
   → Inform user: "Updated! The widget now shows draft PRs too."
```

### Workflow 3: Read Dashboard for User

```
1. GET ALL WIDGET INSTANCES
   GET /api/widgets/instances
   → Returns list of widgets on dashboard with their config

2. FOR WIDGETS WITH SERVER CODE, EXECUTE TO GET FRESH DATA
   For each custom widget:
     POST /api/widgets/:slug/execute
     { "params": { ... } }
     → Returns current data (PRs, weather, usage, etc.)

3. SUMMARIZE FOR USER
   Combine data into natural language:
   "Your dashboard shows:
    - 3 open PRs on libra (newest: 'Add auth' by zeus)
    - Weather in NYC: 45°F, cloudy
    - API usage: 62% of monthly limit"
```

### Workflow 4: Delete a Widget

```
1. CONFIRM WITH USER (optional but recommended)
   "Are you sure you want to delete the weather widget?"

2. DELETE WIDGET INSTANCE (removes from dashboard)
   DELETE /api/widgets/instances/:id
   → Returns { "success": true }

3. OPTIONALLY DELETE WIDGET DEFINITION (removes the code)
   DELETE /api/widgets/:slug
   → Returns { "success": true, "deleted_id": "cw_xxx" }

4. CONFIRM
   → Inform user: "Done! The weather widget has been removed."
```

### Workflow 5: Handle Missing Credentials

```
1. DETECT MISSING CREDENTIAL
   GET /api/credentials
   → Check if provider "github" exists in credentials list

2. EXPLAIN TO USER
   "I need a GitHub personal access token to show your PRs.
    You can create one at https://github.com/settings/tokens
    with the 'repo' scope. Paste it here when ready."

3. RECEIVE AND STORE
   User provides: "ghp_xxxxxxxxxxxx"
   POST /api/credentials
   {
     "provider": "github",
     "name": "GitHub Token",
     "value": "ghp_xxxxxxxxxxxx"
   }

4. CONTINUE WITH ORIGINAL TASK
   Now create the widget as requested.
```

---

## Widget Creation API

Glance uses a **two-step process** for custom widgets:

1. **Widget Definition** (`/api/widgets`) — The code template
2. **Widget Instance** (`/api/widgets/instances`) — A widget placed on the dashboard

All endpoints require authentication via Bearer token.

### Step 1: Create Widget Definition

```http
POST /api/widgets
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "GitHub PRs",
  "description": "Shows open pull requests from a repository",
  "source_code": "function Widget() { return <Card>...</Card>; }",
  "server_code": "const token = await getCredential('github'); ...",
  "server_code_enabled": true,
  "data_providers": ["github"],
  "default_size": { "w": 4, "h": 3 },
  "min_size": { "w": 2, "h": 2 },
  "refresh_interval": 300
}
```

**Request Fields:**

| Field                 | Type     | Required | Description                                            |
| --------------------- | -------- | -------- | ------------------------------------------------------ |
| `name`                | string   | Yes      | Display name for the widget                            |
| `source_code`         | string   | Yes      | JSX/TSX widget code (must define `Widget` function)    |
| `description`         | string   | No       | Description of the widget                              |
| `slug`                | string   | No       | Unique identifier (auto-generated if not provided)     |
| `server_code`         | string   | No       | Server-side code for secure API calls                  |
| `server_code_enabled` | boolean  | No       | Must be `true` to enable server code execution         |
| `data_providers`      | string[] | No       | List of providers used (e.g., `["github"]`)            |
| `default_size`        | object   | No       | Default size `{ w: number, h: number }` (default: 4x3) |
| `min_size`            | object   | No       | Minimum size `{ w: number, h: number }` (default: 2x2) |
| `refresh_interval`    | number   | No       | Auto-refresh interval in seconds (default: 300)        |

**Response (201 Created):**

```json
{
  "id": "cw_abc123xyz",
  "name": "GitHub PRs",
  "slug": "github-prs",
  "description": "Shows open pull requests from a repository",
  "source_code": "function Widget() { ... }",
  "server_code": "const token = ...",
  "server_code_enabled": true,
  "data_providers": ["github"],
  "default_size": { "w": 4, "h": 3 },
  "min_size": { "w": 2, "h": 2 },
  "refresh_interval": 300,
  "enabled": true,
  "created_at": "2026-02-01T12:00:00.000Z",
  "updated_at": "2026-02-01T12:00:00.000Z"
}
```

### Step 2: Add Widget to Dashboard

```http
POST /api/widgets/instances
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "custom",
  "title": "GitHub PRs",
  "custom_widget_id": "cw_abc123xyz",
  "config": { "owner": "acfranzen", "repo": "glance" },
  "position": { "x": 0, "y": 0, "w": 4, "h": 3 }
}
```

**Request Fields:**

| Field              | Type   | Required | Description                                                 |
| ------------------ | ------ | -------- | ----------------------------------------------------------- |
| `type`             | string | Yes      | Must be `"custom"` for custom widgets                       |
| `title`            | string | No       | Display title (defaults to widget name)                     |
| `custom_widget_id` | string | Yes      | ID of the widget definition (from step 1)                   |
| `config`           | object | No       | Configuration accessible via `useConfig()`                  |
| `position`         | object | No       | Position and size `{ x, y, w, h }` (auto-placed if omitted) |

**Response (201 Created):**

```json
{
  "id": "widget_xyz789",
  "type": "custom",
  "title": "GitHub PRs",
  "custom_widget_id": "cw_abc123xyz",
  "config": { "owner": "acfranzen", "repo": "glance" },
  "position": { "x": 0, "y": 0, "w": 4, "h": 3 },
  "created_at": "2026-02-01T12:00:00.000Z",
  "updated_at": "2026-02-01T12:00:00.000Z"
}
```

### Get All Widget Definitions

```http
GET /api/widgets
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "custom_widgets": [
    {
      "id": "cw_abc123",
      "name": "GitHub PRs",
      "slug": "github-prs",
      "description": "Shows open pull requests",
      "default_size": { "w": 4, "h": 3 },
      "enabled": true,
      "created_at": "2026-02-01T12:00:00.000Z"
    }
  ]
}
```

### Get a Single Widget Definition

```http
GET /api/widgets/:slug
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "id": "cw_abc123",
  "name": "GitHub PRs",
  "slug": "github-prs",
  "description": "Shows open pull requests",
  "source_code": "function Widget() { ... }",
  "server_code": "const token = ...",
  "server_code_enabled": true,
  "data_providers": ["github"],
  "default_size": { "w": 4, "h": 3 },
  "min_size": { "w": 2, "h": 2 },
  "refresh_interval": 300,
  "enabled": true,
  "created_at": "2026-02-01T12:00:00.000Z",
  "updated_at": "2026-02-01T12:00:00.000Z"
}
```

### Update a Widget Definition

```http
PATCH /api/widgets/:slug
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "GitHub PRs (Updated)",
  "source_code": "function Widget() { ... }",
  "server_code_enabled": true
}
```

All fields are optional. Only provided fields will be updated.

**Response (200 OK):** Returns the updated widget definition.

### Delete a Widget Definition

```http
DELETE /api/widgets/:slug
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "deleted_id": "cw_abc123"
}
```

### Get All Widget Instances (Dashboard)

```http
GET /api/widgets/instances
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "widgets": [
    {
      "id": "widget_xyz789",
      "type": "custom",
      "title": "GitHub PRs",
      "custom_widget_id": "cw_abc123",
      "config": { "owner": "acfranzen", "repo": "glance" },
      "position": { "x": 0, "y": 0, "w": 4, "h": 3 },
      "created_at": "2026-02-01T12:00:00.000Z"
    }
  ]
}
```

---

## Credential Management

Credentials store API keys and tokens securely for use in server-side widget code. All credentials are encrypted at rest and only decrypted when accessed via `getCredential()` in server code.

### Store a Credential

```http
POST /api/credentials
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "github",
  "name": "My GitHub Token",
  "value": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

**Request Fields:**

| Field      | Type   | Required | Description                              |
| ---------- | ------ | -------- | ---------------------------------------- |
| `provider` | string | Yes      | Provider type (see table below)          |
| `name`     | string | Yes      | Display name for this credential         |
| `value`    | string | Yes      | The API key or token (encrypted at rest) |

**Response (200 OK):**

```json
{
  "success": true,
  "credential": {
    "id": "cred_abc123",
    "provider": "github",
    "name": "My GitHub Token",
    "created_at": "2026-02-01T12:00:00.000Z",
    "updated_at": "2026-02-01T12:00:00.000Z"
  }
}
```

**Note:** The value is never returned after storage.

### List Credentials

```http
GET /api/credentials
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "credentials": [
    {
      "id": "cred_abc123",
      "provider": "github",
      "name": "My GitHub Token",
      "created_at": "2026-02-01T12:00:00.000Z"
    },
    {
      "id": "cred_def456",
      "provider": "openweather",
      "name": "Weather API Key",
      "created_at": "2026-02-01T12:00:00.000Z"
    }
  ],
  "status": {
    "github": { "configured": true, "source": "database" },
    "anthropic": { "configured": false, "source": null },
    "openweather": { "configured": true, "source": "database" }
  },
  "providers": [
    {
      "id": "github",
      "name": "GitHub",
      "description": "GitHub API for PR widgets"
    },
    {
      "id": "anthropic",
      "name": "Anthropic",
      "description": "Claude API (Admin key for usage widgets)"
    }
  ]
}
```

### Get a Credential (Metadata Only)

```http
GET /api/credentials/:id
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "id": "cred_abc123",
  "provider": "github",
  "name": "My GitHub Token",
  "metadata": {},
  "created_at": "2026-02-01T12:00:00.000Z",
  "updated_at": "2026-02-01T12:00:00.000Z"
}
```

**Note:** This endpoint returns metadata only, not the decrypted value. Use `getCredential()` in server code to access the value.

### Delete a Credential

```http
DELETE /api/credentials/:id
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "success": true
}
```

### Available Providers

| Provider    | ID            | Description                       |
| ----------- | ------------- | --------------------------------- |
| GitHub      | `github`      | GitHub API for PR widgets         |
| Anthropic   | `anthropic`   | Claude API (Admin key for usage)  |
| OpenAI      | `openai`      | GPT API (Admin key for usage)     |
| Vercel      | `vercel`      | Vercel API for deployment widgets |
| OpenWeather | `openweather` | Weather data API                  |

### Agent Credentials

Some widgets require authentication or tools that exist on the **OpenClaw agent's machine** rather than stored in Glance. These are called "agent credentials" and use the `type: "agent"` in the widget package.

| Credential Type | Where It Lives | Example |
|-----------------|----------------|---------|
| `api_key` | Glance database (encrypted) | GitHub PAT, OpenWeather key |
| `local_software` | Agent's machine | Homebrew, Docker |
| `oauth` | Glance database | Google Calendar token |
| `agent` | Agent environment | `gh` CLI auth, `gcloud` auth |

**Agent credential fields:**

```typescript
{
  "id": "github_cli",
  "type": "agent",
  "name": "GitHub CLI",
  "description": "OpenClaw agent needs `gh` CLI authenticated",
  "agent_tool": "gh",                    // The CLI tool name
  "agent_auth_check": "gh auth status",  // Command to verify auth
  "agent_auth_instructions": "Run `gh auth login` on the machine running OpenClaw"
}
```

**Why use agent credentials?**

- **CLI tools are more powerful**: `gh pr list` returns richer data than the GitHub REST API
- **No token management**: The agent uses its existing CLI authentication
- **Local machine access**: Some data (like `gcloud` configs) can't be fetched via API

**Example: Widget using agent credentials**

```json
{
  "credentials": [
    {
      "id": "github_cli",
      "type": "agent",
      "name": "GitHub CLI",
      "description": "Agent needs gh CLI authenticated to GitHub",
      "agent_tool": "gh",
      "agent_auth_check": "gh auth status",
      "agent_auth_instructions": "Run `gh auth login` on the agent machine"
    }
  ],
  "fetch": {
    "type": "agent_refresh",
    "instructions": "Run `gh pr list --repo owner/repo --json number,title,author,url,createdAt,isDraft` and POST results to /api/widgets/{slug}/cache",
    "schedule": "*/30 * * * *"
  }
}
```

When importing a widget with agent credentials, Glance will:
1. Show a warning that the widget requires agent-side authentication
2. Display the `agent_tool` and `agent_auth_check` command
3. Mark credentials as "Agent Required" (can't be verified server-side)

### Best Practices

1. **Check before creating widgets:** Always verify required credentials exist before creating a widget that depends on them.

2. **Prompt users for missing credentials:** If a credential is missing, ask the user to provide it rather than failing silently.

3. **Use descriptive error messages:** When a credential is missing, tell the user exactly which credential is needed and how to provide it.

```typescript
// Example: Check if credential exists before creating widget
const response = await fetch("/api/credentials", {
  headers: { Authorization: `Bearer ${token}` },
});
const { status } = await response.json();

if (!status.github?.configured) {
  // Prompt user for GitHub token
  throw new Error(
    "GitHub token required. Please provide your GitHub personal access token.",
  );
}
```

---

## When to Use Server Code

Deciding between client-side `useData` and server-side code depends on your data source and security requirements.

### Decision Tree

```
Does the API require authentication (API key, OAuth token)?
├── YES → Use server code
└── NO
    └── Are you handling any secrets or tokens?
        ├── YES → Use server code
        └── NO
            └── Do you need to transform, aggregate, or combine data from multiple sources?
                ├── YES → Server code is recommended (cleaner, faster)
                └── NO → Client-side useData is fine
```

### When to Use Server Code

- **Authenticated APIs:** GitHub, Anthropic, OpenAI, Notion, Linear—any API requiring tokens
- **Secret handling:** Even if an API is public, if you're using API keys for rate limits
- **Data transformation:** Combining multiple API calls, filtering, or reshaping data
- **Rate limit management:** Server code can implement caching or throttling
- **Sensitive business logic:** Code you don't want exposed in the browser

### When Client-Side is Fine

- **Public APIs:** Open data sources with no authentication
- **Static data:** Configuration or display-only widgets
- **Simple displays:** Widgets that just render provided config data

### Examples

**✅ Use server code:**

```javascript
// GitHub PR fetching with authentication
const token = await getCredential("github");
const response = await fetch("https://api.github.com/repos/owner/repo/pulls", {
  headers: { Authorization: `Bearer ${token}` },
});
return response.json();
```

**✅ Use client-side:**

```tsx
// Simple counter widget - no external data
function Widget() {
  const { state, setState } = useWidgetState("count", 0);
  return <Button onClick={() => setState(state + 1)}>{state}</Button>;
}
```

---

## Reading Widget Data

OpenClaw agents can read widget data to understand what's displayed on the dashboard and summarize it for users.

### Execute Server Code

Triggers execution of the widget's server code to fetch fresh data.

```http
POST /api/widgets/:slug/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "params": {
    "owner": "acfranzen",
    "repo": "glance"
  }
}
```

**Response (200 OK):**

```json
{
  "data": {
    "prs": [
      { "number": 42, "title": "Add new feature", "author": "octocat" },
      { "number": 41, "title": "Fix bug", "author": "developer" }
    ],
    "fetchedAt": "2026-02-01T12:00:00.000Z"
  }
}
```

**Error Response:**

```json
{
  "error": "GitHub API rate limit exceeded"
}
```

### How OpenClaw Uses Widget Data

OpenClaw agents can "read the dashboard" by:

1. **Listing widget instances:** `GET /api/widgets` to see what's on the dashboard
2. **Executing each widget's server code:** `POST /api/widgets/:slug/execute` for fresh data
3. **Summarizing for users:** Convert the raw data into natural language

**Example agent flow:**

```
User: "What's on my dashboard?"

Agent:
1. GET /api/widgets/instances → [{ custom_widget_id: "cw_abc", config: {...} }, ...]
2. GET /api/widgets → [{ slug: "github-prs" }, { slug: "weather" }]
3. POST /api/widgets/github-prs/execute → { data: { prs: [...] } }
4. POST /api/widgets/weather/execute → { data: { temp: 72, conditions: "sunny" } }

Response: "Your dashboard shows:
- 3 open PRs on github/glance (newest: 'Add widget SDK docs' by zeus)
- Weather in SF: 72°F and sunny
- API usage: 45% of monthly limit"
```

---

## Components

All components are pre-imported and available in the widget sandbox. Most components are from [shadcn/ui](https://ui.shadcn.com/docs/components) — see their documentation for full prop references and examples.

**Full component docs:** [ui.shadcn.com/docs/components](https://ui.shadcn.com/docs/components)

### Layout Components

#### Card

Container component available for use within widgets if needed for nested cards or sections.

> **⚠️ Important:** Do NOT wrap your entire widget in a `<Card>`. The framework's `CustomWidgetWrapper` already provides an outer card with:
> - Widget title header
> - Refresh button
> - "Updated X ago" footer
>
> Your widget should render **content only** — just a `<div>` with your data, not a Card.

```tsx
// ✅ CORRECT - render content directly
function Widget({ serverData }) {
  return (
    <div className="space-y-3">
      <p>{serverData.message}</p>
      <List items={serverData.items} />
    </div>
  );
}

// ❌ WRONG - don't wrap in Card (causes double headers, wastes space)
function Widget({ serverData }) {
  return (
    <Card className="h-full">
      <CardHeader><CardTitle>Title</CardTitle></CardHeader>
      <CardContent>...</CardContent>
    </Card>
  );
}
```

#### Stack

Flexbox container for arranging items.

```tsx
<Stack direction="row" gap={2} align="center" justify="between">
  <span>Left</span>
  <span>Right</span>
</Stack>
```

Props:

- `direction`: `'row'` | `'column'` (default: `'column'`)
- `gap`: number (spacing multiplier, default: `2`)
- `align`: `'start'` | `'center'` | `'end'` | `'stretch'`
- `justify`: `'start'` | `'center'` | `'end'` | `'between'` | `'around'`
- `wrap`: boolean

#### Grid

CSS Grid container.

```tsx
<Grid cols={2} gap={3}>
  <Stat label="Metric 1" value={42} />
  <Stat label="Metric 2" value={100} />
</Grid>
```

Props:

- `cols`: number (default: `2`)
- `gap`: number (default: `2`)

### Data Display Components

#### Stat

Display a metric with optional trend indicator.

```tsx
<Stat label="API Usage" value={72} suffix="%" change={5.2} trend="up" />
```

Props:

- `label`: string (required)
- `value`: string | number (required)
- `prefix`: string (e.g., "$")
- `suffix`: string (e.g., "%")
- `change`: number (percentage change)
- `trend`: `'up'` | `'down'` | `'neutral'`

#### Progress

Progress bar with variants.

```tsx
<Progress value={72} max={100} showLabel variant="warning" />
```

Props:

- `value`: number (required)
- `max`: number (default: `100`)
- `showLabel`: boolean (show percentage label)
- `variant`: `'default'` | `'success'` | `'warning'` | `'error'`
- `size`: `'sm'` | `'md'` | `'lg'`

#### Badge

Status badges/labels.

```tsx
<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Failed</Badge>
```

Props:

- `variant`: `'default'` | `'success'` | `'warning'` | `'error'` | `'info'`

#### List

Display a list of items with optional badges.

```tsx
<List
  items={[
    {
      title: "Item 1",
      subtitle: "Description",
      badge: "New",
      badgeVariant: "info",
    },
    { title: "Item 2", subtitle: "Another item" },
  ]}
  emptyMessage="No items found"
/>
```

Props:

- `items`: Array of `{ title, subtitle?, badge?, badgeVariant? }`
- `emptyMessage`: string

#### Avatar

User avatars with fallback.

```tsx
<Avatar>
  <AvatarImage src="https://github.com/user.png" />
  <AvatarFallback>JD</AvatarFallback>
</Avatar>
```

### State Components

#### Loading

Loading spinner with optional message.

```tsx
<Loading message="Fetching data..." />
```

#### ErrorDisplay

Error state with optional retry button.

```tsx
<ErrorDisplay message="Failed to load data" retry={() => refresh()} />
```

#### Empty

Empty state placeholder.

```tsx
<Empty message="No results found" />
```

### Form Components

#### Button

Standard button component.

```tsx
<Button onClick={handleClick} variant="outline" size="sm">
  Click me
</Button>
```

#### Input

Text input field.

```tsx
<Input
  placeholder="Enter value..."
  value={text}
  onChange={(e) => setText(e.target.value)}
/>
```

#### Label

Form label.

```tsx
<Label htmlFor="input-id">Field Label</Label>
```

#### Switch

Toggle switch.

```tsx
<Switch checked={enabled} onCheckedChange={setEnabled} />
```

### Other Components

#### Tabs

Tabbed content.

```tsx
<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```

#### Tooltip

Hover tooltips.

```tsx
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger>Hover me</TooltipTrigger>
    <TooltipContent>Tooltip text</TooltipContent>
  </Tooltip>
</TooltipProvider>
```

#### Separator

Visual divider.

```tsx
<Separator className="my-4" />
```

---

## Hooks

### useData

Fetch data from a configured data provider. **Both arguments are required.**

```tsx
const { data, loading, error, refresh } = useData<ResponseType>(
  provider,
  query,
);
```

**⚠️ Important:** Always pass both arguments, even when using server code:
```tsx
// ✅ Correct - both arguments provided
const { data, loading, error } = useData('github', {});
const { data, loading, error } = useData('github', { endpoint: '/pulls' });

// ❌ Wrong - will throw "Cannot read properties of undefined"
const { data, loading, error } = useData();
```

Parameters:

- `provider`: string **(required)** - The data provider slug (e.g., `'github'`, `'anthropic'`, `'vercel'`)
- `query`: object **(required, can be empty `{}`)** - Query configuration
  - `endpoint`: string - API endpoint path
  - `params`: object - Query parameters
  - `method`: `'GET'` | `'POST'` (default: `'GET'`)
  - `body`: object - Request body for POST requests

Returns:

- `data`: T | null - The response data
- `loading`: boolean - Loading state
- `error`: Error | null - Error if request failed
- `refresh`: () => void - Function to manually refresh data

Example:

```tsx
const { data, loading, error, refresh } = useData<PullRequest[]>("github", {
  endpoint: "/repos/anthropics/claude-code/pulls",
  params: { state: "open", per_page: 10 },
});
```

### useConfig

Access the widget's configuration.

```tsx
const config = useConfig();
const apiKey = config.apiKey;
const threshold = config.threshold || 80;
```

### useWidgetState

Manage widget-local state.

```tsx
const { state, setState } = useWidgetState<number>("counter", 0);

// Update state
setState(state + 1);
setState((prev) => prev + 1);
```

---

## Server-Side Code

For advanced use cases, widgets can execute server-side code to fetch or process data. This is useful when you need to:

- Make authenticated API calls without exposing credentials to the browser
- Process or transform data before sending to the client
- Access credentials securely via `getCredential()`

### Writing Server Code

Server code runs in a sandboxed Node.js VM with limited capabilities:

```javascript
// Server code example
const token = await getCredential("github");

const response = await fetch("https://api.github.com/user", {
  headers: {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github+json",
  },
});

const user = await response.json();
return { user, fetchedAt: new Date().toISOString() };
```

### Available in Server Code

- `fetch` - Make HTTP requests
- `getCredential(provider)` - Get decrypted credential for a provider
- `params` - Parameters passed from the widget
- `console.log/warn/error` - Logging (prefixed with `[server-code]`)
- Standard JS built-ins: `JSON`, `Date`, `Math`, `Array`, `Object`, `Promise`, `Map`, `Set`, etc.

### Blocked in Server Code

For security, the following are blocked:

- `require()` / `import` - No module loading
- `eval()` / `new Function()` - No dynamic code execution
- `process` / `Buffer` - No Node.js process access
- `fs` / `child_process` - No filesystem or shell access
- `global` / `globalThis` - No global object access

### Accessing Server Data in Widget

When server code is enabled, `useData` automatically routes through the server executor:

```tsx
function Widget() {
  // This will execute your server code instead of direct API call
  const { data, loading, error } = useData("github", {
    endpoint: "/custom", // Can be anything - server code controls the actual request
    params: { owner: "anthropics", repo: "claude-code" },
  });

  // ...
}
```

---

## Icons

A curated subset of [Lucide React](https://lucide.dev/icons/) icons is available via the `Icons` object. Only the icons listed below are available in the widget sandbox — if you need an icon not in this list, use one with similar meaning.

```tsx
<Icons.GitPullRequest className="h-4 w-4" />
<Icons.Clock className="h-4 w-4 text-muted-foreground" />
```

**Full icon reference:** [lucide.dev/icons](https://lucide.dev/icons/)

Available icons (sandbox subset):

| Icon           | Name                   |
| -------------- | ---------------------- |
| Activity       | `Icons.Activity`       |
| AlertCircle    | `Icons.AlertCircle`    |
| AlertTriangle  | `Icons.AlertTriangle`  |
| ArrowDown      | `Icons.ArrowDown`      |
| ArrowUp        | `Icons.ArrowUp`        |
| BarChart2      | `Icons.BarChart2`      |
| Check          | `Icons.Check`          |
| ChevronRight   | `Icons.ChevronRight`   |
| Clock          | `Icons.Clock`          |
| Code           | `Icons.Code`           |
| Coffee         | `Icons.Coffee`         |
| Copy           | `Icons.Copy`           |
| Download       | `Icons.Download`       |
| Edit           | `Icons.Edit`           |
| ExternalLink   | `Icons.ExternalLink`   |
| Eye            | `Icons.Eye`            |
| EyeOff         | `Icons.EyeOff`         |
| FileText       | `Icons.FileText`       |
| GitPullRequest | `Icons.GitPullRequest` |
| Globe          | `Icons.Globe`          |
| Heart          | `Icons.Heart`          |
| Home           | `Icons.Home`           |
| Info           | `Icons.Info`           |
| Loader2        | `Icons.Loader2`        |
| Lock           | `Icons.Lock`           |
| Mail           | `Icons.Mail`           |
| MessageSquare  | `Icons.MessageSquare`  |
| Minus          | `Icons.Minus`          |
| MoreHorizontal | `Icons.MoreHorizontal` |
| MoreVertical   | `Icons.MoreVertical`   |
| Package        | `Icons.Package`        |
| Plus           | `Icons.Plus`           |
| RefreshCw      | `Icons.RefreshCw`      |
| Search         | `Icons.Search`         |
| Settings       | `Icons.Settings`       |
| Star           | `Icons.Star`           |
| Trash          | `Icons.Trash`          |
| TrendingDown   | `Icons.TrendingDown`   |
| TrendingUp     | `Icons.TrendingUp`     |
| Unlock         | `Icons.Unlock`         |
| Upload         | `Icons.Upload`         |
| User           | `Icons.User`           |
| X              | `Icons.X`              |
| Zap            | `Icons.Zap`            |

---

## Widget Lifecycle

### Creating a Widget

1. **Check credentials:** Verify any required credentials exist
2. **Create widget definition:** POST to `/api/widgets`
3. **Add to dashboard:** POST to `/api/widgets/instances` with `custom_widget_id`
4. **Verify creation:** Widget appears on dashboard

```http
# Step 1: Create definition
POST /api/widgets
{
  "name": "My Widget",
  "source_code": "function Widget() { return <Card><CardContent>Hello!</CardContent></Card>; }",
  "default_size": { "w": 4, "h": 3 }
}

# Step 2: Add to dashboard
POST /api/widgets/instances
{
  "type": "custom",
  "title": "My Widget",
  "custom_widget_id": "cw_abc123"
}
```

### Updating a Widget

**Update the definition (code changes):**

```http
PATCH /api/widgets/my-widget
Authorization: Bearer <token>
Content-Type: application/json

{
  "source_code": "function Widget() { return <Card><CardContent>Updated!</CardContent></Card>; }",
  "server_code": "...",
  "server_code_enabled": true
}
```

**Update the instance (config, position, size):**

```http
PATCH /api/widgets/instances/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "config": { "showDetails": true },
  "position": { "x": 0, "y": 0, "w": 6, "h": 4 }
}
```

Common update scenarios:

- **Fix bugs:** Update `source_code` or `server_code` on definition
- **Change settings:** Update `config` on instance
- **Resize/reposition:** Update `position` on instance
- **Rename:** Update `name` on definition or `title` on instance

### Deleting a Widget

**Remove from dashboard (keeps definition for reuse):**

```http
DELETE /api/widgets/instances/:id
Authorization: Bearer <token>
```

**Delete definition entirely:**

```http
DELETE /api/widgets/:slug
Authorization: Bearer <token>
```

Response: `{ "success": true, "deleted_id": "cw_abc123" }`

---

## Error Handling Patterns

Widgets should handle errors gracefully and provide helpful feedback to users.

### Missing Credentials

```tsx
function Widget() {
  const { data, loading, error } = useData("github", { endpoint: "/user" });

  if (error?.code === "CREDENTIAL_MISSING") {
    return (
      <Card className="h-full">
        <CardContent className="flex flex-col items-center justify-center h-full gap-4">
          <Icons.Lock className="h-8 w-8 text-muted-foreground" />
          <div className="text-center">
            <p className="font-medium">GitHub token required</p>
            <p className="text-sm text-muted-foreground">
              Add your GitHub personal access token in Settings → Credentials
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // ... rest of widget
}
```

### API Rate Limits

```tsx
if (error?.code === "RATE_LIMITED") {
  const retryAfter = error.retryAfter || 60;
  return (
    <Card className="h-full">
      <CardContent className="flex flex-col items-center justify-center h-full gap-4">
        <Icons.Clock className="h-8 w-8 text-warning" />
        <div className="text-center">
          <p className="font-medium">Rate limit exceeded</p>
          <p className="text-sm text-muted-foreground">
            Try again in {Math.ceil(retryAfter / 60)} minutes
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
```

### Network Failures

```tsx
if (error?.code === "NETWORK_ERROR") {
  return (
    <Card className="h-full">
      <CardContent className="flex flex-col items-center justify-center h-full gap-4">
        <Icons.AlertCircle className="h-8 w-8 text-destructive" />
        <div className="text-center">
          <p className="font-medium">Connection failed</p>
          <p className="text-sm text-muted-foreground">
            Check your internet connection
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={refresh}>
          <Icons.RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </CardContent>
    </Card>
  );
}
```

### Generic Error with Retry

```tsx
function Widget() {
  const { data, loading, error, refresh } = useData("api", {
    endpoint: "/data",
  });

  if (loading) return <Loading />;

  if (error) {
    return (
      <ErrorDisplay
        message={error.message || "Something went wrong"}
        retry={refresh}
      />
    );
  }

  // ... render data
}
```

### Server Code Error Handling

```javascript
// In server code - return structured errors
try {
  const token = await getCredential("github");
  if (!token) {
    return {
      error: { code: "CREDENTIAL_MISSING", message: "GitHub token not found" },
    };
  }

  const response = await fetch("https://api.github.com/user", {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status === 401) {
    return {
      error: { code: "UNAUTHORIZED", message: "Invalid or expired token" },
    };
  }

  if (
    response.status === 403 &&
    response.headers.get("X-RateLimit-Remaining") === "0"
  ) {
    const resetTime = response.headers.get("X-RateLimit-Reset");
    return {
      error: {
        code: "RATE_LIMITED",
        message: "Rate limit exceeded",
        retryAfter: parseInt(resetTime) - Math.floor(Date.now() / 1000),
      },
    };
  }

  if (!response.ok) {
    return {
      error: { code: "API_ERROR", message: `API returned ${response.status}` },
    };
  }

  return await response.json();
} catch (e) {
  return { error: { code: "NETWORK_ERROR", message: e.message } };
}
```

---

## Output Format

Understanding API response structures is critical for parsing and handling data correctly.

### Success Response: Create Widget Definition

```json
{
  "id": "cw_abc123xyz",
  "name": "GitHub PRs",
  "slug": "github-prs",
  "description": "Shows open pull requests",
  "source_code": "function Widget() { ... }",
  "server_code": "const token = await getCredential('github'); ...",
  "server_code_enabled": true,
  "data_providers": ["github"],
  "default_size": { "w": 4, "h": 3 },
  "min_size": { "w": 2, "h": 2 },
  "refresh_interval": 300,
  "enabled": true,
  "created_at": "2026-02-01T12:00:00.000Z",
  "updated_at": "2026-02-01T12:00:00.000Z"
}
```

### Success Response: Create Widget Instance

```json
{
  "id": "widget_xyz789",
  "type": "custom",
  "title": "GitHub PRs",
  "custom_widget_id": "cw_abc123xyz",
  "config": { "owner": "acfranzen", "repo": "libra" },
  "position": { "x": 0, "y": 0, "w": 4, "h": 3 },
  "created_at": "2026-02-01T12:00:00.000Z",
  "updated_at": "2026-02-01T12:00:00.000Z"
}
```

### Success Response: List Widget Definitions

```json
{
  "custom_widgets": [
    {
      "id": "cw_abc123",
      "name": "GitHub PRs",
      "slug": "github-prs",
      "description": "Shows open pull requests",
      "default_size": { "w": 4, "h": 3 },
      "enabled": true,
      "created_at": "2026-02-01T12:00:00.000Z"
    }
  ]
}
```

### Success Response: List Widget Instances

```json
{
  "widgets": [
    {
      "id": "widget_xyz789",
      "type": "custom",
      "title": "GitHub PRs",
      "custom_widget_id": "cw_abc123",
      "config": { "owner": "acfranzen", "repo": "libra" },
      "position": { "x": 0, "y": 0, "w": 4, "h": 3 },
      "created_at": "2026-02-01T12:00:00.000Z"
    },
    {
      "id": "widget_abc456",
      "type": "custom",
      "title": "Weather",
      "custom_widget_id": "cw_weather",
      "config": { "city": "New York" },
      "position": { "x": 4, "y": 0, "w": 3, "h": 3 },
      "created_at": "2026-02-01T12:00:00.000Z"
    }
  ]
}
```

### Success Response: Execute Server Code

```json
{
  "data": {
    "prs": [
      {
        "number": 142,
        "title": "Add credential management",
        "author": "zeus",
        "state": "open",
        "created_at": "2026-01-30T10:00:00.000Z"
      },
      {
        "number": 139,
        "title": "Fix widget rendering",
        "author": "acfranzen",
        "state": "open",
        "created_at": "2026-01-28T14:30:00.000Z"
      }
    ],
    "fetchedAt": "2026-02-01T12:00:00.000Z"
  }
}
```

### Success Response: List Credentials

```json
{
  "credentials": [
    {
      "id": "cred_abc123",
      "provider": "github",
      "name": "My GitHub Token",
      "created_at": "2026-02-01T12:00:00.000Z"
    },
    {
      "id": "cred_def456",
      "provider": "anthropic",
      "name": "Anthropic API",
      "created_at": "2026-02-01T12:00:00.000Z"
    }
  ],
  "status": {
    "github": { "configured": true, "source": "database" },
    "anthropic": { "configured": true, "source": "database" },
    "openweather": { "configured": false, "source": null }
  }
}
```

### Error Response: Not Found

```json
{
  "error": "Custom widget not found"
}
```

### Error Response: Unauthorized

```json
{
  "error": "Unauthorized"
}
```

### Error Response: Server Code Execution Failed

```json
{
  "error": "GitHub API rate limit exceeded"
}
```

### Parsing Tips for Agents

1. **Always check for `error` field first** - If present, handle the error
2. **Use optional chaining** - Response structures may vary: `response?.widgets?.[0]`
3. **Check HTTP status codes** - 2xx = success, 4xx = client error, 5xx = server error
4. **Handle empty arrays** - `widgets: []` and `credentials: []` are valid success responses
5. **Parse dates** - All timestamps are ISO 8601 format

---

## Full API Reference

### Widget Definition Endpoints

| Method   | Endpoint                            | Description                 | Auth         |
| -------- | ----------------------------------- | --------------------------- | ------------ |
| `GET`    | `/api/widgets`               | List all widget definitions | Bearer token |
| `POST`   | `/api/widgets`               | Create a widget definition  | Bearer token |
| `GET`    | `/api/widgets/:slug`         | Get a widget definition     | Bearer token |
| `PATCH`  | `/api/widgets/:slug`         | Update a widget definition  | Bearer token |
| `DELETE` | `/api/widgets/:slug`         | Delete a widget definition  | Bearer token |
| `POST`   | `/api/widgets/:slug/execute` | Execute server code         | Bearer token |

### Widget Instance Endpoints

| Method   | Endpoint                     | Description                   | Auth         |
| -------- | ---------------------------- | ----------------------------- | ------------ |
| `GET`    | `/api/widgets/instances`     | List all widgets on dashboard | Bearer token |
| `POST`   | `/api/widgets/instances`     | Add a widget to dashboard     | Bearer token |
| `GET`    | `/api/widgets/instances/:id` | Get a widget instance         | Bearer token |
| `PATCH`  | `/api/widgets/instances/:id` | Update a widget instance      | Bearer token |
| `DELETE` | `/api/widgets/instances/:id` | Remove widget from dashboard  | Bearer token |

### Credential Endpoints

| Method   | Endpoint               | Description                   | Auth         |
| -------- | ---------------------- | ----------------------------- | ------------ |
| `GET`    | `/api/credentials`     | List all credentials + status | Bearer token |
| `POST`   | `/api/credentials`     | Store a new credential        | Bearer token |
| `GET`    | `/api/credentials/:id` | Get credential metadata       | Bearer token |
| `PUT`    | `/api/credentials/:id` | Update a credential           | Bearer token |
| `DELETE` | `/api/credentials/:id` | Delete a credential           | Bearer token |

### Response Codes

| Code  | Meaning                              |
| ----- | ------------------------------------ |
| `200` | Success                              |
| `201` | Created                              |
| `400` | Bad Request (invalid input)          |
| `401` | Unauthorized (missing/invalid token) |
| `404` | Not Found                            |
| `409` | Conflict (duplicate slug/key)        |
| `429` | Rate Limited                         |
| `500` | Internal Server Error                |

### Error Response Format

```json
{
  "error": "Widget slug already exists"
}
```

Or for validation errors:

```json
{
  "error": "Invalid server code: blocked pattern 'require' detected"
}
```

---

## Best Practices

### Credential Management

1. **Always check credentials first**

   ```
   GET /api/credentials → Check if required key exists
   If missing → Ask user, don't fail silently
   ```

2. **Provide clear credential instructions**
   - Explain what the credential is for
   - Provide the exact URL where they can get it
   - Mention required scopes/permissions
   - Example: "I need a GitHub token with `repo` scope. Create one at https://github.com/settings/tokens"

3. **Never log or expose credential values**
   - Only reference by key name
   - Use `getCredential()` in server code only

### Widget Naming

1. **Use descriptive names**
   - ✅ "Libra GitHub PRs"
   - ✅ "NYC Weather"
   - ❌ "Widget 1"
   - ❌ "My Widget"

2. **Use consistent slug patterns**
   - Format: `{source}-{type}[-{qualifier}]`
   - Examples: `github-prs-libra`, `weather-nyc`, `anthropic-usage`

3. **Include context in config**
   ```json
   {
     "config": {
       "owner": "acfranzen",
       "repo": "libra",
       "show_drafts": false
     }
   }
   ```

### Widget Sizing

Default sizes that work well:

| Widget Type      | Recommended Size | Notes                    |
| ---------------- | ---------------- | ------------------------ |
| Simple stat      | `1x1`            | Single number/metric     |
| List (5 items)   | `1x1`            | PRs, issues, tasks       |
| List (10+ items) | `1x2` or `2x1`   | Longer lists need space  |
| Chart/Graph      | `2x2`            | Visualizations need room |
| Weather          | `1x1`            | Compact info             |
| Calendar         | `2x2`            | Multiple events          |

### Error Handling

1. **Handle missing credentials gracefully**

   ```tsx
   if (error?.code === "CREDENTIAL_MISSING") {
     return <HelpfulMessage explaining="how to add the credential" />;
   }
   ```

2. **Always provide retry options**

   ```tsx
   <ErrorDisplay message={error.message} retry={refresh} />
   ```

3. **Use appropriate error variants**
   - Missing credential → Lock icon + instructions
   - Rate limit → Clock icon + wait time
   - Network error → Retry button
   - Unknown error → Generic message + retry

4. **Log errors in server code**
   ```javascript
   console.error("[widget-name] API error:", response.status);
   ```

### User Communication

1. **Confirm actions**
   - After create: "Done! Your GitHub PRs widget is now on the dashboard."
   - After update: "Updated! The widget now shows draft PRs too."
   - After delete: "Removed the weather widget from your dashboard."

2. **Be proactive with updates**
   - On heartbeats, check widget data
   - Surface notable changes: "You have 2 new PRs since yesterday"

3. **Ask before destructive actions**
   - "Are you sure you want to delete the weather widget?"

### Performance

1. **Minimize API calls**
   - Batch credential checks when creating multiple widgets
   - Use widget data endpoint instead of re-executing when possible

2. **Use appropriate refresh intervals**
   - GitHub PRs: Every 5-15 minutes
   - Weather: Every 30-60 minutes
   - API usage: Every hour

3. **Cache when possible**
   - Server code can return `fetchedAt` timestamps
   - Skip refresh if data is recent enough

---

## OpenClaw Integration Guide

This section describes how OpenClaw agents should interact with Glance to create and manage widgets on behalf of users.

### Step 1: Parse User Request

When a user asks for a widget, extract the key information:

```
User: "Show me open PRs for the libra and glance repos"

Extract:
- Widget type: GitHub PRs
- Repos: ["acfranzen/libra", "acfranzen/glance"]
- Could be: Two separate widgets OR one combined widget
```

### Step 2: Check Required Credentials

Before creating any widget that needs authentication, verify credentials exist:

```http
GET /api/credentials
Authorization: Bearer <token>
```

Check if the required credential key is in the response.

### Step 3: Handle Missing Credentials

If a required credential is missing, ask the user to provide it:

```
Agent: "I need a GitHub personal access token to show PR data.
You can create one at https://github.com/settings/tokens with 'repo' scope.
Once you have it, just paste it here and I'll store it securely."

User: "ghp_xxxxxxxxxxxx"

Agent: [stores credential via POST /api/credentials]
```

```http
POST /api/credentials
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "github",
  "name": "GitHub Token",
  "value": "ghp_xxxxxxxxxxxx"
}
```

### Step 4: Create the Widget

Build and submit the widget definition, then add it to the dashboard:

```http
# Step 4a: Create widget definition
POST /api/widgets
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Libra PRs",
  "description": "Shows open PRs for libra repo",
  "source_code": "function Widget() {\n  const { data, loading, error, refresh } = useData('github', { endpoint: '/pulls' });\n  if (loading) return <Loading />;\n  if (error) return <ErrorDisplay message={error.message} retry={refresh} />;\n  return (\n    <Card className=\"h-full\">\n      <CardHeader>\n        <Stack direction=\"row\" align=\"center\" gap={2}>\n          <Icons.GitPullRequest className=\"h-4 w-4\" />\n          <CardTitle>Libra PRs</CardTitle>\n        </Stack>\n      </CardHeader>\n      <CardContent>\n        <List items={data.map(pr => ({ title: pr.title, subtitle: `#${pr.number} by ${pr.user.login}` }))} emptyMessage=\"No open PRs\" />\n      </CardContent>\n    </Card>\n  );\n}",
  "server_code": "const token = await getCredential('github');\nconst response = await fetch('https://api.github.com/repos/acfranzen/libra/pulls?state=open', {\n  headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json' }\n});\nreturn response.json();",
  "server_code_enabled": true,
  "data_providers": ["github"],
  "default_size": { "w": 4, "h": 3 }
}
# Returns: { "id": "cw_abc123", ... }

# Step 4b: Add to dashboard
POST /api/widgets
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "custom",
  "title": "Libra PRs",
  "custom_widget_id": "cw_abc123",
  "config": { "owner": "acfranzen", "repo": "libra" }
}
```

### Step 5: Confirm to User

```
Agent: "Done! I've added a Libra PRs widget to your dashboard.
It's showing 3 open pull requests right now."
```

### Step 6: Read Widget Data on Heartbeats

During periodic heartbeats, OpenClaw can check widget data and summarize:

```http
GET /api/widgets
Authorization: Bearer <token>
```

For each relevant widget:

```http
GET /api/widgets/cuid_abc123/data
Authorization: Bearer <token>
```

Then summarize proactively if there's something notable:

```
Agent: "Quick update - you have 2 new PRs on Libra since yesterday,
and one of your older PRs just got approved."
```

### Example Conversation Flow

```
User: "Can you add a widget showing my GitHub PRs?"

Agent: [Checks GET /api/credentials]
Agent: "I see you already have a GitHub token saved. Which repos
       would you like to track? I can do one widget per repo or
       combine them."

User: "Just libra for now"

Agent: [Creates widget via POST /api/widgets]
Agent: "Done! Your Libra PRs widget is live. You currently have
       2 open PRs:
       - #142: 'Add credential management' (opened 2 days ago)
       - #139: 'Fix widget rendering' (opened 5 days ago)"

User: "Actually make it show both libra and glance"

Agent: [Updates widget via PATCH /api/widgets/:slug OR creates second widget]
Agent: "Updated! Now showing PRs from both repos."

--- Later, on heartbeat ---

Agent: "Hey, PR #142 on Libra just got merged! 🎉"
```

### Best Practices for OpenClaw Agents

1. **Always check credentials first** - Don't attempt to create authenticated widgets without verifying tokens exist

2. **Provide clear instructions** - When asking for credentials, explain exactly what's needed and where to get it

3. **Use meaningful names and slugs** - `github-prs-libra` is better than `widget-1`

4. **Handle errors gracefully** - If widget creation fails, explain why and offer to fix it

5. **Proactively summarize** - On heartbeats, read widget data and surface interesting changes

6. **Respect user preferences** - Ask before creating multiple widgets; some users prefer combined views

7. **Clean up unused widgets** - Offer to remove widgets that are no longer needed

---

## Widget Package System

Widget packages enable portable, shareable widget definitions with declarative requirements. This system supports WeakAuras-style sharing via compressed base64 strings.

### Package Structure Overview

```
Widget Package
├── meta (identity: name, slug, description, author, version)
├── widget (display: source_code, default_size, min_size)
├── fetch (data source: server_code | webhook | agent_refresh)
├── cache (freshness: ttl, staleness, fallback behavior)
├── credentials[] (requirements: API keys, local software)
├── setup? (one-time config: agent_skill instructions)
├── config_schema? (user options: repo name, refresh interval)
└── error? (retry, fallback, timeout configuration)
```

### Fetch Type Decision Tree

Choosing the right fetch type is critical for widget functionality:

```
Is data available via API?
├── YES → Can widget call directly (CORS-safe)?
│   ├── YES → Use server_code
│   └── NO → Use agent_refresh
└── NO → Use agent_refresh (agent computes/fetches)
```

**Detailed breakdown:**

| Scenario | Fetch Type | Example |
|----------|-----------|---------|
| Public API, CORS-enabled | `server_code` | Weather APIs |
| Authenticated API (GitHub, etc.) | `server_code` | GitHub PRs, Linear issues |
| External webhook pushes data | `webhook` | Stripe events, GitHub webhooks |
| Local software required | `agent_refresh` | Homebrew package counts |
| Agent must compute/fetch | `agent_refresh` | System stats, custom scrapers |
| Complex multi-step data | `agent_refresh` | Aggregated dashboards |

### Agent Refresh Contract

When a widget uses `fetch.type = "agent_refresh"`, the OpenClaw agent **MUST** follow this contract:

#### 1. Refresh Triggers

Widgets can be refreshed via:
- **Cron jobs** — scheduled refreshes (e.g., every 15 minutes)
- **Manual button** — user clicks refresh in the UI, triggers webhook
- **Heartbeat polling** — agent checks for pending refresh requests

**All triggers send the same simple message:**
```
⚡ WIDGET REFRESH: {slug}
```

The agent then:
1. Parses the slug from the message
2. Queries the widget's `fetch.instructions` from the database
3. Spawns a subagent with those instructions

**This keeps instructions in one place** — the widget definition. Cron jobs and webhooks don't duplicate the logic.

Example cron job payload (simple):
```json
{
  "kind": "systemEvent",
  "text": "⚡ WIDGET REFRESH: claude-code-usage"
}
```

Example agent handler (pseudocode):
```javascript
if (message.startsWith('⚡ WIDGET REFRESH:')) {
  const slug = message.split(':')[1].trim();
  const widget = await db.query('SELECT fetch FROM custom_widgets WHERE slug = ?', slug);
  const instructions = widget.fetch.instructions;
  spawnSubagent({ task: instructions, model: 'haiku' });
}
```

#### 2. Data Push Endpoint

```http
POST /api/widgets/{slug}/cache
Authorization: Bearer <token>
Content-Type: application/json

{
  "data": {
    "packages": 142,
    "outdated": 5,
    "fetchedAt": "2026-02-03T18:30:00.000Z"
  }
}
```

#### 3. Required Data Fields

Always include in the data payload:
- `fetchedAt` - ISO 8601 timestamp of when data was fetched
- Any widget-specific fields the source_code expects

#### 4. Error Handling

On fetch errors:
- **DO NOT** overwrite cache with error data
- Retry on next cycle based on `error.retry` config
- The widget will use stale data per `cache.on_error` setting

#### 5. Example Agent Workflow

```javascript
// Cron job triggered by schedule: "*/15 * * * *"
async function refreshHomebrew(slug) {
  try {
    // 1. Execute local command
    const result = await exec('brew list --formula | wc -l');
    const count = parseInt(result.stdout.trim());
    
    // 2. Push to widget cache
    await fetch(`${GLANCE_URL}/api/widgets/${slug}/cache`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GLANCE_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: {
          packageCount: count,
          fetchedAt: new Date().toISOString()
        }
      })
    });
  } catch (error) {
    // Don't overwrite cache on error - widget will use stale data
    console.error('Homebrew refresh failed:', error);
  }
}
```

### Writing fetch.instructions (Critical for Agent Refresh)

For `agent_refresh` widgets, `fetch.instructions` is **the single source of truth** — it tells the agent exactly how to collect and format data. Think of it as the equivalent of `server_code` for API widgets.

**Why single source of truth matters:**
- Cron jobs just send `⚡ WIDGET REFRESH: {slug}` — no duplicated instructions
- Manual refresh webhooks send the same simple message
- Agent looks up `fetch.instructions` from the database and follows them
- Update instructions in one place, all refresh triggers use them automatically

#### What to Include

A good `fetch.instructions` must specify:

1. **Command(s) to run** — exact CLI commands or API calls
2. **Data transformation** — how to parse/format the output  
3. **Expected data shape** — the exact JSON structure the widget expects
4. **Cache endpoint** — where to POST results

#### Template

```markdown
## Data Collection

Run the following command(s):
```bash
<exact command here>
```

## Data Transformation

Parse the output and format as:
```json
{
  "field1": <description>,
  "field2": <description>,
  "fetchedAt": "<ISO 8601 timestamp>"
}
```

## Cache Update

POST to: `/api/widgets/{slug}/cache`
Header: `Origin: http://localhost:3333`
Body: `{ "data": <formatted data above> }`
```

#### Example: GitHub PRs Widget

```markdown
## Data Collection

Fetch PRs from both repos:
```bash
gh pr list --repo acfranzen/libra --json number,title,url,createdAt --limit 10
gh pr list --repo acfranzen/glance --json number,title,url,createdAt --limit 10
```

## Data Transformation

Group PRs by repo:
```json
{
  "libra": [{ "number": 74, "title": "...", "url": "...", "createdAt": "..." }],
  "glance": [{ "number": 30, "title": "...", "url": "...", "createdAt": "..." }],
  "fetchedAt": "2026-02-03T17:00:00Z"
}
```

## Cache Update

POST to: `/api/widgets/open-prs/cache`
Header: `Origin: http://localhost:3333`
```

#### Example: Claude Usage Widget

```markdown
## Data Collection

1. Launch Claude CLI: `claude`
2. Run command: `/status`
3. Parse the usage output

## Data Transformation

Extract percentages and format as flat object:
```json
{
  "session": "98%",
  "sessionResets": "7pm",
  "weekAll": "17%",
  "weekSonnet": "2%",
  "extra": "49%",
  "extraSpent": "$248.26 / $500.00",
  "fetchedAt": "2026-02-03T17:00:00Z"
}
```

## Cache Update

POST to: `/api/widgets/claude-code-usage/cache`
Header: `Origin: http://localhost:3333`
```

#### Why This Matters

Without clear instructions:
- Agent may post wrong data shape → widget shows "No data"
- Agent may miss required fields → widget errors
- Different agents may interpret requirements differently

The `fetch.instructions` field is your **contract** with any agent that will refresh this widget.

### Credential Injection Pattern

Server code accesses credentials securely via `getCredential()`:

```javascript
// In server_code
const token = await getCredential('github');

const response = await fetch('https://api.github.com/user/repos', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Accept': 'application/vnd.github+json'
  }
});

return await response.json();
```

**Available credential types:**

| Type | Description | Example |
|------|-------------|---------|
| `api_key` | API keys stored in Glance | GitHub PAT, OpenWeather key |
| `local_software` | Software installed on agent's machine | Homebrew, Docker |
| `oauth` | OAuth tokens (future) | Google Calendar |

### Cache Configuration

Control data freshness and staleness behavior:

```typescript
interface CacheConfig {
  ttl_seconds: number;              // How long data is "fresh"
  max_staleness_seconds?: number;   // How long to show stale data
  storage?: "memory" | "sqlite";    // Default: sqlite
  on_error?: "use_stale" | "show_error";  // Behavior when fetch fails
  info?: string;                    // AI context
}
```

### Error Configuration

Handle failures gracefully:

```typescript
interface ErrorConfig {
  retry?: {
    max_attempts: number;
    backoff_ms: number;
  };
  fallback?: "use_stale" | "show_error" | "show_placeholder";
  placeholder_data?: unknown;
  timeout_ms?: number;
}
```

### Data Schema Validation

Widgets can define a `data_schema` field to enforce strict validation of cached data. This is especially useful for `agent_refresh` widgets where an AI agent pushes data to the cache endpoint.

**Benefits:**
- Ensures agents push correctly structured data
- Provides clear error messages when data doesn't match expectations
- Documents the expected data format for the widget
- Prevents widget rendering errors from malformed data

**Schema Format:** Uses a subset of JSON Schema:

```typescript
interface DataSchema {
  type: "object";                              // Root must be object
  properties?: Record<string, {
    type: string;                              // "string", "number", "boolean", "array", "object"
    description?: string;                      // Human/AI readable description
    format?: "date-time";                      // For string validation
    items?: { ... };                           // For array element schema
    properties?: { ... };                      // For nested objects
    required?: string[];                       // Required nested fields
  }>;
  required?: string[];                         // Required top-level fields
}
```

**Example: Claude Usage Widget Schema**

```json
{
  "data_schema": {
    "type": "object",
    "properties": {
      "session": { "type": "string", "description": "Session usage %, e.g. '45%'" },
      "sessionResets": { "type": "string", "description": "Reset time, e.g. '7pm'" },
      "weekAll": { "type": "string", "description": "Week all-models usage %" },
      "weekSonnet": { "type": "string", "description": "Week Sonnet usage %" },
      "extra": { "type": "string", "description": "Extra usage %" },
      "extraSpent": { "type": "string", "description": "Spend string, e.g. '$12 / $20'" },
      "fetchedAt": { "type": "string", "format": "date-time" }
    },
    "required": ["session", "weekAll", "fetchedAt"]
  }
}
```

**Example: PR List Widget Schema**

```json
{
  "data_schema": {
    "type": "object",
    "properties": {
      "libra": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "number": { "type": "number" },
            "title": { "type": "string" },
            "url": { "type": "string" },
            "createdAt": { "type": "string" }
          }
        }
      },
      "glance": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "number": { "type": "number" },
            "title": { "type": "string" },
            "url": { "type": "string" },
            "createdAt": { "type": "string" }
          }
        }
      },
      "fetchedAt": { "type": "string", "format": "date-time" }
    },
    "required": ["libra", "glance", "fetchedAt"]
  }
}
```

**Validation Behavior:**

When data is POSTed to `/api/widgets/{slug}/cache`:

1. If widget has a `data_schema`, validate incoming data against it
2. On validation failure, return 400 with detailed error:
   ```json
   {
     "error": "Data validation failed against widget schema",
     "validation_errors": ["session: expected string, got number", "missing required field \"fetchedAt\""],
     "expected_schema": { ... }
   }
   ```
3. On success, cache the data normally

**Adding Schema via API:**

```http
PATCH /api/widgets/{slug}
Content-Type: application/json

{
  "data_schema": {
    "type": "object",
    "properties": {
      "count": { "type": "number" },
      "fetchedAt": { "type": "string", "format": "date-time" }
    },
    "required": ["count", "fetchedAt"]
  }
}
```

**Schema in Widget Package:**

When exporting/importing widgets, the schema is included:

```json
{
  "version": 1,
  "type": "glance-widget",
  "meta": { ... },
  "widget": { ... },
  "fetch": { "type": "agent_refresh", ... },
  "data_schema": {
    "type": "object",
    "properties": { ... },
    "required": [ ... ]
  }
}
```

### Complete Examples

#### Example 1: Server Code Widget (GitHub PRs)

```json
{
  "version": 1,
  "type": "glance-widget",
  "meta": {
    "name": "GitHub PRs",
    "slug": "github-prs",
    "description": "Shows open pull requests",
    "author": "OpenClaw"
  },
  "widget": {
    "source_code": "function Widget() { ... }",
    "server_code": "const token = await getCredential('github'); ...",
    "server_code_enabled": true,
    "default_size": { "w": 4, "h": 3 },
    "min_size": { "w": 2, "h": 2 },
    "refresh_interval": 300
  },
  "credentials": [
    {
      "id": "github",
      "type": "api_key",
      "name": "GitHub Personal Access Token",
      "description": "Token with repo scope for reading PRs",
      "obtain_url": "https://github.com/settings/tokens",
      "obtain_instructions": "Create a token with 'repo' scope"
    }
  ],
  "fetch": {
    "type": "server_code",
    "info": "Fetches PRs from GitHub API using stored token"
  },
  "cache": {
    "ttl_seconds": 300,
    "max_staleness_seconds": 900,
    "on_error": "use_stale"
  }
}
```

#### Example 2: Webhook Widget (Stripe Events)

```json
{
  "version": 1,
  "type": "glance-widget",
  "meta": {
    "name": "Stripe Events",
    "slug": "stripe-events",
    "description": "Shows recent Stripe webhook events"
  },
  "widget": {
    "source_code": "function Widget() { ... }",
    "default_size": { "w": 4, "h": 4 }
  },
  "fetch": {
    "type": "webhook",
    "webhook_path": "/api/webhooks/stripe",
    "webhook_setup_instructions": "Configure your Stripe webhook to POST to this endpoint",
    "refresh_endpoint": "https://api.stripe.com/v1/webhook_endpoints/refresh"
  },
  "setup": {
    "description": "Configure Stripe webhook",
    "agent_skill": "1. Go to Stripe Dashboard > Webhooks\n2. Add endpoint: {glance_url}/api/webhooks/stripe\n3. Select events to listen for",
    "verification": {
      "type": "cache_populated",
      "target": "stripe-events"
    },
    "idempotent": true
  },
  "cache": {
    "ttl_seconds": 60,
    "on_error": "use_stale"
  }
}
```

#### Example 3: Agent Refresh Widget (Homebrew Packages)

```json
{
  "version": 1,
  "type": "glance-widget",
  "meta": {
    "name": "Homebrew Status",
    "slug": "homebrew-status",
    "description": "Shows installed Homebrew packages and updates"
  },
  "widget": {
    "source_code": "function Widget() {\n  const { data } = useData('homebrew', {});\n  if (!data) return <Loading />;\n  return (\n    <Card className=\"h-full\">\n      <CardHeader><CardTitle>Homebrew</CardTitle></CardHeader>\n      <CardContent>\n        <Stat label=\"Packages\" value={data.packageCount} />\n        <p className=\"text-xs text-muted-foreground\">Updated {data.fetchedAt}</p>\n      </CardContent>\n    </Card>\n  );\n}",
    "default_size": { "w": 2, "h": 2 }
  },
  "credentials": [
    {
      "id": "homebrew",
      "type": "local_software",
      "name": "Homebrew",
      "description": "macOS package manager",
      "check_command": "which brew",
      "install_url": "https://brew.sh",
      "install_instructions": "Run: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    }
  ],
  "fetch": {
    "type": "agent_refresh",
    "instructions": "Run `brew list --formula | wc -l` to get package count, then POST to /api/widgets/homebrew-status/cache",
    "schedule": "*/15 * * * *",
    "expected_freshness_seconds": 900,
    "max_staleness_seconds": 3600
  },
  "cache": {
    "ttl_seconds": 900,
    "max_staleness_seconds": 3600,
    "on_error": "use_stale"
  }
}
```

### Import Flow

When importing a widget package:

1. **Decode** - Decompress the `!GW1!...` string
2. **Validate** - Check structure and required fields
3. **Check credentials** - Report which credentials are missing
4. **Check setup** - Verify if one-time setup is needed
5. **Import** - Create widget definition in database
6. **Register cron** - If `agent_refresh` with `schedule`, OpenClaw registers cron job
7. **Add to dashboard** (optional) - Create widget instance

**Import response with cron schedule:**

```json
{
  "valid": true,
  "widget": {
    "id": "cw_abc123",
    "name": "Homebrew Status",
    "slug": "homebrew-status"
  },
  "cronSchedule": {
    "expression": "*/15 * * * *",
    "message": "⚡ WIDGET REFRESH: homebrew-status",
    "slug": "homebrew-status"
  },
  "message": "Widget imported successfully! Cron schedule returned for OpenClaw registration."
}
```

**Note:** The cron message is intentionally simple — just the slug. The agent looks up `fetch.instructions` from the database when processing the refresh request. This keeps instructions in one place (the widget definition) rather than duplicating them in cron payloads.
```

### Sharing Widgets

Export a widget as a shareable string:

```http
GET /api/widget-packages/{slug}
Authorization: Bearer <token>
```

Returns:
```json
{
  "package": "!GW1!eJxVj8EKwjAQRP+l5xY2tFj1JnjyIuJd..."
}
```

Import from a package string:

```http
POST /api/widget-packages/import
Authorization: Bearer <token>
Content-Type: application/json

{
  "package": "!GW1!eJxVj8EKwjAQRP+l5xY2tFj1JnjyIuJd...",
  "dry_run": false,
  "auto_add_to_dashboard": true
}
```

---

## Styling

All components support a `className` prop for custom styling. Glance uses Tailwind CSS, so you can use any Tailwind utility classes:

```tsx
<Card className="h-full bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950">
  <CardContent className="p-6">
    <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
      Styled content
    </span>
  </CardContent>
</Card>
```

The `cn()` utility is available for conditional class merging:

```tsx
<div
  className={cn(
    "rounded-lg p-4",
    isActive && "bg-primary text-primary-foreground",
    !isActive && "bg-muted",
  )}
>
  Content
</div>
```

---

## Examples

### GitHub Pull Requests Widget

```tsx
function Widget() {
  const config = useConfig();
  const owner = config.owner || "anthropics";
  const repo = config.repo || "claude-code";

  const { data, loading, error, refresh } = useData("github", {
    endpoint: `/repos/${owner}/${repo}/pulls`,
    params: { state: "open", per_page: 5 },
  });

  if (loading) return <Loading message="Loading PRs..." />;
  if (error) return <ErrorDisplay message={error.message} retry={refresh} />;

  const prs = data || [];

  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <Stack direction="row" align="center" justify="between">
          <Stack direction="row" align="center" gap={2}>
            <Icons.GitPullRequest className="h-4 w-4" />
            <CardTitle className="text-sm">Open PRs</CardTitle>
          </Stack>
          <Badge>{prs.length}</Badge>
        </Stack>
      </CardHeader>
      <CardContent>
        <List
          items={prs.map((pr) => ({
            title: pr.title,
            subtitle: `#${pr.number} by ${pr.user.login}`,
            badge: pr.draft ? "Draft" : undefined,
            badgeVariant: "info",
          }))}
          emptyMessage="No open PRs"
        />
      </CardContent>
    </Card>
  );
}
```

### API Usage Widget

```tsx
function Widget() {
  const { data, loading, error } = useData("anthropic", {
    endpoint: "/usage",
  });

  if (loading) return <Loading />;
  if (error) return <ErrorDisplay message={error.message} />;

  const usage = data || { used: 0, limit: 100 };
  const percent = (usage.used / usage.limit) * 100;
  const variant = percent > 90 ? "error" : percent > 75 ? "warning" : "default";

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>API Usage</CardTitle>
      </CardHeader>
      <CardContent>
        <Stack gap={4}>
          <Stat
            label="Current Usage"
            value={percent.toFixed(1)}
            suffix="%"
            trend={percent > 75 ? "up" : "neutral"}
          />
          <Progress value={percent} variant={variant} showLabel />
          <p className="text-xs text-muted-foreground">
            ${usage.used.toFixed(2)} of ${usage.limit.toFixed(2)} used
          </p>
        </Stack>
      </CardContent>
    </Card>
  );
}
```

### Weather Widget (with Server Code)

Widget code:

```tsx
function Widget() {
  const config = useConfig();
  const { data, loading, error } = useData("weather", {
    endpoint: "/current",
    params: { city: config.city || "San Francisco" },
  });

  if (loading) return <Loading message="Checking weather..." />;
  if (error) return <ErrorDisplay message={error.message} />;

  return (
    <Card className="h-full">
      <CardHeader>
        <Stack direction="row" align="center" gap={2}>
          <Icons.Globe className="h-4 w-4" />
          <CardTitle>{data.city}</CardTitle>
        </Stack>
      </CardHeader>
      <CardContent>
        <Stack gap={3}>
          <Stat label="Temperature" value={data.temp} suffix="°F" />
          <p className="text-sm text-muted-foreground">{data.conditions}</p>
        </Stack>
      </CardContent>
    </Card>
  );
}
```

Server code:

```javascript
const apiKey = await getCredential("openweather");
const city = params.city || "San Francisco";

const response = await fetch(
  `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${apiKey}&units=imperial`,
);

const weather = await response.json();

return {
  city: weather.name,
  temp: Math.round(weather.main.temp),
  conditions: weather.weather[0].description,
};
```
