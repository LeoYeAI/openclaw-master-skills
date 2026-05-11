# The Graph Subgraph — Auto-Generated Query Patterns Reference

This document describes everything The Graph's graph-node auto-generates from a subgraph's `schema.graphql` file. Given a minimal entity schema, an LLM agent can use these patterns to construct any valid query without needing the full introspection result.

---

## When to use subgraphs vs RPC

**Prefer RPC over subgraph for current state.** The subgraph only updates on
transactions, but Superfluid state changes continuously (streams flow every
second). Balances, flow rates, and distribution states on the subgraph are
always behind. This is especially true for GDA and IDA — their 1-to-many and
N-to-many primitives are built for scalability: a distribution to millions of
pool members updates only the Pool entity on-chain (one event), so individual
PoolMember records on the subgraph won't reflect the new state until each
member transacts. Use `cast call` or `scripts/balance.mjs` for real-time
reads. The subgraph is best for historical queries, event indexing, and
listing/filtering entities.

---

## 1. Scalar Types

The Graph supports these scalar types (beyond standard GraphQL `String`, `Int`, `Boolean`, `ID`):

- `Bytes` — Hex-encoded byte string (e.g. Ethereum address). Value: `"0xabc123..."`
- `BigInt` — Arbitrary-precision integer. Value: `"1000000000000000000"` (string)
- `BigDecimal` — Arbitrary-precision decimal. Value: `"10.99"` (string)
- `Int` — 32-bit signed integer. Value: `42`
- `Int8` — 8-bit signed integer (stored as Int8 in DB). Value: `127`
- `Timestamp` — Nanosecond-precision timestamp. Value: `"1609459200000000000"` (string)
- `String` — UTF-8 text. Value: `"hello"`
- `Boolean` — True/false. Value: `true` / `false`
- `ID` — Unique entity identifier. Value: `"0x..."` or any string

> **Note**: `BigInt`, `BigDecimal`, `Bytes`, and `Timestamp` are always passed as **quoted strings** in queries.

---

## 2. Auto-Generated Query Fields Per Entity

For each `@entity` type, graph-node generates two root query fields:

```graphql
# Given:
type Token @entity {
  id: ID!
  symbol: String!
  totalSupply: BigInt!
}

# Auto-generated root Query fields:
type Query {
  # Single entity lookup by id
  token(
    id: ID!
    block: Block_height
    subgraphError: _SubgraphErrorPolicy_! = deny
  ): Token

  # Collection query with full filtering/sorting/pagination
  tokens(
    skip: Int = 0
    first: Int = 100
    orderBy: Token_orderBy
    orderDirection: OrderDirection
    where: Token_filter
    block: Block_height
    subgraphError: _SubgraphErrorPolicy_! = deny
  ): [Token!]!
}
```

### Naming Convention

- `Token` → singular: `token(id: ...)`, plural: `tokens(...)`, filter: `Token_filter`, orderBy: `Token_orderBy`
- `Stream` → singular: `stream(id: ...)`, plural: `streams(...)`, filter: `Stream_filter`, orderBy: `Stream_orderBy`
- `FlowUpdatedEvent` → singular: `flowUpdatedEvent(id: ...)`, plural: `flowUpdatedEvents(...)`, filter: `FlowUpdatedEvent_filter`, orderBy: `FlowUpdatedEvent_orderBy`

The plural form follows standard English pluralization (entity → entities, etc.), but for most camelCase names it simply appends `s`.

---

## 3. Global Types (Always Present)

```graphql
enum OrderDirection {
  asc
  desc
}

input Block_height {
  hash: Bytes
  number: Int
  number_gte: Int
}

enum _SubgraphErrorPolicy_ {
  allow   # Return data even if there were indexing errors
  deny    # (default) Fail if there were indexing errors
}

# Metadata query
type _Meta_ {
  block: _Block_!
  deployment: String!
  hasIndexingErrors: Boolean!
}

type _Block_ {
  hash: Bytes
  number: Int!
  timestamp: Int
  parentHash: Bytes
}
```

---

## 4. Filter Operators by Type

For each field on an entity, graph-node generates filter input fields on the `Entity_filter` type using **suffix conventions**. Which suffixes are available depends on the field's scalar type.

### Complete Operator Reference

**All types:** _(none)_ = equals, `_not`, `_in`, `_not_in`

**Numeric¹, String, Bytes, ID:** `_gt`, `_lt`, `_gte`, `_lte`

**String, Bytes:** `_contains` (case-sensitive), `_not_contains`, `_starts_with`, `_not_starts_with`, `_ends_with`, `_not_ends_with`

**String only (+ `_nocase` variants):** `_contains_nocase`, `_not_contains_nocase`, `_starts_with_nocase`, `_not_starts_with_nocase`, `_ends_with_nocase`, `_not_ends_with_nocase`

**Entity/interface refs:** `_` (nested filter using the referenced entity's `_filter` type)

¹ Numeric = `Int`, `Int8`, `BigInt`, `BigDecimal`, `Timestamp`

### Per-Type Summary

- **Boolean** — `_not`, `_in`, `_not_in`
- **Int / Int8** — `_not`, `_gt`, `_lt`, `_gte`, `_lte`, `_in`, `_not_in`
- **BigInt / BigDecimal / Timestamp** — `_not`, `_gt`, `_lt`, `_gte`, `_lte`, `_in`, `_not_in`
- **String / ID** — `_not`, `_gt`, `_lt`, `_gte`, `_lte`, `_in`, `_not_in`, `_contains`, `_contains_nocase`, `_not_contains`, `_not_contains_nocase`, `_starts_with`, `_starts_with_nocase`, `_not_starts_with`, `_not_starts_with_nocase`, `_ends_with`, `_ends_with_nocase`, `_not_ends_with`, `_not_ends_with_nocase`
- **Bytes** — `_not`, `_gt`, `_lt`, `_gte`, `_lte`, `_in`, `_not_in`, `_contains`, `_not_contains`, `_starts_with`, `_not_starts_with`, `_ends_with`, `_not_ends_with`
- **Entity ref** — `_` (nested filter using the referenced entity's `_filter` type)
- **List/Array** — `_contains`, `_contains_nocase`, `_not_contains`, `_not_contains_nocase` (checks list membership)

> **Bytes note**: `Bytes` gets the string-like prefix/suffix/contains operators, but **not** the `_nocase` variants, since hex comparisons are inherently case-insensitive in graph-node (addresses are normalized to lowercase).

### Logical Operators (inside any `_filter`)

```graphql
input Token_filter {
  # All field-level filters...
  
  # Logical combinators
  and: [Token_filter]
  or: [Token_filter]
  
  # Block change filter
  _change_block: BlockChangedFilter
}

input BlockChangedFilter {
  number_gte: Int!
}
```

**Syntactic sugar**: Multiple conditions at the top level of `where` are implicitly ANDed:
```graphql
# These are equivalent:
where: { and: [{ symbol: "DAI" }, { totalSupply_gt: "0" }] }
where: { symbol: "DAI", totalSupply_gt: "0" }
```

---

## 5. OrderBy Enum

For each entity, an enum is generated with one value per field (including nested one-level-deep traversal for `String`/`ID` fields on related entities):

```graphql
# Given:
type Token @entity {
  id: ID!
  symbol: String!
  totalSupply: BigInt!
  owner: Account!
}

# Auto-generated:
enum Token_orderBy {
  id
  symbol
  totalSupply
  owner           # Sort by owner's id
  owner__id       # Explicit nested: sort by owner.id
  owner__name     # Sort by owner.name (if Account has a name: String field)
}
```

> **Nested sorting**: Only supports one level deep, and only on `String` or `ID` type fields of the related entity.

Usage:
```graphql
{ tokens(orderBy: totalSupply, orderDirection: desc, first: 10) { id symbol } }
```

---

## 6. Pagination

- **`first`**: Number of results to return (default: 100, max: 1000)
- **`skip`**: Number of results to skip (default: 0) — **avoid for large offsets, poor performance**
- **Cursor-based pagination** (recommended for large datasets):
  ```graphql
  query($lastID: String) {
    tokens(first: 1000, where: { id_gt: $lastID }, orderBy: id, orderDirection: asc) {
      id
      symbol
    }
  }
  ```

---

## 7. Time-Travel Queries (Historical State)

Query entity state at a specific block:

```graphql
# By block number
{ tokens(block: { number: 15000000 }) { id symbol totalSupply } }

# By block hash
{ tokens(block: { hash: "0xabc..." }) { id symbol totalSupply } }

# "At least this block" — useful for consistency when subgraph might be behind
{ tokens(block: { number_gte: 15000000 }) { id symbol totalSupply } }
```

---

## 8. Full-Text Search

Only available if explicitly defined in `subgraph.yaml` with `@fulltext` directive in the schema. If present, generates a dedicated query field:

```graphql
# Schema definition:
type _Schema_
  @fulltext(
    name: "tokenSearch"
    language: en
    algorithm: rank
    include: [{ entity: "Token", fields: [{ name: "symbol" }, { name: "name" }] }]
  )

# Auto-generated query:
tokenSearch(text: String!, first: Int, skip: Int): [TokenSearch!]!
```

Full-text operators (used within the `text` argument string):

- AND `&` — `"super & fluid"`
- OR `|` — `"super | fluid"`
- Follow by (proximity) `<->` — `"super <-> fluid"`
- Prefix match `:*` — `"super:*"`

---

## 9. Subgraph Metadata

Always available:

```graphql
{
  _meta {
    block {
      number
      hash
      timestamp
    }
    deployment
    hasIndexingErrors
  }
}
```

---

## 10. Derived Fields (`@derivedFrom`)

Fields with `@derivedFrom` are **virtual reverse lookups** — they don't create a stored column but instead generate a query that filters the related entity:

```graphql
# In schema:
type Account @entity {
  id: ID!
  tokens: [Token!]! @derivedFrom(field: "owner")
}

type Token @entity {
  id: ID!
  owner: Account!
}
```

When querying `account.tokens`, it's equivalent to querying `tokens(where: { owner: accountId })`. These derived fields support their own sub-selection with `first`, `skip`, `orderBy`, `orderDirection`, and `where`:

```graphql
{
  account(id: "0x...") {
    id
    tokens(first: 10, orderBy: totalSupply, orderDirection: desc) {
      id
      symbol
    }
  }
}
```

---

## 11. Nested Entity Filtering (`_` suffix)

Filter parent entities based on properties of their related entities:

```graphql
# Find all tokens owned by a specific account
{
  tokens(where: { owner_: { id: "0xabc..." } }) {
    id
    symbol
    owner { id }
  }
}
```

This generates a SQL JOIN under the hood. Can be nested but performance degrades.

---

## 12. Recommended: Type-Safe Client with Graph Client CLI

For production use, The Graph provides **`@graphprotocol/client-cli`** — a build-time tool that generates a type-safe client from your subgraph endpoint. It introspects the schema, generates TypeScript types for all entities/filters/enums, and produces a ready-to-use `execute` function.

**Docs**: https://thegraph.com/docs/en/subgraphs/querying/graph-client/README/
**Repo**: https://github.com/graphprotocol/graph-client

### Setup

```bash
npm install --save-dev @graphprotocol/client-cli
```

### Configuration (`.graphclientrc.yml`)

```yaml
sources:
  - name: protocol
    handler:
      graphql:
        endpoint: '{context.url:https://subgraph-endpoints.superfluid.dev/base-mainnet/protocol-v1}'
documents:
  - './**/*.graphql'
codegen:
  scalars:
    BigInt: string
    Bytes: string
    BigDecimal: string
```

> **Scalar typing matters**: By default, the codegen types custom scalars as `any`, which defeats the purpose of type safety. Always map `BigInt`, `Bytes`, and `BigDecimal` to `string` — that's what they actually are in GraphQL query/response payloads.

### Build & Use

```bash
# Generate the typed client artifact into .graphclient/
npx graphclient build

# Interactive GraphiQL for testing queries
npx graphclient serve-dev
```

```typescript
import { execute } from '../.graphclient'

const result = await execute(myQuery, { sender: "0xabc..." })
// result is fully typed based on your query
```

### Key Features

- **Auto-pagination**: Transparently fetches beyond the 1000-entity limit via multiple requests
- **Block tracking**: Automatically follows the polling pattern for consistent reads
- **Fetch strategies**: `fallback`, `race`, `retry`, `timeout`, `highestValue` — for multi-indexer resilience
- **Runtime endpoint override**: Use `{context.url:defaultUrl}` in config, then pass a different URL at runtime via the execute context
- **Integrates with**: Apollo Client, urql, React Query, or standalone

---

## 13. Superfluid-Specific Gotchas

These pitfalls apply across all Superfluid subgraphs.

### Addresses Must Be Lowercased

All subgraphs store addresses in lowercase. Queries are **case-sensitive**. Always `.toLowerCase()` addresses before using them in `where` clauses.

```
WRONG:  { sender: "0xAbC123..." }
RIGHT:  { sender: "0xabc123..." }
```

### Do NOT Use `_nocase` Filter Suffix for Bytes Arrays

The `_nocase` filter operators (e.g., `addresses_contains_nocase`) are **broken** on The Graph Network's decentralized indexer for `Bytes` array fields. Always use the case-sensitive variants and lowercase your input instead.

```
BROKEN: { addresses_contains_nocase: ["0xAbC..."] }
RIGHT:  { addresses_contains: ["0xabc..."] }
```

### Timestamp Fields Are Safe for `Number()`

Timestamp fields in all Superfluid subgraphs are Unix timestamps (seconds). They fit safely in JavaScript's `Number` type — no need for `BigInt` parsing.

### Event `addresses` Field Is Ambiguous

The `addresses` field on protocol events contains **both** account addresses and token addresses. When filtering by `addresses_contains`, you may match on either type. There is no way to filter only by account or only by token through this field alone.

---

## 14. References & Versioning

This document describes the query API as implemented by **graph-node** (the reference Graph Protocol indexer). The auto-generated schema patterns are defined in the graph-node source code, not in a standalone spec document.

### Key Sources

- **Official GraphQL API docs** — https://thegraph.com/docs/en/subgraphs/querying/graphql-api/
- **Graph Client CLI docs** — https://thegraph.com/docs/en/subgraphs/querying/graph-client/README/
- **graph-node repository** — https://github.com/graphprotocol/graph-node
- **Schema generation source** — `graph-node/graphql/src/schema/api.rs` — this is where filter suffixes, orderBy enums, and query field signatures are generated from entity definitions
- **Subgraph spec (GraphQL schema)** — https://github.com/graphprotocol/graph-node/blob/master/docs/subgraph-manifest.md
- **AssemblyScript API (scalar types)** — https://thegraph.com/docs/en/developing/assemblyscript-api/

### Version Context

- **Document written**: February 2026
- **graph-node version context**: v0.35.x+ (logical `and`/`or` operators available since v0.30.0; nested entity filtering with `_` suffix available since v0.30.0; `Int8` and `Timestamp` scalars are newer additions)
- **Spec version**: subgraph manifests using `specVersion: 1.3.0`

### Notable Changes Over Time

- graph-node v0.30.0 — Added `and` / `or` logical operators in `where` filters
- graph-node v0.30.0 — Added nested entity filtering (`_` suffix)
- graph-node v0.32.0+ — Added `Int8` scalar type
- graph-node v0.34.0+ — Added `Timestamp` scalar type
- Ongoing — `_nocase` string filter variants added incrementally

> **If the generated schema ever changes**: Run an introspection query against a live subgraph endpoint to verify. The authoritative source of truth is always the `api.rs` file in graph-node, which programmatically builds the schema from entity definitions.
