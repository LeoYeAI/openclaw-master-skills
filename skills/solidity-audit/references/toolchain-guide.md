# Audit Toolchain Configuration Guide

## Gap Analysis and Solutions

### Gap 1: Missing Toolchain (60%)

**Problem**: AI cannot directly run Slither/Foundry tools

**Solution**: Create tool-assisted audit workflow

---

## Tool Installation Guide

### 1. Slither Static Analysis

```bash
# Installation (requires Python 3.8+)
pip install slither-analyzer

# Verify installation
slither --version

# Quick scan
slither . --exclude-dependencies

# Specific detection
slither . --detect reentrancy-eth,uninitialized-state

# Output JSON
slither . --exclude-dependencies --json slither-report.json
```

### 2. Aderyn (Rust-based, faster)

```bash
# Installation
cargo install aderyn

# Scan
aderyn .

# Output Markdown
aderyn . -o audit-report.md
```

### 3. Foundry Test Framework

```bash
# Installation
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Compile
forge build

# Run tests
forge test

# Fuzz testing
forge test --fuzz-runs 10000
```

---

## Tool Output Interpretation

### Slither High-Risk Detectors

| Detector | Description | EEA Mapping |
|----------|-------------|-------------|
| `reentrancy-eth` | ETH reentrancy | [M] External Calls |
| `uninitialized-state` | Uninitialized state variable | [S] Initialize State |
| `arbitrary-send` | Arbitrary send ETH | [M] Verify Ether Transfer |
| `controlled-delegatecall` | Controlled delegatecall | [S] No assembly |

---

## Gap 2: Time Constraints (25%)

**Solution**: Focus on high-risk modules

### Time Allocation Template

| Phase | Time | Content |
|-------|------|---------|
| Tool scanning | 5 minutes | Slither/Aderyn |
| High-risk modules | 15 minutes | Liquidation/withdrawal/permissions |
| Medium-risk modules | 10 minutes | Price/state updates |
| Report output | 5 minutes | Formatted report |

### High-Risk Function Priority

```
1. Withdrawal functions: withdraw, transfer, claim
2. Liquidation functions: liquidate, absorb, seize
3. Permission functions: setOwner, setConfig
4. Price functions: getPrice, updatePrice
5. External calls: call, delegatecall
```

---

## Gap 3: Knowledge Gaps (15%)

**Solution**: Protocol type knowledge base

### DeFi Protocol Types

| Type | Core Risks | Check Points |
|------|------------|--------------|
| AMM | Price manipulation | Price calculation, liquidity |
| Lending | Liquidation, oracle | Factor checks, interest rates |
| Cross-chain | Verification, replay | Signature verification |
| Aggregator | Composability risks | Interaction order |
| NFT | Royalties, metadata | Transfer, authorization |

---

## Integrated Audit Process

### Standard Process (with tools)

```
1. [Tool] Slither quick scan → 2. [AI] High-risk analysis → 3. [AI] Report
```

### Quick Process (without tools)

```
1. [AI] Access control → 2. [AI] Reentrancy check → 3. [AI] Token security → 4. [AI] Report
```