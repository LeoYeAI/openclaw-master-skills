# Ralph Implementation Plan

Generate `prd.json` in project root using this structure.

## prd.json Schema

```json
{
  "project": "PROJECT_NAME",
  "branchName": "ralph/FEATURE_NAME",
  "description": "Brief description of what we're building",
  "userStories": [
    {
      "id": "US-001",
      "title": "Short title",
      "description": "As a [user], I want [goal] so that [benefit].",
      "acceptanceCriteria": [
        "Specific, testable criterion",
        "Another criterion",
        "Typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Story Sizing Rules

**Right-sized (one context window):**
- Add a database column and migration
- Create a single component
- Add a route with basic data loading
- Implement one form with validation
- Add a filter/sort to a list
- Set up a config file

**Too big (split these):**
- "Build the dashboard" → split into layout, each widget, data fetching
- "Add authentication" → split into schema, login form, signup form, session hooks, protected routes
- "Create the API" → split into each endpoint

## Story Template for SvelteKit PWA

### Foundation Stories (always first)

```json
{
  "id": "US-001",
  "title": "Create root layout with header/footer",
  "description": "As a user, I want consistent navigation across the app.",
  "acceptanceCriteria": [
    "Root +layout.svelte with <Header> and <Footer> components",
    "Header includes navigation links",
    "Footer includes copyright and links",
    "Responsive: mobile hamburger menu, desktop horizontal nav",
    "Typecheck passes"
  ],
  "priority": 1,
  "passes": false,
  "notes": ""
}
```

```json
{
  "id": "US-002", 
  "title": "Set up design tokens and global styles",
  "description": "As a developer, I need consistent styling primitives.",
  "acceptanceCriteria": [
    "Tailwind config with brand colors defined",
    "CSS variables for colors in app.css",
    "Typography scale configured",
    "Typecheck passes"
  ],
  "priority": 2,
  "passes": false,
  "notes": ""
}
```

```json
{
  "id": "US-003",
  "title": "Create home page",
  "description": "As a user, I want a landing page that explains the app.",
  "acceptanceCriteria": [
    "Hero section with headline and CTA",
    "Key features section",
    "Responsive layout",
    "Typecheck passes",
    "Verify in browser"
  ],
  "priority": 3,
  "passes": false,
  "notes": ""
}
```

### Database Stories (if drizzle)

```json
{
  "id": "US-DB-001",
  "title": "Configure Drizzle connection",
  "description": "As a developer, I need database connectivity.",
  "acceptanceCriteria": [
    "drizzle.config.ts configured for [postgres/sqlite]",
    "src/lib/server/db/index.ts exports db client",
    "Connection works (test with simple query)",
    "Typecheck passes"
  ],
  "priority": 4,
  "passes": false,
  "notes": ""
}
```

```json
{
  "id": "US-DB-002",
  "title": "Create [model] schema and migration",
  "description": "As a developer, I need to store [model] data.",
  "acceptanceCriteria": [
    "Schema defined in src/lib/server/db/schema.ts",
    "Migration generated and runs successfully",
    "Can insert/query test data",
    "Typecheck passes"
  ],
  "priority": 5,
  "passes": false,
  "notes": ""
}
```

### Auth Stories (if lucia)

```json
{
  "id": "US-AUTH-001",
  "title": "Configure Lucia auth",
  "description": "As a developer, I need auth infrastructure.",
  "acceptanceCriteria": [
    "src/lib/server/auth.ts exports lucia instance",
    "Session table in database schema",
    "User table in database schema",
    "Migration runs successfully",
    "Typecheck passes"
  ],
  "priority": 6,
  "passes": false,
  "notes": ""
}
```

```json
{
  "id": "US-AUTH-002",
  "title": "Create login page",
  "description": "As a user, I want to log into my account.",
  "acceptanceCriteria": [
    "Login form with email/password fields",
    "Form validation with error messages",
    "Successful login redirects to dashboard",
    "Invalid credentials show error",
    "Typecheck passes",
    "Verify in browser"
  ],
  "priority": 7,
  "passes": false,
  "notes": ""
}
```

### i18n Stories (if paraglide)

```json
{
  "id": "US-I18N-001",
  "title": "Configure Paraglide",
  "description": "As a developer, I need i18n infrastructure.",
  "acceptanceCriteria": [
    "Paraglide configured with [en, es] languages",
    "Language files created in src/lib/i18n/",
    "Default language is English",
    "Typecheck passes"
  ],
  "priority": 8,
  "passes": false,
  "notes": ""
}
```

```json
{
  "id": "US-I18N-002",
  "title": "Add language switcher component",
  "description": "As a user, I want to change the app language.",
  "acceptanceCriteria": [
    "LanguageSwitcher component in header",
    "Switches between [en/es] on click",
    "Preference persists in localStorage",
    "Current language visually indicated",
    "Typecheck passes",
    "Verify in browser"
  ],
  "priority": 9,
  "passes": false,
  "notes": ""
}
```

### UI Stories Pattern

```json
{
  "id": "US-UI-XXX",
  "title": "[Component/Page name]",
  "description": "As a [user], I want [feature].",
  "acceptanceCriteria": [
    "Specific visual/functional requirement",
    "Another requirement",
    "Responsive on mobile/desktop",
    "Typecheck passes",
    "Verify in browser"
  ],
  "priority": 10,
  "passes": false,
  "notes": ""
}
```

### Final Stories (always last)

```json
{
  "id": "US-PWA-001",
  "title": "Configure PWA manifest and icons",
  "description": "As a user, I want to install the app on my device.",
  "acceptanceCriteria": [
    "manifest.json with app name, icons, colors",
    "Icons at 192x192 and 512x512 in static/icons/",
    "App installable on mobile",
    "Typecheck passes",
    "Verify in browser"
  ],
  "priority": 98,
  "passes": false,
  "notes": ""
}
```

```json
{
  "id": "US-TEST-001",
  "title": "Add E2E tests for critical flows",
  "description": "As a developer, I need confidence in deployments.",
  "acceptanceCriteria": [
    "Playwright test for home page load",
    "Playwright test for [critical user flow]",
    "All tests pass",
    "Typecheck passes"
  ],
  "priority": 99,
  "passes": false,
  "notes": ""
}
```

## Acceptance Criteria Rules

Always include:
- "Typecheck passes" (every story)
- "Verify in browser" (any UI story)
- Specific, testable conditions

Good criteria:
- "Button is disabled while form is submitting"
- "Error message appears below invalid field"
- "List shows 'No items found' when empty"

Bad criteria:
- "Works correctly" (not testable)
- "Looks good" (subjective)
- "Handles errors" (not specific)

## Generating the Plan

When user describes their project:

1. Identify core features from description
2. Start with Foundation stories (US-001 through US-003)
3. Add infrastructure stories if needed (DB, Auth, i18n)
4. Break each feature into small UI stories
5. End with PWA and Test stories
6. Number priorities sequentially
7. Output valid JSON to `prd.json`
