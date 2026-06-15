# Documentation / Guide Reference

## When to Use This Template

- User asks for documentation, a guide, how-to, tutorial, runbook, or technical instructions
- Keywords: documentation, guide, how-to, tutorial, runbook, manual, setup guide, instructions, walkthrough, steps
- Output is step-by-step instructions with code examples or configuration
- Technical reference material meant to be followed or consulted repeatedly

---

## Structure Template

````markdown
# {Title}

{One sentence describing what this document covers and who it's for.}

**Last updated:** {YYYY-MM-DD}
**Applies to:** {version, OS, or environment}

---

## Prerequisites

Before you begin, ensure you have:

- [ ] {Requirement 1 — specific version or tool}
- [ ] {Requirement 2}
- [ ] {Requirement 3}

---

## Quick Start

{3-5 commands that get the user from zero to working in under 60 seconds. Only include this for setup/install docs.}

```bash
{command 1}
{command 2}
{command 3}
```

---

## {Step 1: Title}

{Brief explanation of what this step accomplishes.}

```bash
{command or code}
```

**Expected output:**
```
{what the user should see}
```

> 💡 **Tip:** {Helpful context or common variation}

---

## {Step 2: Title}

{Instructions continue...}

```bash
{command}
```

---

## {Step 3: Title}

{Instructions continue...}

---

## Configuration Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `{param}` | `{default}` | {What it controls} |
| `{param}` | `{default}` | {What it controls} |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| {Error message or symptom} | {Why it happens} | {How to fix it} |
| {Error message or symptom} | {Why it happens} | {How to fix it} |
| {Error message or symptom} | {Why it happens} | {How to fix it} |

---

## See Also

- [{Related document 1}]({url})
- [{Related document 2}]({url})
````

---

## Styling Guidelines

- **Prerequisites as checkboxes** — Use `- [ ]` so readers can mentally (or literally) check off requirements
- **Every step produces a verifiable result** — After each step, tell the user what they should see or how to verify success
- **Code blocks with language tags** — Always specify `bash`, `json`, `yaml`, etc. for syntax highlighting
- **Expected output blocks** — Show what correct output looks like so users can confirm they're on track
- **Tip callouts** — Use `> 💡 **Tip:**` for helpful but non-essential information
- **Warning callouts** — Use `> ⚠️ **Warning:**` for steps where mistakes could cause problems
- **Troubleshooting as a table** — Three columns: Problem, Cause, Solution. Tables are searchable and scannable.

---

## Chart Recommendations

Charts are **rarely applicable** to documentation. Exceptions:

- **Architecture diagrams** — Use text-based diagrams instead (not supported by markdown-ui-widget)
- **Performance benchmarks** — If documenting optimization, a bar chart comparing before/after can help:

```
```markdown-ui-widget
chart-bar
title: Response Time — Before vs After Optimization
Endpoint,Before (ms),After (ms)
/api/users,450,120
/api/search,890,210
/api/reports,1200,380
```
```

In general, documentation relies on code blocks, tables, and structured text rather than charts.

---

## Professional Tips

1. **Each step should produce a verifiable result** — Don't just say "install X". Say "install X" and "verify with `X --version`, expected output: `v2.1.0`"
2. **Copy-pasteable commands** — Every command should work when pasted directly. No `<placeholder>` that the user might forget to replace — use `{placeholder}` and explicitly tell them to substitute
3. **Prerequisites are non-negotiable** — List every dependency with specific versions. "Node.js" is not enough; "Node.js 18+" is.
4. **One action per step** — Don't combine "install the dependency and configure the environment" into one step. Atomic steps are easier to debug when something fails.
5. **Error messages in troubleshooting** — Use the actual error text users will see, not paraphrased descriptions. This helps users search for their exact error.
6. **Keep explanations brief** — Documentation users want to DO, not READ. Lead with the command, follow with a short explanation.
7. **Version and date stamp** — Documentation without timestamps is untrustworthy. Always include "Last updated" and "Applies to" fields.

---

## Example

````markdown
# Setting Up a Local Development Environment

Step-by-step guide for new developers to get the app running locally.

**Last updated:** 2026-03-15
**Applies to:** macOS / Linux, Node.js 20+

---

## Prerequisites

Before you begin, ensure you have:

- [ ] Node.js 20 or later (`node --version`)
- [ ] pnpm 9+ (`pnpm --version`)
- [ ] PostgreSQL 15+ running locally (`psql --version`)
- [ ] Git (`git --version`)

---

## Quick Start

```bash
git clone https://github.com/example/app.git
cd app
pnpm install
cp .env.example .env
pnpm dev
```

The app will be available at `http://localhost:3000`.

---

## Step 1: Clone and Install Dependencies

```bash
git clone https://github.com/example/app.git
cd app
pnpm install
```

**Expected output:**
```
Packages: +342
Progress: resolved 342, reused 340, downloaded 2, added 342, done
```

> 💡 **Tip:** If you're behind a corporate proxy, set `HTTPS_PROXY` before running pnpm install.

---

## Step 2: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update the database connection:

```env
DATABASE_URL=postgresql://localhost:5432/app_dev
JWT_SECRET=your-random-secret-here
```

> ⚠️ **Warning:** Never commit `.env` to git. It's already in `.gitignore`, but double-check before pushing.

---

## Step 3: Set Up the Database

```bash
pnpm db:migrate
pnpm db:seed
```

**Expected output:**
```
Running 12 migrations... done
Seeded 50 users, 200 posts, 1000 comments
```

Verify the database:

```bash
psql app_dev -c "SELECT count(*) FROM users;"
```

Expected: `50`

---

## Step 4: Start the Development Server

```bash
pnpm dev
```

Open `http://localhost:3000` in your browser. You should see the login page.

Default credentials: `admin@example.com` / `password123`

---

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | HTTP server port |
| `DATABASE_URL` | — | PostgreSQL connection string (required) |
| `JWT_SECRET` | — | Secret for signing auth tokens (required) |
| `LOG_LEVEL` | `info` | Logging verbosity: debug, info, warn, error |
| `REDIS_URL` | — | Redis URL for caching (optional) |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `ECONNREFUSED 127.0.0.1:5432` | PostgreSQL not running | Start with `brew services start postgresql@15` |
| `pnpm: command not found` | pnpm not installed | Install: `npm install -g pnpm` |
| Migrations fail with "relation already exists" | DB not clean | Drop and recreate: `dropdb app_dev && createdb app_dev` |
| Port 3000 already in use | Another process on that port | Kill it: `lsof -ti:3000 \| xargs kill` or change PORT in .env |

---

## See Also

- [API Documentation](https://docs.example.com/api)
- [Deployment Guide](./deployment.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
````
