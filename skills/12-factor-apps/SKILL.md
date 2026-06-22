---
name: 12-factor-apps
description: Perform 12-Factor App compliance analysis on any codebase. Use when evaluating application architecture, auditing SaaS applications, or reviewing cloud-native applications against the original 12-Factor methodology.
---

# 12-Factor App Compliance Analysis

> Reference: [The Twelve-Factor App](https://12factor.net)

## Overview

The 12-Factor App methodology is a set of best practices for building Software-as-a-Service applications that are:
- Portable across execution environments
- Scalable without architectural changes
- Suitable for continuous deployment
- Maintainable with minimal friction

## Input Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `codebase_path` | Root path of the codebase to analyze | Required |

## Analysis Framework

### Factor I: Codebase

**Principle:** One codebase tracked in revision control, many deploys.

**Search Patterns:**
```bash
# Check for version control
ls -la .git 2>/dev/null || ls -la .hg 2>/dev/null

# Check for multiple apps sharing codebase
find . -name "package.json" -o -name "pyproject.toml" -o -name "setup.py" | head -20

# Check for environment-specific code branches
grep -r "if.*production\|if.*development\|if.*staging" --include="*.py" --include="*.js" --include="*.ts"
```

**File Patterns:** `.git/`, `package.json`, `pyproject.toml`, deployment configs

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Single Git repo, same codebase for all environments, no env-specific code branches |
| **Partial** | Single repo but some environment-specific code paths |
| **Weak** | Multiple repos for same app or significant code duplication across environments |

**Anti-patterns:**
- Multiple Git repositories for the same application
- Environment-specific code branches (`if production: ...`)
- Different source files for dev vs prod
- Shared code not extracted to libraries

---

### Factor II: Dependencies

**Principle:** Explicitly declare and isolate dependencies.

**Search Patterns:**
```bash
# Python dependency files
find . -name "requirements.txt" -o -name "pyproject.toml" -o -name "setup.py" -o -name "Pipfile" -o -name "uv.lock"

# JavaScript/TypeScript dependency files
find . -name "package.json" -o -name "package-lock.json" -o -name "yarn.lock" -o -name "pnpm-lock.yaml"

# Check for system tool assumptions
grep -r "subprocess.*curl\|subprocess.*wget\|os.system.*ffmpeg\|shutil.which" --include="*.py"
grep -r "exec.*curl\|child_process.*curl" --include="*.js" --include="*.ts"

# Docker/container isolation
find . -name "Dockerfile" -o -name "docker-compose*.yml"
```

**File Patterns:** `**/requirements*.txt`, `**/package.json`, `**/*.lock`, `**/Dockerfile`

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Lock files present, dependency isolation (venv/Docker), no implicit system tools |
| **Partial** | Dependencies declared but no lock files or isolation |
| **Weak** | Dependencies in documentation only, relies on system-installed packages |

**Anti-patterns:**
- Missing lock files (non-deterministic builds)
- Assuming system tools (curl, ImageMagick, ffmpeg) are available
- Different dependency managers in dev vs production
- No virtual environment or container isolation

---

### Factor III: Config

**Principle:** Store config in the environment.

**Search Patterns:**
```bash
# Environment variable usage
grep -r "os.environ\|os.getenv\|process.env\|ENV\[" --include="*.py" --include="*.js" --include="*.ts" --include="*.rb"

# Hardcoded credentials (anti-pattern)
grep -r "password.*=.*['\"]" --include="*.py" --include="*.js" --include="*.ts" | grep -v "test\|spec\|example"
grep -r "api_key.*=.*['\"]" --include="*.py" --include="*.js" --include="*.ts" | grep -v "test\|spec\|example"
grep -r "secret.*=.*['\"]" --include="*.py" --include="*.js" --include="*.ts" | grep -v "test\|spec\|example"

# Environment-specific config files (anti-pattern)
find . -name "config.dev.*" -o -name "config.prod.*" -o -name "settings.development.*" -o -name "settings.production.*"

# Database URLs in code
grep -r "postgresql://\|mysql://\|mongodb://\|redis://" --include="*.py" --include="*.js" --include="*.ts" | grep -v ".env\|test\|example"
```

**File Patterns:** `**/.env*`, `**/config/*.py`, `**/settings.py`, environment files

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | All config via environment variables, no hardcoded secrets, could open-source without leaks |
| **Partial** | Most config externalized but some hardcoded defaults |
| **Weak** | Hardcoded credentials, environment-specific config files |

**Anti-patterns:**
- Hardcoded database URLs, API keys, passwords in source
- Config files like `config/production.yml` vs `config/development.yml`
- Environment grouping (`if ENV == 'production': ...`)
- Secrets committed to version control

---

### Factor IV: Backing Services

**Principle:** Treat backing services as attached resources.

**Search Patterns:**
```bash
# Database connection via config
grep -r "DATABASE_URL\|DB_HOST\|REDIS_URL\|CACHE_URL" --include="*.py" --include="*.js" --include="*.ts"

# Service initialization
grep -r "create_engine\|MongoClient\|Redis\|Celery\|boto3" --include="*.py"
grep -r "createPool\|createClient\|new Redis\|S3Client" --include="*.js" --include="*.ts"

# Hardcoded service locations (anti-pattern)
grep -r "localhost:5432\|localhost:6379\|localhost:27017\|127.0.0.1" --include="*.py" --include="*.js" --include="*.ts" | grep -v "test\|spec\|example\|default"
```

**File Patterns:** `**/database/*.py`, `**/services/*.py`, `**/db.py`, connection configurations

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | All services via URL/connection string in config, swappable without code changes |
| **Partial** | Most services configurable but some hardcoded defaults |
| **Weak** | Hardcoded service locations, different code paths per environment |

**Anti-patterns:**
- Hardcoded `localhost` for services in production code
- Conditional logic for local vs cloud services (`if USE_S3: ... else: local_storage`)
- Service-specific code paths based on environment
- Different drivers for dev vs prod

---

### Factor V: Build, Release, Run

**Principle:** Strictly separate build and run stages.

**Search Patterns:**
```bash
# Build/deploy configuration
find . -name "Dockerfile" -o -name "Makefile" -o -name "build.sh" -o -name "deploy.sh"
find . -name ".github/workflows/*.yml" -o -name ".gitlab-ci.yml" -o -name "Jenkinsfile"

# Build scripts in package.json
grep -A5 '"scripts"' package.json 2>/dev/null | grep -E "build|start|deploy"

# Check for runtime compilation (anti-pattern)
grep -r "compile\|transpile\|webpack" --include="*.py" | grep -v "test\|build"
```

**File Patterns:** `**/Dockerfile`, `**/Makefile`, `**/.github/workflows/**`, CI/CD configs

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Immutable releases, clear build/release/run stages, unique release IDs |
| **Partial** | Build and run separated but release not immutable |
| **Weak** | Runtime code modifications, asset compilation at startup |

**Anti-patterns:**
- Runtime code modifications
- Asset compilation during application startup
- Configuration baked into build artifacts
- No release versioning

---

### Factor VI: Processes

**Principle:** Execute the app as one or more stateless processes.

**Search Patterns:**
```bash
# Session storage patterns
grep -r "session\|Session" --include="*.py" --include="*.js" --include="*.ts" | head -20

# In-process state (anti-pattern)
grep -r "global.*cache\|process_local\|instance_cache" --include="*.py"
grep -r "global\..*=\|module\.exports\.cache" --include="*.js" --include="*.ts"

# External session stores (good pattern)
grep -r "redis.*session\|memcached.*session\|session.*redis" --include="*.py" --include="*.js" --include="*.ts"

# Sticky session configuration (anti-pattern)
grep -r "sticky.*session\|session.*affinity" --include="*.yml" --include="*.yaml" --include="*.json"
```

**File Patterns:** `**/middleware/*.py`, `**/session/*.py`, server configurations

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Stateless processes, all state in external datastores (Redis, DB) |
| **Partial** | Mostly stateless but some in-process caching |
| **Weak** | Sticky sessions, in-process session storage, shared memory state |

**Anti-patterns:**
- In-process session storage (`user_sessions = {}`)
- Sticky sessions or session affinity
- File-based caching between requests
- Global mutable state shared across requests

---

### Factor VII: Port Binding

**Principle:** Export services via port binding.

**Search Patterns:**
```bash
# Self-contained port binding
grep -r "app.run\|server.listen\|serve\|uvicorn" --include="*.py"
grep -r "app.listen\|server.listen\|createServer" --include="*.js" --include="*.ts"

# PORT environment variable
grep -r "PORT\|port" --include="*.py" --include="*.js" --include="*.ts" | grep -i "environ\|process.env"

# Webserver as dependency
grep -r "uvicorn\|gunicorn\|flask\|fastapi\|express\|koa\|hapi" package.json pyproject.toml requirements.txt 2>/dev/null
```

**File Patterns:** `**/main.py`, `**/server.py`, `**/app.py`, `**/index.js`

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Self-contained app binds to PORT, webserver is a dependency |
| **Partial** | Port binding but not configurable via environment |
| **Weak** | Relies on external webserver container (Apache, Nginx) to provide HTTP |

**Anti-patterns:**
- Relying on Apache/Nginx/Tomcat to inject webserver functionality
- Hardcoded port numbers
- No PORT environment variable support
- CGI scripts or server modules

---

### Factor VIII: Concurrency

**Principle:** Scale out via the process model.

**Search Patterns:**
```bash
# Process definitions
find . -name "Procfile" -o -name "process.yml" -o -name ".foreman"

# Multiple entry points
find . -name "worker.py" -o -name "scheduler.py" -o -name "web.py"

# Background job systems
grep -r "celery\|rq\|sidekiq\|bull\|agenda" --include="*.py" --include="*.js" --include="*.ts"
grep -r "Celery\|Worker\|BackgroundJob" --include="*.py" --include="*.js" --include="*.ts"
```

**File Patterns:** `**/Procfile`, `**/worker.py`, `**/scheduler.py`, queue configurations

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Explicit process types (web, worker, scheduler), horizontal scaling |
| **Partial** | Multiple process types but not easily scalable |
| **Weak** | Single monolithic process, no separation of concerns |

**Anti-patterns:**
- Single process handling all workloads
- Hard-coded worker counts in code
- No separation between web and background processes
- Vertical scaling only (bigger server, not more processes)

---

### Factor IX: Disposability

**Principle:** Maximize robustness with fast startup and graceful shutdown.

**Search Patterns:**
```bash
# Signal handlers
grep -r "signal.signal\|SIGTERM\|SIGINT\|atexit" --include="*.py"
grep -r "process.on.*SIGTERM\|process.on.*SIGINT" --include="*.js" --include="*.ts"

# Graceful shutdown
grep -r "graceful.*shutdown\|shutdown_handler\|cleanup" --include="*.py" --include="*.js" --include="*.ts"

# Startup time
grep -r "startup\|initialize\|bootstrap" --include="*.py" --include="*.js" --include="*.ts" | head -20
```

**File Patterns:** `**/main.py`, `**/server.py`, lifecycle management code

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Fast startup (<10s), SIGTERM handling, graceful shutdown, jobs returnable to queue |
| **Partial** | Graceful shutdown but slow startup |
| **Weak** | No signal handling, jobs lost on process death, slow startup |

**Anti-patterns:**
- No SIGTERM/SIGINT handlers
- Slow startup (>30 seconds)
- Jobs lost if process crashes
- No cleanup on shutdown

---

### Factor X: Dev/Prod Parity

**Principle:** Keep development, staging, and production as similar as possible.

**Search Patterns:**
```bash
# Different services per environment (anti-pattern)
grep -r "if.*development.*sqlite\|if.*production.*postgres" --include="*.py" --include="*.js" --include="*.ts"
grep -r "development.*SQLite\|production.*PostgreSQL" --include="*.py" --include="*.js" --include="*.ts"

# Docker for parity
find . -name "docker-compose*.yml" -o -name "Dockerfile"

# Environment-specific backends
grep -r "USE_LOCAL_\|LOCAL_STORAGE\|MOCK_" --include="*.py" --include="*.js" --include="*.ts"
```

**File Patterns:** `**/docker-compose*.yml`, environment configurations

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Same services everywhere (PostgreSQL in dev and prod), containerized |
| **Partial** | Mostly same but some lightweight dev alternatives |
| **Weak** | SQLite in dev, PostgreSQL in prod; different backing services |

**Anti-patterns:**
- SQLite for development, PostgreSQL for production
- In-memory cache in dev, Redis in prod
- Different service versions across environments
- "It works on my machine" issues

---

### Factor XI: Logs

**Principle:** Treat logs as event streams.

**Search Patterns:**
```bash
# Stdout logging
grep -r "print(\|logging.info\|logger.info\|console.log" --include="*.py" --include="*.js" --include="*.ts" | head -20

# File-based logging (anti-pattern)
grep -r "FileHandler\|open.*\.log\|writeFile.*log\|fs.appendFile.*log" --include="*.py" --include="*.js" --include="*.ts"
grep -r "/var/log\|/tmp/.*\.log\|logs/" --include="*.py" --include="*.js" --include="*.ts" | grep -v "test\|example"

# Structured logging
grep -r "structlog\|json_logger\|pino\|winston" --include="*.py" --include="*.js" --include="*.ts"
```

**File Patterns:** `**/logging.py`, `**/logger.py`, logging configurations

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Unbuffered stdout only, structured logging (JSON), no file management |
| **Partial** | Stdout logging but with some file handlers |
| **Weak** | Application writes to log files, manages rotation |

**Anti-patterns:**
- Writing logs to files (`FileHandler`, `open('/var/log/app.log')`)
- Log rotation logic in application code
- Log archival managed by application
- Buffered logging

---

### Factor XII: Admin Processes

**Principle:** Run admin/management tasks as one-off processes.

**Search Patterns:**
```bash
# Management commands
find . -name "manage.py" -o -name "Rakefile" -o -name "artisan"
grep -r "@cli.command\|@click.command\|typer.command" --include="*.py"

# Migration scripts
find . -name "migrations" -type d
find . -name "*migration*.py" -o -name "*migrate*.py"

# Admin scripts with proper isolation
grep -r "bundle exec\|source.*venv\|uv run" --include="*.sh" --include="Makefile"
```

**File Patterns:** `**/manage.py`, `**/cli.py`, `**/migrations/**`, admin scripts

**Compliance Criteria:**

| Level | Criteria |
|-------|----------|
| **Strong** | Admin tasks use same dependencies/config, proper isolation, idempotent |
| **Partial** | Admin tasks exist but different setup from app |
| **Weak** | Manual database manipulation, scripts without isolation |

**Anti-patterns:**
- Admin scripts not using app's dependency manager
- Direct SQL manipulation outside of migrations
- Admin scripts with hardcoded credentials
- Non-idempotent migrations

---

## Output Format

### Executive Summary Table

```markdown
| Factor | Status | Notes |
|--------|--------|-------|
| I. Codebase | **Strong/Partial/Weak** | [Key finding] |
| II. Dependencies | **Strong/Partial/Weak** | [Key finding] |
| III. Config | **Strong/Partial/Weak** | [Key finding] |
| IV. Backing Services | **Strong/Partial/Weak** | [Key finding] |
| V. Build/Release/Run | **Strong/Partial/Weak** | [Key finding] |
| VI. Processes | **Strong/Partial/Weak** | [Key finding] |
| VII. Port Binding | **Strong/Partial/Weak** | [Key finding] |
| VIII. Concurrency | **Strong/Partial/Weak** | [Key finding] |
| IX. Disposability | **Strong/Partial/Weak** | [Key finding] |
| X. Dev/Prod Parity | **Strong/Partial/Weak** | [Key finding] |
| XI. Logs | **Strong/Partial/Weak** | [Key finding] |
| XII. Admin Processes | **Strong/Partial/Weak** | [Key finding] |

**Overall**: X Strong, Y Partial, Z Weak
```

### Per-Factor Analysis

For each factor, provide:

1. **Current Implementation**
   - Evidence with file:line references
   - Code snippets showing patterns

2. **Compliance Level**
   - Strong/Partial/Weak with justification

3. **Gaps**
   - What's missing vs. 12-Factor ideal

4. **Recommendations**
   - Actionable improvements with code examples

---

## Analysis Workflow

1. **Initial Scan**
   - Run search patterns for all factors
   - Identify key files for each factor
   - Note any existing compliance documentation

2. **Deep Dive** (per factor)
   - Read identified files
   - Evaluate against compliance criteria
   - Document evidence with file paths

3. **Gap Analysis**
   - Compare current vs. 12-Factor ideal
   - Identify anti-patterns present
   - Prioritize by impact

4. **Recommendations**
   - Provide actionable improvements
   - Include before/after code examples
   - Reference best practices

5. **Summary**
   - Compile executive summary table
   - Highlight strengths and critical gaps
   - Suggest priority order for improvements

---

## Quick Reference: Compliance Scoring

| Score | Meaning | Action |
|-------|---------|--------|
| **Strong** | Fully implements principle | Maintain, minor optimizations |
| **Partial** | Some implementation, significant gaps | Planned improvements |
| **Weak** | Minimal or no implementation | High priority for roadmap |

## When to Use This Skill

- Evaluating new SaaS applications
- Reviewing cloud-native architecture decisions
- Auditing production applications for scalability
- Planning migration to cloud platforms
- Comparing application architectures
- Preparing for containerization/Kubernetes deployment
