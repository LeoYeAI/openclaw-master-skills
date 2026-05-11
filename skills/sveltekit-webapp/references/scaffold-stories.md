# Scaffold & Configure Story Templates

Standard stories for project setup. Include these at the start of every PRD.

## US-SCAFFOLD-001: Create SvelteKit Project

```json
{
  "id": "US-SCAFFOLD-001",
  "title": "Scaffold SvelteKit project",
  "description": "Create the base SvelteKit project with standard tooling.",
  "acceptanceCriteria": [
    "Project created with `pnpx sv create` (minimal template, TypeScript)",
    "Add-ons installed: eslint, prettier, mcp, mdsvex, tailwindcss, vitest, playwright",
    "adapter-auto configured (auto-detects deployment target)",
    "pnpm install completes without errors",
    "pnpm check passes"
  ],
  "priority": 1,
  "passes": false,
  "blocked": false,
  "notes": "Wave 1 - must complete before all other stories"
}
```

### Implementation Commands

```bash
# 1. Create project (use pnpx if pnpm available, else npx)
pnpx sv create [project-name] \
  --template minimal \
  --types ts

cd [project-name]

# 2. Add core add-ons
pnpx sv add eslint prettier mcp mdsvex tailwindcss vitest playwright

# 3. Install dependencies
pnpm install
```

---

## US-SCAFFOLD-002: Configure Skeleton + Bits UI

```json
{
  "id": "US-SCAFFOLD-002",
  "title": "Set up Skeleton and Bits UI component libraries",
  "description": "Install and configure Skeleton (primary) and Bits UI (fallback/headless) for UI components.",
  "acceptanceCriteria": [
    "@skeletonlabs/skeleton and @skeletonlabs/skeleton-svelte installed",
    "Bits UI (@bits-ui/svelte) installed for headless primitives",
    "Skeleton theme configured in Tailwind",
    "Base component imports verified (Button, Card, Input from Skeleton)",
    "pnpm check passes"
  ],
  "priority": 2,
  "passes": false,
  "blocked": false,
  "notes": "Depends on US-SCAFFOLD-001. Skeleton is primary; Bits UI for gaps/custom UI."
}
```

### Implementation

```bash
# Install Skeleton (Svelte 5 version)
pnpm add @skeletonlabs/skeleton @skeletonlabs/skeleton-svelte

# Install Bits UI for headless primitives
pnpm add bits-ui

# Configure Skeleton theme in tailwind.config.js
# See Skeleton docs: https://skeleton.dev/docs/get-started
```

### When to use which:
- **Skeleton**: Pre-styled components (buttons, cards, modals, tables)
- **Bits UI**: Headless primitives when you need full styling control

---

## US-SCAFFOLD-003: Configure PWA

```json
{
  "id": "US-SCAFFOLD-003",
  "title": "Configure PWA support",
  "description": "Set up Progressive Web App capabilities.",
  "acceptanceCriteria": [
    "vite-plugin-pwa installed",
    "vite.config.ts configured with SvelteKitPWA plugin",
    "ReloadPrompt.svelte component created",
    "PWA types added to app.d.ts",
    "pnpm check passes"
  ],
  "priority": 3,
  "passes": false,
  "blocked": false,
  "notes": "Depends on US-SCAFFOLD-001. See pwa-config.md for details."
}
```

### Implementation

```bash
pnpm add -D vite-plugin-pwa
```

See [pwa-config.md](pwa-config.md) for vite.config.ts setup and ReloadPrompt component.

---

## US-SCAFFOLD-004: Set Up Directory Structure

```json
{
  "id": "US-SCAFFOLD-004",
  "title": "Create standard directory structure",
  "description": "Set up conventional directories beyond what sv creates.",
  "acceptanceCriteria": [
    "src/lib/components/ exists (shadcn components go here)",
    "src/lib/server/ exists (server-only code)",
    "src/lib/stores/ exists (Svelte stores)",
    "src/lib/utils/ exists (helper functions)",
    "src/lib/types/ exists (TypeScript types)",
    "static/icons/ exists (PWA icons)",
    ".gitkeep files in empty directories"
  ],
  "priority": 4,
  "passes": false,
  "blocked": false,
  "notes": "Depends on US-SCAFFOLD-001"
}
```

---

## US-SCAFFOLD-005: Configure Tailwind Theme

```json
{
  "id": "US-SCAFFOLD-005",
  "title": "Configure Tailwind with brand colors and plugins",
  "description": "Set up Tailwind with typography, forms, and custom palette.",
  "acceptanceCriteria": [
    "tailwind.config.js includes @tailwindcss/typography plugin",
    "tailwind.config.js includes @tailwindcss/forms plugin",
    "Custom color palette defined (from design refs or defaults)",
    "Skeleton theme tokens integrated with Tailwind",
    "pnpm check passes"
  ],
  "priority": 5,
  "passes": false,
  "blocked": false,
  "notes": "Depends on US-SCAFFOLD-002 (Skeleton sets up base theme)"
}
```

### Implementation

```bash
pnpm add -D @tailwindcss/typography @tailwindcss/forms
```

---

## US-SCAFFOLD-006: Create Environment Template

```json
{
  "id": "US-SCAFFOLD-006",
  "title": "Create .env.example with required variables",
  "description": "Document all required environment variables with type-safe access.",
  "acceptanceCriteria": [
    ".env.example created with all required variables",
    ".env.example added to git",
    ".env added to .gitignore",
    "Variables documented with comments",
    "Type definitions added to src/app.d.ts for $env module"
  ],
  "priority": 6,
  "passes": false,
  "blocked": false,
  "notes": "Depends on US-SCAFFOLD-001"
}
```

### Template (.env.example)

```bash
# Database (if using drizzle)
DATABASE_URL=

# Auth (if using lucia with OAuth)
OAUTH_GOOGLE_CLIENT_ID=
OAUTH_GOOGLE_CLIENT_SECRET=

# Public variables (accessible client-side)
PUBLIC_APP_NAME=
```

### Type definitions (src/app.d.ts)

```typescript
declare global {
  namespace App {
    // interface Error {}
    // interface Locals {}
    // interface PageData {}
    // interface PageState {}
    // interface Platform {}
  }
}

// Ensure $env modules are typed
/// <reference types="vite/client" />

export {};
```

---

## US-SCAFFOLD-007: Create VSCode Workspace

```json
{
  "id": "US-SCAFFOLD-007",
  "title": "Create VSCode workspace file",
  "description": "Generate a VSCode workspace file with recommended settings.",
  "acceptanceCriteria": [
    "[project-name].code-workspace file created in project root",
    "Includes Tailwind CSS file association for *.css",
    "Workspace committed to repo"
  ],
  "priority": 7,
  "passes": false,
  "blocked": false,
  "notes": "Parallel with other Wave 2 stories"
}
```

### Template ([project-name].code-workspace)

```json
{
  "folders": [
    {
      "path": "."
    }
  ],
  "settings": {
    "files.associations": {
      "*.css": "tailwindcss"
    }
  }
}
```

---

## US-SCAFFOLD-008: Set Up Mock Data

```json
{
  "id": "US-SCAFFOLD-008",
  "title": "Create mock data infrastructure",
  "description": "Set up mock data for local development.",
  "acceptanceCriteria": [
    "src/lib/server/mocks/ directory created",
    "Mock data utilities available for use in load functions",
    "Development server uses mocks by default",
    "Pattern documented in progress.txt"
  ],
  "priority": 7,
  "passes": false,
  "blocked": false,
  "notes": "Mocks generated per-feature as needed. This sets up infrastructure."
}
```

### Pattern

```typescript
// src/lib/server/mocks/index.ts
import { dev } from '$app/environment';

export const useMocks = dev;

// src/lib/server/mocks/users.ts
export const mockUsers = [
  { id: '1', name: 'Test User', email: 'test@example.com' }
];

// Usage in +page.server.ts
import { useMocks } from '$lib/server/mocks';
import { mockUsers } from '$lib/server/mocks/users';
import { db } from '$lib/server/db';

export const load = async () => {
  const users = useMocks ? mockUsers : await db.select().from(usersTable);
  return { users };
};
```

---

## Database Stories (if drizzle selected)

### US-DB-001: Configure Drizzle

```json
{
  "id": "US-DB-001",
  "title": "Configure Drizzle ORM",
  "description": "Set up Drizzle with chosen database provider.",
  "acceptanceCriteria": [
    "drizzle-orm and drizzle-kit installed",
    "drizzle.config.ts configured for [postgres/sqlite/turso]",
    "src/lib/server/db/index.ts exports db client",
    "Schema file created at src/lib/server/db/schema.ts",
    "pnpm check passes"
  ],
  "priority": 10,
  "passes": false,
  "blocked": false,
  "notes": "Use mocks in dev; real DB in staging"
}
```

### US-DB-002: Create Initial Migration

```json
{
  "id": "US-DB-002",
  "title": "Generate and apply initial schema migration",
  "description": "Create first database migration from schema.",
  "acceptanceCriteria": [
    "Schema defined in src/lib/server/db/schema.ts",
    "Migration generated with `pnpm drizzle-kit generate`",
    "Migration files in drizzle/ directory",
    "Can apply with `pnpm drizzle-kit push`",
    "Documented in ADMIN.md"
  ],
  "priority": 11,
  "passes": false,
  "blocked": false,
  "notes": "Depends on US-DB-001"
}
```

---

## Wave Planning

**Wave 1 (sequential):**
- US-SCAFFOLD-001 (must complete first)

**Wave 2 (parallel after Wave 1):**
- US-SCAFFOLD-002 (Skeleton + Bits UI)
- US-SCAFFOLD-003 (PWA)
- US-SCAFFOLD-004 (directories)
- US-SCAFFOLD-006 (.env)
- US-SCAFFOLD-007 (VSCode workspace)

**Wave 3 (after Wave 2):**
- US-SCAFFOLD-005 (Tailwind theme — needs Skeleton)
- US-SCAFFOLD-008 (mock data)

**Wave 4+ (features):**
- Foundation stories
- Feature stories
- Database stories (if applicable)

**Final wave:**
- E2E test stories
