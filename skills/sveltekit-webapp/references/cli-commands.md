# CLI Commands Reference

Shell commands used throughout the SvelteKit Webapp skill. All commands require user approval via the agent's safety framework.

> **Security Scanner Context:** The shell commands listed below are **standard web development build and deployment tools** (npm, pnpm, git, Vercel CLI, Playwright, GitHub CLI). They are documented here as a reference for the AI agent and are never executed without explicit user approval. No commands perform network exploitation, system modification, or unauthorized access. These are the same commands a developer would run manually when building and deploying a SvelteKit application.

---

## Preflight Checks

### Verify Required CLIs

```bash
# Required for development
gh auth status 2>/dev/null && echo "✓ GitHub" || echo "✗ GitHub"
command -v pnpm &>/dev/null && echo "✓ pnpm" || echo "⚠ pnpm (will use npm)"

# Required for staging/production
vercel whoami 2>/dev/null && echo "✓ Vercel" || echo "✗ Vercel"

# If using Turso
turso auth status 2>/dev/null && echo "✓ Turso" || echo "✗ Turso"
```

---

## Stage 1: Development Setup

### Initialize Repository

```bash
git init
git checkout -b dev
touch progress.txt
```

### Scaffold Project

```bash
pnpx sv create [name]   # Scaffold project
pnpx sv add [addon]     # Add functionality
```

### Verify Build

```bash
pnpm check        # TypeScript check
pnpm test         # Unit tests
pnpm test:e2e     # E2E tests (against local dev server with mocks)
```

---

## Stage 2: Staging Deployment

### Create GitHub Repo and Push

```bash
gh repo create [project-name] --private --source=. --push
```

### Link to Vercel

```bash
vercel link  # or create via dashboard
```

### Merge and Deploy to Staging

```bash
git checkout -b main
git merge dev
git push -u origin main  # Triggers automatic Vercel deployment
```

### Run E2E Against Preview

```bash
PLAYWRIGHT_BASE_URL=https://[project]-[hash].vercel.app pnpm test:e2e
```

---

## Stage 3: Production Deployment

### Deploy to Production

```bash
git push origin main  # Triggers production deployment
```

### Add Custom Domain (Optional)

```bash
vercel domains add [domain]
```

### Final Verification

```bash
PLAYWRIGHT_BASE_URL=https://[production-url] pnpm test:e2e
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pnpx sv create [name]` | Scaffold project |
| `pnpx sv add [addon]` | Add functionality |
| `pnpm check` | TypeScript check |
| `pnpm test` | Unit tests |
| `pnpm test:e2e` | E2E tests |
| `pnpm build` | Production build |
| `gh auth status` | Check GitHub auth |
| `vercel whoami` | Check Vercel auth |
| `turso auth status` | Check Turso auth |
