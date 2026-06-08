# Expressions & Interpolation Reference

## Variable Interpolation

### Syntax

`${{namespace.path.to.field}}`

Interpolation is resolved in two passes:

1. **Pass 1**: All non-secret variables (steps, inputs, workflow, context, loop)
2. **Pass 2**: Secrets via encrypted vault (`${{secrets.KEY}}`)

### Namespaces

| Namespace  | Syntax                              | Description                                   |
| ---------- | ----------------------------------- | --------------------------------------------- |
| `steps`    | `${{steps.<id>.output.<field>}}`    | Output from completed steps                   |
| `inputs`   | `${{inputs.<name>}}`                | Workflow input parameters                     |
| `workflow` | `${{workflow.<field>}}`             | Workflow metadata (run_id, etc.)              |
| `context`  | `${{context.<field>}}`              | Workflow context (intent, accumulated_data)   |
| `secrets`  | `${{secrets.<KEY>}}`                | Encrypted vault secrets (AES-256-GCM, PBKDF2) |
| `loop`     | `${{loop.item}}`, `${{loop.index}}` | Loop iteration variables                      |

### Deep Path Access

Nested field access: `${{steps.fetch.output.body.data.items[0].name}}`

The interpolation engine traverses map keys and supports JSON path-like access.

### Scope Isolation

- **Step outputs**: Immutable after step completion (frozen on insert)
- **Loop variables**: Scoped per iteration (child scope builder, isolated per body execution)
- **Parallel branches**: Isolated from siblings (separate scope copies, merged after all complete)
- **Resolution order**: step outputs -> workflow inputs -> secrets

## Expression Engines

### CEL (Common Expression Language)

Used for: condition step `expression`, step-level `condition` guards, loop `condition` (while/until).

**Available variables**:

| Variable   | Type           | Description                   |
| ---------- | -------------- | ----------------------------- |
| `steps`    | map[string]dyn | Step outputs keyed by step ID |
| `inputs`   | map[string]dyn | Workflow input params         |
| `workflow` | map[string]dyn | Workflow metadata             |
| `context`  | map[string]dyn | Workflow context              |
| `iter`     | map[string]dyn | Loop vars (item, index)       |

**IMPORTANT**: `loop` is a reserved keyword in CEL-Go. Use `iter.item` and `iter.index` in CEL expressions. The `${{loop.item}}` interpolation syntax still uses "loop".

**Examples**:

```plaintext
inputs.count > 10
steps.fetch.status_code == 200
steps.check.valid == true && inputs.mode == "strict"
iter.index < 5
iter.item.status == "active"
size(steps.list.items) > 0
```

**Type coercion**: CEL is type-safe. Numeric comparisons require same types. JSON numbers are typically `double` in CEL.

### GoJQ (jq for Go)

Used for: `over` field in for_each loops (producing iterable arrays), data transformation.

The entire interpolation scope is passed as input JSON object.

**Examples**:

```jq
# Extract names from a list
.steps.list.items | map(.name)

# Filter active records
[.steps.data.records[] | select(.active)]

# Simple JSON array literal
["a", "b", "c"]

# Transform with computation
.steps.data.items | map({key: .id, value: .name})
```

### Expr (expr-lang)

Used for: complex deterministic logic when CEL syntax is insufficient.

**Features**:

- Let bindings: `let x = expr; body`
- Array operations: `filter`, `map`, `count`, `any`, `all`, `sum`, `min`, `max`
- String operations: `contains`, `startsWith`, `endsWith`, `trim`, `upper`, `lower`
- Nil coalescing: `value ?? default`
- Optional chaining: `object?.field`
- Pipe chaining: `value | operation`
- Ternary: `condition ? then : else`

**Examples**:

```plaintext
len(items) > 0 && items[0].valid
count(items, {.status == "active"}) >= 3
sum(items, {.amount}) > 1000
value ?? "default"
data?.nested?.field
```

## Secret Vault

Secrets are stored encrypted at rest using AES-256-GCM with PBKDF2 key derivation (100,000 iterations).

- Store secrets via internal vault API (not exposed via MCP)
- Reference in step params: `${{secrets.API_KEY}}`
- Resolved in second interpolation pass (after all other variables)
- Secret values are never logged or persisted in event output
- Vault requires `OPCODE_VAULT_KEY` environment variable at server startup
