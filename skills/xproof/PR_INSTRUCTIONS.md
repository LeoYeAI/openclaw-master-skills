# PR Submission: xProof Skill for multiversx-openclaw-skills

## Target Repository

**Repo:** `sasurobert/multiversx-openclaw-skills`
**Branch:** `master`
**URL:** https://github.com/sasurobert/multiversx-openclaw-skills

## Files to Add

```
skills/xproof/
  SKILL.md                     <-- Main skill file (copy from xproof-openclaw/SKILL.md)
  references/
    certification.md           <-- REST API reference
    x402.md                    <-- x402 payment flow
    mcp.md                     <-- MCP JSON-RPC tools
```

**Important:** In the PR, the files go under `skills/xproof/` (not `skills/xproof-openclaw/`). The `-openclaw` suffix is only used locally in this repo to distinguish from the Conway/Automaton skill.

## Step-by-Step

### 1. Fork the Repository

Go to https://github.com/sasurobert/multiversx-openclaw-skills and click **Fork**.

### 2. Create the Files

In your fork, create the directory `skills/xproof/` and add the four files listed above.

Using GitHub web editor:
- Navigate to your fork
- Click **Add file > Create new file**
- Type `skills/xproof/SKILL.md` in the filename field (GitHub will create the directory)
- Paste the contents of `SKILL.md`
- Commit
- Repeat for `skills/xproof/references/certification.md`, `skills/xproof/references/x402.md`, `skills/xproof/references/mcp.md`

### 3. Open the Pull Request

Go to your fork and click **Contribute > Open pull request**.

---

## PR Title

```
feat: add xProof certification skill -- blockchain proof-of-existence for agent outputs
```

## PR Body

```markdown
## What

Adds an **xProof certification skill** that enables MultiversX agents to certify their outputs on-chain -- creating immutable, publicly verifiable proofs of existence, authorship, and timestamp.

## Why

Agents that produce work (code, reports, data, models) need a way to prove what they created and when. xProof provides this as a composable primitive on MultiversX:

- **$0.05/cert** -- negligible cost, high value
- **6-second finality** -- proof is immutable within seconds
- **x402 compatible** -- any x402-enabled agent can certify without an account
- **MCP native** -- discoverable via standard Model Context Protocol
- **Complements MX-8004** -- use xProof hash as `submit_proof` payload in the Validation Registry

## How it Integrates

| MultiversX Skill | xProof Complement |
|:---|:---|
| `init_job` | Certify output before submitting proof |
| `submit_proof` | Use xProof hash as the proof payload |
| `register_agent` | Certify manifest for integrity |
| `deposit` (Escrow) | Certify deliverables before release |

## Files Added

```
skills/xproof/
  SKILL.md                  # Agent-facing skill instructions
  references/
    certification.md        # REST API reference (POST /api/proof, /api/batch, GET /api/proof/:id)
    x402.md                 # x402 payment flow (USDC on Base, no account needed)
    mcp.md                  # MCP JSON-RPC 2.0 tool definitions
```

## Format

Follows the same structure as the root SKILL.md:
- YAML frontmatter (name, version, description, homepage, metadata)
- Skills catalog tables
- Configuration section
- Lifecycle diagram
- Command cheatsheet

## Live

- **App:** https://xproof.app
- **MCP:** `POST https://xproof.app/mcp`
- **x402:** `POST https://xproof.app/api/proof` (no auth, pay per request)
- **Docs:** https://xproof.app/llms-full.txt
```

---

## Context for Robert Sasu

If Robert asks why this belongs in the repo:

1. **Complementary, not competing** -- xProof doesn't replicate identity/escrow/validation. It adds a missing primitive: proof-of-output. Every agent that does work should be able to prove it.

2. **Uses the same stack** -- xProof anchors on MultiversX mainnet, supports x402, and integrates with MX-8004 Validation Registry. The xProof hash is the natural payload for `submit_proof`.

3. **Zero friction** -- agents already using the MultiversX skill bundle can add xProof with one extra curl. No additional wallet or SDK required.

4. **Conway-ready** -- any x402-enabled automaton can certify without setup, making the MultiversX ecosystem more composable for autonomous agents.
