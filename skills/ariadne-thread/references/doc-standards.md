# Documentation Standards (Tier B)

Standards for human-facing project documentation. These documents are maintained at **iteration-end** (not on every code change) and reference Tier A indexes (`AGENTS.md`, `INDEX.md`) as their source of truth.

Every document has one purpose, fits a tiered index, and stays under 500 lines.

## Documentation Directory Structure

```
docs/
├── README.md                # L0: What is this, how to get started (< 1 page)
├── architecture.md          # L1: System overview, component diagrams
├── conventions.md           # L1: Project-wide coding conventions
├── adr/                     # L2: Architecture Decision Records
│   ├── INDEX.md             # Summary table of all ADRs
│   ├── TEMPLATE.md          # ADR template for new decisions
│   ├── 001-database.md
│   └── 002-auth-flow.md
├── api/                     # L2: API reference
│   ├── INDEX.md             # Endpoint summary table
│   ├── authentication.md
│   └── users.md
└── guides/                  # L2: Developer guides
    ├── INDEX.md             # Guide list with summaries
    ├── getting-started.md
    └── deployment.md
```

## Document Rules

1. **One doc = one purpose**: never combine architecture overview + API reference + setup guide
2. **INDEX.md in every directory**: summarize contents so AI can decide what to read
3. **Link, don't inline**: reference other docs via relative links instead of copying content
4. **Max 500 lines**: split into sub-documents if longer
5. **Sync at iteration end**: update doc-level INDEX.md during the Tier B sync; reference Tier A `INDEX.md` as source of truth

## Architecture Document Template

```markdown
# Architecture Overview

## System Context

[1-2 paragraphs: what the system does, who uses it, what it connects to.]

## Component Diagram

\```
┌─────────┐     ┌──────────┐     ┌───────────┐
│  Client  │────▶│  API     │────▶│  Database  │
│  (Web)   │     │  Server  │     │  (Postgres)│
└─────────┘     └──────────┘     └───────────┘
                     │
                     ▼
                ┌──────────┐
                │  Cache   │
                │  (Redis) │
                └──────────┘
\```

## Component Responsibilities

| Component | Purpose | Key Tech |
|-----------|---------|----------|
| API Server | HTTP endpoints, auth, validation | [framework] |
| Database | Persistent storage | [database engine] |
| Cache | Session store, rate limiting | [cache engine] |

## Data Flow

[Describe the primary request/response flow in 3-5 numbered steps.]

1. Client sends request to API server
2. API server validates input and checks auth
3. Business logic processes the request
4. Data is persisted/retrieved from database
5. Response is formatted and returned

## Key Design Decisions

| Decision | Rationale | ADR |
|----------|-----------|-----|
| [Decision 1] | [One-line why] | `adr/001-*.md` |
| [Decision 2] | [One-line why] | `adr/002-*.md` |

## Cross-References

- Module details: see `src/[module]/INDEX.md`
- API reference: see `docs/api/INDEX.md`
- Deployment: see `docs/guides/deployment.md`
```

## ADR (Architecture Decision Record) Template

```markdown
# ADR-[NNN]: [Decision Title]

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-[NNN]
**Date**: YYYY-MM-DD
**Deciders**: [who was involved]

## Context

[What is the issue we're facing? What forces are at play? 2-4 sentences.]

## Decision

[What did we decide? State clearly and concisely. 1-3 sentences.]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

### Neutral
- [Side-effect that's neither good nor bad]

## Alternatives Considered

### [Alternative 1]
[Why rejected — 1-2 sentences.]

### [Alternative 2]
[Why rejected — 1-2 sentences.]
```

## API Reference Document Template

```markdown
# API: [Resource Name]

Base path: `/api/v1/[resource]`

## Endpoints Summary

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/[resource]` | List all | Required |
| POST | `/[resource]` | Create new | Required |
| GET | `/[resource]/:id` | Get by ID | Required |
| PATCH | `/[resource]/:id` | Update | Required |
| DELETE | `/[resource]/:id` | Delete | Admin |

## GET /[resource]

List all [resources] with optional filtering and pagination.

**Query Parameters**:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | number | 1 | Page number |
| `pageSize` | number | 20 | Items per page (max 100) |
| `sort` | string | `createdAt` | Sort field |
| `order` | `asc` \| `desc` | `desc` | Sort direction |

**Response** (200):

\```json
{
  "data": [{ "id": "...", "name": "..." }],
  "meta": { "total": 42, "page": 1, "pageSize": 20 }
}
\```

**Errors**:

| Code | Status | When |
|------|--------|------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |

## POST /[resource]

Create a new [resource].

**Request Body**:

\```json
{
  "name": "string (required)",
  "email": "string (required, valid email)"
}
\```

**Response** (201):

\```json
{
  "data": { "id": "...", "name": "...", "email": "..." }
}
\```
```

## Developer Guide Template

```markdown
# Guide: [Topic]

## Prerequisites

- [Required tool or access 1]
- [Required tool or access 2]

## Steps

### 1. [First Step Title]

[Clear instruction. Include command if applicable.]

\```bash
[command]
\```

[Expected outcome — what you should see.]

### 2. [Second Step Title]

[Clear instruction.]

### 3. [Third Step Title]

[Clear instruction.]

## Verification

[How to confirm the guide was followed correctly.]

\```bash
[verification command]
\```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| [What you see] | [Why it happens] | [What to do] |

## Next Steps

- [Link to related guide or doc]
```

## Iteration-End Sync Checklist (Tier B)

Run this checklist at the end of each development iteration — NOT on every code change. During active development, only Tier A indexes are maintained (see `SKILL.md` Index Maintenance section).

| Accumulated Change | Tier B Action |
|-------------------|---------------|
| API endpoints added/changed | Update `docs/api/INDEX.md` and relevant endpoint doc |
| Architecture decision made | Create ADR, update `docs/adr/INDEX.md` |
| Significant dependency added | Note in `architecture.md` if it affects system design |
| Module structure changed | Update `architecture.md` component diagram/table |
| Build/deploy process changed | Update developer guides |
| New environment variable | Update deployment guide |
| Project scope changed | Update `README.md` overview and quick-start |

**Source of truth**: All Tier B content should be derived from Tier A indexes. When writing `docs/api/users.md`, reference the module's `INDEX.md` Public API table rather than re-documenting from scratch.

**AI instruction**: Only execute this checklist when the user explicitly requests "sync docs", "update docs", "iteration end", or similar. Do not proactively update Tier B files during normal development.

## Writing Style for Docs

- **Present tense**: "The server validates input" (not "will validate")
- **Active voice**: "The function returns a session" (not "A session is returned")
- **Second person for guides**: "Run the test suite" (not "One should run")
- **Tables for structured data**: prefer tables over prose lists
- **Code blocks with language tags**: always specify the language
- **No orphan docs**: every doc must be referenced from an INDEX.md
