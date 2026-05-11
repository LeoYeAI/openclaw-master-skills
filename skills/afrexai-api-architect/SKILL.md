---
name: afrexai-api-architect
description: Design, build, test, document, and secure production-grade APIs. Covers the full lifecycle from schema design through deployment, monitoring, and versioning. Use when designing new APIs, reviewing existing ones, generating OpenAPI specs, building test suites, or debugging production issues.
metadata: {"openclaw":{"os":["linux","darwin","win32"]}}
---

# API Architect — Full Lifecycle API Development

Design, build, test, document, secure, and monitor production-grade APIs. Not just curl commands — a complete engineering methodology.

## When to Use

- Designing a new API (REST, GraphQL, or gRPC)
- Reviewing an existing API for quality, consistency, or security
- Generating or validating OpenAPI/Swagger specs
- Building comprehensive test suites (unit, integration, contract, load)
- Debugging production API issues
- Planning API versioning and deprecation
- Setting up monitoring, rate limiting, and error handling

---

## Phase 1: API Design

### Design-First Approach

Always design before coding. The spec IS the contract.

#### Resource Modeling

Map your domain to resources using this template:

```yaml
# api-design.yaml
service: order-management
base_path: /api/v1
resources:
  - name: orders
    path: /orders
    description: Customer purchase orders
    identifier: order_id (UUID)
    parent: null
    operations: [list, create, get, update, cancel]
    sub_resources:
      - name: line_items
        path: /orders/{order_id}/items
        operations: [list, add, update, remove]
      - name: payments
        path: /orders/{order_id}/payments
        operations: [list, create, get, refund]
    states: [draft, confirmed, processing, shipped, delivered, cancelled]
    transitions:
      - from: draft → to: confirmed (action: confirm)
      - from: confirmed → to: processing (action: process)
      - from: processing → to: shipped (action: ship)
      - from: shipped → to: delivered (action: deliver)
      - from: [draft, confirmed] → to: cancelled (action: cancel)
```

#### Naming Conventions Checklist

| Rule | Good | Bad |
|------|------|-----|
| Plural nouns for collections | `/users` | `/user`, `/getUsers` |
| Kebab-case for multi-word | `/line-items` | `/lineItems`, `/line_items` |
| No verbs in URLs | `POST /orders` | `/createOrder` |
| Nest for ownership | `/users/123/orders` | `/orders?user=123` (for primary relationship) |
| Max 3 levels deep | `/users/123/orders` | `/users/123/orders/456/items/789/options` |
| Filter via query params | `/orders?status=active` | `/active-orders` |
| Actions as sub-resource | `POST /orders/123/cancel` | `PATCH /orders/123 {cancelled:true}` |

#### HTTP Methods — Decision Matrix

```
Need to...                          → Method   Idempotent?  Safe?
Get a resource or collection        → GET      Yes          Yes
Create a new resource               → POST     No           No
Full replace of a resource          → PUT      Yes          No
Partial update of a resource        → PATCH    No*          No
Remove a resource                   → DELETE   Yes          No
Check if resource exists            → HEAD     Yes          Yes
List allowed methods                → OPTIONS  Yes          Yes

* PATCH can be idempotent if using JSON Merge Patch
```

#### Status Code Decision Tree

```
Success?
├── Created something new? → 201 Created (Location header)
├── Accepted for async processing? → 202 Accepted (include status URL)
├── No body to return? → 204 No Content
└── Returning data? → 200 OK

Client error?
├── Malformed request syntax? → 400 Bad Request
├── No/invalid credentials? → 401 Unauthorized
├── Valid credentials but insufficient permissions? → 403 Forbidden
├── Resource doesn't exist? → 404 Not Found
├── Method not allowed on resource? → 405 Method Not Allowed
├── Conflict with current state? → 409 Conflict
├── Resource permanently gone? → 410 Gone
├── Validation failed? → 422 Unprocessable Entity
├── Too many requests? → 429 Too Many Requests (Retry-After header)
└── Precondition failed (etag mismatch)? → 412 Precondition Failed

Server error?
├── Unexpected failure? → 500 Internal Server Error
├── Upstream dependency failed? → 502 Bad Gateway
├── Temporarily overloaded? → 503 Service Unavailable (Retry-After)
└── Upstream timeout? → 504 Gateway Timeout
```

### Request/Response Design

#### Standard Response Envelope

```json
// Success (single resource)
{
  "data": { "id": "ord_abc123", "status": "confirmed", ... },
  "meta": { "request_id": "req_xyz789" }
}

// Success (collection)
{
  "data": [ ... ],
  "meta": { "request_id": "req_xyz789" },
  "pagination": {
    "total": 142,
    "page": 2,
    "per_page": 20,
    "total_pages": 8,
    "next": "/api/v1/orders?page=3&per_page=20",
    "prev": "/api/v1/orders?page=1&per_page=20"
  }
}

// Error
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Must be a valid email address", "code": "INVALID_FORMAT" },
      { "field": "age", "message": "Must be at least 18", "code": "MIN_VALUE", "min": 18 }
    ]
  },
  "meta": { "request_id": "req_xyz789" }
}
```

#### Pagination Patterns — When to Use Which

| Pattern | Use When | Pros | Cons |
|---------|----------|------|------|
| **Offset** `?page=2&per_page=20` | Simple UI pagination, small datasets | Easy to implement, page jumping | Drift on inserts, slow on large offsets |
| **Cursor** `?after=eyJ...&limit=20` | Infinite scroll, real-time feeds, large datasets | Consistent, performant | No page jumping, opaque cursors |
| **Keyset** `?created_after=2024-01-01&limit=20` | Time-series data, logs | Fast, transparent | Requires sortable field, no count |

#### Filtering, Sorting, Field Selection

```
# Filtering
GET /orders?status=active&created_after=2024-01-01&total_min=100

# Sorting (prefix - for descending)
GET /orders?sort=-created_at,total

# Field selection (reduce payload)
GET /orders?fields=id,status,total,customer.name

# Search
GET /products?q=wireless+headphones

# Combined
GET /orders?status=active&sort=-created_at&fields=id,status,total&page=1&per_page=10
```

---

## Phase 2: OpenAPI Specification

### Generate OpenAPI 3.1 Spec

For each resource in your design, generate a complete spec:

```yaml
openapi: 3.1.0
info:
  title: Order Management API
  version: 1.0.0
  description: |
    Order lifecycle management.
    
    ## Authentication
    All endpoints require Bearer token authentication.
    
    ## Rate Limits
    - Standard: 100 req/min
    - Bulk operations: 10 req/min
  contact:
    name: API Support
    email: api@example.com
  license:
    name: MIT
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging

paths:
  /orders:
    get:
      operationId: listOrders
      summary: List orders
      tags: [Orders]
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PerPageParam'
        - name: status
          in: query
          schema:
            $ref: '#/components/schemas/OrderStatus'
        - name: created_after
          in: query
          schema:
            type: string
            format: date-time
      responses:
        '200':
          description: Order list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      operationId: createOrder
      summary: Create an order
      tags: [Orders]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
            examples:
              basic:
                summary: Basic order
                value:
                  customer_id: "cust_abc"
                  items:
                    - product_id: "prod_xyz"
                      quantity: 2
      responses:
        '201':
          description: Order created
          headers:
            Location:
              schema:
                type: string
              description: URL of created order
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderResponse'
        '422':
          $ref: '#/components/responses/ValidationError'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  parameters:
    PageParam:
      name: page
      in: query
      schema: { type: integer, minimum: 1, default: 1 }
    PerPageParam:
      name: per_page
      in: query
      schema: { type: integer, minimum: 1, maximum: 100, default: 20 }

  responses:
    Unauthorized:
      description: Missing or invalid authentication
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    ValidationError:
      description: Request validation failed
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'

security:
  - BearerAuth: []
```

### Spec Quality Checklist (score each 0-2)

| # | Check | Score |
|---|-------|-------|
| 1 | Every endpoint has operationId | /2 |
| 2 | All parameters documented with types + constraints | /2 |
| 3 | Request bodies have examples | /2 |
| 4 | All error responses documented (400, 401, 403, 404, 422, 429, 500) | /2 |
| 5 | Shared schemas use $ref (DRY) | /2 |
| 6 | Pagination parameters standardized | /2 |
| 7 | Security scheme defined + applied globally | /2 |
| 8 | Description includes auth, rate limits, versioning info | /2 |
| 9 | Response headers documented (Location, Retry-After, ETag) | /2 |
| 10 | Enums used for fixed value sets | /2 |

**Score: ___/20** (Target: 16+)

---

## Phase 3: Implementation Patterns

### Request Validation Layer

Every endpoint MUST validate before processing:

```
Validation Order:
1. Content-Type header (reject non-JSON early)
2. Authentication (401 before wasting cycles)
3. Authorization (403 - does this user have access?)
4. Path parameters (404 - does the resource exist?)
5. Query parameters (400 - valid types/ranges?)
6. Request body schema (422 - valid structure?)
7. Business rules (422 - valid state transition?)
```

### Error Handling — Standard Error Codes

Define a consistent error code enum for your API:

```
# Authentication & Authorization
AUTH_REQUIRED          — No credentials provided
AUTH_INVALID           — Invalid/expired credentials
AUTH_INSUFFICIENT      — Valid credentials, wrong permissions
AUTH_RATE_LIMITED       — Too many auth attempts

# Validation
VALIDATION_FAILED      — Generic validation error (see details array)
INVALID_FORMAT         — Field format wrong (email, UUID, etc.)
REQUIRED_FIELD         — Required field missing
OUT_OF_RANGE           — Value outside allowed range
INVALID_ENUM           — Value not in allowed set

# Resource
NOT_FOUND              — Resource doesn't exist
ALREADY_EXISTS         — Duplicate (unique constraint)
CONFLICT               — State conflict (e.g., already cancelled)
GONE                   — Resource permanently deleted

# Business Logic
INSUFFICIENT_FUNDS     — Payment-related
QUOTA_EXCEEDED         — Usage limit reached
FEATURE_DISABLED       — Feature flag off
DEPENDENCY_FAILED      — Upstream service error

# System
INTERNAL_ERROR         — Unexpected server error
SERVICE_UNAVAILABLE    — Temporarily down
TIMEOUT                — Request took too long
```

### Idempotency

For non-idempotent operations (POST), require an idempotency key:

```
Request:
POST /orders
Idempotency-Key: ord_req_abc123

Server behavior:
1. Check if Idempotency-Key was seen before
2. If yes → return cached response (same status, same body)
3. If no → process request, cache response for 24h
4. Key format: client-generated UUID or meaningful string
```

### Rate Limiting

Standard headers to include:

```
X-RateLimit-Limit: 100          # Max requests per window
X-RateLimit-Remaining: 67       # Remaining in current window
X-RateLimit-Reset: 1706886400   # Unix timestamp when window resets
Retry-After: 30                 # Seconds to wait (on 429)
```

Rate limit tiers:

| Tier | Limit | Window | Use Case |
|------|-------|--------|----------|
| Standard | 100/min | Sliding | Normal API calls |
| Bulk | 10/min | Sliding | Batch operations |
| Search | 30/min | Sliding | Full-text search |
| Auth | 5/min | Fixed | Login attempts |
| Webhook | 1000/min | Sliding | Incoming webhooks |

---

## Phase 4: Testing Strategy

### Test Pyramid for APIs

```
        /  E2E  \          — 5-10 critical user flows
       / Contract \        — Schema validation, backward compat
      / Integration \      — Database, external services, auth
     /    Unit Tests  \    — Business logic, validation, transforms
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
```

### Test Checklist Per Endpoint

For EVERY endpoint, test these scenarios:

```yaml
endpoint: POST /orders
tests:
  happy_path:
    - Creates order with valid data → 201
    - Returns created resource with ID
    - Location header points to new resource
    - Timestamps are set (created_at, updated_at)
  
  validation:
    - Missing required fields → 422 with field-level errors
    - Invalid field types (string where int expected) → 422
    - Empty body → 400
    - Invalid Content-Type → 415
    - Extra unknown fields → ignored or 422 (pick one, be consistent)
    - Boundary values (min/max length, 0, negative, empty string vs null)
  
  authentication:
    - No token → 401
    - Expired token → 401
    - Invalid token → 401
    - Valid token, wrong scope → 403
  
  authorization:
    - User accessing own resource → 200
    - User accessing other's resource → 403 or 404 (security choice)
    - Admin accessing any resource → 200
  
  edge_cases:
    - Duplicate creation (same idempotency key) → same 201 response
    - Concurrent creation race condition → one wins, one gets 409
    - Resource at max relationships → 422
    - Unicode in text fields → handled correctly
    - Very long strings → 422 with max length error
    - SQL injection in params → no effect (parameterized queries)
    - XSS in text fields → stored safely, escaped on output
  
  performance:
    - Response time < 200ms (p95)
    - List endpoint with 10K records → paginated, < 500ms
    - Bulk operation timeout handling
```

### curl Testing Recipes

```bash
# === Setup ===
BASE="https://api.example.com/v1"
TOKEN="your_bearer_token"
alias api='curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json"'

# === CRUD Lifecycle Test ===
# Create
ORDER=$(api -X POST "$BASE/orders" -d '{"customer_id":"cust_1","items":[{"product_id":"prod_1","qty":2}]}')
ORDER_ID=$(echo "$ORDER" | jq -r '.data.id')
echo "Created: $ORDER_ID"

# Read
api "$BASE/orders/$ORDER_ID" | jq .

# Update
api -X PATCH "$BASE/orders/$ORDER_ID" -d '{"notes":"Rush order"}' | jq .

# List with filters
api "$BASE/orders?status=draft&sort=-created_at&per_page=5" | jq .

# Action (state transition)
api -X POST "$BASE/orders/$ORDER_ID/confirm" | jq .

# Delete
curl -s -o /dev/null -w "%{http_code}" -X DELETE -H "Authorization: Bearer $TOKEN" "$BASE/orders/$ORDER_ID"

# === Error Testing ===
# No auth
curl -s "$BASE/orders" | jq .error

# Invalid body
api -X POST "$BASE/orders" -d '{"invalid": true}' | jq .error

# Not found
api "$BASE/orders/nonexistent" | jq .error

# === Performance ===
# Timing breakdown
curl -s -o /dev/null -w "DNS:%{time_namelookup} TCP:%{time_connect} TLS:%{time_appconnect} TTFB:%{time_starttransfer} Total:%{time_total}\n" -H "Authorization: Bearer $TOKEN" "$BASE/orders"

# Quick load test (50 requests, 10 concurrent)
seq 50 | xargs -P10 -I{} curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" -H "Authorization: Bearer $TOKEN" "$BASE/orders"
```

### Contract Testing

Validate your API hasn't broken backward compatibility:

```yaml
# contract-tests.yaml
contract:
  name: Order API Contract
  version: 1.0.0
  
  rules:
    # These changes are SAFE (non-breaking)
    safe:
      - Adding new optional fields to responses
      - Adding new endpoints
      - Adding new optional query parameters
      - Adding new enum values (if clients handle unknown)
      - Widening a constraint (min: 5 → min: 1)
    
    # These changes are BREAKING
    breaking:
      - Removing a response field
      - Renaming a response field
      - Changing a field type
      - Adding a new required request field
      - Removing an endpoint
      - Narrowing a constraint (max: 100 → max: 50)
      - Changing error response format
      - Removing an enum value
    
    # Verify after every change
    checks:
      - All existing fields still present in responses
      - All existing field types unchanged
      - All existing required fields still required (no more, no fewer)
      - Default values unchanged
      - Error format unchanged
```

---

## Phase 5: Security

### Security Checklist (audit every API)

```yaml
authentication:
  - [ ] All endpoints require auth (except /health, /docs, public webhooks)
  - [ ] Tokens expire (short-lived access + long-lived refresh)
  - [ ] Token rotation supported
  - [ ] Failed auth returns 401 with no info leakage
  - [ ] API keys are hashed in storage (never plain text)

authorization:
  - [ ] Resource-level checks (user can only access their data)
  - [ ] Endpoint-level checks (role-based access)
  - [ ] No IDOR vulnerabilities (can't guess other users' resource IDs)
  - [ ] Admin endpoints separately protected
  - [ ] Webhook endpoints verify signatures

input_validation:
  - [ ] All inputs validated server-side (never trust client)
  - [ ] SQL injection prevented (parameterized queries only)
  - [ ] NoSQL injection prevented
  - [ ] Path traversal prevented
  - [ ] Request size limited (body, headers, URL length)
  - [ ] File upload types restricted and scanned

output_security:
  - [ ] No sensitive data in responses (passwords, tokens, internal IDs)
  - [ ] No stack traces in production errors
  - [ ] Consistent error format (no info leakage in different error types)
  - [ ] PII redacted in logs

transport:
  - [ ] HTTPS only (HTTP redirects to HTTPS)
  - [ ] HSTS header set
  - [ ] TLS 1.2+ required
  - [ ] CORS configured restrictively (specific origins, not *)
  
headers:
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: DENY
  - [ ] Content-Security-Policy set
  - [ ] No Server version header
  - [ ] Cache-Control: no-store for sensitive endpoints
```

### CORS Configuration

```yaml
# Restrictive (recommended)
cors:
  origins:
    - https://app.example.com
    - https://admin.example.com
  methods: [GET, POST, PUT, PATCH, DELETE]
  headers: [Authorization, Content-Type, X-Request-ID]
  credentials: true
  max_age: 3600

# Common mistakes to avoid:
# ❌ Access-Control-Allow-Origin: *  (with credentials)
# ❌ Reflecting Origin header without validation
# ❌ Allowing all methods/headers
```

---

## Phase 6: Versioning & Deprecation

### Versioning Strategy Decision

| Strategy | Example | Pros | Cons | Use When |
|----------|---------|------|------|----------|
| **URL path** | `/v1/orders` | Explicit, easy routing | URL pollution | Public APIs, multiple major versions |
| **Header** | `API-Version: 2024-01` | Clean URLs | Hidden, harder to test | Internal APIs |
| **Query param** | `?version=2` | Easy to test | Pollutes params | Quick prototypes |
| **Date-based** | `2024-01-15` | Clear timeline | Many versions | Stripe-style APIs |

**Recommended**: URL path for major versions, header for minor variations.

### Deprecation Playbook

```
Timeline:
1. T+0: Announce deprecation (docs, changelog, email)
2. T+0: Add Deprecation + Sunset headers to old endpoints
3. T+30d: Log warnings for old endpoint usage
4. T+60d: Email heavy users of old endpoint directly
5. T+90d: Return 299 warning header
6. T+180d: Shut down old endpoint (410 Gone)

Headers:
Deprecation: true
Sunset: Sat, 01 Jun 2025 00:00:00 GMT
Link: <https://api.example.com/v2/orders>; rel="successor-version"
```

### Migration Guide Template

```markdown
# Migrating from v1 to v2

## Breaking Changes
1. `user.name` split into `user.first_name` + `user.last_name`
2. Pagination changed from offset to cursor-based
3. Error format updated (see new schema)

## Step-by-Step Migration
1. Update your client SDK to v2 (`npm install @example/sdk@2`)
2. Update response parsing for split name fields
3. Replace `?page=N` with `?after=cursor` pagination
4. Update error handling for new error format

## Compatibility Mode
Set `X-Compat-Mode: v1` header to get v1-style responses from v2 endpoints.
Available until 2025-06-01.
```

---

## Phase 7: Monitoring & Observability

### Key Metrics Dashboard

```yaml
availability:
  - Uptime percentage (target: 99.9% = 8.7h downtime/year)
  - Health check status (/health endpoint)
  - Error rate (5xx / total requests)

performance:
  - p50 latency (target: < 100ms)
  - p95 latency (target: < 500ms)
  - p99 latency (target: < 1000ms)
  - Throughput (requests/second)
  - Time to first byte (TTFB)

business:
  - Requests per endpoint (usage patterns)
  - Unique API consumers/day
  - Error rate by endpoint
  - Rate limit hits/day
  - Authentication failures/day

infrastructure:
  - Database query time (p95)
  - Connection pool utilization
  - Memory/CPU per instance
  - Queue depth (async operations)
```

### Structured Logging

Every request should log:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "info",
  "request_id": "req_abc123",
  "method": "POST",
  "path": "/api/v1/orders",
  "status": 201,
  "duration_ms": 45,
  "user_id": "usr_xyz",
  "ip": "203.0.113.1",
  "user_agent": "MyApp/2.0",
  "request_size": 256,
  "response_size": 1024
}
```

### Health Check Endpoint

```json
// GET /health — for load balancers (simple)
{ "status": "ok" }

// GET /health/detailed — for monitoring (authenticated)
{
  "status": "degraded",
  "version": "1.5.2",
  "uptime_seconds": 86400,
  "checks": {
    "database": { "status": "ok", "latency_ms": 5 },
    "redis": { "status": "ok", "latency_ms": 2 },
    "external_payment_api": { "status": "degraded", "latency_ms": 2500, "error": "timeout" },
    "disk": { "status": "ok", "free_gb": 45.2 }
  }
}
```

---

## Phase 8: API Review Scoring

When reviewing an existing API, score across these dimensions:

### API Quality Rubric (0-100)

| Dimension | Weight | Criteria | Score |
|-----------|--------|----------|-------|
| **Design Consistency** | 20% | Naming conventions, HTTP methods, status codes, URL structure | /20 |
| **Documentation** | 15% | OpenAPI spec, examples, error docs, changelog | /15 |
| **Error Handling** | 15% | Consistent format, helpful messages, proper codes, no leakage | /15 |
| **Security** | 20% | Auth, input validation, CORS, headers, no IDOR | /20 |
| **Performance** | 15% | Latency targets met, pagination, caching headers, N+1 prevented | /15 |
| **Developer Experience** | 15% | SDK quality, sandbox available, onboarding time, rate limit clarity | /15 |

**Score: ___/100**

| Rating | Score | Action |
|--------|-------|--------|
| 🟢 Excellent | 85-100 | Minor improvements only |
| 🟡 Good | 70-84 | Address gaps before next major release |
| 🟠 Needs Work | 50-69 | Prioritize improvements, create tech debt tickets |
| 🔴 Critical | <50 | Stop feature work, fix fundamentals first |

### Review Output Template

```markdown
## API Review: [Service Name]

**Date:** YYYY-MM-DD
**Reviewer:** [Agent]
**Score:** XX/100 (Rating)

### Summary
[2-3 sentence overview of API quality]

### Scores by Dimension
- Design Consistency: X/20 — [key finding]
- Documentation: X/15 — [key finding]
- Error Handling: X/15 — [key finding]
- Security: X/20 — [key finding]
- Performance: X/15 — [key finding]
- Developer Experience: X/15 — [key finding]

### Critical Issues (fix immediately)
1. [Issue + recommendation]

### High Priority (fix this sprint)
1. [Issue + recommendation]

### Nice to Have (backlog)
1. [Issue + recommendation]

### Positive Highlights
- [What's working well]
```

---

## GraphQL-Specific Guidance

### Schema Design Principles

```graphql
# Good: clear types, nullable where appropriate, connections for lists
type Order {
  id: ID!
  status: OrderStatus!
  customer: Customer!
  items(first: Int, after: String): ItemConnection!
  total: Money!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Money {
  amount: Int!       # cents, not dollars (avoid float)
  currency: Currency!
}

enum OrderStatus {
  DRAFT
  CONFIRMED
  PROCESSING
  SHIPPED
  DELIVERED
  CANCELLED
}

# Mutations return the modified resource + errors
type CreateOrderPayload {
  order: Order
  errors: [UserError!]!
}

type UserError {
  field: [String!]
  message: String!
  code: ErrorCode!
}
```

### GraphQL Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No depth limit | Query bombs | Limit depth to 5-7 levels |
| No complexity limit | Expensive queries | Assign cost per field, cap at 1000 |
| N+1 queries | Performance death | Use DataLoader pattern |
| No persisted queries | Security risk | Whitelist queries in production |
| Exposing internal IDs | Leaks implementation | Use opaque global IDs |
| No pagination | Memory explosion | Use Relay Connection spec |

---

## Edge Cases & Gotchas

### Timezone Handling
- Always store and return UTC (ISO 8601: `2024-01-15T10:30:00Z`)
- Accept timezone in input, convert to UTC immediately
- Never use local server time

### Large Payloads
- Set `Content-Length` limits (e.g., 1MB default, 10MB for uploads)
- Use streaming for file uploads (multipart/form-data)
- Compress responses (Accept-Encoding: gzip)
- For very large exports → return 202 + poll status endpoint

### Eventual Consistency
- If using async processing, always return 202 + status URL
- Include estimated completion time when possible
- Client should poll with exponential backoff

### Concurrent Updates
- Use ETags for optimistic concurrency:
  - GET returns `ETag: "v1"` header
  - PUT/PATCH sends `If-Match: "v1"` header
  - Server returns 412 if resource changed since

### Webhook Design
- Include event type, timestamp, and full resource in payload
- Sign payloads (HMAC-SHA256)
- Expect retries (make handlers idempotent)
- Return 200 quickly, process async
- Include webhook ID for deduplication

---

## Quick Commands

| Request | Action |
|---------|--------|
| "Design an API for [domain]" | Run Phase 1 resource modeling + naming |
| "Generate OpenAPI spec" | Run Phase 2 with full components |
| "Review this API" | Run Phase 8 scoring rubric |
| "Write tests for [endpoint]" | Run Phase 4 endpoint checklist |
| "Security audit this API" | Run Phase 5 security checklist |
| "How should I version this?" | Run Phase 6 decision matrix |
| "Debug this API issue" | Check Phase 7 logging + health patterns |
| "Design GraphQL schema for [domain]" | Run GraphQL section |
