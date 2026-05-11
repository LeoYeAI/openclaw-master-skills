# Backend Common Issues & Fix Patterns

High-frequency root causes and reusable fix strategies for backend bugs (language/framework agnostic).

---

## Quick Index (By Error Symptom)

| Error Symptom | Possible Root Cause | Section |
|--------------|-------------------|---------|
| `Unknown column 'xxx'` | Model has field but missing migration | 7.3 |
| `Data too long for column` | Field length insufficient | 7.4 |
| `foreign key constraint fails` | FK constraint issue | 7.2 |
| Request has field but response not updated | Update Schema missing field | 1.4 |
| `LookupError: enum value` | Enum native_enum issue | 7.1 |
| HTTP 200 but business failure | Status code inconsistency | 1.2 |
| API occasionally hangs | Missing timeout | 2.1 |
| Duplicate writes/orders | Idempotency not protected | 2.2 |
| Garbled logs/responses | Encoding inconsistency | 5.2 |

---

## 1. API Behavior & Contract

### 1.1 Schema Drift

- **Symptom**: Parsing crash; missing fields; frontend display abnormal
- **Detection**: Compare contract (OpenAPI/Schema) vs actual response; check null/empty/omitted differences
- **Root cause**: Backend changed fields/types/defaults; error structure inconsistent
- **Fix**: Clarify contract; add compat layer (aliases, defaults). Unify error returns: status + error code + message + trace ID
- **Verify**: Contract tests cover success and error branches; old clients don't break

### 1.2 HTTP vs Business Status Inconsistency

- **Symptom**: HTTP 200 but business failure; or HTTP 4xx but client can't distinguish error types
- **Root cause**: Relying solely on HTTP status for business semantics
- **Fix**: Define consistent error model; unify mapping at gateway/middleware
- **Verify**: Under failure, client can distinguish retryable / non-retryable / needs user correction

### 1.3 CORS/Preflight Conflicts with Auth Middleware

- **Symptom**: Browser cross-origin request fails; OPTIONS returns 401/403
- **Detection**: Check if OPTIONS passes through auth middleware; check CORS headers
- **Fix**: Short-circuit OPTIONS at route start (no auth). Set CORS headers per environment
- **Verify**: OPTIONS returns 200/204; real requests with/without credentials succeed

### 1.4 Update/Create Schema Missing Fields (Pydantic Silent Drop)

- **Symptom**: Frontend submitted field but database not updated
- **Detection**: Compare request params and response output in Network panel
- **Root cause**: Pydantic Schema doesn't define the field; `model_dump(exclude_unset=True)` excludes it
- **Fix**: Add missing field to Update/Create Schema. Check all editable fields
- **Verify**: Field in request is correctly updated in response

```python
# Wrong: Schema missing field
class ItemUpdate(BaseModel):
    name: str | None = None
    # Missing model_name!

# Correct: Add all editable fields
class ItemUpdate(BaseModel):
    name: str | None = None
    model_name: str | None = None  # Added
```

## 2. Timeout / Retry / Idempotency

### 2.1 Missing Timeout

- **Symptom**: API occasionally hangs; connection pool exhausted; cascading failure
- **Fix**: Set hard timeouts for external calls, DB, queues. Timeout errors must be observable
- **Verify**: Injecting slow dependency, system fails within controllable time

### 2.2 Retry Without Idempotency

- **Symptom**: Duplicate orders/writes
- **Fix**: Add idempotency key or uniqueness constraint. Only retry retryable errors with backoff
- **Verify**: Duplicate requests produce only one effect

### 2.3 Pagination Boundary Errors

- **Symptom**: List duplicates/misses data; unstable sort order
- **Fix**: Add stable tie-breaker to sort; unify query construction; test boundary pages
- **Verify**: Pagination traversal has no duplicates, sort is stable

## 3. Data Consistency & Transactions

### 3.1 Partial Write (Missing Transaction)

- **Symptom**: Half-written failure causes dirty data
- **Fix**: Wrap related writes in transaction; add compensation for compensatable steps
- **Verify**: After fault injection, data satisfies invariants

### 3.2 Concurrent Update Lost

- **Symptom**: User A's update overwritten by B
- **Fix**: Optimistic locking (version) or pessimistic locking; or atomic update statements
- **Verify**: Under concurrent stress, updates don't get lost

## 4. Performance Issues Manifesting as Bugs

### 4.1 N+1 Query / Loop External Calls

- **Symptom**: Timeout when data volume increases; DB QPS spikes
- **Fix**: Batch query/preloading/Join; cache hotspots; batch processing
- **Verify**: Query count and latency decrease significantly

### 4.2 Connection Pool Exhaustion

- **Symptom**: Occasional timeout; connection count stays high
- **Fix**: Ensure finally/cleanup; set pool size limits; add circuit breaker
- **Verify**: After stress test, connection count drops back

## 5. Serialization / Encoding / Time

### 5.1 Timezone & Time Format

- **Symptom**: Date off by one day; scheduled tasks fire wrong
- **Fix**: Store UTC uniformly; APIs use ISO-8601; display layer localizes
- **Verify**: Cross-timezone cases correct

### 5.2 Encoding Inconsistency

- **Symptom**: Garbled text; field truncation
- **Fix**: UTF-8 throughout; explicit charset in Content-Type; DB encoding aligned
- **Verify**: Mixed character data read/write correctly

### 5.3 JSON Serialization Pitfalls

- **Symptom**: BigInt/Decimal precision loss; frontend parsing anomaly
- **Fix**: Convert BigInt/Decimal to string; use integer cents for money; unify time format
- **Verify**: Extreme values serialize/deserialize without precision loss

## 6. Error Handling & Observability

### 6.1 Error Swallowed / Missing Context

- **Symptom**: Only see "500"; can't identify source
- **Fix**: Unified exception middleware; structured logging; pass trace/correlation ID
- **Verify**: Any error can be traced in logs

### 6.2 Sensitive Information in Logs

- **Symptom**: Tokens, passwords, PII in logs
- **Fix**: Add redaction at log layer; field-level sanitization; disable body logging for sensitive endpoints
- **Verify**: Logs have no sensitive fields; debugging still works via request ID

## 7. ORM/SQLAlchemy Specific

### 7.1 Enum native_enum

- **Symptom**: `LookupError: 'xxx' is not among the defined enum values`
- **Fix**: Add `native_enum=False` to `Enum()` with `values_callable`

### 7.2 Foreign Key Constraint Failure

- **Symptom**: `IntegrityError: foreign key constraint fails`
- **Fix**: Set `ondelete="SET NULL"` + `nullable=True`; or check existence before insert

### 7.3 Missing Migration

- **Symptom**: `OperationalError: Unknown column 'xxx'`
- **Fix**: Create Alembic migration for missing column

### 7.4 Field Length Insufficient

- **Symptom**: `Data too long for column 'xxx'`
- **Fix**: Create migration to extend field length

### 7.5 SQL Dialect Incompatibility

- **Symptom**: `ProgrammingError: syntax error` on specific DB
- **Fix**: Use SQLAlchemy abstractions or cross-DB syntax (e.g. `CAST AS CHAR`)

### 7.6 Cached Old Code

- **Symptom**: Code fixed but error persists
- **Fix**: Delete `.pyc` files and restart

```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

## 8. LLM/Embedding Integration

### 8.1 Embedding Dimension Mismatch

- **Symptom**: Dimension mismatch error during document processing
- **Fix**: Update dimension config or rebuild index

### 8.2 API Key Decryption Failure

- **Symptom**: `InvalidToken` warning; LLM calls fail after key change
- **Fix**: Add context to logs; prompt user to re-enter API Key

### 8.3 LLM Returns Empty Content

- **Symptom**: `InvalidResponseError: Received empty content`
- **Fix**: Implement degradation strategy (skip KG extraction, vector only); add retry

---

## Quick Detection Commands

```bash
# Detect Update Schema missing fields
rg "class.*Update.*BaseModel" --glob "*.py" -A 20

# Detect enums missing native_enum=False
rg "values_callable" --glob "*.py" -A 3 | rg -v "native_enum=False"

# Detect MySQL-incompatible SQL
rg "CAST\(.*AS TEXT\)|ILIKE|::text|::varchar" --glob "*.py"

# Detect foreign keys missing ondelete
rg "ForeignKey\(" --glob "*.py" | rg -v "ondelete"

# Detect pyc cache issues
find . -name "*.pyc" -newer source_file.py
```

---

## 10. OpenClaw-Specific Patterns

### 10.1 Simulated Tool Call Parsing Failure

- **Symptom**: LLM outputs `write_file("path", """content""")` but tool receives garbled single arg
- **Detection**: Check `tool_arguments_remapped` log — if `extra_keys=['input']` appears, parser failed
- **Root cause**: `tool_call_parser.py` regex patterns only handle single-arg calls
- **Fix**: Use AST-based parsing for multi-arg calls; add word boundary `(?<![a-zA-Z0-9_])` to all patterns
- **⚠️ Dual implementation**: `llm_node.py` has its own `parse_simulated_tool_calls` — must fix BOTH
- **Verify**: Test with `write_file("path.md", """content""")` + `deepagents_write_file("p", """c""")`

### 10.2 Tool Argument Remapping Misorder

- **Symptom**: Tool gets wrong parameter filled (e.g. `content` filled instead of `file_path`)
- **Detection**: Check `_remap_mismatched_arguments` in `tool_node.py` — it fills sorted alphabetically
- **Root cause**: Remapper maps extra values to missing required fields in alphabetical order
- **Fix**: Fix the parser to produce correct param names; don't rely on remapper for multi-arg tools
- **Verify**: Check both `file_path` AND `text`/`content` are correctly populated

### 10.3 Server Running Stale Code After Fix

- **Symptom**: Tests pass locally but behavior unchanged in running system
- **Detection**: Check process PID — if same PID as before fix, code not reloaded
- **Root cause**: Python keeps modules in memory; `__pycache__` may serve old bytecode
- **Fix**: Kill process + clear `__pycache__` + restart `run_dev.py`
- **Verify**: New PID + health check at `/docs` + exercise fixed code path

### 10.4 Reasoning Model Simulated Mode Issues

- **Symptom**: Tool calls not detected from deepseek-reasoner / other reasoning models
- **Detection**: Look for `simulated_tool_mode_enabled` in logs
- **Root cause**: Reasoning models don't support native tool calling; output is plain text with code blocks
- **Fix**: Ensure `tool_call_parser.py` handles the model's output format
- **Verify**: Send test message using reasoning model, check tool call execution

### 10.5 MCP Server Lifecycle Failure

- **Symptom**: MCP tool call returns timeout or connection error
- **Detection**: Check `server_status` in tool config; check if subprocess is alive
- **Root cause**: `command`-type MCP server subprocess died or failed to start
- **Fix**: Check `core/mcp/pool.py` lifecycle; restart MCP server; check env vars
- **Verify**: Tool health check passes; actual MCP call returns result

---

## Minimal Verification Checklist (Backend)

- [ ] Original repro case no longer reproduces
- [ ] At least one automated verification (unit/integration/contract)
- [ ] High-risk: timeout/retry/idempotency/transaction tested
- [ ] Errors are traceable; key metrics not degraded
- [ ] Request-response consistency: submitted fields correctly updated
