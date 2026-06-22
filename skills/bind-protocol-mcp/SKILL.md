---
name: bind-mcp
description: Bind Protocol MCP server for credential verification, policy authoring, and zero-knowledge proof generation.
version: 2.0.0
metadata:
  openclaw:
    requires:
      env:
        - BIND_API_KEY
      bins:
        - node
        - npx
    primaryEnv: BIND_API_KEY
    homepage: https://docs.bindprotocol.xyz/mcp/overview
    install:
      - kind: node
        package: "@bind-protocol/mcp-server"
        bins: []
---

# Bind MCP Server — Agent Skill Guide

You have access to the Bind Protocol MCP server. This document teaches you how to use it.

## Prerequisites & Installation

### Requirements

- **Node.js >= 18** — Required to run the server (`npx` handles package installation automatically)
- **Bind account** — Required for API-backed tools. Create one at https://dashboard.bindprotocol.xyz
- **Agent key** (`idbr_agent_...`) — Required for API-backed tools. Regular API keys (`idbr_`) are not supported for MCP.

### Credential Setup

Bind uses **agent keys** for MCP authentication. Agent keys are scoped API keys that let org admins control exactly which tools are available, set daily rate limits, and get audit logs.

| Key type | Format | MCP supported |
|----------|--------|---------------|
| **Agent key** | `idbr_agent_<keyId>_<secret>` | Yes — required for API-backed tools |
| **Regular API key** | `idbr_<keyId>_<secret>` | No — rejected by MCP server |

To create an agent key:
1. Sign in at https://dashboard.bindprotocol.xyz
2. Navigate to **Settings > Agent Keys**
3. Select which tool categories the key can access (e.g., credential verification only, or policy authoring + verification)
4. Copy the key — it is shown only once

### MCP Server Configuration

Add the server to your MCP client configuration. The exact file depends on your tool:

| Tool | Config file |
|------|------------|
| Claude Code | `.mcp.json` in your project root, or `~/.claude/claude_desktop_config.json` |
| Claude Desktop | Settings > Developer > Edit Config |
| Cursor | `.cursor/mcp.json` in your project root |
| Windsurf | MCP settings |

**Configuration JSON:**

```json
{
  "mcpServers": {
    "bind": {
      "command": "npx",
      "args": ["@bind-protocol/mcp-server"],
      "env": {
        "BIND_API_KEY": "${BIND_API_KEY}"
      }
    }
  }
}
```

The `BIND_API_KEY` environment variable must be set in your shell to your agent key before launching your AI tool. **Never hardcode the key directly in config files** — always use environment variable references to avoid accidental credential leakage in shared configs or repositories.

**Environment variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BIND_API_KEY` | For API-backed tools | — | Agent key (`idbr_agent_...`). Without this, only local tools are available. |
| `BIND_API_URL` | No | `https://api.bindprotocol.xyz` | Base URL for API calls |
| `BIND_RECEIPTS_PATH` | No | `~/.bind/receipts` | Directory for receipt chain data |
| `LOG_LEVEL` | No | `info` | Logging verbosity (`debug`, `info`, `warn`, `error`) |

### Verifying the Setup

If you do not have `bind` tools available, prompt the user to complete the setup above. You can test connectivity by calling `bind_whoami` — if it returns org info, the agent key is authenticated. Without a `BIND_API_KEY`, only local tools (parse, verify, hash) are available.

---

## Architecture & Data Flow

The server runs locally via `npx` and communicates with your AI tool over stdio. It provides both local tools (always available) and API-backed tools (require an agent key). You just call the tool by name — routing is handled automatically.

| Tool type | Auth | Purpose |
|-----------|------|---------|
| **Local tools** | None | Parse, verify, and hash VC-JWTs on-device |
| **API-backed tools** | Agent key via `BIND_API_KEY` | Policies, proofs, issuers, revocation, and more |

### What stays local vs. what calls the API

This is critical for understanding the privacy model:

**Local tools (credential data NEVER leaves the machine):**
- `bind_parse_credential` — Decodes the JWT entirely on your machine
- `bind_verify_credential` — Fetches the issuer's public JWKS from the Bind API (public keys only), then verifies the signature locally. The credential itself is never sent.
- `bind_hash_credential` — Computes a SHA-256 hash locally. Only the irreversible hash is used for revocation checks.

**API-backed tools (send requests to `api.bindprotocol.xyz`):**
- `bind_check_revocation` — Sends only the credential **hash** (not the credential). The hash is not reversible.
- `bind_resolve_issuer` — Fetches public keys for an org. No credential data involved.
- `bind_explain_policy`, `bind_list_policies`, `bind_list_circuits` — Read-only public metadata. No credential data involved.
- `bind_submit_prove_job` — Sends circuit inputs to the Bind proving service. These are the raw values being proven (e.g., income amount, mileage count).
- `bind_issue_credential` — Requests the Bind API to sign and issue a VC-JWT from a completed proof.
- `bind_create_policy`, `bind_validate_policy` — Sends policy spec JSON to Bind for validation/storage.
- `bind_share_proof` — Shares a proof record with a verifier org via the Bind API.

**In short:** Raw credentials are local-only. Hashes, policy specs, proof inputs, and metadata go to the API.

---

## Tool Inventory

### Local Tools (no auth required, credential data stays on-machine)

| Tool | What it does |
|------|-------------|
| `bind_parse_credential` | Decode a VC-JWT into header + payload + signature without verification |
| `bind_verify_credential` | Full verification: parse, fetch issuer JWKS, verify ES256 signature, check expiration. Does NOT check revocation. |
| `bind_hash_credential` | SHA-256 hash a VC-JWT. Use the hash with `bind_check_revocation`. |

### API-Backed Tools (require agent key via `BIND_API_KEY`)

**Discovery & Inspection**

| Tool | What it does |
|------|-------------|
| `bind_resolve_issuer` | Fetch an org's public signing keys (JWKS) by org ID |
| `bind_explain_policy` | Get the public spec for a policy by policy ID |
| `bind_check_revocation` | Check if a credential is revoked by its hash (hash only — not the credential) |
| `bind_list_policies` | List available policies (supports `limit`/`offset` pagination) |
| `bind_list_circuits` | List available ZK circuits |

**Proof Generation & Credential Issuance**

| Tool | What it does |
|------|-------------|
| `bind_submit_prove_job` | Submit a ZK proof generation job with circuit ID and inputs |
| `bind_get_prove_job` | Poll a prove job's status by job ID |
| `bind_list_prove_jobs` | List prove jobs, optionally filtered by status |
| `bind_issue_credential` | Issue a verifiable credential from a completed prove job |
| `bind_share_proof` | Share a completed proof with a verifier org |
| `bind_list_shared_proofs` | List proofs shared with/by your org |

**Policy Authoring**

| Tool | What it does |
|------|-------------|
| `bind_whoami` | Get authenticated org info, tier, policy limits, and agent key permissions |
| `bind_validate_policy` | Dry-run validation of a policy spec (catches errors before creation) |
| `bind_create_policy` | Create a new verification policy |
| `bind_generate_circuit` | Trigger ZK circuit compilation for a saved policy |
| `bind_get_circuit_status` | Poll circuit compilation job status |

---

## Workflow 1: Full Credential Verification

**When to use:** A user gives you a VC-JWT string (starts with `eyJ...`) and wants to know if it's valid.

**Steps:**

1. `bind_parse_credential` — Decode the JWT to inspect claims
2. `bind_verify_credential` — Verify signature and expiration
3. `bind_hash_credential` — Compute SHA-256 hash
4. `bind_check_revocation` — Send the hash (not the credential) to check revocation

Steps 1 and 2 can be combined (verify includes parsing), but parsing first lets you show the user what the credential contains before the full check. Steps 1–3 run locally; step 4 sends only the hash to the API.

**Important:** `bind_verify_credential` does NOT check revocation. You must always follow up with hash + revocation check for a complete verification.

```
parse → verify → hash → check_revocation
```

## Workflow 2: Investigate an Issuer

**When to use:** A user wants to know about an organization's keys or policies.

1. `bind_resolve_issuer(orgId)` — Fetch their JWKS
2. `bind_list_policies` or `bind_explain_policy` — Look up their policies

## Workflow 3: Create a Policy

**When to use:** A user wants to define a new verification policy.

**Steps:**

1. `bind_whoami` — Check org name, tier, and limits. **You need the org name for the namespace.**
2. Build the policy spec (see Policy Spec Reference below)
3. `bind_validate_policy` — Dry-run to catch errors before creation
4. Fix any validation errors and re-validate
5. `bind_create_policy` — Save the policy
6. `bind_generate_circuit` — Queue ZK circuit compilation
7. `bind_get_circuit_status` — Poll until status is `completed` or `failed`

**Critical rules:**
- `metadata.namespace` MUST start with your org's slugified name (from `bind_whoami`). The namespaces `bind` and `system` are reserved.
- The policy `id` MUST start with the namespace (e.g., `acme.finance.creditCheck` for namespace `acme`).
- ALWAYS validate before creating. Fix all errors first.
- String inputs MUST have an `encoding` block mapping values to numbers (ZK circuits only work with numbers).

## Workflow 4: Generate a Proof and Issue a Credential

**When to use:** A user wants to generate a ZK proof and get a verifiable credential.

1. `bind_list_policies` or `bind_explain_policy` — Find the right policy/circuit
2. `bind_submit_prove_job(circuitId, inputs)` — Submit the proof job
3. `bind_get_prove_job(jobId)` — Poll until status is `completed`
4. `bind_issue_credential(proveJobId)` — Issue the VC from the completed proof
5. Optionally: `bind_share_proof(proveJobId, verifierOrgId)` — Share with a verifier

---

## Policy Spec Reference

A policy is a JSON object with this structure. All fields shown are required unless marked optional.

```json
{
  "id": "<namespace>.<category>.<name>",
  "version": "0.1.0",
  "metadata": {
    "title": "Human-readable title",
    "description": "What this policy verifies",
    "category": "finance|mobility|identity|demo",
    "namespace": "your-org-name"
  },
  "subject": {
    "type": "individual|organization|vehicle|device",
    "identifier": "wallet_address|did|vin|vehicleTokenId"
  },

  "inputs": [
    {
      "id": "input_name",
      "source": { "kind": "static|api", "api": "optional_api_name" },
      "signal": "input_name",
      "valueType": "number|boolean|string",
      "unit": "USD|count|months",
      "time": { "mode": "point|range|relative", "lookback": "30d" },
      "aggregation": { "op": "latest|sum|mean|count" },
      "encoding": {
        "type": "enum",
        "values": { "label1": 1, "label2": 2 }
      }
    }
  ],

  "rules": [
    {
      "id": "rule_name",
      "description": "Human-readable description",
      "assert": { /* expression — see below */ },
      "severity": "fail|warn|info"
    }
  ],

  "evaluation": {
    "kind": "PASS_FAIL|SCORE",
    "scoreRange": { "min": 0, "max": 100 },
    "baseline": 50,
    "contributions": [
      { "ruleId": "rule_name", "points": 30, "whenPasses": true }
    ]
  },

  "outputs": [
    {
      "name": "output_name",
      "type": "boolean|enum|number",
      "derive": {
        "kind": "PASS_FAIL|SCORE|BAND|CONST",
        "from": "SCORE|input_id",
        "bands": [
          { "label": "LOW", "minInclusive": 0, "maxExclusive": 40 },
          { "label": "HIGH", "minInclusive": 40, "maxExclusive": 101 }
        ],
        "value": 42
      },
      "disclosed": true
    }
  ],

  "validity": { "ttl": "P30D" },
  "disclosure": {
    "default": "SELECTIVE",
    "exposeClaims": ["output_name"]
  },

  "proving": {
    "circuitId": "<namespace>.<name>.v<version>",
    "inputTypes": { "input_name": "u32" },
    "outputType": "u8"
  }
}
```

### Expression Types (used in `rules[].assert`)

| Type | Shape | Example |
|------|-------|---------|
| `ref` | `{ "type": "ref", "inputId": "<input_id>" }` | Reference an input value |
| `const` | `{ "type": "const", "value": <number\|boolean> }` | Literal number or boolean (never strings) |
| `cmp` | `{ "type": "cmp", "cmp": ">=\|<=\|>\|<\|==\|!=", "left": <expr>, "right": <expr> }` | Comparison |
| `op` | `{ "type": "op", "op": "+\|-\|*\|/", "args": [<expr>, ...] }` | Arithmetic |
| `and` | `{ "type": "and", "args": [<expr>, ...] }` | Logical AND |
| `or` | `{ "type": "or", "args": [<expr>, ...] }` | Logical OR |
| `not` | `{ "type": "not", "arg": <expr> }` | Logical NOT |

**Field name gotchas:**
- Use `"inputId"` in ref expressions, NOT `"path"`
- Use `"cmp"` for the comparison operator, NOT `"operator"`
- Use `"args"` for operand lists, NOT `"children"`
- Use `"arg"` (singular) for `not`, NOT `"expr"`
- `const` values must be numbers or booleans, never strings

### Evaluation Kinds

**PASS_FAIL:** All `severity: "fail"` rules must pass. No scoring.

**SCORE:** Starts at `baseline`, adds/subtracts `points` from rule contributions.
```json
{
  "kind": "SCORE",
  "scoreRange": { "min": 0, "max": 100 },
  "baseline": 50,
  "contributions": [
    { "ruleId": "has_high_income", "points": 25, "whenPasses": true },
    { "ruleId": "has_delinquencies", "points": -20, "whenPasses": true }
  ]
}
```

### Output Derive Kinds

| Kind | Use for | Required fields |
|------|---------|----------------|
| `PASS_FAIL` | Boolean pass/fail from evaluation | None |
| `SCORE` | Raw numeric score | `from: "SCORE"` |
| `BAND` | Map score to labeled bands | `from: "SCORE"`, `bands` array |
| `CONST` | Fixed value | `value` |

### Working with String Inputs

ZK circuits only work with numbers. When a policy uses string inputs (employer names, country codes, etc.), you MUST include an `encoding` block:

```json
{
  "id": "employer",
  "source": { "kind": "static" },
  "signal": "employer",
  "valueType": "string",
  "encoding": {
    "type": "enum",
    "values": {
      "Acme Corp": 1,
      "Globex Inc": 2,
      "Initech": 3
    }
  }
}
```

### Proving Section

The `proving` section maps inputs to Noir types for the ZK circuit:

```json
{
  "proving": {
    "circuitId": "acme.safe_driver.v0_1_0",
    "inputTypes": {
      "miles_driven": "u32",
      "hard_brake_pct": "u8",
      "is_commercial": "bool"
    },
    "outputType": "u8"
  }
}
```

Available Noir types: `u8`, `u16`, `u32`, `u64`, `i8`, `i16`, `i32`, `i64`, `bool`, `Field`

---

## Tier Restrictions

Policy authoring is gated by organization tier. Always call `bind_whoami` first to check limits.

| Tier | Can Create Policies | Notes |
|------|-------------------|-------|
| Basic | No | Verification only |
| Premium | Yes | Limited inputs/rules/outputs |
| Scale | Yes | Expanded limits, can create extractors |
| Enterprise | Yes | Unlimited |
| Verifier | No | Cannot create proofs or policies |

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `NAMESPACE_MISMATCH` | Policy namespace doesn't match your org | Use your org name from `bind_whoami` as the namespace prefix |
| `TIER_LIMIT_EXCEEDED` | Your tier doesn't allow this operation | Check `bind_whoami` for limits |
| `INVALID_EXPRESSION` | Malformed rule assertion | Check expression field names (`inputId`, `cmp`, `args`, `arg`) |
| `MISSING_ENCODING` | String input without encoding | Add `encoding.type: "enum"` with values map |
| `CIRCUIT_COMPILATION_FAILED` | Circuit couldn't compile | Check the error in `bind_get_circuit_status`, fix the policy, recreate, and regenerate |

## Example: Complete Policy Creation

Here is a complete example of creating a credit score policy for org `acme`:

```json
{
  "id": "acme.finance.credit-check",
  "version": "0.1.0",
  "metadata": {
    "title": "Credit Eligibility Check",
    "description": "Evaluates creditworthiness based on income and debt ratio",
    "category": "finance",
    "namespace": "acme"
  },
  "subject": {
    "type": "individual",
    "identifier": "wallet_address"
  },
  "inputs": [
    {
      "id": "annual_income",
      "source": { "kind": "static" },
      "signal": "annual_income",
      "valueType": "number",
      "unit": "USD"
    },
    {
      "id": "debt_ratio",
      "source": { "kind": "static" },
      "signal": "debt_ratio",
      "valueType": "number",
      "unit": "percent"
    }
  ],
  "rules": [
    {
      "id": "min_income",
      "description": "Annual income must be at least $30,000",
      "assert": {
        "type": "cmp",
        "cmp": ">=",
        "left": { "type": "ref", "inputId": "annual_income" },
        "right": { "type": "const", "value": 30000 }
      },
      "severity": "fail"
    },
    {
      "id": "max_debt_ratio",
      "description": "Debt-to-income ratio must be under 40%",
      "assert": {
        "type": "cmp",
        "cmp": "<",
        "left": { "type": "ref", "inputId": "debt_ratio" },
        "right": { "type": "const", "value": 40 }
      },
      "severity": "fail"
    }
  ],
  "evaluation": {
    "kind": "PASS_FAIL"
  },
  "outputs": [
    {
      "name": "eligible",
      "type": "boolean",
      "derive": { "kind": "PASS_FAIL" },
      "disclosed": true
    }
  ],
  "validity": { "ttl": "P30D" },
  "disclosure": {
    "default": "SELECTIVE",
    "exposeClaims": ["eligible"]
  },
  "proving": {
    "circuitId": "acme.credit_check.v0_1_0",
    "inputTypes": {
      "annual_income": "u32",
      "debt_ratio": "u8"
    },
    "outputType": "u8"
  }
}
```

Agent workflow for this:
1. `bind_whoami` — Confirm org is `acme` and tier allows policy creation
2. `bind_validate_policy(policy)` — Dry-run validation
3. `bind_create_policy(policy)` — Create the policy
4. `bind_generate_circuit("acme.finance.credit-check")` — Compile the circuit
5. `bind_get_circuit_status(jobId)` — Poll until complete
