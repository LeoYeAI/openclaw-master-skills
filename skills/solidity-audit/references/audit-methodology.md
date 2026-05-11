# Smart Contract Audit Methodology - Fundamental Approach

## Gap Essence Analysis

| Gap | Surface Issue | Root Cause | Solution |
|-----|---------------|------------|----------|
| Cross-chain security | -25% | Insufficient protocol type knowledge | Protocol type templates |
| Math boundaries | Missed | Cannot run fuzz tests | Human-machine toolchain |

---

## Three-Layer Audit Framework

### Layer 1: Protocol Type Templating

**Principle**: Each protocol type has fixed attack surfaces.

| Type | Core Attack Surface |
|------|---------------------|
| Cross-chain Bridge | Message verification, signature replay |
| Lending Protocol | Liquidation, oracle manipulation |
| AMM | Price manipulation, slippage |
| NFT Market | Signature verification, royalties |

---

### Layer 2: Human-Machine Toolchain

| Tool | Purpose | AI Analysis Focus |
|------|---------|-------------------|
| Slither | Static analysis | Analyze detector output |
| Foundry fuzz | Boundary testing | Analyze failed cases |
| Echidna | Invariant testing | Analyze violated invariants |

---

### Layer 3: Continuous Knowledge Base

```
Audit → Discover issues → Update knowledge base → Better next audit
```

---

## Root Methodology

### One-Line Principle

> Protocol type determines attack surface, tools discover boundary conditions, knowledge base provides checklist items