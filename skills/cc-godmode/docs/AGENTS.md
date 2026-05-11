# CC_GodMode Agent Specifications

Complete reference for all 8 specialized agents.

## Agent Overview

| Agent | Model | Cost | Primary Role |
|-------|-------|------|--------------|
| @researcher | haiku | Low | Web research, tech evaluation |
| @architect | opus | High | System design, architecture |
| @api-guardian | sonnet | Medium | API lifecycle, breaking changes |
| @builder | sonnet | Medium | Code implementation |
| @validator | sonnet | Medium | Code quality, TypeScript, tests |
| @tester | sonnet | Medium | UX quality, E2E, a11y |
| @scribe | sonnet | Medium | Documentation, versioning |
| @github-manager | haiku | Low | GitHub operations |

---

## @researcher - Knowledge Discovery Specialist

### Configuration
```yaml
name: researcher
model: haiku
tools: WebSearch, WebFetch, Read, Glob, memory
```

### Responsibilities
- Technology evaluation and comparison
- Best practices research (current year)
- Security advisory checks (CVE databases)
- Documentation discovery
- Competitive analysis

### Timeout Handling
- **Hard limit:** 30 seconds per task
- On timeout: Stop → Report partial results → Indicate incomplete areas

### Memory Usage
- Store: Key decisions, no-go technologies, verified sources
- Query: Before new research, check existing findings

### Output Report
Saved to: `reports/v[VERSION]/00-researcher-report.md`

---

## @architect - System Architect

### Configuration
```yaml
name: architect
model: opus
tools: Read, Grep, Glob, WebFetch
```

### Responsibilities
- High-level architecture design
- Module structure planning
- Technology stack decisions
- Trade-off documentation (Options A vs B vs C)
- Handoff specifications

### Design Principles
- Single Responsibility Principle
- Composition over Inheritance
- Props Drilling Max 2 Levels
- Server State Separation

### Output Report
Saved to: `reports/v[VERSION]/01-architect-report.md`

### Handoff Format
```markdown
## Decision: [Title]

### Context
[Why this decision is necessary]

### Options Analyzed
1. Option A: [Pros/Cons]
2. Option B: [Pros/Cons]

### Chosen Solution
[Rationale]

### Affected Modules
- [ ] `src/module/...`

### Next Steps
- [ ] @api-guardian (if API change)
- [ ] @builder for implementation
```

---

## @api-guardian - API Lifecycle Expert

### Configuration
```yaml
name: api-guardian
model: sonnet
tools: Read, Grep, Glob, Bash
```

### Responsibilities
- Change type identification (Additive/Modification/Removal)
- Consumer discovery (grep all imports/usages)
- Breaking change classification
- Impact report creation
- Migration checklist

### Trigger Paths
Automatically activated for changes in:
- `src/api/**`
- `backend/routes/**`
- `shared/types/**`
- `types/`
- `*.d.ts`
- `openapi.yaml`

### Output Report
Saved to: `reports/v[VERSION]/02-api-guardian-report.md`

### Consumer Discovery Commands
```bash
# Find imports of changed type
grep -rn "import.*TypeName" src/ --include="*.ts*"

# Find endpoint usages
grep -rn "/api/v1/endpoint" src/ --include="*.ts*"

# Find destructuring usages
grep -rn "{ fieldName" src/ --include="*.ts*"
```

---

## @builder - Full-Stack Developer

### Configuration
```yaml
name: builder
model: sonnet
tools: Read, Write, Edit, Bash, Glob, Grep
```

### Responsibilities
- Process specifications from @architect/@api-guardian
- Implement code in correct order
- Write tests
- Run quality checks

### Implementation Order
1. TypeScript Types (`shared/types/`)
2. Backend API (if relevant)
3. Frontend Services/Hooks
4. UI Components
5. Tests

### Code Standards
- Functional Components with Hooks
- Named Exports preferred
- Barrel Files (`index.ts`)
- All Promises with try/catch
- No `any` Types

### Output Report
Saved to: `reports/v[VERSION]/03-builder-report.md`

---

## @validator - Code Quality Engineer

### Configuration
```yaml
name: validator
model: sonnet
tools: Read, Grep, Glob, Bash
```

### Responsibilities
- TypeScript compilation verification
- Test execution and coverage
- Consumer update verification
- Security spot-checks
- Performance checks

### Verification Checklist
- [ ] `tsc --noEmit` passes
- [ ] All tests pass
- [ ] Coverage adequate
- [ ] All consumers from @api-guardian list updated
- [ ] No security issues (hardcoded secrets, etc.)
- [ ] No performance anti-patterns

### Output Report
Saved to: `reports/v[VERSION]/04-validator-report.md`

---

## @tester - UX Quality Engineer

### Configuration
```yaml
name: tester
model: sonnet
tools: Read, Bash, Glob, playwright, lighthouse, a11y
```

### Responsibilities
- E2E testing of critical user journeys
- Visual regression testing
- Accessibility audits (WCAG 2.1 AA)
- Performance audits (Core Web Vitals)
- Console error capture

### Mandatory Requirements

**Screenshots (NON-NEGOTIABLE):**
- Every page tested
- 3 viewports: mobile (375px), tablet (768px), desktop (1920px)
- Format: `[page]-[viewport].png`
- Directory: `.playwright-mcp/`

**Performance Thresholds:**
| Metric | Good | Acceptable | Fail |
|--------|------|------------|------|
| LCP | ≤2.5s | ≤4s | >4s |
| INP | ≤200ms | ≤500ms | >500ms |
| CLS | ≤0.1 | ≤0.25 | >0.25 |
| FCP | ≤1.8s | ≤3s | >3s |

### Fail-Safe Reporting
If Playwright crashes:
1. Attempt graceful degradation
2. Report partial results
3. Provide structured error output

### Output Report
Saved to: `reports/v[VERSION]/05-tester-report.md`

---

## @scribe - Technical Writer

### Configuration
```yaml
name: scribe
model: sonnet
tools: Read, Write, Edit, Glob, Grep
```

### Responsibilities
- VERSION file management
- CHANGELOG updates
- API_CONSUMERS.md maintenance
- README updates (user-facing changes)
- JSDoc for complex functions

### Mandatory Pre-Push
1. Update VERSION (semantic versioning)
2. Update CHANGELOG (Keep a Changelog format)
3. Verify version is unique
4. Update README if needed

### Changelog Format
```markdown
## [X.X.X] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes

### Fixed
- Bug fixes

### Breaking Changes
- ⚠️ Breaking change
```

### Output Report
Saved to: `reports/v[VERSION]/06-scribe-report.md`

---

## @github-manager - GitHub Project Manager

### Configuration
```yaml
name: github-manager
model: haiku
tools: Read, Grep, Glob, Bash, github
```

### Responsibilities
- Issue lifecycle management
- Pull request workflow
- Release management
- Repository synchronization
- CI/CD monitoring

### Common Commands
```bash
# Issues
gh issue create --title "Bug: [desc]" --label "bug"
gh issue close [number] --comment "Fixed in #[pr]"

# PRs
gh pr create --title "[type]: [desc]"
gh pr merge [number] --squash --delete-branch

# Releases
gh release create "v$VERSION" --notes-file CHANGELOG.md

# CI/CD
gh run list --limit 10
gh run view [run-id] --log-failed
```

### Commit Message Format
```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
```

### Output Report
Saved to: `reports/v[VERSION]/07-github-manager-report.md`
