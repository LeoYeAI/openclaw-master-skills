---
name: chatgpt-apps
description: Complete ChatGPT Apps builder - Create, design, implement, test, and deploy ChatGPT Apps with MCP servers, widgets, auth, database integration, and automated deployment
homepage: https://github.com/hollaugo/prompt-circle-claude-plugins
user-invocable: true
---

# ChatGPT Apps Builder

Complete workflow for building, testing, and deploying ChatGPT Apps from concept to production.

## Commands

- `/chatgpt-apps new` - Create a new ChatGPT App
- `/chatgpt-apps add-tool` - Add an MCP tool to your app
- `/chatgpt-apps add-widget` - Add a widget to your app
- `/chatgpt-apps add-auth` - Configure authentication
- `/chatgpt-apps add-database` - Set up database
- `/chatgpt-apps validate` - Validate your app
- `/chatgpt-apps test` - Run tests
- `/chatgpt-apps deploy` - Deploy to production
- `/chatgpt-apps resume` - Resume working on an app

---

## Table of Contents

1. [Create New App](#1-create-new-app)
2. [Add MCP Tool](#2-add-mcp-tool)
3. [Add Widget](#3-add-widget)
4. [Add Authentication](#4-add-authentication)
5. [Add Database](#5-add-database)
6. [Generate Golden Prompts](#6-generate-golden-prompts)
7. [Validate App](#7-validate-app)
8. [Test App](#8-test-app)
9. [Deploy App](#9-deploy-app)
10. [Resume App](#10-resume-app)

---

## 1. Create New App

**Purpose:** Create a new ChatGPT App from concept to working code.

### Workflow

#### Phase 1: Conceptualization

1. **Ask for the app idea**
   "What ChatGPT App would you like to build? Describe what it does and the problem it solves."

2. **Analyze against UX Principles**
   - **Conversational Leverage**: What can users accomplish through natural language?
   - **Native Fit**: How does this integrate with ChatGPT's conversational flow?
   - **Composability**: Can tools work independently and combine with other apps?

3. **Check for Anti-Patterns**
   - Static website content display
   - Complex multi-step workflows requiring external tabs
   - Duplicating ChatGPT's native capabilities
   - Ads or upsells

4. **Define Use Cases**
   Create 3-5 primary use cases with user stories.

#### Phase 2: Design

1. **Tool Topology**
   - Query tools (readOnlyHint: true)
   - Mutation tools (destructiveHint: false)
   - Destructive tools (destructiveHint: true)
   - Widget tools (return UI with _meta)
   - External API tools (openWorldHint: true)

2. **Widget Design**
   For each widget:
   - `id` - unique identifier (kebab-case)
   - `name` - display name
   - `description` - what it shows
   - `mockData` - sample data for preview

3. **Data Model**
   Design entities and relationships.

4. **Auth Requirements**
   - Single-user (no auth needed)
   - Multi-user (Auth0 or Supabase Auth)

#### Phase 3: Implementation

Generate complete application with this structure:

```
{app-name}/
├── package.json
├── tsconfig.server.json
├── setup.sh
├── START.sh
├── .env.example
├── .gitignore
└── server/
    └── index.ts
```

**Critical Requirements:**
- `Server` class from `@modelcontextprotocol/sdk/server/index.js`
- `StreamableHTTPServerTransport` for session management
- Widget URIs: `ui://widget/{widget-id}.html`
- Widget MIME type: `text/html+skybridge`
- `structuredContent` in tool responses
- `_meta` with `openai/outputTemplate` on tools

#### Phase 4: Testing
- Run setup: `./setup.sh`
- Start dev: `./START.sh --dev`
- Preview widgets: `http://localhost:3000/preview`
- Test MCP connection

#### Phase 5: Deployment
- Generate Dockerfile and render.yaml
- Deploy to Render
- Configure ChatGPT connector

---

## 2. Add MCP Tool

**Purpose:** Add a new MCP tool to your ChatGPT App.

### Workflow

1. **Gather Information**
   - What does this tool do?
   - What inputs does it need?
   - What does it return?

2. **Classify Tool Type**
   - **Query** (readOnlyHint: true) - Fetches data
   - **Mutation** (destructiveHint: false) - Creates/updates data
   - **Destructive** (destructiveHint: true) - Deletes data
   - **Widget** - Returns UI content
   - **External** (openWorldHint: true) - Calls external APIs

3. **Design Input Schema**
   Create Zod schema with appropriate types and descriptions.

4. **Generate Tool Handler**
   Use `chatgpt-mcp-generator` agent to create:
   - Tool handler in `server/tools/`
   - Zod schema export
   - Type exports
   - Database queries (if needed)

5. **Register Tool**
   Update `server/index.ts` with metadata:
   ```typescript
   {
     name: "my-tool",
     _meta: {
       "openai/toolInvocation/invoking": "Loading...",
       "openai/toolInvocation/invoked": "Done",
       "openai/outputTemplate": "ui://widget/my-widget.html", // if widget
     }
   }
   ```

6. **Update State**
   Add tool to `.chatgpt-app/state.json`.

### Tool Naming
Use kebab-case: `list-items`, `create-task`, `show-recipe-detail`

### Annotations Guide

| Scenario | readOnlyHint | destructiveHint | openWorldHint |
|----------|--------------|-----------------|---------------|
| List/Get | true | false | false |
| Create/Update | false | false | false |
| Delete | false | true | false |
| External API | varies | varies | true |

---

## 3. Add Widget

**Purpose:** Add inline HTML widgets with HTML/CSS/JS and Apps SDK integration.

### 5 Widget Patterns

1. **Card Grid** - Multiple items in grid
2. **Stats Dashboard** - Key metrics display
3. **Table** - Tabular data
4. **Bar Chart** - Simple visualizations
5. **Detail Widget** - Single item details

### Workflow

1. **Gather Information**
   - Widget purpose and data
   - Visual design (cards, table, chart, etc.)
   - Interactivity needs

2. **Define Data Shape**
   Document expected structure with TypeScript interface.

3. **Add Widget Config**
   ```typescript
   const widgets: WidgetConfig[] = [
     {
       id: "my-widget",
       name: "My Widget",
       description: "Displays data",
       templateUri: "ui://widget/my-widget.html",
       invoking: "Loading...",
       invoked: "Ready",
       mockData: { /* sample */ },
     },
   ];
   ```

4. **Add Widget HTML**
   Generate HTML with:
   - Preview mode support (`window.PREVIEW_DATA`)
   - OpenAI Apps SDK integration (`window.openai.toolOutput`)
   - Event listeners (`openai:set_globals`)
   - Polling fallback (100ms, 10s timeout)

5. **Create/Update Tool**
   Link tool to widget via `widgetId`.

6. **Test Widget**
   Preview at `/preview/{widget-id}` with mock data.

### Widget HTML Structure

```javascript
(function() {
  let rendered = false;

  function render(data) {
    if (rendered || !data) return;
    rendered = true;
    // Render logic
  }

  function tryRender() {
    if (window.PREVIEW_DATA) { render(window.PREVIEW_DATA); return; }
    if (window.openai?.toolOutput) { render(window.openai.toolOutput); }
  }

  window.addEventListener('openai:set_globals', tryRender);

  const poll = setInterval(() => {
    if (window.openai?.toolOutput || window.PREVIEW_DATA) {
      tryRender();
      clearInterval(poll);
    }
  }, 100);
  setTimeout(() => clearInterval(poll), 10000);

  tryRender();
})();
```

---

## 4. Add Authentication

**Purpose:** Configure authentication using Auth0 or Supabase Auth.

### When to Add
- Multiple users
- Persistent private data per user
- User-specific API credentials

### Providers

**Auth0:**
- Enterprise-grade
- OAuth 2.1, PKCE flow
- Social logins (Google, GitHub, etc.)

**Supabase Auth:**
- Simpler setup
- Email/password default
- Integrates with Supabase database

### Workflow

1. **Choose Provider**
   Ask user preference based on needs.

2. **Guide Setup**
   - **Auth0:** Create application, configure callback URLs, get credentials
   - **Supabase:** Already configured with database setup

3. **Generate Auth Code**
   Use `chatgpt-auth-generator` agent to create:
   - Session management middleware
   - User subject extraction
   - Token validation

4. **Update Server**
   Add auth middleware to protect routes.

5. **Update Environment**
   ```bash
   # Auth0
   AUTH0_DOMAIN=your-tenant.auth0.com
   AUTH0_CLIENT_ID=...
   AUTH0_CLIENT_SECRET=...
   
   # Supabase (from database setup)
   SUPABASE_URL=...
   SUPABASE_ANON_KEY=...
   ```

6. **Test**
   Verify login flow and user isolation.

---

## 5. Add Database

**Purpose:** Configure PostgreSQL database using Supabase.

### When to Add
- Persistent user data
- Multi-entity relationships
- Query/filter capabilities

### Workflow

1. **Check Supabase Setup**
   Verify account and project exist.

2. **Gather Credentials**
   - Project URL
   - Anon key (public)
   - Service role key (server-side)

3. **Define Entities**
   For each entity, specify:
   - Fields and types
   - Relationships
   - Indexes

4. **Generate Schema**
   Use `chatgpt-database-generator` agent to create SQL with:
   - `id` (UUID primary key)
   - `user_subject` (varchar, indexed)
   - `created_at` (timestamptz)
   - `updated_at` (timestamptz)
   - RLS policies for user isolation

5. **Setup Connection Pool**
   ```typescript
   import { createClient } from '@supabase/supabase-js';
   
   const supabase = createClient(
     process.env.SUPABASE_URL!,
     process.env.SUPABASE_SERVICE_ROLE_KEY!
   );
   ```

6. **Apply Migrations**
   Run SQL in Supabase dashboard or via migration tool.

### Query Pattern

Always filter by `user_subject`:

```typescript
const { data } = await supabase
  .from('tasks')
  .select('*')
  .eq('user_subject', userSubject);
```

---

## 6. Generate Golden Prompts

**Purpose:** Generate test prompts to validate ChatGPT correctly invokes tools.

### Why Important
- Measure precision/recall
- Enable iteration
- Post-launch monitoring

### 3 Categories

1. **Direct Prompts** - Explicit tool invocation
   - "Show me my task list"
   - "Create a new task called..."

2. **Indirect Prompts** - Outcome-based, ChatGPT should infer tool
   - "What do I need to do today?"
   - "Help me organize my work"

3. **Negative Prompts** - Should NOT trigger tool
   - "What is a task?"
   - "Tell me about project management"

### Workflow

1. **Analyze Tools**
   Review each tool's purpose and inputs.

2. **Generate Prompts**
   For each tool, create:
   - 5+ direct prompts
   - 5+ indirect prompts
   - 3+ negative prompts
   - 2+ edge case prompts

3. **Best Practices**
   - Tool descriptions start with "Use this when..."
   - State limitations clearly
   - Include examples in descriptions

4. **Save Output**
   Write to `.chatgpt-app/golden-prompts.json`:
   ```json
   {
     "toolName": {
       "direct": ["prompt1", "prompt2"],
       "indirect": ["prompt1", "prompt2"],
       "negative": ["prompt1", "prompt2"],
       "edge": ["prompt1", "prompt2"]
     }
   }
   ```

---

## 7. Validate App

**Purpose:** Validation suite before deployment.

### 10 Validation Checks

1. **Required Files**
   - package.json
   - tsconfig.server.json
   - setup.sh (executable)
   - START.sh (executable)
   - server/index.ts
   - .env.example

2. **Server Implementation**
   - Uses `Server` from MCP SDK
   - Has `StreamableHTTPServerTransport`
   - Session management with Map
   - Correct request handlers

3. **Widget Configuration**
   - `widgets` array exists
   - Each has id, name, description, templateUri, mockData
   - URIs match pattern `ui://widget/{id}.html`

4. **Tool Response Format**
   - Returns `structuredContent` (not just `content`)
   - Widget tools have `_meta` with `openai/outputTemplate`

5. **Resource Handler Format**
   - MIME type: `text/html+skybridge`
   - Returns `_meta` with serialization and CSP

6. **Widget HTML Structure**
   - Preview mode support
   - Event listeners for Apps SDK
   - Polling fallback
   - Render guard

7. **Endpoint Existence**
   - `/health` - Health check
   - `/preview` - Widget index
   - `/preview/:widgetId` - Widget preview
   - `/mcp` - MCP endpoint

8. **Package.json Scripts**
   - Has `build:server`
   - Has `start` with HTTP_MODE=true
   - Has `dev` with watch mode
   - NO web build scripts (web/, ui/, client/)

9. **Annotation Validation**
   - readOnlyHint set correctly
   - destructiveHint for delete operations
   - openWorldHint for external APIs

10. **Database Validation** (if enabled)
    - Tables have required fields
    - user_subject indexed
    - RLS policies enabled

### Common Errors

| Error | Fix |
|-------|-----|
| Missing structuredContent | Add to tool response |
| Wrong widget URI | Use ui://widget/{id}.html |
| No session management | Add Map<string, Transport> |
| Missing _meta | Add to tool definition and response |
| Wrong MIME type | Use text/html+skybridge |

**Critical:** Check file existence FIRST before other validations!

---

## 8. Test App

**Purpose:** Run automated tests using MCP Inspector and golden prompts.

### 4 Test Categories

1. **MCP Protocol**
   - Server starts without errors
   - Handles initialize
   - Lists tools correctly
   - Lists resources correctly

2. **Schema Validation**
   - Tool schemas are valid Zod
   - Required fields marked
   - Types match implementation

3. **Widget Tests**
   - All widgets render in preview mode
   - Mock data loads correctly
   - No console errors

4. **Golden Prompt Tests**
   - Direct prompts trigger correct tools
   - Indirect prompts work as expected
   - Negative prompts don't trigger tools

### Workflow

1. **Start Server in Test Mode**
   ```bash
   HTTP_MODE=true NODE_ENV=test npm run dev
   ```

2. **Run MCP Inspector**
   Test protocol compliance:
   - Initialize connection
   - List tools
   - Call each tool with valid inputs
   - Check responses

3. **Schema Validation**
   Verify schemas compile and match implementation.

4. **Golden Prompt Tests**
   Use ChatGPT to test prompts:
   - Record which tool was called
   - Compare to expected tool
   - Calculate precision/recall

5. **Generate Report**
   ```json
   {
     "passed": 42,
     "failed": 3,
     "categories": {
       "mcp": "✅",
       "schema": "✅",
       "widgets": "✅",
       "prompts": "⚠️ 3 failures"
     },
     "timing": "2.3s"
   }
   ```

### Fixing Failures

For each failure, explain:
- What failed
- Why it failed
- How to fix (with code example)

---

## 9. Deploy App

**Purpose:** Deploy ChatGPT App to Render with PostgreSQL and health checks.

### Prerequisites

- ✅ Validation passed
- ✅ Tests passed
- ✅ Git repository clean
- ✅ Environment variables ready

### Workflow

1. **Pre-flight Check**
   - Run validation
   - Run tests
   - Check database connection (if enabled)

2. **Generate render.yaml**
   ```yaml
   services:
     - type: web
       name: {app-name}
       runtime: docker
       plan: free
       healthCheckPath: /health
       envVars:
         - key: PORT
           value: 3000
         - key: HTTP_MODE
           value: true
         - key: NODE_ENV
           value: production
         - key: WIDGET_DOMAIN
           generateValue: true
         # Add auth/database vars if needed
   ```

3. **Generate Dockerfile**
   ```dockerfile
   FROM node:20-slim
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production
   COPY dist ./dist
   EXPOSE 3000
   CMD ["node", "dist/server/index.js"]
   ```

4. **Deploy**
   **Option A: Automated (if Render MCP available)**
   Use Render MCP agent to deploy.
   
   **Option B: Manual**
   - Push to GitHub
   - Connect repo in Render dashboard
   - Set environment variables
   - Deploy

5. **Verify Deployment**
   - Health check: `https://{app}.onrender.com/health`
   - MCP endpoint: `https://{app}.onrender.com/mcp`
   - Tool discovery works
   - Widgets render

6. **Configure ChatGPT Connector**
   - URL: `https://{app}.onrender.com/mcp`
   - Test in ChatGPT

---

## 10. Resume App

**Purpose:** Resume building an in-progress ChatGPT App.

### Workflow

1. **Load State**
   Read `.chatgpt-app/state.json`:
   ```json
   {
     "appName": "My Task Manager",
     "phase": "Implementation",
     "tools": ["list-tasks", "create-task"],
     "widgets": ["task-list"],
     "auth": false,
     "database": true,
     "validated": false,
     "deployed": false
   }
   ```

2. **Display Progress**
   Show current status:
   - App name
   - Current phase
   - Completed items (tools, widgets)
   - Pending items (auth, validation, deployment)

3. **Offer Next Steps**
   Based on phase:
   
   **Concept Phase:**
   - "Let's design the tools and widgets"
   - "Shall we start implementation?"
   
   **Implementation Phase:**
   - "Add another tool?"
   - "Add a widget?"
   - "Set up authentication?"
   - "Set up database?"
   
   **Testing Phase:**
   - "Generate golden prompts?"
   - "Run validation?"
   - "Run tests?"
   
   **Deployment Phase:**
   - "Deploy to Render?"
   - "Configure ChatGPT connector?"

4. **Continue Work**
   Based on user's choice, invoke the appropriate workflow section.

---

## Best Practices

1. **Always save state** after each major step
2. **Validate before moving forward** (especially before deployment)
3. **Use agents for code generation** (chatgpt-mcp-generator, chatgpt-auth-generator, etc.)
4. **Test at every phase** (preview widgets, test tools, run golden prompts)
5. **Keep it conversational** - guide the user naturally through the workflow
6. **Explain trade-offs** when offering choices (Auth0 vs Supabase, etc.)
7. **Show examples** when introducing new concepts

---

## State Management

The `.chatgpt-app/state.json` file tracks progress:

```json
{
  "appName": "string",
  "description": "string",
  "phase": "Concept" | "Implementation" | "Testing" | "Deployment",
  "tools": ["tool-name"],
  "widgets": ["widget-id"],
  "auth": {
    "enabled": boolean,
    "provider": "auth0" | "supabase" | null
  },
  "database": {
    "enabled": boolean,
    "entities": ["entity-name"]
  },
  "validated": boolean,
  "tested": boolean,
  "deployed": boolean,
  "deploymentUrl": "string | null",
  "goldenPromptsGenerated": boolean,
  "lastUpdated": "ISO timestamp"
}
```

---

## Command Reference

```bash
# Setup
./setup.sh

# Development
./START.sh --dev          # Dev mode with watch
./START.sh --preview      # Open preview in browser
./START.sh --stdio        # STDIO mode (testing)
./START.sh                # Production mode

# Testing
npm run validate          # Type checking
curl http://localhost:3000/health

# Deployment
git push origin main      # Trigger Render deploy
```

---

## Getting Started

When the user invokes any chatgpt-app command:

1. Check if `.chatgpt-app/state.json` exists
2. If yes → use **Resume App** workflow
3. If no → use **Create New App** workflow

Always guide users through the natural progression:
**Concept → Implementation → Testing → Deployment**
