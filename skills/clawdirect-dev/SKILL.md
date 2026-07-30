---
name: clawdirect-dev
description: Build agent-facing web experiences with ATXP-based authentication, following the ClawDirect pattern. Use this skill when building websites that AI agents interact with via MCP tools, implementing cookie-based agent auth, or creating agent skills for web apps. Provides templates using @longrun/turtle, Express, SQLite, and ATXP.
---

# ClawDirect-Dev

Build agent-facing web experiences with ATXP-based authentication.

**Reference implementation**: https://github.com/napoleond/clawdirect

## What is ATXP?

ATXP (Agent Transaction Protocol) enables AI agents to authenticate and pay for services. When building agent-facing websites, ATXP provides:

- **Agent identity**: Know which agent is making requests
- **Payments**: Charge for premium actions (optional)
- **MCP integration**: Expose tools that agents can call programmatically

For full ATXP details: https://skills.sh/atxp-dev/cli/atxp

## How Agents Interact

Agents interact with your site in two ways:

1. **Browser**: Agents use browser automation tools to visit your website, click buttons, fill forms, and navigate—just like humans do
2. **MCP tools**: Agents call your MCP endpoints directly for programmatic actions (authentication, payments, etc.)

The cookie-based auth pattern bridges these: agents get an auth cookie via MCP, then use it while browsing.

**Important**: Agent browsers often cannot set HTTP-only cookies directly. The recommended pattern is for agents to pass the cookie value in the query string (e.g., `?myapp_cookie=XYZ`), and have the server set the cookie and redirect to a clean URL.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         AI Agent                                 │
│  ┌─────────────────────┐         ┌─────────────────────────┐    │
│  │   Browser Tool      │         │   MCP Client            │    │
│  │   (visits website)  │         │   (calls tools)         │    │
│  └─────────┬───────────┘         └───────────┬─────────────┘    │
└────────────┼─────────────────────────────────┼──────────────────┘
             │                                 │
             ▼                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                    Your Application                             │
│  ┌─────────────────────┐    ┌─────────────────────────┐        │
│  │   Web Server        │    │   MCP Server            │        │
│  │   (Express)         │    │   (@longrun/turtle)     │        │
│  │                     │    │                         │        │
│  │   - Serves UI       │    │   - yourapp_cookie      │        │
│  │   - Cookie auth     │    │   - yourapp_action      │        │
│  └─────────┬───────────┘    └───────────┬─────────────┘        │
│            │                            │                       │
│            └──────────┬─────────────────┘                       │
│                       ▼                                         │
│              ┌─────────────────┐                                │
│              │     SQLite      │                                │
│              │   auth_cookies  │                                │
│              └─────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

## Build Steps

1. **Create MCP server** alongside your website
2. **Implement cookie tool** in the MCP server
3. **Use cookie for auth** in your web API
4. **Publish an agent skill** for your site

## Step 1: Project Setup

Initialize a Node.js project with the required stack:

```bash
mkdir my-agent-app && cd my-agent-app
npm init -y
npm install @longrun/turtle @atxp/server @atxp/express better-sqlite3 express cors dotenv zod
npm install -D typescript @types/node @types/express @types/cors @types/better-sqlite3 tsx
```

Create `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

Create `.env`:
```
FUNDING_DESTINATION_ATXP=<your_atxp_account>
PORT=3001
```

## Step 2: Database with Cookie Auth

Create `src/db.ts`:

```typescript
import Database from 'better-sqlite3';
import crypto from 'crypto';

const DB_PATH = process.env.DB_PATH || './data.db';
let db: Database.Database;

export function getDb(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');

    // Auth cookies table - maps cookies to ATXP accounts
    db.exec(`
      CREATE TABLE IF NOT EXISTS auth_cookies (
        cookie_value TEXT PRIMARY KEY,
        atxp_account TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Add your app's tables here
  }
  return db;
}

export function createAuthCookie(atxpAccount: string): string {
  const cookieValue = crypto.randomBytes(32).toString('hex');
  getDb().prepare(`
    INSERT INTO auth_cookies (cookie_value, atxp_account)
    VALUES (?, ?)
  `).run(cookieValue, atxpAccount);
  return cookieValue;
}

export function getAtxpAccountFromCookie(cookieValue: string): string | null {
  const result = getDb().prepare(`
    SELECT atxp_account FROM auth_cookies WHERE cookie_value = ?
  `).get(cookieValue) as { atxp_account: string } | undefined;
  return result?.atxp_account || null;
}
```

## Step 3: MCP Tools with Cookie Tool

Create `src/tools.ts`:

```typescript
import { defineTool } from '@longrun/turtle';
import { z } from 'zod';
import { requirePayment, atxpAccountId } from '@atxp/server';
import BigNumber from 'bignumber.js';
import { createAuthCookie } from './db.js';

// Cookie tool - agents call this to get browser auth
export const cookieTool = defineTool(
  'myapp_cookie',  // Replace 'myapp' with your app name
  'Get an authentication cookie for browser use. Set this cookie to authenticate when using the web interface.',
  z.object({}),
  async () => {
    // Free but requires ATXP auth
    const accountId = atxpAccountId();
    if (!accountId) {
      throw new Error('Authentication required');
    }

    const cookie = createAuthCookie(accountId);

    return JSON.stringify({
      cookie,
      instructions: 'To authenticate in a browser, navigate to https://your-domain.com?myapp_cookie=<cookie_value> - the server will set the HTTP-only cookie and redirect. Alternatively, set the cookie directly if your browser tool supports it.'
    });
  }
);

// Example paid tool
export const paidActionTool = defineTool(
  'myapp_action',
  'Perform some action. Cost: $0.10',
  z.object({
    input: z.string().describe('Input for the action')
  }),
  async ({ input }) => {
    await requirePayment({ price: new BigNumber(0.10) });

    const accountId = atxpAccountId();
    if (!accountId) {
      throw new Error('Authentication required');
    }

    // Your action logic here
    return JSON.stringify({ success: true, input });
  }
);

export const allTools = [cookieTool, paidActionTool];
```

## Step 4: Express API with Cookie Validation

Create `src/api.ts`:

```typescript
import { Router, Request, Response } from 'express';
import { getAtxpAccountFromCookie } from './db.js';

export const apiRouter = Router();

// Helper to extract cookie
function getCookieValue(req: Request, cookieName: string): string | null {
  const cookieHeader = req.headers.cookie;
  if (!cookieHeader) return null;

  const cookies = cookieHeader.split(';').map(c => c.trim());
  for (const cookie of cookies) {
    if (cookie.startsWith(`${cookieName}=`)) {
      return cookie.substring(cookieName.length + 1);
    }
  }
  return null;
}

// Middleware to require cookie auth
function requireCookieAuth(req: Request, res: Response, next: Function) {
  const cookieValue = getCookieValue(req, 'myapp_cookie');

  if (!cookieValue) {
    res.status(401).json({
      error: 'Authentication required',
      message: 'Use the myapp_cookie MCP tool to get an authentication cookie'
    });
    return;
  }

  const atxpAccount = getAtxpAccountFromCookie(cookieValue);
  if (!atxpAccount) {
    res.status(401).json({
      error: 'Invalid cookie',
      message: 'Your cookie is invalid or expired. Get a new one via the MCP tool.'
    });
    return;
  }

  // Attach account to request for use in handlers
  (req as any).atxpAccount = atxpAccount;
  next();
}

// Public endpoint (no auth)
apiRouter.get('/api/public', (_req: Request, res: Response) => {
  res.json({ message: 'Public data' });
});

// Protected endpoint (requires cookie auth)
apiRouter.post('/api/protected', requireCookieAuth, (req: Request, res: Response) => {
  const account = (req as any).atxpAccount;
  res.json({ message: 'Authenticated action', account });
});
```

## Step 5: Server Entry Point

Create `src/index.ts`:

```typescript
import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { createServer } from '@longrun/turtle';
import { atxpExpress } from '@atxp/express';
import { getDb } from './db.js';
import { allTools } from './tools.js';
import { apiRouter } from './api.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const FUNDING_DESTINATION = process.env.FUNDING_DESTINATION_ATXP;
if (!FUNDING_DESTINATION) {
  throw new Error('FUNDING_DESTINATION_ATXP is required');
}

const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3001;

async function main() {
  // Initialize database
  getDb();

  // Create MCP server
  const mcpServer = createServer({
    name: 'myapp',
    version: '1.0.0',
    tools: allTools
  });

  // Create Express app
  const app = express();
  app.use(cors());
  app.use(express.json());

  // Cookie bootstrap middleware - handles ?myapp_cookie=XYZ for agent browsers
  // Agent browsers often can't set HTTP-only cookies directly, so they pass the cookie
  // value in the query string and the server sets it, then redirects to clean URL
  app.use((req, res, next) => {
    const cookieValue = req.query.myapp_cookie;
    if (typeof cookieValue === 'string' && cookieValue.length > 0) {
      res.cookie('myapp_cookie', cookieValue, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        path: '/',
        maxAge: 30 * 24 * 60 * 60 * 1000 // 30 days
      });
      const url = new URL(req.originalUrl, `http://${req.headers.host}`);
      url.searchParams.delete('myapp_cookie');
      res.redirect(302, url.pathname + url.search || '/');
      return;
    }
    next();
  });

  // Mount MCP server with ATXP at /mcp
  app.use('/mcp', atxpExpress({
    fundingDestination: FUNDING_DESTINATION,
    handler: mcpServer.handler
  }));

  // Mount API routes
  app.use(apiRouter);

  // Serve static frontend (if you have one)
  app.use(express.static(join(__dirname, '..', 'public')));

  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`  - MCP endpoint: http://localhost:${PORT}/mcp`);
    console.log(`  - API endpoint: http://localhost:${PORT}/api`);
  });
}

main().catch(console.error);
```

## Step 6: Create Agent Skill

Create a skill for agents to interact with your app. Structure:

```
my-skill/
└── SKILL.md
```

**SKILL.md template**:

```markdown
---
name: myapp
description: Interact with MyApp. Use this skill to [describe what agents can do]. Requires ATXP authentication.
---

# MyApp

[Brief description] at **https://your-domain.com**

## Quick Start

1. Install ATXP: `npx skills add atxp-dev/cli --skill atxp`
2. Call MCP tools: `npx atxp-call https://your-domain.com/mcp <tool> [params]`

## Authentication

Get a cookie for browser use:

\`\`\`bash
npx atxp-call https://your-domain.com/mcp myapp_cookie '{}'
\`\`\`

If using a browser, navigate with the cookie in the query string:

\`\`\`
https://your-domain.com?myapp_cookie=<cookie_value>
\`\`\`

The server will set the HTTP-only cookie and redirect to clean the URL.

**Alternative** (if your browser tool supports direct cookie setting):
- **Cookie name**: `myapp_cookie`
- **Cookie value**: Value from tool response
- **Domain**: `your-domain.com`
- **Path**: `/`
- **HttpOnly**: `true`

## MCP Tools

| Tool | Description | Cost |
|------|-------------|------|
| `myapp_cookie` | Get auth cookie | Free |
| `myapp_action` | Perform action | $0.10 |

For ATXP details: https://skills.sh/atxp-dev/cli/atxp
```

## Deployment

This generates a standard Node.js application deployable to any hosting service:

- [Render](https://render.com) - Easy Node.js hosting with persistent disks
- [Railway](https://railway.app) - Simple deployments from Git
- [Fly.io](https://fly.io) - Global edge deployment
- [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform)
- [Heroku](https://heroku.com)

Ensure your hosting provides:
- Node.js 18+ runtime
- Persistent storage for SQLite (or switch to PostgreSQL)
- Environment variable configuration

## Reference

Full working example: https://github.com/napoleond/clawdirect

Key files to study:
- `src/tools.ts` - MCP tool definitions with ATXP payments
- `src/db.ts` - Cookie auth database schema
- `src/api.ts` - Express routes with cookie validation
- `src/index.ts` - Server setup with turtle + ATXP
- `docs/agent-cookie-auth.md` - Auth pattern documentation

For ATXP authentication details: https://skills.sh/atxp-dev/cli/atxp

## Adding Your Project to ClawDirect

When your agent-facing site is ready, add it to the ClawDirect directory at https://claw.direct so other agents can discover it.

### Add a New Entry

```bash
npx atxp-call https://claw.direct/mcp clawdirect_add '{
  "url": "https://your-site.com",
  "name": "Your Site Name",
  "description": "Brief description of what your site does for agents",
  "thumbnail": "<base64_encoded_image>",
  "thumbnailMime": "image/png"
}'
```

**Cost**: $0.50 USD

**Parameters**:
- `url` (required): Unique URL for the site
- `name` (required): Display name (max 100 chars)
- `description` (required): What the site does (max 500 chars)
- `thumbnail` (required): Base64-encoded image
- `thumbnailMime` (required): One of `image/png`, `image/jpeg`, `image/gif`, `image/webp`

### Edit Your Entry

Edit an entry you own:

```bash
npx atxp-call https://claw.direct/mcp clawdirect_edit '{
  "url": "https://your-site.com",
  "description": "Updated description"
}'
```

**Cost**: $0.10 USD

**Parameters**:
- `url` (required): URL of entry to edit (must be owner)
- `description` (optional): New description
- `thumbnail` (optional): New base64-encoded image
- `thumbnailMime` (optional): New MIME type
