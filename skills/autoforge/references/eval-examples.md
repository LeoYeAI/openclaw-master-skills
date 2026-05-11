# Eval Examples by Skill Type

Ready-to-use Yes/No evals for immediate deployment in autoforge loops.

> **Mode mapping:** Categories below correspond to AutoForge modes as follows:
> - **prompt mode** → Briefing, Email, Calendar, Summary, Proposal (Yes/No scenario evals)
> - **code mode** → Python Script, Shell Script, API, Data Pipeline, Build, Docker, CI/CD, Terraform, Kubernetes (single-file measurable evals)
> - **audit mode** → API Documentation, Code Review (verify docs against reality)
> - **project mode** → Project / Repository, Cross-File Consistency, Security Baseline, CI/CD, Docker, Terraform, Kubernetes, Infrastructure (whole-repo / cross-file evals)
> - **Note:** CI/CD, Docker, Terraform, Kubernetes can be `code` (single-file) or `project` (cross-file) — see SKILL.md mapping table
>
> See SKILL.md § "Eval Examples → Mode Mapping" for the full table.

## Briefing / Email Summary
- All configured sources queried? (Yes/No)
- Summary under 400 words? (Yes/No)
- Important senders correctly prioritized? (Yes/No)
- No hallucinated or fabricated content? (Yes/No)

## Proposal / Pitch Generator
- Formatting correct (headings, structure)? (Yes/No)
- ROI or concrete value proposition stated? (Yes/No)
- Tone professional and context-appropriate? (Yes/No)
- All relevant client information included? (Yes/No)

## Code Review
- All critical issues found? (Yes/No)
- Proposed fixes correct and actionable? (Yes/No)
- No false positives (correct code flagged as bug)? (Yes/No)

## Email Assistant
- Tone matches recipient (formal/informal)? (Yes/No)
- All asked questions answered? (Yes/No)
- No hallucinations or false facts? (Yes/No)
- Email ready to send without manual editing? (Yes/No)

## Calendar Briefing
- All day's appointments listed? (Yes/No)
- Time and location correct? (Yes/No)
- Relevant context included (participants, prep)? (Yes/No)

## Summary / TL;DR
- Core message in first 2 sentences? (Yes/No)
- No important points omitted? (Yes/No)
- Under 200 words? (Yes/No)

---

## CI/CD Pipeline
- All pipeline stages documented? (Yes/No)
- Environment variables listed with defaults? (Yes/No)
- Failure modes and rollback described? (Yes/No)
- Secret management explained (no hardcoded values)? (Yes/No)
- Deployment targets and regions specified? (Yes/No)

## Terraform / Infrastructure as Code
- All resources have lifecycle rules? (Yes/No)
- State backend configured and documented? (Yes/No)
- Variables have descriptions and types? (Yes/No)
- Outputs documented for downstream consumers? (Yes/No)
- Provider version constraints specified? (Yes/No)
- Drift detection strategy described? (Yes/No)

## Kubernetes Manifests
- Resource limits and requests set? (Yes/No)
- Health checks (liveness, readiness) configured? (Yes/No)
- Security context (non-root, read-only FS) applied? (Yes/No)
- Namespace isolation enforced? (Yes/No)
- HPA/scaling strategy documented? (Yes/No)
- Network policies defined? (Yes/No)

## API Documentation
- All endpoints listed with methods? (Yes/No)
- Request/response schemas provided? (Yes/No)
- Authentication requirements described? (Yes/No)
- Error codes and messages documented? (Yes/No)
- Rate limiting explained? (Yes/No)
- Versioning strategy described? (Yes/No)

## Database Migration
- Forward migration tested? (Yes/No)
- Rollback migration provided and tested? (Yes/No)
- Data loss risks documented? (Yes/No)
- Performance impact estimated (lock duration, etc.)? (Yes/No)
- Compatible with zero-downtime deployment? (Yes/No)

---

## Project / Repository

Cross-file and whole-repo evals for project mode. Mix and match based on what the repo contains.

### CI/CD Pipeline (GitHub Actions)
- Workflow YAML syntactically valid? (`actionlint` or `yamllint exit 0`)
- Workflow references correct paths/scripts? (Yes/No)
- All secrets used in workflow are documented? (Yes/No)
- Matrix strategy covers target platforms? (Yes/No)
- Caching configured for dependencies? (Yes/No)
- Workflow triggers match branching strategy? (Yes/No)

### CI/CD Pipeline (GitLab CI)
- `.gitlab-ci.yml` valid? (`gitlab-ci-lint` or syntax check)
- Stages defined and ordered correctly? (Yes/No)
- Artifacts and cache configured? (Yes/No)
- Environment-specific variables scoped? (Yes/No)

### Docker
- `docker build .` succeeds? (`exit_code == 0`)
- No secrets in image layers? (`docker history` clean)
- Image size within budget? (`< 500MB` or project-specific)
- Multi-stage build used? (Dockerfile analysis)
- `.dockerignore` excludes build artifacts and secrets? (Yes/No)
- Base image pinned to digest or specific version? (Yes/No)
- `docker compose up` starts without errors? (if compose file exists)
- Health check defined in Dockerfile or compose? (Yes/No)

### Python Repository
- `pytest` passes? (`pytest exit 0`)
- Type checking clean? (`mypy . exit 0`)
- Linter clean? (`ruff check . exit 0` or `flake8 exit 0`)
- All imports resolvable? (`python -c "import pkg"` for each)
- `requirements.txt` ↔ imports consistent? (No missing, no unused)
- `pyproject.toml` / `setup.py` valid? (Yes/No)
- Python version constraint specified? (Yes/No)
- Virtual environment instructions in README? (Yes/No)

### Node.js Repository
- `npm test` passes? (`exit_code == 0`)
- `npm run lint` clean? (if lint script exists)
- `package.json` ↔ `require`/`import` consistent? (No missing, no unused)
- `package-lock.json` up to date? (`npm ci` succeeds)
- `engines` field specifies Node version? (Yes/No)
- No `console.log` in production code? (grep check)
- `main` / `exports` field points to existing file? (Yes/No)
- Scripts (`start`, `build`, `test`) defined and functional? (Yes/No)

### Infrastructure (Terraform)
- `terraform validate` passes? (`exit_code == 0`)
- `terraform fmt -check` clean? (No formatting diffs)
- All variables have descriptions? (Yes/No)
- Backend configuration documented? (Yes/No)
- Provider versions pinned? (Yes/No)
- No hardcoded credentials in `.tf` files? (grep check)

### Infrastructure (Kubernetes)
- Manifests valid? (`kubectl apply --dry-run=client` succeeds)
- Resource limits set on all containers? (Yes/No)
- No `latest` image tags? (grep check)
- Secrets not stored in plain manifests? (Yes/No)
- Namespace specified in all resources? (Yes/No)

### Cross-File Consistency
- README commands match actual CLI `--help` output? (Yes/No)
- README install instructions work? (manual or scripted verification)
- Dependencies file ↔ actual imports in sync? (No orphans, no missing)
- `.env.example` covers all env vars referenced in code? (grep cross-check)
- Config file references match actual file paths? (Yes/No)
- Version strings consistent across files? (package.json, pyproject.toml, Dockerfile, README)
- License file present and referenced in package metadata? (Yes/No)
- `.gitignore` excludes all build outputs and sensitive files? (Yes/No)
- CHANGELOG / release notes match tagged versions? (Yes/No)
- Contributing guide references correct branch/workflow? (Yes/No)

### Security Baseline
- No hardcoded passwords, API keys, or tokens? (`grep -rE "(password|api_key|secret|token)\s*=" exit 1`)
- No `.env` file committed? (`.env` in `.gitignore`)
- Dependencies have no known critical CVEs? (`npm audit` / `pip audit` / `trivy`)
- No overly permissive file permissions? (`find . -perm -o+w`)
- HTTPS used for all external URLs in config? (grep check)

---

# Code-Mode Evals (measurable, automated)

## Python Script
- Exit code 0? (`exit_code == 0`)
- All unit tests green? (`pytest exit 0`)
- No uncaught exceptions in stderr? (`"Traceback" not in stderr`)
- Runtime under limit? (`runtime_ms < 5000`)
- Output is valid JSON? (`json.loads(stdout)`)

## Shell Script
- shellcheck clean? (`shellcheck script.sh exit 0`)
- bash syntax ok? (`bash -n script.sh exit 0`)
- No hardcoded secrets? (`grep -E "(password|secret|key)=" == empty`)
- Exit code 0 on normal run? (`exit_code == 0`)

## API / Web Service
- Health endpoint reachable? (`curl /health → 200`)
- Response is valid JSON? (`json.loads(response)`)
- Response time under limit? (`response_time < 2000ms`)
- No 5xx errors? (`status_code < 500`)

## Data Pipeline
- Output file created? (`file_exists(output_path)`)
- Output not empty? (`file_size > 0`)
- Row count plausible? (`line_count > 100`)
- No duplicates? (`unique_lines == total_lines`)

## Build / Compile
- Build successful? (`exit_code == 0`)
- No warnings? (`"warning" not in stderr`)
- Binary created? (`file_exists(binary_path)`)
- Binary executable? (`binary --version exit 0`)

## Docker / Container
- Image builds without errors? (`docker build exit 0`)
- Container starts and passes health check? (`docker run --health-cmd`)
- No secrets in image layers? (`docker history` clean)
- Image size within budget? (`< 500MB`)
- Multi-stage build used? (Dockerfile analysis)

## Helm Chart
- `helm lint` passes? (`exit_code == 0`)
- `helm template` renders without errors? (`exit_code == 0`)
- Values schema validates? (`helm lint --strict`)
- All required values documented in values.yaml comments? (Yes/No)
