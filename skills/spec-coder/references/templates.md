# Spec Coding — Core Templates

Templates for the primary spec artifacts produced during Phase 1–3. Use as starting points — adapt to the project's needs.

For lifecycle and review templates (index.md, change spec, delta.md, status.md, expert review output), see [templates-lifecycle.md](templates-lifecycle.md).

---

## requirements.md Template

```markdown
# Requirements: [Project/Feature Name]

## Changelog
| Date | Change | Reason |
|------|--------|--------|

## Background & Objectives

[Why this project exists. 2-3 sentences.]

## User Roles

| Role | Description |
|------|-------------|
| Admin | Manages system configuration and users |
| End User | Primary consumer of the feature |

## Use Cases

### UC-001: [Use Case Name]
**Actor:** [Role]
**Precondition:** [What must be true before]
**Flow:** [Step-by-step happy path]
**Postcondition:** [What is true after]

## Functional Requirements

### Module: [Module Name]

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | [Description] | Must |
| FR-002 | [Description] | Should |

### Module: [Module Name]

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-003 | [Description] | Must |

## Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | API response < 200ms p95 |
| NFR-002 | Security | All endpoints require authentication |
| NFR-003 | Availability | 99.9% uptime SLA |

## Existing Architecture (if applicable)

[Summary of relevant existing systems, interfaces, and conventions that this feature must integrate with.]

## Out of Scope

- [Explicitly list what will NOT be built]
- [Be specific to avoid scope creep]
```

---

## design.md Template

```markdown
# Technical Design: [Project/Feature Name]

## Changelog
| Date | Change | Reason |
|------|--------|--------|

## Architecture Overview

[Diagram description or text overview: monolith/microservices, frontend/backend split, tech stack.]

**Tech Stack:**
- Language: [e.g., TypeScript]
- Framework: [e.g., Express.js]
- Database: [e.g., PostgreSQL]
- Other: [e.g., Redis for caching]

## Module Breakdown

### [Module Name]
**Responsibility:** [What this module does]
**Key interfaces:** [Public API surface]
**Dependencies:** [Other modules it depends on]

## Data Models

### [Entity Name]
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | Auto-generated |
| name | string | NOT NULL, max 255 | |
| created_at | timestamp | NOT NULL | Default: now() |

## Key Interfaces

### [Interface Name]
**Direction:** [e.g., REST API, internal function call]
**Caller → Callee:** [Module A → Module B]

[Brief sequence description]

## Cross-Cutting Concerns

### Error Handling
- **Classification:** Client errors (4xx) / Server errors (5xx) / Domain errors
- **Propagation:** [How errors flow across module boundaries]
- **Retry policy:** [Which operations are retryable, backoff strategy]
- **Error response format:**
  ```json
  { "error": { "code": "ERROR_CODE", "message": "Human-readable message" } }
  ```

### Authentication & Authorization
- **Mechanism:** [JWT / OAuth2 / API Key]
- **Authorization model:** [RBAC / ABAC / per-resource]
- **Token lifecycle:** [Issuance, refresh, revocation]

### Observability
- **Logging:** [Structured JSON, log levels, sensitive data redaction]
- **Metrics:** [Key metrics to expose, collection method]
- **Tracing:** [Correlation ID strategy, distributed tracing]

### Deployment & Configuration
- **Topology:** [Single instance / multi-replica / serverless]
- **Configuration:** [Env vars / config files / secrets manager]
- **Data migration:** [Migration tool, versioning strategy]

## NFR Fulfillment Matrix

| NFR ID | Requirement | Design Response | Verification Method |
|--------|-------------|-----------------|---------------------|
| NFR-001 | API response < 200ms p95 | Redis caching + connection pooling | Load test with k6 |
| NFR-002 | All endpoints require auth | JWT middleware on all routes | Auth integration tests |

## Architecture Decisions

### ADR-001: [Decision Title]
- **Context:** [What situation requires a decision]
- **Options:** [Option A / Option B / Option C]
- **Decision:** [Which option was chosen]
- **Consequences:** [Trade-offs and follow-up actions]

## Tech Choices & Trade-offs

| Decision | Chosen | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Database | PostgreSQL | MongoDB | Relational data, ACID needed |
| Cache | Redis | In-memory | Shared across instances |

## Existing Architecture (if applicable)

### What exists
[Current system description]

### What's new
[New components being added]

### What's modified
[Existing components being changed]
```

---

## tasks.md Template

```markdown
# Task Breakdown: [Project/Feature Name]

## Changelog
| Date | Change | Reason |
|------|--------|--------|

## Tasks

| Task ID | Name | Module | Deps | Related Spec | Acceptance Criteria | AI-Auto | Status |
|---------|------|--------|------|--------------|---------------------|---------|--------|
| TASK-001 | Set up project structure | Infra | — | — | Project builds and runs | Yes | Pending |
| TASK-002 | Implement User model | Auth | TASK-001 | spec_auth.md | User CRUD passes all TPs | Yes | Pending |
| TASK-003 | Add authentication API | Auth | TASK-002 | spec_auth.md | Login/logout flows work | Yes | Pending |
| TASK-004 | Integrate with external payment API | Payment | TASK-001 | spec_payment.md | Manual testing required | No | Pending |

Status values: `Pending` | `In Progress` | `Done` | `Blocked [reason]`
Update Status as each task progresses through Phase 3.
```

---

## spec_xxx.md Template

```markdown
# Spec: [Feature Name]

## Changelog
| Date | Change | Reason |
|------|--------|--------|

## Feature Description

[What this feature does, in 2-3 sentences.]

## Use Cases

- UC-001: [Brief description]
- UC-002: [Brief description]

## Interface Definition

### [Endpoint / Function Name]

- **Type:** REST API / CLI / Internal function
- **Path:** `POST /api/v1/users`
- **Auth:** Required (Bearer token)

**Request:**
| Param | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| email | string | Yes | Valid email format | User's email |
| name | string | Yes | 1-255 chars | Display name |

**Response (201 Created):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**
| Status | Code | Condition |
|--------|------|-----------|
| 400 | INVALID_EMAIL | Email format invalid |
| 409 | EMAIL_EXISTS | Email already registered |
| 500 | INTERNAL_ERROR | Unexpected server error |

## Data Model

### User
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | Auto-generated |
| email | string | UNIQUE, NOT NULL | |
| name | string | NOT NULL, max 255 | |
| created_at | timestamp | NOT NULL | Default: now() |

## Business Rules

1. Email must be unique across all users (case-insensitive).
2. Name must be trimmed of leading/trailing whitespace before storage.
3. [Add more rules...]

## Test Points

| TP-ID | Category | Input | Expected Output | Notes |
|-------|----------|-------|-----------------|-------|
| TP-001 | Normal | `{"email":"a@b.com","name":"Alice"}` | 201, user object returned | |
| TP-002 | Normal | `{"email":"A@B.COM","name":"Bob"}` | 201, email stored lowercase | |
| TP-003 | Error | `{"name":"Alice"}` (no email) | 400, INVALID_EMAIL | |
| TP-004 | Error | `{"email":"not-an-email","name":"X"}` | 400, INVALID_EMAIL | |
| TP-005 | Error | duplicate email | 409, EMAIL_EXISTS | |
| TP-006 | Boundary | name = 255 chars | 201, accepted | Max length |
| TP-007 | Boundary | name = 256 chars | 400, validation error | Over max |
| TP-008 | Boundary | name = " Alice " | 201, name stored as "Alice" | Trimming |

## Implementation Map

Updated after Phase 4 (Verify) passes. Enables reverse lookup from spec to code.

| Spec Item | Code File(s) | Function / Class | Notes |
|-----------|-------------|-----------------|-------|
| Interface: POST /api/v1/users | src/routes/users.ts | createUser() | |
| Data Model: User | src/models/user.ts | User class | |
| BR-1: Email uniqueness | src/services/user-service.ts | validateEmail() | Case-insensitive check |
| BR-2: Name trimming | src/services/user-service.ts | normalizeUser() | |
```

---

## Combination Test Point Examples

For complex features, include Combination-category test points that test multiple conditions together:

```markdown
| TP-ID | Category | Input | Expected Output | Notes |
|-------|----------|-------|-----------------|-------|
| TP-010 | Combination | Admin user + expired token + valid payload | 401 Unauthorized | Auth takes precedence over valid payload |
| TP-011 | Combination | Valid user + rate limit exceeded + valid payload | 429 Too Many Requests | Rate limit takes precedence |
| TP-012 | Combination | Concurrent duplicate create requests | One 201 + one 409 | Race condition handling |
| TP-013 | Combination | Bulk import with mix of valid/invalid rows | Partial success with error report | Transactional vs. best-effort |
```

---

## Non-API Test Point Examples

For CLI tools, event-driven systems, UI interactions, and batch processes:

```markdown
| TP-ID | Category | Input | Expected Output | Notes |
|-------|----------|-------|-----------------|-------|
| TP-020 | Normal (CLI) | `mycli export --format csv --output out.csv` | Exit code 0, out.csv with correct headers and rows | |
| TP-021 | Error (CLI) | `mycli export --format xml` (unsupported format) | Exit code 1, stderr: "Unsupported format: xml" | |
| TP-022 | Normal (Event) | Publish `OrderCreated` event with valid payload | `InventoryReserved` event emitted within 5s, stock decremented | Async — verify via event log or poll |
| TP-023 | Error (Event) | Publish `OrderCreated` with insufficient stock | `ReservationFailed` event emitted, order status set to "pending_stock" | Dead-letter handling |
| TP-024 | Normal (UI) | Click "Save" with all required fields filled | Form submits, success toast appears, redirect to list view | |
| TP-025 | Error (UI) | Click "Save" with empty required field | Inline validation error shown on the empty field, form not submitted | |
| TP-026 | Normal (Batch) | Run nightly sync with 10,000 records | All records processed, summary log shows 10,000 success / 0 error | Runtime < 5 min |
| TP-027 | Error (Batch) | Run sync with 3 malformed records in 10,000 | 9,997 success, 3 errors logged with row IDs, job completes (no abort) | Partial failure tolerance |
```

---

## Small Track Walk-Through Example

A complete example of the Small track: adding a "health check" endpoint to an existing API.

**Step 1 — Write lite spec** (skip Phase 1, go straight to spec):

```markdown
# Spec: Health Check Endpoint

## Feature Description
A lightweight endpoint that reports service health, used by load balancers and monitoring.

## Interface Definition

### GET /api/v1/health

- **Type:** REST API
- **Auth:** None (public)

**Response (200 OK):**
{ "status": "ok", "version": "1.2.0", "uptime_seconds": 3600 }

**Response (503 Service Unavailable):**
{ "status": "degraded", "checks": { "database": "unreachable" } }

## Business Rules

1. Returns 200 if all dependency checks pass (database connection, cache connection).
2. Returns 503 if any critical dependency is unreachable. Non-critical failures still return 200.
3. Version string is read from package.json / build metadata at startup, not on every request.

## Test Points

| TP-ID | Category | Input | Expected Output | Notes |
|-------|----------|-------|-----------------|-------|
| TP-001 | Normal | GET /api/v1/health (all deps up) | 200, status=ok, version present | |
| TP-002 | Error | GET /api/v1/health (DB down) | 503, status=degraded, checks.database=unreachable | |
| TP-003 | Error | GET /api/v1/health (cache down, DB up) | 200, status=ok | Cache is non-critical |
| TP-004 | Boundary | GET /api/v1/health (server just started) | 200, uptime_seconds=0 or small positive | |
| TP-005 | Normal | GET /api/v1/health with Authorization header | 200, header ignored | Auth not required |

## Implementation Map

| Spec Item | Code File(s) | Function / Class | Notes |
|-----------|-------------|-----------------|-------|
| (filled after Phase 4) | | | |
```

**Step 2 — Generate** (Phase 3): Implement the endpoint + tests based on spec above. One commit: `feat(TASK-health): add health check endpoint`.

**Step 3 — Verify** (Phase 4): Run tests, map TP-001–005 to pass/fail, update Implementation Map.

**Done.** No requirements.md, no design.md, no tasks.md, no review gates (Small track, trivial scope).
