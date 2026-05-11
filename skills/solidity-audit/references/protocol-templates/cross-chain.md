# Cross-Chain Protocol Audit Template

## Protocol Type Identification

**Characteristics**:
- Supports multi-chain asset transfers
- Cross-chain message verification
- May have fast liquidity
- Supports multiple AMBs

**Key Contracts**:
- Bridge / Portal
- Connector / Hub
- Router / LiquidityProvider
- MessageVerifier

---

## 1. Message Verification Mechanism Check

### 1.1 Verification Mode Identification

| Mode | Principle | Risk | Check Points |
|------|-----------|------|--------------|
| **Optimistic Verification** | Submittable during challenge period | Watcher not timely | Challenge period length |
| **Final Verification** | Wait for source chain finality | High latency | Finality guarantee |
| **Hybrid Mode** | Fast + slow path | State inconsistency | Path switching logic |
| **ZK Verification** | Zero-knowledge proof | Proof system vulnerability | Proof verification |

### 1.2 Optimistic Verification Checklist

- [ ] Challenge period duration sufficient (>= 4 hours)
- [ ] Watcher count and incentive mechanism
- [ ] Handling logic after successful challenge
- [ ] Emergency pause mechanism exists

---

## 2. Signature Security Check

### 2.1 Signature Replay Risk

| Replay Type | Risk | Protection |
|-------------|------|------------|
| Same-chain replay | Low | Nonce management |
| Cross-chain replay | High | chainId in signature |
| Cross-protocol replay | Medium | Protocol identifier |

### 2.2 Checklist

- [ ] Signature includes chainId
- [ ] Signature includes domain separator
- [ ] Nonce correctly managed
- [ ] Signature has expiration

---

## 3. Asset Security Check

### 3.1 Checklist

- [ ] Lock contract has permission control
- [ ] Minting limit exists
- [ ] Emergency withdrawal mechanism exists
- [ ] Token precision handling correct

---

## 4. AMB Dependency Check

### 4.1 Common AMB Characteristics

| AMB | Security Model | Finality |
|-----|----------------|----------|
| Arbitrum | Fraud proof | ~7 days |
| Optimism | Fraud proof | ~7 days |
| Wormhole | Guardian network | Seconds |
| LayerZero | Relayer + Oracle | Seconds |
| Polygon | Checkpoint | ~10 minutes |

### 4.2 Checklist

- [ ] Which AMBs are supported
- [ ] AMB security assumptions
- [ ] Multi-AMB redundancy

---

## 5. Known Attack Cases

| Case | Year | Root Cause |
|------|------|------------|
| Nomad | 2022 | Initialization error |
| Wormhole | 2022 | Signature bypass |
| Multichain | 2023 | Key leak |
| Poly Network | 2021 | Permission bypass |
| Ronin | 2022 | Key leak |

---

## 6. Attack Vector Check

- [ ] Can messages be forged
- [ ] Can messages be replayed
- [ ] Can verification be bypassed
- [ ] Can prices be manipulated

---

## 7. Report Template

```markdown
# [Project Name] Cross-Chain Protocol Audit Report

## Protocol Type
- Verification mode: [Optimistic/Final/Hybrid]
- Supported AMBs: [List]

## Findings Summary
| ID | Finding | Severity |
|----|---------|----------|
| H-01 | ... | High |
```