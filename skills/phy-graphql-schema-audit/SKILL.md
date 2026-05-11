---
name: phy-graphql-schema-audit
description: GraphQL schema static auditor. Reads any .graphql SDL file or introspection JSON to detect N+1 exposure hotspots (nested list-within-list queries with no dataloader hint), unbounded query depth vulnerabilities (no max depth limit configured), deprecated fields still used in operations, naming convention violations (types not PascalCase, fields not camelCase, enums not UPPER_SNAKE_CASE), circular type references, missing pagination on collection fields, and overly broad scalars (String fields that should be typed as ID, Email, or URL). Outputs a prioritized issue list with resolver-level fix suggestions and a query complexity budget recommendation. Zero external API — pure local file analysis. Triggers on "graphql schema", "graphql audit", "schema review", "N+1 graphql", "query depth", "graphql lint", "/graphql-schema-audit".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - graphql
    - schema
    - api-design
    - security
    - performance
    - developer-tools
    - n-plus-one
    - query-depth
---

# GraphQL Schema Auditor

Your GraphQL schema grew organically. You added fields as features shipped. Now a client can write a query that resolves 10,000 database calls — and your schema has no depth limit to stop them.

This skill reads your `.graphql` SDL files or introspection JSON, detects N+1 exposure, unbounded depth, naming violations, deprecated field drift, missing pagination, and overly broad scalar types — then gives you resolver-level fixes.

**Works with any GraphQL schema. Zero external API.**

---

## Trigger Phrases

- "graphql schema audit", "review my schema", "graphql lint"
- "N+1 in graphql", "graphql depth limit", "query complexity"
- "deprecated fields still used", "graphql naming conventions"
- "missing pagination graphql", "graphql security"
- "introspection json", "schema SDL"
- "/graphql-schema-audit"

---

## How to Provide Input

```bash
# Option 1: SDL file(s) — most common
/graphql-schema-audit schema.graphql
/graphql-schema-audit src/graphql/

# Option 2: Introspection JSON (from running server)
npx get-graphql-schema http://localhost:4000/graphql > schema.json
/graphql-schema-audit schema.json

# Option 3: Include operation files to check deprecated usage
/graphql-schema-audit --schema schema.graphql --operations src/queries/

# Option 4: Focus on a specific issue class
/graphql-schema-audit --check depth-limit
/graphql-schema-audit --check n-plus-one
/graphql-schema-audit --check naming

# Option 5: Generate query complexity config
/graphql-schema-audit --output complexity-config
```

---

## Step 1: Discover Schema Files

```bash
python3 -c "
import glob, os
from pathlib import Path

patterns = [
    '**/*.graphql',
    '**/*.graphqls',
    '**/*.gql',
    'schema.json',
    'introspection.json',
]

found = []
for pattern in patterns:
    found.extend(glob.glob(pattern, recursive=True))

# Filter
found = [f for f in found if 'node_modules' not in f and '.next' not in f]

if found:
    total_types = 0
    for f in found:
        size = os.path.getsize(f)
        print(f'{f} ({size:,} bytes)')
    print(f'\\nFound {len(found)} schema file(s)')
else:
    print('No GraphQL schema files found.')
    print('\\nTo get a schema from a running server:')
    print('  npx get-graphql-schema http://localhost:4000/graphql > schema.json')
    print('  OR: look for .graphql files in src/graphql/, src/schema/, or api/')
"
```

---

## Step 2: Parse the Schema

```python
import re
from pathlib import Path
from collections import defaultdict

def parse_graphql_schema(content):
    """Parse GraphQL SDL into typed objects."""

    # Extract type definitions
    types = {}
    type_pattern = re.compile(
        r'(type|interface|input|enum|union)\s+(\w+)(?:\s+implements\s+[\w\s&]+)?\s*\{([^}]+)\}',
        re.MULTILINE | re.DOTALL
    )

    for match in type_pattern.finditer(content):
        kind = match.group(1)
        name = match.group(2)
        body = match.group(3)

        fields = []
        deprecated_fields = []

        # Parse fields
        field_pattern = re.compile(
            r'^\s+(\w+)(?:\(([^)]*)\))?\s*:\s*([\w\[\]!]+)'
            r'(?:\s+@deprecated(?:\(reason:\s*"([^"]*)"\))?)?\s*$',
            re.MULTILINE
        )
        for field_match in field_pattern.finditer(body):
            field_name = field_match.group(1)
            field_args = field_match.group(2) or ''
            field_type = field_match.group(3)
            deprecated_reason = field_match.group(4)

            field_info = {
                'name': field_name,
                'type': field_type,
                'args': field_args,
                'is_list': '[' in field_type,
                'is_required': field_type.endswith('!'),
                'deprecated': deprecated_reason is not None,
                'deprecated_reason': deprecated_reason,
            }
            fields.append(field_info)
            if deprecated_reason is not None:
                deprecated_fields.append(field_name)

        types[name] = {
            'kind': kind,
            'name': name,
            'fields': fields,
            'deprecated_fields': deprecated_fields,
        }

    # Extract enum values
    enum_pattern = re.compile(r'enum\s+(\w+)\s*\{([^}]+)\}', re.MULTILINE | re.DOTALL)
    for match in enum_pattern.finditer(content):
        name = match.group(1)
        body = match.group(2)
        values = [line.strip() for line in body.splitlines() if line.strip() and not line.strip().startswith('#')]
        if name in types:
            types[name]['values'] = values

    return types


def load_schema(path):
    """Load schema from SDL file or introspection JSON."""
    import json

    content = Path(path).read_text(encoding='utf-8')

    if path.endswith('.json'):
        # Introspection JSON — extract SDL-like structure
        data = json.loads(content)
        schema_data = data.get('data', data).get('__schema', {})
        types_data = schema_data.get('types', [])

        # Convert to our internal format
        types = {}
        for t in types_data:
            if t['name'].startswith('__'):
                continue  # skip introspection types
            fields = []
            for f in (t.get('fields') or []):
                fields.append({
                    'name': f['name'],
                    'type': str(f.get('type', {})),
                    'is_list': f.get('type', {}).get('kind') == 'LIST',
                    'deprecated': f.get('isDeprecated', False),
                    'deprecated_reason': f.get('deprecationReason'),
                })
            types[t['name']] = {
                'kind': t.get('kind', 'OBJECT').lower(),
                'name': t['name'],
                'fields': fields,
                'deprecated_fields': [f['name'] for f in fields if f['deprecated']],
            }
        return types
    else:
        return parse_graphql_schema(content)
```

---

## Step 3: Detect Issues

### N+1 Exposure

```python
def detect_n_plus_one_risk(types):
    """
    Detect fields likely to cause N+1 queries:
    A list field on a type that is also returned within another list.
    e.g., Query.users: [User] + User.posts: [Post] = N+1 risk
    """
    risks = []

    # Find all list-returning fields
    list_fields = {}
    for type_name, type_def in types.items():
        for field in type_def.get('fields', []):
            if field['is_list']:
                # What type does this list contain?
                inner_type = field['type'].replace('[', '').replace(']', '').replace('!', '')
                if inner_type not in list_fields:
                    list_fields[inner_type] = []
                list_fields[inner_type].append((type_name, field['name']))

    # N+1 risk: type T has list fields AND T appears in another list
    for type_name, type_def in types.items():
        if type_name in list_fields and type_def['kind'] == 'type':
            # This type is returned in lists
            parent_lists = list_fields[type_name]
            # And it also has list fields itself
            own_list_fields = [
                f for f in type_def.get('fields', [])
                if f['is_list']
            ]
            if own_list_fields and parent_lists:
                for parent_type, parent_field in parent_lists:
                    for nested_field in own_list_fields:
                        risks.append({
                            'query_path': f'{parent_type}.{parent_field} → {type_name}.{nested_field["name"]}',
                            'description': (
                                f'Fetching {parent_type}.{parent_field} returns N {type_name} objects. '
                                f'Each {type_name}.{nested_field["name"]} triggers an additional query → N+1.'
                            ),
                            'fix': (
                                f'Add a DataLoader for {type_name}.{nested_field["name"]} resolver. '
                                f'Batch-load {nested_field["name"]} by {type_name} IDs.'
                            ),
                            'severity': 'HIGH',
                        })

    return risks
```

### Query Depth Vulnerability

```python
def detect_depth_vulnerability(types, max_safe_depth=5):
    """
    Check if the schema allows recursive or very deep query paths.
    """
    issues = []

    # Detect circular references
    def find_cycles(type_name, visited=None, path=None):
        if visited is None:
            visited = set()
        if path is None:
            path = []

        if type_name in visited:
            return [path + [type_name]]
        if type_name not in types:
            return []

        visited = visited | {type_name}
        cycles = []
        for field in types[type_name].get('fields', []):
            inner_type = field['type'].replace('[', '').replace(']', '').replace('!', '')
            if inner_type in types and types[inner_type]['kind'] == 'type':
                cycles.extend(find_cycles(inner_type, visited, path + [type_name]))
        return cycles

    for type_name in types:
        if types[type_name]['kind'] == 'type':
            cycles = find_cycles(type_name)
            for cycle in cycles:
                if len(cycle) > 1:
                    issues.append({
                        'type': 'CIRCULAR_REFERENCE',
                        'path': ' → '.join(cycle),
                        'description': 'Circular type reference enables infinite-depth queries.',
                        'fix': (
                            'Add query depth limiting via graphql-depth-limit or '
                            'graphql-query-complexity. '
                            'Example: depthLimit(7) in your server middleware.'
                        ),
                        'severity': 'HIGH',
                    })

    return issues


def check_depth_limit_configured(schema_dir):
    """Check if depth limiting middleware is configured."""
    import glob

    depth_limit_patterns = [
        'graphql-depth-limit',
        'graphql-query-complexity',
        'depthLimit',
        'queryComplexity',
        'createComplexityLimitRule',
    ]

    source_files = glob.glob('src/**/*.{js,ts}', recursive=True)
    source_files += glob.glob('**/*.{js,ts}', recursive=True)

    for fpath in source_files[:100]:  # Sample first 100 files
        try:
            content = open(fpath).read()
            for pattern in depth_limit_patterns:
                if pattern in content:
                    return True, fpath
        except Exception:
            continue

    return False, None
```

### Naming Convention Violations

```python
import re

def check_naming_conventions(types):
    """
    GraphQL naming best practices:
    - Types, Interfaces, Enums: PascalCase
    - Fields, Arguments: camelCase
    - Enum values: UPPER_SNAKE_CASE
    - Input types: suffix with 'Input'
    - Mutations: verb-first (createUser, deletePost)
    """
    violations = []

    pascal_re = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
    camel_re = re.compile(r'^[a-z][a-zA-Z0-9]*$')
    upper_snake_re = re.compile(r'^[A-Z][A-Z0-9_]*$')

    for type_name, type_def in types.items():
        if type_name.startswith('__'):
            continue

        # Types should be PascalCase
        if type_def['kind'] in ['type', 'interface', 'enum', 'union']:
            if not pascal_re.match(type_name):
                violations.append({
                    'location': f'Type: {type_name}',
                    'issue': f'Type name "{type_name}" should be PascalCase',
                    'fix': f'Rename to {type_name[0].upper() + type_name[1:]}',
                    'severity': 'LOW',
                })

        # Input types should end with Input
        if type_def['kind'] == 'input' and not type_name.endswith('Input'):
            violations.append({
                'location': f'Input: {type_name}',
                'issue': f'Input type "{type_name}" should end with "Input" (e.g., {type_name}Input)',
                'fix': f'Rename to {type_name}Input',
                'severity': 'LOW',
            })

        # Fields should be camelCase
        for field in type_def.get('fields', []):
            if not camel_re.match(field['name']) and not field['name'].startswith('_'):
                violations.append({
                    'location': f'{type_name}.{field["name"]}',
                    'issue': f'Field "{field["name"]}" should be camelCase',
                    'fix': f'Rename to {re.sub(r"_([a-z])", lambda m: m.group(1).upper(), field["name"])}',
                    'severity': 'LOW',
                })

        # Enum values should be UPPER_SNAKE_CASE
        if type_def['kind'] == 'enum':
            for value in type_def.get('values', []):
                if not upper_snake_re.match(value):
                    violations.append({
                        'location': f'{type_name}.{value}',
                        'issue': f'Enum value "{value}" should be UPPER_SNAKE_CASE',
                        'fix': f'Rename to {re.sub(r"([a-z])([A-Z])", r"\\1_\\2", value).upper()}',
                        'severity': 'LOW',
                    })

    return violations
```

### Missing Pagination

```python
def detect_missing_pagination(types):
    """
    Collection fields that return [Type] directly instead of Connection pattern.
    Query.users: [User]  ← BAD (no cursor, no count, can return millions)
    Query.users: UserConnection  ← GOOD
    """
    issues = []

    EXCLUDED_LIST_FIELDS = {'__schema', '__type', '__enumValues'}

    for type_name, type_def in types.items():
        if type_name in ('Query', 'Subscription'):
            for field in type_def.get('fields', []):
                if field['is_list']:
                    inner_type = field['type'].replace('[', '').replace(']', '').replace('!', '')
                    # Check if it uses Connection pattern
                    if not (inner_type.endswith('Connection') or inner_type.endswith('Edge')):
                        # Check if args include pagination hints
                        args = field.get('args', '')
                        has_pagination = any(
                            hint in args.lower()
                            for hint in ['first', 'last', 'after', 'before', 'limit', 'offset', 'page', 'cursor']
                        )
                        if not has_pagination:
                            issues.append({
                                'location': f'{type_name}.{field["name"]}',
                                'type_returned': inner_type,
                                'issue': (
                                    f'{type_name}.{field["name"]} returns [{inner_type}] '
                                    f'with no pagination args — can return unbounded results.'
                                ),
                                'fix': (
                                    f'Add pagination args: {field["name"]}(first: Int, after: String): {inner_type}Connection\n'
                                    f'  OR add limit/offset: {field["name"]}(limit: Int = 20, offset: Int = 0): [{inner_type}]'
                                ),
                                'severity': 'MEDIUM',
                            })

    return issues
```

### Overly Broad Scalars

```python
def detect_broad_scalars(types):
    """
    String fields that should use custom scalars for better type safety.
    """
    issues = []

    # Field name patterns that suggest a more specific scalar
    SCALAR_HINTS = {
        re.compile(r'\bid\b', re.I): ('ID', 'Use ID scalar for identifier fields'),
        re.compile(r'email', re.I): ('Email', 'Use Email scalar (or String with validation)'),
        re.compile(r'url|uri|link|href', re.I): ('URL', 'Use URL scalar for link fields'),
        re.compile(r'date|time|at$|_at$', re.I): ('DateTime', 'Use DateTime scalar (ISO 8601)'),
        re.compile(r'uuid|guid', re.I): ('UUID', 'Use UUID scalar for UUID fields'),
        re.compile(r'json|metadata|data|payload', re.I): ('JSON', 'Use JSON scalar instead of opaque String'),
        re.compile(r'phone|mobile', re.I): ('String @constraint', 'Add phone format constraint'),
    }

    for type_name, type_def in types.items():
        if type_name.startswith('__'):
            continue
        for field in type_def.get('fields', []):
            raw_type = field['type'].replace('[', '').replace(']', '').replace('!', '')
            if raw_type == 'String':
                for pattern, (suggested_scalar, reason) in SCALAR_HINTS.items():
                    if pattern.search(field['name']):
                        issues.append({
                            'location': f'{type_name}.{field["name"]}: String',
                            'issue': f'Field "{field["name"]}" typed as String — likely should be {suggested_scalar}',
                            'fix': f'Change to {suggested_scalar} scalar. {reason}.',
                            'severity': 'LOW',
                        })
                        break  # only report once per field

    return issues
```

---

## Step 4: Output Report

```markdown
## GraphQL Schema Audit
Schema: schema.graphql | Types: 34 | Fields: 187

---

### Summary

| Issue Class | Count | Severity |
|-------------|-------|---------|
| N+1 Exposure Hotspots | 3 | 🔴 HIGH |
| Unbounded Query Depth (circular refs) | 2 | 🔴 HIGH |
| Missing Pagination | 5 | 🟠 MEDIUM |
| Overly Broad Scalars | 11 | 🟡 LOW |
| Naming Violations | 4 | 🟡 LOW |
| Deprecated Fields in Use | 2 | 🟡 LOW |

---

### 🔴 N+1 Exposure Hotspots

**1. Query.users → User.posts**
```
Fetching Query.users returns N User objects.
Each User.posts resolver triggers a SELECT on posts WHERE user_id = ? → N+1.

Current schema:
  type Query { users: [User]! }
  type User  { id: ID!, posts: [Post]! }

Fix: Add DataLoader in posts resolver:
  const userPostsLoader = new DataLoader(async (userIds) => {
    const posts = await Post.findAll({ where: { userId: userIds } });
    return userIds.map(id => posts.filter(p => p.userId === id));
  });
```

**2. Query.organizations → Organization.members → Member.assignments**
```
3-level N+1: 1 query for orgs, N queries for members per org,
N×M queries for assignments per member.

Fix: DataLoader at each level OR use batch-resolve with JOIN in Organization resolver.
```

---

### 🔴 Circular References (Depth Vulnerability)

**User → Post → Comment → User** (cycle length 3)
```
Allows: { user { posts { comments { author { posts { comments { ... } } } } } } }
An attacker can write an arbitrarily deep query — no depth limit = DoS risk.

Fix (add to server setup):
  import depthLimit from 'graphql-depth-limit'

  const server = new ApolloServer({
    validationRules: [depthLimit(7)],
    ...
  })

  // OR with complexity limiting (recommended):
  import { createComplexityLimitRule } from 'graphql-query-complexity'
  validationRules: [createComplexityLimitRule(1000)]
```

**⚠️ Depth limit NOT configured** — searched src/ for `depthLimit`, `queryComplexity` — not found.

---

### 🟠 Missing Pagination (5 fields)

| Field | Returns | Issue |
|-------|---------|-------|
| Query.users | [User] | No limit/offset args |
| Query.products | [Product] | No cursor pagination |
| Query.orders | [Order] | No pagination — high-volume table |
| User.notifications | [Notification] | No limit — could be thousands |
| Organization.auditLogs | [AuditLog] | No pagination — grows unboundedly |

**Fix for Query.users:**
```graphql
# Before
type Query {
  users: [User]!
}

# After (Relay-style Connection)
type Query {
  users(first: Int = 20, after: String): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}
```

---

### 🟡 Overly Broad Scalars (sample)

| Field | Current Type | Should Be | Reason |
|-------|-------------|-----------|--------|
| User.email | String | Email | String allows "not-an-email" |
| Order.createdAt | String | DateTime | Use ISO 8601 scalar |
| Product.thumbnail | String | URL | Validate URL format |
| User.uuid | String | ID or UUID | Use typed identifier |
| Event.metadata | String | JSON | Opaque JSON blob |

**Add custom scalars:**
```graphql
scalar DateTime  # ISO 8601
scalar Email     # RFC 5322
scalar URL       # RFC 3986
scalar JSON      # Arbitrary JSON

# Then use: npm install graphql-scalars
import { DateTimeResolver, EmailAddressResolver, URLResolver } from 'graphql-scalars'
```

---

### 🟡 Naming Violations

| Location | Issue | Fix |
|----------|-------|-----|
| Type: user_profile | Not PascalCase | → UserProfile |
| OrderStatus enum: pending | Not UPPER_SNAKE_CASE | → PENDING |
| Input: CreateOrder | Missing Input suffix | → CreateOrderInput |
| Mutation.user_create | Not camelCase | → createUser |

---

### Deprecated Fields Still Used

```
Field: User.legacyToken @deprecated(reason: "Use authToken instead")
Found in operations:
  src/queries/auth.graphql:12 — uses User.legacyToken
  src/components/Profile.tsx:34 — uses User.legacyToken

Action: Update these files to use User.authToken
Deadline: Remove legacyToken resolver after migration
```

---

### Query Complexity Configuration

Recommended settings for this schema:

```js
// apollo-server or graphql-yoga
import { createComplexityLimitRule } from 'graphql-query-complexity'
import depthLimit from 'graphql-depth-limit'

const complexityLimit = createComplexityLimitRule(1000, {
  scalarCost: 1,
  objectCost: 2,
  listFactor: 10,  // each list field multiplies cost by 10
})

const server = new ApolloServer({
  validationRules: [
    depthLimit(7),    // max 7 levels deep
    complexityLimit,  // max complexity score 1000
  ],
})
```

With this config, `{ users { posts { comments { author { name } } } } }` costs:
`10 × 10 × 10 × 2 + scalars = 2,000+` → rejected before execution.
```

---

## Quick Mode Output

```
GraphQL Schema Audit: schema.graphql (34 types, 187 fields)

🔴 3 N+1 hotspots — add DataLoader for User.posts, Organization.members, Member.assignments
🔴 2 circular refs — User→Post→Comment→User cycle; NO depth limit configured (DoS risk!)
🟠 5 unpaginated list fields — Query.users, Query.products, Query.orders, User.notifications, Organization.auditLogs
🟡 11 overly broad String scalars — use DateTime, Email, URL, JSON
🟡 4 naming violations — user_profile, pending, CreateOrder, user_create
🟡 2 deprecated fields still used in operations

Priority fix: Add depthLimit(7) to your server validation rules NOW (1 line change)
Then: DataLoader for User.posts and User.notifications (highest traffic N+1s)
```
