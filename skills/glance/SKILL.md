---
name: glance
description: "Create, update, and manage Glance dashboard widgets. Use when user wants to: add something to their dashboard, create a widget, track data visually, show metrics/stats, display API data, or monitor usage."
metadata:
  openclaw:
    emoji: "🖥️"
    homepage: "https://github.com/acfranzen/glance"
    requires:
      env: ["GLANCE_URL"]
      bins: ["curl"]
    primaryEnv: GLANCE_URL
---

# Glance

AI-extensible personal dashboard. Create custom widgets with natural language — the AI handles data collection.

## Features

- **Custom Widgets** — Create widgets via AI with auto-generated JSX
- **Agent Refresh** — AI collects data on schedule and pushes to cache
- **Dashboard Export/Import** — Share widget configurations
- **Credential Management** — Secure API key storage
- **Real-time Updates** — Webhook-triggered instant refreshes

## Quick Start

```bash
# Navigate to skill directory (if installed via ClawHub)
cd "$(clawhub list | grep glance | awk '{print $2}')"

# Or clone directly
git clone https://github.com/acfranzen/glance ~/.glance
cd ~/.glance

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your settings

# Start development server
npm run dev

# Or build and start production
npm run build && npm start
```

Dashboard runs at **http://localhost:3333**

## Configuration

Edit `.env.local`:

```bash
# Server
PORT=3333
AUTH_TOKEN=your-secret-token        # Optional: Bearer token auth

# OpenClaw Integration (for instant widget refresh)
OPENCLAW_GATEWAY_URL=https://localhost:18789
OPENCLAW_TOKEN=your-gateway-token

# Database
DATABASE_PATH=./data/glance.db      # SQLite database location
```

## Service Installation (macOS)

```bash
# Create launchd plist
cat > ~/Library/LaunchAgents/com.glance.dashboard.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.glance.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/npm</string>
        <string>run</string>
        <string>dev</string>
    </array>
    <key>WorkingDirectory</key>
    <string>~/.glance</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>~/.glance/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>~/.glance/logs/stderr.log</string>
</dict>
</plist>
EOF

# Load service
mkdir -p ~/.glance/logs
launchctl load ~/Library/LaunchAgents/com.glance.dashboard.plist

# Service commands
launchctl start com.glance.dashboard
launchctl stop com.glance.dashboard
launchctl unload ~/Library/LaunchAgents/com.glance.dashboard.plist
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3333` |
| `AUTH_TOKEN` | Bearer token for API auth | — |
| `DATABASE_PATH` | SQLite database path | `./data/glance.db` |
| `OPENCLAW_GATEWAY_URL` | OpenClaw gateway for webhooks | — |
| `OPENCLAW_TOKEN` | OpenClaw auth token | — |

## Requirements

- Node.js 20+
- npm or pnpm
- SQLite (bundled)

---

# Widget Skill

Create and manage dashboard widgets. Most widgets use `agent_refresh` — **you** collect the data.

## Quick Start

```bash
# Check Glance is running (list widgets)
curl -s -H "Origin: $GLANCE_URL" "$GLANCE_URL/api/widgets" | jq '.custom_widgets[].slug'

# Auth note: Local requests with Origin header bypass Bearer token auth
# For external access, use: -H "Authorization: Bearer $GLANCE_TOKEN"

# Refresh a widget (look up instructions, collect data, POST to cache)
sqlite3 $GLANCE_DATA/glance.db "SELECT json_extract(fetch, '$.instructions') FROM custom_widgets WHERE slug = 'my-widget'"
# Follow the instructions, then:
curl -X POST "$GLANCE_URL/api/widgets/my-widget/cache" \
  -H "Content-Type: application/json" \
  -H "Origin: $GLANCE_URL" \
  -d '{"data": {"value": 42, "fetchedAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}}'

# Verify in browser
browser action:open targetUrl:"$GLANCE_URL"
```

## AI Structured Output Generation (REQUIRED)

When generating widget definitions, **use the JSON Schema** at `docs/schemas/widget-schema.json` with your AI model's structured output mode:
- **Anthropic**: Use `tool_use` with the schema
- **OpenAI**: Use `response_format: { type: "json_schema", schema }`

The schema enforces all required fields at generation time — malformed widgets cannot be produced.

### Required Fields Checklist
Every widget **MUST** have these fields (the schema enforces them):

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Non-empty, human-readable |
| `slug` | string | Lowercase kebab-case (`my-widget`) |
| `source_code` | string | Valid JSX with Widget function |
| `default_size` | `{ w: 1-12, h: 1-20 }` | Grid units |
| `min_size` | `{ w: 1-12, h: 1-20 }` | Cannot resize smaller |
| `fetch.type` | enum | `"server_code"` \| `"webhook"` \| `"agent_refresh"` |
| `fetch.instructions` | string | **REQUIRED if type is `agent_refresh`** |
| `fetch.schedule` | string | **REQUIRED if type is `agent_refresh`** (cron) |
| `data_schema.type` | `"object"` | Always object |
| `data_schema.properties` | object | Define each field |
| `data_schema.required` | array | **MUST include `"fetchedAt"`** |
| `credentials` | array | Use `[]` if none needed |

### Example: Minimal Valid Widget

```json
{
  "name": "My Widget",
  "slug": "my-widget",
  "source_code": "function Widget({ serverData }) { return <div>{serverData?.value}</div>; }",
  "default_size": { "w": 2, "h": 2 },
  "min_size": { "w": 1, "h": 1 },
  "fetch": {
    "type": "agent_refresh",
    "schedule": "*/15 * * * *",
    "instructions": "## Data Collection\nCollect the data...\n\n## Cache Update\nPOST to /api/widgets/my-widget/cache"
  },
  "data_schema": {
    "type": "object",
    "properties": {
      "value": { "type": "number" },
      "fetchedAt": { "type": "string", "format": "date-time" }
    },
    "required": ["value", "fetchedAt"]
  },
  "credentials": []
}
```

---

## ⚠️ Widget Creation Checklist (MANDATORY)

Every widget must complete ALL steps before being considered done:

```
□ Step 1: Create widget definition (POST /api/widgets)
    - source_code with Widget function
    - data_schema (REQUIRED for validation)
    - fetch config (type + instructions for agent_refresh)
    
□ Step 2: Add to dashboard (POST /api/widgets/instances)
    - custom_widget_id matches definition
    - title and config set
    
□ Step 3: Populate cache (for agent_refresh widgets)
    - Data matches data_schema exactly
    - Includes fetchedAt timestamp
    
□ Step 4: Set up cron job (for agent_refresh widgets)
    - Simple message: "⚡ WIDGET REFRESH: {slug}"
    - Appropriate schedule (*/15 or */30 typically)
    
□ Step 5: BROWSER VERIFICATION (MANDATORY)
    - Open http://localhost:3333
    - Widget is visible on dashboard
    - Shows actual data (not loading spinner)
    - Data values match what was cached
    - No errors or broken layouts
    
⛔ DO NOT report widget as complete until Step 5 passes!
```

## Quick Reference

- **Full SDK docs:** See `docs/widget-sdk.md` in the Glance repo
- **Component list:** See [references/components.md](references/components.md)

## Widget Package Structure

```
Widget Package
├── meta (name, slug, description, author, version)
├── widget (source_code, default_size, min_size)
├── fetch (server_code | webhook | agent_refresh)
├── dataSchema? (JSON Schema for cached data - validates on POST)
├── cache (ttl, staleness, fallback)
├── credentials[] (API keys, local software requirements)
├── config_schema? (user options)
└── error? (retry, fallback, timeout)
```

## Fetch Type Decision Tree

```
Is data available via API that the widget can call?
├── YES → Use server_code
└── NO → Does an external service push data?
    ├── YES → Use webhook
    └── NO → Use agent_refresh (YOU collect it)
```

| Scenario | Fetch Type | Who Collects Data? |
|----------|-----------|-------------------|
| Public/authenticated API | `server_code` | Widget calls API at render |
| External service pushes data | `webhook` | External service POSTs to cache |
| **Local CLI tools** | `agent_refresh` | **YOU (the agent) via PTY/exec** |
| **Interactive terminals** | `agent_refresh` | **YOU (the agent) via PTY** |
| **Computed/aggregated data** | `agent_refresh` | **YOU (the agent) on a schedule** |

**⚠️ `agent_refresh` means YOU are the data source.** You set up a cron to remind yourself, then YOU collect the data using your tools (exec, PTY, browser, etc.) and POST it to the cache.

## API Endpoints

### Widget Definitions
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/widgets` | Create widget definition |
| `GET` | `/api/widgets` | List all definitions |
| `GET` | `/api/widgets/:slug` | Get single definition |
| `PATCH` | `/api/widgets/:slug` | Update definition |
| `DELETE` | `/api/widgets/:slug` | Delete definition |

### Widget Instances (Dashboard)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/widgets/instances` | Add widget to dashboard |
| `GET` | `/api/widgets/instances` | List dashboard widgets |
| `PATCH` | `/api/widgets/instances/:id` | Update instance (config, position) |
| `DELETE` | `/api/widgets/instances/:id` | Remove from dashboard |

### Credentials
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/credentials` | List credentials + status |
| `POST` | `/api/credentials` | Store credential |
| `DELETE` | `/api/credentials/:id` | Delete credential |

## Creating a Widget

### Full Widget Package Structure

```json
{
  "name": "GitHub PRs",
  "slug": "github-prs",
  "description": "Shows open pull requests",
  
  "source_code": "function Widget({ serverData }) { ... }",
  "default_size": { "w": 2, "h": 2 },
  "min_size": { "w": 1, "h": 1 },
  "refresh_interval": 300,
  
  "credentials": [
    {
      "id": "github",
      "type": "api_key",
      "name": "GitHub Personal Access Token",
      "description": "Token with repo scope",
      "obtain_url": "https://github.com/settings/tokens"
    }
  ],
  
  "fetch": {
    "type": "agent_refresh",
    "schedule": "*/5 * * * *",
    "instructions": "Fetch open PRs from GitHub API and POST to cache endpoint",
    "expected_freshness_seconds": 300,
    "max_staleness_seconds": 900
  },
  
  "cache": {
    "ttl_seconds": 300,
    "max_staleness_seconds": 900,
    "storage": "sqlite",
    "on_error": "use_stale"
  },
  
  "setup": {
    "description": "Configure GitHub token",
    "agent_skill": "Store GitHub PAT via /api/credentials",
    "verification": {
      "type": "cache_populated",
      "target": "github-prs"
    },
    "idempotent": true
  }
}
```

### Fetch Types

| Type | When to Use | Data Flow |
|------|-------------|-----------|
| `server_code` | Widget can call API directly | Widget → server_code → API |
| `agent_refresh` | Agent must fetch/compute data | Agent → POST /cache → Widget reads |
| `webhook` | External service pushes data | External → POST /cache → Widget reads |

**Most widgets should use `agent_refresh`** — the agent fetches data on a schedule and pushes to the cache endpoint.

### Step 1: Create Widget Definition

```http
POST /api/widgets
Content-Type: application/json

{
  "name": "GitHub PRs",
  "slug": "github-prs",
  "description": "Shows open pull requests",
  "source_code": "function Widget({ serverData }) { ... }",
  "default_size": { "w": 2, "h": 2 },
  "credentials": [...],
  "fetch": { "type": "agent_refresh", "schedule": "*/5 * * * *", ... },
  "data_schema": {
    "type": "object",
    "properties": {
      "prs": { "type": "array", "description": "List of PR objects" },
      "fetchedAt": { "type": "string", "format": "date-time" }
    },
    "required": ["prs", "fetchedAt"]
  },
  "cache": { "ttl_seconds": 300, ... }
}
```

**`data_schema` (REQUIRED)** defines the data contract between the fetcher and the widget. Cache POSTs are validated against it — malformed data returns 400.

> ⚠️ **Always include `data_schema`** when creating widgets. This ensures:
> 1. Data validation on cache POSTs (400 on schema mismatch)
> 2. Clear documentation of expected data structure
> 3. AI agents know the exact format to produce

### Step 2: Add to Dashboard

```http
POST /api/widgets/instances
Content-Type: application/json

{
  "type": "custom",
  "title": "GitHub PRs",
  "custom_widget_id": "cw_abc123",
  "config": { "owner": "acfranzen", "repo": "libra" }
}
```

### Step 3: Populate Cache (for agent_refresh)

```http
POST /api/widgets/github-prs/cache
Content-Type: application/json

{
  "data": {
    "prs": [...],
    "fetchedAt": "2026-02-03T14:00:00Z"
  }
}
```

**⚠️ If the widget has a `dataSchema`, the cache endpoint validates your data against it.** Bad data returns 400 with details. Always check the widget's schema before POSTing:

```http
GET /api/widgets/github-prs
# Response includes dataSchema showing required fields and types
```

### Step 4: Browser Verification (REQUIRED)

**⚠️ MANDATORY: Every widget creation and refresh MUST end with browser verification.**

Never consider a widget "done" until you've visually confirmed it renders correctly on the dashboard.

```javascript
// REQUIRED: Open dashboard and verify widget renders
browser({ 
  action: 'open', 
  targetUrl: 'http://localhost:3333',
  profile: 'openclaw'
});

// Take a snapshot and check the widget
browser({ action: 'snapshot' });

// Look for:
// 1. Widget is visible on the dashboard
// 2. Shows actual data, NOT "Waiting for data..." or loading spinner
// 3. Data values match what was pushed to cache
// 4. No error messages displayed
// 5. Layout looks correct (not broken/overlapping)
```

**Verification checklist (must ALL be true):**
- [ ] Widget visible on dashboard grid
- [ ] Title displays correctly
- [ ] Data renders (not stuck on loading)
- [ ] Values match cached data
- [ ] No error states or broken layouts
- [ ] "Updated X ago" footer shows recent timestamp

**Common issues and fixes:**
| Symptom | Cause | Fix |
|---------|-------|-----|
| "Waiting for data..." | Cache empty | POST data to `/api/widgets/{slug}/cache` |
| Widget not visible | Not added to dashboard | `POST /api/widgets/instances` |
| Wrong/old data | Slug mismatch | Check slug matches between definition and cache POST |
| Broken layout | Bad JSX in source_code | Check widget code for syntax errors |
| "No data" after POST | Schema validation failed | Check data matches `data_schema` |

**If verification fails, fix the issue before reporting success.**

## Widget Code Template (agent_refresh)

For `agent_refresh` widgets, use `serverData` prop (NOT `useData` hook):

```tsx
function Widget({ serverData }) {
  const data = serverData;
  const loading = !serverData;
  const error = serverData?.error;
  
  if (loading) return <Loading message="Waiting for data..." />;
  if (error) return <ErrorDisplay message={error} />;
  
  // NOTE: Do NOT wrap in <Card> - the framework wrapper (CustomWidgetWrapper) 
  // already provides the outer card with title, refresh button, and footer.
  // Just render your content directly.
  return (
    <div className="space-y-3">
      <List items={data.prs?.map(pr => ({
        title: pr.title,
        subtitle: `#${pr.number} by ${pr.author}`,
        badge: pr.state
      })) || []} />
    </div>
  );
}
```

**Important:** The widget wrapper (`CustomWidgetWrapper`) provides:
- Outer `<Card>` container with header (widget title)
- Refresh button and "Updated X ago" footer
- Loading/error states

Your widget code should just render the **content** — no Card, no CardHeader, no footer.

**Key difference:** `agent_refresh` widgets receive data via `serverData` prop, NOT by calling `useData()`. The agent pushes data to `/api/widgets/{slug}/cache`.

## Server Code (Legacy Alternative)

**Prefer `agent_refresh` over `server_code`.** Only use server_code when the widget MUST execute code at render time (rare).

```javascript
// Only for fetch.type = "server_code" widgets
const token = await getCredential('github');
const response = await fetch('https://api.github.com/repos/owner/repo/pulls', {
  headers: { 'Authorization': `Bearer ${token}` }
});
return await response.json();
```

**Available:** `fetch`, `getCredential(provider)`, `params`, `console`
**Blocked:** `require`, `eval`, `fs`, `process`, `global`

## Agent Refresh Contract

**⚠️ CRITICAL: For `agent_refresh` widgets, YOU (the OpenClaw agent) are the data collector.**

This is NOT an external API or service. YOU must:
1. Set up a **cron job to remind yourself** to collect data on a schedule
2. **Use your own tools** (PTY, exec, browser, etc.) to gather the data
3. **Parse the output** into structured JSON
4. **POST to the cache endpoint** so the widget can display it

### The Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  Cron fires → Agent wakes up → Agent collects data →        │
│  Agent POSTs to /cache → Widget displays fresh data         │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step for agent_refresh Widgets

1. **Create the widget** with `fetch.type = "agent_refresh"` and detailed `fetch.instructions`
2. **Set up a cron job** targeting YOUR main session (message is just the slug):
   ```javascript
   cron.add({
     name: "Widget: My Data Refresh",
     schedule: { kind: "cron", expr: "*/15 * * * *" },
     payload: { 
       kind: "systemEvent", 
       text: "⚡ WIDGET REFRESH: my-widget"  // Just the slug!
     },
     sessionTarget: "main"  // Reminds YOU, not an isolated session
   })
   ```
3. **When you receive the refresh message**, look up `fetch.instructions` from the DB and spawn a subagent:
   ```javascript
   // Parse slug from message
   const slug = message.replace('⚡ WIDGET REFRESH:', '').trim();
   // Query widget's fetch.instructions
   const widget = db.query('SELECT fetch FROM custom_widgets WHERE slug = ?', slug);
   // Spawn subagent with the instructions
   sessions_spawn({ task: widget.fetch.instructions, model: 'haiku' });
   ```
4. **The subagent collects the data** using your tools:
   - `exec` for shell commands
   - PTY for interactive CLI tools (like `claude /status`)
   - `browser` for web scraping
   - API calls via `web_fetch`
4. **POST the data to the cache:**
   ```http
   POST /api/widgets/{slug}/cache
   Content-Type: application/json
   
   {
     "data": {
       "myValue": 42,
       "fetchedAt": "2026-02-03T18:30:00.000Z"
     }
   }
   ```

### Writing Excellent fetch.instructions

The `fetch.instructions` field is the **single source of truth** for how to collect widget data. Write them clearly so any subagent can follow them.

**Required sections:**
```markdown
## Data Collection
Exact commands to run with full paths and flags.
Include PTY requirements if interactive.

## Data Transformation
Exact JSON structure expected.
Include field descriptions and examples.

## Cache Update
Full URL, required headers, body format.

## Browser Verification
Confirm the widget renders correctly.
```

**Good example:**
```markdown
## Data Collection
```bash
gog gmail search "in:inbox" --json
```

## Data Transformation
Take first 5-8 emails, generate AI summary (3-5 words) for each:
```json
{
  "emails": [{"id": "...", "from": "...", "subject": "...", "summary": "AI summary here", "unread": true}],
  "fetchedAt": "ISO timestamp"
}
```

## Cache Update
POST to: http://localhost:3333/api/widgets/recent-emails/cache
Header: Origin: http://localhost:3333
Body: { "data": <object above> }

## Browser Verification  
Open http://localhost:3333 and confirm widget shows emails with AI summaries.
```

**Bad example (too vague):**
```
Get emails and post to cache.
```

### Real Example: Claude Max Usage Widget

This widget shows Claude CLI usage stats. The data comes from running `claude` in a PTY and navigating to `/status → Usage`.

**The agent's job every 15 minutes:**
```
1. Spawn PTY: exec("claude", { pty: true })
2. Send: "/status" + Enter
3. Navigate to Usage tab (Right arrow keys)
4. Parse the output: Session %, Week %, Extra %
5. POST to /api/widgets/claude-code-usage/cache
6. Kill the PTY session
7. ⚠️ VERIFY: Open browser to http://localhost:3333 and confirm widget displays new data
```

**This is YOUR responsibility as the agent.** The widget just displays whatever data is in the cache.

### Subagent Task Template for Refreshes

When spawning subagents for widget refreshes, always include browser verification:

```javascript
sessions_spawn({
  task: `${fetchInstructions}

## REQUIRED: Browser Verification
After posting to cache, verify the widget renders correctly:
1. Open http://localhost:3333 in browser
2. Find the widget on the dashboard
3. Confirm it shows the data you just posted
4. Report any rendering issues

Do NOT report success until browser verification passes.`,
  model: 'haiku',
  label: `${slug}-refresh`
});
```

### Cache Endpoint

```http
POST /api/widgets/{slug}/cache
Content-Type: application/json

{
  "data": {
    "packages": 142,
    "fetchedAt": "2026-02-03T18:30:00.000Z"
  }
}
```

### Immediate Refresh via Webhook

**For `agent_refresh` widgets, users can trigger immediate refreshes via the UI refresh button.**

When configured with `OPENCLAW_GATEWAY_URL` and `OPENCLAW_TOKEN` environment variables, clicking the refresh button will:
1. Store a refresh request in the database (fallback for polling)
2. **Immediately POST a wake notification to OpenClaw** via `/api/sessions/wake`
3. The agent receives a prompt to refresh that specific widget now

This eliminates the delay of waiting for the next heartbeat poll.

**Environment variables** (add to `.env.local`):
```bash
OPENCLAW_GATEWAY_URL=http://localhost:18789
OPENCLAW_TOKEN=your-gateway-token
```

**How it works:**
1. User clicks refresh button on widget
2. Glance POSTs to `/api/widgets/{slug}/refresh`
3. If webhook configured, Glance immediately notifies OpenClaw: `⚡ WIDGET REFRESH: Refresh the "{slug}" widget now and POST to cache`
4. Agent wakes up, collects fresh data, POSTs to cache
5. Widget re-renders with updated data

**Response includes webhook status:**
```json
{
  "status": "refresh_requested",
  "webhook_sent": true,
  "fallback_queued": true
}
```

If webhook fails or isn't configured, the DB fallback ensures the next heartbeat/poll will pick it up.

### Rules
- **Always include `fetchedAt`** timestamp
- **Don't overwrite on errors** - let widget use stale data
- **Use main session cron** so YOU handle the collection, not an isolated agent
```

## Credential Requirements Format

### Credential Types

| Type | Storage | Description | Use For |
|------|---------|-------------|---------|
| `api_key` | Glance DB (encrypted) | API tokens stored in Glance | GitHub PAT, OpenWeather key |
| `local_software` | Agent's machine | Software that must be installed | Homebrew, Docker |
| `agent` | Agent environment | Auth that lives on the agent | `gh` CLI auth, `gcloud` auth |
| `oauth` | Glance DB | OAuth tokens (future) | Google Calendar |

### Examples

```json
{
  "credentials": [
    {
      "id": "github",
      "type": "api_key",
      "name": "GitHub Personal Access Token",
      "description": "Token with repo scope",
      "obtain_url": "https://github.com/settings/tokens",
      "obtain_instructions": "Create token with 'repo' scope"
    },
    {
      "id": "homebrew",
      "type": "local_software",
      "name": "Homebrew",
      "check_command": "which brew",
      "install_url": "https://brew.sh"
    },
    {
      "id": "github_cli",
      "type": "agent",
      "name": "GitHub CLI",
      "description": "Agent needs gh CLI authenticated to GitHub",
      "agent_tool": "gh",
      "agent_auth_check": "gh auth status",
      "agent_auth_instructions": "Run `gh auth login` on the machine running OpenClaw"
    }
  ]
}
```

**When to use `agent` type:** Use for `agent_refresh` widgets where the agent collects data using CLI tools that have their own auth (like `gh`, `gcloud`, `aws`). These credentials aren't stored in Glance — they exist in the agent's environment.

## Common Credential Providers

| Provider | ID | Description |
|----------|-----|-------------|
| GitHub | `github` | GitHub API (PAT with repo scope) |
| Anthropic | `anthropic` | Claude API (Admin key for usage) |
| OpenAI | `openai` | GPT API (Admin key for usage) |
| OpenWeather | `openweather` | Weather data API |
| Linear | `linear` | Linear API |
| Notion | `notion` | Notion API |

## Export/Import Packages

### Export

```http
GET /api/widgets/{slug}/export
```

Returns: `{ "package": "!GW1!eJxVj8EKwj..." }`

### Import

```http
POST /api/widgets/import
Content-Type: application/json

{
  "package": "!GW1!eJxVj8EKwj...",
  "dry_run": false,
  "auto_add_to_dashboard": true
}
```

The `!GW1!` prefix indicates Glance Widget v1 format (compressed base64 JSON).

### Import Response with Cron

```json
{
  "valid": true,
  "widget": { "id": "cw_abc", "slug": "homebrew-status" },
  "cronSchedule": {
    "expression": "*/15 * * * *",
    "instructions": "Run brew list...",
    "slug": "homebrew-status"
  }
}
```

When `cronSchedule` is returned, OpenClaw should register a cron job.

## Key UI Components

| Component | Use For |
|-----------|---------|
| `Card` | Widget container (always use `className="h-full"`) |
| `List` | Items with title/subtitle/badge |
| `Stat` | Single metric with trend indicator |
| `Progress` | Progress bars with variants |
| `Badge` | Status labels (success/warning/error) |
| `Stack` | Flexbox layout (row/column) |
| `Grid` | CSS Grid layout |
| `Loading` | Loading spinner |
| `ErrorDisplay` | Error with retry button |

See [references/components.md](references/components.md) for full props.

## Hooks

```tsx
// Fetch data (BOTH args required!)
const { data, loading, error, refresh } = useData('github', {});
const { data } = useData('github', { endpoint: '/pulls', params: { state: 'open' } });

// Get widget config
const config = useConfig();

// Widget-local state
const { state, setState } = useWidgetState('counter', 0);
```

**⚠️ `useData` requires both arguments.** Pass empty `{}` if no query needed.

## Error Handling

```tsx
if (error?.code === 'CREDENTIAL_MISSING') {
  return <Card><CardContent>
    <Icons.Lock className="h-8 w-8" />
    <p>GitHub token required</p>
  </CardContent></Card>;
}
```

Error codes: `CREDENTIAL_MISSING`, `RATE_LIMITED`, `NETWORK_ERROR`, `API_ERROR`

## Best Practices

1. **Always check credentials before creating widgets**
2. **Use meaningful names:** `github-prs-libra` not `widget-1`
3. **Include fetchedAt in all data** for staleness tracking
4. **Handle errors gracefully** with retry options
5. **Confirm actions:** "Done! Widget added to dashboard."
6. **Size appropriately:** Lists 1x1, charts 2x2

## Reading Dashboard Data

To summarize dashboard for user:

```
1. GET /api/widgets/instances → list instances
2. For each: POST /api/widgets/:slug/execute
3. Combine into natural language summary
```

---

## ⚠️ Rules & Gotchas

1. **Use JSON Schema for generation** — `docs/schemas/widget-schema.json` enforces all required fields
2. **Browser verify EVERYTHING** — don't report success until you see the widget render correctly
3. **agent_refresh = YOU collect data** — the widget just displays what you POST to cache
4. **fetch.instructions is the source of truth** — cron jobs just send the slug, you look up instructions
5. **Always include fetchedAt** — widgets need timestamps for "Updated X ago" display
6. **data_schema is REQUIRED** — cache POSTs validate against it, malformed data returns 400
7. **credentials is REQUIRED** — use empty array `[]` if no credentials needed
8. **Don't wrap in Card** — the framework provides the outer card, you render content only
9. **Use Haiku for refresh subagents** — mechanical data collection doesn't need Opus
10. **Mark refresh requests as processed** — `DELETE /api/widgets/{slug}/refresh` after handling
11. **Spawn subagents for refreshes** — don't block main session with PTY/long-running work

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GLANCE_URL` | Glance server URL | `http://localhost:3333` |
| `GLANCE_DATA` | Path to SQLite database | `/tmp/glance-test/data` |
| `OPENCLAW_GATEWAY_URL` | For webhook refresh notifications | `https://localhost:18789` |
| `OPENCLAW_TOKEN` | Gateway auth token | `d551fe97...` |

## Learnings (Feb 2026)

- **Webhook refresh works** — Glance POSTs to OpenClaw gateway, agent wakes immediately
- **Simple cron messages** — just `⚡ WIDGET REFRESH: {slug}`, agent looks up instructions
- **AI summaries need AI** — for recent-emails, YOU generate the summaries, not some API
- **icalBuddy for iCloud** — `gog calendar` doesn't work for iCloud, use `/opt/homebrew/bin/icalBuddy`
- **wttr.in for weather** — free, no API key, JSON format: `wttr.in/City?format=j1`
