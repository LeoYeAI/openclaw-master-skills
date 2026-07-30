---
name: phy-dotenv-inheritance-mapper
description: Maps your full .env inheritance chain into a single resolved view. Reads all .env files (.env, .env.local, .env.example, .env.staging, .env.production, .env.test) in the correct override order, shows which layer each variable comes from, flags conflicts between environments, detects variables missing from .env.example, and identifies variables referenced in code that have no definition anywhere. Works for any framework or language. Zero external API — pure local file analysis. Triggers on "env inheritance", "which env file wins", "merge env files", "effective env values", "env override order", ".env chain", "/dotenv-mapper".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - dotenv
    - environment-variables
    - configuration
    - developer-tools
    - devops
    - twelve-factor
    - debugging
    - local-dev
---

# Dotenv Inheritance Mapper

Every project accumulates `.env` files: `.env`, `.env.local`, `.env.example`, `.env.staging`, `.env.production`, `.env.test`. They override each other in framework-specific order that nobody remembers. When a bug is "only in staging", it's usually a variable that exists in one file and not another.

This skill resolves your full `.env` chain into a single merged view — showing exactly which layer each value comes from, what overrides what, and where the gaps are.

**No external API. No config. Works for Next.js, Vite, Create React App, NestJS, FastAPI, Rails, or any custom setup.**

---

## Trigger Phrases

- "env inheritance", "which .env file wins", "env override order"
- "merge my env files", "what's the effective value of X"
- "missing from .env.example", "env files conflict"
- "env chain", "dotenv hierarchy", ".env resolution order"
- "/dotenv-mapper"

---

## How to Provide Input

```bash
# Option 1: Audit current directory
/dotenv-mapper

# Option 2: Specific directory
/dotenv-mapper src/

# Option 3: Check a specific variable
/dotenv-mapper --check DATABASE_URL

# Option 4: Target environment
/dotenv-mapper --env staging
/dotenv-mapper --env production

# Option 5: Specify framework (auto-detected if omitted)
/dotenv-mapper --framework nextjs
/dotenv-mapper --framework vite
/dotenv-mapper --framework nestjs

# Option 6: Show only conflicts
/dotenv-mapper --conflicts-only
```

---

## Step 1: Detect Framework and Load Order

Different frameworks resolve .env files in different orders. Detect the framework first:

```bash
# Detect framework from config files
if [ -f "next.config.js" ] || [ -f "next.config.ts" ] || [ -f "next.config.mjs" ]; then
  FRAMEWORK="nextjs"
elif grep -q '"vite"' package.json 2>/dev/null; then
  FRAMEWORK="vite"
elif grep -q '"react-scripts"' package.json 2>/dev/null; then
  FRAMEWORK="cra"
elif [ -f "nest-cli.json" ]; then
  FRAMEWORK="nestjs"
elif [ -f "manage.py" ] || [ -f "pyproject.toml" ]; then
  FRAMEWORK="python"
elif [ -f "Gemfile" ]; then
  FRAMEWORK="rails"
else
  FRAMEWORK="generic"
fi
echo "Detected framework: $FRAMEWORK"
```

### Load Order by Framework

| Framework | Order (later overrides earlier) |
|-----------|--------------------------------|
| **Next.js** | `.env` → `.env.local` → `.env.{NODE_ENV}` → `.env.{NODE_ENV}.local` |
| **Vite** | `.env` → `.env.local` → `.env.{mode}` → `.env.{mode}.local` |
| **Create React App** | `.env` → `.env.local` → `.env.{NODE_ENV}` → `.env.{NODE_ENV}.local` |
| **NestJS / Node** | `.env` → `.env.{NODE_ENV}` → `.env.local` |
| **Python/Django** | `.env` → `.env.{ENV}` (via dotenv/environs) |
| **Rails** | `.env` → `.env.{RAILS_ENV}` → `.env.{RAILS_ENV}.local` |
| **Docker Compose** | `.env` overridden by `environment:` block in compose file |
| **Generic** | `.env` → `.env.local` → `.env.{NODE_ENV}` |

### Important: `.local` files are gitignored

```bash
# Check which .env files are gitignored
grep -E "^\.env" .gitignore 2>/dev/null
# .env.local and *.local should be gitignored — if not, flag it
```

---

## Step 2: Discover All .env Files

```bash
# Find all .env files in the project root and one level deep
find . -maxdepth 2 \
  -name ".env" -o \
  -name ".env.local" -o \
  -name ".env.example" -o \
  -name ".env.template" -o \
  -name ".env.sample" -o \
  -name ".env.development" -o \
  -name ".env.development.local" -o \
  -name ".env.staging" -o \
  -name ".env.staging.local" -o \
  -name ".env.production" -o \
  -name ".env.production.local" -o \
  -name ".env.test" -o \
  -name ".env.test.local" \
  2>/dev/null | grep -v "node_modules" | sort

# Also check for Docker Compose env vars
find . -name "docker-compose*.yml" -o -name "docker-compose*.yaml" \
  -not -path "*/node_modules/*" 2>/dev/null | head -5
```

---

## Step 3: Parse and Merge

For each .env file in load order, parse key-value pairs:

```bash
# Parse a single .env file (handles comments, blank lines, quoted values)
parse_env_file() {
  local file="$1"
  local source_label="$2"
  grep -E "^[A-Za-z_][A-Za-z0-9_]*=" "$file" 2>/dev/null | while IFS= read -r line; do
    key="${line%%=*}"
    value="${line#*=}"
    echo "$key|$value|$source_label"
  done
}

# Process each file in load order
for env_file in .env .env.local .env.staging .env.production; do
  [ -f "$env_file" ] && parse_env_file "$env_file" "$env_file"
done
```

### Merge Logic

For each variable key:
1. Start with the value from the **lowest priority** file
2. For each subsequent file in load order, if the same key appears, the new value **overrides** the previous
3. Track the **winning layer** (which file's value is actually used)
4. Track **all layers** that define this key (for conflict detection)

---

## Step 4: Build the Inheritance Map

For each variable, produce a structured record:

```
KEY: DATABASE_URL
  Defined in: .env (base), .env.local (override), .env.production (override)
  Effective value: [from .env.local in development] [from .env.production in production]
  Conflict: YES — 3 different values across environments
```

### Variable Classification

| Class | Condition | Risk |
|-------|-----------|------|
| **CONSISTENT** | Same value in all env files that define it | ✅ No action |
| **OVERRIDDEN** | Different values across files (expected behavior) | ℹ️ Normal |
| **MISSING_FROM_EXAMPLE** | In `.env` or `.env.local` but not in `.env.example` | 🟠 New dev can't set it up |
| **EXAMPLE_ONLY** | In `.env.example` but in NO actual `.env` file | 🟡 New dev knows it exists but no value |
| **STAGING_NOT_PRODUCTION** | Defined in `.env.staging` but missing from `.env.production` | 🔴 Runtime crash in prod |
| **PRODUCTION_NOT_STAGING** | In production only | 🟡 Can't test prod behavior in staging |
| **SENSITIVE_EXPOSED** | Looks like a secret (`_KEY`, `_SECRET`, `_TOKEN`, `_PASSWORD`) AND is in a non-gitignored file | 🔴 Credential leak risk |
| **UNDOCUMENTED** | Not in `.env.example` AND not in any doc | 🟠 Hidden dependency |

---

## Step 5: Find Code-Referenced Variables

Cross-reference .env files against variables actually used in source code:

```bash
# JavaScript/TypeScript: process.env.VAR_NAME
grep -rh "process\.env\." . \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.mjs" \
  --exclude-dir="node_modules" \
  -o | grep -oE "[A-Z_]{3,}" | sort -u

# Python: os.environ.get("VAR_NAME") or os.getenv("VAR_NAME")
grep -rh "os\.environ\|os\.getenv" . \
  --include="*.py" \
  -o | grep -oE "['\"][A-Z_]{3,}['\"]" | tr -d "'\""  | sort -u

# Ruby: ENV["VAR_NAME"] or ENV.fetch("VAR_NAME")
grep -rh "ENV\[" . \
  --include="*.rb" \
  -o | grep -oE "['\"][A-Z_]{3,}['\"]" | tr -d "'\""  | sort -u

# Next.js public vars: process.env.NEXT_PUBLIC_*
grep -rh "NEXT_PUBLIC_" . \
  --include="*.ts" --include="*.tsx" --include="*.js" \
  --exclude-dir="node_modules" \
  -o | grep -oE "NEXT_PUBLIC_[A-Z_]+" | sort -u
```

After collecting all code-referenced variable names:
- **REFERENCED BUT UNDEFINED**: Used in code, not in any .env file → will be `undefined` at runtime
- **DEFINED BUT UNREFERENCED**: In .env files, never read in code → dead configuration

---

## Step 6: Output Report

```markdown
## Dotenv Inheritance Map
Project: my-app | Framework: Next.js | Date: 2026-03-18
Files found: .env, .env.local, .env.example, .env.staging, .env.production

Load order (development): .env → .env.local → .env.development → .env.development.local
Load order (production):  .env → .env.production

---

### Summary

| Category | Count | Action |
|----------|-------|--------|
| 🔴 Missing in production (in staging only) | 3 | Add to .env.production or flag as intent |
| 🔴 Sensitive var in non-gitignored file | 1 | Move to .env.local immediately |
| 🟠 Referenced in code, not defined anywhere | 2 | Will be `undefined` at runtime |
| 🟠 Missing from .env.example | 5 | New developers can't set up without help |
| 🟡 Defined but never read in code | 4 | Dead configuration — remove or document |
| ℹ️ Properly overridden (expected) | 12 | Normal |
| ✅ Consistent across all environments | 8 | No action needed |

---

### Full Variable Map

| Variable | .env | .env.local | .env.staging | .env.production | .env.example | Effective (dev) | Status |
|----------|------|------------|--------------|-----------------|--------------|-----------------|--------|
| DATABASE_URL | ✓ postgres://localhost | ✓ **postgres://dev-db** | ✓ postgres://stg | ✓ postgres://prod | ✓ placeholder | .env.local | ✅ OK |
| STRIPE_SECRET_KEY | ✓ sk_test_xxx | — | ✓ sk_test_stg | ✓ sk_live_xxx | ✓ placeholder | .env (base) | 🔴 .env not gitignored! |
| REDIS_URL | — | — | ✓ redis://stg | — | — | **UNDEFINED** | 🔴 Missing in prod |
| NEXT_PUBLIC_API_URL | ✓ http://localhost:3000 | — | ✓ https://stg.api | ✓ https://api | ✓ placeholder | .env (base) | ✅ OK |
| FEATURE_NEW_UI | ✓ true | — | ✓ false | — | — | .env (base) | 🟡 Dead? Missing from prod |
| LOG_LEVEL | ✓ debug | — | — | — | — | .env (base) | 🟠 Not in .env.example |
| ANALYTICS_KEY | — | — | — | — | ✓ placeholder | **UNDEFINED** | 🟠 Defined only in example |
| OLD_PAYMENT_KEY | ✓ pk_test_xxx | — | — | — | — | .env (base) | 🟡 Never read in code |

---

### 🔴 CRITICAL ISSUES

**1. STRIPE_SECRET_KEY in .env (not gitignored)**
- File: `.env` — check your `.gitignore`
- `.env` is often committed to version control
- A secret key (`_KEY` pattern) should only be in `.env.local` or `.env.*.local` (gitignored)
- Fix: `mv .env .env.local` or add `STRIPE_SECRET_KEY=` to `.env` and set real value in `.env.local`

**2. REDIS_URL: defined in .env.staging but MISSING from .env.production**
- Your staging environment can connect to Redis; production cannot
- This will cause a runtime error or silent failure in production
- Fix: Add `REDIS_URL=` to `.env.production` with the production value

**3. NEXT_PUBLIC_SENTRY_DSN: referenced in code, not defined anywhere**
```
src/lib/monitoring.ts:14  process.env.NEXT_PUBLIC_SENTRY_DSN
src/app/layout.tsx:8      process.env.NEXT_PUBLIC_SENTRY_DSN
```
- Will evaluate to `undefined` in all environments
- Either add it to all .env files, or guard with a null check in code

---

### 🟠 HIGH — Missing from .env.example

These variables exist in your actual `.env` files but are not documented in `.env.example`. A new developer who clones this repo has no way to know they exist:

| Variable | Defined In | Value Type | Suggested .env.example Entry |
|----------|-----------|-----------|------------------------------|
| `LOG_LEVEL` | `.env` | `debug\|info\|warn\|error` | `LOG_LEVEL=info` |
| `INTERNAL_API_SECRET` | `.env.local` | Secret key | `INTERNAL_API_SECRET=` (see 1Password team vault) |
| `FEATURE_DARK_MODE` | `.env`, `.env.local` | `true\|false` | `FEATURE_DARK_MODE=false` |

---

### 🟡 MEDIUM — Defined but Never Referenced in Code

These variables exist in your .env files but no code ever reads them:

| Variable | File | Age | Recommendation |
|----------|------|-----|----------------|
| `OLD_PAYMENT_KEY` | `.env` | Last used 6+ months ago | Delete — check git log to confirm |
| `LEGACY_CDN_URL` | `.env`, `.env.production` | Unknown | Check git history for last use |
| `DEBUG_MODE` | `.env.local` | Unknown | Remove from .env.local, not used |
| `ANALYTICS_KEY` | `.env.example` only | Template artifact | Remove from example if not implemented |

---

### Generated .env.example (Updated)

The current `.env.example` is missing 3 variables. Here's the corrected version to copy in:

```bash
# Database
DATABASE_URL=postgres://user:password@localhost:5432/myapp

# Auth
STRIPE_SECRET_KEY=       # Get from Stripe Dashboard > Developers > API Keys
STRIPE_PUBLISHABLE_KEY=  # Get from Stripe Dashboard (safe to commit)

# Redis
REDIS_URL=redis://localhost:6379

# Monitoring
NEXT_PUBLIC_SENTRY_DSN=  # Get from Sentry > Settings > Projects > DSN

# Logging
LOG_LEVEL=info           # debug | info | warn | error

# Feature Flags
FEATURE_NEW_UI=false
FEATURE_DARK_MODE=false
```

---

### Gitignore Check

```bash
# Current .gitignore status for .env files:
✅ .env.local          — gitignored
✅ .env.*.local        — gitignored
⚠️  .env               — NOT gitignored (contains STRIPE_SECRET_KEY!)
✅ .env.example        — tracked (intended)
```

Recommended `.gitignore` additions:
```
# Environment files
.env
.env.local
.env.*.local
```

Note: If `.env` is currently tracked in git and contains secrets, run:
```bash
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "chore: remove .env from tracking, add to gitignore"
```
```

---

## Quick Mode

One-line summary for a fast sanity check:

```
Dotenv Quick Scan: my-app (Next.js)
Files: .env · .env.local · .env.example · .env.staging · .env.production

🔴 2 critical  (1 secret exposed, 1 missing in prod)
🟠 3 undocumented vars not in .env.example
🟡 4 dead vars never read in code
✅ 8 variables properly configured across all envs

Run /dotenv-mapper for full inheritance table with file-by-file breakdown
```

---

## Environment-Specific Mode

When you need to debug "why does this work in staging but not production?":

```bash
/dotenv-mapper --compare staging production

# Output shows a side-by-side diff of just the differences:
Variable               | staging                | production
-----------------------|------------------------|-------------------
REDIS_URL              | redis://stg-cache:6379 | ❌ MISSING
WORKER_CONCURRENCY     | 4                      | ❌ MISSING
LOG_LEVEL              | info                   | debug (← wrong)
RATE_LIMIT_MAX         | 100                    | 50
```

---

## Twelve-Factor Compliance Check

Assess compliance with the [12-Factor App](https://12factor.net/config) config principle:

```
12-Factor Config Compliance:
✅ Config stored in environment (not code)
✅ Different values per environment (staging ≠ prod)
⚠️  Not all vars documented in .env.example (3 missing)
❌ Secrets in committed files (.env not gitignored)
❌ 2 variables hardcoded in source: API_BASE_URL in src/config.ts:8

Score: 3/5 — Fix: gitignore .env, document missing vars, extract hardcoded values
```

---

## Why This Matters

The average Node.js project has 4-6 `.env` files. The override chain is:
1. Framework-specific (Next.js loads files differently than Vite)
2. Undocumented (nobody reads the Next.js docs for env loading order)
3. Silently broken (missing variables fail at runtime, not startup in many frameworks)

Most production bugs caused by environment configuration are:
- **Variable in staging, missing in production** (Redis, feature flags, third-party keys)
- **Secret committed to git** (in `.env` instead of `.env.local`)
- **New developer never set up correctly** (variable missing from `.env.example`)
- **Dead config** (variable still in all .env files, removed from code 6 months ago)

This skill turns the .env audit from an hour-long detective session into a 2-minute report.
