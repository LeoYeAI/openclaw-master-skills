# Backend Common Issues & Fix Methods (Bug Fixing Catalog)

Goal: Cover high-frequency root causes and reusable fix strategies for backend bugs (language/framework agnostic).

---

## 🔴 Quick Index (By Error Symptom)

| Error Symptom | Possible Root Cause | Jump To |
|--------------|-------------------|---------|
| `Unknown column 'xxx' in 'field list'` | Model has field but missing migration | → 7.3 |
| `Data too long for column` | Field length insufficient | → 7.4 |
| `foreign key constraint fails` | Foreign key constraint issue | → 7.2 |
| Request has field but response not updated | Update Schema missing field | → 1.4 |
| `LookupError: 'xxx' is not among enum values` | Enum native_enum issue | → 7.1 |
| HTTP 200 but business failure | Status code vs business status inconsistency | → 1.2 |
| API occasionally hangs | Missing timeout | → 2.1 |
| Duplicate writes/orders | Idempotency not protected | → 2.2 |
| Garbled logs/responses | Encoding inconsistency | → 5.2 |
| API Key decryption failure with no context | Logs lack context | → 6.1 |

---

## 1) API Behavior & Contract

### 1.1 Request/Response Shape Assumption Error (Schema Drift)

- Symptom: Parsing crash; missing fields cause default value override; frontend display abnormal.
- Quick identification: Compare contract (OpenAPI/Schema) vs actual response; pay attention to null/empty/omitted differences.
- Root cause: Backend changed field names/types/defaults; error code structure inconsistent; compat logic incomplete.
- Fix strategy:
  - Clarify contract and align implementation; add compat layer (old field aliases, default value strategy).
  - Unify error returns: status code + business error code + message + trace/correlation id.
- Verification: Contract validation/integration tests cover success and error branches; old clients don't break.

### 1.2 HTTP Status Code vs Business Status Inconsistency

- Symptom: HTTP 200 but business failure; or HTTP 4xx/5xx but frontend can't distinguish error types.
- Root cause: Relying solely on HTTP status for business semantics; or business errors being swallowed.
- Fix strategy: Define consistent error model; unify mapping at gateway/middleware.
- Verification: Under failure scenarios, client can reliably distinguish "retryable/non-retryable/needs user correction".

### 1.3 CORS/Preflight (OPTIONS) Conflicts with Auth Middleware

- Symptom: Browser cross-origin request fails; OPTIONS returns 401/403; only on auth-required endpoints.
- Quick identification: Check if OPTIONS requests pass through auth middleware; check if response lacks CORS headers.
- Root cause: Treating OPTIONS as regular business request for auth; preflight not handled uniformly; allow-origin/credentials combination incorrect.
- Fix strategy:
  - Short-circuit OPTIONS handling at the beginning of routes/middleware (no auth or minimal auth).
  - Uniformly set CORS headers (allow specific origins per environment).
- Verification: OPTIONS 200/204; real requests with/without credentials work as expected.

### 1.4 🔴 Update/Create Schema Missing Fields (Pydantic Silent Drop)

- Symptom: Frontend submitted field but database not updated; request has value but response shows old value.
- Quick identification: Compare request params and response output in Network panel; check Schema definition.
- Root cause: Pydantic Schema doesn't define the field, `model_dump(exclude_unset=True)` doesn't include it.
- Fix strategy:
  - Add missing field to `XxxUpdate` / `XxxCreate` Schema.
  - Check all editable fields are defined in Schema.
- Verification: Field in request params is correctly updated in response output.
- Real case: BUG-012 editing embedding model model_name won't update

```python
# ❌ Wrong: Schema missing field
class EmbeddingModelUpdate(BaseModel):
    name: str | None = None
    # Missing model_name!

# ✅ Correct: Add all editable fields
class EmbeddingModelUpdate(BaseModel):
    name: str | None = None
    model_name: str | None = None  # Added
```

## 2) Timeout/Retry/Idempotency

### 2.1 Missing Timeout Causes Request Hang

- Symptom: API occasionally hangs; thread/connection pool exhausted; cascading failure.
- Quick identification: External calls/DB calls have no timeout; monitoring shows p99 elongation.
- Fix strategy: Set hard timeouts for external calls, DB, queues; timeout errors must be observable.
- Verification: When injecting slow dependency (sleep/rate limit), system fails within controllable time and releases resources.

### 2.2 Retry Without Idempotency Protection

- Symptom: Duplicate orders/writes; logs show same request succeeded multiple times.
- Root cause: Client/gateway retries; backend write operations not idempotent.
- Fix strategy:
  - Add idempotency key or uniqueness constraint (unique index) for write operations.
  - Only retry "retryable errors" (timeout/connection error), with exponential backoff.
- Verification: Duplicate requests (same idempotency key) produce only one effect.

### 2.3 Pagination/Sorting/Filtering Boundary Errors (Off-by-one / Unstable Sort)

- Symptom: List pagination duplicates/misses data; same query returns different order each time; "last page" is empty.
- Quick identification: Check if sort includes stable primary key; check offset/limit calculation; check if filter conditions are consistently applied to count and list.
- Root cause: Unstable sort (missing tie-breaker); offset/limit boundary calculation error; count and list query conditions inconsistent.
- Fix strategy: Add stable primary key to sort; unify query construction; add tests for boundary pages (page=1, last page, empty result).
- Verification: With fixed dataset, pagination traversal has no duplicates/no misses; sort is stable and reproducible.

## 3) Data Consistency & Transaction Boundaries

### 3.1 Partial Write (Missing or Incorrect Transaction Boundary)

- Symptom: Half-written failure causes dirty data; downstream dependencies break.
- Root cause: Multi-table/multi-step writes without transaction; exception path doesn't rollback.
- Fix strategy:
  - Put writes within the same business invariant into a transaction; for compensatable steps, add compensation logic.
  - Clarify consistency level: strong/eventual consistency, and add retry and reconciliation.
- Verification: After fault injection (mid-way error), data still satisfies invariants or can be auto-repaired.

### 3.2 Concurrent Update Lost (Lost Update)

- Symptom: User A's update overwritten by B; version rollback.
- Root cause: Read-modify-write without concurrency control.
- Fix strategy: Optimistic locking (version) or pessimistic locking (select for update); or atomic update statements.
- Verification: Under concurrent stress test, updates don't get lost, conflicts have clear error codes.

## 4) Performance & Resource Exhaustion (Manifesting as Bugs)

### 4.1 N+1 Query / Loop External Calls

- Symptom: Sudden timeout when data volume increases; CPU/DB QPS spikes.
- Quick identification: Logs/traces show repeated similar queries.
- Fix strategy: Batch query/preloading/Join; cache hotspots; convert loop calls to batch processing.
- Verification: With fixed dataset, query count and latency significantly decrease; p95/p99 improve.

### 4.2 Connection Pool Exhaustion / Not Released

- Symptom: Occasional timeout; connection count stays high; brief recovery after restart.
- Root cause: Connection leak; not closed on timeout; concurrency limit not controlled.
- Fix strategy: Ensure finally/cleanup; set pool size and queue limits; add circuit breaker/rate limiter for external dependencies.
- Verification: After stress test, connection count drops back; no sustained growth trend.

## 5) Serialization/Encoding/Time

### 5.1 Timezone & Time Format

- Symptom: Date off by one day; scheduled tasks fire at wrong time; log and DB time don't match.
- Root cause: Mixing local timezone/UTC; serialization format inconsistent.
- Fix strategy: Store UTC uniformly; APIs use ISO-8601 explicitly; display layer does localization.
- Verification: Cross-timezone cases (UTC+0/UTC+8) all correct.

### 5.2 Encoding Inconsistency (UTF-8)

- Symptom: Garbled text; field truncation; signature verification failure.
- Root cause: Database/HTTP header/application default encoding inconsistent.
- Fix strategy: UTF-8 throughout entire chain; explicit Content-Type charset; DB column encoding aligned.
- Verification: Data with mixed Chinese/English and emoji can be written and read (if supported).

### 5.3 JSON Serialization Type Pitfalls (BigInt/Decimal/Timestamp)

- Symptom: JSON serialization error; monetary precision loss; frontend parsing anomaly.
- Quick identification: Check if BigInt/Decimal returned directly; check if monetary/time fields mix number/string.
- Root cause: JSON doesn't support BigInt; floating point precision causes monetary errors; time field format inconsistent.
- Fix strategy: Convert BigInt/Decimal explicitly to string; use string/integer cents for monetary values; unify time to ISO-8601 or epoch, documented in contract.
- Verification: Cases with extreme values (large integers/high-precision amounts) can serialize, deserialize without precision loss.

## 6) Error Handling & Observability

### 6.1 Error Swallowed / Missing Context

- Symptom: Only see "500"; can't identify file/line/request.
- Root cause: Catch returns generic response; logs lack request id.
- Fix strategy: Unified exception middleware; structured logging; pass through trace/correlation id.
- Verification: Any error can be quickly traced in logs/traces.

### 6.2 Logs Leak Sensitive Information (Token/Password/PII)

- Symptom: Authorization, cookies, passwords, phone numbers/emails appear in logs.
- Quick identification: Global search log fields; check if request logging middleware prints raw header/body.
- Root cause: Structured logging without redaction; debug logs include payload.
- Fix strategy: Add redaction at log layer (whitelist/blacklist); field-level sanitization for body; disable body logging for sensitive endpoints if needed.
- Verification: After stress test/regression, logs have no sensitive fields; error troubleshooting still works (via request id/trace).

## 7) ORM/SQLAlchemy Specific Issues

### 7.1 Enum native_enum Causes Query Failure

- Symptom: `LookupError: 'xxx' is not among the defined enum values`
- Quick identification: Check if `Enum()` uses `values_callable` but lacks `native_enum=False`.
- Root cause: MySQL stores enum names (e.g. `LANGCHAIN`), but `values_callable` expects enum values (e.g. `langchain`).
- Fix strategy: Add `native_enum=False` parameter.
- Verification: Query returns correct results.
- Real case: BUG-003 KBEngineType enum case mismatch

```python
# ❌ Wrong
engine_type = mapped_column(
    Enum(KBEngineType, values_callable=lambda x: [e.value for e in x])
)

# ✅ Correct
engine_type = mapped_column(
    Enum(KBEngineType, 
         values_callable=lambda x: [e.value for e in x],
         native_enum=False)  # Key
)
```

### 7.2 Foreign Key Constraint Failure (Referenced Row Deleted)

- Symptom: `IntegrityError: foreign key constraint fails`
- Quick identification: Check if referenced row exists; check for soft delete/hard delete inconsistency.
- Root cause: Foreign key constraint doesn't account for deletion; or JWT Token's user_id corresponds to a deleted user.
- Fix strategy:
  - Set `ondelete="SET NULL"` + `nullable=True`
  - Or check if referenced row exists before insertion
- Verification: Even if referenced row doesn't exist, insertion handles gracefully.
- Real case: BUG-007 audit log user_id FK constraint failure

### 7.3 🔴 Model Has Field But Database Lacks Column (Missing Migration)

- Symptom: `OperationalError: Unknown column 'xxx' in 'field list'`
- Quick identification: Check if alembic/versions has corresponding migration file.
- Root cause: SQLAlchemy model added field but Alembic migration was not created.
- Fix strategy: Create Alembic migration file to add missing column.
- Verification: `alembic upgrade head` succeeds; queries work normally.
- Real case: BUG-078 chat_sessions.meta_data column missing

```bash
# Detection commands
alembic history  # View migration history
alembic current  # View current version
```

### 7.4 Field Length Insufficient Causes Update Failure

- Symptom: `Data too long for column 'xxx'`
- Quick identification: Check DB column definition vs actual data length.
- Root cause: Field originally designed with insufficient length; feature expansion requires longer data.
- Fix strategy:
  - Create migration to extend field length
  - If there are FK constraints, drop constraints first then extend
- Verification: Longer data can be stored normally.
- Real case: BUG-005 lightrag_llm_provider_id needs to support `provider_id:model_name` format

### 7.5 SQL Dialect Incompatibility

- Symptom: `ProgrammingError: syntax error` (only on specific DB)
- Quick identification: Check raw SQL for `CAST AS TEXT`/`ILIKE`/`::type` syntax.
- Root cause: PostgreSQL syntax unsupported in MySQL.
- Fix strategy:
  - Use SQLAlchemy abstractions
  - Or use cross-DB compatible syntax (e.g. `CAST AS CHAR` instead of `CAST AS TEXT`)
- Verification: Tests pass on target DB type.
- Real case: BUG-004 MySQL incompatible with `CAST AS TEXT`

### 7.6 Cached Old Code (.pyc)

- Symptom: Code is fixed but error persists.
- Quick identification: Check `__pycache__/*.pyc` file timestamps.
- Root cause: Python ran compiled cache of old code.
- Fix strategy: Delete `.pyc` files and restart service.
- Verification: New code takes effect after restart.

```bash
# Cleanup commands
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

## 8) LLM/Embedding Integration Issues

### 8.1 Embedding Dimension Mismatch

- Symptom: `Embedding dimension mismatch: total elements (X) cannot be evenly divided by expected dimension (Y)`
- Quick identification: Check configured dimension vs model actual output dimension.
- Root cause: Changed embedding model without updating dimension config.
- Fix strategy:
  - Modify dimension field in database
  - Or call "reset vectors" API to rebuild index
- Verification: Document processing succeeds.
- Real case: BUG-006 user configured 1536 dimensions but model outputs 1024

### 8.2 API Key Decryption Failure

- Symptom: `InvalidToken` warning; LLM calls fail.
- Quick identification: Check if `ENCRYPTION_KEY` changed.
- Root cause: After encryption key change, old encrypted API Keys can't be decrypted.
- Fix strategy:
  - Add LLM name/ID context to logs
  - Prompt user to re-enter API Key
- Verification: Logs can identify which specific LLM config is affected.
- Real case: BUG-009 API Key decryption failure with no context in logs

### 8.3 LLM Returns Empty Content Causing Processing Failure

- Symptom: `InvalidResponseError: Received empty content`; still fails after retry.
- Quick identification: Check prompt length and model name in LLM logs.
- Root cause: Model returns empty response on specific prompts (rate limit/context too long/model issue).
- Fix strategy:
  - Implement degradation strategy (e.g. skip KG extraction, vector embedding only)
  - Add retry and timeout config
- Verification: Even if LLM fails, the process can degrade and complete.
- Real case: BUG-014 DeepSeek-OCR returns empty content causing index failure

## 9) Minimal Verification Checklist (Backend)

- Original repro case: no longer reproduces after fix.
- At least one automated verification: unit test/integration test/contract validation.
- For high-risk areas: timeout/retry/idempotency/transaction/concurrency — do minimal fault injection.
- Observability: errors are traceable; key metrics not degraded.
- 🔴 Request-response consistency: field in request params is correctly updated in response output.

## 10) Quick Detection Commands

```bash
# Detect Update Schema missing fields
rg "class.*Update.*BaseModel" --glob "*.py" -A 20 | grep -v "model_name\|provider_type"

# Detect enums missing native_enum=False
rg "values_callable" --glob "*.py" -A 3 | grep -v "native_enum=False"

# Detect MySQL-incompatible SQL
rg "CAST\(.*AS TEXT\)|ILIKE|::text|::varchar" --glob "*.py"

# Detect foreign keys missing ondelete
rg "ForeignKey\(" --glob "*.py" | grep -v "ondelete"

# Detect pyc cache
find . -name "*.pyc" -newer source_file.py
```
