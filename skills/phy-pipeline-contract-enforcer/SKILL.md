---
name: phy-pipeline-contract-enforcer
description: Data pipeline contract enforcer. Define the expected schema at each pipeline stage boundary — field names, types, nullability, value ranges, business invariants — and validate actual data samples against those contracts. Catches schema drift between pipeline stages before it reaches production. Supports dbt models, Spark DataFrames, Pandas DataFrames, Kafka topics, REST API payloads, and raw CSV/JSON files. Can auto-generate a contract from a sample, validate a sample against an existing contract, detect when a contract has been broken by upstream changes, and produce a migration plan to fix violations. Zero external API — pure local file and CLI analysis. Triggers on "pipeline contract", "schema drift", "validate pipeline output", "data contract", "pipeline schema mismatch", "contract enforcement", "/pipeline-contract".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - data-engineering
    - data-quality
    - pipeline
    - schema-validation
    - dbt
    - data-contracts
    - great-expectations
    - data-mesh
    - developer-tools
    - testing
---

# Pipeline Contract Enforcer

Data pipelines fail silently. A column goes nullable in staging. An upstream team renames a field. A new data source adds an unexpected type. By the time it surfaces in a dashboard or an alert, the corrupt data is already in production.

Paste a data sample and a contract (or generate the contract from the sample), and get an instant audit: which fields violate the contract, what the violation is, and what to fix.

**Works with dbt, Spark, Pandas, Kafka, REST APIs, CSV/JSON. Zero external services. No Great Expectations config required.**

---

## Trigger Phrases

- "pipeline contract", "data contract", "schema enforcement"
- "validate my pipeline output", "schema drift", "pipeline schema changed"
- "my downstream job broke", "column type mismatch", "unexpected null"
- "generate contract from sample", "write a data contract"
- "dbt schema contract", "validate DataFrame schema"
- "/pipeline-contract"

---

## How to Provide Input

```bash
# Option 1: Generate a contract from a sample file
/pipeline-contract --generate sample.json
/pipeline-contract --generate output.csv

# Option 2: Validate a sample against an existing contract
/pipeline-contract --validate sample.json --contract contracts/orders.yaml

# Option 3: Check for drift between two samples (old vs new)
/pipeline-contract --diff old-output.json new-output.json

# Option 4: From dbt schema.yml
/pipeline-contract --from-dbt models/schema.yml --validate data/orders.csv

# Option 5: Validate a Pandas/Spark DataFrame (paste the schema)
/pipeline-contract --dataframe
[paste df.dtypes or df.schema output here]

# Option 6: Full pipeline audit (multiple stage files)
/pipeline-contract --audit pipeline/
# Reads: pipeline/stage-1.json, pipeline/stage-2.json, contracts/*.yaml
```

---

## Step 1: Infer Pipeline Stage Type

Identify what kind of pipeline artifact is being validated:

```bash
# Detect file type and format
file_ext="${1##*.}"
case "$file_ext" in
  json)   STAGE_TYPE="json_payload" ;;
  csv)    STAGE_TYPE="tabular_csv" ;;
  parquet) STAGE_TYPE="parquet" ;;
  yaml|yml) STAGE_TYPE="contract_or_dbt" ;;
  *)      STAGE_TYPE="unknown" ;;
esac

# Check if it looks like dbt schema.yml
if grep -q "^models:" "$1" 2>/dev/null || grep -q "^version:" "$1" 2>/dev/null; then
  STAGE_TYPE="dbt_schema"
fi

# Check if it's a Python type annotation block (DataFrame schema)
if echo "$1" | grep -qE "dtype|object|int64|float64|datetime64"; then
  STAGE_TYPE="pandas_schema"
fi
```

### Supported Stage Types

| Stage Type | Detection | Examples |
|-----------|-----------|---------|
| JSON payload | `.json` extension or curly braces | REST API output, Kafka message |
| Tabular CSV | `.csv` extension | ETL output, export files |
| dbt schema | `models:` / `version:` key | dbt `schema.yml` |
| Pandas schema | `dtype`/`int64`/`float64` patterns | `df.dtypes` output |
| Spark schema | `StructType` / `StructField` | `df.printSchema()` output |
| Parquet | `.parquet` extension | Processed pipeline files |

---

## Step 2: Extract Schema from Sample

From any data sample, extract the implicit schema:

### JSON / REST Payload

```python
# For each field in the JSON object, infer:
# - field name
# - data type (string, integer, float, boolean, null, array, object)
# - nullable (does the field ever appear as null or absent?)
# - example values (first 3 distinct values)
# - cardinality hint (if < 20 distinct values across samples → likely enum)

def infer_json_schema(samples: list[dict]) -> dict:
    schema = {}
    for sample in samples:
        for key, value in sample.items():
            if key not in schema:
                schema[key] = {
                    "type": type(value).__name__,
                    "nullable": False,
                    "examples": [],
                    "values_seen": set()
                }
            if value is None:
                schema[key]["nullable"] = True
            schema[key]["values_seen"].add(str(value)[:50])
            if len(schema[key]["examples"]) < 3:
                schema[key]["examples"].append(value)
    # Detect enums: < 20 distinct values
    for field in schema.values():
        if len(field["values_seen"]) < 20:
            field["enum_hint"] = sorted(field["values_seen"])
    return schema
```

### CSV / Tabular

```bash
# Get column names, types, null counts, sample values
python3 -c "
import csv, sys
from collections import defaultdict, Counter

with open('$FILE') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

schema = defaultdict(lambda: {'types': Counter(), 'null_count': 0, 'examples': []})
for row in rows:
    for col, val in row.items():
        schema[col]['null_count'] += 1 if not val.strip() else 0
        schema[col]['types'][type(val).__name__] += 1
        if len(schema[col]['examples']) < 3:
            schema[col]['examples'].append(val)

for col, info in schema.items():
    null_pct = round(100 * info['null_count'] / len(rows), 1)
    print(f'{col}: {dict(info[\"types\"])} | null={null_pct}% | examples={info[\"examples\"]}')
"
```

### dbt schema.yml

```bash
# Extract column contracts already defined
grep -A 20 "columns:" "$FILE" | grep -E "name:|description:|tests:" | head -50
```

---

## Step 3: Contract Format

A Pipeline Contract is a YAML file that defines the expected schema at a specific stage boundary:

```yaml
# contracts/orders-output.yaml
contract:
  name: orders-output
  version: "1.0"
  description: "Expected schema at the output of the orders processing stage"
  stage: orders_processor
  produces: downstream-billing, downstream-reporting

  fields:
    order_id:
      type: string
      nullable: false
      pattern: "^ORD-[0-9]{8}$"        # Regex pattern check
      unique: true

    customer_id:
      type: string
      nullable: false

    order_total:
      type: float
      nullable: false
      min: 0.01
      max: 999999.99

    status:
      type: string
      nullable: false
      enum: [pending, confirmed, shipped, delivered, cancelled]

    created_at:
      type: datetime
      nullable: false
      format: "ISO 8601"               # 2026-03-18T10:42:00Z

    discount_code:
      type: string
      nullable: true                   # Explicitly allowed null

    metadata:
      type: object
      nullable: true
      required_keys: [source, version] # If not null, these keys must exist

  invariants:
    - name: "order_total matches items"
      description: "order_total must equal sum of line_items[*].price"
      severity: error
    - name: "shipped orders have tracking"
      description: "If status=shipped, tracking_number must not be null"
      severity: error
    - name: "discount positive"
      description: "discount_amount must be 0 or positive"
      severity: warning

  row_count:
    min: 1
    max: null        # No upper bound
```

---

## Step 4: Validate Sample Against Contract

For each field in the contract, check the sample data:

```python
def validate_against_contract(data: list[dict], contract: dict) -> list[dict]:
    violations = []

    for row_num, row in enumerate(data):
        for field_name, rules in contract["fields"].items():

            # CHECK: Required field present
            if field_name not in row and not rules.get("nullable"):
                violations.append({
                    "row": row_num,
                    "field": field_name,
                    "violation": "MISSING_REQUIRED_FIELD",
                    "expected": f"field '{field_name}' must be present",
                    "got": "field absent"
                })
                continue

            value = row.get(field_name)

            # CHECK: Null constraint
            if value is None and not rules.get("nullable"):
                violations.append({
                    "row": row_num,
                    "field": field_name,
                    "violation": "UNEXPECTED_NULL",
                    "expected": "not null",
                    "got": "null"
                })
                continue

            # CHECK: Type
            if value is not None:
                expected_type = rules.get("type")
                actual_type = type(value).__name__
                if not type_matches(actual_type, expected_type):
                    violations.append({
                        "row": row_num,
                        "field": field_name,
                        "violation": "TYPE_MISMATCH",
                        "expected": expected_type,
                        "got": actual_type
                    })

            # CHECK: Enum
            if "enum" in rules and value not in rules["enum"] and value is not None:
                violations.append({
                    "row": row_num,
                    "field": field_name,
                    "violation": "INVALID_ENUM_VALUE",
                    "expected": f"one of {rules['enum']}",
                    "got": value
                })

            # CHECK: Range
            if "min" in rules and isinstance(value, (int, float)) and value < rules["min"]:
                violations.append({
                    "row": row_num,
                    "field": field_name,
                    "violation": "BELOW_MINIMUM",
                    "expected": f">= {rules['min']}",
                    "got": value
                })

            # CHECK: Pattern
            import re
            if "pattern" in rules and value is not None:
                if not re.match(rules["pattern"], str(value)):
                    violations.append({
                        "row": row_num,
                        "field": field_name,
                        "violation": "PATTERN_MISMATCH",
                        "expected": rules["pattern"],
                        "got": value
                    })

    return violations
```

---

## Step 5: Drift Detection (Old vs New Samples)

When comparing two versions of a pipeline output:

```bash
# Extract field lists from both samples
python3 -c "
import json, sys

old = json.load(open('old-output.json'))
new = json.load(open('new-output.json'))

# Normalize to list of records
old_records = old if isinstance(old, list) else [old]
new_records = new if isinstance(new, list) else [new]

old_fields = set(old_records[0].keys()) if old_records else set()
new_fields = set(new_records[0].keys()) if new_records else set()

added = new_fields - old_fields
removed = old_fields - new_fields
common = old_fields & new_fields

print('ADDED:', sorted(added))
print('REMOVED:', sorted(removed))

# Check type changes on common fields
for field in sorted(common):
    old_type = type(old_records[0].get(field)).__name__
    new_type = type(new_records[0].get(field)).__name__
    if old_type != new_type:
        print(f'TYPE CHANGED: {field}: {old_type} -> {new_type}')

    # Check nullable change
    old_null = any(r.get(field) is None for r in old_records)
    new_null = any(r.get(field) is None for r in new_records)
    if not old_null and new_null:
        print(f'BECAME NULLABLE: {field}')
    if old_null and not new_null:
        print(f'NOW NON-NULL: {field} (stricter)')
"
```

---

## Step 6: Output Report

```markdown
## Pipeline Contract Report
Stage: orders_processor | Contract: contracts/orders-output.yaml
Sample: data/orders-2026-03-18.json (1,247 rows)

### Summary

| Category | Count | Severity |
|----------|-------|----------|
| 🔴 Type mismatch | 3 | Error — downstream will crash |
| 🔴 Unexpected null in required field | 8 | Error — violates contract |
| 🟠 Invalid enum value | 12 | Error — invalid state |
| 🟡 Pattern mismatch | 2 | Warning — format inconsistency |
| ✅ Fields passing all checks | 14 / 18 | — |

Contract status: **BROKEN** — fix before promoting to next stage

---

### 🔴 ERRORS — Pipeline Cannot Proceed Safely

**TYPE MISMATCH: `order_total` (rows 42, 118, 891)**
- Contract: `float`
- Got: `string` (`"49.99"`, `"120.00"`, `"7.50"`)
- Root cause: upstream CSV export is wrapping numbers in quotes
- Fix: Add `df['order_total'] = pd.to_numeric(df['order_total'])` before output
- Impact: Downstream billing service expects float — will throw TypeError on those 3 rows

**UNEXPECTED NULL: `customer_id` (8 rows)**
- Row indices: 15, 77, 203, 344, 502, 601, 788, 934
- Contract: `nullable: false`
- Got: `null`
- Root cause: Guest checkout orders — customer_id not assigned for non-registered users
- Options:
  1. Change contract to `nullable: true` if guest checkout is intentional
  2. Assign a synthetic `guest_XXXX` ID in the upstream transformer
  3. Filter out guest orders before this pipeline stage

**INVALID ENUM VALUE: `status` field (12 rows)**
- Values found: `"processing"` (8 rows), `"refunded"` (4 rows)
- Contract enum: `[pending, confirmed, shipped, delivered, cancelled]`
- Root cause: New statuses added to order system without updating pipeline contract
- Fix: Update contract to add `processing` and `refunded`, or map them to existing statuses in transformer

---

### 🟡 WARNINGS

**PATTERN MISMATCH: `order_id` (2 rows)**
- Contract pattern: `^ORD-[0-9]{8}$`
- Got: `"ORD-123"` (row 88), `"ORD-9999-X"` (row 445)
- Likely test/legacy records — filter before production pipeline

---

### Drift Report (vs previous run 2026-03-17)

| Change | Field | Impact |
|--------|-------|--------|
| ➕ NEW FIELD | `refund_amount` | New field — add to contract |
| 🔄 TYPE CHANGED | `order_total` string → string (was float) | Breaking — see error above |
| 🔄 BECAME NULLABLE | `discount_code` | Was non-null, now null allowed — update contract or fix upstream |
| ➖ REMOVED FIELD | `legacy_channel` | Was in yesterday's output, missing today — check if intentional |

---

### Generated Contract (from this sample)

Based on the actual data, here is the inferred contract to use as a starting point:

```yaml
contract:
  name: orders-output
  version: "1.0"
  stage: orders_processor

  fields:
    order_id:
      type: string
      nullable: false
      pattern: "^ORD-[0-9]{8}$"
    customer_id:
      type: string
      nullable: true          # 8 nulls observed — confirm intent
    order_total:
      type: float
      nullable: false
      min: 0.01
    status:
      type: string
      nullable: false
      enum: [pending, confirmed, shipped, delivered, cancelled, processing, refunded]
    created_at:
      type: string            # datetime — add format: ISO8601 after confirming format
      nullable: false
    discount_code:
      type: string
      nullable: true
    refund_amount:
      type: float
      nullable: true          # New field — confirm semantics
```

---

### Fix Priority

```
1. Fix order_total string → float conversion in transformer (3 rows, crash risk)
2. Decide: guest checkout nulls → contract update or upstream fix (8 rows, silent corruption)
3. Add 'processing' and 'refunded' to status enum (12 rows, data loss risk)
4. Investigate legacy_channel removal (breaking change for downstream consumers?)
5. Update contract: add refund_amount field
```

---

### dbt Integration

If using dbt, add these tests to `models/schema.yml`:

```yaml
models:
  - name: orders_output
    columns:
      - name: order_id
        tests:
          - not_null
          - unique
      - name: customer_id
        tests:
          - not_null     # Remove if guest checkout is valid
      - name: order_total
        tests:
          - not_null
      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
```
```

---

## Quick Mode

Fast one-line summary for CI/CD checks:

```
Pipeline Contract: orders_processor → BROKEN
🔴 3 errors (type mismatch: order_total, unexpected nulls: customer_id, invalid enum: status)
🟡 2 warnings (pattern mismatch: order_id)
📈 1 new field (refund_amount) not in contract

Promote to next stage? NO — fix 3 errors first.
/pipeline-contract --validate for full report with row numbers and fix instructions
```

---

## CI/CD Integration

Use in automated pipelines to gate stage promotion:

```bash
# In a CI step after each pipeline stage runs:
# 1. Capture the output sample
head -n 100 pipeline/stage-2-output.json > /tmp/sample.json

# 2. Ask Claude to validate
# /pipeline-contract --validate /tmp/sample.json --contract contracts/stage-2.yaml

# 3. Exit 1 if contract is BROKEN to fail the CI check
# Claude will output: CONTRACT_STATUS=BROKEN or CONTRACT_STATUS=PASSING
```

---

## Comparison to Existing Tools

| Tool | Approach | When to use |
|------|---------|------------|
| **Great Expectations** | Python library, full test suite | Production pipelines with engineering team |
| **dbt tests** | YAML tests in dbt project | dbt-specific models only |
| **Soda Core** | Managed service, YAML scans | Teams with budget for managed data quality |
| **This skill** | Agent-native, zero config | One-off audits, local dev, design-time contract authoring, cross-team communication |

This skill fills the gap **before** you invest in a full data quality platform: understand your data's shape, write the contract, validate it locally. When you're ready to automate at scale, the contract YAML you generate here can be translated directly to Great Expectations or dbt tests.

---

## Why Contracts at Stage Boundaries

The classic pipeline failure mode:

```
Stage A outputs:   { "price": "12.99" }  ← string
Stage B expects:   { "price": 12.99 }    ← float

Stage B runs. No error thrown.
Aggregation: SUM("12.99" + "8.50") = "12.998.50" (string concat)
Dashboard shows: Revenue = $1.3M (should be $0.21M)
Discovery: 3 weeks later, in a board meeting.
```

A contract at the Stage A → Stage B boundary would have caught this in seconds.
