# Cross-Surface Regression Checklist

When fixing a bug in one "surface" (e.g. an API endpoint or settings page), regressions are often introduced in other surfaces that share the same **contract**, **data**, or **behavior**.

This checklist helps you find and verify *all* affected consumers so the fix can ship in one go with lower risk.

> **Related**: 
> - For full consumer list and invariant templates, see `scope-accuracy-protocol.md`.
> - For multi-layer/cross-process bugs, see `system-rca-track.md`.

---

## 🔴 Scope Accuracy Gate (MANDATORY)

These gates must be satisfied before fixing:

| Gate | Requirement | Template |
|------|------------|---------|
| **Consumer List** | List all consumers | See Step 2 below |
| **Contract List** | List the behaviors/interfaces being modified | `scope-accuracy-protocol.md` |
| **Invariant Check** | List what must remain true after the fix | `scope-accuracy-protocol.md` |
| **Regression Matrix** | Define verification for each consumer | See Step 3 below |

---

## When to Use

Use this checklist when the fix involves any shared artifact:

- API response/request schema
- Database models/data structures
- Shared config (feature flags, provider lists, routing rules)
- Shared UI components or domain hooks/stores
- Shared cache keys/pagination/sorting rules
- "List of things" used across multiple surfaces (settings, runtime selection, admin views, etc.)

## Definitions

- **Surface**: Any user-visible or system-visible touchpoint (UI page, API endpoint, background task, CLI, integration).
- **Contract**: The expectation connecting a producer and consumer (types, schema, invariants, default behavior).
- **Consumer List**: A complete inventory of all locations that depend on the same contract/data.

## Step 1 — Identify Shared Contract/Data

Write down explicitly (1-3 sentences):

- What changed? (field names, endpoint behavior, allowed values, sorting, auth, error structure)
- What must remain stable? (backward compat constraints)
- What is the "source of truth"? (API, database, config file, derived cache)

## Step 2 — Build Consumer List (KEY STEP)

List every consumer that reads/derives from the same contract/data.

- **UI consumers**
  - List views
  - Detail views
  - Settings/config pages
  - Select dropdowns/pickers/modals
  - Export/download flows
- **API consumers**
  - Public endpoints
  - Internal services/clients
  - SDK calls (if any)
- **Background consumers**
  - Tasks/jobs/cron
  - Async pipelines (analytics, indexing, etc.)
- **Ops consumers**
  - Admin dashboards
  - Metrics/alerts/log parsers
  - Migrations/backfills

### Consumer List Template

Fill in the following table:

| Consumer | Surface Type | Entry Point | What It Uses | Risk Level | Verification |
|----------|-------------|-------------|-------------|-----------|-------------|
| UI: Selector | UI | Route → Control | Reads list, filters by status | High | Manual + unit test |
| API: Status endpoint | API | GET /… | Returns updated field | High | Contract test |
| Background analyzer | Task | Task name | Expects enum values | Medium | Integration smoke test |

If you modified a method/class that multiple consumers call (shared utility, shared component),
also follow: `caller-impact-protocol.md`

## Step 3 — Define Minimal Regression Matrix Per Consumer

For each **high-risk** consumer, verify the minimal set of cases that catches 80% of regressions:

- **Normal flow**: Typical request with typical data
- **Empty state**: No items/no results
- **Pagination**: First page vs subsequent pages (if applicable)
- **Sorting**: Default sort and one explicit sort param (if applicable)
- **Filtering**: Most common filter path (if applicable)
- **Permissions**: Allowed vs forbidden user/role (if applicable)
- **Error structure**: One representative error should still be actionable and consistent

## Step 4 — Check Cross-Surface Invariants

These are common sources of "looks fine here, breaks there":

- **Field naming drift**: One surface uses `analysis_status`, another expects `status`
- **Default values**: Missing field vs explicit `null` vs omitted key
- **Compat fallbacks**: Legacy fields overwriting new mappings
- **Caching**: Stale cache keys; different TTLs; inconsistent invalidation triggers
- **Feature flags**: Enabled in one surface but not another
- **Versioned base URLs**: `/v1` vs `/v4`; unexpected double-prefix

## Step 5 — Add Minimal Automated Guard

Choose one (or more) that best fits the contract:

- **Contract test**: Assert response structure and key invariants across versions
- **Unit test**: URL builder, mapper, parsing logic, fallbacks
- **Integration smoke test**: Key path end-to-end for the shared contract

Rule of thumb: If the bug involved a **mapping/fallback**, add a unit test that pins the mapping behavior.

## Similar Bug Search (RECOMMENDED)

After fixing, search for the same pattern elsewhere:

- URL construction patterns (e.g. `/v1` concatenation, trailing slashes)
- Field fallback logic (legacy vs new config)
- Consumer parsing assumptions (list vs dict, optional vs required)

Example search hints (adjust to repo conventions):

- `"legacy" AND "fallback" AND "<field_name>"`
- `"base_url" AND "v1" AND "join"`
- `"model_map" OR "mapping" OR "selector"`
- `"analysis_status" AND ("list" OR "dropdown" OR "picker")`

## Definition of Done (Cross-Surface)

You are NOT "done" until:

- Every **high-risk consumer** in the list has a documented pass/fail result
- At least one **automated guard** exists at the root cause (or a justified exception)
- The fix does not introduce new inconsistencies between list/detail/settings/selection surfaces

---

## Universal Invariant Checklist

When modifying shared artifacts, verify these common invariants:

### API Invariants

| Invariant | Check |
|-----------|-------|
| Response structure never removes fields | Schema diff shows no removals |
| Error codes maintain same semantics | Error handling code review |
| Status codes consistent | No new status codes for same conditions |
| Pagination contract stable | Cursor/offset behavior unchanged |

### State Invariants

| Invariant | Check |
|-----------|-------|
| State transitions valid | No orphan states, no impossible transitions |
| Loading → Success/Error maintained | UI doesn't crash during transitions |
| Optimistic updates rollback on error | Error handling restores previous state |

### Routing Invariants

| Invariant | Check |
|-----------|-------|
| Session routing consistent | Same session ID → same instance |
| Request routing deterministic | Same request → same handler |
| Feature flags respected | Disabled features stay disabled |

### Cache Invariants

| Invariant | Check |
|-----------|-------|
| Idempotent operations cacheable | GET requests can be cached |
| Side-effect operations not cached | POST/PUT/DELETE bypass cache |
| Cache invalidation triggered | Mutations invalidate relevant cache |

### Security Invariants

| Invariant | Check |
|-----------|-------|
| Auth checked before actions | No privilege escalation |
| Data isolation maintained | User A can't see User B's data |
| Rate limits respected | No bypass on new endpoints |

---

## Example: Universal Consumer List

```markdown
## Consumer List for [Feature/API/Component]

| Consumer | Layer | Entry Point | Contract Used | Risk | Verification |
|----------|-------|-------------|---------------|------|-------------|
| Dashboard list | UI | /dashboard | GET /api/items | High | Manual + E2E |
| Detail page | UI | /items/:id | GET /api/items/:id | High | Manual |
| Settings selector | UI | /settings | GET /api/items?type=config | Medium | Unit test |
| Export task | Background | cron | GET /api/items?all=true | Medium | Integration test |
| Admin panel | UI | /admin/items | GET /api/items?admin=true | Low | Manual |
| SDK | External | npm package | GET /api/items | High | Contract test |
| Metrics collector | Ops | prometheus | GET /api/items/metrics | Low | Smoke test |
```
